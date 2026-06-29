# 捕获 Claude Tag 文章知识 Spec

## Why

量子位于 2026-06-24 发表文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》，报道了 Anthropic 发布的全新企业协作工具 **Claude Tag**。该工具代表了 LLM 用户界面演进的新方向（卡帕西称之为「第三次重大变革」），且与 SpecWeave 项目关注的多智能体协作、组织知识沉淀、Agent 工作流等议题高度相关。为避免信息流失并便于后续查阅，需将该文章的核心内容结构化沉淀到项目知识库。

## What Changes

- 新增知识条目 `docs/knowledge/learning/claude-tag-article.md`，结构化记录该公众号文章的核心观点、关键概念、重要数据与专业术语
- 更新 `docs/knowledge/README.md` 索引（通过运行 `scripts/generate_index.py` 自动重新生成）

## Impact

- **受影响 specs**：无既有 spec 受影响，本变更为知识库增量
- **受影响代码**：
  - 新增：`docs/knowledge/learning/claude-tag-article.md`
  - 自动更新：`docs/knowledge/README.md`（索引脚本重新生成）

## ADDED Requirements

### Requirement: 知识条目元数据

知识条目 SHALL 在文件开头以引用块形式标注来源元数据，包含原文标题、来源 URL、作者/公众号、发布日期。

#### Scenario: 元数据完整可溯源

- **WHEN** 读者打开 `claude-tag-article.md`
- **THEN** 文件顶部可见原文标题、公众号（量子位）、作者（henry 发自 凹非寺）、发布日期（2026-06-24）与原文链接

### Requirement: 核心观点捕获

知识条目 SHALL 准确概括文章的核心论点，至少覆盖：

1. Claude Tag 的产品定位（Claude Code 的进化，企业协作工具）
2. 卡帕西提出的「LLM 用户界面三次变革」论断
3. Claude Tag 与传统 AI 助手的根本差异（团队共享 vs 个人独占）
4. Anthropic 强调的四大能力（共享上下文、持续记忆、主动介入、异步执行）
5. 产品形态判断（企业内部统一入口）

#### Scenario: 核心论点可被快速理解

- **WHEN** 读者阅读「核心观点」章节
- **THEN** 能够在不阅读原文的情况下准确把握 Claude Tag 的定位、价值主张与差异点

### Requirement: 关键概念与术语记录

知识条目 SHALL 列出并解释文章中出现的关键概念与专业术语，至少包含：Claude Tag、Ambient Mode（主动介入模式）、共享上下文、持续记忆、异步执行、Claude 身份（权限隔离）、Opus 4.8、Fable 5。

#### Scenario: 术语可被独立查阅

- **WHEN** 读者查阅「关键概念与术语」章节
- **THEN** 每个术语均有简明中文释义，无需回溯原文

### Requirement: 重要数据记录

知识条目 SHALL 记录文章中出现的量化数据与事实性信息，至少包含：

- Anthropic 自身约 65% 产品代码由 Claude Tag 参与完成
- 当前仅支持 Opus 4.8，Fable 5 暂无消息
- 率先登陆 Slack，未来 30 天内逐步取代现有 Slack 版 Claude 应用
- 已向 Claude Enterprise 和 Team 用户开放 Beta 测试
- 计划未来几周内扩展到更多协作平台

#### Scenario: 数据可被引用

- **WHEN** 读者查阅「重要数据」章节
- **THEN** 可直接引用文章中的量化数据与事实，无需重新爬梳原文

### Requirement: 结构框架与索引

知识条目 SHALL 按文章原结构组织章节，并补充「主题思想概括」与「与 SpecWeave 的关联」两节，便于读者快速定位与跨文档引用。

#### Scenario: 结构清晰可导航

- **WHEN** 读者浏览目录或章节标题
- **THEN** 能快速定位到产品概述、核心能力、部署方式、社区反响等子主题

### Requirement: 知识库索引同步

新增知识条目后 SHALL 运行 `python scripts/generate_index.py` 重新生成 `docs/knowledge/README.md` 索引，确保新条目出现在「按类别浏览」「标签索引」「最近更新」章节。

#### Scenario: 索引包含新条目

- **WHEN** 运行索引生成脚本
- **THEN** `docs/knowledge/README.md` 的 learning 分类表与标签索引中出现 `claude-tag-article` 条目
