"""
Executive Copilot Q&A Models

Implements Copilot conversation tracking and response management:
- CopilotQuery: User questions with embeddings for semantic search
- CopilotResponse: AI-generated answers with confidence and citations
- CopilotCitation: Evidence and source data linked to responses
- CopilotMessageHistory: Conversation context and memory
- CopilotFeedback: User feedback on response quality
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table, JSON, Integer, Text, Numeric, ARRAY, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import uuid
import enum

from app.models import Base

# Try to import pgvector Vector type, fallback to ARRAY(Float)
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class CopilotQuery(Base):
    """User question/query for copilot with embeddings"""
    __tablename__ = 'copilot_queries'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True)

    # Question content
    question = Column(Text, nullable=False)
    question_normalized = Column(Text)  # Cleaned/normalized version for search

    # Embedding vector for semantic search (1536 dimensions for OpenAI/Claude)
    # Uses pgvector if available, falls back to ARRAY(Numeric) otherwise
    embedding = Column(Vector(1536) if Vector else ARRAY(Numeric(10, 6)), nullable=True, index=True)

    # Query classification and metadata
    query_type = Column(String(50), nullable=True, index=True)  # metric, calculation, target, benchmark, etc.
    confidence_score = Column(Numeric(5, 4), default=0.5)  # 0-1 user confidence

    # Query status
    status = Column(String(50), default="processed", index=True)  # submitted, processing, processed, failed
    error_message = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    organization = relationship("Organization")
    responses = relationship("CopilotResponse", back_populates="query", cascade="all, delete-orphan")
    message_history = relationship("CopilotMessageHistory", back_populates="query", cascade="all, delete-orphan")
    feedback = relationship("CopilotFeedback", back_populates="query", cascade="all, delete-orphan")


class CopilotResponse(Base):
    """AI-generated response to copilot query"""
    __tablename__ = 'copilot_responses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('copilot_queries.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Response content
    answer = Column(Text, nullable=False)
    answer_summary = Column(String(500), nullable=True)  # Summary for list view

    # AI model information
    model_used = Column(String(100), nullable=True)  # claude-3-opus, claude-3-sonnet, etc.
    model_version = Column(String(50), nullable=True)

    # Quality metrics
    confidence = Column(Numeric(5, 4), nullable=False, default=0.5)  # 0-1, how confident is the answer
    completeness_score = Column(Numeric(5, 4), nullable=True)  # Data completeness (0-1)
    data_quality = Column(String(50), default="good", index=True)  # excellent, good, fair, poor
    has_fabrication = Column(Boolean, default=False, index=True)  # Flagged if answer referenced non-existent data

    # Processing information
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)

    # Response metadata
    response_type = Column(String(50), nullable=True, index=True)  # direct_answer, comparison, analysis, etc.
    language = Column(String(10), default="en")
    includes_visualizations = Column(Boolean, default=False)

    # Status tracking
    status = Column(String(50), default="completed", index=True)  # pending, completed, failed, rejected
    rejection_reason = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    query = relationship("CopilotQuery", back_populates="responses")
    tenant = relationship("Tenant")
    user = relationship("User")
    citations = relationship("CopilotCitation", back_populates="response", cascade="all, delete-orphan")
    feedback = relationship("CopilotFeedback", back_populates="response", cascade="all, delete-orphan")


class CopilotCitation(Base):
    """Citation/evidence linked to a copilot response"""
    __tablename__ = 'copilot_citations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey('copilot_responses.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)

    # Entity being cited
    entity_type = Column(String(100), nullable=False, index=True)  # metric, kpi, calculation, report, threshold, facility, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_name = Column(String(500), nullable=True)  # Name of the entity for quick display

    # Citation data snapshot (JSON to preserve state)
    entity_data = Column(JSON, nullable=False)  # {name: "...", value: "...", unit: "...", timestamp: "...", etc}

    # Citation context
    citation_type = Column(String(50), nullable=True, index=True)  # data_source, calculation_input, example, comparison, etc.
    citation_text = Column(Text, nullable=True)  # How this citation was used in the answer

    # Citation quality
    is_verified = Column(Boolean, default=False)  # Data verified against source
    confidence = Column(Numeric(5, 4), default=1.0)  # 0-1, confidence in this citation
    verification_status = Column(String(50), default="unverified", index=True)  # unverified, verified, questioned, disputed

    # Reference link
    source_url = Column(String(500), nullable=True)  # Link to view source data
    api_endpoint = Column(String(500), nullable=True)  # API endpoint to fetch full source

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    response = relationship("CopilotResponse", back_populates="citations")
    tenant = relationship("Tenant")


class CopilotMessageHistory(Base):
    """Conversation message history for context and memory"""
    __tablename__ = 'copilot_message_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('copilot_queries.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Message content
    role = Column(String(20), nullable=False, index=True)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=True)  # text, metadata, context, etc.

    # For assistant messages
    response_id = Column(UUID(as_uuid=True), ForeignKey('copilot_responses.id', ondelete='SET NULL'), nullable=True)

    # Context information (stored for audit)
    context_summary = Column(JSON, nullable=True)  # Context used for this message

    # Sequence and ordering
    sequence_number = Column(Integer, nullable=False)  # Order in conversation
    conversation_session_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Group messages in sessions

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    query = relationship("CopilotQuery", back_populates="message_history")
    tenant = relationship("Tenant")
    user = relationship("User")
    response = relationship("CopilotResponse")


class CopilotFeedback(Base):
    """User feedback on copilot responses for quality tracking"""
    __tablename__ = 'copilot_feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey('copilot_queries.id', ondelete='CASCADE'), nullable=False, index=True)
    response_id = Column(UUID(as_uuid=True), ForeignKey('copilot_responses.id', ondelete='CASCADE'), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Feedback rating
    rating = Column(Integer, nullable=True)  # 1-5 stars
    helpfulness = Column(String(20), nullable=True)  # very_helpful, helpful, neutral, unhelpful, very_unhelpful
    accuracy = Column(String(20), nullable=True)  # accurate, mostly_accurate, partially_accurate, inaccurate

    # Detailed feedback
    comment = Column(Text, nullable=True)
    issues = Column(ARRAY(String), nullable=True)  # List of issues identified: [missing_data, incorrect_calculation, fabrication, etc]

    # Issues details
    has_missing_data = Column(Boolean, default=False)
    has_incorrect_citation = Column(Boolean, default=False)
    has_fabrication = Column(Boolean, default=False)
    is_irrelevant = Column(Boolean, default=False)

    # Corrected information
    corrected_answer = Column(Text, nullable=True)  # User's corrected version

    # Feedback status
    status = Column(String(50), default="received", index=True)  # received, under_review, action_taken, dismissed
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    query = relationship("CopilotQuery", back_populates="feedback")
    response = relationship("CopilotResponse", back_populates="feedback")
    tenant = relationship("Tenant")
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class CopilotAccessLog(Base):
    """Audit log for all copilot access and queries"""
    __tablename__ = 'copilot_access_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    query_id = Column(UUID(as_uuid=True), ForeignKey('copilot_queries.id', ondelete='SET NULL'), nullable=True, index=True)

    # Action logging
    action = Column(String(100), nullable=False, index=True)  # ask_question, view_response, feedback_submitted, etc.
    action_category = Column(String(50), nullable=True, index=True)  # query, response, feedback, access, etc.

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Details (JSON for flexibility)
    details = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
    query = relationship("CopilotQuery")


class CopilotRateLimit(Base):
    """Rate limiting for copilot queries"""
    __tablename__ = 'copilot_rate_limits'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Rate limit window (hourly/daily tracking)
    window_type = Column(String(20), nullable=False, index=True)  # hourly, daily
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False, index=True)

    # Counts
    query_count = Column(Integer, default=0)
    response_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Limits
    query_limit = Column(Integer, default=100)  # Max queries per window
    token_limit = Column(Integer, default=100000)  # Max tokens per window
    is_exceeded = Column(Boolean, default=False, index=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")
