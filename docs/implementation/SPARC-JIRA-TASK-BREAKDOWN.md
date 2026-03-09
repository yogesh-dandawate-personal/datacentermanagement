# Sprint Task Breakdown: SPARC-Based JIRA Structure

**Role**: Solution Architect Analysis
**Methodology**: SPARC (Specify → Plan → Act → Review → Close)
**Tool**: Jira (Epics → Stories → Subtasks)
**Version**: 1.0.0
**Last Updated**: March 9, 2026

---

## 📋 SPARC Methodology Applied to Sprints

Each sprint follows this governance structure:

```
S - SPECIFY (Planning Phase)
    └─ Create detailed specifications
    └─ Define acceptance criteria
    └─ Document database schema
    └─ Design API contracts

P - PLAN (Design & Architecture)
    └─ Break down into stories
    └─ Design system components
    └─ Create test plans
    └─ Architecture decisions

A - ACT (Implementation)
    └─ Code changes
    └─ Unit testing
    └─ Integration testing
    └─ Code reviews

R - REVIEW (Validation)
    └─ QA testing
    └─ Performance verification
    └─ Security review
    └─ Integration verification

C - CLOSE (Completion)
    └─ Merge to main
    └─ Completion report
    └─ Documentation
    └─ Team sign-off
```

---

## 📊 JIRA Structure Per Sprint

### Epic Level (Sprint Scope)
```
Epic: Sprint 1 - Auth & Tenant Setup
├── Story: Keycloak Integration & Setup
├── Story: JWT Token Management
├── Story: Tenant Scoping Middleware
├── Story: User Role & Permissions
├── Story: Auth UI Components
└── Story: Testing & Documentation
```

### Story Level (Feature/Module)
```
Story: Keycloak Integration & Setup
├── Subtask: Install Keycloak server locally
├── Subtask: Configure realm and client
├── Subtask: Set up user federation
├── Subtask: Create test users and roles
├── Subtask: Document setup guide
└── Acceptance Criteria:
    • Keycloak accessible on localhost:8080
    • Test users created with roles
    • OAuth2 endpoints responding
    • Setup guide documented
```

---

## 🎯 SPRINT 1: AUTH & TENANT - JIRA BREAKDOWN

### Epic: ICARBON-1000 - Auth & Tenant Setup
**Status**: COMPLETED
**Assignee**: Backend Team Lead
**Duration**: Mar 9-22, 2026

#### Story: ICARBON-1001 - Keycloak Integration
**Points**: 8
**Assignee**: Backend Developer 1

```
Subtasks:
├─ ICARBON-1001-1: Set up Keycloak server (Docker)
│  └─ Type: Subtask | Points: 3 | Status: DONE
│  └─ Description: Configure Keycloak on localhost:8080 with Docker
│  └─ Acceptance Criteria:
│     • Keycloak accessible via localhost:8080
│     • Admin console working
│     • Database configured
│
├─ ICARBON-1001-2: Create realm & client configuration
│  └─ Type: Subtask | Points: 3 | Status: DONE
│  └─ Description: Set up 'icarbon' realm and API client
│  └─ Acceptance Criteria:
│     • Realm created and configured
│     • Client created with proper redirect URIs
│     • Client secret generated
│
├─ ICARBON-1001-3: Configure user federation
│  └─ Type: Subtask | Points: 2 | Status: DONE
│  └─ Description: Set up user store in Keycloak DB
│  └─ Acceptance Criteria:
│     • Users can be created in Keycloak
│     • Passwords properly hashed
│
└─ Acceptance Criteria (Story):
   • Keycloak fully functional
   • OAuth2/OIDC endpoints operational
   • Documentation complete
```

#### Story: ICARBON-1002 - JWT Token Management
**Points**: 8
**Assignee**: Backend Developer 2

```
Subtasks:
├─ ICARBON-1002-1: Implement JWT validation middleware
│  └─ Type: Subtask | Points: 5
│  └─ Code Changes:
│     • src/middleware/auth.py
│     • src/services/token_service.py
│  └─ Acceptance Criteria:
│     • Tokens validated on each request
│     • Expired tokens rejected
│     • Invalid signatures rejected
│
├─ ICARBON-1002-2: Create token refresh endpoint
│  └─ Type: Subtask | Points: 3
│  └─ Code Changes:
│     • src/api/v1/auth.py (POST /refresh)
│  └─ Acceptance Criteria:
│     • New token issued with valid refresh token
│     • Old token invalidated on refresh
│     • Proper error handling
│
└─ Acceptance Criteria (Story):
   • JWT validation working
   • Token refresh working
   • Tests passing (>85% coverage)
```

#### Story: ICARBON-1003 - Tenant Isolation Middleware
**Points**: 13
**Assignee**: Backend Team Lead

```
Subtasks:
├─ ICARBON-1003-1: Extract tenant_id from token
│  └─ Type: Subtask | Points: 3
│  └─ Code: src/middleware/tenant.py
│  └─ Tests: tests/unit/test_tenant_extraction.py
│
├─ ICARBON-1003-2: Enforce tenant scoping on queries
│  └─ Type: Subtask | Points: 5
│  └─ Code: src/middleware/database_scoping.py
│  └─ Database: Add tenant_id to all queries
│
├─ ICARBON-1003-3: Implement Row-Level Security (RLS)
│  └─ Type: Subtask | Points: 5
│  └─ Database: PostgreSQL policies per table
│  └─ Tests: tests/integration/test_rls.py
│
└─ Acceptance Criteria (Story):
   • Users can only access their tenant's data
   • RLS policies enforced at DB level
   • Integration tests verify isolation
   • No data leakage across tenants
```

#### Story: ICARBON-1004 - User Roles & Permissions
**Points**: 8
**Assignee**: Backend Developer 2

```
Subtasks:
├─ ICARBON-1004-1: Create roles in database
│  └─ Type: Subtask | Points: 3
│  └─ Schema: roles, role_permissions tables
│  └─ Roles: Admin, Manager, Operator, Viewer
│
├─ ICARBON-1004-2: Implement RBAC middleware
│  └─ Type: Subtask | Points: 3
│  └─ Code: src/middleware/rbac.py
│  └─ @requires_permission('create:organizations')
│
├─ ICARBON-1004-3: Create API endpoint tests
│  └─ Type: Subtask | Points: 2
│  └─ Tests: tests/integration/test_rbac.py
│
└─ Acceptance Criteria (Story):
   • All 4 roles created with permissions
   • Endpoints correctly reject unauthorized users
   • Tests cover permission enforcement
```

#### Story: ICARBON-1005 - Auth UI Components
**Points**: 5
**Assignee**: Frontend Developer 1

```
Subtasks:
├─ ICARBON-1005-1: Create LoginForm component
│  └─ Type: Subtask | Points: 2
│  └─ Code: frontend/src/components/LoginForm.tsx
│  └─ Features:
│     • Email/password inputs
│     • Form validation
│     • Error display
│
├─ ICARBON-1005-2: Create protected route wrapper
│  └─ Type: Subtask | Points: 2
│  └─ Code: frontend/src/components/ProtectedRoute.tsx
│
├─ ICARBON-1005-3: User profile component
│  └─ Type: Subtask | Points: 1
│  └─ Code: frontend/src/components/UserProfile.tsx
│
└─ Acceptance Criteria (Story):
   • Login form functional
   • Protected routes working
   • User can view profile
```

#### Story: ICARBON-1006 - Testing & Documentation
**Points**: 5
**Assignee**: QA + Backend Team

```
Subtasks:
├─ ICARBON-1006-1: Unit tests for auth module
│  └─ Type: Subtask | Points: 2
│  └─ Coverage: >85%
│  └─ File: tests/unit/test_auth_service.py
│
├─ ICARBON-1006-2: Integration tests for auth flows
│  └─ Type: Subtask | Points: 2
│  └─ File: tests/integration/test_auth_flows.py
│  └─ Test scenarios:
│     • Login with valid credentials
│     • Login with invalid credentials
│     • Token refresh
│     • Logout
│
├─ ICARBON-1006-3: Write auth documentation
│  └─ Type: Subtask | Points: 1
│  └─ Doc: docs/AUTH.md
│  └─ Sections:
│     • Setup guide
│     • API reference
│     • Security considerations
│
└─ Acceptance Criteria (Story):
   • Unit test coverage >85%
   • All integration tests passing
   • Documentation complete
```

---

## 🎯 SPRINT 2: ORGANIZATION & FACILITY - JIRA BREAKDOWN

### Epic: ICARBON-2000 - Organization & Facility Hierarchy
**Status**: PLANNED
**Duration**: Mar 30 - Apr 12, 2026

#### Story: ICARBON-2001 - Organization CRUD Operations
**Points**: 13

```
Subtasks:
├─ ICARBON-2001-1: Create Organization model & schema
│  └─ Type: Subtask | Points: 5
│  └─ Schema: CREATE TABLE organizations
│  └─ Code: src/models/organization.py
│  └─ Tests: tests/unit/test_organization_model.py
│
├─ ICARBON-2001-2: Implement Organization service
│  └─ Type: Subtask | Points: 5
│  └─ Methods:
│     • create_organization(tenant_id, data)
│     • get_organization(org_id)
│     • update_organization(org_id, data)
│     • delete_organization(org_id)
│  └─ Tests: tests/unit/test_organization_service.py
│
├─ ICARBON-2001-3: Create Organization API endpoints
│  └─ Type: Subtask | Points: 3
│  └─ Endpoints:
│     • POST /api/v1/organizations
│     • GET /api/v1/organizations
│     • GET /api/v1/organizations/{id}
│     • PATCH /api/v1/organizations/{id}
│  └─ Tests: tests/integration/test_organization_api.py
│
└─ Acceptance Criteria:
   • CRUD operations working
   • Tenant scoping verified
   • >85% test coverage
```

#### Story: ICARBON-2002 - Facility Hierarchy Structure
**Points**: 21

```
Subtasks:
├─ ICARBON-2002-1: Create hierarchy schema (Site, Building, Zone, Rack)
│  └─ Type: Subtask | Points: 5
│  └─ Schema Changes:
│     • CREATE TABLE sites
│     • CREATE TABLE buildings
│     • CREATE TABLE zones
│     • CREATE TABLE racks
│  └─ Constraints: Foreign keys, NOT NULL, indexes
│
├─ ICARBON-2002-2: Implement hierarchy service
│  └─ Type: Subtask | Points: 8
│  └─ Methods:
│     • build_hierarchy_tree(org_id)
│     • validate_hierarchy(org_id) → check cycles
│     • add_facility(parent_id, type, data)
│     • get_descendants(facility_id)
│  └─ Algorithm: DFS cycle detection
│  └─ Tests: tests/unit/test_hierarchy_service.py
│
├─ ICARBON-2002-3: Create API endpoints for hierarchy
│  └─ Type: Subtask | Points: 5
│  └─ Endpoints:
│     • POST /api/v1/sites
│     • POST /api/v1/buildings
│     • POST /api/v1/zones
│     • POST /api/v1/racks
│     • GET /api/v1/hierarchy/{org_id}
│  └─ Tests: tests/integration/test_hierarchy_api.py
│
├─ ICARBON-2002-4: Frontend tree component
│  └─ Type: Subtask | Points: 3
│  └─ Component: FacilityTree.tsx
│  └─ Features:
│     • Collapsible tree view
│     • Recursive rendering
│     • Click handlers for editing
│
└─ Acceptance Criteria:
   • Hierarchy fully functional
   • Circular dependency detection working
   • All tests passing
```

---

## 📋 TASK BREAKDOWN PATTERN (Applicable to ALL Sprints)

### For Each Story:

```jira
Story: ICARBON-{Sprint}00{N} - {Feature Name}
Status: READY FOR DEVELOPMENT
Points: {8|13|21} (use Fibonacci scale)
Assignee: {Team}
Sprint: {Sprint Name}
Due Date: {Sprint End Date}

Description:
{Detailed story description}

Acceptance Criteria:
□ AC1: ...
□ AC2: ...
□ AC3: ...

Subtasks:
├─ ICARBON-{Sprint}00{N}-{M}: {Subtask Name}
│  └─ Points: X
│  └─ Type: Development/Testing/Documentation
│  └─ Assignee: {Developer Name}
│  └─ Code Changes: {files to be modified}
│  └─ Files to Create: {new files}
│  └─ Test Files: {test_file.py}
│  └─ Acceptance Criteria: {subtask-specific}
│
├─ ICARBON-{Sprint}00{N}-{M+1}: ...
│  └─ ...
│
└─ ... (more subtasks)

Testing:
- Unit Tests: tests/unit/test_*.py
- Integration Tests: tests/integration/test_*.py
- E2E Tests: tests/e2e/test_*.py
- Coverage Target: >85%

Documentation:
- Code comments
- Docstrings
- README updates
- API spec (OpenAPI)

Review Requirements:
□ Code review (2 approvals)
□ All tests passing
□ Linting passed (Black, MyPy, ESLint)
□ Security review
□ Performance verified
```

---

## 📊 Complete Sprint 1 JIRA Board Example

```
Epic: ICARBON-1000 (Auth & Tenant Setup)
├─ Story: ICARBON-1001 (8 pts) - Keycloak Integration
│  ├─ Subtask: ICARBON-1001-1 (3 pts) - Set up Keycloak
│  ├─ Subtask: ICARBON-1001-2 (3 pts) - Create realm & client
│  └─ Subtask: ICARBON-1001-3 (2 pts) - Configure federation
│
├─ Story: ICARBON-1002 (8 pts) - JWT Token Management
│  ├─ Subtask: ICARBON-1002-1 (5 pts) - JWT validation
│  └─ Subtask: ICARBON-1002-2 (3 pts) - Token refresh
│
├─ Story: ICARBON-1003 (13 pts) - Tenant Isolation
│  ├─ Subtask: ICARBON-1003-1 (3 pts) - Extract tenant_id
│  ├─ Subtask: ICARBON-1003-2 (5 pts) - Database scoping
│  └─ Subtask: ICARBON-1003-3 (5 pts) - RLS policies
│
├─ Story: ICARBON-1004 (8 pts) - Roles & Permissions
│  ├─ Subtask: ICARBON-1004-1 (3 pts) - Create roles
│  ├─ Subtask: ICARBON-1004-2 (3 pts) - RBAC middleware
│  └─ Subtask: ICARBON-1004-3 (2 pts) - Tests
│
├─ Story: ICARBON-1005 (5 pts) - Auth UI
│  ├─ Subtask: ICARBON-1005-1 (2 pts) - LoginForm
│  ├─ Subtask: ICARBON-1005-2 (2 pts) - Protected routes
│  └─ Subtask: ICARBON-1005-3 (1 pt) - User profile
│
└─ Story: ICARBON-1006 (5 pts) - Testing & Documentation
   ├─ Subtask: ICARBON-1006-1 (2 pts) - Unit tests
   ├─ Subtask: ICARBON-1006-2 (2 pts) - Integration tests
   └─ Subtask: ICARBON-1006-3 (1 pt) - Documentation

Total Points: 60 (ideal for 2-week sprint with 5 developers)
```

---

## 📋 Master Epic Template (Use for all Sprints)

```jira
Epic: ICARBON-{Sprint}000 - {Sprint Name}
===========================================

Sprint: {Number}
Duration: {Start Date} - {End Date} (2 weeks)
Team: {Backend/Frontend/QA}
Status: PLANNED
Points: {Total}

Objectives:
1. {Primary objective}
2. {Secondary objective}
3. {Deliverable}

Stories:
├─ Story {Number}A: {Feature 1} - {Points} pts
├─ Story {Number}B: {Feature 2} - {Points} pts
├─ Story {Number}C: {Feature 3} - {Points} pts
└─ Story {Number}D: {Testing & Docs} - {Points} pts

Success Criteria:
□ All stories completed
□ >85% test coverage
□ All CI checks passing
□ Code review approved
□ No critical bugs
□ Documentation complete

Risks:
- {Risk 1}: Mitigation...
- {Risk 2}: Mitigation...

Dependencies:
- Sprint {N-1} must be complete
- {External dependency}

Blockers:
- {Blocker 1}: Status...
- {Blocker 2}: Status...
```

---

## 🔄 SPARC Phase Task Allocation

### S - SPECIFY Phase (Days 1-2)
```jira
Story: ICARBON-X001 - Requirements & Specification
Assignee: Tech Lead
Duration: 2 days
Tasks:
├─ Subtask: Write detailed requirements
├─ Subtask: Create database schema diagram
├─ Subtask: Define API contracts (OpenAPI)
├─ Subtask: Create test plan
└─ Subtask: Get team sign-off
Status: REVIEW
```

### P - PLAN Phase (Days 2-3)
```jira
Story: ICARBON-X002 - Design & Architecture Planning
Assignee: Architects/Senior Devs
Duration: 1-2 days
Tasks:
├─ Subtask: Break story into subtasks
├─ Subtask: Assign subtasks to developers
├─ Subtask: Create component design
├─ Subtask: Review dependencies
└─ Subtask: Setup test infrastructure
Status: READY FOR DEVELOPMENT
```

### A - ACT Phase (Days 3-8)
```jira
Stories: ICARBON-X003 to ICARBON-X007 - Implementation
Assignee: Developers
Duration: 5-6 days
Tasks:
├─ Subtask: Implement feature
├─ Subtask: Write unit tests
├─ Subtask: Code review
├─ Subtask: Integration testing
└─ Subtask: Performance testing
Status: IN REVIEW
```

### R - REVIEW Phase (Days 8-9)
```jira
Story: ICARBON-X008 - QA & Validation
Assignee: QA Team
Duration: 1-2 days
Tasks:
├─ Subtask: Run full test suite
├─ Subtask: Performance verification
├─ Subtask: Security audit
├─ Subtask: Accessibility check
├─ Subtask: Manual testing
└─ Subtask: Sign-off report
Status: IN QA
```

### C - CLOSE Phase (Days 9-10)
```jira
Story: ICARBON-X009 - Completion & Documentation
Assignee: Tech Lead
Duration: 1 day
Tasks:
├─ Subtask: Merge to main branch
├─ Subtask: Update documentation
├─ Subtask: Create completion report
├─ Subtask: Release notes
└─ Subtask: Team retrospective
Status: DONE
```

---

## 📊 Jira Board Setup Recommendations

### Board Columns
```
TO DO → IN PROGRESS → IN REVIEW → IN QA → DONE → CLOSED
```

### Custom Fields
```
Sprint Field: {Sprint Number}
Story Points: {Number}
SPARC Phase: [S|P|A|R|C]
Code Changes: {Files}
Test Coverage: {Percentage}
Documentation: {Yes/No}
Security Reviewed: {Yes/No}
Performance Tested: {Yes/No}
```

### Automation Rules
```
Rule 1: When subtask moved to DONE, check if all subtasks done
        → If yes, automatically move parent story to review

Rule 2: When story reaches QA, create story for next sprint

Rule 3: Notify team when sprint velocity deviates >20% from plan

Rule 4: Auto-assign test tasks when code review approved
```

---

## 🎯 Development Workflow (Typical Story)

```
1. Story Created (ICARBON-{Sprint}00{N})
   └─ Status: READY FOR DEVELOPMENT
   └─ Points assigned
   └─ Assignees: Backend Lead + 2 Developers
   └─ Duration: 3-5 days (half sprint)

2. Team Kicks Off
   └─ Meeting to discuss requirements
   └─ Clarify acceptance criteria
   └─ Assign specific subtasks
   └─ Create branches: feature/ICARBON-{Sprint}00{N}

3. Development Starts
   ├─ Developer 1 works on ICARBON-{N}-1
   │  └─ Create code, write tests
   │  └─ Self-review, commit to feature branch
   │  └─ Move to IN REVIEW
   │
   ├─ Developer 2 works on ICARBON-{N}-2
   │  └─ Same process
   │
   └─ Developer 3 works on ICARBON-{N}-3
      └─ Same process

4. Code Review
   ├─ Pull request created
   │  └─ 2 peer reviews required
   │  └─ All tests must pass
   │  └─ Coverage >85%
   │
   └─ If approved:
      └─ Merge to develop branch
      └─ Move subtask to DONE
      └─ CI/CD pipeline triggered

5. Integration Testing
   └─ QA team tests integrated features
   └─ Move story to IN QA
   └─ Performance tests run
   └─ Security audit performed

6. Sign-Off
   ├─ Story moved to DONE
   ├─ All acceptance criteria verified
   ├─ Documentation updated
   └─ Ready for next sprint

7. Release Preparation
   └─ Merge to main branch
   └─ Create release notes
   └─ Update deployment runbooks
```

---

## 📈 Sprint Velocity Tracking

```jira
Sprint 1 Target: 60 points
Completed: 50 points (83%)
Velocity: Moderate

Breakdown:
├─ Story 1: 13 pts ✅ DONE
├─ Story 2: 8 pts ✅ DONE
├─ Story 3: 8 pts ✅ DONE
├─ Story 4: 13 pts ✅ DONE (Carried over from Sprint 0)
└─ Story 5: 10 pts 🔄 IN PROGRESS (will complete in Sprint 2)

Burndown:
Day 1:  60 pts remaining
Day 3:  45 pts remaining
Day 5:  30 pts remaining
Day 7:  15 pts remaining
Day 10: 10 pts remaining (overflow to next sprint)
```

---

## ✅ Pre-Coding Checklist (For Each Story)

Before development starts on any story:

- [ ] Requirements clearly defined
- [ ] Acceptance criteria written and approved
- [ ] Database schema finalized
- [ ] API contracts defined (OpenAPI)
- [ ] Test plan created
- [ ] Git branch created
- [ ] Subtasks assigned to developers
- [ ] Dependencies identified
- [ ] Risks assessed and mitigated
- [ ] Kickoff meeting completed
- [ ] Everyone has environment setup

---

**This SPARC + JIRA approach ensures:**
✅ Clear governance and accountability
✅ Transparent progress tracking
✅ Quality gate enforcement
✅ Risk management
✅ Team coordination
✅ Historical records for retrospectives

---

**Implementation**: Ready for adoption across all 13 sprints
**Next Step**: Import this template into Jira Project
**Maintainer**: Engineering Manager / Scrum Master
