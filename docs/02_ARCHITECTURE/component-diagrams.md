# Component Diagrams

**Purpose**: System components and service architecture
**Format**: Mermaid Component Diagrams
**Last Updated**: March 9, 2026

---

## 1. Backend Service Components

```mermaid
graph TB
    subgraph API["API Layer (FastAPI)"]
        AuthAPI["Authentication API<br/>POST /auth/login<br/>POST /auth/refresh<br/>GET /auth/me"]
        TenantAPI["Tenant API<br/>POST /tenants<br/>GET /tenants/{id}<br/>PATCH /tenants/{id}"]
        OrgAPI["Organization API<br/>CRUD operations<br/>Settings management"]
        FacilityAPI["Facility API<br/>Site/Building/Zone/Rack<br/>Hierarchy operations"]
        AssetAPI["Asset Registry API<br/>Device management<br/>Specifications"]
        TelemetryAPI["Telemetry API<br/>POST /telemetry<br/>POST /telemetry/batch<br/>GET /telemetry/history"]
        MetricsAPI["Metrics API<br/>GET /metrics/energy<br/>GET /metrics/carbon<br/>GET /metrics/kpi"]
        ReportAPI["Report API<br/>CRUD reports<br/>Version management<br/>Export formats"]
        EvidenceAPI["Evidence API<br/>Upload/link<br/>Search/retrieve<br/>Retention mgmt"]
        WorkflowAPI["Workflow API<br/>Submit for review<br/>Approve/reject<br/>View history"]
        CopilotAPI["Copilot API<br/>POST /ask<br/>GET /history<br/>Citations"]
    end

    subgraph Services["Service Layer"]
        AuthService["Authentication Service<br/>Keycloak integration<br/>JWT validation<br/>Token refresh"]
        TenantService["Tenant Service<br/>Provisioning<br/>Isolation enforcement<br/>Settings mgmt"]
        OrgService["Organization Service<br/>Hierarchy creation<br/>Settings updates<br/>Reporting config"]
        FacilityService["Facility Service<br/>Hierarchy validation<br/>Asset tree mgmt<br/>Queries"]
        TelemetryService["Telemetry Service<br/>Schema validation<br/>Unit conversion<br/>Anomaly detection"]
        MetricsService["Metrics Service<br/>Energy aggregation<br/>Carbon calculation<br/>KPI snapshots"]
        ReportService["Report Service<br/>Generation<br/>Versioning<br/>Export formatting"]
        EvidenceService["Evidence Service<br/>File management<br/>Metadata tagging<br/>Search indexing"]
        WorkflowService["Workflow Service<br/>State transitions<br/>Approval logic<br/>Notifications"]
        CopilotService["Copilot Service<br/>Vector search<br/>LLM integration<br/>Citation tracking"]
    end

    subgraph Agents["Agent Components"]
        TelemetryAgent["Telemetry Agent<br/>Validates & normalizes<br/>Flags anomalies<br/>Ingests batch"]
        CarbonAgent["Carbon Agent<br/>Calculates Scope1/2<br/>Factor management<br/>Draft emissions"]
        ComplianceAgent["Compliance Agent<br/>Gap analysis<br/>Requirement validation<br/>Evidence mapping"]
        EvidenceAgent["Evidence Agent<br/>Metadata mgmt<br/>Link tracking<br/>Retention schedule"]
        CopilotAgent["Copilot Agent<br/>Query processing<br/>Source retrieval<br/>Response gen"]
    end

    subgraph DataAccess["Data Access Layer"]
        Repositories["Repositories<br/>TenantRepository<br/>UserRepository<br/>MetricRepository<br/>ReportRepository<br/>etc..."]
        ORM["SQLAlchemy ORM<br/>Models & relationships<br/>Query builder<br/>Transaction mgmt"]
    end

    subgraph Middleware["Middleware Stack"]
        TenantMiddleware["Tenant Middleware<br/>Extract tenant ID<br/>Enforce scoping<br/>Validation"]
        AuthMiddleware["Auth Middleware<br/>JWT extraction<br/>Token validation<br/>Role check"]
        ErrorHandler["Error Handler<br/>Exception catching<br/>Response formatting<br/>Logging"]
        RequestLogger["Request Logger<br/>Audit trail<br/>Performance metrics<br/>Error tracking"]
    end

    subgraph External["External Services"]
        Keycloak["Keycloak Server<br/>OAuth2/OIDC<br/>User management<br/>SSO"]
        Kafka["Kafka/Redpanda<br/>Event streaming<br/>Topic management<br/>Consumer groups"]
        Celery["Celery Worker<br/>Async tasks<br/>Scheduled jobs<br/>Queue management"]
        S3["S3 / MinIO<br/>File storage<br/>Object mgmt<br/>Lifecycle"]
        LLM["Claude API<br/>Text generation<br/>Embeddings<br/>Token counting"]
    end

    API -->|Call| Services
    Services -->|Use| Agents
    Services -->|Query| DataAccess
    API -->|Route through| Middleware
    Services -->|Emit events| Kafka
    Services -->|Submit tasks| Celery
    Services -->|Upload/Download| S3
    AuthService -->|Auth| Keycloak
    CopilotAgent -->|Generate| LLM
    TelemetryAgent -->|Validate| TelemetryService
    MetricsService -->|Use| Repositories
    ReportService -->|Use| Repositories

    style API fill:#e1f5ff
    style Services fill:#f3e5f5
    style Agents fill:#e8f5e9
    style DataAccess fill:#fff3e0
    style Middleware fill:#fce4ec
    style External fill:#f1f8e9
```

---

## 2. Frontend Component Architecture

```mermaid
graph TB
    subgraph App["React Application"]
        Router["React Router<br/>Route definitions<br/>Navigation<br/>Guards"]

        subgraph Pages["Pages/Features"]
            Dashboard["Dashboard Page<br/>Energy charts<br/>KPI status<br/>Quick actions"]
            TelemetryPages["Telemetry Pages<br/>Upload form<br/>History view<br/>Validation status"]
            FacilityPages["Facility Pages<br/>Hierarchy tree<br/>Asset registry<br/>Specifications"]
            MetricsPages["Metrics Pages<br/>Energy dashboard<br/>Carbon summary<br/>KPI tracking"]
            ReportPages["Report Pages<br/>Draft creation<br/>Review queue<br/>Approved reports"]
            EvidencePages["Evidence Pages<br/>Document library<br/>Search/filter<br/>Linking"]
            WorkflowPages["Workflow Pages<br/>Approval tasks<br/>Comments<br/>History"]
            AdminPages["Admin Pages<br/>Settings<br/>User management<br/>Configuration"]
            CopilotPages["Copilot Page<br/>Chat interface<br/>Query history<br/>Citations"]
        end

        subgraph Components["Shared Components"]
            Form["Form Components<br/>TextInput<br/>Select<br/>DatePicker<br/>FileUpload"]
            Table["Table Components<br/>DataTable<br/>Pagination<br/>Sorting<br/>Filtering"]
            Chart["Chart Components<br/>LineChart<br/>BarChart<br/>PieChart<br/>using Recharts"]
            Modal["Modal Components<br/>Dialog<br/>Confirmation<br/>Wizard"]
            Notification["Notification<br/>Toast messages<br/>Alerts<br/>Loading"]
            Layout["Layout Components<br/>Header<br/>Sidebar<br/>Navigation"]
        end

        subgraph State["State Management"]
            Redux["Redux Store<br/>Auth slice<br/>Tenant slice<br/>Metrics slice<br/>Report slice<br/>UI slice"]
            Hooks["Custom Hooks<br/>useAuth<br/>useTenant<br/>useMetrics<br/>useForm"]
        end

        subgraph Client["API Client"]
            APIClient["Axios Instance<br/>Base config<br/>Interceptors<br/>Error handling"]
            CodeGen["Generated Types<br/>OpenAPI spec<br/>TypeScript<br/>Schemas"]
        end

        subgraph Utils["Utilities"]
            Auth["Auth Utilities<br/>Token mgmt<br/>Role check<br/>Permission eval"]
            Format["Formatting<br/>Number format<br/>Date format<br/>Units"]
            Validation["Validation<br/>Form validation<br/>Input checking<br/>Constraints"]
        end
    end

    subgraph Runtime["Runtime Environment"]
        Browser["Browser<br/>JavaScript Engine<br/>LocalStorage<br/>SessionStorage"]
    end

    Router -->|Routes to| Pages
    Pages -->|Use| Components
    Pages -->|Dispatch| Redux
    Redux -->|Store state| State
    Components -->|Call| APIClient
    APIClient -->|Typed with| CodeGen
    APIClient -->|Calls| AuthService
    Pages -->|Use| Hooks
    Hooks -->|Access| Redux
    Components -->|Use| Utils
    Redux -->|Execute| Auth

    style App fill:#e3f2fd
    style Pages fill:#f3e5f5
    style Components fill:#e8f5e9
    style State fill:#fff3e0
    style Client fill:#fce4ec
    style Utils fill:#f1f8e9
    style Runtime fill:#ede7f6
```

---

## 3. Data Processing Pipeline Components

```mermaid
graph LR
    subgraph Input["Input Layer"]
        API["REST API<br/>/telemetry"]
        CSV["CSV Upload<br/>Batch import"]
        Stream["IoT Stream<br/>Real-time metrics"]
    end

    subgraph Processing["Processing Layer"]
        Validate["Validation<br/>Schema check<br/>Type conversion<br/>Range check"]
        Normalize["Normalization<br/>Unit conversion<br/>Timezone handling<br/>Deduplication"]
        Enrich["Enrichment<br/>Add metadata<br/>Link devices<br/>Map facilities"]
        Detect["Anomaly Detection<br/>Outlier check<br/>Freshness check<br/>Threshold check"]
    end

    subgraph Storage["Storage Layer"]
        TSDB["TimescaleDB<br/>Hypertables<br/>Compression<br/>Retention policy"]
    end

    subgraph Calculation["Calculation Layer"]
        Energy["Energy Aggregation<br/>Total consumption<br/>By facility<br/>By device"]
        Carbon["Carbon Calculation<br/>Scope 1/2<br/>Factor application<br/>Versioning"]
        KPI["KPI Calculation<br/>PUE, CUE, WUE<br/>Custom formulas<br/>Snapshots"]
    end

    subgraph Distribution["Distribution Layer"]
        Dashboard["Dashboard Update<br/>Pub/Sub cache<br/>WebSocket push"]
        Report["Report Generation<br/>Data aggregation<br/>PDF/JSON export"]
        Alert["Alerting System<br/>Threshold check<br/>Notification dispatch"]
    end

    Input -->|Stream| Validate
    Validate -->|Valid| Normalize
    Normalize -->|Normalized| Enrich
    Enrich -->|Ready| Detect
    Detect -->|Stored| TSDB
    TSDB -->|Query| Energy
    TSDB -->|Query| Carbon
    TSDB -->|Query| KPI
    Energy -->|Publish| Dashboard
    Carbon -->|Publish| Report
    KPI -->|Check| Alert
    Alert -->|Notify| Distribution

    style Input fill:#e1f5ff
    style Processing fill:#f3e5f5
    style Storage fill:#fff3e0
    style Calculation fill:#e8f5e9
    style Distribution fill:#fce4ec
```

---

## 4. Event-Driven Architecture Components

```mermaid
graph TB
    subgraph Producers["Event Producers"]
        TelemetryIngest["Telemetry Ingestion<br/>Emits: TelemetryReceived"]
        MetricsCalc["Metrics Calculation<br/>Emits: MetricsCalculated"]
        ReportWorkflow["Report Workflow<br/>Emits: ReportSubmitted<br/>Emits: ReportApproved"]
        AgentExecution["Agent Execution<br/>Emits: AgentCompleted"]
        UserAction["User Actions<br/>Emits: UserApprovedReport"]
    end

    subgraph EventBus["Kafka Event Bus"]
        TelemetryTopic["Topic: telemetry.events<br/>- TelemetryReceived<br/>- TelemetryValidated<br/>- TelemetryAnomaly"]
        MetricsTopic["Topic: metrics.events<br/>- EnergyCalculated<br/>- CarbonCalculated<br/>- KPIUpdated"]
        WorkflowTopic["Topic: workflow.events<br/>- ReviewRequested<br/>- ApprovalRequested<br/>- StateChanged"]
        NotificationTopic["Topic: notifications.events<br/>- AlertTriggered<br/>- CommentAdded"]
    end

    subgraph Consumers["Event Consumers"]
        Dashboard["Dashboard Service<br/>Listens: metrics.events<br/>Updates: Cache"]
        Notifications["Notification Service<br/>Listens: workflow.events<br/>Sends: Email/Slack"]
        Alerts["Alert Service<br/>Listens: metrics.events<br/>Checks: Thresholds"]
        Indexing["Search Indexing<br/>Listens: all events<br/>Updates: Elasticsearch"]
        Reporting["Reporting Service<br/>Listens: metrics.events<br/>Triggers: Reports"]
    end

    subgraph Cache["Cache Layer"]
        Redis["Redis Cache<br/>Dashboard snapshots<br/>User sessions<br/>Rate limits"]
    end

    Producers -->|Emit| EventBus
    TelemetryIngest -->|TelemetryReceived| TelemetryTopic
    MetricsCalc -->|MetricsCalculated| MetricsTopic
    ReportWorkflow -->|WorkflowEvent| WorkflowTopic
    AgentExecution -->|AgentCompleted| MetricsTopic
    UserAction -->|UserApproved| WorkflowTopic

    TelemetryTopic -->|Subscribe| Alerts
    MetricsTopic -->|Subscribe| Dashboard
    MetricsTopic -->|Subscribe| Reporting
    MetricsTopic -->|Subscribe| Indexing
    WorkflowTopic -->|Subscribe| Notifications
    WorkflowTopic -->|Subscribe| Indexing

    Dashboard -->|Cache| Redis
    Notifications -->|Read| Redis
    Alerts -->|Cache| Redis

    style Producers fill:#e1f5ff
    style EventBus fill:#fff3e0
    style Consumers fill:#e8f5e9
    style Cache fill:#fce4ec
```

---

## 5. Integration & External Services Components

```mermaid
graph TB
    subgraph Platform["iNetZero Platform"]
        API["FastAPI Backend<br/>Core services<br/>APIs"]
        Database["PostgreSQL<br/>+ TimescaleDB<br/>Primary data store"]
        Cache["Redis<br/>Session cache<br/>Rate limits"]
    end

    subgraph AuthServices["Authentication"]
        Keycloak["Keycloak Server<br/>User management<br/>OAuth2/OIDC<br/>SSO"]
        LDAP["LDAP/Active Directory<br/>Enterprise integration<br/>Optional"]
    end

    subgraph DataSources["Data Sources"]
        BMS["BMS Systems<br/>Building Management<br/>HVAC, lighting<br/>Energy data"]
        DCIM["DCIM Software<br/>Data center inventory<br/>Asset tracking"]
        Meters["IoT Meters<br/>Energy meters<br/>Water meters<br/>Temperature sensors"]
        Weather["Weather APIs<br/>Regional data<br/>Cooling factors"]
    end

    subgraph Storage["Object Storage"]
        S3["AWS S3 / MinIO<br/>Reports<br/>Evidence docs<br/>Backups"]
    end

    subgraph Messaging["Messaging & Events"]
        Kafka["Kafka Cluster<br/>Event streaming<br/>Real-time updates<br/>Microservices comm"]
        Celery["Celery/Redis<br/>Async tasks<br/>Scheduled jobs<br/>Background workers"]
    end

    subgraph Analytics["Analytics & Monitoring"]
        OTel["OpenTelemetry<br/>Metrics export<br/>Trace collection<br/>Log aggregation"]
        Prometheus["Prometheus<br/>Metrics storage<br/>Alerting rules"]
        Grafana["Grafana<br/>Dashboards<br/>Visualization<br/>SLA monitoring"]
        ELK["Elasticsearch/Kibana<br/>Log search<br/>Analysis<br/>Troubleshooting"]
    end

    subgraph AI["AI & ML Services"]
        Claude["Claude API<br/>Text generation<br/>Embeddings<br/>Copilot"]
        pgvector["pgvector<br/>Vector storage<br/>Semantic search<br/>Similarity"]
    end

    subgraph Notifications["Notifications"]
        Email["Email Service<br/>Approvals<br/>Alerts<br/>Reports"]
        Slack["Slack Integration<br/>Notifications<br/>Alerts<br/>Digests"]
    end

    API -->|Auth| Keycloak
    API -->|Read/Write| Database
    API -->|Cache| Cache
    API -->|Event Bus| Kafka
    API -->|Async Jobs| Celery
    API -->|File Storage| S3
    API -->|Vector Search| pgvector
    API -->|Vector Gen| Claude

    Database -->|Observe| OTel
    Kafka -->|Observe| OTel
    OTel -->|Export| Prometheus
    Prometheus -->|Visualize| Grafana
    API -->|Logs| ELK

    BMS -->|Telemetry| API
    DCIM -->|Asset Data| API
    Meters -->|Stream| API
    Weather -->|Data| API

    API -->|Send| Email
    API -->|Send| Slack
    Alerts -->|Notify| Email
    Alerts -->|Notify| Slack

    style Platform fill:#e3f2fd
    style AuthServices fill:#f3e5f5
    style DataSources fill:#e8f5e9
    style Storage fill:#fff3e0
    style Messaging fill:#fce4ec
    style Analytics fill:#f1f8e9
    style AI fill:#ede7f6
    style Notifications fill:#fce4ec
```

---

## 6. Deployment Architecture Components

```mermaid
graph TB
    subgraph Development["Development Environment"]
        DockerCompose["Docker Compose<br/>FastAPI container<br/>React container<br/>PostgreSQL container<br/>Redis container<br/>Kafka container"]
        LocalDB["PostgreSQL<br/>Dev database<br/>Test data<br/>Migrations"]
        LocalKafka["Kafka<br/>Dev message bus<br/>Test events"]
    end

    subgraph Production["Production Environment"]
        K8S["Kubernetes Cluster<br/>Namespace: production<br/>High availability<br/>Auto-scaling"]

        subgraph Workloads["Workloads"]
            APIDeployment["API Deployment<br/>FastAPI pods<br/>Replicas: 3+<br/>Resource limits"]
            WorkerDeployment["Worker Deployment<br/>Celery workers<br/>Replicas: 2+"]
            AgentDeployment["Agent Deployment<br/>Agent runners<br/>Replicas: 2+"]
        end

        subgraph Database["Data Layer"]
            PrimaryDB["Primary DB<br/>PostgreSQL<br/>Read/Write<br/>Point-in-time recovery"]
            ReplicaDB["Replica DBs<br/>PostgreSQL<br/>Read-only<br/>Failover support"]
            TSDB["TimescaleDB<br/>Hypertables<br/>Partitioned<br/>Compressed"]
        end

        subgraph Cache["Cache & Queue"]
            ProdKafka["Kafka Cluster<br/>Replication: 3<br/>High availability<br/>Monitoring"]
            ProdRedis["Redis Cluster<br/>Replicated<br/>Sentinel<br/>Persistence"]
        end

        subgraph Storage["Object Storage"]
            ProdS3["S3 Bucket<br/>Versioning<br/>Encryption<br/>Lifecycle rules"]
            Backup["Backup Storage<br/>Daily snapshots<br/>Geo-redundant"]
        end

        subgraph Monitoring["Monitoring & Logging"]
            Prometheus["Prometheus<br/>Metrics collection<br/>Alerting rules"]
            Grafana["Grafana<br/>Dashboards<br/>On-call view"]
            ELK["ELK Stack<br/>Centralized logs<br/>Alert patterns"]
            Tracing["Jaeger<br/>Distributed tracing<br/>Latency analysis"]
        end

        subgraph LB["Load Balancing"]
            Ingress["Nginx Ingress<br/>TLS termination<br/>Rate limiting<br/>Routing"]
        end
    end

    subgraph CI["CI/CD Pipeline"]
        GitHub["GitHub<br/>Code repo<br/>PR reviews<br/>Branch protection"]
        GitHubActions["GitHub Actions<br/>Lint checks<br/>Unit tests<br/>Integration tests<br/>Build Docker images"]
        Registry["Docker Registry<br/>Image storage<br/>Version tags<br/>Scanning"]
    end

    GitHub -->|Trigger| GitHubActions
    GitHubActions -->|Push| Registry
    Registry -->|Pull| K8S

    DockerCompose -->|LocalDev| LocalDB
    DockerCompose -->|LocalDev| LocalKafka

    Ingress -->|Route| APIDeployment
    APIDeployment -->|Read/Write| PrimaryDB
    APIDeployment -->|Replicate| ReplicaDB
    APIDeployment -->|Publish| ProdKafka
    APIDeployment -->|Cache| ProdRedis
    APIDeployment -->|Store| ProdS3
    APIDeployment -->|Observe| Prometheus
    APIDeployment -->|Observe| ELK
    APIDeployment -->|Observe| Tracing

    WorkerDeployment -->|Consume| ProdKafka
    WorkerDeployment -->|Update| TSDB
    WorkerDeployment -->|Observe| Prometheus

    AgentDeployment -->|Consume| ProdKafka
    AgentDeployment -->|Write| PrimaryDB

    PrimaryDB -->|Backup| Backup
    Prometheus -->|Graph| Grafana
    ELK -->|Alert| Grafana

    style Development fill:#e1f5ff
    style Production fill:#fff3e0
    style Workloads fill:#e8f5e9
    style CI fill:#f3e5f5
    style Monitoring fill:#fce4ec
```

---

## Component Communication Patterns

### Synchronous (Request/Response)
```
Frontend → API Gateway → Service → Database
  └─→ Response back (JSON)
```

### Asynchronous (Event-Driven)
```
Producer → Kafka Topic → Consumer → Worker → Result
  └─→ Independent execution
```

### Scheduled (Background Jobs)
```
Scheduler → Celery Queue → Worker → Result
  └─→ Periodic execution (hourly, daily, etc)
```

---

**Navigation**: [Back to Index](./INDEX.md)
