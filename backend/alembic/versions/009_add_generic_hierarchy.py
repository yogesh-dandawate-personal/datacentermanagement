"""Add generic hierarchy framework for Sprint 15

Revision ID: 009_generic_hierarchy
Revises: 008_rbac_system
Create Date: 2026-03-11

Sprint 15: Generic Hierarchy Framework
- HierarchyPattern: Configuration for supported hierarchy patterns
  - IT/DataCenter: Region → Campus → DataCenter → Building → Floor → Room → Rack → Device
  - Corporate: Organization → Division → Department → Team → Individual
  - Energy: Portfolio → Plant → Facility → Unit → Equipment
  - Real Estate: Portfolio → Region → Campus → Building → Floor → Space
  - Supply Chain: Company → Supplier → Site → Department → Process
- HierarchyLevel: Definition of each level within a pattern
- HierarchyEntity: Generic organizational entity with self-referential relationships
- HierarchyMigration & HierarchyMigrationError: Track hierarchy migrations
- HierarchyAuditLog: Complete audit trail for all hierarchy changes
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime

# revision identifiers
revision = '009_generic_hierarchy'
down_revision = '008_rbac_system'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================================
    # HIERARCHY_PATTERNS TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_patterns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('pattern_name', sa.String(100), nullable=False, index=True),  # it_datacenter, corporate, energy, real_estate, supply_chain
        sa.Column('pattern_type', sa.String(50), nullable=False),  # system, custom
        sa.Column('description', sa.Text),
        sa.Column('levels', JSON, server_default='[]'),  # Hierarchy structure definition
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('idx_hierarchy_pattern_tenant_active', 'hierarchy_patterns', ['tenant_id', 'is_active'])

    # ============================================================================
    # HIERARCHY_LEVELS TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_levels',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('pattern_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_patterns.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('level_number', sa.Integer, nullable=False, index=True),  # 1 (root) to N (leaf)
        sa.Column('level_name', sa.String(100), nullable=False),  # Region, Campus, DataCenter, etc.
        sa.Column('level_singular', sa.String(100), nullable=False),  # region, campus, datacenter
        sa.Column('description', sa.Text),
        sa.Column('min_children', sa.Integer, default=0),
        sa.Column('max_children', sa.Integer),
        sa.Column('level_metadata', JSON, server_default='{}'),
        sa.Column('icon_name', sa.String(50)),
        sa.Column('color_code', sa.String(7)),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_hierarchy_level_pattern', 'hierarchy_levels', ['pattern_id', 'level_number'])
    op.create_unique_constraint('uq_pattern_level_number', 'hierarchy_levels', ['pattern_id', 'level_number'])

    # ============================================================================
    # HIERARCHY_ENTITIES TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_entities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('hierarchy_pattern_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_patterns.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('hierarchy_level_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_levels.id', ondelete='SET NULL'), nullable=False, index=True),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_entities.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('hierarchy_level', sa.Integer, nullable=False, index=True),  # Denormalized level_number
        sa.Column('hierarchy_path', sa.String(500), nullable=False, index=True),  # For recursive queries
        sa.Column('hierarchy_depth', sa.Integer, nullable=False),  # Distance from root
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('facility_id', UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('status', sa.String(50), default='active', index=True),  # active, inactive, archived, planned
        sa.Column('entity_metadata', JSON, server_default='{}'),  # Custom attributes
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('idx_hierarchy_entity_parent', 'hierarchy_entities', ['parent_id'])
    op.create_index('idx_hierarchy_entity_tenant_pattern_level_active', 'hierarchy_entities', ['tenant_id', 'hierarchy_pattern_id', 'hierarchy_level', 'is_active'])
    op.create_index('idx_hierarchy_entity_path', 'hierarchy_entities', ['hierarchy_path'])
    op.create_index('idx_hierarchy_entity_org', 'hierarchy_entities', ['organization_id'])
    op.create_unique_constraint('uq_parent_slug', 'hierarchy_entities', ['parent_id', 'slug'])

    # ============================================================================
    # HIERARCHY_MIGRATIONS TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_migrations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('migration_name', sa.String(255), nullable=False, index=True),
        sa.Column('migration_type', sa.String(50), nullable=False),  # rename, restructure, merge, split
        sa.Column('description', sa.Text),
        sa.Column('from_pattern_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_patterns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('to_pattern_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_patterns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('migration_details', JSON, server_default='{}'),
        sa.Column('status', sa.String(50), default='planned', index=True),  # planned, in_progress, completed, failed, rolled_back
        sa.Column('entities_affected', sa.Integer, default=0),
        sa.Column('entities_migrated', sa.Integer, default=0),
        sa.Column('entities_failed', sa.Integer, default=0),
        sa.Column('planned_at', sa.DateTime),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('executed_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_hierarchy_migration_tenant_status', 'hierarchy_migrations', ['tenant_id', 'status'])

    # ============================================================================
    # HIERARCHY_MIGRATION_ERRORS TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_migration_errors',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('migration_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_migrations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('entity_id', UUID(as_uuid=True), sa.ForeignKey('hierarchy_entities.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('error_type', sa.String(100), nullable=False),  # validation_error, constraint_violation, etc.
        sa.Column('error_message', sa.Text, nullable=False),
        sa.Column('error_context', JSON, server_default='{}'),
        sa.Column('status', sa.String(50), default='open', index=True),  # open, fixed, acknowledged, ignored
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime),
    )
    op.create_index('idx_hierarchy_migration_error_migration', 'hierarchy_migration_errors', ['migration_id'])

    # ============================================================================
    # HIERARCHY_AUDIT_LOGS TABLE
    # ============================================================================
    op.create_table(
        'hierarchy_audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),  # CREATE, UPDATE, DELETE, RESTRUCTURE, MIGRATE
        sa.Column('entity_type', sa.String(100), nullable=False, index=True),  # hierarchy_entity, hierarchy_level, hierarchy_pattern
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('old_values', JSON, server_default='{}'),
        sa.Column('new_values', JSON, server_default='{}'),
        sa.Column('changed_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('reason', sa.Text),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
    )
    op.create_index('idx_hierarchy_audit_tenant_entity', 'hierarchy_audit_logs', ['tenant_id', 'entity_type', 'entity_id'])


def downgrade():
    # Drop in reverse order (respecting foreign key dependencies)
    op.drop_table('hierarchy_audit_logs')
    op.drop_table('hierarchy_migration_errors')
    op.drop_table('hierarchy_migrations')
    op.drop_table('hierarchy_entities')
    op.drop_table('hierarchy_levels')
    op.drop_table('hierarchy_patterns')
