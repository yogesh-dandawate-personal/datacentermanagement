"""
Executive Copilot Service

Main service implementing Retrieval-Augmented Generation (RAG):
- Process user questions
- Retrieve relevant context from vector store
- Generate responses using Claude API
- Track citations and prevent fabrication
- Manage conversation history
- Enforce access control and rate limiting
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models import (
    CopilotQuery,
    CopilotResponse,
    CopilotCitation,
    CopilotMessageHistory,
    CopilotFeedback,
    CopilotAccessLog,
    CopilotRateLimit,
    User,
    Tenant,
    Organization,
)
from app.integrations.vector_store import VectorStoreService
from app.integrations.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class CopilotService:
    """
    Main copilot service for Q&A functionality
    Implements RAG with guardrails and citation tracking
    """

    # Configuration
    RESPONSE_CACHE_TTL_MINUTES = 60
    RATE_LIMIT_QUERIES_HOURLY = 100
    RATE_LIMIT_TOKENS_HOURLY = 100000
    MIN_CONFIDENCE_FOR_RESPONSE = 0.3
    MAX_CONTEXT_ITEMS = 10

    def __init__(
        self,
        db: Session,
        vector_store: VectorStoreService,
        claude_client: ClaudeClient,
    ):
        """
        Initialize copilot service

        Args:
            db: SQLAlchemy session
            vector_store: Vector store service for semantic search
            claude_client: Claude API client
        """
        self.db = db
        self.vector_store = vector_store
        self.claude_client = claude_client

    async def ask_question(
        self,
        tenant_id: str,
        user_id: str,
        question: str,
        organization_id: Optional[str] = None,
    ) -> Dict:
        """
        Process a user question and return answer with citations

        Args:
            tenant_id: Tenant ID (multi-tenant isolation)
            user_id: User asking the question
            question: The question text
            organization_id: Optional organization filter

        Returns:
            Dictionary with answer, citations, confidence, etc.
        """
        try:
            # Validate access and rate limits
            access_check = await self._validate_access(tenant_id, user_id)
            if "error" in access_check:
                return access_check

            rate_check = await self._check_rate_limit(tenant_id, user_id)
            if not rate_check["allowed"]:
                return {
                    "error": "Rate limit exceeded",
                    "retry_after_minutes": rate_check.get("retry_after"),
                }

            # Check cache for identical questions
            cached_response = await self._get_cached_response(
                tenant_id, user_id, question
            )
            if cached_response:
                logger.info(f"Returning cached response for question")
                return {**cached_response, "from_cache": True}

            # Create query record
            query = CopilotQuery(
                tenant_id=tenant_id,
                user_id=user_id,
                organization_id=organization_id,
                question=question,
                query_type="general",
                status="processing",
            )
            self.db.add(query)
            self.db.commit()
            query_id = str(query.id)

            logger.info(f"Processing question: {question[:100]}... (Query ID: {query_id})")

            # Generate embedding for semantic search
            embedding = await self.vector_store.generate_embedding(question)
            if embedding:
                query.embedding = embedding
                self.db.commit()

            # Retrieve context using RAG
            context = await self.vector_store.build_retrieval_context(
                tenant_id, user_id, question, context_limit=self.MAX_CONTEXT_ITEMS
            )

            if "error" in context:
                query.status = "failed"
                query.error_message = context["error"]
                self.db.commit()
                return {
                    "error": "Failed to retrieve context",
                    "details": context["error"],
                }

            # Get conversation history if needed
            conversation_history = await self._get_conversation_history(
                query_id, max_messages=10
            )

            # Generate response using Claude
            messages, formatted_context = self.claude_client.create_user_message(
                question, context, conversation_history
            )

            response_text, usage = await self.claude_client.generate_response(
                messages, max_tokens=2000
            )

            if not response_text:
                query.status = "failed"
                query.error_message = "Failed to generate response"
                self.db.commit()
                return {"error": "Failed to generate response from Claude API"}

            # Validate no fabrication
            is_valid, fabrication_issues = self.claude_client.validate_no_fabrication(
                response_text, context
            )

            # Extract citations
            citations = self.claude_client.extract_citations_from_answer(
                response_text, context
            )

            # Calculate confidence
            confidence = self.claude_client.calculate_confidence_score(
                response_text, context, usage
            )

            # Validate confidence threshold
            if confidence < self.MIN_CONFIDENCE_FOR_RESPONSE:
                return {
                    "error": "Low confidence in response",
                    "confidence": float(confidence),
                    "message": "Unable to generate confident answer with available data",
                }

            # Create response record
            response = CopilotResponse(
                query_id=query_id,
                tenant_id=tenant_id,
                user_id=user_id,
                answer=response_text,
                answer_summary=response_text[:500],
                model_used="claude-3-5-sonnet-20241022",
                confidence=Decimal(str(confidence)),
                has_fabrication=not is_valid,
                processing_time_ms=int(usage.get("total_tokens", 0) * 10),  # Estimate
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                tokens_used=usage.get("total_tokens", 0),
                status="completed",
                data_quality="good" if confidence > 0.8 else "fair",
            )
            self.db.add(response)
            self.db.commit()
            response_id = str(response.id)

            # Store citations
            for citation in citations:
                citation_obj = CopilotCitation(
                    response_id=response_id,
                    tenant_id=tenant_id,
                    entity_type=citation.get("entity_type"),
                    entity_id=citation.get("entity_id"),
                    entity_name=citation.get("entity_name"),
                    entity_data=citation.get("entity_data"),
                    citation_type=citation.get("citation_type", "data_source"),
                    is_verified=True,  # Data from our own system is verified
                    confidence=Decimal("1.0"),
                    verification_status="verified",
                )
                self.db.add(citation_obj)

            # Add system message to history
            history_msg = CopilotMessageHistory(
                query_id=query_id,
                tenant_id=tenant_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                response_id=response_id,
                sequence_number=len(conversation_history) + 1,
                context_summary={"context_items": len(context.get("metrics", []))},
            )
            self.db.add(history_msg)

            # Update query status
            query.status = "processed"
            self.db.commit()

            # Log access
            await self._log_access(
                tenant_id, user_id, query_id, "ask_question", organization_id
            )

            # Update rate limit
            await self._update_rate_limit(
                tenant_id, user_id, usage.get("total_tokens", 0)
            )

            return {
                "query_id": query_id,
                "response_id": response_id,
                "answer": response_text,
                "citations": [
                    {
                        "id": c.id,
                        "type": c.entity_type,
                        "name": c.entity_name,
                        "data": c.entity_data,
                        "verified": c.is_verified,
                    }
                    for c in response.citations
                ],
                "confidence": float(confidence),
                "data_quality": response.data_quality,
                "tokens_used": usage.get("total_tokens", 0),
                "has_issues": not is_valid,
                "issues": fabrication_issues if not is_valid else [],
                "created_at": response.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in ask_question: {str(e)}", exc_info=True)
            return {"error": f"Internal error: {str(e)}"}

    async def _validate_access(self, tenant_id: str, user_id: str) -> Dict:
        """
        Validate user has access to copilot and tenant

        Args:
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Empty dict if valid, error dict otherwise
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                return {"error": "User not found"}

            if user.tenant_id != tenant_id:
                logger.warning(
                    f"Unauthorized access attempt: user {user_id} accessing tenant {tenant_id}"
                )
                return {"error": "Unauthorized access"}

            if not user.is_active:
                return {"error": "User is inactive"}

            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant or not tenant.is_active:
                return {"error": "Tenant is inactive"}

            return {}

        except Exception as e:
            logger.error(f"Error validating access: {str(e)}")
            return {"error": "Access validation failed"}

    async def _check_rate_limit(self, tenant_id: str, user_id: str) -> Dict:
        """
        Check if user has exceeded rate limits

        Args:
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Dict with allowed (bool) and retry_after (int) if not allowed
        """
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(hours=1)

            # Get current window
            current_limit = (
                self.db.query(CopilotRateLimit)
                .filter(
                    and_(
                        CopilotRateLimit.tenant_id == tenant_id,
                        CopilotRateLimit.user_id == user_id,
                        CopilotRateLimit.window_type == "hourly",
                        CopilotRateLimit.window_start >= window_start,
                    )
                )
                .first()
            )

            if not current_limit:
                # Create new window
                return {"allowed": True}

            if current_limit.query_count >= self.RATE_LIMIT_QUERIES_HOURLY:
                retry_after = int(
                    (current_limit.window_end - now).total_seconds() / 60
                )
                return {"allowed": False, "retry_after": max(1, retry_after)}

            if current_limit.total_tokens >= self.RATE_LIMIT_TOKENS_HOURLY:
                retry_after = int(
                    (current_limit.window_end - now).total_seconds() / 60
                )
                return {"allowed": False, "retry_after": max(1, retry_after)}

            return {"allowed": True}

        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return {"allowed": True}  # Fail open

    async def _get_cached_response(
        self, tenant_id: str, user_id: str, question: str
    ) -> Optional[Dict]:
        """
        Get cached response for identical question

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            question: Question text

        Returns:
            Cached response dict or None
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(
                minutes=self.RESPONSE_CACHE_TTL_MINUTES
            )

            cached_query = (
                self.db.query(CopilotQuery)
                .filter(
                    and_(
                        CopilotQuery.tenant_id == tenant_id,
                        CopilotQuery.user_id == user_id,
                        CopilotQuery.question == question,
                        CopilotQuery.created_at >= cutoff_time,
                    )
                )
                .order_by(desc(CopilotQuery.created_at))
                .first()
            )

            if cached_query and cached_query.responses:
                response = cached_query.responses[0]
                return {
                    "query_id": str(cached_query.id),
                    "response_id": str(response.id),
                    "answer": response.answer,
                    "citations": [
                        {
                            "id": str(c.id),
                            "type": c.entity_type,
                            "name": c.entity_name,
                            "verified": c.is_verified,
                        }
                        for c in response.citations
                    ],
                    "confidence": float(response.confidence),
                }

            return None

        except Exception as e:
            logger.error(f"Error getting cached response: {str(e)}")
            return None

    async def _get_conversation_history(
        self, query_id: str, max_messages: int = 10
    ) -> List[Dict]:
        """
        Get conversation history for a query

        Args:
            query_id: Query ID
            max_messages: Maximum messages to retrieve

        Returns:
            List of message dicts
        """
        try:
            messages = (
                self.db.query(CopilotMessageHistory)
                .filter_by(query_id=query_id)
                .order_by(CopilotMessageHistory.sequence_number)
                .limit(max_messages)
                .all()
            )

            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []

    async def _log_access(
        self,
        tenant_id: str,
        user_id: str,
        query_id: Optional[str],
        action: str,
        organization_id: Optional[str] = None,
    ) -> bool:
        """
        Log copilot access for audit trail

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            query_id: Query ID if applicable
            action: Action performed
            organization_id: Organization ID if applicable

        Returns:
            True if logged successfully
        """
        try:
            log = CopilotAccessLog(
                tenant_id=tenant_id,
                user_id=user_id,
                query_id=query_id,
                action=action,
                action_category="query",
                organization_id=organization_id,
            )
            self.db.add(log)
            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
            return False

    async def _update_rate_limit(
        self, tenant_id: str, user_id: str, tokens_used: int
    ) -> bool:
        """
        Update rate limit counters

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            tokens_used: Number of tokens used

        Returns:
            True if updated successfully
        """
        try:
            now = datetime.utcnow()
            window_start = now.replace(minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(hours=1)

            limit = (
                self.db.query(CopilotRateLimit)
                .filter(
                    and_(
                        CopilotRateLimit.tenant_id == tenant_id,
                        CopilotRateLimit.user_id == user_id,
                        CopilotRateLimit.window_type == "hourly",
                        CopilotRateLimit.window_start == window_start,
                    )
                )
                .first()
            )

            if not limit:
                limit = CopilotRateLimit(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    window_type="hourly",
                    window_start=window_start,
                    window_end=window_end,
                    query_count=1,
                    total_tokens=tokens_used,
                )
                self.db.add(limit)
            else:
                limit.query_count += 1
                limit.total_tokens += tokens_used
                limit.is_exceeded = (
                    limit.query_count > self.RATE_LIMIT_QUERIES_HOURLY
                    or limit.total_tokens > self.RATE_LIMIT_TOKENS_HOURLY
                )

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating rate limit: {str(e)}")
            return False

    async def get_response_history(
        self, tenant_id: str, user_id: str, limit: int = 20, offset: int = 0
    ) -> Dict:
        """
        Get user's question and response history

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            limit: Number of results
            offset: Offset for pagination

        Returns:
            Dictionary with history and pagination info
        """
        try:
            queries = (
                self.db.query(CopilotQuery)
                .filter(
                    and_(
                        CopilotQuery.tenant_id == tenant_id,
                        CopilotQuery.user_id == user_id,
                    )
                )
                .order_by(desc(CopilotQuery.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            history = [
                {
                    "query_id": str(q.id),
                    "question": q.question,
                    "created_at": q.created_at.isoformat(),
                    "response_count": len(q.responses),
                    "status": q.status,
                    "latest_response": {
                        "id": str(q.responses[0].id),
                        "confidence": float(q.responses[0].confidence),
                        "created_at": q.responses[0].created_at.isoformat(),
                    }
                    if q.responses
                    else None,
                }
                for q in queries
            ]

            total_count = (
                self.db.query(func.count(CopilotQuery.id))
                .filter(
                    and_(
                        CopilotQuery.tenant_id == tenant_id,
                        CopilotQuery.user_id == user_id,
                    )
                )
                .scalar()
            )

            return {
                "history": history,
                "total": total_count,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            logger.error(f"Error getting response history: {str(e)}")
            return {"error": str(e), "history": []}

    async def submit_feedback(
        self,
        tenant_id: str,
        user_id: str,
        query_id: str,
        response_id: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        issues: Optional[List[str]] = None,
    ) -> Dict:
        """
        Submit user feedback on response

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            query_id: Query ID
            response_id: Response ID
            rating: 1-5 star rating
            comment: User comment
            issues: List of issues identified

        Returns:
            Feedback confirmation dict
        """
        try:
            # Verify ownership
            query = (
                self.db.query(CopilotQuery)
                .filter_by(id=query_id, user_id=user_id)
                .first()
            )
            if not query:
                return {"error": "Query not found or access denied"}

            response = (
                self.db.query(CopilotResponse)
                .filter_by(id=response_id, query_id=query_id)
                .first()
            )
            if not response:
                return {"error": "Response not found"}

            # Create feedback
            feedback = CopilotFeedback(
                query_id=query_id,
                response_id=response_id,
                tenant_id=tenant_id,
                user_id=user_id,
                rating=rating,
                comment=comment,
                issues=issues,
                has_fabrication="fabrication" in (issues or []),
                has_missing_data="missing_data" in (issues or []),
                has_incorrect_citation="incorrect_citation" in (issues or []),
            )
            self.db.add(feedback)
            self.db.commit()

            # Log access
            await self._log_access(
                tenant_id, user_id, query_id, "feedback_submitted"
            )

            return {
                "feedback_id": str(feedback.id),
                "status": "recorded",
                "created_at": feedback.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return {"error": str(e)}
