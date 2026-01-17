"""
AI 配置模块
支持多种AI服务提供商（OpenAI、Claude、本地模型等）
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass, field, asdict

from app.utils.logger import log


@dataclass
class AIProviderConfig:
    """AI服务提供商配置"""
    provider: Literal["openai", "claude", "ollama", "custom"] = "openai"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    
    # 功能开关
    enabled: bool = False
    
    # 分析采样数
    sample_size: int = 15  # AI分析文件名时的采样数量
    
    # 自定义设置
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class AIFeaturesConfig:
    """AI功能配置"""
    # 元数据增强
    metadata_enhancement: bool = True  # 启用AI元数据增强
    auto_extract_title: bool = True     # 自动提取书名
    auto_extract_author: bool = True    # 自动提取作者
    auto_generate_summary: bool = True  # 自动生成简介
    
    # 智能分类
    smart_classification: bool = True   # 智能分类
    auto_tagging: bool = True           # 自动打标签
    content_rating: bool = True         # 内容分级
    
    # 搜索增强
    semantic_search: bool = False       # 语义搜索（需要向量数据库）
    
    # 批量处理限制
    batch_limit: int = 50              # 单次批量处理最大数量
    daily_limit: int = 1000            # 每日调用限制


class AIConfig:
    """AI配置管理器"""
    
    CONFIG_FILE = "data/ai_config.json"
    
    def __init__(self):
        self.provider = AIProviderConfig()
        self.features = AIFeaturesConfig()
        self._load_config()
    
    def _get_config_path(self) -> Path:
        """获取配置文件路径"""
        return Path(self.CONFIG_FILE)
    
    def _load_config(self):
        """从文件加载配置"""
        config_path = self._get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载provider配置
                if 'provider' in data:
                    provider_data = data['provider']
                self.provider = AIProviderConfig(
                        provider=provider_data.get('provider', 'openai'),
                        api_key=provider_data.get('api_key'),
                        api_base=provider_data.get('api_base'),
                        model=provider_data.get('model', 'gpt-3.5-turbo'),
                        max_tokens=provider_data.get('max_tokens', 2000),
                        temperature=provider_data.get('temperature', 0.7),
                        timeout=provider_data.get('timeout', 30),
                        enabled=provider_data.get('enabled', False),
                        sample_size=provider_data.get('sample_size', 15),
                        custom_headers=provider_data.get('custom_headers', {}),
                    )
                
                # 加载features配置
                if 'features' in data:
                    features_data = data['features']
                    self.features = AIFeaturesConfig(
                        metadata_enhancement=features_data.get('metadata_enhancement', True),
                        auto_extract_title=features_data.get('auto_extract_title', True),
                        auto_extract_author=features_data.get('auto_extract_author', True),
                        auto_generate_summary=features_data.get('auto_generate_summary', True),
                        smart_classification=features_data.get('smart_classification', True),
                        auto_tagging=features_data.get('auto_tagging', True),
                        content_rating=features_data.get('content_rating', True),
                        semantic_search=features_data.get('semantic_search', False),
                        batch_limit=features_data.get('batch_limit', 50),
                        daily_limit=features_data.get('daily_limit', 1000),
                    )
                
                log.info("AI配置加载成功")
                
            except Exception as e:
                log.warning(f"加载AI配置失败，使用默认配置: {e}")
        else:
            log.info("AI配置文件不存在，使用默认配置")
    
    def save_config(self):
        """保存配置到文件"""
        config_path = self._get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'provider': asdict(self.provider),
            'features': asdict(self.features),
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        log.info("AI配置已保存")
    
    def update_provider(self, **kwargs) -> AIProviderConfig:
        """更新provider配置"""
        for key, value in kwargs.items():
            if hasattr(self.provider, key):
                setattr(self.provider, key, value)
        
        self.save_config()
        return self.provider
    
    def update_features(self, **kwargs) -> AIFeaturesConfig:
        """更新features配置"""
        for key, value in kwargs.items():
            if hasattr(self.features, key):
                setattr(self.features, key, value)
        
        self.save_config()
        return self.features
    
    def is_enabled(self) -> bool:
        """检查AI是否启用"""
        return self.provider.enabled and self.provider.api_key is not None
    
    def get_status(self) -> Dict[str, Any]:
        """获取AI状态信息"""
        return {
            "enabled": self.is_enabled(),
            "provider": self.provider.provider,
            "model": self.provider.model,
            "has_api_key": self.provider.api_key is not None,
            "features": asdict(self.features),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        provider_dict = asdict(self.provider)
        # 隐藏API密钥
        if provider_dict.get('api_key'):
            provider_dict['api_key'] = '***' + provider_dict['api_key'][-4:] if len(provider_dict['api_key']) > 4 else '****'
        
        return {
            'provider': provider_dict,
            'features': asdict(self.features),
        }


# 全局单例
ai_config = AIConfig()
