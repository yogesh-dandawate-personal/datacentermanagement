"""
JSON Report Export Service

Exports complete report data as JSON with:
- All metrics and calculations
- Evidence links
- Flat and nested structure options
- ISO 8601 timestamps
- Tenant isolation validation
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    Report, ReportSignature, ReportVersion, Organization, User, Tenant,
    KPIDefinition, KPISnapshot, KPIThreshold, KPIThresholdBreach,
    ComplianceReport, ComplianceTarget, ComplianceAuditTrail, ReportSection
)

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class JSONExporter:
    """Export reports to JSON format"""

    def __init__(self, db: Session):
        """
        Initialize JSON Exporter

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def _serialize_date(self, value: Optional[datetime]) -> Optional[str]:
        """
        Serialize datetime to ISO 8601 format

        Args:
            value: Datetime value

        Returns:
            ISO 8601 formatted string or None
        """
        return value.isoformat() if value else None

    def _serialize_decimal(self, value: Optional[Decimal]) -> Optional[float]:
        """
        Serialize Decimal to float

        Args:
            value: Decimal value

        Returns:
            Float value or None
        """
        return float(value) if value else None

    def _get_report_basic_info(self, report: Report) -> Dict[str, Any]:
        """
        Get basic report information

        Args:
            report: Report object

        Returns:
            Dictionary with report info
        """
        creator = self.db.query(User).filter(User.id == report.created_by).first()
        updater = self.db.query(User).filter(User.id == report.updated_by).first()
        publisher = self.db.query(User).filter(User.id == report.published_by).first()

        return {
            "id": str(report.id),
            "organization_id": str(report.organization_id),
            "tenant_id": str(report.tenant_id),
            "report_type": report.report_type,
            "period_start": self._serialize_date(report.report_period_start),
            "period_end": self._serialize_date(report.report_period_end),
            "current_state": report.current_state,
            "created_by": {
                "id": str(creator.id) if creator else None,
                "name": f"{creator.first_name} {creator.last_name}" if creator else None,
                "email": creator.email if creator else None
            },
            "updated_by": {
                "id": str(updater.id) if updater else None,
                "name": f"{updater.first_name} {updater.last_name}" if updater else None,
                "email": updater.email if updater else None
            },
            "publisher": {
                "id": str(publisher.id) if publisher else None,
                "name": f"{publisher.first_name} {publisher.last_name}" if publisher else None,
                "email": publisher.email if publisher else None
            },
            "created_at": self._serialize_date(report.created_at),
            "updated_at": self._serialize_date(report.updated_at),
            "published_at": self._serialize_date(report.published_at)
        }

    def _get_organization_info(self, organization_id: UUID) -> Dict[str, Any]:
        """
        Get organization information

        Args:
            organization_id: Organization UUID

        Returns:
            Dictionary with organization info
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()

        if not org:
            return {}

        return {
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "hierarchy_level": org.hierarchy_level
        }

    def _get_signatures(self, report_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all signatures for report

        Args:
            report_id: Report UUID

        Returns:
            List of signature dictionaries
        """
        signatures = self.db.query(ReportSignature).filter(
            ReportSignature.report_id == report_id
        ).all()

        sig_list = []
        for sig in signatures:
            signer = self.db.query(User).filter(User.id == sig.signer_id).first()
            sig_list.append({
                "id": str(sig.id),
                "signer": {
                    "id": str(signer.id) if signer else None,
                    "name": f"{signer.first_name} {signer.last_name}" if signer else None,
                    "email": signer.email if signer else None
                },
                "signer_role": sig.signer_role,
                "signed_at": self._serialize_date(sig.signed_at),
                "signature_method": sig.signature_method,
                "signature_notes": sig.signature_notes
            })
        return sig_list

    def _get_versions(self, report_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all versions of report

        Args:
            report_id: Report UUID

        Returns:
            List of version dictionaries
        """
        versions = self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id
        ).order_by(ReportVersion.version_number.desc()).all()

        version_list = []
        for version in versions:
            versioned_by = self.db.query(User).filter(
                User.id == version.versioned_by
            ).first()

            version_list.append({
                "id": str(version.id),
                "version_number": version.version_number,
                "state": version.version_state,
                "date": self._serialize_date(version.version_date),
                "versioned_by": {
                    "id": str(versioned_by.id) if versioned_by else None,
                    "name": f"{versioned_by.first_name} {versioned_by.last_name}" if versioned_by else None
                },
                "reason": version.version_reason,
                "s3_key_pdf": version.s3_key_pdf,
                "s3_key_json": version.s3_key_json
            })
        return version_list

    def _get_kpi_data(self, organization_id: UUID) -> List[Dict[str, Any]]:
        """
        Get KPI definitions and latest snapshots

        Args:
            organization_id: Organization UUID

        Returns:
            List of KPI dictionaries
        """
        kpis = self.db.query(KPIDefinition).filter(
            KPIDefinition.organization_id == organization_id,
            KPIDefinition.is_active == True
        ).all()

        kpi_list = []
        for kpi in kpis:
            latest_snapshot = self.db.query(KPISnapshot).filter(
                KPISnapshot.kpi_id == kpi.id
            ).order_by(KPISnapshot.snapshot_date.desc()).first()

            kpi_data = {
                "id": str(kpi.id),
                "name": kpi.kpi_name,
                "type": kpi.kpi_type,
                "formula": kpi.formula,
                "unit": kpi.unit,
                "target_value": self._serialize_decimal(kpi.target_value),
                "lower_bound": self._serialize_decimal(kpi.lower_bound),
                "upper_bound": self._serialize_decimal(kpi.upper_bound),
                "latest_snapshot": None
            }

            if latest_snapshot:
                kpi_data["latest_snapshot"] = {
                    "id": str(latest_snapshot.id),
                    "date": self._serialize_date(latest_snapshot.snapshot_date),
                    "calculated_value": self._serialize_decimal(latest_snapshot.calculated_value),
                    "target_value": self._serialize_decimal(latest_snapshot.target_value),
                    "variance_percent": self._serialize_decimal(latest_snapshot.variance_percent),
                    "status": latest_snapshot.status,
                    "data_quality_score": self._serialize_decimal(latest_snapshot.data_quality_score),
                    "calculation_details": latest_snapshot.calculation_details
                }

            kpi_list.append(kpi_data)

        return kpi_list

    def _get_compliance_data(self, report_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get compliance report data if available

        Args:
            report_id: Report UUID

        Returns:
            Dictionary with compliance data or None
        """
        try:
            compliance_report = self.db.query(ComplianceReport).filter(
                ComplianceReport.id == report_id
            ).first()

            if not compliance_report:
                return None

            return {
                "id": str(compliance_report.id),
                "report_type": compliance_report.report_type,
                "reporting_period": compliance_report.reporting_period,
                "fiscal_year": compliance_report.fiscal_year,
                "status": compliance_report.status,
                "scope_1_emissions": self._serialize_decimal(compliance_report.scope_1_emissions),
                "scope_2_emissions": self._serialize_decimal(compliance_report.scope_2_emissions),
                "scope_3_emissions": self._serialize_decimal(compliance_report.scope_3_emissions),
                "carbon_offset_credits_used": self._serialize_decimal(
                    compliance_report.carbon_offset_credits_used
                ),
                "created_by": str(compliance_report.created_by) if compliance_report.created_by else None,
                "submitted_by": str(compliance_report.submitted_by) if compliance_report.submitted_by else None,
                "approved_by": str(compliance_report.approved_by) if compliance_report.approved_by else None,
                "created_at": self._serialize_date(compliance_report.created_at),
                "submitted_at": self._serialize_date(compliance_report.submitted_at),
                "approved_at": self._serialize_date(compliance_report.approved_at)
            }
        except Exception as e:
            logger.warning(f"Error fetching compliance data: {str(e)}")
            return None

    def _get_audit_trail(self, organization_id: UUID, entity_type: str = "report") -> List[Dict[str, Any]]:
        """
        Get audit trail entries

        Args:
            organization_id: Organization UUID
            entity_type: Type of entity to get audit for

        Returns:
            List of audit trail entries
        """
        try:
            audits = self.db.query(ComplianceAuditTrail).filter(
                ComplianceAuditTrail.organization_id == organization_id,
                ComplianceAuditTrail.entity_type == entity_type
            ).order_by(ComplianceAuditTrail.timestamp.desc()).limit(50).all()

            audit_list = []
            for audit in audits:
                changed_by = self.db.query(User).filter(
                    User.id == audit.changed_by_user_id
                ).first()

                audit_list.append({
                    "id": str(audit.id),
                    "action": audit.action,
                    "action_category": audit.action_category,
                    "entity_id": str(audit.entity_id) if audit.entity_id else None,
                    "changed_by": {
                        "id": str(changed_by.id) if changed_by else None,
                        "name": f"{changed_by.first_name} {changed_by.last_name}" if changed_by else None,
                        "email": changed_by.email if changed_by else None
                    },
                    "changed_values": audit.changed_values,
                    "timestamp": self._serialize_date(audit.timestamp),
                    "ip_address": audit.ip_address
                })

            return audit_list
        except Exception as e:
            logger.warning(f"Error fetching audit trail: {str(e)}")
            return []

    def export_flat(
        self,
        report_id: UUID,
        organization_id: UUID,
        tenant_id: UUID,
        scope_1: Optional[Decimal] = None,
        scope_2: Optional[Decimal] = None,
        scope_3: Optional[Decimal] = None,
        key_metrics: Optional[Dict] = None,
        evidence_links: Optional[List[Dict]] = None
    ) -> str:
        """
        Export report as flat JSON structure

        Args:
            report_id: Report UUID
            organization_id: Organization UUID
            tenant_id: Tenant UUID for security
            scope_1: Scope 1 emissions
            scope_2: Scope 2 emissions
            scope_3: Scope 3 emissions
            key_metrics: Dictionary of key metrics
            evidence_links: List of evidence references

        Returns:
            JSON string of report data

        Raises:
            ValueError: If report not found or tenant mismatch
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if report.tenant_id != tenant_id:
            raise ValueError("Tenant mismatch - access denied")

        data = {
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "export_format": "flat",
                "report_id": str(report_id),
                "tenant_id": str(tenant_id)
            },
            "report": self._get_report_basic_info(report),
            "organization": self._get_organization_info(organization_id),
            "emissions": {
                "scope_1": self._serialize_decimal(scope_1),
                "scope_2": self._serialize_decimal(scope_2),
                "scope_3": self._serialize_decimal(scope_3),
                "total": self._serialize_decimal(
                    (scope_1 or Decimal(0)) + (scope_2 or Decimal(0)) + (scope_3 or Decimal(0))
                )
            },
            "key_metrics": key_metrics or {},
            "evidence_references": evidence_links or [],
            "signatures": self._get_signatures(report_id),
            "versions": self._get_versions(report_id)
        }

        try:
            json_str = json.dumps(data, cls=DecimalEncoder, indent=2)
            logger.info(f"Flat JSON export created for report {report_id}")
            return json_str
        except Exception as e:
            logger.error(f"Error creating JSON export for report {report_id}: {str(e)}")
            raise

    def export_nested(
        self,
        report_id: UUID,
        organization_id: UUID,
        tenant_id: UUID,
        scope_1: Optional[Decimal] = None,
        scope_2: Optional[Decimal] = None,
        scope_3: Optional[Decimal] = None,
        key_metrics: Optional[Dict] = None,
        evidence_links: Optional[List[Dict]] = None
    ) -> str:
        """
        Export report as nested JSON structure with full details

        Args:
            report_id: Report UUID
            organization_id: Organization UUID
            tenant_id: Tenant UUID for security
            scope_1: Scope 1 emissions
            scope_2: Scope 2 emissions
            scope_3: Scope 3 emissions
            key_metrics: Dictionary of key metrics
            evidence_links: List of evidence references

        Returns:
            JSON string of report data

        Raises:
            ValueError: If report not found or tenant mismatch
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if report.tenant_id != tenant_id:
            raise ValueError("Tenant mismatch - access denied")

        data = {
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "export_format": "nested",
                "version": "1.0",
                "report_id": str(report_id),
                "tenant_id": str(tenant_id)
            },
            "report": {
                "basic_info": self._get_report_basic_info(report),
                "organization": self._get_organization_info(organization_id),
                "emissions": {
                    "scope_1": {
                        "value": self._serialize_decimal(scope_1),
                        "unit": "Tonnes CO2e",
                        "calculation_method": "GHG Protocol Scope 1"
                    },
                    "scope_2": {
                        "value": self._serialize_decimal(scope_2),
                        "unit": "Tonnes CO2e",
                        "calculation_method": "GHG Protocol Scope 2"
                    },
                    "scope_3": {
                        "value": self._serialize_decimal(scope_3),
                        "unit": "Tonnes CO2e",
                        "calculation_method": "GHG Protocol Scope 3"
                    },
                    "total": {
                        "value": self._serialize_decimal(
                            (scope_1 or Decimal(0)) + (scope_2 or Decimal(0)) + (scope_3 or Decimal(0))
                        ),
                        "unit": "Tonnes CO2e"
                    }
                },
                "key_metrics": key_metrics or {},
                "kpi_performance": self._get_kpi_data(organization_id),
                "compliance_data": self._get_compliance_data(report_id),
                "evidence": {
                    "references": evidence_links or [],
                    "count": len(evidence_links) if evidence_links else 0
                },
                "approvals": {
                    "signatures": self._get_signatures(report_id),
                    "status": report.current_state
                },
                "versions": self._get_versions(report_id),
                "audit_trail": self._get_audit_trail(organization_id, "report")
            }
        }

        try:
            json_str = json.dumps(data, cls=DecimalEncoder, indent=2)
            logger.info(f"Nested JSON export created for report {report_id}")
            return json_str
        except Exception as e:
            logger.error(f"Error creating nested JSON export for report {report_id}: {str(e)}")
            raise
