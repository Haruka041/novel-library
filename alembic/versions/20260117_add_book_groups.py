"""add book_groups table

Revision ID: 20260117_book_groups
Revises: 20260117_add_library_content_rating
Create Date: 2026-01-17 18:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260117_book_groups'
down_revision = '20260117_add_library_content_rating'
branch_labels = None
depends_on = None


def upgrade():
    # 创建书籍组表
    op.create_table(
        'book_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),  # 组名称（可选，默认使用主书籍标题）
        sa.Column('primary_book_id', sa.Integer(), nullable=True),  # 主书籍ID
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_groups_id'), 'book_groups', ['id'], unique=False)
    op.create_index(op.f('ix_book_groups_primary_book_id'), 'book_groups', ['primary_book_id'], unique=False)
    
    # 在 books 表添加 group_id 字段
    op.add_column('books', sa.Column('group_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_books_group_id', 
        'books', 'book_groups',
        ['group_id'], ['id'],
        ondelete='SET NULL'  # 组删除时不删除书籍，只清空 group_id
    )
    op.create_index(op.f('ix_books_group_id'), 'books', ['group_id'], unique=False)


def downgrade():
    # 删除 books 表的 group_id 字段
    op.drop_index(op.f('ix_books_group_id'), table_name='books')
    op.drop_constraint('fk_books_group_id', 'books', type_='foreignkey')
    op.drop_column('books', 'group_id')
    
    # 删除书籍组表
    op.drop_index(op.f('ix_book_groups_primary_book_id'), table_name='book_groups')
    op.drop_index(op.f('ix_book_groups_id'), table_name='book_groups')
    op.drop_table('book_groups')
