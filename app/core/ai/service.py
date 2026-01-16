"""
AI 服务模块
提供与AI API的交互功能
"""
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.core.ai.config import ai_config
from app.utils.logger import log


@dataclass
class AIResponse:
    """AI响应"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None  # token使用量


class AIService:
    """AI服务"""
    
    def __init__(self):
        self.config = ai_config
    
    async def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """调用OpenAI API"""
        provider = self.config.provider
        
        url = provider.api_base or "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
            **provider.custom_headers
        }
        
        data = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', provider.max_tokens),
            "temperature": kwargs.get('temperature', provider.temperature),
        }
        
        try:
            async with httpx.AsyncClient(timeout=provider.timeout) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                content = result['choices'][0]['message']['content']
                usage = result.get('usage')
                
                return AIResponse(
                    success=True,
                    content=content,
                    usage=usage
                )
                
        except httpx.TimeoutException:
            return AIResponse(success=False, error="请求超时")
        except httpx.HTTPStatusError as e:
            return AIResponse(success=False, error=f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            log.error(f"OpenAI API调用失败: {e}")
            return AIResponse(success=False, error=str(e))
    
    async def _call_claude(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """调用Claude API"""
        provider = self.config.provider
        
        url = provider.api_base or "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": provider.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
            **provider.custom_headers
        }
        
        # 转换消息格式
        claude_messages = []
        system_prompt = None
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
            else:
                claude_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        data = {
            "model": provider.model,
            "messages": claude_messages,
            "max_tokens": kwargs.get('max_tokens', provider.max_tokens),
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        try:
            async with httpx.AsyncClient(timeout=provider.timeout) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                content = result['content'][0]['text']
                usage = result.get('usage')
                
                return AIResponse(
                    success=True,
                    content=content,
                    usage=usage
                )
                
        except httpx.TimeoutException:
            return AIResponse(success=False, error="请求超时")
        except httpx.HTTPStatusError as e:
            return AIResponse(success=False, error=f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            log.error(f"Claude API调用失败: {e}")
            return AIResponse(success=False, error=str(e))
    
    async def _call_ollama(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """调用Ollama本地模型"""
        provider = self.config.provider
        
        url = (provider.api_base or "http://localhost:11434") + "/api/chat"
        
        data = {
            "model": provider.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', provider.temperature),
                "num_predict": kwargs.get('max_tokens', provider.max_tokens),
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=provider.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                
                content = result['message']['content']
                
                return AIResponse(
                    success=True,
                    content=content
                )
                
        except httpx.TimeoutException:
            return AIResponse(success=False, error="请求超时")
        except Exception as e:
            log.error(f"Ollama API调用失败: {e}")
            return AIResponse(success=False, error=str(e))
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """
        发送聊天请求到AI
        
        Args:
            messages: 消息列表 [{"role": "user/system/assistant", "content": "..."}]
            **kwargs: 额外参数 (max_tokens, temperature等)
        
        Returns:
            AIResponse
        """
        if not self.config.is_enabled():
            return AIResponse(success=False, error="AI功能未启用")
        
        provider_type = self.config.provider.provider
        
        if provider_type == "openai":
            return await self._call_openai(messages, **kwargs)
        elif provider_type == "claude":
            return await self._call_claude(messages, **kwargs)
        elif provider_type == "ollama":
            return await self._call_ollama(messages, **kwargs)
        elif provider_type == "custom":
            # 自定义provider使用OpenAI兼容格式
            return await self._call_openai(messages, **kwargs)
        else:
            return AIResponse(success=False, error=f"不支持的AI提供商: {provider_type}")
    
    async def extract_metadata(self, filename: str, content_preview: str = "") -> Dict[str, Any]:
        """
        使用AI提取书籍元数据
        
        Args:
            filename: 文件名
            content_preview: 内容预览（前1000字）
        
        Returns:
            提取的元数据字典
        """
        if not self.config.features.metadata_enhancement:
            return {}
        
        prompt = f"""请从以下信息中提取书籍元数据。返回JSON格式。

文件名: {filename}
内容预览: {content_preview[:500] if content_preview else '无'}

请提取以下信息（如果无法确定请返回null）：
- title: 书名
- author: 作者
- description: 简介（根据内容生成，不超过200字）
- genre: 类型（如：玄幻、都市、言情、科幻等）
- tags: 标签数组

返回纯JSON，不要有其他文字："""
        
        response = await self.chat([
            {"role": "system", "content": "你是一个专业的书籍元数据提取助手。只返回JSON格式数据。"},
            {"role": "user", "content": prompt}
        ])
        
        if not response.success:
            log.warning(f"AI元数据提取失败: {response.error}")
            return {}
        
        try:
            import json
            # 尝试提取JSON
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            return json.loads(content)
        except Exception as e:
            log.warning(f"解析AI响应失败: {e}")
            return {}
    
    async def generate_summary(self, content: str, max_length: int = 200) -> Optional[str]:
        """
        使用AI生成书籍简介
        
        Args:
            content: 书籍内容
            max_length: 简介最大长度
        
        Returns:
            生成的简介
        """
        if not self.config.features.auto_generate_summary:
            return None
        
        prompt = f"""请根据以下书籍内容生成一段简介，不超过{max_length}字：

{content[:2000]}

要求：
1. 简洁概括主要内容
2. 不要剧透关键情节
3. 语言流畅自然"""
        
        response = await self.chat([
            {"role": "system", "content": "你是一个专业的书籍简介撰写助手。"},
            {"role": "user", "content": prompt}
        ])
        
        if response.success:
            return response.content[:max_length]
        return None
    
    async def classify_book(self, title: str, content_preview: str = "") -> Dict[str, Any]:
        """
        使用AI分类书籍
        
        Args:
            title: 书名
            content_preview: 内容预览
        
        Returns:
            分类结果
        """
        if not self.config.features.smart_classification:
            return {}
        
        prompt = f"""请对以下书籍进行分类。

书名: {title}
内容预览: {content_preview[:500] if content_preview else '无'}

请返回JSON格式：
{{
    "genre": "主要类型（玄幻/都市/言情/科幻/历史/武侠/悬疑等）",
    "sub_genre": "子类型",
    "tags": ["标签1", "标签2", "标签3"],
    "age_rating": "年龄分级（general/teen/adult）",
    "confidence": 0.8
}}

返回纯JSON："""
        
        response = await self.chat([
            {"role": "system", "content": "你是一个专业的书籍分类助手。只返回JSON格式数据。"},
            {"role": "user", "content": prompt}
        ])
        
        if not response.success:
            return {}
        
        try:
            import json
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            log.warning(f"解析AI分类响应失败: {e}")
            return {}
    
    async def test_connection(self) -> AIResponse:
        """
        测试AI连接
        
        Returns:
            测试结果
        """
        return await self.chat([
            {"role": "user", "content": "请回复'连接成功'"}
        ], max_tokens=20)


# 全局单例
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """获取AI服务单例"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
