"""
Tests for Agent Guardrails Service (Sprint 12)

Test Coverage:
- Fabrication Detection (6 tests)
- Approval Gating (6 tests)
- Data Integrity (4 tests)
- Access Control (6 tests)
- Cross-Tenant Protection (2 tests)
- Comprehensive Validation (2 tests)
"""

import pytest
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import (
    Tenant, User, CarbonCalculation, EmissionFactor,
    KPIDefinition, Organization
)
from app.services.agent_guardrails import AgentGuardrailsService
from app.services.agent_logger import AgentLoggerService


@pytest.fixture
def guardrails(db: Session) -> AgentGuardrailsService:
    """Create guardrails service"""
    return AgentGuardrailsService(db)


@pytest.fixture
def logger_service(db: Session) -> AgentLoggerService:
    """Create logger service"""
    return AgentLoggerService(db)


@pytest.fixture
def demo_organization(db: Session, demo_tenant: Tenant) -> Organization:
    """Create demo organization for tests"""
    org = Organization(
        id=uuid.uuid4(),
        tenant_id=demo_tenant.id,
        name="Test Organization",
        slug="test-org",
        hierarchy_level=0,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


class TestFabricationDetection:
    """Tests for fabrication detection guardrail"""

    def test_check_fabrication_valid_citations(self, db: Session, demo_tenant: Tenant, demo_organization: Organization,
                                               guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test that valid citations pass fabrication check"""
        # Create a carbon calculation (valid entity)
        calc = CarbonCalculation(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            organization_id=demo_organization.id,
            period_start=None,
            period_end=None,
            status="draft",
        )
        db.add(calc)
        db.commit()

        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[str(calc.id)],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            citations=[str(calc.id)],
            referenced_entities={str(calc.id): "calculation"},
        )

        assert is_valid is True
        assert error is None

    def test_check_fabrication_invalid_citations(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                                 logger_service: AgentLoggerService):
        """Test that invalid citations are detected"""
        fake_id = str(uuid.uuid4())

        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[fake_id],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            citations=[fake_id],
            referenced_entities={fake_id: "calculation"},
        )

        assert is_valid is False
        assert "Fabrication detected" in error

    def test_check_fabrication_empty_citations(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                               logger_service: AgentLoggerService):
        """Test that empty citations always pass"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            citations=[],
            referenced_entities={},
        )

        assert is_valid is True
        assert error is None

    def test_check_fabrication_logs_violation(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                             logger_service: AgentLoggerService):
        """Test that fabrication violations are logged"""
        from app.models import AgentGuardrailViolation

        fake_id = str(uuid.uuid4())

        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[fake_id],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            citations=[fake_id],
            referenced_entities={fake_id: "calculation"},
        )

        # Check that violation was recorded
        violations = db.query(AgentGuardrailViolation).filter_by(
            agent_run_id=uuid.UUID(run_id)
        ).all()
        assert len(violations) == 1
        assert violations[0].violation_type == "fabrication"

    def test_check_fabrication_mixed_valid_invalid(self, db: Session, demo_tenant: Tenant, demo_organization: Organization,
                                                   guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test mixed valid and invalid citations"""
        # Create valid calculation
        calc = CarbonCalculation(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            organization_id=demo_organization.id,
            period_start=None,
            period_end=None,
            status="draft",
        )
        db.add(calc)
        db.commit()

        fake_id = str(uuid.uuid4())

        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[str(calc.id), fake_id],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            citations=[str(calc.id), fake_id],
            referenced_entities={},
        )

        assert is_valid is False
        assert fake_id in error

    def test_check_fabrication_cross_tenant(self, db: Session, guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test that cross-tenant entities are not valid"""
        # Create another tenant
        other_tenant = Tenant(
            id=uuid.uuid4(),
            name="Other Tenant",
            slug="other",
            email="other@example.com",
        )
        db.add(other_tenant)

        # Create organization for other tenant
        other_org = Organization(
            id=uuid.uuid4(),
            tenant_id=other_tenant.id,
            name="Other Org",
            slug="other-org",
            hierarchy_level=0,
        )
        db.add(other_org)

        # Create calculation in other tenant
        calc = CarbonCalculation(
            id=uuid.uuid4(),
            tenant_id=other_tenant.id,
            organization_id=other_org.id,
            period_start=None,
            period_end=None,
            status="draft",
        )
        db.add(calc)
        db.commit()

        # Try to reference it from first tenant
        first_tenant = Tenant(
            id=uuid.uuid4(),
            name="First Tenant",
            slug="first",
            email="first@example.com",
        )
        db.add(first_tenant)
        db.commit()

        run_id = logger_service.log_agent_run(
            tenant_id=first_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[str(calc.id)],
            confidence_score=Decimal("0.9"),
        )

        # Should fail - entity from different tenant
        is_valid, error = guardrails.check_fabrication(
            run_id=uuid.UUID(run_id),
            tenant_id=first_tenant.id,
            citations=[str(calc.id)],
            referenced_entities={},
        )

        assert is_valid is False


class TestApprovalGating:
    """Tests for approval gating guardrail"""

    def test_read_operations_never_require_approval(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                                    logger_service: AgentLoggerService):
        """Test that read operations never require approval"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        for action_type in ["READ", "ANALYZE", "QUERY"]:
            requires, reason = guardrails.check_approval_requirement(
                run_id=uuid.UUID(run_id),
                tenant_id=demo_tenant.id,
                action_type=action_type,
                impact_level="high",  # Even high impact
            )
            assert requires is False

    def test_data_modification_requires_approval(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                                  logger_service: AgentLoggerService):
        """Test that data modifications require approval"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        for action_type in ["CREATE", "MODIFY", "DELETE"]:
            requires, reason = guardrails.check_approval_requirement(
                run_id=uuid.UUID(run_id),
                tenant_id=demo_tenant.id,
                action_type=action_type,
                impact_level="low",
            )
            # DELETE always requires, others depend on impact
            if action_type == "DELETE" or action_type == "MODIFY":
                assert requires is True

    def test_high_impact_requires_approval(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                           logger_service: AgentLoggerService):
        """Test that high impact always requires approval"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        for impact in ["high", "critical"]:
            requires, reason = guardrails.check_approval_requirement(
                run_id=uuid.UUID(run_id),
                tenant_id=demo_tenant.id,
                action_type="CREATE",
                impact_level=impact,
            )
            assert requires is True

    def test_low_impact_auto_approved(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                      logger_service: AgentLoggerService):
        """Test that low impact is auto-approved"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        requires, reason = guardrails.check_approval_requirement(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            action_type="READ",
            impact_level="low",
        )
        assert requires is False

    def test_medium_impact_requires_review(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                           logger_service: AgentLoggerService):
        """Test that medium impact requires manager review"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        requires, reason = guardrails.check_approval_requirement(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            action_type="CREATE",
            impact_level="medium",
        )
        assert requires is True
        assert "Medium-impact" in reason


class TestDataIntegrity:
    """Tests for data integrity guardrails"""

    def test_cannot_modify_approved_calculation(self, db: Session, demo_tenant: Tenant, demo_organization: Organization,
                                                guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test that approved calculations cannot be modified"""
        # Create an approved calculation
        calc = CarbonCalculation(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            organization_id=demo_organization.id,
            period_start=None,
            period_end=None,
            status="approved",
        )
        db.add(calc)
        db.commit()

        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_data_integrity(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            target_entity_type="carbon_calculation",
            target_entity_id=calc.id,
            action_type="MODIFY",
        )

        assert is_valid is False
        assert "Cannot modify approved calculation" in error

    def test_create_operations_allowed(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                       logger_service: AgentLoggerService):
        """Test that CREATE operations are allowed"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_data_integrity(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            target_entity_type="carbon_calculation",
            action_type="CREATE",
        )

        assert is_valid is True
        assert error is None

    def test_delete_not_allowed(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                logger_service: AgentLoggerService):
        """Test that DELETE is not allowed for agents"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_data_integrity(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            target_entity_type="calculation",
            target_entity_id=uuid.uuid4(),
            action_type="DELETE",
        )

        assert is_valid is False
        assert "cannot delete" in error.lower()


class TestAccessControl:
    """Tests for access control guardrails"""

    def test_valid_tenant_access(self, db: Session, demo_tenant: Tenant, demo_user: User, guardrails: AgentGuardrailsService,
                                 logger_service: AgentLoggerService):
        """Test that valid tenant access is allowed"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_access_control(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            user_id=demo_user.id,
        )

        assert is_valid is True
        assert error is None

    def test_invalid_tenant(self, db: Session, guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test that invalid tenant is rejected"""
        fake_tenant_id = uuid.uuid4()

        run_id = logger_service.log_agent_run(
            tenant_id=uuid.uuid4(),
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_access_control(
            run_id=uuid.UUID(run_id),
            tenant_id=fake_tenant_id,
        )

        assert is_valid is False
        assert "not found" in error

    def test_inactive_tenant(self, db: Session, guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test that inactive tenant is rejected"""
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Inactive",
            slug="inactive",
            email="test@example.com",
            is_active=False,
        )
        db.add(tenant)
        db.commit()

        run_id = logger_service.log_agent_run(
            tenant_id=uuid.uuid4(),
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_access_control(
            run_id=uuid.UUID(run_id),
            tenant_id=tenant.id,
        )

        assert is_valid is False
        assert "inactive" in error


class TestCrossTenantProtection:
    """Tests for cross-tenant isolation"""

    def test_cross_tenant_operation_detected(self, db: Session, guardrails: AgentGuardrailsService,
                                             logger_service: AgentLoggerService):
        """Test that cross-tenant operations are detected"""
        tenant1 = Tenant(
            id=uuid.uuid4(),
            name="Tenant 1",
            slug="tenant1",
            email="t1@example.com",
        )
        tenant2 = Tenant(
            id=uuid.uuid4(),
            name="Tenant 2",
            slug="tenant2",
            email="t2@example.com",
        )
        db.add(tenant1)
        db.add(tenant2)
        db.commit()

        run_id = logger_service.log_agent_run(
            tenant_id=tenant1.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        # Try to access tenant2 from tenant1 context
        is_valid, error = guardrails.check_cross_tenant_isolation(
            run_id=uuid.UUID(run_id),
            agent_tenant_id=tenant1.id,
            input_context={"tenant_id": str(tenant2.id)},
        )

        assert is_valid is False
        assert "Cross-tenant" in error

    def test_same_tenant_allowed(self, db: Session, demo_tenant: Tenant, guardrails: AgentGuardrailsService,
                                 logger_service: AgentLoggerService):
        """Test that same tenant context is allowed"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        is_valid, error = guardrails.check_cross_tenant_isolation(
            run_id=uuid.UUID(run_id),
            agent_tenant_id=demo_tenant.id,
            input_context={"tenant_id": str(demo_tenant.id)},
        )

        assert is_valid is True
        assert error is None


class TestComprehensiveValidation:
    """Tests for comprehensive validation"""

    def test_validate_valid_action(self, db: Session, demo_tenant: Tenant, demo_user: User,
                                   guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test validation of a valid action"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={"tenant_id": str(demo_tenant.id)},
            tools_used=[],
            output_summary={},
            citations=[],
            confidence_score=Decimal("0.9"),
        )

        result = guardrails.validate_agent_action(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            action_type="READ",
            impact_level="low",
            citations=[],
            referenced_entities={},
            input_context={"tenant_id": str(demo_tenant.id)},
            user_id=demo_user.id,
        )

        assert result["is_valid"] is True
        assert result["checks"]["fabrication"]["passed"] is True
        assert result["checks"]["access_control"]["passed"] is True
        assert result["checks"]["cross_tenant"]["passed"] is True

    def test_validate_invalid_action(self, db: Session, demo_tenant: Tenant, demo_user: User,
                                     guardrails: AgentGuardrailsService, logger_service: AgentLoggerService):
        """Test validation of invalid action"""
        run_id = logger_service.log_agent_run(
            tenant_id=demo_tenant.id,
            agent_type="agent",
            input_context={},
            tools_used=[],
            output_summary={},
            citations=[str(uuid.uuid4())],  # Fabricated ID
            confidence_score=Decimal("0.9"),
        )

        result = guardrails.validate_agent_action(
            run_id=uuid.UUID(run_id),
            tenant_id=demo_tenant.id,
            agent_type="carbon_agent",
            action_type="CREATE",
            impact_level="high",
            citations=[str(uuid.uuid4())],  # Fabricated
            referenced_entities={},
            input_context={},
            user_id=demo_user.id,
        )

        assert result["is_valid"] is False
        assert result["checks"]["fabrication"]["passed"] is False
