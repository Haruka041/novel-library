"""
书签管理路由
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import Bookmark, Book, User
from app.web.routes.auth import get_current_user
from app.web.routes.dependencies import get_accessible_book
from app.utils.logger import log

router = APIRouter()


# Pydantic 模型
class BookmarkCreate(BaseModel):
    """创建书签请求"""
    book_id: int
    position: str
    chapter_title: Optional[str] = None
    note: Optional[str] = None


class BookmarkUpdate(BaseModel):
    """更新书签请求"""
    note: Optional[str] = None
    chapter_title: Optional[str] = None


class BookmarkResponse(BaseModel):
    """书签响应"""
    id: int
    book_id: int
    book_title: str
    position: str
    chapter_title: Optional[str]
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建书签
    需要有书籍访问权限
    """
    # 验证书籍访问权限
    book = await get_accessible_book(bookmark_data.book_id, db, current_user)
    
    # 创建书签
    bookmark = Bookmark(
        user_id=current_user.id,
        book_id=bookmark_data.book_id,
        position=bookmark_data.position,
        chapter_title=bookmark_data.chapter_title,
        note=bookmark_data.note
    )
    
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    
    log.info(f"用户 {current_user.username} 为书籍 {book.title} 创建书签")
    
    return BookmarkResponse(
        id=bookmark.id,
        book_id=bookmark.book_id,
        book_title=book.title,
        position=bookmark.position,
        chapter_title=bookmark.chapter_title,
        note=bookmark.note,
        created_at=bookmark.created_at,
        updated_at=bookmark.updated_at
    )


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    book_id: Optional[int] = Query(None, description="筛选特定书籍"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的书签列表
    可选按书籍筛选
    """
    query = select(Bookmark).where(Bookmark.user_id == current_user.id)
    
    if book_id is not None:
        query = query.where(Bookmark.book_id == book_id)
    
    query = query.options(joinedload(Bookmark.book)).order_by(Bookmark.created_at.desc())
    
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    
    return [
        BookmarkResponse(
            id=b.id,
            book_id=b.book_id,
            book_title=b.book.title,
            position=b.position,
            chapter_title=b.chapter_title,
            note=b.note,
            created_at=b.created_at,
            updated_at=b.updated_at
        )
        for b in bookmarks
    ]


@router.get("/books/{book_id}/bookmarks", response_model=List[BookmarkResponse])
async def get_book_bookmarks(
    book: Book = Depends(get_accessible_book),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取特定书籍的书签列表
    需要有书籍访问权限
    """
    query = (
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id)
        .where(Bookmark.book_id == book.id)
        .order_by(Bookmark.created_at.desc())
    )
    
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    
    return [
        BookmarkResponse(
            id=b.id,
            book_id=b.book_id,
            book_title=book.title,
            position=b.position,
            chapter_title=b.chapter_title,
            note=b.note,
            created_at=b.created_at,
            updated_at=b.updated_at
        )
        for b in bookmarks
    ]


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_data: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新书签（仅备注和章节标题）
    只能更新自己的书签
    """
    # 查询书签
    query = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).options(joinedload(Bookmark.book))
    
    result = await db.execute(query)
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="书签不存在")
    
    # 更新字段
    if bookmark_data.note is not None:
        bookmark.note = bookmark_data.note
    if bookmark_data.chapter_title is not None:
        bookmark.chapter_title = bookmark_data.chapter_title
    
    bookmark.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(bookmark)
    
    return BookmarkResponse(
        id=bookmark.id,
        book_id=bookmark.book_id,
        book_title=bookmark.book.title,
        position=bookmark.position,
        chapter_title=bookmark.chapter_title,
        note=bookmark.note,
        created_at=bookmark.created_at,
        updated_at=bookmark.updated_at
    )


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除书签
    只能删除自己的书签
    """
    # 查询书签
    query = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    )
    
    result = await db.execute(query)
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="书签不存在")
    
    await db.delete(bookmark)
    await db.commit()
    
    log.info(f"用户 {current_user.username} 删除书签 {bookmark_id}")
    
    return {"message": "书签已删除"}
