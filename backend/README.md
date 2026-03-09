# iCarbon Backend

**Framework**: Express.js / Node.js
**Language**: TypeScript
**Database**: PostgreSQL + TimescaleDB
**Status**: In Development

---

## 📋 Overview

The iCarbon backend provides REST and GraphQL APIs for the ESG emissions management platform. Built with Express.js and TypeScript, it integrates with AI agents for emissions analysis and provides real-time monitoring capabilities.

## 🗂️ Project Structure

```
backend/
├── src/
│   ├── api/                         # API Layer
│   │   ├── routes/                 # Route definitions
│   │   │   ├── facilities.ts       # Facility endpoints
│   │   │   ├── emissions.ts        # Emissions endpoints
│   │   │   ├── reports.ts          # Report endpoints
│   │   │   ├── goals.ts            # Goals endpoints
│   │   │   ├── alerts.ts           # Alerts endpoints
│   │   │   ├── users.ts            # User endpoints
│   │   │   └── agents.ts           # Agent endpoints
│   │   └── middleware/
│   │       ├── auth.ts             # Authentication
│   │       ├── validation.ts       # Request validation
│   │       ├── errorHandler.ts     # Error handling
│   │       └── logging.ts          # Request logging
│   │
│   ├── services/                    # Business Logic
│   │   ├── EmissionsService.ts     # Calculations
│   │   ├── ReportingService.ts     # Report generation
│   │   ├── AlertingService.ts      # Alert management
│   │   ├── GoalService.ts          # Goal tracking
│   │   ├── UserService.ts          # User management
│   │   └── AgentService.ts         # Agent orchestration
│   │
│   ├── models/                      # Data Models
│   │   ├── Facility.ts
│   │   ├── Emissions.ts
│   │   ├── Report.ts
│   │   ├── Goal.ts
│   │   ├── Alert.ts
│   │   ├── User.ts
│   │   └── Agent.ts
│   │
│   ├── agents/                      # Agent Integration
│   │   ├── BaseAgent.ts            # Base agent class
│   │   ├── ESGAnalyzerAgent.ts
│   │   ├── EmissionsCalculatorAgent.ts
│   │   ├── InsightsGeneratorAgent.ts
│   │   ├── ComplianceCheckerAgent.ts
│   │   └── RecommendationsAgent.ts
│   │
│   ├── integrations/                # External Integrations
│   │   ├── bms/                    # Building Management Systems
│   │   ├── mqtt/                   # MQTT data sources
│   │   ├── cloud/                  # Cloud providers
│   │   ├── weather/                # Weather data
│   │   └── grid/                   # Grid carbon intensity
│   │
│   ├── middleware/                  # Express Middleware
│   │   ├── authMiddleware.ts
│   │   ├── rateLimiter.ts
│   │   ├── requestLogger.ts
│   │   └── errorHandler.ts
│   │
│   ├── utils/                       # Utilities
│   │   ├── database.ts
│   │   ├── cache.ts
│   │   ├── logger.ts
│   │   ├── validators.ts
│   │   └── formatters.ts
│   │
│   ├── config/                      # Configuration
│   │   ├── env.ts                  # Environment variables
│   │   ├── database.ts             # Database config
│   │   ├── redis.ts                # Cache config
│   │   └── agents.ts               # Agent config
│   │
│   └── app.ts                      # Express app setup
│
├── tests/
│   ├── unit/                       # Unit tests
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── integration/                # Integration tests
│   │   ├── api/
│   │   ├── agents/
│   │   └── services/
│   └── e2e/                        # End-to-end tests
│       ├── workflows/
│       └── scenarios/
│
├── migrations/                     # Database migrations
│   └── [timestamp]_init.sql
│
├── Dockerfile
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── jest.config.js
├── .eslintrc.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- TypeScript 5+

### Installation

```bash
# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Database setup
npm run migrate
npm run seed

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 📡 API Endpoints

### Facilities
```
GET    /api/v1/facilities              # List all facilities
GET    /api/v1/facilities/:id          # Get facility details
POST   /api/v1/facilities              # Create facility
PUT    /api/v1/facilities/:id          # Update facility
DELETE /api/v1/facilities/:id          # Delete facility
```

### Emissions
```
GET    /api/v1/facilities/:id/emissions          # Get emissions
GET    /api/v1/facilities/:id/emissions/summary  # Summary
POST   /api/v1/facilities/:id/emissions/calculate # Calculate
```

### Reports
```
GET    /api/v1/reports                 # List reports
GET    /api/v1/reports/:id            # Get report
POST   /api/v1/reports                # Generate report
GET    /api/v1/reports/:id/export     # Export report
```

### Goals
```
GET    /api/v1/goals                   # List goals
POST   /api/v1/goals                   # Create goal
PUT    /api/v1/goals/:id              # Update goal
GET    /api/v1/goals/:id/progress     # Goal progress
```

### Alerts
```
GET    /api/v1/alerts                  # List alerts
POST   /api/v1/alerts                  # Create alert
PUT    /api/v1/alerts/:id/acknowledge # Acknowledge alert
```

### Agents
```
GET    /api/v1/agents                  # List active agents
POST   /api/v1/agents/tasks           # Submit task to agent
GET    /api/v1/agents/tasks/:id       # Get task status
```

## 🤖 Agent Integration

### Agent Communication

Agents are integrated via service layer:

```typescript
// Example: Using ESG Analyzer Agent
const agent = new ESGAnalyzerAgent();
const analysis = await agent.analyze(facilityData);
const insights = await agent.generateInsights(analysis);
```

### Agent Message Flow
1. Request received by API
2. Service layer routes to appropriate agent
3. Agent processes request
4. Result cached and returned
5. Event published to event bus

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- facilities.test.ts

# Watch mode
npm test -- --watch
```

## 📚 Documentation

- API Docs: `GET /api/docs` (Swagger UI)
- GraphQL: `POST /graphql` (GraphQL endpoint)
- Developer Guide: See `../docs/DEVELOPMENT.md`

## 🔒 Authentication

- OAuth 2.0 / JWT
- Role-based access control
- API key support
- SSO integration (Okta, Azure AD)

## 📊 Database Schema

### Core Tables
- `facilities` - Facility information
- `emissions_records` - Emissions data (TimescaleDB)
- `reports` - Generated reports
- `goals` - Sustainability goals
- `alerts` - System alerts
- `users` - User accounts
- `agents` - Agent configurations

See `migrations/` for complete schema.

## 🚀 Deployment

```bash
# Build Docker image
docker build -t icarbon-backend .

# Run with Docker Compose
docker-compose up backend

# Deploy to Kubernetes
kubectl apply -f ../infrastructure/kubernetes/backend/
```

## 📈 Monitoring

- Health check: `GET /health`
- Metrics: `GET /metrics` (Prometheus)
- Logs: Check `logs/` directory
- Errors: Sentry integration

## 🔄 CI/CD

Tests run automatically on:
- Push to any branch
- Pull requests
- Scheduled nightly builds

See `.github/workflows/ci.yml` for details.

## 📝 Code Standards

- ESLint configuration: `.eslintrc.json`
- Prettier formatting: Auto-format on save
- TypeScript strict mode enabled
- Test coverage: >85% required

## 🤝 Contributing

1. Create feature branch
2. Follow code standards
3. Write tests
4. Submit PR
5. Pass automated checks

See `../CONTRIBUTING.md` for details.

## 📞 Support

- Slack: #icarbon-backend
- Issues: GitHub Issues
- Documentation: See `../docs/`

**Status**: ✅ Active Development
