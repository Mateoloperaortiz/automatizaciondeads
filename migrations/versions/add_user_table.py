"""Add user table for authentication

Revision ID: 55dfae7c7f01
Revises: ebd6d5887923
Create Date: 2025-03-26 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55dfae7c7f01'
down_revision = 'ebd6d5887923'
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('first_name', sa.String(length=64), nullable=True),
        sa.Column('last_name', sa.String(length=64), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('preferences', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for faster lookups
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create admin user for initial setup
    from datetime import datetime
    from sqlalchemy.sql import table, column
    from sqlalchemy import String, Integer, DateTime, Boolean
    from werkzeug.security import generate_password_hash
    
    # Define table structure for data insertion
    users_table = table('users',
        column('id', Integer),
        column('username', String),
        column('email', String),
        column('password_hash', String),
        column('first_name', String),
        column('last_name', String),
        column('role', String),
        column('is_active', Boolean),
        column('created_at', DateTime),
        column('last_login', DateTime)
    )
    
    # Insert admin user
    op.bulk_insert(users_table,
        [
            {
                'id': 1,
                'username': 'admin',
                'email': 'admin@magneto365.com',
                'password_hash': generate_password_hash('adminpassword'),
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_active': True,
                'created_at': datetime.utcnow()
            }
        ]
    )


def downgrade():
    # Drop users table
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')