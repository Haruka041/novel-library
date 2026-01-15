"""
去重检测模块
检测文件是否已经存在于数据库中
"""
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Book
from app.utils.file_hash import calculate_file_hash
from app.utils.logger import log


class Deduplicator:
    """去重检测器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.enabled = settings.deduplicator.enable
        self.algorithm = settings.deduplicator.hash_algorithm
        self.similarity_threshold = settings.deduplicator.similarity_threshold
    
    async def is_duplicate(
        self,
        file_path: Path,
        title: str,
        author: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        检查文件是否重复
        
        Args:
            file_path: 文件路径
            title: 书名
            author: 作者名（可选）
            
        Returns:
            (是否重复, 重复原因)
        """
        if not self.enabled:
            return False, None
        
        # 1. 计算文件Hash
        file_hash = calculate_file_hash(file_path, self.algorithm)
        
        # 2. 检查Hash是否存在
        hash_duplicate = await self._check_hash_duplicate(file_hash)
        if hash_duplicate:
            log.info(f"发现Hash重复: {file_path.name}")
            return True, "文件内容完全相同"
        
        # 3. 检查书名和作者相似度
        if author:
            name_duplicate = await self._check_name_duplicate(title, author)
            if name_duplicate:
                log.info(f"发现名称相似: {file_path.name} ({title} by {author})")
                return True, "书名和作者相似"
        
        return False, None
    
    async def _check_hash_duplicate(self, file_hash: str) -> bool:
        """
        检查Hash是否已存在
        
        Args:
            file_hash: 文件Hash值
            
        Returns:
            是否存在
        """
        result = await self.db.execute(
            select(Book).where(Book.file_hash == file_hash)
        )
        return result.scalar_one_or_none() is not None
    
    async def _check_name_duplicate(self, title: str, author: str) -> bool:
        """
        检查书名和作者是否存在相似项
        
        Args:
            title: 书名
            author: 作者
            
        Returns:
            是否存在相似项
        """
        # 简化实现：精确匹配
        # 更复杂的相似度算法可以后续实现
        from sqlalchemy.orm import joinedload
        from app.models import Author
        
        # 查找相同作者的相同书名
        result = await self.db.execute(
            select(Book)
            .join(Author)
            .where(Author.name == author)
            .where(Book.title == title)
            .options(joinedload(Book.author))
        )
        
        return result.scalar_one_or_none() is not None
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度（Levenshtein距离）
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            相似度 (0.0-1.0)
        """
        # 简单的相似度计算
        if str1 == str2:
            return 1.0
        
        # 使用编辑距离
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()
