"""Add evidence repository tables for compliance and auditing

Revision ID: 003_add_evidence_tables
Revises: 002_add_password_auth
Create Date: 2026-03-10 14:00:00.000000

This migration creates tables for storing evidence documents:
- evidence: Main evidence document storage
- evidence_versions: Version history for evidence documents
- evidence_links: Links between evidence and other entities (metrics, reports, etc.)

Features:
- S3/MinIO document storage with integrity verification (SHA256)
- Version history tracking
- Soft delete support for audit trail preservation
- Multi-tenant isolation
- Comprehensive audit fields (created_by, uploaded_by)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "003_add_evidence_tables"
down_revision: Union[str, None] = "002_add_password_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create evidence tables."""

    # Create evidence table
    op.create_table(
        'evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, comment='Name/title of the evidence document'),
        sa.Column('category', sa.String(100), nullable=False, comment='Category: policy, audit, certification, report, test_result, etc.'),
        sa.Column('description', sa.Text(), nullable=True, comment='Detailed description of the evidence'),
        sa.Column('document_key', sa.String(500), nullable=False, comment='S3/MinIO object key for storage'),
        sa.Column('file_hash', sa.String(64), nullable=False, comment='SHA256 hash for integrity verification'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, comment='File size in bytes'),
        sa.Column('file_type', sa.String(50), nullable=True, comment='File type: pdf, xlsx, png, jpg, csv, doc, etc.'),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True, comment='User who uploaded the evidence'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='When the evidence was uploaded'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='Record creation timestamp'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, comment='User who created this record'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp for audit trail'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_evidence_tenant_id', 'tenant_id'),
        sa.Index('ix_evidence_category', 'category'),
        sa.Index('ix_evidence_created_at', 'created_at'),
        sa.Index('ix_evidence_document_key', 'document_key'),
    )

    # Create evidence_versions table for version history
    op.create_table(
        'evidence_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, comment='Sequential version number'),
        sa.Column('document_key', sa.String(500), nullable=False, comment='S3/MinIO object key for this version'),
        sa.Column('file_hash', sa.String(64), nullable=False, comment='SHA256 hash for this version'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, comment='File size in bytes'),
        sa.Column('change_reason', sa.String(255), nullable=True, comment='Reason for creating this version'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_evidence_versions_evidence_id', 'evidence_id'),
        sa.Index('ix_evidence_versions_tenant_id', 'tenant_id'),
        sa.Index('ix_evidence_versions_created_at', 'created_at'),
        sa.UniqueConstraint('evidence_id', 'version_number', name='uq_evidence_version_unique'),
    )

    # Create evidence_links table for linking evidence to other entities
    op.create_table(
        'evidence_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('linked_to_type', sa.String(50), nullable=False, comment='Type of linked entity: metric, report, calculation, kpi, carbon_credit, etc.'),
        sa.Column('linked_to_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID of the linked entity'),
        sa.Column('link_type', sa.String(50), nullable=False, server_default='supports', comment='Type of link: supports, references, validates, contradicts, etc.'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_evidence_links_evidence_id', 'evidence_id'),
        sa.Index('ix_evidence_links_tenant_id', 'tenant_id'),
        sa.Index('ix_evidence_links_linked_to_type', 'linked_to_type'),
        sa.Index('ix_evidence_links_linked_to_id', 'linked_to_id'),
        sa.Index('ix_evidence_links_composite', 'linked_to_type', 'linked_to_id'),
    )


def downgrade() -> None:
    """Drop evidence tables."""
    op.drop_table('evidence_links')
    op.drop_table('evidence_versions')
    op.drop_table('evidence')
