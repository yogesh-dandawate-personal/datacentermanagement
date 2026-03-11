"""
Integration Service Tests
Sprint 12 - Tests for external API integrations
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.services.integrations import integration_service, RateLimiter
from app.exceptions import ValidationError, NotFoundError


@pytest.mark.asyncio
class TestIntegrationService:
    """Test integration service"""

    async def test_create_integration_success(self, db_session, test_tenant):
        """Test creating integration"""
        credentials = {
            "api_key": "test_key_123",
            "api_secret": "test_secret_456"
        }

        integration = await integration_service.create_integration(
            db_session,
            test_tenant.id,
            "salesforce",
            credentials
        )

        assert integration.id is not None
        assert integration.tenant_id == test_tenant.id
        assert integration.integration_type == "salesforce"
        assert integration.is_active is True

    async def test_create_integration_invalid_type(self, db_session, test_tenant):
        """Test creating integration with invalid type"""
        credentials = {"api_key": "test_key"}

        with pytest.raises(ValidationError) as exc:
            await integration_service.create_integration(
                db_session,
                test_tenant.id,
                "invalid_type",
                credentials
            )

        assert "Unsupported integration type" in str(exc.value)

    async def test_list_integrations(self, db_session, test_tenant):
        """Test listing integrations"""
        # Create test integrations
        for i in range(3):
            await integration_service.create_integration(
                db_session,
                test_tenant.id,
                "slack",
                {"api_key": f"key_{i}"}
            )

        integrations = await integration_service.list_integrations(
            db_session,
            test_tenant.id
        )

        assert len(integrations) == 3

    async def test_get_integration(self, db_session, test_tenant):
        """Test getting integration by ID"""
        integration = await integration_service.create_integration(
            db_session,
            test_tenant.id,
            "github",
            {"api_key": "test_key"}
        )

        fetched = await integration_service.get_integration(
            db_session,
            test_tenant.id,
            integration.id
        )

        assert fetched is not None
        assert fetched.id == integration.id

    async def test_delete_integration(self, db_session, test_tenant):
        """Test deleting integration"""
        integration = await integration_service.create_integration(
            db_session,
            test_tenant.id,
            "slack",
            {"api_key": "test_key"}
        )

        result = await integration_service.delete_integration(
            db_session,
            test_tenant.id,
            integration.id
        )

        assert result is True

        # Verify deleted
        fetched = await integration_service.get_integration(
            db_session,
            test_tenant.id,
            integration.id
        )

        assert fetched is None

    async def test_delete_nonexistent_integration(self, db_session, test_tenant):
        """Test deleting non-existent integration"""
        with pytest.raises(NotFoundError):
            await integration_service.delete_integration(
                db_session,
                test_tenant.id,
                uuid4()
            )


@pytest.mark.asyncio
class TestRateLimiter:
    """Test rate limiter"""

    async def test_rate_limiter_allows_within_limit(self):
        """Test rate limiter allows requests within limit"""
        limiter = RateLimiter(rate=5, per=1)

        # Should allow first 5 requests
        for _ in range(5):
            allowed = await limiter.acquire()
            assert allowed is True

    async def test_rate_limiter_blocks_exceeding_limit(self):
        """Test rate limiter blocks requests exceeding limit"""
        limiter = RateLimiter(rate=2, per=1)

        # Allow first 2
        await limiter.acquire()
        await limiter.acquire()

        # Block 3rd
        allowed = await limiter.acquire()
        assert allowed is False


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
async def test_integration(db_session, test_tenant):
    """Create test integration"""
    integration = await integration_service.create_integration(
        db_session,
        test_tenant.id,
        "salesforce",
        {"api_key": "test_key", "api_secret": "test_secret"}
    )

    return integration
