# Completion Criteria & Quality Gates

**Governance**: Strict Completion Standards
**Enforcement**: No "Partial Completion" - ALL criteria must be met
**Role**: Solution Architect, QA Lead, Tech Lead
**Version**: 1.0.0
**Effective Date**: March 9, 2026

---

## ⚠️ CRITICAL RULE: Nothing is DONE Until EVERYTHING is DONE

```
❌ NEVER mark as DONE if:
   • Code is incomplete
   • Tests are not written
   • Tests are not passing
   • Coverage is <85%
   • Linting fails
   • Type checks fail
   • Documentation is missing
   • Peer review not completed
   • Security review pending
   • Performance tests not run
   • Deployment not verified
   • Any acceptance criterion is incomplete

✅ ONLY mark as DONE when:
   • Code is complete and committed
   • All tests written and PASSING
   • Coverage verified >85%
   • Linting PASSED
   • Type checking PASSED
   • Peer review APPROVED (2+ approvals)
   • Security review APPROVED
   • Performance benchmarks MET
   • Documentation COMPLETE
   • QA sign-off OBTAINED
   • Deployed to staging successfully
```

---

## 📋 Task-Level Completion Criteria

### SUBTASK Definition & Requirements

```
Subtask Status: DEVELOPMENT
Description: {Clear, specific task}
Assignee: {Developer Name}
Points: {Size estimate}
Files to Change: {List of files}
Files to Create: {List of new files}
Tests Required: {Unit/Integration/E2E}
```

### Subtask NOT Complete If Any Of:

```
❌ Code Changes:
   □ Code incomplete (partial implementation)
   □ Code doesn't compile/run
   □ Code violates style guide
   □ Unused imports or variables
   □ Magic numbers (non-configurable values)
   □ Console.log or debug code left in

❌ Testing:
   □ No tests written
   □ Tests written but not passing
   □ Coverage <85%
   □ Edge cases not tested
   □ Error handling not tested
   □ Async code not properly tested

❌ Code Quality:
   □ Linting errors present
   □ Type checking failures (MyPy)
   □ SonarQube issues
   □ Code duplications
   □ Functions >50 lines
   □ Cyclomatic complexity too high

❌ Review:
   □ Not submitted for review
   □ Review comments not addressed
   □ <2 approvals obtained
   □ Security review pending

❌ Documentation:
   □ No docstrings/comments
   □ API documentation missing
   □ Usage examples missing
   □ Architecture notes missing

❌ Performance:
   □ Performance tests not run
   □ Benchmarks not met
   □ Memory leaks detected
   □ Response time exceeds target
```

### Subtask IS Complete Only When:

```
✅ Code Changes:
   ✓ Implementation complete and working
   ✓ Code passes all linting rules (Black, MyPy, ESLint)
   ✓ No console.log or debug code
   ✓ Follows project conventions
   ✓ All imports used
   ✓ Code committed to feature branch

✅ Testing:
   ✓ All unit tests written and PASSING
   ✓ All integration tests PASSING (if applicable)
   ✓ Test coverage >85% (verified by tool)
   ✓ Edge cases covered
   ✓ Error scenarios tested
   ✓ Async operations properly tested

✅ Code Quality:
   ✓ ESLint: 0 errors, 0 warnings
   ✓ Black formatting: Applied
   ✓ MyPy type checking: 0 errors
   ✓ SonarQube: Grade A
   ✓ No code duplication (DRY principle)
   ✓ Functions <50 lines
   ✓ Cyclomatic complexity <10

✅ Review:
   ✓ Pull request created
   ✓ 2+ peer reviews APPROVED
   ✓ All review comments ADDRESSED
   ✓ Security review APPROVED
   ✓ Architecture review APPROVED

✅ Documentation:
   ✓ Docstrings added to all functions/classes
   ✓ Complex logic has explanatory comments
   ✓ API documentation (OpenAPI) updated
   ✓ README updated if needed
   ✓ Usage examples provided
   ✓ Architecture decisions documented

✅ Performance:
   ✓ Performance benchmarks run
   ✓ Results meet targets
   ✓ No memory leaks detected
   ✓ Response times acceptable
   ✓ Approved by performance review

✅ Status:
   ✓ Move to DONE
   ✓ Update task in Jira
   ✓ Add completion checklist comment
```

---

## 📊 Story-Level Completion Criteria

### Story Definition

```
Story: ICARBON-{Sprint}00{N} - {Feature Name}
Status: DEVELOPMENT
Points: {8|13|21}
Description: {User story format: As a {role}, I want {feature}, so that {benefit}}
Acceptance Criteria: {List}
Subtasks: {Related subtasks}
```

### Story NOT Complete If:

```
❌ Development:
   □ Any subtask still in progress
   □ Any subtask failed QA
   □ Code not merged to develop
   □ Features incomplete per AC

❌ Testing:
   □ Unit test coverage <85%
   □ Integration tests failing
   □ E2E tests not running
   □ Manual testing incomplete

❌ Acceptance Criteria:
   □ AC1 not verified ✗
   □ AC2 not verified ✗
   □ AC3 not verified ✗
   □ Any AC marked as "partial"

❌ Quality Gates:
   □ CI/CD pipeline failing
   □ Security scan failed
   □ Performance below targets
   □ Breaking changes not documented

❌ Review:
   □ QA sign-off not obtained
   □ Product owner not approved
   □ Tech lead not reviewed
   □ Security team not approved

❌ Documentation:
   □ No documentation written
   □ API docs not updated
   □ Architecture decision not documented
   □ Known limitations not noted
```

### Story IS Complete Only When:

```
✅ Development:
   ✓ All subtasks DONE (not just "close")
   ✓ Code merged to develop branch
   ✓ No merge conflicts
   ✓ All features implemented per requirements

✅ Testing:
   ✓ Unit test coverage >85% (report attached)
   ✓ All integration tests PASSING
   ✓ All E2E tests for story PASSING
   ✓ No flaky tests
   ✓ Manual testing completed and documented

✅ Acceptance Criteria:
   ✓ AC1 VERIFIED ✓ (with screenshot/evidence)
   ✓ AC2 VERIFIED ✓ (with screenshot/evidence)
   ✓ AC3 VERIFIED ✓ (with screenshot/evidence)
   ✓ AC4 VERIFIED ✓ (if applicable)
   ✓ ALL criteria met, none "partial"

✅ Quality Gates:
   ✓ CI/CD pipeline: ALL GREEN ✅
   ✓ Code quality: Grade A
   ✓ Security: PASSED review
   ✓ Performance: Meets benchmarks
   ✓ No breaking changes (or documented)

✅ Review:
   ✓ Code review: 2+ APPROVED
   ✓ QA sign-off: OBTAINED
   ✓ Product owner: APPROVED
   ✓ Tech lead: APPROVED
   ✓ Security team: APPROVED (if required)

✅ Documentation:
   ✓ Code documentation: Complete
   ✓ API documentation: Updated
   ✓ Architecture decision: Documented
   ✓ Known limitations: Listed
   ✓ Deployment notes: Written

✅ Status Update:
   ✓ Move to DONE
   ✓ Add completion comment with evidence
   ✓ Link to PR/commit
   ✓ Attach coverage report
   ✓ Create follow-up stories if needed
```

---

## 🏆 Sprint-Level Completion Criteria

### Sprint Definition

```
Epic: ICARBON-{Sprint}000 - {Sprint Name}
Sprint Duration: {Date} - {Date}
Sprint Goal: {Clear objective}
Target Velocity: {Story points}
Team: {Members}
Status: IN PROGRESS
```

### Sprint NOT Complete If:

```
❌ Stories:
   □ Any story still "In Progress"
   □ Any story has incomplete subtasks
   □ Velocity <70% of target
   □ Stories marked "Done" but QA caught bugs

❌ Quality:
   □ Code coverage <85% on any module
   □ Build pipeline failing
   □ Security scan failures
   □ Performance regressions

❌ Documentation:
   □ Release notes not written
   □ API changelog not updated
   □ Migration guides missing
   □ Deployment steps not documented

❌ Testing:
   □ QA sign-off not obtained
   □ Critical bugs still open
   □ Regression tests failed
   □ E2E tests incomplete

❌ Deployment Readiness:
   □ Code not in main branch
   □ Database migrations not tested
   □ Rollback plan not documented
   □ Deployment checklist incomplete
```

### Sprint IS Complete Only When:

```
✅ Stories:
   ✓ ALL stories marked DONE
   ✓ ALL stories merged to main
   ✓ Velocity tracked and documented
   ✓ No stories partially done

✅ Quality:
   ✓ Code coverage >85% across all modules
   ✓ Build pipeline: ALL GREEN
   ✓ Security scan: PASSED
   ✓ Performance: Baseline met
   ✓ No blocking bugs open

✅ Testing:
   ✓ All QA tests PASSED
   ✓ All manual testing COMPLETED
   ✓ Regression suite PASSING
   ✓ Critical bugs: 0
   ✓ High severity bugs: 0
   ✓ QA sign-off: OBTAINED

✅ Documentation:
   ✓ Release notes WRITTEN and REVIEWED
   ✓ API changelog UPDATED
   ✓ Migration guide (if needed) WRITTEN
   ✓ Deployment guide UPDATED
   ✓ Known issues DOCUMENTED
   ✓ Breaking changes ANNOUNCED

✅ Deployment:
   ✓ Code in main branch
   ✓ Database migrations tested and reversible
   ✓ Environment variables documented
   ✓ Rollback plan documented and tested
   ✓ Deployment checklist completed
   ✓ Monitoring alerts configured

✅ Team:
   ✓ Retrospective COMPLETED
   ✓ Team sign-off OBTAINED
   ✓ Follow-up items tracked
   ✓ Team morale positive

✅ Status Update:
   ✓ Create Sprint Completion Report
   ✓ Attach evidence:
      • Coverage reports
      • Test reports
      • Security scan results
      • Performance benchmarks
      • Screenshots of features
   ✓ Get tech lead sign-off
   ✓ Schedule deployment
```

---

## 🔍 Quality Gate Checklist Templates

### Code Review Checklist

```markdown
## Code Review Checklist - MUST ALL PASS

### Functionality
- [ ] Code implements the required feature
- [ ] All acceptance criteria met
- [ ] No unnecessary code changes
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is proper

### Code Quality
- [ ] Code follows project style guide
- [ ] No code duplication (DRY principle)
- [ ] Functions <50 lines
- [ ] Classes <200 lines
- [ ] No magic numbers
- [ ] Naming is clear and descriptive
- [ ] No commented-out code

### Testing
- [ ] Unit tests written and passing
- [ ] Test coverage >85%
- [ ] Edge cases tested
- [ ] Error scenarios tested
- [ ] Async code properly tested
- [ ] No flaky tests

### Documentation
- [ ] Docstrings for all public functions
- [ ] Comments explain "why", not "what"
- [ ] API documentation updated (OpenAPI)
- [ ] README updated if needed
- [ ] Complex algorithms documented

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection (if applicable)
- [ ] Authentication/authorization checks

### Performance
- [ ] No N+1 query problems
- [ ] Database indexes present
- [ ] Caching strategy documented
- [ ] Response times acceptable
- [ ] No memory leaks detected

### Dependencies
- [ ] No unnecessary dependencies added
- [ ] Version conflicts resolved
- [ ] Security vulnerabilities checked
- [ ] License compatibility verified

## VERDICT: ☐ APPROVED | ☐ REQUEST CHANGES | ☐ COMMENT
```

### QA Sign-Off Checklist

```markdown
## QA Sign-Off Checklist - MUST ALL PASS

### Manual Testing
- [ ] Happy path tested
- [ ] Error paths tested
- [ ] Edge cases tested
- [ ] Boundary values tested
- [ ] Negative scenarios tested

### Functional Testing
- [ ] AC1 verified ✓
- [ ] AC2 verified ✓
- [ ] AC3 verified ✓
- [ ] AC4 verified ✓

### Integration Testing
- [ ] Integration with other modules works
- [ ] Data integrity maintained
- [ ] No data loss
- [ ] Rollback tested

### Performance Testing
- [ ] Load testing completed
- [ ] Latency within targets
- [ ] Memory usage acceptable
- [ ] No resource leaks
- [ ] Concurrent user handling verified

### Regression Testing
- [ ] Existing features still work
- [ ] No breaking changes
- [ ] Backward compatibility maintained

### Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Touch targets >44px

### Mobile Testing
- [ ] Responsive on mobile
- [ ] Touch interactions work
- [ ] Performance on mobile acceptable
- [ ] Orientation changes handled

### Deployment Verification
- [ ] Feature deployable
- [ ] Migrations reversible
- [ ] Rollback plan verified
- [ ] No blocked deployments

## VERDICT: ☐ APPROVED | ☐ REJECTED (details below)
```

---

## 🚀 Deployment Readiness Checklist

```markdown
## Deployment Readiness - MUST ALL BE CHECKED

### Code Readiness
- [ ] Code in main branch
- [ ] All tests passing in CI/CD
- [ ] No build warnings or errors
- [ ] Performance benchmarks met
- [ ] Security scan passed

### Database Readiness
- [ ] Migrations written
- [ ] Migrations tested (forward + backward)
- [ ] Backups created
- [ ] Rollback procedure documented
- [ ] Data integrity verified

### Documentation Readiness
- [ ] Release notes written
- [ ] API documentation updated
- [ ] Deployment steps documented
- [ ] Rollback steps documented
- [ ] Environment variables listed
- [ ] Known issues documented

### Team Readiness
- [ ] Ops team briefed
- [ ] Support team briefed
- [ ] Monitoring alerts configured
- [ ] On-call schedule set
- [ ] Incident response plan ready

### Environment Readiness
- [ ] Staging deployment successful
- [ ] All tests passing on staging
- [ ] Load testing completed
- [ ] Security review on staging
- [ ] Performance validated on staging

### Approval
- [ ] Tech lead approval ✓
- [ ] QA lead approval ✓
- [ ] Product owner approval ✓
- [ ] Ops lead approval ✓
- [ ] Security team approval ✓

## Status: ☐ READY TO DEPLOY | ☐ HOLD (blocker noted)
```

---

## 📈 Metrics & Reporting

### Definition of Done (DoD)

```
A story is DONE when:

1. Code:
   - Complete and committed
   - Merged to develop branch
   - Passes all CI checks
   - Code review: 2+ approvals

2. Tests:
   - Unit coverage >85%
   - All tests passing
   - Integration tests passing
   - E2E tests passing

3. Quality:
   - Linting: PASSED
   - Type checking: PASSED
   - Security scan: PASSED
   - Performance: Target met

4. Documentation:
   - Code documented
   - API docs updated
   - Architecture documented
   - User guide updated (if needed)

5. Review:
   - QA sign-off: OBTAINED
   - Tech review: APPROVED
   - Security review: APPROVED
   - Product owner: APPROVED

6. Acceptance:
   - ALL AC verified
   - None partially complete
   - Evidence collected
   - Signed off by stakeholder
```

### Burndown Tracking

```
Sprint Burndown Chart (Ideal vs Actual)
Points
100│                    ╱
   │                  ╱
 75│                ╱  ┌─ Ideal burndown
   │              ╱    │
 50│            ╱      │
   │          ╱        │
 25│        ╱          │
   │      ╱      ┌──┐  │
  0├─────────────┴──┴──┘
   │ 1 2 3 4 5 6 7 8 9 10
   └─ Days

Red Zone: Below ideal line by >10 points
Yellow Zone: Within 5-10 points of ideal
Green Zone: On or above ideal line

⚠️ If Red: Swarm on blockers immediately
```

---

## ❌ Anti-Patterns to AVOID

```
❌ DO NOT:

1. Mark as DONE without tests
   "The code works, will test later"

2. Merge incomplete features
   "Tests are optional for this story"

3. Ignore coverage requirements
   "Coverage is close enough at 78%"

4. Skip code review
   "I reviewed my own code"

5. Use "Partial DONE"
   "Story is 80% done"

6. Ignore acceptance criteria
   "The feature works, close to AC"

7. Skip documentation
   "Code is self-documenting"

8. Defer testing
   "We'll test in next sprint"

9. Accept flaky tests
   "The test fails sometimes"

10. Deploy without approval
    "It passed locally, ship it"
```

---

## ✅ Enforcement Actions

### What Happens When Completion Criteria NOT Met?

```
1. Subtask Status: NOT MOVED TO DONE
   └─ Cannot progress until ALL criteria met
   └─ Remains in "IN PROGRESS"
   └─ Team notified of blockers

2. Story Status: BLOCKED
   └─ Cannot move to QA
   └─ Velocity not counted
   └─ Risk escalated to team lead

3. Sprint Status: AT RISK
   └─ If >20% of stories blocked
   └─ Sprint planning adjusted
   └─ Additional resources allocated

4. Deployment: PREVENTED
   └─ Code cannot merge to main
   └─ CI/CD pipeline blocks merge
   └─ Manual override requires multiple approvals

5. Escalation:
   └─ If blocker >24 hours
   └─ Escalated to tech lead
   └─ Daily updates required
   └─ Risk mitigation plan created
```

---

## 📋 Sign-Off Procedures

### Subtask Completion Sign-Off

```
Developer: [Name]
Date: [YYYY-MM-DD]

I certify this subtask meets ALL completion criteria:
✓ Code complete and committed
✓ All tests written and passing
✓ Coverage >85% verified
✓ Linting/type-check passed
✓ Peer review completed (2+ approvals)
✓ Documentation complete
✓ Ready for integration

Signed: _________________________ Date: __________
```

### Story Completion Sign-Off

```
Tech Lead: [Name]
QA Lead: [Name]
Date: [YYYY-MM-DD]

We certify ALL subtasks are DONE and story meets completion criteria:
✓ All subtasks status = DONE
✓ Code merged to develop
✓ All tests passing
✓ Coverage >85%
✓ QA approved
✓ Acceptance criteria all verified
✓ Documentation complete

Tech Lead: _________________ QA Lead: ________________ Date: ___
```

### Sprint Completion Sign-Off

```
Sprint Master: [Name]
Tech Lead: [Name]
Product Owner: [Name]
Date: [YYYY-MM-DD]

We certify Sprint {N} is COMPLETE:
✓ All stories moved to DONE
✓ Velocity: {pts} achieved
✓ Quality gates: ALL PASSED
✓ Documentation: COMPLETE
✓ Team sign-off: OBTAINED
✓ Ready for: {next phase}

Signed:
Sprint Master: _________________ Date: __________
Tech Lead: _________________ Date: __________
Product Owner: _________________ Date: __________
```

---

## 🎯 Bottom Line

**Nothing is DONE until EVERYTHING is DONE.**

No excuses. No exceptions. No partial completions.

When a task says "DONE", it means:
- ✓ Fully implemented
- ✓ Fully tested
- ✓ Fully documented
- ✓ Fully reviewed
- ✓ Ready for production

---

**Enforcement**: Mandatory for all 13 sprints
**Audit**: QA lead reviews completion daily
**Escalation**: Tech lead for any violations
**Consequence**: Tasks moved back to IN PROGRESS if criteria not met
