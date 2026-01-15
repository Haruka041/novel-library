#!/bin/bash

# 小说书库管理系统 - Git 初始化脚本
# 此脚本帮助你快速推送代码到 GitHub

echo "🚀 小说书库管理系统 - GitHub 初始化向导"
echo "========================================="
echo ""

# 检查是否已安装 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误：未检测到 Git"
    echo "请先安装 Git: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git 已安装"
echo ""

# 检查 Git 用户配置
if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    echo "📝 首次使用需要配置 Git 用户信息"
    read -p "请输入你的名字: " username
    read -p "请输入你的邮箱: " email
    
    git config --global user.name "$username"
    git config --global user.email "$email"
    
    echo "✅ Git 用户信息已配置"
    echo ""
fi

# 获取 GitHub 用户名
echo "📦 准备推送到 GitHub"
read -p "请输入你的 GitHub 用户名: " github_username

if [ -z "$github_username" ]; then
    echo "❌ GitHub 用户名不能为空"
    exit 1
fi

echo ""
echo "📋 接下来的操作："
echo "1. 初始化 Git 仓库"
echo "2. 添加所有文件"
echo "3. 创建初始提交"
echo "4. 连接到 GitHub 仓库"
echo "5. 推送代码"
echo ""

read -p "继续吗？(y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

echo ""
echo "🔧 初始化 Git 仓库..."

# 检查是否已经是 Git 仓库
if [ -d ".git" ]; then
    echo "⚠️  已存在 Git 仓库，跳过初始化"
else
    git init
    echo "✅ Git 仓库初始化完成"
fi

echo ""
echo "📁 添加文件..."
git add .

echo ""
echo "💾 创建提交..."
git commit -m "Initial commit: Novel Library Management System" || echo "⚠️  没有新的改动需要提交"

echo ""
echo "🔗 连接到 GitHub..."

# 检查是否已有 origin
if git remote get-url origin &> /dev/null; then
    echo "⚠️  已存在 origin 远程仓库"
    current_origin=$(git remote get-url origin)
    echo "当前 origin: $current_origin"
    read -p "是否替换为新的仓库地址？(y/n): " replace
    
    if [ "$replace" == "y" ] || [ "$replace" == "Y" ]; then
        git remote remove origin
        git remote add origin "https://github.com/$github_username/novel-library.git"
        echo "✅ 已更新 origin"
    fi
else
    git remote add origin "https://github.com/$github_username/novel-library.git"
    echo "✅ 已添加 origin"
fi

echo ""
echo "📤 推送到 GitHub..."
echo ""
echo "⚠️  重要提示："
echo "   如果要求输入密码，请使用 GitHub Personal Access Token"
echo "   获取方式：https://github.com/settings/tokens"
echo "   选择 'Generate new token (classic)' 并勾选 'repo' 权限"
echo ""

# 设置分支名并推送
git branch -M main

if git push -u origin main; then
    echo ""
    echo "🎉 成功推送到 GitHub！"
    echo ""
    echo "📋 下一步操作："
    echo "1. 访问 https://github.com/$github_username/novel-library"
    echo "2. 点击 'Actions' 标签查看自动构建进度"
    echo "3. 构建完成后，在 'Packages' 中将镜像设置为 Public"
    echo "4. 参考 QUICK_START.md 在服务器部署"
    echo ""
    echo "🐳 Docker 镜像地址: ghcr.io/$github_username/novel-library:latest"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "常见问题："
    echo "1. 确保已在 GitHub 创建 novel-library 仓库"
    echo "   创建地址: https://github.com/new"
    echo "2. 使用 Personal Access Token 而非密码"
    echo "3. 检查网络连接"
    echo ""
    echo "详细说明请参考 QUICK_START.md"
fi
