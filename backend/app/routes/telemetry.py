"""Telemetry ingestion and management API routes"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import csv
import io
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.telemetry_service import TelemetryService
from app.schemas import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["telemetry"])


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


@router.post("/tenants/{tenant_id}/telemetry", status_code=201)
async def ingest_reading(
    tenant_id: str,
    reading_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Ingest a single telemetry reading

    Request body:
    {
        "meter_id": "uuid",
        "value": 123.45,
        "unit": "kWh",
        "timestamp": "2026-03-09T22:00:00Z"
    }
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        service = TelemetryService(db)

        timestamp = datetime.fromisoformat(reading_data.get("timestamp", datetime.utcnow().isoformat()))

        result = service.ingest_reading(
            tenant_id=tenant_id,
            meter_id=reading_data["meter_id"],
            value=float(reading_data["value"]),
            timestamp=timestamp,
            unit=reading_data.get("unit", "kWh"),
        )

        if result["status"] == "error":
            return {"status": "error", "message": result["error"]}, 400

        return {
            "status": result["status"],
            "reading_id": result["reading_id"],
            "anomalies_detected": result.get("anomalies", 0),
        }

    except Exception as e:
        logger.error(f"Telemetry ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tenants/{tenant_id}/telemetry/batch", status_code=201)
async def ingest_batch(
    tenant_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Ingest batch of telemetry readings from CSV file

    CSV format:
    meter_id,value,unit,timestamp
    550e8400-e29b-41d4-a716-446655440000,123.45,kWh,2026-03-09T22:00:00Z
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        # Parse CSV file
        contents = await file.read()
        text_stream = io.StringIO(contents.decode())
        reader = csv.DictReader(text_stream)

        readings = []
        for row in reader:
            readings.append(
                {
                    "meter_id": row["meter_id"],
                    "value": float(row["value"]),
                    "unit": row.get("unit", "kWh"),
                    "timestamp": datetime.fromisoformat(row["timestamp"]),
                }
            )

        service = TelemetryService(db)
        result = service.ingest_batch(tenant_id=tenant_id, readings=readings)

        return {
            "total": result["total"],
            "valid": result["valid"],
            "invalid": result["invalid"],
            "ingested": result["ingested"],
            "anomalies_detected": result["anomalies_detected"],
            "errors": result["errors"][:10],  # Return first 10 errors
        }

    except Exception as e:
        logger.error(f"Batch ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/telemetry/latest")
async def get_latest_readings(
    tenant_id: str,
    meter_ids: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get latest readings for meters

    Query parameters:
    - meter_ids: Comma-separated list of meter UUIDs (optional)
    - limit: Number of readings to return (default 100, max 1000)
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        service = TelemetryService(db)

        meter_list = None
        if meter_ids:
            meter_list = meter_ids.split(",")

        readings = service.get_latest_readings(
            tenant_id=tenant_id,
            meter_ids=meter_list,
            limit=limit,
        )

        return {
            "count": len(readings),
            "readings": readings,
        }

    except Exception as e:
        logger.error(f"Error retrieving latest readings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/telemetry/history")
async def get_history(
    tenant_id: str,
    meter_id: str = Query(...),
    start: str = Query(...),
    end: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get historical telemetry readings for a meter

    Query parameters:
    - meter_id: UUID of meter
    - start: Start timestamp (ISO format)
    - end: End timestamp (ISO format)
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        service = TelemetryService(db)
        readings = service.get_history(
            tenant_id=tenant_id,
            meter_id=meter_id,
            start=start_dt,
            end=end_dt,
        )

        return {
            "meter_id": meter_id,
            "start": start,
            "end": end,
            "count": len(readings),
            "readings": readings,
        }

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/telemetry/anomalies")
async def get_anomalies(
    tenant_id: str,
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get detected anomalies

    Query parameters:
    - severity: Filter by severity (low, medium, high, critical)
    - status: Filter by status (open, acknowledged, resolved)
    - limit: Number of anomalies to return
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        service = TelemetryService(db)
        anomalies = service.get_anomalies(
            tenant_id=tenant_id,
            severity=severity,
            status=status or "open",
            limit=limit,
        )

        return {
            "count": len(anomalies),
            "anomalies": anomalies,
        }

    except Exception as e:
        logger.error(f"Error retrieving anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}/telemetry/validation-errors")
async def get_validation_errors(
    tenant_id: str,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get validation errors from telemetry ingestion"""
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        from app.models import TelemetryValidationError

        errors = (
            db.query(TelemetryValidationError)
            .filter_by(tenant_id=tenant_id)
            .order_by(TelemetryValidationError.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "count": len(errors),
            "errors": [
                {
                    "error_id": str(e.id),
                    "meter_id": str(e.meter_id) if e.meter_id else None,
                    "type": e.error_type,
                    "message": e.error_message,
                    "timestamp": e.created_at.isoformat(),
                }
                for e in errors
            ],
        }

    except Exception as e:
        logger.error(f"Error retrieving validation errors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
