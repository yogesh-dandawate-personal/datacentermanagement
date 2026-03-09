"""Tests for organization hierarchy module"""
import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.models import Tenant, User, Organization, Role, Department, Position
from app.database import SessionLocal
from sqlalchemy import text


@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def tenant(db):
    """Create test tenant"""
    tenant = Tenant(
        name="Test Org",
        slug="test-org",
        email="test@example.com"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db, tenant):
    """Create admin user"""
    user = User(
        tenant_id=tenant.id,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestOrganizationCreation:
    """Test organization creation"""

    def test_create_organization_success(self, db, tenant, admin_user):
        """Create organization successfully"""
        org = Organization(
            tenant_id=tenant.id,
            name="Engineering",
            slug="eng",
            description="Engineering department",
            hierarchy_level=0,
            is_active=True,
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        assert org.id is not None
        assert org.name == "Engineering"
        assert org.hierarchy_level == 0
        assert org.tenant_id == tenant.id

    def test_create_organization_with_parent(self, db, tenant, admin_user):
        """Create organization with parent"""
        parent = Organization(
            tenant_id=tenant.id,
            name="Parent Org",
            slug="parent",
            hierarchy_level=0,
            created_by=admin_user.id
        )
        db.add(parent)
        db.commit()

        child = Organization(
            tenant_id=tenant.id,
            parent_id=parent.id,
            name="Child Org",
            slug="child",
            hierarchy_level=1,
            created_by=admin_user.id
        )
        db.add(child)
        db.commit()
        db.refresh(child)

        assert child.parent_id == parent.id
        assert child.hierarchy_level == 1
        assert child.parent == parent

    def test_create_multiple_organizations(self, db, tenant, admin_user):
        """Create multiple organizations"""
        orgs = []
        for i in range(3):
            org = Organization(
                tenant_id=tenant.id,
                name=f"Org {i}",
                slug=f"org-{i}",
                hierarchy_level=0,
                created_by=admin_user.id
            )
            db.add(org)
            orgs.append(org)

        db.commit()

        assert len(orgs) == 3
        assert all(org.id is not None for org in orgs)


class TestOrganizationRetrieval:
    """Test organization retrieval and queries"""

    def test_get_organization_by_id(self, db, tenant, admin_user):
        """Retrieve organization by ID"""
        org = Organization(
            tenant_id=tenant.id,
            name="Test Org",
            slug="test",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        retrieved = db.query(Organization).filter_by(id=org.id).first()
        assert retrieved is not None
        assert retrieved.name == "Test Org"

    def test_get_organization_not_found(self, db):
        """Retrieve non-existent organization"""
        fake_id = uuid.uuid4()
        org = db.query(Organization).filter_by(id=fake_id).first()
        assert org is None

    def test_list_organizations_by_tenant(self, db, tenant, admin_user):
        """List organizations for tenant"""
        for i in range(3):
            org = Organization(
                tenant_id=tenant.id,
                name=f"Org {i}",
                slug=f"org-{i}",
                created_by=admin_user.id
            )
            db.add(org)

        db.commit()

        orgs = db.query(Organization).filter_by(tenant_id=tenant.id).all()
        assert len(orgs) == 3

    def test_organization_isolation_by_tenant(self, db, admin_user):
        """Ensure organizations are isolated by tenant"""
        tenant1 = Tenant(name="Tenant 1", slug="t1", email="t1@example.com")
        tenant2 = Tenant(name="Tenant 2", slug="t2", email="t2@example.com")
        db.add_all([tenant1, tenant2])
        db.commit()

        org1 = Organization(
            tenant_id=tenant1.id,
            name="Org 1",
            slug="org1",
            created_by=admin_user.id
        )
        org2 = Organization(
            tenant_id=tenant2.id,
            name="Org 2",
            slug="org2",
            created_by=admin_user.id
        )
        db.add_all([org1, org2])
        db.commit()

        tenant1_orgs = db.query(Organization).filter_by(tenant_id=tenant1.id).all()
        assert len(tenant1_orgs) == 1
        assert tenant1_orgs[0].name == "Org 1"


class TestOrganizationHierarchy:
    """Test organization hierarchy operations"""

    def test_get_organization_children(self, db, tenant, admin_user):
        """Get organization children"""
        parent = Organization(
            tenant_id=tenant.id,
            name="Parent",
            slug="parent",
            hierarchy_level=0,
            created_by=admin_user.id
        )
        db.add(parent)
        db.commit()

        for i in range(3):
            child = Organization(
                tenant_id=tenant.id,
                parent_id=parent.id,
                name=f"Child {i}",
                slug=f"child-{i}",
                hierarchy_level=1,
                created_by=admin_user.id
            )
            db.add(child)

        db.commit()

        children = db.query(Organization).filter_by(parent_id=parent.id).all()
        assert len(children) == 3

    def test_get_organization_parent(self, db, tenant, admin_user):
        """Get organization parent"""
        parent = Organization(
            tenant_id=tenant.id,
            name="Parent",
            slug="parent",
            created_by=admin_user.id
        )
        db.add(parent)
        db.commit()

        child = Organization(
            tenant_id=tenant.id,
            parent_id=parent.id,
            name="Child",
            slug="child",
            hierarchy_level=1,
            created_by=admin_user.id
        )
        db.add(child)
        db.commit()

        assert child.parent == parent
        assert child.parent.name == "Parent"

    def test_deep_hierarchy(self, db, tenant, admin_user):
        """Create deep organizational hierarchy"""
        orgs = []
        parent_id = None

        for i in range(5):
            org = Organization(
                tenant_id=tenant.id,
                parent_id=parent_id,
                name=f"Level {i}",
                slug=f"level-{i}",
                hierarchy_level=i,
                created_by=admin_user.id
            )
            db.add(org)
            orgs.append(org)
            parent_id = org.id

        db.commit()

        # Verify hierarchy levels
        assert orgs[-1].hierarchy_level == 4
        assert orgs[-1].parent.hierarchy_level == 3


class TestOrganizationUpdate:
    """Test organization update operations"""

    def test_update_organization_details(self, db, tenant, admin_user):
        """Update organization details"""
        org = Organization(
            tenant_id=tenant.id,
            name="Original Name",
            slug="original",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        org.name = "Updated Name"
        org.description = "Updated description"
        db.commit()

        updated = db.query(Organization).filter_by(id=org.id).first()
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"

    def test_update_organization_status(self, db, tenant, admin_user):
        """Update organization active status"""
        org = Organization(
            tenant_id=tenant.id,
            name="Test Org",
            slug="test",
            is_active=True,
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        org.is_active = False
        db.commit()

        updated = db.query(Organization).filter_by(id=org.id).first()
        assert updated.is_active is False


class TestOrganizationDelete:
    """Test organization deletion"""

    def test_delete_leaf_organization(self, db, tenant, admin_user):
        """Delete leaf organization"""
        org = Organization(
            tenant_id=tenant.id,
            name="Leaf Org",
            slug="leaf",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        org_id = org.id
        db.delete(org)
        db.commit()

        deleted = db.query(Organization).filter_by(id=org_id).first()
        assert deleted is None

    def test_delete_organization_with_children(self, db, tenant, admin_user):
        """Delete organization cascades to children"""
        parent = Organization(
            tenant_id=tenant.id,
            name="Parent",
            slug="parent",
            created_by=admin_user.id
        )
        db.add(parent)
        db.commit()

        child = Organization(
            tenant_id=tenant.id,
            parent_id=parent.id,
            name="Child",
            slug="child",
            hierarchy_level=1,
            created_by=admin_user.id
        )
        db.add(child)
        db.commit()

        parent_id = parent.id
        child_id = child.id

        # Delete parent - due to cascade, children reference should be set to NULL or removed
        db.delete(parent)
        db.commit()

        parent_check = db.query(Organization).filter_by(id=parent_id).first()
        assert parent_check is None


class TestDepartmentOperations:
    """Test department operations"""

    def test_create_department(self, db, tenant, admin_user):
        """Create department"""
        org = Organization(
            tenant_id=tenant.id,
            name="Org",
            slug="org",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        dept = Department(
            organization_id=org.id,
            tenant_id=tenant.id,
            name="Engineering",
            description="Eng department",
            manager_id=admin_user.id
        )
        db.add(dept)
        db.commit()

        assert dept.id is not None
        assert dept.organization_id == org.id

    def test_list_departments_by_organization(self, db, tenant, admin_user):
        """List departments for organization"""
        org = Organization(
            tenant_id=tenant.id,
            name="Org",
            slug="org",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        for i in range(3):
            dept = Department(
                organization_id=org.id,
                tenant_id=tenant.id,
                name=f"Dept {i}"
            )
            db.add(dept)

        db.commit()

        depts = db.query(Department).filter_by(organization_id=org.id).all()
        assert len(depts) == 3


class TestPositionOperations:
    """Test position operations"""

    def test_create_position(self, db, tenant, admin_user):
        """Create position"""
        org = Organization(
            tenant_id=tenant.id,
            name="Org",
            slug="org",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        pos = Position(
            organization_id=org.id,
            tenant_id=tenant.id,
            name="Software Engineer",
            description="SE role",
            level=3
        )
        db.add(pos)
        db.commit()

        assert pos.id is not None
        assert pos.organization_id == org.id

    def test_list_positions_by_organization(self, db, tenant, admin_user):
        """List positions for organization"""
        org = Organization(
            tenant_id=tenant.id,
            name="Org",
            slug="org",
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        for i in range(3):
            pos = Position(
                organization_id=org.id,
                tenant_id=tenant.id,
                name=f"Position {i}",
                level=i
            )
            db.add(pos)

        db.commit()

        positions = db.query(Position).filter_by(organization_id=org.id).all()
        assert len(positions) == 3


class TestOrganizationMetadata:
    """Test metadata handling"""

    def test_organization_with_metadata(self, db, tenant, admin_user):
        """Store and retrieve organization metadata"""
        metadata = {
            "cost_center": "CC-001",
            "location": "San Francisco",
            "manager_email": "manager@example.com"
        }

        org = Organization(
            tenant_id=tenant.id,
            name="Test",
            slug="test",
            metadata=metadata,
            created_by=admin_user.id
        )
        db.add(org)
        db.commit()

        retrieved = db.query(Organization).filter_by(id=org.id).first()
        assert retrieved.metadata == metadata
        assert retrieved.metadata["cost_center"] == "CC-001"
