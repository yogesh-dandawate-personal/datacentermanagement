# Evidence Repository Module - Sprint 12

## Overview

The Evidence Repository module provides a comprehensive system for managing compliance evidence documents with support for:

- **Document Upload/Download**: Secure file storage in S3/MinIO
- **Version Control**: Track document changes with version history
- **Evidence Linking**: Link evidence to metrics, reports, carbon calculations, and KPIs
- **Soft Delete**: Preserve audit trail while marking documents as deleted
- **Tenant Isolation**: Complete data isolation between tenants
- **File Integrity**: SHA256 hash verification for data integrity
- **Access Control**: JWT-based authentication and authorization

## Architecture

### Database Models

#### Evidence
Main document record with metadata:
- `id` (UUID): Primary key
- `tenant_id` (UUID): Tenant isolation
- `name` (String): Display name
- `category` (String): Classification (policy, audit, certification, report, test_result, etc.)
- `description` (Text): Detailed description
- `document_key` (String): S3/MinIO object key
- `file_hash` (String): SHA256 hash for integrity verification
- `file_size_bytes` (Integer): File size in bytes
- `file_type` (String): File type (pdf, xlsx, png, jpg, csv, doc, docx)
- `uploaded_by` (UUID): User who uploaded
- `uploaded_at` (DateTime): When uploaded
- `created_at` (DateTime): Record creation
- `created_by` (UUID): Who created record
- `deleted_at` (DateTime, nullable): Soft delete timestamp

**Relationships:**
- `versions`: List of EvidenceVersion records
- `links`: List of EvidenceLink records

#### EvidenceVersion
Version history for documents:
- `id` (UUID): Primary key
- `evidence_id` (UUID): Foreign key to Evidence
- `tenant_id` (UUID): Tenant isolation
- `version_number` (Integer): Sequential version
- `document_key` (String): S3 key for this version
- `file_hash` (String): SHA256 hash for this version
- `file_size_bytes` (Integer): Size of this version
- `change_reason` (String): Why version was created
- `created_at` (DateTime): Creation timestamp
- `created_by` (UUID): Who created this version

**Key Feature:** Unique constraint on (evidence_id, version_number) ensures one record per version.

#### EvidenceLink
Linking evidence to other entities:
- `id` (UUID): Primary key
- `evidence_id` (UUID): Foreign key to Evidence
- `tenant_id` (UUID): Tenant isolation
- `linked_to_type` (String): Type of linked entity (metric, report, calculation, kpi, carbon_credit, etc.)
- `linked_to_id` (UUID): ID of linked entity
- `link_type` (String): Type of relationship (supports, references, validates, contradicts, etc.)
- `created_at` (DateTime): Creation timestamp
- `created_by` (UUID): Who created the link

### S3/MinIO Integration

The `S3Client` wrapper (`app/integrations/s3_client.py`) provides:

**Features:**
- Automatic bucket creation
- Presigned URL generation (default 1 hour)
- SHA256 file hash calculation
- Multi-tenant isolation via path structure: `tenants/{tenant_id}/evidence/{timestamp}_{filename}`
- Support for both AWS S3 and MinIO endpoints
- Comprehensive error handling

**Configuration (Environment Variables):**
```bash
# S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1  # Optional, defaults to us-east-1
S3_BUCKET_NAME=evidence-repository  # Optional

# MinIO Configuration (optional, overrides S3)
MINIO_ENDPOINT_URL=http://localhost:9000
```

**Methods:**
- `upload_file()`: Upload file, returns (document_key, file_hash, file_size_bytes)
- `download_file()`: Get file content as BinaryIO
- `get_presigned_url()`: Generate signed URL for direct download
- `delete_file()`: Remove file from storage
- `verify_file_integrity()`: Verify SHA256 hash
- `is_healthy()`: Check S3 connectivity

### Service Layer

The `EvidenceService` class (`app/services/evidence_service.py`) provides business logic:

**Core Methods:**

```python
# Upload
upload_evidence(
    tenant_id: str,
    file_content: BinaryIO,
    file_name: str,
    category: str,
    uploaded_by_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Evidence

# Download
download_evidence(evidence_id: str, tenant_id: str) -> Tuple[BinaryIO, Evidence]

# List with pagination and filtering
list_evidence(
    tenant_id: str,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
) -> Tuple[List[Evidence], int]

# Get details with versions and links
get_evidence_details(evidence_id: str, tenant_id: str) -> Dict

# Update metadata
update_evidence_metadata(
    evidence_id: str,
    tenant_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    updated_by_id: Optional[str] = None,
) -> Evidence

# Delete (soft by default)
delete_evidence(
    evidence_id: str,
    tenant_id: str,
    deleted_by_id: Optional[str] = None,
    soft_delete: bool = True,
) -> Evidence

# Link to entities
link_evidence(
    evidence_id: str,
    linked_to_type: str,
    linked_to_id: str,
    tenant_id: str,
    link_type: str = "supports",
    created_by_id: Optional[str] = None,
) -> EvidenceLink

link_to_metric(evidence_id: str, metric_id: str, tenant_id: str, ...) -> EvidenceLink
link_to_report(evidence_id: str, report_id: str, tenant_id: str, ...) -> EvidenceLink

# Get evidence for report
get_evidence_for_report(report_id: str, tenant_id: str) -> List[Evidence]

# Get presigned URL
get_presigned_download_url(evidence_id: str, tenant_id: str, ...) -> str
```

**Features:**
- Automatic versioning on upload (always creates version 1 for new documents)
- Tenant isolation enforcement on all operations
- Audit logging for all CRUD operations
- File validation (type and size)
- Duplicate link prevention

### API Routes

All endpoints require JWT authentication via `Authorization: Bearer {token}` header.

#### Upload Evidence
```
POST /api/v1/tenants/{tenant_id}/evidence
```

**Request:** Multipart form data
```
file: (binary)
category: (string, required)  # policy, audit, certification, report, test_result
name: (string, optional)
description: (string, optional)
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Audit Report",
  "category": "audit",
  "description": "Q1 2026 Audit",
  "file_type": "pdf",
  "file_size_bytes": 1024,
  "uploaded_at": "2026-03-10T12:00:00",
  "created_at": "2026-03-10T12:00:00"
}
```

#### List Evidence
```
GET /api/v1/tenants/{tenant_id}/evidence?category=audit&skip=0&limit=50&include_deleted=false
```

**Response (200):**
```json
{
  "total": 42,
  "skip": 0,
  "limit": 50,
  "items": [
    {
      "id": "uuid",
      "name": "Audit Report",
      "category": "audit",
      "file_type": "pdf",
      "file_size_bytes": 1024,
      "uploaded_at": "2026-03-10T12:00:00",
      "created_at": "2026-03-10T12:00:00",
      "deleted_at": null
    }
  ]
}
```

#### Get Evidence Details
```
GET /api/v1/tenants/{tenant_id}/evidence/{evidence_id}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Audit Report",
  "category": "audit",
  "description": "Q1 2026 Audit",
  "file_type": "pdf",
  "file_size_bytes": 1024,
  "file_hash": "sha256_hash",
  "uploaded_by": "user_id",
  "uploaded_at": "2026-03-10T12:00:00",
  "created_by": "user_id",
  "created_at": "2026-03-10T12:00:00",
  "deleted_at": null,
  "versions": [
    {
      "version_number": 1,
      "file_hash": "hash",
      "file_size_bytes": 1024,
      "change_reason": "Initial upload",
      "created_at": "2026-03-10T12:00:00",
      "created_by": "user_id"
    }
  ],
  "links": [
    {
      "id": "uuid",
      "linked_to_type": "report",
      "linked_to_id": "uuid",
      "link_type": "supports",
      "created_at": "2026-03-10T12:00:00"
    }
  ]
}
```

#### Update Evidence Metadata
```
PATCH /api/v1/tenants/{tenant_id}/evidence/{evidence_id}
```

**Request:** Form data
```
name: (string, optional)
description: (string, optional)
category: (string, optional)
```

**Response (200):** Updated evidence object

#### Delete Evidence
```
DELETE /api/v1/tenants/{tenant_id}/evidence/{evidence_id}?hard_delete=false
```

**Response (200):**
```json
{
  "message": "Evidence deleted successfully",
  "evidence_id": "uuid",
  "hard_delete": false
}
```

#### Link Evidence
```
POST /api/v1/tenants/{tenant_id}/evidence/{evidence_id}/link
```

**Request:** Form data
```
linked_to_type: (string, required)  # metric, report, calculation, kpi, carbon_credit
linked_to_id: (string, required)
link_type: (string, optional)  # supports, references, validates, contradicts
```

**Response (200):**
```json
{
  "id": "uuid",
  "evidence_id": "uuid",
  "linked_to_type": "report",
  "linked_to_id": "uuid",
  "link_type": "supports",
  "created_at": "2026-03-10T12:00:00"
}
```

#### Download Evidence
```
GET /api/v1/tenants/{tenant_id}/evidence/{evidence_id}/download
```

**Response (200):** File content as binary stream

#### Get Download URL
```
GET /api/v1/tenants/{tenant_id}/evidence/{evidence_id}/download-url?expires_in_seconds=3600
```

**Response (200):**
```json
{
  "url": "https://s3.example.com/...",
  "evidence_id": "uuid",
  "expires_in_seconds": 3600
}
```

## File Validation

**Allowed File Types:**
- PDF: `pdf`
- Excel: `xlsx`, `xls`
- Images: `png`, `jpg`, `jpeg`
- Data: `csv`, `txt`
- Documents: `doc`, `docx`

**Size Limits:**
- Maximum file size: 100 MB

**Content Types:**
- Original Content-Type is preserved in metadata

## Security Features

### Tenant Isolation
Every operation enforces tenant isolation:
1. Token contains `tenant_id`
2. All queries filter by tenant
3. Cross-tenant access raises 403 Forbidden
4. File paths include tenant_id

### Authentication
- All endpoints require valid JWT token
- Token validation via `extract_token_from_header()` and `verify_token()`
- Invalid/expired tokens return 401 Unauthorized

### File Integrity
- SHA256 hash calculated on upload
- Hash stored in database
- Hash verified on download
- Mismatch detected and reported

### Audit Trail
All operations create AuditLog records:
- `evidence_uploaded`
- `evidence_updated`
- `evidence_soft_deleted`
- `evidence_hard_deleted`
- `evidence_linked`

## Testing

### Unit Tests (`test_evidence_service.py`)
- Upload validation (type, size, tenant)
- Download with isolation
- Listing with pagination and filtering
- Soft/hard delete
- Linking to metrics and reports
- Metadata updates
- 85%+ code coverage

### Integration Tests (`test_evidence_integration.py`)
- Full HTTP request/response cycle
- Multipart file uploads
- Authorization checks
- Tenant isolation
- Error responses

**Run tests:**
```bash
# Unit tests
pytest backend/tests/test_evidence_service.py -v

# Integration tests
pytest backend/tests/test_evidence_integration.py -v

# With coverage
pytest backend/tests/test_evidence*.py --cov=app.services.evidence_service --cov=app.routes.evidence
```

## Database Migration

Migration file: `alembic/versions/003_add_evidence_tables.py`

**Tables Created:**
- `evidence` (main documents)
- `evidence_versions` (version history)
- `evidence_links` (relationships)

**Indexes:**
- `idx_evidence_tenant_category`: For filtered listing
- `idx_evidence_deleted_at`: For soft delete queries
- `idx_evidence_links_linked_to`: For finding evidence by linked entity

**Run migration:**
```bash
alembic upgrade head
```

## Usage Examples

### Upload a Document
```python
from app.services.evidence_service import EvidenceService
from io import BytesIO

service = EvidenceService(db, s3_client)

file_content = BytesIO(b"PDF content...")
evidence = service.upload_evidence(
    tenant_id="tenant-123",
    file_content=file_content,
    file_name="audit_report.pdf",
    category="audit",
    uploaded_by_id="user-456",
    name="Q1 2026 Audit Report",
    description="Annual audit findings"
)
```

### Link to Report
```python
service.link_to_report(
    evidence_id=str(evidence.id),
    report_id="report-789",
    tenant_id="tenant-123",
    link_type="supports"
)
```

### Get Evidence for Report
```python
evidence_list = service.get_evidence_for_report(
    report_id="report-789",
    tenant_id="tenant-123"
)
```

### Get Presigned URL
```python
url = service.get_presigned_download_url(
    evidence_id=str(evidence.id),
    tenant_id="tenant-123",
    expires_in_seconds=7200  # 2 hours
)
# Send URL to user for direct download from S3
```

### Soft Delete (Preserve Audit Trail)
```python
service.delete_evidence(
    evidence_id=str(evidence.id),
    tenant_id="tenant-123",
    deleted_by_id="user-456",
    soft_delete=True  # Keeps data for audit
)
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# S3/MinIO
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=evidence-repository

# Or for MinIO
MINIO_ENDPOINT_URL=http://localhost:9000

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

### Feature Flags
None currently (always enabled)

## Maintenance

### Cleanup Soft-Deleted Records
To permanently remove soft-deleted records after 30 days:

```python
from datetime import datetime, timedelta

cutoff_date = datetime.utcnow() - timedelta(days=30)
old_evidence = db.query(Evidence).filter(
    Evidence.deleted_at < cutoff_date
).all()

for evidence in old_evidence:
    service.delete_evidence(
        evidence_id=str(evidence.id),
        tenant_id=str(evidence.tenant_id),
        soft_delete=False  # Hard delete
    )
```

### Verify File Integrity
```python
is_valid = service.s3_client.verify_file_integrity(
    document_key=evidence.document_key,
    expected_hash=evidence.file_hash
)
```

## Future Enhancements

1. **Virus Scanning**: Integrate ClamAV for malware detection
2. **OCR**: Extract text from PDFs for searching
3. **Preview Generation**: Create thumbnails for images
4. **Change Tracking**: Show diff between versions
5. **Compliance Rules**: Enforce evidence requirements by category
6. **Audit Report**: Generate compliance reports from evidence
7. **Expiration**: Auto-delete evidence after retention period
8. **Encryption**: Enable server-side encryption in S3
9. **Versioning**: Implement S3 object versioning
10. **CloudTrail**: Log all S3 access

## Troubleshooting

### File Upload Fails
- Check S3/MinIO connectivity: `s3_client.is_healthy()`
- Verify AWS credentials in environment variables
- Check bucket permissions
- Verify file size < 100 MB

### Presigned URL Expires
- URLs expire after configured time (default 1 hour)
- Generate new URL for extended access
- Adjust `expires_in_seconds` parameter

### Hash Mismatch
- File may be corrupted during transfer
- Check file integrity: `verify_file_integrity()`
- Re-upload if necessary
- Check S3 storage for issues

### Tenant Isolation Errors
- Verify token contains correct `tenant_id`
- Check evidence belongs to correct tenant
- Ensure all queries filter by tenant

## Support

For issues or questions:
1. Check logs: `app.services.evidence_service` logger
2. Review tests for usage examples
3. Verify S3/database connectivity
4. Contact platform team

---

**Last Updated**: 2026-03-10
**Status**: Production Ready (85%+ test coverage)
**Maintainer**: Platform Team
