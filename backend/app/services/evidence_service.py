"""
Evidence Repository Service

Implements:
- Evidence document upload/download/versioning
- Evidence linking to metrics, reports, and other entities
- Soft delete support
- Tenant isolation
- Audit logging
- File integrity verification
"""

import logging
from typing import List, Optional, Dict, BinaryIO, Tuple
from datetime import datetime
from uuid import UUID
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_

from app.models import (
    Evidence,
    EvidenceVersion,
    EvidenceLink,
    Tenant,
    User,
    AuditLog,
)
from app.integrations.s3_client import S3Client, S3ClientError, get_s3_client

logger = logging.getLogger(__name__)

# Allowed file types for evidence documents
ALLOWED_FILE_TYPES = {"pdf", "xlsx", "xls", "png", "jpg", "jpeg", "csv", "txt", "doc", "docx"}
MAX_FILE_SIZE_MB = 100


class EvidenceServiceError(Exception):
    """Custom exception for Evidence Service"""
    pass


class EvidenceService:
    """Service for managing evidence documents and versioning"""

    def __init__(self, db: Session, s3_client: Optional[S3Client] = None):
        """
        Initialize Evidence Service

        Args:
            db: Database session
            s3_client: S3/MinIO client (defaults to singleton)
        """
        self.db = db
        self.s3_client = s3_client or get_s3_client()

    def upload_evidence(
        self,
        tenant_id: str,
        file_content: BinaryIO,
        file_name: str,
        category: str,
        uploaded_by_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Evidence:
        """
        Upload an evidence document

        Args:
            tenant_id: Tenant ID
            file_content: Binary file content
            file_name: Original file name
            category: Evidence category (policy, audit, certification, report, etc.)
            uploaded_by_id: User ID of uploader
            name: Display name for evidence (defaults to file_name)
            description: Optional description
            metadata: Optional metadata dict

        Returns:
            Created Evidence object

        Raises:
            EvidenceServiceError: If upload fails
        """
        try:
            # Validate tenant
            tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                raise EvidenceServiceError(f"Tenant not found: {tenant_id}")

            # Validate user
            user = self.db.query(User).filter_by(id=uploaded_by_id).first()
            if not user:
                raise EvidenceServiceError(f"User not found: {uploaded_by_id}")

            # Validate file
            file_type = self._extract_file_type(file_name)
            if file_type not in ALLOWED_FILE_TYPES:
                raise EvidenceServiceError(
                    f"File type not allowed: {file_type}. "
                    f"Allowed types: {', '.join(sorted(ALLOWED_FILE_TYPES))}"
                )

            # Upload to S3
            logger.info(f"Uploading evidence: {file_name} for tenant {tenant_id}")
            document_key, file_hash, file_size = self.s3_client.upload_file(
                file_content=file_content,
                tenant_id=tenant_id,
                document_name=file_name,
                metadata=metadata or {},
            )

            # Check file size
            file_size_mb = file_size / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                self.s3_client.delete_file(document_key)
                raise EvidenceServiceError(
                    f"File size exceeds limit: {file_size_mb:.2f}MB > {MAX_FILE_SIZE_MB}MB"
                )

            # Create evidence record
            evidence = Evidence(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                name=name or file_name,
                category=category,
                description=description,
                document_key=document_key,
                file_hash=file_hash,
                file_size_bytes=file_size,
                file_type=file_type,
                uploaded_by=uploaded_by_id,
                created_by=uploaded_by_id,
            )

            self.db.add(evidence)
            self.db.flush()

            # Create initial version
            version = EvidenceVersion(
                id=uuid.uuid4(),
                evidence_id=evidence.id,
                tenant_id=tenant_id,
                version_number=1,
                document_key=document_key,
                file_hash=file_hash,
                file_size_bytes=file_size,
                change_reason="Initial upload",
                created_by=uploaded_by_id,
            )
            self.db.add(version)

            # Audit log
            self._audit_log(
                tenant_id=tenant_id,
                user_id=uploaded_by_id,
                action="evidence_uploaded",
                entity_type="Evidence",
                entity_id=evidence.id,
                changes={
                    "file_name": file_name,
                    "category": category,
                    "file_size": file_size,
                    "file_hash": file_hash,
                },
            )

            self.db.commit()
            self.db.refresh(evidence)

            logger.info(f"Successfully uploaded evidence: {evidence.id}")
            return evidence

        except EvidenceServiceError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error uploading evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def download_evidence(self, evidence_id: str, tenant_id: str) -> Tuple[BinaryIO, Evidence]:
        """
        Download an evidence document

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID (for isolation check)

        Returns:
            Tuple of (file_content, evidence_object)

        Raises:
            EvidenceServiceError: If download fails
        """
        try:
            evidence = self._get_evidence(evidence_id, tenant_id)

            logger.info(f"Downloading evidence: {evidence_id}")
            file_content = self.s3_client.download_file(evidence.document_key)

            logger.info(f"Successfully downloaded evidence: {evidence_id}")
            return file_content, evidence

        except EvidenceServiceError:
            raise
        except Exception as e:
            error_msg = f"Error downloading evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def list_evidence(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Tuple[List[Evidence], int]:
        """
        List evidence documents with pagination

        Args:
            tenant_id: Tenant ID
            category: Optional category filter
            skip: Number of records to skip
            limit: Maximum records to return
            include_deleted: Include soft-deleted records

        Returns:
            Tuple of (evidence_list, total_count)

        Raises:
            EvidenceServiceError: If listing fails
        """
        try:
            query = self.db.query(Evidence).filter_by(tenant_id=tenant_id)

            if not include_deleted:
                query = query.filter(Evidence.deleted_at.is_(None))

            if category:
                query = query.filter_by(category=category)

            total_count = query.count()
            evidence_list = (
                query.order_by(desc(Evidence.uploaded_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            logger.info(f"Listed {len(evidence_list)} evidence documents for tenant {tenant_id}")
            return evidence_list, total_count

        except Exception as e:
            error_msg = f"Error listing evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def get_evidence_details(self, evidence_id: str, tenant_id: str) -> Dict:
        """
        Get detailed information about an evidence document

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID

        Returns:
            Dictionary with evidence details including versions and links

        Raises:
            EvidenceServiceError: If retrieval fails
        """
        try:
            evidence = self._get_evidence(evidence_id, tenant_id)

            # Get versions
            versions = (
                self.db.query(EvidenceVersion)
                .filter_by(evidence_id=evidence_id)
                .order_by(desc(EvidenceVersion.version_number))
                .all()
            )

            # Get links
            links = (
                self.db.query(EvidenceLink)
                .filter_by(evidence_id=evidence_id)
                .all()
            )

            return {
                "id": str(evidence.id),
                "tenant_id": str(evidence.tenant_id),
                "name": evidence.name,
                "category": evidence.category,
                "description": evidence.description,
                "file_type": evidence.file_type,
                "file_size_bytes": evidence.file_size_bytes,
                "file_hash": evidence.file_hash,
                "uploaded_by": str(evidence.uploaded_by) if evidence.uploaded_by else None,
                "uploaded_at": evidence.uploaded_at.isoformat(),
                "created_by": str(evidence.created_by) if evidence.created_by else None,
                "created_at": evidence.created_at.isoformat(),
                "deleted_at": evidence.deleted_at.isoformat() if evidence.deleted_at else None,
                "versions": [
                    {
                        "version_number": v.version_number,
                        "file_hash": v.file_hash,
                        "file_size_bytes": v.file_size_bytes,
                        "change_reason": v.change_reason,
                        "created_at": v.created_at.isoformat(),
                        "created_by": str(v.created_by) if v.created_by else None,
                    }
                    for v in versions
                ],
                "links": [
                    {
                        "id": str(l.id),
                        "linked_to_type": l.linked_to_type,
                        "linked_to_id": str(l.linked_to_id),
                        "link_type": l.link_type,
                        "created_at": l.created_at.isoformat(),
                    }
                    for l in links
                ],
            }

        except EvidenceServiceError:
            raise
        except Exception as e:
            error_msg = f"Error getting evidence details: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def update_evidence_metadata(
        self,
        evidence_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        updated_by_id: Optional[str] = None,
    ) -> Evidence:
        """
        Update evidence metadata (name, description, category)

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID
            name: Optional new name
            description: Optional new description
            category: Optional new category
            updated_by_id: User ID performing update

        Returns:
            Updated Evidence object

        Raises:
            EvidenceServiceError: If update fails
        """
        try:
            evidence = self._get_evidence(evidence_id, tenant_id)

            changes = {}
            if name is not None:
                changes["name"] = name
                evidence.name = name
            if description is not None:
                changes["description"] = description
                evidence.description = description
            if category is not None:
                changes["category"] = category
                evidence.category = category

            if changes:
                self.db.flush()

                if updated_by_id:
                    self._audit_log(
                        tenant_id=tenant_id,
                        user_id=updated_by_id,
                        action="evidence_updated",
                        entity_type="Evidence",
                        entity_id=evidence.id,
                        changes=changes,
                    )

                self.db.commit()
                self.db.refresh(evidence)
                logger.info(f"Updated evidence metadata: {evidence_id}")

            return evidence

        except EvidenceServiceError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error updating evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def delete_evidence(
        self,
        evidence_id: str,
        tenant_id: str,
        deleted_by_id: Optional[str] = None,
        soft_delete: bool = True,
    ) -> Evidence:
        """
        Delete evidence (soft delete by default)

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID
            deleted_by_id: User ID performing deletion
            soft_delete: If True, soft delete; if False, hard delete from S3

        Returns:
            Deleted Evidence object (for soft delete) or None (for hard delete)

        Raises:
            EvidenceServiceError: If deletion fails
        """
        try:
            evidence = self._get_evidence(evidence_id, tenant_id)

            if soft_delete:
                evidence.deleted_at = datetime.utcnow()
                self.db.flush()

                if deleted_by_id:
                    self._audit_log(
                        tenant_id=tenant_id,
                        user_id=deleted_by_id,
                        action="evidence_soft_deleted",
                        entity_type="Evidence",
                        entity_id=evidence.id,
                        changes={"deleted_at": datetime.utcnow().isoformat()},
                    )

                self.db.commit()
                self.db.refresh(evidence)
                logger.info(f"Soft deleted evidence: {evidence_id}")
                return evidence

            else:
                # Hard delete from S3
                try:
                    self.s3_client.delete_file(evidence.document_key)

                    # Delete versions from S3
                    versions = self.db.query(EvidenceVersion).filter_by(
                        evidence_id=evidence_id
                    ).all()
                    for version in versions:
                        try:
                            self.s3_client.delete_file(version.document_key)
                        except Exception as e:
                            logger.warning(f"Failed to delete version file: {str(e)}")

                except S3ClientError as e:
                    logger.warning(f"Could not delete from S3: {str(e)}")

                # Delete from database
                self.db.delete(evidence)
                self.db.flush()

                if deleted_by_id:
                    self._audit_log(
                        tenant_id=tenant_id,
                        user_id=deleted_by_id,
                        action="evidence_hard_deleted",
                        entity_type="Evidence",
                        entity_id=evidence.id,
                        changes={"deleted": True},
                    )

                self.db.commit()
                logger.info(f"Hard deleted evidence: {evidence_id}")
                return None

        except EvidenceServiceError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error deleting evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def link_to_metric(
        self,
        evidence_id: str,
        metric_id: str,
        tenant_id: str,
        link_type: str = "supports",
        created_by_id: Optional[str] = None,
    ) -> EvidenceLink:
        """
        Link evidence to a metric

        Args:
            evidence_id: Evidence ID
            metric_id: Metric ID
            tenant_id: Tenant ID
            link_type: Type of link (default: supports)
            created_by_id: User ID creating link

        Returns:
            Created EvidenceLink object

        Raises:
            EvidenceServiceError: If linking fails
        """
        return self.link_evidence(
            evidence_id=evidence_id,
            linked_to_type="metric",
            linked_to_id=metric_id,
            tenant_id=tenant_id,
            link_type=link_type,
            created_by_id=created_by_id,
        )

    def link_to_report(
        self,
        evidence_id: str,
        report_id: str,
        tenant_id: str,
        link_type: str = "supports",
        created_by_id: Optional[str] = None,
    ) -> EvidenceLink:
        """
        Link evidence to a report

        Args:
            evidence_id: Evidence ID
            report_id: Report ID
            tenant_id: Tenant ID
            link_type: Type of link (default: supports)
            created_by_id: User ID creating link

        Returns:
            Created EvidenceLink object

        Raises:
            EvidenceServiceError: If linking fails
        """
        return self.link_evidence(
            evidence_id=evidence_id,
            linked_to_type="report",
            linked_to_id=report_id,
            tenant_id=tenant_id,
            link_type=link_type,
            created_by_id=created_by_id,
        )

    def link_evidence(
        self,
        evidence_id: str,
        linked_to_type: str,
        linked_to_id: str,
        tenant_id: str,
        link_type: str = "supports",
        created_by_id: Optional[str] = None,
    ) -> EvidenceLink:
        """
        Link evidence to another entity (metric, report, calculation, etc.)

        Args:
            evidence_id: Evidence ID
            linked_to_type: Type of entity being linked (metric, report, calculation, kpi, etc.)
            linked_to_id: ID of entity being linked
            tenant_id: Tenant ID
            link_type: Type of link (supports, references, validates, etc.)
            created_by_id: User ID creating link

        Returns:
            Created EvidenceLink object

        Raises:
            EvidenceServiceError: If linking fails
        """
        try:
            # Validate evidence exists
            evidence = self._get_evidence(evidence_id, tenant_id)

            # Check for duplicate link
            existing_link = self.db.query(EvidenceLink).filter(
                and_(
                    EvidenceLink.evidence_id == evidence_id,
                    EvidenceLink.linked_to_type == linked_to_type,
                    EvidenceLink.linked_to_id == linked_to_id,
                )
            ).first()

            if existing_link:
                logger.info(
                    f"Link already exists: {evidence_id} -> {linked_to_type}:{linked_to_id}"
                )
                return existing_link

            # Create link
            link = EvidenceLink(
                id=uuid.uuid4(),
                evidence_id=evidence_id,
                tenant_id=tenant_id,
                linked_to_type=linked_to_type,
                linked_to_id=linked_to_id,
                link_type=link_type,
                created_by=created_by_id,
            )
            self.db.add(link)
            self.db.flush()

            if created_by_id:
                self._audit_log(
                    tenant_id=tenant_id,
                    user_id=created_by_id,
                    action="evidence_linked",
                    entity_type="EvidenceLink",
                    entity_id=link.id,
                    changes={
                        "evidence_id": evidence_id,
                        "linked_to_type": linked_to_type,
                        "linked_to_id": linked_to_id,
                    },
                )

            self.db.commit()
            self.db.refresh(link)
            logger.info(f"Created link: {evidence_id} -> {linked_to_type}:{linked_to_id}")
            return link

        except EvidenceServiceError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error linking evidence: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def get_evidence_for_report(self, report_id: str, tenant_id: str) -> List[Evidence]:
        """
        Get all evidence linked to a report

        Args:
            report_id: Report ID
            tenant_id: Tenant ID

        Returns:
            List of Evidence objects

        Raises:
            EvidenceServiceError: If retrieval fails
        """
        try:
            links = (
                self.db.query(EvidenceLink)
                .filter(
                    and_(
                        EvidenceLink.linked_to_type == "report",
                        EvidenceLink.linked_to_id == report_id,
                        EvidenceLink.tenant_id == tenant_id,
                    )
                )
                .all()
            )

            evidence_ids = [link.evidence_id for link in links]
            evidence_list = (
                self.db.query(Evidence)
                .filter(
                    and_(
                        Evidence.id.in_(evidence_ids),
                        Evidence.tenant_id == tenant_id,
                        Evidence.deleted_at.is_(None),
                    )
                )
                .all()
            )

            logger.info(f"Retrieved {len(evidence_list)} evidence items for report {report_id}")
            return evidence_list

        except Exception as e:
            error_msg = f"Error getting evidence for report: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def get_presigned_download_url(
        self,
        evidence_id: str,
        tenant_id: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        """
        Get a presigned URL for downloading evidence

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID
            expires_in_seconds: URL expiration time in seconds

        Returns:
            Presigned URL string

        Raises:
            EvidenceServiceError: If URL generation fails
        """
        try:
            evidence = self._get_evidence(evidence_id, tenant_id)
            url = self.s3_client.get_presigned_url(
                evidence.document_key,
                expires_in_seconds=expires_in_seconds,
            )
            logger.info(f"Generated presigned URL for evidence: {evidence_id}")
            return url

        except EvidenceServiceError:
            raise
        except Exception as e:
            error_msg = f"Error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            raise EvidenceServiceError(error_msg)

    def _get_evidence(self, evidence_id: str, tenant_id: str) -> Evidence:
        """
        Get evidence with tenant isolation check

        Args:
            evidence_id: Evidence ID
            tenant_id: Tenant ID

        Returns:
            Evidence object

        Raises:
            EvidenceServiceError: If not found or tenant mismatch
        """
        evidence = self.db.query(Evidence).filter_by(id=evidence_id).first()

        if not evidence:
            raise EvidenceServiceError(f"Evidence not found: {evidence_id}")

        if evidence.tenant_id != tenant_id:
            raise EvidenceServiceError(
                f"Tenant mismatch for evidence {evidence_id}: "
                f"requested {tenant_id}, but evidence belongs to {evidence.tenant_id}"
            )

        return evidence

    @staticmethod
    def _extract_file_type(file_name: str) -> str:
        """Extract file type from file name"""
        if not file_name or "." not in file_name:
            return "unknown"
        return file_name.rsplit(".", 1)[-1].lower()

    def _audit_log(
        self,
        tenant_id: str,
        user_id: Optional[str],
        action: str,
        entity_type: str,
        entity_id: UUID,
        changes: Optional[dict] = None,
    ):
        """Create audit log entry"""
        try:
            audit_log = AuditLog(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes or {},
            )
            self.db.add(audit_log)
            self.db.flush()
        except Exception as e:
            logger.warning(f"Failed to create audit log: {str(e)}")
