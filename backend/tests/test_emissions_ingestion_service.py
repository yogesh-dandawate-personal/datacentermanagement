"""
Tests for Emissions Ingestion Service

Tests the following features:
- Unit conversion (kWh ↔ MWh, kg ↔ tonne, etc.)
- Duplicate detection and deduplication
- Batch retry mechanism with exponential backoff
- Advanced anomaly detection
- Data quality scoring
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import io
import csv

from app.services.emissions_ingestion_service import EmissionsIngestionService
from app.models import EmissionsSource, EmissionsActivityData, EmissionsIngestionLog, Tenant, Organization


@pytest.fixture
def ingestion_service(db_session):
    """Create ingestion service instance"""
    return EmissionsIngestionService(db_session)


@pytest.fixture
def tenant_and_org(db_session):
    """Create test tenant and organization"""
    tenant = Tenant(id=str(uuid4()), name="Test Tenant")
    org = Organization(id=str(uuid4()), tenant_id=tenant.id, name="Test Org")
    db_session.add(tenant)
    db_session.add(org)
    db_session.commit()
    return tenant, org


@pytest.fixture
def emissions_source(db_session, tenant_and_org):
    """Create test emissions source"""
    tenant, org = tenant_and_org
    source = EmissionsSource(
        id=str(uuid4()),
        tenant_id=tenant.id,
        organization_id=org.id,
        source_name="Test Electric Source",
        source_type="electricity",
        scope="scope2",
        unit_of_measure="kWh"
    )
    db_session.add(source)
    db_session.commit()
    return source


class TestUnitConversion:
    """Test unit conversion functionality"""

    def test_convert_kwh_to_mwh(self, ingestion_service):
        """Test converting kWh to MWh"""
        result = ingestion_service._convert_unit(
            Decimal("1000"),
            "kWh",
            "MWh"
        )
        assert result == Decimal("1")

    def test_convert_mwh_to_kwh(self, ingestion_service):
        """Test converting MWh to kWh"""
        result = ingestion_service._convert_unit(
            Decimal("2.5"),
            "MWh",
            "kWh"
        )
        assert result == Decimal("2500")

    def test_convert_kgco2e_to_tco2e(self, ingestion_service):
        """Test converting kg CO2e to tonne CO2e"""
        result = ingestion_service._convert_unit(
            Decimal("5000"),
            "kgCO2e",
            "tCO2e"
        )
        assert result == Decimal("5")

    def test_convert_gallon_to_liter(self, ingestion_service):
        """Test converting gallons to liters"""
        result = ingestion_service._convert_unit(
            Decimal("1"),
            "gallon",
            "L"
        )
        assert abs(result - Decimal("3.785411784")) < Decimal("0.001")

    def test_same_unit_no_conversion(self, ingestion_service):
        """Test that same units return same value"""
        result = ingestion_service._convert_unit(
            Decimal("100"),
            "kWh",
            "kWh"
        )
        assert result == Decimal("100")

    def test_invalid_unit_conversion_raises_error(self, ingestion_service):
        """Test that invalid unit conversion raises error"""
        with pytest.raises(ValueError):
            ingestion_service._convert_unit(
                Decimal("100"),
                "invalid_unit",
                "kWh"
            )


class TestDuplicateDetection:
    """Test duplicate detection functionality"""

    def test_exact_duplicate_detected(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test that exact duplicates are detected"""
        tenant, org = tenant_and_org

        # Create first reading
        reading1 = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh",
            data_source="manual_entry",
            validation_status="valid"
        )
        db_session.add(reading1)
        db_session.commit()

        # Detect duplicate
        duplicate_info = ingestion_service._detect_duplicate(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh"
        )

        assert duplicate_info is not None
        assert duplicate_info["is_duplicate"] is True
        assert duplicate_info["duplicate_type"] == "exact"

    def test_similar_duplicate_detected(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test that similar duplicates (±5%) are detected"""
        tenant, org = tenant_and_org

        # Create reading with value 100
        reading1 = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("100.0"),
            activity_unit="kWh",
            data_source="manual_entry",
            validation_status="valid"
        )
        db_session.add(reading1)
        db_session.commit()

        # Detect similar duplicate (within ±5%)
        duplicate_info = ingestion_service._detect_duplicate(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 35),  # 5 minutes later
            activity_value=Decimal("102.0"),  # 2% difference
            activity_unit="kWh"
        )

        assert duplicate_info is not None
        assert duplicate_info["is_duplicate"] is True
        assert duplicate_info["duplicate_type"] == "similar"
        assert duplicate_info["similarity_percent"] > 95

    def test_no_duplicate_for_unique_reading(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test that unique readings are not flagged as duplicates"""
        tenant, org = tenant_and_org

        duplicate_info = ingestion_service._detect_duplicate(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh"
        )

        assert duplicate_info is None

    def test_no_duplicate_outside_time_window(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test that readings outside time window are not considered duplicates"""
        tenant, org = tenant_and_org

        # Create reading
        reading1 = EmissionsActivityData(
            id=str(uuid4()),
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("100.0"),
            activity_unit="kWh",
            data_source="manual_entry",
            validation_status="valid"
        )
        db_session.add(reading1)
        db_session.commit()

        # Check reading 2 hours later
        duplicate_info = ingestion_service._detect_duplicate(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 16, 30),  # 2 hours later
            activity_value=Decimal("100.0"),
            activity_unit="kWh",
            time_window_minutes=30  # Only 30 minute window
        )

        assert duplicate_info is None


class TestDataQualityScoring:
    """Test data quality scoring functionality"""

    def test_perfect_score_for_valid_data(self, ingestion_service):
        """Test that valid data gets 100% quality score"""
        score, issues = ingestion_service._score_data_quality(
            {
                "activity_value": 150.5,
                "activity_unit": "kWh",
                "timestamp": "2026-03-10T14:30:00"
            },
            validation_status="valid",
            duplicate_info=None
        )

        assert score == 100.0
        assert len(issues) == 0

    def test_score_penalty_for_anomaly(self, ingestion_service):
        """Test quality score penalty for anomalies"""
        score, issues = ingestion_service._score_data_quality(
            {
                "activity_value": 150.5,
                "activity_unit": "kWh",
                "timestamp": "2026-03-10T14:30:00"
            },
            validation_status="suspected_anomaly",
            duplicate_info=None
        )

        assert score == 80.0
        assert len(issues) > 0

    def test_score_penalty_for_exact_duplicate(self, ingestion_service):
        """Test quality score penalty for exact duplicate"""
        score, issues = ingestion_service._score_data_quality(
            {
                "activity_value": 150.5,
                "activity_unit": "kWh",
                "timestamp": "2026-03-10T14:30:00"
            },
            validation_status="valid",
            duplicate_info={
                "is_duplicate": True,
                "duplicate_type": "exact"
            }
        )

        assert score == 70.0  # 100 - 30 penalty
        assert "duplicate" in str(issues).lower()

    def test_score_penalty_for_similar_duplicate(self, ingestion_service):
        """Test quality score penalty for similar duplicate"""
        score, issues = ingestion_service._score_data_quality(
            {
                "activity_value": 150.5,
                "activity_unit": "kWh",
                "timestamp": "2026-03-10T14:30:00"
            },
            validation_status="valid",
            duplicate_info={
                "is_duplicate": True,
                "duplicate_type": "similar",
                "similarity_percent": 98.5
            }
        )

        assert score == 85.0  # 100 - 15 penalty
        assert "similar" in str(issues).lower()


class TestAdvancedValidation:
    """Test advanced validation functionality"""

    def test_valid_reading_passes(self, ingestion_service):
        """Test that valid reading passes validation"""
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": 150.5,
            "activity_unit": "kWh",
            "timestamp": "2026-03-10T14:30:00"
        })

        assert status == "valid"
        assert notes is None

    def test_negative_value_fails(self, ingestion_service):
        """Test that negative values fail validation"""
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": -50.0,
            "activity_unit": "kWh",
            "timestamp": "2026-03-10T14:30:00"
        })

        assert status in ["suspected_anomaly", "invalid"]
        assert notes is not None
        assert "negative" in notes.lower()

    def test_future_timestamp_warning(self, ingestion_service):
        """Test that future timestamp generates warning"""
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": 150.5,
            "activity_unit": "kWh",
            "timestamp": future_time
        })

        assert status == "suspected_anomaly"
        assert "future" in notes.lower()

    def test_zero_value_warning(self, ingestion_service):
        """Test that zero values generate warning"""
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": 0.0,
            "activity_unit": "kWh",
            "timestamp": "2026-03-10T14:30:00"
        })

        assert status == "suspected_anomaly"
        assert "zero" in notes.lower()

    def test_unusually_high_value_warning(self, ingestion_service):
        """Test that unusually high values generate warning"""
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": 2000000.0,
            "activity_unit": "kWh",
            "timestamp": "2026-03-10T14:30:00"
        })

        assert status == "suspected_anomaly"
        assert "high" in notes.lower()

    def test_missing_required_field_fails(self, ingestion_service):
        """Test that missing required fields fail"""
        status, notes = ingestion_service._validate_activity_data({
            "activity_value": 150.5,
            # Missing activity_unit
            "timestamp": "2026-03-10T14:30:00"
        })

        assert status == "suspected_anomaly"
        assert notes is not None


class TestRetryMechanism:
    """Test retry mechanism with exponential backoff"""

    def test_is_retryable_error_detection(self, ingestion_service):
        """Test that retryable errors are correctly identified"""
        assert ingestion_service._is_retryable_error(Exception("Connection timeout")) is True
        assert ingestion_service._is_retryable_error(Exception("Database deadlock")) is True
        assert ingestion_service._is_retryable_error(Exception("Temporarily unavailable")) is True
        assert ingestion_service._is_retryable_error(Exception("Invalid data")) is False
        assert ingestion_service._is_retryable_error(Exception("Not found")) is False


class TestSingleReadingIngestion:
    """Test single reading ingestion with all features"""

    def test_ingest_valid_reading(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test ingesting a valid reading"""
        tenant, org = tenant_and_org

        result = ingestion_service.ingest_single_reading(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh"
        )

        assert result["status"] == "valid"
        assert result["activity_data_id"] is not None
        assert result["value"] == 150.5
        assert result["unit"] == "kWh"
        assert result["quality_score"] == 100

    def test_ingest_with_unit_conversion(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test ingesting with unit conversion"""
        tenant, org = tenant_and_org

        result = ingestion_service.ingest_single_reading(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("2.5"),
            activity_unit="MWh",
            convert_to_unit="kWh"
        )

        assert result["original_unit"] == "MWh"
        assert result["original_value"] == 2.5
        assert result["unit"] == "kWh"
        assert result["value"] == 2500.0

    def test_ingest_duplicate_rejected(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test that duplicates are rejected"""
        tenant, org = tenant_and_org

        # Ingest first reading
        result1 = ingestion_service.ingest_single_reading(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh"
        )

        assert result1["status"] == "valid"

        # Try to ingest exact duplicate
        result2 = ingestion_service.ingest_single_reading(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 30),
            activity_value=Decimal("150.5"),
            activity_unit="kWh",
            allow_duplicates=False
        )

        assert result2["status"] == "duplicate"
        assert result2["activity_data_id"] is None


class TestBatchIngestion:
    """Test batch file ingestion with all features"""

    def test_ingest_csv_file(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test ingesting CSV file with multiple records"""
        tenant, org = tenant_and_org

        # Create CSV content
        csv_content = """emissions_source_id,timestamp,activity_value,activity_unit
{source_id},2026-03-10T14:00:00,100.0,kWh
{source_id},2026-03-10T15:00:00,110.5,kWh
{source_id},2026-03-10T16:00:00,105.3,kWh
""".format(source_id=emissions_source.id).encode()

        result = ingestion_service.ingest_batch_file(
            tenant_id=tenant.id,
            file_content=csv_content,
            file_format="csv"
        )

        assert result["records_received"] == 3
        assert result["records_processed"] == 3
        assert result["records_failed"] == 0
        assert result["status"] == "completed"

    def test_ingest_batch_with_errors(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test batch ingestion with some errors"""
        tenant, org = tenant_and_org

        # Create CSV content with one invalid row
        csv_content = """emissions_source_id,timestamp,activity_value,activity_unit
{source_id},2026-03-10T14:00:00,100.0,kWh
{source_id},2026-03-10T15:00:00,-50.0,kWh
{source_id},2026-03-10T16:00:00,105.3,kWh
""".format(source_id=emissions_source.id).encode()

        result = ingestion_service.ingest_batch_file(
            tenant_id=tenant.id,
            file_content=csv_content,
            file_format="csv"
        )

        assert result["records_received"] == 3
        assert result["records_processed"] >= 2  # At least 2 valid records
        assert result["status"] in ["partial_success", "completed"]

    def test_ingest_batch_with_duplicate_skip(self, ingestion_service, db_session, tenant_and_org, emissions_source):
        """Test batch ingestion with duplicate detection"""
        tenant, org = tenant_and_org

        # Create first reading
        ingestion_service.ingest_single_reading(
            tenant_id=tenant.id,
            source_id=emissions_source.id,
            timestamp=datetime(2026, 3, 10, 14, 0),
            activity_value=Decimal("100.0"),
            activity_unit="kWh"
        )

        # Create CSV with duplicate
        csv_content = """emissions_source_id,timestamp,activity_value,activity_unit
{source_id},2026-03-10T14:00:00,100.0,kWh
{source_id},2026-03-10T15:00:00,110.5,kWh
""".format(source_id=emissions_source.id).encode()

        result = ingestion_service.ingest_batch_file(
            tenant_id=tenant.id,
            file_content=csv_content,
            file_format="csv",
            skip_duplicates=True
        )

        # First record should be skipped as duplicate, second processed
        assert result["records_received"] == 2
        assert result["records_processed"] == 1
        assert result["records_failed"] == 1

