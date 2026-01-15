"""
文件Hash计算工具
"""
import hashlib
from pathlib import Path
from typing import Literal

from app.utils.logger import log


def calculate_file_hash(
    file_path: Path,
    algorithm: Literal["md5", "sha256"] = "md5",
    chunk_size: int = 8192
) -> str:
    """
    计算文件的Hash值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5 或 sha256)
        chunk_size: 读取块大小
        
    Returns:
        文件的Hash字符串
    """
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        log.error(f"计算文件Hash失败: {file_path}, 错误: {e}")
        raise


def quick_hash(file_path: Path, sample_size: int = 1024) -> str:
    """
    快速Hash计算（仅读取文件头部）
    用于快速去重检测
    
    Args:
        file_path: 文件路径
        sample_size: 采样大小（字节）
        
    Returns:
        采样Hash字符串
    """
    hasher = hashlib.md5()
    
    try:
        # 添加文件大小到Hash
        file_size = file_path.stat().st_size
        hasher.update(str(file_size).encode())
        
        # 读取文件头部
        with open(file_path, "rb") as f:
            sample = f.read(sample_size)
            hasher.update(sample)
        
        return hasher.hexdigest()
    except Exception as e:
        log.error(f"快速Hash计算失败: {file_path}, 错误: {e}")
        raise
