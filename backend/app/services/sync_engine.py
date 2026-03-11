"""
Data Sync Engine Service
Sprint 12 - Task 3: Scheduled sync, incremental sync, conflict resolution
Handles bi-directional sync with external systems
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, select, update, and_

from app.models import Base, Tenant, UUID as ModelUUID
from app.exceptions import ValidationError, NotFoundError


class SyncDirection(str, Enum):
    """Sync direction"""
    PULL = "pull"  # From external to internal
    PUSH = "push"  # From internal to external
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Sync status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ConflictResolution(str, Enum):
    """Conflict resolution strategy"""
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    LATEST_WINS = "latest_wins"
    MANUAL = "manual"


class SyncConfiguration(Base):
    """Sync configuration"""
    __tablename__ = "sync_configurations"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)
    integration_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)  # metric, report, calculation, etc.

    direction = Column(String(50), nullable=False, default=SyncDirection.PULL.value)
    schedule_cron = Column(String(100))  # Cron expression for scheduled sync
    is_active = Column(Boolean, default=True, index=True)

    conflict_resolution = Column(
        String(50),
        default=ConflictResolution.LATEST_WINS.value
    )

    field_mapping = Column(JSON, default=dict)  # Field name mappings
    transformation_rules = Column(JSON, default=dict)  # Data transformation rules

    last_sync_at = Column(DateTime)
    last_sync_status = Column(String(50))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncRun(Base):
    """Sync execution run"""
    __tablename__ = "sync_runs"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    sync_config_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    status = Column(String(50), default=SyncStatus.PENDING.value, index=True)
    direction = Column(String(50), nullable=False)

    records_total = Column(Integer, default=0)
    records_synced = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    error_message = Column(Text)
    error_details = Column(JSON)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class SyncConflict(Base):
    """Sync conflict record"""
    __tablename__ = "sync_conflicts"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    sync_run_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(255), nullable=False)  # External entity ID

    source_data = Column(JSON, nullable=False)
    target_data = Column(JSON, nullable=False)

    conflict_type = Column(String(50), nullable=False)  # field_mismatch, duplicate, etc.
    conflict_fields = Column(JSON, default=list)

    resolution_strategy = Column(String(50))
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(ModelUUID(as_uuid=True))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class ChangeTrackingLog(Base):
    """Change tracking for incremental sync"""
    __tablename__ = "change_tracking_logs"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    change_type = Column(String(50), nullable=False)  # create, update, delete
    changed_fields = Column(JSON, default=list)

    data_before = Column(JSON)
    data_after = Column(JSON)
    data_hash = Column(String(64), nullable=False)  # Hash of current data

    sync_status = Column(String(50), default="pending", index=True)
    synced_at = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class SyncEngineService:
    """Data synchronization engine"""

    async def create_sync_config(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_id: UUID,
        name: str,
        entity_type: str,
        direction: SyncDirection,
        schedule_cron: Optional[str] = None,
        conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS,
        field_mapping: Optional[Dict[str, str]] = None,
        transformation_rules: Optional[Dict[str, Any]] = None
    ) -> SyncConfiguration:
        """Create sync configuration"""
        config = SyncConfiguration(
            tenant_id=tenant_id,
            integration_id=integration_id,
            name=name,
            entity_type=entity_type,
            direction=direction.value,
            schedule_cron=schedule_cron,
            conflict_resolution=conflict_resolution.value,
            field_mapping=field_mapping or {},
            transformation_rules=transformation_rules or {},
            is_active=True
        )

        db.add(config)
        await db.commit()
        await db.refresh(config)

        return config

    async def get_sync_config(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        config_id: UUID
    ) -> Optional[SyncConfiguration]:
        """Get sync configuration"""
        result = await db.execute(
            select(SyncConfiguration).where(
                SyncConfiguration.id == config_id,
                SyncConfiguration.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def list_sync_configs(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[SyncConfiguration]:
        """List sync configurations"""
        query = select(SyncConfiguration).where(
            SyncConfiguration.tenant_id == tenant_id
        )

        if is_active is not None:
            query = query.where(SyncConfiguration.is_active == is_active)

        result = await db.execute(query)
        return result.scalars().all()

    async def start_sync(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        config_id: UUID
    ) -> SyncRun:
        """Start sync execution"""
        config = await self.get_sync_config(db, tenant_id, config_id)

        if not config:
            raise NotFoundError(f"Sync configuration {config_id} not found")

        if not config.is_active:
            raise ValidationError("Sync configuration is not active")

        # Create sync run
        sync_run = SyncRun(
            sync_config_id=config_id,
            tenant_id=tenant_id,
            status=SyncStatus.RUNNING.value,
            direction=config.direction,
            started_at=datetime.utcnow()
        )

        db.add(sync_run)
        await db.commit()
        await db.refresh(sync_run)

        # Execute sync asynchronously
        asyncio.create_task(
            self._execute_sync(db, config, sync_run)
        )

        return sync_run

    async def _execute_sync(
        self,
        db: AsyncSession,
        config: SyncConfiguration,
        sync_run: SyncRun
    ):
        """Execute sync operation"""
        try:
            if config.direction == SyncDirection.PULL.value:
                await self._sync_pull(db, config, sync_run)

            elif config.direction == SyncDirection.PUSH.value:
                await self._sync_push(db, config, sync_run)

            elif config.direction == SyncDirection.BIDIRECTIONAL.value:
                await self._sync_bidirectional(db, config, sync_run)

            # Update sync run status
            sync_run.status = SyncStatus.COMPLETED.value
            sync_run.completed_at = datetime.utcnow()

            # Update config last sync
            config.last_sync_at = datetime.utcnow()
            config.last_sync_status = SyncStatus.COMPLETED.value

        except Exception as e:
            sync_run.status = SyncStatus.FAILED.value
            sync_run.error_message = str(e)
            sync_run.completed_at = datetime.utcnow()

            config.last_sync_status = SyncStatus.FAILED.value

        await db.commit()

    async def _sync_pull(
        self,
        db: AsyncSession,
        config: SyncConfiguration,
        sync_run: SyncRun
    ):
        """Pull data from external system"""
        # Get changes since last sync
        last_sync = config.last_sync_at or datetime.utcnow() - timedelta(days=30)

        # Fetch external data (would call integration service)
        external_records = await self._fetch_external_data(
            config.integration_id,
            config.entity_type,
            last_sync
        )

        sync_run.records_total = len(external_records)

        for record in external_records:
            try:
                # Transform data
                transformed = self._transform_data(
                    record,
                    config.field_mapping,
                    config.transformation_rules
                )

                # Check for conflicts
                conflict = await self._detect_conflict(
                    db,
                    config.tenant_id,
                    config.entity_type,
                    record.get("id"),
                    transformed
                )

                if conflict:
                    # Handle conflict
                    resolved = await self._resolve_conflict(
                        db,
                        sync_run,
                        config,
                        conflict
                    )

                    if not resolved:
                        sync_run.records_skipped += 1
                        continue

                # Apply changes
                await self._apply_changes(
                    db,
                    config.tenant_id,
                    config.entity_type,
                    transformed
                )

                sync_run.records_synced += 1

            except Exception as e:
                sync_run.records_failed += 1
                # Log error details
                continue

    async def _sync_push(
        self,
        db: AsyncSession,
        config: SyncConfiguration,
        sync_run: SyncRun
    ):
        """Push data to external system"""
        # Get pending changes since last sync
        result = await db.execute(
            select(ChangeTrackingLog).where(
                and_(
                    ChangeTrackingLog.tenant_id == config.tenant_id,
                    ChangeTrackingLog.entity_type == config.entity_type,
                    ChangeTrackingLog.sync_status == "pending"
                )
            )
        )
        changes = result.scalars().all()

        sync_run.records_total = len(changes)

        for change in changes:
            try:
                # Transform data for external system
                transformed = self._transform_data(
                    change.data_after or change.data_before,
                    config.field_mapping,
                    config.transformation_rules,
                    reverse=True
                )

                # Push to external system
                await self._push_external_data(
                    config.integration_id,
                    config.entity_type,
                    change.change_type,
                    transformed
                )

                # Mark as synced
                change.sync_status = "synced"
                change.synced_at = datetime.utcnow()

                sync_run.records_synced += 1

            except Exception as e:
                sync_run.records_failed += 1
                change.sync_status = "failed"
                continue

    async def _sync_bidirectional(
        self,
        db: AsyncSession,
        config: SyncConfiguration,
        sync_run: SyncRun
    ):
        """Bidirectional sync"""
        # Pull first, then push
        await self._sync_pull(db, config, sync_run)
        await self._sync_push(db, config, sync_run)

    async def track_change(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        change_type: str,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        changed_fields: Optional[List[str]] = None
    ):
        """Track entity change for sync"""
        # Calculate data hash
        current_data = data_after or data_before or {}
        data_hash = self._calculate_hash(current_data)

        change_log = ChangeTrackingLog(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            changed_fields=changed_fields or [],
            data_before=data_before,
            data_after=data_after,
            data_hash=data_hash,
            sync_status="pending"
        )

        db.add(change_log)
        await db.commit()

    async def _detect_conflict(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        entity_type: str,
        entity_id: str,
        external_data: Dict[str, Any]
    ) -> Optional[Tuple[Dict, Dict, List[str]]]:
        """Detect sync conflicts"""
        # Get local data (simplified - would query actual entity table)
        local_data = await self._get_local_data(
            db,
            tenant_id,
            entity_type,
            entity_id
        )

        if not local_data:
            return None

        # Compare data
        conflicting_fields = []

        for field, external_value in external_data.items():
            local_value = local_data.get(field)

            if local_value != external_value:
                conflicting_fields.append(field)

        if conflicting_fields:
            return (local_data, external_data, conflicting_fields)

        return None

    async def _resolve_conflict(
        self,
        db: AsyncSession,
        sync_run: SyncRun,
        config: SyncConfiguration,
        conflict: Tuple[Dict, Dict, List[str]]
    ) -> bool:
        """Resolve sync conflict"""
        local_data, external_data, conflicting_fields = conflict

        # Log conflict
        conflict_record = SyncConflict(
            sync_run_id=sync_run.id,
            tenant_id=config.tenant_id,
            entity_type=config.entity_type,
            entity_id=external_data.get("id", ""),
            source_data=external_data,
            target_data=local_data,
            conflict_type="field_mismatch",
            conflict_fields=conflicting_fields,
            resolution_strategy=config.conflict_resolution
        )

        db.add(conflict_record)

        # Apply resolution strategy
        if config.conflict_resolution == ConflictResolution.SOURCE_WINS.value:
            # Use external data
            return True

        elif config.conflict_resolution == ConflictResolution.TARGET_WINS.value:
            # Keep local data
            return False

        elif config.conflict_resolution == ConflictResolution.LATEST_WINS.value:
            # Compare timestamps
            external_ts = external_data.get("updated_at")
            local_ts = local_data.get("updated_at")

            if external_ts and local_ts:
                return external_ts > local_ts

            return True

        elif config.conflict_resolution == ConflictResolution.MANUAL.value:
            # Require manual resolution
            return False

        return True

    def _transform_data(
        self,
        data: Dict[str, Any],
        field_mapping: Dict[str, str],
        transformation_rules: Dict[str, Any],
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Transform data using field mapping and rules"""
        transformed = {}

        # Apply field mapping
        for source_field, value in data.items():
            if reverse:
                target_field = next(
                    (k for k, v in field_mapping.items() if v == source_field),
                    source_field
                )
            else:
                target_field = field_mapping.get(source_field, source_field)

            # Apply transformation rules
            if target_field in transformation_rules:
                rule = transformation_rules[target_field]

                if rule.get("type") == "multiply":
                    value = float(value) * rule.get("factor", 1.0)

                elif rule.get("type") == "convert_unit":
                    # Unit conversion
                    value = self._convert_unit(value, rule)

            transformed[target_field] = value

        return transformed

    def _convert_unit(self, value: Any, rule: Dict) -> Any:
        """Convert units"""
        # Simplified unit conversion
        from_unit = rule.get("from")
        to_unit = rule.get("to")

        # Example: kWh to MWh
        if from_unit == "kWh" and to_unit == "MWh":
            return float(value) / 1000

        return value

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of data"""
        data_json = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_json.encode()).hexdigest()

    async def _fetch_external_data(
        self,
        integration_id: UUID,
        entity_type: str,
        since: datetime
    ) -> List[Dict]:
        """Fetch data from external system"""
        # Would use integration service to fetch data
        # Simplified for demo
        return []

    async def _push_external_data(
        self,
        integration_id: UUID,
        entity_type: str,
        change_type: str,
        data: Dict
    ):
        """Push data to external system"""
        # Would use integration service to push data
        pass

    async def _get_local_data(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        entity_type: str,
        entity_id: str
    ) -> Optional[Dict]:
        """Get local entity data"""
        # Would query actual entity table
        return None

    async def _apply_changes(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        entity_type: str,
        data: Dict
    ):
        """Apply changes to local entity"""
        # Would update actual entity table
        pass

    async def get_sync_status(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        config_id: UUID
    ) -> Dict[str, Any]:
        """Get sync status and statistics"""
        config = await self.get_sync_config(db, tenant_id, config_id)

        if not config:
            raise NotFoundError(f"Sync configuration {config_id} not found")

        # Get recent runs
        result = await db.execute(
            select(SyncRun)
            .where(SyncRun.sync_config_id == config_id)
            .order_by(SyncRun.created_at.desc())
            .limit(10)
        )
        recent_runs = result.scalars().all()

        # Get pending conflicts
        result = await db.execute(
            select(SyncConflict)
            .where(
                and_(
                    SyncConflict.tenant_id == tenant_id,
                    SyncConflict.resolved == False
                )
            )
        )
        pending_conflicts = result.scalars().all()

        return {
            "config": {
                "id": str(config.id),
                "name": config.name,
                "entity_type": config.entity_type,
                "direction": config.direction,
                "is_active": config.is_active,
                "last_sync_at": config.last_sync_at,
                "last_sync_status": config.last_sync_status
            },
            "recent_runs": [
                {
                    "id": str(run.id),
                    "status": run.status,
                    "records_total": run.records_total,
                    "records_synced": run.records_synced,
                    "records_failed": run.records_failed,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at
                }
                for run in recent_runs
            ],
            "pending_conflicts": len(pending_conflicts)
        }


# Singleton instance
sync_engine = SyncEngineService()
