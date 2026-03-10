"""
Pytest configuration and fixtures for iNetZero backend tests
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, Tenant, User, Role
from app.services.password_service import get_password_service
from app.auth.jwt_handler import create_access_token


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a test database session using SQLite in-memory
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create session
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def demo_tenant(db: Session) -> Tenant:
    """
    Create a demo tenant for testing

    Returns:
        Tenant object with test data
    """
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Demo Corporation",
        slug="demo-corp",
        email="admin@demo.com",
        is_active=True
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def demo_user(db: Session, demo_tenant: Tenant) -> User:
    """
    Create a demo user with real password hash for testing

    Returns:
        User object with hashed password
    """
    password_service = get_password_service()
    password_hash = password_service.hash_password("demo_password_123")

    user = User(
        id=uuid.uuid4(),
        tenant_id=demo_tenant.id,
        email="demo@example.com",
        first_name="Demo",
        last_name="User",
        password_hash=password_hash,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def demo_admin_user(db: Session, demo_tenant: Tenant) -> User:
    """
    Create a demo admin user with password hash for testing

    Returns:
        Admin user object with hashed password and admin role
    """
    password_service = get_password_service()
    password_hash = password_service.hash_password("admin_password_123")

    # Create admin role if it doesn't exist
    admin_role = db.query(Role).filter_by(
        tenant_id=demo_tenant.id,
        name="admin"
    ).first()

    if not admin_role:
        admin_role = Role(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            name="admin",
            description="Administrator role",
            permissions=["read", "write", "delete", "admin"],
            is_active=True
        )
        db.add(admin_role)
        db.flush()

    user = User(
        id=uuid.uuid4(),
        tenant_id=demo_tenant.id,
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        is_active=True
    )
    user.roles.append(admin_role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def demo_access_token(demo_user: User) -> str:
    """
    Create a valid JWT access token for demo user

    Returns:
        JWT access token string
    """
    return create_access_token(
        user_id=str(demo_user.id),
        tenant_id=str(demo_user.tenant_id),
        roles=["viewer"],
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture(scope="function")
def demo_admin_token(demo_admin_user: User) -> str:
    """
    Create a valid JWT access token for demo admin user

    Returns:
        JWT access token string
    """
    roles = [role.name for role in demo_admin_user.roles]
    return create_access_token(
        user_id=str(demo_admin_user.id),
        tenant_id=str(demo_admin_user.tenant_id),
        roles=roles,
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture(scope="function")
def demo_refresh_token(demo_user: User) -> str:
    """
    Create a valid JWT refresh token for demo user

    Returns:
        JWT refresh token string
    """
    return create_access_token(
        user_id=str(demo_user.id),
        tenant_id=str(demo_user.tenant_id),
        roles=["refresh"],
        expires_delta=timedelta(days=7)
    )


@pytest.fixture(scope="function")
def auth_headers(demo_access_token: str) -> dict:
    """
    Create Authorization headers for authenticated requests

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {demo_access_token}"}
