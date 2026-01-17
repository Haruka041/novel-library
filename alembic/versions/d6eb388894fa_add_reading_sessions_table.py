"""add reading sessions table

Revision ID: d6eb388894fa
Revises: 20260117_add_filename_pattern_groups
Create Date: 2026-01-17 19:51:59.813125

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6eb388894fa'
down_revision: Union[str, Sequence[str], None] = '20260117_add_filename_pattern_groups'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建阅读会话表
    op.create_table('reading_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), default=0),
        sa.Column('progress', sa.Float(), nullable=True),  # 0.0 - 1.0
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('device_info', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_reading_sessions_id'), 'reading_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_reading_sessions_user_id'), 'reading_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_reading_sessions_book_id'), 'reading_sessions', ['book_id'], unique=False)
    op.create_index(op.f('ix_reading_sessions_start_time'), 'reading_sessions', ['start_time'], unique=False)


def downgrade() -> None:
    # 删除表和索引
    op.drop_index(op.f('ix_reading_sessions_start_time'), table_name='reading_sessions')
    op.drop_index(op.f('ix_reading_sessions_book_id'), table_name='reading_sessions')
    op.drop_index(op.f('ix_reading_sessions_user_id'), table_name='reading_sessions')
    op.drop_index(op.f('ix_reading_sessions_id'), table_name='reading_sessions')
    op.drop_table('reading_sessions')
