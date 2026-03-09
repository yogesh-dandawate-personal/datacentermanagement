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
	@echo "$(CYAN)Available commands:$(NC)"
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

.DEFAULT_GOAL := help
