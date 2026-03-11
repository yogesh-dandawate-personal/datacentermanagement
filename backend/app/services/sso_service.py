"""
SSO/SAML Service Layer - Sprint 13 (AGENT 1)

Provides enterprise authentication via:
- SAML 2.0 (Single Sign-On)
- OAuth 2.0 (Google, Microsoft, Okta)
- LDAP (Active Directory integration)
- Multi-IdP support
- Session management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_
import jwt
import hashlib
import base64
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urlencode

from ..models import User, Tenant, AuditLog
from ..config import settings


class SSOService:
    """Enterprise SSO/SAML Authentication Service"""

    # Supported Identity Providers
    SUPPORTED_IDPS = {
        'okta': {
            'name': 'Okta',
            'protocol': 'saml2',
            'metadata_url': 'https://{{tenant}}.okta.com/app/{{app_id}}/sso/saml/metadata'
        },
        'azure_ad': {
            'name': 'Microsoft Azure AD',
            'protocol': 'saml2',
            'metadata_url': 'https://login.microsoftonline.com/{{tenant_id}}/federationmetadata/2007-06/federationmetadata.xml'
        },
        'google_workspace': {
            'name': 'Google Workspace',
            'protocol': 'oauth2',
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo'
        },
        'onelogin': {
            'name': 'OneLogin',
            'protocol': 'saml2',
            'metadata_url': 'https://{{subdomain}}.onelogin.com/saml/metadata/{{app_id}}'
        },
        'ping_identity': {
            'name': 'Ping Identity',
            'protocol': 'saml2',
            'metadata_url': 'https://{{env}}.pingidentity.com/idp/{{connection_id}}/metadata'
        },
        'ldap': {
            'name': 'LDAP/Active Directory',
            'protocol': 'ldap',
            'default_port': 389,
            'secure_port': 636
        }
    }

    def __init__(self, db: Session):
        """
        Initialize SSO service

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    # ============================================================================
    # SAML 2.0 IMPLEMENTATION
    # ============================================================================

    def generate_saml_request(
        self,
        tenant_id: UUID,
        idp_config: Dict[str, Any],
        relay_state: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate SAML AuthnRequest for IdP-initiated SSO

        Args:
            tenant_id: Tenant requesting SSO
            idp_config: IdP configuration (entity_id, sso_url, etc.)
            relay_state: Optional state to preserve across redirect

        Returns:
            Dictionary with saml_request and redirect_url
        """
        tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        # Generate unique request ID
        request_id = f"_req_{uuid4().hex}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Build SAML AuthnRequest XML
        saml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp_config['sso_url']}"
    AssertionConsumerServiceURL="{settings.SAML_ACS_URL}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{settings.SAML_ENTITY_ID}</saml:Issuer>
    <samlp:NameIDPolicy
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        AllowCreate="true"/>
</samlp:AuthnRequest>"""

        # Base64 encode and URL encode
        encoded_request = base64.b64encode(saml_request.encode('utf-8')).decode('utf-8')
        url_encoded = quote_plus(encoded_request)

        # Build redirect URL
        params = {'SAMLRequest': url_encoded}
        if relay_state:
            params['RelayState'] = relay_state

        redirect_url = f"{idp_config['sso_url']}?{urlencode(params)}"

        return {
            'request_id': request_id,
            'saml_request': encoded_request,
            'redirect_url': redirect_url,
            'issued_at': issue_instant
        }

    def process_saml_response(
        self,
        saml_response: str,
        relay_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process SAML Response from IdP after authentication

        Args:
            saml_response: Base64-encoded SAML response
            relay_state: Optional relay state from request

        Returns:
            Dictionary with user info and session data
        """
        try:
            # Decode SAML response
            decoded = base64.b64decode(saml_response).decode('utf-8')

            # Parse XML
            root = ET.fromstring(decoded)

            # Extract namespaces
            ns = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }

            # Validate response status
            status_code = root.find('.//samlp:StatusCode', ns)
            if status_code is None or status_code.get('Value') != 'urn:oasis:names:tc:SAML:2.0:status:Success':
                raise ValueError("SAML authentication failed")

            # Extract assertion
            assertion = root.find('.//saml:Assertion', ns)
            if assertion is None:
                raise ValueError("No assertion found in SAML response")

            # Extract subject (user identifier)
            name_id = assertion.find('.//saml:NameID', ns)
            if name_id is None:
                raise ValueError("No NameID found in assertion")

            email = name_id.text

            # Extract attributes
            attributes = {}
            attr_statements = assertion.findall('.//saml:AttributeStatement/saml:Attribute', ns)

            for attr in attr_statements:
                attr_name = attr.get('Name')
                attr_value = attr.find('saml:AttributeValue', ns)
                if attr_value is not None:
                    attributes[attr_name] = attr_value.text

            # Map SAML attributes to user fields
            user_info = {
                'email': email,
                'first_name': attributes.get('firstName', attributes.get('givenName', '')),
                'last_name': attributes.get('lastName', attributes.get('surname', '')),
                'idp_user_id': attributes.get('uid', email),
                'idp_attributes': attributes,
                'authentication_method': 'saml2'
            }

            return user_info

        except ET.ParseError as e:
            raise ValueError(f"Invalid SAML response XML: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process SAML response: {str(e)}")

    # ============================================================================
    # OAuth 2.0 IMPLEMENTATION
    # ============================================================================

    def generate_oauth_url(
        self,
        provider: str,
        client_id: str,
        redirect_uri: str,
        scopes: List[str],
        state: Optional[str] = None
    ) -> str:
        """
        Generate OAuth 2.0 authorization URL

        Args:
            provider: OAuth provider (google_workspace, azure_ad, etc.)
            client_id: OAuth client ID
            redirect_uri: Callback URL after authentication
            scopes: List of OAuth scopes to request
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        if provider not in self.SUPPORTED_IDPS:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        idp_config = self.SUPPORTED_IDPS[provider]
        if idp_config['protocol'] != 'oauth2':
            raise ValueError(f"Provider {provider} does not support OAuth 2.0")

        # Generate state if not provided
        if not state:
            state = hashlib.sha256(str(uuid4()).encode()).hexdigest()

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'
        }

        auth_url = f"{idp_config['auth_url']}?{urlencode(params)}"
        return auth_url

    def exchange_oauth_code(
        self,
        provider: str,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access token

        Args:
            provider: OAuth provider
            code: Authorization code from callback
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Must match the redirect_uri from authorization request

        Returns:
            Dictionary with access_token, refresh_token, and user info
        """
        if provider not in self.SUPPORTED_IDPS:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        idp_config = self.SUPPORTED_IDPS[provider]

        # In production, this would make actual HTTP requests to IdP
        # For now, returning mock structure
        return {
            'access_token': f"mock_access_token_{uuid4().hex}",
            'refresh_token': f"mock_refresh_token_{uuid4().hex}",
            'expires_in': 3600,
            'token_type': 'Bearer',
            'scope': 'openid email profile'
        }

    def get_oauth_user_info(
        self,
        provider: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get user information from OAuth provider

        Args:
            provider: OAuth provider
            access_token: Access token from token exchange

        Returns:
            User profile information
        """
        if provider not in self.SUPPORTED_IDPS:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        # In production, this would make actual HTTP request to userinfo endpoint
        # For now, returning mock structure
        return {
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'idp_user_id': f"oauth_{uuid4().hex}",
            'authentication_method': 'oauth2',
            'provider': provider
        }

    # ============================================================================
    # LDAP IMPLEMENTATION
    # ============================================================================

    def authenticate_ldap(
        self,
        username: str,
        password: str,
        ldap_server: str,
        base_dn: str,
        use_ssl: bool = True
    ) -> Dict[str, Any]:
        """
        Authenticate user via LDAP/Active Directory

        Args:
            username: LDAP username
            password: User password
            ldap_server: LDAP server hostname
            base_dn: Base DN for search (e.g., "dc=example,dc=com")
            use_ssl: Whether to use LDAPS

        Returns:
            User information if authentication successful
        """
        port = 636 if use_ssl else 389

        # In production, this would use ldap3 library
        # For now, returning mock structure

        # Mock validation
        if not username or not password:
            raise ValueError("Username and password required")

        return {
            'email': f"{username}@example.com",
            'first_name': username.split('.')[0].title() if '.' in username else username,
            'last_name': username.split('.')[1].title() if '.' in username else '',
            'idp_user_id': username,
            'authentication_method': 'ldap',
            'ldap_dn': f"cn={username},{base_dn}"
        }

    # ============================================================================
    # USER PROVISIONING (JIT)
    # ============================================================================

    def provision_user_jit(
        self,
        tenant_id: UUID,
        user_info: Dict[str, Any],
        default_role_id: Optional[UUID] = None
    ) -> User:
        """
        Just-In-Time user provisioning after SSO authentication

        Args:
            tenant_id: Tenant to provision user in
            user_info: User information from IdP
            default_role_id: Optional default role to assign

        Returns:
            Created or existing User object
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            and_(
                User.tenant_id == tenant_id,
                User.email == user_info['email']
            )
        ).first()

        if existing_user:
            # Update last login
            existing_user.last_login = datetime.utcnow()
            self.db.commit()
            return existing_user

        # Create new user
        new_user = User(
            tenant_id=tenant_id,
            email=user_info['email'],
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            keycloak_id=user_info.get('idp_user_id'),
            is_active=True,
            last_login=datetime.utcnow()
        )

        self.db.add(new_user)
        self.db.flush()

        # Create audit log
        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=new_user.id,
            action='sso_user_provisioned',
            entity_type='user',
            entity_id=new_user.id,
            changes={
                'authentication_method': user_info.get('authentication_method'),
                'provisioned_at': datetime.utcnow().isoformat()
            }
        )
        self.db.add(audit)
        self.db.commit()

        return new_user

    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================

    def create_sso_session(
        self,
        user_id: UUID,
        tenant_id: UUID,
        authentication_method: str,
        idp_session_id: Optional[str] = None,
        expires_in_hours: int = 8
    ) -> Dict[str, Any]:
        """
        Create SSO session after successful authentication

        Args:
            user_id: Authenticated user
            tenant_id: User's tenant
            authentication_method: saml2, oauth2, ldap
            idp_session_id: Optional IdP session identifier
            expires_in_hours: Session expiration (default 8 hours)

        Returns:
            Session token and metadata
        """
        # Generate session token
        session_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        # Create JWT token
        token_payload = {
            'user_id': str(user_id),
            'tenant_id': str(tenant_id),
            'session_id': session_id,
            'authentication_method': authentication_method,
            'idp_session_id': idp_session_id,
            'exp': expires_at.timestamp(),
            'iat': datetime.utcnow().timestamp()
        }

        access_token = jwt.encode(
            token_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )

        # Create audit log
        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action='sso_session_created',
            entity_type='session',
            changes={
                'session_id': session_id,
                'authentication_method': authentication_method,
                'expires_at': expires_at.isoformat()
            }
        )
        self.db.add(audit)
        self.db.commit()

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in_hours * 3600,
            'expires_at': expires_at.isoformat(),
            'session_id': session_id
        }

    def validate_sso_session(self, access_token: str) -> Dict[str, Any]:
        """
        Validate SSO session token

        Args:
            access_token: JWT access token

        Returns:
            Decoded token payload if valid
        """
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Session expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid session token")

    def logout_sso_session(
        self,
        access_token: str,
        initiate_idp_logout: bool = True
    ) -> Dict[str, str]:
        """
        Logout SSO session (Single Logout)

        Args:
            access_token: Session token to invalidate
            initiate_idp_logout: Whether to initiate IdP logout

        Returns:
            Logout confirmation and optional IdP logout URL
        """
        try:
            payload = self.validate_sso_session(access_token)

            # Create audit log
            audit = AuditLog(
                tenant_id=UUID(payload['tenant_id']),
                user_id=UUID(payload['user_id']),
                action='sso_session_logout',
                entity_type='session',
                changes={
                    'session_id': payload.get('session_id'),
                    'logged_out_at': datetime.utcnow().isoformat()
                }
            )
            self.db.add(audit)
            self.db.commit()

            result = {'status': 'logged_out'}

            # If IdP logout requested, generate SAML LogoutRequest
            if initiate_idp_logout and payload.get('authentication_method') == 'saml2':
                # In production, this would generate proper SAML LogoutRequest
                result['idp_logout_url'] = f"{settings.SAML_IDP_LOGOUT_URL}?session={payload.get('idp_session_id')}"

            return result

        except ValueError as e:
            raise ValueError(f"Logout failed: {str(e)}")

    # ============================================================================
    # MULTI-IDP MANAGEMENT
    # ============================================================================

    def list_configured_idps(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        List all configured Identity Providers for a tenant

        Args:
            tenant_id: Tenant to query

        Returns:
            List of IdP configurations
        """
        # In production, this would query IdP configuration table
        # For now, returning supported IdPs
        return [
            {
                'idp_id': str(uuid4()),
                'name': config['name'],
                'protocol': config['protocol'],
                'enabled': True,
                'is_primary': i == 0
            }
            for i, (key, config) in enumerate(self.SUPPORTED_IDPS.items())
        ]

    def get_idp_config(self, tenant_id: UUID, idp_id: UUID) -> Dict[str, Any]:
        """Get specific IdP configuration for tenant"""
        # In production, this would query database
        # For now, returning mock config
        return {
            'idp_id': str(idp_id),
            'entity_id': 'https://idp.example.com/entity',
            'sso_url': 'https://idp.example.com/sso',
            'slo_url': 'https://idp.example.com/slo',
            'certificate': 'mock_certificate_data',
            'protocol': 'saml2'
        }
