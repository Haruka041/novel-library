# Windows 用户手动推送到 GitHub 指南

如果自动化脚本遇到问题，可以手动执行以下步骤：

## 第一步：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. Repository name 填写：`novel-library`
3. 选择 `Public`（公开）
4. **不要**勾选 "Add a README file"
5. 点击 `Create repository`

## 第二步：打开命令行

在 `novel-library` 文件夹中：
1. 按住 `Shift` 键
2. 右键点击文件夹空白处
3. 选择 "在此处打开 PowerShell 窗口" 或 "在此处打开命令提示符"

## 第三步：复制以下命令并执行

**⚠️ 注意：把 `你的用户名` 替换成你的 GitHub 用户名！**

```bash
git init

git add .

git commit -m "Initial commit: Novel Library Management System"

git remote add origin https://github.com/Haruka041/novel-library.git

git branch -M main

git push -u origin main
```

## 关于密码认证

当执行 `git push` 时，如果要求输入密码，你需要使用 **Personal Access Token**，不是 GitHub 登录密码！

### 如何获取 Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 `Generate new token` → `Generate new token (classic)`
3. 设置说明：比如 "novel-library deploy"
4. 勾选权限：
   - ✅ `repo` （必须勾选）
5. 点击最下方的 `Generate token`
6. **复制生成的 token**（这是唯一一次看到，要保存好）

### 使用 Token 登录

当 Git 要求输入：
- **Username：** 你的 GitHub 用户名
- **Password：** 粘贴刚才复制的 Token（不是你的 GitHub 密码）

## 验证推送成功

1. 访问：`https://github.com/你的用户名/novel-library`
2. 应该能看到所有文件已经上传
3. 点击 `Actions` 标签，查看自动构建进度

## 下一步

推送成功后：
1. 等待 GitHub Actions 构建完成（3-5分钟）
2. 设置镜像为公开：
   - 访问：`https://github.com/你的用户名?tab=packages`
   - 点击 `novel-library` 包
   - `Package settings` → `Change visibility` → `Public`
3. 按照 [`QUICK_START.md`](QUICK_START.md) 在服务器部署

## 常见问题

### Q: 提示 "Git is not recognized"

**A:** 需要安装 Git
- 下载：https://git-scm.com/download/windows
- 安装后重新打开命令行

### Q: 推送失败，提示 "repository not found"

**A:** 
1. 确认仓库名称是 `novel-library`
2. 确认用户名拼写正确（区分大小写）
3. 确认已在 GitHub 创建了仓库

### Q: 推送失败，提示 "authentication failed"

**A:**
1. 使用 Personal Access Token 而非密码
2. 确认 Token 有 `repo` 权限
3. Token 可能过期，需要重新生成

### Q: 出现中文乱码

**A:** 在命令行执行：
```bash
chcp 65001
```
然后重新执行 Git 命令
