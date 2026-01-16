import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';
import '../services/api_config.dart';
import '../services/storage_service.dart';

class ReaderScreen extends StatefulWidget {
  final int bookId;

  const ReaderScreen({super.key, required this.bookId});

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  late StorageService _storage;
  late ApiClient _apiClient;
  
  String? _bookTitle;
  String? _content;
  bool _isLoading = true;
  String? _errorMessage;
  
  // 阅读器设置
  double _fontSize = 18.0;
  double _lineHeight = 1.8;
  String _theme = 'dark'; // dark, light, sepia
  bool _showSettings = false;
  
  // 阅读进度
  final ScrollController _scrollController = ScrollController();
  double _scrollProgress = 0.0;
  int? _currentPosition;

  @override
  void initState() {
    super.initState();
    _initReader();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    _saveProgress();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.hasClients) {
      final maxScroll = _scrollController.position.maxScrollExtent;
      final currentScroll = _scrollController.offset;
      if (maxScroll > 0) {
        setState(() {
          _scrollProgress = currentScroll / maxScroll;
        });
        _currentPosition = currentScroll.toInt();
      }
    }
  }

  Future<void> _initReader() async {
    try {
      _storage = StorageService();
      await _storage.init();
      _apiClient = ApiClient(_storage);
      
      await _loadSettings();
      await _loadBookContent();
      await _loadProgress();
    } catch (e) {
      setState(() {
        _errorMessage = '初始化失败: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadSettings() async {
    // 从本地存储加载设置
    final savedFontSize = await _storage.getThemeMode();
    // 使用默认设置，后续可以扩展
  }

  Future<void> _loadBookContent() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 获取书籍信息
      final bookResponse = await _apiClient.get('/api/books/${widget.bookId}');
      if (bookResponse.statusCode == 200) {
        final bookData = bookResponse.data as Map<String, dynamic>;
        _bookTitle = bookData['title'] as String?;
      }
      
      // 获取内容
      final contentResponse = await _apiClient.get('/api/books/${widget.bookId}/content');
      if (contentResponse.statusCode == 200) {
        final data = contentResponse.data as Map<String, dynamic>;
        setState(() {
          _content = data['content'] as String?;
          _isLoading = false;
        });
      } else {
        throw Exception('无法加载内容');
      }
    } catch (e) {
      setState(() {
        _errorMessage = '加载失败: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadProgress() async {
    try {
      final response = await _apiClient.get('/api/progress/${widget.bookId}');
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final position = data['position'] as String?;
        if (position != null) {
          _currentPosition = int.tryParse(position);
          // 延迟恢复位置，等待内容渲染
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (_currentPosition != null && _scrollController.hasClients) {
              _scrollController.jumpTo(_currentPosition!.toDouble());
            }
          });
        }
      }
    } catch (e) {
      debugPrint('加载进度失败: $e');
    }
  }

  Future<void> _saveProgress() async {
    if (_currentPosition == null) return;
    
    try {
      await _apiClient.post('/api/progress/${widget.bookId}', data: {
        'progress': _scrollProgress,
        'position': _currentPosition.toString(),
        'finished': _scrollProgress >= 0.99,
      });
    } catch (e) {
      debugPrint('保存进度失败: $e');
    }
  }

  // 主题颜色
  Color get _backgroundColor {
    switch (_theme) {
      case 'light':
        return const Color(0xFFF5F5F5);
      case 'sepia':
        return const Color(0xFFFEFCE8);
      default:
        return const Color(0xFF101010);
    }
  }

  Color get _textColor {
    switch (_theme) {
      case 'light':
        return const Color(0xFF111827);
      case 'sepia':
        return const Color(0xFF713F12);
      default:
        return const Color(0xFFE5E5E5);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _backgroundColor,
      appBar: AppBar(
        backgroundColor: _backgroundColor,
        foregroundColor: _textColor,
        title: Text(
          _bookTitle ?? '阅读',
          style: TextStyle(color: _textColor),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            _saveProgress();
            Navigator.of(context).pop();
          },
        ),
        actions: [
          // 进度显示
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Text(
                '${(_scrollProgress * 100).toInt()}%',
                style: TextStyle(
                  color: _textColor.withOpacity(0.7),
                  fontSize: 14,
                ),
              ),
            ),
          ),
          // 设置按钮
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              setState(() {
                _showSettings = !_showSettings;
              });
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // 主要内容
          _isLoading
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: _textColor),
                      const SizedBox(height: 16),
                      Text('加载中...', style: TextStyle(color: _textColor)),
                    ],
                  ),
                )
              : _errorMessage != null
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
                          const SizedBox(height: 16),
                          Text(_errorMessage!, style: TextStyle(color: _textColor)),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: _loadBookContent,
                            child: const Text('重试'),
                          ),
                        ],
                      ),
                    )
                  : _buildReaderContent(),
          
          // 设置面板
          if (_showSettings) _buildSettingsPanel(),
          
          // 底部进度条
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: LinearProgressIndicator(
              value: _scrollProgress,
              backgroundColor: _backgroundColor,
              valueColor: AlwaysStoppedAnimation<Color>(
                Theme.of(context).primaryColor,
              ),
              minHeight: 3,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReaderContent() {
    if (_content == null) return const SizedBox();

    return SingleChildScrollView(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: SelectableText(
        _content!,
        style: TextStyle(
          color: _textColor,
          fontSize: _fontSize,
          height: _lineHeight,
        ),
      ),
    );
  }

  Widget _buildSettingsPanel() {
    return Positioned(
      top: 0,
      right: 0,
      child: Material(
        elevation: 8,
        color: _theme == 'dark' ? const Color(0xFF1A1A1A) : Colors.white,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(16),
        ),
        child: Container(
          width: 280,
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '阅读设置',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _textColor,
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.close, color: _textColor),
                    onPressed: () {
                      setState(() {
                        _showSettings = false;
                      });
                    },
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // 字体大小
              Text('字体大小', style: TextStyle(color: _textColor.withOpacity(0.7))),
              Row(
                children: [
                  IconButton(
                    icon: Icon(Icons.remove, color: _textColor),
                    onPressed: () {
                      if (_fontSize > 12) {
                        setState(() {
                          _fontSize -= 2;
                        });
                      }
                    },
                  ),
                  Expanded(
                    child: Slider(
                      value: _fontSize,
                      min: 12,
                      max: 28,
                      onChanged: (value) {
                        setState(() {
                          _fontSize = value;
                        });
                      },
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.add, color: _textColor),
                    onPressed: () {
                      if (_fontSize < 28) {
                        setState(() {
                          _fontSize += 2;
                        });
                      }
                    },
                  ),
                ],
              ),
              Text(
                '${_fontSize.toInt()}px',
                style: TextStyle(color: _textColor),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 16),
              
              // 行距
              Text('行距', style: TextStyle(color: _textColor.withOpacity(0.7))),
              Slider(
                value: _lineHeight,
                min: 1.2,
                max: 2.4,
                divisions: 6,
                label: _lineHeight.toStringAsFixed(1),
                onChanged: (value) {
                  setState(() {
                    _lineHeight = value;
                  });
                },
              ),
              
              const SizedBox(height: 16),
              
              // 主题
              Text('主题', style: TextStyle(color: _textColor.withOpacity(0.7))),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildThemeButton('dark', '深色', const Color(0xFF101010), Colors.white),
                  _buildThemeButton('light', '浅色', const Color(0xFFF5F5F5), Colors.black),
                  _buildThemeButton('sepia', '护眼', const Color(0xFFFEFCE8), const Color(0xFF713F12)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildThemeButton(String theme, String label, Color bg, Color fg) {
    final isSelected = _theme == theme;
    return GestureDetector(
      onTap: () {
        setState(() {
          _theme = theme;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(8),
          border: isSelected
              ? Border.all(color: Theme.of(context).primaryColor, width: 2)
              : Border.all(color: Colors.grey.withOpacity(0.3)),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: fg,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
