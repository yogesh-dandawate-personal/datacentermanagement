"""
KPI (Key Performance Indicator) API Routes

Endpoints for:
- KPI definitions (CRUD operations)
- KPI calculations and snapshots
- Threshold management
- Breach tracking and acknowledgement
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.kpi_service import KPICalculationService, KPIThresholdService, STANDARD_KPIS
from app.models import KPIDefinition, KPISnapshot, KPIThreshold, KPIThresholdBreach

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["kpi"])


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


@router.get("/organizations/{org_id}/kpis")
async def list_kpis(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all KPIs for an organization

    Returns both standard and custom KPI definitions
    """
    try:
        kpis = (
            db.query(KPIDefinition)
            .filter_by(organization_id=org_id, is_active=True)
            .order_by(KPIDefinition.kpi_name)
            .all()
        )

        return {
            "count": len(kpis),
            "kpis": [
                {
                    "id": str(kpi.id),
                    "name": kpi.kpi_name,
                    "type": kpi.kpi_type,
                    "formula": kpi.formula,
                    "unit": kpi.unit,
                    "target_value": float(kpi.target_value) if kpi.target_value else None,
                    "lower_bound": float(kpi.lower_bound) if kpi.lower_bound else None,
                    "upper_bound": float(kpi.upper_bound) if kpi.upper_bound else None,
                    "created_at": kpi.created_at.isoformat(),
                }
                for kpi in kpis
            ],
        }

    except Exception as e:
        logger.error(f"Error listing KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}")
async def get_kpi(
    kpi_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get detailed KPI definition with latest snapshot

    Returns KPI metadata and most recent data point
    """
    try:
        kpi = db.query(KPIDefinition).filter_by(id=kpi_id).first()
        if not kpi:
            raise HTTPException(status_code=404, detail="KPI not found")

        # Get latest snapshot
        latest_snapshot = (
            db.query(KPISnapshot)
            .filter_by(kpi_id=kpi_id)
            .order_by(KPISnapshot.snapshot_date.desc())
            .first()
        )

        # Get active thresholds
        thresholds = (
            db.query(KPIThreshold)
            .filter_by(kpi_id=kpi_id, is_enabled=True)
            .all()
        )

        return {
            "id": str(kpi.id),
            "name": kpi.kpi_name,
            "type": kpi.kpi_type,
            "formula": kpi.formula,
            "unit": kpi.unit,
            "target_value": float(kpi.target_value) if kpi.target_value else None,
            "lower_bound": float(kpi.lower_bound) if kpi.lower_bound else None,
            "upper_bound": float(kpi.upper_bound) if kpi.upper_bound else None,
            "latest_snapshot": {
                "value": float(latest_snapshot.calculated_value),
                "target": float(latest_snapshot.target_value) if latest_snapshot.target_value else None,
                "status": latest_snapshot.status,
                "variance_percent": float(latest_snapshot.variance_percent) if latest_snapshot.variance_percent else None,
                "timestamp": latest_snapshot.snapshot_date.isoformat(),
            } if latest_snapshot else None,
            "thresholds": [
                {
                    "id": str(t.id),
                    "name": t.threshold_name,
                    "value": float(t.threshold_value),
                    "operator": t.operator,
                    "severity": t.alert_severity,
                }
                for t in thresholds
            ],
            "created_at": kpi.created_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving KPI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/organizations/{org_id}/kpis/{kpi_name}/calculate")
async def calculate_kpi(
    org_id: str,
    kpi_name: str,
    period_days: int = Query(7),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate a KPI value for an organization

    Query parameters:
    - period_days: Number of days to look back for calculation (default: 7)

    Supports: PUE, CUE, WUE, ERE, and custom KPIs
    """
    try:
        # Find KPI definition
        kpi = (
            db.query(KPIDefinition)
            .filter_by(organization_id=org_id, kpi_name=kpi_name, is_active=True)
            .first()
        )
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI {kpi_name} not found")

        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        calc_service = KPICalculationService(db)

        # Calculate based on KPI type
        if kpi_name == "PUE":
            calculated_value, details = calc_service.calculate_pue(
                org_id, period_start, period_end
            )
        elif kpi_name == "CUE":
            calculated_value, details = calc_service.calculate_cue(
                org_id, period_start, period_end
            )
        elif kpi_name == "WUE":
            calculated_value, details = calc_service.calculate_wue(
                org_id, period_start, period_end
            )
        elif kpi_name == "ERE":
            calculated_value, details = calc_service.calculate_ere(
                org_id, period_start, period_end
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown KPI type: {kpi_name}")

        # Create snapshot
        snapshot = calc_service.create_snapshot(
            kpi_id=str(kpi.id),
            organization_id=org_id,
            tenant_id=current_user["tenant_id"],
            kpi_name=kpi_name,
            calculated_value=calculated_value,
            target_value=kpi.target_value or 0,
            calculation_details=details,
        )

        # Check thresholds for breaches
        threshold_service = KPIThresholdService(db)
        breaches = threshold_service.check_breaches(
            kpi_id=str(kpi.id),
            snapshot_id=str(snapshot.id),
            calculated_value=calculated_value,
            target_value=kpi.target_value or 0,
        )

        return {
            "kpi_name": kpi_name,
            "calculated_value": float(calculated_value),
            "target_value": float(kpi.target_value) if kpi.target_value else None,
            "unit": kpi.unit,
            "status": snapshot.status,
            "variance_percent": float(snapshot.variance_percent) if snapshot.variance_percent else None,
            "calculation_details": details,
            "threshold_breaches": len(breaches),
            "timestamp": snapshot.snapshot_date.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating KPI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}/snapshots")
async def get_kpi_snapshots(
    kpi_id: str,
    days: int = Query(30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get historical KPI snapshots for trend analysis

    Query parameters:
    - days: Number of days to retrieve (default: 30)

    Returns time-series data for charting and analysis
    """
    try:
        calc_service = KPICalculationService(db)
        snapshots = calc_service.get_snapshot_trend(kpi_id, days=days)

        return {
            "kpi_id": kpi_id,
            "period_days": days,
            "snapshot_count": len(snapshots),
            "snapshots": snapshots,
        }

    except Exception as e:
        logger.error(f"Error retrieving snapshots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kpis/{kpi_id}/thresholds")
async def create_threshold(
    kpi_id: str,
    threshold_name: str = Query(...),
    threshold_value: float = Query(...),
    operator: str = Query(...),  # >, <, >=, <=, ==, !=
    alert_severity: str = Query("warning"),  # info, warning, critical
    notify_email: bool = Query(True),
    notify_slack: bool = Query(False),
    notify_webhook: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create an alerting threshold for a KPI

    Operators: >, <, >=, <=, ==, !=
    Severity levels: info, warning, critical
    """
    try:
        # Verify KPI exists
        kpi = db.query(KPIDefinition).filter_by(id=kpi_id).first()
        if not kpi:
            raise HTTPException(status_code=404, detail="KPI not found")

        threshold_service = KPIThresholdService(db)
        threshold = threshold_service.create_threshold(
            kpi_id=kpi_id,
            threshold_name=threshold_name,
            threshold_value=threshold_value,
            operator=operator,
            alert_severity=alert_severity,
            notify_email=notify_email,
            notify_slack=notify_slack,
            notify_webhook=notify_webhook,
        )

        return {
            "id": str(threshold.id),
            "kpi_id": str(threshold.kpi_id),
            "name": threshold.threshold_name,
            "value": float(threshold.threshold_value),
            "operator": threshold.operator,
            "severity": threshold.alert_severity,
            "created_at": threshold.created_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}/thresholds")
async def list_thresholds(
    kpi_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all thresholds for a KPI
    """
    try:
        thresholds = (
            db.query(KPIThreshold)
            .filter_by(kpi_id=kpi_id)
            .order_by(KPIThreshold.created_at)
            .all()
        )

        return {
            "kpi_id": kpi_id,
            "count": len(thresholds),
            "thresholds": [
                {
                    "id": str(t.id),
                    "name": t.threshold_name,
                    "value": float(t.threshold_value),
                    "operator": t.operator,
                    "severity": t.alert_severity,
                    "is_enabled": t.is_enabled,
                    "notify_email": t.notify_email,
                    "notify_slack": t.notify_slack,
                    "created_at": t.created_at.isoformat(),
                }
                for t in thresholds
            ],
        }

    except Exception as e:
        logger.error(f"Error listing thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}/breaches")
async def get_breaches(
    kpi_id: str,
    status: Optional[str] = Query(None),  # open, acknowledged, resolved
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get threshold breach history for a KPI

    Query parameters:
    - status: Filter by breach status (open, acknowledged, resolved)
    - limit: Maximum number of breaches to return (default: 100)
    """
    try:
        threshold_service = KPIThresholdService(db)
        breaches = threshold_service.get_breaches(
            kpi_id=kpi_id,
            status=status,
            limit=limit,
        )

        return {
            "kpi_id": kpi_id,
            "count": len(breaches),
            "breaches": breaches,
        }

    except Exception as e:
        logger.error(f"Error retrieving breaches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/breaches/{breach_id}/acknowledge")
async def acknowledge_breach(
    breach_id: str,
    resolution_notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Acknowledge a threshold breach

    Marks breach as acknowledged and records who acknowledged it
    """
    try:
        threshold_service = KPIThresholdService(db)
        breach = threshold_service.acknowledge_breach(
            breach_id=breach_id,
            acknowledged_by=current_user["user_id"],
            resolution_notes=resolution_notes,
        )

        return {
            "id": str(breach.id),
            "status": breach.status,
            "acknowledged_by": str(breach.acknowledged_by),
            "acknowledged_at": breach.acknowledged_at.isoformat(),
            "resolution_notes": breach.resolution_notes,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error acknowledging breach: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/standard/list")
async def list_standard_kpis():
    """
    List available standard KPI definitions

    Returns metadata for standard industry KPIs: PUE, CUE, WUE, ERE
    """
    return {
        "count": len(STANDARD_KPIS),
        "standard_kpis": [
            {
                "name": name,
                "full_name": data["name"],
                "formula": data["formula"],
                "unit": data["unit"],
                "target": data["target"],
                "recommended_range": {
                    "lower": data["lower_bound"],
                    "upper": data["upper_bound"],
                },
            }
            for name, data in STANDARD_KPIS.items()
        ],
    }
