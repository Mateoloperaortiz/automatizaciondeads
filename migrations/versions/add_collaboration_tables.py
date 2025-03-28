"""Add collaboration tables

Revision ID: 67dfcdcf8802
Revises: 55dfae7c7f01
Create Date: 2025-03-26 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67dfcdcf8802'
down_revision = '55dfae7c7f01'
branch_labels = None
depends_on = None


def upgrade():
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create campaign_collaborators table
    op.create_table('campaign_collaborators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_viewed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['ad_campaigns.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'user_id', name='uix_campaign_user')
    )
    
    # Add user_id field to the ad_campaigns table to track ownership
    op.add_column('ad_campaigns', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ad_campaigns', 'users', ['user_id'], ['id'])


def downgrade():
    # Remove user_id field from ad_campaigns
    op.drop_constraint(None, 'ad_campaigns', type_='foreignkey')
    op.drop_column('ad_campaigns', 'user_id')
    
    # Drop collaboration tables
    op.drop_table('campaign_collaborators')
    op.drop_table('team_members')
    op.drop_table('teams')