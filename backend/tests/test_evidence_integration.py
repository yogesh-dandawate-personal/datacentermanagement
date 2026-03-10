"""
Integration tests for Evidence API Routes

Tests:
- HTTP endpoints for upload, download, list, delete
- Request/response validation
- Error handling
- Authorization and tenant isolation
- File handling in multipart requests
"""

import pytest
import uuid
from io import BytesIO
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Tenant, User
from app.database import get_db
from app.auth.jwt_handler import create_access_token


@pytest.fixture
def test_client(db: Session):
    """Create test client with mocked database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def auth_token(demo_user: User):
    """Create auth token for test user"""
    return create_access_token(
        user_id=str(demo_user.id),
        tenant_id=str(demo_user.tenant_id),
        roles=["editor"],
    )


@pytest.fixture
def auth_headers(auth_token: str):
    """Create Authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_s3():
    """Mock S3 client for integration tests"""
    with patch("app.integrations.s3_client.S3Client") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance

        mock_instance.upload_file.return_value = (
            "tenants/test/evidence/test.pdf",
            "abc123def456",
            1024,
        )
        mock_instance.download_file.return_value = BytesIO(b"test content")
        mock_instance.get_presigned_url.return_value = "https://example.com/presigned"
        mock_instance.delete_file.return_value = True

        yield mock_instance


class TestEvidenceUploadEndpoint:
    """Test POST /evidence upload endpoint"""

    def test_upload_evidence_success(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        auth_headers: dict,
        mock_s3,
    ):
        """Test successful file upload"""
        file_content = b"test PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf"),
        }
        data = {
            "category": "audit",
            "name": "Test Audit",
            "description": "Test audit report",
        }

        response = test_client.post(
            f"/api/v1/tenants/{demo_tenant.id}/evidence",
            files=files,
            data=data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Audit"
        assert data["category"] == "audit"
        assert data["file_type"] == "pdf"

    def test_upload_evidence_missing_category(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        auth_headers: dict,
    ):
        """Test upload without required category"""
        files = {
            "file": ("test.pdf", BytesIO(b"content"), "application/pdf"),
        }

        response = test_client.post(
            f"/api/v1/tenants/{demo_tenant.id}/evidence",
            files=files,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_upload_evidence_unauthorized(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
    ):
        """Test upload without authorization"""
        files = {
            "file": ("test.pdf", BytesIO(b"content"), "application/pdf"),
        }
        data = {"category": "audit"}

        response = test_client.post(
            f"/api/v1/tenants/{demo_tenant.id}/evidence",
            files=files,
            data=data,
        )

        assert response.status_code == 401


class TestEvidenceListEndpoint:
    """Test GET /evidence list endpoint"""

    def test_list_evidence_empty(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        auth_headers: dict,
    ):
        """Test listing evidence when none exist"""
        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_evidence_with_pagination(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test listing evidence with pagination"""
        # Create evidence via service
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        for i in range(5):
            file_content = BytesIO(b"test content")
            service.upload_evidence(
                tenant_id=str(demo_tenant.id),
                file_content=file_content,
                file_name=f"test_{i}.pdf",
                category="audit",
                uploaded_by_id=str(demo_user.id),
            )

        # Test pagination
        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence?skip=0&limit=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3

    def test_list_evidence_by_category(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test listing evidence filtered by category"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"audit content"),
            file_name="audit.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )
        service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"policy content"),
            file_name="policy.pdf",
            category="policy",
            uploaded_by_id=str(demo_user.id),
        )

        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence?category=audit",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "audit"


class TestEvidenceDetailEndpoint:
    """Test GET /evidence/{id} detail endpoint"""

    def test_get_evidence_details(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test getting evidence details"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
            name="Test Evidence",
        )

        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(evidence.id)
        assert data["name"] == "Test Evidence"
        assert "versions" in data
        assert "links" in data

    def test_get_evidence_not_found(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        auth_headers: dict,
    ):
        """Test getting non-existent evidence"""
        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestEvidenceUpdateEndpoint:
    """Test PATCH /evidence/{id} update endpoint"""

    def test_update_evidence_metadata(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test updating evidence metadata"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
            name="Original Name",
        )

        response = test_client.patch(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}",
            data={
                "name": "Updated Name",
                "description": "New description",
                "category": "policy",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"
        assert data["category"] == "policy"


class TestEvidenceDeleteEndpoint:
    """Test DELETE /evidence/{id} delete endpoint"""

    def test_soft_delete_evidence(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test soft deleting evidence"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        response = test_client.delete(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Evidence deleted successfully"
        assert data["hard_delete"] is False

    def test_hard_delete_evidence(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test hard deleting evidence"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        response = test_client.delete(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}?hard_delete=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hard_delete"] is True


class TestEvidenceLinkEndpoint:
    """Test POST /evidence/{id}/link linking endpoint"""

    def test_link_evidence_to_metric(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test linking evidence to metric"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        metric_id = str(uuid.uuid4())
        response = test_client.post(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}/link",
            data={
                "linked_to_type": "metric",
                "linked_to_id": metric_id,
                "link_type": "supports",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["linked_to_type"] == "metric"
        assert data["linked_to_id"] == metric_id

    def test_link_evidence_to_report(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test linking evidence to report"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        report_id = str(uuid.uuid4())
        response = test_client.post(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}/link",
            data={
                "linked_to_type": "report",
                "linked_to_id": report_id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["linked_to_type"] == "report"


class TestEvidenceDownloadEndpoint:
    """Test GET /evidence/{id}/download endpoint"""

    def test_get_download_url(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test getting presigned download URL"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        response = test_client.get(
            f"/api/v1/tenants/{demo_tenant.id}/evidence/{evidence.id}/download-url",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert data["evidence_id"] == str(evidence.id)
        assert data["expires_in_seconds"] == 3600


class TestTenantIsolation:
    """Test tenant isolation in endpoints"""

    def test_cannot_access_other_tenant_evidence(
        self,
        test_client: TestClient,
        demo_tenant: Tenant,
        demo_user: User,
        auth_headers: dict,
        mock_s3,
        db: Session,
    ):
        """Test tenant isolation"""
        from app.services.evidence_service import EvidenceService

        service = EvidenceService(db, s3_client=mock_s3)
        evidence = service.upload_evidence(
            tenant_id=str(demo_tenant.id),
            file_content=BytesIO(b"test content"),
            file_name="test.pdf",
            category="audit",
            uploaded_by_id=str(demo_user.id),
        )

        other_tenant_id = str(uuid.uuid4())
        response = test_client.get(
            f"/api/v1/tenants/{other_tenant_id}/evidence/{evidence.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Tenant mismatch"
