import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/book_provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/book_card.dart';
import '../widgets/shimmer_loading.dart';
import '../utils/responsive.dart';
import '../models/library.dart';
import '../services/api_config.dart';

class LibraryScreen extends StatefulWidget {
  final int? libraryId;
  
  const LibraryScreen({super.key, this.libraryId});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  final ScrollController _scrollController = ScrollController();
  int? _selectedLibraryId;

  @override
  void initState() {
    super.initState();
    
    // 如果传入了 libraryId，直接进入该书库
    _selectedLibraryId = widget.libraryId;
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // 加载书库列表
      context.read<DashboardProvider>().loadDashboard();
      
      // 如果已选择书库，加载书籍
      if (_selectedLibraryId != null) {
        context.read<BookProvider>().setFilter(libraryId: _selectedLibraryId);
      }
    });

    // 监听滚动，实现无限加载
    _scrollController.addListener(() {
      if (_selectedLibraryId != null &&
          _scrollController.position.pixels >=
          _scrollController.position.maxScrollExtent - 200) {
        context.read<BookProvider>().loadMore();
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _selectLibrary(int? libraryId) {
    setState(() {
      _selectedLibraryId = libraryId;
    });
    
    if (libraryId != null) {
      context.read<BookProvider>().setFilter(libraryId: libraryId);
    } else {
      context.read<BookProvider>().clearFilter();
    }
  }

  @override
  Widget build(BuildContext context) {
    // 如果没有选择书库，显示书库列表
    if (_selectedLibraryId == null) {
      return _buildLibraryListView();
    }
    
    // 否则显示书籍网格
    return _buildBookGridView();
  }

  /// 书库列表视图
  Widget _buildLibraryListView() {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
        title: const Text('选择书库'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => context.push('/search'),
          ),
        ],
      ),
      body: Consumer<DashboardProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading && provider.libraries.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }
          
          final libraries = provider.libraries;
          
          if (libraries.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.library_books_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('暂无书库', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
          }
          
          return RefreshIndicator(
            onRefresh: () => provider.refresh(),
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: Responsive.isMobile(context) ? 2 : 4,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1.2,
              ),
              itemCount: libraries.length + 1, // +1 for "全部"
              itemBuilder: (context, index) {
                if (index == 0) {
                  return _buildAllLibraryCard();
                }
                return _buildLibraryCard(libraries[index - 1]);
              },
            ),
          );
        },
      ),
    );
  }

  /// "全部书库" 卡片
  Widget _buildAllLibraryCard() {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          context.read<BookProvider>().loadBooks();
          setState(() => _selectedLibraryId = -1); // -1 表示全部
        },
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Theme.of(context).primaryColor.withOpacity(0.8),
                Theme.of(context).primaryColor,
              ],
            ),
          ),
          child: const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.library_books, size: 48, color: Colors.white),
              SizedBox(height: 12),
              Text(
                '全部书籍',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 书库卡片
  Widget _buildLibraryCard(Library library) {
    final coverUrl = library.coverUrl != null 
        ? '${ApiConfig.baseUrl}${library.coverUrl}'
        : '';
    
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _selectLibrary(library.id),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 背景
            if (coverUrl.isNotEmpty)
              ColorFiltered(
                colorFilter: ColorFilter.mode(
                  Colors.black.withOpacity(0.3),
                  BlendMode.darken,
                ),
                child: Image.network(
                  coverUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildLibraryPlaceholder(library),
                ),
              )
            else
              _buildLibraryPlaceholder(library),
            
            // 书库信息
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      Colors.black.withOpacity(0.8),
                    ],
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      library.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${library.bookCount ?? 0} 本书',
                      style: TextStyle(
                        color: Colors.grey[300],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLibraryPlaceholder(Library library) {
    // 根据书库名生成稳定的颜色
    final hash = library.name.hashCode;
    final hue = (hash % 360).abs().toDouble();
    final color = HSLColor.fromAHSL(1.0, hue, 0.4, 0.35).toColor();
    
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [color, color.withOpacity(0.7)],
        ),
      ),
      child: const Center(
        child: Icon(Icons.folder, size: 48, color: Colors.white54),
      ),
    );
  }

  /// 书籍网格视图
  Widget _buildBookGridView() {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            setState(() => _selectedLibraryId = null);
            context.read<BookProvider>().clearFilter();
          },
        ),
        title: Consumer<DashboardProvider>(
          builder: (context, provider, _) {
            if (_selectedLibraryId == -1) {
              return const Text('全部书籍');
            }
            final library = provider.libraries.firstWhere(
              (l) => l.id == _selectedLibraryId,
              orElse: () => Library(id: 0, name: '书库', bookCount: 0),
            );
            return Text(library.name);
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => context.push('/search'),
          ),
        ],
      ),
      body: Consumer<BookProvider>(
        builder: (context, bookProvider, child) {
          // 错误状态
          if (bookProvider.errorMessage != null && bookProvider.books.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(bookProvider.errorMessage!, textAlign: TextAlign.center),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      bookProvider.clearError();
                      bookProvider.loadBooks(refresh: true);
                    },
                    child: const Text('重试'),
                  ),
                ],
              ),
            );
          }

          // 加载中 - 骨架屏
          if (bookProvider.isLoading && bookProvider.books.isEmpty) {
            return Padding(
              padding: const EdgeInsets.all(12),
              child: BookGridSkeleton(
                crossAxisCount: Responsive.getGridCrossAxisCount(context),
                itemCount: 12,
              ),
            );
          }

          // 空状态
          if (bookProvider.books.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.library_books_outlined, size: 64, color: Colors.grey[600]),
                  const SizedBox(height: 16),
                  Text('暂无书籍', style: TextStyle(fontSize: 18, color: Colors.grey[400])),
                ],
              ),
            );
          }

          // 书籍网格
          return RefreshIndicator(
            onRefresh: () => bookProvider.refresh(),
            child: GridView.builder(
              controller: _scrollController,
              padding: Responsive.getPadding(context),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: Responsive.getGridCrossAxisCount(context),
                childAspectRatio: Responsive.getBookCardAspectRatio(context),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: bookProvider.books.length + (bookProvider.isLoadingMore ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == bookProvider.books.length) {
                  return const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16.0),
                      child: CircularProgressIndicator(),
                    ),
                  );
                }

                final book = bookProvider.books[index];
                final coverUrl = bookProvider.getCoverUrl(book.id);

                return BookCard(
                  book: book,
                  coverUrl: coverUrl,
                  onTap: () => context.push('/book/${book.id}'),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
