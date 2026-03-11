# Data Hierarchy Migration - Action Items

**Priority**: 🔴 HIGH
**Timeline**: Sprint 15-16
**Owner**: Architecture Team
**Affects**: Sprints 24-27 (Rack-level tracking), Regional dashboards

---

## Immediate Actions (This Week)

### 1. Review & Alignment ✅
- [x] Identify hierarchy mismatch (Organization → Region → Campus → DataCenter → Building → Floor → Room → Rack)
- [x] Document current vs. required schema
- [x] Create migration strategy

### 2. Team Communication
- [ ] Notify backend team of upcoming changes
- [ ] Review with product team
- [ ] Confirm regional hierarchy is required for MVP
- [ ] Decide: Option A (minimal) or Option B (full redesign)

### 3. Impact Assessment
- [ ] Audit all code using Facility model
- [ ] Check API endpoints that reference Facility
- [ ] Check tests that use hierarchy
- [ ] Check frontend code using Facility

**Files to Audit**:
```bash
# Find all Facility references
grep -r "Facility\|facility" --include="*.py" --include="*.tsx" backend/ frontend/

# Check specific models
grep -r "class.*Facility\|\.facility" backend/app/models/
grep -r "Facility" backend/app/routes/
grep -r "facility_id" backend/app/services/
```

---

## Sprint 15 Deliverables

### 1. Create New Models (3 days)
- [ ] Create `Region` model with geographic hierarchy
- [ ] Create `Campus` model for campus-level organization
- [ ] Update `Building` model to reference DataCenter (not Facility)
- [ ] Rename/create `Room` model (currently Zone)
- [ ] Update all relationships

**Code Location**: `backend/app/models/hierarchy.py` (new file)

### 2. Alembic Migration (2 days)
- [ ] Create migration `009_add_regional_hierarchy.py`
- [ ] Create Region table
- [ ] Create Campus table
- [ ] Data migration from Facility → DataCenter
- [ ] Rename Zone → Room
- [ ] Update foreign keys
- [ ] Create rollback migration

**File**: `backend/alembic/versions/009_add_regional_hierarchy.py`

### 3. Update API Endpoints (2 days)
- [ ] Update Facility endpoints → DataCenter endpoints
- [ ] Add Region CRUD endpoints
- [ ] Add Campus CRUD endpoints
- [ ] Update Building endpoints (new parent: DataCenter)
- [ ] Update Rack endpoints (parent chain: DataCenter → Building → Floor → Room → Rack)
- [ ] Update responses to include full hierarchy

**Files**:
- `backend/app/routes/hierarchy.py` (new - Region, Campus, DataCenter)
- `backend/app/routes/buildings.py` (update)
- `backend/app/routes/racks.py` (update)

### 4. Update Services (1.5 days)
- [ ] Update FacilityService → DataCenterService
- [ ] Create RegionService
- [ ] Create CampusService
- [ ] Update BuildingService (new parent)
- [ ] Update RackService (new parent chain)

**Files**:
- `backend/app/services/datacenter_service.py` (new)
- `backend/app/services/region_service.py` (new)
- `backend/app/services/campus_service.py` (new)

### 5. Update Tests (1.5 days)
- [ ] Update facility tests → datacenter tests
- [ ] Create region tests
- [ ] Create campus tests
- [ ] Update building hierarchy tests
- [ ] Update rack hierarchy tests

**Files**:
- `backend/tests/unit/test_datacenter_service.py` (new)
- `backend/tests/unit/test_region_service.py` (new)
- `backend/tests/integration/test_hierarchy_api.py` (new)

### 6. Documentation (1 day)
- [ ] Update data model documentation
- [ ] Update API documentation (OpenAPI specs)
- [ ] Update database schema diagram
- [ ] Create migration guide for existing customers

---

## Sprint 16 Deliverables

### 1. Frontend Updates
- [ ] Update Facility pages → DataCenter pages
- [ ] Create Region management UI
- [ ] Create Campus management UI
- [ ] Update navigation hierarchy
- [ ] Update dashboard filters

### 2. Data Migration for Existing Customers
- [ ] Create data transformation job
- [ ] Test with sample customer data
- [ ] Create migration playbook
- [ ] Execute migrations (if applicable)

### 3. Backward Compatibility
- [ ] Keep old "facilities" endpoints as deprecated
- [ ] Add deprecation warnings
- [ ] Document migration path

---

## Testing Checklist

### Unit Tests
- [ ] Region CRUD operations
- [ ] Campus CRUD operations
- [ ] DataCenter CRUD operations
- [ ] Hierarchy path validation
- [ ] Orphan handling (delete Region → delete Campuses → delete DataCenters)

### Integration Tests
- [ ] Create full hierarchy (Region → Campus → DataCenter → Building → Floor → Room → Rack)
- [ ] Query by region with aggregations
- [ ] Permissions work with new hierarchy (scoped by Region/Campus)
- [ ] Emissions calculations roll up by Region
- [ ] Rack-level tracking uses proper hierarchy

### Manual Testing
- [ ] Verify hierarchy visualization in UI
- [ ] Test navigation through levels
- [ ] Test filtering by region/campus
- [ ] Test reporting by region
- [ ] Test multi-tenant isolation

---

## Code Examples

### Current (Before Migration)
```python
# Current API
GET /api/v1/facilities/{facility_id}
├── buildings
│   ├── floors
│   │   ├── zones
│   │   │   ├── racks
│   │   │   │   ├── devices
```

### After Migration
```python
# New API
GET /api/v1/regions/{region_id}
├── campuses
│   ├── datacenters
│   │   ├── buildings
│   │   │   ├── floors
│   │   │   │   ├── rooms
│   │   │   │   │   ├── racks
│   │   │   │   │   │   ├── devices
```

### Usage Examples
```python
# Create hierarchy
region = create_region(
    organization_id=org.id,
    name="US-East",
    timezone="America/New_York"
)

campus = create_campus(
    region_id=region.id,
    name="US-East-1A",
    location="Virginia"
)

datacenter = create_datacenter(
    campus_id=campus.id,
    name="Ashburn Data Center",
    pue_rating=1.5
)

# Query with hierarchy
emissions_by_region = db.query(EmissionsCalculation)\
    .join(Rack).join(Room).join(Floor)\
    .join(Building).join(DataCenter)\
    .join(Campus).join(Region)\
    .filter(Region.id == region_id)\
    .group_by(Region.id)\
    .sum(EmissionsCalculation.total_emissions)
```

---

## Risk Mitigation

### Breaking Changes
- [ ] Create migration guide for API clients
- [ ] Provide deprecation timeline (6 months)
- [ ] Support both old and new endpoints temporarily
- [ ] Document breaking changes in release notes

### Data Integrity
- [ ] Backup database before migration
- [ ] Test migration on staging first
- [ ] Create rollback procedure
- [ ] Validate data after migration

### Performance
- [ ] Add database indexes on hierarchy columns
- [ ] Profile queries before/after migration
- [ ] Create materialized views for regional rollups
- [ ] Test with production-sized dataset

---

## Dependencies

### Blocked By
- Decision on whether regional hierarchy is required for MVP

### Blocks
- 🔴 Sprint 24-27 (Rack-level tracking) - Depends on proper hierarchy
- 🔴 Regional dashboards and reporting
- 🟡 Sprint 15 (User Management) - Can run in parallel but coordinate

### Related
- ✅ Sprint 14 (RBAC) - Independent, already complete
- 🟡 Sprint 10 (Emissions Module) - May need updates for new hierarchy
- 🟡 Reporting & Compliance - Will use new hierarchy for regional reports

---

## Success Criteria

✅ All tests passing (unit + integration)
✅ Performance: Hierarchy queries <200ms for 1000-level deep hierarchies
✅ No data loss during migration
✅ RBAC still works with new scoping (Region/Campus level)
✅ Backward compatibility maintained (if required)
✅ Documentation complete
✅ Code review approved
✅ QA sign-off

---

## Estimate

- **Effort**: 40-50 hours (1.5-2 weeks for 2 engineers)
- **Risk**: Medium (significant schema changes, but low-impact on other systems)
- **Complexity**: High (affects multiple layers, requires migration)

---

## Next Steps

1. **Review** this document with architecture/product team
2. **Decide** whether to implement in Sprint 15 or defer
3. **Notify** all teams working on affected systems
4. **Update** project timeline based on decision
5. **Assign** team members to implementation
