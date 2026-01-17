"""add annotations table

Revision ID: 20260117_annotations
Revises: 20260117_add_book_groups
Create Date: 2026-01-17 18:38:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260117_annotations'
down_revision = '20260117_add_book_groups'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 annotations 表
    op.create_table('annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('chapter_index', sa.Integer(), nullable=False),
        sa.Column('chapter_title', sa.String(200), nullable=True),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('selected_text', sa.Text(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('annotation_type', sa.String(20), default='highlight'),
        sa.Column('color', sa.String(20), default='yellow'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_annotations_id'), 'annotations', ['id'], unique=False)
    op.create_index(op.f('ix_annotations_user_id'), 'annotations', ['user_id'], unique=False)
    op.create_index(op.f('ix_annotations_book_id'), 'annotations', ['book_id'], unique=False)
    op.create_index(op.f('ix_annotations_created_at'), 'annotations', ['created_at'], unique=False)
    
    # 创建唯一约束
    op.create_unique_constraint(
        'uq_user_book_annotation_position', 
        'annotations', 
        ['user_id', 'book_id', 'chapter_index', 'start_offset', 'end_offset']
    )


def downgrade() -> None:
    op.drop_constraint('uq_user_book_annotation_position', 'annotations', type_='unique')
    op.drop_index(op.f('ix_annotations_created_at'), table_name='annotations')
    op.drop_index(op.f('ix_annotations_book_id'), table_name='annotations')
    op.drop_index(op.f('ix_annotations_user_id'), table_name='annotations')
    op.drop_index(op.f('ix_annotations_id'), table_name='annotations')
    op.drop_table('annotations')
