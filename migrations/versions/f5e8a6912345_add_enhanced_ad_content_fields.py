"""add enhanced ad content fields and connection status tracking

Revision ID: f5e8a6912345
Revises: ebd6d5887923
Create Date: 2025-03-26 13:45:20.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'f5e8a6912345'
down_revision = 'ebd6d5887923'
branch_labels = None
depends_on = None


def upgrade():
    # Add enhanced ad content fields to the ad_campaigns table
    op.add_column('ad_campaigns', sa.Column('ad_headline', sa.String(100), nullable=True))
    op.add_column('ad_campaigns', sa.Column('ad_text', sa.Text(), nullable=True))
    op.add_column('ad_campaigns', sa.Column('ad_cta', sa.String(50), nullable=True))
    op.add_column('ad_campaigns', sa.Column('ad_image_url', sa.String(255), nullable=True))
    op.add_column('ad_campaigns', sa.Column('platform_specific_content', sa.Text(), nullable=True))
    
    # Add columns to platform_connection_status table for further tracking
    op.add_column('platform_connection_status', sa.Column('performance_score', sa.Integer(), nullable=True))
    op.add_column('platform_connection_status', sa.Column('failure_count', sa.Integer(), nullable=True, default=0))
    op.add_column('platform_connection_status', sa.Column('health_status', sa.String(50), nullable=True))
    op.add_column('platform_connection_status', sa.Column('connection_history', JSONB(), nullable=True))


def downgrade():
    # Remove the enhanced ad content fields
    op.drop_column('ad_campaigns', 'platform_specific_content')
    op.drop_column('ad_campaigns', 'ad_image_url')
    op.drop_column('ad_campaigns', 'ad_cta')
    op.drop_column('ad_campaigns', 'ad_text')
    op.drop_column('ad_campaigns', 'ad_headline')
    
    # Remove the platform connection status tracking columns
    op.drop_column('platform_connection_status', 'connection_history')
    op.drop_column('platform_connection_status', 'health_status')
    op.drop_column('platform_connection_status', 'failure_count')
    op.drop_column('platform_connection_status', 'performance_score')