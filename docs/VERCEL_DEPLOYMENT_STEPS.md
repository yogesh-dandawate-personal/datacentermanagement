# Vercel Staging Deployment - Step by Step Guide

**Status**: Ready to Deploy
**Date**: 2026-03-09
**Staging URL**: https://inetzero-staging.vercel.app

---

## 📋 Prerequisites

- ✅ Vercel account (create at https://vercel.com if needed)
- ✅ Code pushed to GitHub ✓
- ✅ Environment variables generated ✓

---

## 🚀 Deployment Steps

### STEP 1: Go to Vercel Dashboard

1. Open https://vercel.com/dashboard
2. You should see your projects
3. Look for **"netzero"** project in the list

**If you don't see netzero**:
- Click "New Project"
- Select your GitHub repository: `yogesh-dandawate-personal/datacentermanagement`
- Click "Import"
- Click "Deploy"
- Continue to Step 2

---

### STEP 2: Select the Project

1. Click on the **"netzero"** project
2. You'll see:
   - Project name: "netzero"
   - Latest deployment status
   - Domains section
   - Settings menu

---

### STEP 3: Access Environment Variables

1. Click on **"Settings"** tab (top menu)
2. On the left sidebar, click **"Environment Variables"**
3. You should see an input area that says "Add new"

---

### STEP 4: Add Environment Variables

**Variable 1: SECRET_KEY**

1. In the "Name" field, type: `SECRET_KEY`
2. In the "Value" field, paste:
   ```
   A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM
   ```
3. Make sure "Production", "Preview", and "Development" are all checked
4. Click **"Add"** button

**Variable 2: DATABASE_URL**

1. Click "Add new" again
2. In the "Name" field, type: `DATABASE_URL`
3. In the "Value" field, paste your PostgreSQL connection string:

   **Option A: If you have your own database**
   ```
   postgresql://user:password@hostname:5432/netzero_staging
   ```

   **Option B: Using Supabase (FREE - Recommended)**
   - Go to https://supabase.com
   - Sign up for free account
   - Create new project
   - Go to Settings > Database
   - Copy the "Connection string" that looks like:
   ```
   postgresql://postgres.[PROJECT-ID].supabase.co:5432/postgres?password=[PASSWORD]
   ```

4. Make sure "Production", "Preview", and "Development" are all checked
5. Click **"Add"** button

**Variable 3: API_TITLE**

1. Click "Add new" again
2. Name: `API_TITLE`
3. Value: `NetZero API`
4. Click **"Add"** button

**Variable 4: DEBUG**

1. Click "Add new" again
2. Name: `DEBUG`
3. Value: `false`
4. Click **"Add"** button

**Variable 5: API_VERSION**

1. Click "Add new" again
2. Name: `API_VERSION`
3. Value: `1.0.0`
4. Click **"Add"** button

**Variable 6: LOG_LEVEL**

1. Click "Add new" again
2. Name: `LOG_LEVEL`
3. Value: `info`
4. Click **"Add"** button

---

### STEP 5: Verify All Variables Are Added

You should now see all 6 variables:
```
✓ SECRET_KEY = A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM
✓ DATABASE_URL = postgresql://...
✓ API_TITLE = NetZero API
✓ DEBUG = false
✓ API_VERSION = 1.0.0
✓ LOG_LEVEL = info
```

---

### STEP 6: Navigate to Deployments

1. Click on **"Deployments"** tab (top menu)
2. You should see deployment history with latest commits
3. Find the latest deployment (usually at top)
4. It should show the latest commit message: "Add deployment summary - Sprints 1-3 ready for production"

---

### STEP 7: Redeploy with New Environment Variables

1. Find the latest deployment in the list
2. Click the **three dots (⋯)** menu on the right
3. Click **"Redeploy"**
4. A dialog appears asking to confirm
5. Click **"Redeploy"** button in the dialog

**You'll see**:
- Status changes to "Building"
- Then "Initializing"
- Then "Ready" ✅

This usually takes **2-3 minutes**.

---

### STEP 8: Verify Deployment Success

Once deployment shows "Ready" (green checkmark):

1. Go to **"Domains"** section
2. Click on the domain: **inetzero-staging.vercel.app**
3. Or copy this URL: https://inetzero-staging.vercel.app

---

### STEP 9: Test Your API

Open a terminal and test the endpoints:

**Health Check** (should return 200 OK):
```bash
curl https://inetzero-staging.vercel.app/api/v1/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "NetZero API",
  "version": "1.0.0",
  "timestamp": "2026-03-09T..."
}
```

**Create a Tenant** (test POST endpoint):
```bash
curl -X POST https://inetzero-staging.vercel.app/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Organization",
    "slug": "test-org",
    "email": "admin@test.com"
  }'
```

**View API Documentation**:
- Swagger UI: https://inetzero-staging.vercel.app/api/docs
- ReDoc: https://inetzero-staging.vercel.app/api/redoc

---

### STEP 10: Check Deployment Logs (If Issues)

If deployment fails:

1. Click on the failed deployment
2. Look for the error message in the build logs
3. Common issues:
   - **"Module not found"**: Missing Python dependency
   - **"Connection refused"**: DATABASE_URL is wrong
   - **"Timeout"**: Database connection timing out

**Solution**:
- Fix the issue (e.g., update DATABASE_URL)
- Go back to Step 5
- Redeploy

---

## ✅ Deployment Checklist

- [ ] Visited https://vercel.com/dashboard
- [ ] Selected "netzero" project
- [ ] Clicked "Settings" > "Environment Variables"
- [ ] Added SECRET_KEY variable
- [ ] Added DATABASE_URL variable
- [ ] Added API_TITLE variable
- [ ] Added DEBUG = false variable
- [ ] Added API_VERSION variable
- [ ] Added LOG_LEVEL variable
- [ ] Clicked "Deployments" tab
- [ ] Clicked "Redeploy" on latest commit
- [ ] Waited for deployment to complete (green checkmark)
- [ ] Tested health endpoint: `curl https://inetzero-staging.vercel.app/api/v1/health`
- [ ] Got 200 OK response

---

## 🎉 You're Done!

Your staging environment is now live at:
### **https://inetzero-staging.vercel.app**

---

## 📊 What's Deployed

**Sprints 1-3 (R0-R3 Complete)**:
- ✅ Sprint 1: Authentication & Tenant Setup (R0-R7 complete)
- ✅ Sprint 2: Organization Hierarchy (R0-R3 complete)
- ✅ Sprint 3: Facility Management (R0-R3 complete)

**API Endpoints Available**:
- POST `/api/v1/tenants` - Create tenant
- POST `/api/v1/auth/login` - User login
- GET `/api/v1/users/me` - Get current user
- GET `/api/v1/health` - Health check
- POST `/api/v1/orgs` - Create organization
- GET `/api/v1/orgs` - List organizations
- GET `/api/v1/orgs/{id}` - Get org details
- And 8+ more endpoints for organizations and facilities

---

## 🔧 Next Steps After Deployment

### 1. Verify Everything Works
```bash
# Test all key endpoints
curl https://inetzero-staging.vercel.app/api/v1/health
curl https://inetzero-staging.vercel.app/api/docs
```

### 2. Share with Stakeholders
- Send them the staging URL
- Let them test the API
- Get feedback

### 3. Configure Real Database (if using test DB)
- If you used a test database or left it blank
- Update DATABASE_URL in Vercel Environment Variables
- Redeploy

### 4. Monitor Logs
- In Vercel dashboard
- Click on your deployment
- View "Logs" tab to see API calls and errors

### 5. Plan Production Deployment
- Once stakeholders approve staging
- Repeat these steps for production domain
- Or we can do it together

---

## 🆘 Troubleshooting

### Problem: "500 Internal Server Error"
**Solution**:
- Check DATABASE_URL in Environment Variables
- Make sure it's a valid PostgreSQL connection string
- Verify database is running and accessible

### Problem: "Module not found"
**Solution**:
- Check backend/requirements.txt is committed
- Vercel will install dependencies automatically

### Problem: "Deployment taking too long"
**Solution**:
- First deployment is slower (installs Python packages)
- Subsequent deployments are faster
- Wait up to 5 minutes

### Problem: "Domain not working"
**Solution**:
- Wait 30 seconds for DNS to propagate
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private window

---

## 📞 Support

If you need help:
1. Check Vercel logs: Dashboard > Deployments > [Latest] > Logs
2. Review this guide: docs/DEPLOYMENT_GUIDE.md
3. Check API status: https://inetzero-staging.vercel.app/api/v1/health

---

**Deployment Guide Created**: 2026-03-09
**Platform**: Sprints 1-3 Ready
**Status**: 🚀 Ready to Deploy!

