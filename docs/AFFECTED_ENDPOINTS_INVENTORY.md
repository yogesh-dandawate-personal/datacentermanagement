# Tenant Isolation: Affected Endpoints Inventory

**Status**: Design Phase
**Total Endpoints**: 75 (across 8 route modules)
**All require tenant_id filtering**: Yes
**Target**: 100% tenant isolation compliance

---

## Summary by Module

| Module | Count | Status | Notes |
|--------|-------|--------|-------|
| organizations.py | 7 | Design | All use tenant filtering pattern |
| dashboards.py | 4 | Design | Depends on organization context |
| telemetry.py | 6 | Design | High volume data endpoint |
| carbon.py | 7 | Design | Core business logic |
| kpi.py | 9 | Design | Analytics endpoints |
| marketplace.py | 12 | Design | Multi-tenant marketplace |
| reporting.py | 17 | Design | Complex queries |
| workflow.py | 13 | Design | State management |
| **TOTAL** | **75** | - | - |

---

## Module: organizations.py (7 endpoints)

File: `backend/app/routes/organizations.py`
Already has: ✅ Some tenant filtering (see lines 42-96)
Needs: Update pattern to use TenantService helpers

### Endpoints to Modify

#### 1. POST /orgs - Create Organization
- **Line**: 66
- **Current**: Uses `current_user['tenant_id']` ✅
- **Status**: Already correct pattern
- **Test**: Create org, verify belongs to tenant
- **Security**: ✅ Sets tenant_id in create

#### 2. GET /orgs/{org_id} - Get Organization
- **Line**: 126
- **Current**: Uses `get_organization_or_404(db, org_id, current_user['tenant_id'])`
- **Status**: Already has tenant filtering ✅
- **Test**: Cannot access other tenant's org
- **Security**: ✅ Filters by tenant_id

#### 3. GET /orgs - List Organizations
- **Line**: 152
- **Current**: Filters by `tenant_id=current_user['tenant_id']` ✅
- **Status**: Already correct
- **Test**: List only returns own organizations
- **Security**: ✅ Filters by tenant_id

#### 4. PUT /orgs/{org_id} - Update Organization
- **Line**: 190
- **Current**: Uses `get_organization_or_404()` with tenant_id
- **Status**: Already correct ✅
- **Test**: Cannot update other tenant's org
- **Security**: ✅ Validates ownership before update

#### 5. DELETE /orgs/{org_id} - Delete Organization
- **Line**: 234
- **Current**: Uses `get_organization_or_404()` with tenant_id
- **Status**: Already correct ✅
- **Test**: Cannot delete other tenant's org
- **Security**: ✅ Validates ownership before delete

#### 6. GET /orgs/{org_id}/children - Get Child Organizations
- **Line**: 275
- **Current**: Gets parent with tenant check ✅
- **Status**: Already correct (but query children needs filter)
- **Test**: Children list respects parent's tenant
- **Security**: ⚠️ Line 292 - query children should also filter by tenant

#### 7. GET /orgs/{org_id}/tree - Get Organization Tree
- **Line**: 313
- **Current**: Gets root with tenant check ✅
- **Status**: Correct root check (but recursive children need tenant check)
- **Test**: Tree respects tenant boundaries
- **Security**: ⚠️ Line 330 - recursive function should verify tenant_id

---

## Module: dashboards.py (4 endpoints)

File: `backend/app/routes/dashboards.py`
Already has: ⏳ Partial tenant awareness
Needs: Complete tenant filtering on all queries

### Endpoints to Modify

#### 1. POST /dashboards - Create Dashboard
- **Current**: Should set tenant_id ✅
- **Status**: Needs verification
- **Test**: Dashboard belongs to creating tenant
- **Security**: Must verify creation adds tenant_id

#### 2. GET /dashboards/{dashboard_id} - Get Dashboard
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's dashboard
- **Security**: Must validate tenant ownership

#### 3. GET /dashboards - List Dashboards
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: List only shows own dashboards
- **Security**: Must filter by tenant_id

#### 4. PUT /dashboards/{dashboard_id} - Update Dashboard
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's dashboard
- **Security**: Must validate ownership before update

---

## Module: telemetry.py (6 endpoints)

File: `backend/app/routes/telemetry.py`
Already has: ⏳ Basic structure
Needs: Comprehensive tenant filtering (high-volume data)

### Endpoints to Modify

#### 1. POST /telemetry - Create Telemetry Entry
- **Current**: Should set tenant_id
- **Status**: Needs verification + high-volume test
- **Test**: Data ingestion respects tenant
- **Security**: Must include tenant_id in all creates

#### 2. GET /telemetry/facility/{facility_id} - Get Facility Telemetry
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's facility data
- **Security**: Must validate facility ownership first

#### 3. GET /telemetry/summary - Get Telemetry Summary
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Summary only shows own data
- **Security**: Critical - aggregations must respect tenant boundaries

#### 4. GET /telemetry/trends - Get Telemetry Trends
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Trends respect tenant data boundaries
- **Security**: Time-series data must be tenant-isolated

#### 5. GET /telemetry/anomalies - Get Anomalies
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Anomaly detection respects tenant data
- **Security**: Must not leak other tenant's anomalies

#### 6. DELETE /telemetry - Delete Telemetry Data
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot delete other tenant's telemetry
- **Security**: Must validate ownership before bulk delete

---

## Module: carbon.py (7 endpoints)

File: `backend/app/routes/carbon.py`
Already has: ⏳ Basic structure
Needs: Complete tenant filtering (core business logic)

### Endpoints to Modify

#### 1. POST /carbon - Record Carbon Credits
- **Current**: Should set tenant_id
- **Status**: Needs verification
- **Test**: Credits recorded under correct tenant
- **Security**: Must include tenant_id in all creates

#### 2. GET /carbon/{credit_id} - Get Carbon Credit
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's credits
- **Security**: Must validate ownership

#### 3. GET /carbon - List Carbon Credits
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: List shows only own credits
- **Security**: Must filter by tenant_id

#### 4. PUT /carbon/{credit_id} - Update Carbon Credit
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's credits
- **Security**: Must validate ownership

#### 5. DELETE /carbon/{credit_id} - Delete Carbon Credit
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot delete other tenant's credits
- **Security**: Must validate ownership

#### 6. GET /carbon/analytics - Carbon Analytics
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Analytics show only own data
- **Security**: Aggregations must respect tenant

#### 7. GET /carbon/verify - Verify Carbon Credit
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Can only verify own credits
- **Security**: Must validate ownership

---

## Module: kpi.py (9 endpoints)

File: `backend/app/routes/kpi.py`
Already has: ⏳ Basic structure
Needs: Complete tenant filtering (analytics)

### Endpoints to Modify

#### 1. POST /kpi - Create KPI
- **Current**: Should set tenant_id
- **Status**: Needs verification
- **Test**: KPIs belong to creating tenant
- **Security**: Must set tenant_id

#### 2. GET /kpi/{kpi_id} - Get KPI
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's KPI
- **Security**: Must validate ownership

#### 3. GET /kpi - List KPIs
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: List shows only own KPIs
- **Security**: Must filter by tenant_id

#### 4. PUT /kpi/{kpi_id} - Update KPI
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's KPI
- **Security**: Must validate ownership

#### 5. DELETE /kpi/{kpi_id} - Delete KPI
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot delete other tenant's KPI
- **Security**: Must validate ownership

#### 6. GET /kpi/calculate - Calculate KPIs
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Calculations use only own data
- **Security**: Must respect tenant boundaries

#### 7. GET /kpi/dashboard - KPI Dashboard
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Dashboard shows only own KPIs
- **Security**: Must filter by tenant_id

#### 8. GET /kpi/targets - KPI Targets
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Targets show only own data
- **Security**: Must filter by tenant_id

#### 9. POST /kpi/update-status - Update KPI Status
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's status
- **Security**: Must validate ownership

---

## Module: marketplace.py (12 endpoints)

File: `backend/app/routes/marketplace.py`
Already has: ⏳ Basic structure
Needs: Complete tenant filtering (multi-tenant marketplace logic)

### Endpoints to Modify

#### 1. POST /marketplace/listings - Create Listing
- **Current**: Should set tenant_id
- **Status**: Needs verification
- **Test**: Listing belongs to creating tenant
- **Security**: Must set tenant_id

#### 2. GET /marketplace/listings/{listing_id} - Get Listing
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's listing
- **Security**: Must validate ownership

#### 3. GET /marketplace/listings - List Listings
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: List shows only own listings
- **Security**: Must filter by tenant_id

#### 4. PUT /marketplace/listings/{listing_id} - Update Listing
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's listing
- **Security**: Must validate ownership

#### 5. DELETE /marketplace/listings/{listing_id} - Delete Listing
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot delete other tenant's listing
- **Security**: Must validate ownership

#### 6. POST /marketplace/orders - Create Order
- **Current**: Should set tenant_id
- **Status**: Needs verification
- **Test**: Order belongs to buyer tenant
- **Security**: Must set tenant_id

#### 7. GET /marketplace/orders/{order_id} - Get Order
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Cannot access other tenant's order
- **Security**: Must validate ownership (buyer or seller)

#### 8. GET /marketplace/orders - List Orders
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: List shows only own orders
- **Security**: Must filter by tenant_id

#### 9. PUT /marketplace/orders/{order_id} - Update Order
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot update other tenant's order
- **Security**: Must validate ownership

#### 10. DELETE /marketplace/orders/{order_id} - Cancel Order
- **Current**: Should validate tenant_id
- **Status**: Needs verification
- **Test**: Cannot cancel other tenant's order
- **Security**: Must validate ownership

#### 11. GET /marketplace/analytics - Marketplace Analytics
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Analytics show only own data
- **Security**: Must filter by tenant_id

#### 12. GET /marketplace/recommendations - Get Recommendations
- **Current**: Should filter by tenant_id
- **Status**: Needs verification
- **Test**: Recommendations use only own data
- **Security**: Must filter by tenant_id

---

## Module: reporting.py (17 endpoints)

File: `backend/app/routes/reporting.py`
Already has: ⏳ Basic structure
Needs: Complete tenant filtering (complex queries)

### Endpoints to Modify

#### 1-17. All Reporting Endpoints
- **Status**: Needs comprehensive tenant filtering
- **Challenge**: Complex queries with joins
- **Security**: Must ensure all JOINs respect tenant boundaries
- **Test**: All aggregations/reports filter by tenant_id

---

## Module: workflow.py (13 endpoints)

File: `backend/app/routes/workflow.py`
Already has: ⏳ Basic structure
Needs: Complete tenant filtering (state management)

### Endpoints to Modify

#### 1-13. All Workflow Endpoints
- **Status**: Needs comprehensive tenant filtering
- **Challenge**: State machines with multi-step processes
- **Security**: Must ensure workflow progress respects tenant boundaries
- **Test**: Workflows cannot cross tenant boundaries

---

## Implementation Checklist

For each endpoint, verify:

```
Endpoint: [name]
Module: [file]

Security Checklist:
- [ ] Has tenant_id filter in WHERE clause (if read/update/delete)
- [ ] Sets tenant_id in INSERT (if create)
- [ ] Returns 404 for other tenant's data (not 200 + wrong data)
- [ ] No data in error messages that could leak tenant info
- [ ] Test: Same tenant can access their data
- [ ] Test: Other tenant gets 404
- [ ] Test: Unauthenticated gets 401
- [ ] Audit log includes tenant_id

Pattern Check:
- [ ] Uses Depends(get_current_tenant)
- [ ] Extracts tenant_id from current_tenant dict
- [ ] Passes tenant_id to database query
- [ ] Uses consistent query pattern across module

Regression Check:
- [ ] Original test suite still passes
- [ ] New tenant isolation tests pass
- [ ] No performance degradation
- [ ] Proper error messages
```

---

## Testing Strategy

### Test Scenarios (Applied to all 75 endpoints)

1. **Authenticated Tenant Access**
   - User from Tenant A accesses their own resource
   - Expect: 200 OK with correct data

2. **Cross-Tenant Access Attempt**
   - User from Tenant A attempts to access Tenant B's resource
   - Expect: 404 Not Found (not 200 with Tenant B's data)

3. **Unauthenticated Access**
   - Request without Authorization header
   - Expect: 401 Unauthorized

4. **Invalid Token**
   - Request with malformed/expired token
   - Expect: 401 Unauthorized

5. **Same Endpoint, Different Tenants**
   - Two authenticated users from different tenants
   - Expect: Each sees only their own data

### Test Coverage Matrix

| Endpoint Count | Read (GET) | Create (POST) | Update (PUT) | Delete (DELETE) | List |
|---|---|---|---|---|---|
| 75 Total | 35 | 15 | 15 | 10 | 15 |
| Test Scenarios | 5 each | 5 each | 5 each | 5 each | 5 each |
| **Total Tests** | **175** | **75** | **75** | **50** | **75** |
| **Grand Total** | **450 tests** | - | - | - | - |

---

## Migration Path

### Phase 1: Design (Current)
- ✅ Design middleware
- ✅ Design validation service
- ✅ Document all affected endpoints (this file)
- ✅ Create test suite template

### Phase 2: Implementation (After AUTH-FIX)
1. Implement TenantMiddleware
2. Implement TenantService helpers
3. Update all 75 endpoints to use pattern
4. Run full test suite

### Phase 3: Verification (After Implementation)
1. All 75 endpoints validate ownership
2. All tests passing (450+ tests)
3. No data leakage detected
4. Security audit passes

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Query misses tenant_id filter | Code review checklist (this doc) |
| Recursive queries lose tenant context | Use TenantService helpers exclusively |
| Error messages leak data | Consistent "not found" for all 404 cases |
| Performance impact | Tenant_id filtering is indexed |
| Forgot endpoint | Automated grep check for Depends(get_current_user) |

---

## Success Criteria

- [ ] All 75 endpoints have tenant_id filtering
- [ ] Cross-tenant access returns 404 (not data)
- [ ] Same-tenant access returns 200 with correct data
- [ ] All 450+ tests passing
- [ ] No performance regression
- [ ] Security audit approved
- [ ] Zero data leakage in logs/errors

---

**Last Updated**: 2026-03-10 (Design Phase)
**Next Step**: Implementation after AUTH-FIX completion
