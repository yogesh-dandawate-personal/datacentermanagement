# GitHub Secrets Setup Guide

## Overview

GitHub Secrets are encrypted environment variables used by CI/CD workflows. They store sensitive information like API tokens, database credentials, and authentication keys without exposing them in code.

---

## Access Control

### Prerequisites

You need admin access to the GitHub repository. To set secrets:

1. Go to repository Settings
2. Navigate to "Secrets and variables" → "Actions"
3. Click "New repository secret"

---

## Required Secrets

### Vercel Deployment Secrets

These are needed to deploy to Vercel from GitHub Actions.

#### 1. `VERCEL_TOKEN`

**What it is:** Personal access token from Vercel that allows GitHub Actions to deploy

**How to get it:**
1. Go to [vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Click "Create"
3. Name: `GitHub Actions Deployment`
4. Copy the token
5. Keep it secret!

**Add to GitHub:**
1. Go to repo Settings → Secrets
2. Click "New repository secret"
3. Name: `VERCEL_TOKEN`
4. Value: [paste token from Vercel]
5. Click "Add secret"

#### 2. `VERCEL_ORG_ID`

**What it is:** Your Vercel organization/account ID

**How to get it:**
1. Go to [vercel.com/account/settings](https://vercel.com/account/settings)
2. Look for "Team ID" or "Account ID"
3. Copy it

**Add to GitHub:**
1. Name: `VERCEL_ORG_ID`
2. Value: [paste ID from Vercel]
3. Click "Add secret"

#### 3. `VERCEL_PROJECT_ID`

**What it is:** Project ID for your backend in Vercel

**How to get it:**
1. Go to Vercel dashboard
2. Select your backend project
3. Go to Settings → General
4. Look for "Project ID"
5. Copy it

**Add to GitHub:**
1. Name: `VERCEL_PROJECT_ID`
2. Value: [paste ID from Vercel]
3. Click "Add secret"

#### 4. `VERCEL_FRONTEND_PROJECT_ID`

**What it is:** Project ID for your frontend in Vercel

**How to get it:**
1. Go to Vercel dashboard
2. Select your frontend project
3. Go to Settings → General
4. Look for "Project ID"
5. Copy it

**Add to GitHub:**
1. Name: `VERCEL_FRONTEND_PROJECT_ID`
2. Value: [paste ID from Vercel]
3. Click "Add secret"

---

### Database Connection Secrets

These are needed for database migrations and testing.

#### 5. `DATABASE_URL`

**What it is:** PostgreSQL connection string for production database

**Format:**
```
postgresql://username:password@host:port/database_name
```

**Example:**
```
postgresql://admin:password123@prod-db.railway.app:5432/inetzer
```

**How to get it:**
1. Get it from your database provider (Railway, AWS RDS, etc.)
2. Find the connection string in their dashboard

**Add to GitHub:**
1. Go to repo Settings → Secrets → "Environments"
2. Click "production" environment
3. Click "Add secret"
4. Name: `DATABASE_URL`
5. Value: [paste connection string]
6. Click "Add secret"

**Security Note:**
- ⚠️ Never commit this to git
- ⚠️ Never share in Slack or email
- ⚠️ Rotate credentials periodically
- ✅ Use strong passwords (24+ characters)
- ✅ Use database-specific users (not admin)

#### 6. `STAGING_DATABASE_URL`

**What it is:** PostgreSQL connection string for staging database

**Format:** Same as above, but for staging environment

**Add to GitHub:**
1. Go to repo Settings → Secrets → "Environments"
2. Click "staging" environment
3. Click "Add secret"
4. Name: `STAGING_DATABASE_URL`
5. Value: [paste staging connection string]
6. Click "Add secret"

**If using same database for staging:**
```
DATABASE_URL_STAGING=postgresql://staging_user:password@staging-db.railway.app:5432/inetzer_staging
```

---

### Deployment URL Secrets

These are needed for health checks and verification.

#### 7. `STAGING_API_URL`

**What it is:** Base URL for staging API endpoint

**Example:**
```
https://inetzer-staging.vercel.app
```

**How to get it:**
1. Go to Vercel dashboard
2. Select backend project
3. Look for "Domains" section
4. Copy the staging/preview domain

**Add to GitHub:**
1. Go to repo Settings → Secrets
2. Click "New repository secret"
3. Name: `STAGING_API_URL`
4. Value: [paste staging URL]
5. Click "Add secret"

#### 8. `PRODUCTION_API_URL`

**What it is:** Base URL for production API endpoint

**Example:**
```
https://api.yourdomain.com
```

**How to get it:**
1. Go to Vercel dashboard
2. Select backend project
3. Look for "Domains" section
4. Copy the production domain

**Add to GitHub:**
1. Go to repo Settings → Secrets → "Environments"
2. Click "production" environment
3. Click "Add secret"
4. Name: `PRODUCTION_API_URL`
5. Value: [paste production URL]
6. Click "Add secret"

---

### Optional Secrets

#### 9. `CODECOV_TOKEN` (Optional)

**What it is:** Token for Codecov.io (code coverage tracking)

**How to get it:**
1. Go to [codecov.io](https://codecov.io)
2. Sign up with GitHub
3. Connect your repo
4. Go to Settings → Token
5. Copy the upload token

**Add to GitHub:**
1. Name: `CODECOV_TOKEN`
2. Value: [paste token]
3. Click "Add secret"

**Why optional:**
- Only needed if you want code coverage tracking
- Without it, coverage reports still upload but may have rate limits

---

## Secret Rotation Schedule

Rotate secrets regularly for security:

### Monthly Rotation

- `VERCEL_TOKEN` → Generate new token, update GitHub secret
- `CODECOV_TOKEN` → Regenerate if available

### Quarterly Rotation

- `DATABASE_URL` → Change database password
- `STAGING_DATABASE_URL` → Change staging database password

### As Needed

- Any secret that may have been compromised
- Before contractor/team member leaves
- After security audit

---

## Verification Checklist

After setting up all secrets:

- [ ] `VERCEL_TOKEN` - set and valid
- [ ] `VERCEL_ORG_ID` - set and valid
- [ ] `VERCEL_PROJECT_ID` - set and matches backend project
- [ ] `VERCEL_FRONTEND_PROJECT_ID` - set and matches frontend project
- [ ] `DATABASE_URL` - set and connection tested
- [ ] `STAGING_DATABASE_URL` - set and connection tested
- [ ] `STAGING_API_URL` - set and reachable
- [ ] `PRODUCTION_API_URL` - set and reachable
- [ ] `CODECOV_TOKEN` (optional) - set if using coverage

---

## Testing Secrets

### Test Vercel Token

1. Go to GitHub Actions
2. Create a test workflow with:
   ```yaml
   - run: |
       npm install -g vercel
       vercel projects --token ${{ secrets.VERCEL_TOKEN }}
   ```
3. Run workflow
4. If it lists projects, token is valid

### Test Database Connection

1. Create a test workflow with:
   ```yaml
   - run: |
       python -c "from sqlalchemy import create_engine; \
       engine = create_engine('${{ secrets.DATABASE_URL }}'); \
       engine.connect(); print('✅ Connection successful')"
   ```
2. Run workflow
3. If it prints success, connection string is valid

### Test Deployment URLs

1. Run the verify script:
   ```bash
   ./scripts/verify-deployment.sh ${{ secrets.STAGING_API_URL }}
   ```
2. Should see health checks passing

---

## Troubleshooting

### Secret Not Found Error

**Error:** `Undefined secret 'SECRET_NAME'`

**Solution:**
1. Check spelling in workflow matches secret name exactly
2. Check secret is set in repo settings
3. Clear GitHub Actions cache (if using)
4. Wait 5 minutes and retry (sometimes caching issue)

### "Token Unauthorized" Error

**Error:** `Error: Unauthorized (401)`

**Solution:**
1. Verify token is still valid in Vercel dashboard
2. Regenerate token if expired
3. Ensure token has correct permissions
4. Check if token was revoked

### "Connection Refused" Error

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
1. Verify DATABASE_URL is correct
2. Check if database is running/accessible
3. Verify firewall allows GitHub Actions IPs
4. Test connection locally first

### Secrets Not Updating

**Issue:** Changed secret but workflow still uses old value

**Solution:**
1. Secrets are read when workflow starts
2. Restart the workflow to use new secret
3. Clear GitHub Actions cache if needed
4. Wait 1-2 minutes for propagation

---

## Best Practices

### Security

- ✅ Use strong, random values (20+ characters)
- ✅ Rotate secrets quarterly
- ✅ Use environment-specific secrets (prod vs staging)
- ✅ Limit who has access to settings
- ✅ Audit secret usage regularly

### Organization

- ✅ Document what each secret is for
- ✅ Keep list in team wiki/docs
- ✅ Track rotation dates
- ✅ Use consistent naming (`_STAGING`, `_PRODUCTION`)

### Preventing Leaks

- ❌ Don't commit secrets to git
- ❌ Don't paste secrets in chat
- ❌ Don't send secrets in emails
- ❌ Don't hardcode secrets in workflows
- ✅ Always use `${{ secrets.SECRET_NAME }}`

---

## Migration from Environment Files

If you're moving from `.env` files:

### Step 1: Create GitHub Secrets

For each variable in `.env`:
```env
VERCEL_TOKEN=abc123...
DATABASE_URL=postgresql://...
```

Create corresponding GitHub secret.

### Step 2: Update `.env.example`

Keep only non-sensitive values:
```env
# VERCEL_TOKEN=          # Set in GitHub Secrets
# DATABASE_URL=          # Set in GitHub Secrets
DEBUG=false
PORT=8000
```

### Step 3: Update Workflows

Replace `.env` references:
```yaml
# Before
env:
  DATABASE_URL: $(cat .env | grep DATABASE_URL)

# After
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Step 4: Verify

1. Remove `.env` from repo
2. Update `.gitignore` if needed
3. Run workflow to verify it works
4. Delete `.env` from git history

---

## Support

If you need help:

1. Check workflow logs for specific error
2. Review this guide for your specific scenario
3. Test secrets locally if possible
4. Contact DevOps team if still stuck

---

## Quick Reference

```bash
# Add a new secret (via CLI if available)
gh secret set SECRET_NAME --body "secret_value"

# List all secrets
gh secret list

# Delete a secret
gh secret delete SECRET_NAME

# View secret in workflow (for debugging)
echo ${{ secrets.SECRET_NAME }}  # Only visible in logs if explicitly done
```

---

**Last Updated**: March 10, 2026
**Review Date**: March 24, 2026
