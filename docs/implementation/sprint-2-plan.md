# Sprint 2: Organization & Facility Hierarchy

**Sprint**: 2
**Duration**: March 30 - April 12, 2026 (2 weeks)
**Module**: Organization & Facility Management
**Owner**: Backend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Sprint 2 builds the facility hierarchy system that allows organizations to model their data center structure. This includes creating and managing:
- Organization settings and configurations
- Multi-level facility hierarchy (Site → Building → Zone → Rack)
- Asset location and mapping
- Hierarchy queries and tree traversal

**Dependency**: Auth & Tenant module (Sprint 1) ✅ Complete

---

## Scope & Deliverables

### Phase 1: Organization Module
- [x] Organization CRUD operations
- [x] Organization settings (timezone, reporting units, boundaries)
- [x] Reporting scope configuration
- [x] Organization API endpoints
- [x] Organization service layer

### Phase 2: Facility Hierarchy
- [x] Site/Building/Zone/Rack entities
- [x] Hierarchy validation (circular dependency prevention)
- [x] Tree traversal and queries
- [x] Bulk hierarchy creation
- [x] Asset location mapping

### Phase 3: Database Migrations
- [x] Organization table
- [x] Site/Building/Zone/Rack tables
- [x] Hierarchy constraints and indexes
- [x] Migration rollback tests

### Phase 4: API Endpoints
- [x] Organization endpoints (CRUD)
- [x] Facility hierarchy endpoints
- [x] Bulk operations
- [x] Query/search endpoints

### Phase 5: Testing
- [x] Unit tests (>85% coverage)
- [x] Integration tests (hierarchy operations)
- [x] E2E tests (create and navigate hierarchy)

### Phase 6: Frontend (Basic)
- [x] Organization settings page
- [x] Facility tree view component
- [x] Create/edit dialogs

---

## Database Schema Changes

### New Tables

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    reporting_units VARCHAR(20) DEFAULT 'metric',
    reporting_boundaries JSONB,
    configuration JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, name),
    INDEX(tenant_id, status)
);

-- Sites (Top-level facilities)
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(organization_id, status)
);

-- Buildings
CREATE TABLE buildings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(id),
    name VARCHAR(255) NOT NULL,
    building_code VARCHAR(100),
    square_meters DECIMAL(12, 2),
    floor_count INTEGER,
    construction_year INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(site_id, status)
);

-- Zones/Floors
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    building_id UUID NOT NULL REFERENCES buildings(id),
    name VARCHAR(255) NOT NULL,
    zone_type VARCHAR(50), -- 'floor', 'area', 'section'
    floor_number INTEGER,
    square_meters DECIMAL(12, 2),
    cooling_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(building_id, status)
);

-- Racks/Cabinets
CREATE TABLE racks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID NOT NULL REFERENCES zones(id),
    rack_id VARCHAR(100) NOT NULL,
    rack_type VARCHAR(50), -- '42U', '48U', custom
    u_count INTEGER DEFAULT 42,
    power_capacity_kw DECIMAL(8, 2),
    cooling_capacity_kw DECIMAL(8, 2),
    row_position VARCHAR(50),
    column_position VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    UNIQUE(zone_id, rack_id),
    INDEX(zone_id, status)
);

-- Create indexes for hierarchy traversal
CREATE INDEX organizations_tenant_id ON organizations(tenant_id);
CREATE INDEX sites_organization_id ON sites(organization_id);
CREATE INDEX buildings_site_id ON buildings(site_id);
CREATE INDEX zones_building_id ON zones(building_id);
CREATE INDEX racks_zone_id ON racks(zone_id);
```

---

## API Endpoints

### Organization Endpoints
```
POST   /api/v1/tenants/{tenant_id}/organizations
       Create organization
       Request: {name, timezone, reporting_units, description}
       Response: {id, tenant_id, name, ...}

GET    /api/v1/tenants/{tenant_id}/organizations
       List organizations
       Query: ?limit=10&offset=0&status=active
       Response: {items: [...], total_count: N}

GET    /api/v1/organizations/{org_id}
       Get organization details
       Response: {id, tenant_id, name, settings, ...}

PATCH  /api/v1/organizations/{org_id}
       Update organization
       Request: {name, timezone, settings}
       Response: {id, updated_at, ...}

DELETE /api/v1/organizations/{org_id}
       Soft delete organization
       Response: {id, status: 'deleted'}
```

### Facility Hierarchy Endpoints
```
POST   /api/v1/organizations/{org_id}/sites
       Create site
       Request: {name, location, latitude, longitude}
       Response: {id, organization_id, ...}

GET    /api/v1/organizations/{org_id}/hierarchy
       Get full facility tree
       Query: ?expand=all
       Response: Tree structure with all descendants

POST   /api/v1/organizations/{org_id}/sites/{site_id}/buildings
       Create building
       Request: {name, square_meters, floor_count}
       Response: {id, site_id, ...}

GET    /api/v1/sites/{site_id}/hierarchy
       Get site hierarchy
       Response: Nested building → zone → rack tree

POST   /api/v1/buildings/{building_id}/zones
       Create zone
       Request: {name, zone_type, floor_number}
       Response: {id, building_id, ...}

POST   /api/v1/zones/{zone_id}/racks
       Create rack
       Request: {rack_id, rack_type, u_count, power_capacity_kw}
       Response: {id, zone_id, ...}

GET    /api/v1/organizations/{org_id}/hierarchy/search
       Search hierarchy
       Query: ?query=rack-5&type=rack
       Response: [matched items]
```

---

## Data Models & Schemas

### Organization Schema (Pydantic)
```python
class OrganizationCreate(BaseModel):
    name: str
    timezone: str = "UTC"
    reporting_units: str = "metric"
    description: Optional[str] = None
    reporting_boundaries: Optional[dict] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    settings: Optional[dict] = None

class OrganizationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
```

### Facility Hierarchy Schemas
```python
class RackSchema(BaseModel):
    id: UUID
    zone_id: UUID
    rack_id: str
    u_count: int
    power_capacity_kw: float
    status: str

class ZoneSchema(BaseModel):
    id: UUID
    building_id: UUID
    name: str
    zone_type: str
    racks: List[RackSchema] = []

class BuildingSchema(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    zones: List[ZoneSchema] = []

class SiteSchema(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    location: str
    buildings: List[BuildingSchema] = []

class HierarchyResponseSchema(BaseModel):
    organization: dict
    sites: List[SiteSchema]
```

---

## Backend Implementation

### Project Structure
```
src/
├── domain/
│   ├── organizations/
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── service.py          # Business logic
│   │   └── repository.py       # Data access
│   └── facilities/
│       ├── models.py
│       ├── schemas.py
│       ├── service.py          # Hierarchy logic
│       └── repository.py
├── api/
│   └── v1/
│       ├── organizations.py    # Organization endpoints
│       └── facilities.py       # Facility endpoints
└── migrations/
    └── 002_add_organizations.py
```

### Service Layer Example
```python
# src/domain/organizations/service.py
class OrganizationService:
    def create_organization(
        self, tenant_id: UUID, data: OrganizationCreate
    ) -> Organization:
        org = Organization(
            tenant_id=tenant_id,
            name=data.name,
            timezone=data.timezone,
            created_by=current_user.email
        )
        db.add(org)
        db.commit()
        return org

class FacilityService:
    def get_hierarchy(self, org_id: UUID) -> dict:
        """Get complete facility tree for organization"""
        org = Organization.query.get(org_id)
        return self._build_tree(org)

    def validate_hierarchy(self, org_id: UUID) -> list:
        """Validate no circular dependencies"""
        # Check all paths
        return self._detect_cycles()
```

---

## Frontend Implementation

### Components to Create
```
src/domains/organizations/
├── pages/
│   ├── OrganizationSettings.tsx
│   ├── FacilityHierarchy.tsx
│   └── CreateHierarchy.tsx
├── components/
│   ├── OrganizationForm.tsx
│   ├── FacilityTree.tsx
│   ├── HierarchyNode.tsx
│   ├── SiteForm.tsx
│   ├── BuildingForm.tsx
│   ├── ZoneForm.tsx
│   └── RackForm.tsx
└── hooks/
    ├── useOrganization.ts
    ├── useHierarchy.ts
    └── useFacilityTree.ts
```

### Key UI Features
- Collapsible tree view of hierarchy
- Drag-drop to reorganize (future)
- Inline editing for facility properties
- Bulk import from CSV
- Visual map with coordinates
- Filtering and search

---

## Testing Plan

### Unit Tests
```python
# tests/unit/test_organization_service.py
def test_create_organization():
    service = OrganizationService()
    org = service.create_organization(tenant_id, OrganizationCreate(...))
    assert org.name == "Test Org"
    assert org.tenant_id == tenant_id

def test_get_hierarchy():
    service = FacilityService()
    hierarchy = service.get_hierarchy(org_id)
    assert hierarchy['organization'] is not None
    assert len(hierarchy['sites']) > 0

def test_validate_hierarchy_no_cycles():
    service = FacilityService()
    errors = service.validate_hierarchy(org_id)
    assert len(errors) == 0
```

### Integration Tests
```python
# tests/integration/test_hierarchy_operations.py
def test_create_full_hierarchy(client, tenant_token):
    # Create site
    site_resp = client.post(
        f"/api/v1/organizations/{org_id}/sites",
        json={"name": "DC-1", "location": "US-East"},
        headers={"Authorization": f"Bearer {tenant_token}"}
    )
    assert site_resp.status_code == 201
    site_id = site_resp.json()["id"]

    # Create building
    building_resp = client.post(
        f"/api/v1/sites/{site_id}/buildings",
        json={"name": "Building A"}
    )
    assert building_resp.status_code == 201
    # ... continue with zones and racks

def test_hierarchy_tenant_isolation(client, tenant1_token, tenant2_token):
    # Tenant 1 should not see Tenant 2's hierarchy
    org1_id = create_org(tenant1_token)
    org2_id = create_org(tenant2_token)

    resp = client.get(
        f"/api/v1/organizations/{org2_id}/hierarchy",
        headers={"Authorization": f"Bearer {tenant1_token}"}
    )
    assert resp.status_code == 403
```

### E2E Tests
```python
def test_facility_hierarchy_journey(browser):
    # Login
    browser.visit("/login")
    # ... auth flow

    # Navigate to facilities
    browser.visit("/organizations/facilities")

    # Create site
    browser.click(".btn-create-site")
    # ... fill form
    browser.find_element(".rack-tree")  # Verify hierarchy visible
```

---

## Success Criteria

✅ **Database**
- [x] All 5 tables created with constraints
- [x] Indexes created for common queries
- [x] Foreign key relationships enforced
- [x] Migrations reversible

✅ **API**
- [x] All 7 endpoint groups implemented
- [x] Tenant scoping enforced
- [x] Error handling consistent
- [x] OpenAPI spec updated

✅ **Backend Logic**
- [x] Organization CRUD working
- [x] Hierarchy tree operations working
- [x] Validation (no circular deps) working
- [x] Bulk create operations working

✅ **Frontend**
- [x] Organization settings form working
- [x] Facility tree view rendering correctly
- [x] Create/edit dialogs functional
- [x] Responsive design verified

✅ **Tests**
- [x] >85% unit test coverage
- [x] Integration tests for hierarchy operations
- [x] E2E journey for facility creation
- [x] Tenant isolation verified

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Circular dependency in hierarchy | Medium | Validation algorithm + tests |
| Large hierarchy performance | Medium | Lazy loading + pagination |
| Complex tree traversal | Low | Use proven library (sqlalchemy-hierarchy) |
| Bulk import errors | Low | Validation + rollback on error |

---

## Dependencies

**Blocks**:
- Sprint 3 (Asset Registry) - needs facility hierarchy IDs
- Sprint 4 (Telemetry) - needs rack/building IDs for meter locations

**Blocked By**:
- Sprint 1 (Auth & Tenant) ✅

---

## Deliverables Checklist

- [ ] Database migrations (002_add_organizations.py)
- [ ] SQLAlchemy models (5 tables)
- [ ] Pydantic schemas (request/response)
- [ ] Organization service layer
- [ ] Facility service layer (tree operations)
- [ ] 7 API endpoint groups
- [ ] Organization settings page
- [ ] Facility tree component
- [ ] Unit tests (>85% coverage)
- [ ] Integration tests (critical paths)
- [ ] E2E tests (facility creation journey)
- [ ] Completion report

---

## Completion Report Template

```markdown
# Sprint 2 Completion Report

## Scope Delivered
- [x] Organization CRUD
- [x] Facility hierarchy (Site → Building → Zone → Rack)
- [x] Tree operations and queries
- [x] Tenant isolation verified
- [x] API endpoints
- [x] Frontend pages

## Files Changed
- backend/src/domain/organizations/
- backend/src/domain/facilities/
- backend/src/api/v1/organizations.py
- backend/src/api/v1/facilities.py
- frontend/src/domains/organizations/
- database/migrations/002_add_organizations.py

## Tests
- Backend unit: 28 tests, 89% coverage
- Integration: 12 tests (hierarchy operations)
- E2E: Journey 2-4 passing
- All CI checks passed

## Known Gaps
- Visualization map (Phase 2)
- Bulk import from DCIM systems (Phase 3)
- Capacity planning views (Phase 4)

## Verification
- [x] Hierarchy CRUD operations tested
- [x] Tenant isolation verified
- [x] Tree traversal performance OK
- [x] Screenshots attached
- [x] No data loss on rollback
```

---

**Status**: 📋 PLANNED | **Target**: March 30 - April 12, 2026 | **Owner**: Backend Team
