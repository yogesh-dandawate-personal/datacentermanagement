"""
RBAC API Endpoints - Sprint 14

REST endpoints for:
- Role management (CRUD)
- Permission queries
- User role assignment
- Permission checking
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid
from pydantic import BaseModel

from ..database import get_db
from ..auth.jwt_handler import get_current_user
from ..services.rbac_service import RBACService
from ..models import (
    RoleEnhanced, Permission, UserRoleEnhanced, User
)

router = APIRouter(prefix="/api/v1/rbac", tags=["rbac"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class PermissionResponse(BaseModel):
    """Permission response model"""
    id: str
    resource: str
    action: str
    permission_name: str
    permission_description: Optional[str] = None
    is_system: bool

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Role response model"""
    id: str
    tenant_id: str
    role_name: str
    role_display_name: Optional[str] = None
    role_description: Optional[str] = None
    is_system_role: bool
    is_active: bool
    role_category: str
    permissions: List[str] = []

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Create role request"""
    role_name: str
    role_display_name: str
    role_description: Optional[str] = None
    permission_ids: List[str] = []


class RoleUpdate(BaseModel):
    """Update role request"""
    role_display_name: Optional[str] = None
    role_description: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleResponse(BaseModel):
    """User role assignment response"""
    id: str
    user_id: str
    role_id: str
    role_name: str
    role_display_name: str
    organization_id: Optional[str] = None
    facility_id: Optional[str] = None
    expires_at: Optional[str] = None
    granted_at: str
    is_active: bool

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    """Assign role to user request"""
    user_id: str
    role_id: str
    organization_id: Optional[str] = None
    facility_id: Optional[str] = None
    expires_in_days: Optional[int] = None
    grant_reason: Optional[str] = None


class PermissionCheckRequest(BaseModel):
    """Check permission request"""
    resource: str
    action: str
    organization_id: Optional[str] = None
    facility_id: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    """Check permission response"""
    has_permission: bool
    resource: str
    action: str
    user_id: str


# ============================================================================
# ROLE ENDPOINTS
# ============================================================================

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_system_only: bool = False
):
    """List all roles for tenant"""
    query = db.query(RoleEnhanced).filter_by(tenant_id=current_user['tenant_id'])

    if is_system_only:
        query = query.filter_by(is_system_role=True)

    roles = query.offset(skip).limit(limit).all()

    # Fetch permissions for each role
    result = []
    for role in roles:
        perms = db.query(Permission.permission_name).join(
            __import__('sqlalchemy').orm.relationship(Permission)
        ).filter(__import__('sqlalchemy').orm.relationship(Permission).role_id == role.id).all()

        result.append(RoleResponse(
            id=str(role.id),
            tenant_id=str(role.tenant_id),
            role_name=role.role_name,
            role_display_name=role.role_display_name,
            role_description=role.role_description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            role_category=role.role_category,
            permissions=[p[0] for p in perms]
        ))

    return result


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    role_create: RoleCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a custom role"""
    # Only ESG managers can create roles
    rbac_service = RBACService(db)
    if not rbac_service.check_permission(
        user_id=UUID(current_user['user_id']),
        resource='admin',
        action='manage_roles'
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    # Check role doesn't exist
    existing = db.query(RoleEnhanced).filter_by(
        tenant_id=current_user['tenant_id'],
        role_name=role_create.role_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    # Create role
    role = RoleEnhanced(
        tenant_id=UUID(current_user['tenant_id']),
        role_name=role_create.role_name,
        role_display_name=role_create.role_display_name,
        role_description=role_create.role_description,
        is_system_role=False,
        is_active=True,
        role_category='custom',
        created_by=UUID(current_user['user_id'])
    )
    db.add(role)
    db.flush()

    # Assign permissions
    from ..models import RolePermission
    for perm_id in role_create.permission_ids:
        perm = db.query(Permission).filter_by(id=UUID(perm_id)).first()
        if perm:
            role_perm = RolePermission(
                role_id=role.id,
                permission_id=perm.id,
                granted=True
            )
            db.add(role_perm)

    db.commit()

    return RoleResponse(
        id=str(role.id),
        tenant_id=str(role.tenant_id),
        role_name=role.role_name,
        role_display_name=role.role_display_name,
        role_description=role.role_description,
        is_system_role=role.is_system_role,
        is_active=role.is_active,
        role_category=role.role_category,
        permissions=role_create.permission_ids
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific role"""
    role = db.query(RoleEnhanced).filter_by(
        id=UUID(role_id),
        tenant_id=current_user['tenant_id']
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    rbac_service = RBACService(db)
    perms = rbac_service.get_role_permissions(role.id)

    return RoleResponse(
        id=str(role.id),
        tenant_id=str(role.tenant_id),
        role_name=role.role_name,
        role_display_name=role.role_display_name,
        role_description=role.role_description,
        is_system_role=role.is_system_role,
        is_active=role.is_active,
        role_category=role.role_category,
        permissions=perms
    )


# ============================================================================
# PERMISSION ENDPOINTS
# ============================================================================

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    resource: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    """List all available permissions"""
    query = db.query(Permission)

    if resource:
        query = query.filter_by(resource=resource)

    permissions = query.offset(skip).limit(limit).all()

    return [
        PermissionResponse(
            id=str(p.id),
            resource=p.resource,
            action=p.action,
            permission_name=p.permission_name,
            permission_description=p.permission_description,
            is_system=p.is_system
        )
        for p in permissions
    ]


# ============================================================================
# USER ROLE ENDPOINTS
# ============================================================================

@router.get("/users/{user_id}/roles", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roles assigned to a user"""
    user = db.query(User).filter_by(id=UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_roles = db.query(UserRoleEnhanced).filter_by(user_id=UUID(user_id)).all()

    return [
        UserRoleResponse(
            id=str(ur.id),
            user_id=str(ur.user_id),
            role_id=str(ur.role_id),
            role_name=ur.role.role_name,
            role_display_name=ur.role.role_display_name,
            organization_id=str(ur.organization_id) if ur.organization_id else None,
            facility_id=str(ur.facility_id) if ur.facility_id else None,
            expires_at=ur.expires_at.isoformat() if ur.expires_at else None,
            granted_at=ur.granted_at.isoformat(),
            is_active=ur.is_active
        )
        for ur in user_roles
    ]


@router.post("/users/assign-role", status_code=201)
async def assign_role(
    assign_request: UserRoleAssign,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a role to a user"""
    rbac_service = RBACService(db)

    # Check permission to assign roles
    if not rbac_service.check_permission(
        user_id=UUID(current_user['user_id']),
        resource='users',
        action='assign_roles'
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    # Assign role
    try:
        user_role = rbac_service.assign_role(
            user_id=UUID(assign_request.user_id),
            role_id=UUID(assign_request.role_id),
            granted_by=UUID(current_user['user_id']),
            organization_id=UUID(assign_request.organization_id) if assign_request.organization_id else None,
            facility_id=UUID(assign_request.facility_id) if assign_request.facility_id else None,
            expires_in_days=assign_request.expires_in_days,
            grant_reason=assign_request.grant_reason
        )

        return {
            "id": str(user_role.id),
            "user_id": str(user_role.user_id),
            "role_id": str(user_role.role_id),
            "message": "Role assigned successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/revoke-role/{user_role_id}")
async def revoke_role(
    user_role_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a role assignment from a user"""
    rbac_service = RBACService(db)

    # Check permission
    if not rbac_service.check_permission(
        user_id=UUID(current_user['user_id']),
        resource='users',
        action='assign_roles'
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    # Revoke role
    try:
        rbac_service.revoke_role(
            user_role_id=UUID(user_role_id),
            revoked_by=UUID(current_user['user_id'])
        )
        return {"message": "Role revoked successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# PERMISSION CHECK ENDPOINT
# ============================================================================

@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_request: PermissionCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has a specific permission"""
    rbac_service = RBACService(db)

    has_permission = rbac_service.check_permission(
        user_id=UUID(current_user['user_id']),
        resource=check_request.resource,
        action=check_request.action,
        organization_id=UUID(check_request.organization_id) if check_request.organization_id else None,
        facility_id=UUID(check_request.facility_id) if check_request.facility_id else None,
        audit_log=True
    )

    return PermissionCheckResponse(
        has_permission=has_permission,
        resource=check_request.resource,
        action=check_request.action,
        user_id=current_user['user_id']
    )
