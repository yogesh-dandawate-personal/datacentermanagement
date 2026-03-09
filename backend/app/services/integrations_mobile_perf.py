"""Services for Sprints 12-15: Integrations, Mobile, Performance, and Security"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Dict, Optional
from decimal import Decimal

from app.models import (
    APIIntegration, APILog, MobileSession, MobileNotification,
    CacheEntry, PerformanceMetric, SystemConfig, BackupLog, SecurityLog
)


class IntegrationService:
    def __init__(self, db: Session):
        self.db = db

    def create_integration(self, tenant_id: UUID, integration_type: str, api_key: str) -> Dict:
        integration = APIIntegration(tenant_id=tenant_id, integration_type=integration_type, api_key=api_key)
        self.db.add(integration)
        self.db.commit()
        return {"id": str(integration.id), "type": integration_type}

    def log_api_call(self, tenant_id: UUID, method: str, endpoint: str, status_code: int) -> Dict:
        log = APILog(tenant_id=tenant_id, method=method, endpoint=endpoint, status_code=status_code)
        self.db.add(log)
        self.db.commit()
        return {"id": str(log.id), "status": status_code}

    def get_integration_logs(self, tenant_id: UUID) -> List[Dict]:
        logs = self.db.query(APILog).filter(APILog.tenant_id == tenant_id).all()
        return [{"method": l.method, "endpoint": l.endpoint, "status": l.status_code} for l in logs]


class MobileService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: UUID, device_id: str, device_type: str) -> Dict:
        session = MobileSession(user_id=user_id, device_id=device_id, device_type=device_type)
        self.db.add(session)
        self.db.commit()
        return {"id": str(session.id), "device": device_type}

    def send_notification(self, user_id: UUID, title: str, message: str) -> Dict:
        notif = MobileNotification(user_id=user_id, title=title, message=message)
        self.db.add(notif)
        self.db.commit()
        return {"id": str(notif.id), "title": title}

    def get_notifications(self, user_id: UUID) -> List[Dict]:
        notifs = self.db.query(MobileNotification).filter(MobileNotification.user_id == user_id).all()
        return [{"title": n.title, "message": n.message, "read": n.is_read} for n in notifs]


class PerformanceService:
    def __init__(self, db: Session):
        self.db = db

    def record_metric(self, tenant_id: UUID, metric_name: str, metric_value: Decimal) -> Dict:
        metric = PerformanceMetric(tenant_id=tenant_id, metric_name=metric_name, metric_value=metric_value)
        self.db.add(metric)
        self.db.commit()
        return {"id": str(metric.id), "metric": metric_name}

    def cache_value(self, cache_key: str, cache_value: Dict, ttl_seconds: int = 3600) -> Dict:
        expires = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        cache = CacheEntry(cache_key=cache_key, cache_value=cache_value, expires_at=expires)
        self.db.add(cache)
        self.db.commit()
        return {"key": cache_key, "ttl": ttl_seconds}

    def get_cache(self, cache_key: str) -> Optional[Dict]:
        cache = self.db.query(CacheEntry).filter(CacheEntry.cache_key == cache_key).first()
        if cache and (cache.expires_at is None or cache.expires_at > datetime.utcnow()):
            return cache.cache_value
        return None


class SecurityService:
    def __init__(self, db: Session):
        self.db = db

    def log_security_event(self, tenant_id: UUID, event_type: str, user_id: Optional[UUID] = None) -> Dict:
        event = SecurityLog(tenant_id=tenant_id, event_type=event_type, user_id=user_id, severity="low")
        self.db.add(event)
        self.db.commit()
        return {"id": str(event.id), "event": event_type}

    def get_security_logs(self, tenant_id: UUID, days: int = 30) -> List[Dict]:
        since = datetime.utcnow() - timedelta(days=days)
        logs = self.db.query(SecurityLog).filter(
            SecurityLog.tenant_id == tenant_id,
            SecurityLog.created_at >= since
        ).all()
        return [{"event": l.event_type, "severity": l.severity, "timestamp": l.created_at.isoformat()} for l in logs]


class BackupService:
    def __init__(self, db: Session):
        self.db = db

    def log_backup(self, tenant_id: UUID, backup_type: str, file_size_mb: int) -> Dict:
        backup = BackupLog(tenant_id=tenant_id, backup_type=backup_type, file_size_mb=file_size_mb, backup_status="success")
        self.db.add(backup)
        self.db.commit()
        return {"id": str(backup.id), "type": backup_type, "size_mb": file_size_mb}

    def get_backup_history(self, tenant_id: UUID) -> List[Dict]:
        backups = self.db.query(BackupLog).filter(BackupLog.tenant_id == tenant_id).all()
        return [{"type": b.backup_type, "size_mb": b.file_size_mb, "status": b.backup_status} for b in backups]


class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def set_config(self, config_key: str, config_value: str, is_feature_flag: bool = False) -> Dict:
        config = SystemConfig(config_key=config_key, config_value=config_value, is_feature_flag=is_feature_flag)
        self.db.add(config)
        self.db.commit()
        return {"key": config_key, "value": config_value}

    def get_config(self, config_key: str) -> Optional[str]:
        config = self.db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
        return config.config_value if config else None

    def is_feature_enabled(self, feature_flag: str) -> bool:
        config = self.db.query(SystemConfig).filter(
            SystemConfig.config_key == feature_flag,
            SystemConfig.is_feature_flag == True
        ).first()
        return config and config.config_value == "true" if config else False
