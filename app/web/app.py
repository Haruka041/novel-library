"""
FastAPI Web应用
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.utils.logger import log

# 创建FastAPI应用
app = FastAPI(
    title="Novel Library",
    description="小说书库管理系统",
    version="1.0.0",
)

# 配置静态文件
# app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/web/templates")

# 导入路由（延迟导入避免循环依赖）
from app.web.routes import api, auth, pages

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(api.router, prefix="/api", tags=["API"])
app.include_router(pages.router, tags=["页面"])

log.info("FastAPI应用初始化完成")
