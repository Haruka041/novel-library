"""
EPUB元数据解析器
从EPUB文件中提取元数据和封面
"""
from pathlib import Path
from typing import Dict, Optional

import zipfile
import xml.etree.ElementTree as ET
from PIL import Image
from io import BytesIO

from app.config import settings
from app.utils.logger import log


class EpubParser:
    """
    EPUB文件解析器 (轻量级优化版)
    直接通过zipfile读取元数据，避免加载整个文件到内存
    """
    
    def parse(self, file_path: Path) -> Dict[str, Optional[str]]:
        """
        解析EPUB文件元数据
        
        Args:
            file_path: EPUB文件路径
            
        Returns:
            包含元数据的字典
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 1. 查找 container.xml 以确定 OPF 文件位置
                container_xml = zf.read('META-INF/container.xml')
                root = ET.fromstring(container_xml)
                ns = {'n': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                full_path = root.find('.//n:rootfile', ns).attrib['full-path']
                
                # 2. 读取 OPF 文件
                opf_content = zf.read(full_path)
                
                # 3. 解析元数据
                metadata = self._parse_opf(opf_content)
                
                # 如果没有标题，使用文件名
                if not metadata.get('title'):
                    metadata['title'] = file_path.stem
                
                # 4. 提取封面
                cover_path = self._extract_cover(zf, full_path, opf_content, file_path)
                metadata['cover'] = cover_path
                
                log.info(f"成功解析EPUB: {file_path.name} -> {metadata.get('title')} by {metadata.get('author')}")
                return metadata
            
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
    
    def _parse_opf(self, opf_content: bytes) -> Dict[str, Optional[str]]:
        """解析 OPF 内容提取元数据"""
        try:
            root = ET.fromstring(opf_content)
            
            # 处理命名空间 (忽略具体的 URL，只看标签名)
            # 这是一个简单的处理方式，适用于大多数情况
            # 更严谨的做法是提取 xmlns 属性
            
            def find_text(element, tag_name):
                # 在 metadata 标签下查找
                metadata = None
                for child in element:
                    if child.tag.endswith('metadata'):
                        metadata = child
                        break
                
                if metadata is None:
                    return None
                
                for child in metadata:
                    if child.tag.endswith(tag_name):
                        return child.text
                return None
            
            title = find_text(root, 'title')
            author = find_text(root, 'creator')
            publisher = find_text(root, 'publisher')
            description = find_text(root, 'description')
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "publisher": publisher,
            }
        except Exception as e:
            log.warning(f"解析OPF内容失败: {e}")
            return {}

    def _extract_cover(self, zf: zipfile.ZipFile, opf_path: str, opf_content: bytes, file_path: Path) -> Optional[str]:
        """
        提取EPUB封面图片
        
        Args:
            zf: ZipFile对象
            opf_path: OPF文件在zip中的路径
            opf_content: OPF文件内容
            file_path: 原始文件路径
        """
        try:
            cover_href = None
            root = ET.fromstring(opf_content)
            
            # 尝试方法 1: 查找 meta name="cover"
            cover_id = None
            for meta in root.findall(".//{*}meta"):
                if meta.get("name") == "cover":
                    cover_id = meta.get("content")
                    break
            
            # 如果找到 cover_id，在 manifest 中查找对应的 href
            if cover_id:
                for item in root.findall(".//{*}item"):
                    if item.get("id") == cover_id:
                        cover_href = item.get("href")
                        break
            
            # 尝试方法 2: 如果没找到，在 manifest 中查找 id 或 href 包含 cover 的图片
            if not cover_href:
                for item in root.findall(".//{*}item"):
                    media_type = item.get("media-type", "")
                    if "image" in media_type:
                        href = item.get("href", "").lower()
                        item_id = item.get("id", "").lower()
                        if "cover" in href or "cover" in item_id:
                            cover_href = item.get("href")
                            break

            if not cover_href:
                return None
                
            # 解析相对路径
            # opf_path 例如: OEBPS/content.opf
            # cover_href 例如: images/cover.jpg
            # 结果应为: OEBPS/images/cover.jpg
            opf_dir = "/".join(opf_path.split("/")[:-1])
            if opf_dir:
                full_cover_path = f"{opf_dir}/{cover_href}"
            else:
                full_cover_path = cover_href
                
            # 处理路径规范化 (处理 ../)
            # 简单处理，如果路径不在 zip 中，尝试直接用 href
            if full_cover_path not in zf.namelist():
                if cover_href in zf.namelist():
                    full_cover_path = cover_href
                else:
                    # 尝试查找最接近的匹配
                    for name in zf.namelist():
                        if name.endswith(cover_href):
                            full_cover_path = name
                            break
            
            if full_cover_path not in zf.namelist():
                log.warning(f"封面文件在压缩包中未找到: {full_cover_path}")
                return None
                
            # 读取图片数据
            image_data = zf.read(full_cover_path)
            
            # 保存封面
            cover_dir = Path(settings.directories.covers)
            cover_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用文件hash作为封面文件名
            from app.utils.file_hash import calculate_file_hash
            file_hash = calculate_file_hash(file_path)
            cover_save_path = cover_dir / f"{file_hash}.jpg"
            
            # 保存并转换为jpg
            with open(cover_save_path, 'wb') as f:
                try:
                    # 尝试使用PIL转换为jpg
                    img = Image.open(BytesIO(image_data))
                    img = img.convert('RGB')
                    img.save(f, 'JPEG', quality=85)
                except Exception as e:
                    log.warning(f"封面格式转换失败，保存原图: {e}")
                    f.write(image_data)
            
            log.debug(f"提取EPUB封面: {cover_save_path}")
            return str(cover_save_path)
            
        except Exception as e:
            log.warning(f"提取EPUB封面失败: {file_path}, 错误: {e}")
            return None
