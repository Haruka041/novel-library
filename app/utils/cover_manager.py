"""
封面管理器
统一的封面提取、缓存和生成管理
"""
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Book
from app.utils.logger import log


class CoverManager:
    """封面管理器"""
    
    # 默认封面风格
    STYLE_GRADIENT = "gradient"
    STYLE_LETTER = "letter"
    STYLE_BOOK_ICON = "book"
    STYLE_MINIMAL = "minimal"
    
    # 颜色方案（基于书名hash）
    COLOR_SCHEMES = [
        # (起始色, 结束色)
        ("#667eea", "#764ba2"),  # 紫色渐变
        ("#f093fb", "#f5576c"),  # 粉红渐变
        ("#4facfe", "#00f2fe"),  # 蓝色渐变
        ("#43e97b", "#38f9d7"),  # 绿色渐变
        ("#fa709a", "#fee140"),  # 橙色渐变
        ("#30cfd0", "#330867"),  # 深蓝渐变
        ("#a8edea", "#fed6e3"),  # 淡色渐变
        ("#ff9a9e", "#fecfef"),  # 粉色渐变
        ("#ffecd2", "#fcb69f"),  # 暖色渐变
        ("#ff6e7f", "#bfe9ff"),  # 对比渐变
    ]
    
    def __init__(self):
        """初始化封面管理器"""
        self.cover_dir = Path(settings.directories.covers)
        self.cover_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_cover_path(
        self, 
        book_id: int, 
        db: AsyncSession,
        size: str = "original"
    ) -> Optional[str]:
        """
        获取书籍封面路径
        
        Args:
            book_id: 书籍ID
            db: 数据库会话
            size: 尺寸（original/thumbnail）
            
        Returns:
            封面路径，如果不存在返回None
        """
        try:
            # 查询书籍
            result = await db.execute(
                select(Book).where(Book.id == book_id)
            )
            book = result.scalar_one_or_none()
            
            if not book or not book.cover_path:
                return None
            
            cover_path = Path(book.cover_path)
            if not cover_path.exists():
                return None
            
            # 如果需要缩略图，生成或返回缩略图路径
            if size == "thumbnail":
                return await self._get_thumbnail_path(cover_path)
            
            return str(cover_path)
            
        except Exception as e:
            log.error(f"获取封面路径失败: book_id={book_id}, 错误: {e}")
            return None
    
    async def _get_thumbnail_path(self, original_path: Path) -> str:
        """
        获取或生成缩略图
        
        Args:
            original_path: 原始封面路径
            
        Returns:
            缩略图路径
        """
        try:
            # 缩略图保存路径
            thumb_path = original_path.parent / f"thumb_{original_path.name}"
            
            # 如果缩略图已存在，直接返回
            if thumb_path.exists():
                return str(thumb_path)
            
            # 生成缩略图
            img = Image.open(original_path)
            img.thumbnail((300, 450), Image.Resampling.LANCZOS)
            img.save(thumb_path, 'JPEG', quality=85)
            
            return str(thumb_path)
            
        except Exception as e:
            log.error(f"生成缩略图失败: {original_path}, 错误: {e}")
            return str(original_path)
    
    def generate_default_cover(
        self, 
        title: str, 
        author: Optional[str] = None,
        style: str = STYLE_GRADIENT,
        width: int = 600,
        height: int = 900
    ) -> bytes:
        """
        生成默认封面
        
        Args:
            title: 书名
            author: 作者（可选）
            style: 风格（gradient/letter/book/minimal）
            width: 宽度
            height: 高度
            
        Returns:
            PNG图片字节
        """
        try:
            if style == self.STYLE_GRADIENT:
                return self._generate_gradient_cover(title, author, width, height)
            elif style == self.STYLE_LETTER:
                return self._generate_letter_cover(title, author, width, height)
            elif style == self.STYLE_BOOK_ICON:
                return self._generate_book_cover(title, author, width, height)
            else:  # minimal
                return self._generate_minimal_cover(title, author, width, height)
                
        except Exception as e:
            log.error(f"生成默认封面失败: {title}, 错误: {e}")
            # 返回纯色封面作为fallback
            return self._generate_solid_cover(title, width, height)
    
    def _get_color_scheme(self, title: str) -> Tuple[str, str]:
        """
        根据书名获取颜色方案
        
        Args:
            title: 书名
            
        Returns:
            (起始色, 结束色)
        """
        # 使用书名hash选择颜色
        hash_value = int(hashlib.md5(title.encode()).hexdigest(), 16)
        index = hash_value % len(self.COLOR_SCHEMES)
        return self.COLOR_SCHEMES[index]
    
    def _generate_gradient_cover(
        self, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int
    ) -> bytes:
        """生成渐变风格封面"""
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 获取颜色方案
        start_color, end_color = self._get_color_scheme(title)
        
        # 绘制渐变背景
        for y in range(height):
            ratio = y / height
            r = int(int(start_color[1:3], 16) * (1 - ratio) + int(end_color[1:3], 16) * ratio)
            g = int(int(start_color[3:5], 16) * (1 - ratio) + int(end_color[3:5], 16) * ratio)
            b = int(int(start_color[5:7], 16) * (1 - ratio) + int(end_color[5:7], 16) * ratio)
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
        
        # 绘制文字
        self._draw_text(draw, title, author, width, height)
        
        # 转换为字节
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_letter_cover(
        self, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int
    ) -> bytes:
        """生成首字母风格封面（Emby风格）"""
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 获取颜色方案
        start_color, end_color = self._get_color_scheme(title)
        
        # 绘制渐变背景
        for y in range(height):
            ratio = y / height
            r = int(int(start_color[1:3], 16) * (1 - ratio) + int(end_color[1:3], 16) * ratio)
            g = int(int(start_color[3:5], 16) * (1 - ratio) + int(end_color[3:5], 16) * ratio)
            b = int(int(start_color[5:7], 16) * (1 - ratio) + int(end_color[5:7], 16) * ratio)
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
        
        # 绘制圆形背景
        circle_size = min(width, height) // 2
        circle_center = (width // 2, height // 2)
        circle_bbox = [
            circle_center[0] - circle_size // 2,
            circle_center[1] - circle_size // 2,
            circle_center[0] + circle_size // 2,
            circle_center[1] + circle_size // 2
        ]
        draw.ellipse(circle_bbox, fill='white', outline=None)
        
        # 绘制首字母
        first_letter = title[0].upper() if title else '?'
        try:
            font = ImageFont.truetype("arial.ttf", circle_size // 2)
        except:
            font = ImageFont.load_default()
        
        # 获取文字边界框
        bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 居中绘制
        text_x = circle_center[0] - text_width // 2
        text_y = circle_center[1] - text_height // 2
        
        # 使用深色文字
        draw.text((text_x, text_y), first_letter, fill=end_color, font=font)
        
        # 在底部绘制书名
        self._draw_bottom_text(draw, title, author, width, height)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_book_cover(
        self, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int
    ) -> bytes:
        """生成书籍图标风格封面"""
        img = Image.new('RGB', (width, height), '#f5f5f5')
        draw = ImageDraw.Draw(img)
        
        # 获取颜色
        start_color, end_color = self._get_color_scheme(title)
        
        # 绘制书籍图标（简化版）
        book_width = int(width * 0.6)
        book_height = int(height * 0.7)
        book_x = (width - book_width) // 2
        book_y = int(height * 0.15)
        
        # 书籍主体
        draw.rectangle(
            [(book_x, book_y), (book_x + book_width, book_y + book_height)],
            fill=start_color,
            outline=end_color,
            width=3
        )
        
        # 书脊
        spine_width = int(book_width * 0.1)
        draw.rectangle(
            [(book_x, book_y), (book_x + spine_width, book_y + book_height)],
            fill=end_color
        )
        
        # 绘制书名
        self._draw_text(draw, title, author, width, height, y_offset=book_y + book_height + 40)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_minimal_cover(
        self, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int
    ) -> bytes:
        """生成极简风格封面"""
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 获取颜色
        _, accent_color = self._get_color_scheme(title)
        
        # 顶部色块
        draw.rectangle([(0, 0), (width, height // 10)], fill=accent_color)
        
        # 绘制文字
        self._draw_text(draw, title, author, width, height, color=accent_color)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _generate_solid_cover(self, title: str, width: int, height: int) -> bytes:
        """生成纯色封面（fallback）"""
        img = Image.new('RGB', (width, height), '#667eea')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # 截断书名
        display_title = title[:20] + "..." if len(title) > 20 else title
        bbox = draw.textbbox((0, 0), display_title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), display_title, fill='white', font=font)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _draw_text(
        self, 
        draw: ImageDraw.ImageDraw, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int,
        y_offset: Optional[int] = None,
        color: str = 'white'
    ):
        """绘制书名和作者文字"""
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            author_font = ImageFont.truetype("arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
        
        # 处理书名（分行显示）
        max_chars_per_line = 12
        title_lines = []
        if len(title) > max_chars_per_line:
            # 简单分行
            for i in range(0, len(title), max_chars_per_line):
                title_lines.append(title[i:i + max_chars_per_line])
        else:
            title_lines = [title]
        
        # 只显示前3行
        title_lines = title_lines[:3]
        if len(title) > max_chars_per_line * 3:
            title_lines[-1] = title_lines[-1][:-3] + "..."
        
        # 计算总高度
        line_height = 70
        total_height = len(title_lines) * line_height
        if author:
            total_height += 50
        
        # 起始Y坐标
        if y_offset is None:
            start_y = (height - total_height) // 2
        else:
            start_y = y_offset
        
        # 绘制书名
        current_y = start_y
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, current_y), line, fill=color, font=title_font)
            current_y += line_height
        
        # 绘制作者
        if author:
            current_y += 20
            author_text = f"— {author} —"
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, current_y), author_text, fill=color, font=author_font)
    
    def _draw_bottom_text(
        self, 
        draw: ImageDraw.ImageDraw, 
        title: str, 
        author: Optional[str],
        width: int,
        height: int
    ):
        """在底部绘制书名和作者"""
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            author_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
        
        # 截断书名
        display_title = title[:15] + "..." if len(title) > 15 else title
        
        # 计算位置
        bottom_margin = 80
        
        # 绘制书名
        bbox = draw.textbbox((0, 0), display_title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = height - bottom_margin - 50
        draw.text((text_x, text_y), display_title, fill='white', font=title_font)
        
        # 绘制作者
        if author:
            author_text = f"— {author} —"
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = height - bottom_margin
            draw.text((text_x, text_y), author_text, fill='white', font=author_font)
    
    async def clear_orphaned_covers(self, db: AsyncSession) -> int:
        """
        清理孤立的封面文件（数据库中不存在的）
        
        Args:
            db: 数据库会话
            
        Returns:
            清理的文件数量
        """
        try:
            # 获取所有封面路径
            result = await db.execute(
                select(Book.cover_path).where(Book.cover_path.isnot(None))
            )
            valid_covers = {row[0] for row in result.all()}
            
            # 扫描封面目录
            deleted_count = 0
            for cover_file in self.cover_dir.glob("*.jpg"):
                if str(cover_file) not in valid_covers:
                    cover_file.unlink()
                    deleted_count += 1
                    # 同时删除缩略图
                    thumb_file = cover_file.parent / f"thumb_{cover_file.name}"
                    if thumb_file.exists():
                        thumb_file.unlink()
            
            log.info(f"清理了 {deleted_count} 个孤立封面文件")
            return deleted_count
            
        except Exception as e:
            log.error(f"清理孤立封面失败: {e}")
            return 0
    
    async def get_cache_stats(self) -> dict:
        """
        获取封面缓存统计
        
        Returns:
            统计信息字典
        """
        try:
            cover_files = list(self.cover_dir.glob("*.jpg"))
            thumb_files = list(self.cover_dir.glob("thumb_*.jpg"))
            
            total_size = sum(f.stat().st_size for f in cover_files)
            thumb_size = sum(f.stat().st_size for f in thumb_files)
            
            return {
                "cover_count": len(cover_files),
                "thumbnail_count": len(thumb_files),
                "total_size": total_size,
                "thumbnail_size": thumb_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "thumbnail_size_mb": round(thumb_size / 1024 / 1024, 2),
            }
        except Exception as e:
            log.error(f"获取缓存统计失败: {e}")
            return {
                "cover_count": 0,
                "thumbnail_count": 0,
                "total_size": 0,
                "thumbnail_size": 0,
                "total_size_mb": 0,
                "thumbnail_size_mb": 0,
            }


# 全局实例
cover_manager = CoverManager()
