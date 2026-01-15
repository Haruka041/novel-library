# API 集成指南

## 概述

本文档详细说明Flutter应用如何与后端API进行交互。

## API基础配置

### 配置文件

`lib/services/api_config.dart`:

```dart
class ApiConfig {
  // 基础URL - 根据环境修改
  static const String baseUrl = 'http://localhost:8000';
  
  // API端点
  static const String loginEndpoint = '/api/auth/login';
  static const String logoutEndpoint = '/api/auth/logout';
  static const String userInfoEndpoint = '/api/user/me';
  static const String booksEndpoint = '/api/books';
  static const String searchEndpoint = '/api/search';
}
```

### 环境配置

开发环境、测试环境和生产环境的配置：

```dart
enum Environment { development, staging, production }

class ApiConfig {
  static Environment currentEnv = Environment.development;
  
  static String get baseUrl {
    switch (currentEnv) {
      case Environment.development:
        return 'http://localhost:8000';
      case Environment.staging:
        return 'https://staging.example.com';
      case Environment.production:
        return 'https://api.example.com';
    }
  }
}
```

## 认证流程

### 1. 登录

**端点**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true
  }
}
```

**Flutter实现**:
```dart
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await _apiClient.post(
    ApiConfig.loginEndpoint,
    data: {
      'username': username,
      'password': password,
    },
  );
  
  if (response.statusCode == 200) {
    final data = response.data as Map<String, dynamic>;
    
    // 保存Token
    await _storage.saveToken(data['token']);
    
    // 保存用户信息
    await _storage.saveUser(json.encode(data['user']));
    
    return data;
  }
  
  throw Exception('登录失败');
}
```

### 2. Token管理

Token自动添加到请求头：

```dart
_dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) async {
    final token = await storage.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return handler.next(options);
  },
));
```

### 3. Token刷新

```dart
_dio.interceptors.add(InterceptorsWrapper(
  onError: (DioException error, handler) async {
    if (error.response?.statusCode == 401) {
      // Token过期，退出登录
      await authProvider.logout();
      // 导航到登录页
    }
    return handler.next(error);
  },
));
```

## 书籍API

### 1. 获取书籍列表

**端点**: `GET /api/books`

**查询参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `author_id`: 作者ID（可选）
- `library_id`: 书库ID（可选）

**响应**:
```json
[
  {
    "id": 1,
    "title": "书籍标题",
    "author_id": 1,
    "author_name": "作者名",
    "file_path": "/path/to/book.epub",
    "file_format": "epub",
    "file_size": 1024000,
    "description": "简介",
    "tags": ["标签1", "标签2"],
    "age_rating": "general",
    "content_warning": [],
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**Flutter实现**:
```dart
Future<List<Book>> getBooks({
  int page = 1,
  int limit = 20,
  int? authorId,
  int? libraryId,
}) async {
  final response = await _apiClient.get(
    ApiConfig.booksEndpoint,
    queryParameters: {
      'page': page,
      'limit': limit,
      if (authorId != null) 'author_id': authorId,
      if (libraryId != null) 'library_id': libraryId,
    },
  );

  if (response.statusCode == 200) {
    final List<dynamic> data = response.data as List<dynamic>;
    return data.map((json) => Book.fromJson(json)).toList();
  }

  throw Exception('获取书籍列表失败');
}
```

### 2. 获取书籍详情

**端点**: `GET /api/books/{id}`

**响应**: 同上，返回单个书籍对象

**Flutter实现**:
```dart
Future<Book> getBookDetail(int bookId) async {
  final response = await _apiClient.get(
    '${ApiConfig.booksEndpoint}/$bookId',
  );

  if (response.statusCode == 200) {
    return Book.fromJson(response.data);
  }

  throw Exception('获取书籍详情失败');
}
```

### 3. 搜索书籍

**端点**: `GET /api/search`

**查询参数**:
- `q`: 搜索关键词（必需）
- `page`: 页码
- `limit`: 每页数量
- `author_id`: 作者ID
- `formats`: 格式过滤
- `library_id`: 书库ID

**响应**:
```json
{
  "books": [...],
  "total": 100,
  "page": 1,
  "total_pages": 5
}
```

**Flutter实现**:
```dart
Future<Map<String, dynamic>> searchBooks({
  required String query,
  int page = 1,
  int limit = 20,
}) async {
  final response = await _apiClient.get(
    ApiConfig.searchEndpoint,
    queryParameters: {
      'q': query,
      'page': page,
      'limit': limit,
    },
  );

  if (response.statusCode == 200) {
    final data = response.data as Map<String, dynamic>;
    final List<dynamic> booksJson = data['books'];
    
    return {
      'books': booksJson.map((json) => Book.fromJson(json)).toList(),
      'total': data['total'],
      'page': data['page'],
      'total_pages': data['total_pages'],
    };
  }

  throw Exception('搜索失败');
}
```

### 4. 获取书籍封面

**端点**: `GET /api/books/{id}/cover`

**查询参数**:
- `size`: 封面尺寸（thumbnail/medium/large）

**Flutter实现**:
```dart
String getCoverUrl(int bookId, {String size = 'thumbnail'}) {
  return '${ApiConfig.baseUrl}/books/$bookId/cover?size=$size';
}

// 使用CachedNetworkImage显示
CachedNetworkImage(
  imageUrl: getCoverUrl(book.id),
  httpHeaders: {
    'Authorization': 'Bearer $token',
  },
)
```

### 5. 下载书籍

**端点**: `GET /api/books/{id}/download`

**Flutter实现**:
```dart
String getDownloadUrl(int bookId) {
  return '${ApiConfig.baseUrl}/books/$bookId/download';
}

// 使用url_launcher或dio下载
Future<void> downloadBook(int bookId) async {
  final url = getDownloadUrl(bookId);
  final token = await _storage.getToken();
  
  await _dio.download(
    url,
    savePath,
    options: Options(
      headers: {'Authorization': 'Bearer $token'},
    ),
  );
}
```

## 错误处理

### 统一错误处理

```dart
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

// 在拦截器中处理
_dio.interceptors.add(InterceptorsWrapper(
  onError: (DioException error, handler) {
    String message = '网络错误';
    
    if (error.response != null) {
      switch (error.response!.statusCode) {
        case 400:
          message = '请求参数错误';
          break;
        case 401:
          message = '未授权，请重新登录';
          break;
        case 403:
          message = '无权访问';
          break;
        case 404:
          message = '资源不存在';
          break;
        case 500:
          message = '服务器错误';
          break;
      }
    } else if (error.type == DioExceptionType.connectionTimeout) {
      message = '连接超时';
    } else if (error.type == DioExceptionType.receiveTimeout) {
      message = '响应超时';
    }
    
    return handler.reject(
      DioException(
        requestOptions: error.requestOptions,
        error: ApiException(message, error.response?.statusCode),
      ),
    );
  },
));
```

### 在UI中处理错误

```dart
try {
  await bookProvider.loadBooks();
} on ApiException catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(e.message)),
  );
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('未知错误')),
  );
}
```

## 请求/响应日志

### 开发环境日志

```dart
if (kDebugMode) {
  _dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (obj) => debugPrint(obj.toString()),
  ));
}
```

## 性能优化

### 1. 请求缓存

```dart
import 'package:dio_cache_interceptor/dio_cache_interceptor.dart';

final cacheOptions = CacheOptions(
  store: MemCacheStore(),
  maxStale: const Duration(days: 7),
);

_dio.interceptors.add(DioCacheInterceptor(options: cacheOptions));
```

### 2. 请求取消

```dart
final cancelToken = CancelToken();

Future<void> loadBooks() async {
  try {
    await _apiClient.get(
      '/books',
      cancelToken: cancelToken,
    );
  } catch (e) {
    if (CancelToken.isCancel(e)) {
      print('请求已取消');
    }
  }
}

@override
void dispose() {
  cancelToken.cancel('页面已关闭');
  super.dispose();
}
```

### 3. 并发请求

```dart
Future<void> loadMultipleData() async {
  final results = await Future.wait([
    bookService.getBooks(),
    bookService.getPopularBooks(),
    bookService.getRecentBooks(),
  ]);
  
  final books = results[0];
  final popular = results[1];
  final recent = results[2];
}
```

## 测试

### Mock API响应

```dart
class MockApiClient extends ApiClient {
  @override
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    // 返回mock数据
    return Response(
      requestOptions: RequestOptions(path: path),
      data: {'books': []},
      statusCode: 200,
    );
  }
}

// 在测试中使用
final mockClient = MockApiClient();
final bookService = BookService(mockClient);
```

## 安全建议

1. **永远不要在代码中硬编码敏感信息**
2. **使用HTTPS进行生产环境通信**
3. **验证SSL证书**
4. **定期更新Token**
5. **实现请求签名（如果需要）**

## API版本控制

```dart
class ApiConfig {
  static const String apiVersion = 'v1';
  static String get baseUrl => 'http://localhost:8000/api/$apiVersion';
}
```

## 常见问题

### Q: 为什么我的请求返回401？
A: Token可能已过期或无效。检查Token是否正确保存和发送。

### Q: 如何处理大文件上传？
A: 使用MultipartFile和进度回调：
```dart
final formData = FormData.fromMap({
  'file': await MultipartFile.fromFile(filePath),
});

await _dio.post(
  '/upload',
  data: formData,
  onSendProgress: (sent, total) {
    print('${(sent / total * 100).toStringAsFixed(0)}%');
  },
);
```

### Q: 如何实现离线支持？
A: 使用dio_cache_interceptor缓存响应，并在无网络时读取缓存。

## 相关资源

- [Dio文档](https://pub.dev/packages/dio)
- [后端API文档](../README.md)
- [开发文档](./DEVELOPMENT.md)
