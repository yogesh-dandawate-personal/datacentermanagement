# Sprint 10: Workflow & Approvals

**Sprint**: 10
**Duration**: July 20 - August 2, 2026 (2 weeks)
**Module**: Workflow & Approval System
**Owner**: Backend + Frontend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements maker-checker-reviewer approval workflow system:
- Multi-stage approval state machine
- Role-based approval requirements
- Comment and discussion trails
- Deadline management and escalation
- Approval history and audit trails
- Workflow UI and notifications

**Dependency**: Evidence Repository (Sprint 9) ✅

---

## Scope & Deliverables

- [x] Workflow state machine (Draft → Review → Approved)
- [x] Approval stage configuration
- [x] Multi-level approval (maker, checker, reviewer)
- [x] Role-based requirements
- [x] Comment and discussion threads
- [x] Deadline tracking
- [x] Escalation rules
- [x] Approval UI
- [x] Notification system

---

## Database Schema

```sql
CREATE TABLE workflow_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50),
    current_state VARCHAR(50),
    previous_state VARCHAR(50),
    state_changed_at TIMESTAMP,
    changed_by VARCHAR(255),
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50),
    approval_stage VARCHAR(50),
    required_role VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    assigned_to VARCHAR(255),
    due_date DATE,
    completed_date TIMESTAMP,
    completed_by VARCHAR(255),
    decision VARCHAR(50),
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(entity_id, status, due_date)
);

CREATE TABLE approval_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_id UUID NOT NULL REFERENCES approvals(id),
    comment_text TEXT NOT NULL,
    commented_by VARCHAR(255) NOT NULL,
    comment_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

```
POST   /api/v1/tenants/{tenant_id}/workflows
       Create workflow
       Request: {entity_id, entity_type, config}

GET    /api/v1/workflows/{workflow_id}
       Get workflow status

PATCH  /api/v1/approvals/{approval_id}
       Approve/reject
       Request: {decision, comments}

GET    /api/v1/organizations/{org_id}/approval-queue
       List pending approvals
       Query: ?assigned_to=user_email&status=pending

POST   /api/v1/approvals/{approval_id}/comments
       Add approval comment
       Request: {text}
```

---

## Workflow States

```
Draft
  ↓ (Submit)
ReadyForReview
  ↓ (Checker reviews)
  ├→ Checked (Approve)
  └→ ReviewRequested (Request changes → back to Draft)
  ↓
ReadyForApproval
  ↓ (Reviewer reviews)
  ├→ Approved (Sign off → Archive)
  └→ RequestedChanges (Back to Checked)
```

---

**Target**: July 20 - August 2, 2026
