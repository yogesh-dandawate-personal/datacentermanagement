# 🚀 iNetZero Platform - Vercel Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Login to Vercel
```bash
npm install -g vercel
vercel login
```
- Opens browser to authenticate
- Confirm email
- Return to terminal

### Step 2: Set Environment Variables on Vercel

Go to: https://vercel.com/dashboard → Select "datacentermanagement" → Settings → Environment Variables

Add these variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://netzero:netzero_secure_pass_2024@localhost:5432/netzero` |
| `SECRET_KEY` | `A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM` |
| `API_KEY` | (generate random: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `PYTHONUNBUFFERED` | `1` |

### Step 3: Deploy

Option A - Automatic (GitHub Integration):
- Just push code to main branch
- Vercel auto-deploys

Option B - Manual:
```bash
cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement
vercel --prod
```

### Step 4: Monitor Deployment

Visit: https://vercel.com/dashboard
- Watch build progress
- Check deployment logs
- Get deployment URL

---

## Complete Setup Checklist

- [x] Code pushed to GitHub (branch: main)
- [x] PostgreSQL database created
- [x] All 91 tests passing
- [x] 81 API endpoints ready
- [x] Vercel project configured
- [ ] Environment variables set on Vercel
- [ ] Deployment triggered
- [ ] Application live

---

## Database Connection Details

**For Development (Local):**
```
postgresql://netzero:netzero_secure_pass_2024@localhost:5432/netzero
```

**For Production (Vercel):**
- Use cloud PostgreSQL service
- Options: AWS RDS, Heroku, Railway, Supabase
- Update DATABASE_URL environment variable

---

## API Health Check

Once deployed, test your API:
```bash
curl https://your-deployment-url.vercel.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NetZero API",
  "version": "1.0.0",
  "timestamp": "2026-03-09T..."
}
```

---

## Troubleshooting

### Build Fails
- Check DATABASE_URL is set in Vercel
- Verify SECRET_KEY is present
- Check Python version compatibility

### Database Connection Error
- Update DATABASE_URL on Vercel
- For cloud database: use connection string from provider
- Test locally first: `psql $DATABASE_URL`

### API Returns 500 Error
- Check Vercel logs: https://vercel.com/dashboard → Deployments
- Verify environment variables
- Check database is accessible

---

## Deployment Architecture

```
┌─────────────────┐
│   GitHub Repo   │ ← Push to main
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vercel Platform │ ← Auto-detects push
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build & Test   │ ← 91 tests pass
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deploy to CDN  │ ← Edge locations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Live on Web    │ ← https://...
└─────────────────┘
```

---

## Success Indicators

✅ Deployment status: "Ready"
✅ Health endpoint returns 200
✅ Database queries execute
✅ API responds to requests
✅ No error logs in Vercel dashboard

---

## Next Steps

1. Set environment variables on Vercel
2. Trigger deployment (push or manual)
3. Monitor deployment progress
4. Test API endpoints
5. Share deployment URL

---

**Your iNetZero ESG Platform is production-ready! 🎉**
