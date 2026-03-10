# Agent Audit Trails - Quick Reference Guide

## Quick Start

### 1. Log an Agent Run
```python
from app.services.agent_logger import AgentLoggerService
from decimal import Decimal

logger = AgentLoggerService(db)

run_id = logger.log_agent_run(
    tenant_id=tenant.id,
    agent_type="carbon_agent",
    input_context={"metric_type": "scope_2"},
    tools_used=["database", "calculation"],
    output_summary={"result": 45000},
    citations=["metric-123"],
    confidence_score=Decimal("0.95"),
    requires_approval=False,
)
```

### 2. Validate Before Action
```python
from app.services.agent_guardrails import AgentGuardrailsService

guardrails = AgentGuardrailsService(db)

result = guardrails.validate_agent_action(
    run_id=uuid.UUID(run_id),
    tenant_id=tenant.id,
    agent_type="carbon_agent",
    action_type="CREATE",
    impact_level="high",
    citations=["metric-123"],
    referenced_entities={},
    input_context={},
    user_id=user.id
)

if not result["is_valid"]:
    # Handle validation failure
    pass

if result["requires_approval"]:
    # Wait for human approval
    pass
```

### 3. Log a Decision
```python
decision_id = logger.log_agent_decision(
    run_id=uuid.UUID(run_id),
    tenant_id=tenant.id,
    decision_type="CREATE_RECORD",
    action="Create carbon calculation",
    impact_level="high",
    requires_approval=result["requires_approval"],
)
```

### 4. Handle Violations
```python
if not result["checks"]["fabrication"]["passed"]:
    logger.log_guardrail_violation(
        run_id=uuid.UUID(run_id),
        tenant_id=tenant.id,
        violation_type="fabrication",
        description=result["checks"]["fabrication"]["error"],
        severity="critical"
    )
```

---

## API Endpoints

### Query Audit Trail
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/agents/runs?agent_type=carbon_agent&limit=50"
```

### Get Run Details
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/agents/runs/{run_id}"
```

### List Violations
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/agents/violations?severity=critical"
```

### Approve Decision
```bash
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approval_reason": "Data verified",
    "execute": true
  }' \
  "http://localhost:8000/api/v1/admin/agents/decisions/{decision_id}/approve"
```

---

## Decision Flow

### For READ Operations
```
Agent Read → Log Run → Auto-Approved → Execute
(No approval needed, no decisions logged)
```

### For LOW-IMPACT CREATE
```
Agent Create → Log Run → Validate → Auto-Approved → Execute
(Auto-approved by policy)
```

### For HIGH-IMPACT CREATE
```
Agent Create → Log Run → Validate → Decision Logged →
PENDING APPROVAL → Human Review → Approved/Rejected →
Execute/Cancel
```

### If Fabrication Detected
```
Agent Uses ID → Validate → ID Not Found → Log Violation →
Operation Blocked
(No decision logged, operation never executes)
```

---

## Data Models

### AgentRun
| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Unique run ID |
| agent_type | String | carbon_agent, kpi_agent, etc. |
| input_context | JSON | What triggered the agent |
| tools_used | Array | External services called |
| output_summary | JSON | Result produced |
| citations | Array | Source data IDs |
| confidence_score | Decimal(5,2) | 0.00-1.00 confidence |
| requires_approval | Boolean | Approval needed? |
| approved_by | UUID | User who approved |
| status | String | completed, approved, failed |
| created_at | DateTime | Immutable timestamp |

### AgentDecision
| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Unique decision ID |
| agent_run_id | UUID | Which run |
| decision_type | String | CREATE_RECORD, MODIFY_DATA |
| action | String | Human description |
| impact_level | String | low, medium, high, critical |
| requires_approval | Boolean | Approval needed? |
| approval_status | String | pending, approved, rejected |
| executed | Boolean | Did it happen? |
| created_at | DateTime | When logged |

### AgentGuardrailViolation
| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Unique violation ID |
| agent_run_id | UUID | Which run caused it |
| violation_type | String | fabrication, access_control, etc. |
| description | String | What was violated |
| severity | String | low, medium, high, critical |
| resolved | Boolean | Has it been fixed? |
| resolved_by | UUID | User who resolved |
| created_at | DateTime | When detected |

---

## Guardrail Rules

### Fabrication Detection
- All citations must exist in database
- Must belong to same tenant
- Cannot be deleted/archived

### Approval Gating
- READ: Never requires approval
- ANALYZE: Never requires approval
- CREATE + LOW impact: Auto-approved
- CREATE/MODIFY + MEDIUM: Requires approval
- CREATE/MODIFY/DELETE + HIGH/CRITICAL: Requires approval
- DELETE: Always requires approval

### Data Integrity
- Cannot modify approved records
- Cannot delete (agents)
- Can only create drafts
- Maintains lineage

### Access Control
- Tenant must be active
- User must be active
- User must have permissions
- Entity must belong to tenant

### Cross-Tenant Isolation
- Agent only operates in its tenant
- Input context tenant must match
- No mixing of tenant data

---

## Query Examples

### Get all violations in last 7 days
```sql
SELECT * FROM agent_guardrail_violations
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY severity DESC, created_at DESC;
```

### Get approval-pending decisions
```sql
SELECT * FROM agent_decisions
WHERE approval_status = 'pending'
AND requires_approval = true
ORDER BY impact_level DESC;
```

### Get fabrication violations by agent
```sql
SELECT ar.agent_type, COUNT(*) as count
FROM agent_guardrail_violations agv
JOIN agent_runs ar ON agv.agent_run_id = ar.id
WHERE agv.violation_type = 'fabrication'
GROUP BY ar.agent_type
ORDER BY count DESC;
```

### Get agent run success rate
```sql
SELECT
  agent_type,
  COUNT(CASE WHEN status = 'completed' THEN 1 END)::float /
  COUNT(*) * 100 as success_rate
FROM agent_runs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY agent_type;
```

---

## Troubleshooting

### "Fabrication Detected"
**Cause**: Agent referenced ID that doesn't exist
**Fix**:
1. Check citations array in run
2. Verify metric/factor IDs in database
3. Resolve violation with notes
4. Re-run agent with correct IDs

### "Requires Approval"
**Cause**: High-impact action needs human review
**Fix**:
1. Check pending decisions: `GET /api/v1/admin/agents/decisions-pending`
2. Review the decision details
3. Approve or reject via API
4. Monitor for similar patterns

### "Cross-Tenant Operation"
**Cause**: Agent tried to access different tenant
**Fix**:
1. Check input_context.tenant_id
2. Verify it matches agent's tenant
3. Update config to use correct tenant
4. This is a critical security issue - escalate

### "Access Control Violation"
**Cause**: User inactive or insufficient permissions
**Fix**:
1. Verify user.is_active = true
2. Check user has admin role
3. Verify tenant is active
4. Escalate to security team if suspicious

---

## Performance Tips

### For Query Performance
- Always filter by tenant_id
- Use created_at index for date ranges
- Limit to last 100 records initially
- Use pagination for large result sets

### For Write Performance
- Batch violations reporting (queue 10, flush)
- Don't wait for logger confirmation in hot path
- Use async logging if available
- Monitor slow queries with explain

### For Storage Efficiency
- Archive old runs after 90 days
- Compress JSON blobs quarterly
- Partition by tenant_id
- Drop indices on archived tables

---

## Admin Dashboard Queries

### Daily Summary
```python
# Show today's metrics
stats = logger_service.get_agent_audit_trail(
    tenant_id=tenant_id,
    date_from=datetime.now().replace(hour=0, minute=0),
    limit=1000
)
```

### Weekly Violation Report
```python
# Top violations this week
violations = db.query(AgentGuardrailViolation)\
  .filter(AgentGuardrailViolation.tenant_id == tenant_id)\
  .filter(AgentGuardrailViolation.created_at >=
          datetime.now() - timedelta(days=7))\
  .group_by(AgentGuardrailViolation.violation_type)\
  .all()
```

### Monthly Agent Report
```python
# Agent performance metrics
runs = logger_service.get_agent_audit_trail(
    tenant_id=tenant_id,
    date_from=datetime(year, month, 1),
    limit=10000
)
# Analyze runs, decisions, violations
```

---

## Integration Checklist

- [ ] Import AgentLoggerService in agent executor
- [ ] Import AgentGuardrailsService before agent runs
- [ ] Register admin routes in FastAPI app
- [ ] Add tenant isolation checks in API middleware
- [ ] Create admin user with proper roles
- [ ] Set up logging to CloudWatch/ELK
- [ ] Configure alerts for critical violations
- [ ] Document approval process for ops team
- [ ] Train admins on dashboard usage
- [ ] Monitor first week for issues

---

## Related Documentation

- **Full Implementation**: `/docs/implementation/SPRINT_12_AGENT_AUDIT_TRAILS.md`
- **API Docs**: `/docs/api/agent_admin.md`
- **Testing Guide**: `/docs/testing/agent_audit_testing.md`
- **Security Guide**: `/docs/security/agent_governance.md`

