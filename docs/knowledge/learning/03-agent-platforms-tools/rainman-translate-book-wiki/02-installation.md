---
id: "rainman-translate-book-wiki-02"
title: "安装部署指南"
source: "https://mp.weixin.qq.com/s/99dnIuSUL4WHkm-_UzQYAw"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/rainman-translate-book-wiki/02-installation.toml"
---
# 安装部署指南

Rainman Translate Book 依赖多个外部工具，安装过程需要一定的技术基础。本章提供完整的分平台安装指南。

---

## 环境要求

| 依赖项 | 用途 | 最低版本要求 |
|---|---|---|
| Claude Code CLI | 核心运行环境（Skill 宿主） | 最新版 |
| Calibre | 电子书格式转换（ebook-convert 命令） | 最新版 |
| Pandoc | HTML 与 Markdown 互转 | 最新版 |
| Python 3 | 脚本运行环境 | 3.8+ |
| pypandoc（Python 包） | Python 调用 Pandoc | 最新版 |
| beautifulsoup4（Python 包） | HTML 解析 | 最新版 |

**关键要求**：`ebook-convert` 命令（Calibre 提供）和 `pandoc` 命令必须在系统 PATH 中可直接调用。

---

## 分平台安装步骤

### macOS

```bash
# 1. 安装 Claude Code CLI
brew install anthropic/tap/claude-code

# 2. 安装 Calibre（或从 calibre-ebook.com 下载安装包）
brew install --cask calibre

# 3. 安装 Pandoc
brew install pandoc

# 4. 安装 Python 包
pip install pypandoc
pip install beautifulsoup4
```

### Linux (Ubuntu/Debian)

```bash
# 1. 安装 Claude Code CLI（参考 Anthropic 官方文档）

# 2. 安装 Calibre
sudo apt install calibre

# 3. 安装 Pandoc
sudo apt install pandoc

# 4. 安装 Python 包
pip install pypandoc
pip install beautifulsoup4
```

### Windows

```powershell
# 1. 安装 Claude Code CLI（参考 Anthropic 官方文档）

# 2. 安装 Calibre
# 从 https://calibre-ebook.com 下载 Windows 安装包并安装

# 3. 安装 Pandoc
# 从 https://pandoc.org/installing.html 下载 Windows 安装包并安装

# 4. 安装 Python 包
pip install pypandoc
pip install beautifulsoup4
```

> **注意**：Windows 下安装 Calibre 和 Pandoc 后，需确保它们的安装目录已添加到系统 PATH 环境变量中。如果安装后命令行无法识别 `ebook-convert` 或 `pandoc` 命令，请手动添加路径。

---

## 三种 Skill 安装方式

### 方式一：npx（推荐，最省事）

```bash
npx skills add deusyu/translate-book -a claude-code -g
```

这是最简便的方式，npx 会自动处理下载和安装。

### 方式二：ClawHub

```bash
clawhub install translate-book
```

如果你已经安装了 ClawHub，可以使用此命令一键安装。

### 方式三：Git Clone（手动安装）

```bash
git clone https://github.com/deusyu/translate-book.git ~/.claude/skills/translate-book
```

直接将仓库克隆到 Claude Code 的 Skills 目录下。注意路径必须在 `~/.claude/skills/` 下，否则 Claude Code 无法识别。

---

## 验证安装

安装完成后，可通过以下方式验证：

1. **验证依赖工具**：

```bash
# 验证 Calibre
ebook-convert --version

# 验证 Pandoc
pandoc --version

# 验证 Python 包
python3 -c "import pypandoc; import bs4; print('OK')"
```

2. **验证 Skill 安装**：

在 Claude Code 终端中输入 `/` 查看可用命令，如果能看到 `/translate-book`，说明 Skill 已成功安装。

---

## 常见安装问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| `ebook-convert: command not found` | Calibre 未安装或未加入 PATH | 重新安装 Calibre 或手动添加 PATH |
| `pandoc: command not found` | Pandoc 未安装或未加入 PATH | 重新安装 Pandoc 或手动添加 PATH |
| `/translate-book` 命令不可见 | Skill 未安装到正确目录 | 检查 `~/.claude/skills/translate-book/` 目录是否存在 |
| pypandoc 报错 | pypandoc 依赖的 Pandoc 版本不匹配 | 更新 Pandoc 到最新版 |