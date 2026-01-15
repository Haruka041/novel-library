"""
去重检测模块
检测文件是否已经存在于数据库中，支持版本合并
"""
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Book, BookVersion
from app.utils.file_hash import calculate_file_hash
from app.utils.logger import log


class Deduplicator:
    """去重检测器（支持版本管理）"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.enabled = settings.deduplicator.enable
        self.algorithm = settings.deduplicator.hash_algorithm
        self.similarity_threshold = settings.deduplicator.similarity_threshold
    
    async def check_duplicate(
        self,
        file_path: Path,
        title: str,
        author: Optional[str] = None
    ) -> Tuple[str, Optional[int], Optional[str]]:
        """
        检查文件是否重复，并决定处理方式
        
        Args:
            file_path: 文件路径
            title: 书名
            author: 作者名（可选）
            
        Returns:
            (action, book_id, reason)
            - action: 'skip'(跳过), 'add_version'(作为新版本), 'new_book'(新书籍)
            - book_id: 如果是add_version，返回对应的book_id
            - reason: 处理原因说明
        """
        if not self.enabled:
            return 'new_book', None, None
        
        # 1. 计算文件Hash
        file_hash = calculate_file_hash(file_path, self.algorithm)
        
        # 2. 检查Hash是否存在（完全相同的文件）
        hash_result = await self._check_hash_duplicate(file_hash)
        if hash_result:
            log.info(f"发现Hash重复: {file_path.name}")
            return 'skip', None, "文件内容完全相同"
        
        # 3. 检查是否为同一本书的不同版本
        if author:
            existing_book = await self._find_same_book(title, author)
            if existing_book:
                log.info(f"发现同名书籍，作为新版本: {file_path.name} ({title} by {author})")
                return 'add_version', existing_book.id, f"同一本书的新版本"
        
        # 4. 新书籍
        return 'new_book', None, None
    
    # 为了向后兼容，保留旧的API
    async def is_duplicate(
        self,
        file_path: Path,
        title: str,
        author: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        检查文件是否重复（向后兼容API）
        
        Returns:
            (是否跳过, 原因)
        """
        action, _, reason = await self.check_duplicate(file_path, title, author)
        return action == 'skip', reason
    
    async def _check_hash_duplicate(self, file_hash: str) -> bool:
        """
        检查Hash是否已存在于任何版本中
        
        Args:
            file_hash: 文件Hash值
            
        Returns:
            是否存在
        """
        result = await self.db.execute(
            select(BookVersion).where(BookVersion.file_hash == file_hash)
        )
        return result.scalar_one_or_none() is not None
    
    async def _find_same_book(self, title: str, author: str) -> Optional[Book]:
        """
        查找书名和作者都相同的书籍
        
        Args:
            title: 书名
            author: 作者
            
        Returns:
            找到的Book对象，如果没有则返回None
        """
        # 精确匹配书名和作者
        from sqlalchemy.orm import joinedload
        from app.models import Author
        
        result = await self.db.execute(
            select(Book)
            .join(Author)
            .where(Author.name == author)
            .where(Book.title == title)
            .options(joinedload(Book.author))
        )
        
        return result.scalar_one_or_none()
    
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
