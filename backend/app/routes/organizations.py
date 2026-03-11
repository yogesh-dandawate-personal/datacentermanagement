"""Organization management API routes"""
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid
from datetime import datetime

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.models import Organization, Department, Position, Tenant, User
from app.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationTreeNode,
    OrganizationListResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["organizations"])


def get_current_user(authorization: str = Header(None), db = Depends(get_db)):
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


def get_organization_or_404(db: Session, org_id: str, tenant_id: str) -> Organization:
    """Helper to get organization or raise 404"""
    org = db.query(Organization).filter_by(
        id=org_id,
        tenant_id=tenant_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return org


def build_organization_tree(org: Organization, db: Session) -> dict:
    """Recursively build organization tree structure"""
    children = db.query(Organization).filter_by(parent_id=org.id).all()
    return {
        "id": str(org.id),
        "name": org.name,
        "hierarchy_level": org.hierarchy_level,
        "children": [build_organization_tree(child, db) for child in children]
    }


@router.post("/orgs", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new organization

    Creates an organization unit within tenant hierarchy.
    Can specify parent for hierarchical relationship.

    Args:
        org_data: Organization creation data

    Returns:
        Created organization details
    """
    logger.info(f"Creating organization: {org_data.slug} for tenant {current_user['tenant_id']}")

    try:
        # Verify tenant exists
        tenant = db.query(Tenant).filter_by(id=current_user['tenant_id']).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Check hierarchy level if parent provided
        hierarchy_level = 0
        if org_data.parent_id:
            parent = get_organization_or_404(db, org_data.parent_id, current_user['tenant_id'])
            hierarchy_level = parent.hierarchy_level + 1

        # Create organization
        org = Organization(
            tenant_id=current_user['tenant_id'],
            parent_id=org_data.parent_id,
            name=org_data.name,
            slug=org_data.slug,
            description=org_data.description,
            hierarchy_level=hierarchy_level,
            org_metadata=org_data.org_metadata,
            created_by=current_user['user_id']
        )

        db.add(org)
        db.commit()
        db.refresh(org)

        logger.info(f"Organization created: {org.id}")

        return org

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.get("/orgs/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db = Depends(get_db),
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
        org = get_organization_or_404(db, org_id, current_user['tenant_id'])
        return org

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve organization")


@router.get("/orgs", response_model=OrganizationListResponse)
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_db),
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
            "organizations": orgs
        }

    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list organizations")


@router.put("/orgs/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_update: OrganizationUpdate,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update organization

    Args:
        org_id: Organization ID
        org_update: Organization update data

    Returns:
        Updated organization
    """
    try:
        org = get_organization_or_404(db, org_id, current_user['tenant_id'])

        # Update fields that are provided
        if org_update.name:
            org.name = org_update.name
        if org_update.description is not None:
            org.description = org_update.description
        if org_update.is_active is not None:
            org.is_active = org_update.is_active

        org.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(org)

        logger.info(f"Organization updated: {org.id}")

        return org

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update organization")


@router.delete("/orgs/{org_id}", status_code=204)
async def delete_organization(
    org_id: str,
    db = Depends(get_db),
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
        org = get_organization_or_404(db, org_id, current_user['tenant_id'])

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
    db = Depends(get_db),
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
        org = get_organization_or_404(db, org_id, current_user['tenant_id'])
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
    db = Depends(get_db),
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
        org = get_organization_or_404(db, org_id, current_user['tenant_id'])
        return build_organization_tree(org, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization tree: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tree")
