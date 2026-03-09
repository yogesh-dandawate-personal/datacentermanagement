"""Facility and asset management models"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# This module is imported after models/__init__.py, so Base should be available
# We use a delayed import to avoid circular dependency issues
def _get_base():
    from app.models import Base
    return Base


class Facility(Base):
    """Facility entity representing physical locations"""

    __tablename__ = "facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    facility_type = Column(String(100), nullable=False)  # data_center, office, warehouse, etc.
    location = Column(String(255))  # Address or location
    timezone = Column(String(50), default="UTC")

    total_capacity = Column(Numeric(12, 2))  # Total energy/power capacity
    available_capacity = Column(Numeric(12, 2))  # Available capacity

    is_active = Column(Boolean, default=True, index=True)
    facility_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="facilities")
    organization = relationship("Organization")
    buildings = relationship("Building", back_populates="facility", cascade="all, delete-orphan")
    users = relationship("User", secondary="facility_users", back_populates="facilities")
    metrics = relationship("FacilityMetrics", back_populates="facility", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Facility {self.name}>"

    def to_dict(self, include_buildings=False):
        """Convert facility to dictionary"""
        data = {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "slug": self.slug,
            "facility_type": self.facility_type,
            "location": self.location,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

        if include_buildings:
            data["buildings"] = [b.to_dict() for b in self.buildings]

        return data


class Building(Base):
    """Building entity within a facility"""

    __tablename__ = "buildings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    building_number = Column(String(50))  # Building A, Building B, etc.
    description = Column(Text)

    total_floors = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="buildings")
    tenant = relationship("Tenant")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Building {self.name}>"

    def to_dict(self, include_floors=False):
        """Convert building to dictionary"""
        data = {
            "id": str(self.id),
            "facility_id": str(self.facility_id),
            "name": self.name,
            "building_number": self.building_number,
            "total_floors": self.total_floors,
        }

        if include_floors:
            data["floors"] = [f.to_dict() for f in self.floors]

        return data


class Floor(Base):
    """Floor entity within a building"""

    __tablename__ = "floors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    floor_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    total_area = Column(Numeric(12, 2))  # Square meters or feet

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("Building", back_populates="floors")
    tenant = relationship("Tenant")
    zones = relationship("Zone", back_populates="floor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Floor {self.name}>"

    def to_dict(self, include_zones=False):
        """Convert floor to dictionary"""
        data = {
            "id": str(self.id),
            "building_id": str(self.building_id),
            "floor_number": self.floor_number,
            "name": self.name,
            "total_area": float(self.total_area) if self.total_area else None,
        }

        if include_zones:
            data["zones"] = [z.to_dict() for z in self.zones]

        return data


class Zone(Base):
    """Zone entity representing sections within a floor"""

    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    floor_id = Column(UUID(as_uuid=True), ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    zone_type = Column(String(100))  # cold_aisle, hot_aisle, office, etc.
    description = Column(Text)

    area = Column(Numeric(12, 2))
    temperature_setpoint = Column(Numeric(5, 2))  # Celsius or Fahrenheit
    humidity_setpoint = Column(Numeric(5, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    floor = relationship("Floor", back_populates="zones")
    tenant = relationship("Tenant")
    racks = relationship("Rack", back_populates="zone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Zone {self.name}>"

    def to_dict(self, include_racks=False):
        """Convert zone to dictionary"""
        data = {
            "id": str(self.id),
            "floor_id": str(self.floor_id),
            "name": self.name,
            "zone_type": self.zone_type,
            "temperature_setpoint": float(self.temperature_setpoint) if self.temperature_setpoint else None,
        }

        if include_racks:
            data["racks"] = [r.to_dict() for r in self.racks]

        return data


class Rack(Base):
    """Rack entity for equipment placement"""

    __tablename__ = "racks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    rack_position = Column(String(50))  # A1, A2, B1, etc.
    rack_number = Column(Integer)
    description = Column(Text)

    rack_height_units = Column(Integer, default=42)  # Standard is 42U
    available_units = Column(Integer, default=42)

    power_capacity = Column(Numeric(12, 2))  # kW
    cooling_capacity = Column(Numeric(12, 2))  # kW

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    zone = relationship("Zone", back_populates="racks")
    tenant = relationship("Tenant")
    devices = relationship("Device", back_populates="rack", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rack {self.name}>"

    def to_dict(self, include_devices=False):
        """Convert rack to dictionary"""
        data = {
            "id": str(self.id),
            "zone_id": str(self.zone_id),
            "name": self.name,
            "rack_position": self.rack_position,
            "rack_height_units": self.rack_height_units,
            "available_units": self.available_units,
            "power_capacity": float(self.power_capacity) if self.power_capacity else None,
        }

        if include_devices:
            data["devices"] = [d.to_dict() for d in self.devices]

        return data


class Device(Base):
    """Device entity for tracking equipment"""

    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rack_id = Column(UUID(as_uuid=True), ForeignKey("racks.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    device_type = Column(String(100), nullable=False, index=True)  # server, switch, pdu, etc.
    serial_number = Column(String(255), unique=True)
    model = Column(String(255))
    manufacturer = Column(String(255))

    rack_u_start = Column(Integer)  # Starting U position in rack
    rack_u_height = Column(Integer, default=1)  # Height in U units

    status = Column(String(50), default="active", index=True)  # active, inactive, maintenance, retired

    installation_date = Column(DateTime)
    removal_date = Column(DateTime)

    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    rack = relationship("Rack", back_populates="devices")
    tenant = relationship("Tenant")
    specifications = relationship("DeviceSpecification", back_populates="device", cascade="all, delete-orphan")
    meters = relationship("Meter", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device {self.device_type} {self.serial_number}>"

    def to_dict(self, include_specs=False):
        """Convert device to dictionary"""
        data = {
            "id": str(self.id),
            "rack_id": str(self.rack_id),
            "device_type": self.device_type,
            "serial_number": self.serial_number,
            "model": self.model,
            "status": self.status,
        }

        if include_specs:
            data["specifications"] = [s.to_dict() for s in self.specifications]
            data["meters"] = [m.to_dict() for m in self.meters]

        return data


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

    def __repr__(self):
        return f"<DeviceSpec {self.spec_key}={self.spec_value}>"

    def to_dict(self):
        """Convert spec to dictionary"""
        return {
            "key": self.spec_key,
            "value": self.spec_value,
            "unit": self.unit,
        }


class Meter(Base):
    """Meter entity for measuring energy/utilities"""

    __tablename__ = "meters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    meter_type = Column(String(100), nullable=False)  # power, water, gas, etc.
    utility_type = Column(String(100))  # electricity, water, gas, etc.
    unit_of_measure = Column(String(50))  # kW, kWh, liters, m3, etc.

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

    def __repr__(self):
        return f"<Meter {self.meter_type} {self.unit_of_measure}>"

    def to_dict(self):
        """Convert meter to dictionary"""
        return {
            "id": str(self.id),
            "device_id": str(self.device_id),
            "meter_type": self.meter_type,
            "unit_of_measure": self.unit_of_measure,
            "last_reading": self.last_reading.isoformat() if self.last_reading else None,
        }


class FacilityMetrics(Base):
    """Facility metrics for tracking performance"""

    __tablename__ = "facility_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    metric_type = Column(String(100), nullable=False)  # power_consumption, temperature, humidity, etc.
    metric_value = Column(Numeric(12, 4), nullable=False)
    unit = Column(String(50))

    measurement_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="metrics")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<FacilityMetrics {self.metric_type}={self.metric_value}>"

    def to_dict(self):
        """Convert metric to dictionary"""
        return {
            "id": str(self.id),
            "metric_type": self.metric_type,
            "metric_value": float(self.metric_value),
            "unit": self.unit,
            "timestamp": self.measurement_timestamp.isoformat(),
        }
