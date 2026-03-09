# Vercel Production Fix - DATABASE_URL Configuration

**Status**: 🔧 FIXING 500 INTERNAL_SERVER_ERROR

## Problem
The deployed API was returning: **500: INTERNAL_SERVER_ERROR** with message "This Serverless Function has crashed"

## Root Cause
`DATABASE_URL` environment variable was not set in Vercel, causing the app to fail when trying to connect to the database.

## Solution (Implemented)

### 1. **Updated database.py** ✅
- Made database connection resilient to missing DATABASE_URL
- Falls back to SQLite in-memory when DATABASE_URL not provided
- Added connection pooling and timeout handling
- Added detailed logging

### 2. **Updated vercel.json** ✅
- Added `DATABASE_URL` to environment variables configuration
- Updated to use Vercel secrets: `"@database_url"`

### 3. **Updated main.py** ✅
- Enhanced error handling with helpful messages
- Logs full exception details for debugging
- Provides specific error message for database connection failures

## Setup Steps for Production

### Option A: Using Vercel Dashboard (Recommended)

1. Go to: https://vercel.com/dashboard/projects
2. Click on your **iNetZero** project
3. Navigate to **Settings** → **Environment Variables**
4. Add new environment variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string
   - **Environment**: Production
   - Example: `postgresql://username:password@hostname:5432/netzero_prod`

5. Click **Save**
6. Trigger a new deployment:
   ```bash
   git push origin main
   ```

### Option B: Using Vercel CLI

```bash
# Set environment variable for production
vercel env add DATABASE_URL

# When prompted, select "Production"
# Paste your PostgreSQL connection string

# Redeploy
vercel --prod
```

### Option C: Using GitHub Integration

If using Vercel's GitHub integration:
1. Push changes to main branch
2. Add DATABASE_URL in Vercel dashboard before deployment
3. Vercel will automatically build and deploy with the env var

## Testing the Fix

### 1. **Local Testing** (Without DATABASE_URL)
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -c "from app.models import *; from app.database import get_db; print('✅ All imports work')"
```

### 2. **Health Check Endpoint**
After deploying to Vercel with DATABASE_URL set:

```bash
curl https://datacentermanagement-pn26k8vfq-yogesh-dandawates-projects.vercel.app/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "NetZero API",
#   "version": "1.0.0",
#   "timestamp": "2026-03-09T22:30:00.000Z"
# }
```

### 3. **Organization Endpoints**
Once health check passes, test organization endpoints:

```bash
# Get current user (requires auth token)
curl -H "Authorization: Bearer {TOKEN}" \
  https://datacentermanagement-pn26k8vfq-yogesh-dandawates-projects.vercel.app/api/v1/users/me
```

## Database Connection String Format

For **PostgreSQL** (recommended for production):
```
postgresql://username:password@hostname:port/database_name

Examples:
- Local: postgresql://postgres:password@localhost:5432/netzero
- Supabase: postgresql://postgres:password@db.abc123.supabase.co:5432/postgres
- AWS RDS: postgresql://admin:password@netzero-prod.abc123.us-east-1.rds.amazonaws.com:5432/netzero
```

## Troubleshooting

### Still Getting 500 Error?

1. **Check Vercel Logs**:
   ```bash
   vercel logs https://datacentermanagement-pn26k8vfq-yogesh-dandawates-projects.vercel.app
   ```

2. **Verify Environment Variable**:
   - Confirm DATABASE_URL is set in Vercel dashboard
   - Check that it's set for Production environment
   - Verify the connection string is correct

3. **Test Database Connection Locally**:
   ```bash
   psql "postgresql://username:password@hostname:5432/database"
   ```

4. **Check if Database Exists**:
   - Ensure the database specified in the connection string exists
   - Run migrations if needed

### Connection Refused?
- **Cause**: PostgreSQL server not accessible from Vercel
- **Fix**: Ensure your database allows connections from Vercel's IP ranges
- For Supabase: Enable Network Access in Project Settings

### Invalid Credentials?
- **Cause**: Wrong username/password in DATABASE_URL
- **Fix**: Double-check credentials in database provider dashboard

### Timeout?
- **Cause**: Database server taking too long to respond
- **Fix**: Check database server status, reduce connection timeout if needed

## Files Modified

| File | Change |
|------|--------|
| `backend/app/database.py` | Made resilient to missing DATABASE_URL |
| `vercel.json` | Added DATABASE_URL to env config |
| `backend/app/main.py` | Enhanced error handling and logging |

## Next Steps

1. ✅ Deploy this fix to Vercel: `git push origin main`
2. ✅ Set DATABASE_URL in Vercel dashboard
3. ✅ Test health check endpoint
4. ✅ Test organization endpoints
5. ✅ Monitor Vercel logs for any issues

## Deployment Verification Checklist

- [ ] DATABASE_URL set in Vercel dashboard (Production)
- [ ] Code pushed to main branch
- [ ] Vercel deployment completed (no build errors)
- [ ] Health check endpoint responds with 200
- [ ] Organization endpoints accessible with auth token
- [ ] No 500 errors in Vercel logs

---

**Status**: Ready for deployment ✅
**Last Updated**: 2026-03-09
**Estimated Resolution Time**: < 5 minutes (after setting DATABASE_URL)

