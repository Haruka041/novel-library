# 小说书库 Flutter 客户端

基于 Flutter 的跨平台客户端应用，支持 Web、iOS、Android 和 Desktop。

## 项目状态

**当前阶段**：第一阶段 - 项目初始化（已开始）

已完成：
- ✅ 项目配置（pubspec.yaml）
- ✅ 主入口文件（main.dart）
- ✅ API配置（api_config.dart）
- ✅ 路由配置（使用 go_router）

## 技术栈

- **框架**: Flutter 3.x
- **状态管理**: Provider
- **路由**: go_router
- **网络请求**: Dio + HTTP
- **本地存储**: shared_preferences
- **图片缓存**: cached_network_image

## 项目结构

```
flutter_app/
├── lib/
│   ├── main.dart                 # 应用入口
│   ├── models/                   # 数据模型
│   │   ├── book.dart
│   │   ├── user.dart
│   │   ├── library.dart
│   │   └── ...
│   ├── providers/                # 状态管理
│   │   ├── auth_provider.dart   # 认证状态
│   │   ├── theme_provider.dart  # 主题状态
│   │   ├── book_provider.dart   # 书籍状态
│   │   └── ...
│   ├── services/                 # 服务层
│   │   ├── api_config.dart      # API配置 ✅
│   │   ├── api_client.dart      # HTTP客户端
│   │   ├── auth_service.dart    # 认证服务
│   │   ├── book_service.dart    # 书籍服务
│   │   └── storage_service.dart # 本地存储
│   ├── screens/                  # 页面
│   │   ├── login_screen.dart    # 登录页
│   │   ├── home_screen.dart     # 首页
│   │   ├── library_screen.dart  # 书库页
│   │   ├── book_detail_screen.dart
│   │   ├── reader_screen.dart
│   │   ├── search_screen.dart
│   │   └── profile_screen.dart
│   ├── widgets/                  # 通用组件
│   │   ├── book_card.dart
│   │   ├── book_grid.dart
│   │   ├── custom_app_bar.dart
│   │   └── ...
│   └── utils/                    # 工具类
│       ├── constants.dart
│       ├── formatters.dart
│       └── validators.dart
├── pubspec.yaml                  # 项目配置 ✅
├── analysis_options.yaml         # 代码分析配置
└── README.md                     # 本文件 ✅
```

## 后续开发步骤

### 第一阶段：基础框架（当前）

需要创建的文件：

1. **数据模型** (lib/models/)
   - [ ] user.dart - 用户模型
   - [ ] book.dart - 书籍模型
   - [ ] library.dart - 书库模型
   - [ ] author.dart - 作者模型
   - [ ] tag.dart - 标签模型

2. **服务层** (lib/services/)
   - [ ] api_client.dart - HTTP客户端封装
   - [ ] auth_service.dart - 认证服务
   - [ ] book_service.dart - 书籍服务
   - [ ] storage_service.dart - 本地存储服务

3. **状态管理** (lib/providers/)
   - [ ] auth_provider.dart - 认证状态管理
   - [ ] theme_provider.dart - 主题状态管理
   - [ ] book_provider.dart - 书籍状态管理

4. **登录页面** (lib/screens/)
   - [ ] login_screen.dart - 登录界面
   - [ ] 表单验证
   - [ ] 错误处理
   - [ ] 自动登录

5. **主框架** (lib/screens/)
   - [ ] home_screen.dart - 首页框架
   - [ ] 底部导航栏
   - [ ] 侧边抽屉菜单

### 第二阶段：核心功能

1. **首页仪表盘** (Emby风格)
   - 统计卡片
   - 最近阅读
   - 最新添加
   - 推荐书籍

2. **书库浏览**
   - 海报墙布局
   - 网格/列表切换
   - 封面图片加载
   - 下拉刷新

3. **书籍详情**
   - 详情展示
   - 操作按钮
   - 标签显示
   - 进度显示

4. **阅读器**
   - TXT阅读器
   - EPUB阅读器
   - 阅读设置
   - 进度同步

### 第三阶段：用户功能

1. 搜索功能
2. 个人中心
3. 收藏管理
4. 设置页面

## 开发环境设置

### 1. 安装 Flutter SDK

访问 [Flutter官网](https://flutter.dev/docs/get-started/install) 下载并安装Flutter SDK。

### 2. 安装依赖

```bash
cd novel-library/flutter_app
flutter pub get
```

### 3. 运行应用

```bash
# Web
flutter run -d chrome

# iOS
flutter run -d ios

# Android
flutter run -d android

# Desktop (Windows)
flutter run -d windows
```

### 4. 构建发布版本

```bash
# Web
flutter build web

# iOS
flutter build ios

# Android
flutter build apk

# Windows
flutter build windows
```

## API集成

后端API地址配置在 `lib/services/api_config.dart`：

```dart
static const String baseUrl = 'http://localhost:8080';
```

部署时需要修改为实际的服务器地址。

## 可用的后端API端点

后端已完成的API端点（后端完成度：85%）：

### 认证
- POST /api/auth/login - 用户登录
- GET /api/auth/me - 获取当前用户

### 书籍
- GET /api/books - 书籍列表
- GET /api/books/{id} - 书籍详情
- GET /api/search - 搜索书籍
- GET /books/{id}/cover - 书籍封面
- GET /books/{id}/download - 下载书籍

### 书库
- GET /api/libraries - 书库列表
- GET /api/my-libraries - 我的书库

### 作者
- GET /api/authors - 作者列表

### 阅读进度
- GET /api/progress/{book_id} - 获取进度
- POST /api/progress/{book_id} - 更新进度

### 收藏
- GET /api/user/favorites - 收藏列表
- POST /api/user/favorites/{book_id} - 添加收藏
- DELETE /api/user/favorites/{book_id} - 取消收藏
- GET /api/user/favorites/{book_id}/check - 检查收藏状态

### 标签
- GET /api/tags - 系统标签
- GET /api/books/{book_id}/tags - 书籍标签
- GET /api/user/my-tags - 个人标签
- POST /api/user/my-tags/{book_id} - 添加个人标签
- DELETE /api/user/my-tags/{tag_id} - 删除个人标签

### OPDS
- GET /opds - OPDS根目录
- GET /opds/recent - 最新书籍
- GET /opds/authors - 作者列表
- GET /opds/search - OPDS搜索

## 设计参考

UI设计参考 Emby/Jellyfin 媒体库风格：
- 深色主题为主
- 海报墙布局
- 卡片式设计
- 流畅的动画效果

## 相关文档

- 后端API文档：`../docs/`
- Flutter开发计划：`../../plans/flutter-ui-development.md`
- 项目完成报告：`../../plans/project-completion-report.md`

## 下一步

1. 安装Flutter SDK（如果尚未安装）
2. 创建数据模型文件
3. 创建API客户端和服务
4. 实现认证Provider
5. 创建登录页面
6. 创建主框架页面

详细的开发步骤和时间表见 `plans/flutter-ui-development.md`。
