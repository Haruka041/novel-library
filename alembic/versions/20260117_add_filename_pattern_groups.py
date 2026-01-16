"""add filename pattern groups

Revision ID: 20260117_fnpg
Revises: 20260117_add_library_tags_table
Create Date: 2026-01-17 03:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260117_fnpg'
down_revision: Union[str, None] = '20260117_lt'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加捕获组字段到filename_patterns表
    op.add_column('filename_patterns', sa.Column('title_group', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('filename_patterns', sa.Column('author_group', sa.Integer(), nullable=True, server_default='2'))
    op.add_column('filename_patterns', sa.Column('extra_group', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('filename_patterns', sa.Column('library_id', sa.Integer(), nullable=True))
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_filename_patterns_library',
        'filename_patterns', 'libraries',
        ['library_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_filename_patterns_library', 'filename_patterns', type_='foreignkey')
    op.drop_column('filename_patterns', 'library_id')
    op.drop_column('filename_patterns', 'extra_group')
    op.drop_column('filename_patterns', 'author_group')
    op.drop_column('filename_patterns', 'title_group')
