"""
Webhook API Routes
Sprint 12 - Webhook management endpoints
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.services.webhooks import webhook_service
from app.exceptions import ValidationError, NotFoundError


router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


class WebhookCreate(BaseModel):
    name: str = Field(..., description="Webhook name")
    url: HttpUrl = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Event types to listen for")
    secret: Optional[str] = Field(None, description="Signing secret (auto-generated if not provided)")


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    url: str
    events: List[str]
    is_active: bool
    delivery_success_count: int
    delivery_failure_count: int
    last_delivery_at: Optional[str]
    last_delivery_status: Optional[str]
    created_at: str


class WebhookSecretResponse(BaseModel):
    id: str
    secret: str


class EventTrigger(BaseModel):
    event_type: str = Field(..., description="Event type")
    payload: Dict = Field(..., description="Event payload")


class DeliveryResponse(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    status: str
    http_status: Optional[int]
    attempts: int
    created_at: str
    delivered_at: Optional[str]


@router.post("/", response_model=WebhookSecretResponse)
async def register_webhook(
    request: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Register new webhook"""
    try:
        webhook = await webhook_service.register_webhook(
            db,
            UUID(current_user["tenant_id"]),
            request.name,
            str(request.url),
            request.events,
            request.secret
        )

        return WebhookSecretResponse(
            id=str(webhook.id),
            secret=webhook.secret
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all webhooks"""
    webhooks = await webhook_service.list_webhooks(
        db,
        UUID(current_user["tenant_id"]),
        is_active
    )

    return [
        WebhookResponse(
            id=str(w.id),
            tenant_id=str(w.tenant_id),
            name=w.name,
            url=w.url,
            events=w.events,
            is_active=w.is_active,
            delivery_success_count=w.delivery_success_count,
            delivery_failure_count=w.delivery_failure_count,
            last_delivery_at=w.last_delivery_at.isoformat() if w.last_delivery_at else None,
            last_delivery_status=w.last_delivery_status,
            created_at=w.created_at.isoformat()
        )
        for w in webhooks
    ]


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook by ID"""
    webhook = await webhook_service.get_webhook(
        db,
        UUID(current_user["tenant_id"]),
        webhook_id
    )

    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    return WebhookResponse(
        id=str(webhook.id),
        tenant_id=str(webhook.tenant_id),
        name=webhook.name,
        url=webhook.url,
        events=webhook.events,
        is_active=webhook.is_active,
        delivery_success_count=webhook.delivery_success_count,
        delivery_failure_count=webhook.delivery_failure_count,
        last_delivery_at=webhook.last_delivery_at.isoformat() if webhook.last_delivery_at else None,
        last_delivery_status=webhook.last_delivery_status,
        created_at=webhook.created_at.isoformat()
    )


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: UUID,
    request: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update webhook"""
    try:
        webhook = await webhook_service.update_webhook(
            db,
            UUID(current_user["tenant_id"]),
            webhook_id,
            request.name,
            str(request.url) if request.url else None,
            request.events,
            request.is_active
        )

        return WebhookResponse(
            id=str(webhook.id),
            tenant_id=str(webhook.tenant_id),
            name=webhook.name,
            url=webhook.url,
            events=webhook.events,
            is_active=webhook.is_active,
            delivery_success_count=webhook.delivery_success_count,
            delivery_failure_count=webhook.delivery_failure_count,
            last_delivery_at=webhook.last_delivery_at.isoformat() if webhook.last_delivery_at else None,
            last_delivery_status=webhook.last_delivery_status,
            created_at=webhook.created_at.isoformat()
        )

    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete webhook"""
    try:
        await webhook_service.delete_webhook(
            db,
            UUID(current_user["tenant_id"]),
            webhook_id
        )

        return {"message": "Webhook deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test webhook delivery"""
    try:
        result = await webhook_service.test_webhook(
            db,
            UUID(current_user["tenant_id"]),
            webhook_id
        )

        return result

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/trigger")
async def trigger_event(
    request: EventTrigger,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Trigger webhook event"""
    try:
        await webhook_service.trigger_event(
            db,
            UUID(current_user["tenant_id"]),
            request.event_type,
            request.payload
        )

        return {"message": "Event triggered successfully"}

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{webhook_id}/deliveries", response_model=List[DeliveryResponse])
async def get_webhook_deliveries(
    webhook_id: UUID,
    status: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook delivery history"""
    deliveries = await webhook_service.get_deliveries(
        db,
        UUID(current_user["tenant_id"]),
        webhook_id,
        status,
        limit
    )

    return [
        DeliveryResponse(
            id=str(d.id),
            webhook_id=str(d.webhook_id),
            event_type=d.event_type,
            status=d.status,
            http_status=d.http_status,
            attempts=d.attempts,
            created_at=d.created_at.isoformat(),
            delivered_at=d.delivered_at.isoformat() if d.delivered_at else None
        )
        for d in deliveries
    ]


@router.get("/events/supported")
async def get_supported_events():
    """Get list of supported webhook events"""
    return {
        "events": webhook_service.SUPPORTED_EVENTS
    }


@router.post("/verify")
async def verify_webhook_signature(
    request: Request,
    x_webhook_signature: str = Header(...),
    secret: str = Header(...)
):
    """Verify webhook signature (for webhook receivers)"""
    body = await request.body()
    payload = body.decode()

    is_valid = await webhook_service.verify_signature(
        secret,
        payload,
        x_webhook_signature
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )

    return {"valid": True}
