# API Interaction Diagrams

**Purpose**: REST API relationships and call flows
**Format**: Mermaid Graph Diagrams
**Last Updated**: March 9, 2026

---

## 1. Authentication Flow (OAuth2/OIDC with Keycloak)

```mermaid
graph LR
    Browser["Browser<br/>Frontend App"]
    Frontend["React App<br/>icarbon.com"]

    Keycloak["Keycloak Server<br/>OAuth2 Provider"]
    KeycloakDB["Keycloak DB<br/>Users & Roles"]

    API["FastAPI Backend<br/>API Gateway"]
    Database["PostgreSQL<br/>App Data"]

    LocalStorage["LocalStorage<br/>Tokens"]

    Browser -->|1. Click 'Login'| Frontend
    Frontend -->|2. Redirect| Keycloak
    Keycloak -->|3. Login Form| Browser
    Browser -->|4. Username/Password| Keycloak
    Keycloak -->|Validate| KeycloakDB
    Keycloak -->|5. Auth Code| Browser

    Frontend -->|6. Exchange Code<br/>POST /token| Keycloak
    Keycloak -->|7. {access_token, refresh_token}| Frontend
    Frontend -->|Store| LocalStorage

    Frontend -->|8. API Request<br/>Header: Authorization: Bearer {token}| API
    API -->|Validate JWT| Keycloak
    Keycloak -->|Valid| API
    API -->|9. Query data| Database
    API -->|10. Response + data| Frontend

    Browser -->|11. Render page| Frontend

    style Keycloak fill:#f3e5f5
    style API fill:#e3f2fd
    style LocalStorage fill:#fce4ec
```

---

## 2. Tenant Scoping & Authorization

```mermaid
graph LR
    Client["Client<br/>GET /api/v1/organizations"]

    Middleware["Auth Middleware<br/>Extract JWT<br/>Validate signature<br/>Get user claims"]

    TenantMiddleware["Tenant Middleware<br/>Extract tenant_id<br/>from token"]

    RBAC["RBAC Check<br/>user role<br/>required permissions<br/>resource access"]

    ServiceLayer["Service Layer<br/>Apply tenant filter<br/>WHERE tenant_id = $1"]

    Database["PostgreSQL<br/>Query with<br/>tenant scoping"]

    Response["Response<br/>Only user's<br/>tenant data"]

    Client -->|Request with JWT| Middleware
    Middleware -->|Valid JWT| TenantMiddleware
    TenantMiddleware -->|Extract tenant_id| RBAC

    RBAC -->|Check permissions<br/>user.roles<br/>resource.required_permission| RBAC
    RBAC -->|Allowed| ServiceLayer
    RBAC -->|Denied| Error["401 Unauthorized"]

    ServiceLayer -->|Add WHERE<br/>tenant_id clause| Database
    Database -->|Scoped results| Response
    Response -->|200 OK<br/>{data}| Client

    style Middleware fill:#e1f5ff
    style TenantMiddleware fill:#e1f5ff
    style RBAC fill:#f3e5f5
    style ServiceLayer fill:#e8f5e9
    style Database fill:#fff3e0
```

---

## 3. API Endpoint Hierarchy & Organization

```mermaid
graph TD
    API["iNetZero API<br/>Base: /api/v1"]

    AuthGroup["Authentication<br/>/auth"]
    AuthLogin["POST /auth/login"]
    AuthRefresh["POST /auth/refresh"]
    AuthLogout["POST /auth/logout"]
    AuthMe["GET /auth/me"]

    TenantGroup["Tenants<br/>/tenants"]
    TenantCreate["POST /tenants"]
    TenantGet["GET /tenants/{tenant_id}"]
    TenantUpdate["PATCH /tenants/{tenant_id}"]

    OrgGroup["Organizations<br/>/tenants/{tenant_id}/organizations"]
    OrgCreate["POST /organizations"]
    OrgList["GET /organizations"]
    OrgUpdate["PATCH /organizations/{org_id}"]

    FacilityGroup["Facilities<br/>/organizations/{org_id}"]
    SiteCreate["POST /sites"]
    SiteList["GET /sites"]
    BuildingCreate["POST /buildings"]
    BuildingList["GET /buildings"]
    ZoneCreate["POST /zones"]
    RackCreate["POST /racks"]

    AssetGroup["Assets<br/>/organizations/{org_id}/assets"]
    AssetCreate["POST /assets"]
    AssetList["GET /assets"]
    AssetUpdate["PATCH /assets/{asset_id}"]

    TelemetryGroup["Telemetry<br/>/tenants/{tenant_id}/telemetry"]
    TelemetryCreate["POST /telemetry"]
    TelemetryBatch["POST /telemetry/batch"]
    TelemetryHistory["GET /telemetry/history"]

    MetricsGroup["Metrics<br/>/tenants/{tenant_id}/metrics"]
    EnergyMetrics["GET /metrics/energy"]
    CarbonMetrics["GET /metrics/carbon"]
    KPIMetrics["GET /metrics/kpi"]

    ReportGroup["Reports<br/>/tenants/{tenant_id}/reports"]
    ReportCreate["POST /reports"]
    ReportList["GET /reports"]
    ReportGet["GET /reports/{report_id}"]
    ReportUpdate["PATCH /reports/{report_id}"]
    ReportExport["GET /reports/{report_id}/export"]

    EvidenceGroup["Evidence<br/>/tenants/{tenant_id}/evidence"]
    EvidenceUpload["POST /evidence"]
    EvidenceList["GET /evidence"]
    EvidenceLink["PATCH /evidence/{id}"]

    WorkflowGroup["Workflows<br/>/tenants/{tenant_id}/workflows"]
    ApprovalCreate["POST /approvals"]
    ApprovalUpdate["PATCH /approvals/{id}"]
    ApprovalList["GET /approvals"]

    CopilotGroup["Copilot<br/>/tenants/{tenant_id}/copilot"]
    CopilotAsk["POST /copilot/ask"]
    CopilotHistory["GET /copilot/history"]

    API -->|v1 resources| AuthGroup
    API -->|v1 resources| TenantGroup
    API -->|v1 resources| OrgGroup
    API -->|v1 resources| FacilityGroup
    API -->|v1 resources| AssetGroup
    API -->|v1 resources| TelemetryGroup
    API -->|v1 resources| MetricsGroup
    API -->|v1 resources| ReportGroup
    API -->|v1 resources| EvidenceGroup
    API -->|v1 resources| WorkflowGroup
    API -->|v1 resources| CopilotGroup

    AuthGroup --> AuthLogin
    AuthGroup --> AuthRefresh
    AuthGroup --> AuthLogout
    AuthGroup --> AuthMe

    TenantGroup --> TenantCreate
    TenantGroup --> TenantGet
    TenantGroup --> TenantUpdate

    OrgGroup --> OrgCreate
    OrgGroup --> OrgList
    OrgGroup --> OrgUpdate

    FacilityGroup --> SiteCreate
    FacilityGroup --> SiteList
    FacilityGroup --> BuildingCreate
    FacilityGroup --> BuildingList
    FacilityGroup --> ZoneCreate
    FacilityGroup --> RackCreate

    AssetGroup --> AssetCreate
    AssetGroup --> AssetList
    AssetGroup --> AssetUpdate

    TelemetryGroup --> TelemetryCreate
    TelemetryGroup --> TelemetryBatch
    TelemetryGroup --> TelemetryHistory

    MetricsGroup --> EnergyMetrics
    MetricsGroup --> CarbonMetrics
    MetricsGroup --> KPIMetrics

    ReportGroup --> ReportCreate
    ReportGroup --> ReportList
    ReportGroup --> ReportGet
    ReportGroup --> ReportUpdate
    ReportGroup --> ReportExport

    EvidenceGroup --> EvidenceUpload
    EvidenceGroup --> EvidenceList
    EvidenceGroup --> EvidenceLink

    WorkflowGroup --> ApprovalCreate
    WorkflowGroup --> ApprovalUpdate
    WorkflowGroup --> ApprovalList

    CopilotGroup --> CopilotAsk
    CopilotGroup --> CopilotHistory

    style API fill:#e3f2fd
    style AuthGroup fill:#f3e5f5
    style TenantGroup fill:#fff3e0
    style OrgGroup fill:#e8f5e9
    style FacilityGroup fill:#fce4ec
    style AssetGroup fill:#f1f8e9
    style TelemetryGroup fill:#fff9c4
    style MetricsGroup fill:#ffe0b2
    style ReportGroup fill:#ffccbc
    style EvidenceGroup fill:#c8e6c9
    style WorkflowGroup fill:#b3e5fc
    style CopilotGroup fill:#f8bbd0
```

---

## 4. Request/Response Patterns

```mermaid
graph TB
    Client["Client<br/>Browser/SDK"]

    RequestHeader["Request<br/>─────────<br/>Method: GET/POST/PATCH<br/>Path: /api/v1/...<br/>Headers: {<br/>  Authorization: Bearer {token}<br/>  Content-Type: application/json<br/>  X-Tenant-ID: {tenant_id}<br/>}"]

    RequestBody["Body<br/>─────────<br/>{<br/>  field1: value<br/>  field2: value<br/>}<br/>(for POST/PATCH)"]

    Server["FastAPI Server<br/>─────────<br/>1. Validate auth<br/>2. Parse body<br/>3. Validate schema<br/>4. Check auth<br/>5. Execute logic<br/>6. Return response"]

    SuccessResponse["Success Response<br/>─────────<br/>Status: 200/201<br/>{<br/>  id: 'uuid'<br/>  field1: value<br/>  created_at: '2026-03-09...'<br/>  updated_at: '2026-03-09...'<br/>}"]

    ErrorResponse["Error Response<br/>─────────<br/>Status: 400/401/403/500<br/>{<br/>  error: 'string'<br/>  code: 'ERROR_CODE'<br/>  status: 400<br/>  details: {<br/>    field: ['message']<br/>  }<br/>}"]

    PaginatedResponse["Paginated Response<br/>─────────<br/>{<br/>  items: [<br/>    {item1},<br/>    {item2}<br/>  ]<br/>  total_count: 100<br/>  limit: 10<br/>  offset: 0<br/>}"]

    Client -->|Sends| RequestHeader
    RequestHeader -->|With| RequestBody
    RequestBody -->|To| Server

    Server -->|Validates & processes|Server
    Server -->|Returns| SuccessResponse
    Server -->|Or returns| ErrorResponse
    Server -->|Or returns| PaginatedResponse

    SuccessResponse -->|200/201| Client
    ErrorResponse -->|4xx/5xx| Client
    PaginatedResponse -->|200| Client

    style RequestHeader fill:#e3f2fd
    style RequestBody fill:#e3f2fd
    style Server fill:#f3e5f5
    style SuccessResponse fill:#c8e6c9
    style ErrorResponse fill:#ffcdd2
    style PaginatedResponse fill:#fff9c4
```

---

## 5. Tenant Creation & Setup Flow

```mermaid
graph LR
    Admin["Admin User"]

    Step1["1. Create Tenant<br/>POST /tenants<br/>{name, slug}"]
    API1["API: Create<br/>TenantService"]
    DB1["DB: Insert<br/>tenants table"]

    Step2["2. Create Admin User<br/>POST /users<br/>{email, name}"]
    API2["API: Create<br/>UserService"]
    Keycloak["Keycloak<br/>Create user"]
    DB2["DB: Insert<br/>users table"]

    Step3["3. Assign Admin Role<br/>POST /users/{id}/roles<br/>{role: 'admin'}"]
    API3["API: Assign<br/>RoleService"]
    DB3["DB: Insert<br/>user_roles table"]

    Step4["4. Create Organization<br/>POST /organizations<br/>{org_name, settings}"]
    API4["API: Create<br/>OrgService"]
    DB4["DB: Insert<br/>organizations table"]

    Admin -->|Step 1| Step1
    Step1 -->|Execute| API1
    API1 -->|Insert| DB1

    Admin -->|Step 2| Step2
    Step2 -->|Execute| API2
    API2 -->|Create| Keycloak
    API2 -->|Insert| DB2

    Admin -->|Step 3| Step3
    Step3 -->|Execute| API3
    API3 -->|Insert| DB3

    Admin -->|Step 4| Step4
    Step4 -->|Execute| API4
    API4 -->|Insert| DB4

    DB1 -->|{tenant_id}| DB2
    DB2 -->|{user_id}| DB3
    DB3 -->|{role_id}| DB4
    DB4 -->|Ready| Admin

    style Step1 fill:#e3f2fd
    style Step2 fill:#e3f2fd
    style Step3 fill:#e3f2fd
    style Step4 fill:#e3f2fd
    style API1 fill:#f3e5f5
    style API2 fill:#f3e5f5
    style API3 fill:#f3e5f5
    style API4 fill:#f3e5f5
```

---

## 6. Telemetry Ingestion API Call Flow

```mermaid
graph LR
    Device["IoT Device<br/>Meter reading"]

    API["API Endpoint<br/>POST /api/v1/telemetry<br/>Content-Type: application/json"]

    Body["Request Body<br/>─────────<br/>{<br/>  meter_id: 'uuid'<br/>  value: 150.5<br/>  unit: 'kWh'<br/>  timestamp: '2026-03-09T10:30:00Z'<br/>}"]

    Validation["Validation<br/>─────────<br/>✓ Schema valid<br/>✓ Unit valid<br/>✓ Timestamp valid<br/>✓ Tenant scoped"]

    Processing["Processing<br/>─────────<br/>1. Normalize unit<br/>2. Convert timezone<br/>3. Check anomalies<br/>4. Store TSDB"]

    Response["Response<br/>─────────<br/>Status: 201 Created<br/>{<br/>  reading_id: 'uuid'<br/>  status: 'stored'<br/>  created_at: '...'<br/>}"]

    Device -->|HTTP POST| API
    API -->|Body| Body
    Body -->|Validate| Validation
    Validation -->|Valid| Processing
    Processing -->|Success| Response
    Response -->|201| Device

    style API fill:#e3f2fd
    style Body fill:#e3f2fd
    style Validation fill:#f3e5f5
    style Processing fill:#e8f5e9
    style Response fill:#c8e6c9
```

---

## 7. Metrics Query API Call Flow

```mermaid
graph LR
    Frontend["Dashboard<br/>React Component"]

    Query["API Query<br/>GET /api/v1/metrics/energy<br/>?organization_id=uuid<br/>&start_date=2026-03-01<br/>&end_date=2026-03-31<br/>&interval=daily"]

    CacheCheck["Cache Check<br/>Key: metrics_energy_{org}_{dates}<br/>TTL: 5 min<br/>Status: MISS"]

    DatabaseQuery["Database Query<br/>SELECT<br/>  organization_id,<br/>  DATE_TRUNC('day', timestamp) AS date,<br/>  SUM(value) AS total<br/>FROM energy_metrics<br/>WHERE<br/>  tenant_id = $1<br/>  AND organization_id = $2<br/>  AND timestamp BETWEEN $3 AND $4<br/>GROUP BY date"]

    Processing["Processing<br/>─────────<br/>1. Aggregate by interval<br/>2. Calculate totals<br/>3. Format for chart<br/>4. Cache result"]

    Response["Response<br/>─────────<br/>{<br/>  items: [<br/>    {date: '2026-03-01', total_kwh: 5000},<br/>    {date: '2026-03-02', total_kwh: 4900}<br/>  ]<br/>}"]

    Frontend -->|Fetch| Query
    Query -->|Check| CacheCheck
    CacheCheck -->|Miss| DatabaseQuery
    DatabaseQuery -->|Results| Processing
    Processing -->|Cache 5 min| Processing
    Processing -->|Response| Response
    Response -->|200 OK| Frontend

    style Query fill:#e3f2fd
    style CacheCheck fill:#fce4ec
    style DatabaseQuery fill:#fff3e0
    style Processing fill:#e8f5e9
    style Response fill:#c8e6c9
```

---

## 8. Report Approval API Call Flow

```mermaid
graph LR
    Maker["Maker User"]

    Submit["Submit for Review<br/>PATCH /api/v1/reports/{report_id}<br/>{<br/>  action: 'submit_for_review'<br/>}"]

    MakerAPI["API: Update Report<br/>1. Validate ownership<br/>2. Check state<br/>3. Update workflow<br/>4. Publish event"]

    Check["Response<br/>─────────<br/>Status: 200 OK<br/>{<br/>  report_id: 'uuid'<br/>  state: 'ready_for_review'<br/>  updated_at: '...'<br/>}"]

    Checker["Checker User"]

    Review["Review & Approve<br/>PATCH /api/v1/approvals/{approval_id}<br/>{<br/>  decision: 'approved'<br/>  comments: 'LGTM'<br/>}"]

    CheckerAPI["API: Update Approval<br/>1. Validate checker role<br/>2. Check state<br/>3. Update approval<br/>4. Publish event"]

    CheckResp["Response<br/>─────────<br/>Status: 200 OK<br/>{<br/>  approval_id: 'uuid'<br/>  state: 'approved'<br/>}"]

    Reviewer["Reviewer User"]

    Approve["Final Sign-Off<br/>PATCH /api/v1/approvals/{final_id}<br/>{<br/>  decision: 'approved'<br/>  signature: '{sig_data}'<br/>}"]

    ReviewerAPI["API: Final Approval<br/>1. Validate reviewer<br/>2. Lock report<br/>3. Archive version<br/>4. Publish event"]

    FinalResp["Response<br/>─────────<br/>Status: 200 OK<br/>{<br/>  state: 'approved'<br/>  locked: true<br/>}"]

    Maker -->|Submit| Submit
    Submit -->|Execute| MakerAPI
    MakerAPI -->|Return| Check

    Checker -->|Review| Review
    Review -->|Execute| CheckerAPI
    CheckerAPI -->|Return| CheckResp

    Reviewer -->|Sign Off| Approve
    Approve -->|Execute| ReviewerAPI
    ReviewerAPI -->|Return| FinalResp

    style Submit fill:#e3f2fd
    style MakerAPI fill:#f3e5f5
    style Check fill:#c8e6c9
    style Review fill:#e3f2fd
    style CheckerAPI fill:#f3e5f5
    style CheckResp fill:#c8e6c9
    style Approve fill:#e3f2fd
    style ReviewerAPI fill:#f3e5f5
    style FinalResp fill:#c8e6c9
```

---

## 9. Error Handling & Validation

```mermaid
graph TD
    Request["Client Request"]

    Step1["1. Schema Validation<br/>Pydantic<br/>Check types<br/>Check ranges<br/>Check required fields"]
    Pass1{Valid?}
    Fail1["400 Bad Request<br/>{<br/>  error: 'Validation failed'<br/>  details: {<br/>    field: ['error msg']<br/>  }<br/>}"]

    Step2["2. Authentication<br/>Extract JWT<br/>Validate signature<br/>Check expiry"]
    Pass2{Valid?}
    Fail2["401 Unauthorized<br/>{<br/>  error: 'Invalid token'<br/>  code: 'AUTH_INVALID'<br/>}"]

    Step3["3. Authorization<br/>Check tenant_id<br/>Check user roles<br/>Check permissions"]
    Pass3{Valid?}
    Fail3["403 Forbidden<br/>{<br/>  error: 'Insufficient permissions'<br/>  code: 'RBAC_DENIED'<br/>}"]

    Step4["4. Business Logic<br/>Execute service<br/>Update database"]
    Pass4{Success?}
    Fail4["500 Server Error<br/>{<br/>  error: 'Internal error'<br/>  code: 'DB_ERROR'<br/>}"]

    Success["200/201 OK<br/>Return data"]

    Request -->|Validate| Step1
    Step1 -->|Check| Pass1
    Pass1 -->|No| Fail1
    Pass1 -->|Yes| Step2

    Step2 -->|Check| Pass2
    Pass2 -->|No| Fail2
    Pass2 -->|Yes| Step3

    Step3 -->|Check| Pass3
    Pass3 -->|No| Fail3
    Pass3 -->|Yes| Step4

    Step4 -->|Check| Pass4
    Pass4 -->|No| Fail4
    Pass4 -->|Yes| Success

    style Request fill:#e3f2fd
    style Step1 fill:#f3e5f5
    style Step2 fill:#f3e5f5
    style Step3 fill:#f3e5f5
    style Step4 fill:#e8f5e9
    style Success fill:#c8e6c9
    style Fail1 fill:#ffcdd2
    style Fail2 fill:#ffcdd2
    style Fail3 fill:#ffcdd2
    style Fail4 fill:#ffcdd2
```

---

## 10. Rate Limiting & Throttling

```mermaid
graph LR
    Client["Client<br/>API Consumer"]

    Request["HTTP Request<br/>X-Tenant-ID: tenant_abc<br/>Authorization: Bearer ..."]

    RateLimiter["Rate Limiter<br/>Per-tenant bucket<br/>Limit: 100 req/sec<br/>Burst: 500"]

    BucketCheck{"Tokens<br/>Available?"}

    Allowed["Request Allowed<br/>Decrement bucket<br/>Pass to handler"]

    Rejected["429 Too Many Requests<br/>{<br/>  error: 'Rate limit exceeded'<br/>  retry_after: 5<br/>}"]

    Handler["Handler<br/>Process request<br/>Return response"]

    Response["Response<br/>Headers:<br/>  X-RateLimit-Limit: 100<br/>  X-RateLimit-Remaining: 85<br/>  X-RateLimit-Reset: 1234567890"]

    Refill["Token Refill<br/>Every second<br/>Add tokens<br/>Max: 100"]

    Client -->|Send| Request
    Request -->|Check| RateLimiter
    RateLimiter -->|Check bucket| BucketCheck

    BucketCheck -->|Yes| Allowed
    BucketCheck -->|No| Rejected

    Allowed -->|Execute| Handler
    Handler -->|Generate| Response
    Response -->|200 OK| Client

    Rejected -->|429| Client

    RateLimiter -->|Every 1s| Refill
    Refill -->|Update bucket| RateLimiter

    style RateLimiter fill:#f3e5f5
    style BucketCheck fill:#fff3e0
    style Allowed fill:#c8e6c9
    style Rejected fill:#ffcdd2
    style Handler fill:#e8f5e9
    style Response fill:#c8e6c9
```

---

## Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | OK | Successful GET request |
| **201** | Created | Successful POST creating resource |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Validation error |
| **401** | Unauthorized | Invalid/missing token |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Duplicate key / state conflict |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Unhandled exception |
| **503** | Service Unavailable | Maintenance mode |

---

**Navigation**: [Back to Index](./INDEX.md)
