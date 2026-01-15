"""
EPUB元数据解析器
从EPUB文件中提取元数据和封面
"""
from pathlib import Path
from typing import Dict, Optional

import ebooklib
from ebooklib import epub
from PIL import Image

from app.config import settings
from app.utils.logger import log


class EpubParser:
    """EPUB文件解析器"""
    
    def parse(self, file_path: Path) -> Dict[str, Optional[str]]:
        """
        解析EPUB文件元数据
        
        Args:
            file_path: EPUB文件路径
            
        Returns:
            包含元数据的字典
        """
        try:
            book = epub.read_epub(str(file_path))
            
            # 提取标题
            title = book.get_metadata('DC', 'title')
            title = title[0][0] if title else file_path.stem
            
            # 提取作者
            authors = book.get_metadata('DC', 'creator')
            author = authors[0][0] if authors else None
            
            # 提取出版社
            publishers = book.get_metadata('DC', 'publisher')
            publisher = publishers[0][0] if publishers else None
            
            # 提取简介
            descriptions = book.get_metadata('DC', 'description')
            description = descriptions[0][0] if descriptions else None
            
            # 提取封面
            cover_path = self._extract_cover(book, file_path)
            
            log.info(f"成功解析EPUB: {file_path.name} -> {title} by {author}")
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "publisher": publisher,
                "cover": cover_path,
            }
            
        except Exception as e:
            log.error(f"解析EPUB文件失败: {file_path}, 错误: {e}")
            # 解析失败时返回基本信息
            return {
                "title": file_path.stem,
                "author": None,
                "description": None,
                "publisher": None,
                "cover": None,
            }
    
    def _extract_cover(self, book: epub.EpubBook, file_path: Path) -> Optional[str]:
        """
        提取EPUB封面图片
        
        Args:
            book: EPUB书籍对象
            file_path: 原始文件路径
            
        Returns:
            封面图片保存路径，如果没有封面返回None
        """
        try:
            # 尝试获取封面
            cover_item = None
            
            # 方法1: 通过metadata获取
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_COVER:
                    cover_item = item
                    break
            
            # 方法2: 查找cover.jpg或cover.png
            if not cover_item:
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_IMAGE:
                        name = item.get_name().lower()
                        if 'cover' in name:
                            cover_item = item
                            break
            
            if not cover_item:
                return None
            
            # 保存封面
            cover_dir = Path(settings.directories.covers)
            cover_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用文件hash作为封面文件名
            from app.utils.file_hash import calculate_file_hash
            file_hash = calculate_file_hash(file_path)
            cover_path = cover_dir / f"{file_hash}.jpg"
            
            # 保存并转换为jpg
            with open(cover_path, 'wb') as f:
                image_data = cover_item.get_content()
                try:
                    # 尝试使用PIL转换为jpg
                    from io import BytesIO
                    img = Image.open(BytesIO(image_data))
                    img = img.convert('RGB')
                    img.save(f, 'JPEG', quality=85)
                except:
                    # 如果转换失败，直接保存原始数据
                    f.write(image_data)
            
            log.debug(f"提取EPUB封面: {cover_path}")
            return str(cover_path)
            
        except Exception as e:
            log.warning(f"提取EPUB封面失败: {file_path}, 错误: {e}")
            return None
