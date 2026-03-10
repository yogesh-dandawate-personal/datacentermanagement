# Emissions Module - Quick Start Guide

## 🚀 Getting Started

### Access the Module
Navigate to the **Emissions** menu item in the sidebar (green cloud icon)

### Main Landing Page
**URL**: `/emissions`
**File**: `frontend/src/pages/Emissions.tsx`

Shows:
- Module overview and description
- 6 main features with descriptions
- Key metrics placeholders
- Quick start guide (4 steps)
- Standards & compliance info
- Documentation links

---

## 📚 Available Features

### 1. **Facility Dashboard**
**URL**: `/emissions/dashboard` (Ready in Phase 2)

Shows:
- Total emissions by scope (tCO2e)
- Carbon intensity (gCO2e/kWh)
- PUE and renewable energy %
- 30-day trend charts
- Top emitting sources
- Month-over-month comparison

### 2. **Data Entry**
**URL**: `/emissions/data-entry` (Ready in Phase 2)

Features:
- Manual single data point entry
- CSV/Excel batch file upload
- Data validation preview
- Bulk import confirmation

### 3. **Reporting Center**
**URL**: `/emissions/reports` (Ready in Phase 2)

Features:
- Report template selection
- GHG Protocol, CDP, GRI, TCFD report generation
- Report history and versioning
- PDF/Excel export

### 4. **Reduction Targets**
**URL**: `/emissions/targets` (Ready in Phase 2)

Features:
- Set emissions reduction goals
- Track progress by period
- Target status (on_track, at_risk, failed)
- Milestone management

### 5. **Alerts Center**
**URL**: `/emissions/alerts` (Ready in Phase 2)

Features:
- Active alerts list
- Alert rule management
- Threshold configuration
- Acknowledge/resolve actions
- Alert history

### 6. **Analytics**
**URL**: `/emissions/analytics` (Ready in Phase 2)

Features:
- Portfolio overview
- Multi-facility comparison
- Benchmarking charts
- Carbon intensity trends
- Optimization opportunities

---

## 🔧 API Endpoints

### Emissions Sources
```bash
# List sources
GET /api/v1/emissions/organizations/{org_id}/sources

# Create source
POST /api/v1/emissions/organizations/{org_id}/sources
{
  "source_name": "Natural Gas Boilers",
  "source_type": "fuel_combustion",
  "scope": "scope1",
  "facility_id": "...",
  "unit_of_measure": "therms"
}
```

### Activity Data
```bash
# Submit single reading
POST /api/v1/emissions/organizations/{org_id}/activity-data
{
  "source_id": "...",
  "timestamp": "2026-03-10T14:30:00Z",
  "activity_value": 150.5,
  "activity_unit": "kWh"
}

# Upload batch CSV
POST /api/v1/emissions/organizations/{org_id}/activity-data/batch
(multipart/form-data with CSV file)

# Query activity data
GET /api/v1/emissions/organizations/{org_id}/activity-data?source_id=...&start_date=...&end_date=...
```

### Calculations
```bash
# Calculate Scope 1
POST /api/v1/emissions/organizations/{org_id}/calculate/scope1
{
  "source_id": "...",
  "period_start": "2026-03-01T00:00:00Z",
  "period_end": "2026-03-31T23:59:59Z"
}

# Calculate Scope 2
POST /api/v1/emissions/organizations/{org_id}/calculate/scope2
{...same payload...}

# Calculate Scope 3
POST /api/v1/emissions/organizations/{org_id}/calculate/scope3
{...same payload...}

# Query calculations
GET /api/v1/emissions/organizations/{org_id}/calculations?scope=scope1&status=approved
```

### Analytics
```bash
# Facility dashboard
GET /api/v1/emissions/facilities/{facility_id}/dashboard?period=current_month

# Portfolio overview
GET /api/v1/emissions/organizations/{org_id}/portfolio?period=current_year
```

### Targets
```bash
# Get targets
GET /api/v1/emissions/organizations/{org_id}/targets

# Create target
POST /api/v1/emissions/organizations/{org_id}/targets
{
  "target_name": "Net-zero by 2030",
  "target_type": "net_zero",
  "baseline_year": 2021,
  "baseline_value": 50000,
  "target_year": 2030,
  "target_value": 0,
  "scope": "all"
}
```

### Alerts
```bash
# Get active alerts
GET /api/v1/emissions/organizations/{org_id}/alerts?severity=critical

# Get alert rules
GET /api/v1/emissions/organizations/{org_id}/alert-rules

# Create alert rule
POST /api/v1/emissions/organizations/{org_id}/alert-rules
{
  "rule_name": "High emissions warning",
  "metric": "total_emissions",
  "operator": ">",
  "threshold_value": 100000,
  "severity": "warning",
  "notification_channels": ["email", "slack"]
}
```

---

## 📱 Frontend Hooks

### useFacilityEmissions
```typescript
const { data, loading, error } = useFacilityEmissions(facilityId, 'current_month')

// data contains:
// - total_tco2e, scope_1_tco2e, scope_2_tco2e, scope_3_tco2e
// - carbon_intensity_gco2e_kwh, pue, renewable_pct
// - breakdown array, trend_30d array, top_sources array
```

### useEmissionsAlerts
```typescript
const { alerts, loading, error, acknowledgeAlert, resolveAlert } = useEmissionsAlerts(orgId, severity)

// Methods:
await acknowledgeAlert(alertId)
await resolveAlert(alertId)
```

### useEmissionsTargets
```typescript
const { targets, loading, error, createTarget } = useEmissionsTargets(orgId)

// Method:
await createTarget({
  target_name: "...",
  baseline_year: 2021,
  baseline_value: 50000,
  target_year: 2030,
  target_value: 0
})
```

### useCalculateEmissions
```typescript
const { calculateScope1, calculateScope2, calculateScope3, loading, error } = useCalculateEmissions(orgId)

// Methods:
await calculateScope1(sourceId, periodStart, periodEnd)
await calculateScope2(sourceId, periodStart, periodEnd)
await calculateScope3(sourceId, periodStart, periodEnd)
```

### useActivityDataSubmission
```typescript
const { submitSingle, uploadBatch, loading, error } = useActivityDataSubmission(orgId)

// Methods:
await submitSingle(sourceId, timestamp, value, unit)
await uploadBatch(csvFile, sourceId)
```

---

## 🗂️ File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── emissions.py              # 12 database models
│   ├── services/
│   │   ├── emissions_calculation_service.py      # Scope 1/2/3 calculations
│   │   ├── emissions_ingestion_service.py        # CSV/API ingestion
│   │   └── emissions_analytics_service.py        # Dashboards & trends
│   └── routes/
│       └── emissions.py              # 25+ API endpoints

frontend/
├── src/
│   ├── pages/
│   │   └── Emissions.tsx             # Main landing page
│   ├── hooks/
│   │   └── useEmissions.ts           # 8 custom hooks
│   ├── services/
│   │   └── emissions-api.ts          # API client
│   ├── types/
│   │   └── emissions.ts              # 10 TypeScript types
│   └── components/
│       └── Layout.tsx                # Updated with Emissions nav

docs/
└── implementation/
    ├── EMISSIONS_MODULE_IMPLEMENTATION.md    # Full documentation
    └── EMISSIONS_QUICK_START.md             # This file
```

---

## 🔐 Data Flow

```
User Input (Frontend)
    ↓
API Client Service
    ↓
REST API Routes
    ↓
Business Logic Services
    ↓
Database Models
    ↓
PostgreSQL
    ↓
Response → Frontend Hooks → React Components
```

---

## 📊 Database Schema

**Key Tables**:
- `emissions_sources` - Defines what we're tracking
- `emissions_activity_data` - Raw readings (meter, fuel, etc.)
- `emissions_calculations` - Calculated emissions
- `emissions_calculation_details` - Line-item audit trail
- `emissions_reports` - ESG reports
- `emissions_targets` - Reduction goals
- `emissions_alerts` - Threshold breaches
- `emissions_alert_rules` - Alert configurations

**Relationships**:
```
EmissionsSource → EmissionsActivityData → EmissionsCalculation
                                              ↓
                                      EmissionsCalculationDetail
                                              ↓
                                      (Audit Trail)

EmissionsTarget ← EmissionsTargetProgress (tracking)

EmissionsAlertRule → EmissionsAlert (when triggered)

EmissionsReport ← EmissionsReportSection (versioning)
```

---

## 🧪 Testing

### Test API with curl
```bash
# Create emission source
curl -X POST http://localhost:8000/api/v1/emissions/organizations/{org_id}/sources \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "Test Source",
    "source_type": "electricity",
    "scope": "scope2",
    "unit_of_measure": "kWh"
  }'

# Submit activity data
curl -X POST http://localhost:8000/api/v1/emissions/organizations/{org_id}/activity-data \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "{source_id}",
    "timestamp": "2026-03-10T14:30:00Z",
    "activity_value": 100,
    "activity_unit": "kWh"
  }'

# Get facility dashboard
curl http://localhost:8000/api/v1/emissions/facilities/{facility_id}/dashboard
```

---

## 📝 Standard Emission Factors

| Source | Factor | Unit | Scope |
|--------|--------|------|-------|
| Natural Gas | 2.04 | kg CO2e per therm | 1 |
| Diesel Fuel | 10.15 | kg CO2e per gallon | 1 |
| Electricity (US) | 0.42 | kg CO2e per kWh | 2 |
| SF6 Refrigerant | 23,500 | kg CO2e per kg leaked | 1 |

---

## 🚨 Common Issues

### 404 Not Found on API Endpoints
- Ensure tenant_id matches your user's tenant
- Check organization_id exists in database
- Verify facility_id is valid

### Validation Errors on Data Submission
- Ensure activity_value is positive decimal
- Check timestamp is valid ISO format
- Verify activity_unit matches source's unit_of_measure

### Empty Dashboard Data
- Confirm calculations have been run
- Check that calculations have status = "approved"
- Verify facility_id parameter is correct

---

## 📞 Support

For questions or issues:
1. Check the full implementation documentation
2. Review the code comments in service classes
3. Check API endpoint docstrings
4. Review hook implementation in useEmissions.ts

---

## 🎯 Next Phase (Phase 2)

Ready to build:
- Facility Dashboard page
- Data Entry forms
- Reporting Center UI
- Targets & Alerts pages
- Analytics dashboard

All backend infrastructure is ready for integration!
