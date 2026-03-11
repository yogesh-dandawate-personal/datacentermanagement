"""
Tests for Scope 3 Emissions Calculations

Tests the following:
- Supply chain emissions (with lifecycle factors)
- Business travel emissions (distance-based with RFI)
- Category-specific calculations
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.services.emissions_calculation_service import EmissionsCalculationService
from app.models import EmissionsSource, EmissionsActivityData, EmissionFactor, Tenant, Organization, Facility


@pytest.fixture
def calculation_service(db_session):
    """Create calculation service instance"""
    return EmissionsCalculationService(db_session)


@pytest.fixture
def tenant_org_facility(db_session):
    """Create test tenant, org, and facility"""
    tenant = Tenant(id=str(uuid4()), name="Test Tenant")
    org = Organization(id=str(uuid4()), tenant_id=tenant.id, name="Test Org")
    facility = Facility(
        id=str(uuid4()),
        tenant_id=tenant.id,
        organization_id=org.id,
        facility_name="Test Facility",
        facility_type="data_center"
    )
    db_session.add_all([tenant, org, facility])
    db_session.commit()
    return tenant, org, facility


@pytest.fixture
def scope3_supply_chain_source(db_session, tenant_org_facility):
    """Create Scope 3 supply chain emissions source"""
    tenant, org, facility = tenant_org_facility

    # Create emission factor for supply chain
    factor = EmissionFactor(
        id=str(uuid4()),
        tenant_id=tenant.id,
        factor_name="Supply Chain Average",
        factor_type="scope3_supply_chain",
        value=Decimal("2.5"),  # kg CO2e per unit
        source="DEFRA",
        version="2024",
        is_active=True
    )
    db_session.add(factor)
    db_session.commit()

    # Create source
    source = EmissionsSource(
        id=str(uuid4()),
        tenant_id=tenant.id,
        organization_id=org.id,
        facility_id=facility.id,
        source_name="Supplier Materials",
        source_type="purchased_goods",
        scope="scope3",
        emission_factor_id=factor.id,
        unit_of_measure="kg"
    )
    db_session.add(source)
    db_session.commit()
    return source


@pytest.fixture
def scope3_business_travel_source(db_session, tenant_org_facility):
    """Create Scope 3 business travel emissions source"""
    tenant, org, facility = tenant_org_facility

    # Create emission factor for air travel
    factor = EmissionFactor(
        id=str(uuid4()),
        tenant_id=tenant.id,
        factor_name="Air Travel Medium Haul",
        factor_type="scope3_business_travel_air",
        value=Decimal("0.195"),  # gCO2e per km
        source="DEFRA",
        version="2024",
        is_active=True
    )
    db_session.add(factor)
    db_session.commit()

    # Create source
    source = EmissionsSource(
        id=str(uuid4()),
        tenant_id=tenant.id,
        organization_id=org.id,
        facility_id=facility.id,
        source_name="Employee Air Travel",
        source_type="business_travel",
        scope="scope3",
        emission_factor_id=factor.id,
        unit_of_measure="km"
    )
    db_session.add(source)
    db_session.commit()
    return source


class TestScope3SupplyChain:
    """Test Scope 3 supply chain calculations"""

    def test_supply_chain_basic_calculation(self, calculation_service, db_session, tenant_org_facility, scope3_supply_chain_source):
        """Test basic supply chain calculation with lifecycle factors"""
        tenant, org, facility = tenant_org_facility
        source = scope3_supply_chain_source

        # Create activity data for raw materials
        activity1 = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=source.id,
            timestamp=datetime(2026, 3, 10, 14, 0),
            activity_value=Decimal("1000"),  # kg of materials
            activity_unit="kg",
            data_source="manual_entry",
            validation_status="valid",
            source_metadata={
                "supplier_id": "supplier_001",
                "supply_stage": "raw_material"  # 1.5x multiplier
            }
        )

        # Create activity data for manufacturing
        activity2 = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=source.id,
            timestamp=datetime(2026, 3, 10, 15, 0),
            activity_value=Decimal("800"),  # kg of materials
            activity_unit="kg",
            data_source="manual_entry",
            validation_status="valid",
            source_metadata={
                "supplier_id": "supplier_002",
                "supply_stage": "manufacturing"  # 1.0x multiplier
            }
        )

        db_session.add_all([activity1, activity2])
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="supply_chain"
        )

        assert result["status"] == "success"
        assert result["category"] == "supply_chain"
        # Expected: (1000 * 2.5 * 1.5) + (800 * 2.5 * 1.0) = 3750 + 2000 = 5750 kg CO2e
        assert result["total_emissions_kgco2e"] == pytest.approx(5750.0)
        assert result["suppliers_count"] == 2
        assert len(result["top_suppliers"]) == 2

    def test_supply_chain_multiple_suppliers(self, calculation_service, db_session, tenant_org_facility, scope3_supply_chain_source):
        """Test supply chain calculation with multiple suppliers and aggregation"""
        tenant, org, facility = tenant_org_facility
        source = scope3_supply_chain_source

        # Create activities for 3 suppliers
        for supplier_num in range(1, 4):
            activity = EmissionsActivityData(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                timestamp=datetime(2026, 3, 10, 14, supplier_num),
                activity_value=Decimal(str(100 * supplier_num)),  # 100, 200, 300 kg
                activity_unit="kg",
                data_source="manual_entry",
                validation_status="valid",
                source_metadata={
                    "supplier_id": f"supplier_{supplier_num:03d}",
                    "supply_stage": "manufacturing"
                }
            )
            db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="supply_chain"
        )

        assert result["suppliers_count"] == 3
        # Expected: (100 + 200 + 300) * 2.5 = 1500 kg CO2e
        assert result["total_emissions_kgco2e"] == pytest.approx(1500.0)

    def test_supply_chain_stage_multipliers(self, calculation_service, db_session, tenant_org_facility, scope3_supply_chain_source):
        """Test that lifecycle stage multipliers are applied correctly"""
        tenant, org, facility = tenant_org_facility
        source = scope3_supply_chain_source

        # Create activities for each stage
        stages = {
            "raw_material": Decimal("1.5"),
            "manufacturing": Decimal("1.0"),
            "transportation": Decimal("0.3"),
            "distribution": Decimal("0.2"),
            "retail": Decimal("0.1"),
        }

        for stage, multiplier in stages.items():
            activity = EmissionsActivityData(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                timestamp=datetime(2026, 3, 10, 14, 0),
                activity_value=Decimal("100"),
                activity_unit="kg",
                data_source="manual_entry",
                validation_status="valid",
                source_metadata={
                    "supplier_id": f"supplier_{stage}",
                    "supply_stage": stage
                }
            )
            db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="supply_chain"
        )

        # Expected: 100 * 2.5 * (1.5 + 1.0 + 0.3 + 0.2 + 0.1) = 100 * 2.5 * 3.1 = 775 kg CO2e
        expected = 100 * 2.5 * sum(multipliers.values() for multipliers in stages.values())
        assert result["total_emissions_kgco2e"] == pytest.approx(775.0)


class TestScope3BusinessTravel:
    """Test Scope 3 business travel calculations"""

    def test_air_travel_short_haul(self, calculation_service, db_session, tenant_org_facility, scope3_business_travel_source):
        """Test short haul air travel calculation"""
        tenant, org, facility = tenant_org_facility
        source = scope3_business_travel_source

        # Create short haul flight (300 km)
        activity = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=source.id,
            timestamp=datetime(2026, 3, 10, 14, 0),
            activity_value=Decimal("300"),  # 300 km
            activity_unit="km",
            data_source="manual_entry",
            validation_status="valid",
            source_metadata={
                "travel_mode": "air",
                "flight_type": "domestic"
            }
        )
        db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="business_travel"
        )

        assert result["status"] == "success"
        assert result["category"] == "business_travel"
        # Short haul: 300 km * 0.255 gCO2e/km = 76.5 gCO2e = 0.0765 kgCO2e
        # With RFI (2.7x): 0.0765 * 2.7 = 0.20655 kgCO2e
        assert result["total_emissions_kgco2e"] == pytest.approx(0.20655, rel=0.01)

    def test_rail_travel_low_emissions(self, calculation_service, db_session, tenant_org_facility, scope3_business_travel_source):
        """Test rail travel has much lower emissions than air"""
        tenant, org, facility = tenant_org_facility
        source = scope3_business_travel_source

        # Create rail journey (1000 km)
        activity = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=source.id,
            timestamp=datetime(2026, 3, 10, 14, 0),
            activity_value=Decimal("1000"),  # 1000 km
            activity_unit="km",
            data_source="manual_entry",
            validation_status="valid",
            source_metadata={
                "travel_mode": "rail"
            }
        )
        db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="business_travel"
        )

        # Rail: 1000 km * 0.041 gCO2e/km = 41 gCO2e = 0.041 kgCO2e
        assert result["total_emissions_kgco2e"] == pytest.approx(0.041, rel=0.01)

    def test_car_travel_emission_variations(self, calculation_service, db_session, tenant_org_facility, scope3_business_travel_source):
        """Test car travel with different vehicle types"""
        tenant, org, facility = tenant_org_facility
        source = scope3_business_travel_source

        # Create car trips with different vehicle types
        vehicles = {
            "petrol": (Decimal("0.192"), Decimal("100")),     # 100 km petrol car
            "diesel": (Decimal("0.171"), Decimal("100")),     # 100 km diesel car
            "hybrid": (Decimal("0.089"), Decimal("100")),     # 100 km hybrid
            "electric": (Decimal("0.050"), Decimal("100")),   # 100 km EV
        }

        for vehicle_type, (factor, distance) in vehicles.items():
            activity = EmissionsActivityData(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                timestamp=datetime(2026, 3, 10, 14, 0),
                activity_value=distance,
                activity_unit="km",
                data_source="manual_entry",
                validation_status="valid",
                source_metadata={
                    "travel_mode": "car",
                    "car_type": vehicle_type
                }
            )
            db_session.add(activity)
        db_session.commit()

        # Calculate all cars
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="business_travel"
        )

        # Total: (0.192 + 0.171 + 0.089 + 0.050) * 100 / 1000 = 0.502 kgCO2e
        expected = (Decimal("0.192") + Decimal("0.171") + Decimal("0.089") + Decimal("0.050")) * Decimal("100") / Decimal("1000")
        assert result["total_emissions_kgco2e"] == pytest.approx(float(expected), rel=0.01)

    def test_air_travel_rfi_multiplier(self, calculation_service, db_session, tenant_org_facility, scope3_business_travel_source):
        """Test radiative forcing index (RFI) multiplier for air travel"""
        tenant, org, facility = tenant_org_facility
        source = scope3_business_travel_source

        # Create long haul flight (5000 km)
        activity = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=source.id,
            timestamp=datetime(2026, 3, 10, 14, 0),
            activity_value=Decimal("5000"),  # 5000 km long haul
            activity_unit="km",
            data_source="manual_entry",
            validation_status="valid",
            source_metadata={
                "travel_mode": "air"
            }
        )
        db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="business_travel"
        )

        # Long haul: 5000 km * 0.195 gCO2e/km = 975 gCO2e = 0.975 kgCO2e
        # With RFI (2.7x): 0.975 * 2.7 = 2.6325 kgCO2e
        assert result["total_emissions_kgco2e"] == pytest.approx(2.6325, rel=0.01)
        assert "radiative forcing" in result["note"].lower()

    def test_mixed_travel_modes(self, calculation_service, db_session, tenant_org_facility, scope3_business_travel_source):
        """Test mixed travel modes in single calculation"""
        tenant, org, facility = tenant_org_facility
        source = scope3_business_travel_source

        # Create various travel activities
        activities_data = [
            (Decimal("1000"), "air", None),      # Air travel
            (Decimal("500"), "rail", None),      # Rail travel
            (Decimal("200"), "car", "petrol"),  # Car travel
        ]

        for distance, mode, vehicle_type in activities_data:
            metadata = {"travel_mode": mode}
            if vehicle_type:
                metadata["car_type"] = vehicle_type

            activity = EmissionsActivityData(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                timestamp=datetime(2026, 3, 10, 14, 0),
                activity_value=distance,
                activity_unit="km",
                data_source="manual_entry",
                validation_status="valid",
                source_metadata=metadata
            )
            db_session.add(activity)
        db_session.commit()

        # Calculate
        result = calculation_service.calculate_scope_3_emissions(
            tenant_id=tenant.id,
            source_id=source.id,
            period_start=datetime(2026, 3, 10, 0, 0),
            period_end=datetime(2026, 3, 10, 23, 59),
            scope_3_category="business_travel"
        )

        assert result["status"] == "success"
        # Check breakdown exists
        assert "air" in result["breakdown_by_mode"]
        assert "rail" in result["breakdown_by_mode"]
        assert "car" in result["breakdown_by_mode"]

