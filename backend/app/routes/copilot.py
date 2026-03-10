"""
Executive Copilot API Routes

Endpoints for Q&A functionality:
- POST /api/v1/tenants/{tenant_id}/copilot/ask - Submit question
- GET /api/v1/tenants/{tenant_id}/copilot/history - Get query history
- GET /api/v1/tenants/{tenant_id}/copilot/responses/{response_id} - Get full response
- POST /api/v1/tenants/{tenant_id}/copilot/feedback - Submit feedback
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.copilot_service import CopilotService
from app.integrations.vector_store import VectorStoreService
from app.integrations.claude_client import ClaudeClient
from app.models import CopilotQuery, CopilotResponse, CopilotCitation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["copilot"])


def get_current_user(authorization: str = Header(None)):
    """Extract and verify current user from token"""
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or missing token")


def get_copilot_service(db: Session = Depends(get_db)) -> CopilotService:
    """Initialize copilot service with dependencies"""
    vector_store = VectorStoreService(db, None)  # None for embedding client
    claude_client = ClaudeClient()
    return CopilotService(db, vector_store, claude_client)


@router.post("/tenants/{tenant_id}/copilot/ask")
async def ask_copilot(
    tenant_id: str,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit a question to the executive copilot

    Request body:
    {
        "question": "What is our Scope 2 emissions this month?",
        "organization_id": "org-uuid" (optional)
    }

    Returns:
    {
        "query_id": "uuid",
        "response_id": "uuid",
        "answer": "...",
        "citations": [...],
        "confidence": 0.95,
        "tokens_used": 450,
        "created_at": "2026-03-10T..."
    }
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Validate request
        question = question_data.get("question", "").strip()
        if not question or len(question) < 3:
            raise HTTPException(status_code=400, detail="Question must be at least 3 characters")

        if len(question) > 5000:
            raise HTTPException(status_code=400, detail="Question exceeds maximum length")

        organization_id = question_data.get("organization_id")

        # Get copilot service
        copilot_service = get_copilot_service(db)

        # Process question
        result = await copilot_service.ask_question(
            tenant_id=tenant_id,
            user_id=current_user["user_id"],
            question=question,
            organization_id=organization_id,
        )

        # Check for errors
        if "error" in result:
            status_code = 429 if "Rate limit" in result.get("error") else 400
            raise HTTPException(status_code=status_code, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_copilot: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tenants/{tenant_id}/copilot/history")
async def get_copilot_history(
    tenant_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's copilot query history

    Query parameters:
    - limit: Number of results (1-100, default 20)
    - offset: Pagination offset (default 0)

    Returns:
    {
        "history": [
            {
                "query_id": "uuid",
                "question": "...",
                "created_at": "...",
                "response_count": 1,
                "status": "processed",
                "latest_response": {
                    "id": "uuid",
                    "confidence": 0.95,
                    "created_at": "..."
                }
            }
        ],
        "total": 42,
        "limit": 20,
        "offset": 0
    }
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        copilot_service = get_copilot_service(db)

        result = await copilot_service.get_response_history(
            tenant_id=tenant_id,
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset,
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tenants/{tenant_id}/copilot/responses/{response_id}")
async def get_response_details(
    tenant_id: str,
    response_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get full response details with all citations

    Returns:
    {
        "response_id": "uuid",
        "query_id": "uuid",
        "question": "...",
        "answer": "...",
        "model_used": "claude-3-5-sonnet-20241022",
        "confidence": 0.95,
        "data_quality": "good",
        "tokens_used": 450,
        "processing_time_ms": 2500,
        "has_fabrication": false,
        "citations": [
            {
                "id": "uuid",
                "type": "metric",
                "name": "Power Usage Effectiveness",
                "verified": true,
                "entity_data": {
                    "value": 1.45,
                    "unit": "ratio",
                    "timestamp": "..."
                },
                "source_url": "/api/v1/kpis/..."
            }
        ],
        "created_at": "2026-03-10T..."
    }
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Get response
        response = (
            db.query(CopilotResponse)
            .filter(
                CopilotResponse.id == response_id,
                CopilotResponse.tenant_id == tenant_id,
            )
            .first()
        )

        if not response:
            raise HTTPException(status_code=404, detail="Response not found")

        # Verify user owns the query
        if response.user_id != current_user["user_id"]:
            # Allow admins to view any response in tenant
            if "admin" not in current_user.get("roles", []):
                raise HTTPException(status_code=403, detail="Unauthorized access")

        # Get query
        query = db.query(CopilotQuery).filter_by(id=response.query_id).first()

        return {
            "response_id": str(response.id),
            "query_id": str(response.query_id),
            "question": query.question if query else "Unknown",
            "answer": response.answer,
            "model_used": response.model_used,
            "confidence": float(response.confidence),
            "data_quality": response.data_quality,
            "tokens_used": response.tokens_used,
            "processing_time_ms": response.processing_time_ms,
            "has_fabrication": response.has_fabrication,
            "citations": [
                {
                    "id": str(citation.id),
                    "type": citation.entity_type,
                    "name": citation.entity_name,
                    "verified": citation.is_verified,
                    "confidence": float(citation.confidence),
                    "entity_data": citation.entity_data,
                    "source_url": citation.source_url,
                    "citation_type": citation.citation_type,
                }
                for citation in response.citations
            ],
            "created_at": response.created_at.isoformat(),
            "updated_at": response.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting response details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tenants/{tenant_id}/copilot/feedback")
async def submit_response_feedback(
    tenant_id: str,
    feedback_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit feedback on a copilot response

    Request body:
    {
        "query_id": "uuid",
        "response_id": "uuid",
        "rating": 4,
        "comment": "This was helpful but missing recent data",
        "issues": ["missing_data", "outdated_metrics"]
    }

    Returns:
    {
        "feedback_id": "uuid",
        "status": "recorded",
        "created_at": "2026-03-10T..."
    }
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Validate request
        query_id = feedback_data.get("query_id")
        response_id = feedback_data.get("response_id")

        if not query_id or not response_id:
            raise HTTPException(status_code=400, detail="query_id and response_id required")

        rating = feedback_data.get("rating")
        if rating and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be 1-5")

        comment = feedback_data.get("comment", "").strip()
        if len(comment) > 2000:
            raise HTTPException(status_code=400, detail="Comment exceeds maximum length")

        issues = feedback_data.get("issues", [])
        if not isinstance(issues, list):
            raise HTTPException(status_code=400, detail="Issues must be a list")

        copilot_service = get_copilot_service(db)

        result = await copilot_service.submit_feedback(
            tenant_id=tenant_id,
            user_id=current_user["user_id"],
            query_id=query_id,
            response_id=response_id,
            rating=rating,
            comment=comment if comment else None,
            issues=issues if issues else None,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tenants/{tenant_id}/copilot/similar-questions")
async def get_similar_questions(
    tenant_id: str,
    q: str = Query(..., min_length=3, max_length=500, description="Question to find similar to"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Find similar questions asked previously

    Query parameters:
    - q: Question text to find similar questions for
    - limit: Maximum number of results (1-20, default 5)

    Returns:
    [
        {
            "question": "...",
            "created_at": "...",
            "response_count": 1,
            "similarity": 0.92
        }
    ]
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        vector_store = VectorStoreService(db, None)
        similar = await vector_store.get_similar_questions(
            tenant_id=tenant_id,
            query_text=q,
            limit=limit,
        )

        return similar

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tenants/{tenant_id}/copilot/stats")
async def get_copilot_stats(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get copilot usage statistics for the user

    Returns:
    {
        "total_queries": 42,
        "total_responses": 42,
        "avg_confidence": 0.85,
        "queries_with_issues": 3,
        "avg_response_time_ms": 2500,
        "most_common_topics": ["emissions", "metrics"],
        "feedback_count": 5
    }
    """
    try:
        # Verify tenant access
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        from sqlalchemy import func

        # Get statistics
        query_count = (
            db.query(func.count(CopilotQuery.id))
            .filter(
                CopilotQuery.tenant_id == tenant_id,
                CopilotQuery.user_id == current_user["user_id"],
            )
            .scalar()
        )

        response_count = (
            db.query(func.count(CopilotResponse.id))
            .join(CopilotQuery)
            .filter(
                CopilotQuery.tenant_id == tenant_id,
                CopilotQuery.user_id == current_user["user_id"],
            )
            .scalar()
        )

        avg_confidence = (
            db.query(func.avg(CopilotResponse.confidence))
            .join(CopilotQuery)
            .filter(
                CopilotQuery.tenant_id == tenant_id,
                CopilotQuery.user_id == current_user["user_id"],
            )
            .scalar()
        )

        issues_count = (
            db.query(func.count(CopilotResponse.id))
            .join(CopilotQuery)
            .filter(
                CopilotQuery.tenant_id == tenant_id,
                CopilotQuery.user_id == current_user["user_id"],
                CopilotResponse.has_fabrication == True,
            )
            .scalar()
        )

        return {
            "total_queries": query_count or 0,
            "total_responses": response_count or 0,
            "avg_confidence": float(avg_confidence) if avg_confidence else 0.0,
            "queries_with_issues": issues_count or 0,
            "feedback_count": 0,  # Would be calculated from CopilotFeedback
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
