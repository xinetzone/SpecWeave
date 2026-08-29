---
type: Concept
title: 网站爬取与 Bundle 构建流水线
description: 从 URL 到 OKF bundle 的完整流水线，涵盖 Fetcher 抽象、BFS 爬取、内容提取、writer 写入、质量启发与 enrich 可选步骤
tags: [okf, crawl, fetcher, BFS, trafilatura, build, pipeline, enrich]
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

# 网站爬取与 Bundle 构建流水线

`okf build` 命令将一个网站 URL 转化为完整的 OKF bundle。整个流水线分为五个阶段：URL 规范化与输出目录确定 → Fetcher 创建与 BFS 并发爬取 → HTML 解析与 Markdown 提取 → Writer 逐页写入并聚合元数据 → 校验与可选的 enrich 增强。本文档详细描述每个阶段的实现机制。

## 命令入口与参数

`build` 子命令接受位置参数 `url`（Root URL）[F-033]，关键选项包括 [F-034][F-035]：

- `-o/--output DIR`：输出目录，默认为 `./{host}-okf`
- `--max-depth int`：BFS 最大深度，默认 3
- `--max-pages int`：最大页面数，默认 200
- `--js`：使用浏览器渲染模式（BrowserFetcher）
- `--no-robots`：不遵守 robots.txt
- `--path-prefix PATH`：限定爬取路径前缀
- `--all-paths`：不按路径前缀限定范围
- `--enrich`：构建后调用 LLM 生成摘要和标签
- `--enrich-model`：enrich 使用的模型，默认 `gpt-4o-mini`

CLI 的 `main()` 函数将这些参数传递给 `crawl.build_bundle()` [F-046]，成功后若 `--enrich` 为真则调用 `enrich.enrich_bundle()` [F-047]。

## Fetcher 抽象

okf-kit 定义了可插拔的 Fetcher 抽象——"pluggable ways to turn a URL into a Page (markdown + links)" [F-220]。工厂函数 `make_fetcher(js, ...)` 根据 `js` 参数选择实现 [F-242]：

```python
def make_fetcher(js: bool, *, respect_robots=True, verbose=False):
    if js:
        return BrowserFetcher(verbose=verbose)
    return HttpFetcher(respect_robots=respect_robots, verbose=verbose)
```

### HttpFetcher

`HttpFetcher` 的 `kind` 属性为 `"http"` [F-221]，使用 httpx 异步客户端进行轻量级 HTTP 抓取。其 `__init__` 创建 [F-222]：
- `httpx.AsyncClient`（`follow_redirects=True`，自定义 User-Agent，timeout 20 秒）
- `asyncio.Semaphore(concurrency)`（默认并发 8）
- robots.txt 缓存字典与锁

`fetch(url)` 异步方法的执行流程 [F-223][F-224]：
1. 通过 semaphore 限流
2. 检查 robots.txt 权限（`_allowed()` 方法，按 host 缓存 `RobotFileParser`）[F-226]
3. HTTP GET，status >= 400 返回 None，content-type 不含 html 返回 None
4. 调用 `_extract_markdown(html)` 提取 Markdown
5. 调用 `_parse(html, str(resp.url))` 提取 title、description、links、content_links
6. Markdown 为空时调用 `_fallback(html, title)` 降级提取
7. 最终调用 `clean_markdown()` 清洗

### BrowserFetcher

`BrowserFetcher` 的 `kind` 属性为 `"browser"` [F-236]，用于 JavaScript 渲染的单页应用。它延迟导入 `crawl4ai.AsyncWebCrawler` 和 `BrowserConfig` [F-237]，创建 headless 浏览器配置。`fetch(url)` 调用 `crawler.arun(url, config=CrawlerRunConfig())`，从 `result.markdown.raw_markdown` 获取 Markdown，从 `result.links.internal` 获取内部链接 [F-238]。

## 内容提取流水线

### Markdown 提取：trafilatura

`_extract_markdown(html)` 函数调用 trafilatura [F-235]：

```python
trafilatura.extract(
    html,
    output_format="markdown",
    include_tables=True,
    include_formatting=True,
    include_links=True,
    **{_NO_FALLKACK_KW: True}
)
```

`_NO_FALLBACK_KW` 通过 `inspect.signature` 检测 trafilatura 版本，值为 `"fast"` 或 `"no_fallback"` [F-233]。提取结果通过 `_PERMALINK.sub("", md)` 移除永久链接标记 [F-234]。

### HTML 解析：selectolax

`HttpFetcher._parse(html, base_url)` 静态方法使用 selectolax HTMLParser [F-227]，提取：
- **title**：`<title>` 标签文本
- **description**：`<meta name="description">` 的 content
- **links**：所有 `<a href>` 的绝对 URL
- **content_links**：正文区域链接

content_links 的提取是语义边降噪的关键 [F-229]：先从 DOM 中 decompose（移除）`nav`、`header`、`footer`、`aside`、`[role="navigation"]` 节点，再从 `main`、`article`、`body` 元素中提取链接。此外，`meta[http-equiv="refresh"]` 重定向目标被正则提取并插入 links 列表头部，保证跳转关系不丢失 [F-228]。

### 降级提取

当 trafilatura 返回空结果时，`_fallback(html, title)` 静态方法提供降级方案 [F-230]：移除 `script`、`style`、`noscript`、`svg`、`nav`、`footer`、`header` 标签 [F-232]，提取 `h1`-`h4`、`p`、`li` 文本，组装为简单 Markdown。这确保了即使 trafilatura 无法处理的页面也能获得基本内容。

## BFS 爬取

`crawl_site(seed, *, fetcher, max_depth, max_pages, path_prefix, scope, on_page)` 是异步 BFS 主循环 [F-245]。其算法：

1. 规范化 seed URL，初始化 visited 集合和队列
2. 首个页面设置 prefix：若未指定 path_prefix，由 `scope_prefix_for(url)` 从 URL 路径推导 [F-244]——文件路径取其目录，无扩展名路径取自身
3. 逐层 BFS，每层使用 `asyncio.gather(*(fetcher.fetch(u) for u in batch))` 并发获取 [F-246]
4. 对每个页面：同 host、未访问、在路径范围内的链接收录到 next_level
5. 跳过无 Markdown 内容的页面和重复路径 [F-247]
6. 设置 `page.depth = depth`，调用 `on_page(page, path)` 回调
7. 达到 max_depth 或 max_pages 时停止

`normalize_prefix(prefix)` 确保前缀有首尾斜杠 [F-243]。`normalize_url(url)` 去除 fragment 和尾部斜杠 [F-077]，避免重复爬取。

User-Agent 标识为 `okf-kit/{version} (+https://github.com/vinodborole/okf-kit)` [F-231]。

## Writer 写入

### 单页写入

`write_concept(bundle_dir, page, timestamp)` 将每个 Page 写入对应 .md 文件 [F-069]：
- body 为空时返回 None（跳过）
- 写入 frontmatter：`type="Web Page"`、`title`、`description`、`resource`（原始URL）、`timestamp`
- 追加正文 Markdown
- 末尾追加 `# Citations` 段落标注来源 URL

### 元数据聚合

`build_bundle()` 调用 `asyncio.run(_build(...))` [F-248]。在 `_build` 异步函数中 [F-249][F-250]：
1. 对所有 page 调用 `write_concept()`，过滤 None 得到 records 列表
2. 调用 `compute_edges()` 计算边表
3. 调用 `write_bundle_meta()` 聚合并写入：
   - `write_directory_indexes()`：为每个目录生成 `index.md`，含子目录和文件链接 [F-063]
   - `write_root_index()`：写入根 `index.md`，含标题和页面链接 [F-064]
   - `append_log()`：追加日志到 `log.md` [F-072]
   - 写入 `.okf-kit/state.json`（含 generator、version、root_url、config、page_count、pages、edges）[F-073][F-074]

### 输出目录

`_default_output(seed)` 返回 `./{host}-okf`，host 从 urlparse netloc 获取，冒号替换为下划线 [F-241]。

## 质量启发式

构建过程包含一个质量检测 [F-240][F-251]：
- `_SHORT_PAGE_CHARS = 200`：短页面阈值（少于 200 字符）
- `_JS_HINT_RATIO = 0.30`：短页面比例阈值（30%）

当短页面比例超过 30% 且非 JS 模式时，向 stderr 输出提示消息，建议安装 `okf-kit[js]` 并使用 `--js` 标志。这通常表明目标站点是 JavaScript 渲染的 SPA，HttpFetcher 无法获取完整内容。

构建结束后自动调用 `validate_bundle(bundle_dir)` [F-252]，返回 0（成功）或 3（校验失败）。

## Enrich 可选步骤

`--enrich` 标志启用 LLM 增强 [F-047]。`enrich_bundle(bundle_dir, *, model="gpt-4o-mini", enricher=None)` 遍历所有概念文件 [F-315]：

1. 解析 YAML frontmatter
2. 调用 enricher 函数（默认由 `_openai_enricher(model)` 创建）[F-313]
3. enricher 使用 OpenAI API，system prompt 要求返回单句事实描述和 3-7 个小写关键词 [F-311]
4. 使用 JSON schema 约束输出格式（`description` string + `tags` string array，均 required）[F-312]
5. body 截断至 6000 字符以控制 token 消耗 [F-314]
6. 将生成的 description 和 tags 写回 frontmatter

## 完整数据流

```text
URL
 │
 ├─ normalize_url() → 规范化 URL
 ├─ _default_output() → 输出目录
 ├─ make_fetcher() → HttpFetcher | BrowserFetcher
 │
 └─ crawl_site() [BFS]
      │
      ├─ fetcher.fetch() [并发]
      │    ├─ robots.txt 检查
      │    ├─ HTTP GET / 浏览器渲染
      │    ├─ _extract_markdown() [trafilatura]
      │    ├─ _parse() [selectolax: title/desc/links/content_links]
      │    ├─ _fallback() [降级]
      │    └─ clean_markdown()
      │
      └─ on_page 回调
           │
           └─ write_concept() → pages/*.md
                │
                └─ write_bundle_meta()
                     ├─ compute_edges()
                     ├─ write_directory_indexes()
                     ├─ write_root_index()
                     ├─ append_log()
                     └─ state.json
```

## 相关概念

- [Bundle 数据模型与语义边](/concepts/01-bundle-data-model.md)
- [增量同步与安全阀门](/concepts/03-sync-incremental.md)
- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
- [CLI 使用示例](/examples/cli-usage.md)
