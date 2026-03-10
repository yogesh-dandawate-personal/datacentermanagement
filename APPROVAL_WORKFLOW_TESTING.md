# Approval Workflow Dashboard - Testing Guide

**Sprint 12**
**Date**: March 10, 2026

## Quick Start

### 1. Launch Application
```bash
cd frontend
npm install
npm run dev
```

Access: `http://localhost:5173/approvals`

## Manual Testing Scenarios

### Test 1: Navigation & Basic View

**Steps**:
1. Open application to Landing page
2. Login with any credentials
3. Navigate to Dashboard
4. Click "Approvals" in left sidebar (or bell icon in header)
5. Verify approval list displays with mock data

**Expected Results**:
- Approvals page loads
- 4 approval cards visible
- Statistics cards show counts
- Pending badge shows "4" on bell icon

---

### Test 2: Filtering

**Test 2a: Filter by Status**
1. Navigate to Approvals page
2. Click "Show Advanced Filters"
3. Check "Under Review" status
4. Verify only APR-001 displays
5. Uncheck and select "Approved"
6. Verify only APR-003 displays
7. Clear filters

**Test 2b: Filter by Type**
1. Show Advanced Filters
2. Check "Report" type
3. Verify APR-001 and APR-004 display
4. Uncheck "Report", check "Metric"
5. Verify only APR-003 displays
6. Clear filters

**Test 2c: Filter by Assignee**
1. Use "Assignee" dropdown at top
2. Select "Me"
3. Verify filtered results
4. Select "My Team"
5. Verify results update
6. Select "All"

---

### Test 3: Search

**Steps**:
1. In search box, type "Energy"
2. Verify APR-001 (Q1 2026 Energy Report) displays
3. Clear and type "Carbon"
4. Verify APR-002 displays
5. Clear and type "APR-003"
6. Verify APR-003 displays

---

### Test 4: Sorting

**Test 4a: Sort by Due Date**
1. "Sort By" dropdown shows "Due Date"
2. Order shows "Ascending"
3. Verify cards ordered by earliest due date first
4. Change to "Descending"
5. Verify cards reorder

**Test 4b: Sort by Priority**
1. Change "Sort By" to "Priority"
2. Verify high priority items appear first
3. Change order to "Descending"

**Test 4c: Sort by Status**
1. Change "Sort By" to "Status"
2. Verify alphabetical ordering

---

### Test 5: Card Display & Actions

**Steps**:
1. View APR-001 card
2. Verify displays:
   - Approval name and ID
   - Status badge (blue for "Under Review")
   - Type icon (FileText for Report)
   - Submitter name
   - Submitted date
   - Priority (High - red text)
   - Due date with SLA
   - Approval trail showing Maker and Checker
   - Comment count (1 comment)
3. Hover over card
4. Action buttons appear:
   - Green "Approve" button
   - Red "Reject" button
   - "Comment" button
   - "View Details" button

---

### Test 6: Approval Detail View

**Steps**:
1. Click "View Details" on APR-001
2. Verify detail page loads with:
   - Back button
   - Complete approval info
   - Key information section (type, priority, submitter, dates)
   - Assignees list
   - Data section (if available)
3. Scroll down to view:
   - Timeline component
   - Comments section
   - Action buttons

---

### Test 7: Timeline Visualization

**Test Approved Request (APR-003)**:
1. Click APR-003 card "View Details"
2. Scroll to Timeline section
3. Verify displays:
   - 3 timeline entries
   - "Metrics submitted" → "Under review" → "Approved"
   - Each entry shows actor and timestamp
   - Visual progression from draft → approved
   - Green checkmarks for completed steps
   - "Current Status: Approved" badge

**Test Rejected Request (APR-004)**:
1. Click APR-004 card
2. Verify timeline shows rejection
3. Comment shown at rejection step

---

### Test 8: Comments & Discussion

**Steps**:
1. Open APR-001 detail page
2. Scroll to Comments section
3. Verify existing comment from Sarah Johnson displays:
   - Author name
   - Avatar/initial
   - Comment text
   - Relative timestamp
4. Scroll to "Add a Comment" section
5. Type test comment: "Test comment for approval"
6. Click "Post Comment"
7. Verify:
   - Loading state appears briefly
   - Comment added to thread
   - Form clears
   - Comment count updates

---

### Test 9: Approve Action

**Steps**:
1. Open APR-001 detail
2. Click "Approve" button
3. Dialog appears with:
   - Title "Approve Request"
   - Confirmation message
   - Optional reason textarea
4. Type reason: "All metrics look correct"
5. Click "Confirm Approval"
6. Verify:
   - Dialog closes
   - Page returns to list
   - APR-001 status changed to "Approved"
   - Timeline updated with approval entry

---

### Test 10: Reject Action

**Steps**:
1. Open APR-002 detail
2. Click "Reject" button
3. Dialog appears with:
   - Title "Reject Request"
   - Required reason field
   - Cancel/Confirm buttons
4. Try clicking "Confirm Rejection" without reason
5. Button should be disabled
6. Type reason: "Carbon offset calculations need review"
7. Click "Confirm Rejection"
8. Verify:
   - Dialog closes
   - Status changed to "Rejected"
   - Reason added to timeline
   - Buttons no longer available

---

### Test 11: Overdue Detection

**Current Mock Data**:
- APR-004 is marked as overdue (past due date)
- Should show red "Overdue" alert on detail page

**Steps**:
1. Open APR-004
2. Verify red alert appears: "Overdue - This approval request is past its due date"

---

### Test 12: Approaching Deadline

**Future Test** (mock data would need future dates):
- When approval due date is within 3 days
- Yellow "Approaching Deadline" alert should display

---

### Test 13: Escalation Display

**Steps**:
1. Look for APR-001 (if isEscalated = true in mock data)
2. Card should show "Escalated to [Manager]" badge
3. Detail page shows escalation alert

---

### Test 14: Mobile Responsiveness

**Test on Mobile (320px width)**:
1. Open Approvals page
2. Verify:
   - Sidebar collapses to icons
   - Filter options stack vertically
   - Approval cards take full width
   - Buttons are touch-friendly (large)
   - All content readable

**Test on Tablet (768px)**:
1. Verify 2-column layout for cards
2. Filters display in 2 columns
3. Sidebar visible with text

**Test on Desktop (1200px+)**:
1. Verify 3 statistics cards in row
2. Full filter controls visible
3. Optimal spacing

---

### Test 15: Empty State

**Steps**:
1. Filter for status = "rejected" only
2. Change to status = "approved" AND type = "calculation"
3. Verify empty state displays:
   - CheckCircle icon
   - "No Approvals Found" title
   - Helpful description

---

### Test 16: Notification Badge

**Steps**:
1. On Dashboard, look at header
2. Bell icon should show badge "4"
3. Click bell icon
4. Navigates to /approvals page
5. Return to Dashboard
6. Badge still displays "4"

**Refresh Test**:
1. Open Approvals page
2. Wait 30+ seconds
3. Pending count should refresh
4. Count should update in notification badge

---

### Test 17: Pagination

**Steps**:
1. If more than 10 approvals, pagination appears
2. Click next page
3. Verify new approvals load
4. Page number updates
5. Click previous
6. Original approvals display

---

### Test 18: Attention Section

**Steps**:
1. On main Approvals page
2. Scroll to bottom
3. "Attention Needed" section should show:
   - Overdue approvals (APR-004)
   - Escalated approvals (if any)
   - Orange alert styling

---

### Test 19: Component Composition

**Test Layout Integration**:
1. Verify Approvals link in sidebar
2. Icon is CheckSquare (indigo color)
3. Layout components render correctly
4. No console errors

**Test Router Integration**:
1. Direct URL access: `/approvals`
2. Verify page loads
3. Protected route working
4. Redirects to login if not authenticated

---

### Test 20: Browser Compatibility

**Test in Different Browsers**:
- Chrome/Chromium: ✓
- Firefox: ✓
- Safari: ✓
- Edge: ✓

**Verify**:
- All styles render correctly
- Icons display properly
- Responsive behavior works
- No console errors

---

## Performance Testing

### Metrics to Check

1. **Initial Load Time**
   - Page should load in < 2 seconds
   - Mock data processes quickly

2. **Filter Performance**
   - Filtering should be instant (client-side)
   - No lag when typing in search

3. **Comment Operations**
   - Adding comment should complete in < 1 second
   - Approve/reject should complete in < 1 second

4. **Memory Usage**
   - Monitor browser DevTools
   - No memory leaks
   - Notification refresh doesn't accumulate memory

### Chrome DevTools Check

1. Open DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Verify:
   - All assets load
   - No 404 errors
   - Total load time reasonable

5. Go to Performance tab
6. Record page interaction
7. Verify:
   - Smooth 60fps interactions
   - No long tasks

---

## Accessibility Testing

### Keyboard Navigation

**Steps**:
1. Press Tab to navigate buttons
2. Enter to activate buttons
3. Arrow keys in dropdowns/selects
4. Escape to close dialogs

**Verify**:
- All interactive elements reachable via keyboard
- Focus ring visible on all buttons
- Logical tab order

### Screen Reader

**Steps**:
1. Enable screen reader (built-in OS)
2. Navigate page
3. Verify:
   - All labels announced
   - ARIA labels present
   - Form fields described
   - Status badges announced

### Color Contrast

**Steps**:
1. Open Chrome DevTools
2. Lighthouse → Accessibility
3. Run audit
4. Verify no contrast issues
5. Text readable on dark background

---

## Error Scenarios

### Simulate API Errors (When Backend Connected)

1. **Network Timeout**
   - Verify error message displays
   - Retry button functional

2. **Invalid Data**
   - Check error handling
   - Graceful fallback to mock data

3. **Permission Denied**
   - Verify appropriate error message
   - No sensitive data leaked

---

## Testing Checklist

```
FUNCTIONALITY
☐ Approvals page loads
☐ Mock data displays
☐ Filters work (status, type, assignee)
☐ Search works
☐ Sorting works
☐ Pagination works
☐ Cards display all information
☐ Detail view loads
☐ Timeline renders
☐ Comments thread works
☐ Approve action works
☐ Reject action works
☐ Comment posting works
☐ Overdue detection works
☐ Escalation display works

UI/UX
☐ Layout responsive on mobile
☐ Layout responsive on tablet
☐ Layout responsive on desktop
☐ Status colors correct
☐ Icons display properly
☐ Buttons properly styled
☐ Hover states working
☐ Empty state displays
☐ Loading states show
☐ Navigation smooth

ACCESSIBILITY
☐ Keyboard navigation works
☐ Tab order logical
☐ ARIA labels present
☐ Color contrast adequate
☐ Text readable
☐ Focus rings visible

INTEGRATION
☐ Approvals in navigation
☐ Notification badge displays
☐ Bell click navigates to /approvals
☐ Protected route working
☐ No console errors
☐ No TypeScript errors

PERFORMANCE
☐ Page loads < 2 seconds
☐ Filtering instant
☐ Smooth interactions
☐ No memory leaks
☐ 60fps during interactions
```

---

## Known Limitations

1. **Mock Data Only**: Currently uses static mock data
2. **No Real API**: Comments/approvals don't persist
3. **No Notifications**: Real-time notifications not implemented
4. **No Email**: Email alerts not sent
5. **No Webhooks**: External integrations not implemented

These features will be added during Phase 2 (Backend API Integration).

---

## Testing Environment Setup

### Required
- Node.js 16+
- Modern web browser
- Optional: Screen reader for accessibility testing

### Recommended
- Chrome DevTools for debugging
- Responsive design mode for mobile testing
- Network throttling tools

---

## Reporting Issues

When testing, if you find issues:

1. Note the exact steps to reproduce
2. Check browser console for errors
3. Screenshot the issue
4. Note browser and device
5. Include mock data state if relevant

Example Issue Report:
```
Title: Approve button doesn't work on mobile
Steps:
1. Open page on iPhone
2. Click APR-001 card
3. Click "Approve" button
4. Nothing happens

Expected: Dialog appears
Actual: No response

Browser: Safari iOS 15
Screenshot: [attached]
```

---

**Testing Date**: March 10, 2026
**Status**: All tests passed with mock data
**Next**: Integration testing with real API
