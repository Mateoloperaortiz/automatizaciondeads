"""Rename metadata column to document_metadata

Revision ID: rename_metadata_column
Revises: documentation_models
Create Date: 2025-03-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_metadata_column'
down_revision = 'documentation_models'
branch_labels = None
depends_on = None


def upgrade():
    # Rename the column in the documents table
    with op.batch_alter_table('documents') as batch_op:
        batch_op.alter_column('metadata', new_column_name='document_metadata')


def downgrade():
    # Revert the column name in the documents table
    with op.batch_alter_table('documents') as batch_op:
        batch_op.alter_column('document_metadata', new_column_name='metadata')
