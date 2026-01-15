# 备份与恢复系统实施文档

## 概述

备份与恢复系统是小说书库管理系统的关键维护功能，提供完整的数据保护和灾难恢复能力。

## 核心功能

### 1. 备份管理

#### 支持的备份内容
- **database** - 数据库文件（SQLite + Alembic 迁移历史）
- **covers** - 书籍封面图片
- **config** - 系统配置文件

#### 备份文件格式
```
backup_YYYYMMDD_HHMMSS.zip
├── metadata.json          # 备份元数据
├── database/
│   ├── library.db         # 数据库文件
│   └── alembic/versions/  # 迁移脚本
├── covers/                # 封面目录（可选）
│   └── *.jpg
└── config/                # 配置文件（可选）
    └── config.yaml
```

#### 备份元数据
每个备份包含元数据文件 `metadata.json`：
```json
{
  "backup_id": "backup_20260115_230000",
  "created_at": "2026-01-15T23:00:00",
  "description": "每日自动备份",
  "includes": ["database", "covers", "config"],
  "file_size": 52428800,
  "checksum": "5d41402abc4b2a76b9719d911017c592",
  "version": "1.0"
}
```

### 2. 核心模块

#### BackupManager 类
位置：`app/core/backup.py`

**主要方法：**

- `create_backup(includes, description)` - 创建备份
  - 使用 SQLite `.backup()` API 安全备份数据库
  - ZIP 压缩（可配置压缩级别）
  - MD5 校验和计算
  - 自动清理旧备份

- `list_backups()` - 列出所有备份
  - 返回备份列表（按时间降序）
  - 包含文件大小、创建时间等信息

- `validate_backup(backup_id)` - 验证备份完整性
  - ZIP 文件完整性检查
  - MD5 校验和验证
  - 元数据有效性检查

- `restore_backup(backup_id, includes, create_snapshot)` - 恢复备份
  - 恢复前可选创建快照
  - 支持部分恢复（选择性恢复内容）
  - 数据库文件验证
  - 失败自动提示快照回滚

- `delete_backup(backup_id)` - 删除备份

- `get_backup_stats()` - 获取备份统计信息

**私有方法：**
- `_backup_database(zipf)` - 备份数据库到 ZIP
- `_backup_covers(zipf)` - 备份封面到 ZIP
- `_backup_config(zipf)` - 备份配置到 ZIP
- `_restore_database(zipf)` - 从 ZIP 恢复数据库
- `_restore_covers(zipf)` - 从 ZIP 恢复封面
- `_restore_config(zipf)` - 从 ZIP 恢复配置
- `_cleanup_old_backups()` - 清理旧备份
- `_calculate_checksum(file_path)` - 计算 MD5 校验和
- `_generate_backup_id()` - 生成备份 ID

### 3. 配置系统

#### BackupConfig 类
位置：`app/config.py`

```python
class BackupConfig(BaseModel):
    backup_path: str = "/app/data/backups"  # 备份文件保存路径
    retention_count: int = 7                # 保留备份数量
    auto_backup_enabled: bool = False       # 是否启用自动备份
    auto_backup_schedule: str = "0 2 * * *" # Cron 表达式
    default_includes: List[str] = ["database", "covers", "config"]
    compression_level: int = 6              # ZIP 压缩级别 (0-9)
```

#### 配置说明

- **backup_path**: 备份文件存储目录
- **retention_count**: 保留的备份数量（超过后自动删除最旧的）
- **auto_backup_enabled**: 是否启用定时自动备份
- **auto_backup_schedule**: Cron 表达式，默认每天凌晨2点
- **default_includes**: 默认备份的内容
- **compression_level**: ZIP 压缩级别（0=不压缩，9=最大压缩）

### 4. 定时备份调度器

#### BackupScheduler 类
位置：`app/core/scheduler.py`

定时备份调度器基于 APScheduler 实现，支持 Cron 表达式配置自动备份计划。

**主要功能：**

- 自动定时执行备份任务
- 支持 Cron 表达式灵活配置
- 任务状态追踪和监控
- 失败重试和错误处理
- 优雅启动和关闭

**主要方法：**

- `start()` - 启动调度器
  - 根据配置启用/禁用自动备份
  - 解析 Cron 表达式并添加任务

- `enable_auto_backup(schedule)` - 启用自动备份
  - 可选更新 Cron 表达式
  - 动态添加定时任务

- `disable_auto_backup()` - 禁用自动备份
  - 移除定时任务但保持调度器运行

- `trigger_backup_now()` - 手动触发备份
  - 立即执行一次备份
  - 不影响定时计划

- `update_schedule(new_schedule)` - 更新调度计划
  - 验证 Cron 表达式
  - 重新配置任务

- `get_status()` - 获取调度器状态
  - 运行状态、上次执行、下次执行等

- `shutdown()` - 关闭调度器

**任务执行流程：**

1. 调度器按 Cron 时间触发任务
2. 执行 `_auto_backup_task()`
3. 调用 `BackupManager.create_backup()`
4. 记录详细执行日志
5. 更新任务状态（成功/失败）
6. 失败时记录错误信息

**错误处理：**
- 备份失败不影响调度器继续运行
- 详细错误日志记录
- 支持查询上次执行状态

#### 集成到应用

调度器在应用启动时自动初始化：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    await backup_scheduler.start()
    log.info("定时备份调度器已启动")
    
    yield
    
    # 关闭时
    await backup_scheduler.shutdown()
    log.info("定时备份调度器已关闭")
```

### 5. 管理员 API

所有备份 API 需要管理员权限。

#### 备份管理 API

#### POST /api/admin/backup/create
创建备份

**请求体：**
```json
{
  "includes": ["database", "covers"],
  "description": "手动备份"
}
```

**响应：**
```json
{
  "success": true,
  "backup_id": "backup_20260115_230000",
  "file_path": "/app/data/backups/backup_20260115_230000.zip",
  "file_size": 52428800,
  "checksum": "5d41402abc4b2a76b9719d911017c592",
  "includes": ["database", "covers"],
  "description": "手动备份"
}
```

#### GET /api/admin/backup/list
获取备份列表

**响应：**
```json
{
  "backups": [
    {
      "backup_id": "backup_20260115_230000",
      "file_name": "backup_20260115_230000.zip",
      "file_path": "/app/data/backups/backup_20260115_230000.zip",
      "file_size": 52428800,
      "file_size_mb": 50.0,
      "created_at": "2026-01-15T23:00:00",
      "description": "每日自动备份",
      "includes": ["database", "covers", "config"],
      "checksum": "5d41402abc4b2a76b9719d911017c592"
    }
  ],
  "total": 1
}
```

#### GET /api/admin/backup/download/{backup_id}
下载备份文件

**响应：** ZIP 文件下载

#### DELETE /api/admin/backup/{backup_id}
删除备份

**响应：**
```json
{
  "message": "备份已删除",
  "backup_id": "backup_20260115_230000"
}
```

#### POST /api/admin/backup/restore
恢复备份

**请求体：**
```json
{
  "backup_id": "backup_20260115_230000",
  "includes": ["database"],
  "create_snapshot": true
}
```

**响应：**
```json
{
  "success": true,
  "backup_id": "backup_20260115_230000",
  "restored": ["database"],
  "snapshot_id": "backup_20260115_230500"
}
```

#### GET /api/admin/backup/validate/{backup_id}
验证备份完整性

**响应：**
```json
{
  "valid": true,
  "backup_id": "backup_20260115_230000",
  "includes": ["database", "covers", "config"],
  "file_size": 52428800,
  "checksum": "5d41402abc4b2a76b9719d911017c592"
}
```

#### GET /api/admin/backup/stats
获取备份统计信息

**响应：**
```json
{
  "total_backups": 7,
  "total_size": 367001600,
  "total_size_mb": 350.0,
  "backup_dir": "/app/data/backups",
  "retention_count": 7,
  "auto_backup_enabled": false,
  "latest_backup": {
    "backup_id": "backup_20260115_230000",
    "created_at": "2026-01-15T23:00:00",
    "file_size_mb": 50.0
  }
}
```

#### 定时备份调度器管理 API

##### GET /api/admin/backup/scheduler/status
获取调度器状态

**响应：**
```json
{
  "running": true,
  "auto_backup_enabled": true,
  "schedule": "0 2 * * *",
  "next_run": "2026-01-16T02:00:00+08:00",
  "last_run": "2026-01-15T02:00:00+08:00",
  "last_status": "成功",
  "last_error": null
}
```

##### POST /api/admin/backup/scheduler/trigger
手动触发定时备份

立即执行一次备份任务，不影响定时计划。

**响应：**
```json
{
  "success": true,
  "message": "备份任务执行成功",
  "backup_id": "backup_20260115_235900",
  "file_size": 52428800,
  "checksum": "5d41402abc4b2a76b9719d911017c592",
  "includes": ["database", "covers", "config"]
}
```

##### POST /api/admin/backup/scheduler/enable
启用自动备份

**请求体（可选）：**
```json
{
  "schedule": "0 3 * * *"
}
```

如果不提供 `schedule`，使用当前配置的计划。

**响应：**
```json
{
  "message": "自动备份已启用",
  "status": {
    "running": true,
    "auto_backup_enabled": true,
    "schedule": "0 3 * * *",
    "next_run": "2026-01-16T03:00:00+08:00"
  }
}
```

##### POST /api/admin/backup/scheduler/disable
禁用自动备份

**响应：**
```json
{
  "message": "自动备份已禁用",
  "status": {
    "running": true,
    "auto_backup_enabled": false,
    "schedule": "0 2 * * *",
    "next_run": null
  }
}
```

##### PUT /api/admin/backup/scheduler/schedule
更新备份计划

**请求体：**
```json
{
  "schedule": "0 */6 * * *"
}
```

**Cron 表达式格式：** `分 时 日 月 星期`

**示例：**
- `"0 2 * * *"` - 每天凌晨2点
- `"0 */6 * * *"` - 每6小时
- `"0 0 * * 0"` - 每周日午夜
- `"0 3 1 * *"` - 每月1日凌晨3点

**响应：**
```json
{
  "message": "备份计划已更新",
  "schedule": "0 */6 * * *",
  "status": {
    "running": true,
    "auto_backup_enabled": true,
    "schedule": "0 */6 * * *",
    "next_run": "2026-01-16T00:00:00+08:00"
  }
}
```

## 技术实现

### 1. 数据库备份

使用 SQLite 的 `.backup()` API 进行在线备份，无需停止应用：

```python
async with aiosqlite.connect(source_db) as source:
    async with aiosqlite.connect(backup_db) as backup:
        await source.backup(backup)
```

优势：
- ✅ 安全的在线备份
- ✅ 事务一致性
- ✅ 不锁定数据库
- ✅ 适合生产环境

### 2. 文件压缩

使用 Python 标准库 `zipfile`，支持压缩级别配置：

```python
with zipfile.ZipFile(
    backup_file,
    'w',
    zipfile.ZIP_DEFLATED,
    compresslevel=6
) as zipf:
    # 添加文件
    zipf.write(file_path, arcname)
```

### 3. 完整性校验

每个备份计算 MD5 校验和，验证时重新计算并对比：

```python
def _calculate_checksum(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
```

### 4. 自动清理

备份创建后自动清理超过保留数量的旧备份：

```python
async def _cleanup_old_backups(self):
    retention_count = settings.backup.retention_count
    backups = sorted(
        self.backup_dir.glob("backup_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # 保护快照备份
    for old_backup in backups[retention_count:]:
        if not is_snapshot(old_backup):
            old_backup.unlink()
```

### 5. 恢复安全性

恢复前创建快照，失败时可以回滚：

```python
# 创建快照
snapshot = await self.create_backup(
    description=f"恢复前快照 (before restore {backup_id})"
)

try:
    # 执行恢复
    await self._restore_database(zipf)
    await self._restore_covers(zipf)
except Exception as e:
    log.warning(f"可以使用快照回滚: {snapshot['backup_id']}")
    raise
```

## 使用场景

### 1. 手动备份

管理员在重要操作前创建备份：

```bash
# API 调用示例
curl -X POST http://localhost:8080/api/admin/backup/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "includes": ["database", "covers"],
    "description": "升级前备份"
  }'
```

### 2. 定时自动备份

#### 配置文件

在 `config/config.yaml` 中配置：

```yaml
backup:
  backup_path: "/app/data/backups"
  retention_count: 7
  auto_backup_enabled: true          # 启用自动备份
  auto_backup_schedule: "0 2 * * *"  # 每天凌晨2点
  default_includes:
    - database
    - covers
    - config
  compression_level: 6
```

#### 通过 API 管理

**查看调度器状态：**
```bash
curl -X GET http://localhost:8080/api/admin/backup/scheduler/status \
  -H "Authorization: Bearer <token>"
```

**启用自动备份：**
```bash
curl -X POST http://localhost:8080/api/admin/backup/scheduler/enable \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"schedule": "0 2 * * *"}'
```

**更新备份计划：**
```bash
curl -X PUT http://localhost:8080/api/admin/backup/scheduler/schedule \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"schedule": "0 */6 * * *"}'
```

**手动触发备份：**
```bash
curl -X POST http://localhost:8080/api/admin/backup/scheduler/trigger \
  -H "Authorization: Bearer <token>"
```

**禁用自动备份：**
```bash
curl -X POST http://localhost:8080/api/admin/backup/scheduler/disable \
  -H "Authorization: Bearer <token>"
```

#### 自动备份日志

调度器执行备份时会记录详细日志：

```
开始执行自动备份任务
执行时间: 2026-01-15 02:00:00
自动备份完成: backup_20260115_020000
备份大小: 50.23 MB
包含内容: database, covers, config
```

失败时也会记录错误：

```
开始执行自动备份任务
执行时间: 2026-01-15 02:00:00
自动备份失败: [Errno 28] No space left on device
```

### 3. 灾难恢复

系统出现问题时恢复备份：

1. 列出可用备份
2. 验证备份完整性
3. 恢复备份（自动创建快照）
4. 如果恢复失败，使用快照回滚

### 4. 数据迁移

迁移到新服务器：

1. 在旧服务器创建完整备份
2. 下载备份文件
3. 在新服务器上传并恢复

## 最佳实践

### 1. 备份策略

- ✅ 定期自动备份（每天）
- ✅ 保留足够的备份数量（7天）
- ✅ 重要操作前手动备份
- ✅ 定期验证备份完整性

### 2. 存储管理

- ✅ 监控备份目录空间
- ✅ 配置合适的压缩级别
- ✅ 定期清理旧备份
- ✅ 考虑异地存储（可选）

### 3. 恢复测试

- ✅ 定期测试恢复流程
- ✅ 验证恢复后数据完整性
- ✅ 记录恢复时间
- ✅ 准备应急预案

### 4. 安全性

- ✅ 限制备份 API 访问（仅管理员）
- ✅ 备份文件权限控制
- ✅ 考虑备份加密（可选）
- ✅ 审计日志记录

## 注意事项

### ⚠️ 数据库恢复

恢复数据库时会覆盖现有数据，建议：
1. 在恢复前创建快照（默认启用）
2. 确保应用没有大量活跃连接
3. 考虑在维护窗口执行

### ⚠️ 磁盘空间

备份会占用磁盘空间，需要：
1. 监控备份目录空间
2. 配置合理的保留数量
3. 考虑压缩级别平衡

### ⚠️ 恢复时间

大型数据库恢复可能需要时间：
1. 测试估算恢复时间
2. 准备维护通知
3. 考虑增量备份（未来）

## 未来增强

### 计划功能

1. ~~**定时备份调度器**~~ ✅ 已完成
   - ~~集成 APScheduler~~ ✅
   - ~~Cron 表达式调度~~ ✅
   - ~~自动清理旧备份~~ ✅
   - ~~任务状态监控~~ ✅
   - ~~管理员 API~~ ✅

2. **备份加密**
   - 密码保护备份文件
   - AES-256 加密

3. **云存储/网络存储集成**
   - **对象存储**
     - S3 兼容存储（MinIO、阿里云OSS等）
     - Azure Blob Storage
   - **网盘服务**
     - OneDrive
     - Google Drive
     - 坚果云
   - **网络协议**
     - WebDAV（支持各种网盘）
     - SMB/CIFS（Windows共享、NAS）
     - FTP/SFTP
     - NFS（Linux网络文件系统）
   - **功能特性**
     - 自动上传备份到远程
     - 异地容灾备份
     - 多目标同步
     - 加密传输

4. **增量备份**
   - 减少备份大小
   - 加快备份速度
   - 节省存储空间

5. **前端管理界面**
   - 可视化备份管理
   - 一键备份/恢复
   - 进度显示

## 故障排除

### 备份创建失败

**问题：** 备份创建时出错

**解决：**
1. 检查磁盘空间
2. 检查目录权限
3. 查看日志文件
4. 验证数据库连接

### 恢复失败

**问题：** 恢复备份时出错

**解决：**
1. 验证备份文件完整性
2. 检查快照是否创建
3. 使用快照回滚
4. 联系技术支持

### 备份文件损坏

**问题：** 验证时发现备份损坏

**解决：**
1. 尝试使用其他备份
2. 检查磁盘错误
3. 重新创建备份
4. 考虑异地存储

## 相关文档

- [项目完成报告](../plans/project-completion-report.md)
- [数据库迁移文档](../MIGRATION.md)
- [部署文档](../README.md)

## 更新日志

### 2026-01-15

#### 早期
- ✅ 实现核心 BackupManager 类
- ✅ 添加 BackupConfig 配置
- ✅ 实现管理员备份 API
- ✅ 支持数据库、封面、配置备份
- ✅ MD5 校验和验证
- ✅ 自动清理旧备份
- ✅ 恢复前快照功能
- ✅ 完整的 API 文档

#### 晚间
- ✅ 实现 BackupScheduler 定时调度器
- ✅ 集成 APScheduler（AsyncIOScheduler）
- ✅ 支持 Cron 表达式配置
- ✅ 任务状态追踪和监控
- ✅ 应用生命周期集成
- ✅ 调度器管理 API（5个端点）
- ✅ 完整的错误处理和日志
- ✅ 更新系统文档
