from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table, JSON, Integer, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary=user_roles_association, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    organizations = relationship("Organization", secondary="user_organizations", back_populates="users")
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
    users = relationship("User", secondary="user_organizations", back_populates="organizations")


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
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="users")
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
