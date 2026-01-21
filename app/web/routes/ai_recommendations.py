"""
AI 推荐与对话式找书
"""
import json
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import (
    Book,
    BookTag,
    Tag,
    User,
    UserFavorite,
    ReadingProgress,
    Author,
    BookVersion,
)
from app.utils.permissions import check_book_access, get_accessible_library_ids
from app.web.routes.auth import get_current_user
from app.core.ai.config import ai_config
from app.core.ai.service import get_ai_service


router = APIRouter()


class RecommendationItem(BaseModel):
    id: int
    title: str
    author_name: Optional[str]
    file_format: str
    file_size: int
    added_at: str
    score: float


class ChatSearchRequest(BaseModel):
    query: str
    limit: int = 20
    library_id: Optional[int] = None


class ChatSearchResponse(BaseModel):
    parsed: Dict[str, Any]
    books: List[Dict[str, Any]]
    total: int


def _get_primary_version(book: Book) -> Optional[BookVersion]:
    if book.versions:
        primary = next((v for v in book.versions if v.is_primary), None)
        if not primary:
            primary = book.versions[0] if book.versions else None
        return primary
    return None


@router.get("/recommendations", response_model=List[RecommendationItem])
async def get_recommendations(
    limit: int = 20,
    library_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    基于阅读历史/收藏/标签的推荐
    """
    accessible_library_ids = await get_accessible_library_ids(current_user, db)
    if not accessible_library_ids:
        return []

    if library_id and library_id in accessible_library_ids:
        accessible_library_ids = [library_id]

    favorite_result = await db.execute(
        select(UserFavorite.book_id).where(UserFavorite.user_id == current_user.id)
    )
    favorite_ids = {row[0] for row in favorite_result.all()}

    progress_result = await db.execute(
        select(ReadingProgress.book_id).where(ReadingProgress.user_id == current_user.id)
    )
    progress_ids = {row[0] for row in progress_result.all()}

    seed_book_ids = favorite_ids | progress_ids

    if not seed_book_ids:
        query = (
            select(Book)
            .where(Book.library_id.in_(accessible_library_ids))
            .options(joinedload(Book.author), joinedload(Book.versions))
            .order_by(Book.added_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        books = result.unique().scalars().all()
        response_items = []
        for book in books:
            if not await check_book_access(current_user, book.id, db):
                continue
            primary = _get_primary_version(book)
            response_items.append(
                RecommendationItem(
                    id=book.id,
                    title=book.title,
                    author_name=book.author.name if book.author else None,
                    file_format=primary.file_format if primary else "unknown",
                    file_size=primary.file_size if primary else 0,
                    added_at=book.added_at.isoformat(),
                    score=0.0,
                )
            )
        return response_items

    tag_result = await db.execute(
        select(BookTag.tag_id).where(BookTag.book_id.in_(seed_book_ids))
    )
    tag_ids = {row[0] for row in tag_result.all()}

    author_result = await db.execute(
        select(Book.author_id).where(Book.id.in_(seed_book_ids))
    )
    author_ids = {row[0] for row in author_result.all() if row[0] is not None}

    query = (
        select(Book)
        .where(Book.library_id.in_(accessible_library_ids))
        .options(
            joinedload(Book.author),
            joinedload(Book.book_tags).joinedload(BookTag.tag),
            joinedload(Book.versions),
        )
    )

    if seed_book_ids:
        query = query.where(Book.id.notin_(seed_book_ids))

    conditions = []
    if tag_ids:
        query = query.outerjoin(BookTag)
        conditions.append(BookTag.tag_id.in_(tag_ids))
    if author_ids:
        conditions.append(Book.author_id.in_(author_ids))
    if conditions:
        query = query.where(or_(*conditions))

    query = query.order_by(Book.added_at.desc()).limit(limit * 5)

    result = await db.execute(query)
    candidate_books = result.unique().scalars().all()

    recommendations: List[RecommendationItem] = []
    for book in candidate_books:
        if not await check_book_access(current_user, book.id, db):
            continue
        primary = _get_primary_version(book)
        book_tag_ids = {bt.tag_id for bt in book.book_tags}
        tag_score = len(book_tag_ids & tag_ids)
        author_score = 2.0 if book.author_id in author_ids else 0.0
        score = tag_score * 2.0 + author_score
        recommendations.append(
            RecommendationItem(
                id=book.id,
                title=book.title,
                author_name=book.author.name if book.author else None,
                file_format=primary.file_format if primary else "unknown",
                file_size=primary.file_size if primary else 0,
                added_at=book.added_at.isoformat(),
                score=score,
            )
        )

    recommendations.sort(key=lambda item: (item.score, item.added_at), reverse=True)
    return recommendations[:limit]


@router.post("/chat-search", response_model=ChatSearchResponse)
async def chat_search(
    request: ChatSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    对话式找书：将自然语言解析为检索条件
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="搜索内容不能为空")

    parsed: Dict[str, Any] = {
        "keywords": request.query.strip(),
        "author": None,
        "tags": [],
        "formats": [],
        "library_id": request.library_id,
    }

    if ai_config.is_enabled():
        prompt = f"""你是一个书籍检索助手。请把用户描述解析成检索条件，只返回JSON。
用户描述: {request.query}

返回JSON格式（字段可为空）:
{{
  "keywords": "核心关键词",
  "author": "作者名或null",
  "tags": ["标签1", "标签2"],
  "formats": ["txt","epub","pdf"],
  "library_id": null
}}
要求:
1. 只返回JSON
2. formats 必须是小写扩展名，不带点
"""
        ai_service = get_ai_service()
        response = await ai_service.chat(
            messages=[
                {"role": "system", "content": "只返回JSON格式，不要解释。"},
                {"role": "user", "content": prompt},
            ]
        )
        if response.success:
            content = response.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(content[start:end])
                except Exception:
                    parsed = parsed

    keywords = (parsed.get("keywords") or "").strip()
    author_name = (parsed.get("author") or "").strip()
    tags = [t for t in (parsed.get("tags") or []) if isinstance(t, str)]
    formats = [f for f in (parsed.get("formats") or []) if isinstance(f, str)]

    accessible_library_ids = await get_accessible_library_ids(current_user, db)
    if not accessible_library_ids:
        return {"parsed": parsed, "books": [], "total": 0}

    if request.library_id and request.library_id in accessible_library_ids:
        accessible_library_ids = [request.library_id]

    query = select(Book).options(
        joinedload(Book.author),
        joinedload(Book.book_tags).joinedload(BookTag.tag),
        joinedload(Book.versions),
    )
    query = query.where(Book.library_id.in_(accessible_library_ids))

    if keywords:
        search_term = f"%{keywords}%"
        query = query.outerjoin(Author, Book.author_id == Author.id)
        query = query.where(
            or_(
                Book.title.like(search_term),
                Author.name.like(search_term),
            )
        )

    if author_name:
        author_result = await db.execute(
            select(Author).where(Author.name.like(f"%{author_name}%"))
        )
        author = author_result.scalars().first()
        if author:
            query = query.where(Book.author_id == author.id)

    if formats:
        normalized = []
        for fmt in formats:
            cleaned = fmt.lower().replace(".", "").strip()
            if cleaned:
                normalized.append(f".{cleaned}")
                normalized.append(cleaned)
        if normalized:
            query = query.outerjoin(BookVersion).where(BookVersion.file_format.in_(normalized))

    if tags:
        query = query.outerjoin(BookTag).outerjoin(Tag).where(Tag.name.in_(tags))

    query = query.order_by(Book.added_at.desc()).limit(request.limit * 3)
    result = await db.execute(query)
    all_books = result.unique().scalars().all()

    filtered_books = []
    for book in all_books:
        if await check_book_access(current_user, book.id, db):
            filtered_books.append(book)

    response_books = []
    for book in filtered_books[: request.limit]:
        primary = _get_primary_version(book)
        response_books.append(
            {
                "id": book.id,
                "title": book.title,
                "author_name": book.author.name if book.author else None,
                "file_format": primary.file_format if primary else "unknown",
                "file_size": primary.file_size if primary else 0,
                "added_at": book.added_at.isoformat(),
            }
        )

    return {
        "parsed": parsed,
        "books": response_books,
        "total": len(filtered_books),
    }
