"""
Emissions Capture ESG System Models for iNetZero

Implements comprehensive emissions tracking and ESG reporting:
- EmissionsSource: Defines emission sources and scope
- EmissionsActivityData: Raw activity data for emissions calculation
- EmissionsCalculation: Calculated emissions by scope
- EmissionsCalculationDetail: Line-item audit trail
- EmissionsReport: ESG compliance reports
- EmissionsReportSection: Report sections
- EmissionsTarget: Emissions reduction targets
- EmissionsTargetProgress: Target tracking
- EmissionsAlert: Emissions alerts and breaches
- EmissionsAlertRule: Alert rule definitions
- EmissionsIngestionLog: Data ingestion tracking
- EmissionsDataQuality: Data quality metrics
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import uuid

from app.models import Base,UUID


class EmissionsSource(Base):
    """Defines emission sources for tracking"""
    __tablename__ = "emissions_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=True, index=True)

    source_name = Column(String(255), nullable=False)  # e.g., "Natural Gas Boilers", "Grid Electricity"
    source_type = Column(String(100), nullable=False, index=True)  # fuel_consumption, electricity, refrigerant, etc.
    scope = Column(String(20), nullable=False, index=True)  # scope1, scope2, scope3

    asset_id = Column(String(100))  # Reference to physical asset/equipment
    location = Column(String(255))  # Physical location of source

    emission_factor_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)

    unit_of_measure = Column(String(50), nullable=False)  # kWh, gallon, kg, etc.
    description = Column(Text)

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    facility = relationship("Facility")
    emission_factor = relationship("EmissionFactor")
    activity_data = relationship("EmissionsActivityData", back_populates="source", cascade="all, delete-orphan")
    calculations = relationship("EmissionsCalculation", back_populates="source", cascade="all, delete-orphan")


class EmissionsActivityData(Base):
    """Raw activity data for emissions calculation"""
    __tablename__ = "emissions_activity_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("emissions_sources.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)  # When activity occurred
    activity_value = Column(Numeric(18, 6), nullable=False)  # Amount consumed/produced
    activity_unit = Column(String(50), nullable=False)  # kWh, gallon, kg, etc.

    data_source = Column(String(100))  # manual_entry, api_import, dcim, iot_device, etc.
    ingestion_method = Column(String(100))  # csv_upload, manual_form, streaming, etc.

    # Quality tracking
    validation_status = Column(String(50), default="valid", index=True)  # valid, invalid, suspected_anomaly
    validation_notes = Column(Text)

    # Metadata
    source_metadata = Column(JSON, default=dict)  # Additional context

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    source = relationship("EmissionsSource", back_populates="activity_data")
    calculation_details = relationship("EmissionsCalculationDetail", back_populates="activity_data")


class EmissionsCalculation(Base):
    """Calculated emissions by scope"""
    __tablename__ = "emissions_calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("emissions_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    calculation_period_start = Column(DateTime, nullable=False, index=True)
    calculation_period_end = Column(DateTime, nullable=False, index=True)

    scope = Column(String(20), nullable=False, index=True)  # scope1, scope2, scope3
    scope_3_category = Column(String(50), nullable=True, index=True)  # supply_chain, business_travel, employee_commute, waste_disposal, purchased_goods, franchises, investments
    total_emissions_kgco2e = Column(Numeric(18, 6), nullable=False)  # kg CO2e

    calculation_method = Column(String(100))  # average, sum, weighted_average, supply_chain_lifecycle, business_travel_distance_based, etc.
    factor_used_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)

    # Calculation breakdown (JSON for flexible storage of mode/supplier/category breakdowns)
    calculation_breakdown = Column(JSON, nullable=True)  # {'suppliers': {...}, 'by_mode': {...}, etc.}

    status = Column(String(50), default="draft", index=True)  # draft, finalized, approved

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    approval_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    source = relationship("EmissionsSource", back_populates="calculations")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    details = relationship("EmissionsCalculationDetail", back_populates="calculation", cascade="all, delete-orphan")


class EmissionsCalculationDetail(Base):
    """Line-item audit trail for emissions calculations"""
    __tablename__ = "emissions_calculation_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(UUID(as_uuid=True), ForeignKey("emissions_calculations.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_data_id = Column(UUID(as_uuid=True), ForeignKey("emissions_activity_data.id", ondelete="SET NULL"), nullable=True)

    factor_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    factor_value = Column(Numeric(12, 6), nullable=False)  # Factor used at time of calculation

    activity_value = Column(Numeric(18, 6), nullable=False)
    activity_unit = Column(String(50))

    emissions_kgco2e = Column(Numeric(18, 6), nullable=False)  # Result

    calculation_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    calculation = relationship("EmissionsCalculation", back_populates="details")
    activity_data = relationship("EmissionsActivityData", back_populates="calculation_details")
    factor = relationship("EmissionFactor")


class EmissionsReport(Base):
    """ESG compliance reports"""
    __tablename__ = "emissions_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)  # ghg_protocol, cdp, gri, tcfd, custom
    reporting_year = Column(Integer, nullable=False, index=True)
    reporting_period_start = Column(DateTime, nullable=False)
    reporting_period_end = Column(DateTime, nullable=False)

    status = Column(String(50), default="draft", index=True)  # draft, pending_review, approved, submitted, published

    # Emissions summary
    scope_1_emissions = Column(Numeric(18, 6))  # tonnes CO2e
    scope_2_emissions = Column(Numeric(18, 6))  # tonnes CO2e
    scope_3_emissions = Column(Numeric(18, 6))  # tonnes CO2e
    total_emissions = Column(Numeric(18, 6))  # tonnes CO2e

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    sections = relationship("EmissionsReportSection", back_populates="report", cascade="all, delete-orphan")


class EmissionsReportSection(Base):
    """Individual sections within a report"""
    __tablename__ = "emissions_report_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("emissions_reports.id", ondelete="CASCADE"), nullable=False, index=True)

    section_name = Column(String(255), nullable=False)  # executive_summary, methodology, results, etc.
    section_order = Column(Integer, default=0)

    content = Column(JSON, default=dict)  # Formatted section content
    completion_percentage = Column(Integer, default=0)  # 0-100

    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("EmissionsReport", back_populates="sections")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class EmissionsTarget(Base):
    """Emissions reduction targets and goals"""
    __tablename__ = "emissions_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    target_name = Column(String(255), nullable=False)  # e.g., "Net-zero 2030", "50% reduction by 2025"
    target_type = Column(String(50), nullable=False)  # absolute_reduction, intensity_reduction, net_zero
    description = Column(Text)

    baseline_year = Column(Integer, nullable=False)
    baseline_value = Column(Numeric(18, 6), nullable=False)  # Metric tonnes CO2e

    target_year = Column(Integer, nullable=False, index=True)
    target_value = Column(Numeric(18, 6), nullable=False)  # Metric tonnes CO2e

    scope = Column(String(20))  # scope1, scope2, scope3, all

    status = Column(String(50), default="on_track", index=True)  # on_track, at_risk, failed, achieved
    progress_percentage = Column(Integer, default=0)  # 0-100

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    progress_records = relationship("EmissionsTargetProgress", back_populates="target", cascade="all, delete-orphan")


class EmissionsTargetProgress(Base):
    """Target progress tracking"""
    __tablename__ = "emissions_target_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_id = Column(UUID(as_uuid=True), ForeignKey("emissions_targets.id", ondelete="CASCADE"), nullable=False, index=True)

    reporting_period = Column(String(50), nullable=False)  # Q1, Q2, Q3, Q4, annual
    reporting_year = Column(Integer, nullable=False, index=True)

    actual_emissions = Column(Numeric(18, 6), nullable=False)  # Metric tonnes CO2e
    target_emissions = Column(Numeric(18, 6), nullable=False)  # Expected value at this point

    progress_percentage = Column(Numeric(8, 2))  # How close to target
    on_track_status = Column(String(50))  # on_track, at_risk, failed

    notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    target = relationship("EmissionsTarget", back_populates="progress_records")


class EmissionsAlert(Base):
    """Emissions alerts and threshold breaches"""
    __tablename__ = "emissions_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    alert_rule_id = Column(UUID(as_uuid=True), ForeignKey("emissions_alert_rules.id", ondelete="SET NULL"), nullable=True)

    alert_type = Column(String(50), nullable=False)  # threshold_breach, anomaly, target_at_risk, etc.
    severity = Column(String(20), nullable=False, index=True)  # info, warning, critical

    title = Column(String(255), nullable=False)
    description = Column(Text)

    triggered_value = Column(Numeric(18, 6))
    threshold_value = Column(Numeric(18, 6))

    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved

    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    rule = relationship("EmissionsAlertRule")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    resolver = relationship("User", foreign_keys=[resolved_by])


class EmissionsAlertRule(Base):
    """Alert rule definitions"""
    __tablename__ = "emissions_alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_name = Column(String(255), nullable=False)
    description = Column(Text)

    metric = Column(String(100), nullable=False)  # total_emissions, scope_1, carbon_intensity, etc.
    operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==, !=
    threshold_value = Column(Numeric(18, 6), nullable=False)

    severity = Column(String(20), nullable=False)  # info, warning, critical

    notification_channels = Column(JSON, default=list)  # ["email", "slack", "webhook"]
    notification_recipients = Column(JSON, default=list)  # List of user IDs or email addresses

    is_enabled = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")


class EmissionsIngestionLog(Base):
    """Data ingestion tracking"""
    __tablename__ = "emissions_ingestion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("emissions_sources.id", ondelete="SET NULL"), nullable=True)

    ingestion_method = Column(String(100), nullable=False)  # csv_upload, api, manual, etc.
    data_source = Column(String(100))  # Which system provided the data

    records_received = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    status = Column(String(50), default="completed", index=True)  # completed, partial_success, failed
    error_log = Column(JSON, default=list)  # List of error messages

    ingestion_started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ingestion_completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    source = relationship("EmissionsSource")


class EmissionsDataQuality(Base):
    """Data quality metrics for emissions data"""
    __tablename__ = "emissions_data_quality"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("emissions_sources.id", ondelete="CASCADE"), nullable=False, index=True)

    reporting_period = Column(String(50), nullable=False)  # Q1, annual, monthly, etc.
    reporting_year = Column(Integer, nullable=False, index=True)

    completeness_score = Column(Numeric(5, 2))  # 0-100, % of expected data points present
    accuracy_score = Column(Numeric(5, 2))  # 0-100, based on validation rules

    anomaly_count = Column(Integer, default=0)  # Number of anomalies detected
    validation_error_count = Column(Integer, default=0)  # Number of validation errors

    quality_grade = Column(String(20))  # A, B, C, D, F based on overall quality

    notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    source = relationship("EmissionsSource")
