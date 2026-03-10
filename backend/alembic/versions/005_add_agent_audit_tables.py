"""Add autonomous agent audit and decision tracking tables

Revision ID: 005_add_agent_audit_tables
Revises: 004_add_copilot_tables
Create Date: 2026-03-10 14:30:00.000000

This migration creates tables for tracking autonomous agent execution:
- agent_runs: Individual agent execution runs with context and decisions
- agent_decisions: Specific decisions made by agents with approval tracking
- agent_guardrail_violations: Violations of safety and business rules

Features:
- Comprehensive audit trail for agent actions
- JSONB storage for flexible input context and output summaries
- Tool usage tracking
- Confidence scoring and approval workflows
- Guardrail violation detection for safety compliance
- Multi-tenant isolation
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "005_add_agent_audit_tables"
down_revision: Union[str, None] = "004_add_copilot_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agent audit tables."""

    # Create agent_runs table for tracking agent executions
    op.create_table(
        'agent_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(100), nullable=False, comment='Type of agent: analyzer, optimizer, validator, compliance_checker, etc.'),
        sa.Column('run_id', sa.String(255), nullable=False, comment='External run identifier for correlation'),
        sa.Column('status', sa.String(50), nullable=False, server_default='in_progress', comment='in_progress, completed, failed, requires_approval'),
        sa.Column('input_context', postgresql.JSON(), nullable=True, comment='JSONB input context: entities, parameters, constraints'),
        sa.Column('tools_used', postgresql.JSON(), nullable=True, comment='JSONB list of tools/functions used during execution'),
        sa.Column('output_summary', postgresql.JSON(), nullable=True, comment='JSONB summary of results and recommendations'),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=True, comment='Overall confidence score 0-100'),
        sa.Column('citations', postgresql.JSON(), nullable=True, comment='JSONB array of sources/references used'),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error details if run failed'),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True, comment='Execution time in milliseconds'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'run_id', name='uq_agent_run_unique'),
        sa.Index('ix_agent_runs_tenant_id', 'tenant_id'),
        sa.Index('ix_agent_runs_agent_type', 'agent_type'),
        sa.Index('ix_agent_runs_created_at', 'created_at'),
        sa.Index('ix_agent_runs_status', 'status'),
        sa.Index('ix_agent_runs_requires_approval', 'requires_approval'),
        sa.Index('ix_agent_runs_composite', 'tenant_id', 'agent_type', 'created_at'),
    )

    # Create agent_decisions table for tracking specific decisions
    op.create_table(
        'agent_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('agent_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision_type', sa.String(100), nullable=False, comment='Type of decision: optimization, violation_flag, recommendation, alert, etc.'),
        sa.Column('action_entity_type', sa.String(100), nullable=True, comment='Type of entity affected by decision: facility, device, metric, etc.'),
        sa.Column('action_entity_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID of affected entity'),
        sa.Column('action', sa.Text(), nullable=False, comment='The decision/action: reduce_capacity, flag_anomaly, retire_credits, etc.'),
        sa.Column('impact_level', sa.String(50), nullable=False, comment='Impact level: low, medium, high, critical'),
        sa.Column('impact_description', sa.Text(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approval_status', sa.String(50), nullable=False, server_default='pending', comment='pending, approved, rejected'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_reason', sa.Text(), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('auto_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_approval_rule', sa.String(255), nullable=True),
        sa.Column('executed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('execution_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['agent_run_id'], ['agent_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rejected_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_agent_decisions_agent_run_id', 'agent_run_id'),
        sa.Index('ix_agent_decisions_tenant_id', 'tenant_id'),
        sa.Index('ix_agent_decisions_decision_type', 'decision_type'),
        sa.Index('ix_agent_decisions_approval_status', 'approval_status'),
        sa.Index('ix_agent_decisions_created_at', 'created_at'),
    )

    # Create agent_guardrail_violations table
    op.create_table(
        'agent_guardrail_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('agent_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violation_type', sa.String(100), nullable=False, comment='Type of violation: fabrication, access_control, approval_required, cross_tenant'),
        sa.Column('severity', sa.String(50), nullable=False, comment='Severity level: low, medium, high, critical'),
        sa.Column('description', sa.Text(), nullable=False, comment='What was violated and why'),
        sa.Column('entity_type', sa.String(100), nullable=True, comment='Type of entity involved: metric, factor, report'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID of entity involved'),
        sa.Column('violation_data', postgresql.JSON(), nullable=True, comment='Additional context'),
        sa.Column('status', sa.String(50), nullable=False, server_default='open', comment='open, acknowledged, resolved, escalated'),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('escalated_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['agent_run_id'], ['agent_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_agent_guardrail_violations_agent_run_id', 'agent_run_id'),
        sa.Index('ix_agent_guardrail_violations_tenant_id', 'tenant_id'),
        sa.Index('ix_agent_guardrail_violations_violation_type', 'violation_type'),
        sa.Index('ix_agent_guardrail_violations_severity', 'severity'),
        sa.Index('ix_agent_guardrail_violations_status', 'status'),
        sa.Index('ix_agent_guardrail_violations_created_at', 'created_at'),
        sa.Index('ix_agent_guardrail_violations_composite', 'tenant_id', 'severity', 'status'),
    )


def downgrade() -> None:
    """Drop agent audit tables."""
    op.drop_table('agent_guardrail_violations')
    op.drop_table('agent_decisions')
    op.drop_table('agent_runs')
