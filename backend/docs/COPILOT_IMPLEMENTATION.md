# Executive Copilot Q&A Module - Implementation Guide

**Sprint**: Sprint 13 - Critical Gap
**Status**: Complete
**Version**: 1.0.0
**Last Updated**: 2026-03-10

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [API Endpoints](#api-endpoints)
5. [Database Schema](#database-schema)
6. [Configuration](#configuration)
7. [Guardrails & Safety](#guardrails--safety)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Executive Copilot Q&A Module is a Retrieval-Augmented Generation (RAG) system that allows executives to ask natural language questions about ESG data, carbon emissions, sustainability metrics, and KPIs. The system:

- **Retrieves relevant data** from databases using semantic search (vector embeddings)
- **Generates intelligent responses** using Claude AI with strict guardrails
- **Tracks citations** to ensure every fact is sourced and verifiable
- **Prevents hallucination/fabrication** with multiple safety layers
- **Maintains conversation history** for context awareness
- **Enforces access control** with tenant isolation and rate limiting
- **Logs all interactions** for audit and compliance

### Key Features

- ✅ Semantic search using pgvector embeddings
- ✅ Citation tracking with verification
- ✅ Fabrication detection and prevention
- ✅ Confidence scoring for responses
- ✅ Rate limiting per user/tenant
- ✅ Conversation history and context
- ✅ Response caching for identical questions
- ✅ User feedback collection
- ✅ Comprehensive audit logging
- ✅ Multi-language support

---

## Architecture

### High-Level Flow

```
User Question
    ↓
[Validation & Access Control]
    ↓
[Cache Check] → (Return cached if found)
    ↓
[Generate Embedding]
    ↓
[Vector Search] → Retrieve context (metrics, calculations, reports, facilities)
    ↓
[Build Context] → Format data for Claude
    ↓
[Claude API] → Generate response with system prompt (guardrails)
    ↓
[Validate Response] → Check for fabrication, calculate confidence
    ↓
[Extract Citations] → Link response to source data
    ↓
[Store Response & Citations]
    ↓
[Return to User] with citations and confidence score
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Routes                          │
│   (app/routes/copilot.py)                                   │
│  - ask_copilot()                                            │
│  - get_response_history()                                   │
│  - get_response_details()                                   │
│  - submit_feedback()                                        │
│  - get_similar_questions()                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              CopilotService                                  │
│   (app/services/copilot_service.py)                         │
│  - ask_question()                                           │
│  - validate_access()                                        │
│  - check_rate_limit()                                       │
│  - get_cached_response()                                    │
│  - submit_feedback()                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────────┐
        │                     │                  │
┌───────▼────────────┐  ┌─────▼──────┐  ┌──────▼─────────────┐
│ VectorStore        │  │ ClaudeAPI  │  │ Access Control     │
│ (pgvector)         │  │ Integration│  │ & Rate Limiting    │
│                    │  │            │  │                    │
│ - generate_        │  │ - get_     │  │ - validate_access()│
│   embedding()      │  │   system_  │  │ - check_rate_limit()
│ - semantic_search_ │  │   prompt() │  │ - log_access()     │
│   metrics()        │  │ - generate_│  │ - update_rate_     │
│ - semantic_search_ │  │   response()   │   limit()          │
│   calculations()   │  │ - validate_│  │                    │
│ - build_retrieval_ │  │   no_      │  │ Database Models:   │
│   context()        │  │   fabrication()│ - Tenant          │
│ - get_similar_     │  │ - extract_ │  │ - User            │
│   questions()      │  │   citations()  │ - Organization    │
│                    │  │ - calculate    │ - CopilotQuery    │
│                    │  │   confidence() │ - CopilotResponse │
│                    │  │                │ - CopilotCitation │
└────────────────────┘  └────────────────┘ └───────────────────┘
        │                     │                  │
        └──────────────────┬──────────────────┬──┘
                           │
                    ┌──────▼──────────┐
                    │  Database       │
                    │  (PostgreSQL)   │
                    │                 │
                    │ - copilot_      │
                    │   queries       │
                    │ - copilot_      │
                    │   responses     │
                    │ - copilot_      │
                    │   citations     │
                    │ - copilot_      │
                    │   message_      │
                    │   history       │
                    │ - copilot_      │
                    │   feedback      │
                    │ - copilot_      │
                    │   access_logs   │
                    │ - copilot_      │
                    │   rate_limits   │
                    │                 │
                    │ Related tables: │
                    │ - kpi_          │
                    │   definitions   │
                    │ - kpi_snapshots │
                    │ - carbon_       │
                    │   calculations  │
                    │ - reports       │
                    │ - facilities    │
                    └─────────────────┘
```

---

## Components

### 1. Database Models (`app/models/copilot.py`)

#### CopilotQuery
Stores user questions with embedding vectors for semantic search.

```python
class CopilotQuery(Base):
    __tablename__ = 'copilot_queries'

    id: UUID                          # Unique query ID
    tenant_id: UUID                   # Multi-tenant isolation
    user_id: UUID                     # Who asked
    question: Text                    # The question text
    embedding: Vector(1536)           # Embedding for semantic search
    query_type: str                   # Classification: metric, calculation, etc.
    status: str                       # processed, failed, etc.
    created_at: DateTime
```

#### CopilotResponse
Stores AI-generated responses with quality metrics.

```python
class CopilotResponse(Base):
    __tablename__ = 'copilot_responses'

    id: UUID
    query_id: UUID                    # Links to query
    answer: Text                      # Full AI response
    confidence: Decimal(0-1)          # 0-1, confidence in answer
    model_used: str                   # claude-3-5-sonnet-20241022
    tokens_used: int                  # For cost tracking
    input_tokens: int
    output_tokens: int
    has_fabrication: bool             # Safety flag
    data_quality: str                 # excellent, good, fair, poor
    processing_time_ms: int
    status: str                       # completed, failed
    created_at: DateTime
```

#### CopilotCitation
Links response facts to source data with verification.

```python
class CopilotCitation(Base):
    __tablename__ = 'copilot_citations'

    id: UUID
    response_id: UUID                 # Which response
    entity_type: str                  # metric, calculation, report, facility
    entity_id: UUID                   # Reference to source entity
    entity_name: str                  # Name for display
    entity_data: JSON                 # Snapshot of data at time of citation
    is_verified: bool                 # True if from our system
    confidence: Decimal(0-1)          # 0-1, confidence in citation
    source_url: str                   # Link to navigate to source
    api_endpoint: str                 # Programmatic access
    created_at: DateTime
```

#### CopilotMessageHistory
Tracks conversation flow and context.

```python
class CopilotMessageHistory(Base):
    __tablename__ = 'copilot_message_history'

    id: UUID
    query_id: UUID
    role: str                         # user, assistant, system
    content: Text                     # Message content
    sequence_number: int              # Order in conversation
    context_summary: JSON             # Context used
    created_at: DateTime
```

#### CopilotFeedback
Collects user feedback for quality improvement.

```python
class CopilotFeedback(Base):
    __tablename__ = 'copilot_feedback'

    id: UUID
    query_id: UUID
    response_id: UUID
    rating: int                       # 1-5 stars
    accuracy: str                     # accurate, partially, inaccurate
    comment: Text
    issues: Array(str)                # [missing_data, fabrication, etc]
    has_fabrication: bool
    has_missing_data: bool
    status: str                       # received, under_review, action_taken
```

#### CopilotAccessLog
Audit trail for compliance.

```python
class CopilotAccessLog(Base):
    __tablename__ = 'copilot_access_logs'

    id: UUID
    tenant_id: UUID
    user_id: UUID
    query_id: UUID
    action: str                       # ask_question, view_response, feedback
    ip_address: str
    user_agent: str
    details: JSON
    created_at: DateTime
```

#### CopilotRateLimit
Enforces rate limiting.

```python
class CopilotRateLimit(Base):
    __tablename__ = 'copilot_rate_limits'

    id: UUID
    tenant_id: UUID
    user_id: UUID
    window_type: str                  # hourly, daily
    window_start: DateTime
    query_count: int
    total_tokens: int
    query_limit: int = 100
    token_limit: int = 100000
    is_exceeded: bool
```

### 2. Vector Store (`app/integrations/vector_store.py`)

Handles semantic search using pgvector embeddings.

**Key Methods:**

```python
async def generate_embedding(text: str) -> List[float]
    """Generate embedding vector using OpenAI/Claude"""

async def semantic_search_metrics(query_text, limit=5) -> List[Dict]
    """Find relevant KPI metrics by semantic similarity"""

async def semantic_search_calculations(query_text, limit=5) -> List[Dict]
    """Find relevant carbon calculations"""

async def semantic_search_reports(query_text, limit=5) -> List[Dict]
    """Find relevant ESG reports"""

async def build_retrieval_context(query_text) -> Dict
    """Build comprehensive context for RAG"""

async def get_similar_questions(query_text) -> List[Dict]
    """Find similar questions from history"""
```

### 3. Claude API Integration (`app/integrations/claude_client.py`)

Manages interaction with Anthropic Claude API.

**Key Methods:**

```python
def get_system_prompt() -> str
    """System prompt with guardrails and ESG domain knowledge"""

def create_user_message(question, context) -> Tuple[List[Dict], str]
    """Create user message with context"""

async def generate_response(messages) -> Tuple[str, Dict]
    """Generate response using Claude API"""

def extract_citations_from_answer(answer, context) -> List[Dict]
    """Extract and link citations in answer"""

def validate_no_fabrication(answer, context) -> Tuple[bool, List[str]]
    """Detect potential hallucination/fabrication"""

def calculate_confidence_score(answer, context, usage) -> float
    """Calculate 0-1 confidence score"""
```

### 4. Copilot Service (`app/services/copilot_service.py`)

Main orchestration service implementing RAG workflow.

**Key Methods:**

```python
async def ask_question(tenant_id, user_id, question) -> Dict
    """Main Q&A workflow - query to response"""

async def _validate_access(tenant_id, user_id) -> Dict
    """Enforce access control and tenant isolation"""

async def _check_rate_limit(tenant_id, user_id) -> Dict
    """Check if user exceeded rate limits"""

async def _get_cached_response(tenant_id, user_id, question) -> Optional[Dict]
    """Check cache for identical questions"""

async def get_response_history(tenant_id, user_id) -> Dict
    """Get user's query history"""

async def submit_feedback(tenant_id, user_id, query_id, response_id, ...) -> Dict
    """Store user feedback"""
```

### 5. API Routes (`app/routes/copilot.py`)

FastAPI endpoints for copilot functionality.

---

## API Endpoints

### 1. Ask Question

**POST** `/api/v1/tenants/{tenant_id}/copilot/ask`

Ask the copilot a question about ESG data.

**Request:**
```json
{
  "question": "What is our Scope 2 emissions this month?",
  "organization_id": "optional-org-uuid"
}
```

**Response (200):**
```json
{
  "query_id": "uuid",
  "response_id": "uuid",
  "answer": "Based on your submitted data, Scope 2 emissions for February 2026 are 45,000 kg CO2e...",
  "citations": [
    {
      "id": "uuid",
      "type": "calculation",
      "name": "February 2026 Carbon Calculation",
      "data": {
        "period_start": "2026-02-01",
        "period_end": "2026-02-28",
        "total_emissions": 45000,
        "status": "approved"
      },
      "verified": true
    }
  ],
  "confidence": 0.95,
  "data_quality": "good",
  "tokens_used": 450,
  "has_issues": false,
  "issues": [],
  "created_at": "2026-03-10T15:30:00Z"
}
```

**Errors:**
- `400`: Invalid question
- `401`: Unauthorized
- `403`: Access denied to tenant
- `429`: Rate limit exceeded
- `500`: Internal error

---

### 2. Get Query History

**GET** `/api/v1/tenants/{tenant_id}/copilot/history`

Get user's question history with pagination.

**Query Parameters:**
- `limit`: Max results (1-100, default 20)
- `offset`: Pagination offset (default 0)

**Response:**
```json
{
  "history": [
    {
      "query_id": "uuid",
      "question": "What is our Scope 2 emissions this month?",
      "created_at": "2026-03-10T15:30:00Z",
      "response_count": 1,
      "status": "processed",
      "latest_response": {
        "id": "uuid",
        "confidence": 0.95,
        "created_at": "2026-03-10T15:30:00Z"
      }
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

### 3. Get Response Details

**GET** `/api/v1/tenants/{tenant_id}/copilot/responses/{response_id}`

Get full response with all citations and source data.

**Response:**
```json
{
  "response_id": "uuid",
  "query_id": "uuid",
  "question": "What is our Scope 2 emissions this month?",
  "answer": "Based on your submitted data...",
  "model_used": "claude-3-5-sonnet-20241022",
  "confidence": 0.95,
  "data_quality": "good",
  "tokens_used": 450,
  "processing_time_ms": 2500,
  "has_fabrication": false,
  "citations": [
    {
      "id": "uuid",
      "type": "calculation",
      "name": "February 2026 Carbon Calculation",
      "verified": true,
      "confidence": 1.0,
      "entity_data": { ... },
      "source_url": "/api/v1/carbon/calculations/uuid",
      "citation_type": "data_source"
    }
  ],
  "created_at": "2026-03-10T15:30:00Z"
}
```

---

### 4. Submit Feedback

**POST** `/api/v1/tenants/{tenant_id}/copilot/feedback`

Submit feedback on response quality.

**Request:**
```json
{
  "query_id": "uuid",
  "response_id": "uuid",
  "rating": 4,
  "comment": "Helpful but missing recent data",
  "issues": ["missing_data", "outdated"]
}
```

**Response:**
```json
{
  "feedback_id": "uuid",
  "status": "recorded",
  "created_at": "2026-03-10T15:35:00Z"
}
```

---

### 5. Find Similar Questions

**GET** `/api/v1/tenants/{tenant_id}/copilot/similar-questions`

Find similar questions from history.

**Query Parameters:**
- `q`: Question to find similar to (required)
- `limit`: Max results (1-20, default 5)

**Response:**
```json
[
  {
    "question": "What are our emissions this quarter?",
    "created_at": "2026-03-05T10:00:00Z",
    "response_count": 2,
    "similarity": 0.92
  }
]
```

---

### 6. Get Copilot Stats

**GET** `/api/v1/tenants/{tenant_id}/copilot/stats`

Get usage statistics.

**Response:**
```json
{
  "total_queries": 42,
  "total_responses": 42,
  "avg_confidence": 0.85,
  "queries_with_issues": 3,
  "feedback_count": 5
}
```

---

## Database Schema

### Migration: 003_add_copilot_tables.py

Creates all copilot-related tables with proper indexing.

**Tables Created:**
1. `copilot_queries` - User questions
2. `copilot_responses` - AI-generated responses
3. `copilot_citations` - Source citations
4. `copilot_message_history` - Conversation history
5. `copilot_feedback` - User feedback
6. `copilot_access_logs` - Audit trail
7. `copilot_rate_limits` - Rate limiting

**Key Indexes:**
- `ix_copilot_queries_tenant_created` - For listing user queries
- `ix_copilot_responses_tenant_created` - For finding responses
- `ix_copilot_citations_entity` - For citation lookups
- `ix_copilot_feedback_status` - For feedback review queue

**pgvector Setup:**
```sql
CREATE EXTENSION IF NOT EXISTS "vector";
```

The embedding column uses `Vector(1536)` for 1536-dimensional embeddings from OpenAI/Claude.

---

## Configuration

### Environment Variables

```bash
# Claude/Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI API (for embeddings)
OPENAI_API_KEY=sk-...

# Database (includes pgvector extension)
DATABASE_URL=postgresql://user:password@localhost:5432/netzero
```

### Service Configuration

From `CopilotService`:

```python
RESPONSE_CACHE_TTL_MINUTES = 60         # Cache responses for 1 hour
RATE_LIMIT_QUERIES_HOURLY = 100         # Max 100 queries per hour
RATE_LIMIT_TOKENS_HOURLY = 100000       # Max 100k tokens per hour
MIN_CONFIDENCE_FOR_RESPONSE = 0.3        # Reject answers with <30% confidence
MAX_CONTEXT_ITEMS = 10                   # Max items per entity type
```

### Claude Configuration

**Model:** `claude-3-5-sonnet-20241022` (latest Claude 3.5 Sonnet)

**Parameters:**
- Temperature: 0.7 (balanced creativity/determinism)
- Max tokens: 2000
- System prompt: ESG-specific guardrails

---

## Guardrails & Safety

### Multi-Layer Safety

#### 1. System Prompt Guardrails

The Claude system prompt includes explicit instructions:

```
CRITICAL GUARDRAILS:
1. **Data Integrity**: ONLY reference data provided in context
2. **Uncertainty**: Explicitly state when data is incomplete
3. **Citations**: ALWAYS cite sources for every fact
4. **Calculations**: Show calculation steps
5. **Confidence**: Indicate confidence level
6. **Scope Clarification**: Clarify emissions scope (1, 2, 3)

PROHIBITED BEHAVIORS:
- Do NOT invent data
- Do NOT claim certainty when uncertain
- Do NOT extrapolate beyond provided data
- Do NOT make recommendations without methodology
- Do NOT reference data outside context
```

#### 2. Fabrication Detection

Automatic checks for fabrication patterns:

```python
def validate_no_fabrication(answer, context):
    # Detects:
    # - "assumed", "estimated", "likely" without qualification
    # - Numbers without source
    # - Claims outside provided context
    # - Excessive speculation
```

Returns issues list:
```python
[
    "Potential fabrication: Answer uses estimates without data",
    "Answer contains unsourced numerical claims"
]
```

#### 3. Context Verification

Before citation, verify source exists:
- Entity exists in database
- Entity ID is valid
- User has access to entity
- Entity is in approved state

#### 4. Confidence Scoring

Confidence reduced if:
- Limited context available
- Answer contains uncertainty language
- Data quality is poor
- Gaps exist in information

Response rejected if confidence < 0.3 (30%)

#### 5. Access Control

- Verify user belongs to tenant
- Check user is active
- Verify tenant is active
- Enforce organization filters
- Validate report approval status

#### 6. Rate Limiting

Per-user, per-hour limits:
- 100 queries per hour
- 100,000 tokens per hour
- Tracks by sliding hourly window

#### 7. Audit Logging

All interactions logged:
- User ID
- Tenant ID
- Action (ask, view, feedback)
- IP address
- Timestamp
- Entity references

---

## Testing

### Test Coverage

#### Unit Tests (test_copilot_service.py)

1. **Embedding Generation (5 tests)**
   - Valid text
   - Empty text handling
   - Long text handling
   - Special characters
   - Multilingual text

2. **Similarity Search (6 tests)**
   - Metric search
   - Calculation search
   - Report search
   - Facility search
   - Multi-entity combination
   - Threshold enforcement

3. **Citation Extraction (5 tests)**
   - Metric citations
   - Calculation citations
   - Multiple citations
   - Source URL inclusion
   - Database tracking

4. **Guardrail Validation (8 tests)**
   - System prompt contents
   - Citation requirements
   - Uncertainty handling
   - Scope clarification
   - Prohibited behaviors
   - Tenant isolation
   - Access control
   - User active check

5. **Fabrication Detection (6 tests)**
   - Assumption detection
   - Speculation detection
   - Legitimate uncertainty
   - Unsourced numbers
   - Cited facts
   - Issue list generation

6. **Access Control (6 tests)**
   - Tenant isolation
   - User active check
   - Tenant active check
   - Per-user rate limiting
   - Tenant-level limits
   - Retry-after on limit

#### Integration Tests (test_copilot_integration.py)

1. **Full Q&A Workflow (5 tests)**
   - End-to-end question to response
   - Organization filtering
   - Response caching
   - Confidence scoring
   - Low confidence rejection

2. **Vector Search to Response (4 tests)**
   - Context retrieval
   - Calculation context
   - Report context
   - Access control

3. **Citation Accuracy (4 tests)**
   - Source verification
   - Data snapshots
   - Source linking
   - Verification marking

4. **Multi-Language (3 tests)**
   - Spanish queries
   - French queries
   - Mixed language

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_copilot_service.py

# Run with coverage
pytest --cov=app tests/
```

---

## Deployment

### Prerequisites

1. **PostgreSQL with pgvector**
   ```bash
   # Install pgvector extension
   CREATE EXTENSION vector;
   ```

2. **API Keys**
   - Set `ANTHROPIC_API_KEY` for Claude
   - Set `OPENAI_API_KEY` for embeddings

3. **Dependencies**
   ```bash
   pip install anthropic openai pgvector
   ```

### Database Migration

```bash
# Apply copilot migration
alembic upgrade 003_add_copilot_tables

# Verify tables created
\dt copilot_*
```

### Environment Setup

Create `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

### Running the Service

```bash
# Start API server
uvicorn app.main:app --reload

# Server running at http://localhost:8000
# Docs at http://localhost:8000/api/docs
```

---

## Troubleshooting

### Common Issues

#### 1. "pgvector extension not found"

**Solution:**
```bash
# Install pgvector in PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
# Set in environment
export ANTHROPIC_API_KEY=sk-ant-...

# Or in .env file
ANTHROPIC_API_KEY=sk-ant-...
```

#### 3. "Rate limit exceeded"

Check response:
```json
{
  "error": "Rate limit exceeded",
  "retry_after_minutes": 15
}
```

Wait 15 minutes or contact admin to increase limits.

#### 4. "Low confidence in response"

Response rejected because data quality is poor. Ensure:
- Required metrics are entered
- Recent data is available
- Reports are approved

#### 5. "Unauthorized access"

Verify:
- User token is valid
- Token includes correct tenant_id
- User belongs to tenant
- User is active

#### 6. Slow embedding generation

**Cause:** First embedding for a query requires API call

**Solution:**
- Cache is enabled (60 minutes)
- Similar questions reuse embeddings
- Monitor API quotas

---

## Performance Metrics

### Response Time Targets

- Cache hit: < 100ms
- New question: 2-5 seconds
- Database query: < 500ms
- Claude API call: 1-3 seconds
- Citation extraction: < 500ms

### Token Usage

Average per query:
- Input tokens: 200-400
- Output tokens: 150-400
- Total: 350-800 tokens per query

Cost (Claude 3.5 Sonnet pricing):
- Input: $0.003 per 1K tokens
- Output: $0.015 per 1K tokens
- Avg cost: ~$0.005 per query

### Database Size

Per 10,000 queries:
- copilot_queries: ~5 MB
- copilot_responses: ~20 MB
- copilot_citations: ~2 MB
- copilot_message_history: ~8 MB
- Total: ~35 MB for 10K queries

---

## Future Enhancements

1. **Streaming Responses** - Stream Claude responses for real-time feedback
2. **Multi-turn Conversations** - Build on previous Q&A in same session
3. **Custom Data Sources** - Allow integration with external data APIs
4. **Response Explainability** - Detailed breakdown of how confidence calculated
5. **A/B Testing** - Compare Claude models and prompt variations
6. **Fine-tuning** - Fine-tune models on domain-specific examples
7. **Caching Strategy** - Advanced caching with semantic deduplication
8. **Analytics Dashboard** - Visualize most-asked questions, trending topics

---

## References

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
- [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401)

---

**Implementation By**: Claude Code Agent
**Contact**: For questions or issues, refer to project documentation
**License**: Proprietary - NetZero Platform
