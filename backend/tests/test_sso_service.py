"""
Tests for SSO/SAML Service - Sprint 13
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
import jwt
import base64

from app.services.sso_service import SSOService
from app.models import User, Tenant, AuditLog


@pytest.fixture
def sso_service(db):
    """Create SSO service instance"""
    return SSOService(db)


@pytest.fixture
def test_tenant(db):
    """Create test tenant"""
    tenant = Tenant(
        id=uuid4(),
        name="Test Corp",
        slug="test-corp",
        email="admin@testcorp.com",
        is_active=True
    )
    db.add(tenant)
    db.commit()
    return tenant


class TestSAMLFunctions:
    """Test SAML 2.0 functionality"""

    def test_generate_saml_request(self, sso_service, test_tenant):
        """Test SAML AuthnRequest generation"""
        idp_config = {
            'entity_id': 'https://idp.example.com',
            'sso_url': 'https://idp.example.com/sso'
        }

        result = sso_service.generate_saml_request(
            tenant_id=test_tenant.id,
            idp_config=idp_config,
            relay_state='test_state'
        )

        assert 'request_id' in result
        assert 'saml_request' in result
        assert 'redirect_url' in result
        assert idp_config['sso_url'] in result['redirect_url']
        assert 'SAMLRequest=' in result['redirect_url']

    def test_process_saml_response_success(self, sso_service):
        """Test processing valid SAML response"""
        # Mock SAML response XML
        saml_xml = """<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
    </samlp:Status>
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        <saml:Subject>
            <saml:NameID>john.doe@example.com</saml:NameID>
        </saml:Subject>
        <saml:AttributeStatement>
            <saml:Attribute Name="firstName">
                <saml:AttributeValue>John</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="lastName">
                <saml:AttributeValue>Doe</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""

        saml_encoded = base64.b64encode(saml_xml.encode('utf-8')).decode('utf-8')

        user_info = sso_service.process_saml_response(saml_encoded)

        assert user_info['email'] == 'john.doe@example.com'
        assert user_info['first_name'] == 'John'
        assert user_info['last_name'] == 'Doe'
        assert user_info['authentication_method'] == 'saml2'

    def test_process_saml_response_invalid(self, sso_service):
        """Test processing invalid SAML response"""
        invalid_saml = base64.b64encode(b"invalid xml").decode('utf-8')

        with pytest.raises(ValueError, match="Invalid SAML response"):
            sso_service.process_saml_response(invalid_saml)


class TestOAuthFunctions:
    """Test OAuth 2.0 functionality"""

    def test_generate_oauth_url(self, sso_service):
        """Test OAuth authorization URL generation"""
        url = sso_service.generate_oauth_url(
            provider='google_workspace',
            client_id='test_client_id',
            redirect_uri='https://app.example.com/oauth/callback',
            scopes=['openid', 'email', 'profile'],
            state='test_state'
        )

        assert 'https://accounts.google.com/o/oauth2/v2/auth' in url
        assert 'client_id=test_client_id' in url
        assert 'state=test_state' in url
        assert 'scope=openid+email+profile' in url

    def test_exchange_oauth_code(self, sso_service):
        """Test OAuth code exchange"""
        result = sso_service.exchange_oauth_code(
            provider='google_workspace',
            code='test_auth_code',
            client_id='test_client',
            client_secret='test_secret',
            redirect_uri='https://app.example.com/oauth/callback'
        )

        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'expires_in' in result
        assert result['token_type'] == 'Bearer'

    def test_get_oauth_user_info(self, sso_service):
        """Test getting user info from OAuth provider"""
        user_info = sso_service.get_oauth_user_info(
            provider='google_workspace',
            access_token='test_access_token'
        )

        assert 'email' in user_info
        assert 'first_name' in user_info
        assert 'last_name' in user_info
        assert user_info['authentication_method'] == 'oauth2'


class TestLDAPAuthentication:
    """Test LDAP authentication"""

    def test_authenticate_ldap_success(self, sso_service):
        """Test successful LDAP authentication"""
        user_info = sso_service.authenticate_ldap(
            username='john.doe',
            password='test_password',
            ldap_server='ldap.example.com',
            base_dn='dc=example,dc=com',
            use_ssl=True
        )

        assert 'email' in user_info
        assert 'first_name' in user_info
        assert user_info['authentication_method'] == 'ldap'

    def test_authenticate_ldap_missing_credentials(self, sso_service):
        """Test LDAP authentication with missing credentials"""
        with pytest.raises(ValueError, match="Username and password required"):
            sso_service.authenticate_ldap(
                username='',
                password='',
                ldap_server='ldap.example.com',
                base_dn='dc=example,dc=com'
            )


class TestUserProvisioning:
    """Test JIT user provisioning"""

    def test_provision_new_user(self, sso_service, test_tenant, db):
        """Test provisioning new user via SSO"""
        user_info = {
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'idp_user_id': 'idp_123',
            'authentication_method': 'saml2'
        }

        user = sso_service.provision_user_jit(
            tenant_id=test_tenant.id,
            user_info=user_info
        )

        assert user.email == 'jane@example.com'
        assert user.first_name == 'Jane'
        assert user.last_name == 'Smith'
        assert user.keycloak_id == 'idp_123'
        assert user.is_active is True
        assert user.last_login is not None

        # Check audit log
        audit = db.query(AuditLog).filter_by(
            tenant_id=test_tenant.id,
            action='sso_user_provisioned'
        ).first()
        assert audit is not None

    def test_provision_existing_user(self, sso_service, test_tenant, db):
        """Test provisioning existing user updates last_login"""
        # Create existing user
        existing_user = User(
            tenant_id=test_tenant.id,
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            is_active=True
        )
        db.add(existing_user)
        db.commit()

        user_info = {
            'email': 'existing@example.com',
            'first_name': 'Existing',
            'last_name': 'User',
            'idp_user_id': 'idp_456'
        }

        user = sso_service.provision_user_jit(
            tenant_id=test_tenant.id,
            user_info=user_info
        )

        assert user.id == existing_user.id
        assert user.last_login is not None


class TestSessionManagement:
    """Test SSO session management"""

    def test_create_sso_session(self, sso_service, test_tenant, db):
        """Test creating SSO session"""
        user = User(
            tenant_id=test_tenant.id,
            email='user@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        db.add(user)
        db.commit()

        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=test_tenant.id,
            authentication_method='saml2',
            idp_session_id='idp_session_123'
        )

        assert 'access_token' in session_data
        assert 'token_type' in session_data
        assert 'expires_in' in session_data
        assert 'session_id' in session_data
        assert session_data['token_type'] == 'Bearer'

        # Verify token payload
        from app.config import settings
        payload = jwt.decode(
            session_data['access_token'],
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        assert payload['user_id'] == str(user.id)
        assert payload['authentication_method'] == 'saml2'

    def test_validate_sso_session_success(self, sso_service, test_tenant, db):
        """Test validating valid SSO session"""
        user = User(
            tenant_id=test_tenant.id,
            email='user@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        db.add(user)
        db.commit()

        # Create session
        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=test_tenant.id,
            authentication_method='oauth2'
        )

        # Validate session
        payload = sso_service.validate_sso_session(session_data['access_token'])

        assert payload['user_id'] == str(user.id)
        assert payload['tenant_id'] == str(test_tenant.id)

    def test_validate_expired_session(self, sso_service):
        """Test validating expired session"""
        from app.config import settings

        # Create expired token
        expired_payload = {
            'user_id': str(uuid4()),
            'tenant_id': str(uuid4()),
            'exp': (datetime.utcnow() - timedelta(hours=1)).timestamp()
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm='HS256')

        with pytest.raises(ValueError, match="Session expired"):
            sso_service.validate_sso_session(expired_token)

    def test_logout_sso_session(self, sso_service, test_tenant, db):
        """Test SSO logout"""
        user = User(
            tenant_id=test_tenant.id,
            email='user@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        db.add(user)
        db.commit()

        # Create session
        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=test_tenant.id,
            authentication_method='saml2',
            idp_session_id='idp_session_789'
        )

        # Logout
        result = sso_service.logout_sso_session(
            access_token=session_data['access_token'],
            initiate_idp_logout=True
        )

        assert result['status'] == 'logged_out'
        assert 'idp_logout_url' in result

        # Check audit log
        audit = db.query(AuditLog).filter_by(
            tenant_id=test_tenant.id,
            action='sso_session_logout'
        ).first()
        assert audit is not None


class TestMultiIdPSupport:
    """Test Multi-IdP management"""

    def test_list_configured_idps(self, sso_service, test_tenant):
        """Test listing configured IdPs"""
        idps = sso_service.list_configured_idps(test_tenant.id)

        assert len(idps) > 0
        assert all('idp_id' in idp for idp in idps)
        assert all('name' in idp for idp in idps)
        assert all('protocol' in idp for idp in idps)

    def test_get_idp_config(self, sso_service, test_tenant):
        """Test getting specific IdP configuration"""
        idp_id = uuid4()
        config = sso_service.get_idp_config(test_tenant.id, idp_id)

        assert 'idp_id' in config
        assert 'entity_id' in config
        assert 'sso_url' in config
        assert 'protocol' in config
