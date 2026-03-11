"""
Evidence Repository API Routes

Endpoints for:
- Uploading evidence documents
- Downloading evidence
- Listing and searching evidence
- Linking evidence to metrics and reports
- Evidence metadata management
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile, Query, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.evidence_service import EvidenceService, EvidenceServiceError
from app.models import Evidence

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["evidence"])


def get_current_user(authorization: str = Header(None)):
    """Extract and verify current user from token"""
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/tenants/{tenant_id}/evidence")
async def upload_evidence(
    tenant_id: str,
    file: UploadFile = File(...),
    category: str = Form(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload an evidence document

    Args:
        tenant_id: Tenant ID
        file: File to upload
        category: Evidence category (policy, audit, certification, report, etc.)
        name: Optional display name
        description: Optional description

    Returns:
        Created evidence object with metadata
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        file_content = await file.read()

        # Create in-memory file-like object
        from io import BytesIO
        file_obj = BytesIO(file_content)

        evidence = service.upload_evidence(
            tenant_id=tenant_id,
            file_content=file_obj,
            file_name=file.filename,
            category=category,
            uploaded_by_id=current_user["user_id"],
            name=name,
            description=description,
            metadata={"content_type": file.content_type},
        )

        return {
            "id": str(evidence.id),
            "name": evidence.name,
            "category": evidence.category,
            "description": evidence.description,
            "file_type": evidence.file_type,
            "file_size_bytes": evidence.file_size_bytes,
            "uploaded_at": evidence.uploaded_at.isoformat(),
            "created_at": evidence.created_at.isoformat(),
        }

    except EvidenceServiceError as e:
        logger.error(f"Evidence upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error uploading evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/evidence")
async def list_evidence(
    tenant_id: str,
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(False),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List evidence documents with pagination and filtering

    Args:
        tenant_id: Tenant ID
        category: Optional category filter
        skip: Number of records to skip
        limit: Maximum records to return
        include_deleted: Include soft-deleted records

    Returns:
        List of evidence objects with pagination info
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        evidence_list, total_count = service.list_evidence(
            tenant_id=tenant_id,
            category=category,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "items": [
                {
                    "id": str(e.id),
                    "name": e.name,
                    "category": e.category,
                    "description": e.description,
                    "file_type": e.file_type,
                    "file_size_bytes": e.file_size_bytes,
                    "uploaded_at": e.uploaded_at.isoformat(),
                    "created_at": e.created_at.isoformat(),
                    "deleted_at": e.deleted_at.isoformat() if e.deleted_at else None,
                }
                for e in evidence_list
            ],
        }

    except EvidenceServiceError as e:
        logger.error(f"Evidence list error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/evidence/{evidence_id}")
async def get_evidence(
    tenant_id: str,
    evidence_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get detailed evidence information

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID

    Returns:
        Evidence object with all metadata, versions, and links
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        details = service.get_evidence_details(evidence_id=evidence_id, tenant_id=tenant_id)

        return details

    except EvidenceServiceError as e:
        logger.error(f"Error getting evidence: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tenants/{tenant_id}/evidence/{evidence_id}")
async def update_evidence(
    tenant_id: str,
    evidence_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update evidence metadata

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID
        name: Optional new name
        description: Optional new description
        category: Optional new category

    Returns:
        Updated evidence object
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        evidence = service.update_evidence_metadata(
            evidence_id=evidence_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            category=category,
            updated_by_id=current_user["user_id"],
        )

        return {
            "id": str(evidence.id),
            "name": evidence.name,
            "category": evidence.category,
            "description": evidence.description,
            "file_type": evidence.file_type,
            "uploaded_at": evidence.uploaded_at.isoformat(),
            "created_at": evidence.created_at.isoformat(),
        }

    except EvidenceServiceError as e:
        logger.error(f"Error updating evidence: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tenants/{tenant_id}/evidence/{evidence_id}")
async def delete_evidence(
    tenant_id: str,
    evidence_id: str,
    hard_delete: bool = Query(False),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete evidence (soft delete by default)

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID
        hard_delete: If true, hard delete from S3; otherwise soft delete

    Returns:
        Success message
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        service.delete_evidence(
            evidence_id=evidence_id,
            tenant_id=tenant_id,
            deleted_by_id=current_user["user_id"],
            soft_delete=not hard_delete,
        )

        return {
            "message": "Evidence deleted successfully",
            "evidence_id": evidence_id,
            "hard_delete": hard_delete,
        }

    except EvidenceServiceError as e:
        logger.error(f"Error deleting evidence: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tenants/{tenant_id}/evidence/{evidence_id}/link")
async def link_evidence(
    tenant_id: str,
    evidence_id: str,
    linked_to_type: str = Form(...),
    linked_to_id: str = Form(...),
    link_type: str = Form("supports"),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Link evidence to another entity (metric, report, etc.)

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID
        linked_to_type: Type of entity being linked (metric, report, calculation, kpi)
        linked_to_id: ID of the entity being linked
        link_type: Type of link (supports, references, validates, etc.)

    Returns:
        Created link object
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        link = service.link_evidence(
            evidence_id=evidence_id,
            linked_to_type=linked_to_type,
            linked_to_id=linked_to_id,
            tenant_id=tenant_id,
            link_type=link_type,
            created_by_id=current_user["user_id"],
        )

        return {
            "id": str(link.id),
            "evidence_id": str(link.evidence_id),
            "linked_to_type": link.linked_to_type,
            "linked_to_id": str(link.linked_to_id),
            "link_type": link.link_type,
            "created_at": link.created_at.isoformat(),
        }

    except EvidenceServiceError as e:
        logger.error(f"Error linking evidence: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error linking evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/evidence/{evidence_id}/download")
async def download_evidence(
    tenant_id: str,
    evidence_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Download an evidence document

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID

    Returns:
        File content as streaming response
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        file_content, evidence = service.download_evidence(
            evidence_id=evidence_id,
            tenant_id=tenant_id,
        )

        return StreamingResponse(
            file_content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={evidence.name}"},
        )

    except EvidenceServiceError as e:
        logger.error(f"Error downloading evidence: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error downloading evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/evidence/{evidence_id}/download-url")
async def get_download_url(
    tenant_id: str,
    evidence_id: str,
    expires_in_seconds: int = Query(3600, ge=60, le=86400),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a presigned URL for downloading evidence

    Args:
        tenant_id: Tenant ID
        evidence_id: Evidence ID
        expires_in_seconds: URL expiration time (60 seconds to 24 hours)

    Returns:
        Presigned URL
    """
    try:
        # Verify tenant isolation
        if current_user["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        service = EvidenceService(db)
        url = service.get_presigned_download_url(
            evidence_id=evidence_id,
            tenant_id=tenant_id,
            expires_in_seconds=expires_in_seconds,
        )

        return {
            "url": url,
            "evidence_id": evidence_id,
            "expires_in_seconds": expires_in_seconds,
        }

    except EvidenceServiceError as e:
        logger.error(f"Error generating download URL: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating download URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
