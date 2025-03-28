"""initial migration

Revision ID: ebd6d5887923
Revises: 
Create Date: 2025-03-25 11:02:46.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'ebd6d5887923'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the platform_connection_status table
    op.create_table(
        'platform_connection_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('is_connected', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('last_successful_connection', sa.DateTime(), nullable=True),
        sa.Column('connection_details', JSONB(), nullable=True),
        sa.Column('status_message', sa.String(255), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('api_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on platform column
    op.create_index(
        'idx_platform_connection_status_platform',
        'platform_connection_status',
        ['platform']
    )


def downgrade():
    # Drop the platform_connection_status table
    op.drop_index('idx_platform_connection_status_platform')
    op.drop_table('platform_connection_status')