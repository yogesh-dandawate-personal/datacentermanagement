"""
Tests for Agent Logger Service (Sprint 12)

Test Coverage:
- Agent run logging (6 tests)
- Agent decision logging (3 tests)
- Guardrail violation logging (3 tests)
- Audit trail retrieval (4 tests)
- Approval workflows (2 tests)
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import AgentRun, AgentDecision, AgentGuardrailViolation, Tenant, User
from app.services.agent_logger import AgentLoggerService


@pytest.fixture
def agent_logger(db: Session) -> AgentLoggerService:
    """Create logger service"""
    return AgentLoggerService(db)


class TestAgentRunLogging:
    """Tests for agent run logging"""

    def test_log_agent_run_success(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging a successful agent run"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            input_context={"metric_type": "scope_2", "time_period": "2026-02"},
            tools_used=["database_query", "factor_lookup"],
            output_summary={"calculation_id": str(uuid.uuid4()), "result": 45000},
            citations=["metric-123", "factor-456"],
            confidence_score=Decimal("0.95"),
        )

        assert run_id
        run = db.query(AgentRun).filter_by(id=uuid.UUID(run_id)).first()
        assert run is not None
        assert run.agent_type == "carbon_agent"
        assert run.confidence_score == Decimal("0.95")
        assert run.status == "completed"

    def test_log_agent_run_with_approval(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging agent run that requires approval"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="kpi_agent",
            input_context={"kpi_type": "PUE"},
            tools_used=["calculation_engine"],
            output_summary={"kpi_value": 1.2},
            citations=["meter-789"],
            confidence_score=Decimal("0.88"),
            requires_approval=True,
        )

        run = db.query(AgentRun).filter_by(id=uuid.UUID(run_id)).first()
        assert run.requires_approval is True
        assert run.status == "completed"

    def test_log_agent_run_invalid_confidence(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test that invalid confidence score is rejected"""
        with pytest.raises(ValueError, match="confidence_score must be between 0 and 1"):
            agent_logger.log_agent_run(
                tenant_id=demo_tenant.id,
                agent_type="agent",
                input_context={},
                tools_used=[],
                output_summary={},
                citations=[],
                confidence_score=Decimal("1.5"),  # Invalid!
            )

    def test_log_agent_run_missing_agent_type(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test that missing agent_type is rejected"""
        with pytest.raises(ValueError, match="agent_type is required"):
            agent_logger.log_agent_run(
                tenant_id=demo_tenant.id,
                agent_type="",  # Invalid!
                input_context={},
                tools_used=[],
                output_summary={},
                citations=[],
                confidence_score=Decimal("0.9"),
            )

    def test_log_agent_run_with_quality_score(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging agent run with data quality score"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="quality_agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.92"),
            data_quality_score=Decimal("87.5"),
        )

        run = db.query(AgentRun).filter_by(id=uuid.UUID(run_id)).first()
        assert run.data_quality_score == Decimal("87.5")

    def test_log_agent_run_with_user(self, db: Session, demo_tenant: Tenant, demo_user: User, agent_logger: AgentLoggerService):
        """Test logging agent run with user context"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="analysis_agent",
            input_context={"triggered_by": str(demo_user.id)},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.85"),
            user_id=demo_user.id,
        )

        run = db.query(AgentRun).filter_by(id=uuid.UUID(run_id)).first()
        assert run.user_id == demo_user.id


class TestAgentDecisionLogging:
    """Tests for agent decision logging"""

    def test_log_agent_decision_create_record(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging a CREATE decision"""
        # Create agent run first
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        # Log decision
        decision_id = agent_logger.log_agent_decision(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            decision_type="CREATE_RECORD",
            action="Create new carbon calculation",
            impact_level="high",
            requires_approval=True,
        )

        decision = db.query(AgentDecision).filter_by(id=uuid.UUID(decision_id)).first()
        assert decision is not None
        assert decision.decision_type == "CREATE_RECORD"
        assert decision.impact_level == "high"
        assert decision.requires_approval is True
        assert decision.approval_status == "pending"

    def test_log_agent_decision_auto_approved(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging a decision that is auto-approved"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        decision_id = agent_logger.log_agent_decision(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            decision_type="READ",
            action="Read telemetry data",
            impact_level="low",
            requires_approval=False,
        )

        decision = db.query(AgentDecision).filter_by(id=uuid.UUID(decision_id)).first()
        assert decision.requires_approval is False
        assert decision.approval_status == "auto_approved"
        assert decision.auto_approved is True

    def test_log_agent_decision_invalid_impact(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test that invalid impact level is rejected"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        with pytest.raises(ValueError, match="Invalid impact_level"):
            agent_logger.log_agent_decision(
                run_id=uuid.UUID(run_id),
                tenant_id=demo_tenant.id,
                decision_type="MODIFY",
                action="Modify data",
                impact_level="invalid",  # Invalid!
            )


class TestGuardrailViolationLogging:
    """Tests for guardrail violation logging"""

    def test_log_fabrication_violation(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging a fabrication violation"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        violation_id = agent_logger.log_guardrail_violation(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            violation_type="fabrication",
            description="Referenced non-existent metric ID: metric-999",
            severity="critical",
        )

        violation = db.query(AgentGuardrailViolation).filter_by(id=uuid.UUID(violation_id)).first()
        assert violation is not None
        assert violation.violation_type == "fabrication"
        assert violation.severity == "critical"
        assert violation.resolved is False
        assert violation.status == "open"

    def test_log_access_control_violation(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test logging an access control violation"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        violation_id = agent_logger.log_guardrail_violation(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            violation_type="access_control",
            description="Attempted cross-tenant data access",
            severity="high",
        )

        violation = db.query(AgentGuardrailViolation).filter_by(id=uuid.UUID(violation_id)).first()
        assert violation.violation_type == "access_control"

    def test_log_violation_invalid_type(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test that invalid violation type is rejected"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        with pytest.raises(ValueError, match="Invalid violation_type"):
            agent_logger.log_guardrail_violation(
                run_id=uuid.UUID(run_id),
                tenant_id=demo_tenant.id,
                violation_type="invalid_type",  # Invalid!
                description="Test",
                severity="high",
            )


class TestAuditTrailRetrieval:
    """Tests for querying audit trails"""

    def test_get_agent_audit_trail(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test retrieving agent audit trail"""
        # Create multiple runs
        run_id1 = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            input_context={},
            tools_used=["db"],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        run_id2 = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="kpi_agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.8"),
        )

        # Query all runs
        runs = agent_logger.get_agent_audit_trail(tenant_id=demo_tenant.id)
        assert len(runs) == 2

    def test_get_agent_audit_trail_filter_by_type(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test filtering audit trail by agent type"""
        agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="kpi_agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.8"),
        )

        runs = agent_logger.get_agent_audit_trail(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent"
        )
        assert len(runs) == 1
        assert runs[0]["agent_type"] == "carbon_agent"

    def test_get_agent_run_details(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test getting detailed agent run information"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            input_context={"metric_type": "scope_2"},
            tools_used=["db"],
            output_summary={"result": 45000},
            citations=["metric-123"],
            confidence_score=Decimal("0.95"),
        )

        # Log a decision
        agent_logger.log_agent_decision(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            decision_type="CREATE_RECORD",
            action="Create calculation",
            impact_level="high",
        )

        # Get full details
        details = agent_logger.get_agent_run(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
        )

        assert details is not None
        assert details["agent_type"] == "carbon_agent"
        assert details["confidence_score"] == 0.95
        assert len(details["decisions"]) == 1
        assert details["decisions"][0]["decision_type"] == "CREATE_RECORD"

    def test_get_open_violations(self, db: Session, demo_tenant: Tenant, agent_logger: AgentLoggerService):
        """Test retrieving open violations"""
        # Create runs with violations
        run_id1 = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        agent_logger.log_guardrail_violation(
            run_id=uuid.UUID(run_id1),
            tenant_id=demo_tenant.id,
            violation_type="fabrication",
            description="Test violation 1",
            severity="high",
        )

        run_id2 = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        agent_logger.log_guardrail_violation(
            run_id=uuid.UUID(run_id2),
            tenant_id=demo_tenant.id,
            violation_type="access_control",
            description="Test violation 2",
            severity="critical",
        )

        # Get open violations
        violations = agent_logger.get_open_violations(tenant_id=demo_tenant.id)
        assert len(violations) == 2


class TestApprovalWorkflow:
    """Tests for approval workflows"""

    def test_approve_agent_run(self, db: Session, demo_tenant: Tenant, demo_user: User, agent_logger: AgentLoggerService):
        """Test approving an agent run"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
            requires_approval=True,
        )

        # Approve
        success = agent_logger.approve_agent_run(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            approved_by=demo_user.id,
            approval_notes="Verified against source data",
        )

        assert success is True
        run = db.query(AgentRun).filter_by(id=uuid.UUID(run_id)).first()
        assert run.status == "approved"
        assert run.approved_by == demo_user.id
        assert run.approval_notes == "Verified against source data"

    def test_resolve_violation(self, db: Session, demo_tenant: Tenant, demo_user: User, agent_logger: AgentLoggerService):
        """Test resolving a violation"""
        run_id = agent_logger.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        violation_id = agent_logger.log_guardrail_violation(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            violation_type="fabrication",
            description="Test violation",
            severity="high",
        )

        # Resolve
        success = agent_logger.resolve_violation(
            violation_id=uuid.UUID(violation_id),
            tenant_id=demo_tenant.id,
            resolved_by=demo_user.id,
            resolution_notes="Fabricated entities removed",
        )

        assert success is True
        violation = db.query(AgentGuardrailViolation).filter_by(id=uuid.UUID(violation_id)).first()
        assert violation.resolved is True
        assert violation.status == "resolved"
        assert violation.resolved_by == demo_user.id
