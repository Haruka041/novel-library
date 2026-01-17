"""
去重检测模块
检测文件是否已经存在于数据库中，支持书籍组合并（类似Emby）
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import re

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models import Author, Book, BookGroup, BookVersion
from app.utils.file_hash import calculate_file_hash
from app.utils.logger import log


class Deduplicator:
    """去重检测器（支持版本管理和书籍组）"""
    
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
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """
        标准化书名用于比较
        - 去除空格和特殊字符
        - 转为小写
        - 去除常见后缀如 [完结]、（全本）等
        """
        if not title:
            return ""
        
        # 转小写
        normalized = title.lower()
        
        # 去除常见标记
        patterns_to_remove = [
            r'\[完结\]', r'【完结】', r'\(完结\)', r'（完结）',
            r'\[全本\]', r'【全本】', r'\(全本\)', r'（全本）',
            r'\[精校版\]', r'【精校版】', r'\(精校版\)', r'（精校版）',
            r'\[出版\]', r'【出版】', r'\(出版\)', r'（出版）',
            r'_精校', r'-精校', r'\.精校',
            r'_完本', r'-完本', r'\.完本',
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # 去除空格和特殊字符
        normalized = re.sub(r'[\s\-_\.]+', '', normalized)
        
        return normalized.strip()
    
    async def detect_duplicates_in_library(
        self,
        library_id: int,
        similarity_threshold: float = 0.85
    ) -> List[Dict]:
        """
        检测书库中的重复书籍
        
        Args:
            library_id: 书库ID
            similarity_threshold: 相似度阈值
            
        Returns:
            重复书籍分组列表，每个分组包含：
            {
                "key": 标准化的书名+作者,
                "books": [书籍列表],
                "suggested_primary_id": 建议作为主版本的书籍ID,
                "reason": 检测原因
            }
        """
        # 获取书库中所有书籍及其版本
        result = await self.db.execute(
            select(Book)
            .options(
                joinedload(Book.author),
                joinedload(Book.versions),
                joinedload(Book.group)
            )
            .where(Book.library_id == library_id)
        )
        books = result.unique().scalars().all()
        
        if not books:
            return []
        
        # 按标准化书名+作者分组
        groups: Dict[str, List[Book]] = defaultdict(list)
        
        for book in books:
            normalized_title = self.normalize_title(book.title)
            author_name = book.author.name if book.author else ""
            key = f"{normalized_title}|{author_name.lower()}"
            groups[key].append(book)
        
        # 找出有重复的分组（排除已经在同一组的书籍）
        duplicate_groups = []
        
        for key, group_books in groups.items():
            if len(group_books) > 1:
                # 检查是否已经在同一个组中
                group_ids = set(b.group_id for b in group_books if b.group_id)
                if len(group_ids) == 1 and len(group_books) == len([b for b in group_books if b.group_id]):
                    # 所有书籍都在同一个组中，跳过
                    continue
                
                # 选择建议的主书籍
                # 优先级：已有group的主书籍 > 文件更大的 > 有更多版本的 > 添加更早的
                def get_priority(b):
                    is_primary = 0
                    if b.group_id:
                        # 检查是否是组的主书籍
                        if b.group and b.group.primary_book_id == b.id:
                            is_primary = 1
                    return (
                        is_primary,
                        len(b.versions),
                        max(v.file_size for v in b.versions) if b.versions else 0,
                        -b.added_at.timestamp()  # 负数使得更早的排在前面
                    )
                
                suggested = max(group_books, key=get_priority)
                
                duplicate_groups.append({
                    "key": key,
                    "books": [
                        {
                            "id": b.id,
                            "title": b.title,
                            "author_name": b.author.name if b.author else None,
                            "version_count": len(b.versions),
                            "formats": [v.file_format for v in b.versions],
                            "total_size": sum(v.file_size for v in b.versions),
                            "added_at": b.added_at.isoformat(),
                            "group_id": b.group_id,
                            "is_group_primary": b.group and b.group.primary_book_id == b.id if b.group_id else False,
                        }
                        for b in group_books
                    ],
                    "suggested_primary_id": suggested.id,
                    "reason": "书名和作者相同"
                })
        
        return duplicate_groups
    
    async def group_books(
        self,
        primary_book_id: int,
        book_ids: List[int],
        group_name: Optional[str] = None
    ) -> Dict:
        """
        将多本书籍合并到一个组中（不删除任何书籍）
        
        Args:
            primary_book_id: 主书籍ID（用于显示封面、标题等）
            book_ids: 所有要加入组的书籍ID列表（包含primary_book_id）
            group_name: 组名称（可选，默认使用主书籍标题）
            
        Returns:
            操作结果
        """
        # 获取主书籍
        result = await self.db.execute(
            select(Book)
            .options(joinedload(Book.group))
            .where(Book.id == primary_book_id)
        )
        primary_book = result.unique().scalar_one_or_none()
        
        if not primary_book:
            return {"status": "error", "message": "主书籍不存在"}
        
        # 确保 primary_book_id 在列表中
        if primary_book_id not in book_ids:
            book_ids.append(primary_book_id)
        
        # 检查是否已有组
        existing_group = None
        for book_id in book_ids:
            result = await self.db.execute(
                select(Book).options(joinedload(Book.group)).where(Book.id == book_id)
            )
            book = result.unique().scalar_one_or_none()
            if book and book.group_id:
                existing_group = book.group
                break
        
        # 创建或使用现有组
        if existing_group:
            group = existing_group
            # 更新主书籍
            group.primary_book_id = primary_book_id
            if group_name:
                group.name = group_name
        else:
            group = BookGroup(
                name=group_name or primary_book.title,
                primary_book_id=primary_book_id
            )
            self.db.add(group)
            await self.db.flush()
        
        # 将所有书籍加入组
        added_count = 0
        for book_id in book_ids:
            result = await self.db.execute(
                select(Book).where(Book.id == book_id)
            )
            book = result.scalar_one_or_none()
            if book and book.group_id != group.id:
                book.group_id = group.id
                added_count += 1
        
        await self.db.commit()
        
        log.info(
            f"创建/更新书籍组: {group.name} (ID: {group.id}), "
            f"主书籍: {primary_book.title}, 共 {len(book_ids)} 本书"
        )
        
        return {
            "status": "success",
            "group_id": group.id,
            "group_name": group.name,
            "primary_book_id": primary_book_id,
            "book_count": len(book_ids),
            "added_count": added_count,
        }
    
    async def ungroup_book(self, book_id: int) -> Dict:
        """
        将书籍从组中移除
        
        Args:
            book_id: 要移除的书籍ID
            
        Returns:
            操作结果
        """
        result = await self.db.execute(
            select(Book).options(joinedload(Book.group)).where(Book.id == book_id)
        )
        book = result.unique().scalar_one_or_none()
        
        if not book:
            return {"status": "error", "message": "书籍不存在"}
        
        if not book.group_id:
            return {"status": "error", "message": "书籍不在任何组中"}
        
        group = book.group
        group_id = group.id
        was_primary = group.primary_book_id == book_id
        
        # 从组中移除
        book.group_id = None
        
        # 检查组内剩余书籍
        result = await self.db.execute(
            select(Book).where(Book.group_id == group_id)
        )
        remaining_books = result.scalars().all()
        
        if len(remaining_books) == 0:
            # 组为空，删除组
            await self.db.delete(group)
            log.info(f"书籍 {book.title} 从组中移除，组已删除")
        elif len(remaining_books) == 1:
            # 只剩一本书，也删除组并清除该书的group_id
            remaining_book = remaining_books[0]
            remaining_book.group_id = None
            await self.db.delete(group)
            log.info(f"书籍 {book.title} 从组中移除，组只剩1本书，组已删除")
        elif was_primary:
            # 如果移除的是主书籍，选择新的主书籍
            new_primary = max(remaining_books, key=lambda b: len(b.versions) if hasattr(b, 'versions') else 0)
            group.primary_book_id = new_primary.id
            log.info(f"书籍 {book.title} 从组中移除，新主书籍: {new_primary.title}")
        else:
            log.info(f"书籍 {book.title} 从组中移除")
        
        await self.db.commit()
        
        return {
            "status": "success",
            "book_id": book_id,
            "book_title": book.title,
            "was_primary": was_primary,
        }
    
    async def get_grouped_books(self, book_id: int) -> List[Dict]:
        """
        获取与指定书籍同组的所有书籍
        
        Args:
            book_id: 书籍ID
            
        Returns:
            同组书籍列表
        """
        result = await self.db.execute(
            select(Book).options(joinedload(Book.group)).where(Book.id == book_id)
        )
        book = result.unique().scalar_one_or_none()
        
        if not book or not book.group_id:
            return []
        
        # 获取同组的所有书籍
        result = await self.db.execute(
            select(Book)
            .options(
                joinedload(Book.author),
                joinedload(Book.versions),
                joinedload(Book.group)
            )
            .where(Book.group_id == book.group_id)
        )
        grouped_books = result.unique().scalars().all()
        
        group = book.group
        
        return [
            {
                "id": b.id,
                "title": b.title,
                "author_name": b.author.name if b.author else None,
                "cover_path": b.cover_path,
                "version_count": len(b.versions),
                "formats": [v.file_format for v in b.versions],
                "total_size": sum(v.file_size for v in b.versions),
                "is_primary": group.primary_book_id == b.id,
                "is_current": b.id == book_id,
            }
            for b in grouped_books
        ]
    
    async def set_group_primary(self, group_id: int, book_id: int) -> Dict:
        """
        设置组的主书籍
        
        Args:
            group_id: 组ID
            book_id: 新的主书籍ID
            
        Returns:
            操作结果
        """
        result = await self.db.execute(
            select(BookGroup).where(BookGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            return {"status": "error", "message": "组不存在"}
        
        # 验证书籍在组中
        result = await self.db.execute(
            select(Book).where(Book.id == book_id).where(Book.group_id == group_id)
        )
        book = result.scalar_one_or_none()
        
        if not book:
            return {"status": "error", "message": "书籍不在此组中"}
        
        group.primary_book_id = book_id
        await self.db.commit()
        
        log.info(f"组 {group_id} 的主书籍已更改为 {book.title}")
        
        return {
            "status": "success",
            "group_id": group_id,
            "primary_book_id": book_id,
            "primary_book_title": book.title,
        }
    
    # 保留旧的 merge_books 方法作为别名，实际调用 group_books
    async def merge_books(
        self,
        keep_book_id: int,
        merge_book_ids: List[int]
    ) -> Dict:
        """
        合并书籍（兼容旧API，实际创建书籍组）
        
        Args:
            keep_book_id: 主书籍ID
            merge_book_ids: 要加入组的其他书籍ID列表
            
        Returns:
            合并结果
        """
        all_book_ids = [keep_book_id] + merge_book_ids
        result = await self.group_books(
            primary_book_id=keep_book_id,
            book_ids=all_book_ids
        )
        
        # 转换返回格式以兼容旧API
        if result["status"] == "success":
            return {
                "status": "success",
                "keep_book_id": keep_book_id,
                "merged_version_count": result["added_count"],
                "skipped_duplicate_count": 0,
                "group_id": result["group_id"],
            }
        return result
