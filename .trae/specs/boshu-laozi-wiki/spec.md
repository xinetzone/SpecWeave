---
name: boshu-laozi-wiki-spec
version: 1.0.0
created: 2026-08-19
source: "《帛书老子注读[精品]》.epub（掌阅DRM加密，正文不可读）→ 基于公共领域知识生成"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（帛书老子原文属公共领域）
---

# 《帛书老子注读》Wiki 教程

## Why

用户希望学习《帛书老子注读》一书并生成 wiki 教程。经预检确认该 epub 为掌阅（ZhangYue.Inc）DRM 加密格式（RSA+AES-128-CTR，CipherValue 为空），正文、目录、容器文件全部加密，无法直接读取。经用户确认，改为基于帛书老子的公共领域知识生成 wiki 教程——帛书老子（马王堆汉墓出土，约公元前 2 世纪）原文属公共领域，其版本源流、结构差异、核心概念等均为公开学术知识。

目标：将《帛书老子》这一重要道家经典的公共领域知识系统化，生成符合 SpecWeave 知识库规范（learning wiki 目录约定）的原子化教程，沉淀可复用的阅读与知识组织方法。

## What Changes

- 新增 wiki 教程目录 `.agents/docs/knowledge/learning/boshu-laozi-wiki/`
- 按 `NN-slug.md` 命名约定生成 8 个原子化章节 + README 索引
- 章节内容基于公共领域知识，涵盖：帛书老子背景与出土、版本体系、结构差异（德经在前）、核心概念（道/德/无为/自然）、注读方法论、与传世本对照、可复用模式、FAQ 与资源
- 遵循 seven-concepts 场景4 链路：R（事实采集）→ I（洞察）→ E（模式萃取）→ V（对抗审查）→ C（原子提交入库）

## Impact

- 新增目录：`.agents/docs/knowledge/learning/boshu-laozi-wiki/`
- 需更新导航：`.agents/docs/knowledge/learning/README.md`（Learning Wiki 索引）与 `CATEGORIES.md`（统计与清单）按 docgen 约定由 generate-readme.py 自动处理标记区域
- 不修改任何现有文件内容（仅可能追加索引表行）
- 不破坏任何现有功能

## ADDED Requirements

### Requirement: 帛书老子知识库 Wiki 教程

系统 SHALL 提供一套关于帛书老子（马王堆出土）的原子化 wiki 教程，基于公共领域知识，帮助学习者理解帛书老子的版本源流、核心思想与注读方法。

#### Scenario: 学习者阅读教程

- **WHEN** 学习者打开 wiki 目录 README
- **THEN** 能通过索引导航到各章节，章节间通过相对路径交叉引用，无断链

#### Scenario: 事实准确性

- **WHEN** 教程陈述帛书老子的历史事实（出土时间、版本、篇章结构）
- **THEN** 内容与公开学术共识一致（1973 年长沙马王堆三号汉墓出土甲乙本、德经在前道经在后等）

### Requirement: 章节结构规范

每个章节文件 SHALL 遵循 SpecWeave 知识库格式规范：
- frontmatter 含 `id`、`title`、`source`（标注公共领域来源）
- 标题层级清晰（H1→H3），Markdown 表格、引用块、Mermaid 图按需使用
- 文件名 `NN-slug.md`，章节间用相对路径 `[标题](NN-slug.md)` 引用

### Requirement: 可复用模式萃取（G3）

教程 SHALL 包含至少 2 个可复用模式（如"版本对照阅读法""出土文献认知框架"），每个模式含触发场景、核心步骤、反模式、迁移示例。

### Requirement: 方法论文档闭环

教程 SHALL 记录 seven-concepts 方法论应用痕迹（facts/insights/patterns 映射），并至少包含 3 条带四元组（陈述/证据/反常识/行动）的洞察。

## MODIFIED Requirements

无（本任务为全新增量，不修改既有需求）。

## REMOVED Requirements

### Requirement: 直接读取 DRM epub 正文

**Reason**: 掌阅 DRM（RSA+AES-128-CTR）加密，CipherValue 为空，无法解密读取正文。
**Migration**: 用户已确认改用公共领域知识生成；如后续获得可读版本，可补充原文引证。

## 开放问题

- 无（已与用户确认资料来源方案）
