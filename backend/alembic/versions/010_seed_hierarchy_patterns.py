"""Seed 5 predefined hierarchy patterns for Sprint 15

Revision ID: 010_seed_hierarchy_patterns
Revises: 009_generic_hierarchy
Create Date: 2026-03-11

This migration seeds 5 industry-specific hierarchy patterns:
1. IT/DataCenter (8 levels: Region → Campus → DataCenter → Building → Floor → Room → Rack → Device)
2. Corporate (5 levels: Organization → Division → Department → Team → Individual)
3. Energy Portfolio (5 levels: Portfolio → Plant → Facility → Unit → Equipment)
4. Real Estate (6 levels: Portfolio → Region → Campus → Building → Floor → Space)
5. Supply Chain (5 levels: Company → Supplier → Site → Department → Process)

Each pattern includes complete level definitions with metadata, constraints, and UI configuration.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid

# revision identifiers
revision = '010_seed_hierarchy_patterns'
down_revision = '009_generic_hierarchy'
branch_labels = None
depends_on = None


# Global system tenant ID (for seeding patterns)
SYSTEM_TENANT_ID = uuid.UUID('00000000-0000-0000-0000-000000000000')


def get_pattern_data():
    """Define all 5 hierarchy patterns with complete configuration"""
    return [
        # ===== PATTERN 1: IT/DATACENTER =====
        {
            'pattern_name': 'it_datacenter',
            'pattern_type': 'system',
            'description': 'IT/DataCenter infrastructure hierarchy for tracking physical infrastructure, power, and cooling',
            'levels': [
                {'level': 1, 'name': 'Region', 'singular': 'region', 'min_children': 0, 'max_children': None, 'icon': 'globe', 'color': '#1E40AF'},
                {'level': 2, 'name': 'Campus', 'singular': 'campus', 'min_children': 1, 'max_children': 10, 'icon': 'building-2', 'color': '#1E3A8A'},
                {'level': 3, 'name': 'DataCenter', 'singular': 'datacenter', 'min_children': 0, 'max_children': 5, 'icon': 'server', 'color': '#0F172A'},
                {'level': 4, 'name': 'Building', 'singular': 'building', 'min_children': 0, 'max_children': 20, 'icon': 'home', 'color': '#3730A3'},
                {'level': 5, 'name': 'Floor', 'singular': 'floor', 'min_children': 0, 'max_children': 100, 'icon': 'layers', 'color': '#581C87'},
                {'level': 6, 'name': 'Room', 'singular': 'room', 'min_children': 0, 'max_children': 50, 'icon': 'box', 'color': '#7C2D12'},
                {'level': 7, 'name': 'Rack', 'singular': 'rack', 'min_children': 0, 'max_children': None, 'icon': 'layers-3', 'color': '#BE7B04'},
                {'level': 8, 'name': 'Device', 'singular': 'device', 'min_children': 0, 'max_children': None, 'icon': 'cpu', 'color': '#BE540E'},
            ]
        },
        # ===== PATTERN 2: CORPORATE =====
        {
            'pattern_name': 'corporate',
            'pattern_type': 'system',
            'description': 'Corporate organizational structure for enterprise hierarchies',
            'levels': [
                {'level': 1, 'name': 'Organization', 'singular': 'organization', 'min_children': 0, 'max_children': None, 'icon': 'building', 'color': '#1E3A8A'},
                {'level': 2, 'name': 'Division', 'singular': 'division', 'min_children': 0, 'max_children': 20, 'icon': 'sitemap', 'color': '#1E40AF'},
                {'level': 3, 'name': 'Department', 'singular': 'department', 'min_children': 1, 'max_children': 50, 'icon': 'users', 'color': '#0F172A'},
                {'level': 4, 'name': 'Team', 'singular': 'team', 'min_children': 0, 'max_children': 20, 'icon': 'users-group', 'color': '#3730A3'},
                {'level': 5, 'name': 'Individual', 'singular': 'individual', 'min_children': 0, 'max_children': 10, 'icon': 'user', 'color': '#581C87'},
            ]
        },
        # ===== PATTERN 3: ENERGY PORTFOLIO =====
        {
            'pattern_name': 'energy_portfolio',
            'pattern_type': 'system',
            'description': 'Energy portfolio hierarchy for generation, distribution, and consumption tracking',
            'levels': [
                {'level': 1, 'name': 'Portfolio', 'singular': 'portfolio', 'min_children': 0, 'max_children': None, 'icon': 'zap', 'color': '#EAB308'},
                {'level': 2, 'name': 'Plant', 'singular': 'plant', 'min_children': 0, 'max_children': 50, 'icon': 'factory', 'color': '#DC2626'},
                {'level': 3, 'name': 'Facility', 'singular': 'facility', 'min_children': 1, 'max_children': 100, 'icon': 'building-2', 'color': '#9CA3AF'},
                {'level': 4, 'name': 'Unit', 'singular': 'unit', 'min_children': 0, 'max_children': 500, 'icon': 'cpu', 'color': '#1F2937'},
                {'level': 5, 'name': 'Equipment', 'singular': 'equipment', 'min_children': 0, 'max_children': None, 'icon': 'tool', 'color': '#6B7280'},
            ]
        },
        # ===== PATTERN 4: REAL ESTATE =====
        {
            'pattern_name': 'real_estate',
            'pattern_type': 'system',
            'description': 'Real estate and facilities hierarchy for property management',
            'levels': [
                {'level': 1, 'name': 'Portfolio', 'singular': 'portfolio', 'min_children': 0, 'max_children': None, 'icon': 'home', 'color': '#7C3AED'},
                {'level': 2, 'name': 'Region', 'singular': 'region', 'min_children': 0, 'max_children': 10, 'icon': 'map-pin', 'color': '#5B21B6'},
                {'level': 3, 'name': 'Campus', 'singular': 'campus', 'min_children': 0, 'max_children': 20, 'icon': 'building-2', 'color': '#4C1D95'},
                {'level': 4, 'name': 'Building', 'singular': 'building', 'min_children': 1, 'max_children': 100, 'icon': 'building', 'color': '#6B21A8'},
                {'level': 5, 'name': 'Floor', 'singular': 'floor', 'min_children': 0, 'max_children': 500, 'icon': 'layers', 'color': '#7E22CE'},
                {'level': 6, 'name': 'Space', 'singular': 'space', 'min_children': 0, 'max_children': None, 'icon': 'square-2-stack', 'color': '#A855F7'},
            ]
        },
        # ===== PATTERN 5: SUPPLY CHAIN =====
        {
            'pattern_name': 'supply_chain',
            'pattern_type': 'system',
            'description': 'Supply chain hierarchy for vendor and procurement management',
            'levels': [
                {'level': 1, 'name': 'Company', 'singular': 'company', 'min_children': 0, 'max_children': None, 'icon': 'briefcase', 'color': '#05B6D1'},
                {'level': 2, 'name': 'Supplier', 'singular': 'supplier', 'min_children': 0, 'max_children': None, 'icon': 'users', 'color': '#0891B2'},
                {'level': 3, 'name': 'Site', 'singular': 'site', 'min_children': 0, 'max_children': None, 'icon': 'map-pin', 'color': '#06B6D4'},
                {'level': 4, 'name': 'Department', 'singular': 'department', 'min_children': 0, 'max_children': None, 'icon': 'folder', 'color': '#00D9FF'},
                {'level': 5, 'name': 'Process', 'singular': 'process', 'min_children': 0, 'max_children': None, 'icon': 'gear', 'color': '#22D3EE'},
            ]
        },
    ]


def upgrade():
    """Seed all 5 hierarchy patterns into the database"""

    # Get a connection to execute the inserts
    connection = op.get_bind()

    pattern_data = get_pattern_data()

    for pattern_config in pattern_data:
        # Insert hierarchy_pattern record
        pattern_id = uuid.uuid4()

        connection.execute(f"""
            INSERT INTO hierarchy_patterns
            (id, tenant_id, pattern_name, pattern_type, description, levels, is_active, is_default, created_at, updated_at)
            VALUES (
                '{pattern_id}',
                '{SYSTEM_TENANT_ID}',
                '{pattern_config['pattern_name']}',
                '{pattern_config['pattern_type']}',
                '{pattern_config['description'].replace("'", "''")}',
                '[]'::jsonb,
                true,
                false,
                NOW(),
                NOW()
            )
        """)

        # Insert hierarchy_level records for each level in the pattern
        for level_def in pattern_config['levels']:
            level_id = uuid.uuid4()

            connection.execute(f"""
                INSERT INTO hierarchy_levels
                (id, tenant_id, pattern_id, level_number, level_name, level_singular, description,
                 min_children, max_children, icon_name, color_code, is_active, created_at, updated_at)
                VALUES (
                    '{level_id}',
                    '{SYSTEM_TENANT_ID}',
                    '{pattern_id}',
                    {level_def['level']},
                    '{level_def['name']}',
                    '{level_def['singular']}',
                    '{pattern_config['description'].replace("'", "''") + " - Level: " + level_def['name']}',
                    {level_def['min_children']},
                    {level_def['max_children'] or 'NULL'},
                    '{level_def['icon']}',
                    '{level_def['color']}',
                    true,
                    NOW(),
                    NOW()
                )
            """)


def downgrade():
    """Remove seeded hierarchy patterns"""

    connection = op.get_bind()

    # Delete all patterns seeded to the system tenant
    pattern_names = [
        'it_datacenter',
        'corporate',
        'energy_portfolio',
        'real_estate',
        'supply_chain'
    ]

    for pattern_name in pattern_names:
        connection.execute(f"""
            DELETE FROM hierarchy_patterns
            WHERE tenant_id = '{SYSTEM_TENANT_ID}'
            AND pattern_name = '{pattern_name}'
        """)
