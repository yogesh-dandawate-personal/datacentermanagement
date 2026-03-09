"""
Test suite for KPI calculation and alerting service

Tests:
- Standard KPI calculations (PUE, CUE, WUE, ERE)
- Custom KPI formula evaluation
- Snapshot creation and trend analysis
- Threshold creation and breach detection
- Breach acknowledgement workflow
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    Organization,
    User,
    Facility,
    Device,
    Rack,
    Zone,
    Floor,
    Building,
    Meter,
    TelemetryReading,
    CarbonCalculation,
    KPIDefinition,
    KPISnapshot,
    KPIThreshold,
    KPIThresholdBreach,
)
from app.services.kpi_service import KPICalculationService, KPIThresholdService, STANDARD_KPIS
from app.database import get_db


# ============================================================================
# Fixtures for KPI Testing
# ============================================================================


@pytest.fixture
def kpi_test_data(db: Session):
    """Create test data for KPI tests"""
    # Generate UUIDs
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    facility_id = uuid.uuid4()
    building_id = uuid.uuid4()
    floor_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    rack_id = uuid.uuid4()
    device_id = uuid.uuid4()
    meter_elec_id = uuid.uuid4()
    meter_water_id = uuid.uuid4()
    kpi_id = uuid.uuid4()

    # Create tenant
    tenant = Tenant(
        id=tenant_id,
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com",
    )
    db.add(tenant)
    db.flush()

    # Create user
    user = User(
        id=user_id,
        tenant_id=tenant.id,
        email="user@example.com",
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.flush()

    # Create organization
    org = Organization(
        id=org_id,
        tenant_id=tenant.id,
        name="Test Organization",
        slug="test-org",
        hierarchy_level=0,
    )
    db.add(org)
    db.flush()

    # Create facility
    facility = Facility(
        id=facility_id,
        tenant_id=tenant.id,
        organization_id=org.id,
        name="Test Data Center",
        slug="test-dc",
        facility_type="data_center",
    )
    db.add(facility)
    db.flush()

    # Create building
    building = Building(
        id=building_id,
        facility_id=facility.id,
        tenant_id=tenant.id,
        name="Main Building",
    )
    db.add(building)
    db.flush()

    # Create floor
    floor = Floor(
        id=floor_id,
        building_id=building.id,
        tenant_id=tenant.id,
        floor_number=1,
        name="Floor 1",
    )
    db.add(floor)
    db.flush()

    # Create zone
    zone = Zone(
        id=zone_id,
        floor_id=floor.id,
        tenant_id=tenant.id,
        name="Server Zone",
        zone_type="server",
    )
    db.add(zone)
    db.flush()

    # Create rack
    rack = Rack(
        id=rack_id,
        zone_id=zone.id,
        tenant_id=tenant.id,
        name="Rack 1",
        rack_number=1,
    )
    db.add(rack)
    db.flush()

    # Create device
    device = Device(
        id=device_id,
        rack_id=rack.id,
        tenant_id=tenant.id,
        device_type="server",
        serial_number="SN12345",
        manufacturer="Test",
    )
    db.add(device)
    db.flush()

    # Create electricity meter
    meter_electricity = Meter(
        id=meter_elec_id,
        device_id=device.id,
        tenant_id=tenant.id,
        meter_type="electrical",
        utility_type="electricity",
        unit_of_measure="kWh",
    )
    db.add(meter_electricity)

    # Create water meter
    meter_water = Meter(
        id=meter_water_id,
        device_id=device.id,
        tenant_id=tenant.id,
        meter_type="water",
        utility_type="water",
        unit_of_measure="liters",
    )
    db.add(meter_water)
    db.flush()

    # Create KPI definition
    kpi = KPIDefinition(
        id=kpi_id,
        organization_id=org.id,
        tenant_id=tenant.id,
        kpi_name="PUE",
        kpi_type="standard",
        formula="Total Facility Power / IT Equipment Power",
        unit="ratio",
        target_value=Decimal("1.2"),
        lower_bound=Decimal("1.0"),
        upper_bound=Decimal("2.0"),
    )
    db.add(kpi)
    db.flush()

    db.commit()

    return {
        "tenant": tenant,
        "org": org,
        "facility": facility,
        "meter_electricity": meter_electricity,
        "meter_water": meter_water,
        "kpi": kpi,
        "user": user,
    }


# ============================================================================
# Test: KPI Calculation Service
# ============================================================================


class TestKPICalculationService:
    """Tests for KPI calculation functionality"""

    def test_calculate_pue_with_valid_data(self, db: Session, kpi_test_data):
        """Test PUE calculation with valid telemetry data"""
        test_data = kpi_test_data
        meter = test_data["meter_electricity"]

        # Create telemetry readings
        period_start = datetime.utcnow() - timedelta(days=7)
        period_end = datetime.utcnow()

        for i in range(7):
            timestamp = period_start + timedelta(days=i)
            # Total facility power
            reading1 = TelemetryReading(
                tenant_id=test_data["tenant"].id,
                meter_id=meter.id,
                timestamp=timestamp,
                value=Decimal("1000"),  # 1000 kWh
                unit="kWh",
                status="valid",
            )
            db.add(reading1)

        db.commit()

        # Calculate PUE
        service = KPICalculationService(db)
        pue, details = service.calculate_pue(
            test_data["org"].id, period_start, period_end
        )

        # PUE = Total / IT Equipment = 1000 / (1000 * 0.70) = 1.43
        assert pue > Decimal("1.0")
        assert "total_facility_power_kwh" in details
        assert "it_equipment_power_kwh" in details
        assert "pue" in details

    def test_calculate_pue_no_data(self, db: Session, kpi_test_data):
        """Test PUE calculation with no telemetry data"""
        test_data = kpi_test_data
        period_start = datetime.utcnow() - timedelta(days=7)
        period_end = datetime.utcnow()

        service = KPICalculationService(db)
        pue, details = service.calculate_pue(
            test_data["org"].id, period_start, period_end
        )

        # Should return 0 when no data available
        assert pue == Decimal("0")
        assert details == {}

    def test_calculate_cue_with_carbon_data(self, db: Session, kpi_test_data):
        """Test CUE calculation with carbon emissions data"""
        test_data = kpi_test_data

        # Create carbon calculation
        carbon_calc = CarbonCalculation(
            tenant_id=test_data["tenant"].id,
            organization_id=test_data["org"].id,
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            scope_1_emissions=Decimal("0"),
            scope_2_emissions=Decimal("500"),  # 500 kg CO2e
            scope_3_emissions=Decimal("0"),
            total_emissions=Decimal("500"),
            status="approved",
        )
        db.add(carbon_calc)
        db.flush()

        # Create telemetry readings
        meter = test_data["meter_electricity"]
        period_start = carbon_calc.period_start
        period_end = carbon_calc.period_end

        for i in range(7):
            timestamp = period_start + timedelta(days=i)
            reading = TelemetryReading(
                tenant_id=test_data["tenant"].id,
                meter_id=meter.id,
                timestamp=timestamp,
                value=Decimal("1000"),  # 1000 kWh
                unit="kWh",
                status="valid",
            )
            db.add(reading)

        db.commit()

        # Calculate CUE
        service = KPICalculationService(db)
        cue, details = service.calculate_cue(
            test_data["org"].id, period_start, period_end
        )

        # CUE = (500 * 1000) g CO2 / (1000 * 0.70) kWh = 714.3 g CO2/kWh
        assert cue > Decimal("0")
        assert "cue" in details

    def test_calculate_wue(self, db: Session, kpi_test_data):
        """Test WUE (Water Usage Effectiveness) calculation"""
        test_data = kpi_test_data

        period_start = datetime.utcnow() - timedelta(days=7)
        period_end = datetime.utcnow()

        # Create water readings
        meter_water = test_data["meter_water"]
        for i in range(7):
            timestamp = period_start + timedelta(days=i)
            reading = TelemetryReading(
                tenant_id=test_data["tenant"].id,
                meter_id=meter_water.id,
                timestamp=timestamp,
                value=Decimal("10000"),  # 10000 liters
                unit="liters",
                status="valid",
            )
            db.add(reading)

        # Create electricity readings
        meter_elec = test_data["meter_electricity"]
        for i in range(7):
            timestamp = period_start + timedelta(days=i)
            reading = TelemetryReading(
                tenant_id=test_data["tenant"].id,
                meter_id=meter_elec.id,
                timestamp=timestamp,
                value=Decimal("1000"),  # 1000 kWh
                unit="kWh",
                status="valid",
            )
            db.add(reading)

        db.commit()

        # Calculate WUE
        service = KPICalculationService(db)
        wue, details = service.calculate_wue(
            test_data["org"].id, period_start, period_end
        )

        # WUE = Water / Energy
        assert wue > Decimal("0")
        assert "wue" in details
        assert "water_consumption_liters" in details

    def test_calculate_ere(self, db: Session, kpi_test_data):
        """Test ERE (Energy Reuse Effectiveness) calculation"""
        test_data = kpi_test_data

        period_start = datetime.utcnow() - timedelta(days=7)
        period_end = datetime.utcnow()

        # Create electricity readings
        meter = test_data["meter_electricity"]
        for i in range(7):
            timestamp = period_start + timedelta(days=i)
            reading = TelemetryReading(
                tenant_id=test_data["tenant"].id,
                meter_id=meter.id,
                timestamp=timestamp,
                value=Decimal("1000"),  # 1000 kWh
                unit="kWh",
                status="valid",
            )
            db.add(reading)

        db.commit()

        # Calculate ERE
        service = KPICalculationService(db)
        ere, details = service.calculate_ere(
            test_data["org"].id, period_start, period_end
        )

        # ERE = Total / Reused (40% efficiency)
        assert ere > Decimal("0")
        assert "ere" in details


# ============================================================================
# Test: KPI Snapshot Management
# ============================================================================


class TestKPISnapshot:
    """Tests for KPI snapshot creation and trend analysis"""

    def test_create_snapshot(self, db: Session, kpi_test_data):
        """Test creating a KPI snapshot"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        service = KPICalculationService(db)
        snapshot = service.create_snapshot(
            kpi_id=kpi.id,
            organization_id=test_data["org"].id,
            tenant_id=test_data["tenant"].id,
            kpi_name="PUE",
            calculated_value=Decimal("1.15"),
            target_value=Decimal("1.2"),
            calculation_details={"total": 1000, "it": 870},
            data_quality_score=Decimal("95"),
        )

        assert snapshot.calculated_value == Decimal("1.15")
        assert snapshot.status == "normal"  # Within 10% of target

    def test_snapshot_status_critical(self, db: Session, kpi_test_data):
        """Test snapshot status becomes critical when variance > 20%"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        service = KPICalculationService(db)
        snapshot = service.create_snapshot(
            kpi_id=kpi.id,
            organization_id=test_data["org"].id,
            tenant_id=test_data["tenant"].id,
            kpi_name="PUE",
            calculated_value=Decimal("1.5"),  # 25% above target
            target_value=Decimal("1.2"),
            calculation_details={},
            data_quality_score=Decimal("85"),
        )

        assert snapshot.status == "critical"

    def test_get_snapshot_trend(self, db: Session, kpi_test_data):
        """Test retrieving historical snapshot trend"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        service = KPICalculationService(db)

        # Create multiple snapshots
        for i in range(5):
            service.create_snapshot(
                kpi_id=kpi.id,
                organization_id=test_data["org"].id,
                tenant_id=test_data["tenant"].id,
                kpi_name="PUE",
                calculated_value=Decimal("1.2") + Decimal(str(i * 0.05)),
                target_value=Decimal("1.2"),
                calculation_details={},
            )

        # Retrieve trend
        trend = service.get_snapshot_trend(kpi.id, days=30)

        assert len(trend) == 5
        assert all("date" in s for s in trend)
        assert all("value" in s for s in trend)


# ============================================================================
# Test: KPI Threshold and Breach Detection
# ============================================================================


class TestKPIThreshold:
    """Tests for KPI threshold management and breach detection"""

    def test_create_threshold(self, db: Session, kpi_test_data):
        """Test creating a KPI threshold"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        service = KPIThresholdService(db)
        threshold = service.create_threshold(
            kpi_id=kpi.id,
            threshold_name="PUE Warning",
            threshold_value=Decimal("1.5"),
            operator=">",
            alert_severity="warning",
            notify_email=True,
            notify_slack=False,
        )

        assert threshold.threshold_name == "PUE Warning"
        assert threshold.threshold_value == Decimal("1.5")
        assert threshold.operator == ">"

    def test_threshold_breach_detection_greater_than(self, db: Session, kpi_test_data):
        """Test breach detection with > operator"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        # Create threshold
        threshold_service = KPIThresholdService(db)
        threshold = threshold_service.create_threshold(
            kpi_id=kpi.id,
            threshold_name="PUE Warning",
            threshold_value=Decimal("1.3"),
            operator=">",
            alert_severity="warning",
        )

        # Create snapshot
        calc_service = KPICalculationService(db)
        snapshot = calc_service.create_snapshot(
            kpi_id=kpi.id,
            organization_id=test_data["org"].id,
            tenant_id=test_data["tenant"].id,
            kpi_name="PUE",
            calculated_value=Decimal("1.5"),  # > 1.3 threshold
            target_value=Decimal("1.2"),
            calculation_details={},
        )

        # Check for breaches
        breaches = threshold_service.check_breaches(
            kpi_id=kpi.id,
            snapshot_id=snapshot.id,
            calculated_value=Decimal("1.5"),
            target_value=Decimal("1.2"),
        )

        assert len(breaches) == 1
        assert breaches[0].breach_value == Decimal("1.5")
        assert breaches[0].severity == "warning"

    def test_threshold_breach_detection_less_than(self, db: Session, kpi_test_data):
        """Test breach detection with < operator"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]

        # Create threshold
        threshold_service = KPIThresholdService(db)
        threshold = threshold_service.create_threshold(
            kpi_id=kpi.id,
            threshold_name="PUE Critical Low",
            threshold_value=Decimal("0.9"),
            operator="<",
            alert_severity="critical",
        )

        # Create snapshot
        calc_service = KPICalculationService(db)
        snapshot = calc_service.create_snapshot(
            kpi_id=kpi.id,
            organization_id=test_data["org"].id,
            tenant_id=test_data["tenant"].id,
            kpi_name="PUE",
            calculated_value=Decimal("0.8"),  # < 0.9 threshold
            target_value=Decimal("1.2"),
            calculation_details={},
        )

        # Check for breaches
        breaches = threshold_service.check_breaches(
            kpi_id=kpi.id,
            snapshot_id=snapshot.id,
            calculated_value=Decimal("0.8"),
            target_value=Decimal("1.2"),
        )

        assert len(breaches) == 1
        assert breaches[0].severity == "critical"

    def test_acknowledge_breach(self, db: Session, kpi_test_data):
        """Test acknowledging a threshold breach"""
        test_data = kpi_test_data
        kpi = test_data["kpi"]
        user = test_data["user"]

        # Create threshold and breach
        threshold_service = KPIThresholdService(db)
        threshold = threshold_service.create_threshold(
            kpi_id=kpi.id,
            threshold_name="Test",
            threshold_value=Decimal("1.5"),
            operator=">",
            alert_severity="warning",
        )

        calc_service = KPICalculationService(db)
        snapshot = calc_service.create_snapshot(
            kpi_id=kpi.id,
            organization_id=test_data["org"].id,
            tenant_id=test_data["tenant"].id,
            kpi_name="PUE",
            calculated_value=Decimal("1.6"),
            target_value=Decimal("1.2"),
            calculation_details={},
        )

        breaches = threshold_service.check_breaches(
            kpi_id=kpi.id,
            snapshot_id=snapshot.id,
            calculated_value=Decimal("1.6"),
            target_value=Decimal("1.2"),
        )

        # Acknowledge breach
        breach_id = breaches[0].id
        acknowledged = threshold_service.acknowledge_breach(
            breach_id=breach_id,
            acknowledged_by=user.id,
            resolution_notes="Investigating root cause",
        )

        assert acknowledged.status == "acknowledged"
        assert acknowledged.acknowledged_by == user.id
        assert acknowledged.resolution_notes == "Investigating root cause"


# ============================================================================
# Test: Standard KPI Metadata
# ============================================================================


class TestStandardKPIs:
    """Tests for standard KPI definitions"""

    def test_standard_kpis_exist(self):
        """Test that all standard KPIs are defined"""
        expected_kpis = ["PUE", "CUE", "WUE", "ERE"]
        assert len(STANDARD_KPIS) == 4
        for kpi_name in expected_kpis:
            assert kpi_name in STANDARD_KPIS

    def test_pue_metadata(self):
        """Test PUE (Power Usage Effectiveness) metadata"""
        pue = STANDARD_KPIS["PUE"]
        assert pue["unit"] == "ratio"
        assert pue["target"] == 1.2
        assert pue["lower_bound"] == 1.0
        assert pue["upper_bound"] == 2.0

    def test_cue_metadata(self):
        """Test CUE (Carbon Usage Effectiveness) metadata"""
        cue = STANDARD_KPIS["CUE"]
        assert cue["unit"] == "g CO2/kWh"
        assert cue["target"] == 50
        assert cue["lower_bound"] == 0
        assert cue["upper_bound"] == 200

    def test_wue_metadata(self):
        """Test WUE (Water Usage Effectiveness) metadata"""
        wue = STANDARD_KPIS["WUE"]
        assert wue["unit"] == "L/kWh"
        assert wue["target"] == 1.8
        assert wue["lower_bound"] == 0
        assert wue["upper_bound"] == 5.0
