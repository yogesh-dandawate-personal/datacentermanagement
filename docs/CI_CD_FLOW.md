# CI/CD Pipeline Architecture

## Overview

The CI/CD pipeline automates testing, security scanning, and deployment processes for the iNetZero ESG platform. It ensures code quality, security compliance, and reliable deployments.

## Workflow Triggers

### 1. Test Workflow (`test.yml`)

**Triggers:**
- Pull requests (any branch)
- Pushes to `main` branch
- Manual dispatch via GitHub Actions

**Jobs:**
- **Backend Tests**
  - Python 3.12 environment
  - PostgreSQL 15 service
  - Install dependencies: `pip install -r backend/requirements.txt`
  - Run pytest with coverage: `pytest tests/ --cov=app --cov-report=xml`
  - Upload coverage to Codecov

- **Frontend Tests**
  - Node.js 18 environment
  - Type checking: `npm run type-check`
  - Linting: `npm run lint`
  - Build: `npm run build`

**Status Badges:**
- ✅ All tests pass
- ✅ TypeScript compilation succeeds
- ✅ ESLint passes
- ✅ Code coverage tracked

---

### 2. Security Workflow (`security.yml`)

**Triggers:**
- Pull requests (any branch)
- Pushes to `main` branch
- Manual dispatch

**Jobs:**

- **Backend Security Scanning**
  - Bandit: Identifies security issues in Python code
  - Safety: Checks for known vulnerabilities in dependencies
  - Output: JSON report saved as artifact

- **Frontend Security Scanning**
  - npm audit: Checks JavaScript dependencies
  - Audit level: moderate (fails on moderate or high severity)

- **Secret Scanning**
  - TruffleHog: Detects hardcoded secrets
  - Checks: API keys, passwords, tokens

- **Dependency Check**
  - OWASP Dependency-Check: Identifies CVEs
  - Reports: Saved to artifacts for review

**Requirements to Pass:**
- No hardcoded secrets
- No high-severity vulnerabilities in dependencies
- All security scans complete (may warn on medium issues)

---

### 3. Deploy to Staging (`deploy-staging.yml`)

**Triggers:**
- Merges to `main` branch
- Manual dispatch

**Prerequisites:**
- All tests must pass
- Security scans must complete

**Jobs:**

1. **Test & Build**
   - Run backend tests (PostgreSQL service)
   - Build frontend with `npm run build`
   - All must pass to continue

2. **Deploy Backend to Vercel**
   ```bash
   vercel deploy --token $VERCEL_TOKEN
   ```

3. **Deploy Frontend to Vercel**
   ```bash
   cd frontend && vercel deploy --token $VERCEL_TOKEN
   ```

4. **Verify Deployment**
   - Wait 10 seconds for services to start
   - Health check: `curl $STAGING_API_URL/api/organizations`
   - Verify HTTP 200 or 401 response

**Expected Behavior:**
- Automatic deployment when code merged to main
- Takes ~5-10 minutes
- Deploys to Vercel staging environment

---

### 4. Deploy to Production (`deploy-production.yml`)

**Triggers:**
- GitHub Release published
- Manual dispatch

**Environment Protection:**
- Requires manual approval
- Environment: `production`
- Concurrency locked (only one deployment at a time)

**Prerequisites:**
- Security checks must pass
- Release must exist (or manual trigger)

**Jobs:**

1. **Security Check**
   - Run Bandit security scan
   - Fail if high-severity issues found
   - Prevents insecure deployments

2. **Deploy Backend to Production**
   ```bash
   vercel deploy --prod --token $VERCEL_TOKEN
   ```

3. **Deploy Frontend to Production**
   ```bash
   cd frontend && vercel deploy --prod --token $VERCEL_TOKEN
   ```

4. **Run Database Migrations**
   ```bash
   alembic upgrade head
   ```

5. **Smoke Tests**
   - Verify API endpoints respond
   - Retry up to 5 times with 5-second delays
   - Confirm HTTP 200 responses

**Approval Gate:**
- Must manually approve in GitHub Actions
- Only users with production access can approve
- Review deployment details before approval

---

### 5. Database Migrations (`migrate-db.yml`)

**Triggers:**
- Manual dispatch with environment selection
- Called from deploy workflows

**Environments Supported:**
- Staging
- Production

**Jobs:**

- **Staging Migrations**
  - Test database connection
  - Run: `alembic upgrade head`
  - Verify migrations: `alembic current`
  - Rollback on failure: `alembic downgrade -1`

- **Production Migrations**
  - Create backup identifier
  - Test database connection
  - Show pending migrations
  - Run: `alembic upgrade head`
  - Rollback on failure
  - Concurrency lock (no parallel migrations)

**Rollback Capability:**
- Automatic rollback if migration fails
- Rolls back one version: `alembic downgrade -1`
- Requires manual investigation and retry

---

## GitHub Secrets Required

These must be configured in GitHub Settings → Secrets and variables:

### Vercel Deployment
- `VERCEL_TOKEN`: Personal access token from Vercel
- `VERCEL_ORG_ID`: Organization ID in Vercel
- `VERCEL_PROJECT_ID`: Backend project ID in Vercel
- `VERCEL_FRONTEND_PROJECT_ID`: Frontend project ID in Vercel

### Database
- `DATABASE_URL`: PostgreSQL connection string (production)
- `STAGING_DATABASE_URL`: PostgreSQL connection string (staging)

### Environment URLs
- `STAGING_API_URL`: Base URL for staging API (e.g., https://staging-api.vercel.app)
- `PRODUCTION_API_URL`: Base URL for production API

### Optional
- `CODECOV_TOKEN`: For uploading coverage reports

---

## Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Developer creates Pull Request                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Automatic Workflows Trigger                                  │
│    ├─ test.yml (backend + frontend tests)                      │
│    ├─ security.yml (security scanning)                         │
│    └─ All must pass to merge                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Code Review + Approval                                       │
│    ├─ Check test results                                        │
│    ├─ Check security report                                     │
│    └─ Approve & merge to main                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Deploy to Staging (Automatic)                               │
│    ├─ deploy-staging.yml triggers                              │
│    ├─ Run tests again                                          │
│    ├─ Deploy to Vercel staging                                │
│    └─ Verify deployment (health check)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Test in Staging                                              │
│    ├─ Manual QA testing                                        │
│    ├─ Integration testing                                      │
│    └─ Performance testing                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Create Release (Manual)                                     │
│    ├─ Tag version in GitHub                                    │
│    ├─ Create release notes                                     │
│    └─ Publish release                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Deploy to Production (Requires Approval)                    │
│    ├─ deploy-production.yml triggers                           │
│    ├─ Security checks run                                      │
│    ├─ Wait for manual approval                                 │
│    ├─ Run database migrations                                  │
│    ├─ Deploy to Vercel production                             │
│    └─ Run smoke tests                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. Production Live                                              │
│    ├─ Users access production environment                       │
│    ├─ Monitor logs & metrics                                    │
│    └─ Rollback plan ready if needed                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Local Development Workflow

### Running Tests Locally

```bash
# Backend tests
cd backend
pip install -r requirements.txt
pytest tests/ --cov=app -v

# Frontend tests
cd frontend
npm install
npm run type-check
npm run lint
npm run build
```

### Verifying Deployments Locally

```bash
# Use the verify script
./scripts/verify-deployment.sh http://localhost:8000

# Manual verification
curl http://localhost:8000/api/organizations
```

---

## Troubleshooting

### Tests Failing
1. Check test output in GitHub Actions
2. Reproduce locally: `pytest tests/ -v`
3. Fix the issue in your branch
4. Push to update PR

### Security Scanning Warnings
1. Review the security report in artifacts
2. Address high-severity issues
3. Document acceptable risks if needed
4. Update suppression files if false positives

### Deployment Failures
1. Check deployment logs in GitHub Actions
2. Verify all secrets are configured
3. Check Vercel project settings
4. Verify database connectivity

### Migration Failures
1. Check migration file syntax
2. Verify database is accessible
3. Check for conflicts with existing schema
4. Rollback and retry if needed

---

## Best Practices

1. **Always test locally first** before pushing
2. **Write tests for new features** before implementation
3. **Keep migration files clean** and well-documented
4. **Review security reports** before merging
5. **Test in staging** before production deployment
6. **Use semantic versioning** for releases
7. **Keep secrets out of code** - use GitHub Secrets
8. **Monitor deployments** after release

---

## Performance Optimization

### Caching
- pip packages cached between runs
- npm packages cached between runs
- Reduces workflow duration by 30-50%

### Parallel Jobs
- Backend and frontend tests run in parallel
- Reduces overall test time
- Both must pass to continue

### Conditional Execution
- Security checks only run on PRs and main
- Migrations only run when needed
- Production checks only on releases

---

## Monitoring & Alerts

### GitHub Actions Dashboard
- View all workflow runs
- Check individual job logs
- Review artifact downloads

### Vercel Deployment
- Monitor in Vercel dashboard
- Check deployment logs
- View performance metrics

### Codecov Coverage
- Track test coverage over time
- Identify untested code
- Set coverage thresholds

---

**Last Updated**: March 10, 2026
**Status**: ✅ Fully Operational
