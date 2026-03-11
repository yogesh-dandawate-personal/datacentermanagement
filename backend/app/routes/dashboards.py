"""Energy dashboard API routes"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.energy_metrics_service import EnergyMetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["dashboards"])


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


@router.get("/organizations/{org_id}/dashboards/energy")
async def get_energy_dashboard(
    org_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive energy dashboard data

    Returns total consumption, facility breakdown, and trends
    """
    try:
        service = EnergyMetricsService(db)
        dashboard = service.get_energy_dashboard(
            tenant_id=current_user["tenant_id"],
            org_id=org_id,
        )

        return dashboard

    except Exception as e:
        logger.error(f"Error retrieving energy dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/energy")
async def get_energy_metrics(
    period: str = Query("day", description="day, week, month"),
    org_id: Optional[str] = Query(None),
    facility_id: Optional[str] = Query(None),
    days_back: int = Query(7, le=90),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get energy metrics for specified period and facility

    Query parameters:
    - period: 'day', 'week', 'month'
    - org_id: Filter by organization
    - facility_id: Filter by facility
    - days_back: How many days of history (max 90)
    """
    try:
        service = EnergyMetricsService(db)

        if facility_id:
            # Get breakdown by rack for facility
            breakdown = service.get_site_energy_breakdown(
                tenant_id=current_user["tenant_id"],
                facility_id=facility_id,
            )
            return {
                "period": period,
                "facility_id": facility_id,
                "breakdown": breakdown,
            }
        elif org_id:
            # Get consumption metrics for organization
            consumption = service.get_total_consumption(
                tenant_id=current_user["tenant_id"],
                org_id=org_id,
                period=period,
                days_back=days_back,
            )
            return {
                "period": period,
                "org_id": org_id,
                "metrics": consumption,
            }
        else:
            raise HTTPException(status_code=400, detail="Must provide org_id or facility_id")

    except Exception as e:
        logger.error(f"Error retrieving energy metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facilities/{facility_id}/energy/efficiency")
async def get_facility_efficiency(
    facility_id: str,
    days_back: int = Query(7, le=90),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get efficiency metrics for a facility

    Returns:
    {
        "watts_per_server": float,
        "kwh_per_device": float,
        "pue": float
    }
    """
    try:
        service = EnergyMetricsService(db)
        metrics = service.get_efficiency_metrics(
            tenant_id=current_user["tenant_id"],
            facility_id=facility_id,
            days_back=days_back,
        )

        return {
            "facility_id": facility_id,
            "efficiency_metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Error retrieving efficiency metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meters/{meter_id}/energy/peak-usage")
async def get_meter_peak_usage(
    meter_id: str,
    days_back: int = Query(30, le=365),
    limit: int = Query(10, le=100),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get peak usage periods for a meter

    Returns top N peak usage timestamps and values
    """
    try:
        service = EnergyMetricsService(db)
        peaks = service.get_peak_usage(
            tenant_id=current_user["tenant_id"],
            meter_id=meter_id,
            days_back=days_back,
            limit=limit,
        )

        return {
            "meter_id": meter_id,
            "period_days": days_back,
            "peak_usage": peaks,
        }

    except Exception as e:
        logger.error(f"Error retrieving peak usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
