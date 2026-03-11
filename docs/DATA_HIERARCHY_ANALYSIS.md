# Data Hierarchy Analysis & Model Alignment

**Date**: 2026-03-11
**Status**: 🚨 ACTION REQUIRED - Hierarchy Mismatch Identified
**Priority**: HIGH

---

## Issue Summary

The user's specified data capture hierarchy for iNetZero is:

```
Organization
   ↓
Region
   ↓
Campus
   ↓
DataCenter
   ↓
Building
   ↓
Floor
   ↓
Room
   ↓
Rack
   ↓
Device
```

However, the current database schema has:

```
Organization
   ↓
Facility (represents data center/office location)
   ↓
Building
   ↓
Floor
   ↓
Zone (represents individual rooms/areas)
   ↓
Rack
   ↓
Device
```

---

## Root Cause Analysis

### What We Have (Current)
- `Organization` - Parent company/entity
- `Facility` - Generic physical location (data center or office)
- `Building` - Building within facility
- `Floor` - Floor within building
- `Zone` - Room/area within floor (used for cooling zones)
- `Rack` - Rack within zone
- `Device` - Equipment within rack

### What We Need (Required)
- `Organization` - Parent company/entity ✅ (Match)
- `Region` - Geographic region (MISSING)
- `Campus` - Campus within region (MISSING)
- `DataCenter` - Data center within campus (MISSING)
- `Building` - Building within data center ⚠️ (Exists but parent relationship wrong)
- `Floor` - Floor within building ✅ (Match)
- `Room` - Room within floor (Currently called "Zone", should be renamed)
- `Rack` - Rack within room ✅ (Match)
- `Device` - Equipment within rack ✅ (Match)

---

## Impact Assessment

### Current Schema Limitations

1. **No Geographic Hierarchy**
   - Can't organize by regions (US-East, US-West, Europe, APAC, etc.)
   - Can't track multi-campus operations
   - Can't allocate emissions by region

2. **Facility is Too Generic**
   - Conflates office locations with data centers
   - Can't distinguish between different facility types
   - Complicates querying for data center-specific operations

3. **Zone is Confusing**
   - Named for cooling zones, but represents rooms
   - Causes confusion for facility planning

4. **Missing Parent Relationships**
   - Building has parent_id relationship, but to what? (Currently to Facility)
   - Should have proper hierarchy: Region → Campus → DataCenter → Building → Floor → Room

### Implications

This affects:
- **Emissions Allocation**: Can't allocate emissions by region or campus
- **Facility Management**: Can't properly model multi-datacenter enterprises
- **Rack-Level Tracking** (Sprint 24-27): Rack scoping relies on proper hierarchy
- **Tenant Allocation** (Sprint 26): Multi-tenant tracking across regions
- **Reporting**: Regional dashboards, campus summaries

---

## Recommended Solution

### Option A: Minimal Migration (Recommended for Now)

**Keep existing tables, update relationships:**

1. Add `parent_facility_id` to Facility (for hierarchy support)
2. Rename `Zone` → `Room` in data model (name change only)
3. Create views for regional rollups (virtual hierarchy)
4. Map current Facility to "DataCenter" semantically

**Pros**: Minimal breaking changes, can be done incrementally
**Cons**: Doesn't add Region/Campus layers yet

**Timeline**: 1-2 days for renaming + relationship fixes

### Option B: Full Schema Redesign (Better Long-term)

**Create proper hierarchy:**

1. `Region` (new) - Geographic regions
2. `Campus` (new) - Campus within region
3. `DataCenter` - Rename Facility
4. Keep: Building → Floor → Room → Rack → Device

**Pros**: Proper modeling of real-world IT infrastructure
**Cons**: Requires Alembic migration, data transformation

**Timeline**: 1-2 weeks including migration and data transformation

---

## Recommended Action Plan

### Phase 1: Immediate (This Week)
✅ Identify impact on existing code
✅ Create migration strategy
✅ Update documentation
✅ Alert team about upcoming changes

### Phase 2: Short-term (Next Sprint - Sprint 15)
- Create new models: Region, Campus
- Create Alembic migration
- Rename Zone → Room
- Update relationships
- Update all API endpoints
- Update all tests

### Phase 3: Medium-term (Sprints 16-17)
- Update UI to reflect new hierarchy
- Create data transformation job (for existing customers)
- Update onboarding wizard
- Update documentation

---

## Detailed Schema Changes Required

### New Models to Create

```python
class Region(Base):
    """Geographic region (US-East, Europe, APAC, etc.)"""
    __tablename__ = "regions"

    id = Column(UUID, primary_key=True)
    organization_id = Column(UUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)  # "US-East", "Europe", "APAC"
    description = Column(Text)
    location = Column(String(255))  # Geographic identifier
    timezone = Column(String(50))
    latitude = Column(Numeric(11, 8))
    longitude = Column(Numeric(11, 8))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campuses = relationship("Campus", back_populates="region", cascade="all, delete-orphan")


class Campus(Base):
    """Campus within a region (e.g., "US-East-1A", "Dublin-Campus")</
    __tablename__ = "campuses"

    id = Column(UUID, primary_key=True)
    region_id = Column(UUID, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(255))

    total_area = Column(Numeric(12, 2))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    region = relationship("Region", back_populates="campuses")
    datacenters = relationship("DataCenter", back_populates="campus", cascade="all, delete-orphan")


class DataCenter(Base):
    """Data center within a campus (rename from Facility)"""
    __tablename__ = "datacenters"  # Or keep "facilities" with semantic change

    id = Column(UUID, primary_key=True)
    campus_id = Column(UUID, ForeignKey("campuses.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    facility_type = Column(String(100), default="data_center")  # data_center, office, hybrid
    location = Column(String(255))
    timezone = Column(String(50), default="UTC")

    pue_rating = Column(Numeric(5, 2))  # Power Usage Effectiveness
    cooling_type = Column(String(100))  # CRAC, CRAH, immersion, etc.

    total_capacity = Column(Numeric(12, 2))
    available_capacity = Column(Numeric(12, 2))

    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    campus = relationship("Campus", back_populates="datacenters")
    buildings = relationship("Building", back_populates="datacenter", cascade="all, delete-orphan")


# Update existing Building model
class Building(Base):
    """Building within a data center"""
    __tablename__ = "buildings"

    id = Column(UUID, primary_key=True)
    datacenter_id = Column(UUID, ForeignKey("datacenters.id", ondelete="CASCADE"), nullable=False)  # Changed from facility_id
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    building_number = Column(String(50))
    description = Column(Text)

    total_floors = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    datacenter = relationship("DataCenter", back_populates="buildings")  # Changed from facility
    tenant = relationship("Tenant")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")


# Update Zone → Room model
class Room(Base):
    """Room within a floor (formerly Zone)"""
    __tablename__ = "rooms"  # Or add migration from zones

    id = Column(UUID, primary_key=True)
    floor_id = Column(UUID, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    room_number = Column(String(50))
    room_type = Column(String(100))  # server_room, network_room, power_room, cold_aisle, hot_aisle
    description = Column(Text)

    area = Column(Numeric(12, 2))  # Square meters
    temperature_setpoint = Column(Numeric(5, 2))
    humidity_setpoint = Column(Numeric(5, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    floor = relationship("Floor", back_populates="rooms")  # Changed from zones
    tenant = relationship("Tenant")
    racks = relationship("Rack", back_populates="room", cascade="all, delete-orphan")  # Changed from zone
```

---

## Migration Strategy

### Alembic Migration (009_add_regional_hierarchy.py)

1. Create Region table
2. Create Campus table
3. Create DataCenter table (copy from Facility structure)
4. Rename Zone → Room (via alter table)
5. Update foreign keys (Building.facility_id → Building.datacenter_id)
6. Data migration:
   - Create default Region for each tenant
   - Create default Campus for each Region
   - Move Facility → DataCenter
   - Move Zone → Room
7. Create indexes on new columns
8. Add down migration (reversible)

### Backward Compatibility

- Keep "facilities" table name in database (just semantically call it DataCenter)
- Add migration triggers to sync both names
- Update API responses to use new hierarchy names
- Old endpoints still work, new endpoints use full hierarchy

---

## Risk Assessment

### High Risk
- Data transformation for existing customers
- API changes (breaking changes for v1 endpoints)
- Tenant isolation in multi-tenant case

### Medium Risk
- Performance impact on queries with deeper hierarchy
- Caching strategy for hierarchy traversal

### Low Risk
- New model creation
- Migration is reversible

---

## Timeline & Dependencies

### Timeline
- **Week 1**: Finalize design, create detailed migration plan
- **Week 2**: Implement models, create Alembic migration, update tests
- **Week 3**: Update API endpoints, update UI
- **Week 4**: Data transformation for existing customers, documentation

### Dependencies
- ✅ Sprint 14 (RBAC) - No dependencies on hierarchy
- ⚠️ Sprint 15 (User Management UI) - Should wait for hierarchy finalization
- 🔴 Sprint 24-27 (Rack-level tracking) - DEPENDS on proper hierarchy
- 🔴 Multi-region reporting - DEPENDS on Region/Campus models

---

## Recommendation

**Execute Option A (Minimal Migration) immediately**, then plan Option B (Full Redesign) for Sprint 16:

1. **This Week**:
   - Rename Zone → Room conceptually
   - Add documentation clarifying current hierarchy
   - Assess impact on existing code
   - Alert team

2. **Next Sprint (Sprint 15)**:
   - Add Region and Campus models
   - Create migration
   - Update all APIs
   - Update tests

3. **Sprint 16**:
   - Update UI
   - Create data transformation job
   - Updated documentation

---

## Questions for Product Team

1. **Are Region/Campus hierarchy essential for MVP?**
   - If yes: Do Option B immediately (1-2 weeks)
   - If no: Do Option A (minimal changes) first

2. **Do existing customers need data migration?**
   - If yes: Plan data transformation carefully
   - If no: Migration only for new customers

3. **Should we maintain backward compatibility?**
   - If yes: Keep old endpoints, add new ones
   - If no: Breaking change acceptable in v2

---

## Conclusion

The data hierarchy mismatch is **critical for proper data center modeling**. While the current schema works, it doesn't reflect real-world IT infrastructure with multiple regions/campuses.

**Recommended Action**: Implement Option A immediately (minimal, low-risk), then plan Option B for Sprint 16 when team can allocate resources for proper regional hierarchy.

**Impact on Sprint 14**: None (RBAC is independent)
**Impact on Sprint 24-27** (Rack Emissions): High (should use proper hierarchy)
