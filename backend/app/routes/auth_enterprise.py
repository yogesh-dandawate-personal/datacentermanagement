"""
Enterprise Authentication Routes - Sprint 13 (AGENT 1)

Provides SSO/SAML endpoints for:
- SAML 2.0 login/callback
- OAuth 2.0 flows
- LDAP authentication
- Session management
- Multi-IdP support
"""

from fastapi import APIRouter, Depends, HTTPException, Form, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..services.sso_service import SSOService
from ..middleware.tenant import get_current_tenant
from ..models import User, Tenant

router = APIRouter(prefix="/api/v1/auth/enterprise", tags=["Enterprise Auth"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SAMLInitiateRequest(BaseModel):
    """Request to initiate SAML login"""
    idp_id: UUID
    relay_state: Optional[str] = None


class SAMLCallbackRequest(BaseModel):
    """SAML callback with assertion"""
    SAMLResponse: str
    RelayState: Optional[str] = None


class OAuthInitiateRequest(BaseModel):
    """Request to initiate OAuth login"""
    provider: str  # google_workspace, azure_ad, etc.
    scopes: List[str] = ["openid", "email", "profile"]


class OAuthCallbackRequest(BaseModel):
    """OAuth callback with authorization code"""
    code: str
    state: str


class LDAPAuthRequest(BaseModel):
    """LDAP authentication request"""
    username: str
    password: str
    ldap_server: Optional[str] = None
    base_dn: Optional[str] = None


class SessionResponse(BaseModel):
    """SSO session response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    expires_at: str
    session_id: str
    user: Dict[str, Any]


class IdPListResponse(BaseModel):
    """List of configured IdPs"""
    idps: List[Dict[str, Any]]
    default_idp_id: Optional[UUID] = None


# ============================================================================
# SAML 2.0 ENDPOINTS
# ============================================================================

@router.post("/saml/login", response_class=RedirectResponse, status_code=302)
async def saml_login(
    request: SAMLInitiateRequest,
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Initiate SAML 2.0 login flow

    This endpoint generates a SAML AuthnRequest and redirects the user
    to the configured Identity Provider for authentication.

    Args:
        request: SAML initiation parameters
        tenant_id: Current tenant
        db: Database session

    Returns:
        302 redirect to IdP SSO URL
    """
    sso_service = SSOService(db)

    try:
        # Get IdP configuration
        idp_config = sso_service.get_idp_config(tenant_id, request.idp_id)

        # Generate SAML request
        saml_data = sso_service.generate_saml_request(
            tenant_id=tenant_id,
            idp_config=idp_config,
            relay_state=request.relay_state
        )

        # Redirect to IdP
        return RedirectResponse(
            url=saml_data['redirect_url'],
            status_code=302
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAML login failed: {str(e)}")


@router.post("/saml/acs", response_model=SessionResponse)
async def saml_acs(
    SAMLResponse: str = Form(...),
    RelayState: Optional[str] = Form(None),
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    SAML Assertion Consumer Service (ACS) - callback endpoint

    This endpoint receives the SAML Response from the IdP after
    successful authentication, validates it, and creates a session.

    Args:
        SAMLResponse: Base64-encoded SAML assertion
        RelayState: Optional state from initial request
        tenant_id: Current tenant
        db: Database session

    Returns:
        Session token and user information
    """
    sso_service = SSOService(db)

    try:
        # Process SAML response
        user_info = sso_service.process_saml_response(
            saml_response=SAMLResponse,
            relay_state=RelayState
        )

        # Provision user (JIT)
        user = sso_service.provision_user_jit(
            tenant_id=tenant_id,
            user_info=user_info
        )

        # Create session
        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=tenant_id,
            authentication_method='saml2'
        )

        return SessionResponse(
            **session_data,
            user={
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAML assertion processing failed: {str(e)}")


@router.get("/saml/metadata")
async def saml_metadata(
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get SAML Service Provider metadata

    Returns SAML SP metadata XML for IdP configuration.

    Returns:
        XML metadata document
    """
    from ..config import settings

    metadata_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{settings.SAML_ENTITY_ID}">
    <md:SPSSODescriptor
        AuthnRequestsSigned="false"
        WantAssertionsSigned="true"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{settings.SAML_ACS_URL}"
            index="0"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""

    return JSONResponse(
        content=metadata_xml,
        media_type="application/xml"
    )


# ============================================================================
# OAuth 2.0 ENDPOINTS
# ============================================================================

@router.post("/oauth/login", response_class=RedirectResponse, status_code=302)
async def oauth_login(
    request: OAuthInitiateRequest,
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Initiate OAuth 2.0 login flow

    Generates OAuth authorization URL and redirects user to IdP.

    Args:
        request: OAuth initiation parameters
        tenant_id: Current tenant
        db: Database session

    Returns:
        302 redirect to OAuth provider
    """
    sso_service = SSOService(db)

    try:
        # Get OAuth config for tenant (in production, from database)
        # For now, using mock config
        from ..config import settings

        oauth_url = sso_service.generate_oauth_url(
            provider=request.provider,
            client_id=settings.OAUTH_CLIENT_ID,
            redirect_uri=settings.OAUTH_REDIRECT_URI,
            scopes=request.scopes,
            state=str(tenant_id)
        )

        return RedirectResponse(url=oauth_url, status_code=302)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth login failed: {str(e)}")


@router.get("/oauth/callback", response_model=SessionResponse)
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    provider: str = Query("google_workspace"),
    db: Session = Depends(get_db)
):
    """
    OAuth 2.0 callback endpoint

    Receives authorization code from OAuth provider, exchanges for
    access token, and creates session.

    Args:
        code: Authorization code
        state: State parameter (contains tenant_id)
        provider: OAuth provider name
        db: Database session

    Returns:
        Session token and user information
    """
    sso_service = SSOService(db)

    try:
        tenant_id = UUID(state)

        # Exchange code for tokens
        from ..config import settings

        token_data = sso_service.exchange_oauth_code(
            provider=provider,
            code=code,
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            redirect_uri=settings.OAUTH_REDIRECT_URI
        )

        # Get user info from OAuth provider
        user_info = sso_service.get_oauth_user_info(
            provider=provider,
            access_token=token_data['access_token']
        )

        # Provision user (JIT)
        user = sso_service.provision_user_jit(
            tenant_id=tenant_id,
            user_info=user_info
        )

        # Create session
        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=tenant_id,
            authentication_method='oauth2'
        )

        return SessionResponse(
            **session_data,
            user={
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


# ============================================================================
# LDAP ENDPOINTS
# ============================================================================

@router.post("/ldap/login", response_model=SessionResponse)
async def ldap_login(
    request: LDAPAuthRequest,
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Authenticate via LDAP/Active Directory

    Args:
        request: LDAP credentials
        tenant_id: Current tenant
        db: Database session

    Returns:
        Session token and user information
    """
    sso_service = SSOService(db)

    try:
        # Get LDAP config for tenant (in production, from database)
        from ..config import settings

        ldap_server = request.ldap_server or settings.LDAP_SERVER
        base_dn = request.base_dn or settings.LDAP_BASE_DN

        # Authenticate via LDAP
        user_info = sso_service.authenticate_ldap(
            username=request.username,
            password=request.password,
            ldap_server=ldap_server,
            base_dn=base_dn,
            use_ssl=True
        )

        # Provision user (JIT)
        user = sso_service.provision_user_jit(
            tenant_id=tenant_id,
            user_info=user_info
        )

        # Create session
        session_data = sso_service.create_sso_session(
            user_id=user.id,
            tenant_id=tenant_id,
            authentication_method='ldap'
        )

        return SessionResponse(
            **session_data,
            user={
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LDAP authentication failed: {str(e)}")


# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/logout")
async def sso_logout(
    request: Request,
    initiate_idp_logout: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Logout SSO session (Single Logout)

    Args:
        request: HTTP request with Authorization header
        initiate_idp_logout: Whether to initiate IdP logout
        db: Database session

    Returns:
        Logout confirmation
    """
    sso_service = SSOService(db)

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        access_token = auth_header.split(' ')[1]

        # Logout session
        logout_result = sso_service.logout_sso_session(
            access_token=access_token,
            initiate_idp_logout=initiate_idp_logout
        )

        return logout_result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.get("/session/validate")
async def validate_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Validate current SSO session

    Args:
        request: HTTP request with Authorization header
        db: Database session

    Returns:
        Session validity and user info
    """
    sso_service = SSOService(db)

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        access_token = auth_header.split(' ')[1]

        # Validate session
        payload = sso_service.validate_sso_session(access_token)

        # Get user from database
        user = db.query(User).filter_by(id=UUID(payload['user_id'])).first()

        return {
            'valid': True,
            'session_id': payload.get('session_id'),
            'authentication_method': payload.get('authentication_method'),
            'expires_at': datetime.fromtimestamp(payload['exp']).isoformat(),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation failed: {str(e)}")


# ============================================================================
# IDP MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/idps", response_model=IdPListResponse)
async def list_idps(
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    List all configured Identity Providers for tenant

    Args:
        tenant_id: Current tenant
        db: Database session

    Returns:
        List of configured IdPs
    """
    sso_service = SSOService(db)

    try:
        idps = sso_service.list_configured_idps(tenant_id)

        # Find default/primary IdP
        default_idp = next((idp for idp in idps if idp.get('is_primary')), None)

        return IdPListResponse(
            idps=idps,
            default_idp_id=UUID(default_idp['idp_id']) if default_idp else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list IdPs: {str(e)}")


@router.get("/idps/{idp_id}")
async def get_idp_config(
    idp_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get specific IdP configuration

    Args:
        idp_id: IdP identifier
        tenant_id: Current tenant
        db: Database session

    Returns:
        IdP configuration details
    """
    sso_service = SSOService(db)

    try:
        idp_config = sso_service.get_idp_config(tenant_id, idp_id)
        return idp_config

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get IdP config: {str(e)}")
