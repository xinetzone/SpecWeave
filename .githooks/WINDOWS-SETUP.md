# Windows 开发者快速上手指南

> 本文档帮助 Windows 用户在 5 分钟内完成 Git 钩子配置，使 `git commit` 时自动运行敏感信息检测。

---

## 前置要求

| 软件 | 最低版本 | 检查命令 |
|------|---------|---------|
| Git for Windows | 2.9+（推荐 2.30+） | `git --version` |
| Python | 3.8+ | `python --version` |

---

## 第一步：确认 Git 和 Python 已安装

打开 **PowerShell** 或 **CMD**，执行：

```powershell
git --version
python --version
```

如果显示版本号（如 `git version 2.53.0` 和 `Python 3.13.9`），说明已安装。如果提示"不是内部或外部命令"，需要先安装：

- **Git**: 从 https://git-scm.com/download/win 下载安装，安装时保持默认选项即可
- **Python**: 从 https://www.python.org/downloads/ 下载安装，**务必勾选 "Add Python to PATH"**

### 关于 Python 的常见情况

Windows 上可能有多个 Python，请确保 Git Bash 能找到正确的 Python：

| 安装方式 | Python 命令 | Git Bash 是否自动识别 |
|---------|------------|-------------------|
| python.org 官方安装 | `python` | ✅ 是 |
| Anaconda/Miniconda | `python` | ✅ 是 |
| Microsoft Store 版 | `python3` | ⚠️ 需要额外配置 |
| WindowsApps 存根 | `python` | ❌ 可能打开应用商店 |

**验证 Git Bash 是否能找到 Python**：
1. 右键项目文件夹 → "Open Git Bash here"
2. 执行：`python --version`
3. 如果显示版本号，说明正常；如果报错，见下方"常见问题"

---

## 第二步：一键配置钩子

在项目根目录下打开 PowerShell，执行：

```powershell
python .githooks/setup-hooks.py
```

成功后会看到：
```
✅ 已配置当前仓库使用 .githooks 目录
✅ pre-commit 钩子已就绪
```

> 💡 这一步只需要执行一次，之后 `git pull` 获取最新代码时钩子会自动更新。

---

## 第三步：验证钩子是否生效

### 测试1：正常提交（干净代码应通过）

创建一个测试文件并提交：

```powershell
# 在 Git Bash 中执行
echo 'print("hello")' > test_hook.py
git add test_hook.py
git commit -m "test: verify hook works"
```

你应该看到：
```
🔒 敏感信息检测 (Pre-commit Hook)
✅ 未检测到敏感信息。
⚡ 并发模块安全检查 (Pre-commit Hook)
✅ 未检测到并发安全问题，可以提交。
[master xxxxxxx] test: verify hook works
```

提交成功后删除测试文件：
```powershell
git rm test_hook.py
git commit -m "chore: remove test file"
```

### 测试2：拦截敏感信息（应阻断提交）

创建一个包含假 API Key 的文件：

```powershell
echo 'api_key = "sk-YOUR-API-KEY-HERE-REPLACE-ME"' > test_secret.py
git add test_secret.py
git commit -m "test: should be blocked"
```

你应该看到：
```
❌ 检测到 1 项高风险敏感信息，提交已阻断！
```

提交被阻止后，删除测试文件：
```powershell
rm test_secret.py
git reset HEAD test_secret.py
```

---

## 使用 Git GUI 工具？

如果你使用 **VS Code**、**SourceTree**、**TortoiseGit**、**GitHub Desktop** 等 GUI 工具提交代码：

| GUI 工具 | 钩子是否生效 | 说明 |
|---------|------------|------|
| VS Code 内置 Git | ✅ 生效 | 使用 Git Bash 环境调用钩子 |
| GitHub Desktop | ✅ 生效 | 同上 |
| SourceTree | ✅ 生效 | 需在设置中指定 Git 为系统 Git |
| TortoiseGit | ⚠️ 需配置 | 见下方说明 |
| IDEA / PyCharm | ✅ 生效 | 使用内置 Git 可执行文件 |

### TortoiseGit 配置

1. 打开 TortoiseGit → Settings → General
2. 将 "Git.exe path" 设置为 `C:\Program Files\Git\bin\git.exe`（不是 `cmd\git.exe`）
3. 在 Hooks 脚本设置中确保启用了 shell 钩子

---

## 环境变量用法（临时跳过）

### 在 PowerShell 中临时跳过

```powershell
# 完全跳过敏感信息检查
$env:SENSITIVE_CHECK_SKIP=1; git commit -m "紧急修复"; $env:SENSITIVE_CHECK_SKIP=""

# 只警告不阻断（看到风险但允许提交）
$env:SENSITIVE_CHECK_WARN_ONLY=1; git commit -m "紧急修复"; $env:SENSITIVE_CHECK_WARN_ONLY=""
```

### 在 Git Bash 中临时跳过

```bash
# 完全跳过
SENSITIVE_CHECK_SKIP=1 git commit -m "紧急修复"

# 只警告不阻断
SENSITIVE_CHECK_WARN_ONLY=1 git commit -m "紧急修复"
```

### 在 CMD 中临时跳过

```cmd
set SENSITIVE_CHECK_SKIP=1 && git commit -m "紧急修复" && set SENSITIVE_CHECK_SKIP=
```

---

## 常见问题

### Q1: 提交时提示 "python: command not found"

**原因**: Git Bash 的 PATH 中没有 Python。

**解决方法**:

方法A（推荐）— 将 Python 目录添加到 Windows 系统 PATH：
1. 找到 Python 安装路径（执行 `where python` 查看，如 `D:\Users\xxx\anaconda3\python.exe`）
2. 将 Python 所在目录（如 `D:\Users\xxx\anaconda3`）和 Scripts 子目录添加到系统环境变量 PATH
3. 重启所有终端窗口

方法B — 创建符号链接（Git Bash 专用）：
在 Git Bash 中执行：
```bash
ln -s "/c/Users/你的用户名/AppData/Local/Programs/Python/Python312/python.exe" /usr/bin/python
```

方法C — 重新安装 Python：
运行 Python 安装程序，选择 "Modify"，确保勾选 "Add Python to environment variables"。

### Q2: 钩子脚本没有执行权限

**原因**: Windows 文件系统不支持 Unix 执行权限位，但 Git for Windows 通常会自动处理。

**解决方法**: 在 Git Bash 中执行：
```bash
chmod +x .githooks/pre-commit
```

### Q3: 使用 Microsoft Store 版 Python 导致问题

**症状**: 输入 `python` 打开 Microsoft Store，或在 Git Bash 中找不到 python3。

**解决方法**:
1. 打开 Windows 设置 → 应用 → 高级应用设置 → 应用执行别名
2. 关闭 "应用安装程序 - python.exe" 和 "python3.exe"
3. 安装 python.org 官方版本

### Q4: 想彻底禁用钩子

```powershell
# 仅禁用本仓库
python .githooks/setup-hooks.py --uninstall

# 临时跳过所有钩子（包括本项目的其他检查）
git commit --no-verify -m "跳过所有检查"
```

### Q5: GUI 工具中提交不触发钩子

**原因**: GUI 工具可能使用了内置的 Git 或没有正确调用 shell。

**解决方法**:
- VS Code: 设置中搜索 "git.path"，设置为 `C:\\Program Files\\Git\\bin\\git.exe`
- 确保使用 Git for Windows 的 `bin\git.exe`（不是 `cmd\git.exe` 或 GUI 内置 Git）

---

## 钩子检查了什么？

每次 `git commit` 时自动运行两项检查：

1. **🔒 敏感信息检测**：检查密码、API密钥、Token、手机号、邮箱、数据库连接串、个人路径、私钥等
2. **⚡ 并发模块安全检查**（仅Python文件）：超时、幂等、边界、防御、配置、国际化六维检查

发现高风险问题会**阻断提交**，中风险问题仅警告不阻断。

---

## 更新钩子

钩子文件在 `.githooks/` 和 `.agents/scripts/hooks/` 目录，随代码一起版本管理。
执行 `git pull` 后自动获得最新版本，无需重新配置。
