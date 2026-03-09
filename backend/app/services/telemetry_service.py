"""
Telemetry ingestion, validation, and normalization service

This module provides:
- ValidationService: Validates telemetry readings against device specs
- NormalizationService: Normalizes units, timestamps, and precision
- AnomalyDetectionService: Detects stale feeds and outliers
- TelemetryService: Main orchestration service for the complete pipeline
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    TelemetryReading,
    TelemetryValidationError,
    TelemetryAnomaly,
    Meter,
    Device,
    DeviceSpecification,
)

logger = logging.getLogger(__name__)

# Constants
STALE_FEED_THRESHOLD = timedelta(hours=1)
OUTLIER_Z_SCORE_THRESHOLD = 3.0
MIN_READINGS_FOR_OUTLIER_DETECTION = 5
OUTLIER_CRITICAL_THRESHOLD = 5.0


class ValidationService:
    """Validates telemetry data against device specifications"""

    @staticmethod
    def validate_reading(
        db: Session,
        meter_id: str,
        value: float,
        timestamp: datetime,
        unit: str,
        tenant_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a telemetry reading against device specifications

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check meter exists and belongs to tenant
        meter = db.query(Meter).filter_by(id=meter_id, tenant_id=tenant_id).first()
        if not meter:
            return False, f"Meter {meter_id} not found for tenant"

        # Check device exists
        device = db.query(Device).filter_by(id=meter.device_id).first()
        if not device:
            return False, f"Device for meter {meter_id} not found"

        # Type validation
        if not isinstance(value, (int, float)):
            return False, f"Value must be numeric, got {type(value).__name__}"

        # Range validation against device specifications
        specs = (
            db.query(DeviceSpecification)
            .filter_by(device_id=device.id)
            .filter(DeviceSpecification.spec_key.in_(["min_value", "max_value"]))
            .all()
        )

        spec_dict = {spec.spec_key: float(spec.spec_value) for spec in specs}

        if "min_value" in spec_dict and value < spec_dict["min_value"]:
            return False, f"Value {value} below minimum {spec_dict['min_value']}"

        if "max_value" in spec_dict and value > spec_dict["max_value"]:
            return False, f"Value {value} above maximum {spec_dict['max_value']}"

        # Timestamp validation
        if timestamp > datetime.utcnow():
            return False, "Timestamp cannot be in the future"

        # Unit validation
        if unit and unit not in ["kW", "kWh", "C", "RH", "Pa", "lpm"]:
            return False, f"Unknown unit: {unit}"

        return True, None

    @staticmethod
    def validate_batch(
        db: Session, tenant_id: str, readings: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate a batch of readings

        Returns:
            Tuple of (valid_readings, invalid_readings_with_errors)
        """
        valid = []
        invalid = []

        for idx, reading in enumerate(readings):
            try:
                meter_id = reading.get("meter_id")
                value = reading.get("value")
                timestamp = reading.get("timestamp")
                unit = reading.get("unit", "kWh")

                is_valid, error_msg = ValidationService.validate_reading(
                    db, meter_id, value, timestamp, unit, tenant_id
                )

                if is_valid:
                    valid.append(reading)
                else:
                    invalid.append({"index": idx, "error": error_msg, "data": reading})

            except Exception as e:
                invalid.append(
                    {
                        "index": idx,
                        "error": str(e),
                        "data": reading,
                    }
                )

        return valid, invalid


class NormalizationService:
    """Normalizes telemetry readings (units, timezone, timestamps, precision)"""

    # Unit conversion factors (all to kWh base)
    UNIT_CONVERSIONS = {
        "kWh": 1.0,
        "kW": 1.0,  # Will need time interval for conversion
        "Wh": 0.001,
        "W": 0.001,
        "MWh": 1000.0,
        "MW": 1000.0,
        "C": 1.0,  # Celsius (no conversion needed, pass-through)
        "RH": 1.0,  # Relative Humidity (pass-through)
        "Pa": 1.0,  # Pascal (pass-through)
        "lpm": 1.0,  # Liters per minute (pass-through)
    }

    @staticmethod
    def convert_unit(
        value: float, from_unit: str, to_unit: str = "kWh"
    ) -> float:
        """
        Convert value from one unit to another

        For power (kW) to energy (kWh), assumes 1 hour interval
        """
        if from_unit == to_unit:
            return value

        # Energy conversions
        if from_unit in ["kW", "W"] and to_unit in ["kWh", "Wh"]:
            # Assume 1-hour reading interval
            value = value * 1  # 1 hour
            from_unit = "kWh" if from_unit == "kW" else "Wh"

        # Convert to base unit (kWh)
        if from_unit in NormalizationService.UNIT_CONVERSIONS:
            value *= NormalizationService.UNIT_CONVERSIONS[from_unit]

        # Convert from base unit
        if to_unit in NormalizationService.UNIT_CONVERSIONS:
            value /= NormalizationService.UNIT_CONVERSIONS[to_unit]

        return value

    @staticmethod
    def normalize_timestamp(timestamp: datetime) -> datetime:
        """Normalize timestamp to UTC"""
        if timestamp.tzinfo is not None:
            return timestamp.astimezone(None).replace(tzinfo=None)
        return timestamp

    @staticmethod
    def normalize_precision(value: float, decimals: int = 6) -> Decimal:
        """Normalize numeric precision"""
        return Decimal(str(round(value, decimals)))

    @staticmethod
    def normalize_reading(
        value: float,
        from_unit: str,
        to_unit: str = "kWh",
        timestamp: Optional[datetime] = None,
    ) -> Dict:
        """
        Normalize a reading

        Returns dict with normalized value, unit, timestamp
        """
        normalized_value = NormalizationService.convert_unit(value, from_unit, to_unit)
        normalized_timestamp = NormalizationService.normalize_timestamp(
            timestamp or datetime.utcnow()
        )
        normalized_decimal = NormalizationService.normalize_precision(
            normalized_value
        )

        return {
            "value": normalized_decimal,
            "unit": to_unit,
            "timestamp": normalized_timestamp,
        }


class AnomalyDetectionService:
    """
    Detects anomalies in telemetry data

    Detections:
    - Stale feeds: No reading received within threshold period
    - Outliers: Values deviating more than threshold std devs from mean
    """

    @staticmethod
    def detect_stale_feed(
        db: Session, meter_id: str, current_timestamp: datetime
    ) -> Optional[Dict]:
        """
        Detect if meter hasn't reported in the threshold period

        Returns anomaly dict if stale (high severity), None otherwise
        """
        last_reading = (
            db.query(TelemetryReading)
            .filter_by(meter_id=meter_id, status="valid")
            .order_by(TelemetryReading.timestamp.desc())
            .first()
        )

        if not last_reading:
            return None

        time_since_last = current_timestamp - last_reading.timestamp
        if time_since_last > STALE_FEED_THRESHOLD:
            return {
                "anomaly_type": "stale_feed",
                "severity": "high",
                "expected_value": None,
                "actual_value": None,
                "resolution_notes": f"No readings for {time_since_last}",
            }

        return None

    @staticmethod
    def detect_outlier(
        db: Session,
        meter_id: str,
        value: float,
        current_timestamp: datetime,
        lookback_hours: int = 24,
    ) -> Optional[Dict]:
        """
        Detect if value is an outlier based on recent history

        Uses Z-score method: (value - mean) / std_dev
        Returns anomaly dict if outlier exceeds threshold, None otherwise
        """
        lookback = current_timestamp - timedelta(hours=lookback_hours)

        readings = (
            db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.meter_id == meter_id,
                    TelemetryReading.status == "valid",
                    TelemetryReading.timestamp >= lookback,
                )
            )
            .all()
        )

        if len(readings) < MIN_READINGS_FOR_OUTLIER_DETECTION:
            return None

        values = [float(r.value) for r in readings]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        # Check if value is outlier (>threshold std devs from mean)
        z_score = abs((value - mean) / std_dev) if std_dev > 0 else 0

        if z_score > OUTLIER_Z_SCORE_THRESHOLD:
            severity = "critical" if z_score > OUTLIER_CRITICAL_THRESHOLD else "high"
            return {
                "anomaly_type": "outlier",
                "severity": severity,
                "expected_value": mean,
                "actual_value": value,
                "resolution_notes": f"Z-score: {z_score:.2f} (threshold: {OUTLIER_Z_SCORE_THRESHOLD})",
            }

        return None

    @staticmethod
    def detect_anomalies(
        db: Session,
        meter_id: str,
        value: float,
        timestamp: datetime,
    ) -> List[Dict]:
        """
        Detect all anomalies for a reading

        Returns list of anomaly dicts
        """
        anomalies = []

        stale = AnomalyDetectionService.detect_stale_feed(db, meter_id, timestamp)
        if stale:
            anomalies.append(stale)

        outlier = AnomalyDetectionService.detect_outlier(db, meter_id, value, timestamp)
        if outlier:
            anomalies.append(outlier)

        return anomalies


class TelemetryService:
    """Main telemetry ingestion and processing service"""

    def __init__(self, db: Session):
        self.db = db
        self.validation = ValidationService()
        self.normalization = NormalizationService()
        self.anomaly_detection = AnomalyDetectionService()

    def ingest_reading(
        self,
        tenant_id: str,
        meter_id: str,
        value: float,
        timestamp: datetime,
        unit: str = "kWh",
    ) -> Dict:
        """
        Ingest a single telemetry reading

        Complete pipeline: validate → normalize → detect anomalies → store
        """
        # Step 1: Validate
        is_valid, error_msg = self.validation.validate_reading(
            self.db, meter_id, value, timestamp, unit, tenant_id
        )

        if not is_valid:
            # Record validation error
            error_record = TelemetryValidationError(
                tenant_id=tenant_id,
                meter_id=meter_id,
                error_type="validation_error",
                error_message=error_msg,
                source_data={"value": value, "unit": unit, "timestamp": str(timestamp)},
            )
            self.db.add(error_record)
            self.db.commit()

            return {
                "status": "error",
                "error": error_msg,
                "reading_id": None,
            }

        # Step 2: Normalize
        normalized = self.normalization.normalize_reading(
            value, unit, to_unit="kWh", timestamp=timestamp
        )

        # Step 3: Detect anomalies
        anomalies = self.anomaly_detection.detect_anomalies(
            self.db, meter_id, float(normalized["value"]), normalized["timestamp"]
        )

        # Determine status based on anomalies
        status = "anomaly" if anomalies else "valid"

        # Step 4: Store reading
        reading = TelemetryReading(
            tenant_id=tenant_id,
            meter_id=meter_id,
            timestamp=normalized["timestamp"],
            value=normalized["value"],
            unit=normalized["unit"],
            status=status,
        )
        self.db.add(reading)
        self.db.commit()

        # Step 5: Record anomalies if detected
        for anomaly in anomalies:
            anomaly_record = TelemetryAnomaly(
                tenant_id=tenant_id,
                meter_id=meter_id,
                anomaly_timestamp=normalized["timestamp"],
                anomaly_type=anomaly["anomaly_type"],
                expected_value=anomaly.get("expected_value"),
                actual_value=anomaly["actual_value"],
                severity=anomaly["severity"],
                resolution_notes=anomaly.get("resolution_notes"),
            )
            self.db.add(anomaly_record)

        self.db.commit()

        return {
            "status": status,
            "reading_id": str(reading.id),
            "anomalies": len(anomalies),
        }

    def ingest_batch(
        self,
        tenant_id: str,
        readings: List[Dict],
    ) -> Dict:
        """
        Ingest batch of readings from CSV

        Returns summary with total, valid, invalid counts
        """
        # Validate all readings
        valid_readings, invalid_readings = self.validation.validate_batch(
            self.db, tenant_id, readings
        )

        # Ingest valid readings
        ingested_count = 0
        anomaly_count = 0

        for reading in valid_readings:
            result = self.ingest_reading(
                tenant_id=tenant_id,
                meter_id=reading["meter_id"],
                value=reading["value"],
                timestamp=reading.get("timestamp", datetime.utcnow()),
                unit=reading.get("unit", "kWh"),
            )

            if result["status"] in ["valid", "anomaly"]:
                ingested_count += 1
                anomaly_count += result.get("anomalies", 0)

        # Record errors for invalid readings
        for invalid in invalid_readings:
            error_record = TelemetryValidationError(
                tenant_id=tenant_id,
                meter_id=invalid["data"].get("meter_id"),
                error_type="batch_validation_error",
                error_message=invalid["error"],
                source_data=invalid["data"],
            )
            self.db.add(error_record)

        self.db.commit()

        return {
            "total": len(readings),
            "valid": len(valid_readings),
            "invalid": len(invalid_readings),
            "ingested": ingested_count,
            "anomalies_detected": anomaly_count,
            "errors": invalid_readings,
        }

    def get_latest_readings(
        self, tenant_id: str, meter_ids: Optional[List[str]] = None, limit: int = 100
    ) -> List[Dict]:
        """Get latest readings for meters"""
        query = self.db.query(TelemetryReading).filter_by(
            tenant_id=tenant_id, status="valid"
        )

        if meter_ids:
            query = query.filter(TelemetryReading.meter_id.in_(meter_ids))

        readings = (
            query.order_by(TelemetryReading.timestamp.desc()).limit(limit).all()
        )

        return [
            {
                "reading_id": str(r.id),
                "meter_id": str(r.meter_id),
                "value": float(r.value),
                "unit": r.unit,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in readings
        ]

    def get_history(
        self,
        tenant_id: str,
        meter_id: str,
        start: datetime,
        end: datetime,
    ) -> List[Dict]:
        """Get historical readings for a meter"""
        readings = (
            self.db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.tenant_id == tenant_id,
                    TelemetryReading.meter_id == meter_id,
                    TelemetryReading.timestamp >= start,
                    TelemetryReading.timestamp <= end,
                    TelemetryReading.status == "valid",
                )
            )
            .order_by(TelemetryReading.timestamp)
            .all()
        )

        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": float(r.value),
                "unit": r.unit,
            }
            for r in readings
        ]

    def get_anomalies(
        self,
        tenant_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get detected anomalies"""
        query = self.db.query(TelemetryAnomaly).filter_by(tenant_id=tenant_id)

        if severity:
            query = query.filter_by(severity=severity)

        if status:
            query = query.filter_by(status=status)

        anomalies = query.order_by(TelemetryAnomaly.created_at.desc()).limit(limit).all()

        return [
            {
                "anomaly_id": str(a.id),
                "meter_id": str(a.meter_id),
                "type": a.anomaly_type,
                "severity": a.severity,
                "timestamp": a.anomaly_timestamp.isoformat(),
                "expected_value": float(a.expected_value) if a.expected_value else None,
                "actual_value": float(a.actual_value),
                "status": a.status,
            }
            for a in anomalies
        ]
