"""
MOBI/AZW3元数据解析器
从MOBI文件中提取元数据和封面
"""
from pathlib import Path
from typing import Dict, Optional
import shutil
import os

from app.config import settings
from app.utils.logger import log


class MobiParser:
    """MOBI/AZW3文件解析器"""
    
    def parse(self, file_path: Path) -> Dict[str, Optional[str]]:
        """
        解析MOBI/AZW3文件元数据
        
        Args:
            file_path: MOBI文件路径
            
        Returns:
            包含元数据的字典
        """
        try:
            # 尝试使用mobi库解析
            import mobi
            
            tempdir, filepath = mobi.extract(str(file_path))
            
            # 读取OPF文件获取元数据
            opf_file = None
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    if file.endswith('.opf'):
                        opf_file = os.path.join(root, file)
                        break
                if opf_file:
                    break
            
            metadata = {}
            if opf_file:
                metadata = self._parse_opf(opf_file)
            else:
                # 使用文件名作为默认值
                metadata = {
                    "title": file_path.stem,
                    "author": None,
                    "description": None,
                    "publisher": None,
                }
            
            # 尝试提取封面
            cover_path = self._extract_cover(tempdir, file_path)
            metadata["cover"] = cover_path
            
            # 清理临时文件
            shutil.rmtree(tempdir, ignore_errors=True)
            
            log.info(f"成功解析MOBI: {file_path.name} -> {metadata.get('title', file_path.stem)}")
            return metadata
                
        except Exception as e:
            log.warning(f"MOBI解析失败，使用文件名: {file_path}, 错误: {e}")
            # 解析失败时返回基本信息
            return {
                "title": file_path.stem,
                "author": None,
                "description": None,
                "publisher": None,
                "cover": None,
            }
    
    def _parse_opf(self, opf_path: str) -> Dict[str, Optional[str]]:
        """
        解析OPF文件获取元数据
        
        Args:
            opf_path: OPF文件路径
            
        Returns:
            元数据字典
        """
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(opf_path)
            root = tree.getroot()
            
            # 定义命名空间
            ns = {'dc': 'http://purl.org/dc/elements/1.1/',
                  'opf': 'http://www.idpf.org/2007/opf'}
            
            # 提取元数据
            title_elem = root.find('.//dc:title', ns)
            title = title_elem.text if title_elem is not None else None
            
            creator_elem = root.find('.//dc:creator', ns)
            author = creator_elem.text if creator_elem is not None else None
            
            publisher_elem = root.find('.//dc:publisher', ns)
            publisher = publisher_elem.text if publisher_elem is not None else None
            
            description_elem = root.find('.//dc:description', ns)
            description = description_elem.text if description_elem is not None else None
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "publisher": publisher,
            }
            
        except Exception as e:
            log.error(f"解析OPF文件失败: {opf_path}, 错误: {e}")
            return {
                "title": None,
                "author": None,
                "description": None,
                "publisher": None,
            }
    
    def _extract_cover(self, tempdir: str, file_path: Path) -> Optional[str]:
        """
        从MOBI解压目录中提取封面
        
        Args:
            tempdir: 临时解压目录
            file_path: 原始MOBI文件路径
            
        Returns:
            封面图片保存路径，如果没有封面返回None
        """
        try:
            from PIL import Image
            from io import BytesIO
            
            # 查找封面图片
            cover_image_path = None
            
            # 方法1: 查找常见封面文件名
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    file_lower = file.lower()
                    if any(name in file_lower for name in ['cover', 'jacket']):
                        if file_lower.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            cover_image_path = os.path.join(root, file)
                            break
                if cover_image_path:
                    break
            
            # 方法2: 如果没找到，查找第一张图片（通常是封面）
            if not cover_image_path:
                for root, dirs, files in os.walk(tempdir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            cover_image_path = os.path.join(root, file)
                            break
                    if cover_image_path:
                        break
            
            if not cover_image_path:
                log.debug(f"未找到MOBI封面: {file_path.name}")
                return None
            
            # 保存封面
            cover_dir = Path(settings.directories.covers)
            cover_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用文件hash作为封面文件名
            from app.utils.file_hash import calculate_file_hash
            file_hash = calculate_file_hash(file_path)
            cover_save_path = cover_dir / f"{file_hash}.jpg"
            
            # 转换并保存为JPG
            img = Image.open(cover_image_path)
            img = img.convert('RGB')
            img.save(cover_save_path, 'JPEG', quality=85)
            
            log.debug(f"提取MOBI封面: {cover_save_path}")
            return str(cover_save_path)
            
        except Exception as e:
            log.warning(f"提取MOBI封面失败: {file_path}, 错误: {e}")
            return None

    def extract_text(self, file_path: Path) -> Optional[str]:
        """
        从MOBI/AZW3文件中提取纯文本内容
        """
        try:
            import mobi
            from bs4 import BeautifulSoup
            
            # 解压
            # mobi.extract 返回 (tempdir, filepath)
            tempdir, filepath = mobi.extract(str(file_path))
            content = ""
            
            try:
                if os.path.isfile(filepath):
                    # 读取主文件内容
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        # 使用换行符分隔段落
                        content = soup.get_text(separator='\n')
            finally:
                # 清理临时文件
                shutil.rmtree(tempdir, ignore_errors=True)
                
            return content
            
        except Exception as e:
            log.error(f"提取MOBI文本失败: {file_path}, 错误: {e}")
            return None
