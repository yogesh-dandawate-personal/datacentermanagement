# Vercel Environment Variables Setup

This guide explains how to configure environment variables in Vercel for the NetZero API to connect to your Railway.sh PostgreSQL database.

## Overview

Once your Railway PostgreSQL database is running, you need to add the connection string to Vercel's environment variables so your deployed API can access the database.

## Prerequisites

- ✅ Vercel project created and linked to GitHub
- ✅ Railway PostgreSQL instance running
- ✅ Connection string copied from Railway dashboard
  - Format: `postgresql://postgres:password@host:5432/database?sslmode=require`

---

## Step 1: Go to Vercel Project Settings

1. Open https://vercel.com/dashboard
2. Click on your project (`netzero` or similar)
3. Click **"Settings"** (in the top navigation bar)
4. Click **"Environment Variables"** (in the left sidebar)

---

## Step 2: Add DATABASE_URL

1. Click **"Add New"** button
2. Fill in the fields:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the connection string from Railway:
     ```
     postgresql://postgres:SecurePassword123@containers-us-west.railway.internal:5432/railway?sslmode=require
     ```
   - **Environments**: Select which environments need this variable:
     - ✅ **Production** (required)
     - ✅ **Preview** (optional, for staging tests)
     - ✅ **Development** (optional, for local testing)
3. Click **"Save"**

**Example**:
```
Name: DATABASE_URL
Value: postgresql://postgres:MySecurePassword@containers-us-west.railway.internal:5432/railway?sslmode=require
Environments: Production ✓ Preview ✓ Development ✓
```

---

## Step 3: Add Connection Pool Configuration

Add the following environment variables to configure connection pooling:

### DATABASE_POOL_SIZE

1. Click **"Add New"**
2. **Name**: `DATABASE_POOL_SIZE`
3. **Value**: `20`
4. **Environments**: Production ✓ Preview ✓
5. Click **"Save"**

### DATABASE_POOL_MAX_OVERFLOW

1. Click **"Add New"**
2. **Name**: `DATABASE_POOL_MAX_OVERFLOW`
3. **Value**: `40`
4. **Environments**: Production ✓ Preview ✓
5. Click **"Save"**

### DATABASE_POOL_PRE_PING

1. Click **"Add New"**
2. **Name**: `DATABASE_POOL_PRE_PING`
3. **Value**: `true`
4. **Environments**: Production ✓ Preview ✓
5. Click **"Save"**

---

## Step 4: Verify Variables Are Set

1. Go to **Settings** → **Environment Variables**
2. You should see all variables listed:
   ```
   DATABASE_URL = ••••••••••••••••••••••••••••
   DATABASE_POOL_SIZE = 20
   DATABASE_POOL_MAX_OVERFLOW = 40
   DATABASE_POOL_PRE_PING = true
   ```

3. Click on `DATABASE_URL` to verify it's set correctly
4. It should show the beginning and end masked but still indicate it's set

---

## Step 5: Redeploy to Apply Changes

After adding/modifying environment variables, Vercel doesn't automatically apply them to existing deployments. You need to redeploy:

**Option 1: Redeploy from Dashboard**
1. Go to your Vercel project
2. Click **"Deployments"**
3. Click the three-dot menu (⋯) on the latest deployment
4. Select **"Redeploy"**
5. Wait for deployment to complete

**Option 2: Redeploy via Git**
1. Make a small commit and push to main branch:
   ```bash
   git commit --allow-empty -m "Trigger redeploy with new environment variables"
   git push origin main
   ```
2. Vercel will automatically redeploy

---

## Step 6: Verify Deployment

Once redeployed, verify the API is working:

1. Open your Vercel deployment URL:
   - Format: `https://<project-name>.vercel.app`
2. Test the health endpoint:
   ```bash
   curl https://<your-domain>.vercel.app/api/v1/health
   ```

   **Expected response** (200 OK):
   ```json
   {
     "status": "healthy",
     "service": "NetZero API",
     "version": "1.0.0",
     "timestamp": "2026-03-10T12:34:56.789012"
   }
   ```

3. Test the organizations endpoint:
   ```bash
   curl https://<your-domain>.vercel.app/api/organizations
   ```

   **Expected response** (200 OK):
   ```json
   []
   ```

---

## Environment Variables Reference

| Variable | Value | Purpose | Required |
|----------|-------|---------|----------|
| `DATABASE_URL` | `postgresql://...` | Database connection string | ✅ Yes |
| `DATABASE_POOL_SIZE` | `20` | Max connections in pool | ✅ Yes |
| `DATABASE_POOL_MAX_OVERFLOW` | `40` | Extra connections allowed | ✅ Yes |
| `DATABASE_POOL_PRE_PING` | `true` | Test connections before use | ✅ Yes |

---

## Troubleshooting

### Issue: Still getting 500 error after redeploy

**Solution**:
1. Check Vercel deployment logs:
   - Go to Deployments → Click deployment → Click "Logs"
   - Look for database connection errors
2. Verify `DATABASE_URL` is set:
   - Settings → Environment Variables
   - Click on DATABASE_URL
   - Confirm it's populated (not empty)
3. Verify Railway connection string is correct:
   - Go to Railway dashboard
   - Copy fresh connection string
   - Update in Vercel (overwrite old value)
4. Redeploy again

### Issue: Connection timeout errors

**Solution**:
- Railway may have connection limits on free tier
- Reduce `DATABASE_POOL_SIZE` from 20 to 5
- Increase `DATABASE_POOL_MAX_OVERFLOW` from 40 to 10
- Test again

### Issue: SSL certificate errors

**Solution**:
- Verify connection string includes `?sslmode=require`
- Don't use `?sslmode=disable` in production
- Update connection string if Railway region changed

### Issue: Can't see environment variable values in Vercel

**Solution**:
- This is by design (security)
- Vercel only shows the first 4 characters and last 4 characters
- To update, click on the variable, delete, and re-add with new value

---

## Advanced: Environment-Specific Configuration

You can set different values for different Vercel environments:

### Production Database (Primary)
```
DATABASE_URL = postgresql://user:password@prod-host/prod_db
DATABASE_POOL_SIZE = 30         # Higher for production
```

### Preview Database (Staging)
```
DATABASE_URL = postgresql://user:password@staging-host/staging_db
DATABASE_POOL_SIZE = 10         # Lower for staging
```

### Development (Local)
```
# Set locally in .env file, not in Vercel
DATABASE_URL = postgresql://localhost/netzero_dev
```

---

## Vercel Secrets (Optional - for sensitive variables)

For highly sensitive values, use Vercel Secrets instead:

1. Go to **Settings** → **Secrets (Git environments)**
2. This syncs with GitHub Secrets
3. More secure than Environment Variables

---

## Monitoring Deployments

To monitor your environment variables are being used correctly:

1. Go to **Deployments**
2. Click on active deployment
3. Click **"Logs"** tab
4. Filter for "DATABASE" to see connection logs:
   ```
   INFO  [app.database] Using PostgreSQL database: containers-us-west.railway.internal
   INFO  [app.database] Connection pool configured:
      - Pool size: 20
      - Max overflow: 40
      - Pre-ping enabled: True
   ```

---

## Next Steps

1. ✅ Set DATABASE_URL in Vercel
2. ✅ Set connection pool variables
3. ✅ Redeploy application
4. ✅ Test health endpoint
5. ✅ Monitor logs for errors
6. 📋 Run migrations (if applicable)
7. 📋 Verify production API calls work
8. 📋 Set up monitoring alerts (optional)

---

## Reference

- **Vercel Environment Variables**: https://vercel.com/docs/projects/environment-variables
- **Vercel Secrets**: https://vercel.com/docs/concepts/projects/environment-variables/managing-environment-variables
- **Railway.sh Documentation**: https://docs.railway.app
- **SQLAlchemy Connection Pooling**: https://docs.sqlalchemy.org/en/20/core/pooling.html

---

**Last Updated**: 2026-03-10
**Status**: Ready to use
