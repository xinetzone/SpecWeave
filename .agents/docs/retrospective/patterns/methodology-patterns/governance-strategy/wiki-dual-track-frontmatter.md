---
id: "wiki-dual-track-frontmatter"
source: "../../../reports/competitive-analysis/retrospective-sunlogin-camera-su1-wiki-20260704/export-suggestions.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/wiki-dual-track-frontmatter.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  -   - "format-evidence-over-memory-pattern"
  -   - "convention-driven-creation"
  -   - "batched-creation-independent-review"
  -   - "subagent-wiki-delivery-checklist"
---
# Wiki双轨Frontmatter规范模式

## 模式概述

Wiki教程类文档存在两种架构类型（单文件wiki和原子化wiki），每种类型使用不同的YAML frontmatter字段集。模板、任务描述、验收清单必须明确区分这两种类型，提供对应的标准字段模板，禁止混用字段或凭记忆添加"看起来有用"的额外字段。

## 核心逻辑

```
Wiki文档有两种类型 → 每种类型frontmatter字段不同 → 模板/检查清单必须类型感知
单文件wiki：title, source, date, tags（4字段）
原子化wiki：id, title, source, x-toml-ref（4字段，其余元数据外置到TOML）
禁止：混合使用两套字段、添加author/version/category等额外字段
```

**问题根因**：原wiki模板和验收清单只描述了原子化wiki的frontmatter规范（id/title/source/x-toml-ref），但大量实际wiki任务产出的是单文件wiki（无需原子化拆分），子代理和主代理都缺乏单文件wiki的frontmatter标准参考，导致：
- 要么错误使用原子化wiki的字段要求
- 要么"好心"添加author/version等不在惯例中的字段
- 检查标准不一致，同一类问题反复出现

## 问题现象：frontmatter规范漂移

| 问题 | 表现 | 根因 |
|------|------|------|
| **字段混用** | 单文件wiki中出现id/x-toml-ref字段，或原子化wiki中出现date/tags | 模板未区分类型，子代理凭记忆拼凑字段 |
| **多余字段** | 添加author/version/category等"看起来有用"的字段 | 没有明确的"禁止添加"字段列表 |
| **规范漂移** | 任务模板复制粘贴时逐渐偏离原始规范 | 没有single source of truth，每次复制引入小偏差 |
| **检查标准不一致** | 不同wiki的frontmatter字段数不同（4个/5个/6个不等） | 验收清单没有按类型区分检查项 |

## 双轨规范

### 类型判定标准

在Spec阶段（L3层）必须明确wiki类型，判定标准：

| 判断维度 | 单文件wiki | 原子化wiki |
|---------|-----------|-----------|
| 预计行数 | <300行 | >300行 |
| 章节独立性 | 各章节需要连续阅读，独立引用价值低 | 各章节可独立阅读/引用 |
| 未来扩展 | 内容稳定，不预期持续新增章节 | 预期会持续新增章节/内容 |
| 复用需求 | 无跨文档引用单个章节的需求 | 单个章节会被其他文档引用 |
| TOML文件 | 不需要 | 需要.meta/toml/镜像路径下的TOML文件 |

### 单文件wiki Frontmatter标准

```yaml
---
title: "{{中文完整标题}}"
source: "{{原始URL或来源描述}}"
date: "{{YYYY-MM-DD}}"
tags: ["tag1", "tag2", "..."]
---
```

**字段说明**：
- `title`：中文完整标题，与H1标题一致
- `source`：原始来源URL或父文档路径
- `date`：创建/更新日期，格式YYYY-MM-DD
- `tags`：内联数组格式的标签列表

**禁止添加**：`id`、`x-toml-ref`、`author`、`version`、`category`等字段

**参考示例**：`docs/knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md`

### 原子化wiki Frontmatter标准

```yaml
---
id: "{{wiki-name}}-{{chapter-id}}"
title: "{{章节标题}}"
source: "{{来源URL或父文件路径}}"
x-toml-ref: "{{正确计算的相对路径}}"
---
```

**字段说明**：
- `id`：kebab-case英文唯一标识
- `title`：中文章节标题
- `source`：来源溯源，URL或父文件路径+锚点
- `x-toml-ref`：外部TOML元数据文件的相对路径

**禁止在YAML中添加**：`date`、`tags`、`category`、`author`、`version`等（这些应放在TOML外部文件中）

**参考示例**：`docs/knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/00-overview.md`

## 实施步骤

### 步骤1：Spec阶段类型声明

在spec.md的原子化决策部分，必须明确声明：
- [ ] **需要原子化拆分**：采用索引页+目录+数字前缀原子文件结构 → 使用原子化wiki frontmatter
- [ ] **保持单文件**：所有内容在一个md文件中 → 使用单文件wiki frontmatter

决策依据必须记录（满足哪条判定标准）。

### 步骤2：任务模板类型感知

子代理任务描述必须包含：
1. 明确声明本次wiki类型
2. 提供对应类型的frontmatter标准模板（4个字段，完整示例）
3. 明确列出禁止添加的字段
4. 参考示例文件路径

### 步骤3：验收清单类型区分

质量检查清单必须：
- 首先确认wiki类型
- 按类型检查对应字段是否完整且无多余
- 单文件wiki不检查TOML文件和x-toml-ref
- 原子化wiki必须检查TOML文件和x-toml-ref路径

### 步骤4：格式证据优先

不管模板如何描述，强制前置步骤要求子代理先读取对应类型的**现有参考文件**确认实际格式，以实际文件为准（参见"format-evidence-over-memory"模式）。

## 适用边界

### 适用场景

- ✅ docs/knowledge/learning/下的wiki教程文档
- ✅ 存在单文件/原子化两种形态的文档类型
- ✅ 使用子代理批量创作的文档工作流
- ✅ 需要标准化验收检查的文档生产流程

### 反模式（何时不适用）

- ❌ .agents/下的规范文档（使用id/x-toml-ref/source/title的原子化规范格式）
- ❌ docs/retrospective/下的复盘报告（有独立的报告frontmatter规范）
- ❌ 只有一种形态的文档类型（无需双轨区分）
- ❌ 临时笔记/草稿（不需要严格frontmatter规范）

## 案例验证

### 向日葵SU1摄像头wiki（L1验证）

本次任务中，SU1 wiki被创建为单文件wiki（约660行，虽然超过300行但章节独立性低，选择保持单文件），但由于模板未提供单文件wiki的frontmatter标准，创作时错误添加了`author: "AI Learning Wiki"`和`version: "1.0"`两个不在惯例中的字段。

调查现有同目录wiki发现：
- `sunlogin-security-wiki.md`：4字段（title/source/date/tags）✅
- `sunlogin-bootbox-analysis.md`：4字段（title/source/date/tags）✅
- `agnes-pavo-creative-platform-wiki.md`：4字段（title/source/date/tags）✅
- `sunlogin-camera-su1-wiki.md`：6字段（包含author/version）❌ → 已修复为4字段

修复后，模板被更新为双轨规范，新增"步骤0：确认wiki类型"，从5点检查升级为7点检查（新增字段类型检查和编号检查）。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [format-evidence-over-memory-pattern.md](format-evidence-over-memory-pattern.md) | 父模式 | 本模式是"格式证据优先于记忆"原则在wiki frontmatter领域的具体应用 |
| [convention-driven-creation.md](convention-driven-creation.md) | 上位 | 约定驱动创作原则要求每种文档类型有明确规范 |
| [batched-creation-independent-review.md](../ai-collaboration/batched-creation-independent-review.md) | 配套 | 独立质检是执行frontmatter规范检查的关键环节 |
| [subagent-wiki-delivery-checklist.md](../../../../../templates/subagent-wiki-delivery-checklist.md) | 工具 | 已更新的子代理验收清单是本模式的落地工具 |
| [wiki-spec-template.md](../../../../../templates/wiki-spec-template.md) | 工具 | 已更新的wiki模板是本模式的规范载体 |
