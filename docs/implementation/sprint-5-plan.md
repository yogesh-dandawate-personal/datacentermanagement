# Sprint 5: Energy Dashboards & Analytics

**Sprint**: 5
**Duration**: May 11 - May 24, 2026 (2 weeks)
**Module**: Energy Analytics & Dashboards
**Owner**: Frontend + Backend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Builds real-time energy dashboard with analytics, trend analysis, and efficiency views:
- Real-time energy consumption dashboard
- Site-level and rack-level breakdowns
- Trend charts (hourly, daily, monthly)
- Peak usage identification
- Efficiency metrics and comparisons
- WebSocket real-time updates

**Dependency**: Telemetry Ingestion (Sprint 4) ✅

---

## Scope & Deliverables

### Phase 1: Energy Metrics Service
- [x] Energy aggregation (site, facility, rack level)
- [x] Total consumption calculations
- [x] Peak usage identification
- [x] Efficiency ratios (W/server, etc.)
- [x] Trend calculations

### Phase 2: Dashboard API
- [x] GET /api/v1/dashboards/{org_id}/energy
- [x] GET /api/v1/metrics/energy
- [x] Drill-down endpoints (site → facility → rack)
- [x] Time-range filtering
- [x] Real-time metric streaming

### Phase 3: Frontend Components
- [x] Energy dashboard page
- [x] Total consumption card
- [x] Line chart (consumption trends)
- [x] Bar chart (facility comparison)
- [x] Peak usage alerts
- [x] Efficiency metrics cards

### Phase 4: Real-time Features
- [x] WebSocket connection for live updates
- [x] Automatic refresh (30 sec intervals)
- [x] Cache invalidation
- [x] Connection recovery

### Phase 5: Analytics
- [x] Comparison to baseline
- [x] Forecast calculations
- [x] Anomaly highlighting
- [x] Export to CSV/PDF

### Phase 6: Testing
- [x] Unit tests (calculations)
- [x] Integration tests (API)
- [x] E2E tests (dashboard journey)
- [x] Performance tests (<2s load time)

---

## Database Queries

```sql
-- Total site consumption (hourly)
SELECT
  DATE_TRUNC('hour', timestamp) AS hour,
  SUM(value) AS total_kwh
FROM telemetry_readings
WHERE meter_id IN (SELECT id FROM meters WHERE device_id IN (...))
  AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour DESC;

-- Peak usage detection
SELECT
  DATE_TRUNC('hour', timestamp) AS hour,
  MAX(value) AS peak_kw
FROM telemetry_readings
WHERE meter_id = $1
  AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY hour
ORDER BY peak_kw DESC
LIMIT 10;
```

---

## Frontend Components

```typescript
// components/EnergyDashboard.tsx
- EnergyCard (total consumption)
- TrendChart (recharts LineChart)
- FacilityBreakdown (BarChart)
- PeakUsageTable
- EfficiencyMetrics
- TimeRangePicker

// hooks/useEnergyMetrics.ts
- Fetch dashboard data
- Subscribe to WebSocket updates
- Cache management
- Error handling
```

---

## API Endpoints

```
GET    /api/v1/organizations/{org_id}/dashboards/energy
       Full energy dashboard data
       Response: {total_kwh, sites: [], trends: [], peaks: []}

GET    /api/v1/metrics/energy
       Energy metrics query
       Query: ?period=day&interval=hour&org_id=uuid
       Response: [{timestamp, value}]

GET    /api/v1/sites/{site_id}/energy/breakdown
       Site energy breakdown by facility
       Response: [{building: {...}, total_kwh}]

GET    /api/v1/racks/{rack_id}/energy/devices
       Rack-level device breakdown
       Response: [{device, power_kw}]

WS     /api/v1/ws/dashboards/{org_id}/energy
       WebSocket for live updates
       Emits: {type: 'energy_update', data: {...}}
```

---

## Testing

- Unit tests: aggregation, peak detection, efficiency calculations
- Integration tests: dashboard API, data retrieval
- E2E tests: load dashboard, view trends, export data
- Performance: dashboard load <2 seconds

---

**Target**: May 11 - May 24, 2026 | **Owner**: Frontend + Backend Team
