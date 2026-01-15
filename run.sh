#!/bin/bash

# 小说书库管理系统 - 宿主机运行脚本
# 适用于 Docker 网络有问题的情况

set -e

echo "================================================"
echo "  小说书库管理系统 - 启动脚本"
echo "================================================"
echo ""

# 检查 Python 版本
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION >= 3.9" | bc)" -eq 1 ]; then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "错误: 未找到 Python 3.9+ 环境"
    echo "请安装 Python 3.9 或更高版本"
    exit 1
fi

echo "✓ 使用 Python: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo ""

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
echo ""
pip install --upgrade pip
pip install -r requirements.txt
echo ""
echo "✓ 依赖安装完成"
echo ""

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/logs
mkdir -p covers
echo "✓ 目录创建完成"
echo ""

# 设置环境变量（如果未设置）
export ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
export SECRET_KEY="${SECRET_KEY:-change-this-secret-key-$(date +%s)}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export TZ="${TZ:-Asia/Shanghai}"

echo "环境变量："
echo "  管理员用户名: $ADMIN_USERNAME"
echo "  管理员密码: $ADMIN_PASSWORD"
echo "  密钥: ${SECRET_KEY:0:20}..."
echo ""
echo "⚠️  请在首次登录后修改默认密码！"
echo ""

# 启动应用
echo "================================================"
echo "  启动应用..."
echo "================================================"
echo ""
echo "Web 界面: http://localhost:8080"
echo "API 文档: http://localhost:8080/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

$PYTHON_CMD -m app.main
