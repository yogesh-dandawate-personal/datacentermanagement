"""
RBAC Service Layer - Sprint 14

Provides business logic for:
- Role management (create, assign, revoke)
- Permission checking with caching
- Permission audit logging
- System role seeding
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json
import redis

from ..models import (
    User, Permission, RolePermission, RoleEnhanced, UserRoleEnhanced,
    PermissionAuditLog, RBACConfig, Tenant, Organization, Facility
)


class RBACService:
    """Role-Based Access Control Service"""

    # System roles and their permission definitions
    SYSTEM_ROLES = {
        'esg_manager': {
            'display_name': 'ESG Manager',
            'description': 'Manages ESG program, emissions tracking, and reporting',
            'category': 'governance',
            'permissions': [
                # Organization management
                'organizations:create', 'organizations:read', 'organizations:update',
                # Facilities
                'facilities:create', 'facilities:read', 'facilities:update', 'facilities:delete',
                # Emissions
                'emissions:submit', 'emissions:read', 'emissions:approve',
                # Assessments
                'assessments:start', 'assessments:complete', 'assessments:read',
                # Roadmaps
                'roadmaps:generate', 'roadmaps:update', 'roadmaps:read',
                # Reports
                'reports:generate', 'reports:submit', 'reports:read',
                # Users
                'users:invite', 'users:assign_roles',
                # Audit logs
                'audit_logs:read',
            ]
        },
        'facility_manager': {
            'display_name': 'Facility Manager',
            'description': 'Manages facility operations and emissions at facility level',
            'category': 'operational',
            'permissions': [
                # Facilities (facility-scoped)
                'facilities:read', 'facilities:update',
                # Emissions
                'emissions:submit', 'emissions:read',
                # Assessments (facility-scoped)
                'assessments:complete', 'assessments:read',
                # Roadmaps
                'roadmaps:update', 'roadmaps:read',
                # Reports
                'reports:read',
            ]
        },
        'data_entry': {
            'display_name': 'Data Entry Operator',
            'description': 'Enters and validates emissions data',
            'category': 'operational',
            'permissions': [
                # Emissions only
                'emissions:submit', 'emissions:read',
                # Can view reports
                'reports:read',
            ]
        },
        'auditor': {
            'display_name': 'Auditor',
            'description': 'Reviews and verifies ESG data and reports (read-only + approve)',
            'category': 'governance',
            'permissions': [
                # Read-only on most resources
                'organizations:read', 'facilities:read',
                'emissions:read',
                'assessments:read',
                'roadmaps:read',
                'reports:read',
                'audit_logs:read',
                # Can approve calculations
                'emissions:approve',
            ]
        },
        'stakeholder': {
            'display_name': 'Stakeholder',
            'description': 'External stakeholder with public-only access',
            'category': 'stakeholder',
            'permissions': [
                # Read-only public data
                'organizations:read',
                'reports:read',
            ]
        },
        'api_service': {
            'display_name': 'API Service Account',
            'description': 'Service account for API integrations',
            'category': 'system',
            'permissions': [
                # API operations
                'emissions:submit', 'emissions:read',
                'facilities:read',
                'reports:generate',
            ]
        },
    }

    # All possible permissions in the system
    ALL_PERMISSIONS = [
        # Organizations
        ('organizations', 'create', 'organizations:create', 'Create organizations'),
        ('organizations', 'read', 'organizations:read', 'View organizations'),
        ('organizations', 'update', 'organizations:update', 'Edit organizations'),
        ('organizations', 'delete', 'organizations:delete', 'Delete organizations'),
        # Facilities
        ('facilities', 'create', 'facilities:create', 'Create facilities'),
        ('facilities', 'read', 'facilities:read', 'View facilities'),
        ('facilities', 'update', 'facilities:update', 'Edit facilities'),
        ('facilities', 'delete', 'facilities:delete', 'Delete facilities'),
        # Emissions
        ('emissions', 'submit', 'emissions:submit', 'Submit activity data'),
        ('emissions', 'read', 'emissions:read', 'View emissions data'),
        ('emissions', 'update', 'emissions:update', 'Edit emissions data'),
        ('emissions', 'delete', 'emissions:delete', 'Delete emissions data'),
        ('emissions', 'approve', 'emissions:approve', 'Approve emissions calculations'),
        # Assessments
        ('assessments', 'start', 'assessments:start', 'Start ESG assessments'),
        ('assessments', 'complete', 'assessments:complete', 'Complete assessments'),
        ('assessments', 'read', 'assessments:read', 'View assessment results'),
        ('assessments', 'delete', 'assessments:delete', 'Delete assessments'),
        # Roadmaps
        ('roadmaps', 'generate', 'roadmaps:generate', 'Generate roadmaps'),
        ('roadmaps', 'read', 'roadmaps:read', 'View roadmaps'),
        ('roadmaps', 'update', 'roadmaps:update', 'Edit roadmaps'),
        ('roadmaps', 'delete', 'roadmaps:delete', 'Delete roadmaps'),
        # Reports
        ('reports', 'generate', 'reports:generate', 'Generate reports'),
        ('reports', 'read', 'reports:read', 'View reports'),
        ('reports', 'update', 'reports:update', 'Edit reports'),
        ('reports', 'delete', 'reports:delete', 'Delete reports'),
        ('reports', 'submit', 'reports:submit', 'Submit reports externally'),
        # Users
        ('users', 'invite', 'users:invite', 'Invite new users'),
        ('users', 'read', 'users:read', 'View users'),
        ('users', 'update', 'users:update', 'Edit users'),
        ('users', 'delete', 'users:delete', 'Delete users'),
        ('users', 'assign_roles', 'users:assign_roles', 'Assign roles to users'),
        # Audit logs
        ('audit_logs', 'read', 'audit_logs:read', 'View audit logs'),
        # KPIs
        ('kpis', 'read', 'kpis:read', 'View KPIs'),
        ('kpis', 'update', 'kpis:update', 'Edit KPIs'),
        # Marketplace
        ('marketplace', 'read', 'marketplace:read', 'View marketplace'),
        ('marketplace', 'trade', 'marketplace:trade', 'Execute trades'),
        # Integrations
        ('integrations', 'read', 'integrations:read', 'View integrations'),
        ('integrations', 'manage', 'integrations:manage', 'Manage integrations'),
        # Admin
        ('admin', 'manage_roles', 'admin:manage_roles', 'Manage roles'),
        ('admin', 'manage_permissions', 'admin:manage_permissions', 'Manage permissions'),
        ('admin', 'system_config', 'admin:system_config', 'Configure system settings'),
    ]

    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        """
        Initialize RBAC service

        Args:
            db: SQLAlchemy session
            redis_client: Redis client for caching (optional)
        """
        self.db = db
        self.redis = redis_client

    def seed_system_permissions(self, tenant_id: UUID) -> int:
        """
        Seed all system permissions for a tenant

        Returns:
            Number of permissions created
        """
        created_count = 0

        for resource, action, permission_name, description in self.ALL_PERMISSIONS:
            existing = self.db.query(Permission).filter_by(permission_name=permission_name).first()

            if not existing:
                permission = Permission(
                    resource=resource,
                    action=action,
                    permission_name=permission_name,
                    permission_description=description,
                    is_system=True
                )
                self.db.add(permission)
                created_count += 1

        self.db.commit()
        return created_count

    def seed_system_roles(self, tenant_id: UUID) -> int:
        """
        Seed all system roles for a tenant with their permissions

        Returns:
            Number of roles created
        """
        created_count = 0
        tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()

        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        # First, ensure all permissions exist
        self.seed_system_permissions(tenant_id)

        # Create system roles
        for role_name, role_config in self.SYSTEM_ROLES.items():
            existing = self.db.query(RoleEnhanced).filter_by(
                tenant_id=tenant_id,
                role_name=role_name
            ).first()

            if not existing:
                role = RoleEnhanced(
                    tenant_id=tenant_id,
                    role_name=role_name,
                    role_display_name=role_config['display_name'],
                    role_description=role_config['description'],
                    role_category=role_config['category'],
                    is_system_role=True,
                    is_active=True
                )
                self.db.add(role)
                self.db.flush()  # Flush to get role.id

                # Assign permissions to role
                for permission_name in role_config['permissions']:
                    perm = self.db.query(Permission).filter_by(permission_name=permission_name).first()

                    if perm:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=perm.id,
                            granted=True
                        )
                        self.db.add(role_perm)

                created_count += 1

        self.db.commit()
        return created_count

    def assign_role(
        self,
        user_id: UUID,
        role_id: UUID,
        granted_by: UUID,
        organization_id: Optional[UUID] = None,
        facility_id: Optional[UUID] = None,
        expires_in_days: Optional[int] = None,
        grant_reason: Optional[str] = None
    ) -> UserRoleEnhanced:
        """
        Assign a role to a user

        Args:
            user_id: User to assign role to
            role_id: Role to assign
            granted_by: User granting the role
            organization_id: Optional org scoping
            facility_id: Optional facility scoping
            expires_in_days: Optional expiration (None = permanent)
            grant_reason: Optional reason for grant

        Returns:
            Created UserRoleEnhanced record
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        role = self.db.query(RoleEnhanced).filter_by(id=role_id).first()
        if not role:
            raise ValueError(f"Role {role_id} not found")

        # Check if assignment already exists
        existing = self.db.query(UserRoleEnhanced).filter_by(
            user_id=user_id,
            role_id=role_id,
            organization_id=organization_id,
            facility_id=facility_id
        ).first()

        if existing:
            # Update existing assignment
            existing.is_active = True
            existing.granted_by = granted_by
            existing.granted_at = datetime.utcnow()
            if expires_in_days:
                existing.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            if grant_reason:
                existing.grant_reason = grant_reason
            self.db.commit()
            return existing

        # Create new assignment
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        user_role = UserRoleEnhanced(
            user_id=user_id,
            role_id=role_id,
            organization_id=organization_id,
            facility_id=facility_id,
            granted_by=granted_by,
            expires_at=expires_at,
            grant_reason=grant_reason,
            is_active=True
        )

        self.db.add(user_role)
        self.db.commit()

        # Invalidate permission cache for this user
        self._invalidate_user_permission_cache(user_id)

        return user_role

    def revoke_role(
        self,
        user_role_id: UUID,
        revoked_by: Optional[UUID] = None
    ) -> bool:
        """
        Revoke a role assignment from a user

        Args:
            user_role_id: UserRoleEnhanced record ID to revoke
            revoked_by: User revoking the role

        Returns:
            True if successful
        """
        user_role = self.db.query(UserRoleEnhanced).filter_by(id=user_role_id).first()

        if not user_role:
            raise ValueError(f"User role assignment {user_role_id} not found")

        user_id = user_role.user_id
        user_role.is_active = False
        self.db.commit()

        # Invalidate cache
        self._invalidate_user_permission_cache(user_id)

        return True

    def check_permission(
        self,
        user_id: UUID,
        resource: str,
        action: str,
        organization_id: Optional[UUID] = None,
        facility_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        audit_log: bool = True
    ) -> bool:
        """
        Check if user has a specific permission

        Args:
            user_id: User to check
            resource: Resource type (organizations, facilities, emissions, etc.)
            action: Action type (create, read, update, delete, approve, etc.)
            organization_id: Optional org scope to check
            facility_id: Optional facility scope to check
            ip_address: For audit logging
            user_agent: For audit logging
            audit_log: Whether to log this check

        Returns:
            True if user has permission, False otherwise
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            granted = False
        else:
            # Try cache first
            cache_key = f"permission:{user_id}:{resource}:{action}"
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached is not None:
                    granted = cached == b'1'
                else:
                    granted = self._check_permission_db(user_id, resource, action, organization_id, facility_id)
                    # Cache result
                    ttl = self._get_cache_ttl(user.tenant_id)
                    self.redis.setex(cache_key, ttl, b'1' if granted else b'0')
            else:
                granted = self._check_permission_db(user_id, resource, action, organization_id, facility_id)

        # Audit log if enabled
        if audit_log:
            self._create_audit_log(
                user_id=user_id,
                action='check',
                resource=resource,
                permission_name=f"{resource}:{action}",
                granted=granted,
                ip_address=ip_address,
                user_agent=user_agent
            )

        return granted

    def _check_permission_db(
        self,
        user_id: UUID,
        resource: str,
        action: str,
        organization_id: Optional[UUID] = None,
        facility_id: Optional[UUID] = None
    ) -> bool:
        """
        Check permission in database

        Returns:
            True if user has permission
        """
        # Query: Get all roles for user, get their permissions, check if permission exists
        user_roles = self.db.query(UserRoleEnhanced).filter(
            and_(
                UserRoleEnhanced.user_id == user_id,
                UserRoleEnhanced.is_active == True,
                or_(
                    UserRoleEnhanced.expires_at.is_(None),
                    UserRoleEnhanced.expires_at > datetime.utcnow()
                )
            )
        ).all()

        if not user_roles:
            return False

        # Check if scope matches
        role_matches_scope = False
        for user_role in user_roles:
            # If role has org scope, user must request from same org
            if user_role.organization_id:
                if organization_id != user_role.organization_id:
                    continue

            # If role has facility scope, user must request from same facility
            if user_role.facility_id:
                if facility_id != user_role.facility_id:
                    continue

            role_matches_scope = True
            break

        if not role_matches_scope and any(ur.organization_id or ur.facility_id for ur in user_roles):
            return False

        # Get the role IDs that match scope
        valid_role_ids = [ur.role_id for ur in user_roles]

        # Check if any role has the required permission
        permission_exists = self.db.query(RolePermission).join(
            Permission
        ).filter(
            and_(
                RolePermission.role_id.in_(valid_role_ids),
                Permission.resource == resource,
                Permission.action == action,
                RolePermission.granted == True
            )
        ).first()

        return permission_exists is not None

    def get_user_roles(self, user_id: UUID) -> List[Dict]:
        """Get all active roles for a user"""
        user_roles = self.db.query(UserRoleEnhanced).filter(
            and_(
                UserRoleEnhanced.user_id == user_id,
                UserRoleEnhanced.is_active == True,
                or_(
                    UserRoleEnhanced.expires_at.is_(None),
                    UserRoleEnhanced.expires_at > datetime.utcnow()
                )
            )
        ).all()

        return [
            {
                'role_id': str(ur.role_id),
                'role_name': ur.role.role_name,
                'role_display_name': ur.role.role_display_name,
                'organization_id': str(ur.organization_id) if ur.organization_id else None,
                'facility_id': str(ur.facility_id) if ur.facility_id else None,
                'expires_at': ur.expires_at.isoformat() if ur.expires_at else None,
                'granted_at': ur.granted_at.isoformat(),
            }
            for ur in user_roles
        ]

    def get_role_permissions(self, role_id: UUID) -> List[str]:
        """Get all permissions for a role"""
        perms = self.db.query(Permission).join(
            RolePermission
        ).filter(
            and_(
                RolePermission.role_id == role_id,
                RolePermission.granted == True
            )
        ).all()

        return [p.permission_name for p in perms]

    def _create_audit_log(
        self,
        user_id: Optional[UUID],
        action: str,
        resource: Optional[str] = None,
        permission_name: Optional[str] = None,
        granted: Optional[bool] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Create an audit log entry"""
        if not user_id:
            return  # Don't log if no user

        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            return

        audit = PermissionAuditLog(
            tenant_id=user.tenant_id,
            user_id=user_id,
            action=action,
            resource=resource,
            permission_name=permission_name,
            granted=granted,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.db.add(audit)
        self.db.commit()

    def _invalidate_user_permission_cache(self, user_id: UUID) -> None:
        """Invalidate all cached permissions for a user"""
        if not self.redis:
            return

        # Delete all permission keys for this user
        pattern = f"permission:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def _get_cache_ttl(self, tenant_id: UUID) -> int:
        """Get cache TTL from config, default 300 seconds"""
        config = self.db.query(RBACConfig).filter_by(tenant_id=tenant_id).first()
        if config:
            return config.cache_ttl_seconds
        return 300  # 5 minutes default
