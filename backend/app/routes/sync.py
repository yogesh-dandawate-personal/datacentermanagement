"""
Data Sync API Routes
Sprint 12 - Data synchronization endpoints
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.services.sync_engine import sync_engine, SyncDirection, ConflictResolution
from app.exceptions import ValidationError, NotFoundError


router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncConfigCreate(BaseModel):
    integration_id: str = Field(..., description="Integration ID")
    name: str = Field(..., description="Sync configuration name")
    entity_type: str = Field(..., description="Entity type to sync")
    direction: SyncDirection = Field(..., description="Sync direction")
    schedule_cron: Optional[str] = Field(None, description="Cron schedule expression")
    conflict_resolution: ConflictResolution = Field(
        ConflictResolution.LATEST_WINS,
        description="Conflict resolution strategy"
    )
    field_mapping: Optional[Dict[str, str]] = Field(None, description="Field name mappings")
    transformation_rules: Optional[Dict] = Field(None, description="Data transformation rules")


class SyncConfigResponse(BaseModel):
    id: str
    tenant_id: str
    integration_id: str
    name: str
    entity_type: str
    direction: str
    schedule_cron: Optional[str]
    conflict_resolution: str
    is_active: bool
    last_sync_at: Optional[str]
    last_sync_status: Optional[str]
    created_at: str


class SyncRunResponse(BaseModel):
    id: str
    sync_config_id: str
    status: str
    direction: str
    records_total: int
    records_synced: int
    records_failed: int
    records_skipped: int
    started_at: Optional[str]
    completed_at: Optional[str]


class ChangeTrackRequest(BaseModel):
    entity_type: str = Field(..., description="Entity type")
    entity_id: str = Field(..., description="Entity ID")
    change_type: str = Field(..., description="Change type (create, update, delete)")
    data_before: Optional[Dict] = None
    data_after: Optional[Dict] = None
    changed_fields: Optional[List[str]] = None


@router.post("/configs", response_model=SyncConfigResponse)
async def create_sync_config(
    request: SyncConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create sync configuration"""
    try:
        config = await sync_engine.create_sync_config(
            db,
            UUID(current_user["tenant_id"]),
            UUID(request.integration_id),
            request.name,
            request.entity_type,
            request.direction,
            request.schedule_cron,
            request.conflict_resolution,
            request.field_mapping,
            request.transformation_rules
        )

        return SyncConfigResponse(
            id=str(config.id),
            tenant_id=str(config.tenant_id),
            integration_id=str(config.integration_id),
            name=config.name,
            entity_type=config.entity_type,
            direction=config.direction,
            schedule_cron=config.schedule_cron,
            conflict_resolution=config.conflict_resolution,
            is_active=config.is_active,
            last_sync_at=config.last_sync_at.isoformat() if config.last_sync_at else None,
            last_sync_status=config.last_sync_status,
            created_at=config.created_at.isoformat()
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/configs", response_model=List[SyncConfigResponse])
async def list_sync_configs(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List sync configurations"""
    configs = await sync_engine.list_sync_configs(
        db,
        UUID(current_user["tenant_id"]),
        is_active
    )

    return [
        SyncConfigResponse(
            id=str(c.id),
            tenant_id=str(c.tenant_id),
            integration_id=str(c.integration_id),
            name=c.name,
            entity_type=c.entity_type,
            direction=c.direction,
            schedule_cron=c.schedule_cron,
            conflict_resolution=c.conflict_resolution,
            is_active=c.is_active,
            last_sync_at=c.last_sync_at.isoformat() if c.last_sync_at else None,
            last_sync_status=c.last_sync_status,
            created_at=c.created_at.isoformat()
        )
        for c in configs
    ]


@router.get("/configs/{config_id}", response_model=SyncConfigResponse)
async def get_sync_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sync configuration"""
    config = await sync_engine.get_sync_config(
        db,
        UUID(current_user["tenant_id"]),
        config_id
    )

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync config not found")

    return SyncConfigResponse(
        id=str(config.id),
        tenant_id=str(config.tenant_id),
        integration_id=str(config.integration_id),
        name=config.name,
        entity_type=config.entity_type,
        direction=config.direction,
        schedule_cron=config.schedule_cron,
        conflict_resolution=config.conflict_resolution,
        is_active=config.is_active,
        last_sync_at=config.last_sync_at.isoformat() if config.last_sync_at else None,
        last_sync_status=config.last_sync_status,
        created_at=config.created_at.isoformat()
    )


@router.post("/configs/{config_id}/start", response_model=SyncRunResponse)
async def start_sync(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start sync execution"""
    try:
        sync_run = await sync_engine.start_sync(
            db,
            UUID(current_user["tenant_id"]),
            config_id
        )

        return SyncRunResponse(
            id=str(sync_run.id),
            sync_config_id=str(sync_run.sync_config_id),
            status=sync_run.status,
            direction=sync_run.direction,
            records_total=sync_run.records_total,
            records_synced=sync_run.records_synced,
            records_failed=sync_run.records_failed,
            records_skipped=sync_run.records_skipped,
            started_at=sync_run.started_at.isoformat() if sync_run.started_at else None,
            completed_at=sync_run.completed_at.isoformat() if sync_run.completed_at else None
        )

    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/configs/{config_id}/status")
async def get_sync_status(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sync status and statistics"""
    try:
        status_data = await sync_engine.get_sync_status(
            db,
            UUID(current_user["tenant_id"]),
            config_id
        )

        return status_data

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/track-change")
async def track_change(
    request: ChangeTrackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Track entity change for sync"""
    await sync_engine.track_change(
        db,
        UUID(current_user["tenant_id"]),
        request.entity_type,
        UUID(request.entity_id),
        request.change_type,
        request.data_before,
        request.data_after,
        request.changed_fields
    )

    return {"message": "Change tracked successfully"}


@router.get("/directions")
async def get_sync_directions():
    """Get supported sync directions"""
    return {
        "directions": [d.value for d in SyncDirection]
    }


@router.get("/conflict-strategies")
async def get_conflict_strategies():
    """Get supported conflict resolution strategies"""
    return {
        "strategies": [s.value for s in ConflictResolution]
    }
