# 安装与使用

book-to-skill 提供两种安装方式：作为 Agent Skill 集成到 AI 助手环境中，或作为独立 CLI 工具直接使用。本章详细介绍安装流程、依赖管理、环境预检和基本使用方法。

## 两种安装方式

### 方式 1：作为 Agent Skill 安装

这是推荐的使用方式——将 book-to-skill 安装到 Agent 的 skills 目录后，AI 助手可直接调用该技能处理书籍文档。

**安装步骤**：

```bash
# 方式 A：HTTPS
git clone https://github.com/virgiliojr94/book-to-skill.git <skills-directory>/book-to-skill

# 方式 B：SSH
git clone git@github.com:virgiliojr94/book-to-skill.git <skills-directory>/book-to-skill
```

**支持的 Agent 目录位置**：

| Agent 平台 | Skill 安装路径 | 优先级 |
|-----------|---------------|--------|
| GitHub Copilot CLI | `~/.copilot/skills/` | 用户级 |
| Copilot CLI / Amp（跨 Agent） | `~/.agents/skills/` | 用户级 |
| Claude Code | `~/.claude/skills/` | 用户级 |
| 项目级（任意 Agent） | `.github/skills/` | 项目级 |
| 项目级（Claude） | `.claude/skills/` | 项目级 |
| 项目级（通用） | `.agents/skills/` | 项目级 |

> **Skill 位置优先级**：项目级目录（`.github/skills/`、`.claude/skills/`、`.agents/skills/`）优先级高于用户级目录。Agent 会按上表顺序查找，找到即加载。

**Skill 目录结构**：安装后，生成的 Skill 输出到 `<SKILLS_HOME>/<slug>/`，包含以下文件：

```
<slug>/
├── SKILL.md         # 核心框架 + 章节/主题索引（约 4K tokens）
├── chapters/*.md    # 按需加载的章节文件
├── glossary.md      # 术语表
├── patterns.md      # 技术模式
└── cheatsheet.md    # 决策规则/决策树/权衡/识别信号
```

架构细节参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md)。

### 方式 2：作为独立 CLI 工具安装

如果需要直接在命令行使用提取功能，可通过 pip 安装：

**PyPI 安装（发布后可用）**：

```bash
pip install book-to-skill
```

**源码安装（开发模式）**：

```bash
git clone https://github.com/virgiliojr94/book-to-skill.git
cd book-to-skill
pip install -e .
```

安装后可直接使用 `book-to-skill` 命令，或通过 `scripts/extract.py` 脚本调用（保持向后兼容）：

```bash
# 方式 A：通过 pip 安装的命令
book-to-skill --check

# 方式 B：通过源码目录的脚本
python3 scripts/extract.py --check
```

CLI 入口配置参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/pyproject.toml#L13-L14](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/pyproject.toml#L13-L14)。

## 可选依赖说明

book-to-skill 采用"核心轻量 + 可选依赖"设计，核心功能仅依赖 Python 标准库，各种格式的解析器作为可选依赖按需要安装。

### 依赖分组

根据 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/pyproject.toml#L16-L30](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/pyproject.toml#L16-L30)，可选依赖分为以下几组：

| extra 分组 | 包含包 | 支持格式 | 用途说明 |
|-----------|--------|---------|---------|
| `epub` | `ebooklib`, `beautifulsoup4` | EPUB | 高质量 EPUB 解析，缺失时回退到 stdlib zipfile 解析 |
| `pdf` | `pypdf`, `pdfminer.six` | PDF（文本型） | Python PDF 解析器，需配合 `pdftotext`（poppler-utils）获得最佳效果 |
| `docx` | `python-docx` | DOCX | Word 文档解析，缺失时回退到 stdlib ZIP/XML 解析 |
| `rtf` | `striprtf` | RTF | RTF 格式解析，缺失时回退到基础正则清理 |
| `technical` | `docling` | PDF（技术型） | 支持表格、代码、公式的布局感知提取，仅 `--mode technical` 时使用 |
| `all` | 上述所有包 | 全部格式 | 一键安装所有可选依赖 |

**系统依赖**：

| 工具 | 所属包 | 支持格式 | 说明 |
|-----|--------|---------|------|
| `pdftotext` | poppler-utils | PDF | 最快的 PDF 文本提取（推荐） |
| `ebook-convert` | Calibre | MOBI/AZW/AZW3 | **必需**，无回退方案——MOBI 格式必须安装 Calibre |

安装示例：

```bash
# 仅安装 PDF 支持
pip install "book-to-skill[pdf]"

# 安装 EPUB + DOCX 支持
pip install "book-to-skill[epub,docx]"

# 安装全部依赖（推荐用于完整功能）
pip install "book-to-skill[all]"

# 技术书籍模式（需要 docling）
pip install "book-to-skill[technical]"
```

模块名到 pip 包名的映射参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L26-L34](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L26-L34)。

### 依赖探测模式

book-to-skill 运行时会自动探测依赖是否安装，并根据配置决定是否自动安装缺失依赖。共有三种模式，通过 `--install-missing` 参数或 `BOOK_SKILL_INSTALL_MISSING` 环境变量控制。

实现细节参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L102-L116](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L102-L116)。

| 模式值 | 命令行参数 | 环境变量值 | 行为 |
|-------|-----------|-----------|------|
| `ask`（默认） | `--install-missing ask` | `ask` / 未设置 | 交互模式下询问用户是否安装；非交互模式使用回退解析器 |
| `yes` | `--install-missing` 或 `--install-missing yes` | `yes` / `1` / `true` / `y` / `install` | 自动安装缺失的 Python 包 |
| `no` | `--no-install-missing` 或 `--install-missing no` | `no` / `0` / `false` / `n` / `fallback` / `skip` | 不安装，直接使用回退方案（若无回退则失败） |

**设置示例**：

```bash
# 环境变量方式（永久生效）
export BOOK_SKILL_INSTALL_MISSING=yes

# 命令行方式（单次生效）
book-to-skill book.pdf --install-missing yes
book-to-skill book.pdf --no-install-missing
```

## Skill 位置优先级表

根据架构设计，Agent 查找 Skill 时按以下优先级顺序搜索（项目级优先于用户级）：

| 优先级 | 路径 | 作用域 | 典型使用场景 |
|-------|------|--------|-------------|
| 1（最高） | `.github/skills/` | 当前项目 | GitHub Copilot 项目级技能 |
| 2 | `.claude/skills/` | 当前项目 | Claude Code 项目级技能 |
| 3 | `.agents/skills/` | 当前项目 | 通用跨 Agent 项目级技能 |
| 4 | `~/.copilot/skills/` | 当前用户 | GitHub Copilot 用户级全局技能 |
| 5 | `~/.agents/skills/` | 当前用户 | 跨 Agent 用户级全局技能 |
| 6（最低） | `~/.claude/skills/` | 当前用户 | Claude Code 用户级全局技能 |

> **设计原则**：项目级 Skill 可以覆盖用户级同名 Skill，便于团队在特定仓库中定制技能行为。

优先级来源参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L35-L39](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L35-L39)。

## 环境预检

首次使用前，建议运行依赖检查命令验证环境是否就绪：

```bash
# CLI 安装方式
book-to-skill --check

# 源码方式（未 pip install）
python3 scripts/extract.py --check
```

检查实现参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L216-L289](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L216-L289)。

**输出示例**：

```
book-to-skill — dependency check

  PDF (text-heavy)
      ✓ python: pypdf
      ✓ python: pdfminer.six
      ✓ system: pdftotext (poppler-utils)
      → ready — any one of pdftotext / pypdf / pdfminer is enough

  PDF (technical: tables, code, formulas)
      ✗ python: docling
      → fallback available (install for best quality) — needed only for --mode technical; otherwise falls back to the text chain

  EPUB
      ✓ python: ebooklib
      ✓ python: beautifulsoup4
      → ready — falls back to a stdlib zipfile parser if missing

  DOCX
      ✓ python: python-docx
      → ready — falls back to a stdlib ZIP/XML parser if missing

  HTML
      ✓ python: beautifulsoup4
      → ready — falls back to the stdlib html.parser if missing

  RTF
      ✗ python: striprtf
      → fallback available (install for best quality) — falls back to a basic regex cleanup if missing

  MOBI / AZW / AZW3
      ✗ system: ebook-convert (Calibre)
      → MISSING — required, no fallback — Calibre is required for these formats

To enable the best extractor for every format, install the missing pieces:

  python3 -m pip install docling striprtf
  # Calibre: install Calibre: https://calibre-ebook.com/download

Note: missing Python packages are optional — most formats fall back to a
stdlib parser. Calibre is the only hard requirement, and only for MOBI/AZW files.
```

**状态说明**：

- `✓ ready`：依赖已就绪，可获得最佳提取质量
- `fallback available`：缺少可选依赖，将使用标准库回退方案（质量可能略低）
- `MISSING — required, no fallback`：必需依赖缺失（仅 Calibre），对应格式无法处理

## 基本使用示例

### 提取单本书

最简单的使用方式——直接传入文件路径：

```bash
book-to-skill book.pdf
```

提取完成后，输出到临时目录（默认 `$TMPDIR/book_skill_work/`）：

- `full_text.txt`：提取并合并后的全文本
- `metadata.json`：元数据（页数、字数、token 估算、章节检测等）

**输出示例**：

```
Extracting PDF: book.pdf
Mode: text — using pdftotext...
Trying pdftotext... OK

Extraction complete:
   Sources : 1 processed
   Size    : 2.35 MB
   Pages   : 248
   Words   : 87,432
   Tokens  : ~116K
   Chapters: 12 detected overall
   ToC     : yes

   Text -> /tmp/book_skill_work/full_text.txt
   Meta -> /tmp/book_skill_work/metadata.json
```

### 指定输出目录

通过 `BOOK_SKILL_WORKDIR` 环境变量自定义输出位置：

```bash
# Linux/macOS
BOOK_SKILL_WORKDIR=./output book-to-skill book.pdf

# Windows PowerShell
$env:BOOK_SKILL_WORKDIR = "./output"; book-to-skill book.pdf
```

输出路径配置参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L5-L12](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L5-L12)。

### 技术书籍模式（表格、代码、公式）

对于包含大量表格、代码块、数学公式的技术书籍，使用 `--mode technical` 启用 Docling 布局感知提取：

```bash
# 先确保安装了 technical 依赖
pip install "book-to-skill[technical]"

# 使用 technical 模式提取
book-to-skill technical-book.pdf --mode technical
```

**模式对比**：

| 模式 | 提取器 | 适用场景 | 特点 |
|-----|--------|---------|------|
| `text`（默认） | pdftotext → pypdf → pdfminer 链 | 小说、散文、纯文本书籍 | 速度快，纯文本提取 |
| `technical` | Docling（优先）→ text 链回退 | 技术书籍、教材、论文 | 保留表格结构、代码格式、公式布局 |

技术模式提取流程参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L484-L526](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L484-L526)。

### 批量处理与 glob 模式

支持批量处理多个文件、目录或 glob 模式：

```bash
# 处理多个文件
book-to-skill book1.pdf book2.epub book3.docx

# 处理目录下所有支持的文件
book-to-skill ./books/

# 使用 glob 模式
book-to-skill "./books/**/*.pdf"

# 混合使用
book-to-skill intro.pdf ./chapters/ "./appendixes/*.docx"
```

支持的格式列表参见 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L19-L24](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L19-L24)：

```
.pdf, .epub, .docx, .rtf, .txt, .text, .md, .markdown, .rst, .adoc, .asciidoc,
.html, .htm, .xhtml, .mobi, .azw, .azw3
```

---

**事实来源**：本章节基于以下事实编号 F-036, F-037, F-038
