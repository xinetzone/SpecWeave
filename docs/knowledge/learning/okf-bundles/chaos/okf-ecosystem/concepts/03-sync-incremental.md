---
type: Concept
title: 增量同步与安全阀门
description: okf sync 基于 state.json 恢复与 content_hash 三集合 diff 的增量同步机制，含安全阀门阈值与 post_sync 钩子
tags: [okf, sync, incremental, diff, content-hash, safety-valve, post-sync]
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

# 增量同步与安全阀门

`okf sync` 命令对已有 bundle 执行增量更新。它不是简单地重新爬取覆盖，而是读取 `state.json` 中的旧页面记录（含 content_hash），重新爬取后对新旧两个页面集合做集合论 diff，得到 added、removed、changed 三个互斥集合，仅对变化部分执行文件操作。关键设计是「安全阀门」：当新爬取结果异常变小时（可能因反爬拦截、网站改版、网络故障），默认拒绝同步，防止用残缺结果覆盖已有知识。

## 命令入口与参数

`sync` 子命令接受位置参数 `directory` [F-038]，选项包括：
- `--max-depth int`：最大深度，默认 None（沿用 build 时配置）
- `--max-pages int`：最大页面数，默认 None（沿用 build 时配置）
- `--force`：绕过安全阀门，强制同步

CLI 的 `main()` 调用 `sync.sync_bundle(directory, max_depth, max_pages, force)` [F-050]。`sync_bundle()` 是同步包装器，调用 `asyncio.run(run_sync(...))`，返回 0 或 3 [F-091]。

## 状态恢复

`run_sync(directory, *, max_depth, max_pages, force, post_sync)` 异步函数首先读取 state.json [F-292]：

```python
state = json.loads((state_path).read_text(encoding="utf-8"))
root_url = state["root_url"]
config = state.get("config", {})
```

从 state.json 恢复的信息包括：
- `root_url`：重新爬取的种子 URL
- `config`：原始构建配置，包括 fetcher 类型（http/browser）、path_prefix、max_depth、max_pages 等
- `pages`：旧页面记录列表，每项含 path/url/title/hash

根据 `config.fetcher` 判断是否使用 browser 模式 [F-293]，调用 `make_fetcher()` 创建对应的 Fetcher。path_prefix 被保留——pre-0.1.3 版本的 bundle 默认 path_prefix 为 `"/"`，代码做了兼容处理。CLI 传入的 max_depth/max_pages 若为 None 则沿用 config 中的原始值。

## 三集合 Diff

核心算法在新旧两个页面集合之间计算三个互斥集合 [F-294]：

```python
old_pages = {p["path"]: p for p in state["pages"]}
new_pages = {bundle_path_for(p.url): PageRecord(...) for p in crawled_pages}

added = new_paths - old_paths
removed = old_paths - new_paths
changed = {
    path for path in new_paths & old_paths
    if new_pages[path].content_hash != old_pages[path].hash
}
```

- **added**（新增）：新爬取到但旧 state 中不存在的页面路径
- **removed**（删除）：旧 state 中存在但新爬取未发现的页面路径
- **changed**（变更）：两者交集且 content_hash 不同的页面

`content_hash` 是 `hashlib.sha256(markdown.encode("utf8")).hexdigest()` [F-081]，基于清洗后的 Markdown 而非原始 HTML。这意味着页面样式微调、导航栏变化不会触发 changed，只有正文内容变化才会。changed 判定不依赖 HTTP ETag、Last-Modified 或时间戳，完全由内容决定。

## 安全阀门

安全阀门是同步机制中最重要的防护设计 [F-290][F-295]：

```python
_SAFETY_MIN_PAGES = 4
_SAFETY_RATIO = 0.5

if not force and len(old_pages) > _SAFETY_MIN_PAGES:
    if len(new_pages) < len(old_pages) * _SAFETY_RATIO:
        raise SystemExit(
            f"Sync would remove {len(removed)} of {len(old_pages)} pages. "
            f"Use --force to override."
        )
```

触发条件（同时满足）：
1. 非 `--force` 模式
2. 旧页面数 > 4（`_SAFETY_MIN_PAGES`，避免对小 bundle 误触发）
3. 新页面数 < 旧页面数 × 0.5（`_SAFETY_RATIO`）

这两个阈值硬编码在源码中，不可通过命令行配置。设计意图是：当爬取结果异常变小（如返回登录页、软 404、限流页面），HTTP 状态码可能仍是 200，但页面数会骤降。阀门宁可拒绝同步让用户人工确认，也不静默丢失知识。`--force` 标志显式绕过阀门，适用于站点大规模重构等确知页面减少的场景。

## 文件操作

通过安全阀门后，`run_sync` 按以下顺序执行文件变更 [F-296]：

1. **删除 removed 文件**：遍历 removed 集合，删除对应的 .md 文件
2. **清理空目录**：调用 `prune_empty_dirs()` 逆序遍历目录，删除空子目录 [F-071]
3. **写入 added+changed**：对新增和变更的页面调用 `write_concept()` 写入新内容
4. **更新元数据**：调用 `write_bundle_meta()` 更新 state.json、index.md、log.md 和 edges

changed 页面的处理方式是「覆盖写入」——先删除旧文件再写入新内容（通过 write_concept 直接覆盖），不保留历史版本。版本管理建议将 bundle 纳入 git 等外部版本控制系统。

## post_sync 钩子

`run_sync` 支持 `post_sync` 参数——一个异步可调用对象的元组 [F-297]：

```python
for hook in post_sync:
    await hook(bundle_dir, state, diff)
```

钩子在元数据写入后执行，可用于扩展同步行为（如自动 enrich、触发通知、启动索引重建等）。钩子执行完成后，调用 `validate_bundle(bundle_dir, quiet=True)` 静默校验，确保同步结果结构完整。

## 与 build 的关系

build 和 sync 共享底层爬取引擎，但有关键区别：

| 维度 | `okf build` | `okf sync` |
|------|------------|-----------|
| 起始状态 | 从零创建 | 从 state.json 恢复 |
| 配置来源 | CLI 参数 | state.json config（CLI 参数可覆盖） |
| 写入策略 | 全量写入 | 三集合 diff 增量写入 |
| 安全检查 | 短页面比例提示（非阻断） | 页面数比例阀门（阻断） |
| 后处理 | 可选 enrich | post_sync 钩子 + 静默 validate |
| 退出码 | 0 或 3 | 0 或 3 |

build 阶段也有质量启发式：短页面（<200 字符）比例超过 30% 时提示启用 JS 模式 [F-251]，但这只是 stderr 提示而非阻断。sync 的安全阀门则是硬阻断，体现了「默认保守、强制显式覆盖」的信任模型。

## 设计哲学

安全阀门体现了与大多数同步工具相反的信任模型。常见工具奉行「新即真」（latest wins），爬取到什么就覆盖什么。OKF 则不信任单次爬取结果的完整性，尤其是当结果「异常变小」时。50% 阈值不是统计学最优值，而是工程上的「防呆」下限——宁可拒绝同步让用户人工确认，也不静默将整个 bundle 替换成一页「请登录」。

这种设计在知识管理工具中比在数据管道中更重要，因为知识包的重建成本（人工审核、重新爬取、可能丢失的注释和 frontmatter 增强）高于存储成本。

## 相关概念

- [Bundle 数据模型与语义边](/concepts/01-bundle-data-model.md)
- [网站爬取与 Bundle 构建流水线](/concepts/02-crawl-build-pipeline.md)
- [MCP/Chat/HTTP 三模服务架构](/concepts/04-service-modes.md)
- [CLI 使用示例](/examples/cli-usage.md)
