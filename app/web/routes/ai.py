"""
AI 配置 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.web.routes.admin import admin_required
from app.core.ai.config import ai_config
from app.core.ai.service import get_ai_service


router = APIRouter(prefix="/api/admin/ai", tags=["AI管理"])


class ProviderUpdate(BaseModel):
    """AI提供商配置更新"""
    provider: Optional[str] = None  # openai, claude, ollama, custom
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    enabled: Optional[bool] = None


class FeaturesUpdate(BaseModel):
    """AI功能配置更新"""
    metadata_enhancement: Optional[bool] = None
    auto_extract_title: Optional[bool] = None
    auto_extract_author: Optional[bool] = None
    auto_generate_summary: Optional[bool] = None
    smart_classification: Optional[bool] = None
    auto_tagging: Optional[bool] = None
    content_rating: Optional[bool] = None
    semantic_search: Optional[bool] = None
    batch_limit: Optional[int] = None
    daily_limit: Optional[int] = None


@router.get("/config")
async def get_ai_config(admin = Depends(admin_required)):
    """获取AI配置"""
    return ai_config.to_dict()


@router.get("/status")
async def get_ai_status(admin = Depends(admin_required)):
    """获取AI状态"""
    return ai_config.get_status()


@router.put("/provider")
async def update_provider(data: ProviderUpdate, admin = Depends(admin_required)):
    """更新AI提供商配置"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的数据")
    
    ai_config.update_provider(**update_data)
    return {"message": "配置已更新", "config": ai_config.to_dict()['provider']}


@router.put("/features")
async def update_features(data: FeaturesUpdate, admin = Depends(admin_required)):
    """更新AI功能配置"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的数据")
    
    ai_config.update_features(**update_data)
    return {"message": "配置已更新", "config": ai_config.to_dict()['features']}


@router.post("/test")
async def test_connection(admin = Depends(admin_required)):
    """测试AI连接"""
    if not ai_config.is_enabled():
        raise HTTPException(status_code=400, detail="AI功能未启用，请先配置API密钥")
    
    service = get_ai_service()
    result = await service.test_connection()
    
    if result.success:
        return {
            "success": True,
            "message": "连接成功",
            "response": result.content,
            "usage": result.usage
        }
    else:
        return {
            "success": False,
            "message": "连接失败",
            "error": result.error
        }


@router.post("/extract-metadata")
async def extract_metadata(
    filename: str,
    content_preview: str = "",
    admin = Depends(admin_required)
):
    """使用AI提取元数据（测试）"""
    if not ai_config.is_enabled():
        raise HTTPException(status_code=400, detail="AI功能未启用")
    
    service = get_ai_service()
    result = await service.extract_metadata(filename, content_preview)
    
    return {
        "success": bool(result),
        "metadata": result
    }


@router.post("/classify")
async def classify_book(
    title: str,
    content_preview: str = "",
    admin = Depends(admin_required)
):
    """使用AI分类书籍（测试）"""
    if not ai_config.is_enabled():
        raise HTTPException(status_code=400, detail="AI功能未启用")
    
    service = get_ai_service()
    result = await service.classify_book(title, content_preview)
    
    return {
        "success": bool(result),
        "classification": result
    }


# 预设模型列表
PRESET_MODELS = {
    "openai": [
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16K"},
    ],
    "claude": [
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
        {"id": "claude-2.1", "name": "Claude 2.1"},
    ],
    "ollama": [
        {"id": "llama2", "name": "Llama 2"},
        {"id": "llama3", "name": "Llama 3"},
        {"id": "mistral", "name": "Mistral"},
        {"id": "qwen", "name": "Qwen"},
        {"id": "yi", "name": "Yi"},
    ],
}


@router.get("/models")
async def get_models(provider: Optional[str] = None, admin = Depends(admin_required)):
    """获取预设模型列表"""
    if provider:
        return PRESET_MODELS.get(provider, [])
    return PRESET_MODELS
