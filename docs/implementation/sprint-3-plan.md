# Sprint 3: Asset Registry & Device Management

**Sprint**: 3
**Duration**: April 13 - April 26, 2026 (2 weeks)
**Module**: Asset Registry
**Owner**: Backend Team
**Status**: 📋 PLANNED

---

## Executive Summary

Sprint 3 implements comprehensive asset tracking system for data center devices:
- Device registration and inventory
- Device specifications and metadata
- Meter configuration and location mapping
- Asset lifecycle tracking
- Device specifications and customization

**Dependency**: Facility Hierarchy (Sprint 2) ✅

---

## Scope & Deliverables

### Phase 1: Device Management
- [x] Device CRUD operations
- [x] Device types (server, UPS, PDU, chiller, meter, etc.)
- [x] Serial number tracking
- [x] Inventory management
- [x] Device status tracking

### Phase 2: Meter Configuration
- [x] Meter entity and types
- [x] Meter location mapping
- [x] Meter specifications (accuracy, range)
- [x] Meter-to-facility linkage
- [x] Last reading timestamp tracking

### Phase 3: Device Specifications
- [x] Extensible specifications model
- [x] Power capacity tracking
- [x] Cooling requirements
- [x] Physical dimensions
- [x] Custom attribute support

### Phase 4: Asset Lifecycle
- [x] Installation date tracking
- [x] Maintenance history
- [x] Deprecation scheduling
- [x] End-of-life handling
- [x] Replacement tracking

### Phase 5: API & Frontend
- [x] Device management endpoints
- [x] Meter configuration API
- [x] Asset inventory page
- [x] Device detail pages
- [x] Bulk import support

### Phase 6: Testing
- [x] Unit tests (>85% coverage)
- [x] Integration tests
- [x] Inventory accuracy tests

---

## Database Schema

```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rack_id UUID NOT NULL REFERENCES racks(id),
    device_type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(255) UNIQUE,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    installation_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(rack_id, device_type, status)
);

CREATE TABLE device_specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id),
    spec_key VARCHAR(100) NOT NULL,
    spec_value TEXT NOT NULL,
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(device_id, spec_key),
    INDEX(device_id, spec_key)
);

CREATE TABLE meters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id),
    meter_type VARCHAR(50) NOT NULL,
    utility VARCHAR(50),
    unit_of_measure VARCHAR(20),
    accuracy_percent DECIMAL(5, 2),
    last_reading TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,
    INDEX(device_id, meter_type, status)
);

CREATE TABLE asset_lifecycle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(id),
    event_type VARCHAR(50) NOT NULL,
    event_date DATE NOT NULL,
    event_description TEXT,
    event_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    INDEX(device_id, event_type, event_date)
);
```

---

## API Endpoints

```
POST   /api/v1/organizations/{org_id}/assets
       Create device
       Request: {rack_id, device_type, serial_number, model, ...}

GET    /api/v1/organizations/{org_id}/assets
       List devices
       Query: ?rack_id=uuid&device_type=server&limit=50

GET    /api/v1/assets/{device_id}
       Get device details
       Response: {id, rack_id, type, specs, meters, ...}

PATCH  /api/v1/assets/{device_id}
       Update device
       Request: {model, status, specifications}

POST   /api/v1/assets/{device_id}/specifications
       Add/update specifications
       Request: [{key, value, unit}]

POST   /api/v1/assets/{device_id}/meters
       Configure meter
       Request: {meter_type, utility, accuracy}

GET    /api/v1/organizations/{org_id}/meters
       List all meters
       Response: [meter objects]

POST   /api/v1/organizations/{org_id}/assets/bulk-import
       Bulk import from CSV
       Request: File upload + mapping
```

---

## Testing

- Unit tests for asset CRUD
- Meter configuration tests
- Specification management tests
- Asset lifecycle tracking tests
- Bulk import validation tests
- Data integrity tests (foreign keys)

---

**Target**: April 13 - April 26, 2026 | **Owner**: Backend Team
