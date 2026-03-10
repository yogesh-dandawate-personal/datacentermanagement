# Environment Configuration Guide

## Overview

This guide explains how to set up environment variables for local development, staging, and production deployments. Never commit `.env` files with actual secrets to Git.

## SECURITY FIRST

Important security principles:
- **NEVER** commit `.env` files containing secrets to Git
- **ALWAYS** use `.env.example` as a template
- **ALWAYS** use GitHub Secrets for CI/CD pipelines
- **ALWAYS** use Vercel Environment Variables for Vercel deployments
- **ALWAYS** regenerate secrets for each environment (dev, staging, prod)
- **NEVER** reuse development secrets in production

## File Structure

```
.
├── .env                      # LOCAL DEV ONLY (in .gitignore)
├── .env.local                # LOCAL DEV ALTERNATIVE (in .gitignore)
├── .env.staging              # STAGING TEMPLATE (in .gitignore)
├── .env.example              # Template for Vercel/Production
├── backend/.env.example      # Backend-specific template
└── docs/SETUP_ENVIRONMENT.md # This file
```

## Local Development Setup

### Option 1: Using .env.local (Docker Compose)

1. Copy the environment template:
   ```bash
   cp backend/.env.example .env.local
   ```

2. Update `.env.local` with your local values:
   ```env
   DB_USER=netzero
   DB_PASSWORD=postgres          # Simple password for local dev
   DB_NAME=netzero
   DATABASE_URL=postgresql://netzero:postgres@postgres:5432/netzero
   SECRET_KEY=local-dev-key-123456789012345678901234567890
   ```

3. Run Docker Compose:
   ```bash
   docker-compose up
   ```

Docker Compose will automatically source variables from `.env.local` in the root directory.

### Option 2: Using .env (Flask/FastAPI Direct)

1. Copy the backend template:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Update `backend/.env` with your values:
   ```env
   DATABASE_URL=postgresql://localhost:5432/netzero
   SECRET_KEY=your-local-secret-key
   DEBUG=True
   ```

3. Run the backend directly:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

### Option 3: Using .env (Manual Environment Variables)

Set environment variables directly in your shell:

```bash
export DATABASE_URL="postgresql://localhost:5432/netzero"
export SECRET_KEY="your-local-secret-key"
export DEBUG=True
export PYTHONUNBUFFERED=1

# Then run your application
cd backend
uvicorn app.main:app --reload
```

## Generating Secure Keys

### Generate a SECRET_KEY for Production

Use Python to generate a cryptographically secure random key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Output example:
```
d4YM5-Z3xK9vL2pQwRjS1tUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz
```

**Copy this value and use it in your `.env` files or GitHub Secrets.**

### Alternative: Using OpenSSL

```bash
openssl rand -base64 32
```

## Staging Deployment (Vercel)

### Step 1: Create Staging Secrets in Vercel

1. Go to Vercel Dashboard > Your Project > Settings > Environment Variables
2. Add each variable from `.env.staging`:

| Variable | Value |
|----------|-------|
| DATABASE_URL | `postgresql://staging-user:password@host:5432/netzero_staging` |
| SECRET_KEY | Generated using `secrets.token_urlsafe(32)` |
| API_KEY | Generated unique key for staging |
| DEBUG | `false` |
| ENV | `staging` |

### Step 2: Deploy to Vercel

```bash
vercel deploy --prod
```

Vercel automatically injects environment variables during the build process.

## Production Deployment (Vercel)

### Step 1: Create Production Secrets in Vercel

1. Go to Vercel Dashboard > Your Project > Settings > Environment Variables
2. Set `Environment` filter to `Production`
3. Add production values:

| Variable | Value |
|----------|-------|
| DATABASE_URL | `postgresql://prod-user:password@prod-host:5432/netzero_prod` |
| SECRET_KEY | Strong key generated via `secrets.token_urlsafe(32)` |
| API_KEY | Unique production API key |
| DEBUG | `false` |
| ENV | `production` |

**IMPORTANT**: Use different values for each environment!

### Step 2: Deploy to Production

```bash
vercel deploy --prod
```

## CI/CD Pipeline (GitHub Actions)

### Setting Up GitHub Secrets

For GitHub Actions workflows:

1. Go to GitHub Repository > Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add each secret:

```
Name: DATABASE_URL
Value: postgresql://gh-user:password@host:5432/netzero_ci

Name: SECRET_KEY
Value: [generated key]

Name: API_KEY
Value: [unique api key]
```

### Example GitHub Actions Workflow

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm install

      - name: Build with environment variables
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          API_KEY: ${{ secrets.API_KEY }}
        run: npm run build

      - name: Deploy to Vercel
        uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Docker Compose Environment Variables

### Using .env.local with Docker Compose

Create `.env.local` in the root directory:

```bash
cp backend/.env.example .env.local
```

Update with Docker-specific values:

```env
# Database (using postgres service name)
DB_USER=netzero
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
DATABASE_URL=postgresql://netzero:postgres@postgres:5432/netzero

# Security
SECRET_KEY=local-dev-secret-key
API_KEY=local-dev-api-key

# Configuration
DEBUG=False
ENV=development
LOG_LEVEL=debug
PYTHONUNBUFFERED=1
```

### Run Docker Compose

```bash
docker-compose up
```

Docker Compose automatically loads variables from `.env.local` and the `environment:` section in `docker-compose.yml`.

## Troubleshooting

### Issue: "SECRET_KEY is not set"

**Solution**: Make sure you have a `.env` or `.env.local` file with the variable:
```bash
cp backend/.env.example .env
```

### Issue: Database connection fails

**Solution**: Verify DATABASE_URL format:
```
✅ Correct: postgresql://user:password@localhost:5432/dbname
❌ Wrong:   postgres://user:password@localhost:5432/dbname  (old format)
```

### Issue: Variables not loading in Docker Compose

**Solution**: Ensure `.env.local` or `.env` is in the root directory (same level as `docker-compose.yml`):
```bash
ls -la .env*  # Should show your .env files
docker-compose config | grep -A 5 "environment:"  # Verify variables are loaded
```

### Issue: "ModuleNotFoundError" or "secrets not found"

**Solution**: Verify environment variables are exported:
```bash
echo $DATABASE_URL
echo $SECRET_KEY
# Should print your values
```

## Security Best Practices

1. **Never commit secrets**
   ```bash
   # Verify .env is in .gitignore
   git check-ignore .env
   # Output should be: .env
   ```

2. **Rotate secrets regularly**
   - Change production secrets every 90 days
   - Immediately rotate compromised secrets

3. **Use unique secrets per environment**
   - Development: simple key for testing
   - Staging: unique generated key
   - Production: strong generated key

4. **Audit secret access**
   - Monitor GitHub Secrets access logs
   - Monitor Vercel Environment Variable changes
   - Use repository activity logs

5. **Backup secrets securely**
   - Keep backup in encrypted password manager
   - Never share unencrypted in emails or chat
   - Use LastPass, 1Password, or similar for team sharing

## Reference Tables

### Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| SECRET_KEY | Yes | - | JWT signing key (min 32 chars) |
| API_KEY | No | local-dev-key | API authentication key |
| DEBUG | No | False | Flask/FastAPI debug mode |
| ENV | No | development | Environment name (dev/staging/prod) |
| LOG_LEVEL | No | info | Logging verbosity |
| ALGORITHM | No | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 30 | Token expiration |
| PYTHONUNBUFFERED | No | 1 | Disable Python buffering |

### Database Connection Strings

```
# PostgreSQL (Recommended)
postgresql://username:password@host:5432/database_name

# PostgreSQL with special characters in password
postgresql://username:pass%40word@host:5432/database_name

# Vercel Postgres
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

## Next Steps

1. Create `.env.local` or `backend/.env` for local development
2. Update placeholders with your actual values
3. Verify `.env` files are in `.gitignore`
4. Test that your application loads variables correctly
5. Set up GitHub Secrets for CI/CD
6. Configure Vercel Environment Variables for deployments
7. Document any additional environment variables specific to your setup

## Support

For issues or questions:
1. Check `docker-compose.yml` for environment variable syntax
2. Review `.env.example` for all available variables
3. Check Vercel logs for deployment errors
4. Use `docker-compose logs` for container debugging
