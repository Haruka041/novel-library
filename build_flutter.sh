#!/bin/bash

# Flutter Web 本地构建脚本
# 用于在本地构建Flutter Web，然后部署到Docker

set -e  # 遇到错误立即退出

echo "🚀 开始构建 Flutter Web..."

# 检查Flutter是否安装
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter SDK 未找到！"
    echo "请先安装 Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

# 进入Flutter项目目录
cd flutter_app

# 检查Flutter版本
echo "📦 检查 Flutter 版本..."
flutter --version

# 启用Web支持
echo "🌐 启用 Web 支持..."
flutter config --enable-web

# 下载依赖
echo "📥 下载依赖..."
flutter pub get

# 构建Web（生产模式）
echo "🔨 构建 Flutter Web..."
flutter build web --release --web-renderer canvaskit

# 创建静态文件目录
echo "📁 准备静态文件目录..."
cd ..
mkdir -p app/web/static/flutter

# 清空旧文件
rm -rf app/web/static/flutter/*

# 复制构建产物
echo "📋 复制构建产物..."
cp -r flutter_app/build/web/* app/web/static/flutter/

# 完成
echo "✅ Flutter Web 构建完成！"
echo ""
echo "构建产物位于: app/web/static/flutter/"
echo ""
echo "下一步："
echo "1. docker-compose down"
echo "2. docker-compose build"
echo "3. docker-compose up -d"
echo ""
echo "访问: http://192.168.0.106:8080/"
