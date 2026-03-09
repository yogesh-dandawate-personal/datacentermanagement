"""Comprehensive tests for telemetry service"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    User,
    Meter,
    Device,
    Rack,
    Zone,
    Floor,
    Building,
    Facility,
    DeviceSpecification,
    TelemetryReading,
    TelemetryValidationError,
    TelemetryAnomaly,
)
from app.services.telemetry_service import (
    ValidationService,
    NormalizationService,
    AnomalyDetectionService,
    TelemetryService,
)


class TestValidationService:
    """Test validation logic"""

    def test_validate_reading_valid(self, db_session: Session, meter_fixture):
        """Test validation passes for valid reading"""
        meter, tenant_id, device_id = meter_fixture

        is_valid, error = ValidationService.validate_reading(
            db_session,
            str(meter.id),
            100.0,
            datetime.utcnow(),
            "kWh",
            str(tenant_id),
        )

        assert is_valid is True
        assert error is None

    def test_validate_reading_nonexistent_meter(self, db_session: Session):
        """Test validation fails for nonexistent meter"""
        fake_meter_id = "00000000-0000-0000-0000-000000000000"
        fake_tenant_id = "00000000-0000-0000-0000-000000000001"

        is_valid, error = ValidationService.validate_reading(
            db_session,
            fake_meter_id,
            100.0,
            datetime.utcnow(),
            "kWh",
            fake_tenant_id,
        )

        assert is_valid is False
        assert "not found" in error

    def test_validate_reading_invalid_type(self, db_session: Session, meter_fixture):
        """Test validation fails for non-numeric value"""
        meter, tenant_id, device_id = meter_fixture

        is_valid, error = ValidationService.validate_reading(
            db_session,
            str(meter.id),
            "invalid",
            datetime.utcnow(),
            "kWh",
            str(tenant_id),
        )

        assert is_valid is False
        assert "numeric" in error

    def test_validate_reading_future_timestamp(
        self, db_session: Session, meter_fixture
    ):
        """Test validation fails for future timestamp"""
        meter, tenant_id, device_id = meter_fixture
        future_timestamp = datetime.utcnow() + timedelta(hours=1)

        is_valid, error = ValidationService.validate_reading(
            db_session,
            str(meter.id),
            100.0,
            future_timestamp,
            "kWh",
            str(tenant_id),
        )

        assert is_valid is False
        assert "future" in error

    def test_validate_batch(self, db_session: Session, meter_fixture):
        """Test batch validation"""
        meter, tenant_id, device_id = meter_fixture

        readings = [
            {
                "meter_id": str(meter.id),
                "value": 100.0,
                "unit": "kWh",
                "timestamp": datetime.utcnow(),
            },
            {
                "meter_id": "invalid-uuid",
                "value": 200.0,
                "unit": "kWh",
                "timestamp": datetime.utcnow(),
            },
        ]

        valid, invalid = ValidationService.validate_batch(
            db_session, str(tenant_id), readings
        )

        assert len(valid) == 1
        assert len(invalid) == 1


class TestNormalizationService:
    """Test normalization logic"""

    def test_convert_unit_same(self):
        """Test converting to same unit"""
        result = NormalizationService.convert_unit(100.0, "kWh", "kWh")
        assert result == 100.0

    def test_convert_unit_wh_to_kwh(self):
        """Test converting Wh to kWh"""
        result = NormalizationService.convert_unit(1000.0, "Wh", "kWh")
        assert result == 1.0

    def test_convert_unit_mwh_to_kwh(self):
        """Test converting MWh to kWh"""
        result = NormalizationService.convert_unit(1.0, "MWh", "kWh")
        assert result == 1000.0

    def test_normalize_timestamp_naive(self):
        """Test normalizing naive timestamp"""
        ts = datetime(2026, 3, 9, 10, 30, 0)
        result = NormalizationService.normalize_timestamp(ts)
        assert result == ts

    def test_normalize_precision(self):
        """Test precision normalization"""
        result = NormalizationService.normalize_precision(100.123456789, decimals=6)
        assert isinstance(result, Decimal)
        assert float(result) == pytest.approx(100.123457)

    def test_normalize_reading(self):
        """Test complete reading normalization"""
        result = NormalizationService.normalize_reading(
            100.0, "kWh", to_unit="kWh", timestamp=datetime.utcnow()
        )

        assert "value" in result
        assert "unit" in result
        assert "timestamp" in result
        assert result["unit"] == "kWh"
        assert isinstance(result["value"], Decimal)


class TestAnomalyDetectionService:
    """Test anomaly detection logic"""

    def test_detect_stale_feed_no_readings(self, db_session: Session):
        """Test stale feed detection with no prior readings"""
        result = AnomalyDetectionService.detect_stale_feed(
            db_session, "00000000-0000-0000-0000-000000000000", datetime.utcnow()
        )

        assert result is None

    def test_detect_stale_feed_recent(
        self, db_session: Session, meter_fixture, tenant_fixture
    ):
        """Test stale feed detection with recent reading"""
        meter, tenant_id, device_id = meter_fixture

        # Add recent reading
        reading = TelemetryReading(
            tenant_id=tenant_id,
            meter_id=meter.id,
            timestamp=datetime.utcnow() - timedelta(minutes=30),
            value=Decimal("100.0"),
            unit="kWh",
            status="valid",
        )
        db_session.add(reading)
        db_session.commit()

        result = AnomalyDetectionService.detect_stale_feed(
            db_session, str(meter.id), datetime.utcnow()
        )

        assert result is None

    def test_detect_stale_feed_old(
        self, db_session: Session, meter_fixture, tenant_fixture
    ):
        """Test stale feed detection with old reading"""
        meter, tenant_id, device_id = meter_fixture

        # Add old reading
        reading = TelemetryReading(
            tenant_id=tenant_id,
            meter_id=meter.id,
            timestamp=datetime.utcnow() - timedelta(hours=2),
            value=Decimal("100.0"),
            unit="kWh",
            status="valid",
        )
        db_session.add(reading)
        db_session.commit()

        result = AnomalyDetectionService.detect_stale_feed(
            db_session, str(meter.id), datetime.utcnow()
        )

        assert result is not None
        assert result["anomaly_type"] == "stale_feed"

    def test_detect_outlier_insufficient_data(
        self, db_session: Session, meter_fixture
    ):
        """Test outlier detection with insufficient historical data"""
        meter, tenant_id, device_id = meter_fixture

        result = AnomalyDetectionService.detect_outlier(
            db_session, str(meter.id), 1000.0, datetime.utcnow()
        )

        assert result is None

    def test_detect_outlier_normal(self, db_session: Session, meter_fixture):
        """Test outlier detection for normal value"""
        meter, tenant_id, device_id = meter_fixture

        # Add historical readings
        for i in range(10):
            reading = TelemetryReading(
                tenant_id=tenant_id,
                meter_id=meter.id,
                timestamp=datetime.utcnow() - timedelta(hours=i),
                value=Decimal("100.0"),
                unit="kWh",
                status="valid",
            )
            db_session.add(reading)

        db_session.commit()

        # Test with value close to mean
        result = AnomalyDetectionService.detect_outlier(
            db_session, str(meter.id), 102.0, datetime.utcnow()
        )

        assert result is None

    def test_detect_outlier_extreme(self, db_session: Session, meter_fixture):
        """Test outlier detection for extreme value"""
        meter, tenant_id, device_id = meter_fixture

        # Add historical readings with narrow range
        for i in range(10):
            reading = TelemetryReading(
                tenant_id=tenant_id,
                meter_id=meter.id,
                timestamp=datetime.utcnow() - timedelta(hours=i),
                value=Decimal("100.0"),
                unit="kWh",
                status="valid",
            )
            db_session.add(reading)

        db_session.commit()

        # Test with extreme outlier
        result = AnomalyDetectionService.detect_outlier(
            db_session, str(meter.id), 500.0, datetime.utcnow()
        )

        assert result is not None
        assert result["anomaly_type"] == "outlier"


class TestTelemetryService:
    """Test main telemetry service"""

    def test_ingest_reading_valid(self, db_session: Session, meter_fixture):
        """Test ingesting a valid reading"""
        meter, tenant_id, device_id = meter_fixture

        service = TelemetryService(db_session)
        result = service.ingest_reading(
            tenant_id=str(tenant_id),
            meter_id=str(meter.id),
            value=100.0,
            timestamp=datetime.utcnow(),
            unit="kWh",
        )

        assert result["status"] in ["valid", "anomaly"]
        assert result["reading_id"] is not None

        # Verify reading was stored
        reading = db_session.query(TelemetryReading).filter_by(
            meter_id=meter.id
        ).first()
        assert reading is not None
        assert float(reading.value) == 100.0

    def test_ingest_reading_invalid(self, db_session: Session):
        """Test ingesting invalid reading"""
        fake_meter_id = "00000000-0000-0000-0000-000000000000"
        fake_tenant_id = "00000000-0000-0000-0000-000000000001"

        service = TelemetryService(db_session)
        result = service.ingest_reading(
            tenant_id=fake_tenant_id,
            meter_id=fake_meter_id,
            value=100.0,
            timestamp=datetime.utcnow(),
            unit="kWh",
        )

        assert result["status"] == "error"
        assert result["reading_id"] is None

        # Verify error was recorded
        error = db_session.query(TelemetryValidationError).first()
        assert error is not None

    def test_ingest_batch(self, db_session: Session, meter_fixture):
        """Test batch ingestion"""
        meter, tenant_id, device_id = meter_fixture

        readings = [
            {
                "meter_id": str(meter.id),
                "value": 100.0,
                "unit": "kWh",
                "timestamp": datetime.utcnow(),
            },
            {
                "meter_id": str(meter.id),
                "value": 110.0,
                "unit": "kWh",
                "timestamp": datetime.utcnow() - timedelta(hours=1),
            },
            {
                "meter_id": "invalid-id",
                "value": 200.0,
                "unit": "kWh",
                "timestamp": datetime.utcnow(),
            },
        ]

        service = TelemetryService(db_session)
        result = service.ingest_batch(str(tenant_id), readings)

        assert result["total"] == 3
        assert result["valid"] == 2
        assert result["invalid"] == 1
        assert result["ingested"] >= 2

    def test_get_latest_readings(self, db_session: Session, meter_fixture):
        """Test retrieving latest readings"""
        meter, tenant_id, device_id = meter_fixture

        # Add some readings
        for i in range(5):
            reading = TelemetryReading(
                tenant_id=tenant_id,
                meter_id=meter.id,
                timestamp=datetime.utcnow() - timedelta(hours=i),
                value=Decimal(str(100.0 + i)),
                unit="kWh",
                status="valid",
            )
            db_session.add(reading)

        db_session.commit()

        service = TelemetryService(db_session)
        readings = service.get_latest_readings(str(tenant_id), [str(meter.id)], limit=3)

        assert len(readings) == 3
        assert all("reading_id" in r for r in readings)
        assert all("value" in r for r in readings)

    def test_get_history(self, db_session: Session, meter_fixture):
        """Test retrieving historical readings"""
        meter, tenant_id, device_id = meter_fixture

        # Add readings over time period
        now = datetime.utcnow()
        for i in range(24):
            reading = TelemetryReading(
                tenant_id=tenant_id,
                meter_id=meter.id,
                timestamp=now - timedelta(hours=i),
                value=Decimal(str(100.0 + i)),
                unit="kWh",
                status="valid",
            )
            db_session.add(reading)

        db_session.commit()

        service = TelemetryService(db_session)
        start = now - timedelta(hours=12)
        end = now

        readings = service.get_history(
            tenant_id=str(tenant_id),
            meter_id=str(meter.id),
            start=start,
            end=end,
        )

        assert len(readings) > 0
        assert all("timestamp" in r for r in readings)
        assert all("value" in r for r in readings)

    def test_get_anomalies(self, db_session: Session, meter_fixture):
        """Test retrieving detected anomalies"""
        meter, tenant_id, device_id = meter_fixture

        # Add anomaly
        anomaly = TelemetryAnomaly(
            tenant_id=tenant_id,
            meter_id=meter.id,
            anomaly_timestamp=datetime.utcnow(),
            anomaly_type="outlier",
            actual_value=Decimal("500.0"),
            severity="high",
        )
        db_session.add(anomaly)
        db_session.commit()

        service = TelemetryService(db_session)
        anomalies = service.get_anomalies(
            tenant_id=str(tenant_id), severity="high", status="open"
        )

        assert len(anomalies) == 1
        assert anomalies[0]["type"] == "outlier"
        assert anomalies[0]["severity"] == "high"


# Pytest fixtures
@pytest.fixture
def tenant_fixture(db_session: Session):
    """Create test tenant"""
    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com",
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant


@pytest.fixture
def user_fixture(db_session: Session, tenant_fixture):
    """Create test user"""
    user = User(
        tenant_id=tenant_fixture.id,
        email="user@example.com",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def facility_fixture(db_session: Session, tenant_fixture, user_fixture):
    """Create test facility"""
    facility = Facility(
        tenant_id=tenant_fixture.id,
        name="Test Facility",
        slug="test-facility",
        facility_type="datacenter",
        location="US-East-1",
        created_by=user_fixture.id,
    )
    db_session.add(facility)
    db_session.commit()
    return facility


@pytest.fixture
def building_fixture(db_session: Session, tenant_fixture, facility_fixture):
    """Create test building"""
    building = Building(
        facility_id=facility_fixture.id,
        tenant_id=tenant_fixture.id,
        name="Building A",
    )
    db_session.add(building)
    db_session.commit()
    return building


@pytest.fixture
def floor_fixture(db_session: Session, tenant_fixture, building_fixture):
    """Create test floor"""
    floor = Floor(
        building_id=building_fixture.id,
        tenant_id=tenant_fixture.id,
        floor_number=1,
        name="Floor 1",
    )
    db_session.add(floor)
    db_session.commit()
    return floor


@pytest.fixture
def zone_fixture(db_session: Session, tenant_fixture, floor_fixture):
    """Create test zone"""
    zone = Zone(
        floor_id=floor_fixture.id,
        tenant_id=tenant_fixture.id,
        name="Zone A",
    )
    db_session.add(zone)
    db_session.commit()
    return zone


@pytest.fixture
def rack_fixture(db_session: Session, tenant_fixture, zone_fixture):
    """Create test rack"""
    rack = Rack(
        zone_id=zone_fixture.id,
        tenant_id=tenant_fixture.id,
        name="Rack 1",
    )
    db_session.add(rack)
    db_session.commit()
    return rack


@pytest.fixture
def device_fixture(db_session: Session, tenant_fixture, rack_fixture, user_fixture):
    """Create test device"""
    device = Device(
        rack_id=rack_fixture.id,
        tenant_id=tenant_fixture.id,
        device_type="server",
        created_by=user_fixture.id,
    )
    db_session.add(device)
    db_session.commit()

    # Add specifications
    spec_min = DeviceSpecification(
        device_id=device.id,
        spec_key="min_value",
        spec_value="0",
    )
    spec_max = DeviceSpecification(
        device_id=device.id,
        spec_key="max_value",
        spec_value="1000",
    )
    db_session.add_all([spec_min, spec_max])
    db_session.commit()

    return device


@pytest.fixture
def meter_fixture(db_session: Session, tenant_fixture, device_fixture, user_fixture):
    """Create test meter"""
    meter = Meter(
        device_id=device_fixture.id,
        tenant_id=tenant_fixture.id,
        meter_type="power",
        utility_type="electricity",
        unit_of_measure="kWh",
        created_by=user_fixture.id,
    )
    db_session.add(meter)
    db_session.commit()
    return meter, tenant_fixture.id, device_fixture.id


@pytest.fixture
def db_session():
    """Create test database session"""
    from app.database import SessionLocal
    from app.models import Base

    # Create tables
    Base.metadata.create_all(bind=SessionLocal().get_bind())

    session = SessionLocal()
    yield session
    session.close()
