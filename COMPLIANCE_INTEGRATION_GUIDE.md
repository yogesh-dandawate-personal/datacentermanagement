# Compliance Dashboard - Backend Integration Guide

**Last Updated:** March 10, 2026
**Status:** Ready for Implementation
**API Version:** v1

---

## Quick Start

### 1. Backend Setup

The Compliance Dashboard frontend is ready and uses mock data. To connect to your backend:

#### Step 1: Implement Backend Endpoints

Create the following endpoints in your backend:

```python
# Django/FastAPI Example
@router.get("/api/v1/compliance/status")
def get_compliance_status(org_id: str):
    """Return overall compliance status"""
    return {
        "overallStatus": "On Track" | "At Risk" | "Non-Compliant",
        "scorePercentage": 0-100,
        "requiredMetricsCount": int,
        "submittedMetricsCount": int,
        "gapCount": int,
        "criticalGapCount": int,
        "pendingTasksCount": int,
        "overdueTasks": int,
        "frameworks": {
            "gri": {"status": "On Track", "score": 78},
            "tcfd": {"status": "At Risk", "score": 68},
            "cdp": {"status": "At Risk", "score": 70}
        }
    }

@router.get("/api/v1/compliance/score")
def get_compliance_score(org_id: str):
    """Return compliance score trends"""
    return {
        "overallScore": 72,
        "griScore": 78,
        "tcfdScore": 68,
        "cdpScore": 70,
        "lastUpdated": "2025-03-10T18:30:00Z",
        "trend": [
            {
                "date": "2025-01",
                "overallScore": 65,
                "griScore": 70,
                "tcfdScore": 60,
                "cdpScore": 65
            }
            # ... monthly data
        ]
    }

@router.get("/api/v1/compliance/matrix/{framework}")
def get_compliance_matrix(org_id: str, framework: str):
    """Return compliance matrix for a framework (GRI, TCFD, CDP)"""
    return {
        "framework": "GRI",
        "totalRequirements": 18,
        "complete": 12,
        "inProgress": 4,
        "notStarted": 2,
        "completionPercentage": 67,
        "requirements": [
            {
                "id": "gri-req-1",
                "framework": "GRI",
                "code": "GRI-1",
                "title": "Requirement 1: Description",
                "description": "Full requirement description",
                "status": "Complete" | "In Progress" | "Not Started",
                "completionPercentage": 100,
                "lastUpdated": "2025-03-10T18:30:00Z",
                "evidence": ["doc-1", "doc-2"],
                "assignedTo": "John Smith",
                "dueDate": "2025-04-30"
            }
            # ... more requirements
        ]
    }

@router.get("/api/v1/compliance/gaps")
def get_compliance_gaps(org_id: str):
    """Return identified compliance gaps"""
    return [
        {
            "id": "gap-1",
            "framework": "TCFD",
            "requirement": "Climate Risk Assessment",
            "gapDescription": "Missing comprehensive climate scenario analysis...",
            "severity": "Critical" | "High" | "Medium" | "Low",
            "identifiedDate": "2025-01-15",
            "targetRemediationDate": "2025-06-30",
            "owner": "John Smith",
            "ownerEmail": "john.smith@company.com",
            "relatedTasks": ["task-1", "task-2"],
            "evidence": ["doc-3"]
        }
        # ... more gaps
    ]

@router.get("/api/v1/compliance/tasks")
def get_remediation_tasks(org_id: str):
    """Return remediation tasks"""
    return [
        {
            "id": "task-1",
            "title": "Conduct Climate Scenario Analysis",
            "description": "Perform detailed climate risk analysis...",
            "gapId": "gap-1",
            "framework": "TCFD",
            "status": "Assigned" | "In Progress" | "Completed",
            "priority": "P0" | "P1" | "P2" | "P3",
            "assignedTo": "John Smith",
            "assignedEmail": "john.smith@company.com",
            "createdDate": "2025-02-01",
            "dueDate": "2025-05-30",
            "completedDate": null,
            "progressPercentage": 45,
            "notes": "Task notes...",
            "deliverables": ["Report", "Assessment"]
        }
        # ... more tasks
    ]

@router.get("/api/v1/compliance/targets")
def get_target_tracking(org_id: str):
    """Return target tracking data"""
    return [
        {
            "id": "target-1",
            "name": "Emissions Reduction Target",
            "framework": "TCFD",
            "targetValue": 50,
            "targetUnit": "%",
            "currentValue": 28,
            "targetDate": "2030-12-31",
            "startDate": "2020-01-01",
            "progressPercentage": 56,
            "trend": [
                {
                    "date": "2020-01",
                    "value": 0,
                    "forecast": 0
                }
                # ... monthly data
            ]
        }
        # ... more targets
    ]

@router.get("/api/v1/compliance/kpi-targets")
def get_kpi_targets(org_id: str):
    """Return KPI targets (PUE, CUE, WUE, ERE)"""
    return [
        {
            "kpiName": "Power Usage Effectiveness",
            "kpiCode": "PUE",
            "targetValue": 1.2,
            "targetUnit": "ratio",
            "standardValue": 1.5,
            "currentValue": 1.35,
            "currentDate": "2025-03-10",
            "progress": 56,
            "status": "On Track" | "At Risk" | "Behind",
            "historicalData": [
                {
                    "date": "2024-01",
                    "value": 1.55
                }
                # ... monthly data
            ],
            "forecastedValue": 1.25,
            "forecastDate": "2025-12-31"
        }
        # ... CUE, WUE, ERE
    ]

@router.get("/api/v1/compliance/audit-trail")
def get_audit_trail(org_id: str):
    """Return compliance audit trail"""
    return [
        {
            "id": "audit-1",
            "timestamp": "2025-03-08T10:30:00Z",
            "eventType": "requirement_updated",
            "description": "GRI-15 requirement status updated to In Progress",
            "changedBy": "Jane Doe",
            "changedByEmail": "jane.doe@company.com",
            "requirementId": "gri-req-15",
            "previousValue": "Not Started",
            "newValue": "In Progress",
            "notes": null
        }
        # ... more entries
    ]
```

#### Step 2: Update Frontend API Service

The API methods are already added to `frontend/src/services/api.ts`. They currently use mock data.

Update the hooks in `frontend/src/hooks/useCompliance.ts` to remove mock data and call the real API:

```typescript
export function useComplianceStatus(): UseApiState<ComplianceStatusSummary> {
  return useApi(
    () => api.getComplianceStatus(),  // Replace mock data call
    []
  )
}
```

#### Step 3: Test Integration

1. Start backend server with new endpoints
2. Update API base URL if needed in `frontend/src/services/api.ts`
3. Remove `shouldUseMockData()` conditions or set to false
4. Run frontend: `npm run dev`
5. Navigate to `/compliance` route
6. Verify all data loads from backend

---

## API Request/Response Examples

### GET /api/v1/compliance/status

**Request:**
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/compliance/status
```

**Response (200):**
```json
{
  "overallStatus": "At Risk",
  "scorePercentage": 72,
  "requiredMetricsCount": 45,
  "submittedMetricsCount": 32,
  "gapCount": 8,
  "criticalGapCount": 2,
  "pendingTasksCount": 15,
  "overdueTasks": 3,
  "frameworks": {
    "gri": {
      "status": "On Track",
      "score": 78
    },
    "tcfd": {
      "status": "At Risk",
      "score": 68
    },
    "cdp": {
      "status": "At Risk",
      "score": 70
    }
  }
}
```

---

## Database Schema (Reference)

### ComplianceRequirement Table
```sql
CREATE TABLE compliance_requirements (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL,
    framework VARCHAR(50) NOT NULL,  -- GRI, TCFD, CDP
    code VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,  -- Complete, In Progress, Not Started
    completion_percentage INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_to VARCHAR(255),
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    INDEX idx_framework (framework),
    INDEX idx_status (status)
);
```

### ComplianceGap Table
```sql
CREATE TABLE compliance_gaps (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    requirement VARCHAR(500) NOT NULL,
    gap_description TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL,  -- Critical, High, Medium, Low
    identified_date DATE NOT NULL,
    target_remediation_date DATE NOT NULL,
    owner_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_framework (framework),
    INDEX idx_severity (severity)
);
```

### RemediationTask Table
```sql
CREATE TABLE remediation_tasks (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL,
    gap_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    framework VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- Assigned, In Progress, Completed
    priority VARCHAR(50) NOT NULL,  -- P0, P1, P2, P3
    assigned_to_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    completed_date DATE,
    progress_percentage INT DEFAULT 0,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (gap_id) REFERENCES compliance_gaps(id),
    FOREIGN KEY (assigned_to_id) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_priority (priority)
);
```

---

## Feature Implementation Roadmap

### Phase 1: Current (Completed)
- ✅ Frontend UI/UX complete
- ✅ Mock data integration
- ✅ Component library created
- ✅ Navigation integrated

### Phase 2: Backend Integration (Next)
- API endpoint implementation
- Database schema creation
- Real data binding
- Testing

### Phase 3: Enhancements
- PDF report export
- Email notifications
- Approval workflow integration
- Advanced filtering
- Custom dashboards

### Phase 4: Advanced Features
- Benchmarking
- Historical comparisons
- Automated checks
- Real-time alerts
- Mobile app support

---

## Testing Guide

### Unit Tests (Recommended)
```typescript
// Example: Test ComplianceScore component
import { render, screen } from '@testing-library/react'
import { ComplianceScore } from './ComplianceScore'

describe('ComplianceScore', () => {
  it('displays overall score correctly', () => {
    const mockData = {
      overallScore: 72,
      griScore: 78,
      tcfdScore: 68,
      cdpScore: 70,
      lastUpdated: '2025-03-10T18:30:00Z',
      trend: []
    }
    render(<ComplianceScore data={mockData} loading={false} />)
    expect(screen.getByText('72')).toBeInTheDocument()
  })
})
```

### Integration Tests (Recommended)
```typescript
// Test data flow from API to component
describe('Compliance Dashboard', () => {
  it('fetches and displays compliance status', async () => {
    render(<Compliance />)

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('On Track')).toBeInTheDocument()
    })
  })
})
```

---

## Troubleshooting

### Issue: Mock data not loading
**Solution:** Check `frontend/src/services/api.ts` for `shouldUseMockData()` function

### Issue: API endpoints not responding
**Solution:** Verify backend server is running and endpoints are implemented

### Issue: Type errors after API integration
**Solution:** Ensure backend responses match TypeScript interfaces in `frontend/src/types/compliance.ts`

### Issue: Performance issues with large datasets
**Solution:** Implement pagination in gap and task lists

---

## Support

For questions or issues during integration:
1. Check this guide first
2. Review the component files for implementation details
3. Check TypeScript interfaces for expected data format
4. Review mock data for expected structure

---

## Checklist for Integration

- [ ] Backend endpoints implemented
- [ ] Database schema created
- [ ] API authentication configured
- [ ] Data populated in database
- [ ] Frontend API calls enabled
- [ ] Mock data disabled
- [ ] All endpoints tested
- [ ] Error handling verified
- [ ] Loading states tested
- [ ] Response time acceptable
- [ ] UI displays real data correctly
- [ ] Filters and search working
- [ ] Charts rendering properly
- [ ] Responsive design verified
- [ ] Ready for production

---

**Ready to integrate!** 🚀
