# iNetZero Architecture Diagrams

**Version**: 1.0.0
**Last Updated**: March 9, 2026
**Status**: Complete for Sprint 1

---

## 📋 Diagram Index

This directory contains comprehensive architecture diagrams for the iNetZero ESG platform, suitable for development, code generation, and system design reviews.

### 1. **Domain Model** (`domain-model.md`)
- **Purpose**: Class and entity diagrams showing all domain objects
- **Diagrams**:
  - Core Entity Diagram (Tenant, Organization, Site, Zone, Rack, Device)
  - Energy & Carbon Entities (Telemetry, Metrics, Factors)
  - Workflow & Approval Entities (Report, Workflow, AuditLog)
  - Evidence & Copilot Entities

### 2. **Sequence Diagrams** (`sequence-diagrams.md`)
- **Purpose**: Show interactions between systems for key user journeys
- **Diagrams**:
  - Telemetry Ingestion Sequence
  - Carbon Calculation Workflow
  - Approval Workflow Sequence
  - Copilot Query Resolution
  - Dashboard Data Loading

### 3. **State Diagrams** (`state-diagrams.md`)
- **Purpose**: State machines for critical workflows
- **Diagrams**:
  - Report Approval Workflow (Draft → Approved → Archived)
  - Telemetry Validation States
  - Calculation Processing States
  - Evidence Lifecycle States

### 4. **Component Diagrams** (`component-diagrams.md`)
- **Purpose**: System components and their relationships
- **Diagrams**:
  - Backend Service Components
  - Agent Components
  - Frontend Components
  - Data Processing Pipeline
  - Integration Points

### 5. **Deployment Diagram** (`deployment-diagram.md`)
- **Purpose**: Infrastructure and deployment topology
- **Diagrams**:
  - Development Environment (Docker Compose)
  - Production Kubernetes Cluster
  - Database Topology (Primary, Replicas)
  - External Service Integrations

### 6. **Event Flow Diagrams** (`event-flow-diagrams.md`)
- **Purpose**: Asynchronous event-driven flows
- **Diagrams**:
  - Telemetry Ingestion Event Flow
  - Metric Calculation Event Flow
  - Approval Notification Event Flow
  - Real-time Dashboard Update Flow

### 7. **API Interaction Diagrams** (`api-interaction-diagrams.md`)
- **Purpose**: REST API relationships and call flows
- **Diagrams**:
  - Authentication Flow (OAuth2/OIDC)
  - Tenant Scoping & Authorization
  - API Endpoint Hierarchy
  - Request/Response Patterns

### 8. **Data Flow Diagram** (`data-flow-diagram.md`)
- **Purpose**: Information flow through system
- **Diagrams**:
  - End-to-End Data Flow (Ingestion → Processing → Reporting)
  - Telemetry Processing Pipeline
  - Report Generation Flow
  - Evidence Repository Flow

---

## 🎯 Quick Start for Developers

### By Role:

**Backend Developers**:
- Start with: Domain Model → Component Diagrams → Sequence Diagrams
- Reference: API Interaction Diagrams, Event Flow Diagrams

**Frontend Developers**:
- Start with: Component Diagrams → Sequence Diagrams (user journeys)
- Reference: API Interaction Diagrams, State Diagrams (UI states)

**DevOps/Infrastructure**:
- Start with: Deployment Diagram → Event Flow Diagrams
- Reference: Component Diagrams (for service dependencies)

**QA/Testing**:
- Start with: Sequence Diagrams → State Diagrams
- Reference: Domain Model (test data structure)

### By Feature:

**Telemetry Ingestion**:
- Sequence: Telemetry Ingestion Sequence
- State: Telemetry Validation States
- Event: Telemetry Ingestion Event Flow
- Data Flow: Telemetry Processing Pipeline

**Carbon Accounting**:
- Sequence: Carbon Calculation Workflow
- State: Calculation Processing States
- Event: Metric Calculation Event Flow
- Domain: Energy & Carbon Entities

**Approval Workflows**:
- Sequence: Approval Workflow Sequence
- State: Report Approval Workflow
- Event: Approval Notification Event Flow
- API: Request/Response Patterns

**Executive Copilot**:
- Sequence: Copilot Query Resolution
- Domain: Evidence & Copilot Entities
- Data Flow: Report Generation Flow

---

## 📐 Diagram Formats

All diagrams use **Mermaid** syntax, which is:
- ✅ Natively supported in GitHub markdown
- ✅ Rendererable in VS Code with extensions
- ✅ Exportable to PNG, SVG, PDF
- ✅ Version-controllable (plain text)

To view/export diagrams:
1. **GitHub**: Open `.md` files, diagrams render automatically
2. **Mermaid Editor**: https://mermaid.live (paste code, export)
3. **VS Code**: Install "Markdown Preview Mermaid Support" extension
4. **Command Line**:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i diagram.md -o diagram.png
   ```

---

## 🔄 Diagram Relationships

```
Domain Model
    ↓
Component Diagrams ←→ Sequence Diagrams
    ↓                      ↓
Deployment Diagram    State Diagrams
    ↓                      ↓
Event Flow Diagrams ←→ Data Flow Diagram
    ↓
API Interaction Diagrams
```

---

## ✅ Development Workflow

1. **Design Phase**: Review diagrams in this order:
   - Domain Model (what entities exist?)
   - Component Diagrams (how do they interact?)
   - Sequence Diagrams (what's the flow?)

2. **Implementation Phase**:
   - Use Component Diagrams for code structure
   - Reference State Diagrams for workflow implementation
   - Follow API Interaction Diagrams for endpoint contracts

3. **Testing Phase**:
   - Use Sequence Diagrams to design test cases
   - Use State Diagrams to verify state transitions
   - Use Event Flow Diagrams to test async behavior

4. **Deployment Phase**:
   - Follow Deployment Diagram for infrastructure setup
   - Verify all integrations in Event Flow Diagrams
   - Validate API contracts in API Interaction Diagrams

---

## 🔧 Maintaining Diagrams

### When to Update Diagrams:
- ✅ New domain entities added (update Domain Model)
- ✅ API endpoints added/changed (update API Interaction)
- ✅ New services added (update Component Diagrams)
- ✅ Workflow states added (update State Diagrams)
- ✅ Event types added (update Event Flow Diagrams)

### Version Control:
- Diagrams are **plain text** (Mermaid syntax)
- Commit all changes to git
- Include diagram updates with code PRs
- Review diagram changes in code review

### Tools for Editing:
- **Markdown Editor**: Any text editor (VS Code, Sublime, etc.)
- **Mermaid Live Editor**: https://mermaid.live
- **IDE Plugins**: Mermaid support for VSCode, IntelliJ

---

## 📚 Related Documentation

- **PRD**: `/docs/PRD.md` (high-level requirements)
- **Sprint Plans**: `/docs/implementation/sprint-X-plan.md` (implementation details)
- **OpenAPI Spec**: `/docs/openapi.json` (API contract)
- **Database Schema**: `/docs/schema/` (DDL and migrations)

---

**Navigation**:
- [Domain Model](./domain-model.md)
- [Sequence Diagrams](./sequence-diagrams.md)
- [State Diagrams](./state-diagrams.md)
- [Component Diagrams](./component-diagrams.md)
- [Deployment Diagram](./deployment-diagram.md)
- [Event Flow Diagrams](./event-flow-diagrams.md)
- [API Interaction Diagrams](./api-interaction-diagrams.md)
- [Data Flow Diagram](./data-flow-diagram.md)
