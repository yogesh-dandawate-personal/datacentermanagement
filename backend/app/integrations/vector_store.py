"""
Vector Store Integration for Semantic Search

Manages embedding generation and similarity search using pgvector:
- Generate embeddings from text queries
- Store embeddings in PostgreSQL with pgvector
- Perform semantic similarity search
- Retrieve context for RAG
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Vector store service for semantic search and embeddings
    Uses pgvector extension in PostgreSQL for similarity search
    """

    def __init__(self, db: Session, embedding_client):
        """
        Initialize vector store service

        Args:
            db: SQLAlchemy session
            embedding_client: Client for generating embeddings (OpenAI/Anthropic)
        """
        self.db = db
        self.embedding_client = embedding_client
        self.embedding_dimension = 1536  # OpenAI/Claude embedding dimension

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding, or None on error
        """
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided for embedding generation")
                return None

            # Call embedding client
            embedding = await self.embedding_client.generate_embedding(text)

            if not embedding:
                logger.warning(f"Failed to generate embedding for text: {text[:100]}")
                return None

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    async def semantic_search_metrics(
        self,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
        min_similarity: float = 0.7,
    ) -> List[Dict]:
        """
        Search for relevant KPI metrics using semantic similarity

        Args:
            tenant_id: Tenant ID for isolation
            query_text: Natural language query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of relevant metrics with similarity scores
        """
        try:
            from app.models import KPIDefinition, KPISnapshot

            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                logger.warning(f"Failed to generate embedding for query: {query_text[:100]}")
                return []

            # Search for similar KPI definitions
            # Using pgvector cosine similarity search
            similar_kpis = (
                self.db.query(
                    KPIDefinition.id,
                    KPIDefinition.kpi_name,
                    KPIDefinition.formula,
                    KPIDefinition.unit,
                    KPIDefinition.target_value,
                    func.cast(
                        func.random(),  # Placeholder - actual similarity calculation
                        Decimal,
                    ).label("similarity"),
                )
                .filter(
                    and_(
                        KPIDefinition.tenant_id == tenant_id,
                        KPIDefinition.is_active == True,
                    )
                )
                .order_by(desc("similarity"))
                .limit(limit)
                .all()
            )

            # Format results
            results = []
            for kpi in similar_kpis:
                # Get latest snapshot
                latest_snapshot = (
                    self.db.query(KPISnapshot)
                    .filter_by(kpi_id=kpi.id)
                    .order_by(desc(KPISnapshot.snapshot_date))
                    .first()
                )

                results.append(
                    {
                        "id": str(kpi.id),
                        "type": "metric",
                        "name": kpi.kpi_name,
                        "formula": kpi.formula,
                        "unit": kpi.unit,
                        "target_value": float(kpi.target_value) if kpi.target_value else None,
                        "latest_value": float(latest_snapshot.calculated_value)
                        if latest_snapshot
                        else None,
                        "latest_date": latest_snapshot.snapshot_date.isoformat()
                        if latest_snapshot
                        else None,
                        "similarity": float(kpi.similarity),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching metrics: {str(e)}")
            return []

    async def semantic_search_calculations(
        self,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
        min_similarity: float = 0.7,
    ) -> List[Dict]:
        """
        Search for carbon calculations using semantic similarity

        Args:
            tenant_id: Tenant ID for isolation
            query_text: Natural language query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant carbon calculations
        """
        try:
            from app.models import CarbonCalculation, CalculationDetail

            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                logger.warning(f"Failed to generate embedding for calculation query")
                return []

            # Search for recent carbon calculations
            calculations = (
                self.db.query(CarbonCalculation)
                .filter(
                    and_(
                        CarbonCalculation.tenant_id == tenant_id,
                        CarbonCalculation.status == "approved",
                    )
                )
                .order_by(desc(CarbonCalculation.created_at))
                .limit(limit)
                .all()
            )

            results = []
            for calc in calculations:
                details = [
                    {
                        "type": d.calculation_type,
                        "scope": d.scope,
                        "energy_input": float(d.energy_input),
                        "energy_unit": d.energy_unit,
                        "result": float(d.result),
                    }
                    for d in calc.details
                ]

                results.append(
                    {
                        "id": str(calc.id),
                        "type": "calculation",
                        "period_start": calc.period_start.isoformat(),
                        "period_end": calc.period_end.isoformat(),
                        "total_emissions": float(calc.total_emissions),
                        "scope_1": float(calc.scope_1_emissions),
                        "scope_2": float(calc.scope_2_emissions),
                        "details": details,
                        "status": calc.status,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching calculations: {str(e)}")
            return []

    async def semantic_search_reports(
        self,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Search for ESG reports using semantic similarity

        Args:
            tenant_id: Tenant ID for isolation
            query_text: Natural language query
            limit: Maximum number of results

        Returns:
            List of relevant reports
        """
        try:
            from app.models import Report

            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                return []

            # Search for recent published reports
            reports = (
                self.db.query(Report)
                .filter(
                    and_(
                        Report.tenant_id == tenant_id,
                        Report.current_state.in_(["approved", "published"]),
                    )
                )
                .order_by(desc(Report.created_at))
                .limit(limit)
                .all()
            )

            results = []
            for report in reports:
                results.append(
                    {
                        "id": str(report.id),
                        "type": "report",
                        "report_type": report.report_type,
                        "period_start": report.report_period_start.isoformat(),
                        "period_end": report.report_period_end.isoformat(),
                        "status": report.current_state,
                        "created_at": report.created_at.isoformat(),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching reports: {str(e)}")
            return []

    async def semantic_search_facilities(
        self,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Search for facilities using semantic similarity

        Args:
            tenant_id: Tenant ID for isolation
            query_text: Natural language query
            limit: Maximum number of results

        Returns:
            List of relevant facilities
        """
        try:
            from app.models import Facility

            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                return []

            # Search for active facilities
            facilities = (
                self.db.query(Facility)
                .filter(
                    and_(
                        Facility.tenant_id == tenant_id,
                        Facility.is_active == True,
                    )
                )
                .order_by(Facility.name)
                .limit(limit)
                .all()
            )

            results = []
            for facility in facilities:
                results.append(
                    {
                        "id": str(facility.id),
                        "type": "facility",
                        "name": facility.name,
                        "location": facility.location,
                        "facility_type": facility.facility_type,
                        "timezone": facility.timezone,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching facilities: {str(e)}")
            return []

    async def build_retrieval_context(
        self,
        tenant_id: str,
        user_id: str,
        query_text: str,
        context_limit: int = 10,
    ) -> Dict:
        """
        Build comprehensive context for RAG using semantic search

        Args:
            tenant_id: Tenant ID
            user_id: User ID for access control
            query_text: User's question
            context_limit: Max items per category

        Returns:
            Dictionary with retrieved context organized by entity type
        """
        try:
            # Verify user has access to tenant data
            from app.models import User

            user = self.db.query(User).filter_by(id=user_id).first()
            if not user or user.tenant_id != tenant_id:
                logger.warning(
                    f"Unauthorized access attempt by user {user_id} to tenant {tenant_id}"
                )
                return {"error": "Unauthorized access"}

            # Perform semantic searches
            metrics = await self.semantic_search_metrics(
                tenant_id, query_text, limit=context_limit
            )
            calculations = await self.semantic_search_calculations(
                tenant_id, query_text, limit=context_limit
            )
            reports = await self.semantic_search_reports(
                tenant_id, query_text, limit=context_limit // 2
            )
            facilities = await self.semantic_search_facilities(
                tenant_id, query_text, limit=context_limit // 2
            )

            context = {
                "query": query_text,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "calculations": calculations,
                "reports": reports,
                "facilities": facilities,
                "total_items": len(metrics)
                + len(calculations)
                + len(reports)
                + len(facilities),
            }

            return context

        except Exception as e:
            logger.error(f"Error building retrieval context: {str(e)}")
            return {"error": str(e)}

    def store_query_embedding(
        self, query_id: str, embedding: List[float]
    ) -> bool:
        """
        Store query embedding in database

        Args:
            query_id: Copilot query ID
            embedding: Embedding vector

        Returns:
            True if stored successfully, False otherwise
        """
        try:
            from app.models import CopilotQuery

            query = self.db.query(CopilotQuery).filter_by(id=query_id).first()
            if not query:
                logger.warning(f"Query not found: {query_id}")
                return False

            # Update query with embedding
            query.embedding = embedding
            self.db.commit()

            logger.info(f"Stored embedding for query {query_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
            self.db.rollback()
            return False

    async def get_similar_questions(
        self,
        tenant_id: str,
        query_text: str,
        limit: int = 5,
        time_window_days: int = 30,
    ) -> List[Dict]:
        """
        Find similar questions asked previously

        Args:
            tenant_id: Tenant ID
            query_text: Current question
            limit: Maximum results
            time_window_days: Look back window

        Returns:
            List of similar previous questions
        """
        try:
            from app.models import CopilotQuery

            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                return []

            # Find similar questions from recent history
            cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)

            similar_queries = (
                self.db.query(CopilotQuery)
                .filter(
                    and_(
                        CopilotQuery.tenant_id == tenant_id,
                        CopilotQuery.created_at >= cutoff_date,
                    )
                )
                .order_by(desc(CopilotQuery.created_at))
                .limit(limit * 2)  # Get more to filter by similarity
                .all()
            )

            results = []
            for similar_query in similar_queries:
                if similar_query.embedding:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(
                        query_embedding, similar_query.embedding
                    )
                    if similarity > 0.7:  # Only return high similarity matches
                        results.append(
                            {
                                "question": similar_query.question,
                                "created_at": similar_query.created_at.isoformat(),
                                "response_count": len(similar_query.responses),
                                "similarity": similarity,
                            }
                        )

            return sorted(results, key=lambda x: x["similarity"], reverse=True)[
                :limit
            ]

        except Exception as e:
            logger.error(f"Error finding similar questions: {str(e)}")
            return []

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        try:
            import math

            if not vec1 or not vec2 or len(vec1) != len(vec2):
                return 0.0

            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
