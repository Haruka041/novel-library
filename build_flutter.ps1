# Flutter Web 本地构建脚本 (PowerShell)
# 用于在本地构建Flutter Web，然后部署到Docker

Write-Host "🚀 开始构建 Flutter Web..." -ForegroundColor Green
Write-Host ""

# 检查Flutter是否安装
$flutterPath = Get-Command flutter -ErrorAction SilentlyContinue
if (-not $flutterPath) {
    Write-Host "❌ Flutter SDK 未找到！" -ForegroundColor Red
    Write-Host "请检查：" -ForegroundColor Yellow
    Write-Host "1. Flutter 是否已安装" -ForegroundColor Yellow
    Write-Host "2. PATH 环境变量是否包含 Flutter bin 目录" -ForegroundColor Yellow
    Write-Host "3. 重启 VSCode/PowerShell 后再试" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "或者手动执行以下命令：" -ForegroundColor Cyan
    Write-Host "cd flutter_app" -ForegroundColor White
    Write-Host "flutter config --enable-web" -ForegroundColor White
    Write-Host "flutter pub get" -ForegroundColor White
    Write-Host "flutter build web --release --web-renderer canvaskit" -ForegroundColor White
    Write-Host "cd .." -ForegroundColor White
    Write-Host "Copy-Item -Path flutter_app\build\web\* -Destination app\web\static\flutter\ -Recurse -Force" -ForegroundColor White
    pause
    exit 1
}

# 进入Flutter项目目录
Set-Location flutter_app

# 检查Flutter版本
Write-Host "📦 检查 Flutter 版本..." -ForegroundColor Cyan
flutter --version
Write-Host ""

# 启用Web支持
Write-Host "🌐 启用 Web 支持..." -ForegroundColor Cyan
flutter config --enable-web
Write-Host ""

# 下载依赖
Write-Host "📥 下载依赖..." -ForegroundColor Cyan
flutter pub get
Write-Host ""

# 构建Web（生产模式）
Write-Host "🔨 构建 Flutter Web..." -ForegroundColor Cyan
flutter build web --release --web-renderer canvaskit
Write-Host ""

# 返回上级目录
Set-Location ..

# 创建静态文件目录
Write-Host "📁 准备静态文件目录..." -ForegroundColor Cyan
if (-not (Test-Path "app\web\static\flutter")) {
    New-Item -ItemType Directory -Path "app\web\static\flutter" -Force | Out-Null
}

# 清空旧文件
Write-Host "清理旧文件..." -ForegroundColor Cyan
Remove-Item "app\web\static\flutter\*" -Recurse -Force -ErrorAction SilentlyContinue

# 复制构建产物
Write-Host "📋 复制构建产物..." -ForegroundColor Cyan
Copy-Item -Path "flutter_app\build\web\*" -Destination "app\web\static\flutter\" -Recurse -Force

# 完成
Write-Host ""
Write-Host "✅ Flutter Web 构建完成！" -ForegroundColor Green
Write-Host ""
Write-Host "构建产物位于: app\web\static\flutter\" -ForegroundColor Yellow
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1. docker-compose down" -ForegroundColor White
Write-Host "2. docker-compose build" -ForegroundColor White  
Write-Host "3. docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "访问: http://192.168.0.106:8080/" -ForegroundColor Green
Write-Host ""
