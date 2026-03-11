"""
Webhook Service Tests
Sprint 12 - Tests for webhook management
"""

import pytest
from uuid import uuid4

from app.services.webhooks import webhook_service
from app.exceptions import ValidationError, NotFoundError


@pytest.mark.asyncio
class TestWebhookService:
    """Test webhook service"""

    async def test_register_webhook_success(self, db_session, test_tenant):
        """Test registering webhook"""
        webhook = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["metric.created", "report.published"]
        )

        assert webhook.id is not None
        assert webhook.tenant_id == test_tenant.id
        assert webhook.name == "Test Webhook"
        assert webhook.url == "https://example.com/webhook"
        assert len(webhook.events) == 2
        assert webhook.is_active is True
        assert webhook.secret is not None

    async def test_register_webhook_with_custom_secret(self, db_session, test_tenant):
        """Test registering webhook with custom secret"""
        custom_secret = "my_custom_secret_123"

        webhook = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["metric.created"],
            custom_secret
        )

        assert webhook.secret == custom_secret

    async def test_register_webhook_invalid_events(self, db_session, test_tenant):
        """Test registering webhook with invalid events"""
        with pytest.raises(ValidationError) as exc:
            await webhook_service.register_webhook(
                db_session,
                test_tenant.id,
                "Test Webhook",
                "https://example.com/webhook",
                ["invalid.event", "metric.created"]
            )

        assert "Invalid events" in str(exc.value)

    async def test_register_webhook_invalid_url(self, db_session, test_tenant):
        """Test registering webhook with invalid URL"""
        with pytest.raises(ValidationError) as exc:
            await webhook_service.register_webhook(
                db_session,
                test_tenant.id,
                "Test Webhook",
                "not-a-valid-url",
                ["metric.created"]
            )

        assert "must start with http://" in str(exc.value)

    async def test_list_webhooks(self, db_session, test_tenant):
        """Test listing webhooks"""
        # Create test webhooks
        for i in range(3):
            await webhook_service.register_webhook(
                db_session,
                test_tenant.id,
                f"Webhook {i}",
                f"https://example.com/webhook{i}",
                ["metric.created"]
            )

        webhooks = await webhook_service.list_webhooks(
            db_session,
            test_tenant.id
        )

        assert len(webhooks) == 3

    async def test_list_webhooks_filter_active(self, db_session, test_tenant):
        """Test listing webhooks with active filter"""
        # Create active webhook
        active = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Active Webhook",
            "https://example.com/active",
            ["metric.created"]
        )

        # Create inactive webhook
        inactive = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Inactive Webhook",
            "https://example.com/inactive",
            ["metric.created"]
        )

        await webhook_service.update_webhook(
            db_session,
            test_tenant.id,
            inactive.id,
            is_active=False
        )

        # List only active
        active_webhooks = await webhook_service.list_webhooks(
            db_session,
            test_tenant.id,
            is_active=True
        )

        assert len(active_webhooks) == 1
        assert active_webhooks[0].id == active.id

    async def test_get_webhook(self, db_session, test_tenant):
        """Test getting webhook by ID"""
        webhook = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["metric.created"]
        )

        fetched = await webhook_service.get_webhook(
            db_session,
            test_tenant.id,
            webhook.id
        )

        assert fetched is not None
        assert fetched.id == webhook.id

    async def test_update_webhook(self, db_session, test_tenant):
        """Test updating webhook"""
        webhook = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Original Name",
            "https://example.com/original",
            ["metric.created"]
        )

        updated = await webhook_service.update_webhook(
            db_session,
            test_tenant.id,
            webhook.id,
            name="Updated Name",
            url="https://example.com/updated",
            events=["report.published", "alert.triggered"]
        )

        assert updated.name == "Updated Name"
        assert updated.url == "https://example.com/updated"
        assert len(updated.events) == 2

    async def test_delete_webhook(self, db_session, test_tenant):
        """Test deleting webhook"""
        webhook = await webhook_service.register_webhook(
            db_session,
            test_tenant.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["metric.created"]
        )

        result = await webhook_service.delete_webhook(
            db_session,
            test_tenant.id,
            webhook.id
        )

        assert result is True

        # Verify deleted
        fetched = await webhook_service.get_webhook(
            db_session,
            test_tenant.id,
            webhook.id
        )

        assert fetched is None

    async def test_generate_signature(self):
        """Test signature generation"""
        secret = "test_secret"
        payload = '{"event": "test"}'

        signature1 = webhook_service._generate_signature(secret, payload)
        signature2 = webhook_service._generate_signature(secret, payload)

        # Same input should generate same signature
        assert signature1 == signature2

        # Different secret should generate different signature
        signature3 = webhook_service._generate_signature("different_secret", payload)
        assert signature1 != signature3

    async def test_verify_signature(self):
        """Test signature verification"""
        secret = "test_secret"
        payload = '{"event": "test"}'

        signature = webhook_service._generate_signature(secret, payload)

        # Valid signature
        is_valid = await webhook_service.verify_signature(secret, payload, signature)
        assert is_valid is True

        # Invalid signature
        is_valid = await webhook_service.verify_signature(secret, payload, "invalid_sig")
        assert is_valid is False

    async def test_supported_events(self):
        """Test supported events list"""
        events = webhook_service.SUPPORTED_EVENTS

        assert "metric.created" in events
        assert "metric.updated" in events
        assert "calculation.completed" in events
        assert "report.published" in events
        assert "alert.triggered" in events
        assert "trade.completed" in events
        assert "threshold.breached" in events


# Fixtures

@pytest.fixture
async def test_tenant(db_session):
    """Create test tenant"""
    from app.models import Tenant

    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com"
    )

    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)

    return tenant


@pytest.fixture
async def test_webhook(db_session, test_tenant):
    """Create test webhook"""
    webhook = await webhook_service.register_webhook(
        db_session,
        test_tenant.id,
        "Test Webhook",
        "https://example.com/webhook",
        ["metric.created", "report.published"]
    )

    return webhook
