# 🚀 新手快速部署指南

这是一个简化版的部署指南，专为新手准备。只需跟着步骤操作即可！

## 📦 第一步：推送到 GitHub（5分钟）

### 1. 打开终端

- **Windows**: 打开 Git Bash（如果没有，先安装 Git: https://git-scm.com/download/windows）
- **Mac**: 打开 Terminal
- **Linux**: 打开终端

### 2. 进入项目目录

```bash
cd novel-library
```

### 3. 设置 Git 用户信息（首次使用需要）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 4. 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. Repository name 填写：`novel-library`
3. 选择 `Public`（公开）
4. **不要**勾选 "Add a README file"
5. 点击 `Create repository`

### 5. 复制下面的命令执行

**⚠️ 注意：替换 `YOUR_USERNAME` 为你的 GitHub 用户名**

```bash
# 初始化
git init
git add .
git commit -m "Initial commit"

# 连接到 GitHub（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/novel-library.git

# 推送
git branch -M main
git push -u origin main
```

如果要求输入用户名和密码：
- 用户名：你的 GitHub 用户名
- 密码：使用 Personal Access Token（不是 GitHub 密码）
  - 获取 Token: https://github.com/settings/tokens
  - 点击 `Generate new token (classic)`
  - 勾选 `repo` 权限
  - 生成后复制，粘贴作为密码

---

## ⏱️ 第二步：等待自动构建（3-5分钟）

### 查看构建进度

1. 访问你的仓库：`https://github.com/YOUR_USERNAME/novel-library`
2. 点击顶部的 `Actions` 标签
3. 看到绿色的 ✅ 表示构建成功

### 设置镜像为公开（推荐）

1. 访问：`https://github.com/YOUR_USERNAME?tab=packages`
2. 点击 `novel-library` 包
3. 点击右侧的 `Package settings`
4. 滚动到底部 `Danger Zone`
5. 点击 `Change visibility` → 选择 `Public` → 确认

这样服务器拉取镜像时不需要登录。

---

## 🖥️ 第三步：服务器部署（5分钟）

### 在服务器执行以下命令

```bash
# 1. 创建部署目录
mkdir -p ~/novel-deploy
cd ~/novel-deploy

# 2. 创建配置文件
nano docker-compose.yml
```

### 复制以下内容到文件中

**⚠️ 注意修改以下4处：**
1. `YOUR_USERNAME` → 你的 GitHub 用户名
2. `/path/to/your/novels` → 你的小说文件夹路径
3. `your-strong-password` → 设置管理员密码
4. `your-random-secret-key` → 随机字符串（可用这个命令生成：`openssl rand -hex 32`）

```yaml
version: '3.8'

services:
  novel-library:
    image: ghcr.io/YOUR_USERNAME/novel-library:latest
    container_name: novel-library
    ports:
      - "8080:8080"
    volumes:
      - /path/to/your/novels:/data/novels:ro
      - ./data:/app/data
      - ./covers:/app/covers
    environment:
      - TZ=Asia/Shanghai
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-strong-password
      - SECRET_KEY=your-random-secret-key
    restart: unless-stopped
```

按 `Ctrl + O` 保存，`Ctrl + X` 退出。

### 启动服务

```bash
# 拉取镜像并启动
docker-compose up -d

# 查看日志（确认启动成功）
docker-compose logs -f
```

看到类似 `启动Web服务器: 0.0.0.0:8080` 表示成功！

按 `Ctrl + C` 退出日志查看。

---

## 🎉 第四步：使用系统

### 1. 打开浏览器

访问：`http://你的服务器IP:8080`

### 2. 登录

- 用户名：`admin`
- 密码：你在 docker-compose.yml 中设置的密码

### 3. 添加媒体库

1. 点击顶部导航 `设置` 或 `媒体库`
2. 点击 `添加媒体库`
3. 输入名称（如：我的小说）
4. 输入路径：`/data/novels`
5. 点击 `保存` 并 `开始扫描`

系统会自动解压、分类你的小说！

---

## 🔄 如何更新

### 当你修改代码后

**本地：**
```bash
cd novel-library
git add .
git commit -m "更新说明"
git push
```

**服务器：**
```bash
cd ~/novel-deploy
docker-compose pull
docker-compose up -d
```

---

## 📝 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart

# 停止
docker-compose down

# 更新
docker-compose pull && docker-compose up -d
```

---

## ❓ 遇到问题？

### GitHub 推送失败

- 确认 GitHub 用户名正确
- 使用 Personal Access Token 而非密码
- 检查网络连接

### Docker 镜像拉取失败

```bash
# 如果镜像是私有的，需要先登录
echo "你的GitHub_Token" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### 容器启动失败

```bash
# 查看详细错误
docker logs novel-library
```

### 无法访问 8080 端口

- 检查服务器防火墙
- 确认 Docker 容器正在运行：`docker ps`

---

## ✅ 完成！

现在你有一个：
- ✅ 自动解压压缩包的小说管理系统
- ✅ 托管在 GitHub 的代码仓库
- ✅ 自动构建的 Docker 镜像
- ✅ 运行在服务器上的 Web 服务

每次修改代码推送到 GitHub，会自动构建新镜像，服务器更新即可！
