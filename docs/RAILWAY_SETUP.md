# Railway.sh PostgreSQL Setup Guide

This guide walks you through setting up a PostgreSQL database on Railway.sh (free tier) for the NetZero ESG Platform.

## Why Railway.sh?

- **Free Tier**: $5/month credit (no credit card required)
- **PostgreSQL 15+**: Latest version with full feature support
- **SSL Support**: Secure connections out of the box
- **Easy Integration**: Simple environment variable setup
- **Scalable**: Can upgrade when needed

---

## Step 1: Create Railway.sh Account

1. Go to https://railway.app
2. Click **"Start Free"** or **"Sign Up"**
3. Choose sign-up method (GitHub, Google, or email)
4. Verify email (if using email signup)
5. You'll be taken to the Railway dashboard

**Note**: No credit card required for free tier ($5/month credit)

---

## Step 2: Create PostgreSQL Project

1. In Railway dashboard, click **"New Project"**
2. Select **"Provision PostgreSQL"** or **"PostgreSQL"**
3. Railway will auto-create a new PostgreSQL 15 instance
4. Wait for the service to start (usually 30-60 seconds)

---

## Step 3: Get Connection String

1. Click on the PostgreSQL service in your project
2. Go to the **"Connect"** tab
3. Look for the **"Database URL"** or **"DATABASE_URL"**
4. It will look like:
   ```
   postgresql://postgres:[password]@[host].[region].railway.internal:5432/railway?sslmode=require
   ```
5. **Copy the entire connection string** (you'll need it soon)

### Connection String Breakdown
```
postgresql://postgres:SecurePassword123@containers-us-west.railway.internal:5432/railway?sslmode=require
│          │                       │                    │             │   │        │
└─ Schema  └─ User      Password  └─ Hostname        Port  Database  │    SSL Required
                                       (Region may vary)
```

---

## Step 4: Add to Vercel Environment Variables

If you're deploying to Vercel:

1. Go to your Vercel project: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Click **"Add New"**
5. **Name**: `DATABASE_URL`
6. **Value**: Paste the connection string from Railway
7. **Select Environments**: Choose "Preview", "Production", or both
8. Click **"Save"**
9. **Redeploy** your application for changes to take effect

### Example Value
```
postgresql://postgres:your_password_here@containers-us-west.railway.internal:5432/railway?sslmode=require
```

---

## Step 5: Test Connection Locally

Before running migrations, verify the connection works:

```bash
# Set the environment variable (macOS/Linux)
export DATABASE_URL="postgresql://postgres:your_password@host:5432/railway?sslmode=require"

# Or on Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:your_password@host:5432/railway?sslmode=require"

# Run the connection test
python test_database_connection.py
```

**Expected output**:
```
📝 Testing connection to: postgresql://postgres:****@containers-us-west.railway.internal:5432/railway?sslmode=require
✅ Database connected: (1,)
✅ Connection pool configured:
   - Pool size: 20
   - Max overflow: 40
   - Pre-ping enabled: True
   - Pool checkedout: 0
   - Pool size: 0

📊 Testing connection pool with concurrent requests...
✅ Successfully opened 5 concurrent connections

✅ All tests passed! Database connection is working correctly.
```

---

## Step 6: Run Alembic Migrations

Create initial migration files from your models:

```bash
cd backend

# Initialize alembic (if not already done)
# alembic init alembic

# Create migration from current models
alembic revision --autogenerate -m "Initial migration"

# Apply all migrations to Railway database
alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 1234567890ab, Initial migration
INFO  [alembic.runtime.migration] Running upgrade 1234567890ab -> 2345678901bc, Add user authentication
...
```

---

## Step 7: Verify Schema Creation

After migrations complete, verify the tables were created:

```bash
# Connect to your Railway PostgreSQL
psql postgresql://postgres:password@host:5432/railway

# Count tables
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public';

# List tables
\dt

# Exit
\q
```

**Expected result**: 28+ tables including:
- `tenants` - Multi-tenant organization
- `users` - Platform users
- `roles` - User roles
- `facilities` - Organizational facilities
- `meters` - Energy/water meters
- `carbon_calculations` - ESG calculations
- `kpi_snapshots` - KPI tracking
- `marketplace_trades` - Carbon credit marketplace
- And more...

---

## Step 8: Test API Endpoints

Start the backend server and test the connection:

```bash
cd backend

# Start the API
uvicorn app.main:app --reload

# In another terminal, test the health endpoint
curl http://localhost:8000/api/v1/health

# Test organizations endpoint (should return empty array)
curl http://localhost:8000/api/organizations
```

**Expected output**:
```json
{
  "status": "healthy",
  "service": "NetZero API",
  "version": "1.0.0",
  "timestamp": "2026-03-10T12:34:56.789012"
}
```

---

## Step 9: Connection Pool Configuration

The connection pool is automatically configured in `backend/app/config.py`:

```python
database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
database_pool_max_overflow: int = int(os.getenv("DATABASE_POOL_MAX_OVERFLOW", "40"))
database_pool_pre_ping: bool = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true"
```

**Settings explained**:
- **pool_size=20**: Maximum 20 connections in the pool
- **max_overflow=40**: Allow up to 40 additional connections if needed
- **pool_pre_ping=true**: Test each connection before using it (ensures freshness)
- **connect_timeout=10**: Wait max 10 seconds for a connection

**To adjust** (edit `.env` file or Vercel environment variables):
```bash
DATABASE_POOL_SIZE=30          # For higher concurrency
DATABASE_POOL_MAX_OVERFLOW=60  # For traffic spikes
DATABASE_POOL_PRE_PING=true    # Keep as true for production
```

---

## Step 10: Data Persistence & Monitoring

### Verify Data Persists

1. Create a test record via API
2. Restart the server
3. Verify the data is still there

### Monitor Usage in Railway

1. Open Railway.sh → Your Project → PostgreSQL
2. Go to the **"Metrics"** tab
3. Monitor:
   - Database size
   - Connection count
   - CPU usage
   - Memory usage

### Free Tier Limits

- **Storage**: 10 GB
- **Connections**: Up to 100 concurrent
- **Transfer**: Unlimited
- **Monthly Credit**: $5 (enough for development)

---

## Common Issues & Solutions

### Issue: `could not translate host name "containers-us-west.railway.internal" to address`

**Solution**:
- Make sure you're using the correct connection string from Railway dashboard
- Check if `.railway.internal` is being resolved (it only works from Railway environment or with proper VPN/network access)
- For local testing, you may need to use the public domain if Railway provides one

### Issue: `SSL certificate problem: self signed certificate`

**Solution**:
- Add `sslmode=require` to connection string (it's already there)
- Add `sslmode=disable` only for development (not recommended for production)

### Issue: `Connection pool size warning`

**Solution**:
- Reduce `DATABASE_POOL_SIZE` if getting memory warnings
- Increase if seeing "queue empty" errors

### Issue: `Alembic migrations fail`

**Solution**:
```bash
# Rollback last migration
alembic downgrade -1

# Check migration status
alembic current

# Manually check database
psql postgresql://...
\dt  # List tables
```

---

## Environment Variables Summary

Place these in:
1. **Local development**: `backend/.env`
2. **Docker Compose**: `.env` (root)
3. **Vercel**: Settings → Environment Variables
4. **GitHub Actions**: Settings → Secrets and variables

### Required Variables
```bash
DATABASE_URL=postgresql://postgres:password@host:5432/railway?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_POOL_MAX_OVERFLOW=40
DATABASE_POOL_PRE_PING=true
```

### Optional Variables
```bash
LOG_LEVEL=info
DEBUG=false
```

---

## Next Steps

1. ✅ Create Railway account and PostgreSQL instance
2. ✅ Get connection string
3. ✅ Set DATABASE_URL in Vercel
4. ✅ Test connection locally
5. ✅ Run Alembic migrations
6. ✅ Verify schema
7. ✅ Test API endpoints
8. 📋 Deploy to Vercel
9. 📋 Monitor production database
10. 📋 Set up automated backups (optional)

---

## Reference Links

- **Railway.sh Documentation**: https://docs.railway.app
- **PostgreSQL Connection Strings**: https://www.postgresql.org/docs/current/libpq-connect-using-params.html
- **Alembic Documentation**: https://alembic.sqlalchemy.org
- **SQLAlchemy Connection Pooling**: https://docs.sqlalchemy.org/en/20/core/pooling.html

---

**Last Updated**: 2026-03-10
**Status**: Ready for deployment
