"""Add content column to post table

Revision ID: 583a3e6adac6
Revises: f065f8f3ca18
Create Date: 2022-03-19 19:28:43.039003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '583a3e6adac6'
down_revision = 'f065f8f3ca18'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
