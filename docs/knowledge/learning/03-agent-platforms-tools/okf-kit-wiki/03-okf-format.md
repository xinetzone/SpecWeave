---
type: Wiki Tutorial

id: "okf-kit-wiki-03"
title: "okf-kit 完全指南 — OKF 格式与 Bundle 结构"
source: "https://github.com/vinodborole/okf-kit/blob/main/okf_kit/okf.py"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/03-okf-format.toml"
---
# okf-kit 完全指南 — OKF 格式与 Bundle 结构

> 一句话摘要：OKF（Open Knowledge Format v0.1）将知识表示为"目录中带 YAML frontmatter 的 Markdown 文件"，每个非保留 Markdown 文件必须包含 `type` 字段标识概念类型，每个目录有 `index.md` 供 Agent 渐进式导航，state.json 存储爬取元数据用于增量同步。

---

## 1. OKF 规范核心原则

OKF 的设计目标是让知识对 Agent 而言像文件系统对人类一样自然——无需特殊 SDK、无需运行时服务、无需网络请求，只需标准文件读取即可获取和导航知识。

三条核心原则：

| 原则 | 说明 |
|------|------|
| **文件原生** | 知识以普通 Markdown 文件存储，可用任何文本编辑器、git、zip 处理 |
| **渐进式导航** | 目录索引让 Agent 可以从根开始逐层浏览，无需猜测路径 |
| **自描述** | 每个文件通过 frontmatter 声明自己的类型和元数据 |

---

## 2. Bundle 目录结构

一个典型的 OKF bundle 目录结构如下：

```
my-docs/                           # Bundle 根目录
├── index.md                       # 根目录索引（入口文件）
├── log.md                         # 构建日志（保留文件，不算概念）
├── overview.md                    # 根级概念页面
│
├── pages/                         # 概念页面目录（由 writer.py 生成）
│   ├── index.md                   # pages/ 目录索引
│   ├── guide/                     # 子目录（对应网站路径段）
│   │   ├── index.md               # guide/ 目录索引
│   │   ├── getting-started.md     # 概念文件
│   │   └── installation.md        # 概念文件
│   └── api/
│       ├── index.md
│       └── reference.md
│
└── .okf-kit/                      # okf-kit 元数据目录
    └── state.json                 # 状态文件（URL映射、content hash、链接边等）
```

### 2.1 结构规则

1. **根目录必须包含 `index.md`**：作为 Agent 入口点
2. **每个子目录必须包含 `index.md`**：列出该目录的内容
3. **保留文件名**：`index.md`（目录列表）和 `log.md`（构建日志）不作为概念文件
4. **非保留 `.md` 文件**：即概念文件，必须有合法的 frontmatter
5. **`.okf-kit/` 目录**：okf-kit 的内部状态目录，不纳入 OKF 规范
6. **无二进制文件**：Bundle 是纯文本 Markdown（图片不嵌入，保持为链接）

---

## 3. index.md — 目录索引文件

### 3.1 作用

每个目录的 `index.md` 是 Agent 导航的关键。它列出该目录下的所有子目录和概念文件，使 Agent 不需要猜测文件路径即可浏览 bundle。

### 3.2 格式

```markdown
# / — directory listing

- [pages/](/pages/index.md)
- [overview](/overview.md)
```

子目录条目以 `/` 结尾并链接到子目录的 `index.md`：

```markdown
# /pages/guide — directory listing

Subdirectories:
- [advanced/](/pages/guide/advanced/index.md)

Files:
- [getting-started](/pages/guide/getting-started.md)
- [installation](/pages/guide/installation.md)
```

### 3.3 导航模式（渐进式展开）

Agent 从根索引开始导航：

```
读取 /index.md → 发现有 pages/ 子目录
→ 读取 /pages/index.md → 发现有 guide/ 子目录
→ 读取 /pages/guide/index.md → 发现 getting-started.md
→ 读取 /pages/guide/getting-started.md → 获取目标内容
```

这类似于人类在文件管理器中双击文件夹逐层深入的过程。Agent 永远不需要猜测路径——每个目录的 index.md 会告诉它有什么可用。

---

## 4. 概念文件（Concept Markdown）

### 4.1 Frontmatter 字段

每个概念文件（非 index.md/log.md 的 .md 文件）开头必须有 YAML frontmatter：

```yaml
---
type: concept              # 必需：OKF 概念类型
title: "Getting Started"   # 推荐：页面标题
description: "..."         # 推荐：meta description 或摘要
source_url: "https://..."  # okf-kit 添加：原始URL
crawled_at: "2026-08-18T14:30:22Z"  # okf-kit 添加：爬取时间
content_hash: "sha256:..." # okf-kit 添加：内容hash（用于增量同步）
path_depth: 3              # okf-kit 添加：BFS深度
resource:                  # 可选：关联资源
  - url: "https://..."
    rel: "source"
---

# 页面标题

正文内容（Markdown 格式）...
```

### 4.2 type 字段（必需）

`type` 是 OKF 规范唯一强制要求的字段。合法值包括：

| type 值 | 含义 | okf-kit 使用情况 |
|---------|------|----------------|
| `concept` | 通用概念页面 | ✅ 默认类型（所有爬取的页面） |
| `tutorial` | 教程 | 可由 LLM 富化标注 |
| `reference` | 参考文档 | 可由 LLM 富化标注 |
| `howto` | How-to 指南 | 可由 LLM 富化标注 |
| `overview` | 概述/概览 | 可由 LLM 富化标注 |
| `faq` | 常见问题 | 可由 LLM 富化标注 |
| `index` | 目录索引 | ❌ index.md 使用，但不作为概念 |

### 4.3 正文格式

正文是标准 Markdown，okf-kit 保留以下结构：

- **标题层级**：`<h1>`~`<h6>` 转换为 `#`~`######`
- **代码块**：`<pre><code>` → fenced code block（```` ``` ````）
- **内联代码**：`<code>` → `` `code` ``
- **粗体/斜体**：`<strong>`/`<em>` → `**bold**`/`*italic*`
- **链接**：`<a href="...">` → `[text](url)`
- **表格**：HTML 表格 → Markdown 表格
- **列表**：`<ul>/<ol>` → `-`/`1.` 列表
- **段落**：`<p>` 转换为普通段落，保留段落间距

### 4.4 内部链接处理

okf-kit 会自动将页面间的链接转换为相对路径链接：

- 同域页面链接转换为 bundle 内的相对 Markdown 路径
- 外部链接保持原始 URL
- 这使得 bundle 是自包含的——内部引用不需要网络连接

---

## 5. log.md — 构建日志

构建日志记录爬取过程中的信息和错误：

```markdown
# Build Log — my-docs

- Seed: https://docs.example.com
- Started: 2026-08-18T14:30:00Z
- Max depth: 3, Max pages: 200

## Pages Crawled

- ✅ https://docs.example.com/ → /index.md
- ✅ https://docs.example.com/guide → /pages/guide/index.md
- ⚠️ https://docs.example.com/old-page → skipped (short content, possibly JS-rendered)
- ❌ https://docs.example.com/missing → HTTP 404

## Summary

- Crawled: 42 pages
- Skipped: 3
- Errors: 1
- Duration: 45s
```

---

## 6. state.json — 状态文件

`.okf-kit/state.json` 是 okf-kit 的核心元数据文件，存储增量同步所需的所有状态。

### 6.1 顶层结构

```json
{
  "version": "0.3.3",
  "okf_version": "0.1",
  "name": "my-docs",
  "title": "Example Documentation",
  "root_url": "https://docs.example.com",
  "path_prefix": "/",
  "max_depth": 3,
  "max_pages": 200,
  "created_at": "2026-08-18T14:30:00Z",
  "updated_at": "2026-08-18T14:35:00Z",
  "page_count": 42,
  "pages": { ... },
  "url_to_path": { ... },
  "links": { ... },
  "config": { ... }
}
```

### 6.2 pages 字段

`pages` 是一个以相对路径为 key 的字典，记录每个页面的详细信息：

```json
{
  "pages": {
    "/pages/guide/getting-started.md": {
      "url": "https://docs.example.com/guide/getting-started",
      "title": "Getting Started",
      "description": "Learn how to get started with Example",
      "content_hash": "sha256:a1b2c3d4e5f6...",
      "depth": 2,
      "crawled_at": "2026-08-18T14:31:00Z",
      "status": "ok",
      "word_count": 1523
    }
  }
}
```

### 6.3 url_to_path 字段

`url_to_path` 记录原始 URL 到 bundle 内相对路径的映射：

```json
{
  "url_to_path": {
    "https://docs.example.com/": "/index.md",
    "https://docs.example.com/guide/getting-started": "/pages/guide/getting-started.md",
    "https://docs.example.com/guide/installation/": "/pages/guide/installation.md"
  }
}
```

这是 URL→路径映射的反向索引，sync 时用它判断哪些 URL 是新的、哪些已存在。

### 6.4 links 字段

`links` 记录页面间的链接关系（邻接表），用于知识图谱可视化：

```json
{
  "links": {
    "/index.md": [
      "/pages/guide/index.md",
      "/overview.md"
    ],
    "/pages/guide/getting-started.md": [
      "/pages/guide/installation.md",
      "/pages/api/reference.md"
    ]
  }
}
```

### 6.5 content_hash 字段

`content_hash` 是每个页面 Markdown 正文（不含 frontmatter）的 SHA-256 哈希值。sync 通过对比新旧 hash 判断页面是否变更：

```python
# sync.py 中的核心判断逻辑
old_hash = old_state["pages"].get(path, {}).get("content_hash")
new_hash = compute_hash(new_markdown_body)
if old_hash != new_hash:
    # 页面已变更，需要重写
```

---

## 7. URL 到文件路径的映射

mapper.py 负责将网站 URL 转换为 bundle 内的文件路径。这是 okf-kit 的核心逻辑之一。

### 7.1 映射规则

| URL 特征 | 映射规则 | 示例 URL | 映射路径 |
|---------|---------|---------|---------|
| 根路径/首页 | → `/index.md` | `https://docs.example.com/` | `/index.md` |
| 路径尾部 `/` | 视为目录页 → `<path>/index.md` | `.../guide/` | `/pages/guide/index.md` |
| 无扩展名路径 | 视为页面 → `<path>.md` | `.../guide/getting-started` | `/pages/guide/getting-started.md` |
| `.html`/`.htm` | 去掉扩展名 → `<path>.md` | `.../page.html` | `/pages/page.md` |
| 含 query 参数 | 参数 hash 后缀 → `<path>__<hash>.md` | `.../search?q=api` | `/pages/search__a1b2.md` |
| 保留文件名冲突 | 添加后缀避让 | `.../index`（非目录） | `/pages/index__page.md` |
| 路径段过长 | 截断 | `.../a/b/c/d/e/f/g` | `/pages/a/b/c/d/e/f/g.md`（受 max_depth 限制） |

### 7.2 pages/ 前缀

除了根级页面（如首页映射到 `/index.md`），所有页面都放在 `pages/` 目录下。这是 okf-kit 的约定，而非 OKF 规范要求，但它确保 bundle 根目录整洁。

### 7.3 保留名避让

如果 URL 的路径段恰好是保留文件名（index, log），mapper 会添加 `__page` 后缀：

| URL | 避让前（冲突） | 避让后 |
|-----|--------------|--------|
| `.../index` | `/pages/index.md`（与目录索引冲突） | `/pages/index__page.md` |
| `.../log` | `/log.md`（与构建日志冲突） | `/pages/log__page.md` |

---

## 8. Bundle 验证规则

`okf validate` 执行以下检查：

| 检查 | 规则 | 级别 |
|------|------|------|
| 根 index.md 存在 | `<bundle>/index.md` 必须存在 | Error |
| Frontmatter 可解析 | 每个 `.md` 文件的 frontmatter 必须是合法 YAML | Error |
| type 字段存在 | 非保留 `.md` 文件必须有 `type` 字段 | Error |
| type 枚举合法 | type 必须是 OKF v0.1 定义的合法值 | Warning |
| title 字段存在 | 非保留 `.md` 文件应有 `title` 字段 | Warning |
| 内部链接有效 | 正文中的相对链接目标文件必须存在 | Warning |
| 目录索引存在 | 每个有 `.md` 文件的子目录应有 `index.md` | Warning |
| state.json 存在 | `.okf-kit/state.json` 应存在（影响 sync） | Warning |

---

## 9. 手动创建 Bundle

除了 `okf build`，你也可以手动创建符合 OKF 规范的 bundle：

```bash
mkdir my-knowledge
cd my-knowledge

# 1. 创建根索引
cat > index.md << 'EOF'
---
type: index
title: "My Knowledge Base"
---
# My Knowledge Base

- [concepts/](/concepts/index.md)
EOF

# 2. 创建概念目录
mkdir concepts
cat > concepts/index.md << 'EOF'
# /concepts — directory listing

- [python](/concepts/python.md)
EOF

# 3. 创建概念文件
cat > concepts/python.md << 'EOF'
---
type: concept
title: "Python 入门"
description: "Python 编程语言基础知识"
---

# Python 入门

Python 是一种解释型、高级编程语言...
EOF

# 4. 验证
okf validate .
```

---

## 10. Bundle 与 Git

由于 okf-kit 的增量同步机制保证未变更页面字节级一致，bundle 非常适合纳入 git 版本控制：

```bash
cd my-docs
git init
git add -A
git commit -m "Initial bundle: 42 pages"

# 一段时间后同步
okf sync .
git diff              # 只看到变更页面的差异
git add -A && git commit -m "Sync: +3 -1 =5"
```

这使得知识库的变更可以像代码一样被 review、分支、回滚。

---

- [← 上一章：CLI 命令参考](02-cli-reference.md) | [下一章：核心架构](04-core-architecture.md) →
