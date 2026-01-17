"""add library content rating

Revision ID: 20260117_lib_rating
Revises: 20260117_add_library_tags_table
Create Date: 2026-01-17 13:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260117_lib_rating'
down_revision: Union[str, None] = '20260117_add_library_tags_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加书库内容分级字段
    op.add_column('libraries', sa.Column('content_rating', sa.String(20), server_default='general', nullable=True))


def downgrade() -> None:
    op.drop_column('libraries', 'content_rating')
