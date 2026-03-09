# Complete Sprint Template (With All Required Elements)

**Template Version**: 1.0.0
**Status**: Master Template - Use for all Sprints
**Last Updated**: March 9, 2026

---

## ⚡ MASTER TEMPLATE - APPLY THIS STRUCTURE TO ALL SPRINTS 1-13

Every sprint must include EXACTLY these sections in this order:

---

# Sprint {N}: {Feature Name}

**Sprint**: {N}
**Duration**: {Start Date} - {End Date} (2 weeks)
**Module**: {Module Name}
**Owner**: {Team Name}
**Status**: 📋 PLANNED
**Target Velocity**: {Points}

---

## 📋 Executive Summary

{Brief 2-3 sentence summary of what this sprint delivers}

**Dependency**: {Previous Sprint} ✅

---

## 🎯 Scope & Deliverables

### Phase 1: {Feature Name}
- [x] {Deliverable 1}
- [x] {Deliverable 2}
- [x] {Deliverable 3}

### Phase 2: {Feature Name}
- [x] {Deliverable 4}
- [x] {Deliverable 5}

### Phase 3: {Testing & Docs}
- [x] {Testing deliverable}
- [x] {Documentation deliverable}

---

## 🎨 Design System & UX Requirements

**Design Style**: Glasmorphic Design System
**Component Library**: Radix UI + Tailwind CSS + Styled Components

### Glasmorphic Components to Build (if applicable)
```
└─ Glasmorphic {ComponentName}
   ├─ Primary Glass Background: rgba(255, 255, 255, 0.1) + blur(12px)
   ├─ Border Color: rgba(0, 217, 255, 0.3) [Neon Cyan]
   ├─ Text Shadow Glow: Neon Cyan (#00D9FF)
   ├─ Hover State: Border opacity 0.5, glow intensifies
   └─ Dark Mode: Glass background rgba(15, 20, 50, 0.35)
```

### UI Requirements for This Sprint
- [x] All components follow glasmorphic design system
- [x] Neon cyan accents (#00D9FF) for primary actions
- [x] Proper backdrop-filter blur (10-20px based on depth)
- [x] Dark mode support with adjusted glass colors
- [x] Accessibility (WCAG 2.1 AA): Color contrast >4.5:1
- [x] Mobile responsive (320px→desktop)
- [x] Touch targets ≥44px on mobile

---

## 📊 Database Schema Changes

### New Tables/Modifications

```sql
{Schema definition}
{Create table statements}
{Index definitions}
{Constraint definitions}
```

### Migration File: {Version}_add_{feature_name}.py

```python
{Migration code}
```

---

## 🔧 API Endpoints

### Module: {Module Name}

```
{HTTP_METHOD}  {path}
Description: {What it does}
Request:  {Request schema}
Response: {Response schema}
Auth:     {JWT required}
Scoping:  {Tenant scoped}
Test:     {Test location}
```

---

## 💻 Backend Implementation

### Project Structure
```
src/
├── domain/
│   └── {module_name}/
│       ├── models.py
│       ├── schemas.py
│       ├── service.py
│       └── repository.py
├── api/
│   └── v1/
│       └── {module_name}.py
└── migrations/
    └── 00X_add_{module_name}.py
```

### Code Examples

```python
{Sample code}
```

---

## 🎨 Frontend Implementation

### Components to Create
```
src/domains/{domain}/
├── pages/
│   ├── {Page1}.tsx
│   └── {Page2}.tsx
├── components/
│   ├── {Component1}.tsx
│   └── {Component2}.tsx
└── hooks/
    └── use{Feature}.ts
```

### Key Features
- {Feature 1}
- {Feature 2}
- {Feature 3}

---

## 🧪 Testing Plan

### Unit Tests
**Target**: >85% coverage
**File**: tests/unit/test_{module}.py

```python
{Test examples}
```

### Integration Tests
**File**: tests/integration/test_{module}.py

```python
{Integration test examples}
```

### E2E Tests
**File**: tests/e2e/test_{journey}.py

```python
{E2E test examples}
```

---

## ✅ Completion Criteria - STRICT ENFORCEMENT

### ⚠️ CRITICAL: Nothing is DONE Until EVERYTHING is DONE

A task is ONLY complete when ALL criteria below are verified and checked off:

### Code Completion
- [ ] Code implementation: 100% complete (no placeholders)
- [ ] Code compiles/runs without errors
- [ ] All code committed to feature branch
- [ ] Branch name: feature/ICARBON-{sprint}00{N}
- [ ] Follows Black code style (auto-formatted)
- [ ] No console.log or debug statements
- [ ] No unused imports or variables
- [ ] No magic numbers (all configurable)

### Testing Completion
- [ ] All unit tests written
- [ ] All unit tests PASSING (0 failures)
- [ ] Unit test coverage >85% (tool verified)
- [ ] All integration tests PASSING
- [ ] All E2E tests PASSING
- [ ] Edge cases covered
- [ ] Error scenarios tested
- [ ] No flaky tests (pass 3x minimum)

### Code Quality Completion
- [ ] ESLint: 0 errors, 0 warnings
- [ ] Black: Formatting applied & verified
- [ ] MyPy: 0 type errors
- [ ] SonarQube: Grade A
- [ ] No code duplication (DRY)
- [ ] Functions <50 lines
- [ ] Classes <200 lines
- [ ] Cyclomatic complexity <10

### Review Completion
- [ ] Pull request created
- [ ] 2+ peer code reviews: APPROVED
- [ ] All review comments: ADDRESSED
- [ ] Security review: APPROVED
- [ ] Tech lead review: APPROVED
- [ ] Architecture review: APPROVED
- [ ] CI/CD pipeline: ALL GREEN ✅

### Documentation Completion
- [ ] Docstrings: ALL public functions
- [ ] Comments explain "why", not "what"
- [ ] API documentation (OpenAPI): UPDATED
- [ ] README.md: UPDATED
- [ ] Architecture decisions: DOCUMENTED
- [ ] Known limitations: LISTED

### Acceptance Criteria Verification
- [ ] AC1: {Criterion} ✓ (screenshot/evidence attached)
- [ ] AC2: {Criterion} ✓ (test passing)
- [ ] AC3: {Criterion} ✓ (verified)
- [ ] AC4: {Criterion} ✓ (verified)

### Performance Verification
- [ ] Load test: PASSED
- [ ] Latency: Within targets (<100ms)
- [ ] Memory: No leaks detected
- [ ] Response time: Acceptable
- [ ] Concurrent users: Verified

### Quality Gates
- [ ] Security scan: PASSED
- [ ] Performance benchmark: MET
- [ ] Accessibility audit: PASSED (WCAG 2.1 AA)
- [ ] Mobile responsiveness: VERIFIED
- [ ] Dark mode: WORKING
- [ ] Glasmorphic design: IMPLEMENTED
- [ ] No breaking changes (or documented)

### Final Sign-Offs
- [ ] Developer: Task complete & ready for review
- [ ] Peer reviewer: Code approved
- [ ] Tech lead: Architecture approved
- [ ] QA: All tests passing, sign-off obtained
- [ ] Security: Security review approved
- [ ] Product owner: Acceptance criteria verified

---

## 🏆 JIRA Task Structure

### Epic: ICARBON-{Sprint}000 - {Sprint Name}
**Points**: {Total}
**Owner**: {Team}

#### Story: ICARBON-{Sprint}00{N} - {Feature Name}
**Points**: {8|13|21} (Fibonacci)
**Status**: READY FOR DEVELOPMENT

##### Subtask: ICARBON-{Sprint}00{N}-{M}
- **Type**: Development | Testing | Documentation
- **Points**: {Size}
- **Code Changes**: {files}
- **Tests**: {test_files}
- **Acceptance Criteria**: {Local AC}
- **Sign-off Required**: ✓ {Role}

---

## 🚨 WHAT WILL CAUSE TASK TO BE MARKED "NOT DONE"

❌ Task CANNOT be marked DONE if:

**Code Issues**:
- [ ] Code is incomplete or non-functional
- [ ] Code doesn't compile/run
- [ ] Breaking changes not documented
- [ ] Magic numbers present
- [ ] Unused code/imports left

**Testing Issues**:
- [ ] Tests not written
- [ ] Tests failing
- [ ] Coverage <85%
- [ ] Edge cases not tested
- [ ] Flaky tests present

**Quality Issues**:
- [ ] Linting errors present
- [ ] Type checking errors
- [ ] Code duplication
- [ ] Functions >50 lines
- [ ] Classes >200 lines

**Review Issues**:
- [ ] Peer review not completed
- [ ] <2 approvals obtained
- [ ] Review comments not addressed
- [ ] Security review pending
- [ ] Tech lead sign-off missing

**Documentation Issues**:
- [ ] No docstrings
- [ ] API docs not updated
- [ ] README not updated
- [ ] Architecture decisions not documented

**Acceptance Issues**:
- [ ] Any AC not verified
- [ ] AC marked as "partial"
- [ ] Evidence not attached
- [ ] QA sign-off not obtained

**Performance Issues**:
- [ ] Performance tests not run
- [ ] Benchmarks not met
- [ ] Response time too slow
- [ ] Memory leaks detected

**Deployment Issues**:
- [ ] Code not in main branch
- [ ] Migrations not tested
- [ ] Rollback plan not documented

---

## 📋 Sign-Off Procedures

### Developer Sign-Off (Before Pull Request)

```
Developer: [Name]
Date: [YYYY-MM-DD]

I certify this task meets ALL completion criteria:
✓ Code complete and committed
✓ All tests written and PASSING
✓ Coverage >85% verified
✓ Linting PASSED
✓ Type-check PASSED
✓ Documentation complete
✓ Ready for peer review

Signed: _________________________ Date: __________
```

### Peer Reviewer Sign-Off (Minimum 2 required)

```
Reviewer 1: [Name]
Date: [YYYY-MM-DD]

Code Review: ☐ APPROVED | ☐ REQUEST CHANGES

Concerns/Comments:
{List any issues found}

Signed: _________________________ Date: __________
```

### QA Sign-Off

```
QA Lead: [Name]
Date: [YYYY-MM-DD]

Testing: ☐ APPROVED | ☐ FAILED

Tests Run:
- Unit: {# passed}/{# total}
- Integration: {# passed}/{# total}
- E2E: {# passed}/{# total}

Coverage: {%} (Target >85%)

Issues Found: {None | List}

Signed: _________________________ Date: __________
```

### Story Completion Sign-Off

```
Tech Lead: [Name]
Date: [YYYY-MM-DD]

Sprint {N} Story {ICARBON-{N}00{M}} Completion Verification:

✓ All subtasks: DONE (not in progress)
✓ Code: MERGED to develop
✓ Tests: ALL PASSING
✓ Coverage: >85%
✓ QA: APPROVED
✓ Acceptance Criteria: ALL VERIFIED
✓ Documentation: COMPLETE

STATUS: ☐ APPROVED FOR DEPLOYMENT | ☐ HOLD

Signed: _________________________ Date: __________
```

---

## 📈 Sprint Burndown Tracking

### Daily Progress

```
Day 1:  {Points} remaining
Day 2:  {Points} remaining
Day 3:  {Points} remaining
...
Day 10: {Points} remaining

Burndown Rate: {Points/day}
Forecast: {On-track | At-risk | Over-capacity}
```

---

## 🎯 Success Metrics

### Definition of Done (DoD) - MUST ALL BE TRUE

1. **Code**: Complete, committed, merged
2. **Tests**: All passing, >85% coverage
3. **Quality**: Linting/type-check passed
4. **Review**: 2+ approvals, concerns addressed
5. **Documentation**: Complete and reviewed
6. **Acceptance**: ALL criteria verified
7. **Sign-offs**: All required approvals obtained
8. **Deployment**: Ready to push to production

---

## 🔄 What Happens If Criteria Not Met

**Consequence 1: Task Moved Back to IN PROGRESS**
- Cannot move to DONE
- Blocker identified
- Team notified of what's blocking

**Consequence 2: Story Cannot Close**
- Velocity not counted
- Sprint at risk
- Tech lead escalation

**Consequence 3: Sprint Cannot Close**
- If >20% stories blocked
- Retrospective focuses on blockers
- Process improvement created

**Consequence 4: Code Cannot Merge to Main**
- CI/CD pipeline blocks merge
- Manual override requires 3+ approvals
- Incident report created

---

## ✨ Bottom Line

### COMPLETION IS BINARY: DONE or NOT DONE

**There is NO "close enough" or "good enough".**

When a task says **DONE**, it means:
- ✓ Fully implemented (100%, no placeholders)
- ✓ Fully tested (all passing, >85% coverage)
- ✓ Fully documented (code, API, architecture)
- ✓ Fully reviewed (2+ approvals)
- ✓ Fully verified (QA sign-off)
- ✓ Production ready

**Anything less = NOT DONE. Period.**

---

## 📚 Files to Reference

- [Completion Criteria & Quality Gates](./COMPLETION-CRITERIA-QUALITY-GATES.md)
- [SPARC-Based JIRA Breakdown](./SPARC-JIRA-TASK-BREAKDOWN.md)
- [Glasmorphic Design System](./UX-GLASMORPHIC-DESIGN.md)
- [UX Playbook](./UX-PLAYBOOK.md)

---

**Template Status**: Ready for use in all 13 sprints
**Last Updated**: March 9, 2026
**Owner**: Solution Architect
**Authority**: Enforcement via JIRA automation + Tech Lead review
