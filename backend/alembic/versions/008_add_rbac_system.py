"""Add comprehensive RBAC system for Sprint 14

Revision ID: 008_rbac_system
Revises: 007_add_analytics_reporting_tables
Create Date: 2026-03-11

Sprint 14: RBAC System Implementation
- Permission model with resource:action pattern
- Enhanced Role model with permissions tracking
- RolePermission association (maps roles to permissions)
- UserRoleEnhanced with scoping and expiration
- Permission audit logging
- RBAC configuration per tenant
- 6 system roles (esg_manager, facility_manager, data_entry, auditor, stakeholder, api_service)
- 50+ permissions across all resources
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime

# revision identifiers
revision = '008_rbac_system'
down_revision = '007_add_analytics_reporting_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # PERMISSIONS TABLE
    # ============================================================================
    op.create_table(
        'permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('resource', sa.String(100), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('permission_name', sa.String(150), nullable=False, unique=True, index=True),
        sa.Column('permission_description', sa.Text),
        sa.Column('is_system', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create index for resource + action lookups
    op.create_index('idx_permission_resource_action', 'permissions', ['resource', 'action'])

    # ============================================================================
    # ROLE_PERMISSIONS ASSOCIATION TABLE
    # ============================================================================
    op.create_table(
        'role_permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles_enhanced.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('permission_id', UUID(as_uuid=True), sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('granted', sa.Boolean, default=True, index=True),
        sa.Column('grant_reason', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )

    op.create_index('idx_role_permission_role_id', 'role_permissions', ['role_id'])
    op.create_index('idx_role_permission_permission_id', 'role_permissions', ['permission_id'])

    # ============================================================================
    # ROLES_ENHANCED TABLE (Enhanced role with permissions)
    # ============================================================================
    op.create_table(
        'roles_enhanced',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('legacy_role_id', UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role_name', sa.String(100), nullable=False),
        sa.Column('role_display_name', sa.String(100)),
        sa.Column('role_description', sa.Text),
        sa.Column('is_system_role', sa.Boolean, default=False, index=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('role_category', sa.String(50), default='custom'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )

    # ============================================================================
    # USER_ROLES_ENHANCED TABLE (Enhanced user role assignment)
    # ============================================================================
    op.create_table(
        'user_roles_enhanced',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles_enhanced.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('facility_id', UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('expires_at', sa.DateTime, nullable=True, index=True),
        sa.Column('granted_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('granted_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('grant_reason', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('idx_user_roles_user_id', 'user_roles_enhanced', ['user_id'])
    op.create_index('idx_user_roles_role_id', 'user_roles_enhanced', ['role_id'])
    op.create_index('idx_user_roles_org_id', 'user_roles_enhanced', ['organization_id'])
    op.create_index('idx_user_roles_facility_id', 'user_roles_enhanced', ['facility_id'])
    op.create_index('idx_user_roles_expires_at', 'user_roles_enhanced', ['expires_at'])

    # ============================================================================
    # PERMISSION_AUDIT_LOGS TABLE
    # ============================================================================
    op.create_table(
        'permission_audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('resource', sa.String(100), nullable=True),
        sa.Column('permission_name', sa.String(150), nullable=True),
        sa.Column('granted', sa.Boolean, nullable=True, index=True),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('details', JSON, default=dict),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
    )

    op.create_index('idx_permission_audit_user_id', 'permission_audit_logs', ['user_id'])
    op.create_index('idx_permission_audit_timestamp', 'permission_audit_logs', ['timestamp'])
    op.create_index('idx_permission_audit_action', 'permission_audit_logs', ['action'])

    # ============================================================================
    # RBAC_CONFIG TABLE
    # ============================================================================
    op.create_table(
        'rbac_config',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('cache_ttl_seconds', sa.Integer, default=300),
        sa.Column('require_all_approvals', sa.Boolean, default=True),
        sa.Column('enable_permission_caching', sa.Boolean, default=True),
        sa.Column('log_all_permission_checks', sa.Boolean, default=False),
        sa.Column('log_denied_permissions', sa.Boolean, default=True),
        sa.Column('enforce_scope_checks', sa.Boolean, default=True),
        sa.Column('allow_custom_roles', sa.Boolean, default=True),
        sa.Column('allow_temporary_roles', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    # ============================================================================
    # Drop tables in reverse order of creation
    # ============================================================================
    op.drop_table('rbac_config')
    op.drop_table('permission_audit_logs')
    op.drop_table('user_roles_enhanced')
    op.drop_table('roles_enhanced')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
