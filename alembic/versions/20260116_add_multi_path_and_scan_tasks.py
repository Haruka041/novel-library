"""add multi path and scan tasks support

Revision ID: 20260116_multipath
Revises: a65cf1a541fe
Create Date: 2026-01-16 20:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20260116_add_multi_path_and_scan_tasks'
down_revision = '868a6b4cdfa7'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 library_paths 表
    op.create_table(
        'library_paths',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('library_id', sa.Integer(), sa.ForeignKey('libraries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )
    op.create_index('ix_library_paths_library_id', 'library_paths', ['library_id'])
    
    # 迁移现有数据：将 libraries.path 迁移到 library_paths 表
    op.execute("""
        INSERT INTO library_paths (library_id, path, enabled, created_at)
        SELECT id, path, true, created_at FROM libraries WHERE path IS NOT NULL AND path != ''
    """)
    
    # 创建 scan_tasks 表
    op.create_table(
        'scan_tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('library_id', sa.Integer(), sa.ForeignKey('libraries.id'), nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), default=0),
        sa.Column('total_files', sa.Integer(), default=0),
        sa.Column('processed_files', sa.Integer(), default=0),
        sa.Column('added_books', sa.Integer(), default=0),
        sa.Column('skipped_books', sa.Integer(), default=0),
        sa.Column('error_count', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )
    op.create_index('ix_scan_tasks_library_id', 'scan_tasks', ['library_id'])
    op.create_index('ix_scan_tasks_status', 'scan_tasks', ['status'])
    op.create_index('ix_scan_tasks_created_at', 'scan_tasks', ['created_at'])
    
    # 修改 libraries.path 为可空（向后兼容）
    # SQLite 不支持直接修改列，需要重建表或保持现有约束
    # 为简化，保持 path 字段，在新系统中优先使用 library_paths


def downgrade():
    # 删除索引
    op.drop_index('ix_scan_tasks_created_at', 'scan_tasks')
    op.drop_index('ix_scan_tasks_status', 'scan_tasks')
    op.drop_index('ix_scan_tasks_library_id', 'scan_tasks')
    op.drop_index('ix_library_paths_library_id', 'library_paths')
    
    # 删除表
    op.drop_table('scan_tasks')
    op.drop_table('library_paths')
