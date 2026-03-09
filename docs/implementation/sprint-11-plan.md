# Sprint 11: Reporting Engine

**Sprint**: 11
**Duration**: August 3 - August 16, 2026 (2 weeks)
**Module**: Reporting Engine
**Owner**: Backend + Frontend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements comprehensive ESG reporting system:
- ESG monthly reports
- Emissions summaries (Scope 1/2/3)
- KPI performance reports
- Evidence-linked exports
- Multiple export formats (PDF, Excel, JSON)
- Report versioning and snapshots
- Template customization

**Dependency**: Workflow & Approvals (Sprint 10) ✅

---

## Scope & Deliverables

- [x] Report generation service
- [x] Data aggregation across all modules
- [x] PDF/Excel/JSON export
- [x] Evidence linking in reports
- [x] Report versioning
- [x] Template system
- [x] Report approval workflows
- [x] Reporting dashboard

---

## Report Types

```
1. ESG Monthly Report
   - Organization info
   - Executive summary
   - Scope 1/2 breakdown
   - KPI performance
   - Evidence references
   - Approval signatures

2. Emissions Summary
   - Scope 1, 2, 3 totals
   - Monthly trends
   - Factor notes

3. KPI Summary
   - PUE, CUE, WUE trends
   - Threshold breaches
   - Benchmarking

4. Evidence-Linked Export
   - CSV with all metrics
   - References to supporting docs
```

---

## Database Schema

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    organization_id UUID NOT NULL,
    report_type VARCHAR(50),
    report_period_start DATE,
    report_period_end DATE,
    current_state VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(organization_id, report_period_start)
);

CREATE TABLE report_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id),
    version_number INTEGER,
    s3_key_pdf VARCHAR(500),
    s3_key_json VARCHAR(500),
    state VARCHAR(50),
    version_date TIMESTAMP,
    versioned_by VARCHAR(255),
    version_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE report_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_version_id UUID NOT NULL,
    signer_name VARCHAR(255),
    signer_role VARCHAR(100),
    signature_data TEXT,
    signed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

```
POST   /api/v1/tenants/{tenant_id}/reports
       Create report
       Request: {organization_id, period_start, period_end}
       Response: {report_id, status: 'draft'}

GET    /api/v1/tenants/{tenant_id}/reports
       List reports
       Query: ?organization_id=uuid&status=approved

GET    /api/v1/reports/{report_id}
       Get report details

GET    /api/v1/reports/{report_id}/export
       Export report
       Query: ?format=pdf|excel|json
       Response: File download

PATCH  /api/v1/reports/{report_id}
       Update/submit report
       Request: {action: 'submit_for_review'}
```

---

## Report Generation Service

```python
class ReportService:
    def generate_report(self, org_id, period_start, period_end):
        # Aggregate energy data
        # Aggregate carbon data
        # Get KPI snapshots
        # Find evidence
        # Create sections
        # Generate PDF/Excel
        # Store versions
```

---

**Target**: August 3 - August 16, 2026
