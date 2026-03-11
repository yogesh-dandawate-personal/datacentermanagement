# ESG Hierarchies - Multiple Frameworks Support

**Purpose**: Support different organizational structures across ESG domains
**Status**: Design Document (Pre-Implementation)
**Date**: 2026-03-11

---

## Overview

Different organizations structure their ESG data capture hierarchies based on:
- Industry (IT, Energy, Manufacturing, Finance, etc.)
- Geography
- Regulatory requirements
- Internal governance structure

iNetZero should support **multiple hierarchy patterns** to accommodate diverse customers.

---

## Proposed Hierarchy Patterns

### Pattern 1: IT/Data Center Focus (Current Requirement)
```
Organization
  ↓
Region (geographic)
  ↓
Campus (multi-building complex)
  ↓
DataCenter (facility)
  ↓
Building (within datacenter)
  ↓
Floor (within building)
  ↓
Room (server rooms, network rooms)
  ↓
Rack (equipment container)
  ↓
Device (servers, switches, UPS, etc.)
```

**Use Case**: Cloud providers, hosting companies, IT service providers
**Example**: AWS, Azure, Google Cloud, Equinix, Digital Realty

---

### Pattern 2: Corporate/Multi-Site (Alternative)
```
Organization
  ↓
Division (business unit)
  ↓
Region (geographic)
  ↓
Site/Facility (location - office, plant, warehouse)
  ↓
Department (functional area)
  ↓
Equipment (machinery, vehicles, HVAC systems)
```

**Use Case**: Manufacturing, Retail, Finance, Energy companies
**Example**: Walmart, Toyota, Microsoft Corporate, GE

---

### Pattern 3: Energy Utility (Specialized)
```
Organization
  ↓
Region (service territory)
  ↓
Generation Unit (power plant, renewable site)
  ↓
Facility Type (generation, transmission, distribution)
  ↓
Asset (transformer, turbine, inverter)
```

**Use Case**: Utilities, Energy companies
**Example**: Duke Energy, NextEra Energy, Vestas Wind

---

### Pattern 4: Real Estate/Property (Alternative)
```
Organization
  ↓
Portfolio (property portfolio)
  ↓
Property (building/complex)
  ↓
Building (physical structure)
  ↓
Floor (level)
  ↓
Zone/Space (room, office, suite)
  ↓
Equipment (HVAC, lighting, etc.)
```

**Use Case**: Real estate firms, property managers, hotel chains
**Example**: CBRE, JLL, Marriott, Hilton

---

### Pattern 5: Supply Chain/Logistics (Specialized)
```
Organization
  ↓
Region
  ↓
Warehouse/Distribution Center
  ↓
Section (warehouse section)
  ↓
Equipment (forklifts, conveyor, cold storage)
```

**Use Case**: Logistics, E-commerce, Distribution
**Example**: Amazon, DHL, Target Supply Chain

---

## Generic Hierarchy Framework

Instead of hardcoding each pattern, implement a **generic hierarchical data model**:

### Core Concept: "HierarchyLevel"

```python
class HierarchyLevel(Base):
    """Define levels in the organizational hierarchy"""
    __tablename__ = "hierarchy_levels"

    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"))

    level_number = Column(Integer)  # 1, 2, 3, etc.
    level_name = Column(String(100))  # "Region", "Campus", "DataCenter", "Division"
    level_display_name = Column(String(100))  # "Geographic Region", "Company Division"
    description = Column(Text)

    # Data model configuration
    supports_multiple_children = Column(Boolean, default=True)
    allows_peers = Column(Boolean, default=True)
    data_collection_required = Column(Boolean, default=False)

    # Custom properties for this level
    custom_properties = Column(JSON, default=dict)  # {location, timezone, budget, etc.}

    is_active = Column(Boolean, default=True)

    # Relationships
    tenant = relationship("Tenant")
    parent_level = relationship("HierarchyLevel", remote_side=[id])  # Level above


class HierarchyEntity(Base):
    """Generic entity in any hierarchy level"""
    __tablename__ = "hierarchy_entities"

    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id", ondelete="CASCADE"))
    hierarchy_level_id = Column(UUID, ForeignKey("hierarchy_levels.id"))
    parent_id = Column(UUID, ForeignKey("hierarchy_entities.id"), nullable=True)

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    # Polymorphic type
    entity_type = Column(String(50))  # "region", "campus", "datacenter", "building", etc.

    # Custom properties for this entity
    properties = Column(JSON, default=dict)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    hierarchy_level = relationship("HierarchyLevel")
    parent = relationship("HierarchyEntity", remote_side=[parent_id])
    children = relationship("HierarchyEntity", foreign_keys=[parent_id])

    # Enable data collection at this level
    metrics = relationship("HierarchyMetric", back_populates="entity", cascade="all")
    emissions = relationship("EmissionsCalculation", back_populates="hierarchy_entity", cascade="all")
```

### Benefits

✅ **Flexible**: Support any hierarchy pattern
✅ **Configurable**: Each tenant defines their own hierarchy
✅ **Scalable**: Works for 3-level or 10-level hierarchies
✅ **Extensible**: Custom properties per level/entity
✅ **Future-proof**: New patterns don't require code changes

---

## Implementation Options

### Option A: Generic Framework (Recommended Long-term)
Implement `HierarchyLevel` + `HierarchyEntity` + configuration UI

**Pros**:
- Support any hierarchy pattern
- Tenant self-service hierarchy configuration
- Maximum flexibility

**Cons**:
- More complex to implement
- Query performance trickier (recursive CTEs)
- Requires admin UI for configuration

**Timeline**: 3-4 weeks (requires significant R&D)

---

### Option B: Multi-Pattern Support (Pragmatic)
Define 5 standard patterns, tenant selects one during onboarding

```python
class OrganizationHierarchyTemplate(Enum):
    """Predefined hierarchy patterns"""
    IT_DATACENTER = "it_datacenter"  # Region → Campus → DC → Building → Floor → Room → Rack
    CORPORATE = "corporate"  # Division → Region → Site → Department → Equipment
    ENERGY_UTILITY = "energy_utility"  # Region → Unit → Facility → Asset
    REAL_ESTATE = "real_estate"  # Portfolio → Property → Building → Floor → Zone → Equipment
    SUPPLY_CHAIN = "supply_chain"  # Region → Warehouse → Section → Equipment
    CUSTOM = "custom"  # User-defined (requires API calls)
```

**Pros**:
- Fast to implement (1-2 weeks)
- Covers 80% of use cases
- Clear, predictable data model

**Cons**:
- Less flexible
- Custom patterns require API work
- May not fit unique customer needs

**Timeline**: 1-2 weeks

---

### Option C: Hybrid Approach (Best Balance)
Start with **Pattern 1** (IT/DataCenter) for Sprint 15, then:
- Sprint 16: Add `HierarchyLevel` configuration
- Sprint 17: Add other predefined patterns
- Later: Build generic `HierarchyEntity` system

**Pros**:
- MVP gets Pattern 1 (immediate requirement)
- Extensible for future patterns
- Low initial investment

**Cons**:
- Phased approach, not all-at-once

**Timeline**: 2-3 weeks over multiple sprints

---

## Recommendation

**Implement Option C (Hybrid) with this phasing**:

### Sprint 15 (Current Priority)
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

### Sprint 16 (Add Flexibility)
- Add `HierarchyLevel` configuration table
- Allow tenants to customize level names
- Support different level orderings

### Sprint 17 (Add Patterns)
- Add support for Pattern 2-5
- Tenant selects pattern during onboarding
- Auto-generate appropriate hierarchy

### Future
- Full generic `HierarchyEntity` system
- Tenant creates completely custom hierarchies
- Dynamic hierarchy management UI

---

## Configuration Examples

### Pattern 1 Config (IT/DataCenter)
```json
{
  "pattern": "it_datacenter",
  "levels": [
    {"level": 1, "name": "Region", "plural": "Regions"},
    {"level": 2, "name": "Campus", "plural": "Campuses"},
    {"level": 3, "name": "DataCenter", "plural": "DataCenters"},
    {"level": 4, "name": "Building", "plural": "Buildings"},
    {"level": 5, "name": "Floor", "plural": "Floors"},
    {"level": 6, "name": "Room", "plural": "Rooms"},
    {"level": 7, "name": "Rack", "plural": "Racks"},
    {"level": 8, "name": "Device", "plural": "Devices"}
  ],
  "data_collection_points": [3, 6, 8],  // DataCenter, Room, Device
  "geographical_levels": [1, 2],  // Region, Campus
  "default_timezone": "UTC"
}
```

### Pattern 2 Config (Corporate)
```json
{
  "pattern": "corporate",
  "levels": [
    {"level": 1, "name": "Division", "plural": "Divisions"},
    {"level": 2, "name": "Region", "plural": "Regions"},
    {"level": 3, "name": "Site", "plural": "Sites"},
    {"level": 4, "name": "Department", "plural": "Departments"},
    {"level": 5, "name": "Equipment", "plural": "Equipment"}
  ],
  "data_collection_points": [3, 5],  // Site, Equipment
  "geographical_levels": [2],  // Region
  "functional_levels": [1, 4]  // Division, Department
}
```

---

## Database Queries with Generic Hierarchy

### Example: Get all equipment under a Region
```sql
-- With Pattern 1
SELECT d.* FROM devices d
JOIN racks r ON d.rack_id = r.id
JOIN rooms ro ON r.room_id = ro.id
JOIN floors f ON ro.floor_id = f.id
JOIN buildings b ON f.building_id = b.id
JOIN datacenters dc ON b.datacenter_id = dc.id
JOIN campuses c ON dc.campus_id = c.id
JOIN regions rg ON c.region_id = rg.id
WHERE rg.id = ?;

-- With Generic HierarchyEntity (would need recursive CTE)
WITH RECURSIVE hierarchy AS (
  SELECT id, parent_id FROM hierarchy_entities WHERE id = ? AND entity_type = 'region'
  UNION ALL
  SELECT h.id, h.parent_id FROM hierarchy_entities h
  JOIN hierarchy ON h.parent_id = hierarchy.id
)
SELECT * FROM devices d
WHERE d.hierarchy_entity_id IN (SELECT id FROM hierarchy WHERE entity_type = 'device');
```

---

## Performance Considerations

### Pattern-Specific Models (Pattern 1, 2, etc.)
- ✅ Fast queries (direct JOINs)
- ✅ Simple indexes
- ❌ Schema changes needed for new patterns
- ❌ Code changes for each pattern

### Generic HierarchyEntity Model
- ⚠️ Slower queries (recursive CTEs)
- ⚠️ Complex indexing
- ✅ No schema changes for new patterns
- ✅ Flexible configuration

### Hybrid Approach
- ✅ Fast queries for predefined patterns
- ✅ Extensible for custom patterns
- ✅ Best performance/flexibility tradeoff

---

## Implementation Roadmap

### Sprint 15: Pattern 1 (IT/DataCenter)
```
Effort: 2 weeks
Deliverables:
- Region, Campus, DataCenter models
- Updated Building, Floor relationships
- Rename Zone → Room
- API endpoints for full hierarchy
- Tests
```

### Sprint 16: Hierarchy Configuration
```
Effort: 1 week
Deliverables:
- HierarchyLevel configuration table
- Tenant-defined level names
- Dynamic level properties
- Configuration UI
```

### Sprint 17: Multi-Pattern Support
```
Effort: 1.5 weeks
Deliverables:
- Pattern 2 (Corporate) models & API
- Pattern 3-5 (Optional, depends on customer need)
- Pattern selection during onboarding
- Automated hierarchy creation
```

### Future: Generic Framework
```
Effort: 3+ weeks
Deliverables:
- HierarchyEntity generic model
- Recursive query support
- Custom hierarchy builder
- Full flexibility
```

---

## Recommendation Summary

For iNetZero MVP:
- ✅ **Implement Pattern 1** (IT/DataCenter) - Sprint 15
- ✅ **Prepare for extensibility** - Sprint 16 (HierarchyLevel config)
- ⏸️ **Defer other patterns** - Future sprints (add as customer demand increases)

This provides:
1. Immediate solution for IT/DataCenter companies (primary market)
2. Foundation for future pattern support
3. Clear upgrade path to generic framework
4. Balanced effort/benefit tradeoff

---

## Questions for Product Team

1. **Is Pattern 1 (IT/DataCenter) correct for MVP?**
2. **Will customers need other patterns within 6 months?**
3. **Is tenant-defined customization required?**
4. **Should we allow unlimited custom hierarchies?**
5. **What's the acceptable query performance impact** for deep hierarchies (10+ levels)?

---

## Conclusion

iNetZero can support **multiple ESG hierarchies** through:
- **Short-term**: Implement Pattern 1 + make it extensible
- **Medium-term**: Add support for other patterns
- **Long-term**: Transition to full generic framework

This approach balances **speed-to-market** with **architectural flexibility**.
