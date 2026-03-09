# Sprint 13: Executive Copilot (AI Assistant)

**Sprint**: 13
**Duration**: August 31 - September 13, 2026 (2 weeks)
**Module**: Executive Copilot
**Owner**: Backend + ML Team
**Status**: 📋 PLANNED

---

## Executive Summary

Implements AI-powered Q&A system for ESG data analysis:
- Natural language question answering
- Vector embeddings and semantic search
- Integration with Claude API
- Citation tracking and provenance
- Access control and data filtering
- Query history and analytics
- No hallucination guardrails

**Dependency**: Agent Orchestrator (Sprint 12) ✅

---

## Scope & Deliverables

- [x] Copilot chat interface
- [x] Semantic search with pgvector
- [x] Claude API integration
- [x] Citation tracking
- [x] Access control enforcement
- [x] Query validation
- [x] Response caching
- [x] Audit logging
- [x] Query analytics

---

## Core Features

```
1. Natural Language Queries
   "What's our Scope 2 emissions this month?"
   "Show me PUE trends for DC-North"
   "Which facilities exceeded water usage targets?"

2. Intelligent Responses
   - Retrieved from ESG data
   - Cited with source IDs
   - Links to underlying data
   - No fabrication

3. Multi-turn Conversations
   - Context awareness
   - Follow-up questions
   - Refinement

4. Safety & Governance
   - Only approved data (or user-authorized draft)
   - Explicit access control
   - Audit trail of all queries
   - Confidence scores
```

---

## Database Schema

```sql
CREATE TABLE copilot_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    question_text TEXT NOT NULL,
    response_text TEXT,
    confidence_score DECIMAL(5, 4),
    status VARCHAR(50),
    query_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX(tenant_id, user_id, created_at)
);

CREATE TABLE copilot_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES copilot_queries(id),
    source_entity_type VARCHAR(50),
    source_entity_id UUID NOT NULL,
    citation_text TEXT,
    relevance_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vector_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID NOT NULL,
    entity_text TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX USING hnsw (embedding vector_cosine_ops)
);

CREATE TABLE document_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_type VARCHAR(50),
    document_id UUID NOT NULL,
    document_text TEXT,
    text_embedding vector(1536),
    last_indexed TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX USING hnsw (text_embedding vector_cosine_ops)
);
```

---

## API Endpoints

```
POST   /api/v1/tenants/{tenant_id}/copilot/ask
       Ask question to copilot
       Request: {question}
       Response: {response, citations: [{entity_id, text}], confidence}

GET    /api/v1/tenants/{tenant_id}/copilot/history
       Get query history
       Query: ?limit=50&offset=0
       Response: {items: [...], total_count: N}

GET    /api/v1/tenants/{tenant_id}/copilot/analytics
       Copilot usage analytics
       Response: {total_queries, most_asked, confidence_distribution}

POST   /api/v1/copilot/embeddings/refresh
       Refresh vector embeddings
       Request: {entity_types: ['report', 'metric']}
```

---

## Copilot Service Architecture

```python
class CopilotService:
    def answer_question(self, tenant_id, user_id, question):
        # 1. Validate user has access to ESG data
        # 2. Semantic search for relevant documents
        docs = self.semantic_search(question, top_k=10)
        # 3. Filter by user permissions
        docs = self.filter_by_access(user_id, docs)
        # 4. Call Claude API with context
        response = self.llm.generate(question, context=docs)
        # 5. Extract and validate citations
        citations = self.extract_citations(response, docs)
        # 6. Check confidence score
        confidence = self.calculate_confidence(response, citations)
        # 7. Log query and audit
        self.audit_log(tenant_id, user_id, question, response)
        return {response, citations, confidence}

class VectorSearchService:
    def semantic_search(self, query, top_k=10):
        # Generate embedding for query
        query_embedding = self.embed(query)
        # Search pgvector index
        results = self.db.search_similarity(
            query_embedding,
            similarity_threshold=0.7,
            limit=top_k
        )
        return results
```

---

## Example Queries & Responses

```
Q: "What's our Scope 2 emissions this month?"
A: "Based on your grid consumption of 50,000 kWh in March 2026
    and a regional emission factor of 0.4 kg CO₂/kWh, your Scope 2
    emissions are 20,000 kg CO₂e.

    Sources:
    - Report: March 2026 ESG Report (report-id-123)
    - Metric: Grid consumption (metric-id-456)
    - Factor: US Eastern Grid 2026 v3 (factor-id-789)"

Q: "Which facilities exceeded water targets?"
A: "DC-North exceeded its WUE target in February by 0.3 L/kWh.

    Facility: DC-North
    Target: <1.8 L/kWh
    Actual: 2.1 L/kWh
    Exceeded by: 16.7%

    Sources:
    - Metric: DC-North February KPI (metric-id-111)
    - Threshold: WUE target (threshold-id-222)"

Q: "Show me PUE trends"
A: "Unable to provide trend data. To show historical trends,
    please specify a date range:
    'Show me PUE trends for January-March 2026'"
```

---

## Safety Guardrails

```python
# 1. No Fabrication
if confidence < 0.5:
    return "I don't have sufficient data to answer this question."

# 2. Access Control
approved_data = filter_by_user_access(user, data)
if not approved_data:
    return "You don't have access to this information."

# 3. Citation Requirement
if not citations_found:
    return "Unable to answer - supporting data not found."

# 4. Audit Logging
log_query(user_id, tenant_id, question, response, confidence)

# 5. Rate Limiting
check_rate_limit(user_id, queries_per_min=10)
```

---

## Integration with Other Modules

- **Reports**: Cite report IDs and versions
- **Metrics**: Link to energy, carbon, KPI snapshots
- **Evidence**: Reference supporting documents
- **Approvals**: Check if data is in approved state
- **Agents**: Leverage agent outputs and citations

---

## Testing

- Unit tests: embedding generation, similarity search
- Integration tests: vector search, access control
- E2E tests: question answering journey
- Safety tests: no hallucinations, proper citations
- Performance: response time <2 seconds
- Accuracy: citation validation tests

---

## Future Enhancements (Phase 2)

- Multi-turn conversation context
- Recommendation suggestions
- Optimization insights
- Predictive analysis
- Natural language report generation

---

**Target**: August 31 - September 13, 2026 | **Owner**: Backend + ML Team

---

## Completion Status

This represents the **final sprint** of the core MVP. Upon completion:

✅ **13 modules implemented**
✅ **Full ESG platform operational**
✅ **All user journeys enabled**
✅ **Approval workflows active**
✅ **AI agents operational**
✅ **Executive copilot live**

**Platform ready for:** Production deployment, customer testing, market launch
