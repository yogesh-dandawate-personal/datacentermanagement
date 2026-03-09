"""
API routes for compliance reporting and auditing

Endpoints:
- Report Management (7 endpoints)
- Report Sections (3 endpoints)
- Audit Trail (2 endpoints)
- Compliance Targets (2 endpoints)
- Benchmarking (2 endpoints)
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import List, Optional

from app.database import get_db
from app.services.reporting_service import (
    ComplianceReportService,
    AuditTrailService,
    ComplianceTargetService,
    BenchmarkingService,
)

router = APIRouter(prefix="/api/v1", tags=["reporting"])


# ============================================================================
# Report Management Endpoints
# ============================================================================


@router.post("/organizations/{org_id}/reports/create")
async def create_report(
    org_id: UUID,
    report_type: str,
    reporting_period: str,
    fiscal_year: int,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
    x_user_id: str = Header(None),
):
    """Create a new compliance report"""
    try:
        service = ComplianceReportService(db)
        result = service.create_report(
            organization_id=org_id,
            tenant_id=UUID(x_tenant_id),
            report_type=report_type,
            reporting_period=reporting_period,
            fiscal_year=fiscal_year,
            created_by=UUID(x_user_id),
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/reports")
async def list_reports(
    org_id: UUID,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
):
    """List all reports for organization"""
    try:
        service = ComplianceReportService(db)
        reports = service.get_report_history(org_id)
        return {"success": True, "data": reports}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/reports/{report_id}")
async def get_report(
    org_id: UUID,
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Get report details"""
    try:
        from app.models import ComplianceReport

        report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")

        return {
            "success": True,
            "data": {
                "id": str(report.id),
                "report_type": report.report_type,
                "fiscal_year": report.fiscal_year,
                "status": report.status,
                "scope_1_emissions": float(report.scope_1_emissions) if report.scope_1_emissions else 0,
                "scope_2_emissions": float(report.scope_2_emissions) if report.scope_2_emissions else 0,
                "scope_3_emissions": float(report.scope_3_emissions) if report.scope_3_emissions else 0,
                "created_at": report.created_at.isoformat(),
                "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/organizations/{org_id}/reports/{report_id}")
async def update_report(
    org_id: UUID,
    report_id: UUID,
    scope_1: Optional[float] = None,
    scope_2: Optional[float] = None,
    scope_3: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Update report emissions data"""
    try:
        from app.models import ComplianceReport

        report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")

        if scope_1 is not None:
            report.scope_1_emissions = Decimal(str(scope_1))
        if scope_2 is not None:
            report.scope_2_emissions = Decimal(str(scope_2))
        if scope_3 is not None:
            report.scope_3_emissions = Decimal(str(scope_3))

        db.commit()

        return {
            "success": True,
            "data": {
                "id": str(report.id),
                "status": report.status,
                "scope_1_emissions": float(report.scope_1_emissions) if report.scope_1_emissions else 0,
                "scope_2_emissions": float(report.scope_2_emissions) if report.scope_2_emissions else 0,
                "scope_3_emissions": float(report.scope_3_emissions) if report.scope_3_emissions else 0,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/reports/{report_id}/submit")
async def submit_report(
    org_id: UUID,
    report_id: UUID,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None),
):
    """Submit report for approval"""
    try:
        service = ComplianceReportService(db)
        result = service.submit_for_approval(report_id, UUID(x_user_id))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/reports/{report_id}/approve")
async def approve_report(
    org_id: UUID,
    report_id: UUID,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None),
):
    """Approve report"""
    try:
        service = ComplianceReportService(db)
        result = service.approve_report(report_id, UUID(x_user_id))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/reports/{report_id}/export")
async def export_report(
    org_id: UUID,
    report_id: UUID,
    format: str = "json",
    db: Session = Depends(get_db),
):
    """Export report in specified format"""
    try:
        service = ComplianceReportService(db)
        result = service.export_report(report_id, format)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Report Sections Endpoints
# ============================================================================


@router.post("/reports/{report_id}/sections")
async def create_report_section(
    report_id: UUID,
    section_name: str,
    content: dict,
    db: Session = Depends(get_db),
):
    """Create a report section"""
    try:
        from app.models import ReportSection

        section = ReportSection(
            report_id=report_id,
            section_name=section_name,
            content=content,
            completion_percentage=0,
        )
        db.add(section)
        db.commit()

        return {
            "success": True,
            "data": {
                "id": str(section.id),
                "section_name": section_name,
                "completion_percentage": 0,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/{report_id}/sections")
async def get_report_sections(
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all sections of a report"""
    try:
        from app.models import ReportSection

        sections = db.query(ReportSection).filter(ReportSection.report_id == report_id).all()

        return {
            "success": True,
            "data": [
                {
                    "id": str(s.id),
                    "section_name": s.section_name,
                    "completion_percentage": s.completion_percentage,
                    "requires_review": s.requires_review,
                    "reviewed": s.reviewed_at is not None,
                }
                for s in sections
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/reports/{report_id}/sections/{section_id}")
async def update_report_section(
    report_id: UUID,
    section_id: UUID,
    completion_percentage: Optional[int] = None,
    content: Optional[dict] = None,
    db: Session = Depends(get_db),
):
    """Update report section"""
    try:
        from app.models import ReportSection

        section = db.query(ReportSection).filter(ReportSection.id == section_id).first()
        if not section:
            raise ValueError("Section not found")

        if completion_percentage is not None:
            section.completion_percentage = min(100, max(0, completion_percentage))
        if content is not None:
            section.content = content

        db.commit()

        return {
            "success": True,
            "data": {
                "id": str(section.id),
                "completion_percentage": section.completion_percentage,
                "updated_at": section.updated_at.isoformat(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Audit Trail Endpoints
# ============================================================================


@router.get("/organizations/{org_id}/audit-trail")
async def get_audit_trail(
    org_id: UUID,
    days: int = 90,
    db: Session = Depends(get_db),
):
    """Get audit trail for organization"""
    try:
        service = AuditTrailService(db)
        trail = service.get_audit_trail(org_id, days)
        return {"success": True, "data": trail}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/audit-trail/{entity_id}")
async def get_entity_audit_trail(
    org_id: UUID,
    entity_id: UUID,
    db: Session = Depends(get_db),
):
    """Get audit trail for specific entity"""
    try:
        from app.models import ComplianceAuditTrail

        entries = (
            db.query(ComplianceAuditTrail)
            .filter(
                ComplianceAuditTrail.organization_id == org_id,
                ComplianceAuditTrail.entity_id == entity_id,
            )
            .order_by(ComplianceAuditTrail.timestamp.desc())
            .all()
        )

        return {
            "success": True,
            "data": [
                {
                    "action": e.action,
                    "timestamp": e.timestamp.isoformat(),
                    "changed_by": str(e.changed_by_user_id) if e.changed_by_user_id else None,
                    "changes": e.changed_values,
                }
                for e in entries
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Compliance Targets Endpoints
# ============================================================================


@router.post("/organizations/{org_id}/targets")
async def create_compliance_target(
    org_id: UUID,
    target_name: str,
    target_type: str,
    baseline_year: int,
    baseline_value: float,
    target_year: int,
    target_value: float,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
):
    """Create a compliance target"""
    try:
        service = ComplianceTargetService(db)
        result = service.set_target(
            organization_id=org_id,
            tenant_id=UUID(x_tenant_id),
            target_name=target_name,
            target_type=target_type,
            baseline_year=baseline_year,
            baseline_value=Decimal(str(baseline_value)),
            target_year=target_year,
            target_value=Decimal(str(target_value)),
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/targets")
async def get_compliance_targets(
    org_id: UUID,
    db: Session = Depends(get_db),
):
    """List compliance targets"""
    try:
        from app.models import ComplianceTarget

        targets = db.query(ComplianceTarget).filter(ComplianceTarget.organization_id == org_id).all()

        return {
            "success": True,
            "data": [
                {
                    "id": str(t.id),
                    "target_name": t.target_name,
                    "target_type": t.target_type,
                    "baseline_year": t.baseline_year,
                    "target_year": t.target_year,
                    "progress_percentage": t.progress_percentage,
                    "status": t.status,
                }
                for t in targets
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/organizations/{org_id}/targets/{target_id}")
async def update_compliance_target(
    org_id: UUID,
    target_id: UUID,
    current_value: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Update compliance target with progress"""
    try:
        service = ComplianceTargetService(db)
        if current_value is not None:
            result = service.track_progress(target_id, Decimal(str(current_value)))
        else:
            result = service.get_target_status(target_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Benchmarking Endpoints
# ============================================================================


@router.get("/organizations/{org_id}/benchmarks")
async def get_organization_benchmarks(
    org_id: UUID,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
):
    """Get benchmarks for organization"""
    try:
        service = BenchmarkingService(db)
        insights = service.generate_insights(UUID(x_tenant_id))
        return {"success": True, "data": insights}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/peer-comparison")
async def get_peer_comparison(
    org_id: UUID,
    metric_name: str,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
):
    """Get peer comparison for metric"""
    try:
        service = BenchmarkingService(db)
        comparison = service.get_peer_comparison(UUID(x_tenant_id), metric_name)
        return {"success": True, "data": comparison}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
