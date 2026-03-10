"""
Tests for PDF Report Generation Service

Test Coverage:
- PDF generation with all sections (cover, summary, emissions, KPI, evidence)
- Watermark application (draft/approved status)
- Signature inclusion
- Landscape/portrait orientation
- Error handling for missing reports
- Large dataset handling
- Missing data scenarios
"""

import pytest
from io import BytesIO
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.models import (
    Report, Organization, Tenant, User, Role,
    ReportSignature, KPIDefinition, KPISnapshot
)
from app.services.pdf_generator import PDFGenerator


@pytest.fixture
def pdf_generator(db):
    """Create PDF generator instance"""
    return PDFGenerator(db)


@pytest.fixture
def setup_report_data(db, tenant, organization):
    """Setup report with related data"""
    # Create users
    user1 = User(
        tenant_id=tenant.id,
        email="creator@example.com",
        first_name="John",
        last_name="Creator",
        is_active=True
    )
    user2 = User(
        tenant_id=tenant.id,
        email="approver@example.com",
        first_name="Jane",
        last_name="Approver",
        is_active=True
    )
    db.add_all([user1, user2])
    db.commit()

    # Create report
    report = Report(
        organization_id=organization.id,
        tenant_id=tenant.id,
        report_type="esg_monthly",
        report_period_start=datetime(2024, 1, 1),
        report_period_end=datetime(2024, 1, 31),
        created_by=user1.id,
        current_state="draft"
    )
    db.add(report)
    db.commit()

    # Create signatures
    sig1 = ReportSignature(
        report_id=report.id,
        signer_id=user1.id,
        signer_role="preparer",
        signed_at=datetime.utcnow(),
        signature_method="digital"
    )
    sig2 = ReportSignature(
        report_id=report.id,
        signer_id=user2.id,
        signer_role="approver",
        signed_at=datetime.utcnow(),
        signature_method="digital"
    )
    db.add_all([sig1, sig2])
    db.commit()

    return report, user1, user2


class TestPDFGenerationBasics:
    """Test basic PDF generation"""

    def test_pdf_generator_initialization(self, pdf_generator):
        """Test PDF generator initializes correctly"""
        assert pdf_generator.db is not None
        assert pdf_generator.styles is not None

    def test_custom_styles_setup(self, pdf_generator):
        """Test custom paragraph styles are created"""
        assert 'CustomTitle' in pdf_generator.styles
        assert 'SectionTitle' in pdf_generator.styles
        assert 'NormalText' in pdf_generator.styles
        assert 'EmphasisText' in pdf_generator.styles

    def test_generate_pdf_basic(self, pdf_generator, setup_report_data):
        """Test basic PDF generation with minimal data"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00")
        )

        assert isinstance(pdf_buffer, BytesIO)
        assert pdf_buffer.tell() == 0  # Position at start
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b"%PDF")  # PDF magic number

    def test_generate_pdf_with_metrics(self, pdf_generator, setup_report_data):
        """Test PDF generation with key metrics"""
        report, _, _ = setup_report_data

        key_metrics = {
            "pue": 1.45,
            "cue": 48.5,
            "wue": 1.8,
            "ere": 1.6
        }

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("150.50"),
            scope_2=Decimal("200.75"),
            scope_3=Decimal("500.25"),
            key_metrics=key_metrics
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_generate_pdf_with_evidence(self, pdf_generator, setup_report_data):
        """Test PDF generation with evidence links"""
        report, _, _ = setup_report_data

        evidence_links = [
            {
                "name": "Energy Audit Report",
                "uploaded_at": "2024-01-15",
                "type": "audit",
                "link": "https://example.com/evidence/1"
            },
            {
                "name": "Carbon Certification",
                "uploaded_at": "2024-02-01",
                "type": "certification",
                "link": "https://example.com/evidence/2"
            }
        ]

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            evidence_links=evidence_links
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")


class TestPDFWatermarks:
    """Test watermark functionality"""

    def test_pdf_draft_watermark(self, pdf_generator, setup_report_data):
        """Test draft status watermark"""
        report, _, _ = setup_report_data
        report.current_state = "draft"

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            report_status="draft"
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_approved_watermark(self, pdf_generator, setup_report_data):
        """Test approved status watermark"""
        report, _, _ = setup_report_data
        report.current_state = "approved"

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            report_status="approved"
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_published_watermark(self, pdf_generator, setup_report_data):
        """Test published status watermark"""
        report, _, _ = setup_report_data
        report.current_state = "published"

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            report_status="published"
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")


class TestPDFOrientations:
    """Test page orientation"""

    def test_pdf_portrait_orientation(self, pdf_generator, setup_report_data):
        """Test portrait orientation (default)"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            landscape_mode=False
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_landscape_orientation(self, pdf_generator, setup_report_data):
        """Test landscape orientation"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            landscape_mode=True
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")


class TestPDFErrorHandling:
    """Test error handling"""

    def test_pdf_missing_report(self, pdf_generator):
        """Test error when report not found"""
        with pytest.raises(ValueError) as exc_info:
            pdf_generator.generate_pdf(
                report_id=uuid4(),
                organization_id=uuid4()
            )
        assert "not found" in str(exc_info.value)

    def test_pdf_missing_organization(self, pdf_generator, setup_report_data, db):
        """Test error when organization not found"""
        report, _, _ = setup_report_data

        with pytest.raises(ValueError) as exc_info:
            pdf_generator.generate_pdf(
                report_id=report.id,
                organization_id=uuid4()
            )
        assert "not found" in str(exc_info.value)

    def test_pdf_missing_data_graceful(self, pdf_generator, setup_report_data):
        """Test PDF generation with missing optional data"""
        report, _, _ = setup_report_data

        # Should not raise error with None values
        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=None,
            scope_2=None,
            scope_3=None
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")


class TestPDFLargeDatasets:
    """Test handling of large datasets"""

    def test_pdf_with_many_signatures(self, pdf_generator, setup_report_data, db):
        """Test PDF with many signatures"""
        report, _, _ = setup_report_data

        # Add additional signatures
        for i in range(5):
            user = User(
                tenant_id=report.tenant_id,
                email=f"signer{i}@example.com",
                first_name=f"Signer",
                last_name=f"{i}",
                is_active=True
            )
            db.add(user)
            db.commit()

            sig = ReportSignature(
                report_id=report.id,
                signer_id=user.id,
                signer_role="reviewer",
                signed_at=datetime.utcnow(),
                signature_method="digital"
            )
            db.add(sig)
        db.commit()

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00")
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_with_many_evidence_items(self, pdf_generator, setup_report_data):
        """Test PDF with many evidence references"""
        report, _, _ = setup_report_data

        evidence_links = [
            {
                "name": f"Evidence Document {i}",
                "uploaded_at": f"2024-01-{(i % 28) + 1:02d}",
                "type": ["audit", "certification", "report", "record"][i % 4],
                "link": f"https://example.com/evidence/{i}"
            }
            for i in range(30)
        ]

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("100.00"),
            scope_2=Decimal("200.00"),
            scope_3=Decimal("300.00"),
            evidence_links=evidence_links
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")


class TestPDFEmissions:
    """Test emissions data formatting"""

    def test_pdf_zero_emissions(self, pdf_generator, setup_report_data):
        """Test PDF with zero emissions"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("0.00"),
            scope_2=Decimal("0.00"),
            scope_3=Decimal("0.00")
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_large_emissions(self, pdf_generator, setup_report_data):
        """Test PDF with large emission values"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("10000000.99"),
            scope_2=Decimal("20000000.50"),
            scope_3=Decimal("30000000.75")
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")

    def test_pdf_fractional_emissions(self, pdf_generator, setup_report_data):
        """Test PDF with fractional emission values"""
        report, _, _ = setup_report_data

        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report.id,
            organization_id=report.organization_id,
            scope_1=Decimal("123.456789"),
            scope_2=Decimal("234.567891"),
            scope_3=Decimal("345.678912")
        )

        assert isinstance(pdf_buffer, BytesIO)
        content = pdf_buffer.read()
        assert content.startswith(b"%PDF")
