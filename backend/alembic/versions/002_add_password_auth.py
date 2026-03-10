"""Add password authentication fields to users table

Revision ID: 002_add_password_auth
Revises: 001_initial_schema
Create Date: 2026-03-10 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_password_auth'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add password_hash and last_login columns to users table"""
    # Add password_hash column (nullable for legacy/SSO users)
    op.add_column('users', sa.Column(
        'password_hash',
        sa.String(255),
        nullable=True,
        comment='Argon2 hashed password for real authentication'
    ))

    # Add last_login column to track login timestamps
    op.add_column('users', sa.Column(
        'last_login',
        sa.DateTime(),
        nullable=True,
        comment='Timestamp of last successful login'
    ))


def downgrade() -> None:
    """Remove password_hash and last_login columns from users table"""
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'password_hash')
