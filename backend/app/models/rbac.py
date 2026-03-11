"""
RBAC (Role-Based Access Control) Models - Sprint 14

This module defines the comprehensive RBAC system with:
- Permission model (resource:action pattern)
- Enhanced Role model (with permissions relationship)
- RolePermission association (for mapping roles to permissions)
- UserRole enhancement (with scoping and expiration)
- Audit logging for all permission checks
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from . import UUID, Base


class Permission(Base):
    """Permission definition with resource:action pattern"""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Resource (organizations, facilities, emissions, reports, users, audit_logs, etc.)
    resource = Column(String(100), nullable=False, index=True)

    # Action (create, read, update, delete, approve, submit, etc.)
    action = Column(String(50), nullable=False, index=True)

    # Full permission name (e.g., "organizations:create")
    permission_name = Column(String(150), nullable=False, unique=True, index=True)

    # Human-readable description
    permission_description = Column(Text)

    # Whether this is a system permission (cannot be deleted)
    is_system = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_permission_resource_action', 'resource', 'action'),
    )


class RolePermission(Base):
    """Association table: Maps permissions to roles"""
    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Role being assigned permissions
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Permission being assigned
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Allow or deny (for exceptions/overrides)
    granted = Column(Boolean, default=True, index=True)

    # Optional context for why this permission was granted/denied
    grant_reason = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    # Unique constraint: role can't have duplicate permissions
    __table_args__ = (
        Index('idx_role_permission_role_id', 'role_id'),
        Index('idx_role_permission_permission_id', 'permission_id'),
    )


class RoleEnhanced(Base):
    """Enhanced Role definition with permissions tracking"""
    __tablename__ = "roles_enhanced"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to the old Role table for backward compatibility
    legacy_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=True)

    # Tenant this role belongs to
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Role details
    role_name = Column(String(100), nullable=False)  # esg_manager, facility_manager, data_entry, auditor, stakeholder, api_service
    role_display_name = Column(String(100))  # "ESG Manager", "Facility Manager", etc.
    role_description = Column(Text)

    # Is this a system role (predefined, cannot be deleted)
    is_system_role = Column(Boolean, default=False, index=True)

    # Active/inactive
    is_active = Column(Boolean, default=True, index=True)

    # Role category for grouping
    role_category = Column(String(50), default="custom")  # system, governance, operational, stakeholder, custom

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan", foreign_keys=[RolePermission.role_id])
    user_roles = relationship("UserRoleEnhanced", back_populates="role")


class UserRoleEnhanced(Base):
    """Enhanced User Role assignment with scoping and expiration"""
    __tablename__ = "user_roles_enhanced"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User being assigned role
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Role being assigned
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles_enhanced.id", ondelete="CASCADE"), nullable=False, index=True)

    # Scope: What resources this role applies to
    # If null, applies to all resources at that level
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=True, index=True)

    # Expiration: When this role assignment expires (for temporary access)
    # Null means it never expires
    expires_at = Column(DateTime, nullable=True, index=True)

    # Who granted this role
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Optional reason for granting
    grant_reason = Column(Text)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("RoleEnhanced", back_populates="user_roles")
    organization = relationship("Organization")
    facility = relationship("Facility")
    granter = relationship("User", foreign_keys=[granted_by])

    __table_args__ = (
        Index('idx_user_roles_user_id', 'user_id'),
        Index('idx_user_roles_role_id', 'role_id'),
        Index('idx_user_roles_org_id', 'organization_id'),
        Index('idx_user_roles_facility_id', 'facility_id'),
        Index('idx_user_roles_expires_at', 'expires_at'),
    )


class PermissionAuditLog(Base):
    """Audit trail for all permission checks and grants"""
    __tablename__ = "permission_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # User performing the action
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Action: 'check' (permission check), 'grant' (assign role), 'revoke' (remove role), 'modify' (change permissions)
    action = Column(String(50), nullable=False, index=True)

    # What resource/permission was involved
    resource = Column(String(100), nullable=True)
    permission_name = Column(String(150), nullable=True)

    # The result
    granted = Column(Boolean, nullable=True, index=True)  # True=allowed, False=denied, None=N/A for grants

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Additional details as JSON
    details = Column(JSON, default=dict)

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    __table_args__ = (
        Index('idx_permission_audit_user_id', 'user_id'),
        Index('idx_permission_audit_timestamp', 'timestamp'),
        Index('idx_permission_audit_action', 'action'),
    )


class RBACConfig(Base):
    """RBAC system configuration"""
    __tablename__ = "rbac_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Cache settings
    cache_ttl_seconds = Column(Integer, default=300)  # 5 minutes default

    # Permission check behavior
    require_all_approvals = Column(Boolean, default=True)  # All roles must grant permission (OR vs AND logic)
    enable_permission_caching = Column(Boolean, default=True)

    # Audit logging
    log_all_permission_checks = Column(Boolean, default=False)  # Be careful with performance
    log_denied_permissions = Column(Boolean, default=True)

    # Enforcement
    enforce_scope_checks = Column(Boolean, default=True)  # Enforce org/facility scoping

    # Feature flags
    allow_custom_roles = Column(Boolean, default=True)
    allow_temporary_roles = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
