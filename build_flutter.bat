@echo off
REM Flutter Web 本地构建脚本 (Windows)
REM 用于在本地构建Flutter Web，然后部署到Docker

echo 🚀 开始构建 Flutter Web...
echo.

REM 检查Flutter是否安装
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Flutter SDK 未找到！
    echo 请先安装 Flutter: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

REM 进入Flutter项目目录
cd flutter_app

REM 检查Flutter版本
echo 📦 检查 Flutter 版本...
flutter --version
echo.

REM 启用Web支持
echo 🌐 启用 Web 支持...
flutter config --enable-web
echo.

REM 下载依赖
echo 📥 下载依赖...
flutter pub get
echo.

REM 构建Web（生产模式）
echo 🔨 构建 Flutter Web...
flutter build web --release --web-renderer canvaskit
echo.

REM 创建静态文件目录
echo 📁 准备静态文件目录...
cd ..
if not exist "app\web\static\flutter" mkdir "app\web\static\flutter"

REM 清空旧文件
echo 清理旧文件...
del /q "app\web\static\flutter\*.*" 2>nul
for /d %%p in ("app\web\static\flutter\*") do rmdir "%%p" /s /q

REM 复制构建产物
echo 📋 复制构建产物...
xcopy "flutter_app\build\web\*" "app\web\static\flutter\" /E /I /Y

REM 完成
echo.
echo ✅ Flutter Web 构建完成！
echo.
echo 构建产物位于: app\web\static\flutter\
echo.
echo 下一步：
echo 1. docker-compose down
echo 2. docker-compose build
echo 3. docker-compose up -d
echo.
echo 访问: http://192.168.0.106:8080/
echo.
pause
