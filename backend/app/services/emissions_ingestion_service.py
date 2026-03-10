"""
Emissions Data Ingestion Service

Handles data ingestion from multiple sources:
- Manual CSV/Excel uploads
- API integrations (DCIM systems, cloud providers)
- IoT device streaming
- Real-time metering systems
"""

from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
import io
import csv
import logging
from uuid import UUID

from app.models import (
    EmissionsSource, EmissionsActivityData, EmissionsIngestionLog, Tenant
)

logger = logging.getLogger(__name__)


class EmissionsIngestionService:
    """Service for ingesting emissions activity data"""

    def __init__(self, db: Session):
        self.db = db

    def ingest_single_reading(
        self,
        tenant_id: UUID,
        source_id: UUID,
        timestamp: datetime,
        activity_value: Decimal,
        activity_unit: str,
        data_source: str = "manual_entry",
        ingestion_method: str = "manual_form"
    ) -> Dict:
        """Ingest a single activity data reading"""
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

            # Create activity data record
            activity = EmissionsActivityData(
                tenant_id=tenant_id,
                source_id=source_id,
                timestamp=timestamp,
                activity_value=activity_value,
                activity_unit=activity_unit,
                data_source=data_source,
                ingestion_method=ingestion_method,
                validation_status=validation_status,
                validation_notes=validation_notes
            )

            self.db.add(activity)
            self.db.commit()

            logger.info(f"Ingested single reading for source {source_id}: {activity_value} {activity_unit}")

            return {
                "activity_data_id": str(activity.id),
                "status": validation_status,
                "value": float(activity_value),
                "unit": activity_unit,
                "timestamp": timestamp.isoformat()
            }

        except Exception as e:
            logger.error(f"Error ingesting single reading: {str(e)}")
            self.db.rollback()
            raise

    def ingest_batch_file(
        self,
        tenant_id: UUID,
        file_content: bytes,
        source_id: Optional[UUID] = None,
        file_format: str = "csv",
        ingestion_method: str = "csv_upload"
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

            # Process each row
            for row_num, row in enumerate(rows, 1):
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

                    # Create record
                    activity = EmissionsActivityData(
                        tenant_id=tenant_id,
                        source_id=current_source_id,
                        timestamp=timestamp,
                        activity_value=activity_value,
                        activity_unit=activity_unit,
                        data_source="file_upload",
                        ingestion_method=ingestion_method,
                        validation_status=validation_status,
                        validation_notes=validation_notes
                    )

                    self.db.add(activity)
                    records_processed += 1

                except Exception as e:
                    records_failed += 1
                    errors.append(f"Row {row_num}: {str(e)}")
                    logger.warning(f"Failed to process row {row_num}: {str(e)}")

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

    def _validate_activity_data(self, data: Dict) -> Tuple[str, Optional[str]]:
        """
        Validate activity data

        Returns: (validation_status, validation_notes)
        """
        try:
            activity_value = float(data.get("activity_value", 0))
            activity_unit = data.get("activity_unit", "")
            timestamp = data.get("timestamp", "")

            issues = []

            # Check for required fields
            if activity_value < 0:
                issues.append("Activity value cannot be negative")

            if not activity_unit:
                issues.append("Activity unit is required")

            if not timestamp:
                issues.append("Timestamp is required")

            # Check for anomalies (very large or very small values)
            if activity_value > Decimal("999999999"):
                issues.append("Activity value exceeds expected range")

            # Return status
            if not issues:
                return "valid", None
            elif len(issues) <= 1:
                return "suspected_anomaly", " | ".join(issues)
            else:
                return "invalid", " | ".join(issues)

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
