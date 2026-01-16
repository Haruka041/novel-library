import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import '../services/api_client.dart';
import '../services/storage_service.dart';

/// 章节信息
class Chapter {
  final String title;
  final int startIndex;
  
  Chapter({required this.title, required this.startIndex});
}

class ReaderScreen extends StatefulWidget {
  final int bookId;

  const ReaderScreen({super.key, required this.bookId});

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> with WidgetsBindingObserver {
  late StorageService _storage;
  late ApiClient _apiClient;
  
  String? _bookTitle;
  String? _content;
  bool _isLoading = true;
  bool _isRestoringProgress = false;
  String? _errorMessage;
  
  // 阅读器设置
  double _fontSize = 18.0;
  double _lineHeight = 1.8;
  String _theme = 'dark';
  String _fontFamily = 'default';
  bool _showSettings = false;
  bool _showChapters = false;
  
  // 章节目录
  List<Chapter> _chapters = [];
  int _currentChapterIndex = 0;
  
  // 自动滚动
  bool _autoScrollEnabled = false;
  int _scrollSpeed = 5; // 1-10
  Timer? _autoScrollTimer;
  
  // 阅读进度
  final ScrollController _scrollController = ScrollController();
  double _scrollProgress = 0.0;
  int? _currentPosition;
  int? _savedPosition;
  bool _progressRestored = false;
  
  // 保存进度防抖
  Timer? _saveProgressDebounce;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initReader();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    _autoScrollTimer?.cancel();
    _saveProgressDebounce?.cancel();
    _saveProgress();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused) {
      _saveProgress();
      _saveSettings();
    }
  }

  void _onScroll() {
    if (_scrollController.hasClients) {
      final maxScroll = _scrollController.position.maxScrollExtent;
      final currentScroll = _scrollController.offset;
      if (maxScroll > 0) {
        final newProgress = currentScroll / maxScroll;
        if ((newProgress - _scrollProgress).abs() > 0.001) {
          setState(() {
            _scrollProgress = newProgress;
          });
        }
        _currentPosition = currentScroll.toInt();
        
        // 更新当前章节
        _updateCurrentChapter(currentScroll.toInt());
        
        // 防抖保存进度
        _saveProgressDebounce?.cancel();
        _saveProgressDebounce = Timer(const Duration(seconds: 2), _saveProgress);
      }
    }
  }

  void _updateCurrentChapter(int position) {
    if (_chapters.isEmpty) return;
    
    for (int i = _chapters.length - 1; i >= 0; i--) {
      if (position >= _chapters[i].startIndex) {
        if (_currentChapterIndex != i) {
          setState(() {
            _currentChapterIndex = i;
          });
        }
        break;
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
    final settings = await _storage.loadAllReaderSettings();
    setState(() {
      _fontSize = settings['fontSize'] as double;
      _lineHeight = settings['lineHeight'] as double;
      _theme = settings['theme'] as String;
      _fontFamily = settings['fontFamily'] as String;
      _autoScrollEnabled = settings['autoScroll'] as bool;
      _scrollSpeed = settings['scrollSpeed'] as int;
    });
  }

  Future<void> _saveSettings() async {
    await _storage.saveAllReaderSettings(
      fontSize: _fontSize,
      lineHeight: _lineHeight,
      theme: _theme,
      fontFamily: _fontFamily,
      autoScroll: _autoScrollEnabled,
      scrollSpeed: _scrollSpeed,
    );
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
      final contentResponse = await _apiClient.get('/books/${widget.bookId}/content');
      if (contentResponse.statusCode == 200) {
        final data = contentResponse.data as Map<String, dynamic>;
        final content = data['content'] as String?;
        
        // 解析章节
        if (content != null) {
          _parseChapters(content);
        }
        
        setState(() {
          _content = content;
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

  void _parseChapters(String content) {
    final chapters = <Chapter>[];
    
    // 章节识别正则
    final patterns = [
      RegExp(r'^第[一二三四五六七八九十百千万零0-9]+[章节卷部回集篇].*', multiLine: true),
      RegExp(r'^Chapter\s+\d+.*', multiLine: true, caseSensitive: false),
      RegExp(r'^\d+[\.、]\s*.+', multiLine: true),
    ];
    
    for (final pattern in patterns) {
      final matches = pattern.allMatches(content);
      for (final match in matches) {
        chapters.add(Chapter(
          title: match.group(0)!.trim(),
          startIndex: match.start,
        ));
      }
      if (chapters.isNotEmpty) break;
    }
    
    // 按位置排序
    chapters.sort((a, b) => a.startIndex.compareTo(b.startIndex));
    
    // 如果没有找到章节，创建一个默认章节
    if (chapters.isEmpty) {
      chapters.add(Chapter(title: '正文', startIndex: 0));
    }
    
    _chapters = chapters;
  }

  Future<void> _loadProgress() async {
    try {
      final response = await _apiClient.get('/api/progress/${widget.bookId}');
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final position = data['position'] as String?;
        if (position != null) {
          _savedPosition = int.tryParse(position);
          if (_savedPosition != null && _savedPosition! > 0) {
            // 显示恢复进度确认
            _showRestoreProgressDialog();
          }
        }
      }
    } catch (e) {
      debugPrint('加载进度失败: $e');
    }
  }

  void _showRestoreProgressDialog() {
    if (!mounted) return;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('继续阅读'),
        content: Text('检测到上次阅读进度 (${(_savedPosition! / 1000).toStringAsFixed(1)}k 字符处)，是否恢复？'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _progressRestored = true;
            },
            child: const Text('从头开始'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              _restoreProgress();
            },
            child: const Text('继续阅读'),
          ),
        ],
      ),
    );
  }

  void _restoreProgress() {
    if (_savedPosition == null || !_scrollController.hasClients) {
      // 延迟重试
      SchedulerBinding.instance.addPostFrameCallback((_) {
        Future.delayed(const Duration(milliseconds: 200), () {
          if (mounted && _savedPosition != null) {
            _restoreProgress();
          }
        });
      });
      return;
    }
    
    setState(() {
      _isRestoringProgress = true;
    });
    
    // 等待内容渲染后跳转
    SchedulerBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients && _savedPosition != null) {
        final maxScroll = _scrollController.position.maxScrollExtent;
        final targetPosition = _savedPosition!.toDouble().clamp(0.0, maxScroll);
        
        _scrollController.jumpTo(targetPosition);
        
        setState(() {
          _isRestoringProgress = false;
          _progressRestored = true;
        });
        
        // 显示提示
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('已恢复到上次阅读位置'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    });
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

  void _jumpToChapter(Chapter chapter) {
    if (!_scrollController.hasClients || _content == null) return;
    
    // 计算大概的滚动位置（基于字符索引估算）
    final totalLength = _content!.length;
    final maxScroll = _scrollController.position.maxScrollExtent;
    final estimatedPosition = (chapter.startIndex / totalLength) * maxScroll;
    
    _scrollController.animateTo(
      estimatedPosition.clamp(0.0, maxScroll),
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
    
    setState(() {
      _showChapters = false;
    });
  }

  // 自动滚动
  void _toggleAutoScroll() {
    setState(() {
      _autoScrollEnabled = !_autoScrollEnabled;
    });
    
    if (_autoScrollEnabled) {
      _startAutoScroll();
    } else {
      _stopAutoScroll();
    }
  }

  void _startAutoScroll() {
    _autoScrollTimer?.cancel();
    
    // 每50ms滚动一次
    _autoScrollTimer = Timer.periodic(const Duration(milliseconds: 50), (_) {
      if (_scrollController.hasClients && _autoScrollEnabled) {
        final maxScroll = _scrollController.position.maxScrollExtent;
        final currentScroll = _scrollController.offset;
        
        if (currentScroll < maxScroll) {
          // 速度映射：1-10 -> 0.5-5.0 像素/50ms
          final speed = 0.5 + (_scrollSpeed - 1) * 0.5;
          _scrollController.jumpTo(currentScroll + speed);
        } else {
          // 到达底部，停止滚动
          _toggleAutoScroll();
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('已到达底部')),
          );
        }
      }
    });
  }

  void _stopAutoScroll() {
    _autoScrollTimer?.cancel();
    _autoScrollTimer = null;
  }

  // 主题颜色
  Color get _backgroundColor {
    switch (_theme) {
      case 'light':
        return const Color(0xFFF5F5F5);
      case 'sepia':
        return const Color(0xFFFEFCE8);
      case 'green':
        return const Color(0xFFE8F5E9);
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
      case 'green':
        return const Color(0xFF1B5E20);
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
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _bookTitle ?? '阅读',
              style: TextStyle(color: _textColor, fontSize: 16),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (_chapters.isNotEmpty)
              Text(
                _chapters[_currentChapterIndex].title,
                style: TextStyle(
                  color: _textColor.withOpacity(0.6),
                  fontSize: 12,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            _saveProgress();
            _saveSettings();
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
          // 目录按钮
          IconButton(
            icon: const Icon(Icons.list),
            tooltip: '目录',
            onPressed: () {
              setState(() {
                _showChapters = !_showChapters;
                _showSettings = false;
              });
            },
          ),
          // 自动滚动按钮
          IconButton(
            icon: Icon(_autoScrollEnabled ? Icons.pause : Icons.play_arrow),
            tooltip: _autoScrollEnabled ? '停止自动滚动' : '自动滚动',
            onPressed: _toggleAutoScroll,
          ),
          // 设置按钮
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: '阅读设置',
            onPressed: () {
              setState(() {
                _showSettings = !_showSettings;
                _showChapters = false;
              });
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // 主要内容
          _buildMainContent(),
          
          // 章节目录面板
          if (_showChapters) _buildChaptersPanel(),
          
          // 设置面板
          if (_showSettings) _buildSettingsPanel(),
          
          // 进度恢复中指示器
          if (_isRestoringProgress)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('恢复阅读进度...', style: TextStyle(color: Colors.white)),
                  ],
                ),
              ),
            ),
          
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

  Widget _buildMainContent() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: _textColor),
            const SizedBox(height: 16),
            Text('加载中...', style: TextStyle(color: _textColor)),
          ],
        ),
      );
    }
    
    if (_errorMessage != null) {
      return Center(
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
      );
    }
    
    return _buildReaderContent();
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
          fontFamily: _fontFamily == 'default' ? null : _fontFamily,
        ),
      ),
    );
  }

  Widget _buildChaptersPanel() {
    return Positioned(
      top: 0,
      left: 0,
      bottom: 0,
      child: Material(
        elevation: 8,
        color: _theme == 'dark' ? const Color(0xFF1A1A1A) : Colors.white,
        child: SizedBox(
          width: 280,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '目录 (${_chapters.length}章)',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: _textColor,
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.close, color: _textColor),
                      onPressed: () => setState(() => _showChapters = false),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView.builder(
                  itemCount: _chapters.length,
                  itemBuilder: (context, index) {
                    final chapter = _chapters[index];
                    final isCurrentChapter = index == _currentChapterIndex;
                    
                    return ListTile(
                      title: Text(
                        chapter.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: isCurrentChapter 
                            ? Theme.of(context).primaryColor 
                            : _textColor,
                          fontWeight: isCurrentChapter 
                            ? FontWeight.bold 
                            : FontWeight.normal,
                        ),
                      ),
                      leading: isCurrentChapter 
                        ? Icon(Icons.bookmark, color: Theme.of(context).primaryColor)
                        : Icon(Icons.bookmark_border, color: _textColor.withOpacity(0.5)),
                      onTap: () => _jumpToChapter(chapter),
                    );
                  },
                ),
              ),
            ],
          ),
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
          width: 300,
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
                      setState(() => _showSettings = false);
                      _saveSettings();
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
                        setState(() => _fontSize -= 2);
                      }
                    },
                  ),
                  Expanded(
                    child: Slider(
                      value: _fontSize,
                      min: 12,
                      max: 32,
                      divisions: 10,
                      label: '${_fontSize.toInt()}px',
                      onChanged: (value) {
                        setState(() => _fontSize = value);
                      },
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.add, color: _textColor),
                    onPressed: () {
                      if (_fontSize < 32) {
                        setState(() => _fontSize += 2);
                      }
                    },
                  ),
                ],
              ),
              Center(
                child: Text(
                  '${_fontSize.toInt()}px',
                  style: TextStyle(color: _textColor),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 行距
              Text('行距', style: TextStyle(color: _textColor.withOpacity(0.7))),
              Slider(
                value: _lineHeight,
                min: 1.2,
                max: 2.5,
                divisions: 13,
                label: _lineHeight.toStringAsFixed(1),
                onChanged: (value) {
                  setState(() => _lineHeight = value);
                },
              ),
              
              const SizedBox(height: 16),
              
              // 主题
              Text('阅读主题', style: TextStyle(color: _textColor.withOpacity(0.7))),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildThemeButton('dark', '深色', const Color(0xFF101010), Colors.white),
                  _buildThemeButton('light', '浅色', const Color(0xFFF5F5F5), Colors.black),
                  _buildThemeButton('sepia', '护眼', const Color(0xFFFEFCE8), const Color(0xFF713F12)),
                  _buildThemeButton('green', '绿色', const Color(0xFFE8F5E9), const Color(0xFF1B5E20)),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // 自动滚动速度
              Text('自动滚动速度', style: TextStyle(color: _textColor.withOpacity(0.7))),
              Slider(
                value: _scrollSpeed.toDouble(),
                min: 1,
                max: 10,
                divisions: 9,
                label: '$_scrollSpeed',
                onChanged: (value) {
                  setState(() => _scrollSpeed = value.toInt());
                  if (_autoScrollEnabled) {
                    _stopAutoScroll();
                    _startAutoScroll();
                  }
                },
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
        setState(() => _theme = theme);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
