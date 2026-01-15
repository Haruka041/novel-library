# Flutter Web UI 部署指南

## 概述

Novel Library 现在包含两套Web UI：
- **Flutter Web UI** (推荐) - 现代化Material Design 3界面
- **Jinja2 Template UI** (传统) - 服务器渲染的HTML模板

## 自动部署（Docker方式）

### 1. 重新构建Docker镜像

Docker会自动下载Flutter SDK并构建Web应用：

```bash
cd novel-library

# 停止现有容器
docker-compose down

# 重新构建镜像（需要15-30分钟，取决于网络速度）
docker-compose build --no-cache

# 启动容器
docker-compose up -d

# 查看构建日志
docker-compose logs -f
```

### 2. 访问Flutter Web UI

构建完成后，访问：

- **Flutter Web UI**: http://192.168.0.106:8080/
  - 自动重定向到 `/flutter/`
  - 现代化Emby风格界面
  
- **旧版UI**: http://192.168.0.106:8080/legacy
  - 传统Jinja2模板界面
  - 作为备用保留

- **API文档**: http://192.168.0.106:8080/docs
  - FastAPI Swagger文档

## 构建过程说明

### 多阶段Docker构建

```
阶段1: Flutter Builder
├─ 下载Flutter SDK (~400MB)
├─ 复制flutter_app/
├─ flutter pub get (下载依赖)
└─ flutter build web --release (构建产物)

阶段2: Python应用
├─ 复制Python代码
├─ 安装Python依赖
└─ 复制Flutter构建产物到 /app/web/static/flutter/
```

### 预计时间和大小

- **首次构建时间**: 15-30分钟
  - 下载Flutter SDK: 5-10分钟
  - 构建Flutter Web: 5-10分钟
  - 安装Python依赖: 2-5分钟

- **最终镜像大小**: ~800MB
  - Python基础镜像: ~120MB
  - Python依赖: ~200MB
  - Flutter Web产物: ~20MB
  - 应用代码: ~10MB

- **后续构建**: 5-10分钟
  - Docker会缓存Flutter SDK层

## 故障排除

### 1. 构建超时或失败

如果Flutter SDK下载超时：

```bash
# 使用国内镜像加速
# 编辑 Dockerfile，修改Flutter安装行：
ENV PUB_HOSTED_URL=https://pub.flutter-io.cn
ENV FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
```

### 2. 内存不足

Flutter构建需要至少2GB内存：

```bash
# 增加Docker内存限制
# Docker Desktop -> Settings -> Resources -> Memory: 4GB
```

### 3. 访问404错误

如果访问Flutter UI返回404：

```bash
# 检查构建产物是否存在
docker exec -it novel-library ls -la /app/web/static/flutter/

# 应该看到:
# index.html
# main.dart.js
# flutter.js
# 等文件
```

### 4. 回退到旧版UI

如果Flutter UI有问题，可以临时使用旧版：

1. 访问 http://192.168.0.106:8080/legacy
2. 或修改 `app/web/routes/pages.py`，注释掉重定向

## 本地开发（不使用Docker）

### 方式1: 本地构建Flutter Web

```bash
# 1. 构建Flutter Web
cd flutter_app
flutter pub get
flutter build web --release

# 2. 复制到静态文件目录
mkdir -p ../app/web/static/flutter
cp -r build/web/* ../app/web/static/flutter/

# 3. 运行Python后端
cd ..
python -m app.main
```

### 方式2: Flutter开发服务器

```bash
# Flutter在开发模式运行（热重载）
cd flutter_app
flutter run -d chrome --web-port=3000

# 访问 http://localhost:3000
# 但需要修改API地址为 http://192.168.0.106:8080
```

## UI对比

### Flutter Web UI
✅ 现代化Material Design 3  
✅ 流畅的动画效果  
✅ 响应式设计  
✅ 单页应用（SPA）  
✅ 离线支持  
⚠️ 首次加载稍慢（~2MB JS）

### Jinja2 Template UI
✅ 服务器渲染，首屏快  
✅ SEO友好  
✅ 无需JavaScript  
✅ 兼容性好  
⚠️ 页面刷新跳转  
⚠️ UI较传统

## 性能优化

### 1. 启用Gzip压缩

在nginx配置中：

```nginx
gzip on;
gzip_types application/javascript text/css application/json;
gzip_min_length 1000;
```

### 2. 启用缓存

Flutter产物可以长期缓存：

```nginx
location /flutter/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. CDN加速

将Flutter静态文件上传到CDN，修改`index.html`中的base路径。

## 更新Flutter版本

```bash
# 修改Dockerfile中的Flutter版本
# 将 -b stable 改为 -b 3.16.0 等特定版本

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

## 卸载Flutter（节省空间）

如果不需要Flutter UI：

1. 使用旧版Dockerfile（不含Flutter构建阶段）
2. 删除 `flutter_app/` 目录
3. 修改路由，移除重定向

```bash
# 恢复到Python-only镜像
git checkout HEAD -- Dockerfile
docker-compose build
docker-compose up -d
```

## 支持

如果遇到问题：
1. 查看Docker日志: `docker-compose logs -f`
2. 检查Flutter构建日志
3. 提交Issue到GitHub

---

**构建时间**: 首次 15-30分钟，后续 5-10分钟  
**镜像大小**: ~800MB  
**运行内存**: ~200MB  
**适用场景**: 需要现代化Web UI的用户
