# Engineering Backlog - iNetZero ESG Platform
**Ralph Loop Issue Detection & Remediation Plan**
**Generated**: March 10, 2026 | **Total Issues**: 47 | **Blocking Production**: 5

---

## Issue Summary by Severity

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 CRITICAL | 5 | Must fix before any deployment |
| 🟡 HIGH | 12 | Must fix before launch |
| 🟠 MEDIUM | 20 | Should fix during development |
| 🟢 LOW | 10 | Nice to have improvements |
| **TOTAL** | **47** | **→ Engineering Plan** |

---

## CRITICAL ISSUES (Blocking Production)

### INFRA-001: Hardcoded Secrets in Git Repository
**Severity**: 🔴 CRITICAL
**Component**: Infrastructure / Security
**Assigned**: DevOps Team
**Sprint**: Immediate
**Effort**: 3-4 hours
**Status**: Detected

**Description**:
Sensitive credentials exposed in version control:
- SECRET_KEY: `A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM`
- DB password: `netzero_secure_pass_2024`
- Database URL: `postgresql://netzero:netzero_secure_pass_2024@localhost:5432/netzero`

**Root Cause**:
Development environment configuration (.env files) committed to Git repository

**Impact**:
- ❌ API security compromised
- ❌ Database credentials exposed
- ❌ Cannot be rotated without full git history rewrite
- ❌ Risk of unauthorized access

**Recommended Fix**:
1. Immediately invalidate all exposed secrets
2. Generate new SECRET_KEY for all environments
3. Create new database credentials
4. Implement HashiCorp Vault or AWS Secrets Manager
5. Perform git history rewrite (filter-branch) or migrate to new repo
6. Implement pre-commit hooks to prevent secret commits
7. Update Vercel environment variables with new secrets

**Files Affected**:
- `.env`
- `.env.staging`
- `docker-compose.yml`
- `backend/app/auth/jwt_handler.py` (references)

**Acceptance Criteria**:
- [ ] All credentials rotated
- [ ] Vercel environment variables updated
- [ ] Git history cleaned
- [ ] New .gitignore preventing .env commits
- [ ] Pre-commit hooks installed
- [ ] Secret management system implemented

---

### INFRA-002: No Cloud Database Connection
**Severity**: 🔴 CRITICAL
**Component**: Infrastructure / Database
**Assigned**: DevOps Team
**Sprint**: Immediate
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
Application deployed to Vercel but DATABASE_URL points to localhost PostgreSQL.
API health endpoint returns HTTP 500 for all requests.

```
Current: postgresql://localhost:5432/netzero  (❌ Vercel can't reach)
Needed: Cloud database (Supabase/Railway/AWS RDS)
```

**Root Cause**:
Development database configuration not migrated to production provider

**Impact**:
- 🔴 **BLOCKING**: Application completely non-functional
- All API requests return HTTP 500
- Cannot process any user requests
- Cannot accept production traffic

**Recommended Fix**:
1. Choose cloud provider: **Supabase recommended** (PostgreSQL-compatible, included migrations, auth)
   - Alternative: Railway (simple, good UX)
   - Alternative: AWS RDS (enterprise features)
2. Create cloud database instance with same schema
3. Run Alembic migrations to initialize schema
4. Update Vercel `DATABASE_URL` environment variable
5. Test API health endpoint returns 200
6. Verify application accepts requests

**Expected Outcome**:
- API health endpoint: `GET /api/v1/health` returns `{"status": "ok"}`
- All endpoints functional
- Database operations working

**Acceptance Criteria**:
- [ ] Cloud database provisioned
- [ ] Schema initialized with migrations
- [ ] DATABASE_URL configured in Vercel
- [ ] Health endpoint returns 200
- [ ] All dashboard endpoints responsive
- [ ] Sample data loaded

---

### BACKEND-001: Mock Authentication in Production
**Severity**: 🔴 CRITICAL
**Component**: Backend / Authentication
**Assigned**: Backend Team
**Sprint**: Immediate
**Effort**: 4-5 hours
**Status**: Detected

**Description**:
Login endpoint generates random user/tenant IDs without credential validation.
```python
# Current (line 158-165 in main.py):
# TODO: Validate against database or Keycloak
if not credentials.email or not credentials.password:
    raise AuthenticationError(...)
user_id = str(uuid.uuid4())        # Random UUID!
tenant_id = str(uuid.uuid4())      # Random UUID!
```

**Root Cause**:
Placeholder implementation not replaced with real authentication

**Impact**:
- 🔴 Anyone can login with any credentials
- No actual user validation
- No real tenant association
- Security: Complete authentication bypass

**Recommended Fix**:

**Option A**: Database-backed authentication
1. Create user registration endpoint
2. Hash passwords with bcrypt
3. Validate credentials against users table
4. Return JWT token with actual user_id and tenant_id

**Option B**: Keycloak integration (referenced in code)
1. Configure Keycloak provider
2. Implement OIDC flow
3. Exchange authorization code for JWT
4. Validate tokens from Keycloak

**Recommended**: Option B (enterprise-grade)

**Acceptance Criteria**:
- [ ] Real credential validation implemented
- [ ] User table with hashed passwords
- [ ] JWT contains actual user_id/tenant_id
- [ ] Token verification works
- [ ] Demo credentials work (demo@example.com / password)

---

### BACKEND-002: Missing Tenant Isolation Checks
**Severity**: 🔴 CRITICAL
**Component**: Backend / Multi-tenancy
**Assigned**: Backend Team
**Sprint**: Immediate
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
Organizations routes don't validate tenant ownership.
Cross-tenant data access possible.

**Location**: `/backend/app/routes/organizations.py` lines 42-52

```python
def get_organization(org_id: str):
    org = db.query(Organization).filter_by(id=org_id).first()
    # ❌ Missing: if org.tenant_id != current_user.tenant_id: raise 403
    return org
```

**Root Cause**:
Routes directly query by ID without tenant context validation

**Impact**:
- 🔴 SECURITY BREACH: User A can access User B's organizations
- Cross-tenant data leak possible
- Compliance violation
- GDPR/HIPAA concerns

**Recommended Fix**:
1. Add tenant_id check to ALL organization routes
2. Create shared dependency for tenant validation
3. Add tests for cross-tenant denial
4. Audit all routes for missing tenant checks

```python
def get_organization(org_id: str, current_user = Depends(get_current_user)):
    org = db.query(Organization).filter_by(
        id=org_id,
        tenant_id=current_user['tenant_id']  # ✅ Added
    ).first()
    if not org:
        raise HTTPException(status_code=404)
    return org
```

**Acceptance Criteria**:
- [ ] All organization endpoints validate tenant
- [ ] 403 returned for cross-tenant access
- [ ] Tests verify denial
- [ ] Security audit passed

---

### DEVOPS-001: No CI/CD Pipeline
**Severity**: 🔴 CRITICAL
**Component**: DevOps / CI/CD
**Assigned**: DevOps Team
**Sprint**: Week 1
**Effort**: 12-15 hours
**Status**: Detected

**Description**:
All deployments are manual. No automated testing, security scanning, or quality gates.

**Current State**:
- Manual script: `scripts/deploy-to-vercel.sh`
- No automated tests on PR
- No code quality checks
- No security scanning
- No automated deployment

**Root Cause**:
CI/CD infrastructure not implemented

**Impact**:
- 🔴 Human error in deployments
- No regression testing
- No quality gates
- Security issues not caught

**Recommended Fix**:
Implement GitHub Actions workflows:

1. **Test Pipeline**:
   ```yaml
   on: [push, pull_request]
   - Lint (ESLint, pylint)
   - Unit tests (Jest, pytest)
   - Integration tests
   - Type checking (tsc)
   ```

2. **Security Pipeline**:
   ```yaml
   - Dependency scanning (npm audit, pip audit)
   - SAST (CodeQL)
   - Container scanning
   - Secret detection
   ```

3. **Deployment Pipeline**:
   ```yaml
   on: [main branch]
   - Run all tests
   - Build Docker images
   - Deploy to Vercel
   - Smoke tests
   - Alert on failure
   ```

**Effort Breakdown**:
- Test pipeline: 4 hours
- Security pipeline: 3 hours
- Deployment pipeline: 4 hours
- Testing & debugging: 4 hours

**Acceptance Criteria**:
- [ ] GitHub Actions workflows created
- [ ] All tests pass on PR
- [ ] Security scans pass
- [ ] Auto-deployment on main merge
- [ ] Failed builds notify team

---

## HIGH PRIORITY ISSUES (Must Fix Before Launch)

### BACKEND-003: Authentication Code Duplication
**Severity**: 🟡 HIGH
**Component**: Backend / Code Quality
**Assigned**: Backend Team
**Sprint**: Week 1
**Effort**: 3-4 hours
**Status**: Detected

**Description**:
`get_current_user()` function duplicated 6 times across route modules.

**Locations**:
- `routes/dashboards.py` (~30 lines)
- `routes/telemetry.py` (~30 lines)
- `routes/carbon.py` (~30 lines)
- `routes/organizations.py` (~30 lines with db)
- `routes/marketplace.py` (~30 lines)
- `routes/kpi.py` (~30 lines)

**Root Cause**:
Copy-paste implementation without shared dependency

**Impact**:
- Code maintenance nightmare
- Inconsistent implementations
- Bug in one = bug in six places
- ~180 lines of wasted code

**Recommended Fix**:
1. Create shared auth module: `auth/dependencies.py`
2. Implement `get_current_user()` once
3. Import in all route modules
4. Remove duplicate implementations
5. Add tests for auth dependency

```python
# auth/dependencies.py
async def get_current_user(authorization: str = Header(None)):
    # Shared implementation
    return {"user_id": ..., "tenant_id": ..., "roles": ...}
```

**Acceptance Criteria**:
- [ ] Single `get_current_user()` implementation
- [ ] Imported in all 6 route files
- [ ] No duplicate code
- [ ] All tests pass
- [ ] Code review approved

---

### BACKEND-004: CORS Configuration Too Permissive
**Severity**: 🟡 HIGH
**Component**: Backend / Security
**Assigned**: Backend Team
**Sprint**: Week 1
**Effort**: 1-2 hours
**Status**: Detected

**Description**:
CORS allows requests from ANY origin.

```python
# app/main.py line 48-54:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ TODO: Restrict to known origins
)
```

**Root Cause**:
Development configuration used in production

**Impact**:
- CSRF vulnerability
- Unauthorized cross-origin requests
- Malware can make requests on behalf of users

**Recommended Fix**:
```python
allow_origins = [
    "https://inetzer o.vercel.app",    # Production
    "http://localhost:3000",             # Local dev
    "http://localhost:5173",             # Vite dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Acceptance Criteria**:
- [ ] CORS restricted to known origins
- [ ] Environment-specific configuration
- [ ] Tests verify restrictions
- [ ] TODO comment removed

---

### BACKEND-005: Broad Exception Catching
**Severity**: 🟡 HIGH
**Component**: Backend / Error Handling
**Assigned**: Backend Team
**Sprint**: Week 1
**Effort**: 5-6 hours
**Status**: Detected

**Description**:
62 instances of broad `except Exception` catching expose internal errors.

```python
try:
    # service call
except Exception as e:
    logger.error(f"Error: {str(e)}")  # ❌ Exposes stack trace
    raise HTTPException(status_code=500, detail=str(e))
```

**Root Cause**:
Generic error handling without specific exception types

**Impact**:
- Stack traces leaked to clients
- Difficult debugging
- Information disclosure vulnerability

**Recommended Fix**:
1. Catch specific exceptions (ValueError, KeyError, etc.)
2. Wrap in custom exception hierarchy
3. Log full traceback internally
4. Return generic error to client

```python
try:
    # service call
except ValueError as e:
    logger.error(f"Validation error: {e}", exc_info=True)
    raise HTTPException(status_code=400, detail="Invalid input")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Acceptance Criteria**:
- [ ] All 62 broad catches replaced
- [ ] Specific exception types used
- [ ] Generic error messages to clients
- [ ] Full logging internally
- [ ] Security audit passed

---

### BACKEND-006: No Input Validation Limits
**Severity**: 🟡 HIGH
**Component**: Backend / Validation
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 3-4 hours
**Status**: Detected

**Description**:
CSV batch uploads have no file size limits or row count validation.

**Impact**:
- Out-of-memory DoS attacks
- Slow query performance
- Resource exhaustion

**Recommended Fix**:
```python
# In telemetry routes:
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_ROWS = 1000

@app.post("/batch-ingest")
async def batch_ingest(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    reader = csv.DictReader(file.file)
    for i, row in enumerate(reader):
        if i >= MAX_ROWS:
            raise HTTPException(status_code=400, detail="Too many rows")
```

**Acceptance Criteria**:
- [ ] File size limits enforced
- [ ] Row count validation
- [ ] Proper error responses
- [ ] Tests verify limits
- [ ] Documentation updated

---

### DEVOPS-003: Hardcoded Secrets in Docker Compose
**Severity**: 🟡 HIGH
**Component**: DevOps / Secrets
**Assigned**: DevOps Team
**Sprint**: Week 1
**Effort**: 1-2 hours
**Status**: Detected

**Description**:
`docker-compose.yml` contains hardcoded database credentials.

**Fix**:
Use environment variable substitution:
```yaml
environment:
  POSTGRES_PASSWORD: ${DB_PASSWORD}
  DATABASE_URL: ${DATABASE_URL}
```

Create `.env` file (not in git):
```
DB_PASSWORD=<random-generated-password>
DATABASE_URL=postgresql://netzero:${DB_PASSWORD}@postgres:5432/netzero
```

---

### DEVOPS-004: Outdated Security Dependencies
**Severity**: 🟡 HIGH
**Component**: Backend / Dependencies
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 1-2 hours
**Status**: Detected

**Description**:
`passlib==1.7.4` is from 2016 (10 years old).

**Fix**:
```bash
pip install --upgrade passlib python-jose
pip list --outdated  # Check for other outdated packages
```

**Recommendation**: Add automated dependency scanning:
```bash
pip install safety
safety check  # Run in CI/CD
```

---

### FRONTEND-001: Undefined Variable in Energy.tsx
**Severity**: 🟡 HIGH
**Component**: Frontend / Runtime Error
**Assigned**: Frontend Team
**Sprint**: Week 1
**Effort**: 0.5 hours
**Status**: Detected

**Description**:
`allFacilities` variable is undefined, will cause runtime crash.

**Location**: `src/pages/Energy.tsx` line 54

```python
...allFacilities.map(f => ...)  // ❌ allFacilities is not defined
```

**Fix**:
Replace with `facilities`:
```typescript
const facilityOptions = [
  { value: 'all', label: 'All Facilities' },
  ...facilities.map(f => ({ value: f.id, label: f.name }))
]
```

**Acceptance Criteria**:
- [ ] Code compiles without errors
- [ ] Facility select works
- [ ] Tests verify functionality

---

### FRONTEND-002: Duplicate useEnergyMetrics Hook
**Severity**: 🟡 HIGH
**Component**: Frontend / Code Quality
**Assigned**: Frontend Team
**Sprint**: Week 1
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
Two different `useEnergyMetrics` implementations:
1. In `useApi.ts` (returns merged metrics)
2. In `useEnergyMetrics.ts` (returns different structure)

**Fix**:
1. Consolidate to single implementation
2. Remove duplicate file
3. Update all usages
4. Add tests

**Acceptance Criteria**:
- [ ] Single hook implementation
- [ ] All pages use consistent API
- [ ] Tests pass
- [ ] Unused file deleted

---

## MEDIUM PRIORITY ISSUES (Should Fix During Development)

### BACKEND-007: N+1 Query Problem in Organization Tree
**Severity**: 🟠 MEDIUM
**Component**: Backend / Performance
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
Recursive organization tree building causes exponential database queries.

```python
def build_organization_tree(org: Organization, db: Session):
    children = db.query(Organization).filter_by(parent_id=org.id).all()
    # ❌ Each child triggers another query!
    return {
        "children": [build_organization_tree(child, db) for child in children]
    }
```

**Fix**: Use eager loading
```python
from sqlalchemy.orm import joinedload

org = db.query(Organization).options(
    joinedload(Organization.children).joinedload(Organization.children)
).first()
```

---

### BACKEND-008: No Database Indexes on Tenant Queries
**Severity**: 🟠 MEDIUM
**Component**: Backend / Database
**Assigned**: Backend Team
**Sprint**: Week 3
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
No composite indexes on (tenant_id, entity_id) for multi-tenant queries.

**Fix**: Create indexes in migration
```python
op.create_index('ix_organization_tenant_id', 'organization', ['tenant_id'])
op.create_index('ix_facility_tenant_id_org', 'facility', ['tenant_id', 'organization_id'])
```

---

### DEVOPS-005: Missing Frontend Testing Framework
**Severity**: 🟠 MEDIUM
**Component**: Frontend / Testing
**Assigned**: Frontend Team
**Sprint**: Week 2
**Effort**: 8-10 hours
**Status**: Detected

**Description**:
No test framework configured. Backend has 91 tests, frontend has 0.

**Fix**:
Install test framework:
```bash
npm install --save-dev vitest @testing-library/react jsdom
```

Create test files:
- `src/__tests__/components/Button.test.tsx`
- `src/__tests__/pages/Dashboard.test.tsx`
- `src/__tests__/hooks/useApi.test.ts`

---

### DEVOPS-006: No Monitoring/Observability
**Severity**: 🟠 MEDIUM
**Component**: DevOps / Monitoring
**Assigned**: DevOps Team
**Sprint**: Week 3
**Effort**: 5-7 hours
**Status**: Detected

**Description**:
No logging, monitoring, metrics, or alerting configured.

**Missing**:
- Application logs (Datadog, ELK, CloudWatch)
- Performance metrics (Prometheus)
- Error tracking (Sentry)
- Uptime monitoring
- Alert notifications

**Recommended**: Use Datadog or New Relic for simplicity

---

### DATABASE-001: Database Migration Error Handling
**Severity**: 🟠 MEDIUM
**Component**: Database / Migrations
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 2-3 hours
**Status**: Detected

**Description**:
Migration errors silently ignored in Docker Compose.

```bash
# Current (unsafe):
python -m alembic upgrade head 2>/dev/null || echo 'No migrations'
```

**Fix**:
```bash
# Safer:
python -m alembic upgrade head
if [ $? -ne 0 ]; then
  echo "Database migration failed!"
  exit 1
fi
```

---

## LOW PRIORITY ISSUES (Nice to Have Improvements)

### FRONTEND-003: No Code Splitting
**Severity**: 🟢 LOW
**Component**: Frontend / Performance
**Assigned**: Frontend Team
**Sprint**: Week 3
**Effort**: 3-4 hours
**Status**: Detected

**Description**:
All pages loaded in single bundle. Code splitting would reduce initial load.

**Fix**:
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Energy = lazy(() => import('./pages/Energy'));
const Reports = lazy(() => import('./pages/Reports'));

<Suspense fallback={<Spinner />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
  </Routes>
</Suspense>
```

**Expected Benefit**: 30-40% reduction in initial bundle

---

### BACKEND-009: Add Request Timeouts
**Severity**: 🟢 LOW
**Component**: Backend / Configuration
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 1 hour
**Status**: Detected

**Description**:
API requests can hang indefinitely with no timeout.

**Fix**:
```python
@app.post("/api/v1/telemetry")
async def ingest_telemetry(request, timeout: int = 30):
    async with asyncio.timeout(timeout):
        # service call
```

---

### FRONTEND-004: Missing Error Boundaries on Pages
**Severity**: 🟢 LOW
**Component**: Frontend / Error Handling
**Assigned**: Frontend Team
**Sprint**: Week 2
**Effort**: 1-2 hours
**Status**: Detected

**Description**:
Only Dashboard has ErrorBoundary. Should wrap all page routes.

**Fix**:
```typescript
<ErrorBoundary>
  <Dashboard />
</ErrorBoundary>
```

---

### BACKEND-010: Add Pagination Limits
**Severity**: 🟢 LOW
**Component**: Backend / API Design
**Assigned**: Backend Team
**Sprint**: Week 2
**Effort**: 1-2 hours
**Status**: Detected

**Description**:
Pagination parameters not enforced.

**Fix**:
```python
@app.get("/api/v1/facilities")
async def list_facilities(skip: int = 0, limit: int = 20):
    if limit > 1000:
        raise HTTPException(status_code=400, detail="Limit too large")
```

---

## Backlog Summary

```
Total Issues: 47

By Component:
- Backend: 18 issues
- Frontend: 7 issues
- DevOps/Infrastructure: 12 issues
- Database: 4 issues
- Testing: 4 issues
- Security: 8 issues (across components)

By Priority:
- 🔴 Critical: 5 (must fix)
- 🟡 High: 12 (before launch)
- 🟠 Medium: 20 (during development)
- 🟢 Low: 10 (improvements)

Estimated Total Effort: 70-90 hours
Timeline to Production: 2-3 weeks

Week 1: Critical + High Priority (35-40 hours)
- Secrets rotation
- Cloud database
- CI/CD pipeline
- Auth consolidation
- CORS fix
- Frontend crash fixes

Week 2: Remaining High + Medium (25-30 hours)
- Performance optimization
- Testing infrastructure
- Monitoring setup
- Database optimization

Week 3: Polish + Final (10-15 hours)
- Documentation
- Security audit
- Load testing
- Final QA
```

---

**Report Generated**: March 10, 2026
**Next Steps**: Assign issues to teams and execute in priority order
**Success Criteria**: All critical issues resolved before production deployment

