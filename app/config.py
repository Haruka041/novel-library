"""
配置管理模块
加载 YAML 配置文件和环境变量
"""
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = "sqlite+aiosqlite:///data/library.db"


class DirectoriesConfig(BaseModel):
    """目录配置"""
    data: str = "/app/data"
    covers: str = "/app/covers"
    temp: str = "/tmp/novel-library"


class ScannerConfig(BaseModel):
    """扫描器配置"""
    interval: int = 3600
    recursive: bool = True
    supported_formats: List[str] = Field(default_factory=lambda: [
        ".txt", ".epub", ".mobi", ".azw3",
        ".zip", ".rar", ".7z", ".iso", ".tar.gz", ".tar.bz2"
    ])


class ExtractorConfig(BaseModel):
    """解压器配置"""
    max_file_size: int = 524288000  # 500MB
    encoding: str = "utf-8"
    nested_depth: int = 3


class DeduplicatorConfig(BaseModel):
    """去重器配置"""
    enable: bool = True
    hash_algorithm: str = "md5"
    similarity_threshold: float = 0.85


class SecurityConfig(BaseModel):
    """安全配置"""
    secret_key: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7天


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "json"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    file: str = "/app/data/logs/app.log"


class OPDSConfig(BaseModel):
    """OPDS配置"""
    title: str = "我的小说书库"
    author: str = "Novel Library"
    description: str = "个人小说收藏"
    page_size: int = 50


class Config(BaseModel):
    """主配置类"""
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    directories: DirectoriesConfig = Field(default_factory=DirectoriesConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    extractor: ExtractorConfig = Field(default_factory=ExtractorConfig)
    deduplicator: DeduplicatorConfig = Field(default_factory=DeduplicatorConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    opds: OPDSConfig = Field(default_factory=OPDSConfig)

    @classmethod
    def load(cls, config_path: str = "config/config.yaml") -> "Config":
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Config实例
        """
        # 尝试加载YAML配置
        config_data: Dict[str, Any] = {}
        
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
        
        # 环境变量覆盖
        if server_host := os.getenv("SERVER_HOST"):
            config_data.setdefault("server", {})["host"] = server_host
        if server_port := os.getenv("SERVER_PORT"):
            config_data.setdefault("server", {})["port"] = int(server_port)
        if db_url := os.getenv("DATABASE_URL"):
            config_data.setdefault("database", {})["url"] = db_url
        if secret_key := os.getenv("SECRET_KEY"):
            config_data.setdefault("security", {})["secret_key"] = secret_key
        if log_level := os.getenv("LOG_LEVEL"):
            config_data.setdefault("logging", {})["level"] = log_level
        if scan_interval := os.getenv("SCAN_INTERVAL"):
            config_data.setdefault("scanner", {})["interval"] = int(scan_interval)
        
        return cls(**config_data)

    def ensure_directories(self):
        """确保所有必要的目录存在"""
        for dir_path in [self.directories.data, self.directories.covers, self.directories.temp]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # 确保日志目录存在
        log_dir = Path(self.logging.file).parent
        log_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Config.load()
