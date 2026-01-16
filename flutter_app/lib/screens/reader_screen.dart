import 'package:flutter/material.dart';
import '../services/api_config.dart';
import '../services/storage_service.dart';

// 条件导入以支持 Web
import 'reader_screen_stub.dart'
    if (dart.library.html) 'reader_screen_web.dart' as platform;

class ReaderScreen extends StatefulWidget {
  final int bookId;

  const ReaderScreen({super.key, required this.bookId});

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  late StorageService _storage;
  bool _isLoading = true;
  String? _errorMessage;
  bool _redirected = false;

  @override
  void initState() {
    super.initState();
    _initReader();
  }

  Future<void> _initReader() async {
    try {
      _storage = StorageService();
      await _storage.init();
      
      // 获取 token
      final token = await _storage.getToken();
      if (token == null) {
        setState(() {
          _errorMessage = '未登录，请先登录';
          _isLoading = false;
        });
        return;
      }

      // 直接重定向到后端阅读器页面
      final readerUrl = '${ApiConfig.baseUrl}/reader/${widget.bookId}?token=$token';
      platform.openUrl(readerUrl);
      
      setState(() {
        _isLoading = false;
        _redirected = true;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载阅读器失败: $e';
        _isLoading = false;
      });
    }
  }

  void _openInNewTab() async {
    final token = await _storage.getToken();
    if (token != null) {
      final url = '${ApiConfig.baseUrl}/reader/${widget.bookId}?token=$token';
      platform.openUrl(url);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('阅读器'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 64, color: Colors.red),
                      const SizedBox(height: 16),
                      Text(_errorMessage!),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _initReader,
                        child: const Text('重试'),
                      ),
                    ],
                  ),
                )
              : Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.auto_stories, size: 64, color: Colors.blue),
                      const SizedBox(height: 16),
                      const Text(
                        '阅读器已在新窗口打开',
                        style: TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '如果没有自动打开，请点击下方按钮',
                        style: TextStyle(color: Colors.grey[400]),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _openInNewTab,
                        icon: const Icon(Icons.open_in_new),
                        label: const Text('打开阅读器'),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('返回'),
                      ),
                    ],
                  ),
                ),
    );
  }
}
