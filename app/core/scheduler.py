"""
定时任务调度器模块
使用 APScheduler 实现自动备份等定时任务
"""
from datetime import datetime
from typing import Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.core.backup import backup_manager
from app.utils.logger import log


class BackupScheduler:
    """备份任务调度器"""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.backup_job = None
        self.last_run: Optional[datetime] = None
        self.last_status: str = "未运行"
        self.last_error: Optional[str] = None
    
    async def start(self):
        """启动调度器"""
        if self.scheduler is not None:
            log.warning("调度器已经在运行")
            return
        
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        
        # 如果启用了自动备份，添加定时任务
        if settings.backup.auto_backup_enabled:
            await self._add_backup_job()
            log.info(
                f"自动备份已启用，计划: {settings.backup.auto_backup_schedule}"
            )
        else:
            log.info("自动备份未启用")
        
        self.scheduler.start()
        log.info("定时任务调度器已启动")
    
    async def _add_backup_job(self):
        """添加备份任务"""
        try:
            # 解析 Cron 表达式
            trigger = CronTrigger.from_crontab(
                settings.backup.auto_backup_schedule,
                timezone="Asia/Shanghai"
            )
            
            # 添加任务
            self.backup_job = self.scheduler.add_job(
                self._auto_backup_task,
                trigger=trigger,
                id="auto_backup",
                name="自动备份任务",
                replace_existing=True,
                max_instances=1,  # 同时只运行一个实例
                coalesce=True,  # 错过的任务合并执行
                misfire_grace_time=3600  # 错过任务的宽限时间（1小时）
            )
            
            # 获取下次执行时间
            next_run = self.backup_job.next_run_time
            log.info(f"备份任务已添加，下次执行时间: {next_run}")
            
        except Exception as e:
            log.error(f"添加备份任务失败: {e}")
            raise
    
    async def _auto_backup_task(self):
        """自动备份任务执行函数"""
        self.last_run = datetime.now()
        log.info("=" * 60)
        log.info("开始执行自动备份任务")
        log.info(f"执行时间: {self.last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 调用备份管理器创建备份
            result = await backup_manager.create_backup(
                includes=settings.backup.default_includes,
                description=f"自动备份 - {self.last_run.strftime('%Y-%m-%d %H:%M')}"
            )
            
            self.last_status = "成功"
            self.last_error = None
            
            log.info(f"自动备份完成: {result['backup_id']}")
            log.info(f"备份大小: {result['file_size'] / 1024 / 1024:.2f} MB")
            log.info(f"包含内容: {', '.join(result['includes'])}")
            log.info("=" * 60)
            
        except Exception as e:
            self.last_status = "失败"
            self.last_error = str(e)
            
            log.error(f"自动备份失败: {e}")
            log.error("=" * 60)
            
            # 不抛出异常，避免影响调度器继续运行
    
    async def enable_auto_backup(self, schedule: Optional[str] = None):
        """
        启用自动备份
        
        Args:
            schedule: 可选的新 Cron 表达式
        """
        if self.scheduler is None:
            raise RuntimeError("调度器未启动")
        
        # 更新配置（这里只更新运行时配置，不修改文件）
        if schedule:
            settings.backup.auto_backup_schedule = schedule
        
        settings.backup.auto_backup_enabled = True
        
        # 移除现有任务（如果存在）
        if self.backup_job:
            self.scheduler.remove_job("auto_backup")
        
        # 添加新任务
        await self._add_backup_job()
        
        log.info("自动备份已启用")
    
    async def disable_auto_backup(self):
        """禁用自动备份"""
        if self.scheduler is None:
            raise RuntimeError("调度器未启动")
        
        settings.backup.auto_backup_enabled = False
        
        # 移除任务
        if self.backup_job:
            self.scheduler.remove_job("auto_backup")
            self.backup_job = None
        
        log.info("自动备份已禁用")
    
    async def trigger_backup_now(self) -> Dict[str, Any]:
        """
        立即触发一次备份任务（不影响定时计划）
        
        Returns:
            备份结果
        """
        log.info("手动触发自动备份任务")
        
        try:
            result = await backup_manager.create_backup(
                includes=settings.backup.default_includes,
                description=f"手动触发的自动备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            log.info(f"手动触发备份完成: {result['backup_id']}")
            
            return {
                "success": True,
                "message": "备份任务执行成功",
                **result
            }
            
        except Exception as e:
            log.error(f"手动触发备份失败: {e}")
            return {
                "success": False,
                "message": f"备份任务执行失败: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取调度器状态
        
        Returns:
            状态信息字典
        """
        if self.scheduler is None:
            return {
                "running": False,
                "auto_backup_enabled": False,
                "message": "调度器未启动"
            }
        
        status = {
            "running": self.scheduler.running,
            "auto_backup_enabled": settings.backup.auto_backup_enabled,
            "schedule": settings.backup.auto_backup_schedule,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_status": self.last_status,
            "last_error": self.last_error
        }
        
        # 获取下次运行时间
        if self.backup_job:
            next_run = self.backup_job.next_run_time
            status["next_run"] = next_run.isoformat() if next_run else None
        else:
            status["next_run"] = None
        
        return status
    
    async def update_schedule(self, new_schedule: str):
        """
        更新 Cron 表达式
        
        Args:
            new_schedule: 新的 Cron 表达式
        """
        if self.scheduler is None:
            raise RuntimeError("调度器未启动")
        
        # 验证 Cron 表达式
        try:
            CronTrigger.from_crontab(new_schedule)
        except Exception as e:
            raise ValueError(f"无效的 Cron 表达式: {e}")
        
        # 更新配置
        settings.backup.auto_backup_schedule = new_schedule
        
        # 如果自动备份已启用，重新添加任务
        if settings.backup.auto_backup_enabled:
            if self.backup_job:
                self.scheduler.remove_job("auto_backup")
            await self._add_backup_job()
        
        log.info(f"备份计划已更新: {new_schedule}")
    
    async def shutdown(self):
        """关闭调度器"""
        if self.scheduler is None:
            log.warning("调度器未运行")
            return
        
        log.info("正在关闭定时任务调度器...")
        
        self.scheduler.shutdown(wait=True)
        self.scheduler = None
        self.backup_job = None
        
        log.info("定时任务调度器已关闭")


# 全局实例
backup_scheduler = BackupScheduler()
