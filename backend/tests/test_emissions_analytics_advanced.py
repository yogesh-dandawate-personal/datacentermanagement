"""
Tests for Advanced Emissions Analytics

Tests:
- Trend analysis with linear regression
- Emissions forecasting with confidence intervals
- Facility comparison and benchmarking
- Anomaly detection
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.services.emissions_analytics_service import EmissionsAnalyticsService
from app.models import EmissionsCalculation, EmissionsSource, Tenant, Organization, Facility


@pytest.fixture
def analytics_service(db_session):
    """Create analytics service instance"""
    return EmissionsAnalyticsService(db_session)


@pytest.fixture
def tenant_org_facilities(db_session):
    """Create test tenant, org, and multiple facilities"""
    tenant = Tenant(id=str(uuid4()), name="Analytics Test Tenant")
    org = Organization(id=str(uuid4()), tenant_id=tenant.id, name="Analytics Test Org")

    facilities = []
    for i in range(3):
        facility = Facility(
            id=str(uuid4()),
            tenant_id=tenant.id,
            organization_id=org.id,
            facility_name=f"Test Facility {i+1}",
            facility_type="data_center"
        )
        facilities.append(facility)

    db_session.add_all([tenant, org] + facilities)
    db_session.commit()
    return tenant, org, facilities


@pytest.fixture
def emissions_source(db_session, tenant_org_facilities):
    """Create test emissions source"""
    tenant, org, facilities = tenant_org_facilities
    facility = facilities[0]

    source = EmissionsSource(
        id=str(uuid4()),
        tenant_id=tenant.id,
        organization_id=org.id,
        facility_id=facility.id,
        source_name="Test Analytics Source",
        source_type="electricity",
        scope="scope2",
        unit_of_measure="kWh"
    )
    db_session.add(source)
    db_session.commit()
    return source


class TestTrendAnalysis:
    """Test trend analysis with linear regression"""

    def test_trend_increasing(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test detection of increasing trend"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Create daily emissions data with increasing trend (100, 110, 120, 130...)
        base_date = datetime.utcnow() - timedelta(days=20)

        for day in range(20):
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str((100 + day * 10) * 1000)),  # 100-290 tCO2e
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Analyze trend
        result = analytics_service.analyze_trend(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            days=20
        )

        assert result["status"] == "success"
        assert result["trend"]["slope_direction"] == "increasing"
        assert result["trend"]["slope"] > 0
        assert result["trend"]["r_squared"] > 0.9  # High R² for linear data

    def test_trend_decreasing(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test detection of decreasing trend"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Create daily emissions with decreasing trend (290, 280, 270...)
        base_date = datetime.utcnow() - timedelta(days=20)

        for day in range(20):
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str((290 - day * 10) * 1000)),  # 290-100 tCO2e
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Analyze trend
        result = analytics_service.analyze_trend(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            days=20
        )

        assert result["status"] == "success"
        assert result["trend"]["slope_direction"] == "decreasing"
        assert result["trend"]["slope"] < 0

    def test_anomaly_detection(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test detection of anomalous emissions spikes"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Create baseline emissions (100 tCO2e/day)
        base_date = datetime.utcnow() - timedelta(days=20)

        for day in range(20):
            # Inject anomaly on day 10
            if day == 10:
                emissions = 500  # 5x spike
            else:
                emissions = 100

            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str(emissions * 1000)),
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Analyze trend
        result = analytics_service.analyze_trend(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            days=20
        )

        assert result["status"] == "success"
        assert len(result["anomalies"]) > 0  # Should detect the spike

    def test_insufficient_data(self, analytics_service, tenant_org_facilities):
        """Test handling of insufficient data"""
        tenant, org, facilities = tenant_org_facilities
        facility = facilities[0]

        # No data for facility
        result = analytics_service.analyze_trend(
            tenant_id=tenant.id,
            facility_id=facility.id,
            days=30
        )

        assert result["status"] == "insufficient_data"


class TestForecastingEngine:
    """Test emissions forecasting with confidence intervals"""

    def test_forecast_basic(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test basic forecasting functionality"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Create 90 days of increasing emissions data
        base_date = datetime.utcnow() - timedelta(days=90)

        for day in range(90):
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str((100 + day * 2) * 1000)),
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Generate forecast
        result = analytics_service.forecast_emissions(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            forecast_days=30,
            historical_days=90
        )

        assert result["status"] == "success"
        assert len(result["forecasts"]) == 30
        assert result["forecast_confidence"] > 0.5  # Should have reasonable confidence
        assert result["forecasts"][0]["forecasted_tco2e"] > 0

    def test_forecast_confidence_intervals(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test that confidence intervals are calculated correctly"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Create 60 days of stable emissions data
        base_date = datetime.utcnow() - timedelta(days=60)

        for day in range(60):
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str(150 * 1000)),  # Constant 150 tCO2e
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Generate forecast
        result = analytics_service.forecast_emissions(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            forecast_days=30
        )

        assert result["status"] == "success"
        # For stable data, upper_bound > forecasted > lower_bound
        for forecast in result["forecasts"]:
            assert forecast["lower_bound_tco2e"] <= forecast["forecasted_tco2e"]
            assert forecast["forecasted_tco2e"] <= forecast["upper_bound_tco2e"]

    def test_forecast_insufficient_history(self, analytics_service, db_session, tenant_org_facilities, emissions_source):
        """Test forecasting with minimal historical data"""
        tenant, org, facilities = tenant_org_facilities
        source = emissions_source

        # Only 3 days of data
        base_date = datetime.utcnow() - timedelta(days=3)

        for day in range(3):
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=base_date + timedelta(days=day),
                calculation_period_end=base_date + timedelta(days=day, hours=23),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str(100 * 1000)),
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Forecast should handle this gracefully
        result = analytics_service.forecast_emissions(
            tenant_id=tenant.id,
            facility_id=source.facility_id,
            forecast_days=30,
            historical_days=90  # More than we have
        )

        # Should either succeed with low confidence or return insufficient data
        assert result["status"] in ["success", "insufficient_data_for_forecast"]


class TestFacilityComparison:
    """Test comparative analytics across facilities"""

    def test_compare_two_facilities(self, analytics_service, db_session, tenant_org_facilities):
        """Test comparing emissions between two facilities"""
        tenant, org, facilities = tenant_org_facilities
        facility_1, facility_2 = facilities[0], facilities[1]

        # Create sources for each facility
        source_1 = EmissionsSource(
            id=str(uuid4()),
            tenant_id=tenant.id,
            organization_id=org.id,
            facility_id=facility_1.id,
            source_name="Facility 1 Source",
            source_type="electricity",
            scope="scope2"
        )

        source_2 = EmissionsSource(
            id=str(uuid4()),
            tenant_id=tenant.id,
            organization_id=org.id,
            facility_id=facility_2.id,
            source_name="Facility 2 Source",
            source_type="electricity",
            scope="scope2"
        )

        db_session.add_all([source_1, source_2])
        db_session.commit()

        # Create emissions data: facility 1 = 500 tCO2e, facility 2 = 300 tCO2e
        for source, emissions_amount in [(source_1, 500), (source_2, 300)]:
            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=datetime(2026, 1, 1),
                calculation_period_end=datetime(2026, 12, 31),
                scope="scope2",
                total_emissions_kgco2e=Decimal(str(emissions_amount * 1000)),
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Compare facilities
        result = analytics_service.compare_facilities(
            tenant_id=tenant.id,
            facility_ids=[facility_1.id, facility_2.id],
            period="current_year"
        )

        assert result["status"] == "success"
        assert result["facility_count"] == 2
        # Facility 1 should be top emitter
        assert result["comparison"][0]["facility_id"] == str(facility_1.id)
        assert result["comparison"][0]["total_emissions_tco2e"] == 500
        assert result["comparison"][1]["total_emissions_tco2e"] == 300
        assert result["total_portfolio_tco2e"] == 800

    def test_compare_multiple_scopes(self, analytics_service, db_session, tenant_org_facilities):
        """Test comparison with multiple scopes"""
        tenant, org, facilities = tenant_org_facilities
        facility = facilities[0]

        # Create sources for each scope
        scopes = {
            "scope1": 100,  # tCO2e
            "scope2": 200,
            "scope3": 500
        }

        for scope_name, emissions_amount in scopes.items():
            source = EmissionsSource(
                id=str(uuid4()),
                tenant_id=tenant.id,
                organization_id=org.id,
                facility_id=facility.id,
                source_name=f"{scope_name} Source",
                source_type="electricity",
                scope=scope_name
            )
            db_session.add(source)
            db_session.flush()

            calc = EmissionsCalculation(
                id=str(uuid4()),
                tenant_id=tenant.id,
                source_id=source.id,
                organization_id=org.id,
                calculation_period_start=datetime(2026, 1, 1),
                calculation_period_end=datetime(2026, 12, 31),
                scope=scope_name,
                total_emissions_kgco2e=Decimal(str(emissions_amount * 1000)),
                status="approved"
            )
            db_session.add(calc)
        db_session.commit()

        # Compare facility against itself
        result = analytics_service.compare_facilities(
            tenant_id=tenant.id,
            facility_ids=[facility.id],
            period="current_year"
        )

        assert result["status"] == "success"
        assert result["comparison"][0]["total_emissions_tco2e"] == 800  # 100 + 200 + 500
        assert result["comparison"][0]["scope_1_tco2e"] == 100
        assert result["comparison"][0]["scope_2_tco2e"] == 200
        assert result["comparison"][0]["scope_3_tco2e"] == 500

