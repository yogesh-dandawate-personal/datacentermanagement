"""Organization management API routes"""
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import uuid
from datetime import datetime

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.models import Organization, Department, Position, Tenant, User
from app.schemas import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["organizations"])


# Schemas for organization operations
class OrganizationCreate:
    """Request to create organization"""
    def __init__(self, name: str, slug: str, parent_id: Optional[str] = None,
                 description: Optional[str] = None, metadata: Optional[dict] = None):
        self.name = name
        self.slug = slug
        self.parent_id = parent_id
        self.description = description
        self.metadata = metadata or {}


class OrganizationResponse:
    """Organization response"""
    def __init__(self, org: Organization):
        self.id = str(org.id)
        self.tenant_id = str(org.tenant_id)
        self.parent_id = str(org.parent_id) if org.parent_id else None
        self.name = org.name
        self.slug = org.slug
        self.description = org.description
        self.hierarchy_level = org.hierarchy_level
        self.is_active = org.is_active
        self.created_at = org.created_at.isoformat()
        self.created_by = str(org.created_by) if org.created_by else None


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract and verify current user from token"""
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/orgs", response_model=dict, status_code=201)
async def create_organization(
    name: str,
    slug: str,
    parent_id: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new organization

    Creates an organization unit within tenant hierarchy.
    Can specify parent for hierarchical relationship.

    Args:
        name: Organization name
        slug: URL-friendly slug
        parent_id: Parent organization ID (optional)
        description: Organization description (optional)
        metadata: Additional metadata (optional)

    Returns:
        Created organization details
    """
    logger.info(f"Creating organization: {slug} for tenant {current_user['tenant_id']}")

    try:
        # Verify tenant exists
        tenant = db.query(Tenant).filter_by(id=current_user['tenant_id']).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Check hierarchy level if parent provided
        hierarchy_level = 0
        if parent_id:
            parent = db.query(Organization).filter_by(
                id=parent_id,
                tenant_id=current_user['tenant_id']
            ).first()

            if not parent:
                raise HTTPException(status_code=404, detail="Parent organization not found")

            hierarchy_level = parent.hierarchy_level + 1

        # Create organization
        org = Organization(
            tenant_id=current_user['tenant_id'],
            parent_id=parent_id if parent_id else None,
            name=name,
            slug=slug,
            description=description,
            hierarchy_level=hierarchy_level,
            metadata=metadata or {},
            created_by=current_user['user_id']
        )

        db.add(org)
        db.commit()
        db.refresh(org)

        logger.info(f"Organization created: {org.id}")

        return {
            "id": str(org.id),
            "tenant_id": str(org.tenant_id),
            "parent_id": str(org.parent_id) if org.parent_id else None,
            "name": org.name,
            "slug": org.slug,
            "hierarchy_level": org.hierarchy_level,
            "created_at": org.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.get("/orgs/{org_id}")
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get organization details

    Args:
        org_id: Organization ID

    Returns:
        Organization details
    """
    try:
        org = db.query(Organization).filter_by(
            id=org_id,
            tenant_id=current_user['tenant_id']
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        return {
            "id": str(org.id),
            "tenant_id": str(org.tenant_id),
            "parent_id": str(org.parent_id) if org.parent_id else None,
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "hierarchy_level": org.hierarchy_level,
            "is_active": org.is_active,
            "created_at": org.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve organization")


@router.get("/orgs")
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List organizations for tenant

    Args:
        skip: Number of records to skip
        limit: Max records to return

    Returns:
        List of organizations
    """
    try:
        orgs = db.query(Organization).filter_by(
            tenant_id=current_user['tenant_id']
        ).offset(skip).limit(limit).all()

        total = db.query(Organization).filter_by(
            tenant_id=current_user['tenant_id']
        ).count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "organizations": [
                {
                    "id": str(org.id),
                    "name": org.name,
                    "slug": org.slug,
                    "hierarchy_level": org.hierarchy_level,
                    "is_active": org.is_active
                }
                for org in orgs
            ]
        }

    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list organizations")


@router.put("/orgs/{org_id}")
async def update_organization(
    org_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update organization

    Args:
        org_id: Organization ID
        name: New organization name (optional)
        description: New description (optional)
        is_active: Active status (optional)

    Returns:
        Updated organization
    """
    try:
        org = db.query(Organization).filter_by(
            id=org_id,
            tenant_id=current_user['tenant_id']
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        if name:
            org.name = name
        if description is not None:
            org.description = description
        if is_active is not None:
            org.is_active = is_active

        org.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(org)

        logger.info(f"Organization updated: {org.id}")

        return {
            "id": str(org.id),
            "name": org.name,
            "description": org.description,
            "is_active": org.is_active,
            "updated_at": org.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update organization")


@router.delete("/orgs/{org_id}", status_code=204)
async def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete organization

    Args:
        org_id: Organization ID to delete

    Returns:
        No content
    """
    try:
        org = db.query(Organization).filter_by(
            id=org_id,
            tenant_id=current_user['tenant_id']
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Check for children
        children = db.query(Organization).filter_by(parent_id=org_id).all()
        if children:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete organization with children. Delete children first."
            )

        db.delete(org)
        db.commit()

        logger.info(f"Organization deleted: {org_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting organization: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete organization")


@router.get("/orgs/{org_id}/children")
async def get_organization_children(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get child organizations

    Args:
        org_id: Parent organization ID

    Returns:
        List of child organizations
    """
    try:
        org = db.query(Organization).filter_by(
            id=org_id,
            tenant_id=current_user['tenant_id']
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        children = db.query(Organization).filter_by(parent_id=org_id).all()

        return {
            "parent_id": str(org.id),
            "children": [
                {
                    "id": str(child.id),
                    "name": child.name,
                    "hierarchy_level": child.hierarchy_level
                }
                for child in children
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving child organizations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve children")


@router.get("/orgs/{org_id}/tree")
async def get_organization_tree(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get full organization subtree

    Args:
        org_id: Organization ID

    Returns:
        Full hierarchy tree
    """
    try:
        org = db.query(Organization).filter_by(
            id=org_id,
            tenant_id=current_user['tenant_id']
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        def build_tree(org_obj):
            """Recursively build tree structure"""
            children = db.query(Organization).filter_by(parent_id=org_obj.id).all()
            return {
                "id": str(org_obj.id),
                "name": org_obj.name,
                "hierarchy_level": org_obj.hierarchy_level,
                "children": [build_tree(child) for child in children]
            }

        return build_tree(org)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization tree: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tree")
