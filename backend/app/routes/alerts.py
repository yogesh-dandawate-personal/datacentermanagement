"""
Alert and Prediction Routes
SPRINT 10 - AGENT 3 & 4: Alert Management

Endpoints:
- GET /api/v1/alerts/predictions - Get predictive alerts
- POST /api/v1/alerts/configure - Configure threshold
- GET /api/v1/alerts/active - Get active breaches
- POST /api/v1/alerts/{breach_id}/acknowledge - Acknowledge breach
- POST /api/v1/alerts/{breach_id}/resolve - Resolve breach
- GET /api/v1/alerts/history - Get breach history
"""
from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.predictive_alerts import PredictiveAlertEngine
from app.services.threshold_monitor import ThresholdMonitor, ThresholdConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class ThresholdConfigRequest(BaseModel):
    kpi_id: str
    metric_name: str
    threshold_value: float
    operator: str  # >, <, >=, <=, ==, !=
    severity: str  # info, warning, critical
    notify_email: bool = True
    notify_slack: bool = False


class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


class ResolveRequest(BaseModel):
    notes: str


@router.get("/predictions")
async def get_predictive_alerts(
    facility_id: Optional[str] = Query(None),
    metric_type: Optional[str] = Query(None),
    authorization: str = Header(None),
):
    """
    Get predictive alerts for potential threshold breaches

    Query Parameters:
        facility_id: Optional facility filter
        metric_type: Optional metric type filter (energy, carbon, water, etc.)

    Returns:
        List of predictions and alerts
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        tenant_id = token_data.tenant_id

        # Get historical data from database
        # For demo purposes, using mock data
        historical_data = [
            {'timestamp': datetime.utcnow() - timedelta(hours=i), 'value': 1200 + i * 10}
            for i in range(168)  # 7 days of hourly data
        ]

        # Initialize predictive engine
        engine = PredictiveAlertEngine()

        # Predict threshold breach
        prediction = engine.predict_threshold_breach(
            historical_data=historical_data,
            threshold_value=1500.0,
            metric_name='Energy Consumption',
        )

        predictions = []
        if prediction and prediction.confidence >= engine.confidence_threshold:
            alert = engine.create_alert(
                alert_type='threshold_breach',
                metric_name='Energy Consumption',
                current_value=historical_data[-1]['value'],
                prediction=prediction,
                threshold_value=1500.0,
            )

            predictions.append({
                'alert': {
                    'alert_id': alert.alert_id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'priority_score': alert.priority_score,
                    'message': alert.message,
                },
                'prediction': {
                    'predicted_value': prediction.predicted_value,
                    'confidence': prediction.confidence,
                    'threshold_breach_probability': prediction.threshold_breach_probability,
                    'predicted_for': prediction.predicted_for.isoformat(),
                },
            })

        return {
            'status': 'ok',
            'predictions': predictions,
            'count': len(predictions),
        }

    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure")
async def configure_threshold(
    config: ThresholdConfigRequest,
    authorization: str = Header(None),
):
    """
    Configure a new threshold or update existing

    Body:
        ThresholdConfigRequest with threshold configuration

    Returns:
        Created threshold ID
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)

        db = next(get_db())
        monitor = ThresholdMonitor(db)

        threshold_config = ThresholdConfig(
            metric_name=config.metric_name,
            threshold_value=config.threshold_value,
            operator=config.operator,
            severity=config.severity,
            notify_email=config.notify_email,
            notify_slack=config.notify_slack,
        )

        threshold_id = monitor.configure_threshold(
            kpi_id=config.kpi_id,
            threshold_config=threshold_config,
        )

        if not threshold_id:
            raise HTTPException(status_code=500, detail="Failed to configure threshold")

        return {
            'status': 'ok',
            'threshold_id': threshold_id,
            'message': 'Threshold configured successfully',
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_breaches(
    facility_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    authorization: str = Header(None),
):
    """
    Get all active (unresolved) threshold breaches

    Query Parameters:
        facility_id: Optional facility filter
        severity: Optional severity filter (info, warning, critical)

    Returns:
        List of active breaches
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        tenant_id = token_data.tenant_id

        db = next(get_db())
        monitor = ThresholdMonitor(db)

        breaches = monitor.get_active_breaches(
            tenant_id=tenant_id,
            facility_id=facility_id,
            severity=severity,
        )

        return {
            'status': 'ok',
            'breaches': breaches,
            'count': len(breaches),
        }

    except Exception as e:
        logger.error(f"Error getting active breaches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{breach_id}/acknowledge")
async def acknowledge_breach(
    breach_id: str,
    request: AcknowledgeRequest,
    authorization: str = Header(None),
):
    """
    Acknowledge a threshold breach

    Path Parameters:
        breach_id: Breach ID to acknowledge

    Body:
        notes: Optional acknowledgement notes

    Returns:
        Acknowledgement confirmation
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        user_id = token_data.sub

        db = next(get_db())
        monitor = ThresholdMonitor(db)

        success = monitor.acknowledge_breach(
            breach_id=breach_id,
            user_id=user_id,
            notes=request.notes,
        )

        if not success:
            raise HTTPException(status_code=404, detail="Breach not found")

        return {
            'status': 'ok',
            'breach_id': breach_id,
            'message': 'Breach acknowledged successfully',
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging breach: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{breach_id}/resolve")
async def resolve_breach(
    breach_id: str,
    request: ResolveRequest,
    authorization: str = Header(None),
):
    """
    Resolve a threshold breach

    Path Parameters:
        breach_id: Breach ID to resolve

    Body:
        notes: Resolution notes (required)

    Returns:
        Resolution confirmation
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        user_id = token_data.sub

        db = next(get_db())
        monitor = ThresholdMonitor(db)

        success = monitor.resolve_breach(
            breach_id=breach_id,
            user_id=user_id,
            notes=request.notes,
        )

        if not success:
            raise HTTPException(status_code=404, detail="Breach not found")

        return {
            'status': 'ok',
            'breach_id': breach_id,
            'message': 'Breach resolved successfully',
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving breach: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_breach_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    authorization: str = Header(None),
):
    """
    Get historical threshold breaches

    Query Parameters:
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results (1-1000, default 100)

    Returns:
        List of historical breaches
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        tenant_id = token_data.tenant_id

        db = next(get_db())
        monitor = ThresholdMonitor(db)

        history = monitor.get_breach_history(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        return {
            'status': 'ok',
            'history': history,
            'count': len(history),
        }

    except Exception as e:
        logger.error(f"Error getting breach history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
