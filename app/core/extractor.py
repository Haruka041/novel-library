"""
压缩包解压模块
支持 zip、rar、7z、iso、tar.gz 等格式
"""
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import List

import py7zr
import pycdlib
import rarfile

from app.config import settings
from app.utils.logger import log


class Extractor:
    """压缩包解压器"""
    
    def __init__(self):
        self.temp_dir = Path(settings.directories.temp)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(self, archive_path: Path, dest_dir: Path) -> List[Path]:
        """
        解压压缩包
        
        Args:
            archive_path: 压缩包路径
            dest_dir: 目标目录
            
        Returns:
            解压后的文件列表
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        suffix = archive_path.suffix.lower()
        
        try:
            if suffix == '.zip':
                self._extract_zip(archive_path, dest_dir)
            elif suffix == '.rar':
                self._extract_rar(archive_path, dest_dir)
            elif suffix == '.7z':
                self._extract_7z(archive_path, dest_dir)
            elif suffix == '.iso':
                self._extract_iso(archive_path, dest_dir)
            elif suffix in ['.gz', '.bz2'] or archive_path.name.endswith('.tar.gz') or archive_path.name.endswith('.tar.bz2'):
                self._extract_tar(archive_path, dest_dir)
            else:
                raise ValueError(f"不支持的压缩格式: {suffix}")
            
            log.info(f"成功解压: {archive_path} -> {dest_dir}")
            
            # 查找所有电子书文件
            return self._find_ebook_files(dest_dir)
            
        except Exception as e:
            log.error(f"解压失败: {archive_path}, 错误: {e}")
            raise
    
    def _extract_zip(self, archive_path: Path, dest_dir: Path):
        """解压 ZIP 文件"""
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
    
    def _extract_rar(self, archive_path: Path, dest_dir: Path):
        """解压 RAR 文件"""
        with rarfile.RarFile(archive_path, 'r') as rar_ref:
            rar_ref.extractall(dest_dir)
    
    def _extract_7z(self, archive_path: Path, dest_dir: Path):
        """解压 7Z 文件"""
        with py7zr.SevenZipFile(archive_path, 'r') as z_ref:
            z_ref.extractall(dest_dir)
    
    def _extract_tar(self, archive_path: Path, dest_dir: Path):
        """解压 TAR 文件"""
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(dest_dir)
    
    def _extract_iso(self, archive_path: Path, dest_dir: Path):
        """解压 ISO 文件"""
        iso = pycdlib.PyCdlib()
        iso.open(str(archive_path))
        
        # 遍历ISO中的所有文件
        for dirname, dirlist, filelist in iso.walk(iso_path='/'):
            for filename in filelist:
                iso_file_path = dirname + '/' + filename if dirname != '/' else '/' + filename
                
                # 构建输出路径
                rel_path = iso_file_path.lstrip('/')
                output_path = dest_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 提取文件
                iso.get_file_from_iso(output_path, iso_path=iso_file_path)
        
        iso.close()
    
    def _find_ebook_files(self, directory: Path) -> List[Path]:
        """
        查找目录中的所有电子书文件
        
        Args:
            directory: 搜索目录
            
        Returns:
            电子书文件路径列表
        """
        ebook_files = []
        ebook_extensions = ['.txt', '.epub', '.mobi', '.azw3']
        
        for ext in ebook_extensions:
            ebook_files.extend(directory.rglob(f'*{ext}'))
        
        log.debug(f"在 {directory} 中找到 {len(ebook_files)} 个电子书文件")
        return ebook_files
    
    def cleanup(self, directory: Path):
        """
        清理临时目录
        
        Args:
            directory: 要清理的目录
        """
        try:
            if directory.exists() and directory.is_dir():
                shutil.rmtree(directory)
                log.debug(f"清理临时目录: {directory}")
        except Exception as e:
            log.warning(f"清理临时目录失败: {directory}, 错误: {e}")
