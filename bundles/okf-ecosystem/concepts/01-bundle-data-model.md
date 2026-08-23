---
type: Concept
title: Bundle 数据模型与语义边
description: OKF bundle 的目录结构、Page/PageRecord 数据类、frontmatter 规范、URL 映射、content_hash 与边计算策略
tags: [okf, bundle, data-model, frontmatter, state.json, edges, content-hash]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: okf-kit-source
    resource: "/references/okf-kit-source.md"
    title: okf-kit 源码
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# Bundle 数据模型与语义边

OKF 知识包（bundle）的核心设计哲学是「纯文件即数据库」。它不使用 SQLite、不使用向量数据库，而是以 Markdown 文件加 YAML frontmatter 构成知识表示，配合单个 `state.json` 记录全局索引与边表。这种设计使得 bundle 可 zip 打包、可离线分发、可人工阅读，同时被 MCP、Chat、HTTP、桌面四种消费端复用。

## 目录结构

一个构建完成的 bundle 目录结构如下：

```text
my-site-okf/
├── index.md              # 根索引（自动生成）
├── log.md                # 变更日志（按日期分节）
├── pages/                # 网页内容，每个 URL 对应一个 .md 文件
│   ├── index.md          # 首页（经 dodge_reserved 实际为 home.md）
│   ├── about.md
│   └── docs/
│       ├── guide.md
│       └── api.md
└── .okf-kit/
    └── state.json        # 全局元数据、页面清单、边表
```

有两个保留文件名被特殊处理 [F-060]：`index.md` 和 `log.md`。当 URL 映射结果恰好是这两个名称时，`dodge_reserved()` 函数会将 `index.md` 重命名为 `home.md`，`log.md` 重命名为 `history.md`，以避免与自动生成的根索引和日志文件冲突 [F-062]。

## Page 与 PageRecord 数据类

`Page` 是爬取阶段的内存数据结构 [F-090]，使用 `@dataclass` 装饰器，字段如下 [F-091~F-094]：

```python
@dataclass
class Page:
    url: str
    title: str | None
    markdown: str
    description: str | None = None
    links: list[str] = field(default_factory=list)
    content_links: list[str] | None = None
    depth: int = 0
```

- `url`：规范化后的页面 URL
- `title`/`description`：从 HTML `<title>` 和 `<meta name="description">` 提取
- `markdown`：清洗后的正文 Markdown
- `links`：全页所有超链接（含导航栏、页脚等）
- `content_links`：正文区域链接（排除 nav/header/footer/aside），为 None 表示未提取
- `depth`：BFS 爬取深度

`PageRecord` 是写入 state.json 的持久化记录 [F-095]，字段精简为 [F-096]：

```python
@dataclass
class PageRecord:
    path: str
    url: str
    title: str | None
    content_hash: str
```

`content_hash` 由 `content_hash(markdown)` 函数生成，算法为 `hashlib.sha256(markdown.encode("utf8")).hexdigest()` [F-081]。它用于增量同步时判定页面内容是否变化，不依赖 HTTP ETag 或时间戳。

## Frontmatter 规范

每个页面文件由 `write_concept()` 写入 [F-069]，frontmatter 包含以下字段：

```yaml
---
type: "Web Page"
title: "页面标题"
description: "页面描述"
resource: "https://example.com/original-url"
timestamp: "2026-08-23T12:00:00+00:00"
---
```

`frontmatter(fields)` 函数使用 `yaml.safe_dump(..., sort_keys=False, allow_unicode=True)` 序列化 [F-061]，并过滤值为 None、空字符串、空列表的字段，使输出简洁。正文 Markdown 之后追加 `# Citations` 段落，标注来源 URL。

`type` 字段是校验的核心依据。`validate_bundle()` 遍历 `bundle_dir.rglob("*.md")`，跳过 `.okf-kit/` 目录和保留文件，检查每个文件的 frontmatter 是否存在且 `type` 字段非空 [F-065]。校验失败返回 False，CLI 退出码为 3。

## URL 到文件路径的映射

`url_to_relpath(url)` 函数负责将 URL 转换为 bundle 内的相对路径 [F-079]。映射规则如下：

1. **根路径**：URL 路径为 `/` 时返回 `PurePosixPath("index")`
2. **扩展名剥离**：`.html`、`.htm`、`.php`、`.asp`、`.aspx`、`.jsp` 等页面扩展名被移除 [F-075]
3. **Query string**：保留 query string，生成 SHA1 前 8 位十六进制摘要作为后缀 `-q-<digest>`，避免不同 query 参数覆盖同一文件
4. **不安全字符**：`<>:"\\|?*` 及控制字符由 `_UNSAFE_CHARS` 正则匹配并替换为 `-` [F-076][F-078]
5. **空段处理**：strip `.` 和空格后为空的段替换为 `"unnamed"`

URL 规范化由 `normalize_url(url)` 完成 [F-077]：去除 fragment（`#...`）、去除尾部斜杠、保留 query string。

最终文件路径由 `bundle_path_for(url)` 组装 [F-068]：先经 `dodge_reserved()` 处理保留名，再添加 `.md` 后缀，最后置于 `pages/` 目录下。

```python
def bundle_path_for(url: str) -> str:
    rel = dodge_reserved(url_to_relpath(url).with_suffix(".md"))
    return str(PurePosixPath("pages") / rel)
```

## Markdown 清洗

`clean_markdown(md)` 函数执行三项清洗 [F-082]：
1. 移除 pilcrow 符号（`¶`），由 `_PILCROW` 正则匹配
2. 将 3 个及以上连续换行压缩为 2 个，由 `_EXTRA_BLANKS` 正则匹配
3. strip 首尾空白

此外，`_extract_markdown()` 还使用 `_PERMALINK` 正则移除 trafilatura 生成的永久链接标记（`[¶](#...)`、`[#](#...)` 等）[F-234][F-235]。

## 边计算策略

边（edges）是知识图谱的核心。`compute_edges(pages, present_paths)` 函数计算页面间的链接关系 [F-070]：

```python
def compute_edges(pages, present_paths: set[str]) -> list[list[str]]:
    edges = []
    for page in pages:
        src = bundle_path_for(page.url)
        links = page.content_links if page.content_links is not None else page.links
        for url in links:
            dst = bundle_path_for(url)
            if dst in present_paths and dst != src:
                edges.append([src, dst])
    return edges
```

关键设计是**内容链接优先**：优先使用 `page.content_links`（正文区域链接），仅当其为 None 时才回退到 `page.links`（全页链接）。`content_links` 的提取在 `HttpFetcher._parse()` 中完成 [F-227][F-229]：先从 HTML DOM 中 decompose（移除）`nav`、`header`、`footer`、`aside`、`[role="navigation"]` 等导航性节点，再从 `main`、`article`、`body` 元素中提取链接。这确保了导航栏、侧边栏、页脚的「站点结构链接」被排除在知识图谱边之外，只有正文中的「内容引用链接」构成语义关联。

边只收录目标在 `present_paths` 集合中的链接（即指向 bundle 内其他页面的内部链接），自链接被排除。返回格式为 `[src_path, dst_path]` 对列表。

## state.json 全局元数据

`write_bundle_meta()` 函数写入 `.okf-kit/state.json` [F-073][F-074]，包含以下字段：

```json
{
  "generator": "okf-kit",
  "okf_version": "0.1",
  "root_url": "https://example.com",
  "updated_at": "2026-08-23T12:00:00+00:00",
  "config": { ... },
  "page_count": 42,
  "pages": [
    {"path": "pages/index.md", "url": "...", "title": "...", "hash": "sha256..."}
  ],
  "edges": [
    ["pages/index.md", "pages/about.md"]
  ]
}
```

`pages` 列表每项含 `path`、`url`、`title`、`hash`（即 content_hash）。`edges` 持久化了计算出的边表。

## 边的双来源重建

`read_bundle(bundle_dir)` 函数在读取 bundle 时从两个来源重建边集 [F-259]：
1. **Markdown 链接**：用 `_LINK` 正则从正文中提取 `](path)` 链接目标 [F-258]
2. **state.json edges**：读取持久化的边表

`_target_id(target, from_id)` 函数严格解析链接目标 [F-260]：去除 fragment 和 query、要求以 `.md` 结尾、解析相对路径、拒绝 `..` 路径遍历和绝对路径。这种双来源设计形成「可重建的冗余」——即使 state.json 丢失，边也可从 Markdown 链接重新推导。

## 校验规则

`validate_bundle()` 的校验规则 intentionally minimal [F-065]：
- 遍历所有 `*.md` 文件
- 跳过 `.okf-kit/` 目录（STATE_DIRNAME）和保留文件（`index.md`、`log.md`）
- 检查 frontmatter 是否存在
- 检查 `type` 字段是否非空

这种极简校验反映了 OKF 的设计哲学：bundle 是人类可读的纯文本，结构正确性靠约定而非 schema 强制。

## 相关概念

- [OKF 知识包生态概览](/concepts/00-okf-overview.md)
- [网站爬取与 Bundle 构建流水线](/concepts/02-crawl-build-pipeline.md)
- [增量同步与安全阀门](/concepts/03-sync-incremental.md)
- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
