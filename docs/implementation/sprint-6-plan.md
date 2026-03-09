# Sprint 6: Carbon Accounting Engine

**Sprint**: 6
**Duration**: May 25 - June 7, 2026 (2 weeks)
**Module**: Carbon Accounting
**Owner**: Backend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements comprehensive carbon emissions calculation engine:
- Scope 1 (direct) emissions: fuel, refrigerants
- Scope 2 (indirect) emissions: grid electricity
- GHG Protocol methodology compliance
- Emission factor versioning and traceability
- Calculation audit trails
- Draft and approved states

**Dependency**: Energy Dashboards (Sprint 5) ✅

---

## Scope & Deliverables

### Phase 1: Emission Factors
- [x] Factor repository with versioning
- [x] Regional grid factors
- [x] Fuel type factors
- [x] Refrigerant factors
- [x] Factor update history

### Phase 2: Scope 1 Calculations
- [x] Fuel consumption × factor
- [x] Refrigerant leakage emissions
- [x] On-site vehicle emissions (placeholder)
- [x] Calculation traceability

### Phase 3: Scope 2 Calculations
- [x] Grid electricity × factor
- [x] Location-based factors
- [x] Market-based options
- [x] REC handling (placeholder)

### Phase 4: Calculation Service
- [x] Draft calculations
- [x] Recalculation with different factors
- [x] Batch processing
- [x] Result caching
- [x] Audit logging

### Phase 5: API & Integration
- [x] Calculate emissions endpoints
- [x] Factor lookup API
- [x] Calculation history
- [x] Approval workflow integration

### Phase 6: Testing
- [x] Calculation accuracy tests
- [x] Factor versioning tests
- [x] Approval workflow tests

---

## Database Schema

```sql
CREATE TABLE emission_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    factor_name VARCHAR(255) NOT NULL,
    factor_type VARCHAR(50),
    value NUMERIC(12, 6) NOT NULL,
    unit VARCHAR(50),
    region VARCHAR(100),
    data_source VARCHAR(255),
    effective_date DATE,
    obsolete_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE factor_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    factor_id UUID NOT NULL REFERENCES emission_factors(id),
    version_number INTEGER,
    value NUMERIC(12, 6),
    changelog TEXT,
    effective_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE carbon_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    organization_id UUID NOT NULL,
    period_start DATE,
    period_end DATE,
    scope_1_emissions NUMERIC(18, 6),
    scope_2_emissions NUMERIC(18, 6),
    scope_3_emissions NUMERIC(18, 6),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calculation_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_id UUID NOT NULL REFERENCES carbon_calculations(id),
    calculation_type VARCHAR(50),
    energy_input NUMERIC(12, 6),
    factor_id UUID NOT NULL,
    factor_version INTEGER,
    result NUMERIC(18, 6),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

```
GET    /api/v1/tenants/{tenant_id}/factors
       List emission factors
       Response: [{id, name, value, unit, region}]

GET    /api/v1/factors/{factor_id}/versions
       Factor version history
       Response: [{version, value, effective_date}]

POST   /api/v1/tenants/{tenant_id}/carbon/calculate
       Trigger carbon calculation
       Request: {org_id, period_start, period_end}
       Response: {calculation_id, status: 'draft'}

GET    /api/v1/carbon-calculations/{calc_id}
       Get calculation details
       Response: {id, scope1, scope2, details: [...]}

POST   /api/v1/carbon-calculations/{calc_id}/submit-for-review
       Submit to approval workflow
       Request: {comments}
       Response: {status: 'ready_for_review'}
```

---

## Carbon Service

```python
class CarbonService:
    def calculate_scope_1(self, org_id, period):
        # Query fuel consumption data
        # Get fuel factors
        # Calculate: fuel × factor

    def calculate_scope_2(self, org_id, period):
        # Query electricity consumption
        # Get grid factors (location-based)
        # Calculate: kwh × factor

    def get_factor_version(self, factor_id, date):
        # Get factor effective on date
```

---

## Testing

- GHG Protocol calculation accuracy
- Factor versioning and historical lookups
- Scope 1 and 2 calculations
- Approval workflow integration
- Data lineage traceability

---

**Target**: May 25 - June 7, 2026 | **Owner**: Backend Team
