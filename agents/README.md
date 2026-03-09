# iCarbon Agents - Agentic AI System

**Framework**: LangChain / CrewAI
**Language**: Python 3.11+
**LLM**: Claude API
**Status**: In Development

---

## 🤖 Overview

iCarbon uses a multi-agent system powered by Claude AI for specialized ESG tasks. Each agent is designed for specific responsibilities with clear inputs, outputs, and decision-making processes.

## 🏗️ Agent Architecture

### Agent System Overview

```
┌─────────────────────────────────────────────────────┐
│          Agent Orchestration Layer                   │
│     (Router → Task Dispatcher → Result Aggregator)  │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐   ┌──────────┐
   │ ESG     │   │Emissions │   │Insights  │
   │Analyzer │   │Calculator│   │Generator │
   │Agent    │   │Agent     │   │Agent     │
   └─────────┘   └──────────┘   └──────────┘
        │              │              │
        ▼              ▼              ▼
   ┌──────────────────────────────────────────┐
   │     Message Queue & Event Bus             │
   └──────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │Compliance│   │Recommend │   │Knowledge │
   │Checker   │   │Engine    │   │Store     │
   └──────────┘   └──────────┘   └──────────┘
```

## 📋 Core Agents

### 1. ESG Analyzer Agent
**Purpose**: Analyze facility data for ESG patterns and risks

**Inputs**:
- Facility data (emissions, operations, efficiency)
- Historical data
- Industry benchmarks
- Regulatory context

**Responsibilities**:
- Identify ESG patterns and anomalies
- Compare against benchmarks
- Assess risks and opportunities
- Generate risk reports
- Track compliance status

**Outputs**:
- ESG analysis report
- Risk assessment
- Opportunity identification
- Compliance status

**Example**:
```python
analyzer = ESGAnalyzerAgent()
analysis = await analyzer.analyze(
    facility_id="fac-001",
    data_period="2024-Q1"
)
```

### 2. Emissions Calculator Agent
**Purpose**: Calculate and track emissions across all scopes

**Inputs**:
- Energy consumption data
- Fuel usage data
- Facility operations
- Scope factor updates
- Baseline values

**Responsibilities**:
- Calculate Scope 1 emissions (direct)
- Calculate Scope 2 emissions (indirect - grid)
- Calculate Scope 3 emissions (value chain)
- Apply GHG Protocol methodology
- Update emission factors
- Track calculation history

**Outputs**:
- Scope 1, 2, 3 emissions
- Total CO₂e
- Calculation breakdown
- Uncertainty ranges
- Audit trail

**Example**:
```python
calculator = EmissionsCalculatorAgent()
emissions = await calculator.calculate(
    facility_id="fac-001",
    period="2024-Q1"
)
```

### 3. Insights Generator Agent
**Purpose**: Generate actionable insights from emissions data

**Inputs**:
- Emissions data
- Operational metrics
- Cost data
- Industry standards
- Customer goals

**Responsibilities**:
- Identify trends and patterns
- Detect anomalies
- Generate insights
- Create executive summaries
- Suggest actions
- Prioritize opportunities

**Outputs**:
- Key insights
- Trend analysis
- Actionable recommendations
- Executive summary
- Impact projections

**Example**:
```python
insights = InsightsGeneratorAgent()
results = await insights.generate(
    facility_id="fac-001",
    analysis_type="trends"
)
```

### 4. Compliance Checker Agent
**Purpose**: Validate compliance with regulatory standards

**Inputs**:
- Emissions data
- Reports
- Facility configuration
- Regulatory requirements
- Data quality metrics

**Responsibilities**:
- Validate GRI 305 compliance
- Check TCFD requirements
- Verify CDP alignment
- Audit ISO 14064-1
- Track regulatory changes
- Flag missing data
- Generate audit reports

**Outputs**:
- Compliance status
- Audit findings
- Missing data report
- Recommendations
- Certification status

**Example**:
```python
compliance = ComplianceCheckerAgent()
status = await compliance.check(
    facility_id="fac-001",
    standard="GRI-305"
)
```

### 5. Recommendations Engine Agent
**Purpose**: Suggest optimization initiatives

**Inputs**:
- Emissions data
- Operational efficiency
- Cost analysis
- Industry best practices
- Technology options
- Customer constraints

**Responsibilities**:
- Identify efficiency gains
- Calculate ROI
- Rank recommendations
- Estimate implementation cost
- Project savings
- Suggest timelines
- Track implementation

**Outputs**:
- Ranked recommendations
- ROI analysis
- Implementation roadmap
- Cost-benefit analysis
- Success metrics

**Example**:
```python
recommender = RecommendationsEngineAgent()
recommendations = await recommender.suggest(
    facility_id="fac-001",
    focus_area="efficiency"
)
```

## 🗂️ Project Structure

```
agents/
├── esg-analyzer/
│   ├── agent.py               # Agent implementation
│   ├── prompts.py             # LLM prompts
│   ├── tools.py               # Available tools
│   └── config.json            # Configuration
│
├── emissions-calculator/
│   ├── agent.py
│   ├── models.py              # Calculation models
│   ├── factors.json           # Emission factors
│   └── config.json
│
├── insights-generator/
│   ├── agent.py
│   ├── templates.py           # Report templates
│   ├── prompts.py
│   └── config.json
│
├── compliance-checker/
│   ├── agent.py
│   ├── standards.json         # Compliance rules
│   ├── requirements.py        # Regulatory requirements
│   └── config.json
│
├── recommendations-engine/
│   ├── agent.py
│   ├── models.py              # ML/optimization models
│   ├── roi_calculator.py      # ROI calculation
│   └── config.json
│
├── shared/
│   ├── base_agent.py          # Base agent class
│   ├── tools/                 # Shared tools
│   ├── utils/                 # Utilities
│   └── config.py              # Shared config
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🔧 Base Agent Architecture

### BaseAgent Class

All agents inherit from BaseAgent:

```python
class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = Claude()
        self.memory = AgentMemory()
        self.tools = []

    async def execute(self, task: Task) -> Result:
        """Execute a task and return result"""
        pass

    def register_tool(self, tool: Tool):
        """Register a tool for use"""
        pass

    async def think(self, input: str) -> str:
        """Process input through LLM"""
        pass
```

### Agent Lifecycle

1. **Initialization**: Set up agent with tools and configuration
2. **Input Reception**: Receive task/query
3. **Thinking**: Process through LLM with context
4. **Tool Usage**: Call tools as needed
5. **Decision Making**: Make choices based on results
6. **Output Generation**: Format and return results
7. **Logging**: Track decisions and reasoning

## 🔗 Agent Communication

### Message Protocol

Agents communicate via message queue:

```python
# Publishing a task
await bus.publish(
    topic="agent-tasks",
    message={
        "agent": "emissions-calculator",
        "task": "calculate_scope2",
        "facility_id": "fac-001",
        "period": "2024-Q1"
    }
)

# Subscribing to results
@bus.subscribe("agent-results")
async def handle_result(message):
    result = message.get("result")
    facility_id = message.get("facility_id")
    # Process result
```

### Event Bus Topics

- `agent-tasks` - Incoming tasks
- `agent-results` - Task completions
- `agent-errors` - Error handling
- `data-updates` - Data change notifications
- `compliance-alerts` - Compliance issues

## 🛠️ Agent Tools

### Available Tools

Each agent has access to:

**Data Access**:
- Query facility data
- Get historical emissions
- Access operational metrics
- Get user configuration

**Calculations**:
- Calculate emissions
- Compute ROI
- Generate statistics
- Run models

**External**:
- Call grid carbon API
- Fetch weather data
- Access regulatory databases
- Get industry benchmarks

**Communication**:
- Send notifications
- Create alerts
- Update database
- Log events

### Tool Usage Pattern

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent", "analysis")
        self.register_tool(DataAccessTool())
        self.register_tool(CalculationTool())
        self.register_tool(NotificationTool())
```

## 📊 Agent Configuration

### config.json Format

```json
{
  "agents": [
    {
      "name": "esg-analyzer",
      "enabled": true,
      "model": "claude-opus",
      "temperature": 0.7,
      "tools": ["data-access", "analysis"],
      "concurrency": 5,
      "timeout": 300,
      "retries": 3,
      "logging": "INFO"
    }
  ]
}
```

## 🚀 Getting Started

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run tests
pytest

# Start agents
python -m agents
```

### Environment Variables

```bash
CLAUDE_API_KEY=sk-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
KAFKA_BROKERS=localhost:9092
LOG_LEVEL=INFO
AGENT_TIMEOUT=300
```

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=agents tests/

# Specific agent test
pytest tests/unit/test_emissions_calculator.py
```

## 📈 Monitoring

### Agent Metrics
- Task success rate
- Average execution time
- Error rate
- Tool usage frequency
- Cache hit rate

### Logging
- Agent decisions
- Tool calls
- Error traces
- Performance metrics

```python
import logging

logger = logging.getLogger("agents")
logger.info(f"Agent {self.name} executing task {task.id}")
```

## 🔒 Security

- API key management
- Input validation
- Output sanitization
- Audit logging
- Rate limiting
- Error handling

## 🌐 Multi-Agent Workflows

### Example: Full Analysis Workflow

```python
async def analyze_facility(facility_id: str):
    # Step 1: Calculate emissions
    emissions = await EmissionsCalculatorAgent().execute(
        task=Task(facility_id=facility_id, action="calculate")
    )

    # Step 2: Analyze ESG patterns
    analysis = await ESGAnalyzerAgent().execute(
        task=Task(
            facility_id=facility_id,
            emissions_data=emissions
        )
    )

    # Step 3: Check compliance
    compliance = await ComplianceCheckerAgent().execute(
        task=Task(
            facility_id=facility_id,
            analysis=analysis
        )
    )

    # Step 4: Generate recommendations
    recommendations = await RecommendationsEngineAgent().execute(
        task=Task(
            facility_id=facility_id,
            analysis=analysis,
            compliance_status=compliance
        )
    )

    # Step 5: Generate insights
    insights = await InsightsGeneratorAgent().execute(
        task=Task(
            facility_id=facility_id,
            emissions=emissions,
            analysis=analysis,
            recommendations=recommendations
        )
    )

    return {
        "emissions": emissions,
        "analysis": analysis,
        "compliance": compliance,
        "recommendations": recommendations,
        "insights": insights
    }
```

## 📚 Documentation

- Agent Specifications: See `../docs/AGENTS.md`
- API Integration: See `../docs/API.md`
- Development Guide: See `../docs/DEVELOPMENT.md`

## 🤝 Contributing

1. Create feature branch
2. Implement agent with tests
3. Document functionality
4. Submit PR
5. Pass automated checks

## 📞 Support

- Slack: #icarbon-agents
- Issues: GitHub Issues
- Documentation: See `../docs/AGENTS.md`

**Status**: ✅ Active Development
