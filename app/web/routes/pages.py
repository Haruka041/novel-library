"""
页面路由
提供旧版HTML页面（已弃用，保留给非Flutter客户端）
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.web.app import templates

router = APIRouter()


# 旧版阅读器路由已删除，现在使用 Flutter 原生阅读器
# 如果通过旧链接访问，重定向到 Flutter UI

@router.get("/legacy/reader/{book_id}", response_class=HTMLResponse)
async def legacy_reader_page(request: Request, book_id: int):
    """
    旧版阅读器入口（保留供兼容性）
    建议使用 Flutter 阅读器: /#/reader/{book_id}
    """
    return templates.TemplateResponse(
        "reader.html",
        {"request": request, "book_id": book_id, "title": "在线阅读"}
    )


@router.get("/legacy/reader/txt/{book_id}", response_class=HTMLResponse)
async def legacy_txt_reader_page(request: Request, book_id: int):
    """旧版TXT阅读器页面"""
    return templates.TemplateResponse(
        "reader_txt.html",
        {"request": request, "book_id": book_id, "title": "TXT阅读器"}
    )


@router.get("/legacy/reader/epub/{book_id}", response_class=HTMLResponse)
async def legacy_epub_reader_page(request: Request, book_id: int):
    """旧版EPUB阅读器页面"""
    return templates.TemplateResponse(
        "reader_epub.html",
        {"request": request, "book_id": book_id, "title": "EPUB阅读器"}
    )
