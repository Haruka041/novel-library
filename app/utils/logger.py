"""
日志工具模块
使用 loguru 进行日志管理
"""
import sys
from pathlib import Path

from loguru import logger

from app.config import settings


def setup_logger():
    """
    配置日志系统
    """
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True,
    )
    
    # 添加文件处理器
    log_file = Path(settings.logging.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.logging.level,
        rotation=settings.logging.max_size,
        retention=settings.logging.backup_count,
        compression="zip",
        encoding="utf-8",
    )
    
    return logger


# 初始化日志
log = setup_logger()
