# Executive Copilot - Quick Start Guide

**Time to Deploy**: 10 minutes
**Difficulty**: Easy

---

## Prerequisites

1. PostgreSQL 12+ with pgvector extension
2. Python 3.9+
3. Anthropic API key (Claude)
4. OpenAI API key (embeddings)

---

## Step 1: Install Dependencies (2 min)

```bash
cd backend

# Install new packages
pip install anthropic==0.25.3 openai==1.3.7 pgvector==0.2.4 numpy==1.24.3
```

---

## Step 2: Set Up Environment Variables (2 min)

Add to your `.env` file:

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI API (for embeddings)
OPENAI_API_KEY=sk-your-key-here

# Database (ensure pgvector is installed)
DATABASE_URL=postgresql://user:password@localhost:5432/netzero
```

---

## Step 3: Enable pgvector Extension (1 min)

Connect to PostgreSQL and run:

```sql
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Verify:
```sql
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
```

---

## Step 4: Apply Database Migration (2 min)

From the backend directory:

```bash
# Apply the copilot migration
alembic upgrade 003_add_copilot_tables

# Verify tables created
psql -d netzero -c "\dt copilot_*"
```

You should see 7 tables:
- copilot_queries
- copilot_responses
- copilot_citations
- copilot_message_history
- copilot_feedback
- copilot_access_logs
- copilot_rate_limits

---

## Step 5: Start the API Server (1 min)

```bash
# From backend directory
uvicorn app.main:app --reload

# Server running at http://localhost:8000
# API Docs at http://localhost:8000/api/docs
```

---

## Step 6: Test the Copilot (2 min)

### Option A: Using cURL

```bash
# Get your JWT token first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'

# Save the token from response

# Ask a question
curl -X POST http://localhost:8000/api/v1/tenants/YOUR_TENANT_ID/copilot/ask \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our total carbon emissions this month?"
  }'
```

### Option B: Using API Documentation

1. Open http://localhost:8000/api/docs
2. Click "Authorize" button
3. Enter your JWT token
4. Find endpoint: `POST /api/v1/tenants/{tenant_id}/copilot/ask`
5. Click "Try it out"
6. Enter your tenant_id and question
7. Execute

### Option C: Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
TENANT_ID = "your-tenant-id"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{BASE_URL}/tenants/{TENANT_ID}/copilot/ask",
    headers=headers,
    json={"question": "What are our emissions trends?"}
)

print(json.dumps(response.json(), indent=2))
```

---

## Expected Response

```json
{
  "query_id": "uuid",
  "response_id": "uuid",
  "answer": "Based on your submitted data...",
  "citations": [
    {
      "id": "uuid",
      "type": "calculation",
      "name": "February 2026 Carbon Calculation",
      "data": { ... },
      "verified": true
    }
  ],
  "confidence": 0.95,
  "data_quality": "good",
  "tokens_used": 450,
  "has_issues": false,
  "created_at": "2026-03-10T15:30:00Z"
}
```

---

## Common Issues & Solutions

### "pgvector extension not found"

```bash
# In PostgreSQL
CREATE EXTENSION vector;

# Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### "ANTHROPIC_API_KEY not set"

```bash
# Set in environment
export ANTHROPIC_API_KEY=sk-ant-...

# Or verify .env file has it
cat .env | grep ANTHROPIC_API_KEY
```

### "Rate limit exceeded"

Wait 1 hour for the rate limit window to reset. Default limits:
- 100 queries per hour
- 100,000 tokens per hour

### "Low confidence in response"

The copilot rejected the response because available data is insufficient. Ensure:
- Relevant metrics are entered in system
- Carbon calculations are submitted and approved
- Data is recent (within last 30 days)

### "Unauthorized"

Verify:
- JWT token is valid
- Token hasn't expired
- User belongs to the tenant
- Token includes correct tenant_id

---

## Next Steps

### View API Documentation

Open http://localhost:8000/api/docs for:
- All 6 copilot endpoints
- Request/response examples
- Parameter descriptions
- Error codes

### Run Tests

```bash
# Run all copilot tests
pytest tests/test_copilot_service.py -v
pytest tests/test_copilot_integration.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Explore Endpoints

1. **POST /tenants/{id}/copilot/ask** - Ask a question
2. **GET /tenants/{id}/copilot/history** - View query history
3. **GET /tenants/{id}/copilot/responses/{id}** - View full response
4. **POST /tenants/{id}/copilot/feedback** - Submit feedback
5. **GET /tenants/{id}/copilot/similar-questions** - Find similar questions
6. **GET /tenants/{id}/copilot/stats** - View usage statistics

---

## Full Documentation

For detailed information, see:
- Architecture: `/backend/docs/COPILOT_IMPLEMENTATION.md`
- API Reference: `/backend/docs/COPILOT_IMPLEMENTATION.md#api-endpoints`
- Database Schema: `/backend/docs/COPILOT_IMPLEMENTATION.md#database-schema`
- Deployment: `/backend/docs/COPILOT_IMPLEMENTATION.md#deployment`

---

## Key Features to Try

### 1. Ask Natural Language Questions

```
"What's our Scope 2 emissions this quarter?"
"Compare our PUE with the industry average"
"Show me our carbon reduction progress"
"What are the top energy-consuming facilities?"
```

### 2. View Response Details

```bash
curl http://localhost:8000/api/v1/tenants/{id}/copilot/responses/{response_id} \
  -H "Authorization: Bearer $TOKEN"
```

Get full response with all citations and source data.

### 3. Check Query History

```bash
curl http://localhost:8000/api/v1/tenants/{id}/copilot/history \
  -H "Authorization: Bearer $TOKEN"
```

View all previous questions with pagination.

### 4. Submit Feedback

```bash
curl -X POST http://localhost:8000/api/v1/tenants/{id}/copilot/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "uuid",
    "response_id": "uuid",
    "rating": 4,
    "comment": "Helpful but missing recent data"
  }'
```

Provide feedback to improve response quality.

---

## Performance Tips

1. **Cache Identical Questions**: Same question within 60 minutes returns cached response
2. **Batch Questions**: Ask multiple related questions in one session
3. **Monitor Token Usage**: Track tokens_used in response for cost optimization
4. **Use Organization Filter**: Filter context to specific organization when relevant

---

## Monitoring & Logging

The system logs all activities:

```bash
# View recent queries
psql -d netzero -c "SELECT * FROM copilot_queries ORDER BY created_at DESC LIMIT 10"

# View responses
psql -d netzero -c "SELECT * FROM copilot_responses ORDER BY created_at DESC LIMIT 10"

# Check access logs (audit trail)
psql -d netzero -c "SELECT * FROM copilot_access_logs ORDER BY created_at DESC LIMIT 20"

# View rate limit status
psql -d netzero -c "SELECT * FROM copilot_rate_limits WHERE is_exceeded = true"
```

---

## Cost Optimization

Claude 3.5 Sonnet pricing:
- Input: $0.003 per 1,000 tokens
- Output: $0.015 per 1,000 tokens
- Average query: 500 tokens total
- **Average cost per query: ~$0.01**

Ways to reduce costs:
1. Use response caching (60 min TTL)
2. Ask specific questions (fewer tokens)
3. Batch similar questions
4. Set lower MAX_CONTEXT_ITEMS if cost is concern

---

## Security Checklist

Before production deployment:

- [ ] Rotate API keys
- [ ] Set up rate limiting per tenant (if needed)
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly (not allowing *)
- [ ] Set up audit log archival
- [ ] Configure backup strategy
- [ ] Set up monitoring/alerting
- [ ] Test access control thoroughly
- [ ] Document security procedures

---

## Support & Troubleshooting

### Enable Debug Logging

```python
# In app/main.py, set log level
logging.basicConfig(level=logging.DEBUG)
```

### Check Database Connection

```bash
# Test database connection
psql -d netzero -c "SELECT COUNT(*) FROM tenants"

# Verify pgvector extension
psql -d netzero -c "SELECT COUNT(*) FROM information_schema.sequences"
```

### Monitor API Logs

```bash
# Follow FastAPI logs
tail -f uvicorn.log | grep copilot
```

---

**You're all set!** The Executive Copilot is now ready to use.

For questions, refer to the full implementation guide at:
`/backend/docs/COPILOT_IMPLEMENTATION.md`
