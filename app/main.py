"""
主程序入口
初始化数据库、创建默认管理员用户并启动Web服务
"""
import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal, init_db
from app.models import User
from app.security import hash_password
from app.utils.logger import log


async def create_default_admin():
    """创建默认管理员用户"""
    async with AsyncSessionLocal() as db:
        # 检查是否已存在管理员
        result = await db.execute(
            select(User).where(User.is_admin == True)
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            # 创建默认管理员
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            admin_user = User(
                username=admin_username,
                password_hash=hash_password(admin_password),
                is_admin=True
            )
            
            db.add(admin_user)
            await db.commit()
            
            log.info(f"创建默认管理员用户: {admin_username}")
            log.warning(f"请及时修改默认密码！")
        else:
            log.info("管理员用户已存在")


async def startup():
    """启动时初始化"""
    log.info("正在初始化应用...")
    
    # 确保目录存在
    settings.ensure_directories()
    
    # 初始化数据库
    await init_db()
    log.info("数据库初始化完成")
    
    # 创建默认管理员
    await create_default_admin()
    
    log.info("应用初始化完成")


def main():
    """主函数"""
    # 运行启动任务
    asyncio.run(startup())
    
    # 启动Web服务器
    log.info(f"启动Web服务器: {settings.server.host}:{settings.server.port}")
    
    uvicorn.run(
        "app.web.app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_config=None,  # 使用我们自己的日志配置
    )


if __name__ == "__main__":
    main()
