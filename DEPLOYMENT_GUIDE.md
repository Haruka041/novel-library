# 📦 GitHub 同步与 Docker 自动构建部署指南

本指南将帮助你把项目推送到 GitHub，并自动构建 Docker 镜像。

## 📋 前置准备

### 1. 安装 Git（如果还没有）

**Windows:**
- 下载：https://git-scm.com/download/windows
- 安装后打开 Git Bash

**Mac/Linux:**
```bash
# Mac
brew install git

# Ubuntu/Debian
sudo apt-get install git
```

### 2. 配置 Git

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

### 3. 创建 GitHub 账号

访问 https://github.com 注册账号（如果还没有）

---

## 🚀 第一步：推送代码到 GitHub

### 1. 在 GitHub 创建新仓库

1. 登录 GitHub
2. 点击右上角的 `+` → `New repository`
3. 填写信息：
   - Repository name: `novel-library`
   - Description: `小说书库管理系统`
   - 选择 `Public`（公开）或 `Private`（私有）
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 `Create repository`

### 2. 推送本地代码

在 `novel-library` 目录下打开终端（Windows 用 Git Bash），执行：

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "Initial commit: Novel Library Management System"

# 4. 添加 GitHub 远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/你的用户名/novel-library.git

# 5. 推送到 GitHub
git branch -M main
git push -u origin main
```

**如果遇到认证问题：**
- GitHub 现在需要使用 Personal Access Token (PAT)
- 访问：https://github.com/settings/tokens
- 点击 `Generate new token` → `Generate new token (classic)`
- 勾选 `repo` 权限
- 生成后复制 token，推送时用 token 作为密码

---

## 🐳 第二步：GitHub Actions 自动构建 Docker 镜像

### 自动触发构建

推送代码后，GitHub Actions 会自动：
1. 检出代码
2. 构建 Docker 镜像
3. 推送到 GitHub Container Registry (ghcr.io)

### 查看构建状态

1. 访问你的 GitHub 仓库
2. 点击 `Actions` 标签
3. 查看 `Build and Push Docker Image` 工作流
4. 等待构建完成（大约 3-5 分钟）

### 构建成功后

镜像会发布到：`ghcr.io/你的用户名/novel-library:latest`

---

## 🖥️ 第三步：服务器部署

### 方法一：使用 docker-compose（推荐）

#### 1. 在服务器上创建部署目录

```bash
mkdir -p ~/novel-library-deploy
cd ~/novel-library-deploy
```

#### 2. 下载配置文件

从 GitHub 下载 `docker-compose.prod.yml`：

```bash
wget https://raw.githubusercontent.com/你的用户名/novel-library/main/docker-compose.prod.yml
mv docker-compose.prod.yml docker-compose.yml
```

或者手动创建 `docker-compose.yml`，内容见下方。

#### 3. 编辑 docker-compose.yml

```bash
nano docker-compose.yml
```

修改以下内容：

```yaml
version: '3.8'

services:
  novel-library:
    # 替换为你的 GitHub 用户名
    image: ghcr.io/你的用户名/novel-library:latest
    container_name: novel-library
    ports:
      - "8080:8080"
    volumes:
      # 修改为你的小说文件路径
      - /path/to/your/novels:/data/novels:ro
      - ./data:/app/data
      - ./covers:/app/covers
      - ./config:/app/config
    environment:
      - TZ=Asia/Shanghai
      - ADMIN_USERNAME=admin
      # 修改为强密码
      - ADMIN_PASSWORD=你的强密码
      # 生成随机密钥：openssl rand -hex 32
      - SECRET_KEY=你的随机密钥
    restart: unless-stopped
```

#### 4. 拉取镜像并启动

```bash
# 如果镜像是私有的，需要先登录
echo "你的GitHub_PAT" | docker login ghcr.io -u 你的用户名 --password-stdin

# 拉取镜像
docker pull ghcr.io/你的用户名/novel-library:latest

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 5. 访问系统

打开浏览器访问：`http://服务器IP:8080`

默认账户：
- 用户名：`admin`
- 密码：你在 docker-compose.yml 中设置的密码

---

### 方法二：直接使用 docker run

```bash
docker run -d \
  --name novel-library \
  -p 8080:8080 \
  -v /path/to/your/novels:/data/novels:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/covers:/app/covers \
  -v $(pwd)/config:/app/config \
  -e TZ=Asia/Shanghai \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=你的密码 \
  -e SECRET_KEY=你的密钥 \
  --restart unless-stopped \
  ghcr.io/你的用户名/novel-library:latest
```

---

## 🔄 第四步：更新部署

### 当你修改代码并推送到 GitHub 后：

```bash
# 在服务器上
cd ~/novel-library-deploy

# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d

# 查看新容器状态
docker-compose logs -f
```

---

## 🔐 配置 GitHub Container Registry 权限

### 设置镜像为公开（推荐）

1. 访问：https://github.com/你的用户名?tab=packages
2. 点击 `novel-library` 包
3. 点击 `Package settings`
4. 在 `Danger Zone` → `Change package visibility` → 选择 `Public`

这样服务器拉取镜像时不需要登录。

### 如果保持私有

需要创建 GitHub Personal Access Token：

1. 访问：https://github.com/settings/tokens
2. `Generate new token (classic)`
3. 勾选 `read:packages` 权限
4. 复制 token

在服务器登录：
```bash
echo "你的TOKEN" | docker login ghcr.io -u 你的用户名 --password-stdin
```

---

## 📝 常用命令速查

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker exec -it novel-library bash

# 清理旧镜像
docker image prune -a
```

---

## ❓ 常见问题

### Q: GitHub Actions 构建失败？

**A:** 检查 Actions 日志，常见原因：
- Dockerfile 语法错误
- 依赖安装失败（网络问题）
- 权限不足（检查 workflow 文件的 permissions）

### Q: 服务器拉取镜像失败？

**A:** 
1. 确认镜像名称正确（包括用户名小写）
2. 如果是私有镜像，确认已登录 ghcr.io
3. 检查网络连接

### Q: 容器启动失败？

**A:**
```bash
# 查看详细日志
docker logs novel-library

# 检查配置
docker-compose config
```

### Q: 如何生成安全的 SECRET_KEY？

**A:**
```bash
# Linux/Mac
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_hex(32))"

# Windows PowerShell
-join ((48..57) + (97..102) | Get-Random -Count 64 | % {[char]$_})
```

---

## 🎯 完整流程总结

1. **本地开发** → 修改代码
2. **Git 推送** → `git push`
3. **自动构建** → GitHub Actions 构建 Docker 镜像
4. **镜像发布** → 推送到 ghcr.io
5. **服务器部署** → `docker-compose pull && docker-compose up -d`

每次修改代码后，只需执行 `git push`，GitHub 会自动构建新镜像，服务器更新镜像即可。

---

## 📞 获取帮助

- GitHub 仓库：https://github.com/你的用户名/novel-library
- 提交 Issue：https://github.com/你的用户名/novel-library/issues
- 查看 Actions 构建日志：https://github.com/你的用户名/novel-library/actions
