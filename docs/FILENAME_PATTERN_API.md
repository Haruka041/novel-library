# 文件名模式识别系统 API 文档

## 概述

智能文件名识别系统通过分析书库中的文件命名模式，自动生成和管理解析规则，帮助系统更准确地从文件名中提取书名和作者信息。

## 数据模型

### FilenamePattern（文件名解析规则）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 规则名称 |
| description | Text | 规则描述 |
| regex_pattern | Text | 正则表达式模式 |
| priority | Integer | 优先级（数字越大越优先） |
| is_active | Boolean | 是否启用 |
| match_count | Integer | 匹配次数 |
| success_count | Integer | 成功提取次数 |
| accuracy_rate | Float | 准确率 |
| created_by | String(20) | 创建方式（manual/auto/ai） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| example_filename | String(500) | 示例文件名 |
| example_result | Text | 示例解析结果（JSON） |

## API 端点

### 1. 分析书库文件名模式

**端点**: `POST /api/admin/analyze-library/{library_id}`

**权限**: 管理员

**描述**: 分析指定书库中的文件名模式，生成统计报告和规则建议

**路径参数**:
- `library_id` (int): 书库ID

**响应示例**:
```json
{
  "library_id": 1,
  "library_name": "我的书库",
  "total_files": 150,
  "analyzed_files": 150,
  "patterns_found": {
    "total_files": 150,
    "separators": {
      "-": {
        "count": 80,
        "percentage": 53.33,
        "examples": ["作者1-书名1.txt", "作者2-书名2.txt"]
      },
      "_": {
        "count": 40,
        "percentage": 26.67,
        "examples": ["作者3_书名3.txt"]
      }
    },
    "brackets": {
      "[]": {
        "count": 20,
        "percentage": 13.33
      }
    },
    "patterns": {
      "作者-书名": {
        "count": 80,
        "percentage": 53.33,
        "examples": ["作者1-书名1.txt", "作者2-书名2.txt"]
      }
    }
  },
  "suggested_patterns": [
    {
      "name": "Pattern with separator \"-\"",
      "regex_pattern": "^(.+?)[-](.+?)\\.(txt|epub|mobi)$",
      "priority": 80,
      "example_filename": "作者1-书名1.txt",
      "coverage": "80 files (53.3%)"
    }
  ]
}
```

### 2. 获取所有文件名规则

**端点**: `GET /api/admin/filename-patterns`

**权限**: 管理员

**查询参数**:
- `active_only` (bool, 可选): 仅返回启用的规则，默认 false

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "作者-书名模式",
    "description": "使用连字符分隔作者和书名",
    "regex_pattern": "^(.+?)[-](.+?)\\.txt$",
    "priority": 100,
    "is_active": true,
    "match_count": 80,
    "success_count": 75,
    "accuracy_rate": 93.75,
    "created_by": "manual",
    "created_at": "2026-01-15T14:30:00",
    "updated_at": "2026-01-15T14:30:00",
    "example_filename": "鲁迅-阿Q正传.txt",
    "example_result": "{\"author\": \"鲁迅\", \"title\": \"阿Q正传\"}"
  }
]
```

### 3. 创建文件名规则

**端点**: `POST /api/admin/filename-patterns`

**权限**: 管理员

**请求体**:
```json
{
  "name": "作者-书名模式",
  "description": "使用连字符分隔作者和书名",
  "regex_pattern": "^(.+?)[-](.+?)\\.txt$",
  "priority": 100,
  "example_filename": "鲁迅-阿Q正传.txt",
  "example_result": "{\"author\": \"鲁迅\", \"title\": \"阿Q正传\"}"
}
```

**响应**: 返回创建的规则对象（同上）

### 4. 获取单个规则详情

**端点**: `GET /api/admin/filename-patterns/{pattern_id}`

**权限**: 管理员

**路径参数**:
- `pattern_id` (int): 规则ID

**响应**: 返回规则对象（格式同上）

### 5. 更新文件名规则

**端点**: `PUT /api/admin/filename-patterns/{pattern_id}`

**权限**: 管理员

**路径参数**:
- `pattern_id` (int): 规则ID

**请求体** (所有字段可选):
```json
{
  "name": "新名称",
  "description": "新描述",
  "regex_pattern": "新正则表达式",
  "priority": 200,
  "is_active": false,
  "example_filename": "新示例.txt",
  "example_result": "{\"author\": \"作者\", \"title\": \"书名\"}"
}
```

**响应**: 返回更新后的规则对象

### 6. 删除文件名规则

**端点**: `DELETE /api/admin/filename-patterns/{pattern_id}`

**权限**: 管理员

**路径参数**:
- `pattern_id` (int): 规则ID

**响应**:
```json
{
  "message": "规则已删除",
  "pattern_name": "作者-书名模式"
}
```

### 7. 获取规则统计信息

**端点**: `GET /api/admin/filename-patterns/stats/summary`

**权限**: 管理员

**响应示例**:
```json
{
  "total_patterns": 10,
  "active_patterns": 8,
  "inactive_patterns": 2,
  "total_matches": 1500,
  "total_success": 1425,
  "average_accuracy": 95.0
}
```

## 使用流程

### 1. 分析书库文件名

```javascript
// 分析书库1的文件名模式
const response = await fetch('/api/admin/analyze-library/1', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

const analysis = await response.json();
console.log('发现的模式:', analysis.patterns_found);
console.log('建议的规则:', analysis.suggested_patterns);
```

### 2. 创建规则

```javascript
// 基于分析结果创建规则
const pattern = analysis.suggested_patterns[0];

const response = await fetch('/api/admin/filename-patterns', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: pattern.name,
    regex_pattern: pattern.regex_pattern,
    priority: pattern.priority,
    example_filename: pattern.example_filename
  })
});

const created = await response.json();
console.log('规则已创建:', created);
```

### 3. 查看所有规则

```javascript
const response = await fetch('/api/admin/filename-patterns?active_only=true', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

const patterns = await response.json();
console.log('活跃规则数:', patterns.length);
```

### 4. 更新规则

```javascript
// 禁用某个规则
const response = await fetch('/api/admin/filename-patterns/1', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    is_active: false
  })
});
```

### 5. 查看统计

```javascript
const response = await fetch('/api/admin/filename-patterns/stats/summary', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

const stats = await response.json();
console.log('平均准确率:', stats.average_accuracy + '%');
```

## 正则表达式模式示例

### 常见模式

1. **作者-书名**
   - 正则: `^(.+?)[-](.+?)\.(txt|epub|mobi)$`
   - 示例: `鲁迅-阿Q正传.txt`

2. **作者_书名**
   - 正则: `^(.+?)[_](.+?)\.(txt|epub|mobi)$`
   - 示例: `鲁迅_阿Q正传.txt`

3. **[作者]书名**
   - 正则: `^\[(.+?)\](.+?)\.(txt|epub|mobi)$`
   - 示例: `[鲁迅]阿Q正传.txt`

4. **作者《书名》**
   - 正则: `^(.+?)《(.+?)》\.(txt|epub|mobi)$`
   - 示例: `鲁迅《阿Q正传》.txt`

5. **书名(作者)**
   - 正则: `^(.+?)\((.+?)\)\.(txt|epub|mobi)$`
   - 示例: `阿Q正传(鲁迅).txt`

## 最佳实践

### 1. 规则优先级设置

- 高优先级（100+）：精确匹配的模式
- 中优先级（50-99）：常见但可能有歧义的模式
- 低优先级（<50）：宽泛的通用模式

### 2. 正则表达式建议

- 使用非贪婪匹配 `(.+?)`
- 明确指定分隔符和扩展名
- 考虑多种文件格式 `(txt|epub|mobi)`

### 3. 规则管理

- 定期检查规则的准确率
- 禁用准确率低的规则
- 基于实际使用情况调整优先级

### 4. 测试流程

1. 先在测试书库上运行分析
2. 查看建议的规则是否合理
3. 创建规则并设置为 `is_active=false`
4. 手动测试几个文件验证效果
5. 确认无误后启用规则

## 错误处理

### 常见错误

- **404 Not Found**: 书库或规则不存在
- **403 Forbidden**: 需要管理员权限
- **400 Bad Request**: 书库中没有书籍或请求数据无效

### 错误响应示例

```json
{
  "detail": "书库不存在"
}
```

## 数据库迁移

使用 Alembic 创建 `filename_patterns` 表：

```bash
# 运行迁移
python -m alembic upgrade head
```

迁移文件位置: `alembic/versions/a65cf1a541fe_add_filename_patterns_table.py`

## 相关文档

- [文件名分析器文档](./FILENAME_ANALYSIS.md)
- [命令行分析工具](../scripts/analyze_filenames.py)
- [书库扫描器](../app/core/scanner.py)
