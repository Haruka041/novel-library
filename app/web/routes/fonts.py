"""
字体管理 API
"""
import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user
from app.models import User

router = APIRouter(prefix="/api/fonts", tags=["fonts"])

# 字体存储目录
FONTS_DIR = Path("/data/fonts")
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# 允许的字体格式
ALLOWED_EXTENSIONS = {'.ttf', '.otf', '.woff', '.woff2'}

# 内置字体列表
BUILTIN_FONTS = [
    {"id": "system", "name": "系统默认", "family": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'},
    {"id": "noto-serif", "name": "思源宋体", "family": '"Noto Serif SC", "Source Han Serif CN", serif'},
    {"id": "noto-sans", "name": "思源黑体", "family": '"Noto Sans SC", "Source Han Sans CN", sans-serif'},
    {"id": "fangsong", "name": "仿宋", "family": '"FangSong", "STFangsong", serif'},
    {"id": "kaiti", "name": "楷体", "family": '"KaiTi", "STKaiti", serif'},
    {"id": "songti", "name": "宋体", "family": '"SimSun", "STSong", serif'},
]


class FontInfo(BaseModel):
    id: str
    name: str
    family: str
    is_builtin: bool = False
    file_url: Optional[str] = None


class FontListResponse(BaseModel):
    fonts: List[FontInfo]


def get_custom_fonts() -> List[FontInfo]:
    """获取自定义字体列表"""
    fonts = []
    if FONTS_DIR.exists():
        for font_file in FONTS_DIR.iterdir():
            if font_file.suffix.lower() in ALLOWED_EXTENSIONS:
                font_name = font_file.stem
                fonts.append(FontInfo(
                    id=f"custom-{font_name}",
                    name=font_name,
                    family=f'"{font_name}"',
                    is_builtin=False,
                    file_url=f"/api/fonts/file/{font_file.name}"
                ))
    return fonts


@router.get("", response_model=FontListResponse)
async def list_fonts(current_user: User = Depends(get_current_user)):
    """获取所有可用字体"""
    # 内置字体
    builtin = [FontInfo(
        id=f["id"],
        name=f["name"],
        family=f["family"],
        is_builtin=True
    ) for f in BUILTIN_FONTS]
    
    # 自定义字体
    custom = get_custom_fonts()
    
    return FontListResponse(fonts=builtin + custom)


@router.post("/upload")
async def upload_font(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传自定义字体（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查文件类型
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的字体格式。支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 保存字体文件
    font_name = Path(filename).stem
    # 清理文件名
    safe_name = "".join(c for c in font_name if c.isalnum() or c in '-_ ')
    if not safe_name:
        safe_name = str(uuid.uuid4())[:8]
    
    save_path = FONTS_DIR / f"{safe_name}{ext}"
    
    # 检查是否已存在
    if save_path.exists():
        raise HTTPException(status_code=400, detail=f"字体 '{safe_name}' 已存在")
    
    # 保存文件
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    
    return {
        "message": "字体上传成功",
        "font": {
            "id": f"custom-{safe_name}",
            "name": safe_name,
            "family": f'"{safe_name}"',
            "file_url": f"/api/fonts/file/{safe_name}{ext}"
        }
    }


@router.delete("/{font_id}")
async def delete_font(
    font_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除自定义字体（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    if not font_id.startswith("custom-"):
        raise HTTPException(status_code=400, detail="不能删除内置字体")
    
    font_name = font_id[7:]  # 去掉 "custom-" 前缀
    
    # 查找并删除字体文件
    deleted = False
    for ext in ALLOWED_EXTENSIONS:
        font_path = FONTS_DIR / f"{font_name}{ext}"
        if font_path.exists():
            font_path.unlink()
            deleted = True
            break
    
    if not deleted:
        raise HTTPException(status_code=404, detail="字体不存在")
    
    return {"message": "字体删除成功"}


@router.get("/file/{filename}")
async def get_font_file(filename: str):
    """获取字体文件"""
    font_path = FONTS_DIR / filename
    
    if not font_path.exists():
        raise HTTPException(status_code=404, detail="字体文件不存在")
    
    # 确定 MIME 类型
    ext = font_path.suffix.lower()
    mime_types = {
        '.ttf': 'font/ttf',
        '.otf': 'font/otf',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    
    return FileResponse(
        font_path,
        media_type=mime_types.get(ext, 'application/octet-stream'),
        headers={
            'Cache-Control': 'public, max-age=31536000',  # 缓存一年
        }
    )
