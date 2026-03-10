"""
Agent Logging Service (Sprint 12)

Provides audit trail functionality for agent operations:
- Log agent runs with inputs, tools, and outputs
- Track agent decisions with impact assessment
- Record guardrail violations
- Query audit trails by agent type, date range, etc.

All logging is append-only with immutable records.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models import AgentRun, AgentDecision, AgentGuardrailViolation

logger = logging.getLogger(__name__)


class AgentLoggerService:
    """Service for logging agent operations"""

    def __init__(self, db: Session):
        self.db = db

    def log_agent_run(
        self,
        tenant_id: UUID,
        agent_type: str,
        input_context: Dict[str, Any],
        tools_used: List[str],
        output_summary: Dict[str, Any],
        citations: List[str],
        confidence_score: Decimal,
        requires_approval: bool = False,
        user_id: Optional[UUID] = None,
        agent_version: Optional[str] = None,
        data_quality_score: Optional[Decimal] = None,
    ) -> str:
        """
        Log an agent run with complete execution context

        Args:
            tenant_id: Tenant that owns this agent run
            agent_type: Type of agent (carbon_agent, kpi_agent, etc.)
            input_context: Input parameters that triggered the agent
            tools_used: List of external tools/services called
            output_summary: Summary of output produced
            citations: List of source data IDs used
            confidence_score: 0.00-1.00 confidence in the result
            requires_approval: Does this action need approval?
            user_id: User who triggered the agent
            agent_version: Version of agent code
            data_quality_score: 0-100 score of data completeness

        Returns:
            run_id: UUID of the created agent run

        Raises:
            ValueError: If input validation fails
        """
        try:
            # Validate inputs
            if not agent_type:
                raise ValueError("agent_type is required")
            if not isinstance(confidence_score, (int, float, Decimal)):
                raise ValueError("confidence_score must be numeric")
            if not (0 <= float(confidence_score) <= 1):
                raise ValueError("confidence_score must be between 0 and 1")

            # Extract tenant context from input if provided
            context_tenant_id = input_context.get("tenant_id") if isinstance(input_context, dict) else None

            # Create agent run record (immutable)
            run = AgentRun(
                tenant_id=tenant_id,
                user_id=user_id,
                agent_type=agent_type,
                agent_version=agent_version,
                input_context=input_context,
                context_tenant_id=context_tenant_id,
                tools_used=tools_used,
                tool_call_count=len(tools_used) if tools_used else 0,
                output_summary=output_summary,
                citations=citations,
                confidence_score=confidence_score,
                data_quality_score=data_quality_score,
                requires_approval=requires_approval,
                status="completed",
            )

            self.db.add(run)
            self.db.flush()
            self.db.commit()

            logger.info(
                f"Agent run logged: {run.id} (type={agent_type}, confidence={confidence_score}, "
                f"requires_approval={requires_approval})"
            )
            return str(run.id)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log agent run: {str(e)}")
            raise

    def log_agent_decision(
        self,
        run_id: UUID,
        tenant_id: UUID,
        decision_type: str,
        action: str,
        impact_level: str,
        requires_approval: bool = False,
        action_entity_type: Optional[str] = None,
        action_entity_id: Optional[UUID] = None,
        impact_description: Optional[str] = None,
    ) -> str:
        """
        Log a decision made by an agent

        Args:
            run_id: Agent run this decision is part of
            tenant_id: Tenant context
            decision_type: Type of decision (CREATE_RECORD, MODIFY_DATA, TRIGGER_ALERT)
            action: Human-readable description of action
            impact_level: low, medium, high, critical
            requires_approval: Does this decision need approval?
            action_entity_type: Type of entity being acted on
            action_entity_id: ID of entity being acted on
            impact_description: Why this impact level was assigned

        Returns:
            decision_id: UUID of the created decision

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate impact level
            if impact_level not in ["low", "medium", "high", "critical"]:
                raise ValueError(f"Invalid impact_level: {impact_level}")

            # Create decision record
            decision = AgentDecision(
                agent_run_id=run_id,
                tenant_id=tenant_id,
                decision_type=decision_type,
                action=action,
                action_entity_type=action_entity_type,
                action_entity_id=action_entity_id,
                impact_level=impact_level,
                impact_description=impact_description,
                requires_approval=requires_approval,
                approval_status="pending" if requires_approval else "auto_approved",
                auto_approved=not requires_approval,
            )

            self.db.add(decision)
            self.db.flush()
            self.db.commit()

            logger.info(
                f"Agent decision logged: {decision.id} (type={decision_type}, "
                f"impact={impact_level}, requires_approval={requires_approval})"
            )
            return str(decision.id)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log agent decision: {str(e)}")
            raise

    def log_guardrail_violation(
        self,
        run_id: UUID,
        tenant_id: UUID,
        violation_type: str,
        description: str,
        severity: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        violation_data: Optional[Dict] = None,
    ) -> str:
        """
        Log a guardrail violation (immutable audit record)

        Args:
            run_id: Agent run that caused violation
            tenant_id: Tenant context
            violation_type: fabrication, access_control, approval_required, cross_tenant
            description: Detailed description of violation
            severity: low, medium, high, critical
            entity_type: Type of entity involved
            entity_id: ID of entity involved
            violation_data: Additional context about violation

        Returns:
            violation_id: UUID of the created violation record

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate inputs
            valid_types = ["fabrication", "access_control", "approval_required", "cross_tenant", "data_integrity"]
            if violation_type not in valid_types:
                raise ValueError(f"Invalid violation_type: {violation_type}")

            if severity not in ["low", "medium", "high", "critical"]:
                raise ValueError(f"Invalid severity: {severity}")

            # Create immutable violation record
            violation = AgentGuardrailViolation(
                agent_run_id=run_id,
                tenant_id=tenant_id,
                violation_type=violation_type,
                description=description,
                severity=severity,
                entity_type=entity_type,
                entity_id=entity_id,
                violation_data=violation_data or {},
                status="open",
                resolved=False,
            )

            self.db.add(violation)
            self.db.flush()
            self.db.commit()

            logger.warning(
                f"Guardrail violation recorded: {violation.id} (type={violation_type}, "
                f"severity={severity}, agent_run={run_id})"
            )
            return str(violation.id)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log guardrail violation: {str(e)}")
            raise

    def get_agent_audit_trail(
        self,
        tenant_id: UUID,
        agent_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Query agent audit trail with filtering

        Args:
            tenant_id: Tenant to query
            agent_type: Filter by agent type
            date_from: Start date for range query
            date_to: End date for range query
            status: Filter by status (completed, failed, pending_approval, etc.)
            limit: Maximum results to return

        Returns:
            List of agent run records with full details
        """
        try:
            query = self.db.query(AgentRun).filter_by(tenant_id=tenant_id)

            if agent_type:
                query = query.filter_by(agent_type=agent_type)

            if status:
                query = query.filter_by(status=status)

            if date_from:
                query = query.filter(AgentRun.created_at >= date_from)

            if date_to:
                query = query.filter(AgentRun.created_at <= date_to)

            runs = query.order_by(desc(AgentRun.created_at)).limit(limit).all()

            result = []
            for run in runs:
                result.append({
                    "run_id": str(run.id),
                    "agent_type": run.agent_type,
                    "agent_version": run.agent_version,
                    "input_context": run.input_context,
                    "tools_used": run.tools_used,
                    "output_summary": run.output_summary,
                    "citations": run.citations,
                    "confidence_score": float(run.confidence_score),
                    "data_quality_score": float(run.data_quality_score) if run.data_quality_score else None,
                    "requires_approval": run.requires_approval,
                    "status": run.status,
                    "approved_by": str(run.approved_by) if run.approved_by else None,
                    "approved_at": run.approved_at.isoformat() if run.approved_at else None,
                    "created_at": run.created_at.isoformat(),
                    "decisions": len(run.decisions),
                    "violations": len(run.violations),
                })

            return result

        except Exception as e:
            logger.error(f"Failed to query agent audit trail: {str(e)}")
            raise

    def get_agent_run(self, run_id: UUID, tenant_id: UUID) -> Optional[Dict]:
        """
        Get detailed information about a specific agent run

        Args:
            run_id: Run to retrieve
            tenant_id: Tenant context (for security)

        Returns:
            Full agent run details with decisions and violations, or None if not found
        """
        try:
            run = self.db.query(AgentRun).filter(
                and_(
                    AgentRun.id == run_id,
                    AgentRun.tenant_id == tenant_id
                )
            ).first()

            if not run:
                return None

            # Build full response with related data
            return {
                "run_id": str(run.id),
                "agent_type": run.agent_type,
                "agent_version": run.agent_version,
                "user_id": str(run.user_id) if run.user_id else None,
                "input_context": run.input_context,
                "tools_used": run.tools_used,
                "tool_call_count": run.tool_call_count,
                "output_summary": run.output_summary,
                "citations": run.citations,
                "referenced_entities": run.referenced_entities,
                "confidence_score": float(run.confidence_score),
                "data_quality_score": float(run.data_quality_score) if run.data_quality_score else None,
                "requires_approval": run.requires_approval,
                "status": run.status,
                "error_message": run.error_message,
                "approved_by": str(run.approved_by) if run.approved_by else None,
                "approved_at": run.approved_at.isoformat() if run.approved_at else None,
                "approval_notes": run.approval_notes,
                "created_at": run.created_at.isoformat(),
                "decisions": [
                    {
                        "decision_id": str(d.id),
                        "decision_type": d.decision_type,
                        "action": d.action,
                        "impact_level": d.impact_level,
                        "approval_status": d.approval_status,
                        "approved_at": d.approved_at.isoformat() if d.approved_at else None,
                    }
                    for d in run.decisions
                ],
                "violations": [
                    {
                        "violation_id": str(v.id),
                        "violation_type": v.violation_type,
                        "severity": v.severity,
                        "status": v.status,
                        "resolved": v.resolved,
                        "created_at": v.created_at.isoformat(),
                    }
                    for v in run.violations
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get agent run: {str(e)}")
            raise

    def approve_agent_run(
        self,
        run_id: UUID,
        tenant_id: UUID,
        approved_by: UUID,
        approval_notes: Optional[str] = None,
    ) -> bool:
        """
        Approve an agent run that was pending approval

        Args:
            run_id: Run to approve
            tenant_id: Tenant context
            approved_by: User approving
            approval_notes: Optional notes from approver

        Returns:
            True if approved successfully

        Raises:
            ValueError: If run not found or not pending approval
        """
        try:
            run = self.db.query(AgentRun).filter(
                and_(
                    AgentRun.id == run_id,
                    AgentRun.tenant_id == tenant_id
                )
            ).first()

            if not run:
                raise ValueError(f"Agent run {run_id} not found")

            if not run.requires_approval:
                raise ValueError(f"Agent run {run_id} does not require approval")

            # Update approval fields
            run.status = "approved"
            run.approved_by = approved_by
            run.approved_at = datetime.utcnow()
            run.approval_notes = approval_notes

            self.db.commit()

            logger.info(f"Agent run {run_id} approved by {approved_by}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to approve agent run: {str(e)}")
            raise

    def resolve_violation(
        self,
        violation_id: UUID,
        tenant_id: UUID,
        resolved_by: UUID,
        resolution_notes: str,
    ) -> bool:
        """
        Mark a guardrail violation as resolved

        Args:
            violation_id: Violation to resolve
            tenant_id: Tenant context
            resolved_by: User resolving
            resolution_notes: Resolution details

        Returns:
            True if resolved successfully
        """
        try:
            violation = self.db.query(AgentGuardrailViolation).filter(
                and_(
                    AgentGuardrailViolation.id == violation_id,
                    AgentGuardrailViolation.tenant_id == tenant_id
                )
            ).first()

            if not violation:
                raise ValueError(f"Violation {violation_id} not found")

            violation.resolved = True
            violation.status = "resolved"
            violation.resolved_by = resolved_by
            violation.resolved_at = datetime.utcnow()
            violation.resolution_notes = resolution_notes

            self.db.commit()

            logger.info(f"Violation {violation_id} resolved by {resolved_by}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to resolve violation: {str(e)}")
            raise

    def get_open_violations(
        self,
        tenant_id: UUID,
        severity: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get open (unresolved) guardrail violations

        Args:
            tenant_id: Tenant to query
            severity: Filter by severity (low, medium, high, critical)
            limit: Maximum results

        Returns:
            List of open violations
        """
        try:
            query = self.db.query(AgentGuardrailViolation).filter(
                and_(
                    AgentGuardrailViolation.tenant_id == tenant_id,
                    AgentGuardrailViolation.resolved == False
                )
            )

            if severity:
                query = query.filter_by(severity=severity)

            violations = query.order_by(
                desc(AgentGuardrailViolation.created_at)
            ).limit(limit).all()

            return [
                {
                    "violation_id": str(v.id),
                    "violation_type": v.violation_type,
                    "description": v.description,
                    "severity": v.severity,
                    "status": v.status,
                    "entity_type": v.entity_type,
                    "entity_id": str(v.entity_id) if v.entity_id else None,
                    "created_at": v.created_at.isoformat(),
                    "agent_run_id": str(v.agent_run_id),
                }
                for v in violations
            ]

        except Exception as e:
            logger.error(f"Failed to get open violations: {str(e)}")
            raise
