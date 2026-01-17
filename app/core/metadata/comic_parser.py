"""
漫画/压缩包解析器
支持 ZIP/CBZ 格式的漫画文件解析
"""
import zipfile
import re
from pathlib import Path
from typing import List, Dict, Optional, IO

class ComicParser:
    """漫画文件解析器"""
    
    # 支持的图片扩展名
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    
    @staticmethod
    def _natural_sort_key(s: str) -> List:
        """自然排序键生成"""
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    @classmethod
    def get_image_list(cls, file_path: Path) -> List[Dict[str, str]]:
        """
        获取压缩包内的图片列表
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict]: 图片信息列表，包含 filename 和 size
        """
        if not file_path.exists():
            return []
            
        images = []
        try:
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for info in zf.infolist():
                        # 忽略目录和隐藏文件
                        if info.is_dir() or info.filename.startswith('.') or '__MACOSX' in info.filename:
                            continue
                            
                        # 检查扩展名
                        ext = Path(info.filename).suffix.lower()
                        if ext in cls.IMAGE_EXTENSIONS:
                            images.append({
                                "filename": info.filename,
                                "size": info.file_size
                            })
                            
            # 自然排序
            images.sort(key=lambda x: cls._natural_sort_key(x['filename']))
            return images
            
        except Exception as e:
            # 记录错误但不抛出，返回空列表
            print(f"解析漫画文件失败: {e}")
            return []

    @classmethod
    def get_image_stream(cls, file_path: Path, filename: str) -> Optional[IO[bytes]]:
        """
        获取单张图片的字节流
        
        Args:
            file_path: 压缩包路径
            filename: 图片文件名（包含路径）
            
        Returns:
            IO[bytes]: 图片字节流，如果未找到或出错则返回 None
        """
        try:
            if zipfile.is_zipfile(file_path):
                zf = zipfile.ZipFile(file_path, 'r')
                try:
                    return zf.open(filename)
                except KeyError:
                    zf.close()
                    return None
                # 注意：这里我们返回了打开的文件流。
                # 调用者负责关闭它，或者我们需要改变策略读取到内存。
                # 对于大文件，ZipExtFile 是流式的，但ZipFile 对象需要保持打开状态吗？
                # ZipFile 上下文管理器会在退出时关闭文件。
                # 如果我们返回 zf.open() 的结果，zf 关闭后流可能不可用。
                # 更好的方式可能是读取内容到 BytesIO，或者让调用者管理 ZipFile。
                # 为了简单起见，这里我们读取到内存 BytesIO，因为单张图片通常不大。
                
        except Exception as e:
            print(f"读取图片流失败: {e}")
            return None
            
        return None

    @classmethod
    def get_image_data(cls, file_path: Path, filename: str) -> Optional[bytes]:
        """
        获取单张图片的二进制数据
        """
        try:
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    return zf.read(filename)
        except Exception as e:
            print(f"读取图片数据失败: {e}")
            return None
        return None
