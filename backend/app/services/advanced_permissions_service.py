"""
Advanced Permissions Service - Sprint 13 (AGENT 2)

Provides fine-grained access control:
- Resource-level permissions (row-level security)
- Custom role creation
- Permission inheritance
- Delegation support
- Conditional permissions
- Audit logging
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json

from ..models import (
    User, Permission, RolePermission, RoleEnhanced, UserRoleEnhanced,
    PermissionAuditLog, Tenant, Organization, Facility
)


class AdvancedPermissionsService:
    """Advanced permission management with resource-level control"""

    # Resource-level permission patterns
    RESOURCE_PATTERNS = {
        'organization': {
            'scope': 'organization_id',
            'actions': ['create', 'read', 'update', 'delete', 'manage_users'],
            'inheritable': True
        },
        'facility': {
            'scope': 'facility_id',
            'actions': ['create', 'read', 'update', 'delete', 'manage_devices'],
            'inheritable': True,
            'parent_scope': 'organization_id'
        },
        'emissions': {
            'scope': 'organization_id',
            'actions': ['submit', 'read', 'update', 'approve', 'delete'],
            'inheritable': True
        },
        'report': {
            'scope': 'organization_id',
            'actions': ['generate', 'read', 'update', 'delete', 'publish'],
            'inheritable': True
        },
        'kpi': {
            'scope': 'organization_id',
            'actions': ['create', 'read', 'update', 'delete'],
            'inheritable': True
        },
        'marketplace': {
            'scope': 'organization_id',
            'actions': ['read', 'trade', 'list_credits'],
            'inheritable': False
        }
    }

    def __init__(self, db: Session):
        """
        Initialize Advanced Permissions service

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    # ============================================================================
    # RESOURCE-LEVEL PERMISSIONS
    # ============================================================================

    def check_resource_permission(
        self,
        user_id: UUID,
        resource_type: str,
        action: str,
        resource_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        facility_id: Optional[UUID] = None,
        check_inheritance: bool = True
    ) -> bool:
        """
        Check if user has permission on a specific resource

        Args:
            user_id: User to check
            resource_type: Type of resource (organization, facility, emissions, etc.)
            action: Action to perform (create, read, update, delete, etc.)
            resource_id: Specific resource ID (if checking specific record)
            organization_id: Organization scope
            facility_id: Facility scope
            check_inheritance: Whether to check inherited permissions

        Returns:
            True if user has permission
        """
        # Get user's active roles
        user_roles = self._get_active_user_roles(user_id)

        if not user_roles:
            return False

        # Check direct permission
        permission_name = f"{resource_type}:{action}"
        has_permission = False

        for user_role in user_roles:
            role_id = user_role.role_id

            # Check if role has the permission
            role_has_perm = self.db.query(RolePermission).join(
                Permission
            ).filter(
                and_(
                    RolePermission.role_id == role_id,
                    Permission.permission_name == permission_name,
                    RolePermission.granted == True
                )
            ).first()

            if not role_has_perm:
                continue

            # Check scope constraints
            role_org_id = user_role.organization_id
            role_facility_id = user_role.facility_id

            # If role has no scope constraints, permission granted
            if not role_org_id and not role_facility_id:
                has_permission = True
                break

            # If role has org scope, check if it matches
            if role_org_id:
                if organization_id == role_org_id:
                    has_permission = True
                    break

                # Check inheritance
                if check_inheritance and self._is_descendant_organization(organization_id, role_org_id):
                    has_permission = True
                    break

            # If role has facility scope, check if it matches
            if role_facility_id:
                if facility_id == role_facility_id:
                    has_permission = True
                    break

                # Check if facility belongs to user's organization
                if organization_id and self._facility_belongs_to_org(role_facility_id, organization_id):
                    has_permission = True
                    break

        return has_permission

    def _get_active_user_roles(self, user_id: UUID) -> List[UserRoleEnhanced]:
        """Get all active, non-expired roles for a user"""
        return self.db.query(UserRoleEnhanced).filter(
            and_(
                UserRoleEnhanced.user_id == user_id,
                UserRoleEnhanced.is_active == True,
                or_(
                    UserRoleEnhanced.expires_at.is_(None),
                    UserRoleEnhanced.expires_at > datetime.utcnow()
                )
            )
        ).all()

    def _is_descendant_organization(self, child_id: Optional[UUID], parent_id: UUID) -> bool:
        """Check if child_id is a descendant of parent_id in org hierarchy"""
        if not child_id:
            return False

        # In production, this would traverse org hierarchy
        # For now, simple parent check
        org = self.db.query(Organization).filter_by(id=child_id).first()
        if not org:
            return False

        return org.parent_id == parent_id

    def _facility_belongs_to_org(self, facility_id: UUID, org_id: UUID) -> bool:
        """Check if facility belongs to organization"""
        facility = self.db.query(Facility).filter_by(id=facility_id).first()
        if not facility:
            return False

        return facility.organization_id == org_id

    # ============================================================================
    # CUSTOM ROLE CREATION
    # ============================================================================

    def create_custom_role(
        self,
        tenant_id: UUID,
        role_name: str,
        role_display_name: str,
        role_description: str,
        permissions: List[str],
        created_by: UUID,
        role_category: str = 'custom',
        is_inheritable: bool = True
    ) -> RoleEnhanced:
        """
        Create custom role with specific permissions

        Args:
            tenant_id: Tenant creating the role
            role_name: Internal role name (slug)
            role_display_name: Display name
            role_description: Role description
            permissions: List of permission names to grant
            created_by: User creating the role
            role_category: Category (custom, governance, operational, etc.)
            is_inheritable: Whether role can be inherited in hierarchy

        Returns:
            Created RoleEnhanced object
        """
        # Check if role name already exists
        existing = self.db.query(RoleEnhanced).filter_by(
            tenant_id=tenant_id,
            role_name=role_name
        ).first()

        if existing:
            raise ValueError(f"Role '{role_name}' already exists")

        # Create role
        role = RoleEnhanced(
            tenant_id=tenant_id,
            role_name=role_name,
            role_display_name=role_display_name,
            role_description=role_description,
            role_category=role_category,
            is_system_role=False,
            is_active=True,
            created_by=created_by
        )

        self.db.add(role)
        self.db.flush()

        # Assign permissions
        for perm_name in permissions:
            perm = self.db.query(Permission).filter_by(permission_name=perm_name).first()

            if not perm:
                # Log warning but don't fail
                print(f"Warning: Permission '{perm_name}' not found")
                continue

            role_perm = RolePermission(
                role_id=role.id,
                permission_id=perm.id,
                granted=True,
                granted_by=created_by,
                conditions=None
            )
            self.db.add(role_perm)

        self.db.commit()

        # Audit log
        self._create_audit_log(
            tenant_id=tenant_id,
            user_id=created_by,
            action='create_custom_role',
            resource='role',
            permission_name=None,
            granted=True,
            metadata={
                'role_id': str(role.id),
                'role_name': role_name,
                'permissions_count': len(permissions)
            }
        )

        return role

    def update_custom_role(
        self,
        role_id: UUID,
        permissions: Optional[List[str]] = None,
        role_display_name: Optional[str] = None,
        role_description: Optional[str] = None,
        updated_by: Optional[UUID] = None
    ) -> RoleEnhanced:
        """
        Update custom role definition

        Args:
            role_id: Role to update
            permissions: New permission list (replaces existing)
            role_display_name: New display name
            role_description: New description
            updated_by: User making the update

        Returns:
            Updated RoleEnhanced object
        """
        role = self.db.query(RoleEnhanced).filter_by(id=role_id).first()

        if not role:
            raise ValueError(f"Role {role_id} not found")

        if role.is_system_role:
            raise ValueError("Cannot modify system role")

        # Update basic fields
        if role_display_name:
            role.role_display_name = role_display_name

        if role_description:
            role.role_description = role_description

        # Update permissions if provided
        if permissions is not None:
            # Delete existing permissions
            self.db.query(RolePermission).filter_by(role_id=role_id).delete()

            # Add new permissions
            for perm_name in permissions:
                perm = self.db.query(Permission).filter_by(permission_name=perm_name).first()

                if perm:
                    role_perm = RolePermission(
                        role_id=role_id,
                        permission_id=perm.id,
                        granted=True,
                        granted_by=updated_by
                    )
                    self.db.add(role_perm)

        self.db.commit()

        # Audit log
        self._create_audit_log(
            tenant_id=role.tenant_id,
            user_id=updated_by,
            action='update_custom_role',
            resource='role',
            permission_name=None,
            granted=True,
            metadata={
                'role_id': str(role_id),
                'updated_fields': {
                    'permissions': permissions is not None,
                    'display_name': role_display_name is not None,
                    'description': role_description is not None
                }
            }
        )

        return role

    def delete_custom_role(self, role_id: UUID, deleted_by: Optional[UUID] = None) -> bool:
        """
        Delete custom role (soft delete - mark as inactive)

        Args:
            role_id: Role to delete
            deleted_by: User deleting the role

        Returns:
            True if successful
        """
        role = self.db.query(RoleEnhanced).filter_by(id=role_id).first()

        if not role:
            raise ValueError(f"Role {role_id} not found")

        if role.is_system_role:
            raise ValueError("Cannot delete system role")

        # Mark as inactive
        role.is_active = False
        self.db.commit()

        # Audit log
        self._create_audit_log(
            tenant_id=role.tenant_id,
            user_id=deleted_by,
            action='delete_custom_role',
            resource='role',
            permission_name=None,
            granted=False,
            metadata={
                'role_id': str(role_id),
                'role_name': role.role_name
            }
        )

        return True

    # ============================================================================
    # PERMISSION INHERITANCE
    # ============================================================================

    def get_inherited_permissions(
        self,
        user_id: UUID,
        resource_type: str,
        organization_id: Optional[UUID] = None
    ) -> List[str]:
        """
        Get all permissions user has, including inherited ones

        Args:
            user_id: User to check
            resource_type: Type of resource
            organization_id: Optional org scope

        Returns:
            List of permission names user has access to
        """
        user_roles = self._get_active_user_roles(user_id)

        all_permissions = set()

        for user_role in user_roles:
            # Get direct role permissions
            role_perms = self.db.query(Permission).join(
                RolePermission
            ).filter(
                and_(
                    RolePermission.role_id == user_role.role_id,
                    RolePermission.granted == True,
                    Permission.resource == resource_type
                )
            ).all()

            for perm in role_perms:
                # Check scope
                if user_role.organization_id:
                    # If role is org-scoped, check if requested org is same or descendant
                    if not organization_id or organization_id == user_role.organization_id:
                        all_permissions.add(perm.permission_name)
                    elif self._is_descendant_organization(organization_id, user_role.organization_id):
                        all_permissions.add(perm.permission_name)
                else:
                    # No scope constraint
                    all_permissions.add(perm.permission_name)

        return list(all_permissions)

    def list_accessible_resources(
        self,
        user_id: UUID,
        resource_type: str,
        action: str,
        tenant_id: UUID
    ) -> List[UUID]:
        """
        List all resource IDs user has access to

        Args:
            user_id: User to check
            resource_type: Type of resource
            action: Action to check (read, update, etc.)
            tenant_id: Tenant scope

        Returns:
            List of resource IDs user can access
        """
        # Get user's roles with scopes
        user_roles = self._get_active_user_roles(user_id)

        accessible_resources = set()

        for user_role in user_roles:
            # Check if role has the permission
            permission_name = f"{resource_type}:{action}"
            has_perm = self.db.query(RolePermission).join(
                Permission
            ).filter(
                and_(
                    RolePermission.role_id == user_role.role_id,
                    Permission.permission_name == permission_name,
                    RolePermission.granted == True
                )
            ).first()

            if not has_perm:
                continue

            # If role has org scope, add all resources in that org
            if user_role.organization_id:
                if resource_type == 'organization':
                    accessible_resources.add(user_role.organization_id)

                    # Add descendant organizations
                    children = self.db.query(Organization).filter_by(
                        parent_id=user_role.organization_id
                    ).all()
                    for child in children:
                        accessible_resources.add(child.id)

                elif resource_type == 'facility':
                    facilities = self.db.query(Facility).filter_by(
                        organization_id=user_role.organization_id
                    ).all()
                    for facility in facilities:
                        accessible_resources.add(facility.id)

            # If role has facility scope, add that facility
            elif user_role.facility_id:
                if resource_type == 'facility':
                    accessible_resources.add(user_role.facility_id)

            # If role has no scope, user can access all
            else:
                # Return all resources (in production, paginate this)
                if resource_type == 'organization':
                    orgs = self.db.query(Organization).filter_by(tenant_id=tenant_id).all()
                    for org in orgs:
                        accessible_resources.add(org.id)

                elif resource_type == 'facility':
                    facilities = self.db.query(Facility).filter_by(tenant_id=tenant_id).all()
                    for facility in facilities:
                        accessible_resources.add(facility.id)

        return list(accessible_resources)

    # ============================================================================
    # DELEGATION SUPPORT
    # ============================================================================

    def delegate_permission(
        self,
        delegator_user_id: UUID,
        delegatee_user_id: UUID,
        permission_name: str,
        organization_id: Optional[UUID] = None,
        facility_id: Optional[UUID] = None,
        expires_in_days: Optional[int] = 30,
        delegation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delegate specific permission to another user (temporary grant)

        Args:
            delegator_user_id: User delegating the permission
            delegatee_user_id: User receiving the permission
            permission_name: Permission to delegate
            organization_id: Optional org scope
            facility_id: Optional facility scope
            expires_in_days: Delegation expiration (default 30 days)
            delegation_reason: Reason for delegation

        Returns:
            Delegation record
        """
        # Verify delegator has the permission
        resource, action = permission_name.split(':')
        has_permission = self.check_resource_permission(
            user_id=delegator_user_id,
            resource_type=resource,
            action=action,
            organization_id=organization_id,
            facility_id=facility_id
        )

        if not has_permission:
            raise ValueError(f"User {delegator_user_id} does not have permission {permission_name} to delegate")

        # Get delegatee's tenant
        delegatee = self.db.query(User).filter_by(id=delegatee_user_id).first()
        if not delegatee:
            raise ValueError(f"Delegatee user {delegatee_user_id} not found")

        # Create temporary delegation role
        delegation_role_name = f"delegation_{uuid4().hex[:8]}"
        delegation_role = self.create_custom_role(
            tenant_id=delegatee.tenant_id,
            role_name=delegation_role_name,
            role_display_name=f"Delegated: {permission_name}",
            role_description=f"Delegated by user {delegator_user_id}. Reason: {delegation_reason or 'N/A'}",
            permissions=[permission_name],
            created_by=delegator_user_id,
            role_category='delegation',
            is_inheritable=False
        )

        # Assign role to delegatee with expiration
        from .rbac_service import RBACService
        rbac_service = RBACService(self.db)

        user_role = rbac_service.assign_role(
            user_id=delegatee_user_id,
            role_id=delegation_role.id,
            granted_by=delegator_user_id,
            organization_id=organization_id,
            facility_id=facility_id,
            expires_in_days=expires_in_days,
            grant_reason=f"Delegation: {delegation_reason or 'N/A'}"
        )

        return {
            'delegation_id': str(user_role.id),
            'delegator_id': str(delegator_user_id),
            'delegatee_id': str(delegatee_user_id),
            'permission': permission_name,
            'expires_at': user_role.expires_at.isoformat() if user_role.expires_at else None,
            'created_at': user_role.granted_at.isoformat()
        }

    def revoke_delegation(
        self,
        delegation_id: UUID,
        revoked_by: Optional[UUID] = None
    ) -> bool:
        """
        Revoke a delegated permission

        Args:
            delegation_id: UserRoleEnhanced ID of the delegation
            revoked_by: User revoking the delegation

        Returns:
            True if successful
        """
        from .rbac_service import RBACService
        rbac_service = RBACService(self.db)

        return rbac_service.revoke_role(delegation_id, revoked_by)

    # ============================================================================
    # PERMISSION LISTS & QUERIES
    # ============================================================================

    def list_user_permissions(
        self,
        user_id: UUID,
        include_inherited: bool = True
    ) -> Dict[str, List[str]]:
        """
        List all permissions user has, grouped by resource

        Args:
            user_id: User to query
            include_inherited: Whether to include inherited permissions

        Returns:
            Dictionary mapping resource types to permission lists
        """
        user_roles = self._get_active_user_roles(user_id)

        permissions_by_resource = {}

        for user_role in user_roles:
            role_perms = self.db.query(Permission).join(
                RolePermission
            ).filter(
                and_(
                    RolePermission.role_id == user_role.role_id,
                    RolePermission.granted == True
                )
            ).all()

            for perm in role_perms:
                resource = perm.resource
                if resource not in permissions_by_resource:
                    permissions_by_resource[resource] = []

                permissions_by_resource[resource].append(perm.permission_name)

        # Deduplicate
        for resource in permissions_by_resource:
            permissions_by_resource[resource] = list(set(permissions_by_resource[resource]))

        return permissions_by_resource

    def list_available_actions(
        self,
        user_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None
    ) -> List[str]:
        """
        List all actions user can perform on a resource

        Args:
            user_id: User to check
            resource_type: Type of resource
            resource_id: Specific resource (optional)
            organization_id: Org scope (optional)

        Returns:
            List of action names user can perform
        """
        available_actions = []

        # Get all possible actions for this resource type
        resource_config = self.RESOURCE_PATTERNS.get(resource_type, {})
        possible_actions = resource_config.get('actions', [])

        for action in possible_actions:
            has_permission = self.check_resource_permission(
                user_id=user_id,
                resource_type=resource_type,
                action=action,
                resource_id=resource_id,
                organization_id=organization_id
            )

            if has_permission:
                available_actions.append(action)

        return available_actions

    # ============================================================================
    # AUDIT LOGGING
    # ============================================================================

    def _create_audit_log(
        self,
        tenant_id: UUID,
        user_id: Optional[UUID],
        action: str,
        resource: Optional[str] = None,
        permission_name: Optional[str] = None,
        granted: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Create permission audit log entry"""
        if not user_id:
            return

        audit = PermissionAuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource=resource,
            permission_name=permission_name,
            granted=granted,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Store metadata as JSON in a text field (if model supports it)
        # For now, skip metadata storage

        self.db.add(audit)
        self.db.commit()

    def get_permission_audit_log(
        self,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query permission audit logs

        Args:
            tenant_id: Tenant to query
            user_id: Optional user filter
            action: Optional action filter
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        query = self.db.query(PermissionAuditLog).filter_by(tenant_id=tenant_id)

        if user_id:
            query = query.filter_by(user_id=user_id)

        if action:
            query = query.filter_by(action=action)

        if start_date:
            query = query.filter(PermissionAuditLog.timestamp >= start_date)

        if end_date:
            query = query.filter(PermissionAuditLog.timestamp <= end_date)

        logs = query.order_by(PermissionAuditLog.timestamp.desc()).limit(limit).all()

        return [
            {
                'id': str(log.id),
                'user_id': str(log.user_id) if log.user_id else None,
                'action': log.action,
                'resource': log.resource,
                'permission_name': log.permission_name,
                'granted': log.granted,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat()
            }
            for log in logs
        ]
