from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table, JSON, Integer, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import uuid

Base = declarative_base()

# Association table for user-role many-to-many
user_roles_association = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'))
)

# Association table for user-facility many-to-many
facility_users = Table(
    'facility_users',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('facility_id', UUID(as_uuid=True), ForeignKey('facilities.id', ondelete='CASCADE'))
)


class Tenant(Base):
    """Multi-tenant organization"""
    __tablename__ = 'tenants'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    organizations = relationship("Organization", back_populates="tenant", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """Platform user"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    keycloak_id = Column(String(255), unique=True)  # Keycloak user ID
    email = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    password_hash = Column(String(255), nullable=True)  # Argon2 hashed password (nullable for legacy/SSO users)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)  # Track last login timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary=user_roles_association, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    # Use association class for user-organization relationships (allows role/position tracking)
    organization_assignments = relationship("UserOrganization", back_populates="user")
    facilities = relationship("Facility", secondary=facility_users, back_populates="users")


class Role(Base):
    """Role definition"""
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)  # admin, editor, viewer
    description = Column(String(500))
    permissions = Column(JSON, default=list)  # List of permission strings
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", secondary=user_roles_association, back_populates="roles")


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(UUID(as_uuid=True))
    changes = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")


# Define Organization models inline to avoid circular imports
class Organization(Base):
    """Organization entity representing hierarchical organizational units"""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    description = Column(String(1000))

    hierarchy_level = Column(Integer, nullable=False, default=0, index=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)

    org_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="organizations")
    parent = relationship("Organization", remote_side=[id], backref="children")
    user_assignments = relationship("UserOrganization", back_populates="organization")


class Department(Base):
    """Department entity for organizing sub-units within organizations"""
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000))

    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    budget = Column(String(20))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    manager = relationship("User")


class Position(Base):
    """Position entity for defining roles within organizations"""
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000))
    level = Column(Integer)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")


class UserOrganization(Base):
    """Association table for users assigned to organizations with roles"""
    __tablename__ = "user_organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="organization_assignments")
    organization = relationship("Organization", back_populates="user_assignments")
    position = relationship("Position")
    role = relationship("Role")


# Define Facility models inline to avoid circular imports
class Facility(Base):
    """Facility entity representing physical locations"""
    __tablename__ = "facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    facility_type = Column(String(100), nullable=False)
    location = Column(String(255))
    timezone = Column(String(50), default="UTC")

    total_capacity = Column(Numeric(12, 2))
    available_capacity = Column(Numeric(12, 2))

    is_active = Column(Boolean, default=True, index=True)
    facility_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="facilities")
    organization = relationship("Organization")
    buildings = relationship("Building", back_populates="facility", cascade="all, delete-orphan")
    users = relationship("User", secondary=facility_users, back_populates="facilities")
    metrics = relationship("FacilityMetrics", back_populates="facility", cascade="all, delete-orphan")


class Building(Base):
    """Building entity within a facility"""
    __tablename__ = "buildings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    building_number = Column(String(50))
    description = Column(Text)

    total_floors = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="buildings")
    tenant = relationship("Tenant")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")


class Floor(Base):
    """Floor entity within a building"""
    __tablename__ = "floors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    floor_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    total_area = Column(Numeric(12, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("Building", back_populates="floors")
    tenant = relationship("Tenant")
    zones = relationship("Zone", back_populates="floor", cascade="all, delete-orphan")


class Zone(Base):
    """Zone entity representing sections within a floor"""
    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    floor_id = Column(UUID(as_uuid=True), ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    zone_type = Column(String(100))
    description = Column(Text)

    area = Column(Numeric(12, 2))
    temperature_setpoint = Column(Numeric(5, 2))
    humidity_setpoint = Column(Numeric(5, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    floor = relationship("Floor", back_populates="zones")
    tenant = relationship("Tenant")
    racks = relationship("Rack", back_populates="zone", cascade="all, delete-orphan")


class Rack(Base):
    """Rack entity for equipment placement"""
    __tablename__ = "racks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    rack_position = Column(String(50))
    rack_number = Column(Integer)
    description = Column(Text)

    rack_height_units = Column(Integer, default=42)
    available_units = Column(Integer, default=42)

    power_capacity = Column(Numeric(12, 2))
    cooling_capacity = Column(Numeric(12, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    zone = relationship("Zone", back_populates="racks")
    tenant = relationship("Tenant")
    devices = relationship("Device", back_populates="rack", cascade="all, delete-orphan")


class Device(Base):
    """Device entity for tracking equipment"""
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rack_id = Column(UUID(as_uuid=True), ForeignKey("racks.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    device_type = Column(String(100), nullable=False, index=True)
    serial_number = Column(String(255), unique=True)
    model = Column(String(255))
    manufacturer = Column(String(255))

    rack_u_start = Column(Integer)
    rack_u_height = Column(Integer, default=1)

    status = Column(String(50), default="active", index=True)

    installation_date = Column(DateTime)
    removal_date = Column(DateTime)

    is_active = Column(Boolean, default=True)
    device_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    rack = relationship("Rack", back_populates="devices")
    tenant = relationship("Tenant")
    specifications = relationship("DeviceSpecification", back_populates="device", cascade="all, delete-orphan")
    meters = relationship("Meter", back_populates="device", cascade="all, delete-orphan")


class DeviceSpecification(Base):
    """Device specification for storing extensible attributes"""
    __tablename__ = "device_specifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)

    spec_key = Column(String(255), nullable=False)
    spec_value = Column(Text, nullable=False)
    unit = Column(String(50))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    device = relationship("Device", back_populates="specifications")


class Meter(Base):
    """Meter entity for measuring energy/utilities"""
    __tablename__ = "meters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    meter_type = Column(String(100), nullable=False)
    utility_type = Column(String(100))
    unit_of_measure = Column(String(50))

    accuracy_percent = Column(Numeric(5, 2))
    last_reading = Column(DateTime)
    last_reading_value = Column(Numeric(12, 4))

    status = Column(String(50), default="active", index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="meters")
    tenant = relationship("Tenant")


class FacilityMetrics(Base):
    """Facility metrics for tracking performance"""
    __tablename__ = "facility_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    metric_type = Column(String(100), nullable=False)
    metric_value = Column(Numeric(12, 4), nullable=False)
    unit = Column(String(50))

    measurement_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="metrics")
    tenant = relationship("Tenant")


# Telemetry models for Sprint 4
class TelemetryReading(Base):
    """High-volume telemetry readings with time-series storage"""
    __tablename__ = "telemetry_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    meter_id = Column(UUID(as_uuid=True), ForeignKey("meters.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Numeric(18, 6), nullable=False)
    unit = Column(String(20))

    status = Column(String(50), default="valid", index=True)  # valid, invalid, anomaly, stale

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    meter = relationship("Meter")


class TelemetryValidationError(Base):
    """Records validation errors from ingestion"""
    __tablename__ = "telemetry_validation_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    meter_id = Column(UUID(as_uuid=True), ForeignKey("meters.id", ondelete="SET NULL"), nullable=True, index=True)

    error_type = Column(String(100), nullable=False)  # validation_error, type_error, range_error, etc.
    error_message = Column(Text)
    source_data = Column(JSON)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    meter = relationship("Meter")


class TelemetryAnomaly(Base):
    """Detected anomalies in telemetry data"""
    __tablename__ = "telemetry_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    meter_id = Column(UUID(as_uuid=True), ForeignKey("meters.id", ondelete="CASCADE"), nullable=False, index=True)

    anomaly_timestamp = Column(DateTime, nullable=False, index=True)
    anomaly_type = Column(String(100), nullable=False)  # stale_feed, outlier, spike, etc.

    expected_value = Column(Numeric(18, 6))
    actual_value = Column(Numeric(18, 6), nullable=False)

    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved

    resolution_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    meter = relationship("Meter")


# Carbon Accounting models for Sprint 6
class EmissionFactor(Base):
    """Emission factors for carbon calculation (versioned)"""
    __tablename__ = "emission_factors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    factor_name = Column(String(255), nullable=False, index=True)
    factor_type = Column(String(50), nullable=False, index=True)  # scope1, scope2, fuel, electricity, refrigerant

    value = Column(Numeric(12, 6), nullable=False)  # kg CO2e per unit
    unit = Column(String(50), nullable=False)  # kWh, gallon, kg, etc.
    unit_measurement = Column(String(50))  # metric: kg CO2e per [unit_measurement]

    region = Column(String(100), index=True)  # US-East, Europe, Global, etc.
    data_source = Column(String(255))  # EPA, IVA, regional grid operator, etc.

    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    obsolete_date = Column(DateTime, nullable=True, index=True)  # When this factor is no longer valid

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = relationship("FactorVersion", back_populates="factor", cascade="all, delete-orphan")


class FactorVersion(Base):
    """Version history for emission factors"""
    __tablename__ = "factor_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factor_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="CASCADE"), nullable=False, index=True)

    version_number = Column(Integer, nullable=False)
    value = Column(Numeric(12, 6), nullable=False)

    changelog = Column(Text)  # What changed in this version
    effective_date = Column(DateTime, nullable=False, index=True)

    status = Column(String(50), default="active", index=True)  # active, superseded, withdrawn

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    factor = relationship("EmissionFactor", back_populates="versions")


class CarbonCalculation(Base):
    """Carbon emissions calculation record"""
    __tablename__ = "carbon_calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)

    scope_1_emissions = Column(Numeric(18, 6), default=0)  # kg CO2e
    scope_2_emissions = Column(Numeric(18, 6), default=0)  # kg CO2e
    scope_3_emissions = Column(Numeric(18, 6), default=0)  # kg CO2e (placeholder)

    total_emissions = Column(Numeric(18, 6), default=0)  # Sum of scopes, kg CO2e

    status = Column(String(50), default="draft", index=True)  # draft, ready_for_review, approved, rejected

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    approval_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    details = relationship("CalculationDetail", back_populates="calculation", cascade="all, delete-orphan")


class CalculationDetail(Base):
    """Individual calculation line items with audit trail"""
    __tablename__ = "calculation_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(UUID(as_uuid=True), ForeignKey("carbon_calculations.id", ondelete="CASCADE"), nullable=False, index=True)

    calculation_type = Column(String(50), nullable=False, index=True)  # scope1_fuel, scope2_electricity, etc.
    scope = Column(String(50), nullable=False)  # scope1, scope2, scope3

    energy_input = Column(Numeric(12, 6), nullable=False)  # Amount consumed (kWh, gallons, etc.)
    energy_unit = Column(String(50))  # kWh, gallon, kg, etc.

    factor_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    factor_version = Column(Integer)  # Version of factor used for audit trail
    factor_value = Column(Numeric(12, 6))  # Factor value at time of calculation (for audit)

    result = Column(Numeric(18, 6), nullable=False)  # Final emission result (kg CO2e)

    notes = Column(Text)  # Additional context about this calculation

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    calculation = relationship("CarbonCalculation", back_populates="details")
    factor = relationship("EmissionFactor")


# KPI models for Sprint 7
class KPIDefinition(Base):
    """KPI definitions with formulas and targets"""
    __tablename__ = "kpi_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    kpi_name = Column(String(100), nullable=False, index=True)  # PUE, CUE, WUE, ERE, or custom
    kpi_type = Column(String(50), nullable=False)  # standard, custom
    formula = Column(Text, nullable=False)  # Human-readable formula description
    formula_code = Column(Text)  # Python/SQL code for calculation
    unit = Column(String(50), nullable=False)  # %, L/kWh, g CO2/kWh, etc.

    target_value = Column(Numeric(12, 6))  # Target value for this KPI
    lower_bound = Column(Numeric(12, 6))  # Good range lower bound
    upper_bound = Column(Numeric(12, 6))  # Good range upper bound

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    snapshots = relationship("KPISnapshot", back_populates="kpi", cascade="all, delete-orphan")
    thresholds = relationship("KPIThreshold", back_populates="kpi", cascade="all, delete-orphan")


class KPISnapshot(Base):
    """Time-series KPI data points"""
    __tablename__ = "kpi_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    snapshot_date = Column(DateTime, nullable=False, index=True)
    calculated_value = Column(Numeric(18, 6), nullable=False)
    target_value = Column(Numeric(18, 6))

    variance_percent = Column(Numeric(8, 2))  # Deviation from target
    status = Column(String(50), default="normal", index=True)  # normal, warning, critical

    calculation_details = Column(JSON)  # Intermediate values used in calculation
    data_quality_score = Column(Numeric(5, 2))  # 0-100, how complete the data was

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    kpi = relationship("KPIDefinition", back_populates="snapshots")
    tenant = relationship("Tenant")


class KPIThreshold(Base):
    """Alerting thresholds for KPIs"""
    __tablename__ = "kpi_thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)

    threshold_name = Column(String(100), nullable=False)
    threshold_value = Column(Numeric(12, 6), nullable=False)
    operator = Column(String(10), nullable=False, index=True)  # >, <, >=, <=, ==, !=

    alert_severity = Column(String(20), nullable=False)  # info, warning, critical
    is_enabled = Column(Boolean, default=True, index=True)

    # Notification settings
    notify_email = Column(Boolean, default=True)
    notify_slack = Column(Boolean, default=False)
    notify_webhook = Column(String(500))  # Optional webhook URL

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    kpi = relationship("KPIDefinition", back_populates="thresholds")


class KPIThresholdBreach(Base):
    """Records when a threshold is breached"""
    __tablename__ = "kpi_threshold_breaches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    threshold_id = Column(UUID(as_uuid=True), ForeignKey("kpi_thresholds.id", ondelete="CASCADE"), nullable=False, index=True)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpi_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("kpi_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)

    breach_value = Column(Numeric(18, 6), nullable=False)
    expected_value = Column(Numeric(18, 6))

    severity = Column(String(20), nullable=False, index=True)  # info, warning, critical
    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved

    resolution_notes = Column(Text)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    threshold = relationship("KPIThreshold")
    kpi = relationship("KPIDefinition")
    snapshot = relationship("KPISnapshot")


# Marketplace models for Sprint 8
class CarbonCredit(Base):
    """Carbon credits generated from emissions reductions"""
    __tablename__ = "carbon_credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("credit_batches.id", ondelete="SET NULL"), nullable=True, index=True)

    credit_type = Column(String(50), nullable=False)  # verified, unverified, retirement
    vintage_year = Column(Integer, nullable=False, index=True)  # Year credit was generated

    quantity = Column(Numeric(18, 6), nullable=False)  # Number of credits (metric tons CO2e)
    unit = Column(String(50), default="metric_tons_co2e")

    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expiration_date = Column(DateTime, nullable=True, index=True)

    status = Column(String(50), default="active", index=True)  # active, traded, retired, expired
    source_calculation_id = Column(UUID(as_uuid=True), ForeignKey("carbon_calculations.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    source_calculation = relationship("CarbonCalculation")
    batch = relationship("CreditBatch", back_populates="credits")


class CreditBatch(Base):
    """Batch of carbon credits ready for trading"""
    __tablename__ = "credit_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    batch_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    total_credits = Column(Numeric(18, 6), nullable=False)  # Sum of credits in batch
    quality_score = Column(Numeric(5, 2), default=Decimal("100"))  # 0-100 based on data quality

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    credits = relationship("CarbonCredit", back_populates="batch")
    listings = relationship("MarketplaceListing", back_populates="batch", cascade="all, delete-orphan")


class MarketplaceListing(Base):
    """Listing of carbon credits on marketplace"""
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("credit_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    quantity_available = Column(Numeric(18, 6), nullable=False)
    price_per_credit = Column(Numeric(12, 2), nullable=False)  # USD

    listing_type = Column(String(50), nullable=False)  # fixed_price, auction, negotiable
    status = Column(String(50), default="active", index=True)  # active, sold, cancelled

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)

    minimum_bid = Column(Numeric(12, 2))  # For auction listings

    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seller = relationship("Organization", foreign_keys=[seller_id])
    batch = relationship("CreditBatch", back_populates="listings")
    tenant = relationship("Tenant")
    trades = relationship("Trade", back_populates="listing", cascade="all, delete-orphan")


class Trade(Base):
    """Carbon credit trade transaction"""
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    quantity = Column(Numeric(18, 6), nullable=False)
    price_per_credit = Column(Numeric(12, 2), nullable=False)  # Final price agreed
    total_price = Column(Numeric(18, 2), nullable=False)  # quantity * price_per_credit

    status = Column(String(50), default="pending", index=True)  # pending, completed, cancelled
    payment_status = Column(String(50), default="pending", index=True)  # pending, completed, failed

    trade_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completion_date = Column(DateTime, nullable=True)

    trade_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    listing = relationship("MarketplaceListing", back_populates="trades")
    buyer = relationship("Organization", foreign_keys=[buyer_id])
    seller_org = relationship("Organization", foreign_keys=[seller_id])
    tenant = relationship("Tenant")


class CreditRetirement(Base):
    """Record of carbon credits being retired (used)"""
    __tablename__ = "credit_retirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    retired_credits = Column(Numeric(18, 6), nullable=False)  # Quantity retired
    retirement_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    retirement_reason = Column(String(500))  # Compliance requirement, offset project, etc.

    registry_reference = Column(String(255))  # Reference to external registry if applicable
    audit_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")


class MarketplaceAnalytics(Base):
    """Analytics and pricing data for marketplace"""
    __tablename__ = "marketplace_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    metric_date = Column(DateTime, nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # avg_price, volume, trades_count, etc.

    metric_value = Column(Numeric(18, 6), nullable=False)

    # Store trending data as JSON for price history, volume trends, etc.
    trend_data = Column(JSON, default=dict)  # Historical values for charting

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


# ============================================================================
# SPRINT 9: REPORTING & COMPLIANCE MODELS
# ============================================================================

class ComplianceReport(Base):
    """Regulatory compliance report (GHG Protocol, TCFD, SEC)"""
    __tablename__ = "compliance_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    report_type = Column(String(50), nullable=False, index=True)  # ghg_protocol, tcfd, sec_climate, custom
    reporting_period = Column(String(50), nullable=False)  # Q1, Q2, Q3, Q4, annual
    fiscal_year = Column(Integer, nullable=False, index=True)

    status = Column(String(50), default="draft", index=True)  # draft, pending_review, approved, submitted, published

    scope_1_emissions = Column(Numeric(18, 6))  # Metric tonnes CO2e
    scope_2_emissions = Column(Numeric(18, 6))  # Metric tonnes CO2e
    scope_3_emissions = Column(Numeric(18, 6))  # Metric tonnes CO2e
    carbon_offset_credits_used = Column(Numeric(18, 6), default=0)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")


class ReportSection(Base):
    """Individual sections within a compliance report"""
    __tablename__ = "report_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("compliance_reports.id", ondelete="CASCADE"), nullable=False, index=True)

    section_name = Column(String(255), nullable=False)  # executive_summary, methodology, results, targets, etc.
    content = Column(JSON, default=dict)  # Formatted content with text, tables, etc.
    completion_percentage = Column(Integer, default=0)  # 0-100

    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("ComplianceReport", back_populates="sections")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class ComplianceAuditTrail(Base):
    """Detailed audit trail of all compliance-related changes"""
    __tablename__ = "compliance_audit_trails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, RETIRE, TRADE, APPROVE, SUBMIT
    action_category = Column(String(50), nullable=False, index=True)  # report, credit, target, etc.
    entity_type = Column(String(100), nullable=False, index=True)  # carbon_calculation, credit_batch, report, etc.
    entity_id = Column(UUID(as_uuid=True), index=True)

    changed_values = Column(JSON, default=dict)  # Before/after values

    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    changed_by_user = relationship("User", foreign_keys=[changed_by_user_id])


class ComplianceTarget(Base):
    """Emissions reduction targets and goals"""
    __tablename__ = "compliance_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    target_name = Column(String(255), nullable=False, index=True)  # science-based target, net-zero 2030, etc.
    target_type = Column(String(50), nullable=False)  # absolute_reduction, intensity_reduction, net_zero
    description = Column(Text)

    baseline_year = Column(Integer, nullable=False)
    baseline_value = Column(Numeric(18, 6), nullable=False)  # Metric tonnes CO2e

    target_year = Column(Integer, nullable=False, index=True)
    target_value = Column(Numeric(18, 6), nullable=False)  # Metric tonnes CO2e

    status = Column(String(50), default="on_track", index=True)  # on_track, at_risk, failed
    progress_percentage = Column(Integer, default=0)  # 0-100

    verification_status = Column(String(50))  # unverified, verified, approved
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    verifier = relationship("User", foreign_keys=[verified_by])


class ReportingBenchmark(Base):
    """Industry and regional benchmarks for comparison"""
    __tablename__ = "reporting_benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    benchmark_name = Column(String(255), nullable=False, index=True)  # industry_average, regional_average, best_in_class
    metric_name = Column(String(100), nullable=False, index=True)  # pue, cue, wue, ere, carbon_intensity
    benchmark_category = Column(String(100), nullable=False)  # data_center, facility, organization, etc.

    benchmark_value = Column(Numeric(18, 6), nullable=False)
    benchmark_unit = Column(String(50))  # percentage, ratio, g/kWh, etc.

    organization_percentile_rank = Column(Integer)  # 0-100, where organization ranks
    organization_value = Column(Numeric(18, 6))  # Current organization value for comparison

    industry = Column(String(100))  # Optional: specific industry segment
    region = Column(String(100))  # Optional: geographic region
    data_year = Column(Integer)

    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


# ============================================================================
# SPRINT 10: WORKFLOW & APPROVAL SYSTEM MODELS
# ============================================================================

class WorkflowState(Base):
    """Workflow state tracking for approval entities"""
    __tablename__ = "workflow_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)  # report, credit_batch, target, etc.

    current_state = Column(String(50), nullable=False, index=True)  # draft, review, approved, archived
    previous_state = Column(String(50))

    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_reason = Column(Text)

    state_changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    changed_by_user = relationship("User", foreign_keys=[changed_by])


class Approval(Base):
    """Individual approval step in workflow"""
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)

    approval_stage = Column(String(50), nullable=False)  # maker, checker, reviewer
    required_role = Column(String(100), nullable=False)  # admin, reviewer, approver, etc.

    status = Column(String(50), default="pending", index=True)  # pending, approved, rejected, commented
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    due_date = Column(DateTime, nullable=True, index=True)
    completed_date = Column(DateTime, nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    decision = Column(String(50))  # approve, reject, request_changes
    comment_summary = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_user = relationship("User", foreign_keys=[assigned_to], backref="approvals_assigned")
    completed_by_user = relationship("User", foreign_keys=[completed_by], backref="approvals_completed")
    comments = relationship("ApprovalComment", back_populates="approval", cascade="all, delete-orphan")


class ApprovalComment(Base):
    """Comments on approvals for discussion threads"""
    __tablename__ = "approval_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_id = Column(UUID(as_uuid=True), ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False, index=True)

    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(50), default="comment")  # comment, request_changes, approve, reject

    commented_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    approval = relationship("Approval", back_populates="comments")
    commented_by_user = relationship("User", foreign_keys=[commented_by])


class WorkflowConfig(Base):
    """Workflow configuration templates"""
    __tablename__ = "workflow_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    config_name = Column(String(255), nullable=False)  # for_reports, for_credits, for_targets
    entity_type = Column(String(100), nullable=False)  # report, credit_batch, target

    stages = Column(JSON, default=list)  # [{stage: "maker", role: "editor", required: true}, ...]
    auto_escalate_days = Column(Integer, default=7)
    require_all_approvals = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


# ============================================================================
# SPRINT 11: REPORTING ENGINE MODELS
# ============================================================================

class Report(Base):
    """ESG Reports with versioning and exports"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    report_type = Column(String(50), nullable=False, index=True)  # esg_monthly, emissions_summary, kpi_summary
    report_period_start = Column(DateTime, nullable=False, index=True)
    report_period_end = Column(DateTime, nullable=False)

    current_state = Column(String(50), default="draft", index=True)  # draft, approved, published, archived

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization")
    tenant_obj = relationship("Tenant")
    creator_user = relationship("User", foreign_keys=[created_by])
    updater_user = relationship("User", foreign_keys=[updated_by])
    publisher_user = relationship("User", foreign_keys=[published_by])
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")


class ReportVersion(Base):
    """Versioned snapshots of reports"""
    __tablename__ = "report_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)

    version_number = Column(Integer, nullable=False)
    s3_key_pdf = Column(String(500))
    s3_key_json = Column(String(500))

    version_state = Column(String(50))  # draft, approved, published
    version_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    versioned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    version_reason = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    report = relationship("Report", back_populates="versions")
    versioned_by_user = relationship("User", foreign_keys=[versioned_by])


class ReportSignature(Base):
    """Approval signatures on reports"""
    __tablename__ = "report_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)

    signer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    signer_role = Column(String(100))  # preparer, reviewer, approver

    signed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    signature_method = Column(String(50))  # digital, manual, auto
    signature_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    report = relationship("Report")
    signer_user = relationship("User", foreign_keys=[signer_id])


class ReportTemplate(Base):
    """Customizable report templates"""
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    template_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # esg_monthly, emissions_summary, kpi_summary

    template_config = Column(JSON, default=dict)  # {sections: [], formats: [], etc.}
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant_obj = relationship("Tenant")
    creator_user = relationship("User", foreign_keys=[created_by])


# ============================================================================
# SPRINT 12: INTEGRATIONS & API GATEWAY MODELS
# ============================================================================

class APIIntegration(Base):
    """Third-party API integrations"""
    __tablename__ = "api_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    integration_type = Column(String(100), nullable=False)  # salesforce, sap, snowflake, etc.
    api_key = Column(String(500))
    api_secret = Column(String(500))
    api_endpoint = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_relation = relationship("Tenant")


class APILog(Base):
    """Logging for API calls"""
    __tablename__ = "api_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("api_integrations.id", ondelete="SET NULL"))
    method = Column(String(10))
    endpoint = Column(String(500))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    tenant_relation = relationship("Tenant")


# ============================================================================
# SPRINT 13: MOBILE APP MODELS
# ============================================================================

class MobileSession(Base):
    """Mobile app sessions"""
    __tablename__ = "mobile_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(255), nullable=False)
    device_type = Column(String(50))  # iOS, Android
    app_version = Column(String(50))
    session_token = Column(String(500), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_rel = relationship("User")


class MobileNotification(Base):
    """Push notifications for mobile"""
    __tablename__ = "mobile_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    user_rel = relationship("User")


# ============================================================================
# SPRINT 14: PERFORMANCE OPTIMIZATION MODELS
# ============================================================================

class CacheEntry(Base):
    """Cache management for performance"""
    __tablename__ = "cache_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), unique=True, nullable=False)
    cache_value = Column(JSON)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PerformanceMetric(Base):
    """System performance metrics"""
    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Numeric(18, 6))
    metric_unit = Column(String(50))
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    tenant_relation = relationship("Tenant")


# ============================================================================
# SPRINT 15: PRODUCTION HARDENING MODELS
# ============================================================================

class SystemConfig(Base):
    """System configuration and feature flags"""
    __tablename__ = "system_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(String(1000))
    is_feature_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class BackupLog(Base):
    """Database backup logging"""
    __tablename__ = "backup_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    backup_type = Column(String(50))  # full, incremental, snapshot
    backup_location = Column(String(500))
    file_size_mb = Column(Integer)
    backup_status = Column(String(50))  # success, failed, in_progress
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    tenant_relation = relationship("Tenant")


class SecurityLog(Base):
    """Security and compliance logging"""
    __tablename__ = "security_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100))  # login, logout, permission_change, failed_auth
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    ip_address = Column(String(45))
    severity = Column(String(20))  # low, medium, high, critical
    event_details = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    tenant_relation = relationship("Tenant")
    user_relation = relationship("User")


# ============================================================================
# SPRINT 12: EVIDENCE REPOSITORY MODELS
# ============================================================================

class Evidence(Base):
    """Evidence documents for compliance and auditing"""
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # policy, audit, certification, report, etc.
    description = Column(Text)

    document_key = Column(String(500), nullable=False)  # S3/MinIO object key
    file_hash = Column(String(64), nullable=False)  # SHA256 hash for integrity verification
    file_size_bytes = Column(Integer)  # Size of the file in bytes
    file_type = Column(String(50))  # pdf, xlsx, png, jpg, csv, etc.

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Soft delete support
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("EvidenceVersion", back_populates="evidence", cascade="all, delete-orphan")
    links = relationship("EvidenceLink", back_populates="evidence", cascade="all, delete-orphan")


class EvidenceVersion(Base):
    """Version history for evidence documents"""
    __tablename__ = "evidence_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    version_number = Column(Integer, nullable=False)
    document_key = Column(String(500), nullable=False)  # S3/MinIO object key for this version
    file_hash = Column(String(64), nullable=False)  # SHA256 hash for this version
    file_size_bytes = Column(Integer)

    change_reason = Column(String(255))  # Why this version was created

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="versions")
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


class EvidenceLink(Base):
    """Links evidence documents to metrics, reports, or other entities"""
    __tablename__ = "evidence_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    linked_to_type = Column(String(50), nullable=False, index=True)  # metric, report, calculation, kpi, etc.
    linked_to_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # ID of the linked entity

    link_type = Column(String(50), default="supports")  # supports, references, validates, etc.

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="links")
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


# ============================================================================
# Import Copilot and Agent models from separate modules
# ============================================================================
try:
    from .copilot import (
        CopilotQuery,
        CopilotResponse,
        CopilotCitation,
        CopilotMessageHistory,
        CopilotFeedback,
        CopilotAccessLog,
        CopilotRateLimit,
    )
except ImportError:
    pass  # Models will be loaded by Alembic


try:
    from .agent import (
        AgentRun,
        AgentDecision,
        AgentGuardrailViolation,
    )
except ImportError:
    pass  # Models will be loaded by Alembic


# ============================================================================
# SPRINT 9: ADVANCED ANALYTICS & REPORTING MODELS
# ============================================================================
try:
    from .analytics import (
        EmissionsTrend,
        EnergyAnalysis,
        WaterUsage,
        WasteMetrics,
        SustainabilityScore,
        OptimizationOpportunity,
    )
except ImportError:
    pass

try:
    from .reporting_advanced import (
        ScheduledReport,
        ReportTemplateAdvanced,
        ReportDistribution,
        ReportDeliveryLog,
        ReportGenerationHistory,
    )
except ImportError:
    pass

try:
    from .benchmarking import (
        Benchmark,
        ComparisonResult,
        BenchmarkGap,
        PeerGroup,
        BenchmarkAlert,
    )
except ImportError:
    pass

try:
    from .notifications import (
        Notification,
        NotificationPreference,
        NotificationLog,
        NotificationChannel,
        NotificationTemplate,
    )
except ImportError:
    pass
