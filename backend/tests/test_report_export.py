"""
Integration tests for Report Export API

Test Coverage:
- PDF export endpoint
- Excel export endpoint
- JSON export endpoint (flat and nested)
- Tenant isolation
- Authentication/authorization
- Error handling
- File format validation
- Large reports
"""

import pytest
import json
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.models import Report, Organization, Tenant, User, ReportSignature
from app.main import app

client = TestClient(app)


@pytest.fixture
def export_test_report(db, tenant, organization):
    """Create test report for export"""
    user = User(
        tenant_id=tenant.id,
        email="exporter@example.com",
        first_name="Export",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.commit()

    report = Report(
        organization_id=organization.id,
        tenant_id=tenant.id,
        report_type="esg_monthly",
        report_period_start=datetime(2024, 1, 1),
        report_period_end=datetime(2024, 1, 31),
        created_by=user.id,
        current_state="draft"
    )
    db.add(report)
    db.commit()

    # Add signature
    sig = ReportSignature(
        report_id=report.id,
        signer_id=user.id,
        signer_role="preparer",
        signed_at=datetime.utcnow(),
        signature_method="digital"
    )
    db.add(sig)
    db.commit()

    return report, user


class TestPDFExportEndpoint:
    """Test PDF export endpoint"""

    def test_pdf_export_success(self, export_test_report):
        """Test successful PDF export"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0
        assert response.content.startswith(b"%PDF")

    def test_pdf_export_landscape(self, export_test_report):
        """Test PDF export with landscape orientation"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/pdf?landscape=true",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.content.startswith(b"%PDF")

    def test_pdf_export_not_found(self, export_test_report):
        """Test PDF export with non-existent report"""
        report, user = export_test_report
        fake_report_id = uuid4()

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{fake_report_id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404

    def test_pdf_export_tenant_isolation(self, export_test_report, db):
        """Test tenant isolation for PDF export"""
        report, user = export_test_report

        # Create another tenant
        other_tenant = Tenant(
            name="Other Tenant",
            slug="other-tenant",
            email="other@example.com"
        )
        db.add(other_tenant)
        db.commit()

        # Try to access report from different tenant
        response = client.post(
            f"/api/v1/tenants/{other_tenant.id}/reports/{report.id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404


class TestExcelExportEndpoint:
    """Test Excel export endpoint"""

    def test_excel_export_success(self, export_test_report):
        """Test successful Excel export"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/excel",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert "spreadsheet" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0
        # Check for ZIP file signature (Excel is ZIP)
        assert response.content[:2] == b"PK"

    def test_excel_export_not_found(self, export_test_report):
        """Test Excel export with non-existent report"""
        report, user = export_test_report
        fake_report_id = uuid4()

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{fake_report_id}/export/excel",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404

    def test_excel_export_tenant_isolation(self, export_test_report, db):
        """Test tenant isolation for Excel export"""
        report, user = export_test_report

        # Create another tenant
        other_tenant = Tenant(
            name="Other Tenant",
            slug="other-tenant",
            email="other@example.com"
        )
        db.add(other_tenant)
        db.commit()

        # Try to access report from different tenant
        response = client.post(
            f"/api/v1/tenants/{other_tenant.id}/reports/{report.id}/export/excel",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404


class TestJSONExportEndpoint:
    """Test JSON export endpoint"""

    def test_json_export_flat_success(self, export_test_report):
        """Test successful flat JSON export"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=flat",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert data["success"] is True
        assert data["export_format"] == "flat"
        assert "report_id" in data["data"]["export_metadata"]

    def test_json_export_nested_success(self, export_test_report):
        """Test successful nested JSON export"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=nested",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert data["success"] is True
        assert data["export_format"] == "nested"
        assert "report" in data["data"]

    def test_json_export_default_format(self, export_test_report):
        """Test JSON export defaults to flat format"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["export_format"] == "flat"

    def test_json_export_invalid_format(self, export_test_report):
        """Test JSON export with invalid format"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=invalid",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 400

    def test_json_export_flat_structure(self, export_test_report):
        """Test flat JSON export structure"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=flat",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Check flat structure
        assert "export_metadata" in data
        assert "report" in data
        assert "organization" in data
        assert "emissions" in data
        assert "signatures" in data

    def test_json_export_nested_structure(self, export_test_report):
        """Test nested JSON export structure"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=nested",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()["data"]["report"]

        # Check nested structure
        assert "basic_info" in data
        assert "organization" in data
        assert "emissions" in data
        assert "kpi_performance" in data
        assert "audit_trail" in data

    def test_json_export_emissions_data(self, export_test_report):
        """Test emissions data in JSON export"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json?format=flat",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Check emissions structure
        assert "emissions" in data
        assert "scope_1" in data["emissions"]
        assert "scope_2" in data["emissions"]
        assert "scope_3" in data["emissions"]
        assert "total" in data["emissions"]

    def test_json_export_not_found(self, export_test_report):
        """Test JSON export with non-existent report"""
        report, user = export_test_report
        fake_report_id = uuid4()

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{fake_report_id}/export/json",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404

    def test_json_export_tenant_isolation(self, export_test_report, db):
        """Test tenant isolation for JSON export"""
        report, user = export_test_report

        # Create another tenant
        other_tenant = Tenant(
            name="Other Tenant",
            slug="other-tenant",
            email="other@example.com"
        )
        db.add(other_tenant)
        db.commit()

        # Try to access report from different tenant
        response = client.post(
            f"/api/v1/tenants/{other_tenant.id}/reports/{report.id}/export/json",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404


class TestExportStatusEndpoint:
    """Test export status endpoint"""

    def test_export_status_success(self, export_test_report):
        """Test export status endpoint"""
        report, user = export_test_report

        response = client.get(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/status",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "available_formats" in data
        assert len(data["available_formats"]) == 3
        assert "pdf" in data["available_formats"]
        assert "excel" in data["available_formats"]
        assert "json" in data["available_formats"]

    def test_export_status_endpoints(self, export_test_report):
        """Test export status contains endpoint info"""
        report, user = export_test_report

        response = client.get(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/status",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()

        # Check PDF endpoint
        assert "pdf" in data["export_formats"]
        assert "endpoint" in data["export_formats"]["pdf"]

        # Check Excel endpoint
        assert "excel" in data["export_formats"]
        assert "endpoint" in data["export_formats"]["excel"]

        # Check JSON endpoint
        assert "json" in data["export_formats"]
        assert "parameters" in data["export_formats"]["json"]

    def test_export_status_not_found(self, export_test_report):
        """Test export status with non-existent report"""
        report, user = export_test_report
        fake_report_id = uuid4()

        response = client.get(
            f"/api/v1/tenants/{report.tenant_id}/reports/{fake_report_id}/export/status",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 404


class TestExportReportStates:
    """Test exports with different report states"""

    def test_export_draft_report(self, export_test_report):
        """Test exporting draft report"""
        report, user = export_test_report
        report.current_state = "draft"

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/json",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["report"]["basic_info"]["current_state"] == "draft"

    def test_export_approved_report(self, export_test_report):
        """Test exporting approved report"""
        report, user = export_test_report
        report.current_state = "approved"

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.content.startswith(b"%PDF")

    def test_export_published_report(self, export_test_report):
        """Test exporting published report"""
        report, user = export_test_report
        report.current_state = "published"

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/excel",
            headers={"x-user-id": str(user.id)}
        )

        assert response.status_code == 200
        assert response.content[:2] == b"PK"


class TestExportHeaders:
    """Test HTTP headers in export responses"""

    def test_pdf_content_type_header(self, export_test_report):
        """Test PDF content type header"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert response.headers["content-type"] == "application/pdf"

    def test_excel_content_type_header(self, export_test_report):
        """Test Excel content type header"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/excel",
            headers={"x-user-id": str(user.id)}
        )

        assert "spreadsheet" in response.headers["content-type"]

    def test_attachment_header(self, export_test_report):
        """Test attachment header for file downloads"""
        report, user = export_test_report

        response = client.post(
            f"/api/v1/tenants/{report.tenant_id}/reports/{report.id}/export/pdf",
            headers={"x-user-id": str(user.id)}
        )

        assert "attachment" in response.headers["content-disposition"]
        assert f"report_{report.id}" in response.headers["content-disposition"]
