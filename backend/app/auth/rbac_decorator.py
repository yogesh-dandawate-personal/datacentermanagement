"""
RBAC Authorization Decorator - Sprint 14

Provides @require_permission() decorator for FastAPI endpoints
to enforce role-based access control.
"""

from functools import wraps
from typing import Optional
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
import redis

from ..services.rbac_service import RBACService
from .jwt_handler import get_current_user
from ..database import get_db


def require_permission(
    resource: str,
    action: str,
    scoped_by_org: bool = False,
    scoped_by_facility: bool = False
):
    """
    Decorator for FastAPI endpoints to enforce permission checks

    Args:
        resource: Resource type (organizations, facilities, emissions, etc.)
        action: Action type (create, read, update, delete, approve, etc.)
        scoped_by_org: If True, check org_id from path/query params
        scoped_by_facility: If True, check facility_id from path/query params

    Usage:
        @router.post("/facilities")
        @require_permission("facilities", "create")
        async def create_facility(
            facility: FacilityCreate,
            current_user: dict = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            pass

        @router.get("/facilities/{facility_id}/emissions")
        @require_permission("emissions", "read", scoped_by_facility=True)
        async def get_facility_emissions(
            facility_id: str,
            current_user: dict = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            pass
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db), **kwargs):
            # Get user_id and tenant_id from current_user
            user_id = current_user.get('user_id')
            tenant_id = current_user.get('tenant_id')

            if not user_id or not tenant_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            # Initialize RBAC service
            redis_client = None
            try:
                redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                redis_client.ping()
            except Exception:
                pass  # Redis is optional

            rbac_service = RBACService(db, redis_client)

            # Extract scope parameters if needed
            org_id = None
            facility_id = None

            if scoped_by_org:
                # Try to get from kwargs first (path parameter)
                org_id = kwargs.get('org_id') or kwargs.get('organization_id')

            if scoped_by_facility:
                # Try to get from kwargs first (path parameter)
                facility_id = kwargs.get('facility_id')

            # Get request info for audit logging
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            ip_address = request.client.host if request else None
            user_agent = request.headers.get('user-agent') if request else None

            # Check permission
            has_permission = rbac_service.check_permission(
                user_id=user_id,
                resource=resource,
                action=action,
                organization_id=org_id,
                facility_id=facility_id,
                ip_address=ip_address,
                user_agent=user_agent,
                audit_log=True
            )

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: {resource}:{action}"
                )

            # Call original function with injected dependencies
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator


def require_one_of_permissions(permissions: list):
    """
    Decorator that requires at least one of the given permissions

    Args:
        permissions: List of (resource, action) tuples

    Usage:
        @router.get("/reports")
        @require_one_of_permissions([
            ("reports", "read"),
            ("reports", "generate")
        ])
        async def get_reports(...):
            pass
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db), **kwargs):
            user_id = current_user.get('user_id')
            tenant_id = current_user.get('tenant_id')

            if not user_id or not tenant_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            # Initialize RBAC service
            redis_client = None
            try:
                redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                redis_client.ping()
            except Exception:
                pass

            rbac_service = RBACService(db, redis_client)

            # Check if user has any of the permissions
            has_any_permission = False
            for resource, action in permissions:
                if rbac_service.check_permission(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    audit_log=False  # Don't spam audit logs
                ):
                    has_any_permission = True
                    break

            if not has_any_permission:
                permission_list = ', '.join([f"{r}:{a}" for r, a in permissions])
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: requires one of {permission_list}"
                )

            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator


def require_all_permissions(permissions: list):
    """
    Decorator that requires ALL of the given permissions

    Args:
        permissions: List of (resource, action) tuples
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db), **kwargs):
            user_id = current_user.get('user_id')
            tenant_id = current_user.get('tenant_id')

            if not user_id or not tenant_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            # Initialize RBAC service
            redis_client = None
            try:
                redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                redis_client.ping()
            except Exception:
                pass

            rbac_service = RBACService(db, redis_client)

            # Check if user has ALL permissions
            for resource, action in permissions:
                if not rbac_service.check_permission(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    audit_log=False
                ):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access denied: requires {resource}:{action}"
                    )

            return await func(*args, current_user=current_user, db=db, **kwargs)

        return wrapper

    return decorator
