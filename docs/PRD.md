# iCarbon: Agentic Data Center ESG Platform - Living PRD

**Version**: 1.0.0
**Status**: Active Development
**Last Updated**: March 9, 2026
**Maintained By**: Product & Engineering Team
**Living Document**: Yes - Updates tracked with date stamps

---

## 📑 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Objective](#product-objective)
3. [Mandatory Stack & Architecture](#mandatory-stack--architecture)
4. [Build Principles](#build-principles)
5. [Product Modules (Implementation Order)](#product-modules-implementation-order)
6. [Required Agents](#required-agents)
7. [Functional Scope - MVP](#functional-scope---mvp)
8. [Architecture Design](#architecture-design)
9. [Implementation Governance](#implementation-governance)
10. [Rules & Standards](#rules--standards)
11. [Testing Requirements](#testing-requirements)
12. [User Journeys](#user-journeys)
13. [Completion Criteria](#completion-criteria)
14. [Status & Progress Tracking](#status--progress-tracking)

---

## Executive Summary

**iCarbon** is an enterprise-grade, multi-tenant Software-as-a-Service (SaaS) platform designed to help data center operators track, calculate, report, and optimize Environmental, Social, and Governance (ESG) metrics with AI-powered agents and audit-ready governance workflows.

The platform enables organizations to:
- 🏢 Onboard multiple tenants and manage facility hierarchies
- 📊 Ingest and normalize telemetry from diverse sources
- 🔋 Calculate energy, cooling, water, and carbon metrics
- 📈 Generate compliance-ready ESG reports
- 🤖 Use AI agents for anomaly detection and optimization recommendations
- ✅ Enforce maker-checker-reviewer approval workflows
- 📋 Maintain immutable audit trails and evidence repositories

---

## Product Objective

Build a **production-grade, multi-tenant ESG platform for data centers** that:

### Core Capabilities
- ✅ **Tenant & Organization Management**: Multi-tenant onboarding with isolation, organization settings, reporting boundaries
- ✅ **Facility Hierarchy**: Site/building/zone/rack hierarchies with asset lifecycle tracking
- ✅ **Telemetry Ingestion**: API, CSV uploads, with extensibility for BACnet/Modbus/SNMP connectors
- ✅ **Energy Analytics**: Site and rack-level usage views, trend charts, peak usage analysis
- ✅ **Carbon Accounting**: Scope 1 (generators, refrigerants) and Scope 2 (grid electricity) calculations with factor versioning
- ✅ **KPI Engine**: PUE, CUE, WUE, and custom KPI snapshots with thresholds
- ✅ **Evidence Repository**: Versioned document storage, linking to metrics and reports, retention-ready schema
- ✅ **Approval Workflows**: Maker-checker-reviewer states with audit trail
- ✅ **Reporting**: ESG reports, emissions summaries, KPI summaries, evidence-linked exports
- ✅ **Executive Copilot**: AI-powered Q&A over approved/draft data with citations, no fabrication

### Extensibility Targets
- 🔄 Scope 3 emissions (business travel, supply chain, employee commuting)
- 🔄 Cooling efficiency analysis and recommendations
- 🔄 Water usage intelligence
- 🔄 Workload carbon attribution
- 🔄 Real-time anomaly detection and alerting

---

## Mandatory Stack & Architecture

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18+ / TypeScript | Modern, type-safe UI framework |
| **Backend** | FastAPI / Python 3.11+ | High-performance async APIs, easy AI/ML integration |
| **Primary DB** | PostgreSQL 15+ | ACID-compliant, rich data types, JSON support |
| **Time-Series DB** | TimescaleDB (PostgreSQL extension) | Optimized for telemetry data at scale |
| **Vector Store** | pgvector (PostgreSQL extension) | Embeddings for semantic search and retrieval |
| **Authentication** | Keycloak | Enterprise SSO, multi-tenant user management |
| **Object Storage** | S3-compatible (AWS S3 / MinIO) | Scalable evidence and report storage |
| **Async Workflows** | Celery or Temporal | Reliable task orchestration for calculations |
| **Message Bus** | Kafka or Redpanda | Event streaming for real-time updates |
| **Observability** | OpenTelemetry + Prometheus | Standardized metrics and tracing |
| **Containerization** | Docker / Docker Compose | Reproducible environments |
| **Orchestration** | Kubernetes (optional) | Production scaling |

### Architectural Principles
- **Multi-tenant by design**: Strict tenant isolation at database and API layers
- **Event-driven**: Decoupled services via message bus
- **Audit-first**: Every material change logged with user, timestamp, reason
- **API-first**: OpenAPI 3.0 spec, versioned endpoints
- **Type-safe**: TypeScript frontend, Pydantic schemas backend
- **Observable**: All operations traceable via OpenTelemetry
- **Testable**: Unit, integration, and E2E test coverage required

---

## Build Principles

### Non-Negotiable Rules

1. **Do not fake completion** - No partial scaffolding marked as done
2. **Verify before shipping** - Code, tests, API contracts, docs, UI paths all required
3. **Discover first** - Inspect current repository before making changes
4. **Preserve working behavior** - No breaking changes without explicit approval
5. **Make everything auditable** - All material workflows must have audit trails
6. **AI agents are explainable** - Every agent action logged, approved, cited
7. **Never corrupt approved data** - Reporting snapshots are immutable; use restatement workflows
8. **Enforce governance** - Maker-checker-reviewer workflows mandatory
9. **Keep it modular** - Domain logic is reusable and testable
10. **Vertical slices over scaffolding** - Incremental, end-to-end features

---

## Product Modules (Implementation Order)

Implement in this sequence unless repository discovery reveals a better path:

### Phase 1: Foundation (Sprints 1-3)
| # | Module | Dependencies | Status | Owner |
|---|--------|--------------|--------|-------|
| 1 | **Auth & Tenant Setup** | Keycloak, JWT | 🔄 In Progress | Backend |
| 2 | **Organization & Facility Hierarchy** | Auth, DB migrations | 📋 Planned | Backend |
| 3 | **Asset Registry** | Org/Facility, DB schema | 📋 Planned | Backend |

### Phase 2: Data Ingestion & Analytics (Sprints 4-6)
| # | Module | Dependencies | Status | Owner |
|---|--------|--------------|--------|-------|
| 4 | **Telemetry Ingestion & Normalization** | Asset registry, APIs | 📋 Planned | Backend |
| 5 | **Energy Dashboards** | Telemetry, Frontend | 📋 Planned | Frontend + Backend |
| 6 | **Carbon Accounting Engine** | Telemetry, Factor library | 📋 Planned | Backend |
| 7 | **ESG KPI Engine** | Energy data, Carbon data | 📋 Planned | Backend |

### Phase 3: Governance & Agents (Sprints 7-9)
| # | Module | Dependencies | Status | Owner |
|---|--------|--------------|--------|-------|
| 8 | **Alerting & Anomalies** | Telemetry, Metrics | 📋 Planned | Backend + ML |
| 9 | **Evidence Repository** | S3, DB schema, Versioning | 📋 Planned | Backend |
| 10 | **Workflow & Approvals** | Auth, Audit logging | 📋 Planned | Backend + Frontend |
| 11 | **Reporting Engine** | All metrics, Evidence | 📋 Planned | Backend |

### Phase 4: AI & Advanced Features (Sprints 10-12)
| # | Module | Dependencies | Status | Owner |
|---|--------|--------------|--------|-------|
| 12 | **Agent Orchestrator** | APIs, Workflows, Kafka | 📋 Planned | Backend |
| 13 | **Executive Copilot** | LLM, Vector search, Auth | 📋 Planned | Backend + ML |

---

## Required Agents

### MVP Agents (Must Implement)

#### 1. Telemetry Agent
**Purpose**: Validate, normalize, and ingest telemetry data
- **Inputs**: Raw meter readings, CSV uploads, API streams
- **Actions**: Validate schema, normalize units/timestamps, detect stale feeds, flag anomalies
- **Outputs**: Normalized telemetry records, validation reports, anomaly alerts
- **Authority**: Read-only; creates audit logs, never overwrites approved records
- **Guardrails**: Reject malformed data, enforce tenant isolation, version factor changes

#### 2. Carbon Accounting Agent
**Purpose**: Calculate Scope 1 and Scope 2 emissions with factor traceability
- **Inputs**: Energy consumption, fuel usage, grid mix data, emission factors
- **Actions**: Apply GHG Protocol methodology, calculate emissions, track factor versions
- **Outputs**: Scope 1/2 emission records, calculation breakdowns, audit logs
- **Authority**: Creates draft calculations, suggests corrections, never overwrites approved reports
- **Guardrails**: Use versioned factors, cite source data, flag missing inputs

#### 3. Compliance Agent
**Purpose**: Validate data completeness and regulatory alignment
- **Inputs**: Organization config, metric completeness, reporting requirements
- **Actions**: Check GRI/TCFD/CDP alignment, flag missing evidence, validate scope boundaries
- **Outputs**: Compliance status reports, gap analyses, remediation tasks
- **Authority**: Creates compliance flags and tasks for human review
- **Guardrails**: Never suppress non-compliance, require evidence for approvals

#### 4. Evidence Agent
**Purpose**: Manage evidence linking and metadata
- **Inputs**: Document uploads, metric IDs, report IDs
- **Actions**: Tag evidence, link to metrics, version documents, manage retention
- **Outputs**: Versioned evidence records, link records, retention schedule
- **Authority**: Creates evidence metadata and versions
- **Guardrails**: Prevent orphaned documents, maintain chain of custody

#### 5. Executive Copilot Agent
**Purpose**: Answer questions over ESG data with citations
- **Inputs**: User questions, approved/draft data, evidence repository
- **Actions**: Retrieve relevant data, generate responses with citations, explain reasoning
- **Outputs**: Answer with source references, no fabrication
- **Authority**: Read-only, citations mandatory
- **Guardrails**: Never invent missing data, require approval for draft data access

### Future Agents (Placeholders)
- Cooling Efficiency Agent
- Water Intelligence Agent
- Recommendation Agent
- Workload Carbon Agent

---

## Functional Scope - MVP

### TENANT & ORGANIZATION

**Features**:
- [ ] Tenant creation and provisioning
- [ ] Organization settings (name, address, timezone, reporting units)
- [ ] Reporting boundaries configuration
- [ ] Timezone and unit preferences (kWh/MWh, Metric/Imperial)
- [ ] Tenant-aware access controls

**Test Coverage**: Unit tests for tenant isolation, integration tests for multi-tenant queries

**Approval**: None required; system admin action

---

### FACILITY & ASSETS

**Facility Hierarchy**:
```
Tenant
  ├── Organization
      ├── Site/Building
          ├── Zone/Floor
              ├── Rack/Cabinet
                  └── Device
```

**Devices**:
- Servers, UPS, PDU
- Generator, Chiller, CRAH/CRAC
- Meters (electricity, water, gas)
- Custom devices via extensible schema

**Asset Metadata**:
- [ ] Installation date, lifecycle status
- [ ] Capacity and specifications
- [ ] Location coordinates
- [ ] Maintenance history tracking
- [ ] Deprecation scheduling

**Test Coverage**: Hierarchy validation, circular dependency prevention, asset lookup performance

---

### TELEMETRY

**Ingestion Methods (MVP)**:
- [ ] REST API endpoint (`POST /api/v1/tenants/{tenant_id}/telemetry`)
- [ ] CSV batch upload with schema validation
- [ ] Future: BACnet, Modbus, SNMP via abstraction layer

**Data Normalization**:
- [ ] Timestamp normalization (UTC conversion, timezone awareness)
- [ ] Unit conversion (kW, kWh, Watts, etc.)
- [ ] Stale feed detection (e.g., readings >1 hour old)
- [ ] Outlier flagging (values outside device spec)
- [ ] Deduplication (same metric, same timestamp)

**Storage**:
- [ ] TimescaleDB hypertables for high-cardinality metrics
- [ ] Automatic compression for old data
- [ ] Query optimization for time-range scans

**Test Coverage**: Schema validation, unit conversion accuracy, performance under load

---

### ENERGY

**Views & Analytics**:
- [ ] Site-level energy usage dashboard
- [ ] Rack-level energy consumption breakdown
- [ ] Trend charts (hourly, daily, monthly)
- [ ] Peak usage identification
- [ ] Comparison to baselines and forecasts

**Calculations**:
- [ ] Total site consumption (kWh, kW)
- [ ] Per-rack consumption
- [ ] Efficiency metrics (W per server, etc.)

**Test Coverage**: Aggregation accuracy, chart data correctness

---

### CARBON ACCOUNTING

**Scope 1: Direct Emissions**
- [ ] Generator fuel consumption (diesel, natural gas) → CO₂e calculation
- [ ] Refrigerant emissions (HFC, HCF, R-22 leakage)
- [ ] On-site vehicles (optional for MVP)
- [ ] Emission factors by fuel type (versioned)

**Scope 2: Indirect (Grid Electricity)**
- [ ] Purchased electricity consumption
- [ ] Regional grid emission factors (location-based)
- [ ] Renewable energy certificates (RECs) handling
- [ ] Market-based vs. location-based options

**Calculation Engine**:
- [ ] GHG Protocol alignment
- [ ] Calculation traceability (audit trail)
- [ ] Factor versioning and change history
- [ ] Uncertainty ranges (±%)
- [ ] Support for custom emission factors

**Scope 3: Placeholder**
- Database schema ready for:
  - Business travel (flights, hotels)
  - Commuting
  - Supply chain (embodied carbon in equipment)
  - Waste disposal

**Test Coverage**: Calculation accuracy against GHG Protocol, factor versioning, data lineage

---

### KPIs

**Standard KPIs**:
- [ ] **PUE** (Power Usage Effectiveness) = Total Facility Power / IT Equipment Power
  - Target: <1.2 for efficient data centers
- [ ] **CUE** (Carbon Usage Effectiveness) = Facility Carbon Emissions / Total Computing Power
  - Target: <50 g CO₂/kWh
- [ ] **WUE** (Water Usage Effectiveness) = Annual Water / Annual Energy (L/kWh)
  - Target: <1.8 L/kWh
- [ ] **ERE** (Energy Reuse Effectiveness) = Total Energy Used / Total Energy Wasted
- [ ] **Custom KPIs**: User-defined formulas

**Snapshots & Thresholds**:
- [ ] KPI calculation at specified intervals (hourly, daily, monthly)
- [ ] Threshold alerting (e.g., PUE >1.5)
- [ ] Historical snapshots (never overwrite, only restate)
- [ ] Comparison to targets and benchmarks

**Test Coverage**: KPI calculation formulas, threshold alerting

---

### EVIDENCE REPOSITORY

**Capabilities**:
- [ ] Document upload (PDF, images, Excel)
- [ ] Metadata tagging (category, date, facility, metric tags)
- [ ] Versioning (keep audit history)
- [ ] Link to metrics and reports
- [ ] Retention scheduling
- [ ] Full-text search

**Schema**:
- ID, name, category
- Upload timestamp, uploader (user)
- File hash (integrity check)
- Linked metric/report IDs
- Version history
- Retention expiry
- Soft delete flag

**Test Coverage**: Upload/download, linking integrity, version management

---

### WORKFLOWS & APPROVALS

**Maker-Checker-Reviewer Pattern**:
- [ ] **Draft state**: Data entry, calculations in progress
- [ ] **Ready for review**: Maker marks as complete, awaits checker validation
- [ ] **Checked**: Checker reviews for accuracy, data quality, approves or rejects
- [ ] **Ready for approval**: Checked data awaits final sign-off
- [ ] **Approved**: Reviewer signs off; data becomes immutable reference
- [ ] **Comments trail**: All decisions logged with comments and signatures

**Workflow Actions**:
- [ ] Submit for review (maker → checker)
- [ ] Approve/request changes (checker → maker)
- [ ] Final sign-off (reviewer)
- [ ] Restatement (if approved data must be corrected)

**Audit Logging**:
- [ ] User ID, timestamp, action
- [ ] Old/new values (for material changes)
- [ ] Comment/reason
- [ ] Role-based authorization

**Test Coverage**: State transitions, permission checks, audit trail completeness

---

### REPORTING

**Reports (MVP)**:
- [ ] **ESG Monthly Report**:
  - Cover page (organization, period)
  - Executive summary (top metrics, trends)
  - Scope 1, 2, 3 breakdown
  - KPI performance vs. targets
  - Evidence references
  - Approval sign-off page

- [ ] **Emissions Summary**: Scope 1/2/3, trend charts, factor notes

- [ ] **KPI Summary**: PUE, CUE, WUE trends, threshold breaches

- [ ] **Evidence-Linked Export**: CSV/JSON with document references

**Report States**:
- [ ] Draft (editable, approval pending)
- [ ] Under review (awaiting checker/reviewer)
- [ ] Approved (immutable reference)
- [ ] Restated (previous version marked superseded, audit trail)

**Formats**:
- [ ] PDF (printable, signed)
- [ ] Excel (data, charts)
- [ ] JSON (API export)
- [ ] HTML (web view)

**Test Coverage**: Report generation, approval states, export accuracy

---

### COPILOT (EXECUTIVE Q&A)

**Capabilities**:
- [ ] Natural language questions: "What is our Scope 2 emissions this month?"
- [ ] Citation of sources: "Based on grid consumption data and regional factors"
- [ ] Navigation to underlying data: Links to reports, metrics, evidence
- [ ] No fabrication: "I don't have complete data for..."
- [ ] Access control: Only approved data (or draft if user authorized)

**Implementation**:
- [ ] Semantic search over approved/draft records
- [ ] Claude API (or similar) for text generation
- [ ] Vector embeddings for data retrieval
- [ ] Citation tracking (source entity IDs)
- [ ] Audit logging of copilot requests

**Test Coverage**: Citation accuracy, no hallucination, access control

---

## Architecture Design

### Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   External Systems                        │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐            │
│  │ BMS/DCIM│  │ Meter APIs │  │ Weather  │            │
│  │ Systems │  │  (Iot)     │  │Services  │            │
│  └────┬─────┘  └──────┬─────┘  └──────┬───┘            │
└───────┼────────────────┼──────────────┼─────────────────┘
        │                │              │
        └────────────────┼──────────────┘
                         │
        ┌────────────────▼──────────────┐
        │    iCarbon ESG Platform       │
        │  (React + FastAPI + PG)       │
        │  ┌──────────────────────────┐ │
        │  │ Frontend (React/TS)      │ │
        │  │ Dashboards, Reports,     │ │
        │  │ Approval UI, Copilot     │ │
        │  └────────────┬─────────────┘ │
        │               │                 │
        │  ┌────────────▼─────────────┐ │
        │  │ Backend (FastAPI/Python) │ │
        │  │ APIs, Agents, Services   │ │
        │  └──────────┬────────────────┘ │
        │             │                   │
        │  ┌──────────▼──────────────┐  │
        │  │ PostgreSQL + Extensions│  │
        │  │ TimescaleDB, pgvector   │  │
        │  │ Evidence, Audit logs    │  │
        │  └─────────────────────────┘  │
        └────────────────────────────────┘
             │            │            │
   ┌─────────┴─┐  ┌──────┴─────┐  ┌──┴────────┐
   │  Keycloak │  │   Kafka    │  │ S3 / MinIO│
   │ (Auth)    │  │ (Events)   │  │(Evidence) │
   └───────────┘  └────────────┘  └───────────┘
```

### Container Diagram

```
iCarbon Platform:
┌──────────────────────────────────────────────────────┐
│ Frontend Container                                   │
│ ├── React App                                       │
│ ├── API Client (TypeScript)                         │
│ ├── State Management (Redux)                        │
│ └── Route Guards, Role-Based UI                     │
└──────────────┬───────────────────────────────────────┘
               │ HTTP/REST
┌──────────────▼───────────────────────────────────────┐
│ Backend Container                                    │
│ ├── FastAPI Application                             │
│ ├── Authentication (Keycloak integration)           │
│ ├── Tenant Middleware (isolation)                   │
│ ├── API Routes (/api/v1/...)                        │
│ ├── Business Logic (Services)                       │
│ ├── Agent Orchestrator                              │
│ │   ├── Telemetry Agent                             │
│ │   ├── Carbon Agent                                │
│ │   ├── Compliance Agent                            │
│ │   ├── Evidence Agent                              │
│ │   └── Copilot Agent                               │
│ ├── Celery/Temporal Workers (async tasks)           │
│ └── OpenTelemetry Exporter                          │
└───────┬──────────┬──────────┬──────────┬─────────────┘
        │          │          │          │
        │ (SQL)    │(Async)   │(Events)  │
        │          │          │          │
┌───────▼────┐ ┌───┴────┐ ┌──┴──┐ ┌───┴────────┐
│ PostgreSQL │ │ Celery │ │Kafka│ │ Keycloak   │
│ + TS + PG │ │ Broker │ │ Bus │ │ (OAuth2)   │
│  + pgvector│ │ (Redis)│ │     │ └────────────┘
└────────────┘ └────────┘ └─────┘
        │
        └────┬────┐
            │    │
        ┌───▼──┐ ┌┴────────┐
        │TimescaleDB     │
        │Hypertables    │
        └────────────────┘
```

### Domain Model Summary

**Core Entities**:
- **Tenant**: Isolated customer with multiple organizations
- **Organization**: Business unit with settings
- **Site/Building/Zone/Rack**: Facility hierarchy
- **Device**: Physical asset (meter, server, UPS, etc.)
- **Telemetry**: Time-series readings from devices
- **Metric**: Calculated value (energy, emissions, KPI)
- **Factor**: Emission factor (version history)
- **Report**: ESG report (draft, checked, approved, restated)
- **Evidence**: Supporting documents (versioned, linked)
- **Workflow**: Approval state machine (maker-checker-reviewer)
- **AuditLog**: Immutable change record

---

### Event Flow Summary

```
1. Telemetry Ingestion
   User/API → FastAPI → Telemetry Agent → Validate → TimescaleDB

2. Metric Calculation
   TimescaleDB → Kafka (telemetry event) → Carbon Agent → Calculate
   → Store Metrics → Kafka (metric event) → Dashboard Update

3. Approval Workflow
   User (Maker) → Submit Report → Kafka → Notify Checker
   → Checker Reviews → Approve/Reject → Kafka → Notify Maker/Reviewer
   → Final Approval → Mark as Approved → Archive Reference

4. Copilot Query
   User Question → Copilot Agent → Vector Search (pgvector)
   → Retrieve Documents → LLM → Generate Response + Citations
   → Send to User → Log Request
```

---

### API Module Boundaries

#### Authentication Module
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

#### Tenant Module
- `POST /api/v1/tenants` (admin)
- `GET /api/v1/tenants/{tenant_id}` (tenant admin)
- `PATCH /api/v1/tenants/{tenant_id}` (tenant admin)

#### Organization Module
- `POST /api/v1/tenants/{tenant_id}/organizations`
- `GET /api/v1/tenants/{tenant_id}/organizations`
- `PATCH /api/v1/tenants/{tenant_id}/organizations/{org_id}`

#### Facility & Asset Module
- `POST /api/v1/organizations/{org_id}/sites`
- `GET /api/v1/organizations/{org_id}/hierarchy`
- `POST /api/v1/organizations/{org_id}/assets`
- `GET /api/v1/organizations/{org_id}/assets`

#### Telemetry Module
- `POST /api/v1/tenants/{tenant_id}/telemetry` (streaming)
- `POST /api/v1/tenants/{tenant_id}/telemetry/batch` (CSV upload)
- `GET /api/v1/tenants/{tenant_id}/telemetry/latest`
- `GET /api/v1/tenants/{tenant_id}/telemetry/history`

#### Metrics Module
- `GET /api/v1/tenants/{tenant_id}/metrics/energy`
- `GET /api/v1/tenants/{tenant_id}/metrics/carbon`
- `GET /api/v1/tenants/{tenant_id}/metrics/kpi`

#### Reports Module
- `POST /api/v1/tenants/{tenant_id}/reports` (create draft)
- `GET /api/v1/tenants/{tenant_id}/reports/{report_id}`
- `PATCH /api/v1/tenants/{tenant_id}/reports/{report_id}` (submit, review, approve)
- `GET /api/v1/tenants/{tenant_id}/reports/{report_id}/export`

#### Evidence Module
- `POST /api/v1/tenants/{tenant_id}/evidence` (upload)
- `GET /api/v1/tenants/{tenant_id}/evidence`
- `PATCH /api/v1/tenants/{tenant_id}/evidence/{evidence_id}` (link metrics)

#### Copilot Module
- `POST /api/v1/tenants/{tenant_id}/copilot/ask`
- `GET /api/v1/tenants/{tenant_id}/copilot/history`

---

### Database Domain List

#### Transactional Domain
- `tenants`, `organizations`, `sites`, `zones`, `racks`, `devices`
- `users`, `roles`, `permissions`
- `factors`, `factor_versions`
- `reports`, `report_versions`
- `workflow_states`, `approvals`

#### Telemetry Domain (TimescaleDB)
- `telemetry_readings` (hypertable)
- `telemetry_anomalies`
- `telemetry_validation_errors`

#### Metrics Domain (TimescaleDB)
- `energy_metrics` (hypertable)
- `carbon_metrics` (hypertable)
- `kpi_snapshots` (hypertable)

#### Evidence Domain
- `evidence`, `evidence_versions`, `evidence_links`

#### Audit Domain
- `audit_logs`, `audit_details`

---

## Implementation Governance

### SPARC Model Execution

Every major module follows this structure:

#### Phase 1: Specify
- **Task**: Write `/docs/implementation/<module>-plan.md`
- **Contents**:
  - Exact scope and dependencies
  - Database schema changes
  - API endpoints and Pydantic schemas
  - UI pages/components and routes
  - Test plan (unit, integration, E2E)
  - Acceptance criteria

#### Phase 2: Plan
- **Task**: Detail all code changes
- **Contents**:
  - File changes (new/modified)
  - Database migrations (reversible)
  - API contract (OpenAPI)
  - Component hierarchy
  - Testing approach
  - Rollback strategy

#### Phase 3: Act
- **Task**: Implement minimal coherent slice
- **Rules**:
  - Write test-first (or at least parallel)
  - One feature per branch
  - Commit messages reference task ID
  - No "WIP" commits to main/develop

#### Phase 4: Review
- **Task**: Validation before merge
- **Checks**:
  - All tests pass (unit, integration, E2E)
  - ESLint, Black, MyPy pass
  - OpenAPI spec valid
  - Manual path testing (happy path + edge cases)
  - Peer code review

#### Phase 5: Close
- **Task**: Write `/docs/implementation/<module>-completion-report.md`
- **Contents**:
  - Scope delivered vs. planned
  - Files added/changed
  - Migrations applied
  - API endpoints added/changed
  - UI routes/components added
  - Tests added and passed
  - Known gaps or deferred work
  - Screenshots or manual verification notes
  - Rollback considerations
  - Deployment checklist

---

## Rules & Standards

### Database Rules

- ✅ Use PostgreSQL migrations (Alembic); no silent schema drift
- ✅ Separate transactional tables from telemetry tables
- ✅ Use TimescaleDB hypertables for high-volume time-series
- ✅ Create version tables for factor changes and reporting snapshots
- ✅ Add audit fields: `created_by`, `created_at`, `modified_by`, `modified_at`, `deleted_at` (soft delete)
- ✅ Use constraints to enforce data integrity (NOT NULL, unique, foreign keys)
- ✅ Index frequently queried columns and foreign keys
- ✅ Document schema with comments (business meaning, units)
- ✅ Test migrations for reversibility (rollback)

### API Rules

- ✅ Versioned endpoints (`/api/v1/`)
- ✅ OpenAPI 3.0 spec must be kept current
- ✅ All request/response payloads use Pydantic models (no `Any` types)
- ✅ Tenant scoping enforced on every read/write
- ✅ Authentication required on all endpoints except `/health`
- ✅ Role-based authorization (RBAC) with explicit permission checks
- ✅ Consistent error response format:
  ```json
  {
    "error": "string",
    "code": "ERROR_CODE",
    "status": 400,
    "details": { "field": ["error message"] }
  }
  ```
- ✅ Pagination on list endpoints (`limit`, `offset`, `total_count`)
- ✅ Rate limiting per user/tenant
- ✅ Idempotent write operations (POST for creation is OK; PUT/PATCH safe)

### Frontend Rules

- ✅ React 18+ with TypeScript (strict mode)
- ✅ Strongly typed API client (code-generated from OpenAPI)
- ✅ Domain-based folder structure (e.g., `/src/domains/facilities/`)
- ✅ Route guards by role (cannot access unauthorized pages)
- ✅ Dashboards must support states: empty, loading, error, data
- ✅ Forms must validate client-side (with server-side fallback)
- ✅ Approval workflow states visible (badge, color-coded)
- ✅ Audit trail viewable (activity log, change history)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Accessibility (WCAG 2.1 AA): semantic HTML, aria labels, keyboard navigation
- ✅ No hardcoded strings (use i18n)

### Agent Rules

- ✅ Agents **never directly overwrite** approved records
- ✅ Agents can create:
  - Draft calculations (awaiting approval)
  - Suggestions (for human review)
  - Flagged incidents (anomalies, compliance gaps)
  - Audit log entries
- ✅ Every agent run must store:
  - `run_id` (unique identifier)
  - `input_context` (what prompted the run)
  - `tools_used` (which integrations were called)
  - `output_summary` (what was calculated/found)
  - `confidence` (0.0-1.0, where applicable)
  - `citations` (IDs of source entities)
  - `requires_approval` (boolean)
- ✅ Approval gating for high-impact agent actions
- ✅ No fabrication of missing data; agents acknowledge gaps
- ✅ Full audit trail of agent reasoning (logged to disk/DB)

### Testing Rules

- ✅ Backend unit tests: >85% line coverage
- ✅ Frontend unit tests: >80% component coverage
- ✅ Integration tests for critical workflows (end-to-end data flow)
- ✅ Database migration tests (verify reversibility)
- ✅ Workflow approval tests (all state transitions)
- ✅ Agent guardrail tests (no data corruption, access control)
- ✅ Smoke tests for main user journeys
- ✅ Performance tests for telemetry ingestion (>1000 readings/sec)
- ✅ Load tests for dashboards (concurrent users, query time <2s)

### Coding Standards

- ✅ Clear, domain-appropriate naming (no `data`, `thing`, `process`)
- ✅ Functions < 50 lines; classes < 200 lines
- ✅ No god modules; split by responsibility
- ✅ Type hints on all function signatures (Python/TypeScript)
- ✅ DTOs and schemas explicit (Pydantic, TypeScript interfaces)
- ✅ Reusable UI components (no copy-paste)
- ✅ Modular service boundaries (services, repositories, use cases)
- ✅ Reversible migrations (never DROP without migration)
- ✅ Immutable value objects where appropriate
- ✅ Dependency injection for testability
- ✅ Error handling explicit (no silent failures)
- ✅ Logging at key decision points and errors
- ✅ Comments explain *why*, not *what* (code explains what)

---

## Testing Requirements

### Test Types & Coverage

| Test Type | Framework | Target Coverage | Responsibility |
|-----------|-----------|-----------------|-----------------|
| **Unit Tests** | pytest (backend), Jest (frontend) | >85% line coverage | Every developer |
| **Integration Tests** | pytest + fixtures | API endpoints, DB integration | Backend team |
| **E2E Tests** | Cypress or Playwright | Critical user journeys | QA + Backend |
| **DB Migration Tests** | pytest + testcontainers | Reversibility, schema correctness | DBA/Backend |
| **Performance Tests** | pytest + Apache JMeter | Telemetry: >1000/sec, Dashboard: <2s | Backend/DevOps |
| **Security Tests** | OWASP ZAP, manual | SQL injection, XSS, CSRF, RBAC bypass | Security engineer |

### Test Execution

- ✅ Run all tests on every commit (pre-commit hook)
- ✅ CI/CD pipeline runs tests on PR (block merge if failing)
- ✅ Coverage reports generated (fail if coverage drops)
- ✅ Performance regressions detected (benchmark comparison)
- ✅ Nightly full test suite + load tests

---

## User Journeys

### 1. Tenant Onboarding
```
Admin → Create Tenant → Assign Admin User → Keycloak enrollment
→ Admin logs in → Organization created → Settings configured
✓ Success: Tenant ready for facility setup
```
**Test**: User can log in, sees empty dashboard, can access settings

### 2. Facility Creation
```
Admin → Create Site → Add Building → Add Zones → Add Racks
→ Save hierarchy → Verify in UI
✓ Success: Facility visible in organization tree
```
**Test**: Hierarchy correctly persisted, audited, accessible via API

### 3. Asset Registration
```
Admin → Add Device (Meter, Server, UPS) → Configure specs (capacity, location)
→ Save asset → Link to rack → Verify in registry
✓ Success: Device appears in energy dashboard (once data ingested)
```
**Test**: Asset metadata persisted, accessible in asset list API

### 4. Telemetry Upload
```
User → Navigate to Telemetry Upload → Upload CSV (timestamp, device_id, kWh)
→ System validates schema → Normalizes units/timestamps → Stores in TimescaleDB
→ Notification: "1000 readings ingested"
✓ Success: Data visible in energy charts within 1 minute
```
**Test**: CSV parsing, validation, unit conversion, stale feed detection

### 5. KPI Calculation
```
System (scheduled) → Fetch latest telemetry → Calculate PUE, CUE, WUE
→ Store KPI snapshot → Trigger Kafka event → Dashboard updates
✓ Success: Dashboard shows latest KPI with trend (no data older than 1 hour)
```
**Test**: KPI formula correctness, snapshot creation, alert triggers

### 6. Emissions Calculation
```
System (triggered by telemetry or monthly) → Carbon Agent queries grid factors
→ Calculates Scope 2 = kWh × factor → Creates calculation record
→ Workflow: Draft → Maker marks ready → Checker reviews → Reviewer approves
✓ Success: Approved emissions in report, audit trail shows all reviews
```
**Test**: Scope 1/2 formulas, factor versioning, workflow state transitions

### 7. Evidence Upload & Linking
```
User → Upload PDF (sustainability certificate) → Tag with metadata (category: audit, facility: site-1)
→ Link to emissions report → Verify link in report UI
✓ Success: Report preview shows evidence reference
```
**Test**: File storage (S3), metadata indexing, link persistence

### 8. Report Draft Generation
```
User → Request report (date range, scope) → System: Aggregate metrics + evidence
→ Generate PDF draft → Present for review → Maker submits
✓ Success: Report shows in "pending review" list
```
**Test**: Report generation, asset availability, approval state

### 9. Approval Workflow Completion
```
Maker: Submits → Checker: Reviews data quality, approves → Reviewer: Signs off
→ Report marked "Approved" → Archived as reference → Cannot edit
✓ Success: Report is immutable reference; any corrections trigger "restatement"
```
**Test**: Permission checks, state transitions, audit trail, immutability

### 10. Copilot Q&A with Citations
```
User → Ask: "What's our Scope 2 emissions this month?"
→ Copilot: Vector search → Retrieve metrics + evidence → LLM response
→ "Based on 50,000 kWh grid consumption (meter: meter-123) and regional factor
  0.4 kg CO₂/kWh, we have 20,000 kg CO₂e."
→ Links to: Report ID, Factor version, Meter readings
✓ Success: Answer cites sources, user can navigate to underlying data
```
**Test**: Citation accuracy, no fabrication (fails gracefully for incomplete data)

---

## Completion Criteria

### A Module is Complete When:

1. **Scope Delivered**
   - All specified requirements in plan are implemented
   - Known gaps are explicitly documented (not hidden)

2. **Code Quality**
   - Passes linting (ESLint, Black, MyPy)
   - >85% unit test coverage
   - All tests pass locally and in CI

3. **Database**
   - Migrations written and tested (including rollback)
   - Schema documented with comments
   - Indexes in place for query performance

4. **API**
   - All endpoints implemented and match OpenAPI spec
   - Pydantic schemas explicit (no `Any` types)
   - Tenant scoping enforced
   - Error responses consistent

5. **Frontend**
   - All pages/components implemented
   - Route guards in place
   - Empty, loading, error, and no-data states supported
   - Approval states visible
   - Responsive design verified

6. **Tests**
   - Unit tests written (>85% coverage)
   - Integration tests for critical paths
   - E2E journey tests passing
   - Performance benchmarks met

7. **Documentation**
   - Module plan completed
   - Completion report signed off
   - Known gaps listed (not hidden)
   - Screenshots provided for UI changes
   - API changes documented in OpenAPI

8. **Verification**
   - Manual testing of main journeys documented
   - Screenshots of happy path + edge cases
   - No broken links or orphaned data
   - Rollback plan documented

9. **Audit**
   - Audit log entries created for material changes
   - Approval states trackable
   - Change history accessible

### Completion Report Template

```markdown
# <Module> - Completion Report

## Scope
- [x] Feature 1
- [x] Feature 2
- [ ] Feature 3 (deferred to phase 2, reason: ...)

## Files Changed
- backend/app/domain/module.py (new)
- backend/tests/test_module.py (new)
- frontend/src/domains/module/ (new)
- migrations/0001_add_module.py (new)
- docs/architecture/module.md (new)

## Migrations
- 0001_add_module (verified reversible)

## API Changes
- POST /api/v1/module (new)
- GET /api/v1/module/{id} (new)
- OpenAPI spec updated: docs/openapi.json

## UI Changes
- src/domains/module/pages/ModuleList.tsx (new)
- src/domains/module/components/ModuleForm.tsx (new)
- Routes guarded by role

## Tests
- Backend unit: 24 tests, 87% coverage
- Integration: 8 tests (critical paths)
- E2E: Journey 1-4 passing
- All CI checks passed

## Known Gaps
- Scope 3 emissions placeholder (phase 2)
- Cooling agent not implemented (phase 3)

## Verification
- [x] Happy path journeys 1-4 work end-to-end
- [x] Rollback tested
- [x] No orphaned data
- [x] Approval workflow verified
- [x] Screenshots attached

## Rollback
- Reverse migration 0001_add_module
- Revert UI changes (git revert)
- No customer data loss
```

---

## Status & Progress Tracking

### Module Implementation Status

| # | Module | Status | Owner | Target Date | Risk |
|---|--------|--------|-------|-------------|------|
| 1 | Auth & Tenant | 🔴 Not Started | Backend | Week 1 | 🟠 Medium |
| 2 | Org & Hierarchy | 🔴 Not Started | Backend | Week 2 | 🟢 Low |
| 3 | Asset Registry | 🔴 Not Started | Backend | Week 3 | 🟢 Low |
| 4 | Telemetry | 🔴 Not Started | Backend | Week 4 | 🟠 Medium |
| 5 | Energy Dashboard | 🔴 Not Started | Frontend | Week 5 | 🟡 Medium |
| 6 | Carbon Engine | 🔴 Not Started | Backend | Week 6 | 🔴 High |
| 7 | KPI Engine | 🔴 Not Started | Backend | Week 7 | 🔴 High |
| 8 | Alerting | 🔴 Not Started | Backend | Week 8 | 🟢 Low |
| 9 | Evidence Repo | 🔴 Not Started | Backend | Week 9 | 🟡 Medium |
| 10 | Workflows | 🔴 Not Started | Backend/Frontend | Week 10 | 🔴 High |
| 11 | Reporting | 🔴 Not Started | Backend/Frontend | Week 11 | 🔴 High |
| 12 | Agent Orch | 🔴 Not Started | Backend | Week 12 | 🔴 High |
| 13 | Copilot | 🔴 Not Started | Backend/ML | Week 13 | 🔴 High |

**Legend**: 🔴 Not Started | 🟠 In Progress | 🟡 Blocked | 🟢 Complete

### Current Cycle Status

**Cycle**: Sprint 1 (Foundation)
**Target**: Auth & Tenant Setup
**Start Date**: March 9, 2026
**End Date**: March 23, 2026
**Owner**: Backend Team
**Status**: 🔴 Not Started

**Deliverables**:
- [ ] Repository discovery report
- [ ] Architecture docs (context, container, domain)
- [ ] Database schema (migrations)
- [ ] API spec (OpenAPI)
- [ ] Auth endpoints (login, logout, refresh)
- [ ] Tenant creation & provisioning
- [ ] Keycloak integration
- [ ] Unit tests (>85% coverage)
- [ ] Integration tests (critical paths)
- [ ] Completion report

---

## Document Updates & Changelog

**Living Document Update Log**:

| Date | Author | Section | Change | Impact |
|------|--------|---------|--------|--------|
| 2026-03-09 | Architecture Team | All | Initial PRD creation from requirements | v1.0.0 |

---

## Contact & Governance

**Product Owner**: [Name]
**Tech Lead**: [Name]
**QA Lead**: [Name]
**Governance Controller**: [Name]

**Meeting Cadence**:
- Daily standup: 9 AM (15 min)
- Weekly review: Friday 2 PM (60 min)
- Architecture sync: Tuesday 10 AM (45 min)
- Approval workflow review: As needed

---

**Document Status**: 📗 **ACTIVE LIVING DOCUMENT**
**Next Review**: March 12, 2026 (during Sprint 1)
**Approval**: Pending architecture review
**Distribution**: Internal team (GitHub wiki)

---

*This PRD will be updated continuously as implementation progresses. Updates will be tracked in the changelog above. Check back regularly for the latest version.*
