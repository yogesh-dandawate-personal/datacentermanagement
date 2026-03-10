"""
Tenant Isolation Middleware

This middleware extracts the tenant context from JWT tokens and makes it available
to all request handlers through request.state.

Architecture:
1. Extract JWT token from Authorization header
2. Decode token (already verified by route-level dependency)
3. Extract tenant_id from token payload
4. Add tenant_id to request.state for use in handlers
5. Add tenant_context dict with user_id, tenant_id, roles

Error Handling:
- Missing Authorization header: Pass through (routes will handle)
- Invalid token: Pass through (routes will handle)
- No tenant_id in token: Raise 401

Implementation Strategy:
- Use ASGI middleware for early tenant extraction
- Add to app before all routes
- Set request.state.tenant_id and request.state.tenant_context
- All route handlers depend on get_current_tenant() which reads request.state

Security Considerations:
- Tenant_id must be in signed JWT (cannot be spoofed)
- Each request must have tenant_id before reaching handlers
- No fallback to query params or cookies for tenant_id
- All database queries must filter by tenant_id

Performance:
- O(1) token decode (already signed, just extraction)
- O(1) state assignment
- No database lookups in middleware (defer to route level)

TODO: Implement after AUTH-FIX provides working JWT tokens
"""

from typing import Callable, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant context from JWT token.

    Sets request.state with:
    - tenant_id: UUID of tenant from JWT
    - tenant_context: Dict with user_id, tenant_id, roles
    - user_id: UUID of current user
    - roles: List of user roles
    """

    async def __call__(self, request: Request, call_next: Callable) -> object:
        """
        Process request to extract tenant context.

        Implementation Steps:
        1. Extract token from Authorization header (catch and ignore if missing)
        2. Verify token (catch and set flag if invalid)
        3. Extract tenant_id from token
        4. Add tenant_id to request.state
        5. Add full tenant_context to request.state
        6. Call next handler

        Args:
            request: Starlette request object
            call_next: Next middleware/handler in chain

        Returns:
            Response object

        Raises:
            (None - errors are handled by route-level dependencies)
        """

        # Implementation strategy:
        # - Don't raise errors here, let routes handle it
        # - Just extract what we can and add to state
        # - Routes use Depends(get_current_tenant()) to enforce auth

        try:
            # Step 1: Try to extract token from header
            token = extract_token_from_header(request.headers.get("authorization"))

            # Step 2: Verify and decode token
            token_data = verify_token(token)

            # Step 3: Extract tenant_id from decoded token
            tenant_id = token_data.tenant_id
            user_id = token_data.sub
            roles = token_data.roles or []

            # Step 4: Add to request state
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id
            request.state.roles = roles
            request.state.tenant_context = {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "roles": roles
            }

            logger.debug(f"Tenant context set: tenant_id={tenant_id}, user_id={user_id}")

        except Exception as e:
            # If token extraction/verification fails, don't set state
            # Route-level Depends(get_current_tenant()) will raise 401
            logger.debug(f"Could not extract tenant from token: {str(e)}")
            request.state.tenant_id = None
            request.state.user_id = None
            request.state.tenant_context = None

        # Step 5: Call next handler in chain
        response = await call_next(request)

        # Optional: Add tenant info to response headers for debugging
        # response.headers["X-Tenant-ID"] = str(request.state.tenant_id or "unknown")

        return response


# Dependency Injection Function
# This will be used in all route handlers to get current tenant

async def get_current_tenant(request: Request) -> dict:
    """
    Dependency to get current tenant context from request state.

    MUST be used in all route handlers that need tenant validation.

    Usage in route:
    ```python
    @router.get("/orgs/{org_id}")
    async def get_organization(
        org_id: str,
        current_tenant: dict = Depends(get_current_tenant),
        db: Session = Depends(get_db)
    ):
        # current_tenant = {
        #     "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        #     "user_id": "550e8400-e29b-41d4-a716-446655440001",
        #     "roles": ["admin", "editor"]
        # }
        org = db.query(Organization).filter(
            Organization.id == org_id,
            Organization.tenant_id == current_tenant["tenant_id"]  # CRITICAL
        ).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org
    ```

    Args:
        request: FastAPI request object

    Returns:
        Dict with tenant_id, user_id, roles

    Raises:
        HTTPException(401): If tenant context not found in request state
    """

    # Get tenant context from middleware
    tenant_context = getattr(request.state, "tenant_context", None)

    if not tenant_context or not tenant_context.get("tenant_id"):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Tenant context not found. Invalid or missing token."
        )

    return tenant_context


# Alternative: Direct dependency if we only need tenant_id (for simple cases)
async def get_current_tenant_id(request: Request) -> str:
    """
    Dependency to get just the tenant_id.

    Simpler version for cases where you only need tenant_id.

    Usage:
    ```python
    @router.get("/orgs")
    async def list_organizations(
        tenant_id: str = Depends(get_current_tenant_id),
        db: Session = Depends(get_db)
    ):
        orgs = db.query(Organization).filter_by(tenant_id=tenant_id).all()
        return orgs
    ```

    Args:
        request: FastAPI request object

    Returns:
        Tenant ID string

    Raises:
        HTTPException(401): If tenant_id not found
    """

    tenant_id = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Tenant context not found. Invalid or missing token."
        )

    return tenant_id
