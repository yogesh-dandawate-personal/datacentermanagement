# Domain Model Diagrams

**Purpose**: Entity and class relationships showing all domain objects in iNetZero
**Format**: Mermaid UML Class Diagrams
**Last Updated**: March 9, 2026

---

## 1. Core Tenant & Organization Entities

```mermaid
classDiagram
    class Tenant {
        +UUID id
        +String name
        +String slug
        +String description
        +String status
        +DateTime created_at
        +String created_by
        +DateTime updated_at
        +String updated_by
        +DateTime deleted_at
    }

    class Organization {
        +UUID id
        +UUID tenant_id
        +String name
        +String address
        +String timezone
        +String reporting_units
        +String status
        +DateTime created_at
        +String created_by
        +DateTime updated_at
        +String updated_by
    }

    class Site {
        +UUID id
        +UUID org_id
        +String name
        +String location
        +Float latitude
        +Float longitude
        +String status
        +DateTime created_at
    }

    class Building {
        +UUID id
        +UUID site_id
        +String name
        +String floor_count
        +Float square_meters
        +DateTime created_at
    }

    class Zone {
        +UUID id
        +UUID building_id
        +String name
        +String zone_type
        +Float area
        +DateTime created_at
    }

    class Rack {
        +UUID id
        +UUID zone_id
        +String rack_id
        +Integer u_count
        +Float power_capacity_kw
        +DateTime created_at
    }

    Tenant "1" -- "*" Organization
    Organization "1" -- "*" Site
    Site "1" -- "*" Building
    Building "1" -- "*" Zone
    Zone "1" -- "*" Rack
```

---

## 2. Asset & Device Entities

```mermaid
classDiagram
    class Device {
        +UUID id
        +UUID rack_id
        +String device_type
        +String serial_number
        +String model
        +String manufacturer
        +DateTime installation_date
        +String status
        +DateTime created_at
    }

    class DeviceSpecification {
        +UUID id
        +UUID device_id
        +String spec_key
        +String spec_value
        +String unit
        +DateTime created_at
    }

    class Meter {
        +UUID id
        +UUID device_id
        +String meter_type
        +String utility
        +String unit_of_measure
        +Float accuracy_percent
        +DateTime last_reading
        +DateTime created_at
    }

    class MeterReading {
        +UUID id
        +UUID meter_id
        +DateTime reading_timestamp
        +Float value
        +String status
        +DateTime created_at
    }

    class AssetLifecycle {
        +UUID id
        +UUID device_id
        +String event_type
        +DateTime event_date
        +String event_description
        +String event_status
        +DateTime created_at
    }

    Device "1" -- "*" DeviceSpecification
    Device "1" -- "*" Meter
    Device "1" -- "*" AssetLifecycle
    Meter "1" -- "*" MeterReading
```

---

## 3. Telemetry Entities

```mermaid
classDiagram
    class TelemetryReading {
        +UUID id
        +UUID tenant_id
        +UUID meter_id
        +DateTime timestamp
        +Float value
        +String unit
        +String status
        +DateTime created_at
    }

    class TelemetryValidationError {
        +UUID id
        +UUID tenant_id
        +DateTime error_timestamp
        +String error_type
        +String error_message
        +String source_data
        +DateTime created_at
    }

    class TelemetryAnomaly {
        +UUID id
        +UUID tenant_id
        +UUID meter_id
        +DateTime anomaly_timestamp
        +String anomaly_type
        +Float expected_value
        +Float actual_value
        +String severity
        +String status
        +DateTime created_at
    }

    class TelemetrySchema {
        +UUID id
        +UUID tenant_id
        +String schema_name
        +JSON schema_definition
        +String status
        +DateTime created_at
        +DateTime updated_at
    }

    TelemetryReading "1" -- "*" TelemetryValidationError
    TelemetryReading "1" -- "*" TelemetryAnomaly
    TelemetrySchema "1" -- "*" TelemetryReading
```

---

## 4. Energy & Carbon Entities

```mermaid
classDiagram
    class EnergyMetric {
        +UUID id
        +UUID tenant_id
        +UUID organization_id
        +DateTime metric_date
        +Float total_consumption_kwh
        +Float it_consumption_kwh
        +Float cooling_consumption_kwh
        +Float overhead_consumption_kwh
        +String status
        +DateTime created_at
    }

    class CarbonMetric {
        +UUID id
        +UUID tenant_id
        +UUID organization_id
        +DateTime metric_date
        +Float scope_1_emissions_kg_co2e
        +Float scope_2_emissions_kg_co2e
        +Float scope_3_emissions_kg_co2e
        +String methodology
        +String status
        +DateTime created_at
    }

    class EmissionFactor {
        +UUID id
        +String factor_name
        +String factor_type
        +Float value
        +String unit
        +String region
        +String data_source
        +DateTime effective_date
        +DateTime obsolete_date
        +DateTime created_at
    }

    class FactorVersion {
        +UUID id
        +UUID factor_id
        +Integer version_number
        +Float value
        +String changelog
        +DateTime effective_date
        +String status
        +DateTime created_at
    }

    class CarbonCalculation {
        +UUID id
        +UUID carbon_metric_id
        +String calculation_type
        +Float energy_input_kwh
        +UUID factor_id
        +Integer factor_version
        +Float result_kg_co2e
        +String status
        +DateTime created_at
    }

    EnergyMetric "*" -- "1" CarbonMetric
    CarbonMetric "1" -- "*" CarbonCalculation
    EmissionFactor "1" -- "*" FactorVersion
    CarbonCalculation "*" -- "1" EmissionFactor
    CarbonCalculation "*" -- "1" FactorVersion
```

---

## 5. KPI Entities

```mermaid
classDiagram
    class KPIDefinition {
        +UUID id
        +UUID organization_id
        +String kpi_name
        +String formula
        +String unit
        +Float target_value
        +String calculation_method
        +String status
        +DateTime created_at
    }

    class KPISnapshot {
        +UUID id
        +UUID kpi_definition_id
        +UUID organization_id
        +DateTime snapshot_date
        +Float calculated_value
        +Float target_value
        +Float variance_percent
        +String status
        +DateTime created_at
    }

    class KPIThreshold {
        +UUID id
        +UUID kpi_definition_id
        +String threshold_name
        +Float threshold_value
        +String operator
        +String alert_severity
        +String status
        +DateTime created_at
    }

    class KPIThresholdBreach {
        +UUID id
        +UUID threshold_id
        +UUID snapshot_id
        +DateTime breach_timestamp
        +Float breached_value
        +String severity
        +String status
        +DateTime created_at
    }

    KPIDefinition "1" -- "*" KPISnapshot
    KPIDefinition "1" -- "*" KPIThreshold
    KPIThreshold "1" -- "*" KPIThresholdBreach
    KPISnapshot "*" -- "*" KPIThresholdBreach
```

---

## 6. Evidence Repository Entities

```mermaid
classDiagram
    class Evidence {
        +UUID id
        +UUID tenant_id
        +String document_name
        +String document_type
        +String file_path
        +String s3_key
        +String file_hash
        +Integer file_size_bytes
        +String category
        +DateTime upload_date
        +String uploaded_by
        +String status
        +DateTime created_at
    }

    class EvidenceVersion {
        +UUID id
        +UUID evidence_id
        +Integer version_number
        +String s3_key
        +String file_hash
        +DateTime version_date
        +String changed_by
        +String change_reason
        +DateTime created_at
    }

    class EvidenceMetadata {
        +UUID id
        +UUID evidence_id
        +String metadata_key
        +String metadata_value
        +DateTime created_at
    }

    class EvidenceLink {
        +UUID id
        +UUID evidence_id
        +String linked_entity_type
        +UUID linked_entity_id
        +String link_type
        +DateTime created_at
    }

    class EvidenceRetention {
        +UUID id
        +UUID evidence_id
        +String retention_category
        +DateTime retention_until_date
        +String status
        +DateTime created_at
    }

    Evidence "1" -- "*" EvidenceVersion
    Evidence "1" -- "*" EvidenceMetadata
    Evidence "1" -- "*" EvidenceLink
    Evidence "1" -- "*" EvidenceRetention
```

---

## 7. Workflow & Approval Entities

```mermaid
classDiagram
    class WorkflowState {
        +UUID id
        +UUID entity_id
        +String entity_type
        +String current_state
        +String previous_state
        +DateTime state_changed_at
        +String changed_by
        +String change_reason
        +DateTime created_at
    }

    class Approval {
        +UUID id
        +UUID entity_id
        +String entity_type
        +String approval_stage
        +String required_role
        +String status
        +DateTime due_date
        +String assigned_to
        +DateTime completed_date
        +String completed_by
        +String decision
        +String comments
        +DateTime created_at
    }

    class ApprovalComment {
        +UUID id
        +UUID approval_id
        +String comment_text
        +String commented_by
        +String comment_type
        +DateTime created_at
    }

    class ApprovalHistory {
        +UUID id
        +UUID approval_id
        +String previous_status
        +String new_status
        +DateTime status_changed_at
        +String changed_by
        +String change_reason
        +DateTime created_at
    }

    WorkflowState "1" -- "*" Approval
    Approval "1" -- "*" ApprovalComment
    Approval "1" -- "*" ApprovalHistory
```

---

## 8. Report & Reporting Entities

```mermaid
classDiagram
    class Report {
        +UUID id
        +UUID tenant_id
        +UUID organization_id
        +String report_type
        +DateTime report_period_start
        +DateTime report_period_end
        +String current_state
        +DateTime created_at
        +String created_by
        +DateTime updated_at
        +String updated_by
    }

    class ReportVersion {
        +UUID id
        +UUID report_id
        +Integer version_number
        +String version_label
        +String s3_key_pdf
        +String s3_key_json
        +String state
        +DateTime version_date
        +String versioned_by
        +String version_reason
        +DateTime created_at
    }

    class ReportSection {
        +UUID id
        +UUID report_version_id
        +String section_name
        +String section_content
        +JSON section_data
        +Integer section_order
        +DateTime created_at
    }

    class ReportApproval {
        +UUID id
        +UUID report_id
        +String approval_stage
        +String assigned_to
        +String status
        +String comments
        +DateTime approved_date
        +String approved_by
        +DateTime created_at
    }

    class ReportSignature {
        +UUID id
        +UUID report_version_id
        +String signer_name
        +String signer_role
        +String signature_data
        +String signature_timestamp
        +DateTime signed_date
        +DateTime created_at
    }

    Report "1" -- "*" ReportVersion
    ReportVersion "1" -- "*" ReportSection
    Report "1" -- "*" ReportApproval
    ReportVersion "1" -- "*" ReportSignature
```

---

## 9. User & Authorization Entities

```mermaid
classDiagram
    class User {
        +UUID id
        +UUID tenant_id
        +String keycloak_id
        +String email
        +String first_name
        +String last_name
        +String status
        +DateTime last_login
        +DateTime created_at
    }

    class Role {
        +UUID id
        +UUID tenant_id
        +String role_name
        +String role_description
        +String status
        +DateTime created_at
    }

    class Permission {
        +UUID id
        +String permission_name
        +String permission_description
        +String resource
        +String action
        +DateTime created_at
    }

    class UserRole {
        +UUID id
        +UUID user_id
        +UUID role_id
        +DateTime assigned_at
        +String assigned_by
        +DateTime revoked_at
        +DateTime created_at
    }

    class RolePermission {
        +UUID id
        +UUID role_id
        +UUID permission_id
        +DateTime granted_at
        +DateTime revoked_at
        +DateTime created_at
    }

    User "1" -- "*" UserRole
    Role "1" -- "*" UserRole
    Role "1" -- "*" RolePermission
    Permission "1" -- "*" RolePermission
```

---

## 10. Audit & Compliance Entities

```mermaid
classDiagram
    class AuditLog {
        +UUID id
        +UUID tenant_id
        +String entity_type
        +UUID entity_id
        +String action_type
        +String action_description
        +String old_value
        +String new_value
        +String user_id
        +String user_email
        +String ip_address
        +DateTime action_timestamp
        +DateTime created_at
    }

    class AuditDetail {
        +UUID id
        +UUID audit_log_id
        +String field_name
        +String old_value
        +String new_value
        +DateTime created_at
    }

    class ComplianceFlag {
        +UUID id
        +UUID organization_id
        +String compliance_framework
        +String gap_description
        +String severity
        +String status
        +DateTime created_at
        +DateTime resolved_date
    }

    class ComplianceEvidence {
        +UUID id
        +UUID compliance_flag_id
        +UUID evidence_id
        +String mapping_type
        +DateTime created_at
    }

    AuditLog "1" -- "*" AuditDetail
    ComplianceFlag "1" -- "*" ComplianceEvidence
```

---

## 11. Agent Execution & Logging Entities

```mermaid
classDiagram
    class AgentRun {
        +UUID id
        +UUID tenant_id
        +String agent_type
        +String trigger_type
        +DateTime run_timestamp
        +Float execution_duration_seconds
        +String status
        +DateTime created_at
    }

    class AgentInput {
        +UUID id
        +UUID agent_run_id
        +String input_context
        +JSON input_data
        +DateTime created_at
    }

    class AgentOutput {
        +UUID id
        +UUID agent_run_id
        +String output_summary
        +JSON output_data
        +Float confidence_score
        +String status
        +DateTime created_at
    }

    class AgentCitation {
        +UUID id
        +UUID agent_run_id
        +String source_entity_type
        +UUID source_entity_id
        +String citation_type
        +DateTime created_at
    }

    class AgentAction {
        +UUID id
        +UUID agent_run_id
        +String action_type
        +String action_description
        +String action_status
        +DateTime action_timestamp
        +DateTime created_at
    }

    AgentRun "1" -- "*" AgentInput
    AgentRun "1" -- "*" AgentOutput
    AgentRun "1" -- "*" AgentCitation
    AgentRun "1" -- "*" AgentAction
```

---

## 12. Copilot & Vector Search Entities

```mermaid
classDiagram
    class CopilotQuery {
        +UUID id
        +UUID tenant_id
        +UUID user_id
        +String question_text
        +String response_text
        +Float confidence_score
        +String status
        +DateTime query_timestamp
        +DateTime created_at
    }

    class CopilotCitation {
        +UUID id
        +UUID copilot_query_id
        +String source_entity_type
        +UUID source_entity_id
        +String citation_text
        +Float relevance_score
        +DateTime created_at
    }

    class VectorEmbedding {
        +UUID id
        +UUID tenant_id
        +String entity_type
        +UUID entity_id
        +String entity_text
        +Vector embedding
        +DateTime created_at
        +DateTime updated_at
    }

    class DocumentIndex {
        +UUID id
        +UUID tenant_id
        +String document_type
        +UUID document_id
        +String document_text
        +Vector text_embedding
        +DateTime last_indexed
        +DateTime created_at
    }

    CopilotQuery "1" -- "*" CopilotCitation
    VectorEmbedding "*" -- "1" CopilotQuery
    DocumentIndex "*" -- "*" CopilotCitation
```

---

## Relationship Summary

```
Tenant (Root)
├── Organization
│   ├── Site → Building → Zone → Rack → Device
│   │                                      ├── Meter → MeterReading
│   │                                      ├── DeviceSpecification
│   │                                      └── AssetLifecycle
│   │
│   ├── EnergyMetric → CarbonMetric → CarbonCalculation
│   │                                      └── EmissionFactor
│   │
│   ├── KPIDefinition → KPISnapshot → KPIThresholdBreach
│   │                                      └── KPIThreshold
│   │
│   └── Report → ReportVersion → ReportSection
│                                   ├── ReportApproval
│                                   └── ReportSignature
│
├── User → UserRole → Role → RolePermission → Permission
│
├── Evidence → EvidenceVersion, EvidenceMetadata, EvidenceLink, EvidenceRetention
│
├── WorkflowState → Approval → ApprovalComment, ApprovalHistory
│
├── AuditLog → AuditDetail
│
├── AgentRun → AgentInput, AgentOutput, AgentCitation, AgentAction
│
└── CopilotQuery → CopilotCitation
```

---

**Key Design Patterns**:
- ✅ Soft deletes (deleted_at fields)
- ✅ Audit fields (created_by, updated_by, created_at, updated_at)
- ✅ Immutable versions (Version tables for tracking changes)
- ✅ Tenant isolation (tenant_id on all customer-scoped entities)
- ✅ Status tracking (status field for state machines)
- ✅ Extensibility (metadata tables, custom KPIs)
- ✅ Traceability (audit logs, citations, lineage)

---

**Navigation**: [Back to Index](./INDEX.md)
