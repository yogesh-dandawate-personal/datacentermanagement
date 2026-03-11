"""
Advanced Reporting Models for Sprint 9

Implements:
- ScheduledReport: Automated report scheduling with cron
- ReportTemplate: Custom report templates
- ReportDistribution: Email/Slack/webhook delivery
- ReportDeliveryLog: Delivery tracking
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models import Base,UUID


class ScheduledReport(Base):
    """Automated report scheduling"""
    __tablename__ = "scheduled_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates_advanced.id", ondelete="SET NULL"), nullable=True)

    schedule_name = Column(String(255), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)  # sustainability, emissions, kpi, custom

    # Scheduling (cron-style)
    schedule_cron = Column(String(100), nullable=False)  # "0 9 1 * *" = 9am on 1st of month
    schedule_timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True, index=True)

    # Report configuration
    report_config = Column(JSON, default=dict)  # Parameters, filters, date ranges
    include_sections = Column(JSON)  # ["executive_summary", "trends", "recommendations"]

    # Distribution
    delivery_channels = Column(JSON)  # [{"type": "email", "recipients": [...]}, {"type": "slack", "webhook": "..."}]

    # Output formats
    formats = Column(JSON)  # ["pdf", "excel", "json"]

    # Execution tracking
    last_run_at = Column(DateTime, index=True)
    next_run_at = Column(DateTime, index=True)
    last_run_status = Column(String(50))  # success, failed, partial
    failure_count = Column(Integer, default=0)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    template = relationship("ReportTemplateAdvanced", back_populates="scheduled_reports")
    creator = relationship("User", foreign_keys=[created_by])
    delivery_logs = relationship("ReportDeliveryLog", back_populates="scheduled_report", cascade="all, delete-orphan")


class ReportTemplateAdvanced(Base):
    """Custom report templates"""
    __tablename__ = "report_templates_advanced"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    template_name = Column(String(255), nullable=False, index=True)
    template_type = Column(String(100), nullable=False)  # sustainability, emissions, kpi, custom
    description = Column(Text)

    # Template structure
    sections = Column(JSON, nullable=False)  # [{"name": "executive_summary", "order": 1, "config": {...}}, ...]

    # Data sources
    data_sources = Column(JSON)  # [{"type": "emissions", "filters": {...}}, {"type": "kpi", ...}]

    # Visualization config
    charts = Column(JSON)  # [{"type": "line", "data_source": "emissions", "config": {...}}, ...]

    # Formatting
    page_layout = Column(JSON)  # {"orientation": "portrait", "margins": {...}, ...}
    branding = Column(JSON)  # {"logo_url": "...", "colors": {...}, ...}

    # Metadata
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Available to all tenants
    category = Column(String(100))  # regulatory, internal, stakeholder
    tags = Column(JSON)  # ["monthly", "executive", "regulatory"]

    usage_count = Column(Integer, default=0)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])
    scheduled_reports = relationship("ScheduledReport", back_populates="template")


class ReportDistribution(Base):
    """Report distribution configuration"""
    __tablename__ = "report_distributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    distribution_name = Column(String(255), nullable=False)
    distribution_type = Column(String(50), nullable=False, index=True)  # email, slack, webhook, sftp

    # Email configuration
    email_recipients = Column(JSON)  # [{"email": "...", "name": "...", "type": "to/cc/bcc"}, ...]
    email_subject_template = Column(String(500))
    email_body_template = Column(Text)

    # Slack configuration
    slack_webhook_url = Column(String(500))
    slack_channel = Column(String(100))
    slack_message_template = Column(Text)

    # Webhook configuration
    webhook_url = Column(String(500))
    webhook_method = Column(String(10), default="POST")  # POST, PUT
    webhook_headers = Column(JSON)  # {"Authorization": "Bearer ...", ...}

    # SFTP configuration
    sftp_host = Column(String(255))
    sftp_port = Column(Integer, default=22)
    sftp_username = Column(String(100))
    sftp_password = Column(String(500))  # Encrypted
    sftp_path = Column(String(500))

    is_active = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


class ReportDeliveryLog(Base):
    """Delivery tracking for scheduled reports"""
    __tablename__ = "report_delivery_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_report_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_reports.id", ondelete="CASCADE"), nullable=True, index=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)

    delivery_attempt_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    delivery_status = Column(String(50), nullable=False, index=True)  # success, failed, partial

    # Delivery details
    delivery_channel = Column(String(50))  # email, slack, webhook, sftp
    recipients = Column(JSON)  # List of actual recipients

    # Files delivered
    files_delivered = Column(JSON)  # [{"format": "pdf", "size_bytes": 12345, "s3_key": "..."}, ...]

    # Response tracking
    http_status_code = Column(Integer)
    response_time_ms = Column(Integer)
    error_message = Column(Text)
    error_details = Column(JSON)

    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    scheduled_report = relationship("ScheduledReport", back_populates="delivery_logs")
    report = relationship("Report")


class ReportGenerationHistory(Base):
    """History of report generation runs"""
    __tablename__ = "report_generation_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_report_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_reports.id", ondelete="CASCADE"), nullable=True, index=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)

    generation_started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    generation_completed_at = Column(DateTime)
    generation_duration_ms = Column(Integer)

    status = Column(String(50), nullable=False, index=True)  # queued, running, completed, failed

    # Generation metadata
    report_period_start = Column(DateTime)
    report_period_end = Column(DateTime)
    data_points_processed = Column(Integer)

    # Performance metrics
    query_time_ms = Column(Integer)
    render_time_ms = Column(Integer)
    export_time_ms = Column(Integer)

    # Output
    output_formats = Column(JSON)  # ["pdf", "excel"]
    output_files = Column(JSON)  # [{"format": "pdf", "s3_key": "...", "size_bytes": 12345}, ...]

    # Error handling
    error_message = Column(Text)
    error_stacktrace = Column(Text)

    triggered_by = Column(String(50))  # cron, user, api
    triggered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    scheduled_report = relationship("ScheduledReport")
    report = relationship("Report")
    triggered_by_user = relationship("User", foreign_keys=[triggered_by_user_id])
