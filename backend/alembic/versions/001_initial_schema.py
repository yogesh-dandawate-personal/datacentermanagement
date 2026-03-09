"""Initial schema migration - Create all tables from models

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-10

This migration creates the complete NetZero ESG platform schema:
- Multi-tenant support (tenants, organizations)
- User management (users, roles, permissions)
- Facility management (facilities, meters)
- Carbon calculations and tracking
- KPI monitoring
- Marketplace for carbon credits
- Audit logging
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the NetZero platform."""

    # Enable UUID extension if using PostgreSQL
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create tenants table (multi-tenant foundation)
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('permissions', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('keycloak_id', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('keycloak_id')
    )

    # Create user_roles association table
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('changes', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create facilities table
    op.create_table(
        'facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('facility_type', sa.String(100), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create facility_users association table
    op.create_table(
        'facility_users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'facility_id')
    )

    # Create meters table
    op.create_table(
        'meters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meter_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create carbon_calculations table
    op.create_table(
        'carbon_calculations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scope', sa.String(50), nullable=False),
        sa.Column('emission_type', sa.String(100), nullable=True),
        sa.Column('value', sa.Numeric(precision=15, scale=6), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('calculation_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create kpi_snapshots table
    op.create_table(
        'kpi_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kpi_type', sa.String(100), nullable=False),
        sa.Column('value', sa.Numeric(precision=15, scale=6), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create marketplace_trades table (for carbon credit marketplace)
    op.create_table(
        'marketplace_trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seller_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('credits', sa.Numeric(precision=15, scale=6), nullable=False),
        sa.Column('price_per_credit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seller_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index(op.f('ix_organizations_tenant_id'), 'organizations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_facilities_tenant_id'), 'facilities', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_facilities_organization_id'), 'facilities', ['organization_id'], unique=False)
    op.create_index(op.f('ix_meters_facility_id'), 'meters', ['facility_id'], unique=False)
    op.create_index(op.f('ix_meters_tenant_id'), 'meters', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_carbon_calculations_organization_id'), 'carbon_calculations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_carbon_calculations_facility_id'), 'carbon_calculations', ['facility_id'], unique=False)
    op.create_index(op.f('ix_carbon_calculations_tenant_id'), 'carbon_calculations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_kpi_snapshots_organization_id'), 'kpi_snapshots', ['organization_id'], unique=False)
    op.create_index(op.f('ix_kpi_snapshots_tenant_id'), 'kpi_snapshots', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_tenant_id'), 'audit_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_marketplace_trades_tenant_id'), 'marketplace_trades', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_marketplace_trades_buyer_id'), 'marketplace_trades', ['buyer_id'], unique=False)
    op.create_index(op.f('ix_marketplace_trades_seller_id'), 'marketplace_trades', ['seller_id'], unique=False)


def downgrade() -> None:
    """Rollback the initial schema migration."""

    # Drop indexes
    op.drop_index(op.f('ix_marketplace_trades_seller_id'), table_name='marketplace_trades')
    op.drop_index(op.f('ix_marketplace_trades_buyer_id'), table_name='marketplace_trades')
    op.drop_index(op.f('ix_marketplace_trades_tenant_id'), table_name='marketplace_trades')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_tenant_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_kpi_snapshots_tenant_id'), table_name='kpi_snapshots')
    op.drop_index(op.f('ix_kpi_snapshots_organization_id'), table_name='kpi_snapshots')
    op.drop_index(op.f('ix_carbon_calculations_tenant_id'), table_name='carbon_calculations')
    op.drop_index(op.f('ix_carbon_calculations_facility_id'), table_name='carbon_calculations')
    op.drop_index(op.f('ix_carbon_calculations_organization_id'), table_name='carbon_calculations')
    op.drop_index(op.f('ix_meters_tenant_id'), table_name='meters')
    op.drop_index(op.f('ix_meters_facility_id'), table_name='meters')
    op.drop_index(op.f('ix_facilities_organization_id'), table_name='facilities')
    op.drop_index(op.f('ix_facilities_tenant_id'), table_name='facilities')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_index(op.f('ix_organizations_tenant_id'), table_name='organizations')

    # Drop tables
    op.drop_table('marketplace_trades')
    op.drop_table('kpi_snapshots')
    op.drop_table('carbon_calculations')
    op.drop_table('meters')
    op.drop_table('facility_users')
    op.drop_table('facilities')
    op.drop_table('audit_logs')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('organizations')
    op.drop_table('tenants')
