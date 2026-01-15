"""
TXT文件名解析器
从文件名提取作者和书名信息
"""
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from app.utils.logger import log


class TxtParser:
    """TXT文件名解析器"""
    
    # 解析规则列表（优先级从高到低）
    PATTERNS = [
        # 作者-书名.txt
        (r'^(.+?)[-_](.+?)\.txt$', 1, 2),
        # [作者]书名.txt
        (r'^\[(.+?)\](.+?)\.txt$', 1, 2),
        # 作者《书名》.txt
        (r'^(.+?)《(.+?)》\.txt$', 1, 2),
        # 书名(作者).txt
        (r'^(.+?)\((.+?)\)\.txt$', 2, 1),
        # 作者_书名.txt
        (r'^(.+?)_(.+?)\.txt$', 1, 2),
        # 【作者】书名.txt
        (r'^【(.+?)】(.+?)\.txt$', 1, 2),
    ]
    
    def parse(self, file_path: Path) -> Dict[str, Optional[str]]:
        """
        解析TXT文件名
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含title和author的字典
        """
        filename = file_path.name
        
        for pattern, author_group, title_group in self.PATTERNS:
            if match := re.match(pattern, filename):
                author = self._normalize(match.group(author_group))
                title = self._normalize(match.group(title_group))
                
                log.debug(f"成功解析文件名: {filename} -> 作者: {author}, 书名: {title}")
                
                return {
                    "title": title,
                    "author": author,
                    "description": None,
                    "publisher": None,
                    "cover": None,
                }
        
        # 无法解析，使用文件名作为书名
        title = file_path.stem
        log.warning(f"无法解析文件名格式: {filename}，使用文件名作为书名")
        
        return {
            "title": title,
            "author": None,
            "description": None,
            "publisher": None,
            "cover": None,
        }
    
    def _normalize(self, text: str) -> str:
        """
        标准化文本（去除首尾空格）
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        return text.strip()
