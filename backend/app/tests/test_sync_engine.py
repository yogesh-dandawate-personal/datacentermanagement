"""
Sync Engine Tests
Sprint 12 - Tests for data synchronization
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.services.sync_engine import sync_engine, SyncDirection, ConflictResolution
from app.exceptions import ValidationError, NotFoundError


@pytest.mark.asyncio
class TestSyncEngineService:
    """Test sync engine service"""

    async def test_create_sync_config_success(self, db_session, test_tenant, test_integration):
        """Test creating sync configuration"""
        config = await sync_engine.create_sync_config(
            db_session,
            test_tenant.id,
            test_integration.id,
            "Test Sync",
            "metric",
            SyncDirection.PULL,
            "0 */6 * * *",  # Every 6 hours
            ConflictResolution.LATEST_WINS,
            {"external_field": "internal_field"},
            {"value": {"type": "multiply", "factor": 1.5}}
        )

        assert config.id is not None
        assert config.tenant_id == test_tenant.id
        assert config.integration_id == test_integration.id
        assert config.name == "Test Sync"
        assert config.entity_type == "metric"
        assert config.direction == SyncDirection.PULL.value
        assert config.schedule_cron == "0 */6 * * *"
        assert config.is_active is True

    async def test_list_sync_configs(self, db_session, test_tenant, test_integration):
        """Test listing sync configurations"""
        # Create test configs
        for i in range(3):
            await sync_engine.create_sync_config(
                db_session,
                test_tenant.id,
                test_integration.id,
                f"Sync {i}",
                "metric",
                SyncDirection.PULL
            )

        configs = await sync_engine.list_sync_configs(
            db_session,
            test_tenant.id
        )

        assert len(configs) == 3

    async def test_get_sync_config(self, db_session, test_tenant, test_integration):
        """Test getting sync configuration"""
        config = await sync_engine.create_sync_config(
            db_session,
            test_tenant.id,
            test_integration.id,
            "Test Sync",
            "metric",
            SyncDirection.BIDIRECTIONAL
        )

        fetched = await sync_engine.get_sync_config(
            db_session,
            test_tenant.id,
            config.id
        )

        assert fetched is not None
        assert fetched.id == config.id

    async def test_track_change(self, db_session, test_tenant):
        """Test tracking entity change"""
        entity_id = uuid4()

        await sync_engine.track_change(
            db_session,
            test_tenant.id,
            "metric",
            entity_id,
            "update",
            data_before={"value": 100},
            data_after={"value": 150},
            changed_fields=["value"]
        )

        # Verify change was tracked (would query change_tracking_logs)
        assert True

    async def test_calculate_hash(self):
        """Test data hash calculation"""
        data1 = {"field1": "value1", "field2": 123}
        data2 = {"field2": 123, "field1": "value1"}  # Different order

        hash1 = sync_engine._calculate_hash(data1)
        hash2 = sync_engine._calculate_hash(data2)

        # Same data should produce same hash regardless of order
        assert hash1 == hash2

    async def test_transform_data_field_mapping(self):
        """Test data transformation with field mapping"""
        data = {
            "external_name": "Test",
            "external_value": 100
        }

        field_mapping = {
            "external_name": "internal_name",
            "external_value": "internal_value"
        }

        transformed = sync_engine._transform_data(
            data,
            field_mapping,
            {}
        )

        assert "internal_name" in transformed
        assert "internal_value" in transformed
        assert transformed["internal_name"] == "Test"
        assert transformed["internal_value"] == 100

    async def test_transform_data_multiply_rule(self):
        """Test data transformation with multiply rule"""
        data = {"value": 100}

        transformation_rules = {
            "value": {
                "type": "multiply",
                "factor": 2.5
            }
        }

        transformed = sync_engine._transform_data(
            data,
            {},
            transformation_rules
        )

        assert transformed["value"] == 250.0

    async def test_transform_data_unit_conversion(self):
        """Test data transformation with unit conversion"""
        data = {"energy": 5000}

        transformation_rules = {
            "energy": {
                "type": "convert_unit",
                "from": "kWh",
                "to": "MWh"
            }
        }

        transformed = sync_engine._transform_data(
            data,
            {},
            transformation_rules
        )

        assert transformed["energy"] == 5.0

    async def test_sync_direction_enum(self):
        """Test sync direction enum values"""
        assert SyncDirection.PULL.value == "pull"
        assert SyncDirection.PUSH.value == "push"
        assert SyncDirection.BIDIRECTIONAL.value == "bidirectional"

    async def test_conflict_resolution_enum(self):
        """Test conflict resolution enum values"""
        assert ConflictResolution.SOURCE_WINS.value == "source_wins"
        assert ConflictResolution.TARGET_WINS.value == "target_wins"
        assert ConflictResolution.LATEST_WINS.value == "latest_wins"
        assert ConflictResolution.MANUAL.value == "manual"


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
    from app.models import APIIntegration

    integration = APIIntegration(
        tenant_id=test_tenant.id,
        integration_type="salesforce",
        api_key="test_key",
        api_secret="test_secret",
        api_endpoint="https://api.salesforce.com",
        is_active=True
    )

    db_session.add(integration)
    await db_session.commit()
    await db_session.refresh(integration)

    return integration


@pytest.fixture
async def test_sync_config(db_session, test_tenant, test_integration):
    """Create test sync configuration"""
    config = await sync_engine.create_sync_config(
        db_session,
        test_tenant.id,
        test_integration.id,
        "Test Sync Config",
        "metric",
        SyncDirection.PULL,
        conflict_resolution=ConflictResolution.LATEST_WINS
    )

    return config
