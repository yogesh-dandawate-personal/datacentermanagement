# Hierarchy Patterns Specification - Sprint 15 Task 15.2

**Status**: ✅ SPECIFICATION COMPLETE
**Created**: 2026-03-11
**Framework**: Generic Hierarchy (GHF) - iNetZero Platform
**Target Sprints**: 15.3-15.8

---

## Executive Summary

This document defines **5 industry-specific hierarchy patterns** that can be instantiated through the iNetZero Generic Hierarchy Framework. Each pattern addresses a unique organizational structure while leveraging the same database schema and service layer.

**Patterns Defined**:
1. **IT/DataCenter Hierarchy** - Technology infrastructure focus
2. **Corporate Hierarchy** - Business organizational structure
3. **Energy Portfolio Hierarchy** - Energy management and operations
4. **Real Estate Hierarchy** - Property and facilities management
5. **Supply Chain Hierarchy** - Vendor and procurement management

---

## Pattern #1: IT/DataCenter Hierarchy

### Overview
Designed for IT organizations managing data centers, colocation facilities, and distributed computing infrastructure.

**Use Cases**:
- Data center operators tracking power, cooling, and emissions per rack
- Cloud providers managing multi-regional infrastructure
- Telecom operators organizing distributed network nodes
- IT companies with multiple campuses and office locations

### Hierarchy Structure

```
Level 1: REGION (Root)
  └─ Level 2: CAMPUS
      └─ Level 3: DATACENTER
          └─ Level 4: BUILDING
              └─ Level 5: FLOOR
                  └─ Level 6: ROOM
                      └─ Level 7: RACK
                          └─ Level 8: DEVICE (Leaf)
```

### Detailed Level Definitions

| Level | Name | Singular | Description | Min Children | Max Children | Key Metadata |
|-------|------|----------|-------------|------------|-------------|--------------|
| 1 | Region | region | Geographic region (US East, EMEA, APAC) | 0 | None | location (lat/lng), timezone, climate_zone |
| 2 | Campus | campus | Physical campus/site within region | 1 | 10 | address, square_footage, power_capacity_kw |
| 3 | DataCenter | datacenter | Data center facility (MD1, DC5) | 0 | 5 | tier_rating (III, IV), sla_uptime, security_classification |
| 4 | Building | building | Physical building (A, B, C) | 0 | 20 | floors, construction_year, hvac_system |
| 5 | Floor | floor | Floor within building (1, 2, 3) | 0 | 100 | elevation, floor_area_sqft, power_distribution |
| 6 | Room | room | Equipment room or cage (A1, A2) | 0 | 50 | room_type (cage, suite, open_floor), access_control |
| 7 | Rack | rack | Physical equipment rack (R001, R002) | 0 | unlimited | rack_height_u, power_capacity_watts, cooling_capacity_kw |
| 8 | Device | device | Individual server/switch/PDU | 0 | unlimited | device_type, cpu_cores, ram_gb, power_consumption_watts |

### JSON Configuration

```json
{
  "pattern_name": "it_datacenter",
  "pattern_type": "system",
  "description": "IT/DataCenter infrastructure hierarchy with 8 levels",
  "levels": [
    {
      "level": 1,
      "name": "Region",
      "singular": "region",
      "min_children": 0,
      "max_children": null,
      "icon_name": "globe",
      "color_code": "#1E40AF",
      "metadata": {
        "fields": ["location", "timezone", "climate_zone"],
        "validations": {
          "timezone": "IANA timezone identifier"
        }
      }
    },
    {
      "level": 2,
      "name": "Campus",
      "singular": "campus",
      "min_children": 1,
      "max_children": 10,
      "icon_name": "building-2",
      "color_code": "#1E3A8A",
      "metadata": {
        "fields": ["address", "square_footage", "power_capacity_kw"],
        "validations": {
          "power_capacity_kw": "positive number",
          "square_footage": "positive number"
        }
      }
    },
    {
      "level": 3,
      "name": "DataCenter",
      "singular": "datacenter",
      "min_children": 0,
      "max_children": 5,
      "icon_name": "server",
      "color_code": "#0F172A",
      "metadata": {
        "fields": ["tier_rating", "sla_uptime", "security_classification"],
        "validations": {
          "tier_rating": ["I", "II", "III", "IV"],
          "sla_uptime": "number (99.0-99.999)",
          "security_classification": ["public", "private", "secret"]
        }
      }
    },
    {
      "level": 4,
      "name": "Building",
      "singular": "building",
      "min_children": 0,
      "max_children": 20,
      "icon_name": "home",
      "color_code": "#3730A3",
      "metadata": {
        "fields": ["floors", "construction_year", "hvac_system"],
        "validations": {
          "construction_year": "year >= 1950",
          "hvac_system": ["chilled_water", "direct_expansion", "in_row"]
        }
      }
    },
    {
      "level": 5,
      "name": "Floor",
      "singular": "floor",
      "min_children": 0,
      "max_children": 100,
      "icon_name": "layers",
      "color_code": "#581C87",
      "metadata": {
        "fields": ["elevation", "floor_area_sqft", "power_distribution"],
        "validations": {
          "floor_area_sqft": "positive number"
        }
      }
    },
    {
      "level": 6,
      "name": "Room",
      "singular": "room",
      "min_children": 0,
      "max_children": 50,
      "icon_name": "box",
      "color_code": "#7C2D12",
      "metadata": {
        "fields": ["room_type", "access_control"],
        "validations": {
          "room_type": ["cage", "suite", "open_floor", "cold_aisle"],
          "access_control": "text (badge reader, biometric, etc.)"
        }
      }
    },
    {
      "level": 7,
      "name": "Rack",
      "singular": "rack",
      "min_children": 0,
      "max_children": null,
      "icon_name": "layers-3",
      "color_code": "#BE7B04",
      "metadata": {
        "fields": ["rack_height_u", "power_capacity_watts", "cooling_capacity_kw"],
        "validations": {
          "rack_height_u": "number (typically 42)",
          "power_capacity_watts": "positive number",
          "cooling_capacity_kw": "positive number"
        }
      }
    },
    {
      "level": 8,
      "name": "Device",
      "singular": "device",
      "min_children": 0,
      "max_children": null,
      "icon_name": "cpu",
      "color_code": "#BE540E",
      "metadata": {
        "fields": ["device_type", "cpu_cores", "ram_gb", "power_consumption_watts"],
        "validations": {
          "device_type": ["server", "switch", "router", "pdu", "ups", "cooling_unit"],
          "cpu_cores": "positive integer",
          "ram_gb": "positive integer",
          "power_consumption_watts": "positive number"
        }
      }
    }
  ]
}
```

### Sample Entity Tree

```
Region: US-EAST (Level 1)
├─ Campus: Northern VA (Level 2)
│  ├─ DataCenter: Ashburn DC1 (Level 3)
│  │  ├─ Building: Building A (Level 4)
│  │  │  ├─ Floor: Floor 2 (Level 5)
│  │  │  │  ├─ Room: Cage A-2-1 (Level 6)
│  │  │  │  │  ├─ Rack: R0201 (Level 7)
│  │  │  │  │  │  ├─ Device: Server-001 (Level 8)
│  │  │  │  │  │  ├─ Device: Server-002 (Level 8)
│  │  │  │  │  │  └─ Device: PDU-A (Level 8)
│  │  │  │  │  └─ Rack: R0202 (Level 7)
│  │  │  │  │     └─ Device: Switch-Core-01 (Level 8)
│  │  ├─ Building: Building B (Level 4)
│  │  │  └─ Floor: Floor 1 (Level 5)
├─ Campus: Dallas (Level 2)
```

### Key Characteristics

- **Depth**: 8 levels from Region to Device
- **Branching Factor**: Moderate (10s-100s per level)
- **Purpose**: Asset tracking, power management, emissions calculation
- **Default Scoping**: Organization → Facility mapping uses regions/campuses
- **Emissions Tracking**: Device and Rack levels track power for Scope 2 calculations

---

## Pattern #2: Corporate Hierarchy

### Overview
Traditional business organizational structure for enterprises with multiple business units, divisions, and teams.

**Use Cases**:
- Large enterprises with complex organizational structure
- Conglomerates with multiple subsidiaries
- Organizations tracking ESG metrics by department
- Companies managing carbon emissions across business units

### Hierarchy Structure

```
Level 1: ORGANIZATION (Root)
  └─ Level 2: DIVISION
      └─ Level 3: DEPARTMENT
          └─ Level 4: TEAM
              └─ Level 5: INDIVIDUAL (Leaf)
```

### Detailed Level Definitions

| Level | Name | Singular | Description | Min Children | Max Children | Key Metadata |
|-------|------|----------|-------------|------------|-------------|--------------|
| 1 | Organization | organization | Parent company/holding (Acme Corp) | 0 | None | industry, employee_count, hq_location |
| 2 | Division | division | Business division (Products, Services) | 0 | 20 | division_head, annual_budget, business_unit_code |
| 3 | Department | department | Functional department (Engineering, Sales) | 1 | 50 | manager, headcount, cost_center, reporting_line |
| 4 | Team | team | Sub-team within department (Backend, Frontend) | 0 | 20 | team_lead, fte_count, monthly_opex |
| 5 | Individual | individual | Employee/contractor | 0 | 10 | employee_id, role, email, salary_band |

### JSON Configuration

```json
{
  "pattern_name": "corporate",
  "pattern_type": "system",
  "description": "Corporate organizational structure with 5 levels",
  "levels": [
    {
      "level": 1,
      "name": "Organization",
      "singular": "organization",
      "min_children": 0,
      "max_children": null,
      "icon_name": "building",
      "color_code": "#1E3A8A",
      "metadata": {
        "fields": ["industry", "employee_count", "hq_location"],
        "validations": {
          "industry": "text (NACE code optional)",
          "employee_count": "positive integer"
        }
      }
    },
    {
      "level": 2,
      "name": "Division",
      "singular": "division",
      "min_children": 0,
      "max_children": 20,
      "icon_name": "sitemap",
      "color_code": "#1E40AF",
      "metadata": {
        "fields": ["division_head", "annual_budget", "business_unit_code"],
        "validations": {
          "annual_budget": "positive number (USD)",
          "business_unit_code": "text (e.g., BU-001)"
        }
      }
    },
    {
      "level": 3,
      "name": "Department",
      "singular": "department",
      "min_children": 1,
      "max_children": 50,
      "icon_name": "users",
      "color_code": "#0F172A",
      "metadata": {
        "fields": ["manager", "headcount", "cost_center", "reporting_line"],
        "validations": {
          "headcount": "positive integer",
          "cost_center": "text (accounting code)"
        }
      }
    },
    {
      "level": 4,
      "name": "Team",
      "singular": "team",
      "min_children": 0,
      "max_children": 20,
      "icon_name": "users-group",
      "color_code": "#3730A3",
      "metadata": {
        "fields": ["team_lead", "fte_count", "monthly_opex"],
        "validations": {
          "fte_count": "positive number (allows fractional FTE)",
          "monthly_opex": "positive number (USD)"
        }
      }
    },
    {
      "level": 5,
      "name": "Individual",
      "singular": "individual",
      "min_children": 0,
      "max_children": 10,
      "icon_name": "user",
      "color_code": "#581C87",
      "metadata": {
        "fields": ["employee_id", "role", "email", "salary_band"],
        "validations": {
          "employee_id": "unique identifier",
          "email": "valid email format",
          "salary_band": "text (A-F scale)"
        }
      }
    }
  ]
}
```

### Sample Entity Tree

```
Organization: Acme Corporation (Level 1)
├─ Division: Products (Level 2)
│  ├─ Department: Engineering (Level 3)
│  │  ├─ Team: Backend (Level 4)
│  │  │  ├─ Individual: Alice Johnson (Level 5)
│  │  │  ├─ Individual: Bob Smith (Level 5)
│  │  │  └─ Individual: Carol White (Level 5)
│  │  ├─ Team: Frontend (Level 4)
│  │  │  ├─ Individual: David Chen (Level 5)
│  │  │  └─ Individual: Eve Martinez (Level 5)
│  ├─ Department: Product Mgmt (Level 3)
│  │  └─ Team: Product (Level 4)
│  │     ├─ Individual: Frank Brown (Level 5)
├─ Division: Services (Level 2)
│  ├─ Department: Sales (Level 3)
│  ├─ Department: Support (Level 3)
```

### Key Characteristics

- **Depth**: 5 levels from Organization to Individual
- **Branching Factor**: Small (5-20 per level)
- **Purpose**: Organizational structure, responsibility tracking, cost allocation
- **Default Scoping**: Organization level maps to iNetZero Tenant
- **ESG Application**: Track emissions by department, team, or business unit

---

## Pattern #3: Energy Portfolio Hierarchy

### Overview
Specialized for energy companies, utilities, and organizations tracking energy generation, distribution, and consumption.

**Use Cases**:
- Electric utilities managing generation plants and substations
- Energy trading companies managing portfolios
- Organizations tracking energy consumption across facilities
- Renewable energy operators managing solar/wind farms

### Hierarchy Structure

```
Level 1: PORTFOLIO (Root)
  └─ Level 2: PLANT
      └─ Level 3: FACILITY
          └─ Level 4: UNIT
              └─ Level 5: EQUIPMENT (Leaf)
```

### Detailed Level Definitions

| Level | Name | Singular | Description | Min Children | Max Children | Key Metadata |
|-------|------|----------|-------------|------------|-------------|--------------|
| 1 | Portfolio | portfolio | Energy portfolio (renewable, conventional) | 0 | None | portfolio_type, total_capacity_mw, target_emissions |
| 2 | Plant | plant | Generation/processing plant | 0 | 50 | location, commissioned_year, fuel_type, capacity_mw |
| 3 | Facility | facility | Sub-facility within plant | 1 | 100 | facility_type, uptime_sla, maintenance_schedule |
| 4 | Unit | unit | Equipment unit (turbine, boiler, transformer) | 0 | 500 | unit_type, manufacturer, model, capacity_mw |
| 5 | Equipment | equipment | Individual component (rotor, blade, sensor) | 0 | unlimited | equipment_type, installation_date, warranty_expiry |

### JSON Configuration

```json
{
  "pattern_name": "energy_portfolio",
  "pattern_type": "system",
  "description": "Energy portfolio hierarchy for generation and distribution",
  "levels": [
    {
      "level": 1,
      "name": "Portfolio",
      "singular": "portfolio",
      "min_children": 0,
      "max_children": null,
      "icon_name": "zap",
      "color_code": "#EAB308",
      "metadata": {
        "fields": ["portfolio_type", "total_capacity_mw", "target_emissions"],
        "validations": {
          "portfolio_type": ["renewable", "conventional", "mixed"],
          "total_capacity_mw": "positive number"
        }
      }
    },
    {
      "level": 2,
      "name": "Plant",
      "singular": "plant",
      "min_children": 0,
      "max_children": 50,
      "icon_name": "factory",
      "color_code": "#DC2626",
      "metadata": {
        "fields": ["location", "commissioned_year", "fuel_type", "capacity_mw"],
        "validations": {
          "fuel_type": ["solar", "wind", "hydro", "nuclear", "coal", "gas", "biomass"],
          "commissioned_year": "year >= 1900"
        }
      }
    },
    {
      "level": 3,
      "name": "Facility",
      "singular": "facility",
      "min_children": 1,
      "max_children": 100,
      "icon_name": "building-2",
      "color_code": "#9CA3AF",
      "metadata": {
        "fields": ["facility_type", "uptime_sla", "maintenance_schedule"],
        "validations": {
          "facility_type": ["generation", "transmission", "distribution", "storage"],
          "uptime_sla": "percentage (99-99.999)"
        }
      }
    },
    {
      "level": 4,
      "name": "Unit",
      "singular": "unit",
      "min_children": 0,
      "max_children": 500,
      "icon_name": "cpu",
      "color_code": "#1F2937",
      "metadata": {
        "fields": ["unit_type", "manufacturer", "model", "capacity_mw"],
        "validations": {
          "unit_type": ["turbine_wind", "turbine_steam", "boiler", "transformer", "inverter"],
          "capacity_mw": "positive number"
        }
      }
    },
    {
      "level": 5,
      "name": "Equipment",
      "singular": "equipment",
      "min_children": 0,
      "max_children": null,
      "icon_name": "tool",
      "color_code": "#6B7280",
      "metadata": {
        "fields": ["equipment_type", "installation_date", "warranty_expiry"],
        "validations": {
          "equipment_type": "text",
          "installation_date": "ISO date",
          "warranty_expiry": "ISO date"
        }
      }
    }
  ]
}
```

### Sample Entity Tree

```
Portfolio: Renewable Energy - 2026 (Level 1)
├─ Plant: Solar Farm - Arizona (Level 2)
│  ├─ Facility: Array A (Level 3)
│  │  ├─ Unit: Inverter A1 (Level 4)
│  │  │  ├─ Equipment: DC Combiner Box (Level 5)
│  │  ├─ Unit: Transformer A2 (Level 4)
│  ├─ Facility: Array B (Level 3)
├─ Plant: Wind Farm - Texas (Level 2)
│  ├─ Facility: North Field (Level 3)
│  │  ├─ Unit: Turbine T-01 (Level 4)
│  │  │  ├─ Equipment: Rotor Blade (Level 5)
│  │  │  ├─ Equipment: Gearbox (Level 5)
│  │  │  └─ Equipment: Generator (Level 5)
│  │  ├─ Unit: Turbine T-02 (Level 4)
```

### Key Characteristics

- **Depth**: 5 levels from Portfolio to Equipment
- **Branching Factor**: High (50-500 per level)
- **Purpose**: Asset management, capacity tracking, maintenance scheduling
- **Default Scoping**: Portfolio maps to Organization-level tracking
- **Emissions Application**: Track generation emissions and carbon intensity by plant

---

## Pattern #4: Real Estate Hierarchy

### Overview
Property and facility management hierarchy for real estate organizations and large enterprises managing multiple buildings.

**Use Cases**:
- Real estate investment trusts (REITs) managing property portfolios
- Multinational enterprises with global office networks
- Property management companies
- Organizations tracking utility usage and emissions across buildings

### Hierarchy Structure

```
Level 1: PORTFOLIO (Root)
  └─ Level 2: REGION
      └─ Level 3: CAMPUS
          └─ Level 4: BUILDING
              └─ Level 5: FLOOR
                  └─ Level 6: SPACE (Leaf)
```

### Detailed Level Definitions

| Level | Name | Singular | Description | Min Children | Max Children | Key Metadata |
|-------|------|----------|-------------|------------|-------------|--------------|
| 1 | Portfolio | portfolio | Property portfolio | 0 | None | property_count, total_sqft, asset_value_usd |
| 2 | Region | region | Geographic region (Americas, EMEA) | 0 | 10 | region_code, headquarters, regional_manager |
| 3 | Campus | campus | Campus/complex (multiple buildings) | 0 | 20 | location, parking_spaces, security_type |
| 4 | Building | building | Individual building | 1 | 100 | building_code, year_built, hvac_system, elevator_count |
| 5 | Floor | floor | Floor within building | 0 | 500 | floor_number, floor_area_sqft, hvac_zones |
| 6 | Space | space | Tenant space or room (office, lab, cafeteria) | 0 | unlimited | space_type, occupant, floor_area_sqft, lease_type |

### JSON Configuration

```json
{
  "pattern_name": "real_estate",
  "pattern_type": "system",
  "description": "Real estate and facilities hierarchy",
  "levels": [
    {
      "level": 1,
      "name": "Portfolio",
      "singular": "portfolio",
      "min_children": 0,
      "max_children": null,
      "icon_name": "home",
      "color_code": "#7C3AED",
      "metadata": {
        "fields": ["property_count", "total_sqft", "asset_value_usd"],
        "validations": {
          "property_count": "positive integer",
          "total_sqft": "positive number",
          "asset_value_usd": "positive number (currency)"
        }
      }
    },
    {
      "level": 2,
      "name": "Region",
      "singular": "region",
      "min_children": 0,
      "max_children": 10,
      "icon_name": "map-pin",
      "color_code": "#5B21B6",
      "metadata": {
        "fields": ["region_code", "headquarters", "regional_manager"],
        "validations": {
          "region_code": "text (e.g., AMER, EMEA, APAC)",
          "headquarters": "city name"
        }
      }
    },
    {
      "level": 3,
      "name": "Campus",
      "singular": "campus",
      "min_children": 0,
      "max_children": 20,
      "icon_name": "building-2",
      "color_code": "#4C1D95",
      "metadata": {
        "fields": ["location", "parking_spaces", "security_type"],
        "validations": {
          "parking_spaces": "positive integer",
          "security_type": ["badge", "guard", "biometric", "none"]
        }
      }
    },
    {
      "level": 4,
      "name": "Building",
      "singular": "building",
      "min_children": 1,
      "max_children": 100,
      "icon_name": "building",
      "color_code": "#6B21A8",
      "metadata": {
        "fields": ["building_code", "year_built", "hvac_system", "elevator_count"],
        "validations": {
          "building_code": "text (e.g., BLD-001)",
          "year_built": "year >= 1800",
          "hvac_system": ["central_chiller", "vrf", "ptac", "rooftop_units"],
          "elevator_count": "non-negative integer"
        }
      }
    },
    {
      "level": 5,
      "name": "Floor",
      "singular": "floor",
      "min_children": 0,
      "max_children": 500,
      "icon_name": "layers",
      "color_code": "#7E22CE",
      "metadata": {
        "fields": ["floor_number", "floor_area_sqft", "hvac_zones"],
        "validations": {
          "floor_number": "integer (can be negative for basement)",
          "floor_area_sqft": "positive number",
          "hvac_zones": "positive integer"
        }
      }
    },
    {
      "level": 6,
      "name": "Space",
      "singular": "space",
      "min_children": 0,
      "max_children": null,
      "icon_name": "square-2-stack",
      "color_code": "#A855F7",
      "metadata": {
        "fields": ["space_type", "occupant", "floor_area_sqft", "lease_type"],
        "validations": {
          "space_type": ["office", "conference", "lab", "cafeteria", "restroom", "lobby", "storage"],
          "floor_area_sqft": "positive number",
          "lease_type": ["leased", "owned", "subleased"]
        }
      }
    }
  ]
}
```

### Sample Entity Tree

```
Portfolio: Global Real Estate (Level 1)
├─ Region: Americas (Level 2)
│  ├─ Campus: San Francisco (Level 3)
│  │  ├─ Building: HQ-1 (Level 4)
│  │  │  ├─ Floor: 1 (Level 5)
│  │  │  │  ├─ Space: Office 1-101 (Level 6)
│  │  │  │  ├─ Space: Conference Room 1-105 (Level 6)
│  │  │  │  └─ Space: Cafeteria 1-110 (Level 6)
│  │  │  ├─ Floor: 2 (Level 5)
│  │  ├─ Building: Office-Annex (Level 4)
│  ├─ Campus: New York (Level 3)
├─ Region: EMEA (Level 2)
│  ├─ Campus: London (Level 3)
│  ├─ Campus: Frankfurt (Level 3)
```

### Key Characteristics

- **Depth**: 6 levels from Portfolio to Space
- **Branching Factor**: Moderate (10-500 per level)
- **Purpose**: Facility management, tenant tracking, utility metering
- **Default Scoping**: Campus or Building maps to iNetZero Facility
- **Emissions Application**: Track electricity, water, and gas usage by building/floor/space

---

## Pattern #5: Supply Chain Hierarchy

### Overview
Vendor and procurement management hierarchy for organizations tracking supplier relationships and supply chain emissions.

**Use Cases**:
- Global enterprises managing thousands of suppliers
- Organizations calculating Scope 3 supply chain emissions
- Procurement departments tracking vendor performance
- Fashion/retail companies managing production networks

### Hierarchy Structure

```
Level 1: COMPANY (Root)
  └─ Level 2: SUPPLIER
      └─ Level 3: SITE
          └─ Level 4: DEPARTMENT
              └─ Level 5: PROCESS (Leaf)
```

### Detailed Level Definitions

| Level | Name | Singular | Description | Min Children | Max Children | Key Metadata |
|-------|------|----------|-------------|------------|-------------|--------------|
| 1 | Company | company | Parent company | 0 | None | company_name, industry, supplier_count |
| 2 | Supplier | supplier | Vendor/supplier company | 0 | unlimited | supplier_id, supplier_name, rating, audit_status |
| 3 | Site | site | Physical location/factory | 0 | unlimited | location, facility_size, certifications, emissions_data |
| 4 | Department | department | Department within supplier | 0 | unlimited | dept_type (manufacturing, warehouse, admin), headcount |
| 5 | Process | process | Manufacturing/business process | 0 | unlimited | process_type, material_input, emissions_factor, volume |

### JSON Configuration

```json
{
  "pattern_name": "supply_chain",
  "pattern_type": "system",
  "description": "Supply chain and vendor hierarchy",
  "levels": [
    {
      "level": 1,
      "name": "Company",
      "singular": "company",
      "min_children": 0,
      "max_children": null,
      "icon_name": "briefcase",
      "color_code": "#05B6D1",
      "metadata": {
        "fields": ["company_name", "industry", "supplier_count"],
        "validations": {
          "company_name": "text",
          "industry": "text (NACE code optional)",
          "supplier_count": "positive integer"
        }
      }
    },
    {
      "level": 2,
      "name": "Supplier",
      "singular": "supplier",
      "min_children": 0,
      "max_children": null,
      "icon_name": "users",
      "color_code": "#0891B2",
      "metadata": {
        "fields": ["supplier_id", "supplier_name", "rating", "audit_status"],
        "validations": {
          "supplier_id": "unique identifier",
          "rating": "number (1-5 stars)",
          "audit_status": ["audited", "in_progress", "pending", "failed"]
        }
      }
    },
    {
      "level": 3,
      "name": "Site",
      "singular": "site",
      "min_children": 0,
      "max_children": null,
      "icon_name": "map-pin",
      "color_code": "#06B6D4",
      "metadata": {
        "fields": ["location", "facility_size", "certifications", "emissions_data"],
        "validations": {
          "facility_size": "text (small, medium, large)",
          "certifications": ["ISO14001", "ISO50001", "B-Corp", "LEED"],
          "emissions_data": "JSON object with Scope 1/2/3"
        }
      }
    },
    {
      "level": 4,
      "name": "Department",
      "singular": "department",
      "min_children": 0,
      "max_children": null,
      "icon_name": "folder",
      "color_code": "#00D9FF",
      "metadata": {
        "fields": ["dept_type", "headcount"],
        "validations": {
          "dept_type": ["manufacturing", "warehouse", "admin", "quality", "logistics"],
          "headcount": "positive integer"
        }
      }
    },
    {
      "level": 5,
      "name": "Process",
      "singular": "process",
      "min_children": 0,
      "max_children": null,
      "icon_name": "gear",
      "color_code": "#22D3EE",
      "metadata": {
        "fields": ["process_type", "material_input", "emissions_factor", "volume"],
        "validations": {
          "process_type": "text (sewing, dyeing, cutting, assembly, etc.)",
          "emissions_factor": "positive number (kg CO2e per unit)",
          "volume": "positive number (units per month)"
        }
      }
    }
  ]
}
```

### Sample Entity Tree

```
Company: Acme Textiles (Level 1)
├─ Supplier: TechFab India (Level 2)
│  ├─ Site: Mumbai Factory (Level 3)
│  │  ├─ Department: Weaving (Level 4)
│  │  │  ├─ Process: Loom A (Level 5)
│  │  │  ├─ Process: Loom B (Level 5)
│  │  │  └─ Process: Loom C (Level 5)
│  │  ├─ Department: Dyeing (Level 4)
│  │  │  ├─ Process: Vat Dyeing (Level 5)
│  │  │  └─ Process: Digital Printing (Level 5)
│  │  └─ Department: Warehouse (Level 4)
│  ├─ Site: Bangalore Quality Center (Level 3)
├─ Supplier: StyleCut Vietnam (Level 2)
│  ├─ Site: Ho Chi Minh Factory (Level 3)
│  │  ├─ Department: Cutting (Level 4)
│  │  ├─ Department: Assembly (Level 4)
```

### Key Characteristics

- **Depth**: 5 levels from Company to Process
- **Branching Factor**: High (unlimited for suppliers/sites)
- **Purpose**: Supply chain tracking, Scope 3 emissions calculation, vendor management
- **Default Scoping**: Supplier and Site can map to iNetZero Facilities for emissions
- **Emissions Application**: Aggregate emissions from supplier processes to calculate Scope 3 supply chain impact

---

## Cross-Pattern Analysis

### Comparison Matrix

| Aspect | IT/DataCenter | Corporate | Energy | Real Estate | Supply Chain |
|--------|--------------|-----------|--------|-------------|--------------|
| **Depth** | 8 | 5 | 5 | 6 | 5 |
| **Breadth** | Moderate | Small | High | Moderate | Very High |
| **Primary Purpose** | Asset ops | Organization | Generation | Facility mgmt | Vendor mgmt |
| **Leaf Unit** | Device | Individual | Equipment | Space | Process |
| **Typical Instances** | 10K-100K | 100-10K | 100-10K | 100-1K | 100K-1M |
| **Scope 1/2** | Rack/Device | Dept | Plant | Building | Site |
| **Scope 3** | None | Dept emissions | Portfolio | Supply chain | Process |

### Common Metadata Fields Across Patterns

All patterns include these standard fields:

```json
{
  "standard_fields": {
    "entity": {
      "id": "UUID",
      "name": "string (255 chars)",
      "slug": "string (100 chars, unique per parent)",
      "description": "text",
      "hierarchy_level": "integer (1-N)",
      "hierarchy_path": "string (e.g., 'region/campus/building')",
      "hierarchy_depth": "integer (0 for root)",
      "parent_id": "UUID (nullable for root)",
      "children": "relationship array",
      "status": "active|inactive|archived|planned",
      "entity_metadata": "JSON (flexible custom fields)",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "created_by": "user_id",
      "updated_by": "user_id"
    },
    "level": {
      "level_number": "integer",
      "level_name": "string",
      "level_singular": "string (API slug)",
      "min_children": "integer",
      "max_children": "integer or null",
      "icon_name": "string",
      "color_code": "hex color",
      "level_metadata": "JSON (validations, custom fields)"
    }
  }
}
```

---

## Implementation Guidance

### Pattern Selection Criteria

Choose your pattern based on:

1. **IT/DataCenter**: If you're tracking physical infrastructure with focus on racks, servers, power consumption
2. **Corporate**: If you're mapping traditional business org structure with departments and teams
3. **Energy**: If you're in energy generation/distribution with plants, facilities, and equipment
4. **Real Estate**: If you're managing properties with multiple buildings, floors, and tenant spaces
5. **Supply Chain**: If you're tracking vendors, suppliers, and manufacturing processes

### Customization Options

Each pattern can be customized:

- **Add levels**: Insert additional levels between existing ones (e.g., add "Zone" between Floor and Rack)
- **Rename levels**: Change level names while preserving structure (e.g., Campus → Hub)
- **Modify constraints**: Adjust min_children/max_children based on your structure
- **Custom metadata**: Add domain-specific fields to level_metadata
- **Multiple patterns**: Use different patterns for different business units

### Data Migration Path

When migrating from old structure to hierarchy:

1. Map existing entities (Organization → Facility) to new hierarchy levels
2. Use HierarchyMigration table to track transformation
3. Maintain backward compatibility with organization_id and facility_id fields
4. Run data validation before finalizing migration
5. Record any migration errors in HierarchyMigrationError table

---

## Next Steps (Sprint 15.3+)

**Sprint 15.3**: Alembic migration with seed data for all 5 patterns
**Sprint 15.4-15.5**: HierarchyService implementation and API endpoints
**Sprint 15.6-15.7**: Comprehensive tests and documentation
**Sprint 15.8**: QA, code review, and production deployment

---

**Specification Complete**: 2026-03-11
**Total Patterns Defined**: 5
**Total Levels Across Patterns**: 31
**Total Metadata Fields**: 150+
**Status**: Ready for Sprint 15.3 Alembic migration implementation
