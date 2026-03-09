# State Diagrams

**Purpose**: State machines for critical workflows
**Format**: Mermaid State Diagrams
**Last Updated**: March 9, 2026

---

## 1. Report Approval Workflow

```mermaid
stateDiagram-v2
    [*] --> Draft: Create Report

    Draft --> Draft: Edit Content
    Draft --> ReadyForReview: Submit for Review

    ReadyForReview --> Draft: Request Changes (Checker)
    ReadyForReview --> Checked: Approve (Checker)

    Checked --> ReadyForApproval: Checker Approves
    Checked --> ReadyForReview: Checker Requests Changes

    ReadyForApproval --> Checked: Reviewer Requests Changes
    ReadyForApproval --> Approved: Sign Off (Reviewer)

    Approved --> Restated: Restatement Required
    Approved --> [*]: Archive

    Restated --> Draft: Create Restatement

    note right of Draft
        - Data entry phase
        - Fully editable
        - No approval required
    end note

    note right of ReadyForReview
        - Awaiting checker review
        - Changes blocked
        - Notifications sent
    end note

    note right of Checked
        - Checker approved
        - Awaiting final sign-off
        - Immutability pending
    end note

    note right of ReadyForApproval
        - Final approval pending
        - Reviewer review complete
    end note

    note right of Approved
        - Immutable reference
        - Cannot edit directly
        - Must use Restatement
    end note
```

---

## 2. Telemetry Data Validation State Machine

```mermaid
stateDiagram-v2
    [*] --> Received: Data Ingestion

    Received --> Validating: Schema Check

    Validating --> ValidationError: Invalid Schema
    ValidationError --> [*]: Reject & Log

    Validating --> NormalizeUnits: Schema Valid

    NormalizeUnits --> CheckTimestamps: Units Converted
    CheckTimestamps --> AnomalyDetection: Timestamps Valid

    AnomalyDetection --> Anomalous: Outlier Detected
    Anomalous --> Stored: Flag & Continue

    AnomalyDetection --> Normal: In Range
    Normal --> Stored: Store Reading

    Stored --> CheckFreshness: Scheduled Task
    CheckFreshness --> Stale: >1 Hour Old
    Stale --> Alert: Create Alert
    Alert --> [*]

    CheckFreshness --> Fresh: Current
    Fresh --> [*]

    note right of Received
        Raw meter data arrived
    end note

    note right of Validating
        Check against schema
        for tenant
    end note

    note right of NormalizeUnits
        Convert to standard units
        (kWh, °C, etc)
    end note

    note right of Stored
        Persisted in TimescaleDB
        Ready for metrics
    end note

    note right of Anomalous
        Flagged for review
        Stored but marked
    end note
```

---

## 3. Carbon Metric Calculation State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Trigger (Scheduler)

    Pending --> DataGathering: Start Calculation
    DataGathering --> DataReady: Energy Data Retrieved

    DataReady --> FactorLookup: Get Emission Factors
    FactorLookup --> FactorNotFound: Region/Date Mismatch
    FactorNotFound --> FactorPending: Escalate
    FactorPending --> DataReady: Factor Added

    FactorLookup --> FactorFound: Factor Retrieved
    FactorFound --> Calculating: Use Factor v{N}

    Calculating --> Calculated: Emissions Computed
    Calculated --> DraftMetric: Store as Draft

    DraftMetric --> ValidateCalculation: Peer Review
    ValidateCalculation --> CalculationError: Errors Found
    CalculationError --> Calculating: Recalculate

    ValidateCalculation --> CalculationValid: Valid
    CalculationValid --> ReadyForApproval: Create Workflow

    ReadyForApproval --> Approved: Reviewer Sign-Off
    Approved --> Published: Locked for Reporting
    Published --> [*]: Used in Reports

    note right of DataGathering
        Query TimescaleDB
        for consumption
    end note

    note right of FactorLookup
        Retrieve current version
        with fallback logic
    end note

    note right of Calculating
        Scope1 = Fuel × Factor
        Scope2 = kWh × Factor
    end note

    note right of DraftMetric
        Status: draft
        Not yet in reports
    end note

    note right of Approved
        Immutable reference
        Audit trail complete
    end note
```

---

## 4. Evidence Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Uploaded: User Upload

    Uploaded --> Validating: Hash & Scan
    Validating --> ValidationFailed: Corrupted File
    ValidationFailed --> [*]: Reject

    Validating --> Stored: Valid & Stored
    Stored --> Unlinked: Awaiting Link

    Unlinked --> Linked: Link to Report/Metric
    Linked --> Active: In Use

    Active --> Active: Version Created (New Upload)
    Active --> Retained: Retention Period Active

    Retained --> Expiring: Near Expiry Date
    Expiring --> Archived: Auto-Archive

    Archived --> SoftDeleted: Mark Deleted
    SoftDeleted --> [*]: Historical Only

    Active --> ManuallyArchived: Admin Action
    ManuallyArchived --> [*]

    Unlinked --> ManuallyDeleted: Admin Delete
    ManuallyDeleted --> [*]: Removed

    note right of Uploaded
        File received via S3
        Pending validation
    end note

    note right of Stored
        Hash verified
        Saved to storage
    end note

    note right of Linked
        Associated with
        Report/Metric
    end note

    note right of Retained
        Retention active
        Cannot delete
    end note

    note right of SoftDeleted
        Marked for deletion
        Still queryable
    end note
```

---

## 5. KPI Threshold Violation State Machine

```mermaid
stateDiagram-v2
    [*] --> Healthy: Within Threshold

    Healthy --> Healthy: Metric Updates

    Healthy --> Warning: Approaches Threshold
    Warning --> Warning: Continue Monitoring
    Warning --> Healthy: Recovers
    Warning --> Violation: Breaches Threshold

    Violation --> Active: Alert Created
    Active --> Active: Continues Breached
    Active --> Acknowledged: Team Acknowledged

    Acknowledged --> Investigating: Root Cause Analysis
    Investigating --> Investigating: Investigation Ongoing
    Investigating --> Resolved: Fix Applied

    Resolved --> Validating: Verify Recovery
    Validating --> Healthy: Confirmed
    Validating --> Violation: Still Breached

    note right of Healthy
        PUE: 1.15
        Within target <1.2
    end note

    note right of Warning
        PUE: 1.18
        Close to limit
    end note

    note right of Violation
        PUE: 1.25
        Exceeds 1.2 threshold
    end note

    note right of Active
        Notification sent
        Logged in audit trail
    end note

    note right of Resolved
        Corrective action
        applied
    end note
```

---

## 6. Approval Stage State Machine

```mermaid
stateDiagram-v2
    [*] --> Unassigned: Created

    Unassigned --> Assigned: Assign to Approver
    Assigned --> Reviewing: Approver Starts Review

    Reviewing --> Reviewing: Add Comments
    Reviewing --> RequestChanges: Needs Modification
    RequestChanges --> [*]: Return to Maker

    Reviewing --> Approved: Decision: Approve
    Approved --> [*]: Stage Complete

    Assigned --> Expired: Due Date Passed
    Expired --> Escalated: Notify Management
    Escalated --> Reviewing: New Reviewer Assigned

    RequestChanges --> Reopened: Maker Resubmitted
    Reopened --> Reviewing: Back for Review

    note right of Unassigned
        Pending assignment
    end note

    note right of Reviewing
        Active review period
        Comments documented
    end note

    note right of RequestChanges
        Feedback provided
        Requires response
    end note

    note right of Approved
        Decision documented
        Signatures collected
    end note

    note right of Expired
        Escalation required
        SLA breach
    end note
```

---

## 7. Agent Execution State Machine

```mermaid
stateDiagram-v2
    [*] --> Queued: Triggered

    Queued --> Running: Worker Acquired
    Running --> Running: Processing

    Running --> InputValidationError: Bad Input
    InputValidationError --> Failed: Cannot Process

    Running --> Processing: Valid Input
    Processing --> Calculating: Computing

    Calculating --> Success: Completed
    Success --> Outputting: Generate Output

    Outputting --> RequiresApproval: High-Impact Action
    RequiresApproval --> PendingApproval: Waiting for Human
    PendingApproval --> Approved: Human Approved
    PendingApproval --> Rejected: Human Rejected

    Approved --> Persisting: Store Results
    Rejected --> [*]: Discarded

    Outputting --> NoApprovalNeeded: Low-Impact
    NoApprovalNeeded --> Persisting: Store Results

    Persisting --> Citation: Generate Citations
    Citation --> Complete: Log Completion
    Complete --> [*]: Archived

    Calculating --> Timeout: Exceeded Time Limit
    Timeout --> Failed: Timeout

    Failed --> [*]: Error Logged

    note right of Queued
        Agent job created
        Waiting for execution
    end note

    note right of Running
        Agent started
        Consuming input
    end note

    note right of RequiresApproval
        Action type requires
        human validation
    end note

    note right of Persisting
        Results saved
        Audit logged
    end note

    note right of Complete
        Agent run archived
        Ready for query
    end note
```

---

## 8. User Session State Machine

```mermaid
stateDiagram-v2
    [*] --> LoggedOut: Initial

    LoggedOut --> AuthenticatIng: Login Request
    AuthenticatIng --> InvalidCredentials: Failed Auth
    InvalidCredentials --> LoggedOut: Retry

    AuthenticatIng --> TokenIssued: Successful
    TokenIssued --> Active: Session Started

    Active --> Active: API Requests
    Active --> TokenExpiring: 15 min Left

    TokenExpiring --> TokenExpiring: Activity Detected
    TokenExpiring --> RefreshToken: Auto-Refresh
    RefreshToken --> Active: New Token

    TokenExpiring --> SessionExpired: No Activity
    SessionExpired --> LoggedOut: Logout

    Active --> LoggedOut: User Logout
    Active --> TimedOut: Inactivity >30 min
    TimedOut --> LoggedOut: Session Ended

    LoggedOut --> [*]: End Session

    note right of AuthenticatIng
        Keycloak validation
        JWT issued
    end note

    note right of Active
        Valid session
        Authorized requests
    end note

    note right of TokenExpiring
        Token < 15 min
        Refresh available
    end note

    note right of SessionExpired
        Token expired
        Reauth required
    end note
```

---

## 9. Organization Onboarding State Machine

```mermaid
stateDiagram-v2
    [*] --> Created: Tenant Created

    Created --> Configuring: Setup Phase
    Configuring --> Configuring: Add Settings
    Configuring --> ConfigurationComplete: All Required Fields Set

    ConfigurationComplete --> UserProvisioning: Create Users
    UserProvisioning --> UserProvisioning: Add Users & Roles
    UserProvisioning --> ReadyForUse: Users Ready

    ReadyForUse --> Active: Enabled
    Active --> Active: Normal Operation

    Active --> Paused: Temporary Suspend
    Paused --> Active: Reactivate

    Active --> Decommissioned: Delete
    Decommissioned --> [*]: Archived

    note right of Created
        Tenant provisioned
        in Keycloak
    end note

    note right of Configuring
        Organization details
        Reporting boundaries
    end note

    note right of UserProvisioning
        Admin users created
        Roles assigned
    end note

    note right of Active
        Operational
        Accepting data
    end note
```

---

## 10. Report Restatement State Machine

```mermaid
stateDiagram-v2
    [*] --> Approved: Approved Report

    Approved --> ErrorFound: Audit Identified Issue
    ErrorFound --> RestateRequested: Restatement Initiated

    RestateRequested --> MarkingSuperseded: Version Superseded
    MarkingSuperseded --> DraftRestatement: Create New Draft

    DraftRestatement --> DraftRestatement: Edit Corrections
    DraftRestatement --> ReviewingRestatement: Submit for Review

    ReviewingRestatement --> RequestChanges: Checker: Needs Work
    RequestChanges --> DraftRestatement: Revise

    ReviewingRestatement --> Approved: Checker & Reviewer Approve
    Approved --> RestatementFinalized: New Approved Version

    RestatementFinalized --> [*]: Archived

    note right of Approved
        Original approved report
        Marked as restated
    end note

    note right of RestateRequested
        Correction identified
        Restatement workflow
    end note

    note right of DraftRestatement
        New draft with
        corrections
    end note

    note right of RestatementFinalized
        Original superseded
        New version approved
        Full audit trail
    end note
```

---

## State Machine Transitions Summary

| Workflow | Initial | Terminal | Key Transitions | Approval Required? |
|----------|---------|----------|-----------------|-------------------|
| **Report** | Draft | Approved/Archived | Draft → Review → Check → Approved | Yes (2 stages) |
| **Telemetry** | Received | Stored | Validate → Normalize → Detect → Store | No |
| **Carbon** | Pending | Published | Calculate → Validate → Approve | Yes (1 stage) |
| **Evidence** | Uploaded | Archived | Upload → Link → Retain → Archive | No |
| **KPI** | Healthy | Resolved | Normal → Warning → Violation → Resolved | No (alert only) |
| **Agent** | Queued | Complete | Queue → Run → Process → Output → Store | Optional |
| **User** | LoggedOut | LoggedOut | Auth → Active → Refresh → Logout | No |

---

**Navigation**: [Back to Index](./INDEX.md)
