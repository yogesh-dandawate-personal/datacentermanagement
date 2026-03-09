# Sprint 7: KPI Engine & Performance Metrics

**Sprint**: 7
**Duration**: June 8 - June 21, 2026 (2 weeks)
**Module**: KPI Engine
**Owner**: Backend + Frontend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements KPI calculation and tracking system:
- Standard KPIs: PUE, CUE, WUE, ERE
- Custom KPI definitions
- Hourly/daily/monthly snapshots
- Threshold-based alerting
- Benchmark comparisons
- Dashboard widgets

**Dependency**: Carbon Engine (Sprint 6) ✅

---

## Scope & Deliverables

- [x] KPI definitions (PUE, CUE, WUE, ERE, custom)
- [x] Snapshot calculations at intervals
- [x] Threshold configuration
- [x] Alert triggers
- [x] Historical tracking
- [x] KPI dashboard page
- [x] Comparison reports

---

## Database Schema

```sql
CREATE TABLE kpi_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    kpi_name VARCHAR(100) NOT NULL,
    formula TEXT NOT NULL,
    unit VARCHAR(50),
    target_value NUMERIC(12, 6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE kpi_snapshots (
    id UUID NOT NULL,
    kpi_id UUID NOT NULL,
    snapshot_date TIMESTAMP NOT NULL,
    calculated_value NUMERIC(18, 6),
    target_value NUMERIC(18, 6),
    variance_percent NUMERIC(8, 2),
    PRIMARY KEY (snapshot_date, id)
) PARTITION BY RANGE (snapshot_date);

CREATE TABLE kpi_thresholds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID NOT NULL,
    threshold_name VARCHAR(100),
    threshold_value NUMERIC(12, 6),
    operator VARCHAR(10),
    alert_severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

```
POST   /api/v1/organizations/{org_id}/kpi-definitions
       Create KPI definition
       Request: {name, formula, unit, target}

GET    /api/v1/organizations/{org_id}/kpi-definitions
       List KPIs

GET    /api/v1/kpi-snapshots
       Get KPI snapshots
       Query: ?kpi_id=uuid&start_date=date&end_date=date

POST   /api/v1/kpi-definitions/{id}/thresholds
       Create threshold

GET    /api/v1/organizations/{org_id}/kpi-thresholds/breaches
       Get threshold breaches
```

---

## KPI Formulas

```
PUE = Total Facility Power / IT Equipment Power
      Target: <1.2 (efficient DC)

CUE = Carbon Emissions / Total Computing Power
      Target: <50 g CO₂/kWh

WUE = Annual Water / Annual Energy
      Target: <1.8 L/kWh

ERE = Total Energy Used / Total Energy Reused
```

---

**Target**: June 8 - June 21, 2026
