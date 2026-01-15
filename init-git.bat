@echo off
chcp 65001 >nul
REM 小说书库管理系统 - Git 初始化脚本 (Windows版)

echo.
echo 小说书库管理系统 - GitHub 初始化向导
echo =========================================
echo.

REM 检查是否已安装 Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到 Git
    echo 请先安装 Git: https://git-scm.com/download/windows
    pause
    exit /b 1
)

echo [OK] Git 已安装
echo.

REM 获取 GitHub 用户名
set "github_username="
set /p "github_username=请输入你的 GitHub 用户名: "

if "%github_username%"=="" (
    echo [错误] GitHub 用户名不能为空
    pause
    exit /b 1
)

echo.
echo 接下来的操作：
echo 1. 初始化 Git 仓库
echo 2. 添加所有文件
echo 3. 创建初始提交
echo 4. 连接到 GitHub 仓库
echo 5. 推送代码
echo.

set "confirm="
set /p "confirm=继续吗？(y/n): "
if /i not "%confirm%"=="y" (
    echo [取消] 操作已取消
    pause
    exit /b 0
)

echo.
echo [步骤1] 初始化 Git 仓库...

if exist .git (
    echo [提示] 已存在 Git 仓库，跳过初始化
) else (
    git init
    if %ERRORLEVEL% equ 0 (
        echo [OK] Git 仓库初始化完成
    )
)

echo.
echo [步骤2] 添加文件...
git add .

echo.
echo [步骤3] 创建提交...
git commit -m "Initial commit: Novel Library Management System"

echo.
echo [步骤4] 连接到 GitHub...

REM 检查是否已有 origin
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [提示] 已存在 origin 远程仓库，正在移除...
    git remote remove origin
)

git remote add origin https://github.com/%github_username%/novel-library.git
echo [OK] 已添加 origin

echo.
echo [步骤5] 推送到 GitHub...
echo.
echo [重要提示]
echo 如果要求输入密码，请使用 GitHub Personal Access Token
echo 获取方式：https://github.com/settings/tokens
echo 选择 'Generate new token (classic)' 并勾选 'repo' 权限
echo.

git branch -M main
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo [成功] 已成功推送到 GitHub！
    echo ========================================
    echo.
    echo 下一步操作：
    echo 1. 访问 https://github.com/%github_username%/novel-library
    echo 2. 点击 'Actions' 标签查看自动构建进度
    echo 3. 构建完成后，在 'Packages' 中将镜像设置为 Public
    echo 4. 参考 QUICK_START.md 在服务器部署
    echo.
    echo Docker 镜像地址: ghcr.io/%github_username%/novel-library:latest
) else (
    echo.
    echo ========================================
    echo [失败] 推送失败
    echo ========================================
    echo.
    echo 常见问题：
    echo 1. 确保已在 GitHub 创建 novel-library 仓库
    echo    创建地址: https://github.com/new
    echo 2. 使用 Personal Access Token 而非密码
    echo 3. 检查网络连接
    echo.
    echo 详细说明请参考 QUICK_START.md
)

echo.
pause
