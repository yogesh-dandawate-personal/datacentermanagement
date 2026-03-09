"""
Test suite for Compliance Reporting and Auditing Service

Tests:
- ComplianceReportService (5 tests)
- ReportSectionService (4 tests)
- AuditTrailService (3 tests)
- ComplianceTargetService (4 tests)
- BenchmarkingService (4 tests)
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    Organization,
    User,
    ComplianceReport,
    ReportSection,
    ComplianceAuditTrail,
    ComplianceTarget,
    ReportingBenchmark,
)
from app.services.reporting_service import (
    ComplianceReportService,
    AuditTrailService,
    ComplianceTargetService,
    BenchmarkingService,
)


@pytest.fixture
def reporting_test_data(db: Session):
    """Create test data for reporting tests"""
    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com",
    )
    db.add(tenant)
    db.flush()

    # Create user
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="user@example.com",
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.flush()

    # Create organization
    organization = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Test Organization",
        slug="test-org",
        hierarchy_level=0,
    )
    db.add(organization)
    db.commit()

    return {
        "tenant": tenant,
        "organization": organization,
        "user": user,
    }


# ============================================================================
# Test: Compliance Report Service
# ============================================================================


class TestComplianceReportService:
    """Tests for compliance report creation and management"""

    def test_create_report(self, db: Session, reporting_test_data):
        """Test creating a compliance report"""
        test_data = reporting_test_data

        service = ComplianceReportService(db)
        result = service.create_report(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="ghg_protocol",
            reporting_period="Q1",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )

        assert result["report_type"] == "ghg_protocol"
        assert result["fiscal_year"] == 2024
        assert result["status"] == "draft"

    def test_generate_report_data(self, db: Session, reporting_test_data):
        """Test generating report emissions data"""
        test_data = reporting_test_data

        service = ComplianceReportService(db)
        report_result = service.create_report(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="tcfd",
            reporting_period="annual",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )

        result = service.generate_report_data(
            report_id=uuid.UUID(report_result["id"]),
            scope_1=Decimal("1000"),
            scope_2=Decimal("500"),
            scope_3=Decimal("2000"),
        )

        assert result["scope_1"] == 1000
        assert result["scope_2"] == 500
        assert result["scope_3"] == 2000
        assert result["total_emissions"] == 3500

    def test_submit_report_for_approval(self, db: Session, reporting_test_data):
        """Test submitting report for approval"""
        test_data = reporting_test_data

        service = ComplianceReportService(db)
        report_result = service.create_report(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="sec_climate",
            reporting_period="Q2",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )

        submit_result = service.submit_for_approval(
            report_id=uuid.UUID(report_result["id"]),
            submitted_by=test_data["user"].id,
        )

        assert submit_result["status"] == "pending_review"
        assert submit_result["submitted_at"] is not None

    def test_approve_report(self, db: Session, reporting_test_data):
        """Test approving report"""
        test_data = reporting_test_data

        service = ComplianceReportService(db)
        report_result = service.create_report(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="custom",
            reporting_period="Q3",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )

        service.submit_for_approval(
            report_id=uuid.UUID(report_result["id"]),
            submitted_by=test_data["user"].id,
        )

        approve_result = service.approve_report(
            report_id=uuid.UUID(report_result["id"]),
            approved_by=test_data["user"].id,
        )

        assert approve_result["status"] == "approved"

    def test_get_report_history(self, db: Session, reporting_test_data):
        """Test retrieving report history"""
        test_data = reporting_test_data

        service = ComplianceReportService(db)
        for i in range(3):
            service.create_report(
                organization_id=test_data["organization"].id,
                tenant_id=test_data["tenant"].id,
                report_type="ghg_protocol",
                reporting_period=f"Q{i+1}",
                fiscal_year=2024,
                created_by=test_data["user"].id,
            )

        history = service.get_report_history(test_data["organization"].id)

        assert len(history) == 3
        assert all(r["report_type"] == "ghg_protocol" for r in history)


# ============================================================================
# Test: Report Section Service
# ============================================================================


class TestReportSectionService:
    """Tests for report sections"""

    def test_create_report_section(self, db: Session, reporting_test_data):
        """Test creating report section"""
        test_data = reporting_test_data

        # Create report
        report = ComplianceReport(
            id=uuid.uuid4(),
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="ghg_protocol",
            reporting_period="Q1",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )
        db.add(report)
        db.flush()

        # Create section
        section = ReportSection(
            id=uuid.uuid4(),
            report_id=report.id,
            section_name="executive_summary",
            content={"text": "Summary content"},
        )
        db.add(section)
        db.commit()

        assert section.section_name == "executive_summary"
        assert section.completion_percentage == 0

    def test_update_section_completion(self, db: Session, reporting_test_data):
        """Test updating section completion"""
        test_data = reporting_test_data

        report = ComplianceReport(
            id=uuid.uuid4(),
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="tcfd",
            reporting_period="annual",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )
        db.add(report)
        db.flush()

        section = ReportSection(
            id=uuid.uuid4(),
            report_id=report.id,
            section_name="methodology",
            content={"text": "Methodology"},
        )
        db.add(section)
        db.flush()

        section.completion_percentage = 75
        db.commit()

        assert section.completion_percentage == 75

    def test_review_section(self, db: Session, reporting_test_data):
        """Test reviewing report section"""
        test_data = reporting_test_data

        report = ComplianceReport(
            id=uuid.uuid4(),
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="sec_climate",
            reporting_period="Q2",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )
        db.add(report)
        db.flush()

        section = ReportSection(
            id=uuid.uuid4(),
            report_id=report.id,
            section_name="results",
            content={},
            requires_review=True,
        )
        db.add(section)
        db.flush()

        section.reviewed_by = test_data["user"].id
        section.reviewed_at = datetime.utcnow()
        section.review_notes = "Approved"
        db.commit()

        assert section.reviewed_at is not None

    def test_multiple_sections_per_report(self, db: Session, reporting_test_data):
        """Test multiple sections in report"""
        test_data = reporting_test_data

        report = ComplianceReport(
            id=uuid.uuid4(),
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="ghg_protocol",
            reporting_period="Q3",
            fiscal_year=2024,
            created_by=test_data["user"].id,
        )
        db.add(report)
        db.flush()

        sections = []
        for name in ["summary", "methodology", "results"]:
            section = ReportSection(
                id=uuid.uuid4(),
                report_id=report.id,
                section_name=name,
                content={},
            )
            sections.append(section)
            db.add(section)

        db.commit()

        assert len(sections) == 3


# ============================================================================
# Test: Audit Trail Service
# ============================================================================


class TestAuditTrailService:
    """Tests for audit trail tracking"""

    def test_log_action(self, db: Session, reporting_test_data):
        """Test logging an action"""
        test_data = reporting_test_data

        service = AuditTrailService(db)
        result = service.log_action(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            action="CREATE",
            action_category="report",
            entity_type="compliance_report",
            entity_id=uuid.uuid4(),
            changed_by_user_id=test_data["user"].id,
            changed_values={"status": "draft"},
        )

        assert result["action"] == "CREATE"
        assert result["entity_type"] == "compliance_report"

    def test_get_audit_trail(self, db: Session, reporting_test_data):
        """Test retrieving audit trail"""
        test_data = reporting_test_data

        service = AuditTrailService(db)
        for i in range(3):
            service.log_action(
                organization_id=test_data["organization"].id,
                tenant_id=test_data["tenant"].id,
                action="UPDATE",
                action_category="report",
                entity_type="compliance_report",
                entity_id=uuid.uuid4(),
                changed_by_user_id=test_data["user"].id,
                changed_values={"field": f"value{i}"},
            )

        trail = service.get_audit_trail(test_data["organization"].id, days=30)

        assert len(trail) == 3
        assert all(e["action"] == "UPDATE" for e in trail)

    def test_generate_compliance_certificate(self, db: Session, reporting_test_data):
        """Test generating compliance certificate"""
        test_data = reporting_test_data

        # Create approved report
        report = ComplianceReport(
            id=uuid.uuid4(),
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            report_type="ghg_protocol",
            reporting_period="annual",
            fiscal_year=2024,
            created_by=test_data["user"].id,
            status="approved",
            approved_by=test_data["user"].id,
            approved_at=datetime.utcnow(),
            scope_1_emissions=Decimal("1000"),
            scope_2_emissions=Decimal("500"),
            scope_3_emissions=Decimal("2000"),
        )
        db.add(report)
        db.commit()

        service = AuditTrailService(db)
        cert = service.generate_compliance_certificate(test_data["organization"].id, report.id)

        assert cert["status"] == "valid"
        assert cert["total_emissions_mtco2e"] == 3500


# ============================================================================
# Test: Compliance Target Service
# ============================================================================


class TestComplianceTargetService:
    """Tests for compliance targets"""

    def test_set_target(self, db: Session, reporting_test_data):
        """Test setting a compliance target"""
        test_data = reporting_test_data

        service = ComplianceTargetService(db)
        result = service.set_target(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            target_name="Net Zero 2030",
            target_type="net_zero",
            baseline_year=2020,
            baseline_value=Decimal("10000"),
            target_year=2030,
            target_value=Decimal("0"),
        )

        assert result["target_name"] == "Net Zero 2030"
        assert result["status"] == "on_track"

    def test_track_progress(self, db: Session, reporting_test_data):
        """Test tracking target progress"""
        test_data = reporting_test_data

        service = ComplianceTargetService(db)
        target_result = service.set_target(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            target_name="50% Reduction 2030",
            target_type="absolute_reduction",
            baseline_year=2020,
            baseline_value=Decimal("10000"),
            target_year=2030,
            target_value=Decimal("5000"),
        )

        progress = service.track_progress(
            target_id=uuid.UUID(target_result["id"]),
            current_value=Decimal("7500"),
        )

        assert progress["progress_percentage"] == 50
        assert progress["status"] == "on_track"

    def test_get_target_status(self, db: Session, reporting_test_data):
        """Test getting target status"""
        test_data = reporting_test_data

        service = ComplianceTargetService(db)
        target_result = service.set_target(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            target_name="Test Target",
            target_type="intensity_reduction",
            baseline_year=2021,
            baseline_value=Decimal("100"),
            target_year=2025,
            target_value=Decimal("50"),
        )

        status = service.get_target_status(uuid.UUID(target_result["id"]))

        assert status["target_name"] == "Test Target"
        assert status["status"] == "on_track"

    def test_forecast_achievement(self, db: Session, reporting_test_data):
        """Test forecasting target achievement"""
        test_data = reporting_test_data

        service = ComplianceTargetService(db)
        target_result = service.set_target(
            organization_id=test_data["organization"].id,
            tenant_id=test_data["tenant"].id,
            target_name="Future Target",
            target_type="absolute_reduction",
            baseline_year=2023,
            baseline_value=Decimal("1000"),
            target_year=2025,
            target_value=Decimal("500"),
        )

        service.track_progress(
            target_id=uuid.UUID(target_result["id"]),
            current_value=Decimal("800"),
        )

        forecast = service.forecast_achievement(uuid.UUID(target_result["id"]))

        assert "will_achieve" in forecast
        assert "projected_progress" in forecast


# ============================================================================
# Test: Benchmarking Service
# ============================================================================


class TestBenchmarkingService:
    """Tests for benchmarking and comparison"""

    def test_calculate_benchmarks(self, db: Session, reporting_test_data):
        """Test calculating benchmarks"""
        test_data = reporting_test_data

        service = BenchmarkingService(db)
        result = service.calculate_benchmarks(
            tenant_id=test_data["tenant"].id,
            metric_name="pue",
            benchmark_value=Decimal("1.5"),
            organization_value=Decimal("1.8"),
        )

        assert result["metric_name"] == "pue"
        assert result["benchmark_value"] == 1.5
        assert result["percentile_rank"] == 120

    def test_get_peer_comparison(self, db: Session, reporting_test_data):
        """Test getting peer comparison"""
        test_data = reporting_test_data

        service = BenchmarkingService(db)
        service.calculate_benchmarks(
            tenant_id=test_data["tenant"].id,
            metric_name="cue",
            benchmark_value=Decimal("50"),
            organization_value=Decimal("45"),
        )

        comparison = service.get_peer_comparison(test_data["tenant"].id, "cue")

        assert comparison["metric_name"] == "cue"
        assert comparison["organization_value"] == 45.0

    def test_generate_insights(self, db: Session, reporting_test_data):
        """Test generating benchmark insights"""
        test_data = reporting_test_data

        service = BenchmarkingService(db)
        for metric in ["pue", "cue", "wue"]:
            service.calculate_benchmarks(
                tenant_id=test_data["tenant"].id,
                metric_name=metric,
                benchmark_value=Decimal("1.5"),
                organization_value=Decimal("1.2") if metric == "pue" else Decimal("60"),
            )

        insights = service.generate_insights(test_data["tenant"].id)

        assert insights["total_metrics"] > 0
        assert "recommendations" in insights

    def test_benchmark_tracking(self, db: Session, reporting_test_data):
        """Test tracking benchmarks over time"""
        test_data = reporting_test_data

        service = BenchmarkingService(db)
        for year in [2022, 2023, 2024]:
            benchmark = ReportingBenchmark(
                id=uuid.uuid4(),
                tenant_id=test_data["tenant"].id,
                benchmark_name="industry_average",
                metric_name="ere",
                benchmark_category="data_center",
                benchmark_value=Decimal("1.5"),
                organization_value=Decimal("1.4"),
                data_year=year,
            )
            db.add(benchmark)

        db.commit()

        comparison = service.get_peer_comparison(test_data["tenant"].id, "ere")

        assert comparison["benchmark_count"] >= 1
