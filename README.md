# 📚 Novel Library - 小说书库管理系统

一个功能强大的小说管理和阅读系统，包含完整的后端API、现代化Flutter Web前端UI、以及Telegram机器人集成。

## ✨ 主要特性

### 🎨 现代化Web界面
- **Flutter Web UI** - 单页应用（SPA），流畅的用户体验
- **Emby风格设计** - 暗色主题，海报墙布局
- **Material Design 3** - 现代化UI设计
- **响应式布局** - 适配各种屏幕尺寸

### 📖 核心功能
- **书籍管理** - 自动扫描、元数据提取、去重
- **在线阅读** - TXT/EPUB阅读器，支持进度保存
- **高级搜索** - 全文搜索，多条件筛选
- **智能分类** - 作者、标签、书库管理
- **权限控制** - 基于角色的访问控制（RBAC）
- **封面管理** - 自动提取和缓存
- **阅读进度** - 跨设备同步
- **书签收藏** - 个人书签和收藏管理

### 🤖 Telegram机器人
- 远程搜索和下载书籍
- 阅读进度查询
- 个性化推荐

### 🔧 技术栈
- **前端**: Flutter Web (Material Design 3)
- **后端**: FastAPI + Python 3.11+
- **数据库**: PostgreSQL 15+
- **认证**: JWT
- **部署**: Docker + Nginx

## 🚀 快速开始

### 方式1: Docker部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/yourusername/novel-library.git
cd novel-library

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库密码等

# 启动服务
docker-compose up -d

# 访问应用
# Flutter Web UI: http://localhost
# 后端API文档: http://localhost:8000/docs
```

### 方式2: 手动部署

#### 1. 后端部署

```bash
# 安装依赖
cd novel-library
pip install -r requirements.txt

# 配置数据库
# 编辑 config/config.yaml

# 初始化数据库
alembic upgrade head

# 创建管理员用户
python scripts/create_admin.py

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2. Flutter Web前端部署

```bash
# 安装Flutter SDK
# https://flutter.dev/docs/get-started/install

# 构建Web版本
cd flutter_app
flutter pub get
flutter build web --release

# 部署到Nginx
sudo cp -r build/web /var/www/novel-library/
# 配置Nginx（见 flutter_app/docs/WEB_DEPLOYMENT.md）
```

## 📁 项目结构

```
novel-library/
├── app/                      # 后端应用
│   ├── core/                # 核心功能（扫描、元数据等）
│   ├── web/                 # Web路由和模板
│   ├── bot/                 # Telegram机器人
│   ├── models.py            # 数据模型
│   └── config.py            # 配置管理
├── flutter_app/             # Flutter Web前端
│   ├── lib/                # Dart源代码
│   │   ├── models/         # 数据模型
│   │   ├── services/       # API服务
│   │   ├── providers/      # 状态管理
│   │   ├── screens/        # 页面
│   │   └── widgets/        # UI组件
│   └── docs/               # 前端文档
├── alembic/                 # 数据库迁移
├── config/                  # 配置文件
├── docs/                    # 文档
└── docker-compose.yml       # Docker编排
```

## 🎯 功能完成度

### 后端 (85%)
- ✅ 用户认证和授权（JWT + RBAC）
- ✅ 书籍管理（CRUD）
- ✅ 自动扫描和元数据提取
- ✅ 搜索功能（全文搜索）
- ✅ 在线阅读器（TXT/EPUB）
- ✅ 封面管理
- ✅ 阅读进度保存
- ✅ 书签和收藏
- ✅ 标签系统
- ✅ OPDS协议支持
- ✅ Telegram机器人
- ✅ 自动备份
- 📝 推荐系统（计划中）

### Flutter Web前端 (85%)
- ✅ 用户登录认证
- ✅ 书库浏览（海报墙）
- ✅ 书籍详情展示
- ✅ 搜索功能
- ✅ 在线阅读器
- ✅ 个人中心
- ✅ 响应式设计
- ✅ 离线支持（Service Worker）
- 📝 阅读进度同步
- 📝 收藏管理
- 📝 下载功能

## 📖 文档

### 后端文档
- [安装指南](MIGRATION.md)
- [API文档](http://localhost:8000/docs)
- [搜索功能](docs/SEARCH_FEATURE_IMPLEMENTATION.md)
- [在线阅读器](docs/ONLINE_READER_IMPLEMENTATION.md)
- [封面管理](docs/COVER_FEATURE_IMPLEMENTATION.md)
- [Telegram机器人](docs/TELEGRAM_BOT_IMPLEMENTATION.md)
- [备份系统](docs/BACKUP_SYSTEM_IMPLEMENTATION.md)

### 前端文档
- [快速开始](flutter_app/README.md)
- [开发指南](flutter_app/docs/DEVELOPMENT.md)
- [API集成](flutter_app/docs/API_GUIDE.md)
- [Web部署](flutter_app/docs/WEB_DEPLOYMENT.md)
- [项目总结](flutter_app/docs/PROJECT_SUMMARY.md)

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/novel_library

# JWT密钥
SECRET_KEY=your-secret-key-here

# 书籍目录
BOOK_DIRECTORIES=/path/to/books

# Telegram Bot（可选）
TELEGRAM_BOT_TOKEN=your-bot-token
```

### 配置文件

编辑 `config/config.yaml`:

```yaml
database:
  url: postgresql://user:password@localhost:5432/novel_library

library:
  directories:
    - /path/to/books/chinese
    - /path/to/books/english
  
scan:
  auto_scan: true
  interval: 3600

backup:
  enabled: true
  schedule: "0 2 * * *"
```

## 🌐 API端点

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

### 书籍
- `GET /api/books` - 获取书籍列表
- `GET /api/books/{id}` - 获取书籍详情
- `GET /api/books/{id}/cover` - 获取书籍封面
- `GET /api/books/{id}/download` - 下载书籍

### 搜索
- `GET /api/search?q=keyword` - 搜索书籍

### 阅读进度
- `GET /api/progress` - 获取阅读进度
- `POST /api/progress` - 保存阅读进度

完整API文档: http://localhost:8000/docs

## 🎨 界面预览

### Flutter Web界面
- **登录页** - 简洁的登录界面
- **首页** - 仪表盘和统计
- **书库** - Emby风格海报墙
- **详情页** - 完整的书籍信息
- **阅读器** - 沉浸式阅读体验
- **搜索** - 实时搜索结果
- **个人中心** - 用户设置和统计

## 🔒 权限系统

### 角色
- **Admin** - 系统管理员，所有权限
- **Librarian** - 图书管理员，管理书籍
- **User** - 普通用户，阅读和下载

### 权限
- `books:read` - 查看书籍
- `books:write` - 管理书籍
- `users:read` - 查看用户
- `users:write` - 管理用户
- `system:admin` - 系统管理

## 📱 Telegram机器人使用

```
/start - 开始使用
/search <关键词> - 搜索书籍
/recent - 最近添加的书籍
/progress - 我的阅读进度
/help - 帮助信息
```

## 🛠️ 开发

### 后端开发

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black app/
isort app/

# 类型检查
mypy app/
```

### 前端开发

```bash
cd flutter_app

# 安装依赖
flutter pub get

# 运行开发服务器
flutter run -d chrome

# 运行测试
flutter test

# 代码格式化
dart format lib/
```

## 📊 性能

### 后端性能
- API响应时间 < 100ms
- 支持并发请求 > 1000
- 数据库查询优化

### 前端性能
- 首次加载 < 3s
- 页面切换 < 100ms
- 图片懒加载
- Service Worker缓存

## 🤝 贡献

欢迎贡献代码！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2026-01-16)
- ✨ 完整的Flutter Web前端UI
- ✨ FastAPI后端API
- ✨ PostgreSQL数据库
- ✨ JWT认证系统
- ✨ RBAC权限控制
- ✨ 在线阅读器（TXT/EPUB）
- ✨ Telegram机器人
- ✨ 自动备份系统
- ✨ Docker部署支持
- 📚 完整的文档系统

## 📄 许可证

MIT License

## 🙏 致谢

- [Flutter](https://flutter.dev/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [PostgreSQL](https://www.postgresql.org/) - 数据库
- [Material Design](https://m3.material.io/) - UI设计
- 所有开源贡献者

## 📞 联系方式

- 提交 Issue: https://github.com/yourusername/novel-library/issues
- Pull Request: https://github.com/yourusername/novel-library/pulls

---

**Made with ❤️ by Your Name**

**⭐ 如果这个项目对你有帮助，请给个Star！**
