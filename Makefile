.PHONY: help install setup dev test build deploy clean

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
AGENTS_DIR = agents

# Color output
CYAN = \033[0;36m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m # No Color

help:
	@echo "$(CYAN)iCarbon - SaaS ESG Emissions Platform$(NC)"
	@echo ""
	@echo "$(CYAN)Development Commands:$(NC)"
	@echo "  $(GREEN)make install$(NC)        - Install all dependencies"
	@echo "  $(GREEN)make setup$(NC)          - Setup local development environment"
	@echo "  $(GREEN)make dev$(NC)            - Start all services in development mode"
	@echo "  $(GREEN)make backend-dev$(NC)    - Start backend only"
	@echo "  $(GREEN)make frontend-dev$(NC)   - Start frontend only"
	@echo "  $(GREEN)make agents-dev$(NC)     - Start agents only"
	@echo "  $(GREEN)make test$(NC)           - Run all tests"
	@echo "  $(GREEN)make test-unit$(NC)      - Run unit tests only"
	@echo "  $(GREEN)make test-integration$(NC) - Run integration tests"
	@echo "  $(GREEN)make build$(NC)          - Build for production"
	@echo "  $(GREEN)make docker-build$(NC)   - Build Docker images"
	@echo "  $(GREEN)make docker-up$(NC)      - Start Docker containers"
	@echo "  $(GREEN)make docker-down$(NC)    - Stop Docker containers"
	@echo "  $(GREEN)make migrate$(NC)        - Run database migrations"
	@echo "  $(GREEN)make seed$(NC)           - Seed database with test data"
	@echo "  $(GREEN)make lint$(NC)           - Run linters"
	@echo "  $(GREEN)make format$(NC)         - Format code"
	@echo "  $(GREEN)make clean$(NC)          - Clean build artifacts"
	@echo ""
	@echo "$(CYAN)Autonomous Development (NEW):$(NC)"
	@echo "  $(GREEN)make sprints-execute$(NC)  - Run all 13 sprints in parallel"
	@echo "  $(GREEN)make live-progress$(NC)    - Real-time progress bar (updates every 5s)"
	@echo "  $(GREEN)make live-progress-once$(NC) - Show current progress once"
	@echo "  $(GREEN)make agent-status$(NC)     - Show agent utilization metrics"
	@echo "  $(GREEN)make daily-standup$(NC)    - Generate daily standup report"

# Installation
install: install-backend install-frontend install-agents
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-backend:
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && npm install

install-frontend:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install

install-agents:
	@echo "Installing agents dependencies..."
	cd $(AGENTS_DIR) && python -m pip install -r requirements.txt

# Setup
setup: install env-setup
	@echo "$(GREEN)✓ Development environment setup complete$(NC)"

env-setup:
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp config/.env.example .env; \
		echo "$(YELLOW)⚠ Please update .env with your configuration$(NC)"; \
	fi

# Development
dev: docker-up
	@echo "$(CYAN)Starting all services...$(NC)"
	@echo "$(YELLOW)Backend will start on http://localhost:3000$(NC)"
	@echo "$(YELLOW)Frontend will start on http://localhost:3001$(NC)"
	@echo "$(YELLOW)API docs: http://localhost:3000/api/docs$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@sleep 2
	@make backend-dev & make frontend-dev & make agents-dev

backend-dev:
	@echo "Starting backend..."
	cd $(BACKEND_DIR) && npm run dev

frontend-dev:
	@echo "Starting frontend..."
	cd $(FRONTEND_DIR) && npm start

agents-dev:
	@echo "Starting agents..."
	cd $(AGENTS_DIR) && python -m agents

# Testing
test: test-backend test-frontend test-agents
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-unit: test-backend-unit test-frontend-unit
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

test-integration: test-backend-integration

test-backend:
	@echo "Running backend tests..."
	cd $(BACKEND_DIR) && npm test

test-backend-unit:
	@echo "Running backend unit tests..."
	cd $(BACKEND_DIR) && npm run test:unit

test-backend-integration:
	@echo "Running backend integration tests..."
	cd $(BACKEND_DIR) && npm run test:integration

test-frontend:
	@echo "Running frontend tests..."
	cd $(FRONTEND_DIR) && npm test -- --watchAll=false

test-agents:
	@echo "Running agent tests..."
	cd $(AGENTS_DIR) && python -m pytest

# Building
build: build-backend build-frontend
	@echo "$(GREEN)✓ Production build complete$(NC)"

build-backend:
	@echo "Building backend..."
	cd $(BACKEND_DIR) && npm run build

build-frontend:
	@echo "Building frontend..."
	cd $(FRONTEND_DIR) && npm run build

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis: localhost:6379"
	@echo "  Kafka: localhost:9092"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	@echo "$(GREEN)✓ Docker volumes cleaned$(NC)"

# Database
migrate:
	@echo "Running database migrations..."
	cd $(BACKEND_DIR) && npm run migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

migrate-fresh:
	@echo "Refreshing database (WARNING: This will delete all data)..."
	cd $(BACKEND_DIR) && npm run migrate:fresh

seed:
	@echo "Seeding database with test data..."
	cd $(BACKEND_DIR) && npm run seed
	@echo "$(GREEN)✓ Database seeded$(NC)"

seed-fresh: migrate-fresh seed

# Code Quality
lint: lint-backend lint-frontend lint-agents
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-backend:
	@echo "Linting backend..."
	cd $(BACKEND_DIR) && npm run lint

lint-frontend:
	@echo "Linting frontend..."
	cd $(FRONTEND_DIR) && npm run lint

lint-agents:
	@echo "Linting agents..."
	cd $(AGENTS_DIR) && python -m pylint agents/

format: format-backend format-frontend format-agents
	@echo "$(GREEN)✓ Formatting complete$(NC)"

format-backend:
	@echo "Formatting backend..."
	cd $(BACKEND_DIR) && npm run format

format-frontend:
	@echo "Formatting frontend..."
	cd $(FRONTEND_DIR) && npm run format

format-agents:
	@echo "Formatting agents..."
	cd $(AGENTS_DIR) && python -m black agents/

type-check: type-check-backend type-check-frontend

type-check-backend:
	@echo "Type checking backend..."
	cd $(BACKEND_DIR) && npm run type-check

type-check-frontend:
	@echo "Type checking frontend..."
	cd $(FRONTEND_DIR) && npm run type-check

# Deployment
deploy: deploy-staging

deploy-staging: build
	@echo "Deploying to staging..."
	@echo "$(YELLOW)TODO: Implement staging deployment$(NC)"

deploy-prod: build test
	@echo "Deploying to production..."
	@echo "$(YELLOW)TODO: Implement production deployment$(NC)"

# Cleanup
clean: docker-clean
	@echo "Cleaning build artifacts..."
	rm -rf $(BACKEND_DIR)/dist
	rm -rf $(BACKEND_DIR)/build
	rm -rf $(BACKEND_DIR)/coverage
	rm -rf $(FRONTEND_DIR)/build
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(AGENTS_DIR)/build
	rm -rf $(AGENTS_DIR)/__pycache__
	rm -rf $(AGENTS_DIR)/.pytest_cache
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Status
status:
	@echo "$(CYAN)Service Status:$(NC)"
	@docker-compose ps || echo "Docker not running"
	@echo ""
	@echo "$(CYAN)Git Status:$(NC)"
	@git status --short || echo "Not a git repository"

# Agent orchestration
agent-start:
	@python3 scripts/agent-orchestrator.py --daemon

agent-stop:
	@pkill -f agent-orchestrator.py

orchestrator-start:
	@python3 scripts/agent-orchestrator.py --mode daemon &
	@python3 scripts/progress-reporter.py --watch &
	@echo "$(GREEN)✓ Orchestrator started (detached)$(NC)"
	@echo "  View progress: make progress-watch"

orchestrator-stop:
	@pkill -f agent-orchestrator.py || true
	@pkill -f progress-reporter.py || true
	@echo "$(GREEN)✓ Orchestrator stopped$(NC)"

# Progress reporting
progress-report:
	@python3 scripts/progress-reporter.py

progress-watch:
	@python3 scripts/progress-reporter.py --watch

live-progress:
	@python3 scripts/live-progress.py --watch

live-progress-once:
	@python3 scripts/live-progress.py

daily-standup:
	@python3 scripts/daily-standup-generator.py --date $(DATE)

standup-save:
	@python3 scripts/progress-reporter.py --save-standup

# Checkpoint management
checkpoint-create:
	@python3 scripts/checkpoint-manager.py create $(SESSION) $(AGENT) $(PHASE)

checkpoint-restore:
	@python3 scripts/checkpoint-manager.py restore $(SESSION) $(AGENT) $(CHECKPOINT)

checkpoint-list:
	@python3 scripts/checkpoint-manager.py list $(SESSION) $(AGENT)

# Agent status
agent-status:
	@python3 scripts/agent-orchestrator.py --status $(AGENT)

agent-sessions:
	@tmux list-sessions 2>/dev/null | grep agent- || echo "No active agent sessions"

# Parallel TDD
parallel-tdd:
	@python3 scripts/parallel-tdd-orchestrator.py $(STORY)

# Ralph Loop execution
ralph-loop:
	@python3 scripts/ralph-loop-executor.py $(STORY) $(AGENT)

# Help commands
docs:
	@echo "Opening documentation..."
	@open docs/README.md || xdg-open docs/README.md

logs:
	@docker-compose logs -f

ps:
	@docker-compose ps

# Development utilities
db-shell:
	docker-compose exec postgres psql -U postgres -d icarbon

redis-cli:
	docker-compose exec redis redis-cli

# All-in-one commands
start: setup dev

start-fresh: clean install setup seed dev

stop:
	docker-compose down

restart: stop start

reset: clean install setup seed

# Autonomous development
autonomous-start: docker-up orchestrator-start
	@echo "$(GREEN)✓ Autonomous development system started$(NC)"
	@echo "  Dashboard: make progress-watch"
	@echo "  Agent status: make agent-status"
	@echo "  Daily standup: make daily-standup"

autonomous-stop: orchestrator-stop docker-down
	@echo "$(GREEN)✓ Autonomous development system stopped$(NC)"

# Parallel sprint execution (all 13 sprints in parallel with auto-progression)
sprints-execute:
	@echo "$(CYAN)Executing all 13 sprints in parallel mode...$(NC)"
	@echo "$(YELLOW)No user prompts - full autonomous mode enabled$(NC)"
	@python3 scripts/agent-orchestrator.py --mode daemon &
	@python3 scripts/progress-reporter.py --watch &
	@python3 scripts/recovery-handler.py --daemon &
	@echo "$(GREEN)✓ Parallel sprint execution started$(NC)"
	@echo "  13 sprints will execute with auto-progression"
	@echo "  Max 2 sprints in parallel (parallel_group 1 & 2)"
	@echo "  Zero user interaction required"
	@echo "  View progress: make progress-watch"

sprints-status:
	@python3 scripts/progress-reporter.py

sprints-stop:
	@pkill -f agent-orchestrator.py || true
	@pkill -f progress-reporter.py || true
	@pkill -f recovery-handler.py || true
	@echo "$(GREEN)✓ Sprint execution stopped$(NC)"

# Deployment
deploy-staging:
	@echo "$(CYAN)Deploying to Vercel Staging...$(NC)"
	@bash scripts/deploy-vercel.sh staging
	@echo "$(GREEN)✓ Staging deployment complete$(NC)"
	@echo "  URL: https://netzero.vercel.app"

deploy-production:
	@echo "$(CYAN)Deploying to Vercel Production...$(NC)"
	@bash scripts/deploy-vercel.sh production
	@echo "$(GREEN)✓ Production deployment complete$(NC)"
	@echo "  URL: https://app.netzero.io"

deploy-force-production:
	@echo "$(RED)⚠ FORCING PRODUCTION DEPLOYMENT$(NC)"
	@bash scripts/deploy-vercel.sh production true
	@echo "$(GREEN)✓ Production deployment complete$(NC)"

.DEFAULT_GOAL := help
