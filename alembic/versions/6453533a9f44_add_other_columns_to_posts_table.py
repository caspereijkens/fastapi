"""Add other columns to posts table

Revision ID: 6453533a9f44
Revises: 2d641ef3357c
Create Date: 2022-03-19 19:46:55.901211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6453533a9f44'
down_revision = '2d641ef3357c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column(
        'published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column(
        'edited', sa.Boolean(), nullable=False, server_default='FALSE'),)
    op.add_column('posts', sa.Column(
        'created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)
    pass


def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'edited')
    op.drop_column('posts', 'created_at')
    pass
