# Flutter 小说书库 - 开发文档

## 目录

1. [项目概述](#项目概述)
2. [技术栈](#技术栈)
3. [项目结构](#项目结构)
4. [开发环境配置](#开发环境配置)
5. [核心功能实现](#核心功能实现)
6. [状态管理](#状态管理)
7. [API集成](#api集成)
8. [UI组件](#ui组件)
9. [路由导航](#路由导航)
10. [调试技巧](#调试技巧)
11. [构建发布](#构建发布)

## 项目概述

小说书库是一个基于Flutter开发的跨平台小说阅读应用，采用MVVM架构，提供完整的书籍浏览、搜索、阅读功能。

### 核心特性

- 🔐 完整的用户认证系统
- 📚 Emby风格的书库浏览
- 🔍 强大的搜索功能
- 📖 沉浸式阅读体验
- 🎨 Material Design 3 设计
- 🌓 深色主题支持
- 📱 跨平台支持

## 技术栈

### 核心框架
- **Flutter**: 3.x
- **Dart**: 3.x

### 状态管理
- **Provider**: 6.x - 简单高效的状态管理

### 网络请求
- **Dio**: 5.x - HTTP客户端
- **dio_cookie_manager**: Cookie管理

### 图片处理
- **cached_network_image**: 3.x - 图片缓存

### 路由导航
- **go_router**: 14.x - 声明式路由

### 本地存储
- **shared_preferences**: 2.x - 键值对存储

## 项目结构

```
lib/
├── main.dart                    # 应用入口
├── models/                      # 数据模型
│   ├── user.dart               # 用户模型
│   └── book.dart               # 书籍模型
├── services/                    # 服务层
│   ├── api_config.dart         # API配置
│   ├── api_client.dart         # HTTP客户端
│   ├── storage_service.dart    # 存储服务
│   ├── auth_service.dart       # 认证服务
│   └── book_service.dart       # 书籍服务
├── providers/                   # 状态管理
│   ├── auth_provider.dart      # 认证状态
│   ├── theme_provider.dart     # 主题状态
│   └── book_provider.dart      # 书籍状态
├── widgets/                     # 可复用组件
│   └── book_card.dart          # 书籍卡片
└── screens/                     # 页面
    ├── login_screen.dart       # 登录页
    ├── home_screen.dart        # 首页
    ├── library_screen.dart     # 书库页
    ├── book_detail_screen.dart # 详情页
    ├── search_screen.dart      # 搜索页
    ├── profile_screen.dart     # 个人中心
    └── reader_screen.dart      # 阅读器
```

## 开发环境配置

### 1. 安装Flutter SDK

```bash
# 下载Flutter SDK
# 访问 https://flutter.dev/docs/get-started/install

# 验证安装
flutter doctor
```

### 2. 克隆项目

```bash
cd novel-library/flutter_app
```

### 3. 安装依赖

```bash
flutter pub get
```

### 4. 配置API地址

编辑 `lib/services/api_config.dart`:

```dart
class ApiConfig {
  static const String baseUrl = 'http://your-server:8000';
  // ...
}
```

### 5. 运行项目

```bash
# Web版
flutter run -d chrome

# Windows桌面
flutter run -d windows

# Android
flutter run -d android
```

## 核心功能实现

### 1. 用户认证

#### 登录流程

```dart
// 1. 用户输入用户名密码
// 2. 调用AuthService.login()
// 3. 保存Token到SharedPreferences
// 4. 更新AuthProvider状态
// 5. 导航到首页
```

#### 代码示例

```dart
final authService = AuthService(apiClient);
final result = await authService.login(username, password);

if (result['success']) {
  final token = result['token'];
  await storage.saveToken(token);
  await storage.saveUser(result['user']);
  _currentUser = User.fromJson(result['user']);
  notifyListeners();
}
```

### 2. 书籍浏览

#### 分页加载

```dart
Future<void> loadBooks({bool refresh = false}) async {
  if (refresh) {
    _currentPage = 1;
    _books.clear();
  }

  final newBooks = await _bookService.getBooks(
    page: _currentPage,
    limit: 20,
  );

  _books.addAll(newBooks);
  _currentPage++;
  notifyListeners();
}
```

#### 无限滚动

```dart
_scrollController.addListener(() {
  if (_scrollController.position.pixels >=
      _scrollController.position.maxScrollExtent - 200) {
    context.read<BookProvider>().loadMore();
  }
});
```

### 3. 搜索功能

```dart
Future<void> _performSearch(String query) async {
  final result = await _bookService.searchBooks(
    query: query,
    page: 1,
    limit: 50,
  );

  setState(() {
    _searchResults = result['books'];
    _totalResults = result['total'];
  });
}
```

### 4. 阅读器

#### 沉浸式体验

```dart
@override
void initState() {
  super.initState();
  // 隐藏系统UI
  SystemChrome.setEnabledSystemUIMode(
    SystemUiMode.immersiveSticky,
  );
}

@override
void dispose() {
  // 恢复系统UI
  SystemChrome.setEnabledSystemUIMode(
    SystemUiMode.edgeToEdge,
  );
  super.dispose();
}
```

## 状态管理

### Provider模式

#### 1. 定义Provider

```dart
class BookProvider extends ChangeNotifier {
  List<Book> _books = [];
  bool _isLoading = false;

  List<Book> get books => _books;
  bool get isLoading => _isLoading;

  Future<void> loadBooks() async {
    _isLoading = true;
    notifyListeners();

    // 加载数据...

    _isLoading = false;
    notifyListeners();
  }
}
```

#### 2. 注册Provider

```dart
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => AuthProvider()),
    ChangeNotifierProvider(create: (_) => BookProvider()),
  ],
  child: MyApp(),
)
```

#### 3. 使用Provider

```dart
// 读取状态
Consumer<BookProvider>(
  builder: (context, bookProvider, child) {
    return Text('${bookProvider.books.length} 本书');
  },
)

// 调用方法
context.read<BookProvider>().loadBooks();
```

## API集成

### Dio配置

```dart
class ApiClient {
  late final Dio _dio;

  ApiClient(StorageService storage) {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));

    // 请求拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));
  }
}
```

### API调用示例

```dart
// GET请求
Future<List<Book>> getBooks({int page = 1, int limit = 20}) async {
  final response = await _apiClient.get(
    '/books',
    queryParameters: {'page': page, 'limit': limit},
  );
  
  return (response.data as List)
      .map((json) => Book.fromJson(json))
      .toList();
}

// POST请求
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await _apiClient.post(
    '/auth/login',
    data: {'username': username, 'password': password},
  );
  
  return response.data;
}
```

## UI组件

### 自定义书籍卡片

```dart
class BookCard extends StatelessWidget {
  final Book book;
  final String coverUrl;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Column(
          children: [
            // 封面
            CachedNetworkImage(
              imageUrl: coverUrl,
              fit: BoxFit.cover,
            ),
            // 信息
            Text(book.title),
            Text(book.authorName ?? '未知作者'),
          ],
        ),
      ),
    );
  }
}
```

### 主题配置

```dart
class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.dark;

  ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF00A4DC),
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: const Color(0xFF0F0F0F),
  );
}
```

## 路由导航

### go_router配置

```dart
GoRouter _router() {
  return GoRouter(
    initialLocation: '/home',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/books/:id',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return BookDetailScreen(bookId: id);
        },
      ),
    ],
  );
}
```

### 导航方法

```dart
// 跳转
context.push('/books/123');
context.go('/home');

// 返回
context.pop();

// 替换
context.replace('/login');
```

## 调试技巧

### 1. 调试输出

```dart
import 'package:flutter/foundation.dart';

if (kDebugMode) {
  print('Debug: $variable');
}
```

### 2. 断点调试

```dart
// 在VS Code或Android Studio中设置断点
debugger(); // 强制暂停
```

### 3. Widget Inspector

```bash
# 运行应用后按
# d - 切换调试信息
# i - Widget Inspector
# p - 显示网格
```

### 4. 性能分析

```bash
flutter run --profile
# 然后打开 DevTools
flutter pub global activate devtools
flutter pub global run devtools
```

## 构建发布

### Web版

```bash
flutter build web --release

# 输出目录: build/web
```

### Windows桌面

```bash
flutter build windows --release

# 输出目录: build/windows/runner/Release
```

### Android APK

```bash
flutter build apk --release

# 输出: build/app/outputs/flutter-apk/app-release.apk
```

### iOS

```bash
flutter build ios --release

# 需要在Xcode中配置签名
```

## 最佳实践

### 1. 代码组织

- 保持文件小而专注
- 使用清晰的命名
- 遵循Dart风格指南

### 2. 状态管理

- 避免过度使用全局状态
- 合理划分Provider
- 及时dispose资源

### 3. 性能优化

- 使用const构造函数
- 避免不必要的rebuild
- 图片使用缓存
- 列表使用虚拟滚动

### 4. 错误处理

- 使用try-catch捕获异常
- 提供友好的错误提示
- 记录错误日志

## 常见问题

### 1. Hot Reload不工作

```bash
# 尝试Hot Restart
flutter run --hot
# 按 R 键重启
```

### 2. 依赖冲突

```bash
flutter pub upgrade
flutter pub get
```

### 3. 构建错误

```bash
flutter clean
flutter pub get
flutter run
```

## 参考资源

- [Flutter官方文档](https://flutter.dev/docs)
- [Dart语言指南](https://dart.dev/guides)
- [Provider文档](https://pub.dev/packages/provider)
- [Dio文档](https://pub.dev/packages/dio)
- [Material Design](https://m3.material.io/)

## 联系方式

如有问题，请提交Issue或Pull Request。
