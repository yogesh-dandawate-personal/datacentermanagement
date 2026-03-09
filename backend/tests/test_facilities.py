"""Tests for facility management module"""
import pytest
import uuid
from datetime import datetime
from decimal import Decimal

from app.models import Tenant, User, Facility, Building, Floor, Zone, Rack, Device
from app.database import SessionLocal


@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def tenant(db):
    """Create test tenant"""
    tenant = Tenant(
        name="Test Org",
        slug="test-org",
        email="test@example.com"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db, tenant):
    """Create admin user"""
    user = User(
        tenant_id=tenant.id,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestFacilityCreation:
    """Test facility creation"""

    def test_create_facility_success(self, db, tenant, admin_user):
        """Create facility successfully"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            location="San Francisco, CA",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()
        db.refresh(facility)

        assert facility.id is not None
        assert facility.name == "Data Center 1"
        assert facility.facility_type == "data_center"
        assert facility.is_active is True

    def test_create_facility_with_capacity(self, db, tenant, admin_user):
        """Create facility with capacity specifications"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            total_capacity=Decimal("500.00"),  # 500 kW
            available_capacity=Decimal("500.00"),
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()
        db.refresh(facility)

        assert facility.total_capacity == Decimal("500.00")
        assert facility.available_capacity == Decimal("500.00")

    def test_create_multiple_facilities(self, db, tenant, admin_user):
        """Create multiple facilities"""
        facilities = []
        for i in range(3):
            f = Facility(
                tenant_id=tenant.id,
                name=f"Data Center {i}",
                slug=f"dc-{i}",
                facility_type="data_center",
                created_by=admin_user.id
            )
            db.add(f)
            facilities.append(f)

        db.commit()
        assert len(facilities) == 3


class TestFacilityRetrieval:
    """Test facility retrieval"""

    def test_get_facility_by_id(self, db, tenant, admin_user):
        """Retrieve facility by ID"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        retrieved = db.query(Facility).filter_by(id=facility.id).first()
        assert retrieved is not None
        assert retrieved.name == "Data Center 1"

    def test_list_facilities_by_tenant(self, db, tenant, admin_user):
        """List facilities for tenant"""
        for i in range(3):
            f = Facility(
                tenant_id=tenant.id,
                name=f"Data Center {i}",
                slug=f"dc-{i}",
                facility_type="data_center",
                created_by=admin_user.id
            )
            db.add(f)

        db.commit()

        facilities = db.query(Facility).filter_by(tenant_id=tenant.id).all()
        assert len(facilities) == 3

    def test_facility_isolation_by_tenant(self, db, admin_user):
        """Ensure facilities are isolated by tenant"""
        tenant1 = Tenant(name="Tenant 1", slug="t1", email="t1@example.com")
        tenant2 = Tenant(name="Tenant 2", slug="t2", email="t2@example.com")
        db.add_all([tenant1, tenant2])
        db.commit()

        f1 = Facility(
            tenant_id=tenant1.id,
            name="Data Center 1",
            slug="dc1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        f2 = Facility(
            tenant_id=tenant2.id,
            name="Data Center 2",
            slug="dc2",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add_all([f1, f2])
        db.commit()

        tenant1_facilities = db.query(Facility).filter_by(tenant_id=tenant1.id).all()
        assert len(tenant1_facilities) == 1
        assert tenant1_facilities[0].name == "Data Center 1"


class TestFacilityHierarchy:
    """Test facility hierarchy (building -> floor -> zone -> rack)"""

    def test_create_building(self, db, tenant, admin_user):
        """Create building within facility"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A",
            building_number="A",
            total_floors=3
        )
        db.add(building)
        db.commit()
        db.refresh(building)

        assert building.id is not None
        assert building.facility_id == facility.id

    def test_create_floor(self, db, tenant, admin_user):
        """Create floor within building"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A",
            total_floors=3
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1",
            total_area=Decimal("1000.00")
        )
        db.add(floor)
        db.commit()
        db.refresh(floor)

        assert floor.floor_number == 1
        assert floor.building_id == building.id

    def test_create_zone(self, db, tenant, admin_user):
        """Create zone within floor"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A",
            zone_type="cold_aisle",
            temperature_setpoint=Decimal("18.0")
        )
        db.add(zone)
        db.commit()
        db.refresh(zone)

        assert zone.name == "Cold Aisle A"
        assert zone.temperature_setpoint == Decimal("18.0")

    def test_create_rack(self, db, tenant, admin_user):
        """Create rack within zone"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A",
            zone_type="cold_aisle"
        )
        db.add(zone)
        db.commit()

        rack = Rack(
            zone_id=zone.id,
            tenant_id=tenant.id,
            name="Rack A1",
            rack_position="A1",
            rack_height_units=42,
            power_capacity=Decimal("10.0")
        )
        db.add(rack)
        db.commit()
        db.refresh(rack)

        assert rack.name == "Rack A1"
        assert rack.available_units == 42

    def test_full_hierarchy(self, db, tenant, admin_user):
        """Create full facility hierarchy"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A"
        )
        db.add(zone)
        db.commit()

        rack = Rack(
            zone_id=zone.id,
            tenant_id=tenant.id,
            name="Rack A1"
        )
        db.add(rack)
        db.commit()

        # Verify relationships
        assert facility.buildings[0] == building
        assert building.floors[0] == floor
        assert floor.zones[0] == zone
        assert zone.racks[0] == rack


class TestDeviceManagement:
    """Test device management"""

    def test_create_device(self, db, tenant, admin_user):
        """Create device in rack"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A"
        )
        db.add(zone)
        db.commit()

        rack = Rack(
            zone_id=zone.id,
            tenant_id=tenant.id,
            name="Rack A1"
        )
        db.add(rack)
        db.commit()

        device = Device(
            rack_id=rack.id,
            tenant_id=tenant.id,
            device_type="server",
            serial_number="SRV-001",
            model="Dell PowerEdge R750",
            manufacturer="Dell",
            rack_u_start=1,
            rack_u_height=2,
            created_by=admin_user.id
        )
        db.add(device)
        db.commit()
        db.refresh(device)

        assert device.id is not None
        assert device.device_type == "server"
        assert device.serial_number == "SRV-001"

    def test_device_with_specifications(self, db, tenant, admin_user):
        """Create device with specifications"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A"
        )
        db.add(zone)
        db.commit()

        rack = Rack(
            zone_id=zone.id,
            tenant_id=tenant.id,
            name="Rack A1"
        )
        db.add(rack)
        db.commit()

        device = Device(
            rack_id=rack.id,
            tenant_id=tenant.id,
            device_type="server",
            serial_number="SRV-001",
            model="Dell PowerEdge R750",
            created_by=admin_user.id
        )
        db.add(device)
        db.commit()

        # Add specifications
        from app.models.facility import DeviceSpecification
        specs = [
            DeviceSpecification(device_id=device.id, spec_key="cpu_cores", spec_value="16", unit="cores"),
            DeviceSpecification(device_id=device.id, spec_key="memory", spec_value="256", unit="GB"),
            DeviceSpecification(device_id=device.id, spec_key="power_draw", spec_value="800", unit="W"),
        ]
        db.add_all(specs)
        db.commit()

        # Verify specifications
        device_specs = db.query(DeviceSpecification).filter_by(device_id=device.id).all()
        assert len(device_specs) == 3
        assert device_specs[0].spec_key == "cpu_cores"


class TestFacilityUpdate:
    """Test facility updates"""

    def test_update_facility_details(self, db, tenant, admin_user):
        """Update facility details"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        facility.name = "Data Center 1 - Updated"
        facility.location = "New Location"
        db.commit()

        updated = db.query(Facility).filter_by(id=facility.id).first()
        assert updated.name == "Data Center 1 - Updated"
        assert updated.location == "New Location"

    def test_update_rack_capacity(self, db, tenant, admin_user):
        """Update rack capacity"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        floor = Floor(
            building_id=building.id,
            tenant_id=tenant.id,
            floor_number=1,
            name="Floor 1"
        )
        db.add(floor)
        db.commit()

        zone = Zone(
            floor_id=floor.id,
            tenant_id=tenant.id,
            name="Cold Aisle A"
        )
        db.add(zone)
        db.commit()

        rack = Rack(
            zone_id=zone.id,
            tenant_id=tenant.id,
            name="Rack A1",
            available_units=42
        )
        db.add(rack)
        db.commit()

        rack.available_units = 38  # 4 U occupied
        db.commit()

        updated = db.query(Rack).filter_by(id=rack.id).first()
        assert updated.available_units == 38


class TestFacilityDelete:
    """Test facility deletion"""

    def test_delete_facility(self, db, tenant, admin_user):
        """Delete facility"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        facility_id = facility.id
        db.delete(facility)
        db.commit()

        deleted = db.query(Facility).filter_by(id=facility_id).first()
        assert deleted is None

    def test_delete_facility_cascades_to_buildings(self, db, tenant, admin_user):
        """Delete facility cascades to buildings"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        building = Building(
            facility_id=facility.id,
            tenant_id=tenant.id,
            name="Building A"
        )
        db.add(building)
        db.commit()

        facility_id = facility.id
        building_id = building.id

        db.delete(facility)
        db.commit()

        facility_check = db.query(Facility).filter_by(id=facility_id).first()
        building_check = db.query(Building).filter_by(id=building_id).first()

        assert facility_check is None
        assert building_check is None


class TestFacilityUserAssignment:
    """Test user assignment to facilities"""

    def test_assign_user_to_facility(self, db, tenant, admin_user):
        """Assign user to facility"""
        facility = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add(facility)
        db.commit()

        facility.users.append(admin_user)
        db.commit()

        assert admin_user in facility.users

    def test_user_can_access_multiple_facilities(self, db, tenant, admin_user):
        """User can be assigned to multiple facilities"""
        f1 = Facility(
            tenant_id=tenant.id,
            name="Data Center 1",
            slug="dc-1",
            facility_type="data_center",
            created_by=admin_user.id
        )
        f2 = Facility(
            tenant_id=tenant.id,
            name="Data Center 2",
            slug="dc-2",
            facility_type="data_center",
            created_by=admin_user.id
        )
        db.add_all([f1, f2])
        db.commit()

        admin_user.facilities.append(f1)
        admin_user.facilities.append(f2)
        db.commit()

        assert len(admin_user.facilities) == 2
