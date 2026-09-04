---
title: "Spec：Claude 系统提示词发布史 OKF Wiki"
status: "draft"
---

# Spec：Claude 系统提示词发布史 OKF Wiki

> **change-id**: `create-claude-system-prompts-wiki`
> **信源**：`https://platform.claude.com/docs/zh-CN/release-notes/system-prompts/overview` 及其全部子条目（en 版为内容基线，zh-CN 为翻译对照）
> **方法**：seven-concepts 场景4 知识沉淀（R→I→E→V 收尾）
> **内容敏感度**：公开内容（Anthropic 官方文档）→ 标准工作流，产出物入 awesome-okf-xs 子模块 `doc/bundles/`
> **产出位置**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/anthropic/system-prompts/`（anthropic 组现有 6 束，本束为第 7 束）

## Why

Anthropic 自 2024-07 起在官方文档持续公开 claude.ai 网页端与移动端各代模型的**核心系统提示词全文**（16 个模型、28 个日期条目，覆盖 Opus 3 → Opus 5），是研究"产品级系统提示词设计"的第一手权威材料，且官方明确声明其不适用于 API——这一公开边界本身也是重要知识。目前 bundles 库无任何系统性中文整理。将其萃取为 OKF 知识包，补全 `jishu/ai/anthropic` 组的主题空缺。

## What Changes

- **新增束** `jishu/ai/anthropic/system-prompts/`（14 文件：`index.md` + `concepts/` 7 篇 + `references/` 3 篇 + `log.md`）
- **更新组索引** `jishu/ai/anthropic/index.md`（子Bundle导航表新增行、文档统计表、toctree）与 `jishu/ai/anthropic/log.md`（追加日志条目）
- **更新域索引** `jishu/ai/index.md`（anthropic 组束数/描述）
- **更新总索引** `doc/bundles/index.md`（束/组/域计数——**以 `invoke gates.bundles` 重算为准，禁止手填**）
- 不修改 SpecWeave 主权区文档；**不自动 commit/push**（用户未要求，提交由用户决定，可用 atomic-commit-cmd）

## Impact

- Affected specs：无既有 spec 关联（独立新增束）
- Affected code：
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/anthropic/system-prompts/**`（新增）
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/anthropic/index.md`、`log.md`（修改）
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/index.md`、`doc/bundles/index.md`（注册）

## 已知约束（R 阶段前置事实）

1. **直连 fetch 被 Region 墙拦截**：`platform.claude.com` / `docs.anthropic.com` 对当前出口 IP 返回 "App unavailable"。已验证**搜索引擎可分段提取页面内容**（Accordion 折叠全文已被索引），且存在 `.md` 原文端点（如 `docs/en/release-notes/system-prompts.md`，含 frontmatter 与全部条目）。
2. **页面结构**：单页承载全部内容——16 模型 × 28 日期条目（Accordion），模型间多版本差异以加粗标注；Claude 4.6 起每个 model ID 为单一固定快照，仅一个条目。
3. **条目全景**（en 页已确认）：Opus 5 (2026-07-24)、Fable 5 (2026-06-09)、Opus 4.8 (05-28)、Opus 4.7 (04-16)、Sonnet 4.6 (02-17)、Opus 4.6 (02-05)、Opus 4.5 (01-18/2025-11-24)、Haiku 4.5 (01-18/11-19/10-15)、Sonnet 4.5 (01-18/11-19/09-29)、Opus 4.1 (2025-08-05)、Opus 4 (08-05/07-31/05-22)、Sonnet 4 (08-05/07-31/05-22)、Sonnet 3.7 (2025-02-24)、Sonnet 3.5 (2024-11-22/10-22/09-09/07-12)、Haiku 3.5 (2024-10-22)、Opus 3 (2024-07-12)、Haiku 3 (2024-07-12)。
4. **zh-CN 子页面结构待确认**：用户给定 URL 带 `/overview` 后缀，zh-CN 站点可能拆分为 overview + 各模型子页，R 阶段第一步探测确认。

## ADDED Requirements

### Requirement: 束内容完整性（R→I→E 产出）

束 SHALL 基于官方页面系统覆盖以下四层，正文中文、关键段落保留英文原文摘录并配中文解析：

1. **公开机制与政策边界**：claude.ai/移动端系统提示词的角色（注入当前日期、行为引导）、与 API 的区别（更新不适用 API）、多版本加粗差异标注约定、4.6 起固定快照机制
2. **全景矩阵**：16 模型 × 28 日期条目的完整索引（模型-日期-要点）
3. **分时代条目详解**：按四个时代逐条目解析——
   - 3.x 时代（2024-07 → 2025-02，8 条目）
   - 4.0/4.1 多版本时代（2025-05 → 2025-08，7 条目）
   - 4.5 代（2025-09 → 2026-01，7 条目）
   - 4.6 → 5.x 固定快照时代（2026-02 → 2026-07，6 条目，含 Fable 5/Mythos/Glasswing 产品信息结构）
4. **设计思想演进分析**（洞察层）：行为规范措辞变化、工具生态扩张、记忆系统（memory_filesystem/[stated] 标签/隐私黑名单）、安全合规模块的演进轨迹

#### Scenario: 条目事实可靠
- **WHEN** 阅读 concepts 中任一模型条目
- **THEN** 模型名、日期、关键内容与官方页一致（V 阶段抽查 ≥5 条逐字比对）；无法采集的条目以纯文本"（待补）"标注（禁止先放链接后补文件）

#### Scenario: 内容详实且不失真
- **WHEN** 撰写条目解析
- **THEN** 关键行为规范段落引用官方原文（英文）并中文解读；不整篇翻译超大条目（单条可达 3 万+ token），以结构化拆解呈现；第三方解读（技术博客/新闻）仅作交叉印证并显式标注，禁止作为事实主源

### Requirement: 格式与结构合规

- OKF v0.2 YAML frontmatter（含 `sources` 溯源字段）；正文中文；文件名 kebab-case 纯英文
- toctree 完整：束根 `index.md` 以 `{toctree}` 引用全部内容页；组索引/域索引/总索引引用链闭合
- 相对路径交叉引用，禁止 `file:///`；UTF-8 无 BOM
- **规避已知陷阱**：frontmatter 双引号标量内禁 ASCII 双引号（中文语境用全角""）；脚注块前禁手写 `---`

#### Scenario: 质量门全绿
- **WHEN** 在子模块根运行 `invoke gates.utf8`、`invoke gates.toctrees`、`invoke gates.bundles`、`invoke build`
- THEN 四门全部通过；`gates.bundles` 重算的束/组/域计数回填各索引（anthropic 组 6→7 束）

### Requirement: 信源采集多通道兜底

R 阶段采集 SHALL 按以下升级链执行，直至 28 条目采集完毕或确认不可达：

1. **首选**：WebFetch 直取 `.md` 原文端点（en 与 zh-CN 各试一次）
2. **次选**：WebSearch 分段提取（按模型/时代构造查询，多轮拼接 Accordion 内容）
3. **兜底**：浏览器自动化（agent-browser / kimi-webbridge，经用户真实浏览器通道）
4. **交叉印证**（不作为主源）：官方博客、可信第三方技术媒体存档

#### Scenario: 采集失败诚实降级
- **WHEN** 某条目经全部通道仍不可达
- **THEN** 该条目标"（待补）"并在 log.md 记录采集过程，不虚构内容

## MODIFIED Requirements

（无既有需求变更）

## REMOVED Requirements

（无）
