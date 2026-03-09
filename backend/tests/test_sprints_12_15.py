"""Tests for Sprints 12-15: Integrations, Mobile, Performance, Security"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Tenant, User, APIIntegration, MobileSession
from app.services.integrations_mobile_perf import (
    IntegrationService, MobileService, PerformanceService, SecurityService,
    BackupService, ConfigService
)


@pytest.fixture
def test_data(db: Session):
    tenant = Tenant(id=uuid.uuid4(), name="Test", slug="test", email="test@test.com")
    user = User(id=uuid.uuid4(), tenant_id=tenant.id, email="user@test.com", first_name="Test", last_name="User")
    db.add(tenant)
    db.add(user)
    db.commit()
    return {"tenant": tenant, "user": user}


class TestIntegrationService:
    def test_create_integration(self, db: Session, test_data):
        service = IntegrationService(db)
        result = service.create_integration(test_data["tenant"].id, "salesforce", "api_key_123")
        assert result["type"] == "salesforce"

    def test_log_api_call(self, db: Session, test_data):
        service = IntegrationService(db)
        result = service.log_api_call(test_data["tenant"].id, "GET", "/api/data", 200)
        assert result["status"] == 200

    def test_get_logs(self, db: Session, test_data):
        service = IntegrationService(db)
        service.log_api_call(test_data["tenant"].id, "POST", "/api/sync", 201)
        result = service.get_integration_logs(test_data["tenant"].id)
        assert len(result) >= 1


class TestMobileService:
    def test_create_session(self, db: Session, test_data):
        service = MobileService(db)
        result = service.create_session(test_data["user"].id, "device123", "iOS")
        assert result["device"] == "iOS"

    def test_send_notification(self, db: Session, test_data):
        service = MobileService(db)
        result = service.send_notification(test_data["user"].id, "Alert", "Test message")
        assert result["title"] == "Alert"

    def test_get_notifications(self, db: Session, test_data):
        service = MobileService(db)
        service.send_notification(test_data["user"].id, "N1", "M1")
        service.send_notification(test_data["user"].id, "N2", "M2")
        result = service.get_notifications(test_data["user"].id)
        assert len(result) == 2


class TestPerformanceService:
    def test_record_metric(self, db: Session, test_data):
        service = PerformanceService(db)
        result = service.record_metric(test_data["tenant"].id, "cpu_usage", Decimal("75.5"))
        assert result["metric"] == "cpu_usage"

    def test_cache_operations(self, db: Session, test_data):
        service = PerformanceService(db)
        service.cache_value("key1", {"data": "value"}, ttl_seconds=3600)
        result = service.get_cache("key1")
        assert result == {"data": "value"}

    def test_cache_expired(self, db: Session, test_data):
        service = PerformanceService(db)
        service.cache_value("key2", {"data": "value"}, ttl_seconds=-10)
        result = service.get_cache("key2")
        assert result is None


class TestSecurityService:
    def test_log_security_event(self, db: Session, test_data):
        service = SecurityService(db)
        result = service.log_security_event(test_data["tenant"].id, "login", test_data["user"].id)
        assert result["event"] == "login"

    def test_get_security_logs(self, db: Session, test_data):
        service = SecurityService(db)
        service.log_security_event(test_data["tenant"].id, "login")
        service.log_security_event(test_data["tenant"].id, "logout")
        result = service.get_security_logs(test_data["tenant"].id)
        assert len(result) >= 2


class TestBackupService:
    def test_log_backup(self, db: Session, test_data):
        service = BackupService(db)
        result = service.log_backup(test_data["tenant"].id, "full", 1024)
        assert result["type"] == "full"
        assert result["size_mb"] == 1024

    def test_backup_history(self, db: Session, test_data):
        service = BackupService(db)
        service.log_backup(test_data["tenant"].id, "full", 512)
        service.log_backup(test_data["tenant"].id, "incremental", 256)
        result = service.get_backup_history(test_data["tenant"].id)
        assert len(result) == 2


class TestConfigService:
    def test_set_and_get_config(self, db: Session, test_data):
        service = ConfigService(db)
        service.set_config("timeout", "30")
        result = service.get_config("timeout")
        assert result == "30"

    def test_feature_flag(self, db: Session, test_data):
        service = ConfigService(db)
        service.set_config("feature_new_ui", "true", is_feature_flag=True)
        result = service.is_feature_enabled("feature_new_ui")
        assert result == True

    def test_disabled_feature_flag(self, db: Session, test_data):
        service = ConfigService(db)
        service.set_config("feature_old_api", "false", is_feature_flag=True)
        result = service.is_feature_enabled("feature_old_api")
        assert result == False
