"""Reporting engine for ESG reports, versioning, and exports"""

from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Optional

from app.models import Report, ReportVersion, ReportSignature, ReportTemplate, User


class ReportGenerationService:
    """Generate and manage ESG reports"""

    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        organization_id: UUID,
        tenant_id: UUID,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        created_by: UUID,
    ) -> Dict:
        """Create new report"""
        report = Report(
            organization_id=organization_id,
            tenant_id=tenant_id,
            report_type=report_type,
            report_period_start=period_start,
            report_period_end=period_end,
            created_by=created_by,
            current_state="draft",
        )
        self.db.add(report)
        self.db.commit()
        return {"id": str(report.id), "state": "draft", "type": report_type}

    def generate_report(self, report_id: UUID, template_id: Optional[UUID] = None) -> Dict:
        """Generate report content"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        return {
            "report_id": str(report_id),
            "status": "generated",
            "period_start": report.report_period_start.isoformat(),
            "period_end": report.report_period_end.isoformat(),
        }

    def publish_report(self, report_id: UUID, published_by: UUID) -> Dict:
        """Publish report"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        report.current_state = "published"
        report.published_by = published_by
        report.published_at = datetime.utcnow()
        self.db.commit()
        return {"id": str(report_id), "state": "published"}

    def export_report(self, report_id: UUID, export_format: str) -> Dict:
        """Export report in format"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError("Report not found")
        return {
            "report_id": str(report_id),
            "format": export_format,
            "status": "exported",
            "file_size": "0 MB",
        }

    def list_organization_reports(self, organization_id: UUID) -> List[Dict]:
        """List reports for organization"""
        reports = self.db.query(Report).filter(Report.organization_id == organization_id).all()
        return [
            {
                "id": str(r.id),
                "type": r.report_type,
                "state": r.current_state,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ]


class ReportVersioningService:
    """Manage report versions and snapshots"""

    def __init__(self, db: Session):
        self.db = db

    def create_version(
        self,
        report_id: UUID,
        version_reason: str,
        versioned_by: UUID,
        s3_key_pdf: Optional[str] = None,
    ) -> Dict:
        """Create report version"""
        # Get latest version number
        max_version = (
            self.db.query(ReportVersion)
            .filter(ReportVersion.report_id == report_id)
            .count()
        )

        version = ReportVersion(
            report_id=report_id,
            version_number=max_version + 1,
            s3_key_pdf=s3_key_pdf,
            version_reason=version_reason,
            versioned_by=versioned_by,
            version_state="draft",
        )
        self.db.add(version)
        self.db.commit()
        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
        }

    def get_report_versions(self, report_id: UUID) -> List[Dict]:
        """Get all versions of report"""
        versions = (
            self.db.query(ReportVersion)
            .filter(ReportVersion.report_id == report_id)
            .order_by(ReportVersion.version_number.desc())
            .all()
        )
        return [
            {
                "version_number": v.version_number,
                "state": v.version_state,
                "date": v.version_date.isoformat(),
            }
            for v in versions
        ]

    def restore_version(self, version_id: UUID) -> Dict:
        """Restore to previous version"""
        version = self.db.query(ReportVersion).filter(ReportVersion.id == version_id).first()
        if not version:
            raise ValueError("Version not found")
        return {
            "version_id": str(version_id),
            "status": "restored",
        }


class ReportSignatureService:
    """Manage report signatures and approvals"""

    def __init__(self, db: Session):
        self.db = db

    def sign_report(
        self,
        report_id: UUID,
        signer_id: UUID,
        signer_role: str,
        signature_method: str = "digital",
    ) -> Dict:
        """Sign/approve report"""
        signature = ReportSignature(
            report_id=report_id,
            signer_id=signer_id,
            signer_role=signer_role,
            signature_method=signature_method,
        )
        self.db.add(signature)
        self.db.commit()
        return {
            "signature_id": str(signature.id),
            "signer_role": signer_role,
            "signed_at": signature.signed_at.isoformat(),
        }

    def get_report_signatures(self, report_id: UUID) -> List[Dict]:
        """Get signatures for report"""
        signatures = (
            self.db.query(ReportSignature)
            .filter(ReportSignature.report_id == report_id)
            .all()
        )
        return [
            {
                "signer_role": s.signer_role,
                "signed_at": s.signed_at.isoformat(),
                "method": s.signature_method,
            }
            for s in signatures
        ]


class ReportTemplateService:
    """Manage report templates"""

    def __init__(self, db: Session):
        self.db = db

    def create_template(
        self,
        tenant_id: UUID,
        template_name: str,
        report_type: str,
        template_config: Dict,
        created_by: UUID,
    ) -> Dict:
        """Create report template"""
        template = ReportTemplate(
            tenant_id=tenant_id,
            template_name=template_name,
            report_type=report_type,
            template_config=template_config,
            created_by=created_by,
        )
        self.db.add(template)
        self.db.commit()
        return {"id": str(template.id), "name": template_name}

    def list_templates(self, tenant_id: UUID, report_type: Optional[str] = None) -> List[Dict]:
        """List templates"""
        query = self.db.query(ReportTemplate).filter(ReportTemplate.tenant_id == tenant_id)
        if report_type:
            query = query.filter(ReportTemplate.report_type == report_type)
        templates = query.all()
        return [
            {"id": str(t.id), "name": t.template_name, "type": t.report_type}
            for t in templates
        ]

    def get_template(self, template_id: UUID) -> Dict:
        """Get template details"""
        template = self.db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
        if not template:
            raise ValueError("Template not found")
        return {
            "id": str(template.id),
            "name": template.template_name,
            "config": template.template_config,
        }
