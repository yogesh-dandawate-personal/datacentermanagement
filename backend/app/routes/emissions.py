"""
Emissions API Routes

REST API for emissions management:
- Sources CRUD
- Activity data submission (single/batch)
- Calculations (trigger, query, approve)
- Analytics (dashboard, trends, breakdown)
- Reporting (generate, download)
- Targets (CRUD, progress tracking)
- Alerts (CRUD rules, manage)
"""

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import io
import logging

from app.database import get_db
from app.auth.security import get_current_user
from app.models import (
    EmissionsSource, EmissionsActivityData, EmissionsCalculation,
    EmissionsReport, EmissionsTarget, EmissionsAlert, EmissionsAlertRule
)
from app.services.emissions_calculation_service import EmissionsCalculationService
from app.services.emissions_ingestion_service import EmissionsIngestionService
from app.services.emissions_analytics_service import EmissionsAnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/emissions", tags=["emissions"])


# ============================================================================
# EMISSIONS SOURCES ENDPOINTS
# ============================================================================

@router.get("/organizations/{org_id}/sources")
async def get_emission_sources(
    org_id: str,
    facility_id: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get emission sources for organization"""
    try:
        query = db.query(EmissionsSource).filter(
            EmissionsSource.organization_id == org_id,
            EmissionsSource.tenant_id == current_user["tenant_id"]
        )

        if facility_id:
            query = query.filter(EmissionsSource.facility_id == facility_id)

        if scope:
            query = query.filter(EmissionsSource.scope == scope)

        if is_active is not None:
            query = query.filter(EmissionsSource.is_active == is_active)

        sources = query.all()

        return {
            "data": [
                {
                    "id": str(s.id),
                    "source_name": s.source_name,
                    "source_type": s.source_type,
                    "scope": s.scope,
                    "facility_id": str(s.facility_id) if s.facility_id else None,
                    "unit_of_measure": s.unit_of_measure,
                    "is_active": s.is_active,
                    "created_at": s.created_at.isoformat()
                }
                for s in sources
            ],
            "count": len(sources)
        }

    except Exception as e:
        logger.error(f"Error getting emission sources: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/sources")
async def create_emission_source(
    org_id: str,
    source_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new emission source"""
    try:
        source = EmissionsSource(
            tenant_id=current_user["tenant_id"],
            organization_id=org_id,
            source_name=source_data["source_name"],
            source_type=source_data["source_type"],
            scope=source_data["scope"],
            facility_id=source_data.get("facility_id"),
            unit_of_measure=source_data.get("unit_of_measure", "kWh"),
            description=source_data.get("description")
        )

        db.add(source)
        db.commit()

        return {
            "id": str(source.id),
            "source_name": source.source_name,
            "scope": source.scope,
            "status": "created"
        }

    except Exception as e:
        logger.error(f"Error creating emission source: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ACTIVITY DATA ENDPOINTS
# ============================================================================

@router.post("/organizations/{org_id}/activity-data")
async def submit_activity_data(
    org_id: str,
    source_id: str,
    timestamp: datetime,
    activity_value: Decimal,
    activity_unit: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Submit single activity data reading"""
    try:
        service = EmissionsIngestionService(db)

        result = service.ingest_single_reading(
            tenant_id=current_user["tenant_id"],
            source_id=source_id,
            timestamp=timestamp,
            activity_value=activity_value,
            activity_unit=activity_unit
        )

        return result

    except Exception as e:
        logger.error(f"Error submitting activity data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/activity-data/batch")
async def upload_batch_file(
    org_id: str,
    file: UploadFile = File(...),
    source_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload batch CSV file with activity data"""
    try:
        service = EmissionsIngestionService(db)

        # Read file content
        content = await file.read()

        # Determine format
        file_format = "csv" if file.filename.endswith(".csv") else "csv"

        result = service.ingest_batch_file(
            tenant_id=current_user["tenant_id"],
            file_content=content,
            source_id=source_id,
            file_format=file_format,
            ingestion_method="csv_upload"
        )

        return result

    except Exception as e:
        logger.error(f"Error uploading batch file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/activity-data")
async def get_activity_data(
    org_id: str,
    source_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Query activity data with filters"""
    try:
        query = db.query(EmissionsActivityData).filter(
            EmissionsActivityData.tenant_id == current_user["tenant_id"]
        )

        if source_id:
            query = query.filter(EmissionsActivityData.source_id == source_id)

        if start_date:
            query = query.filter(EmissionsActivityData.timestamp >= start_date)

        if end_date:
            query = query.filter(EmissionsActivityData.timestamp <= end_date)

        total = query.count()
        data = query.order_by(EmissionsActivityData.timestamp.desc()).offset(offset).limit(limit).all()

        return {
            "data": [
                {
                    "id": str(d.id),
                    "source_id": str(d.source_id),
                    "timestamp": d.timestamp.isoformat(),
                    "activity_value": float(d.activity_value),
                    "activity_unit": d.activity_unit,
                    "validation_status": d.validation_status
                }
                for d in data
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error querying activity data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# CALCULATIONS ENDPOINTS
# ============================================================================

@router.post("/organizations/{org_id}/calculate/scope1")
async def calculate_scope1(
    org_id: str,
    source_id: str,
    period_start: datetime,
    period_end: datetime,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Trigger Scope 1 emissions calculation"""
    try:
        service = EmissionsCalculationService(db)

        result = service.calculate_scope_1_emissions(
            tenant_id=current_user["tenant_id"],
            source_id=source_id,
            period_start=period_start,
            period_end=period_end,
            created_by_user_id=current_user["user_id"]
        )

        return result

    except Exception as e:
        logger.error(f"Error calculating Scope 1: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/calculate/scope2")
async def calculate_scope2(
    org_id: str,
    source_id: str,
    period_start: datetime,
    period_end: datetime,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Trigger Scope 2 emissions calculation"""
    try:
        service = EmissionsCalculationService(db)

        result = service.calculate_scope_2_location_based(
            tenant_id=current_user["tenant_id"],
            source_id=source_id,
            period_start=period_start,
            period_end=period_end,
            created_by_user_id=current_user["user_id"]
        )

        return result

    except Exception as e:
        logger.error(f"Error calculating Scope 2: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/calculate/scope3")
async def calculate_scope3(
    org_id: str,
    source_id: str,
    period_start: datetime,
    period_end: datetime,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Trigger Scope 3 emissions calculation"""
    try:
        service = EmissionsCalculationService(db)

        result = service.calculate_scope_3_emissions(
            tenant_id=current_user["tenant_id"],
            source_id=source_id,
            period_start=period_start,
            period_end=period_end,
            created_by_user_id=current_user["user_id"]
        )

        return result

    except Exception as e:
        logger.error(f"Error calculating Scope 3: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/calculations")
async def get_calculations(
    org_id: str,
    scope: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Query calculations with filters"""
    try:
        query = db.query(EmissionsCalculation).filter(
            EmissionsCalculation.organization_id == org_id,
            EmissionsCalculation.tenant_id == current_user["tenant_id"]
        )

        if scope:
            query = query.filter(EmissionsCalculation.scope == scope)

        if status:
            query = query.filter(EmissionsCalculation.status == status)

        calculations = query.order_by(EmissionsCalculation.created_at.desc()).limit(limit).all()

        return {
            "data": [
                {
                    "id": str(c.id),
                    "scope": c.scope,
                    "total_emissions_tco2e": float(c.total_emissions_kgco2e / 1000),
                    "status": c.status,
                    "period_start": c.calculation_period_start.isoformat(),
                    "period_end": c.calculation_period_end.isoformat(),
                    "created_at": c.created_at.isoformat()
                }
                for c in calculations
            ],
            "count": len(calculations)
        }

    except Exception as e:
        logger.error(f"Error querying calculations: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/facilities/{facility_id}/dashboard")
async def get_facility_dashboard(
    facility_id: str,
    period: str = Query("current_month"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get facility emissions dashboard"""
    try:
        service = EmissionsAnalyticsService(db)

        dashboard = service.get_facility_dashboard_data(
            tenant_id=current_user["tenant_id"],
            facility_id=facility_id,
            period=period
        )

        return dashboard

    except Exception as e:
        logger.error(f"Error getting facility dashboard: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/portfolio")
async def get_portfolio_overview(
    org_id: str,
    period: str = Query("current_year"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get portfolio-wide emissions overview"""
    try:
        service = EmissionsAnalyticsService(db)

        portfolio = service.get_portfolio_overview(
            tenant_id=current_user["tenant_id"],
            period=period
        )

        return portfolio

    except Exception as e:
        logger.error(f"Error getting portfolio overview: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# TARGETS ENDPOINTS
# ============================================================================

@router.get("/organizations/{org_id}/targets")
async def get_emission_targets(
    org_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get emission reduction targets"""
    try:
        targets = db.query(EmissionsTarget).filter(
            EmissionsTarget.organization_id == org_id,
            EmissionsTarget.tenant_id == current_user["tenant_id"]
        ).all()

        return {
            "data": [
                {
                    "id": str(t.id),
                    "target_name": t.target_name,
                    "target_year": t.target_year,
                    "baseline_value": float(t.baseline_value),
                    "target_value": float(t.target_value),
                    "progress_percentage": t.progress_percentage,
                    "status": t.status
                }
                for t in targets
            ],
            "count": len(targets)
        }

    except Exception as e:
        logger.error(f"Error getting targets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/targets")
async def create_emission_target(
    org_id: str,
    target_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create emission reduction target"""
    try:
        target = EmissionsTarget(
            tenant_id=current_user["tenant_id"],
            organization_id=org_id,
            target_name=target_data["target_name"],
            target_type=target_data.get("target_type", "absolute_reduction"),
            baseline_year=target_data["baseline_year"],
            baseline_value=Decimal(str(target_data["baseline_value"])),
            target_year=target_data["target_year"],
            target_value=Decimal(str(target_data["target_value"])),
            scope=target_data.get("scope")
        )

        db.add(target)
        db.commit()

        return {
            "id": str(target.id),
            "target_name": target.target_name,
            "status": "created"
        }

    except Exception as e:
        logger.error(f"Error creating target: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@router.get("/organizations/{org_id}/alerts")
async def get_emissions_alerts(
    org_id: str,
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get emission alerts"""
    try:
        query = db.query(EmissionsAlert).filter(
            EmissionsAlert.organization_id == org_id,
            EmissionsAlert.tenant_id == current_user["tenant_id"]
        )

        if severity:
            query = query.filter(EmissionsAlert.severity == severity)

        if status:
            query = query.filter(EmissionsAlert.status == status)

        alerts = query.order_by(EmissionsAlert.triggered_at.desc()).limit(limit).all()

        return {
            "data": [
                {
                    "id": str(a.id),
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "status": a.status,
                    "triggered_at": a.triggered_at.isoformat(),
                    "triggered_value": float(a.triggered_value) if a.triggered_value else None
                }
                for a in alerts
            ],
            "count": len(alerts)
        }

    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/organizations/{org_id}/alert-rules")
async def get_alert_rules(
    org_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get alert rule definitions"""
    try:
        rules = db.query(EmissionsAlertRule).filter(
            EmissionsAlertRule.organization_id == org_id,
            EmissionsAlertRule.tenant_id == current_user["tenant_id"]
        ).all()

        return {
            "data": [
                {
                    "id": str(r.id),
                    "rule_name": r.rule_name,
                    "metric": r.metric,
                    "operator": r.operator,
                    "threshold_value": float(r.threshold_value),
                    "severity": r.severity,
                    "is_enabled": r.is_enabled
                }
                for r in rules
            ],
            "count": len(rules)
        }

    except Exception as e:
        logger.error(f"Error getting alert rules: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations/{org_id}/alert-rules")
async def create_alert_rule(
    org_id: str,
    rule_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create alert rule"""
    try:
        rule = EmissionsAlertRule(
            tenant_id=current_user["tenant_id"],
            organization_id=org_id,
            rule_name=rule_data["rule_name"],
            metric=rule_data["metric"],
            operator=rule_data["operator"],
            threshold_value=Decimal(str(rule_data["threshold_value"])),
            severity=rule_data.get("severity", "warning"),
            notification_channels=rule_data.get("notification_channels", ["email"])
        )

        db.add(rule)
        db.commit()

        return {
            "id": str(rule.id),
            "rule_name": rule.rule_name,
            "status": "created"
        }

    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
