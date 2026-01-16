import 'package:flutter/material.dart';
import '../models/book.dart';

class BookCard extends StatelessWidget {
  final Book book;
  final String coverUrl;
  final VoidCallback onTap;

  const BookCard({
    super.key,
    required this.book,
    required this.coverUrl,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 封面图片 - 占大部分空间
            Expanded(
              flex: 4,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  _buildCoverImage(),
                  
                  // 格式标签（左上角）
                  Positioned(
                    top: 6,
                    left: 6,
                    child: _buildFormatTag(book.fileFormat.toUpperCase()),
                  ),
                  
                  // 年龄分级徽章（右上角）
                  if (book.ageRating == 'adult')
                    Positioned(
                      top: 6,
                      right: 6,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          '18+',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            
            // 书籍信息 - 独立区域，深色背景
            Container(
              color: Colors.grey[900],
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 书名
                  Text(
                    book.title,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                      color: Colors.white,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  // 作者
                  Text(
                    book.authorName ?? '未知',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 10,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCoverImage() {
    if (coverUrl.isEmpty) {
      return _buildPlaceholder();
    }

    return Image.network(
      coverUrl,
      fit: BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Container(
          color: Colors.grey[850],
          child: Center(
            child: CircularProgressIndicator(
              value: loadingProgress.expectedTotalBytes != null
                  ? loadingProgress.cumulativeBytesLoaded /
                      loadingProgress.expectedTotalBytes!
                  : null,
              strokeWidth: 2,
              color: Colors.grey[600],
            ),
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) {
        return _buildPlaceholder();
      },
    );
  }

  Widget _buildPlaceholder() {
    // 根据书名生成稳定的颜色
    final hash = book.title.hashCode;
    final hue = (hash % 360).abs().toDouble();
    final color = HSLColor.fromAHSL(1.0, hue, 0.3, 0.25).toColor();
    
    return Container(
      color: color,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.menu_book,
                size: 40,
                color: Colors.white.withOpacity(0.4),
              ),
              const SizedBox(height: 8),
              Text(
                book.title,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.7),
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFormatTag(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 6,
        vertical: 3,
      ),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.6),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 9,
          color: Colors.white,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
