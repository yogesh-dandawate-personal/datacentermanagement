"""Add AI Copilot tables for conversational assistance

Revision ID: 004_add_copilot_tables
Revises: 003_add_evidence_tables
Create Date: 2026-03-10 14:15:00.000000

This migration creates tables for AI Copilot functionality:
- copilot_queries: User questions/queries with vector embeddings
- copilot_responses: AI-generated responses with confidence scores
- copilot_citations: References used in response generation

Features:
- pgvector support for semantic search
- Embedding vectors for similarity matching
- Citation tracking for RAG (Retrieval-Augmented Generation)
- Multi-tenant isolation
- Audit trail with user attribution
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "004_add_copilot_tables"
down_revision: Union[str, None] = "003_add_evidence_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create copilot tables with pgvector support."""

    # Create pgvector extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create copilot_queries table
    op.create_table(
        'copilot_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question', sa.Text(), nullable=False, comment='The user question or query'),
        sa.Column('embedding', postgresql.ARRAY(sa.Float(), dimensions=2), nullable=True, comment='Vector embedding for semantic search'),
        sa.Column('context', postgresql.JSON(), nullable=True, comment='Context about the query (source, filters, etc.)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_copilot_queries_tenant_id', 'tenant_id'),
        sa.Index('ix_copilot_queries_user_id', 'user_id'),
        sa.Index('ix_copilot_queries_created_at', 'created_at'),
    )

    # Create copilot_responses table
    op.create_table(
        'copilot_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('query_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False, comment='The AI-generated response'),
        sa.Column('response_type', sa.String(50), nullable=False, server_default='text', comment='text, code, table, visualization, etc.'),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True, comment='Confidence score 0-100'),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false', comment='Whether response requires human review'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True, comment='User feedback on response quality'),
        sa.Column('feedback_score', sa.Integer(), nullable=True, comment='Feedback score -1 (bad), 0 (neutral), 1 (good)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['query_id'], ['copilot_queries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_copilot_responses_query_id', 'query_id'),
        sa.Index('ix_copilot_responses_tenant_id', 'tenant_id'),
        sa.Index('ix_copilot_responses_created_at', 'created_at'),
        sa.Index('ix_copilot_responses_requires_approval', 'requires_approval'),
    )

    # Create copilot_citations table for tracking sources
    op.create_table(
        'copilot_citations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False, comment='Type of source: document, metric, report, calculation, evidence, etc.'),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID of the source entity'),
        sa.Column('source_title', sa.String(255), nullable=True, comment='Human-readable title of the source'),
        sa.Column('source_url', sa.String(500), nullable=True, comment='URL or path to source if available'),
        sa.Column('relevance_score', sa.Numeric(5, 2), nullable=True, comment='How relevant this citation is 0-100'),
        sa.Column('quote', sa.Text(), nullable=True, comment='Direct quote from source used in response'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['response_id'], ['copilot_responses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_copilot_citations_response_id', 'response_id'),
        sa.Index('ix_copilot_citations_tenant_id', 'tenant_id'),
        sa.Index('ix_copilot_citations_source_type', 'source_type'),
    )


def downgrade() -> None:
    """Drop copilot tables."""
    op.drop_table('copilot_citations')
    op.drop_table('copilot_responses')
    op.drop_table('copilot_queries')
