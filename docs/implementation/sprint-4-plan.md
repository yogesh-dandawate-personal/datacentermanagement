# Sprint 4: Telemetry Ingestion & Normalization

**Sprint**: 4
**Duration**: April 27 - May 10, 2026 (2 weeks)
**Module**: Telemetry Ingestion & Normalization
**Owner**: Backend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements telemetry data ingestion from multiple sources with validation, normalization, and quality assurance:
- REST API telemetry endpoint
- CSV batch upload processing
- Schema validation
- Unit normalization
- Timestamp standardization
- Anomaly detection
- Stale feed detection
- High-volume time-series storage

**Dependency**: Asset Registry (Sprint 3) ✅

---

## Scope & Deliverables

### Phase 1: Telemetry API
- [x] POST /telemetry endpoint
- [x] Request validation (schema, types)
- [x] Rate limiting per tenant
- [x] Batch response with status
- [x] Error reporting for invalid records

### Phase 2: CSV Batch Upload
- [x] Multipart file upload endpoint
- [x] CSV parsing and validation
- [x] Schema mapping and configuration
- [x] Error collection and reporting
- [x] Rollback on critical errors

### Phase 3: Data Validation
- [x] Schema validation against device specs
- [x] Type checking (float, integer, string)
- [x] Range validation based on device specs
- [x] Null/missing value handling
- [x] Duplicate detection

### Phase 4: Normalization
- [x] Unit conversion (kW → kWh, etc.)
- [x] Timezone conversion to UTC
- [x] Timestamp standardization
- [x] Precision handling
- [x] Rounding rules

### Phase 5: Quality Assurance
- [x] Stale feed detection (>1 hour)
- [x] Outlier flagging (outside spec range)
- [x] Deduplication (same meter, timestamp)
- [x] Anomaly event creation
- [x] Alert triggering

### Phase 6: Storage & Testing
- [x] TimescaleDB hypertable storage
- [x] Automatic partitioning by date
- [x] Query optimization
- [x] Unit and integration tests
- [x] Performance tests (>1000 readings/sec)

---

## Database Schema

```sql
CREATE TABLE telemetry_readings (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    meter_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value NUMERIC(18, 6) NOT NULL,
    unit VARCHAR(20),
    status VARCHAR(50) DEFAULT 'valid',
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (timestamp, id)
) PARTITION BY RANGE (timestamp);

SELECT create_hypertable('telemetry_readings', 'timestamp');
SELECT set_chunk_time_interval('telemetry_readings', INTERVAL '1 day');

CREATE TABLE telemetry_validation_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    meter_id UUID,
    error_type VARCHAR(50),
    error_message TEXT,
    source_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(tenant_id, created_at)
);

CREATE TABLE telemetry_anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    meter_id UUID NOT NULL,
    anomaly_timestamp TIMESTAMP,
    anomaly_type VARCHAR(50),
    expected_value NUMERIC(18, 6),
    actual_value NUMERIC(18, 6),
    severity VARCHAR(20),
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(tenant_id, meter_id, created_at)
);
```

---

## API Endpoints

```
POST   /api/v1/tenants/{tenant_id}/telemetry
       Single reading ingestion
       Request: {meter_id, value, unit, timestamp}
       Response: {reading_id, status}

POST   /api/v1/tenants/{tenant_id}/telemetry/batch
       Batch CSV upload
       Request: File + schema mapping
       Response: {total: N, valid: N, errors: [...]}

GET    /api/v1/tenants/{tenant_id}/telemetry/latest
       Get latest readings
       Query: ?meter_ids=uuid1,uuid2&limit=100
       Response: [{meter_id, value, timestamp}]

GET    /api/v1/tenants/{tenant_id}/telemetry/history
       Query historical data
       Query: ?meter_id=uuid&start=date&end=date
       Response: [{timestamp, value}]

GET    /api/v1/tenants/{tenant_id}/telemetry/anomalies
       Get flagged anomalies
       Query: ?severity=high&status=open
       Response: [{anomaly}]

GET    /api/v1/tenants/{tenant_id}/telemetry/validation-errors
       Get validation errors
       Response: [{error}]
```

---

## Telemetry Service Architecture

```python
class TelemetryService:
    def ingest_reading(self, meter_id, value, timestamp, unit):
        # Validate
        self.validate_against_device_spec(meter_id, value)
        # Normalize
        normalized = self.normalize(value, unit, timestamp)
        # Check anomalies
        self.detect_anomalies(meter_id, normalized)
        # Store
        self.store_reading(meter_id, normalized)

class NormalizationService:
    def normalize(self, value, from_unit, to_unit='kWh'):
        return self.convert_units(value, from_unit, to_unit)

class AnomalyDetectionService:
    def detect_stale_feed(self, meter_id, timestamp):
        # Compare to last reading

    def detect_outlier(self, meter_id, value, timestamp):
        # Compare to device specs and historical range
```

---

## Testing

- Unit tests: validation, normalization, anomaly detection
- Integration tests: API ingestion, CSV upload, storage
- Performance tests: >1000 readings/sec throughput
- Data quality tests: deduplication, uniqueness

---

**Target**: April 27 - May 10, 2026 | **Owner**: Backend Team
