# 封面功能完善实施文档

## 概述

本文档记录了小说书库管理系统封面功能的完整实施，包括 EPUB/MOBI 封面提取、封面管理器、缓存机制和管理员 API。

**实施日期**: 2026-01-15
**状态**: ✅ 已完成

## 实施内容

### 1. MOBI 封面提取 ✅

**文件**: `app/core/metadata/mobi_parser.py`

**功能**:
- 从 MOBI/AZW3 文件解压目录中提取封面图片
- 支持两种查找策略：
  1. 查找包含 "cover" 或 "jacket" 的图片文件
  2. 如果找不到，使用第一张图片（通常是封面）
- 自动转换为 JPG 格式并保存到 covers 目录
- 使用文件 hash 作为封面文件名避免重复

**关键方法**:
```python
def _extract_cover(self, tempdir: str, file_path: Path) -> Optional[str]
```

### 2. 封面管理器 ✅

**文件**: `app/utils/cover_manager.py`

**核心功能**:

#### 2.1 封面路径管理
- `get_cover_path()` - 获取书籍封面路径（支持原图/缩略图）
- 自动生成和缓存缩略图（300x450px）
- 使用 LANCZOS 算法确保高质量缩放

#### 2.2 默认封面生成
提供 **4 种风格** 的默认封面：

1. **gradient** - 渐变风格（默认）
   - 基于书名 hash 的 10 种渐变色方案
   - 显示书名（自动分行）和作者

2. **letter** - 首字母风格（Emby 风格）
   - 渐变背景 + 白色圆形 + 彩色首字母
   - 底部显示书名和作者

3. **book** - 书籍图标风格
   - 灰色背景 + 彩色书籍图标
   - 图标包含书脊效果

4. **minimal** - 极简风格
   - 白色背景 + 顶部彩色条
   - 使用主题色显示文字

**颜色方案**（基于书名 hash 自动选择）:
```python
("#667eea", "#764ba2"),  # 紫色
("#f093fb", "#f5576c"),  # 粉红
("#4facfe", "#00f2fe"),  # 蓝色
("#43e97b", "#38f9d7"),  # 绿色
("#fa709a", "#fee140"),  # 橙色
# ... 等 10 种
```

#### 2.3 缓存管理
- `get_cache_stats()` - 获取封面缓存统计（文件数、大小等）
- `clear_orphaned_covers()` - 清理数据库中不存在的孤立封面文件
- 自动清理对应的缩略图

### 3. 增强的封面 API ✅

**文件**: `app/web/routes/reader.py`

**端点**: `GET /books/{book_id}/cover`

**新增参数**:
- `size` - 封面尺寸
  - `original` - 原始尺寸（默认）
  - `thumbnail` - 缩略图（300x450）
- `style` - 默认封面风格（无封面时使用）
  - `gradient` - 渐变风格（默认）
  - `letter` - 首字母风格
  - `book` - 书籍图标风格
  - `minimal` - 极简风格

**示例**:
```bash
# 获取原图
GET /books/123/cover

# 获取缩略图
GET /books/123/cover?size=thumbnail

# 指定默认封面风格
GET /books/456/cover?style=letter
```

### 4. 管理员封面管理 API ✅

**文件**: `app/web/routes/admin.py`

#### 4.1 重新提取封面
```
POST /api/admin/covers/refresh/{book_id}
```
- 支持 EPUB 和 MOBI 格式
- 重新从电子书文件中提取封面
- 更新数据库记录

#### 4.2 批量提取封面
```
POST /api/admin/covers/batch-extract?library_id={id}
```
- 查找没有封面的书籍
- 可选择指定书库
- 返回待处理书籍数量
- 注：完整的后台任务支持待实现

#### 4.3 封面统计
```
GET /api/admin/covers/stats
```
返回信息：
- 数据库统计
  - 总书籍数
  - 有封面的书籍数
  - 无封面的书籍数
  - 封面覆盖率
- 缓存统计
  - 封面文件数量
  - 缩略图数量
  - 总文件大小（MB）

#### 4.4 清理孤立封面
```
DELETE /api/admin/covers/cleanup
```
- 扫描 covers 目录
- 删除数据库中不存在的封面文件
- 同时删除对应的缩略图
- 返回清理数量

### 5. 封面配置 ✅

**文件**: `app/config.py`

**新增配置类**: `CoverConfig`

```python
class CoverConfig(BaseModel):
    quality: int = 85              # JPG 压缩质量 (1-100)
    max_width: int = 800           # 最大宽度（像素）
    max_height: int = 1200         # 最大高度（像素）
    thumbnail_width: int = 300     # 缩略图宽度
    thumbnail_height: int = 450    # 缩略图高度
    default_style: str = "gradient"  # 默认封面风格
    cache_enabled: bool = True     # 是否启用缓存
```

**配置使用**:
```python
from app.config import settings

# 访问封面配置
quality = settings.cover.quality
style = settings.cover.default_style
```

## 技术细节

### 封面提取流程

```
EPUB:
1. ebooklib.epub.read_epub() 读取 EPUB
2. 查找 ITEM_COVER 类型的项目
3. 如果找不到，查找名称包含 "cover" 的图片
4. 使用 PIL 转换为 JPG 并保存

MOBI:
1. mobi.extract() 解压 MOBI 文件
2. 遍历解压目录查找封面图片
3. 优先级：cover*/jacket* > 第一张图片
4. 使用 PIL 转换为 JPG 并保存
5. 清理临时目录
```

### 缓存策略

```
封面文件命名：{file_hash}.jpg
缩略图命名：thumb_{file_hash}.jpg

存储位置：settings.directories.covers
默认路径：/app/covers

缓存检查：
1. 检查数据库 cover_path 字段
2. 验证文件是否存在
3. 如需缩略图，检查是否已生成
4. 按需生成缩略图并缓存
```

### 默认封面生成

```
1. 基于书名 MD5 hash 选择颜色方案（10选1）
2. 使用 PIL 创建图片（600x900）
3. 根据风格绘制：
   - 渐变背景
   - 文字/图标/形状
4. 返回 PNG 字节数据
5. 如生成失败，使用纯色 fallback
```

## 使用示例

### 前端获取封面

```html
<!-- 书籍列表 - 使用缩略图 -->
<img src="/api/books/123/cover?size=thumbnail" 
     alt="书籍封面">

<!-- 书籍详情 - 使用原图 -->
<img src="/api/books/123/cover" 
     alt="书籍封面">

<!-- 无封面书籍 - 指定风格 -->
<img src="/api/books/456/cover?style=letter" 
     alt="默认封面">
```

### 管理员操作

```bash
# 重新提取单本书封面
curl -X POST http://localhost:8080/api/admin/covers/refresh/123 \
  -H "Authorization: Bearer {token}"

# 查看封面统计
curl http://localhost:8080/api/admin/covers/stats \
  -H "Authorization: Bearer {token}"

# 清理孤立封面
curl -X DELETE http://localhost:8080/api/admin/covers/cleanup \
  -H "Authorization: Bearer {token}"
```

## 性能优化

### 已实现
1. ✅ 使用文件 hash 避免重复存储
2. ✅ 缩略图按需生成并缓存
3. ✅ 封面文件使用 JPG 压缩（85% 质量）
4. ✅ 封面路径缓存在数据库中

### 待优化（未来）
- [ ] 封面内存缓存（Redis/Memcached）
- [ ] CDN 集成
- [ ] 异步批量提取（后台任务队列）
- [ ] 封面预加载策略
- [ ] WebP 格式支持

## 依赖库

```python
from PIL import Image, ImageDraw, ImageFont  # 图片处理
import ebooklib                               # EPUB 解析
from ebooklib import epub
import mobi                                   # MOBI 解析
```

## 测试建议

### 功能测试
1. 上传包含封面的 EPUB 文件，验证封面提取
2. 上传包含封面的 MOBI 文件，验证封面提取
3. 上传无封面的书籍，验证默认封面生成
4. 测试 4 种默认封面风格
5. 测试缩略图生成
6. 测试孤立封面清理

### API 测试
```bash
# 测试封面 API
curl http://localhost:8080/api/books/1/cover
curl http://localhost:8080/api/books/1/cover?size=thumbnail
curl http://localhost:8080/api/books/1/cover?style=letter

# 测试管理员 API
curl -X POST http://localhost:8080/api/admin/covers/refresh/1
curl http://localhost:8080/api/admin/covers/stats
curl -X DELETE http://localhost:8080/api/admin/covers/cleanup
```

### 性能测试
- 测试大量封面加载速度
- 测试缩略图生成时间
- 测试并发封面请求
- 测试缓存命中率

## 已知限制

1. **字体依赖**: 默认封面生成依赖系统字体（arial.ttf），在 Docker 容器中可能需要安装字体包
2. **MOBI 支持**: MOBI 封面提取依赖 mobi 库，部分特殊格式可能无法提取
3. **批量处理**: 当前批量提取仅返回统计，未实现真正的后台任务
4. **中文字体**: 默认封面的中文显示可能不理想，建议配置中文字体

## 解决方案

### Docker 字体支持
```dockerfile
# Dockerfile 中添加
RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*
```

### 自定义字体路径
```python
# 在 cover_manager.py 中
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 60)
except:
    font = ImageFont.load_default()
```

## 后续计划

### 优先级高
- [ ] Docker 镜像添加字体支持
- [ ] 实现真正的批量封面提取后台任务
- [ ] 添加封面管理前端界面

### 优先级中
- [ ] 支持更多电子书格式封面提取（PDF、AZW 等）
- [ ] 封面编辑功能（裁剪、旋转）
- [ ] 自定义默认封面模板

### 优先级低
- [ ] 封面搜索功能（从网络获取）
- [ ] 封面推荐系统
- [ ] 封面质量分析

## 更新日志

### 2026-01-15
- ✅ 实现 MOBI 封面提取
- ✅ 创建封面管理器（CoverManager）
- ✅ 实现 4 种默认封面风格
- ✅ 添加封面 API 参数支持（size、style）
- ✅ 实现管理员封面管理 API（4个端点）
- ✅ 添加封面配置（CoverConfig）
- ✅ 文档编写

## 相关文档

- [在线阅读器实施](ONLINE_READER_IMPLEMENTATION.md)
- [OPDS 协议支持](../README.md#opds)
- [项目完成报告](../../plans/project-completion-report.md)
