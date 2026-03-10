"""
API routes for report export functionality

Endpoints:
- POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export/pdf - Export as PDF
- POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export/excel - Export as Excel
- POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export/json - Export as JSON
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from typing import Optional, List, Dict
import logging
import json

from app.database import get_db
from app.models import Report, Organization, Tenant
from app.services.pdf_generator import PDFGenerator
from app.services.excel_generator import ExcelGenerator
from app.services.json_exporter import JSONExporter

router = APIRouter(prefix="/api/v1", tags=["report_export"])
logger = logging.getLogger(__name__)


def _verify_tenant_access(
    tenant_id: UUID,
    report_id: UUID,
    db: Session
) -> Report:
    """
    Verify tenant has access to report

    Args:
        tenant_id: Tenant UUID
        report_id: Report UUID
        db: Database session

    Returns:
        Report object

    Raises:
        HTTPException: If not found or access denied
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.tenant_id == tenant_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


def _get_report_data(report: Report, db: Session) -> tuple:
    """
    Extract report data for export

    Args:
        report: Report object
        db: Database session

    Returns:
        Tuple of (scope_1, scope_2, scope_3, key_metrics, evidence_links)
    """
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == report.organization_id
    ).first()

    # For now, use sample data - in real implementation would fetch from compliance reports
    scope_1 = Decimal("150.50")
    scope_2 = Decimal("200.75")
    scope_3 = Decimal("500.25")

    key_metrics = {
        "pue": 1.45,
        "cue": 48.5,
        "wue": 1.8,
        "ere": 1.6
    }

    evidence_links = [
        {
            "name": "Energy Usage Report Q1 2024",
            "uploaded_at": "2024-01-15",
            "type": "energy_audit",
            "link": "https://example.com/evidence/energy_q1"
        },
        {
            "name": "Carbon Footprint Certification",
            "uploaded_at": "2024-02-20",
            "type": "certification",
            "link": "https://example.com/evidence/carbon_cert"
        }
    ]

    return scope_1, scope_2, scope_3, key_metrics, evidence_links


@router.post("/tenants/{tenant_id}/reports/{report_id}/export/pdf")
async def export_report_pdf(
    tenant_id: UUID,
    report_id: UUID,
    landscape: bool = False,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export report as PDF

    Args:
        tenant_id: Tenant UUID
        report_id: Report UUID
        landscape: Use landscape orientation
        x_user_id: User ID from header
        db: Database session

    Returns:
        PDF file as streaming response

    Raises:
        HTTPException: If validation fails or PDF generation fails
    """
    try:
        # Verify tenant access
        report = _verify_tenant_access(tenant_id, report_id, db)

        # Get report data
        scope_1, scope_2, scope_3, key_metrics, evidence_links = _get_report_data(report, db)

        # Generate PDF
        pdf_generator = PDFGenerator(db)
        pdf_buffer = pdf_generator.generate_pdf(
            report_id=report_id,
            organization_id=report.organization_id,
            scope_1=scope_1,
            scope_2=scope_2,
            scope_3=scope_3,
            key_metrics=key_metrics,
            evidence_links=evidence_links,
            report_status=report.current_state,
            landscape_mode=landscape
        )

        filename = f"report_{report_id}_export.pdf"
        logger.info(f"PDF export generated for report {report_id} by user {x_user_id}")

        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ValueError as e:
        logger.warning(f"Validation error in PDF export: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating PDF for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF report"
        )


@router.post("/tenants/{tenant_id}/reports/{report_id}/export/excel")
async def export_report_excel(
    tenant_id: UUID,
    report_id: UUID,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export report as Excel workbook

    Args:
        tenant_id: Tenant UUID
        report_id: Report UUID
        x_user_id: User ID from header
        db: Database session

    Returns:
        Excel file as streaming response

    Raises:
        HTTPException: If validation fails or Excel generation fails
    """
    try:
        # Verify tenant access
        report = _verify_tenant_access(tenant_id, report_id, db)

        # Get report data
        scope_1, scope_2, scope_3, key_metrics, evidence_links = _get_report_data(report, db)

        # Generate Excel
        excel_generator = ExcelGenerator(db)
        excel_buffer = excel_generator.generate_workbook(
            report_id=report_id,
            organization_id=report.organization_id,
            scope_1=scope_1,
            scope_2=scope_2,
            scope_3=scope_3,
            key_metrics=key_metrics,
            evidence_links=evidence_links
        )

        filename = f"report_{report_id}_export.xlsx"
        logger.info(f"Excel export generated for report {report_id} by user {x_user_id}")

        return StreamingResponse(
            iter([excel_buffer.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ValueError as e:
        logger.warning(f"Validation error in Excel export: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating Excel for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate Excel report"
        )


@router.post("/tenants/{tenant_id}/reports/{report_id}/export/json")
async def export_report_json(
    tenant_id: UUID,
    report_id: UUID,
    format: str = "flat",
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """
    Export report as JSON

    Args:
        tenant_id: Tenant UUID
        report_id: Report UUID
        format: Export format - "flat" or "nested"
        x_user_id: User ID from header
        db: Database session

    Returns:
        JSON response with report data

    Raises:
        HTTPException: If validation fails or JSON generation fails
    """
    try:
        # Verify tenant access
        report = _verify_tenant_access(tenant_id, report_id, db)

        # Validate format
        if format not in ["flat", "nested"]:
            raise ValueError("Format must be 'flat' or 'nested'")

        # Get report data
        scope_1, scope_2, scope_3, key_metrics, evidence_links = _get_report_data(report, db)

        # Generate JSON
        json_exporter = JSONExporter(db)

        if format == "flat":
            json_string = json_exporter.export_flat(
                report_id=report_id,
                organization_id=report.organization_id,
                tenant_id=tenant_id,
                scope_1=scope_1,
                scope_2=scope_2,
                scope_3=scope_3,
                key_metrics=key_metrics,
                evidence_links=evidence_links
            )
        else:  # nested
            json_string = json_exporter.export_nested(
                report_id=report_id,
                organization_id=report.organization_id,
                tenant_id=tenant_id,
                scope_1=scope_1,
                scope_2=scope_2,
                scope_3=scope_3,
                key_metrics=key_metrics,
                evidence_links=evidence_links
            )

        logger.info(f"JSON export (format={format}) generated for report {report_id} by user {x_user_id}")

        return {
            "success": True,
            "message": f"Report exported successfully as {format} JSON",
            "report_id": str(report_id),
            "export_format": format,
            "data": json.loads(json_string)
        }

    except ValueError as e:
        logger.warning(f"Validation error in JSON export: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating JSON for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate JSON report"
        )


@router.get("/tenants/{tenant_id}/reports/{report_id}/export/status")
async def get_export_status(
    tenant_id: UUID,
    report_id: UUID,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """
    Check export status and available formats

    Args:
        tenant_id: Tenant UUID
        report_id: Report UUID
        x_user_id: User ID from header
        db: Database session

    Returns:
        Export status and available formats

    Raises:
        HTTPException: If report not found
    """
    try:
        report = _verify_tenant_access(tenant_id, report_id, db)

        return {
            "success": True,
            "report_id": str(report_id),
            "available_formats": ["pdf", "excel", "json"],
            "export_formats": {
                "pdf": {
                    "endpoint": f"/api/v1/tenants/{tenant_id}/reports/{report_id}/export/pdf",
                    "description": "Professional PDF report with watermark",
                    "parameters": {"landscape": "boolean"}
                },
                "excel": {
                    "endpoint": f"/api/v1/tenants/{tenant_id}/reports/{report_id}/export/excel",
                    "description": "Excel workbook with multiple sheets",
                    "parameters": {}
                },
                "json": {
                    "endpoint": f"/api/v1/tenants/{tenant_id}/reports/{report_id}/export/json",
                    "description": "JSON export with flat or nested structure",
                    "parameters": {"format": "flat|nested"}
                }
            },
            "report_status": report.current_state
        }

    except Exception as e:
        logger.error(f"Error checking export status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check export status"
        )
