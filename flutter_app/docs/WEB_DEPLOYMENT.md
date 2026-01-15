# Flutter Web UI 部署指南

## 概述

本Flutter应用主要作为**Web前端UI**使用，提供现代化的单页应用（SPA）体验，替代传统的Jinja2模板。

## Web部署架构

```
┌─────────────────┐
│   用户浏览器     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Nginx/Apache   │  静态文件服务
│  (端口 80/443)  │
└────────┬────────┘
         │
         ├─► Flutter Web (/)          - 前端UI
         │   build/web/
         │
         └─► Backend API (/api)       - 后端API
             FastAPI (端口 8000)
```

## 构建Flutter Web

### 1. 生产构建

```bash
cd novel-library/flutter_app

# 构建Web版本
flutter build web --release

# 输出目录: build/web/
```

### 2. 构建选项

```bash
# 基础构建
flutter build web --release

# 自定义base href（用于子目录部署）
flutter build web --release --base-href /app/

# 优化体积（使用CanvasKit）
flutter build web --release --web-renderer canvaskit

# 使用HTML renderer（更小的体积，更快的加载）
flutter build web --release --web-renderer html

# 推荐：混合模式
flutter build web --release --web-renderer auto
```

### 3. 构建输出

```
build/web/
├── index.html              # 入口HTML
├── main.dart.js           # 主要JS文件
├── flutter.js             # Flutter核心
├── assets/                # 资源文件
├── icons/                 # 图标
├── canvaskit/             # CanvasKit渲染器
└── version.json           # 版本信息
```

## Nginx配置

### 1. 完整配置示例

创建 `/etc/nginx/sites-available/novel-library`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 强制HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Flutter Web静态文件
    location / {
        root /var/www/novel-library/flutter_app/build/web;
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # index.html不缓存
        location = /index.html {
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            expires 0;
        }
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 书籍封面和文件下载
    location /books {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # 大文件优化
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;
}
```

### 2. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/novel-library /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## Apache配置

创建 `/etc/apache2/sites-available/novel-library.conf`:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    DocumentRoot /var/www/novel-library/flutter_app/build/web
    
    <Directory /var/www/novel-library/flutter_app/build/web>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # SPA路由支持
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # API代理
    ProxyPass /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api
    
    ProxyPass /books http://127.0.0.1:8000/books
    ProxyPassReverse /books http://127.0.0.1:8000/books
    
    # 启用压缩
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css
        AddOutputFilterByType DEFLATE application/javascript application/json
    </IfModule>
    
    # 缓存控制
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType image/* "access plus 1 year"
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType text/html "access plus 0 seconds"
    </IfModule>
</VirtualHost>
```

## Docker部署

### Dockerfile for Web

创建 `novel-library/flutter_app/Dockerfile.web`:

```dockerfile
# 构建阶段
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# 复制pubspec文件
COPY pubspec.yaml pubspec.lock ./

# 安装依赖
RUN flutter pub get

# 复制源代码
COPY . .

# 构建Web版本
RUN flutter build web --release --web-renderer auto

# 生产阶段
FROM nginx:alpine

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=build /app/build/web /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf for Docker

创建 `novel-library/flutter_app/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
    
    # SPA路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # index.html不缓存
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires 0;
    }
}
```

### docker-compose.yml 整合

更新 `novel-library/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # 后端API
  backend:
    build: .
    container_name: novel-library-backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/novel_library
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    networks:
      - novel-network
    depends_on:
      - db

  # Flutter Web前端
  frontend:
    build:
      context: ./flutter_app
      dockerfile: Dockerfile.web
    container_name: novel-library-frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    networks:
      - novel-network
    depends_on:
      - backend

  # 数据库
  db:
    image: postgres:15
    container_name: novel-library-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=novel_library
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - novel-network

networks:
  novel-network:
    driver: bridge

volumes:
  db_data:
```

## 部署脚本

创建 `novel-library/flutter_app/deploy.sh`:

```bash
#!/bin/bash

echo "=== Flutter Web 部署脚本 ==="

# 颜色输出
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 检查Flutter
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}错误: Flutter未安装${NC}"
    exit 1
fi

echo -e "${GREEN}1. 清理旧构建...${NC}"
flutter clean

echo -e "${GREEN}2. 获取依赖...${NC}"
flutter pub get

echo -e "${GREEN}3. 构建Web版本...${NC}"
flutter build web --release --web-renderer auto

echo -e "${GREEN}4. 部署到服务器...${NC}"

# 方式1: 直接复制到Nginx目录
WEB_DIR="/var/www/novel-library/flutter_app/build/web"
if [ -d "$WEB_DIR" ]; then
    sudo rm -rf "$WEB_DIR"
fi
sudo mkdir -p "$(dirname "$WEB_DIR")"
sudo cp -r build/web "$WEB_DIR"
sudo chown -R www-data:www-data "$WEB_DIR"

echo -e "${GREEN}5. 重启Nginx...${NC}"
sudo systemctl restart nginx

echo -e "${GREEN}✓ 部署完成!${NC}"
echo -e "${YELLOW}访问: https://your-domain.com${NC}"
```

## 配置API地址

### 生产环境配置

更新 `lib/services/api_config.dart`:

```dart
class ApiConfig {
  // Web部署时，API在同域名下的/api路径
  static String get baseUrl {
    // 检查是否在Web环境
    if (kIsWeb) {
      // 生产环境：使用相对路径
      return window.location.origin;
    }
    // 开发环境
    return 'http://localhost:8000';
  }
  
  static const String apiPrefix = '/api';
  static String get loginEndpoint => '$apiPrefix/auth/login';
  static String get booksEndpoint => '$apiPrefix/books';
  static String get searchEndpoint => '$apiPrefix/search';
}
```

## 性能优化

### 1. 启用Service Worker

Flutter Web自动生成Service Worker，启用离线支持：

```javascript
// 在index.html中已自动配置
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('flutter_service_worker.js');
}
```

### 2. 预加载关键资源

在 `web/index.html` 中添加：

```html
<head>
  <!-- 预加载关键字体 -->
  <link rel="preload" href="assets/fonts/MaterialIcons-Regular.otf" as="font" crossorigin>
  
  <!-- DNS预解析 -->
  <link rel="dns-prefetch" href="//your-api-domain.com">
</head>
```

### 3. 压缩和优化

```bash
# 构建时自动压缩
flutter build web --release --tree-shake-icons

# 使用wasm（实验性）
flutter build web --release --wasm
```

## 监控和日志

### Nginx访问日志

```nginx
access_log /var/log/nginx/novel-library-access.log;
error_log /var/log/nginx/novel-library-error.log;
```

### 查看日志

```bash
# 实时查看访问日志
tail -f /var/log/nginx/novel-library-access.log

# 查看错误日志
tail -f /var/log/nginx/novel-library-error.log
```

## 安全配置

### 1. Content Security Policy

在Nginx配置中添加：

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://your-api-domain.com;" always;
```

### 2. HTTPS强制

```nginx
# 强制HTTPS
if ($scheme != "https") {
    return 301 https://$server_name$request_uri;
}

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 常见问题

### Q: Flutter Web刷新后404？
A: 确保Nginx/Apache配置了`try_files $uri /index.html`

### Q: API调用跨域问题？
A: 使用Nginx反向代理，API和前端在同一域名下

### Q: 首次加载慢？
A: 
1. 启用Gzip压缩
2. 使用HTML renderer
3. 配置CDN
4. 启用浏览器缓存

### Q: 如何更新部署？
A: 运行 `./deploy.sh` 脚本自动构建和部署

## 总结

Flutter Web作为现代化前端UI的优势：

1. **单页应用** - 流畅的用户体验
2. **响应式设计** - 适配各种屏幕
3. **离线支持** - Service Worker缓存
4. **性能优秀** - 比传统Web快
5. **易于维护** - 统一的代码库
6. **现代化UI** - Material Design 3

部署后，用户访问网站将获得类似原生App的体验！
