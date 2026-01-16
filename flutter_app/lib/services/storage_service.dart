import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/user.dart';
import 'api_config.dart';

class StorageService {
  SharedPreferences? _prefs;
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    
    debugPrint('💾 StorageService: Initializing...');
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
    debugPrint('💾 StorageService: Initialized successfully');
    
    // 调试：打印当前存储的数据
    if (kDebugMode) {
      final token = _prefs?.getString(ApiConfig.tokenKey);
      debugPrint('💾 StorageService: Token present: ${token != null && token.isNotEmpty}');
    }
  }

  // Token管理
  Future<void> saveToken(String token) async {
    debugPrint('💾 StorageService: Saving token (${token.length} chars)');
    await _prefs?.setString(ApiConfig.tokenKey, token);
  }

  Future<String?> getToken() async {
    if (_prefs == null) {
      debugPrint('⚠️ StorageService: getToken called before init!');
      return null;
    }
    final token = _prefs?.getString(ApiConfig.tokenKey);
    debugPrint('💾 StorageService: getToken returns ${token != null ? "token (${token.length} chars)" : "null"}');
    return token;
  }

  Future<void> deleteToken() async {
    debugPrint('💾 StorageService: Deleting token');
    await _prefs?.remove(ApiConfig.tokenKey);
  }

  // 用户信息管理
  Future<void> saveUser(User user) async {
    final userJson = json.encode(user.toJson());
    debugPrint('💾 StorageService: Saving user: ${user.username}');
    await _prefs?.setString(ApiConfig.userKey, userJson);
  }

  Future<User?> getUser() async {
    final userJson = _prefs?.getString(ApiConfig.userKey);
    if (userJson == null) {
      debugPrint('💾 StorageService: No saved user');
      return null;
    }
    
    try {
      final userMap = json.decode(userJson) as Map<String, dynamic>;
      final user = User.fromJson(userMap);
      debugPrint('💾 StorageService: Loaded user: ${user.username}');
      return user;
    } catch (e) {
      debugPrint('❌ StorageService: Error loading user: $e');
      return null;
    }
  }

  Future<void> deleteUser() async {
    debugPrint('💾 StorageService: Deleting user');
    await _prefs?.remove(ApiConfig.userKey);
  }

  // 清除所有数据
  Future<void> clearAll() async {
    debugPrint('💾 StorageService: Clearing all data');
    await _prefs?.clear();
  }

  // 主题设置
  Future<void> saveThemeMode(String mode) async {
    await _prefs?.setString('theme_mode', mode);
  }

  Future<String?> getThemeMode() async {
    return _prefs?.getString('theme_mode');
  }

  // 主题色存储
  Future<void> saveSeedColor(int colorValue) async {
    await _prefs?.setInt('seed_color', colorValue);
  }

  Future<int?> getSeedColor() async {
    return _prefs?.getInt('seed_color');
  }

  // 记住密码
  Future<void> saveRememberMe(bool value) async {
    await _prefs?.setBool('remember_me', value);
  }

  Future<bool> getRememberMe() async {
    return _prefs?.getBool('remember_me') ?? false;
  }

  Future<void> saveUsername(String username) async {
    await _prefs?.setString('saved_username', username);
  }

  Future<String?> getSavedUsername() async {
    return _prefs?.getString('saved_username');
  }

  // ===== 阅读器设置 =====
  
  // 全局阅读器设置键
  static const String _readerFontSizeKey = 'reader_font_size';
  static const String _readerLineHeightKey = 'reader_line_height';
  static const String _readerThemeKey = 'reader_theme';
  static const String _readerFontFamilyKey = 'reader_font_family';
  static const String _readerAutoScrollKey = 'reader_auto_scroll';
  static const String _readerScrollSpeedKey = 'reader_scroll_speed';
  static const String _readerPageModeKey = 'reader_page_mode';
  
  // 获取书籍特定设置的键
  String _bookSettingsKey(int bookId, String setting) => 'book_${bookId}_$setting';
  
  // 全局字体大小
  Future<void> saveReaderFontSize(double size) async {
    await _prefs?.setDouble(_readerFontSizeKey, size);
  }
  
  Future<double> getReaderFontSize() async {
    return _prefs?.getDouble(_readerFontSizeKey) ?? 18.0;
  }
  
  // 全局行距
  Future<void> saveReaderLineHeight(double height) async {
    await _prefs?.setDouble(_readerLineHeightKey, height);
  }
  
  Future<double> getReaderLineHeight() async {
    return _prefs?.getDouble(_readerLineHeightKey) ?? 1.8;
  }
  
  // 全局主题
  Future<void> saveReaderTheme(String theme) async {
    await _prefs?.setString(_readerThemeKey, theme);
  }
  
  Future<String> getReaderTheme() async {
    return _prefs?.getString(_readerThemeKey) ?? 'dark';
  }
  
  // 全局字体
  Future<void> saveReaderFontFamily(String fontFamily) async {
    await _prefs?.setString(_readerFontFamilyKey, fontFamily);
  }
  
  Future<String> getReaderFontFamily() async {
    return _prefs?.getString(_readerFontFamilyKey) ?? 'default';
  }
  
  // 自动滚动开关
  Future<void> saveReaderAutoScroll(bool enabled) async {
    await _prefs?.setBool(_readerAutoScrollKey, enabled);
  }
  
  Future<bool> getReaderAutoScroll() async {
    return _prefs?.getBool(_readerAutoScrollKey) ?? false;
  }
  
  // 滚动速度
  Future<void> saveReaderScrollSpeed(int speed) async {
    await _prefs?.setInt(_readerScrollSpeedKey, speed);
  }
  
  Future<int> getReaderScrollSpeed() async {
    return _prefs?.getInt(_readerScrollSpeedKey) ?? 5;
  }
  
  // 翻页模式: scroll, tap, slide
  Future<void> saveReaderPageMode(String mode) async {
    await _prefs?.setString(_readerPageModeKey, mode);
  }
  
  Future<String> getReaderPageMode() async {
    return _prefs?.getString(_readerPageModeKey) ?? 'scroll';
  }
  
  // 书籍特定设置
  Future<void> saveBookReaderSettings(int bookId, Map<String, dynamic> settings) async {
    final jsonStr = json.encode(settings);
    await _prefs?.setString('book_${bookId}_reader_settings', jsonStr);
  }
  
  Future<Map<String, dynamic>?> getBookReaderSettings(int bookId) async {
    final jsonStr = _prefs?.getString('book_${bookId}_reader_settings');
    if (jsonStr == null) return null;
    try {
      return json.decode(jsonStr) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }
  
  // 保存所有阅读器设置（一次性保存）
  Future<void> saveAllReaderSettings({
    required double fontSize,
    required double lineHeight,
    required String theme,
    String? fontFamily,
    bool? autoScroll,
    int? scrollSpeed,
    String? pageMode,
  }) async {
    await _prefs?.setDouble(_readerFontSizeKey, fontSize);
    await _prefs?.setDouble(_readerLineHeightKey, lineHeight);
    await _prefs?.setString(_readerThemeKey, theme);
    if (fontFamily != null) await _prefs?.setString(_readerFontFamilyKey, fontFamily);
    if (autoScroll != null) await _prefs?.setBool(_readerAutoScrollKey, autoScroll);
    if (scrollSpeed != null) await _prefs?.setInt(_readerScrollSpeedKey, scrollSpeed);
    if (pageMode != null) await _prefs?.setString(_readerPageModeKey, pageMode);
  }
  
  // 加载所有阅读器设置
  Future<Map<String, dynamic>> loadAllReaderSettings() async {
    return {
      'fontSize': _prefs?.getDouble(_readerFontSizeKey) ?? 18.0,
      'lineHeight': _prefs?.getDouble(_readerLineHeightKey) ?? 1.8,
      'theme': _prefs?.getString(_readerThemeKey) ?? 'dark',
      'fontFamily': _prefs?.getString(_readerFontFamilyKey) ?? 'default',
      'autoScroll': _prefs?.getBool(_readerAutoScrollKey) ?? false,
      'scrollSpeed': _prefs?.getInt(_readerScrollSpeedKey) ?? 5,
      'pageMode': _prefs?.getString(_readerPageModeKey) ?? 'scroll',
    };
  }
}
