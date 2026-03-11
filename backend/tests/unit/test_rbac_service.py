"""
Unit Tests for RBAC Service - Sprint 14

Tests for:
- Permission checking with and without cache
- Role assignment and revocation
- Permission audit logging
- System role seeding
- Scope-based access control
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ...app.models import Base, Tenant, User, Organization, Facility, Permission, RoleEnhanced, UserRoleEnhanced, PermissionAuditLog
from ...app.services.rbac_service import RBACService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_tenant(db_session):
    """Create test tenant"""
    tenant = Tenant(
        id=uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        email="test@tenant.com",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create test user"""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="user@test.com",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_org(db_session, test_tenant):
    """Create test organization"""
    org = Organization(
        id=uuid4(),
        tenant_id=test_tenant.id,
        name="Test Organization",
        slug="test-org",
        hierarchy_level=0
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def test_facility(db_session, test_tenant, test_org):
    """Create test facility"""
    facility = Facility(
        id=uuid4(),
        tenant_id=test_tenant.id,
        organization_id=test_org.id,
        name="Test Facility",
        slug="test-facility",
        facility_type="data_center",
        location="US-East-1"
    )
    db_session.add(facility)
    db_session.commit()
    return facility


@pytest.fixture
def rbac_service(db_session):
    """Create RBAC service instance"""
    return RBACService(db_session, redis_client=None)


# ============================================================================
# PERMISSION TESTS
# ============================================================================

class TestPermissions:
    """Test permission seeding and management"""

    def test_seed_system_permissions(self, rbac_service, test_tenant):
        """Test that all system permissions are seeded"""
        count = rbac_service.seed_system_permissions(test_tenant.id)

        assert count == len(RBACService.ALL_PERMISSIONS)

        # Verify all permissions are in database
        permissions = rbac_service.db.query(Permission).all()
        assert len(permissions) == len(RBACService.ALL_PERMISSIONS)

        # Verify specific permissions
        org_create = rbac_service.db.query(Permission).filter_by(
            permission_name='organizations:create'
        ).first()
        assert org_create is not None
        assert org_create.resource == 'organizations'
        assert org_create.action == 'create'

    def test_permission_uniqueness(self, rbac_service, test_tenant):
        """Test that permissions are unique"""
        rbac_service.seed_system_permissions(test_tenant.id)

        # Try to seed again, should not create duplicates
        count = rbac_service.seed_system_permissions(test_tenant.id)
        assert count == 0

        permissions = rbac_service.db.query(Permission).all()
        assert len(permissions) == len(RBACService.ALL_PERMISSIONS)


# ============================================================================
# ROLE TESTS
# ============================================================================

class TestRoles:
    """Test role seeding and management"""

    def test_seed_system_roles(self, rbac_service, test_tenant):
        """Test that system roles are created with correct permissions"""
        rbac_service.seed_system_permissions(test_tenant.id)
        count = rbac_service.seed_system_roles(test_tenant.id)

        assert count == len(RBACService.SYSTEM_ROLES)

        # Verify ESG Manager role
        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            tenant_id=test_tenant.id,
            role_name='esg_manager'
        ).first()

        assert esg_manager is not None
        assert esg_manager.role_display_name == 'ESG Manager'
        assert esg_manager.is_system_role is True

        # Verify permissions assigned
        perms = rbac_service.get_role_permissions(esg_manager.id)
        assert 'organizations:create' in perms
        assert 'emissions:approve' in perms
        assert len(perms) > 0

    def test_role_idempotency(self, rbac_service, test_tenant):
        """Test that seeding roles twice doesn't create duplicates"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        # Seed again
        count = rbac_service.seed_system_roles(test_tenant.id)
        assert count == 0

        roles = rbac_service.db.query(RoleEnhanced).filter_by(
            tenant_id=test_tenant.id
        ).all()
        assert len(roles) == len(RBACService.SYSTEM_ROLES)


# ============================================================================
# USER ROLE ASSIGNMENT TESTS
# ============================================================================

class TestUserRoleAssignment:
    """Test user role assignment and revocation"""

    def test_assign_role_success(self, rbac_service, test_tenant, test_user):
        """Test successful role assignment"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        # Get ESG Manager role
        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        # Assign role
        user_role = rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id,
            grant_reason="Test assignment"
        )

        assert user_role.user_id == test_user.id
        assert user_role.role_id == esg_manager.id
        assert user_role.is_active is True
        assert user_role.expires_at is None

    def test_assign_role_with_expiration(self, rbac_service, test_tenant, test_user):
        """Test role assignment with expiration"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        # Assign temporary role
        user_role = rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id,
            expires_in_days=7
        )

        assert user_role.expires_at is not None
        assert user_role.expires_at > datetime.utcnow()

    def test_assign_role_with_scope(self, rbac_service, test_tenant, test_user, test_org, test_facility):
        """Test role assignment with org/facility scope"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        facility_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='facility_manager'
        ).first()

        # Assign role scoped to facility
        user_role = rbac_service.assign_role(
            user_id=test_user.id,
            role_id=facility_manager.id,
            granted_by=test_user.id,
            facility_id=test_facility.id
        )

        assert user_role.facility_id == test_facility.id
        assert user_role.organization_id is None

    def test_revoke_role(self, rbac_service, test_tenant, test_user):
        """Test role revocation"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        # Assign and then revoke
        user_role = rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id
        )

        rbac_service.revoke_role(user_role.id)

        # Verify revocation
        revoked = rbac_service.db.query(UserRoleEnhanced).filter_by(
            id=user_role.id
        ).first()
        assert revoked.is_active is False


# ============================================================================
# PERMISSION CHECKING TESTS
# ============================================================================

class TestPermissionChecks:
    """Test permission checking logic"""

    def test_check_permission_with_role(self, rbac_service, test_tenant, test_user):
        """Test that user with role has permission"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id
        )

        # Check permission
        has_perm = rbac_service.check_permission(
            user_id=test_user.id,
            resource='organizations',
            action='create',
            audit_log=False
        )

        assert has_perm is True

    def test_check_permission_without_role(self, rbac_service, test_tenant, test_user):
        """Test that user without role lacks permission"""
        rbac_service.seed_system_permissions(test_tenant.id)

        has_perm = rbac_service.check_permission(
            user_id=test_user.id,
            resource='organizations',
            action='create',
            audit_log=False
        )

        assert has_perm is False

    def test_check_permission_expired_role(self, rbac_service, test_tenant, test_user):
        """Test that expired roles don't grant permission"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        # Assign role that expires immediately
        user_role = rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id,
            expires_in_days=0
        )

        # Manually set to past
        user_role.expires_at = datetime.utcnow() - timedelta(hours=1)
        rbac_service.db.commit()

        has_perm = rbac_service.check_permission(
            user_id=test_user.id,
            resource='organizations',
            action='create',
            audit_log=False
        )

        assert has_perm is False

    def test_check_permission_scoped_org(self, rbac_service, test_tenant, test_user, test_org):
        """Test permission checking with org scope"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        facility_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='facility_manager'
        ).first()

        # Assign role scoped to org
        rbac_service.assign_role(
            user_id=test_user.id,
            role_id=facility_manager.id,
            granted_by=test_user.id,
            organization_id=test_org.id
        )

        # Check permission in same org
        has_perm = rbac_service.check_permission(
            user_id=test_user.id,
            resource='facilities',
            action='read',
            organization_id=test_org.id,
            audit_log=False
        )

        assert has_perm is True

        # Check permission in different org
        other_org = Organization(
            id=uuid4(),
            tenant_id=test_tenant.id,
            name="Other Org",
            slug="other-org",
            hierarchy_level=0
        )
        rbac_service.db.add(other_org)
        rbac_service.db.commit()

        has_perm = rbac_service.check_permission(
            user_id=test_user.id,
            resource='facilities',
            action='read',
            organization_id=other_org.id,
            audit_log=False
        )

        assert has_perm is False


# ============================================================================
# AUDIT LOGGING TESTS
# ============================================================================

class TestAuditLogging:
    """Test permission audit logging"""

    def test_audit_log_created_on_permission_check(self, rbac_service, test_tenant, test_user):
        """Test that audit log is created for permission checks"""
        rbac_service.seed_system_permissions(test_tenant.id)

        rbac_service.check_permission(
            user_id=test_user.id,
            resource='organizations',
            action='create',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            audit_log=True
        )

        audit = rbac_service.db.query(PermissionAuditLog).filter_by(
            user_id=test_user.id
        ).first()

        assert audit is not None
        assert audit.action == 'check'
        assert audit.resource == 'organizations'
        assert audit.permission_name == 'organizations:create'
        assert audit.granted is False  # User has no role
        assert audit.ip_address == '192.168.1.1'

    def test_audit_log_granted_permission(self, rbac_service, test_tenant, test_user):
        """Test audit log for granted permissions"""
        rbac_service.seed_system_permissions(test_tenant.id)
        rbac_service.seed_system_roles(test_tenant.id)

        esg_manager = rbac_service.db.query(RoleEnhanced).filter_by(
            role_name='esg_manager'
        ).first()

        rbac_service.assign_role(
            user_id=test_user.id,
            role_id=esg_manager.id,
            granted_by=test_user.id
        )

        rbac_service.check_permission(
            user_id=test_user.id,
            resource='organizations',
            action='create',
            audit_log=True
        )

        audit = rbac_service.db.query(PermissionAuditLog).filter_by(
            user_id=test_user.id,
            granted=True
        ).first()

        assert audit is not None
        assert audit.granted is True
