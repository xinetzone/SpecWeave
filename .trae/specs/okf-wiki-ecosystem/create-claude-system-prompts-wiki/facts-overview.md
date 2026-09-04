# 总览层事实登记（F-OV-xxx）

> 信源：`https://platform.claude.com/docs/en/release-notes/system-prompts/overview`（本地落盘 `%TEMP%\sp-en.md`，curl 直取 .md 端点）+ en 单页旧版快照（搜索引擎索引）
> 采集时间：2026-09-02

## F-OV-001 页面体系结构

overview 页为卡片导航页，不含提示词正文。`<CardGroup cols={3}>` 列出 18 个模型子页面（每模型独立 URL），顺序（官方排列，新→旧）：

| # | 卡片标题 | 子页 slug |
|---|---------|-----------|
| 1 | Claude Fable 5.1 | claude-fable-5-1 |
| 2 | Claude Opus 5 | claude-opus-5 |
| 3 | Claude Fable 5 | claude-fable-5 |
| 4 | Claude Opus 4.8 | claude-opus-4-8 |
| 5 | Claude Opus 4.7 | claude-opus-4-7 |
| 6 | Claude Sonnet 4.6 | claude-sonnet-4-6 |
| 7 | Claude Opus 4.6 | claude-opus-4-6 |
| 8 | Claude Opus 4.5 | claude-opus-4-5 |
| 9 | Claude Haiku 4.5 | claude-haiku-4-5 |
| 10 | Claude Sonnet 4.5 | claude-sonnet-4-5 |
| 11 | Claude Opus 4.1 | claude-opus-4-1 |
| 12 | Claude Opus 4 | claude-opus-4 |
| 13 | Claude Sonnet 4 | claude-sonnet-4 |
| 14 | Claude Sonnet 3.7 | claude-sonnet-3-7 |
| 15 | Claude Sonnet 3.5 | claude-sonnet-3-5 |
| 16 | Claude Haiku 3.5 | claude-haiku-3-5 |
| 17 | Claude Opus 3 | claude-opus-3 |
| 18 | Claude Haiku 3 | claude-haiku-3 |

（sp-en.md L9-L45）

## F-OV-002 官方定位声明（逐字引用，overview 页 frontmatter 下方首段）

- [quote] "Claude's web interface (claude.ai) and mobile apps use a system prompt to provide up-to-date information, such as the current date, to Claude at the start of every conversation. The system prompt also encourages certain behaviors, such as always providing code snippets in Markdown. This prompt is periodically updated to improve Claude's responses. These system prompt updates do not apply to the Claude API. Some models have multiple dated entries on their pages. Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot, so those models have one entry."（sp-en.md L7）

中文解读：系统提示词是 claude.ai 网页端与移动端在每次会话开始时注入的"产品级配置"，承担两个职责——①提供实时信息（当前日期）；②引导特定行为（如代码片段用 Markdown）。更新节奏为"定期"，且**明确不适用于 Claude API**。

## F-OV-003 版本差异标注约定（两代页面表述并存）

- 旧版单页（搜索引擎快照）表述：[quote] "Where a model has multiple dated entries below, updates between versions are bolded."——版本间差异以**加粗**标注。
- 新版 overview 页表述（F-OV-002 末两句）仅说明"部分模型有多个日期条目、4.6 起单一固定快照"，**未再提及加粗约定**。
- 实测（facts-era-3x.md）：Sonnet 3.5 页面 4 个条目中仅 1 处实际使用加粗标注，多数变更未标注——加粗约定执行不严格。

## F-OV-004 固定快照机制

- [quote] "Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot"（sp-en.md L7）+ 外链 `docs/en/about-claude/models/model-ids-and-versions`。
- 中文解读：自 4.6 代起每个模型 ID 是单一固定快照，提示词不再随时间演进，故每模型仅一个条目；4.6 之前的模型页面保留多个日期条目（历史演进）。

## F-OV-005 语言版本与可达性（采集过程记录）

- 用户指定 zh-CN 入口：`https://platform.claude.com/docs/zh-CN/release-notes/system-prompts/overview`。
- 本环境实测：zh-CN 路径（HTML 与 .md）均返回 "App unavailable in region"（WebFetch 与 curl 一致）；en 路径 .md 端点 curl 可直连（间歇性地域拦截，重试可过）。
- 结论：以 en 版为内容基线（18 页全量采集成功），zh-CN 仅作页面结构佐证。

## F-OV-006 条目总量核对

18 个模型页面共 **30 个日期条目**：3.x 时代 8 条（Opus 3 ×1、Haiku 3 ×1、Sonnet 3.5 ×4、Haiku 3.5 ×1、Sonnet 3.7 ×1）+ 4.0/4.1 时代 7 条（Sonnet 4 ×3、Opus 4 ×3、Opus 4.1 ×1）+ 4.5 代 8 条（Sonnet 4.5 ×3、Haiku 4.5 ×3、Opus 4.5 ×2）+ 固定快照时代 7 条（Opus 4.6、Sonnet 4.6、Opus 4.7、Opus 4.8、Fable 5、Opus 5、Fable 5.1 各 1）。

> 注：Spec 撰写时基于旧版单页快照估计为"16 模型 × 28 条目"；实际采集核实为 **18 模型 × 30 条目**（新增 Fable 5.1 于 2026-09-01 上线，且旧快照未含个别条目）。以本核实数为准。
