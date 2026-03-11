"""
Notification System Models for Sprint 9

Implements:
- Notification: Alert messages
- NotificationPreference: User notification preferences
- NotificationLog: Delivery tracking
- NotificationChannel: Channel configuration (Email, Slack, SMS, Webhook)
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models import Base,UUID


class Notification(Base):
    """Alert notifications"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)

    notification_type = Column(String(100), nullable=False, index=True)  # threshold_breach, anomaly, target_missed, report_ready
    category = Column(String(50), nullable=False, index=True)  # alert, info, warning, critical

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    message_html = Column(Text)  # HTML formatted version for email

    # Alert context
    source_entity_type = Column(String(100))  # kpi, emission, energy, benchmark
    source_entity_id = Column(UUID(as_uuid=True))
    related_data = Column(JSON)  # Context data for the notification

    # Priority and urgency
    priority = Column(String(20), nullable=False, default="medium", index=True)  # low, medium, high, critical
    urgency = Column(String(20), default="normal")  # normal, urgent, immediate
    severity = Column(String(20))  # info, warning, error, critical

    # Delivery configuration
    delivery_channels = Column(JSON, default=list)  # ["email", "slack", "sms"]
    recipients = Column(JSON)  # [{"type": "user", "id": "..."}, {"type": "role", "role": "admin"}, ...]

    # Lifecycle
    status = Column(String(50), default="pending", index=True)  # pending, sent, failed, acknowledged, resolved
    sent_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Resolution
    resolution_notes = Column(Text)
    auto_resolve = Column(Boolean, default=False)  # Auto-resolve when condition clears
    auto_resolved = Column(Boolean, default=False)

    # Metadata
    expires_at = Column(DateTime)  # Notification expiry for time-sensitive alerts
    tags = Column(JSON)  # ["sla_violation", "after_hours", ...]

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    delivery_logs = relationship("NotificationLog", back_populates="notification", cascade="all, delete-orphan")


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    email_address = Column(String(255))  # Override default user email
    email_digest = Column(Boolean, default=False)  # Daily digest instead of immediate
    email_digest_time = Column(String(5))  # "09:00" for 9am

    slack_enabled = Column(Boolean, default=False)
    slack_user_id = Column(String(255))  # Slack user ID
    slack_channel = Column(String(100))  # Preferred Slack channel

    sms_enabled = Column(Boolean, default=False)
    sms_phone_number = Column(String(20))

    webhook_enabled = Column(Boolean, default=False)
    webhook_url = Column(String(500))

    # Notification type preferences
    notification_types = Column(JSON, default=dict)  # {"threshold_breach": {"enabled": true, "channels": ["email", "slack"]}, ...}

    # Priority filtering
    minimum_priority = Column(String(20), default="low")  # Only send notifications >= this priority
    critical_only_off_hours = Column(Boolean, default=True)  # Only critical notifications outside business hours

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))  # "08:00"
    quiet_hours_timezone = Column(String(50), default="UTC")

    # Rate limiting
    max_notifications_per_hour = Column(Integer, default=10)
    max_notifications_per_day = Column(Integer, default=100)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    tenant = relationship("Tenant")


class NotificationLog(Base):
    """Delivery tracking for notifications"""
    __tablename__ = "notification_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    delivery_channel = Column(String(50), nullable=False, index=True)  # email, slack, sms, webhook
    recipient = Column(String(255), nullable=False)  # email address, slack user ID, phone number

    # Delivery status
    status = Column(String(50), nullable=False, index=True)  # queued, sending, sent, failed, bounced
    attempt_count = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)

    # Timing
    queued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)  # Confirmed delivery (e.g., Slack ack, SMS delivery receipt)
    failed_at = Column(DateTime)

    # Response tracking
    http_status_code = Column(Integer)
    response_message = Column(Text)
    response_time_ms = Column(Integer)

    # Error handling
    error_message = Column(Text)
    error_code = Column(String(50))
    retry_scheduled_at = Column(DateTime)

    # External tracking
    external_id = Column(String(255))  # Message ID from external service (SendGrid, Twilio, etc.)
    tracking_url = Column(String(500))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    notification = relationship("Notification", back_populates="delivery_logs")
    tenant = relationship("Tenant")


class NotificationChannel(Base):
    """Notification channel configuration"""
    __tablename__ = "notification_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    channel_name = Column(String(255), nullable=False)
    channel_type = Column(String(50), nullable=False, index=True)  # email, slack, sms, webhook

    # Email configuration (SMTP)
    smtp_host = Column(String(255))
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255))
    smtp_password = Column(String(500))  # Encrypted
    smtp_use_tls = Column(Boolean, default=True)
    smtp_from_email = Column(String(255))
    smtp_from_name = Column(String(255))

    # SendGrid configuration
    sendgrid_api_key = Column(String(500))  # Encrypted
    sendgrid_from_email = Column(String(255))

    # Slack configuration
    slack_webhook_url = Column(String(500))  # Encrypted
    slack_bot_token = Column(String(500))  # Encrypted
    slack_default_channel = Column(String(100))

    # Twilio (SMS) configuration
    twilio_account_sid = Column(String(255))
    twilio_auth_token = Column(String(500))  # Encrypted
    twilio_from_number = Column(String(20))

    # SNS (AWS) configuration
    sns_access_key = Column(String(255))
    sns_secret_key = Column(String(500))  # Encrypted
    sns_region = Column(String(50))

    # Webhook configuration
    webhook_url = Column(String(500))
    webhook_method = Column(String(10), default="POST")
    webhook_headers = Column(JSON)  # {"Authorization": "Bearer ...", ...}
    webhook_auth_type = Column(String(50))  # none, basic, bearer, api_key

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)

    # Health monitoring
    is_active = Column(Boolean, default=True, index=True)
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)

    # Usage statistics
    total_sent = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    last_sent_at = Column(DateTime)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


class NotificationTemplate(Base):
    """Reusable notification templates"""
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    template_name = Column(String(255), nullable=False, index=True)
    template_type = Column(String(100), nullable=False)  # threshold_breach, report_ready, anomaly_detected

    # Template content (supports Jinja2 templating)
    subject_template = Column(String(500))  # For email/SMS
    message_template = Column(Text, nullable=False)
    message_html_template = Column(Text)  # HTML version for email

    # Slack-specific formatting
    slack_blocks_template = Column(JSON)  # Slack Block Kit JSON

    # Variables
    required_variables = Column(JSON)  # ["metric_name", "current_value", "threshold_value"]
    optional_variables = Column(JSON)

    # Usage
    is_default = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])
