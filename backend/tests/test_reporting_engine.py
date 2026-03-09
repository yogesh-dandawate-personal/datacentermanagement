"""Tests for Reporting Engine"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Tenant, User, Report, ReportVersion, ReportSignature, ReportTemplate
from app.services.reporting_engine import (
    ReportGenerationService,
    ReportVersioningService,
    ReportSignatureService,
    ReportTemplateService,
)


@pytest.fixture
def reporting_engine_data(db: Session):
    """Test data for reporting engine"""
    tenant = Tenant(id=uuid.uuid4(), name="Test", slug="test", email="test@test.com")
    user = User(id=uuid.uuid4(), tenant_id=tenant.id, email="user@test.com", first_name="Test", last_name="User")
    db.add(tenant)
    db.add(user)
    db.flush()

    from app.models import Organization
    org = Organization(id=uuid.uuid4(), tenant_id=tenant.id, name="Test Org", slug="test-org", hierarchy_level=0)
    db.add(org)
    db.commit()
    return {"tenant": tenant, "user": user, "org": org}


class TestReportGeneration:
    def test_create_report(self, db: Session, reporting_engine_data):
        service = ReportGenerationService(db)
        result = service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="esg_monthly",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )
        assert result["type"] == "esg_monthly"

    def test_generate_report(self, db: Session, reporting_engine_data):
        service = ReportGenerationService(db)
        report_result = service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="emissions_summary",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )
        result = service.generate_report(uuid.UUID(report_result["id"]))
        assert result["status"] == "generated"

    def test_publish_report(self, db: Session, reporting_engine_data):
        service = ReportGenerationService(db)
        report_result = service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="kpi_summary",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )
        result = service.publish_report(uuid.UUID(report_result["id"]), reporting_engine_data["user"].id)
        assert result["state"] == "published"

    def test_export_report(self, db: Session, reporting_engine_data):
        service = ReportGenerationService(db)
        report_result = service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="esg_monthly",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )
        result = service.export_report(uuid.UUID(report_result["id"]), "pdf")
        assert result["format"] == "pdf"

    def test_list_reports(self, db: Session, reporting_engine_data):
        service = ReportGenerationService(db)
        for i in range(3):
            service.create_report(
                organization_id=reporting_engine_data["org"].id,
                tenant_id=reporting_engine_data["tenant"].id,
                report_type="esg_monthly",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30),
                created_by=reporting_engine_data["user"].id,
            )
        result = service.list_organization_reports(reporting_engine_data["org"].id)
        assert len(result) == 3


class TestReportVersioning:
    def test_create_version(self, db: Session, reporting_engine_data):
        gen_service = ReportGenerationService(db)
        report_result = gen_service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="esg_monthly",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )

        service = ReportVersioningService(db)
        result = service.create_version(
            report_id=uuid.UUID(report_result["id"]),
            version_reason="Initial version",
            versioned_by=reporting_engine_data["user"].id,
        )
        assert result["version_number"] == 1

    def test_get_versions(self, db: Session, reporting_engine_data):
        gen_service = ReportGenerationService(db)
        report_result = gen_service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="emissions_summary",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )

        report_id = uuid.UUID(report_result["id"])
        version_service = ReportVersioningService(db)
        for i in range(2):
            version_service.create_version(
                report_id=report_id,
                version_reason=f"Version {i}",
                versioned_by=reporting_engine_data["user"].id,
            )

        versions = version_service.get_report_versions(report_id)
        assert len(versions) == 2


class TestReportSignatures:
    def test_sign_report(self, db: Session, reporting_engine_data):
        gen_service = ReportGenerationService(db)
        report_result = gen_service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="kpi_summary",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )

        sig_service = ReportSignatureService(db)
        result = sig_service.sign_report(
            report_id=uuid.UUID(report_result["id"]),
            signer_id=reporting_engine_data["user"].id,
            signer_role="approver",
        )
        assert result["signer_role"] == "approver"

    def test_get_signatures(self, db: Session, reporting_engine_data):
        gen_service = ReportGenerationService(db)
        report_result = gen_service.create_report(
            organization_id=reporting_engine_data["org"].id,
            tenant_id=reporting_engine_data["tenant"].id,
            report_type="esg_monthly",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
            created_by=reporting_engine_data["user"].id,
        )

        sig_service = ReportSignatureService(db)
        sig_service.sign_report(
            report_id=uuid.UUID(report_result["id"]),
            signer_id=reporting_engine_data["user"].id,
            signer_role="reviewer",
        )

        result = sig_service.get_report_signatures(uuid.UUID(report_result["id"]))
        assert len(result) == 1


class TestReportTemplates:
    def test_create_template(self, db: Session, reporting_engine_data):
        service = ReportTemplateService(db)
        result = service.create_template(
            tenant_id=reporting_engine_data["tenant"].id,
            template_name="Monthly ESG",
            report_type="esg_monthly",
            template_config={"sections": ["summary", "emissions"]},
            created_by=reporting_engine_data["user"].id,
        )
        assert result["name"] == "Monthly ESG"

    def test_list_templates(self, db: Session, reporting_engine_data):
        service = ReportTemplateService(db)
        for i in range(2):
            service.create_template(
                tenant_id=reporting_engine_data["tenant"].id,
                template_name=f"Template {i}",
                report_type="esg_monthly",
                template_config={},
                created_by=reporting_engine_data["user"].id,
            )

        result = service.list_templates(reporting_engine_data["tenant"].id)
        assert len(result) >= 2
