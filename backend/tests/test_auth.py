"""
Comprehensive authentication tests for real credential validation and JWT tokens

Tests cover:
- Valid credentials → returns tokens
- Invalid credentials → 401
- Token validation → success
- Expired tokens → 401
- Refresh tokens → new access token
- Password hashing with Argon2
- User registration
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.main import app
from app.models import User, Tenant, Role
from app.services.password_service import PasswordService
from app.auth.jwt_handler import create_access_token, verify_token

# Create test client
client = TestClient(app)


class TestPasswordService:
    """Test Argon2 password hashing and verification"""

    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing creates a valid Argon2 hash"""
        service = PasswordService()
        password = "my_secure_password_123"

        hash_value = service.hash_password(password)

        # Hash should start with $argon2
        assert hash_value.startswith("$argon2")
        # Hash should not equal plain password
        assert hash_value != password

    def test_verify_password_succeeds_with_correct_password(self):
        """Test that password verification succeeds with correct password"""
        service = PasswordService()
        password = "my_secure_password_123"
        hash_value = service.hash_password(password)

        result = service.verify_password(password, hash_value)

        assert result is True

    def test_verify_password_fails_with_incorrect_password(self):
        """Test that password verification fails with incorrect password"""
        service = PasswordService()
        password = "my_secure_password_123"
        wrong_password = "wrong_password"
        hash_value = service.hash_password(password)

        result = service.verify_password(wrong_password, hash_value)

        assert result is False

    def test_hash_password_rejects_short_password(self):
        """Test that short passwords are rejected"""
        service = PasswordService()
        short_password = "short"

        with pytest.raises(ValueError, match="at least 8 characters"):
            service.hash_password(short_password)

    def test_hash_password_rejects_empty_password(self):
        """Test that empty passwords are rejected"""
        service = PasswordService()

        with pytest.raises(ValueError, match="non-empty string"):
            service.hash_password("")


class TestLoginEndpoint:
    """Test login endpoint with real credential validation"""

    def test_login_with_valid_credentials_returns_tokens(
        self, db: Session, demo_user: User
    ):
        """Test login with valid email and password returns JWT tokens"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "demo_password_123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "bearer"
        assert data["user_id"] == str(demo_user.id)
        assert data["tenant_id"] == str(demo_user.tenant_id)

    def test_login_with_invalid_password_returns_401(self, db: Session, demo_user: User):
        """Test login with invalid password returns 401"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "wrong_password"
            }
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_with_nonexistent_user_returns_401(self):
        """Test login with non-existent email returns 401"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "some_password_123"
            }
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_with_missing_email_returns_422(self):
        """Test login with missing email returns validation error"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "password": "demo_password_123"
            }
        )

        assert response.status_code == 422

    def test_login_updates_last_login_timestamp(self, db: Session, demo_user: User):
        """Test that successful login updates last_login timestamp"""
        # Before login
        assert demo_user.last_login is None

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "demo_password_123"
            }
        )

        assert response.status_code == 200

        # Check last_login was updated
        db.refresh(demo_user)
        assert demo_user.last_login is not None


class TestRefreshTokenEndpoint:
    """Test refresh token endpoint"""

    def test_refresh_token_with_valid_token_returns_new_access_token(
        self, demo_user: User, demo_refresh_token: str
    ):
        """Test refresh token endpoint returns new access token"""
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": demo_refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["refresh_token"] == demo_refresh_token
        assert data["token_type"] == "bearer"
        assert data["user_id"] == str(demo_user.id)

    def test_refresh_token_with_invalid_token_returns_401(self):
        """Test refresh token with invalid token returns 401"""
        response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401


class TestTokenValidation:
    """Test JWT token validation and claims extraction"""

    def test_verify_token_extracts_claims(self, demo_user: User):
        """Test that token verification extracts all claims"""
        token = create_access_token(
            user_id=str(demo_user.id),
            tenant_id=str(demo_user.tenant_id),
            roles=["admin", "editor"]
        )

        token_data = verify_token(token)

        assert token_data.sub == str(demo_user.id)
        assert token_data.tenant_id == str(demo_user.tenant_id)
        assert "admin" in token_data.roles
        assert "editor" in token_data.roles

    def test_verify_expired_token_raises_error(self, demo_user: User):
        """Test that expired token raises TokenExpiredError"""
        # Create token that expired 1 hour ago
        token = create_access_token(
            user_id=str(demo_user.id),
            tenant_id=str(demo_user.tenant_id),
            expires_delta=timedelta(hours=-1)
        )

        from app.exceptions import TokenExpiredError
        with pytest.raises(TokenExpiredError):
            verify_token(token)


class TestGetCurrentUserEndpoint:
    """Test /auth/me endpoint"""

    def test_get_current_user_with_valid_token(
        self, demo_user: User, demo_access_token: str
    ):
        """Test getting current user with valid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {demo_access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == demo_user.email

    def test_get_current_user_without_token_returns_401(self):
        """Test getting current user without token returns 401"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestLogoutEndpoint:
    """Test logout endpoint"""

    def test_logout_with_valid_token_returns_204(self, demo_access_token: str):
        """Test logout with valid token returns 204 No Content"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {demo_access_token}"}
        )

        assert response.status_code == 204
        assert response.json()["token_type"] == "bearer"

    def test_user_login_invalid_credentials(self, client):
        """Invalid credentials should return 401"""
        response = client.post("/api/v1/auth/login", json={
            "username": "user@example.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_jwt_token_validation(self, client, auth_token):
        """Valid JWT token should allow API access"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        assert "id" in response.json()


class TestRoleBasedAccess:
    """Test role-based access control"""

    def test_admin_access(self, client, admin_token):
        """Admin should access admin endpoints"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200

    def test_viewer_cannot_delete(self, client, viewer_token):
        """Viewer role cannot perform destructive actions"""
        headers = {"Authorization": f"Bearer {viewer_token}"}
        response = client.delete("/api/v1/facilities/123", headers=headers)
        assert response.status_code == 403

    def test_editor_can_edit(self, client, editor_token):
        """Editor role can edit data"""
        headers = {"Authorization": f"Bearer {editor_token}"}
        response = client.put("/api/v1/facilities/123", 
            headers=headers,
            json={"name": "Updated Facility"}
        )
        assert response.status_code == 200


class TestAuditLogging:
    """Test that all actions are logged"""

    def test_audit_log_created_on_user_creation(self, client, admin_token):
        """Creating user should log audit entry"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/users", 
            headers=headers,
            json={"email": "newuser@example.com", "role": "editor"}
        )
        
        # Verify audit log entry was created
        response = client.get("/api/v1/audit-logs", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) > 0


@pytest.fixture
def client():
    """Provide test client"""
    from fastapi.testclient import TestClient
    # Will be implemented
    pass


@pytest.fixture
def auth_token():
    """Provide valid JWT token"""
    pass


@pytest.fixture
def admin_token():
    """Provide admin JWT token"""
    pass


@pytest.fixture
def editor_token():
    """Provide editor JWT token"""
    pass


@pytest.fixture
def viewer_token():
    """Provide viewer JWT token"""
    pass
