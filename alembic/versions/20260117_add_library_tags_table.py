"""add library_tags table

Revision ID: 20260117_library_tags
Revises: 20260116_add_multi_path_and_scan_tasks
Create Date: 2026-01-17 02:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260117_add_library_tags_table'
down_revision: Union[str, None] = '20260116_add_multi_path_and_scan_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建书库标签关联表
    op.create_table('library_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('library_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['library_id'], ['libraries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('library_id', 'tag_id', name='uq_library_tag')
    )
    op.create_index(op.f('ix_library_tags_id'), 'library_tags', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_library_tags_id'), table_name='library_tags')
    op.drop_table('library_tags')
