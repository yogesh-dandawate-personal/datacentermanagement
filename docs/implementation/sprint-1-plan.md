# Sprint 1 Implementation Plan: Auth & Tenant Setup

**Sprint**: Sprint 1
**Duration**: 3 weeks (March 9-29, 2026)
**Objective**: Build authentication, tenant isolation, and foundational infrastructure
**Owner**: Backend Team + DevOps
**Status**: 📋 READY FOR EXECUTION

---

## Sprint Overview

### User Story
```
As a SaaS administrator,
I want to onboard new tenants with isolated multi-tenant infrastructure,
So that each customer has secure, separate access to the platform.
```

### Acceptance Criteria
- [ ] A tenant can be created via API with unique slug and configuration
- [ ] A user can log in via Keycloak OAuth2 flow
- [ ] User context (tenant, roles) is extracted from JWT token
- [ ] API endpoints enforce tenant scoping (cannot access other tenant data)
- [ ] All material changes are logged to audit table with user/timestamp
- [ ] Integration tests pass for complete tenant-to-authenticated-user flow
- [ ] At least 85% unit test coverage for auth modules
- [ ] All linting and type checking passes (Black, MyPy)

---

## Phase 1: Database Schema & Migrations

### Task: Create Initial Alembic Migration

**Files to Create**:
```
backend/
├── alembic/                               # Migration tool config
│   ├── env.py                            # Alembic environment
│   ├── script.py.mako                    # Migration template
│   └── versions/
│       └── 001_initial_schema.py         # Phase 1 migration
├── alembic.ini                           # Alembic configuration
└── models/
    └── __init__.py
```

**Migration: 001_initial_schema.py**

Tables to create:
1. **tenants** - Root isolation boundary
2. **organizations** - Logical groups within tenant
3. **users** - App user records (linked to Keycloak)
4. **roles** - Role definitions (admin, editor, viewer)
5. **user_roles** - User-role assignments
6. **audit_logs** - Immutable change trail

```sql
-- tenants (root multi-tenancy table)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,  -- URL-friendly identifier
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, suspended
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_status ON tenants(status);

-- organizations (within tenant)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    unit_system VARCHAR(20) DEFAULT 'metric',  -- metric, imperial
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_orgs_tenant ON organizations(tenant_id);

-- users (keycloak user mapping)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    keycloak_id VARCHAR(255) UNIQUE NOT NULL,  -- Keycloak user ID
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, invited
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_keycloak ON users(keycloak_id);

-- roles (permission sets)
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]'::jsonb,  -- Array of permission strings
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_roles_tenant ON roles(tenant_id);

-- user_roles (many-to-many)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by VARCHAR(255) NOT NULL,
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);

-- audit_logs (immutable trail)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resource_type VARCHAR(100) NOT NULL,  -- 'tenant', 'organization', 'user', etc.
    resource_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete', 'approve', etc.
    old_values JSONB,
    new_values JSONB,
    reason TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
```

**Constraints & Indexes**:
- ✅ Foreign key constraints enforce referential integrity
- ✅ NOT NULL constraints on required fields
- ✅ UNIQUE constraints prevent duplicates
- ✅ Indexes on frequently queried columns
- ✅ Soft delete support (deleted_at column)
- ✅ Audit fields on all transactional tables

**Testing**:
- [ ] Migration is reversible (test rollback)
- [ ] Schema matches Pydantic models
- [ ] All indexes create successfully
- [ ] Foreign keys prevent orphaned records

---

## Phase 2: Backend Application Setup

### Task: Create FastAPI Project Structure

**File Structure**:
```
backend/
├── pyproject.toml                        # Project metadata & deps
├── requirements.txt                      # Pinned dependencies
├── setup.py                              # Package setup
├── .env.example                          # Environment template
├── Dockerfile                            # Container config
├── alembic.ini                           # Migration config
├── src/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app entry
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                  # Config management
│   │   ├── database.py                  # DB connection
│   │   └── keycloak.py                  # Keycloak config
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py                    # Tenant model
│   │   ├── organization.py              # Organization model
│   │   ├── user.py                      # User model
│   │   └── audit.py                     # Audit log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── tenant.py                    # Pydantic schemas
│   │   ├── auth.py
│   │   └── common.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Auth endpoints
│   │   │   └── tenants.py               # Tenant endpoints
│   │   └── health.py                    # Health check
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                      # JWT validation
│   │   ├── tenant.py                    # Tenant scoping
│   │   ├── logging.py                   # Request logging
│   │   └── error_handler.py             # Exception handling
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tenant_service.py            # Business logic
│   │   ├── auth_service.py
│   │   └── audit_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── base_repository.py           # ORM abstraction
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py                  # Password hashing
│   │   ├── logging.py                   # Logger setup
│   │   └── validators.py                # Common validation
│   └── dependencies/
│       ├── __init__.py
│       ├── database.py                  # DB session dep
│       └── auth.py                      # Current user dep
├── tests/
│   ├── conftest.py                      # Shared fixtures
│   ├── test_auth.py                     # Auth endpoint tests
│   ├── test_tenant.py                   # Tenant tests
│   ├── test_models.py                   # Model tests
│   └── fixtures/
│       ├── tenant.py
│       ├── user.py
│       └── keycloak.py
└── README.md
```

**Key Files to Implement**:

### src/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import Settings
from src.middleware.auth import JWTAuthMiddleware
from src.middleware.tenant import TenantMiddleware
from src.api.v1 import auth, tenants
from src.api.health import router as health_router

settings = Settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(TenantMiddleware)
app.add_middleware(JWTAuthMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(tenants.router, prefix="/api/v1/tenants")

@app.on_event("startup")
async def startup():
    # Initialize database connection
    # Setup logging
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup resources
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
```

### src/config/settings.py
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API
    API_TITLE: str = "iNetZero ESG Platform"
    API_VERSION: str = "1.0.0"
    API_PORT: int = 3000
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/icarbon"

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Keycloak
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "icarbon"
    KEYCLOAK_CLIENT_ID: str = "icarbon-backend"
    KEYCLOAK_CLIENT_SECRET: str

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
```

---

## Phase 3: Authentication Implementation

### Task: Keycloak Integration

**Steps**:
1. Start Keycloak service: `docker-compose up keycloak`
2. Access Keycloak admin: http://localhost:8080
3. Create realm: `icarbon`
4. Create client: `icarbon-backend`
5. Configure client credentials
6. Create default roles

**Setup Script** (scripts/keycloak-setup.sh):
```bash
#!/bin/bash
# Configure Keycloak realm and client
# Runs after first Keycloak startup

KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"

# Get access token
TOKEN=$(curl -s -X POST \
  "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=$ADMIN_USER" \
  -d "password=$ADMIN_PASSWORD" \
  -d "grant_type=password" | jq -r '.access_token')

# Create realm
curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "icarbon",
    "enabled": true
  }'

# Create client
curl -s -X POST \
  "$KEYCLOAK_URL/admin/realms/icarbon/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "icarbon-backend",
    "secret": "your-secret-here",
    "enabled": true,
    "bearerOnly": true,
    "publicClient": false,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "redirectUris": ["http://localhost:3000/*"]
  }'

echo "Keycloak setup complete"
```

---

## Phase 4: API Endpoints

### Task: Implement Auth & Tenant Endpoints

**Endpoints to Create**:

#### Authentication (src/api/v1/auth.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from src.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, UserInfo
from src.services.auth_service import AuthService

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, service: AuthService = Depends()):
    """Authenticate user with Keycloak"""
    token = await service.authenticate_with_keycloak(
        username=request.username,
        password=request.password
    )
    return LoginResponse(access_token=token)

@router.post("/refresh", response_model=LoginResponse)
async def refresh(request: RefreshRequest, service: AuthService = Depends()):
    """Refresh JWT token"""
    token = await service.refresh_token(request.refresh_token)
    return LoginResponse(access_token=token)

@router.post("/logout")
async def logout(service: AuthService = Depends()):
    """Logout user (client-side token cleanup)"""
    return {"message": "logged out"}

@router.get("/me", response_model=UserInfo)
async def get_current_user(current_user = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        tenant_id=current_user.tenant_id,
        roles=current_user.roles
    )
```

#### Tenant Management (src/api/v1/tenants.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from src.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from src.services.tenant_service import TenantService
from src.dependencies.auth import get_current_user

router = APIRouter(tags=["tenants"])

@router.post("", response_model=TenantResponse)
async def create_tenant(
    request: TenantCreate,
    service: TenantService = Depends(),
    current_user = Depends(get_current_user)
):
    """Create new tenant (admin only)"""
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    tenant = await service.create_tenant(
        name=request.name,
        slug=request.slug,
        created_by=current_user.id
    )
    return TenantResponse.from_orm(tenant)

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    service: TenantService = Depends(),
    current_user = Depends(get_current_user)
):
    """Get tenant details (tenant member only)"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    tenant = await service.get_tenant(tenant_id)
    return TenantResponse.from_orm(tenant)

@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdate,
    service: TenantService = Depends(),
    current_user = Depends(get_current_user)
):
    """Update tenant (tenant admin only)"""
    if current_user.tenant_id != tenant_id or "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin role required")

    tenant = await service.update_tenant(
        tenant_id=tenant_id,
        **request.dict(exclude_unset=True),
        updated_by=current_user.id
    )
    return TenantResponse.from_orm(tenant)
```

---

## Phase 5: Testing

### Task: Implement Unit & Integration Tests

**Test Structure**:
```
tests/
├── conftest.py                    # Shared pytest fixtures
├── fixtures/
│   ├── keycloak.py               # Keycloak mock
│   ├── database.py               # Test database setup
│   ├── tenant.py                 # Tenant test fixtures
│   └── user.py                   # User test fixtures
├── unit/
│   ├── test_auth_service.py
│   ├── test_tenant_service.py
│   └── test_models.py
├── integration/
│   ├── test_auth_endpoints.py
│   ├── test_tenant_endpoints.py
│   └── test_tenant_scoping.py
└── e2e/
    └── test_tenant_onboarding_flow.py
```

**Key Tests**:

```python
# tests/integration/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def keycloak_token(mocker):
    # Mock Keycloak token response
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

def test_login_success(client, keycloak_token, mocker):
    """Test successful login"""
    mocker.patch("src.services.auth_service.get_keycloak_token", return_value=keycloak_token)

    response = client.post("/api/v1/auth/login", json={
        "username": "user@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_tenant_isolation(client, keycloak_token):
    """Test that users cannot access other tenant data"""
    # User from tenant-A tries to access tenant-B
    response = client.get(
        "/api/v1/tenants/tenant-b",
        headers={"Authorization": f"Bearer {keycloak_token}"}
    )

    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

# tests/unit/test_models.py
def test_tenant_creation():
    """Test Tenant model"""
    tenant = Tenant(
        name="ACME Corp",
        slug="acme-corp",
        created_by="admin-user-id"
    )

    assert tenant.name == "ACME Corp"
    assert tenant.slug == "acme-corp"
    assert tenant.status == "active"

# tests/e2e/test_tenant_onboarding_flow.py
def test_complete_tenant_onboarding_flow(client, keycloak_token):
    """Test complete flow: create tenant → create user → login → access tenant"""

    # Step 1: Create tenant
    response = client.post(
        "/api/v1/tenants",
        json={"name": "Test Corp", "slug": "test-corp"},
        headers={"Authorization": f"Bearer {keycloak_token}"}
    )
    assert response.status_code == 201
    tenant_id = response.json()["id"]

    # Step 2: Get tenant (verify creation)
    response = client.get(
        f"/api/v1/tenants/{tenant_id}",
        headers={"Authorization": f"Bearer {keycloak_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == tenant_id
```

**Coverage Target**: >85% line coverage

---

## Phase 6: API Documentation

### Task: Create OpenAPI Specification

**File**: backend/openapi.json (auto-generated from FastAPI)

**Manual Additions** (in docstrings):

```python
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    request: TenantCreate,
    service: TenantService = Depends()
):
    """
    Create a new tenant

    - **name**: Tenant display name (required)
    - **slug**: URL-friendly identifier (required, unique)

    Returns: Created tenant with auto-generated ID

    Permissions: Admin role required
    """
    ...
```

**API Spec Documentation**:
```
POST   /api/v1/auth/login              → Login with credentials
POST   /api/v1/auth/refresh            → Refresh access token
POST   /api/v1/auth/logout             → Logout (clear client token)
GET    /api/v1/auth/me                 → Get current user info
POST   /api/v1/tenants                 → Create tenant (admin)
GET    /api/v1/tenants/{tenant_id}     → Get tenant details
PATCH  /api/v1/tenants/{tenant_id}     → Update tenant settings
GET    /health                         → System health check
```

---

## Phase 7: CI/CD Pipeline

### Task: GitHub Actions Workflow

**File**: .github/workflows/ci.yml

```yaml
name: Continuous Integration

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run linting (Black)
        run: cd backend && black --check src tests

      - name: Run type checking (MyPy)
        run: cd backend && mypy src

      - name: Run tests
        run: cd backend && pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Run linting
        run: cd frontend && npm run lint

      - name: Run tests
        run: cd frontend && npm test -- --coverage
```

---

## Phase 8: Documentation & Completion

### Task: Create Completion Report

**File**: docs/implementation/sprint-1-completion-report.md

Template structure:
- [x] All scope delivered
- [x] Files added/changed (with paths)
- [x] Migrations applied
- [x] API endpoints working
- [x] Tests passing (>85% coverage)
- [x] Linting/TypeChecking passed
- [x] Known gaps documented
- [x] Verification steps completed
- [x] Screenshots included (API docs, health check)
- [x] Rollback plan documented
- [x] Deployment checklist

---

## Deliverables Checklist

### Week 1
- [ ] Alembic migration created (001_initial_schema.py)
- [ ] Migration tested (forward + rollback)
- [ ] FastAPI project structure created
- [ ] main.py with app initialization
- [ ] requirements.txt with dependencies
- [ ] Keycloak realm/client configured

### Week 2
- [ ] Auth service implemented (Keycloak integration)
- [ ] JWT middleware working
- [ ] Tenant service implemented
- [ ] API endpoints functional
- [ ] Pydantic models/schemas created
- [ ] Error handling configured

### Week 3
- [ ] Unit tests written (>85% coverage)
- [ ] Integration tests passing
- [ ] E2E flow tested
- [ ] GitHub Actions CI/CD working
- [ ] OpenAPI docs auto-generated
- [ ] Completion report signed off
- [ ] All documentation updated

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Auth endpoints functional | 100% | ⬜ |
| Tenant CRUD working | 100% | ⬜ |
| Tenant scoping enforced | 100% | ⬜ |
| Test coverage | >85% | ⬜ |
| Linting passed | 100% | ⬜ |
| Type checking passed | 100% | ⬜ |
| Integration tests passing | 100% | ⬜ |
| Audit logging working | 100% | ⬜ |
| Migration reversible | 100% | ⬜ |
| Documentation complete | 100% | ⬜ |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Keycloak setup delays | High | Pre-configure realm in docker-compose |
| JWT validation complexity | Medium | Use python-jose library, test thoroughly |
| Tenant isolation bugs | Critical | Add tenant scoping tests, code review |
| Database schema issues | Medium | Test migration reversibility, use constraints |
| API contract breaking | Medium | Freeze OpenAPI spec early, test compatibility |

---

## Next Steps (Sprint 2)

Sprint 2 will build on Sprint 1 foundation:
- Facility hierarchy (sites, buildings, zones, racks)
- Asset registry (devices, meters, equipment)
- Additional database migrations
- API endpoints for hierarchy management
- Tests for hierarchy operations

---

**Plan Status**: ✅ **READY FOR SPRINT 1 KICKOFF**

**Next Action**: Begin implementation on March 9, 2026
**Daily Standup**: 9:00 AM
**Weekly Review**: Friday, 2:00 PM
**Target Completion**: March 29, 2026

---

*This plan is a living document. Updates will be made as work progresses and issues are discovered. All changes will be documented in the completion report.*
