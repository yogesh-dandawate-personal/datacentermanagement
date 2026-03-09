# iCarbon Project Structure

## Directory Tree

```
icarbon/
├── backend/                          # Node.js/Express Backend
│   ├── src/
│   │   ├── api/                     # REST & GraphQL endpoints
│   │   ├── services/                # Business logic
│   │   ├── models/                  # Data models
│   │   ├── agents/                  # Agent integration
│   │   ├── integrations/            # External connectors
│   │   ├── middleware/              # Auth, validation, logging
│   │   ├── utils/                   # Helper functions
│   │   └── config/                  # Configuration
│   ├── tests/                       # Unit, integration, E2E
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
│
├── frontend/                         # React Web Application
│   ├── src/
│   │   ├── components/              # UI components
│   │   ├── pages/                   # Page components
│   │   ├── services/                # API clients
│   │   ├── hooks/                   # Custom hooks
│   │   ├── store/                   # Redux state
│   │   ├── utils/                   # Utilities
│   │   └── assets/                  # Images, styles
│   ├── public/                      # Static files
│   ├── tests/                       # Component tests
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
│
├── agents/                          # AI Agents (Python)
│   ├── esg-analyzer/               # ESG analysis agent
│   ├── emissions-calculator/       # Emissions calculator
│   ├── insights-generator/         # Insights generation
│   ├── compliance-checker/         # Compliance validation
│   ├── recommendations-engine/     # Recommendations
│   ├── shared/                     # Shared utilities
│   ├── tests/                      # Agent tests
│   ├── requirements.txt
│   └── README.md
│
├── infrastructure/                  # DevOps & Infrastructure
│   ├── docker/                     # Docker configs
│   ├── kubernetes/                 # K8s manifests
│   ├── terraform/                  # IaC
│   └── scripts/                    # Setup scripts
│
├── docs/                            # Documentation
│   ├── API.md                      # API documentation
│   ├── ARCHITECTURE.md             # System design
│   ├── AGENTS.md                   # Agent specs
│   ├── INSTALLATION.md             # Setup guide
│   ├── DEVELOPMENT.md              # Dev guide
│   └── DEPLOYMENT.md               # Deploy guide
│
├── config/                          # Configuration
│   ├── .env.example                # Env template
│   ├── logging.yml                 # Logging config
│   └── app-config.yml              # App config
│
├── scripts/                         # Utility scripts
│   ├── setup.sh                    # Initial setup
│   ├── migrate.sh                  # DB migrations
│   └── seed-data.sh                # Test data
│
├── .github/                         # GitHub Actions
│   └── workflows/
│       ├── ci.yml                  # Tests & linting
│       ├── cd.yml                  # Deployment
│       └── security.yml            # Security scans
│
├── .gitignore
├── docker-compose.yml              # Local dev setup
├── Makefile                        # Common commands
├── README.md                       # Project README
├── STRUCTURE.md                    # This file
├── CHANGELOG.md                    # Version history
└── LICENSE                         # MIT License
```

## Directory Descriptions

### Backend (`/backend`)
- **Framework**: Express.js
- **Language**: TypeScript
- **Purpose**: REST/GraphQL APIs, business logic
- **Key Files**:
  - `src/api/` - API endpoints
  - `src/services/` - Service layer
  - `src/agents/` - Agent integration
  - `tests/` - Test suites

### Frontend (`/frontend`)
- **Framework**: React 18
- **Language**: TypeScript
- **Purpose**: Web dashboard and UI
- **Key Files**:
  - `src/components/` - Reusable components
  - `src/pages/` - Page layouts
  - `src/store/` - Redux state
  - `tests/` - Component tests

### Agents (`/agents`)
- **Framework**: LangChain / CrewAI
- **Language**: Python 3.11+
- **Purpose**: AI-powered ESG analysis
- **Key Files**:
  - `esg-analyzer/` - ESG analyzer agent
  - `emissions-calculator/` - Emissions agent
  - `insights-generator/` - Insights agent
  - `compliance-checker/` - Compliance agent
  - `recommendations-engine/` - Recommendations agent

### Infrastructure (`/infrastructure`)
- **Purpose**: DevOps, deployment, infrastructure as code
- **Key Files**:
  - `docker/` - Docker configurations
  - `kubernetes/` - K8s manifests
  - `terraform/` - Terraform modules
  - `scripts/` - Setup and deployment scripts

### Documentation (`/docs`)
- **Purpose**: Project and API documentation
- **Key Files**:
  - `API.md` - REST/GraphQL API docs
  - `ARCHITECTURE.md` - System architecture
  - `AGENTS.md` - Agent specifications
  - `DEVELOPMENT.md` - Developer guide
  - `DEPLOYMENT.md` - Deployment guide

### Configuration (`/config`)
- **Purpose**: Configuration files and templates
- **Key Files**:
  - `.env.example` - Environment variables template
  - `logging.yml` - Logging configuration
  - `app-config.yml` - Application configuration

### Scripts (`/scripts`)
- **Purpose**: Utility and setup scripts
- **Key Files**:
  - `setup.sh` - Initial project setup
  - `migrate.sh` - Database migrations
  - `seed-data.sh` - Test data seeding

### GitHub Actions (`/.github/workflows`)
- **Purpose**: CI/CD pipelines
- **Key Files**:
  - `ci.yml` - Continuous integration
  - `cd.yml` - Continuous deployment
  - `security.yml` - Security scanning

## Key Files at Root

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `STRUCTURE.md` | This file - directory structure guide |
| `Makefile` | Common commands (make install, make dev, etc.) |
| `docker-compose.yml` | Local development environment setup |
| `.gitignore` | Git ignore patterns |
| `CHANGELOG.md` | Version history and releases |
| `LICENSE` | MIT License |

## Technology Stack Overview

### Backend
- Node.js 18+ / Express.js
- TypeScript
- PostgreSQL + TimescaleDB
- Redis
- Kafka
- Elasticsearch

### Frontend
- React 18
- TypeScript
- Redux Toolkit
- Tailwind CSS
- Chart.js / D3.js

### Agents
- Python 3.11+
- LangChain / CrewAI
- Claude API
- NumPy, Pandas, Scikit-learn

### Infrastructure
- Docker & Docker Compose
- Kubernetes
- Terraform
- GitHub Actions
- Prometheus & Grafana

## Development Workflow

1. **Clone Repository**
   ```bash
   git clone <repo-url>
   cd icarbon
   ```

2. **Setup Environment**
   ```bash
   make setup
   ```

3. **Start Development**
   ```bash
   make dev
   ```

4. **Make Changes**
   - Create feature branch
   - Write code following standards
   - Add tests

5. **Test & Validate**
   ```bash
   make lint
   make test
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: description"
   git push origin feature-branch
   ```

7. **Submit Pull Request**
   - Automated tests run
   - Code review
   - Merge to develop
   - Deploy to staging

## Quick Commands

```bash
# Start everything
make dev

# Run tests
make test

# Build for production
make build

# Deploy
make deploy-prod

# Clean everything
make clean

# Database operations
make migrate
make seed
make seed-fresh
```

See `Makefile` for all available commands.

## Environment Setup

### Required Environment Variables

Create `.env` from template:
```bash
cp config/.env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `KAFKA_BROKERS` - Kafka brokers
- `CLAUDE_API_KEY` - Claude API key
- `JWT_SECRET` - JWT signing secret
- `LOG_LEVEL` - Logging level

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3001 | http://localhost:3001 |
| Backend | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Kafka | 9092 | localhost:9092 |
| Elasticsearch | 9200 | http://localhost:9200 |
| Kibana | 5601 | http://localhost:5601 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3002 | http://localhost:3002 |

## Testing Structure

```
tests/
├── backend/tests/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
├── frontend/tests/
│   ├── unit/           # Component tests
│   └── integration/    # Feature tests
└── agents/tests/
    ├── unit/           # Agent tests
    └── integration/    # Multi-agent tests
```

## CI/CD Pipeline

### On Push to Any Branch
- ✅ Run linters (ESLint, Pylint)
- ✅ Run unit tests
- ✅ Build artifacts
- ✅ Security scanning

### On Pull Request
- ✅ All above checks
- ✅ Integration tests
- ✅ Code coverage validation
- ✅ Manual code review

### On Merge to Main
- ✅ All checks
- ✅ Deploy to production
- ✅ Run smoke tests
- ✅ Update documentation

## Contributing

See `CONTRIBUTING.md` for:
- Code standards
- Pull request process
- Commit message format
- Testing requirements
- Documentation guidelines

## Documentation

### For Users
- `README.md` - Getting started
- `docs/INSTALLATION.md` - Installation guide

### For Developers
- `docs/DEVELOPMENT.md` - Development setup
- `docs/ARCHITECTURE.md` - System design
- `backend/README.md` - Backend guide
- `frontend/README.md` - Frontend guide
- `agents/README.md` - Agents guide

### For DevOps
- `docs/DEPLOYMENT.md` - Production deployment
- `infrastructure/README.md` - Infrastructure guide

### For API Consumers
- `docs/API.md` - API documentation
- `http://localhost:3000/api/docs` - Interactive Swagger UI

## Support & Resources

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: GitHub Wiki
- **Documentation**: `/docs` folder
- **Slack**: #icarbon-dev

## License

MIT License - See `LICENSE` file

---

**Status**: ✅ Project structure ready for development
**Last Updated**: March 9, 2026
