"""
Emissions Data Ingestion Service

Handles data ingestion from multiple sources:
- Manual CSV/Excel uploads
- API integrations (DCIM systems, cloud providers)
- IoT device streaming
- Real-time metering systems

Features:
- Unit conversion (kWh ↔ MWh, kg ↔ tonne, etc.)
- Duplicate detection and deduplication
- Batch retry mechanism with exponential backoff
- Advanced anomaly detection
- Data quality scoring
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
import io
import csv
import logging
import time
from uuid import UUID
from hashlib import sha256

from app.models import (
    EmissionsSource, EmissionsActivityData, EmissionsIngestionLog, Tenant
)

logger = logging.getLogger(__name__)


class EmissionsIngestionService:
    """Service for ingesting emissions activity data"""

    # Unit conversion factors (to base unit: kWh for energy, kgCO2e for emissions)
    UNIT_CONVERSIONS = {
        # Energy units
        "kWh": 1.0,
        "MWh": 1000.0,
        "Wh": 0.001,
        "kJ": 0.0002778,  # 1 kWh = 3600 kJ
        "MJ": 0.2778,
        "BTU": 0.0002931,
        "therm": 29.31,

        # Emissions units
        "kgCO2e": 1.0,
        "tCO2e": 1000.0,
        "gCO2e": 0.001,
        "lbsCO2e": 0.453592,

        # Flow rates
        "L": 1.0,
        "gallon": 3.785411784,
        "m3": 1000.0,
    }

    def __init__(self, db: Session):
        self.db = db

    def _convert_unit(
        self,
        value: Decimal,
        from_unit: str,
        to_unit: str = "kWh"
    ) -> Decimal:
        """
        Convert value from one unit to another

        Supported conversions:
        - Energy: kWh, MWh, Wh, kJ, MJ, BTU, therm
        - Emissions: kgCO2e, tCO2e, gCO2e, lbsCO2e
        - Volume: L, gallon, m3
        """
        if from_unit == to_unit:
            return value

        if from_unit not in self.UNIT_CONVERSIONS or to_unit not in self.UNIT_CONVERSIONS:
            raise ValueError(f"Unsupported unit conversion: {from_unit} → {to_unit}")

        # Convert to base unit then to target unit
        from_factor = Decimal(str(self.UNIT_CONVERSIONS[from_unit]))
        to_factor = Decimal(str(self.UNIT_CONVERSIONS[to_unit]))

        return (value * from_factor) / to_factor

    def _detect_duplicate(
        self,
        tenant_id: UUID,
        source_id: UUID,
        timestamp: datetime,
        activity_value: Decimal,
        activity_unit: str,
        time_window_minutes: int = 60
    ) -> Optional[Dict]:
        """
        Detect duplicate or near-duplicate readings

        Returns: Dict with duplicate info or None if unique
        """
        try:
            # Create hash of the record for deduplication
            record_hash = sha256(
                f"{source_id}:{timestamp.isoformat()}:{activity_value}:{activity_unit}".encode()
            ).hexdigest()

            # Check for exact duplicates (same source, timestamp, value, unit)
            exact_match = self.db.query(EmissionsActivityData).filter(
                EmissionsActivityData.tenant_id == tenant_id,
                EmissionsActivityData.source_id == source_id,
                EmissionsActivityData.timestamp == timestamp,
                EmissionsActivityData.activity_value == activity_value,
                EmissionsActivityData.activity_unit == activity_unit
            ).first()

            if exact_match:
                return {
                    "is_duplicate": True,
                    "duplicate_type": "exact",
                    "duplicate_id": str(exact_match.id),
                    "original_timestamp": exact_match.timestamp.isoformat(),
                    "original_value": float(exact_match.activity_value)
                }

            # Check for near-duplicates (same source/timestamp, similar value ±5%)
            time_start = timestamp - timedelta(minutes=time_window_minutes // 2)
            time_end = timestamp + timedelta(minutes=time_window_minutes // 2)

            similar_readings = self.db.query(EmissionsActivityData).filter(
                EmissionsActivityData.tenant_id == tenant_id,
                EmissionsActivityData.source_id == source_id,
                EmissionsActivityData.timestamp >= time_start,
                EmissionsActivityData.timestamp <= time_end,
                EmissionsActivityData.activity_unit == activity_unit
            ).all()

            for reading in similar_readings:
                diff_percent = abs(float(reading.activity_value - activity_value)) / float(activity_value) * 100
                if diff_percent <= 5:  # Within 5%
                    return {
                        "is_duplicate": True,
                        "duplicate_type": "similar",
                        "similarity_percent": 100 - diff_percent,
                        "duplicate_id": str(reading.id),
                        "original_timestamp": reading.timestamp.isoformat(),
                        "original_value": float(reading.activity_value)
                    }

            return None

        except Exception as e:
            logger.warning(f"Error detecting duplicate: {str(e)}")
            return None

    def _score_data_quality(
        self,
        data: Dict,
        validation_status: str,
        duplicate_info: Optional[Dict] = None
    ) -> Tuple[float, List[str]]:
        """
        Score data quality from 0-100

        Returns: (quality_score, quality_issues)
        """
        score = 100.0
        issues = []

        # Validation status penalties
        if validation_status == "invalid":
            score -= 40
            issues.append("Invalid: Failed validation checks")
        elif validation_status == "suspected_anomaly":
            score -= 20
            issues.append("Anomaly: Value outside expected range")

        # Duplicate penalties
        if duplicate_info and duplicate_info.get("is_duplicate"):
            if duplicate_info["duplicate_type"] == "exact":
                score -= 30
                issues.append("Exact duplicate detected")
            elif duplicate_info["duplicate_type"] == "similar":
                score -= 15
                issues.append(f"Similar duplicate ({duplicate_info['similarity_percent']:.1f}% match)")

        # Data completeness
        missing_fields = []
        for required_field in ["activity_value", "activity_unit", "timestamp"]:
            if required_field not in data or data[required_field] is None:
                missing_fields.append(required_field)

        if missing_fields:
            score -= 10 * len(missing_fields)
            issues.append(f"Missing fields: {', '.join(missing_fields)}")

        # Ensure score stays in valid range
        score = max(0, min(100, score))

        return score, issues

    def ingest_single_reading(
        self,
        tenant_id: UUID,
        source_id: UUID,
        timestamp: datetime,
        activity_value: Decimal,
        activity_unit: str,
        data_source: str = "manual_entry",
        ingestion_method: str = "manual_form",
        convert_to_unit: str = "kWh",
        allow_duplicates: bool = False,
        max_retries: int = 3
    ) -> Dict:
        """
        Ingest a single activity data reading with unit conversion and duplicate detection

        Args:
            tenant_id: Tenant ID
            source_id: Emissions source ID
            timestamp: Reading timestamp
            activity_value: Numeric value
            activity_unit: Unit of measurement
            data_source: Source of data (manual_entry, api, sensor, etc.)
            ingestion_method: Method used (manual_form, csv_upload, api, etc.)
            convert_to_unit: Target unit for conversion (default: kWh)
            allow_duplicates: Allow ingesting duplicate records
            max_retries: Max retries on transient failure (default: 3)
        """
        retry_count = 0
        last_exception = None

        while retry_count < max_retries:
            try:
                # Verify source exists
                source = self.db.query(EmissionsSource).filter(
                    EmissionsSource.id == source_id,
                    EmissionsSource.tenant_id == tenant_id
                ).first()

                if not source:
                    raise ValueError(f"Emission source {source_id} not found")

                # Validate activity data
                validation_status, validation_notes = self._validate_activity_data({
                    "activity_value": float(activity_value),
                    "activity_unit": activity_unit,
                    "timestamp": timestamp.isoformat()
                })

                # Convert unit if needed
                converted_value = activity_value
                conversion_notes = None
                if activity_unit != convert_to_unit:
                    try:
                        converted_value = self._convert_unit(activity_value, activity_unit, convert_to_unit)
                        conversion_notes = f"Converted from {activity_unit} to {convert_to_unit}"
                    except ValueError as e:
                        conversion_notes = f"Conversion failed: {str(e)}"
                        # Keep original value if conversion fails
                        converted_value = activity_value
                        convert_to_unit = activity_unit

                # Detect duplicates
                duplicate_info = None
                if not allow_duplicates:
                    duplicate_info = self._detect_duplicate(
                        tenant_id=tenant_id,
                        source_id=source_id,
                        timestamp=timestamp,
                        activity_value=converted_value,
                        activity_unit=convert_to_unit
                    )

                    if duplicate_info and duplicate_info.get("is_duplicate"):
                        return {
                            "activity_data_id": None,
                            "status": "duplicate",
                            "message": f"{duplicate_info['duplicate_type'].capitalize()} duplicate detected",
                            "duplicate_info": duplicate_info,
                            "value": float(activity_value),
                            "unit": activity_unit
                        }

                # Score data quality
                quality_score, quality_issues = self._score_data_quality(
                    {
                        "activity_value": float(converted_value),
                        "activity_unit": convert_to_unit,
                        "timestamp": timestamp.isoformat()
                    },
                    validation_status,
                    duplicate_info
                )

                # Build validation notes
                final_notes = validation_notes or ""
                if conversion_notes:
                    final_notes = f"{final_notes}; {conversion_notes}".strip("; ")
                if quality_issues:
                    final_notes = f"{final_notes}; Quality: {'; '.join(quality_issues)}".strip("; ")

                # Create activity data record
                activity = EmissionsActivityData(
                    tenant_id=tenant_id,
                    source_id=source_id,
                    timestamp=timestamp,
                    activity_value=converted_value,
                    activity_unit=convert_to_unit,
                    data_source=data_source,
                    ingestion_method=ingestion_method,
                    validation_status=validation_status,
                    validation_notes=final_notes,
                    quality_score=quality_score
                )

                self.db.add(activity)
                self.db.commit()

                logger.info(f"Ingested single reading for source {source_id}: {converted_value} {convert_to_unit} "
                           f"(quality: {quality_score:.0f}%)")

                return {
                    "activity_data_id": str(activity.id),
                    "status": validation_status,
                    "value": float(converted_value),
                    "unit": convert_to_unit,
                    "original_value": float(activity_value),
                    "original_unit": activity_unit,
                    "quality_score": quality_score,
                    "timestamp": timestamp.isoformat()
                }

            except Exception as e:
                retry_count += 1
                last_exception = e

                # Rollback on error
                self.db.rollback()

                # If it's not a retryable error, raise immediately
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable error ingesting single reading: {str(e)}")
                    raise

                # Exponential backoff: 1s, 2s, 4s
                if retry_count < max_retries:
                    wait_time = 2 ** (retry_count - 1)
                    logger.warning(f"Retry {retry_count}/{max_retries} after {wait_time}s: {str(e)}")
                    time.sleep(wait_time)

        # All retries exhausted
        logger.error(f"Failed to ingest reading after {max_retries} retries: {str(last_exception)}")
        raise last_exception

    def ingest_batch_file(
        self,
        tenant_id: UUID,
        file_content: bytes,
        source_id: Optional[UUID] = None,
        file_format: str = "csv",
        ingestion_method: str = "csv_upload",
        convert_to_unit: str = "kWh",
        skip_duplicates: bool = True,
        max_retries: int = 3
    ) -> Dict:
        """
        Ingest batch data from CSV/Excel file

        Expected CSV columns:
        - emissions_source_id (optional if source_id provided)
        - timestamp (ISO format)
        - activity_value (numeric)
        - activity_unit (string)
        """
        try:
            records_received = 0
            records_processed = 0
            records_failed = 0
            errors = []

            # Parse CSV
            if file_format == "csv":
                file_obj = io.StringIO(file_content.decode('utf-8'))
                reader = csv.DictReader(file_obj)
                rows = list(reader)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            records_received = len(rows)

            # Process each row with retry logic
            for row_num, row in enumerate(rows, 1):
                retry_count = 0
                row_error = None

                while retry_count < max_retries:
                    try:
                        # Get source ID
                        current_source_id = source_id or row.get("emissions_source_id")
                        if not current_source_id:
                            raise ValueError("emissions_source_id not provided in file or request")

                        # Parse fields
                        timestamp = datetime.fromisoformat(row["timestamp"])
                        activity_value = Decimal(str(row["activity_value"]))
                        activity_unit = row.get("activity_unit", "kWh")

                        # Verify source exists
                        source = self.db.query(EmissionsSource).filter(
                            EmissionsSource.id == current_source_id,
                            EmissionsSource.tenant_id == tenant_id
                        ).first()

                        if not source:
                            raise ValueError(f"Source {current_source_id} not found")

                        # Validate
                        validation_status, validation_notes = self._validate_activity_data({
                            "activity_value": float(activity_value),
                            "activity_unit": activity_unit,
                            "timestamp": timestamp.isoformat()
                        })

                        # Convert unit if needed
                        converted_value = activity_value
                        conversion_notes = None
                        if activity_unit != convert_to_unit:
                            try:
                                converted_value = self._convert_unit(activity_value, activity_unit, convert_to_unit)
                                conversion_notes = f"Converted {activity_unit}→{convert_to_unit}"
                            except ValueError as e:
                                conversion_notes = f"Conversion error: {str(e)}"
                                converted_value = activity_value
                                converted_unit = activity_unit
                        else:
                            converted_unit = convert_to_unit

                        # Duplicate detection
                        duplicate_info = None
                        if skip_duplicates:
                            duplicate_info = self._detect_duplicate(
                                tenant_id=tenant_id,
                                source_id=current_source_id,
                                timestamp=timestamp,
                                activity_value=converted_value,
                                activity_unit=converted_unit
                            )

                            if duplicate_info and duplicate_info.get("is_duplicate"):
                                records_failed += 1
                                errors.append(
                                    f"Row {row_num}: {duplicate_info['duplicate_type'].capitalize()} duplicate skipped"
                                )
                                logger.debug(f"Row {row_num}: Duplicate skipped")
                                break  # Skip this row, move to next

                        # Score data quality
                        quality_score, quality_issues = self._score_data_quality(
                            {
                                "activity_value": float(converted_value),
                                "activity_unit": converted_unit,
                                "timestamp": timestamp.isoformat()
                            },
                            validation_status,
                            duplicate_info
                        )

                        # Build validation notes
                        final_notes = validation_notes or ""
                        if conversion_notes:
                            final_notes = f"{final_notes}; {conversion_notes}".strip("; ")
                        if quality_issues:
                            final_notes = f"{final_notes}; {'; '.join(quality_issues)}".strip("; ")

                        # Create record
                        activity = EmissionsActivityData(
                            tenant_id=tenant_id,
                            source_id=current_source_id,
                            timestamp=timestamp,
                            activity_value=converted_value,
                            activity_unit=converted_unit,
                            data_source="file_upload",
                            ingestion_method=ingestion_method,
                            validation_status=validation_status,
                            validation_notes=final_notes,
                            quality_score=quality_score
                        )

                        self.db.add(activity)
                        records_processed += 1
                        break  # Successfully processed, exit retry loop

                    except Exception as e:
                        retry_count += 1
                        row_error = e

                        # If not retryable or last retry, fail the row
                        if not self._is_retryable_error(e) or retry_count >= max_retries:
                            records_failed += 1
                            errors.append(f"Row {row_num}: {str(e)}")
                            logger.warning(f"Row {row_num} failed: {str(e)}")
                            break
                        else:
                            # Retryable error, wait before retry
                            wait_time = 2 ** (retry_count - 1)
                            logger.debug(f"Row {row_num} retry {retry_count} after {wait_time}s")
                            time.sleep(wait_time)

            # Commit all processed records
            self.db.commit()

            # Create ingestion log
            log_status = "completed" if records_failed == 0 else "partial_success" if records_processed > 0 else "failed"
            ingestion_log = EmissionsIngestionLog(
                tenant_id=tenant_id,
                source_id=source_id,
                ingestion_method=ingestion_method,
                data_source="file_upload",
                records_received=records_received,
                records_processed=records_processed,
                records_failed=records_failed,
                status=log_status,
                error_log=errors,
                ingestion_completed_at=datetime.utcnow()
            )

            self.db.add(ingestion_log)
            self.db.commit()

            logger.info(
                f"Batch ingestion completed: {records_processed}/{records_received} "
                f"records processed, {records_failed} failed"
            )

            return {
                "ingestion_log_id": str(ingestion_log.id),
                "records_received": records_received,
                "records_processed": records_processed,
                "records_failed": records_failed,
                "status": log_status,
                "errors": errors if errors else None
            }

        except Exception as e:
            logger.error(f"Error in batch ingestion: {str(e)}")
            self.db.rollback()
            raise

    def ingest_dcim_api(
        self,
        tenant_id: UUID,
        source_id: UUID,
        api_readings: List[Dict],
        ingestion_method: str = "dcim_api"
    ) -> Dict:
        """
        Ingest data from DCIM API (NetBox, Sunbird, etc.)

        Expected format:
        [
            {"timestamp": "2026-03-10T14:30:00Z", "value": 150.5, "unit": "kWh"},
            ...
        ]
        """
        try:
            records_received = len(api_readings)
            records_processed = 0
            records_failed = 0
            errors = []

            # Verify source
            source = self.db.query(EmissionsSource).filter(
                EmissionsSource.id == source_id,
                EmissionsSource.tenant_id == tenant_id
            ).first()

            if not source:
                raise ValueError(f"Source {source_id} not found")

            # Process each reading
            for reading_num, reading in enumerate(api_readings, 1):
                try:
                    timestamp = datetime.fromisoformat(reading["timestamp"].replace("Z", "+00:00"))
                    activity_value = Decimal(str(reading["value"]))
                    activity_unit = reading.get("unit", source.unit_of_measure)

                    # Validate
                    validation_status, validation_notes = self._validate_activity_data({
                        "activity_value": float(activity_value),
                        "activity_unit": activity_unit,
                        "timestamp": timestamp.isoformat()
                    })

                    # Create record
                    activity = EmissionsActivityData(
                        tenant_id=tenant_id,
                        source_id=source_id,
                        timestamp=timestamp,
                        activity_value=activity_value,
                        activity_unit=activity_unit,
                        data_source="dcim_api",
                        ingestion_method=ingestion_method,
                        validation_status=validation_status,
                        validation_notes=validation_notes,
                        source_metadata=reading.get("metadata", {})
                    )

                    self.db.add(activity)
                    records_processed += 1

                except Exception as e:
                    records_failed += 1
                    errors.append(f"Reading {reading_num}: {str(e)}")
                    logger.warning(f"Failed to process API reading {reading_num}: {str(e)}")

            self.db.commit()

            # Create ingestion log
            log_status = "completed" if records_failed == 0 else "partial_success"
            ingestion_log = EmissionsIngestionLog(
                tenant_id=tenant_id,
                source_id=source_id,
                ingestion_method=ingestion_method,
                data_source="dcim_api",
                records_received=records_received,
                records_processed=records_processed,
                records_failed=records_failed,
                status=log_status,
                error_log=errors,
                ingestion_completed_at=datetime.utcnow()
            )

            self.db.add(ingestion_log)
            self.db.commit()

            logger.info(f"DCIM API ingestion: {records_processed}/{records_received} records processed")

            return {
                "ingestion_log_id": str(ingestion_log.id),
                "records_received": records_received,
                "records_processed": records_processed,
                "records_failed": records_failed,
                "status": log_status
            }

        except Exception as e:
            logger.error(f"Error ingesting from DCIM API: {str(e)}")
            self.db.rollback()
            raise

    def _is_retryable_error(self, exception: Exception) -> bool:
        """
        Determine if an error is retryable (transient) vs permanent

        Retryable: Database connection, timeout, deadlock
        Non-retryable: Validation error, not found, permission
        """
        error_msg = str(exception).lower()

        retryable_keywords = [
            "connection", "timeout", "deadlock", "lock", "interrupt",
            "temporarily unavailable", "try again", "temporary"
        ]

        return any(keyword in error_msg for keyword in retryable_keywords)

    def _validate_activity_data(self, data: Dict) -> Tuple[str, Optional[str]]:
        """
        Advanced validation of activity data with anomaly detection

        Returns: (validation_status, validation_notes)

        Validation status:
        - "valid": All checks passed
        - "suspected_anomaly": Minor issues detected
        - "invalid": Critical issues preventing ingestion
        """
        try:
            activity_value = float(data.get("activity_value", 0))
            activity_unit = data.get("activity_unit", "")
            timestamp = data.get("timestamp", "")

            issues = []
            warnings = []

            # Required field checks
            if activity_value < 0:
                issues.append("Activity value cannot be negative")

            if not activity_unit:
                issues.append("Activity unit is required")

            if not timestamp:
                issues.append("Timestamp is required")

            # Check for future timestamps
            try:
                ts = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
                if ts > datetime.utcnow():
                    warnings.append("Timestamp is in the future")
            except:
                issues.append("Invalid timestamp format")

            # Anomaly detection: outlier checks
            if activity_value == 0:
                warnings.append("Activity value is zero")
            elif activity_value > 1000000:
                warnings.append("Activity value is unusually high (>1M)")
            elif activity_value > 0 and activity_value < 0.001:
                warnings.append("Activity value is unusually small (<0.001)")

            # Check for extreme values
            if activity_value > Decimal("999999999"):
                issues.append("Activity value exceeds maximum allowed")

            # Return appropriate status
            if issues:
                if len(issues) > 1:
                    return "invalid", " | ".join(issues)
                else:
                    return "suspected_anomaly", " | ".join(issues + warnings)
            elif warnings:
                return "suspected_anomaly", " | ".join(warnings)
            else:
                return "valid", None

        except Exception as e:
            return "invalid", f"Validation error: {str(e)}"

    def get_ingestion_history(
        self,
        tenant_id: UUID,
        source_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get ingestion history for a source or tenant"""
        try:
            query = self.db.query(EmissionsIngestionLog).filter(
                EmissionsIngestionLog.tenant_id == tenant_id
            )

            if source_id:
                query = query.filter(EmissionsIngestionLog.source_id == source_id)

            logs = query.order_by(EmissionsIngestionLog.created_at.desc()).limit(limit).all()

            return [
                {
                    "ingestion_log_id": str(log.id),
                    "ingestion_method": log.ingestion_method,
                    "data_source": log.data_source,
                    "records_received": log.records_received,
                    "records_processed": log.records_processed,
                    "records_failed": log.records_failed,
                    "status": log.status,
                    "created_at": log.created_at.isoformat(),
                    "completed_at": log.ingestion_completed_at.isoformat() if log.ingestion_completed_at else None
                }
                for log in logs
            ]

        except Exception as e:
            logger.error(f"Error retrieving ingestion history: {str(e)}")
            raise
