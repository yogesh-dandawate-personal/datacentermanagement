# Quick Start: Secrets & Environment Variables

## Local Development (Docker Compose)

### 1. Create your local environment file
```bash
cp .env.local .env
```

### 2. Generate a secure SECRET_KEY (optional for dev, required for prod)
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Update .env with your values
```bash
# Edit .env and update:
SECRET_KEY=<paste_generated_key_here>
DATABASE_URL=postgresql://netzero:postgres@postgres:5432/netzero
```

### 4. Start everything
```bash
docker-compose up
```

### 5. Verify it's working
```bash
curl http://localhost:8000/docs
```

---

## For Staging/Production

### 1. In Vercel Dashboard
Settings → Environment Variables → Add each variable:
- DATABASE_URL (your production database)
- SECRET_KEY (generate new key)
- API_KEY (unique key)
- DEBUG=false
- ENV=production/staging

### 2. Deploy
```bash
vercel deploy --prod
```

---

## For CI/CD (GitHub Actions)

### 1. In GitHub Repository
Settings → Secrets and variables → Actions → New secret:
- DATABASE_URL_CI
- SECRET_KEY_CI
- API_KEY_CI

### 2. Use in workflows
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL_CI }}
  SECRET_KEY: ${{ secrets.SECRET_KEY_CI }}
```

---

## Important Security Rules

⚠️ **NEVER**:
- Commit .env files to git
- Share secrets in email/chat
- Use dev secrets in production
- Reuse secrets across environments

✅ **ALWAYS**:
- Use .env.example as template
- Copy template to .env (git ignored)
- Update placeholders with real values
- Generate new key for each environment
- Use GitHub Secrets for CI/CD
- Use Vercel variables for deployments

---

## Reference

| File | Purpose | In Git? | Notes |
|------|---------|---------|-------|
| .env.example | Template | ✅ | Copy and update to create .env |
| backend/.env.example | Template | ✅ | Backend-specific variables |
| .env.local | Local dev | ❌ | .gitignored, safe defaults |
| .env | Alternative | ❌ | .gitignored, your values |
| .env.staging | Staging template | ❌ | .gitignored for safety |

---

## Troubleshooting

### "SECRET_KEY is not set"
```bash
# Update your .env file:
SECRET_KEY=your_generated_key_here
```

### Docker won't start
```bash
# Verify .env exists in root directory:
ls -la .env

# Check values are loaded:
docker-compose config | grep SECRET_KEY
```

### Can't connect to database
```bash
# Check DATABASE_URL format:
# postgresql://user:password@host:port/dbname

# Test connection:
docker-compose exec backend psql $DATABASE_URL
```

---

## Full Documentation

See `/docs/SETUP_ENVIRONMENT.md` for complete setup instructions covering:
- 3 ways to set up local development
- Secure key generation
- Staging deployment
- Production deployment
- GitHub Actions setup
- Docker Compose details
- Security best practices
