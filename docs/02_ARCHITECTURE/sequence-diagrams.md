# Sequence Diagrams

**Purpose**: Interactions and flows for critical user journeys
**Format**: Mermaid Sequence Diagrams
**Last Updated**: March 9, 2026

---

## 1. Telemetry Ingestion Sequence

```mermaid
sequenceDiagram
    Actor User
    participant API as FastAPI<br/>REST API
    participant TAgent as Telemetry<br/>Agent
    participant Kafka as Kafka<br/>Bus
    participant TSDB as TimescaleDB<br/>Telemetry
    participant AuditLog as Audit<br/>Logger

    User->>API: POST /api/v1/telemetry<br/>{meter_id, value, timestamp}
    API->>API: Validate Tenant Scoping
    API->>API: Validate JWT Token
    API->>TAgent: Process Telemetry
    TAgent->>TAgent: Normalize Units
    TAgent->>TAgent: Convert Timestamps to UTC
    TAgent->>TAgent: Check for Anomalies
    TAgent->>TSDB: Store Reading
    TSDB-->>TAgent: Confirmation
    TAgent->>Kafka: Emit TelemetryReceived Event
    TAgent->>AuditLog: Log Ingestion
    Kafka->>Kafka: Route Event
    API-->>User: 200 OK {reading_id}

    Note over Kafka: Event triggers:<br/>Carbon Agent<br/>Dashboard Update<br/>Anomaly Detection
```

---

## 2. Carbon Calculation Workflow

```mermaid
sequenceDiagram
    participant Scheduler as Scheduled<br/>Trigger
    participant CAgent as Carbon<br/>Agent
    participant TSDB as TimescaleDB<br/>Energy Data
    participant FactorDB as Factor<br/>Repository
    participant MetricDB as Metrics<br/>Database
    participant Kafka as Kafka<br/>Bus
    participant Workflow as Workflow<br/>Engine

    Scheduler->>CAgent: Calculate Monthly Scope 2
    CAgent->>TSDB: Query Energy (kWh) for Period
    TSDB-->>CAgent: {total_kwh: 50000}
    CAgent->>FactorDB: Get Grid Factor<br/>(region, date)
    FactorDB-->>CAgent: {factor: 0.4 kg CO2/kWh<br/>version: v3}
    CAgent->>CAgent: Calculate:<br/>Scope2 = 50000 * 0.4<br/>= 20000 kg CO2e
    CAgent->>MetricDB: Create Carbon Metric<br/>{status: draft}
    MetricDB-->>CAgent: {metric_id: UUID}
    CAgent->>Kafka: Emit CarbonCalculated Event
    Kafka->>Workflow: Route to Approval Engine
    Workflow->>Workflow: Create Workflow State<br/>(Draft → ReadyForReview)
    Note over Kafka: Notification sent to<br/>Checker Role

    Workflow-->>CAgent: Workflow Created
```

---

## 3. Approval Workflow Sequence

```mermaid
sequenceDiagram
    Actor Maker as Maker<br/>(Data Entry)
    Actor Checker as Checker<br/>(Validator)
    Actor Reviewer as Reviewer<br/>(Approver)
    participant API as FastAPI<br/>API
    participant WFEngine as Workflow<br/>Engine
    participant DB as PostgreSQL<br/>Database
    participant Kafka as Kafka<br/>Notifications
    participant AuditLog as Audit<br/>Trail

    Maker->>API: PATCH /report/{id}<br/>{submit_for_review: true}
    API->>WFEngine: Change State
    WFEngine->>DB: Update WorkflowState<br/>Draft → ReadyForReview
    WFEngine->>Kafka: Emit ReviewRequested
    Kafka->>Checker: Notification: Review Required
    AuditLog->>AuditLog: Log State Change

    Checker->>API: GET /report/{id}/details
    API-->>Checker: Report Data + Validation
    Checker->>API: PATCH /approval/{id}<br/>{decision: approved, comments}
    API->>WFEngine: Process Approval
    WFEngine->>DB: Update Approval Status
    WFEngine->>DB: Update WorkflowState<br/>ReadyForReview → Checked
    WFEngine->>Kafka: Emit CheckerApproved
    Kafka->>Reviewer: Notification: Ready for Sign-Off

    Reviewer->>API: GET /report/{id}
    API-->>Reviewer: Full Report
    Reviewer->>API: PATCH /approval/{id}<br/>{decision: approved, signature}
    API->>WFEngine: Final Approval
    WFEngine->>DB: Update WorkflowState<br/>Checked → Approved
    WFEngine->>DB: Archive Report Version<br/>{status: approved, immutable: true}
    WFEngine->>Kafka: Emit ReportApproved
    AuditLog->>AuditLog: Log Final Approval

    Kafka->>Maker: Notification: Approved
```

---

## 4. Dashboard Data Loading (Real-time)

```mermaid
sequenceDiagram
    Actor User
    participant FrontEnd as React<br/>Dashboard
    participant API as FastAPI<br/>REST API
    participant Cache as Redis<br/>Cache
    participant TSDB as TimescaleDB

    User->>FrontEnd: Load Dashboard
    FrontEnd->>API: GET /api/v1/dashboards/{org_id}
    API->>Cache: Check Cache (key: dash_org_{id})
    alt Cache Hit
        Cache-->>API: {cached_data}
        API-->>FrontEnd: 200 OK {data}
    else Cache Miss
        API->>TSDB: Query Latest Metrics
        API->>TSDB: Aggregate Energy (last 24h)
        API->>TSDB: Calculate KPIs
        TSDB-->>API: {energy, kpi_data}
        API->>Cache: Set Cache (TTL: 5 min)
        API-->>FrontEnd: 200 OK {data}
    end
    FrontEnd->>FrontEnd: Render Charts
    FrontEnd->>FrontEnd: Set Auto-refresh (30s)

    Note over FrontEnd: Every 30 seconds
    loop Auto-Refresh
        FrontEnd->>API: GET /api/v1/metrics/latest
        API-->>FrontEnd: Latest Data
        FrontEnd->>FrontEnd: Update Charts
    end
```

---

## 5. Copilot Query Resolution

```mermaid
sequenceDiagram
    Actor User
    participant Frontend as React<br/>Chat UI
    participant API as FastAPI<br/>API
    participant VSearch as Vector<br/>Search (pgvector)
    participant LLM as Claude<br/>API
    participant AuditLog as Audit<br/>Logger

    User->>Frontend: Ask: "What's Scope 2<br/>emissions this month?"
    Frontend->>API: POST /copilot/ask<br/>{question, tenant_id}
    API->>API: Verify User Auth &<br/>Tenant Scoping
    API->>VSearch: Semantic Search<br/>for relevant documents
    VSearch-->>API: Top 10 Results<br/>(reports, metrics, evidence)
    API->>API: Filter by User Access<br/>(approved only)
    API->>LLM: Generate Response<br/>with context + citations
    LLM-->>API: Response + Sources
    API->>API: Format Citations<br/>(entity IDs, links)
    API->>AuditLog: Log Query
    API-->>Frontend: {response, citations}
    Frontend->>Frontend: Render with Links
    Frontend->>Frontend: Highlight Citations
    User->>Frontend: Click Citation
    Frontend->>API: GET /metrics/{metric_id}
    API-->>Frontend: Metric Details
```

---

## 6. Evidence Upload & Linking

```mermaid
sequenceDiagram
    Actor User
    participant Frontend as React<br/>UI
    participant API as FastAPI<br/>API
    participant S3 as S3 / MinIO<br/>Storage
    participant DB as PostgreSQL<br/>Database
    participant Kafka as Kafka<br/>Bus

    User->>Frontend: Upload File (PDF)
    Frontend->>API: Multipart POST<br/>/evidence/upload
    API->>API: Validate File<br/>(type, size, hash)
    API->>S3: Upload File<br/>with tenant prefix
    S3-->>API: {s3_key, etag}
    API->>DB: Create Evidence Record<br/>{tenant_id, file_hash}
    DB-->>API: {evidence_id}
    User->>Frontend: Tag Evidence<br/>(category: audit)
    User->>Frontend: Link to Report
    Frontend->>API: PATCH /evidence/{id}<br/>{links: [{type: report, id}]}
    API->>DB: Create EvidenceLink
    API->>Kafka: Emit EvidenceLinked
    Kafka->>API: Trigger Report Update
    API-->>Frontend: 200 OK
```

---

## 7. Facility Hierarchy Creation

```mermaid
sequenceDiagram
    Actor Admin
    participant Frontend as React<br/>UI
    participant API as FastAPI<br/>API
    participant DB as PostgreSQL<br/>Database
    participant AuditLog as Audit<br/>Trail

    Admin->>Frontend: Create Site
    Frontend->>API: POST /sites<br/>{org_id, name, location}
    API->>DB: Insert Site Record
    DB-->>API: {site_id}
    API->>AuditLog: Log Creation
    API-->>Frontend: {site_id}

    Admin->>Frontend: Create Building
    Frontend->>API: POST /buildings<br/>{site_id, name, floors}
    API->>DB: Insert Building
    DB-->>API: {building_id}
    API->>AuditLog: Log Creation

    Admin->>Frontend: Create Zones
    loop For Each Zone
        Frontend->>API: POST /zones<br/>{building_id, name}
        API->>DB: Insert Zone
        API->>AuditLog: Log Creation
    end

    Admin->>Frontend: Create Racks
    loop For Each Rack
        Frontend->>API: POST /racks<br/>{zone_id, rack_id}
        API->>DB: Insert Rack
        API->>AuditLog: Log Creation
    end

    Frontend->>Frontend: Show Hierarchy Tree
```

---

## 8. KPI Threshold Alert

```mermaid
sequenceDiagram
    participant Scheduler as Scheduled<br/>Task
    participant Engine as KPI<br/>Engine
    participant TSDB as TimescaleDB
    participant AlertService as Alert<br/>Service
    participant Kafka as Kafka<br/>Bus
    participant Email as Email<br/>Service

    Scheduler->>Engine: Calculate KPIs (hourly)
    Engine->>TSDB: Query Latest Metrics
    TSDB-->>Engine: {pue: 1.8, target: 1.2}
    Engine->>Engine: Check Thresholds<br/>1.8 > 1.5 (alert threshold)
    Engine->>AlertService: Create Alert<br/>{severity: high, metric: PUE}
    AlertService->>TSDB: Store Threshold Breach
    AlertService->>Kafka: Emit ThresholdBreached
    Kafka->>Email: Route Alert Notification
    Email->>Email: Build Alert Message
    Email->>Email: Send to Org Admins
    Note over Email: Alert also visible<br/>in Dashboard
```

---

## 9. Token Refresh & Auth Flow

```mermaid
sequenceDiagram
    Actor User
    participant Frontend as React<br/>App
    participant API as FastAPI<br/>API
    participant Keycloak as Keycloak<br/>Server
    participant TokenDB as Token<br/>Cache (Redis)

    User->>Frontend: Log In
    Frontend->>Keycloak: POST /auth/realms/{realm}/protocol/openid-connect/token<br/>{username, password}
    Keycloak-->>Frontend: {access_token, refresh_token}
    Frontend->>Frontend: Store Tokens<br/>(LocalStorage)
    Frontend->>API: GET /api/v1/auth/me<br/>Header: Authorization: Bearer {token}
    API->>API: Extract & Validate Token
    API-->>Frontend: {user_id, roles, permissions}

    Note over Frontend: Token expires in 15 min
    Frontend->>Frontend: Token Check<br/>(on each request)
    alt Token Valid
        Frontend->>API: Normal Request
    else Token Expired
        Frontend->>Keycloak: POST /token<br/>{refresh_token}
        Keycloak-->>Frontend: {new_access_token}
        Frontend->>Frontend: Update Token
        Frontend->>API: Retry Request
    end
```

---

## 10. Metrics Aggregation & Reporting

```mermaid
sequenceDiagram
    participant Scheduler as Monthly<br/>Scheduler
    participant Aggregator as Metrics<br/>Aggregator
    participant TSDB as TimescaleDB
    participant ReportEngine as Report<br/>Generator
    participant S3 as S3<br/>Storage
    participant DB as PostgreSQL

    Scheduler->>Aggregator: Generate Monthly Report
    Aggregator->>TSDB: Query Energy Data<br/>(month range)
    TSDB-->>Aggregator: Hourly readings
    Aggregator->>Aggregator: Aggregate Daily Values
    Aggregator->>TSDB: Query Carbon Data
    TSDB-->>Aggregator: Daily emissions
    Aggregator->>TSDB: Query KPI Snapshots
    TSDB-->>Aggregator: KPI trends

    Aggregator->>ReportEngine: Generate Report<br/>{data, format: PDF}
    ReportEngine->>ReportEngine: Build PDF<br/>(charts, tables)
    ReportEngine->>S3: Upload PDF
    S3-->>ReportEngine: {s3_key}
    ReportEngine->>DB: Create Report Record<br/>{status: draft}
    DB-->>ReportEngine: {report_id}
    ReportEngine-->>Aggregator: {report_id, s3_key}
    Note over DB: Report ready for review
```

---

## Interaction Patterns

### Request/Response Pattern
```
Client Request
  ├── Authentication (JWT)
  ├── Tenant Scoping Validation
  ├── Authorization (RBAC)
  ├── Request Validation (Pydantic)
  └── Business Logic
        └── Database Operations
              └── Audit Logging
                    └── Event Emission (Kafka)
                          └── Notification Dispatch
Server Response (JSON with status, data, errors)
```

### Async Event Pattern
```
Synchronous Trigger (API, Scheduled)
  └── Emit Event to Kafka
        ├── Service A subscribes
        ├── Service B subscribes
        └── Service C subscribes
              └── Each processes independently
                    └── Maintains own state
```

### State Machine Pattern
```
Current State + Action
  └── Validate Transition
        └── Apply Side Effects
              └── Emit Events
                    └── Update State
                          └── Audit Log Entry
```

---

**Navigation**: [Back to Index](./INDEX.md)
