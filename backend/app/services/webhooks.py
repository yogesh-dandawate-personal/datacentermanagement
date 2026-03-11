"""
Webhook Framework Service
Sprint 12 - Task 2: Webhook registration, delivery, and testing
Handles webhook signing, verification, and retry logic
"""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, select, update
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models import Base, Tenant, UUID as ModelUUID
from app.exceptions import ValidationError, NotFoundError


class Webhook(Base):
    """Webhook registration"""
    __tablename__ = "webhooks"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)  # Webhook signing secret

    events = Column(JSON, default=list)  # List of event types to listen for
    is_active = Column(Boolean, default=True, index=True)

    delivery_success_count = Column(Integer, default=0)
    delivery_failure_count = Column(Integer, default=0)
    last_delivery_at = Column(DateTime, nullable=True)
    last_delivery_status = Column(String(50))  # success, failed, pending

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookDelivery(Base):
    """Webhook delivery log"""
    __tablename__ = "webhook_deliveries"

    id = Column(ModelUUID(as_uuid=True), primary_key=True, default=uuid4)
    webhook_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(ModelUUID(as_uuid=True), nullable=False, index=True)

    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)

    status = Column(String(50), default="pending", index=True)  # pending, success, failed, retrying
    http_status = Column(Integer)
    response_body = Column(Text)

    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)

    next_retry_at = Column(DateTime)
    delivered_at = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class WebhookService:
    """Webhook management and delivery service"""

    SUPPORTED_EVENTS = [
        "metric.created",
        "metric.updated",
        "calculation.completed",
        "report.published",
        "alert.triggered",
        "trade.completed",
        "threshold.breached"
    ]

    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

    async def register_webhook(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        name: str,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Register new webhook

        Args:
            db: Database session
            tenant_id: Tenant ID
            name: Webhook name
            url: Webhook URL
            events: List of event types to listen for
            secret: Optional signing secret (auto-generated if not provided)
        """
        # Validate events
        invalid_events = [e for e in events if e not in self.SUPPORTED_EVENTS]
        if invalid_events:
            raise ValidationError(
                f"Invalid events: {', '.join(invalid_events)}. "
                f"Supported: {', '.join(self.SUPPORTED_EVENTS)}"
            )

        # Validate URL
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValidationError("Webhook URL must start with http:// or https://")

        # Generate secret if not provided
        if not secret:
            secret = self._generate_secret()

        webhook = Webhook(
            tenant_id=tenant_id,
            name=name,
            url=url,
            secret=secret,
            events=events,
            is_active=True
        )

        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)

        return webhook

    async def get_webhook(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        webhook_id: UUID
    ) -> Optional[Webhook]:
        """Get webhook by ID"""
        result = await db.execute(
            select(Webhook).where(
                Webhook.id == webhook_id,
                Webhook.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def list_webhooks(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[Webhook]:
        """List all webhooks for tenant"""
        query = select(Webhook).where(Webhook.tenant_id == tenant_id)

        if is_active is not None:
            query = query.where(Webhook.is_active == is_active)

        result = await db.execute(query)
        return result.scalars().all()

    async def update_webhook(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        webhook_id: UUID,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Webhook:
        """Update webhook"""
        webhook = await self.get_webhook(db, tenant_id, webhook_id)

        if not webhook:
            raise NotFoundError(f"Webhook {webhook_id} not found")

        if name:
            webhook.name = name

        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                raise ValidationError("Webhook URL must start with http:// or https://")
            webhook.url = url

        if events:
            invalid_events = [e for e in events if e not in self.SUPPORTED_EVENTS]
            if invalid_events:
                raise ValidationError(f"Invalid events: {', '.join(invalid_events)}")
            webhook.events = events

        if is_active is not None:
            webhook.is_active = is_active

        webhook.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(webhook)

        return webhook

    async def delete_webhook(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        webhook_id: UUID
    ) -> bool:
        """Delete webhook"""
        webhook = await self.get_webhook(db, tenant_id, webhook_id)

        if not webhook:
            raise NotFoundError(f"Webhook {webhook_id} not found")

        await db.delete(webhook)
        await db.commit()

        return True

    async def trigger_event(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """
        Trigger webhook event

        Args:
            db: Database session
            tenant_id: Tenant ID
            event_type: Event type (e.g., "metric.created")
            payload: Event payload
        """
        if event_type not in self.SUPPORTED_EVENTS:
            raise ValidationError(f"Invalid event type: {event_type}")

        # Get all active webhooks listening for this event
        result = await db.execute(
            select(Webhook).where(
                Webhook.tenant_id == tenant_id,
                Webhook.is_active == True,
                Webhook.events.contains([event_type])
            )
        )
        webhooks = result.scalars().all()

        # Create delivery records and trigger deliveries
        for webhook in webhooks:
            delivery = WebhookDelivery(
                webhook_id=webhook.id,
                tenant_id=tenant_id,
                event_type=event_type,
                payload=payload,
                status="pending",
                attempts=0,
                max_attempts=self.MAX_RETRIES
            )

            db.add(delivery)
            await db.commit()
            await db.refresh(delivery)

            # Trigger delivery asynchronously
            asyncio.create_task(
                self._deliver_webhook(db, webhook, delivery)
            )

    async def _deliver_webhook(
        self,
        db: AsyncSession,
        webhook: Webhook,
        delivery: WebhookDelivery
    ):
        """Deliver webhook with retry logic"""
        payload_json = json.dumps(delivery.payload, default=str)
        signature = self._generate_signature(webhook.secret, payload_json)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": delivery.event_type,
            "X-Webhook-Delivery": str(delivery.id)
        }

        delivery.attempts += 1

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    delivery.http_status = response.status
                    delivery.response_body = await response.text()

                    if 200 <= response.status < 300:
                        # Success
                        delivery.status = "success"
                        delivery.delivered_at = datetime.utcnow()

                        webhook.delivery_success_count += 1
                        webhook.last_delivery_at = datetime.utcnow()
                        webhook.last_delivery_status = "success"

                    else:
                        # Failed
                        await self._handle_delivery_failure(db, webhook, delivery)

        except Exception as e:
            delivery.response_body = str(e)
            await self._handle_delivery_failure(db, webhook, delivery)

        await db.commit()

    async def _handle_delivery_failure(
        self,
        db: AsyncSession,
        webhook: Webhook,
        delivery: WebhookDelivery
    ):
        """Handle webhook delivery failure with retry logic"""
        if delivery.attempts < delivery.max_attempts:
            # Schedule retry
            delay_seconds = self.RETRY_DELAYS[delivery.attempts - 1]
            delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            delivery.status = "retrying"

            # Schedule retry task
            await asyncio.sleep(delay_seconds)
            await self._deliver_webhook(db, webhook, delivery)

        else:
            # Max retries exceeded
            delivery.status = "failed"

            webhook.delivery_failure_count += 1
            webhook.last_delivery_at = datetime.utcnow()
            webhook.last_delivery_status = "failed"

    async def test_webhook(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        webhook_id: UUID
    ) -> Dict[str, Any]:
        """
        Test webhook delivery

        Args:
            db: Database session
            tenant_id: Tenant ID
            webhook_id: Webhook ID

        Returns:
            Test result with status and response
        """
        webhook = await self.get_webhook(db, tenant_id, webhook_id)

        if not webhook:
            raise NotFoundError(f"Webhook {webhook_id} not found")

        test_payload = {
            "event": "webhook.test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "This is a test webhook delivery"
            }
        }

        payload_json = json.dumps(test_payload)
        signature = self._generate_signature(webhook.secret, payload_json)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": "webhook.test"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    return {
                        "status": "success" if 200 <= response.status < 300 else "failed",
                        "http_status": response.status,
                        "response": await response.text()
                    }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def verify_signature(
        self,
        secret: str,
        payload: str,
        signature: str
    ) -> bool:
        """
        Verify webhook signature

        Args:
            secret: Webhook secret
            payload: Request payload as string
            signature: Signature from X-Webhook-Signature header
        """
        expected_signature = self._generate_signature(secret, payload)
        return hmac.compare_digest(expected_signature, signature)

    async def get_deliveries(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        webhook_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Get webhook delivery history"""
        query = select(WebhookDelivery).where(
            WebhookDelivery.tenant_id == tenant_id
        )

        if webhook_id:
            query = query.where(WebhookDelivery.webhook_id == webhook_id)

        if status:
            query = query.where(WebhookDelivery.status == status)

        query = query.order_by(WebhookDelivery.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    def _generate_secret(self) -> str:
        """Generate webhook signing secret"""
        import secrets
        return secrets.token_urlsafe(32)

    def _generate_signature(self, secret: str, payload: str) -> str:
        """Generate HMAC signature for payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()


# Singleton instance
webhook_service = WebhookService()
