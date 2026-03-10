"""NetZero ESG Platform API"""
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import uuid
from datetime import datetime
import os
from pathlib import Path

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
from app.routes.auth import router as auth_router
from app.routes.organizations import router as org_router
from app.routes.telemetry import router as telemetry_router
from app.routes.dashboards import router as dashboards_router
from app.routes.carbon import router as carbon_router
from app.routes.kpi import router as kpi_router
from app.routes.marketplace import router as marketplace_router
from app.routes.reporting import router as reporting_router
from app.routes.workflow import router as workflow_router

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
app.include_router(auth_router)  # Authentication routes
app.include_router(org_router)
app.include_router(telemetry_router)
app.include_router(dashboards_router)
app.include_router(carbon_router)
app.include_router(kpi_router)
app.include_router(marketplace_router)
app.include_router(reporting_router)
app.include_router(workflow_router)

# Mount frontend assets
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    # Mount static assets under /assets
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    logger.info(f"Frontend assets mounted from: {frontend_dist / 'assets'}")
else:
    logger.warning(f"Frontend dist directory not found at: {frontend_dist}")

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


# Authentication endpoints are now in app.routes.auth
# This keeps main.py clean and separates concerns


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


# Serve frontend index.html for all non-API routes (SPA routing)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve frontend SPA - returns index.html for all non-API routes
    This allows React Router to handle all client-side routes
    """
    # Don't serve index.html for API routes or assets
    if full_path.startswith("api/") or full_path.startswith("assets/"):
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Not found"}, status_code=404)

    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    index_path = frontend_dist / "index.html"

    if index_path.exists():
        return FileResponse(index_path)

    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "Frontend not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
