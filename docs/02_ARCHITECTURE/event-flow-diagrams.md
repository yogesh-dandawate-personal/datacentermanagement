# Event Flow Diagrams

**Purpose**: Asynchronous event-driven workflows
**Format**: Mermaid Graph Diagrams
**Last Updated**: March 9, 2026

---

## 1. Telemetry Ingestion Event Flow

```mermaid
graph LR
    User["User / API<br/>POST /telemetry"]
    API["FastAPI<br/>Validation"]
    Queue["Kafka Topic:<br/>telemetry.received"]

    TAgent["Telemetry Agent<br/>Validate<br/>Normalize<br/>Detect anomalies"]
    Dashboard["Dashboard Service<br/>Cache update"]
    Anomaly["Anomaly Service<br/>Create alerts"]
    Index["Search Index<br/>Elasticsearch"]

    Storage["TimescaleDB<br/>Store reading"]
    Notification["Notification Service<br/>Send alerts"]

    Audit["Audit Logger<br/>Log ingestion"]

    User -->|HTTP POST| API
    API -->|Valid| Queue

    Queue -->|telemetry.received| TAgent
    Queue -->|telemetry.received| Index

    TAgent -->|normalize| Storage
    TAgent -->|publish: TelemetryValidated| Kafka2["Kafka Topic:<br/>telemetry.validated"]

    Kafka2 -->|metric.updated| Dashboard
    Kafka2 -->|metric.updated| Anomaly

    Storage -->|Confirm| API
    API -->|200 OK| User

    Anomaly -->|anomaly detected| Kafka3["Kafka Topic:<br/>alerts.created"]
    Kafka3 -->|Send email| Notification
    Kafka3 -->|Send Slack| Notification

    API -->|Log event| Audit

    style Queue fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style Kafka3 fill:#fff3e0
```

---

## 2. Carbon Calculation Event Flow

```mermaid
graph LR
    Scheduler["Scheduler<br/>Monthly trigger"]
    CAgent["Carbon Agent<br/>Calculate emissions<br/>Lookup factors<br/>Create draft"]

    Kafka1["Kafka Topic:<br/>metrics.calculated"]
    WFEngine["Workflow Engine<br/>Create approval<br/>Assign checker"]

    Kafka2["Kafka Topic:<br/>workflow.created"]
    Notifier["Notification Service<br/>Email checker<br/>Slack notification"]

    Dashboard["Dashboard Cache<br/>Update PUE/CUE"]
    Indexer["Search Index<br/>Index emissions"]
    Auditor["Audit Logger<br/>Log calculation"]

    Database["PostgreSQL<br/>Store metric<br/>Store approvals"]

    Scheduler -->|Trigger: calc month| CAgent

    CAgent -->|Energy data| Database
    CAgent -->|Lookup factor| Database
    CAgent -->|Create draft metric| Database
    CAgent -->|metric.calculated| Kafka1

    Kafka1 -->|workflow event| WFEngine
    Kafka1 -->|update cache| Dashboard
    Kafka1 -->|index| Indexer

    WFEngine -->|Create workflow| Database
    WFEngine -->|workflow.created| Kafka2

    Kafka2 -->|Send notifications| Notifier
    Notifier -->|Email| User["Checker User"]

    CAgent -->|Log action| Auditor
    WFEngine -->|Log workflow| Auditor

    Database -->|Confirm| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
```

---

## 3. Approval Workflow Event Flow

```mermaid
graph LR
    Maker["Maker<br/>Submit for review"]
    API["API Endpoint<br/>PATCH /report/{id}"]

    Kafka1["Kafka Topic:<br/>workflow.review_requested"]

    WFService["Workflow Service<br/>State: ReadyForReview<br/>Create approval task"]
    Notifier1["Notification Service<br/>Email Checker"]
    Dashboard1["Dashboard<br/>Add to review queue"]

    Checker["Checker<br/>Review & approve"]
    Kafka2["Kafka Topic:<br/>workflow.checked"]

    Reviewer["Reviewer<br/>Final sign-off"]
    Kafka3["Kafka Topic:<br/>workflow.approved"]

    Archiver["Archiver Service<br/>Lock report<br/>Create snapshot"]
    Notifier2["Notification Service<br/>Notify all parties"]

    Auditor["Audit Logger<br/>Log all transitions"]
    Database["Database<br/>Update workflow state"]

    Maker -->|Submit| API
    API -->|State change| Kafka1

    Kafka1 -->|Update state| WFService
    Kafka1 -->|Add task| Dashboard1
    WFService -->|Send email| Notifier1

    Checker -->|Approve| API
    API -->|State change| Kafka2

    Kafka2 -->|Update state| WFService
    Kafka2 -->|Add approval| Archiver

    Reviewer -->|Sign-off| API
    API -->|State change| Kafka3

    Kafka3 -->|Lock| Archiver
    Kafka3 -->|Notify| Notifier2

    Archiver -->|Archive| Database
    Notifier2 -->|Email| Maker

    Kafka1 -->|Log| Auditor
    Kafka2 -->|Log| Auditor
    Kafka3 -->|Log| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style Kafka3 fill:#fff3e0
```

---

## 4. Real-time Dashboard Update Event Flow

```mermaid
graph LR
    TelemetryData["Telemetry Data<br/>Ingested"]

    Kafka1["Kafka Topic:<br/>telemetry.validated"]

    Aggregator["Aggregator Service<br/>Calculate rolling avg<br/>Last 24h data"]

    Cache["Redis Cache<br/>Store: dashboard_{org_id}"]

    Frontend["Frontend<br/>Subscribed to updates"]

    WebSocket["WebSocket<br/>Real-time push<br/>Every 30 sec"]

    Charts["React Charts<br/>Update visuals"]

    Kafka2["Kafka Topic:<br/>dashboard.updated"]

    TelemetryData -->|Store in TSDB| TimescaleDB["TimescaleDB"]
    TimescaleDB -->|New data| Kafka1

    Kafka1 -->|Aggregate| Aggregator
    Aggregator -->|Calc metrics| Cache
    Aggregator -->|Publish| Kafka2

    Cache -->|Query| Aggregator
    Cache -->|TTL: 5 min| Cache

    Frontend -->|Poll/Subscribe| WebSocket
    WebSocket -->|Data update| Charts
    WebSocket -->|Fetch fresh| Cache

    Kafka2 -->|Update| Cache

    style Cache fill:#fce4ec
    style WebSocket fill:#e1f5ff
    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
```

---

## 5. KPI Threshold Alert Event Flow

```mermaid
graph LR
    Scheduler["Scheduler<br/>Hourly trigger"]

    KPIEngine["KPI Engine<br/>Query latest data<br/>Calculate PUE/CUE<br/>Create snapshot"]

    Kafka1["Kafka Topic:<br/>metrics.kpi_updated"]

    AlertService["Alert Service<br/>Check thresholds<br/>Create breach if needed"]

    Kafka2["Kafka Topic:<br/>alerts.threshold_breached"]

    NotifyEmail["Email Service<br/>Send alert"]
    NotifySlack["Slack Service<br/>Post notification"]
    Dashboard["Dashboard<br/>Show alert badge"]

    Database["Database<br/>Store threshold breach"]
    Auditor["Audit Logger<br/>Log alert"]

    Scheduler -->|Execute| KPIEngine
    KPIEngine -->|Query| TimescaleDB["TimescaleDB"]
    KPIEngine -->|Calculate| Database
    KPIEngine -->|Publish| Kafka1

    Kafka1 -->|Check thresholds| AlertService
    AlertService -->|Query threshold config| Database

    AlertService -->|PUE > 1.5| Kafka2

    Kafka2 -->|Send| NotifyEmail
    Kafka2 -->|Send| NotifySlack
    Kafka2 -->|Update UI| Dashboard
    Kafka2 -->|Log| Auditor

    Database -->|Store| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style Dashboard fill:#fce4ec
```

---

## 6. Report Generation Event Flow

```mermaid
graph LR
    Scheduler["Scheduler<br/>End of month"]

    ReportEngine["Report Generator<br/>Aggregate metrics<br/>Gather evidence<br/>Create draft"]

    Kafka1["Kafka Topic:<br/>reports.generated"]

    PDFService["PDF Generator<br/>Create PDF<br/>Upload to S3"]

    Kafka2["Kafka Topic:<br/>reports.ready"]

    WFService["Workflow Service<br/>Create approval<br/>Assign maker"]

    Dashboard["Dashboard<br/>Add to reports"]
    Index["Search Index<br/>Index report"]

    Mailer["Email Service<br/>Notify maker<br/>Report ready"]

    Database["Database<br/>Store report<br/>Store versions"]
    Auditor["Audit Logger"]

    Scheduler -->|Trigger| ReportEngine
    ReportEngine -->|Query| TimescaleDB["TimescaleDB"]
    ReportEngine -->|Fetch| Database
    ReportEngine -->|Publish| Kafka1

    Kafka1 -->|Generate| PDFService
    PDFService -->|Upload| S3["S3 Storage"]
    PDFService -->|Store reference| Database
    PDFService -->|Publish| Kafka2

    Kafka2 -->|Create workflow| WFService
    Kafka2 -->|Update UI| Dashboard
    Kafka2 -->|Index| Index

    WFService -->|Send| Mailer
    Mailer -->|Email| User["Maker User"]

    ReportEngine -->|Log| Auditor
    PDFService -->|Log| Auditor
    WFService -->|Log| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style S3 fill:#fce4ec
```

---

## 7. Evidence Upload & Linking Event Flow

```mermaid
graph LR
    User["User<br/>Upload document"]
    API["API<br/>POST /evidence"]

    Kafka1["Kafka Topic:<br/>evidence.uploaded"]

    FileService["File Service<br/>Upload to S3<br/>Compute hash<br/>Scan for malware"]

    MetadataService["Metadata Service<br/>Create metadata<br/>Tag document<br/>Index content"]

    Kafka2["Kafka Topic:<br/>evidence.indexed"]

    LinkService["Link Service<br/>Create link<br/>Update report reference"]

    Dashboard["Dashboard<br/>Show evidence"]
    Search["Search Index<br/>Full-text search"]

    Database["Database<br/>Store evidence<br/>Store links"]
    Auditor["Audit Logger"]

    User -->|Upload| API
    API -->|Validate| Kafka1

    Kafka1 -->|Upload| FileService
    Kafka1 -->|Extract metadata| MetadataService

    FileService -->|Store in S3| S3["S3 Storage"]
    FileService -->|Scan| Scan["Malware Scanner"]
    FileService -->|Store hash| Database

    MetadataService -->|Index| Database
    MetadataService -->|Publish| Kafka2

    Kafka2 -->|Show| Dashboard
    Kafka2 -->|Index| Search

    User -->|Link to report| LinkService
    LinkService -->|Create link| Database
    LinkService -->|Update| Dashboard

    API -->|Log| Auditor
    FileService -->|Log| Auditor
    MetadataService -->|Log| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style S3 fill:#fce4ec
```

---

## 8. Copilot Query Processing Event Flow

```mermaid
graph LR
    User["User<br/>Ask question"]
    API["API<br/>POST /copilot/ask"]

    Kafka1["Kafka Topic:<br/>copilot.query_received"]

    VectorSearch["Vector Search<br/>Semantic search<br/>Find top-k docs"]

    AccessControl["Access Control<br/>Filter approved only<br/>Check permissions"]

    LLMService["LLM Service<br/>Send to Claude<br/>Generate response<br/>Extract citations"]

    Kafka2["Kafka Topic:<br/>copilot.response_ready"]

    CitationService["Citation Service<br/>Validate sources<br/>Create links<br/>Track provenance"]

    ResponseCache["Response Cache<br/>Store response<br/>TTL: 24h"]

    Database["Database<br/>Store query<br/>Store citations<br/>Store usage"]
    Auditor["Audit Logger<br/>Log query"]

    User -->|Question| API
    API -->|Publish| Kafka1

    Kafka1 -->|Search| VectorSearch
    VectorSearch -->|Query pgvector| Database
    VectorSearch -->|Filter| AccessControl
    AccessControl -->|Approved docs| LLMService

    LLMService -->|API call| Claude["Claude API"]
    Claude -->|Response| LLMService
    LLMService -->|Publish| Kafka2

    Kafka2 -->|Validate| CitationService
    Kafka2 -->|Cache| ResponseCache

    CitationService -->|Store| Database
    CitationService -->|Log| Auditor

    LLMService -->|Log| Auditor
    ResponseCache -->|Return| API
    API -->|Response with citations| User

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style Claude fill:#f3e5f5
```

---

## 9. Agent Orchestration Event Flow

```mermaid
graph LR
    Trigger["Trigger<br/>Scheduled/Manual"]

    Orchestrator["Agent Orchestrator<br/>Determine agents<br/>Get prerequisites<br/>Sequence execution"]

    Kafka1["Kafka Topic:<br/>agents.execute"]

    AgentWorkers["Agent Workers<br/>Consume jobs<br/>Execute agents<br/>Produce results"]

    Kafka2["Kafka Topic:<br/>agents.completed"]

    PostProcessor["Post-Processor<br/>Validate results<br/>Store outputs<br/>Link citations"]

    Database["Database<br/>Store agent runs<br/>Store results<br/>Store citations"]

    Notification["Notification<br/>Alert if needed<br/>Log completion"]

    Auditor["Audit Logger<br/>Log execution"]

    Trigger -->|Start| Orchestrator
    Orchestrator -->|Check prerequisites| Database
    Orchestrator -->|Sequence agents| Kafka1

    Kafka1 -->|Telemetry Agent| AgentWorkers
    Kafka1 -->|Carbon Agent| AgentWorkers
    Kafka1 -->|Compliance Agent| AgentWorkers

    AgentWorkers -->|Results| Kafka2

    Kafka2 -->|Aggregate| PostProcessor
    PostProcessor -->|Validate| Database
    PostProcessor -->|Store| Database

    Database -->|Confirm| Notification
    Notification -->|Log| Auditor

    Orchestrator -->|Log start| Auditor
    AgentWorkers -->|Log execution| Auditor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style Database fill:#fff3e0
```

---

## 10. Data Archival & Cleanup Event Flow

```mermaid
graph LR
    Scheduler["Scheduler<br/>Daily/Weekly"]

    Archiver["Archiver Service<br/>Identify stale data<br/>Apply retention<br/>Compress"]

    Kafka1["Kafka Topic:<br/>archival.started"]

    Compressor["Compression Service<br/>Compress old telemetry<br/>Archive cold data<br/>Update indexes"]

    Deleter["Deletion Service<br/>Soft delete expired<br/>Purge audit logs<br/>Clean temp files"]

    Kafka2["Kafka Topic:<br/>archival.completed"]

    Auditor["Audit Logger<br/>Log archival"]
    Monitor["Monitoring<br/>Alert on space<br/>Track retention"]

    Database["Database<br/>Compressed tables<br/>Retention flags"]
    S3["S3 Storage<br/>Archive bucket<br/>Versioned"]

    Scheduler -->|Execute| Archiver
    Archiver -->|Query age| Database
    Archiver -->|Publish| Kafka1

    Kafka1 -->|Compress| Compressor
    Kafka1 -->|Delete| Deleter

    Compressor -->|Compress TS| TimescaleDB["TimescaleDB"]
    Compressor -->|Archive to S3| S3
    Compressor -->|Update policy| Database

    Deleter -->|Soft delete| Database
    Deleter -->|Purge logs| Database

    Compressor -->|Publish| Kafka2
    Deleter -->|Publish| Kafka2

    Kafka2 -->|Log| Auditor
    Kafka2 -->|Alert| Monitor

    style Kafka1 fill:#fff3e0
    style Kafka2 fill:#fff3e0
    style S3 fill:#fce4ec
```

---

## Event Topic Reference

| Topic | Producer | Consumers | Schema |
|-------|----------|-----------|--------|
| `telemetry.received` | API Ingestion | Validation, Indexing | {reading_id, meter_id, value, timestamp} |
| `telemetry.validated` | Telemetry Agent | Dashboard, Anomaly Detection | {reading_id, status, validation_result} |
| `metrics.calculated` | Carbon Agent | Workflow, Dashboard, Indexing | {metric_id, metric_type, value, status} |
| `metrics.kpi_updated` | KPI Engine | Dashboard, Alerting, Indexing | {kpi_id, value, snapshot_date} |
| `alerts.threshold_breached` | Alert Service | Email, Slack, Dashboard | {alert_id, metric_id, threshold, breach_value} |
| `reports.generated` | Report Generator | Workflow, S3, Indexing | {report_id, period, status} |
| `workflow.review_requested` | API | Notification, Dashboard | {entity_id, entity_type, stage} |
| `workflow.checked` | Workflow Service | Notification, Archiving | {entity_id, checker_id, decision} |
| `workflow.approved` | Workflow Service | Notification, Archiver | {entity_id, reviewer_id, signature} |
| `evidence.uploaded` | API | File Service, Metadata Service | {evidence_id, file_name, file_hash} |
| `evidence.indexed` | Metadata Service | Dashboard, Search | {evidence_id, metadata} |
| `copilot.query_received` | API | Vector Search, Citation | {query_id, question, user_id} |
| `copilot.response_ready` | LLM Service | Citation Service, Cache | {query_id, response, citations} |
| `agents.execute` | Orchestrator | Agent Workers | {run_id, agent_type, input_data} |
| `agents.completed` | Agent Workers | Post-Processor | {run_id, status, output_data} |

---

**Navigation**: [Back to Index](./INDEX.md)
