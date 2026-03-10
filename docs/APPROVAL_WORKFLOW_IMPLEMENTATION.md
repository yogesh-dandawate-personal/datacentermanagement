# Approval Workflow Dashboard Implementation Guide

**Sprint 12 - Critical Gap**
**Status**: COMPLETE ✓
**Date**: March 10, 2026

---

## Overview

Implemented a comprehensive Approval Workflow Dashboard system that enables users to manage, track, and approve critical requests (reports, calculations, metrics) with full audit trails, comments, and SLA tracking.

## Architecture

### Directory Structure

```
frontend/src/
├── pages/
│   └── Approvals.tsx                 # Main dashboard page
├── components/
│   ├── ApprovalCard.tsx              # Card component for list view
│   ├── ApprovalDetail.tsx            # Full detail view
│   ├── ApprovalTimeline.tsx          # Visual timeline
│   ├── ApprovalFilters.tsx           # Filter controls
│   └── CommentThread.tsx             # Comments section
├── hooks/
│   └── useApprovals.ts               # Custom hooks for data
└── types/
    └── approval.ts                   # TypeScript type definitions
```

## Core Components

### 1. Approvals Dashboard Page (`/approvals`)

**Location**: `/frontend/src/pages/Approvals.tsx`

Main page containing:
- Statistics cards (Pending, Approved, Rejected counts)
- Advanced filtering and search controls
- Paginated approval list with card view
- Navigation to detail pages
- Attention section for overdue/escalated items

**Key Features**:
- Grid layout for statistics (responsive)
- Real-time filtering with search
- Pagination (10 items per page)
- Empty state handling
- Loading indicators
- Error handling

**Usage**:
```tsx
import { Approvals } from './pages/Approvals'

// Route in App.tsx
<Route path="/approvals" element={<ProtectedRoute><Layout><Approvals /></Layout></ProtectedRoute>} />
```

### 2. Approval Card Component

**Location**: `/frontend/src/components/ApprovalCard.tsx`

Displays individual approval request in card format.

**Props**:
```typescript
interface ApprovalCardProps {
  approval: ApprovalRequest
  onApprove: (id: string) => void
  onReject: (id: string) => void
  onComment: (id: string) => void
  onClick: (id: string) => void
  isLoading?: boolean
}
```

**Displays**:
- Approval name and ID
- Status badge with color coding
- Type (report/calculation/metric) with icon
- Submitter, submitted date, type, priority
- Approval trail (maker → checker → reviewer)
- Due date with SLA warnings
- Escalation status
- Quick action buttons
- Comment count

**Status Colors**:
- Draft: Gray
- Under Review: Blue
- Approved: Green
- Rejected: Red

### 3. Approval Detail Page Component

**Location**: `/frontend/src/components/ApprovalDetail.tsx`

Full approval request view with:
- Complete approval information
- Data being reviewed (metrics, calculations, evidence)
- Approval timeline
- Comment thread
- Action buttons (approve/reject with reason dialogs)

**Features**:
- Detailed metadata display
- SLA and deadline information
- Overdue/escalation alerts
- Modular data display for metrics/calculations/evidence
- Approve dialog with optional reason
- Reject dialog with mandatory feedback
- Comments thread integration

### 4. Approval Timeline Component

**Location**: `/frontend/src/components/ApprovalTimeline.tsx`

Visual timeline of approval progression.

**Shows**:
- Status progression (Draft → Under Review → Approved/Rejected)
- Actor names and timestamps
- Comments at each stage
- Visual timeline with connector lines
- Current status badge

**Status Nodes**:
- Submitted (Draft)
- Under Review (Review)
- Approved (Success)
- Rejected (Error)

### 5. Comment Thread Component

**Location**: `/frontend/src/components/CommentThread.tsx`

Discussion area for approval feedback.

**Features**:
- Display comments with author info
- User avatars with initials fallback
- Relative timestamps (e.g., "2m ago")
- Edit indicators
- Add new comment form
- Post comment button
- Read-only mode for approved/rejected requests

### 6. Approval Filters Component

**Location**: `/frontend/src/components/ApprovalFilters.tsx`

Advanced filtering and search controls.

**Filters**:
- **Search**: By name, submitter, or approval ID
- **Assignee**: All, Me, My Team
- **Status** (advanced): Draft, Under Review, Approved, Rejected
- **Type** (advanced): Report, Calculation, Metric
- **Sort**: Due Date, Submitted Date, Priority, Status
- **Order**: Ascending, Descending

**Features**:
- Show/hide advanced filters toggle
- Active filter display with clear option
- Real-time filtering
- Sort direction toggle
- Multi-select for status and type

## Custom Hooks

### useApprovals(filter, sort, page, pageSize)

**Location**: `/frontend/src/hooks/useApprovals.ts`

Fetches and manages approval list.

```typescript
const approvalsData = useApprovals(
  { status: ['under_review'], type: ['report'] },
  { field: 'due_date', direction: 'asc' },
  1,
  10
)

// Returns:
{
  data: {
    approvals: ApprovalRequest[],
    total: number,
    pages: number,
    pendingCount: number
  },
  loading: boolean,
  error: null
}
```

**Features**:
- Client-side filtering and sorting
- Pagination support
- Filter by status, type, assignee
- Sort by multiple fields
- Search capability

### useApprovalDetail(approvalId)

Fetches single approval request.

```typescript
const { data: approval, loading, error } = useApprovalDetail('APR-001')
```

### usePendingApprovalsCount()

Gets count of pending approvals (refreshes every 30s).

```typescript
const pendingCount = usePendingApprovalsCount()
// Used in Layout for notification badge
```

### useApprovalAction(approvalId)

Handles approval mutations (approve, reject, comment).

```typescript
const { approve, reject, addComment, loading, error } = useApprovalAction(approvalId)

await approve('Looks good!')
await reject('Please revise the calculations')
await addComment('Need more details on methodology')
```

## Type Definitions

**Location**: `/frontend/src/types/approval.ts`

### ApprovalStatus
```typescript
type ApprovalStatus = 'draft' | 'under_review' | 'approved' | 'rejected'
```

### ApprovalType
```typescript
type ApprovalType = 'report' | 'calculation' | 'metric'
```

### ApprovalRequest
Complete approval request object:
- `id`: Unique identifier
- `name`: Request title
- `type`: Type of request
- `status`: Current status
- `submitter`: Who submitted
- `submitterAvatar`: Avatar URL
- `submittedDate`: ISO date
- `dueDate`: Target completion date
- `slaDeadline`: SLA deadline
- `priority`: Low/Medium/High
- `description`: Request details
- `assignees`: Assigned reviewers
- `comments`: Discussion thread
- `timeline`: Status progression history
- `approvalTrail`: Maker/Checker/Reviewer info
- `data`: Metrics/calculations/evidence
- `isOverdue`: Boolean flag
- `isEscalated`: Boolean flag
- `escalatedTo`: Manager name (if escalated)
- `previousVersions`: Version history

## Integration with Layout

### Navigation Addition

The Approvals link has been added to the main sidebar navigation:

```typescript
{
  icon: CheckSquare,
  label: 'Approvals',
  href: '/approvals',
  color: 'text-indigo-400'
}
```

### Notification Badge

The bell icon in the header now shows pending approval count:
- Updates every 30 seconds
- Displays badge with count
- Clicking navigates to /approvals page
- Real-time count updates

## Mock Data

**Location**: `/frontend/src/hooks/useApprovals.ts`

Includes 4 realistic mock approval requests:
- **APR-001**: Q1 2026 Energy Report (Under Review)
- **APR-002**: Carbon Offset Calculation (Draft)
- **APR-003**: KPI Performance Metrics (Approved)
- **APR-004**: Water Usage Report (Rejected/Overdue)

Mock data includes:
- Full approval trails
- Comments with timestamps
- Timeline entries
- Various status types
- Priority levels
- Escalation scenarios

## Design System Integration

### Colors
- **Primary Blue**: Primary actions (#2563eb)
- **Green**: Success/Approved (#16a34a)
- **Red**: Danger/Rejected (#dc2626)
- **Yellow**: Warning/Approaching deadline (#eab308)
- **Gray**: Draft/Inactive (#64748b)

### Components Used
- Card, CardHeader, CardContent, CardTitle, CardDescription
- Button (primary, secondary, outline, ghost, danger)
- Badge (with status colors)
- Input (for search)
- Select (for filtering)
- Checkbox (for multi-select)
- Alert (for warnings)
- Dialog (for action confirmations)
- Pagination
- Spinner
- EmptyState

### Spacing
- 8px base unit
- Responsive gaps (4-6 gap units)
- Mobile-optimized padding

### Icons (Lucide)
- CheckSquare: Approvals nav
- Clock: Timeline/Due dates
- CheckCircle: Approved status
- XCircle: Rejected status
- AlertCircle: Warnings
- FileText/Calculator/TrendingUp: Approval types
- MessageSquare: Comments
- Send: Post comment
- Search: Search input
- Filter: Advanced filters

## Styling

### Dark Mode
- Slate-900/950 backgrounds
- White text (#ffffff)
- Slate-400/500 muted text
- Glass-morphism effects with backdrop blur
- Gradient overlays

### Responsive Design
- Mobile first approach
- 1 column on mobile (max-width: 768px)
- 2-3 columns on tablet
- Full layout on desktop
- Touch-friendly buttons (minimum 44px)
- Adaptive font sizes

### Accessibility
- ARIA labels on all interactive elements
- Keyboard navigation support
- Focus rings on buttons
- Color contrast compliance
- Semantic HTML structure
- Skip to content link

## API Integration Patterns

### Current Implementation
Uses mock data for development. Ready to integrate with real API:

```typescript
// Pattern for real API integration
async function getApprovals(filter, sort, page) {
  const response = await api.request('/approvals', {
    params: {
      status: filter.status?.join(','),
      type: filter.type?.join(','),
      search: filter.search,
      page,
      sort: sort.field,
      order: sort.direction
    }
  })
  return response.data
}
```

### Expected API Endpoints
- `GET /api/v1/approvals` - List with filters
- `GET /api/v1/approvals/{id}` - Detail
- `POST /api/v1/approvals/{id}/approve` - Approve
- `POST /api/v1/approvals/{id}/reject` - Reject
- `POST /api/v1/approvals/{id}/comments` - Add comment
- `GET /api/v1/approvals/count/pending` - Pending count

## Testing

### Component Testing Ready
All components follow patterns suitable for unit testing:
- Props-based configuration
- Pure components where possible
- Callback props for actions
- Testable mock data

### Test Scenarios

```typescript
// Example test structure
describe('ApprovalCard', () => {
  it('should display approval information', () => {})
  it('should call onApprove when approve button clicked', () => {})
  it('should show overdue warning for past due dates', () => {})
  it('should display comment count', () => {})
})

describe('ApprovalFilters', () => {
  it('should filter by status', () => {})
  it('should filter by type', () => {})
  it('should search by name', () => {})
  it('should sort by due date', () => {})
})

describe('Approvals Page', () => {
  it('should display approval list', () => {})
  it('should navigate to detail on card click', () => {})
  it('should show empty state when no approvals', () => {})
  it('should update pending count in notification badge', () => {})
})
```

## Performance Considerations

- Mock data processing is client-side (minimal backend load)
- Pagination reduces DOM nodes (10 per page)
- Lazy component loading via React Router
- useCallback hooks prevent unnecessary re-renders
- useEffect dependencies properly specified
- Notification refresh interval: 30 seconds (configurable)

## Mobile Responsiveness

### Mobile (< 768px)
- Single column layout
- Stacked filters
- Sidebar collapses to icons
- Bottom navigation for quick access
- Full-width cards
- Touch-optimized button sizes

### Tablet (768px - 1024px)
- 2 column layout for cards
- Side-by-side filters
- Sidebar visible with reduced width
- Readable font sizes

### Desktop (> 1024px)
- 3 column layout for statistics
- Full filters panel
- Side-by-side approval cards
- Optimal spacing

## Security & Permissions

**Current Implementation**: No authentication/permission checks (dev mode)

**Future Integration Points**:
- Verify user can access approval
- Check approval permissions (can approve?)
- Audit all approval actions
- Rate limiting on API calls
- CSRF token handling

## Error Handling

- Graceful fallbacks for missing data
- Empty state messages
- Error alerts with retry options
- Loading states during fetches
- Validation on form submissions
- User-friendly error messages

## Future Enhancements

1. **Batch Operations**: Approve/reject multiple at once
2. **Templates**: Pre-defined comment templates
3. **Notifications**: Email/SMS alerts for new approvals
4. **Delegation**: Assign approvals to other team members
5. **Analytics**: Approval metrics and trends
6. **Webhooks**: Trigger external systems on approval
7. **Version Control**: Track changes over approval versions
8. **Scheduled Actions**: Auto-approve after SLA
9. **Workflow Rules**: Custom approval workflows
10. **Integration**: Slack, Teams, email notifications

## File Manifest

### Frontend Files Created
```
frontend/src/components/ApprovalCard.tsx           (370 lines)
frontend/src/components/ApprovalDetail.tsx         (430 lines)
frontend/src/components/ApprovalFilters.tsx        (280 lines)
frontend/src/components/ApprovalTimeline.tsx       (230 lines)
frontend/src/components/CommentThread.tsx          (150 lines)
frontend/src/pages/Approvals.tsx                   (310 lines)
frontend/src/hooks/useApprovals.ts                 (400 lines)
frontend/src/types/approval.ts                     (110 lines)
```

### Files Modified
```
frontend/src/App.tsx                               (Added import & route)
frontend/src/components/Layout.tsx                 (Added nav item & notification)
```

**Total Lines of Code**: ~2,280 lines

## Deployment Checklist

- [x] All components compile without TypeScript errors
- [x] Mock data properly structured
- [x] Responsive design tested
- [x] Navigation integration complete
- [x] Notification badge functional
- [x] Comments working
- [x] Filter/search functional
- [x] Timeline renders correctly
- [x] Mobile layout responsive
- [ ] API integration (pending backend)
- [ ] Unit tests (pending)
- [ ] E2E tests (pending)
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Security review

## Getting Started

### View the Approvals Dashboard
```bash
# Start development server
npm run dev

# Navigate to
http://localhost:5173/approvals
```

### Test with Mock Data
The system comes with 4 realistic mock approval requests. No backend API required for development.

### Integrate with Real API
Update `useApprovals` hook to call real API endpoints instead of mock data.

## Support & Questions

For questions or issues regarding the Approval Workflow implementation, refer to:
- Component prop types in TypeScript files
- Mock data structure in `useApprovals.ts`
- Design patterns in existing components
- API integration guide above

---

**Implementation Date**: March 10, 2026
**Status**: Production Ready (mock data)
**Next Phase**: Backend API Integration
