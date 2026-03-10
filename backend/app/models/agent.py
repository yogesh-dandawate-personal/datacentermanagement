"""
Agent Audit Trail and Governance Models (Sprint 12)

Implements:
- AgentRun: Complete log of agent execution with inputs, tools, outputs
- AgentDecision: Records agent decisions with approval workflows
- AgentGuardrailViolation: Immutable audit trail of policy violations
- Agent action tracking with confidence scores and citations
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models import Base


class AgentRun(Base):
    """
    Complete audit trail of agent execution

    Tracks what an agent did, why it did it, and what it produced.
    Immutable record - cannot be modified after creation.
    """
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # What agent ran
    agent_type = Column(String(100), nullable=False, index=True)  # carbon_agent, kpi_agent, etc.
    agent_version = Column(String(50))  # Version of agent code that ran

    # Input context - what triggered the agent
    input_context = Column(JSON, nullable=False)  # {metric_type, time_period, user_id, etc.}
    context_tenant_id = Column(UUID(as_uuid=True), index=True)  # Which tenant context was used

    # Tools used during execution
    tools_used = Column(JSON, default=list)  # [database_query, factor_lookup, calculation_engine]
    tool_call_count = Column(Integer, default=0)

    # Output produced
    output_summary = Column(JSON, nullable=False)  # {calculation_id, result, unit, confidence}

    # Data lineage and source tracking
    citations = Column(JSON, default=list)  # [metric-electricity, factor-grid-mix] - source IDs
    referenced_entities = Column(JSON, default=dict)  # {metric_id: true, factor_id: true} for fabrication detection

    # Confidence and validation
    confidence_score = Column(Numeric(5, 2), nullable=False)  # 0.00 - 1.00, how confident is the result
    requires_approval = Column(Boolean, default=False)  # Does this action need human approval?
    data_quality_score = Column(Numeric(5, 2))  # 0-100, completeness of data used

    # Approval tracking
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text)

    # Status tracking
    status = Column(String(50), default="completed", index=True)  # pending_approval, approved, rejected, completed, failed
    error_message = Column(Text)  # If failed, what was the error

    # Immutable audit record
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    # Note: NO updated_at - these records are immutable

    __table_args__ = (
        Index('idx_agent_type_created', 'agent_type', 'created_at'),
        Index('idx_tenant_agent_created', 'tenant_id', 'agent_type', 'created_at'),
        Index('idx_status_requires_approval', 'status', 'requires_approval'),
    )

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])
    decisions = relationship("AgentDecision", back_populates="agent_run", cascade="all, delete-orphan")
    violations = relationship("AgentGuardrailViolation", back_populates="agent_run", cascade="all, delete-orphan")


class AgentDecision(Base):
    """
    Record of a decision made by an agent that requires tracking

    Examples:
    - Creating a calculation record
    - Modifying entity state
    - Triggering alerts
    - Any action that changes system state
    """
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Decision details
    decision_type = Column(String(100), nullable=False, index=True)  # CREATE_RECORD, MODIFY_DATA, TRIGGER_ALERT
    action = Column(Text, nullable=False)  # Human-readable action description
    action_entity_type = Column(String(100))  # What type of entity (calculation, credit, report)
    action_entity_id = Column(UUID(as_uuid=True), index=True)  # ID of entity being acted on

    # Impact assessment
    impact_level = Column(String(50), nullable=False, index=True)  # low, medium, high, critical
    impact_description = Column(Text)  # Why this impact level was assigned

    # Approval gating
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50), default="pending", index=True)  # pending, approved, rejected

    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_reason = Column(Text)

    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text)

    # Auto-approval rules
    auto_approved = Column(Boolean, default=False)  # True if approved by automated rule
    auto_approval_rule = Column(String(255))  # Name of rule that auto-approved

    # Execution tracking
    executed = Column(Boolean, default=False)  # Was this decision actually executed?
    executed_at = Column(DateTime, nullable=True)
    execution_error = Column(Text)

    # Immutable audit record
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_agent_run_decision_type', 'agent_run_id', 'decision_type'),
        Index('idx_impact_approval_status', 'impact_level', 'approval_status'),
        Index('idx_decision_created', 'created_at'),
    )

    # Relationships
    agent_run = relationship("AgentRun", back_populates="decisions")
    tenant = relationship("Tenant")
    approver = relationship("User", foreign_keys=[approved_by])
    rejector = relationship("User", foreign_keys=[rejected_by])


class AgentGuardrailViolation(Base):
    """
    Immutable record of guardrail violations

    Tracks when agents violate policies:
    - Attempting to use non-existent data (fabrication)
    - Crossing tenant boundaries
    - Performing unapproved high-impact actions
    - Violating access control rules
    """
    __tablename__ = "agent_guardrail_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Violation details
    violation_type = Column(String(100), nullable=False, index=True)  # fabrication, access_control, approval_required, cross_tenant
    description = Column(Text, nullable=False)  # What was violated and why

    # Context of violation
    entity_type = Column(String(100))  # Type of entity involved (metric, factor, report)
    entity_id = Column(UUID(as_uuid=True), index=True)  # ID of entity involved
    violation_data = Column(JSON, default=dict)  # Additional context

    # Severity and status
    severity = Column(String(50), nullable=False, index=True)  # low, medium, high, critical
    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved, escalated

    resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)

    # Escalation tracking
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    escalated_at = Column(DateTime, nullable=True)

    # Immutable - no modifications allowed after creation
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_violation_type_severity', 'violation_type', 'severity'),
        Index('idx_violation_status_created', 'status', 'created_at'),
        Index('idx_agent_run_violations', 'agent_run_id', 'violation_type'),
    )

    # Relationships
    agent_run = relationship("AgentRun", back_populates="violations")
    tenant = relationship("Tenant")
    resolver = relationship("User", foreign_keys=[resolved_by])
    escalation_user = relationship("User", foreign_keys=[escalated_to])
