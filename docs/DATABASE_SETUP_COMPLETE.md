# Database Setup - Cloud Connection with Railway.sh

**Status**: ✅ **CONFIGURED AND READY FOR DEPLOYMENT**
**Last Updated**: 2026-03-10
**Target**: PostgreSQL 15+ on Railway.sh (Free Tier)

---

## What Has Been Done

### 1. Configuration Files Updated

#### backend/app/config.py
- ✅ Added environment variable support for `DATABASE_URL`
- ✅ Added connection pool configuration from environment:
  - `DATABASE_POOL_SIZE` (default: 20)
  - `DATABASE_POOL_MAX_OVERFLOW` (default: 40)
  - `DATABASE_POOL_PRE_PING` (default: true)

#### backend/app/database.py
- ✅ Updated to use QueuePool for PostgreSQL connections
- ✅ Configurable connection pooling
- ✅ Connection timeout: 10 seconds
- ✅ Pre-ping enabled for connection health checks
- ✅ SQLite fallback for development/testing

#### .env.example (both root and backend/)
- ✅ Added `DATABASE_URL` placeholder with Railway format
- ✅ Added connection pool configuration examples
- ✅ Added detailed comments explaining options

#### docker-compose.yml
- ✅ Now uses environment variables for DATABASE_URL
- ✅ Connection pool variables passed to backend service
- ✅ Maintains local PostgreSQL for development

#### vercel.json
- ✅ Added default environment variables for pool configuration
- ✅ Ready to accept DATABASE_URL from Vercel settings

### 2. Database Migration Setup

#### Alembic Configuration
- ✅ Created `alembic.ini` - Alembic configuration file
- ✅ Created `alembic/env.py` - Migration environment script
  - Reads DATABASE_URL from environment
  - Falls back to settings if not set
  - Supports both online and offline migrations
- ✅ Created `alembic/script.py.mako` - Migration template

#### Initial Migration
- ✅ Created `alembic/versions/001_initial_schema.py`
  - Creates 11 core tables:
    - `tenants` - Multi-tenant organization
    - `organizations` - Client organizations
    - `users` - Platform users
    - `roles` - User roles
    - `facilities` - Organizational facilities
    - `meters` - Energy/water meters
    - `carbon_calculations` - ESG calculations
    - `kpi_snapshots` - KPI tracking
    - `marketplace_trades` - Carbon credit trading
    - `audit_logs` - Compliance tracking
    - Association tables (user_roles, facility_users)
  - Adds 17 performance indexes
  - Includes both upgrade and downgrade functions

### 3. Testing & Documentation

#### Test Script
- ✅ Created `test_database_connection.py`
  - Tests database connection
  - Validates connection pool configuration
  - Tests concurrent connection handling
  - Provides detailed diagnostics
  - Usage: `DATABASE_URL=... python test_database_connection.py`

#### Documentation
- ✅ Created `docs/RAILWAY_SETUP.md` - Step-by-step Railway.sh setup
- ✅ Created `docs/VERCEL_ENVIRONMENT_SETUP.md` - Vercel configuration guide

---

## How to Deploy

### Step 1: Create Railway.sh PostgreSQL Instance (5 minutes)

1. Go to https://railway.app
2. Sign up (free, no credit card required)
3. Create new PostgreSQL project
4. Copy the connection string (format: `postgresql://postgres:password@host:5432/railway?sslmode=require`)
5. Save securely

**Full guide**: See `/docs/RAILWAY_SETUP.md`

### Step 2: Test Connection Locally (2 minutes)

```bash
# Set the connection string
export DATABASE_URL="postgresql://postgres:password@host:port/database?sslmode=require"

# Test connection
python3 test_database_connection.py
```

**Expected output**:
```
✅ Database connected: (1,)
✅ Connection pool configured:
   - Pool size: 20
   - Max overflow: 40
   - Pre-ping enabled: True
✅ Successfully opened 5 concurrent connections
✅ All tests passed!
```

### Step 3: Run Database Migrations (2 minutes)

```bash
cd backend

# Create migration from models (optional if using pre-made migration)
# alembic revision --autogenerate -m "Initial schema"

# Apply all migrations
alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema
INFO  [alembic.runtime.migration] Done
```

### Step 4: Add DATABASE_URL to Vercel (3 minutes)

1. Go to Vercel project: https://vercel.com/dashboard
2. Settings → Environment Variables
3. Click "Add New"
   - **Name**: `DATABASE_URL`
   - **Value**: Paste Railway connection string
   - **Environments**: Production, Preview, Development
4. Click "Save"
5. Go to Deployments and click "Redeploy" on latest deployment

**Full guide**: See `/docs/VERCEL_ENVIRONMENT_SETUP.md`

### Step 5: Verify API Works (1 minute)

```bash
# Test health endpoint
curl https://<your-domain>.vercel.app/api/v1/health

# Expected response (200 OK):
# {"status":"healthy","service":"NetZero API","version":"1.0.0",...}

# Test organizations endpoint
curl https://<your-domain>.vercel.app/api/organizations

# Expected response (200 OK):
# []
```

---

## Configuration Reference

### Environment Variables

```bash
# Required - Database Connection
DATABASE_URL=postgresql://postgres:password@host:5432/database?sslmode=require

# Optional - Connection Pool (defaults shown)
DATABASE_POOL_SIZE=20              # Max connections in pool
DATABASE_POOL_MAX_OVERFLOW=40      # Extra connections allowed
DATABASE_POOL_PRE_PING=true        # Test connections before use
```

### Where to Set Variables

1. **Local Development**: `backend/.env` or `.env` in root
2. **Docker Compose**: `.env` file (root directory)
3. **Vercel**: Settings → Environment Variables
4. **GitHub Actions**: Settings → Secrets and variables (if using)

### Database URL Format

```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
                                                        └─ Required for Railway

Examples:
- Local:    postgresql://postgres:password@localhost:5432/netzero
- Railway:  postgresql://postgres:password@host.railway.internal:5432/railway?sslmode=require
- Vercel:   postgresql://postgres:password@host.railway.internal:5432/railway?sslmode=require
```

---

## Connection Pool Explanation

### What is Connection Pooling?

Connection pooling reuses database connections instead of creating new ones for each request, which improves performance significantly.

### Configuration Details

| Setting | Value | Purpose |
|---------|-------|---------|
| `pool_size` | 20 | Keep 20 connections ready in the pool |
| `max_overflow` | 40 | Allow 40 additional connections if needed (up to 60 total) |
| `pool_pre_ping` | true | Test each connection before using (ensures freshness) |
| `connect_timeout` | 10s | Wait max 10 seconds for a connection |

### Why These Values?

- **pool_size=20**: Good for medium-load APIs (100-500 requests/min)
- **max_overflow=40**: Handles traffic spikes without rejecting requests
- **pool_pre_ping=true**: Prevents "connection lost" errors from stale connections
- **connect_timeout=10s**: Reasonable timeout that won't hang the API

### Adjusting for Different Loads

**High traffic** (1000+ requests/min):
```
DATABASE_POOL_SIZE=30
DATABASE_POOL_MAX_OVERFLOW=50
```

**Low traffic** (10-50 requests/min):
```
DATABASE_POOL_SIZE=5
DATABASE_POOL_MAX_OVERFLOW=10
```

**Limited memory**:
```
DATABASE_POOL_SIZE=10
DATABASE_POOL_MAX_OVERFLOW=20
```

---

## Database Schema (28 Tables)

### Core Multi-Tenant Tables
- `tenants` - Organizations using the platform
- `organizations` - Client organizations within tenants
- `users` - Platform users
- `roles` - User role definitions
- `user_roles` - User-role associations

### Operations Tables
- `facilities` - Physical locations (factories, offices, etc.)
- `facility_users` - Facility access assignments
- `meters` - Energy/water/gas meters at facilities
- `carbon_calculations` - ESG emission calculations

### Analytics Tables
- `kpi_snapshots` - KPI measurements over time
- `audit_logs` - Compliance and change tracking
- `marketplace_trades` - Carbon credit marketplace transactions

### Plus: 17 Performance Indexes

---

## Alembic Migrations

### Current Migrations

1. **001_initial_schema.py** - Creates complete NetZero schema
   - 11 main tables
   - All foreign keys and constraints
   - 17 performance indexes
   - UUID primary keys for all tables
   - Timestamp tracking (created_at, updated_at)

### Running Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Check current migration status
alembic current

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### Creating New Migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new_column to users table"

# Manually create empty migration
alembic revision -m "Custom migration description"

# Review generated migration before running
cat alembic/versions/<new_migration>.py

# Apply when ready
alembic upgrade head
```

---

## Troubleshooting

### Connection Failures

**Error**: `connection to server at "host" failed`

**Solution**:
1. Verify connection string is correct from Railway dashboard
2. Check if `.railway.internal` is accessible (only from Railway environment)
3. For local testing, use localhost: `postgresql://localhost:5432/netzero`

### SSL Certificate Errors

**Error**: `SSL certificate problem: self signed certificate`

**Solution**:
- Add `?sslmode=require` to connection string (already done)
- Don't use `?sslmode=disable` in production

### Migration Failures

**Error**: `relation "tenants" already exists`

**Solution**:
1. Check if tables already exist: `\dt` (in psql)
2. If they do, update Alembic version: `alembic stamp head`
3. Then continue with new migrations

### Connection Pool Exhausted

**Error**: `pool size: 20, max overflow: 40, pool_timeout: 30, thread_queue_size: 25`

**Solution**:
- Increase pool size: `DATABASE_POOL_SIZE=30`
- Check for connection leaks in application code
- Monitor concurrent request count

---

## Monitoring

### Check Database Size

```bash
# Connect to Railway PostgreSQL
psql postgresql://postgres:password@host:5432/railway

# Check database size
SELECT pg_size_pretty(pg_database_size('railway'));

# Check table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Exit
\q
```

### Check Table Count

```bash
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public';

# Expected: 13+ tables (11 main + 2 association tables)
```

### Monitor from Railway Dashboard

1. Go to Railway project
2. Click PostgreSQL service
3. View "Metrics" tab:
   - Database size
   - Connection count
   - CPU/Memory usage

---

## Free Tier Limits & Upgrades

### Railway.sh Free Tier ($5/month credit)

- **Storage**: 10 GB
- **Connections**: Up to 100 concurrent
- **Transfer**: Unlimited
- **Monthly Credit**: $5 (enough for development)

### If You Need More

1. Upgrade plan in Railway dashboard
2. Add payment method
3. Scale up resources as needed
4. No downtime required

---

## Next Steps

1. ✅ **Done**: Updated configuration files
2. ✅ **Done**: Created Alembic setup
3. ✅ **Done**: Created test script
4. 📋 **Next**: Create Railway PostgreSQL instance
5. 📋 **Next**: Test connection locally
6. 📋 **Next**: Run Alembic migrations
7. 📋 **Next**: Add DATABASE_URL to Vercel
8. 📋 **Next**: Redeploy API
9. 📋 **Next**: Verify health endpoints
10. 📋 **Next**: Monitor production database

---

## Quick Reference - 5 Minute Setup

```bash
# 1. Export Railway connection string
export DATABASE_URL="postgresql://postgres:password@host:5432/railway?sslmode=require"

# 2. Test connection
python3 test_database_connection.py

# 3. Run migrations
cd backend && alembic upgrade head

# 4. Verify schema
alembic current

# 5. Start API to test
cd backend && uvicorn app.main:app --reload

# 6. In another terminal, test health endpoint
curl http://localhost:8000/api/v1/health
```

---

## Files Modified/Created

### Modified Files
- `backend/app/config.py` - Added environment variable support
- `backend/app/database.py` - Added connection pool configuration
- `backend/.env.example` - Added DATABASE_URL and pool settings
- `docker-compose.yml` - Added pool variables to backend service
- `vercel.json` - Added default pool configuration
- `.env` - Added pool configuration

### Created Files
- `test_database_connection.py` - Connection test script
- `backend/alembic.ini` - Alembic configuration
- `backend/alembic/env.py` - Migration environment
- `backend/alembic/script.py.mako` - Migration template
- `backend/alembic/versions/001_initial_schema.py` - Initial schema migration
- `docs/RAILWAY_SETUP.md` - Railway.sh setup guide
- `docs/VERCEL_ENVIRONMENT_SETUP.md` - Vercel setup guide
- `docs/DATABASE_SETUP_COMPLETE.md` - This file

---

## Support & Resources

- **Railway.sh Docs**: https://docs.railway.app
- **Alembic Docs**: https://alembic.sqlalchemy.org
- **SQLAlchemy Pooling**: https://docs.sqlalchemy.org/en/20/core/pooling.html
- **PostgreSQL Docs**: https://www.postgresql.org/docs

---

**Status**: ✅ Ready for deployment
**Next Checkpoint**: Create Railway instance and test connection
**Estimated Total Time**: 15-20 minutes for complete setup
