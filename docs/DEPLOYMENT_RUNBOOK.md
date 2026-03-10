# Deployment Runbook

## Quick Start Guide

### Prerequisites

Before deploying to production, ensure:
- [ ] All tests pass (GitHub Actions)
- [ ] Security scans complete with no high-severity issues
- [ ] Code reviewed and approved
- [ ] Staging deployment tested
- [ ] Database backup available (if applicable)

---

## Staging Deployment

### Automatic Staging Deployment

Staging deployments are **automatic** when you merge code to the `main` branch.

**Timeline:**
1. Merge PR to `main` → Test workflow runs (5 min)
2. Tests pass → Deploy workflow runs (5-10 min)
3. Deployment complete → Automatic health check (1 min)
4. **Total time: 11-16 minutes**

### Manual Staging Deployment

If you need to redeploy staging:

1. Go to GitHub Actions
2. Click "Deploy to Staging" workflow
3. Click "Run workflow"
4. Select `main` branch
5. Click "Run workflow"
6. Monitor logs for completion

### Verify Staging Deployment

```bash
# Run verification script
./scripts/verify-deployment.sh https://staging-api.vercel.app

# Or manually
curl https://staging-api.vercel.app/api/organizations

# Expected response: HTTP 200 or 401 (auth required)
```

---

## Production Deployment

### Step 1: Create a Release

1. Go to GitHub repo
2. Click "Releases" → "Draft a new release"
3. Enter version number (e.g., `v1.0.0`)
4. Click "Generate release notes"
5. Review changes
6. Click "Publish release"

### Step 2: Approve Deployment

1. Go to GitHub Actions
2. Find "Deploy to Production" workflow run
3. It will be waiting for approval
4. Review:
   - Git commit hash
   - Security scan results
   - Deployment environment (production)
5. Click "Review deployments"
6. Select "production"
7. Click "Approve and deploy"

### Step 3: Monitor Deployment

1. Watch the deployment logs in real-time
2. Check for:
   - ✅ Security checks passing
   - ✅ Backend deployment successful
   - ✅ Frontend deployment successful
   - ✅ Database migrations successful
   - ✅ Smoke tests passing
3. If any step fails, logs will show error details

### Step 4: Verify Production

1. Test production endpoints:
   ```bash
   ./scripts/verify-deployment.sh https://api.yourdomain.com
   ```

2. Manual verification:
   ```bash
   curl https://api.yourdomain.com/api/organizations
   ```

3. Check Vercel dashboard:
   - Both projects deployed
   - No errors in logs
   - Deployment time < 2 minutes

---

## Rollback Procedures

### Automatic Rollback (if deployment fails)

**Triggers automatically if:**
- Security checks fail
- Database migrations fail
- Health checks fail after deployment

**What happens:**
1. GitHub Actions stops the workflow
2. Database migrations are rolled back (if applicable)
3. Previous Vercel deployment remains live
4. Slack notification sent (if configured)

### Manual Rollback

If production is broken and needs immediate rollback:

#### Option 1: Revert in Vercel (Fastest - 1 minute)

1. Go to Vercel dashboard
2. Select the production project
3. Find the previous successful deployment
4. Click "Redeploy"
5. Confirm redeployment
6. **Verify**: API responds with HTTP 200

#### Option 2: Rollback Database (if migrations caused issue)

1. Connect to production database
2. Run rollback:
   ```bash
   cd backend
   alembic current              # Check current version
   alembic downgrade -1         # Rollback one version
   alembic current              # Verify rollback
   ```
3. Verify API responds
4. **Important**: Only do this if you understand the migration!

#### Option 3: Full Rollback Workflow

Use GitHub Actions to trigger manual rollback:

1. Go to GitHub Actions
2. Create/use a "Rollback" workflow (manual dispatch)
3. Run with previous commit hash
4. Redeploy that specific version

---

## Database Migration Management

### Pre-Migration Checklist

- [ ] Database backup created (automatic)
- [ ] Migration file reviewed for correctness
- [ ] Migration tested in local environment
- [ ] Estimated downtime acceptable (if any)
- [ ] Rollback plan documented

### Running Migrations Manually

**Staging:**
```bash
# Via GitHub Actions (Recommended)
1. Go to Actions → "Database Migrations"
2. Click "Run workflow"
3. Select "staging"
4. Monitor logs
```

**Production:**
```bash
# Via GitHub Actions (Recommended)
1. Go to Actions → "Database Migrations"
2. Click "Run workflow"
3. Select "production"
4. Wait for approval prompt
5. Approve deployment
6. Monitor logs for success
```

**Local (Emergency Only):**
```bash
cd backend
export DATABASE_URL="your-prod-connection-string"
alembic upgrade head
```

### Verifying Migrations

After migrations complete:

```bash
# Check migration history
cd backend
alembic history -v

# Check current version
alembic current

# List pending migrations
alembic heads
```

---

## Common Issues & Solutions

### Issue: Tests Failing in CI/CD

**Symptoms:** Test workflow fails on `pytest`

**Solution:**
```bash
# Reproduce locally
cd backend
pip install -r requirements.txt
pytest tests/ -v

# Fix the failing test
# Push fix to your PR
```

### Issue: Security Scan Reports Vulnerabilities

**Symptoms:** Security workflow shows vulnerabilities

**Solution:**

1. Review Bandit report in workflow artifacts
2. For false positives, add suppression comment above code:
   ```python
   # nosec B607
   os.system(command)  # Reviewed, acceptable risk
   ```
3. For real issues, update dependency:
   ```bash
   pip install --upgrade vulnerable-package
   ```

### Issue: Deployment Takes Too Long

**Symptoms:** Deployment doesn't complete within 30 minutes

**Solution:**
- Check for network issues
- Verify Vercel credentials are valid
- Check if Vercel API is responding
- If >5 min, it may be normal (especially first deploy)

### Issue: Database Migration Rollback

**Symptoms:** Migration failed and needs rollback

**Solution:**

1. Automatic rollback will try first
2. If manual needed:
   ```bash
   cd backend
   alembic downgrade -1
   ```
3. Investigate failure
4. Fix migration file
5. Retry with corrected version

### Issue: Staging Works, Production Fails

**Symptoms:** Deployment passes in staging but fails in prod

**Solution:**

1. Check environment variable differences
2. Verify production secrets are correct
3. Check database differences
4. Test migrations on production schema
5. Revert and diagnose

---

## Hotfix Procedure

When you need to deploy an urgent fix:

### Step 1: Create Hotfix Branch

```bash
git checkout -b hotfix/issue-description
# Make your minimal fix
git add .
git commit -m "hotfix: describe the issue fixed"
```

### Step 2: Fast-Track Approval

1. Create PR from `hotfix/...` to `main`
2. Mark as "Urgent" in PR title: `[URGENT] Fix X`
3. Request immediate review
4. Automated tests must still pass

### Step 3: Deploy Immediately

1. Merge to `main` (auto-deploy to staging)
2. Verify in staging (5 minutes)
3. Create release immediately
4. Approve production deployment
5. Monitor closely

### Step 4: Post-Deployment

1. Verify fix resolved the issue
2. Monitor logs for 30 minutes
3. Document issue and fix for future
4. Plan permanent solution

---

## Monitoring After Deployment

### First 15 Minutes (Critical)

- [ ] Check Vercel deployment logs (no errors)
- [ ] Test health endpoints
- [ ] Check error logs in monitoring tool
- [ ] Verify no spike in API response times

### First Hour

- [ ] Monitor CPU and memory usage
- [ ] Check database query performance
- [ ] Verify all endpoints responding
- [ ] Check for any user-reported issues

### Next 24 Hours

- [ ] Daily review of logs
- [ ] Check error rates vs. baseline
- [ ] Verify feature works as expected
- [ ] Check performance metrics

### If Issues Found

```
Issues Found?
    ↓
Severity = High?
    ↓ YES           ↓ NO
  Rollback       Monitor
    ↓              ↓
Fix & Test      Schedule Fix
    ↓              ↓
Redeploy        Fix in Next Release
```

---

## Deployment Checklist

Before you start:
- [ ] All PRs merged to `main`
- [ ] All tests passing
- [ ] No high-severity security issues
- [ ] Staging tested and verified
- [ ] Team notified of deployment

During deployment:
- [ ] Create release in GitHub
- [ ] Monitor approval workflow
- [ ] Watch deployment logs
- [ ] Verify each step completes

After deployment:
- [ ] Run verification script
- [ ] Test key endpoints manually
- [ ] Check Vercel deployment logs
- [ ] Verify database state
- [ ] Monitor for 1 hour

---

## Contacts & Escalation

### Deployment Issues

1. **Check GitHub Actions** logs first
2. **Check Vercel dashboard** for deployment details
3. **Check database connectivity** if migrations failed
4. **Contact DevOps team** if unable to resolve

### Emergency Contacts

- **On-call DevOps**: [phone/slack]
- **Database Admin**: [contact]
- **Security Team**: [contact]

---

## Documentation Links

- [CI/CD Flow Diagram](./CI_CD_FLOW.md)
- [GitHub Secrets Setup](./GITHUB_SECRETS_SETUP.md)
- [Database Backup Guide](./DATABASE_BACKUP.md)
- [Rollback Procedures](./ROLLBACK_GUIDE.md)

---

**Last Updated**: March 10, 2026
**Next Review**: March 17, 2026
**Owned by**: DevOps Team
