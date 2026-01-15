"""
MOBI/AZW3元数据解析器
从MOBI文件中提取元数据
"""
from pathlib import Path
from typing import Dict, Optional

from app.utils.logger import log


class MobiParser:
    """MOBI/AZW3文件解析器"""
    
    def parse(self, file_path: Path) -> Dict[str, Optional[str]]:
        """
        解析MOBI/AZW3文件元数据
        
        注意：mobi库的支持有限，主要从文件名解析
        
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
            import os
            opf_file = None
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    if file.endswith('.opf'):
                        opf_file = os.path.join(root, file)
                        break
                if opf_file:
                    break
            
            if opf_file:
                metadata = self._parse_opf(opf_file)
                
                # 清理临时文件
                import shutil
                shutil.rmtree(tempdir, ignore_errors=True)
                
                log.info(f"成功解析MOBI: {file_path.name} -> {metadata['title']}")
                return metadata
            else:
                # 清理临时文件
                import shutil
                shutil.rmtree(tempdir, ignore_errors=True)
                
                raise Exception("未找到OPF文件")
                
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
                "cover": None,  # MOBI封面提取较复杂，暂不实现
            }
            
        except Exception as e:
            log.error(f"解析OPF文件失败: {opf_path}, 错误: {e}")
            return {
                "title": None,
                "author": None,
                "description": None,
                "publisher": None,
                "cover": None,
            }
