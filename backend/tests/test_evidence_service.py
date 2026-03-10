"""
Unit tests for Evidence Service

Tests:
- Evidence upload with file validation
- Versioning on re-upload
- Linking to metrics and reports
- Soft delete functionality
- Access control and tenant isolation
- File integrity verification
"""

import pytest
import uuid
from io import BytesIO
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base, Tenant, User, Evidence, EvidenceVersion, EvidenceLink
from app.services.evidence_service import EvidenceService, EvidenceServiceError
from app.integrations.s3_client import S3Client, S3ClientError


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing"""
    client = Mock(spec=S3Client)
    client.upload_file = Mock(
        return_value=(
            "tenants/test-tenant/evidence/20260310_120000_test.pdf",
            "abc123def456",  # file hash
            1024,  # file size
        )
    )
    client.download_file = Mock(return_value=BytesIO(b"test content"))
    client.get_presigned_url = Mock(return_value="https://example.com/presigned-url")
    client.delete_file = Mock(return_value=True)
    client.verify_file_integrity = Mock(return_value=True)
    return client


@pytest.fixture
def evidence_service(db: Session, mock_s3_client):
    """Create Evidence Service with mocked S3"""
    return EvidenceService(db, s3_client=mock_s3_client)


class TestEvidenceUpload:
    """Test evidence upload functionality"""

    def test_upload_evidence_success(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
        mock_s3_client,
    ):
        """Test successful evidence upload"""
        file_content = BytesIO(b"test PDF content" * 100)
        file_name = "audit_report.pdf"

        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name=file_name,
            category="audit",
            uploaded_by_id=str(demo_user.id),
            name="Audit Report",
            description="Q1 2026 Audit Report",
        )

        assert evidence.id is not None
        assert evidence.tenant_id == demo_tenant.id
        assert evidence.name == "Audit Report"
        assert evidence.category == "audit"
        assert evidence.file_type == "pdf"
        assert evidence.file_hash == "abc123def456"
        assert evidence.file_size_bytes == 1024
        assert evidence.uploaded_by == demo_user.id
        assert evidence.created_by == demo_user.id

        # Verify S3 was called
        mock_s3_client.upload_file.assert_called_once()

    def test_upload_evidence_invalid_file_type(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test upload with invalid file type"""
        file_content = BytesIO(b"test content")
        file_name = "invalid_file.exe"

        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name=file_name,
                category="audit",
                uploaded_by_id=str(demo_user.id),
            )

        assert "File type not allowed" in str(exc_info.value)

    def test_upload_evidence_file_too_large(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
        mock_s3_client,
    ):
        """Test upload with file exceeding size limit"""
        mock_s3_client.upload_file.return_value = (
            "tenants/test-tenant/evidence/large.pdf",
            "hash123",
            200 * 1024 * 1024,  # 200 MB - exceeds 100 MB limit
        )

        file_content = BytesIO(b"test" * 1000)

        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name="large_file.pdf",
                category="report",
                uploaded_by_id=str(demo_user.id),
            )

        assert "File size exceeds limit" in str(exc_info.value)

    def test_upload_evidence_invalid_tenant(
        self,
        db: Session,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test upload with invalid tenant"""
        file_content = BytesIO(b"test content")

        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.upload_evidence(
                tenant_id=str(uuid.uuid4()),  # Non-existent tenant
                file_content=file_content,
                file_name="test.pdf",
                category="audit",
                uploaded_by_id=str(demo_user.id),
            )

        assert "Tenant not found" in str(exc_info.value)

    def test_upload_evidence_creates_version(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test that upload creates initial version record"""
        file_content = BytesIO(b"test content")

        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        # Check version was created
        versions = db.query(EvidenceVersion).filter_by(
            evidence_id=evidence.id
        ).all()

        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert versions[0].change_reason == "Initial upload"


class TestEvidenceDownload:
    """Test evidence download functionality"""

    def test_download_evidence_success(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test successful evidence download"""
        # First upload
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        # Then download
        downloaded_content, retrieved_evidence = evidence_service.download_evidence(
            evidence_id=str(evidence.id),
            tenant_id=str(demo_tenant.id),
        )

        assert retrieved_evidence.id == evidence.id
        assert retrieved_evidence.name == evidence.name

    def test_download_evidence_not_found(
        self,
        db: Session,
        demo_tenant: Tenant,
        evidence_service: EvidenceService,
    ):
        """Test download of non-existent evidence"""
        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.download_evidence(
                evidence_id=str(uuid.uuid4()),
                tenant_id=str(demo_tenant.id),
            )

        assert "Evidence not found" in str(exc_info.value)

    def test_download_evidence_tenant_isolation(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test tenant isolation on download"""
        # Upload evidence
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        # Try to download with wrong tenant
        other_tenant_id = str(uuid.uuid4())
        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.download_evidence(
                evidence_id=str(evidence.id),
                tenant_id=other_tenant_id,
            )

        assert "Tenant mismatch" in str(exc_info.value)


class TestEvidenceList:
    """Test evidence listing functionality"""

    def test_list_evidence_empty(
        self,
        db: Session,
        demo_tenant: Tenant,
        evidence_service: EvidenceService,
    ):
        """Test listing evidence when none exist"""
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id)
        )

        assert len(evidence_list) == 0
        assert total == 0

    def test_list_evidence_with_pagination(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test listing evidence with pagination"""
        # Create multiple evidence items
        for i in range(5):
            file_content = BytesIO(b"test content " * 10)
            evidence_service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name=f"test_{i}.pdf",
                category="audit",
                uploaded_by_id=str(demo_user.id),
            )

        # Test first page
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id),
            skip=0,
            limit=3,
        )

        assert len(evidence_list) == 3
        assert total == 5

        # Test second page
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id),
            skip=3,
            limit=3,
        )

        assert len(evidence_list) == 2
        assert total == 5

    def test_list_evidence_by_category(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test listing evidence filtered by category"""
        # Create evidence with different categories
        for category in ["audit", "policy", "certification"]:
            file_content = BytesIO(b"test content")
            evidence_service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name=f"test_{category}.pdf",
                category=category,
                uploaded_by_id=str(demo_user.id),
            )

        # Filter by category
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id),
            category="audit",
        )

        assert len(evidence_list) == 1
        assert total == 1
        assert evidence_list[0].category == "audit"

    def test_list_evidence_exclude_deleted(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test that soft-deleted evidence is excluded by default"""
        # Create and delete evidence
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        evidence_service.delete_evidence(
            evidence_id=str(evidence.id),
            tenant_id=str(demo_tenant.id),
            soft_delete=True,
        )

        # List should not include deleted
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id),
            include_deleted=False,
        )

        assert len(evidence_list) == 0
        assert total == 0

        # But should include when requested
        evidence_list, total = evidence_service.list_evidence(
            tenant_id=str(demo_tenant.id),
            include_deleted=True,
        )

        assert len(evidence_list) == 1
        assert evidence_list[0].deleted_at is not None


class TestEvidenceDelete:
    """Test evidence deletion functionality"""

    def test_soft_delete_evidence(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test soft delete (sets deleted_at)"""
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        deleted_evidence = evidence_service.delete_evidence(
            evidence_id=str(evidence.id),
            tenant_id=str(demo_tenant.id),
            deleted_by_id=str(demo_user.id),
            soft_delete=True,
        )

        assert deleted_evidence.deleted_at is not None

    def test_hard_delete_evidence(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
        mock_s3_client,
    ):
        """Test hard delete (removes from S3 and database)"""
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        result = evidence_service.delete_evidence(
            evidence_id=str(evidence.id),
            tenant_id=str(demo_tenant.id),
            deleted_by_id=str(demo_user.id),
            soft_delete=False,
        )

        assert result is None

        # Verify S3 delete was called
        mock_s3_client.delete_file.assert_called()

        # Verify evidence is gone from database
        with pytest.raises(EvidenceServiceError):
            evidence_service.download_evidence(
                evidence_id=str(evidence.id),
                tenant_id=str(demo_tenant.id),
            )


class TestEvidenceLinking:
    """Test evidence linking functionality"""

    def test_link_evidence_to_metric(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test linking evidence to a metric"""
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        metric_id = str(uuid.uuid4())
        link = evidence_service.link_to_metric(
            evidence_id=str(evidence.id),
            metric_id=metric_id,
            tenant_id=str(demo_tenant.id),
            created_by_id=str(demo_user.id),
        )

        assert link.evidence_id == evidence.id
        assert link.linked_to_type == "metric"
        assert link.linked_to_id == metric_id
        assert link.link_type == "supports"

    def test_link_evidence_to_report(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test linking evidence to a report"""
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        report_id = str(uuid.uuid4())
        link = evidence_service.link_to_report(
            evidence_id=str(evidence.id),
            report_id=report_id,
            tenant_id=str(demo_tenant.id),
            created_by_id=str(demo_user.id),
        )

        assert link.linked_to_type == "report"
        assert link.linked_to_id == report_id

    def test_get_evidence_for_report(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test retrieving all evidence linked to a report"""
        # Create evidence
        report_id = str(uuid.uuid4())
        evidence_ids = []

        for i in range(3):
            file_content = BytesIO(b"test content")
            evidence = evidence_service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name=f"test_{i}.pdf",
                category="audit",
                uploaded_by_id=str(demo_user.id),
            )
            evidence_ids.append(str(evidence.id))

            # Link to report
            evidence_service.link_to_report(
                evidence_id=str(evidence.id),
                report_id=report_id,
                tenant_id=str(demo_tenant.id),
            )

        # Retrieve linked evidence
        linked_evidence = evidence_service.get_evidence_for_report(
            report_id=report_id,
            tenant_id=str(demo_tenant.id),
        )

        assert len(linked_evidence) == 3


class TestEvidenceMetadata:
    """Test evidence metadata update functionality"""

    def test_update_evidence_metadata(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test updating evidence metadata"""
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
            name="Original Name",
        )

        updated_evidence = evidence_service.update_evidence_metadata(
            evidence_id=str(evidence.id),
            tenant_id=str(demo_tenant.id),
            name="Updated Name",
            description="New description",
            category="policy",
            updated_by_id=str(demo_user.id),
        )

        assert updated_evidence.name == "Updated Name"
        assert updated_evidence.description == "New description"
        assert updated_evidence.category == "policy"


class TestEvidenceTenantIsolation:
    """Test tenant isolation"""

    def test_tenant_cannot_access_other_tenant_evidence(
        self,
        db: Session,
        demo_tenant: Tenant,
        demo_user: User,
        evidence_service: EvidenceService,
    ):
        """Test that evidence is isolated by tenant"""
        # Create evidence in first tenant
        file_content = BytesIO(b"test content")
        evidence = evidence_service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=file_content,
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        # Try to access with different tenant ID
        other_tenant_id = str(uuid.uuid4())
        with pytest.raises(EvidenceServiceError) as exc_info:
            evidence_service.get_evidence_details(
                evidence_id=str(evidence.id),
                tenant_id=other_tenant_id,
            )

        assert "Tenant mismatch" in str(exc_info.value)
