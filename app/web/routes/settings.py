"""
系统设置 API 路由
"""
import json
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models import User
from app.web.routes.admin import admin_required
from app.web.routes.auth import get_current_user
from app.utils.logger import log

router = APIRouter()

# 设置文件路径
SETTINGS_FILE = Path("config/system_settings.json")

# 默认设置
DEFAULT_SETTINGS = {
    "server_name": "小说书库",
    "server_description": "个人小说管理系统",
    "welcome_message": "欢迎使用小说书库",
    "registration_enabled": False,
    "default_theme": "system",
    "default_cover_size": "medium",
}


def load_settings() -> dict:
    """加载系统设置"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                # 合并默认设置和保存的设置
                return {**DEFAULT_SETTINGS, **saved}
        except Exception as e:
            log.error(f"加载系统设置失败: {e}")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> bool:
    """保存系统设置"""
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log.error(f"保存系统设置失败: {e}")
        return False


class SettingsUpdate(BaseModel):
    """更新设置请求"""
    server_name: Optional[str] = None
    server_description: Optional[str] = None
    welcome_message: Optional[str] = None
    registration_enabled: Optional[bool] = None
    default_theme: Optional[str] = None
    default_cover_size: Optional[str] = None


@router.get("/settings/public")
async def get_public_settings():
    """
    获取公开系统设置（无需登录）
    只返回需要公开的设置如服务器名称
    """
    settings = load_settings()
    return {
        "server_name": settings.get("server_name", DEFAULT_SETTINGS["server_name"]),
        "server_description": settings.get("server_description", DEFAULT_SETTINGS["server_description"]),
        "welcome_message": settings.get("welcome_message", DEFAULT_SETTINGS["welcome_message"]),
        "registration_enabled": settings.get("registration_enabled", DEFAULT_SETTINGS["registration_enabled"]),
    }


@router.get("/settings")
async def get_settings(
    current_user: User = Depends(get_current_user)
):
    """
    获取系统设置（需要登录）
    普通用户只能获取部分设置
    """
    settings = load_settings()
    
    # 普通用户返回有限的设置
    return {
        "server_name": settings.get("server_name"),
        "server_description": settings.get("server_description"),
        "welcome_message": settings.get("welcome_message"),
        "default_theme": settings.get("default_theme"),
        "default_cover_size": settings.get("default_cover_size"),
    }


@router.get("/admin/settings")
async def get_admin_settings(
    admin: User = Depends(admin_required)
):
    """
    获取所有系统设置（管理员）
    """
    settings = load_settings()
    return settings


@router.put("/admin/settings")
async def update_settings(
    data: SettingsUpdate,
    admin: User = Depends(admin_required)
):
    """
    更新系统设置（管理员）
    """
    settings = load_settings()
    
    # 更新非空字段
    update_count = 0
    for key, value in data.dict().items():
        if value is not None:
            settings[key] = value
            update_count += 1
    
    if update_count == 0:
        raise HTTPException(status_code=400, detail="没有要更新的设置")
    
    if not save_settings(settings):
        raise HTTPException(status_code=500, detail="保存设置失败")
    
    log.info(f"管理员 {admin.username} 更新了系统设置: {list(data.dict(exclude_none=True).keys())}")
    
    return {
        "message": f"已更新 {update_count} 项设置",
        "settings": settings
    }
