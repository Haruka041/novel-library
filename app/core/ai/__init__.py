"""
AI 模块
提供AI相关功能，包括元数据增强、智能分类等
"""
from app.core.ai.config import AIConfig, ai_config
from app.core.ai.service import AIService, get_ai_service

__all__ = ['AIConfig', 'ai_config', 'AIService', 'get_ai_service']
