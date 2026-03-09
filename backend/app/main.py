"""NetZero ESG Platform API"""
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime

from app.auth.jwt_handler import create_access_token, verify_token
from app.auth.utils import extract_token_from_header, validate_token_format
from app.exceptions import (
    NetZeroException,
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.schemas import (
    TenantCreate,
    TenantResponse,
    LoginRequest,
    LoginResponse,
    ErrorResponse,
    HealthCheckResponse,
)
from app.routes.organizations import router as org_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NetZero API",
    description="Multi-tenant ESG & Carbon Credit Platform",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS middleware - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to known origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(org_router)

# Global exception handler
@app.exception_handler(NetZeroException)
async def netzero_exception_handler(request: Request, exc: NetZeroException):
    """Handle custom NetZero exceptions"""
    logger.error(f"NetZero exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected exception: {str(exc)}", exc_info=True)

    # Return more helpful error messages
    error_message = "An unexpected error occurred"
    if "database" in str(exc).lower() or "connection" in str(exc).lower():
        error_message = "Database connection failed. Please check DATABASE_URL environment variable."

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": error_message,
            "status_code": 500,
            "detail": {
                "error_type": exc.__class__.__name__,
                "error_msg": str(exc)[:200]  # Truncate to 200 chars for safety
            },
        },
    )


# Routes
@app.post("/api/v1/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(tenant: TenantCreate):
    """
    Create new tenant

    This endpoint initializes a new tenant in the multi-tenant system.
    Each tenant is completely isolated with separate data, users, and configurations.

    Args:
        tenant: Tenant creation request with name, slug, and email

    Returns:
        TenantResponse with created tenant details
    """
    logger.info(f"Creating tenant: {tenant.slug}")

    tenant_id = str(uuid.uuid4())

    # TODO: Save to database
    # tenant_obj = Tenant(**tenant.dict(), id=tenant_id)
    # db.add(tenant_obj)
    # db.commit()

    return TenantResponse(
        id=tenant_id,
        name=tenant.name,
        slug=tenant.slug,
        email=tenant.email,
        is_active=True,
        created_at=datetime.utcnow(),
    )


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    User login endpoint

    Authenticates user and returns JWT access token for subsequent API calls.

    Args:
        credentials: Email and password

    Returns:
        LoginResponse with access token and user details

    Raises:
        AuthenticationError: If credentials are invalid
    """
    logger.info(f"Login attempt for user: {credentials.email}")

    # TODO: Validate against database or Keycloak
    if not credentials.email or not credentials.password:
        raise AuthenticationError("Email and password are required")

    # Mock user validation - replace with real authentication
    user_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    user_roles = ["admin", "editor"]

    token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=user_roles,
    )

    logger.info(f"User logged in successfully: {user_id}")

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        tenant_id=tenant_id,
        roles=user_roles,
    )


@app.get("/api/v1/users/me")
async def get_current_user(authorization: str = Header(None)):
    """
    Get current authenticated user

    Returns details of the authenticated user from JWT token.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        User details including id, tenant_id, and roles

    Raises:
        AuthenticationError: If Authorization header is missing
        InvalidTokenError: If token is invalid
        TokenExpiredError: If token has expired
    """
    try:
        token = extract_token_from_header(authorization)

        if not validate_token_format(token):
            raise InvalidTokenError("Token has invalid format")

        token_data = verify_token(token)

        logger.info(f"Retrieved user info for: {token_data.sub}")

        return {
            "id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }

    except (AuthenticationError, InvalidTokenError, TokenExpiredError):
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise InvalidTokenError("Failed to retrieve user information")


@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint

    Returns service status and version information.

    Returns:
        HealthCheckResponse with status, service name, and version
    """
    return HealthCheckResponse(
        status="healthy",
        service="NetZero API",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
