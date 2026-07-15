---
source: "../tasks.md#Task 8"
generated_at: "2026-07-15 10:43:47"
task: "SubTask 8.7"
type: "mermaid-governance-batches"
---

# Task 8.7：Mermaid 存量问题分批治理清单

## 说明

- 本文件只建立治理清单，不回填 `tasks.md`。
- 当前失败面基于 `python .agents/scripts/repo-check.py mermaid` 的全仓扫描结果整理。
- 本轮目标不是立即修完全部 Mermaid，而是先把后续治理拆成可执行批次，供 `SubTask 8.8`、`8.9`、`8.10` 承接。

## 当前失败面摘要

| 类别 | 问题文件数 | 错误 | 警告 | 当前建议 |
|---|---:|---:|---:|---|
| 核心规范文档 | 19 | 180 | 2 | 直接修复，优先进入 `SubTask 8.8` |
| `.agents/docs` 人类文档 | 84 | 543 | 136 | 按主题目录分批修复，进入 `SubTask 8.9` |
| 历史 spec 产物 | 14 | 151 | 0 | 先判断是否仍需保留为可渲染资产，再决定修复/豁免 |
| 生成型输出 | 30 | 490 | 48 | 优先找源头与镜像关系，避免双份手工修复 |
| 合计 | 147 | 1364 | 186 | 先做高价值入口，后做低复用历史产物 |

## 分类口径

为避免同一文件既算“人类文档”又算“生成型输出”，本清单采用以下优先级：

1. **生成型输出优先**：命中文件名或目录特征即归为“生成型输出”，如 `task*-output.md`、`analysis-result.md`、`report.md`、`execution-retrospective.md`、`export-suggestions.md`、`insight-extraction.md`，以及 `.agents/docs/retrospective/reports/` 下的报告类产物。
2. **历史 spec 产物次之**：位于 `.trae/specs/` 下、但未命中“生成型输出”规则的文件，归为“历史 spec 产物”。
3. **`.agents/docs` 人类文档**：位于 `.agents/docs/` 下、且不属于“生成型输出”的文件，归为“人类文档”。
4. **其余归入核心规范文档**：如 `README.md`、`.agents/commands/`、`.agents/checklists/`、`.agents/protocols/`、`.agents/rules/`、`.agents/templates/` 等规范入口。

## 共性问题族

本轮失败面不是随机散点，主要集中在以下 6 类：

1. 节点文本未加双引号：中文、空格、特殊字符节点直接裸写。
2. 边标签未加双引号：尤其是 `是/否`、中文短语、带 `<br/>` 的标签。
3. `subgraph` 裸中文 ID：应改为 `subgraph EN_ID ["中文标题"]`。
4. Mermaid 代码块空行：导致解析器提前中断。
5. 节点内使用 `\n`：应统一改成 `<br/>`。
6. 次级问题：`style` 语句含中文、`end` 作为节点 ID、participant 别名未加引号。

## 一、核心规范文档

### 批次 C1：入口级真问题优先

| 批次 | 范围 | 文件数 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---:|---|---|---|
| C1 | `README.md` + `.agents/commands/` + `.agents/checklists/` | 5 | `README.md`、`.agents/commands/seven-concepts.md`、`.agents/checklists/risk-scoring-checklist.md`、`.agents/checklists/tech-doc-writing-precheck.md`、`.agents/checklists/meta-retrospective-checklist.md` | 裸中文节点、裸边标签、少量裸 `subgraph` ID | 作为 `SubTask 8.8` 第一批，逐文件修到 `repo-check mermaid` 零错误 |

说明：

- 这是最该先修的一批，因为它们是入口级规范文档，读者与智能体都会直接消费。
- 当前错误量主要集中在 `.agents/commands/seven-concepts.md`，适合作为核心批次的首个目标文件。

### 批次 C2：高频路由与核心规则

| 批次 | 范围 | 文件数 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---:|---|---|---|
| C2 | `.agents/protocols/` + `.agents/rules/` 中存在 Mermaid 的核心路由文档 | 5 | `.agents/protocols/prompt-bootstrap.md`、`.agents/protocols/workspace-discovery.md`、`.agents/rules/meta-document-priority-principle.md`、`.agents/rules/three-stage-universal-principle.md`、`.agents/rules/skill-five-elements-mindmap.md` | 裸节点、裸边标签、`\n`、少量 warning | 紧随 C1 修复；保留在校验范围内，不建议豁免 |

说明：

- 这批文件错误量不大，但属于工作区发现、提示词自举、核心方法论入口，长期留红会持续污染全仓 `repo-check` 信号。

### 批次 C3：模板与样板文档

| 批次 | 范围 | 文件数 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---:|---|---|---|
| C3 | `.agents/templates/` 与少量数据安全规则文档 | 9 | `.agents/templates/design-review-standards.md`、`.agents/templates/two-stage-parallel-context-template.md`、`.agents/templates/new-user-first-quota-onboarding.md`、`.agents/templates/preflight-exploration-template.md`、`.agents/templates/mermaid-templates/*.md` | 裸节点、裸边标签、模板遗留旧写法 | 作为核心规范收尾批次；修后同步检查模板是否需要补入“安全写法示例” |

说明：

- 模板类文件的价值在“阻止新问题继续生成”，所以虽不如入口文档紧急，但修复收益很高。

## 二、`.agents/docs` 人类文档

### 批次 H1：学习型 Wiki 系列

| 批次 | 范围 | 目录簇 | 主要文件示例 | 主要问题 | 建议动作 |
|---|---|---|---|---|---|
| H1 | 七概念/学习型 Wiki | `.agents/docs/knowledge/learning/03-agent-platforms-tools/seven-concepts-monkeycode-vibe-coding-wiki/`、`.agents/docs/knowledge/learning/06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/`、`.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/` | `01-seven-concepts-framework.md`、`07-seven-concepts-applied.md`、`00-overview.md`、`10-case-study.md` | 裸节点、裸边标签、整组目录写法不一致 | 按“目录簇”为单位修，不按单文件跳着修；修完一簇立即复扫该簇 |

说明：

- 这批最适合目录级治理，因为同一系列文档往往复用同一套 Mermaid 写法，逐文件切换成本高。

### 批次 H2：厂商/平台分析类文档

| 批次 | 范围 | 目录簇 | 主要文件示例 | 主要问题 | 建议动作 |
|---|---|---|---|---|---|
| H2 | 厂商产品学习与技术分析 | `.agents/docs/knowledge/learning/07-vendor-product-learning/openai/`、`.agents/docs/knowledge/learning/07-vendor-product-learning/volcengine/`、`.agents/docs/knowledge/mdi-research/` | `volcengine-computer-use-agent-analysis.md`、`volcengine-eip-analysis.md`、`03-technical-architecture.md` | 裸节点、participant 别名、少量 style warning | 归入 `SubTask 8.9` 第二批；适合按“文档用途”连续清理 |

### 批次 H3：高复用模式文档

| 批次 | 范围 | 目录簇 | 主要文件示例 | 主要问题 | 建议动作 |
|---|---|---|---|---|---|
| H3 | 复盘模式库与方法论文档 | `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/`、`.agents/docs/retrospective/patterns/methodology-patterns/document-architecture/`、`.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/`、`.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/` | `dual-track-metadata-consistency.md`、`tech-selection-three-checks.md`、`protocol-reference-distill-verify.md`、`implement-review-harden-sop.md` | 裸节点、裸 `subgraph` ID、部分 `end` 保留字冲突 | 作为 `SubTask 8.9` 的高价值批次，优先于低复用学习笔记 |

说明：

- 这批属于可复用知识资产，修复收益高于普通学习笔记。
- 修完后建议把其中 1-2 个典型安全写法回填到 Mermaid 教程或模板。

### 批次 H4：零散入口与长尾文档

| 批次 | 范围 | 主要文件示例 | 主要问题 | 建议动作 |
|---|---|---|---|---|
| H4 | 不在前三批目录簇内的 `.agents/docs` 零散文件 | `.agents/docs/retrospective/2026-07-13-task0-workspace-protocols.md`、`.agents/docs/quality/mermaid-manual-fix-guide.md`、`.agents/docs/patterns/pattern-comparison-implement-review-harden-vs-configurable-by-default.md` | 类型杂，修法不完全一致 | 在 H1-H3 收敛后清理；避免与主题目录批次混做 |

## 三、历史 spec 产物

### 批次 S1：仍具参考价值的 spec 主文档

| 批次 | 范围 | 文件数 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---:|---|---|---|
| S1 | `spec.md` / `tasks.md` / 非输出型分析文档 | 6 | `.trae/specs/agent-app-marketplace/spec.md`、`analyze-ems-energy-management-article/tasks.md`、`analyze-yihuakaitian-meeting-record/tasks.md`、`first-principles-learning-mode-analysis/tasks.md` | 裸节点、边标签、空行 | 先判断是否仍作为活跃参考资产；若是则修，否则转入豁免候选 |

### 批次 S2：专题分析类 spec 文档簇

| 批次 | 范围 | 目录簇 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---|---|---|---|
| S2 | `retrospectives-insights` 下的专题分析 spec | `.trae/specs/retrospectives-insights/analyze-mem0-agent-memory-framework/`、`analyze-ai-hardware-design-tools/`、`analyze-wechat-article-E2FXmFb/`、`analyze-wechat-article-1nNIr/` | `analysis-report.md`、`task2-architecture.md`、`task3-write-flow.md`、`task4-search-mechanism.md`、`task2-methodology-analysis.md` | 裸节点、`\n`、空行 | 不建议散修单文件；按 spec family 判定“保留修复 / 历史冻结 / 校验排除” |

说明：

- 历史 spec 的核心问题不是“修不修得动”，而是“是否还值得维持可渲染状态”。
- 这类文件应作为 `SubTask 8.10` 的前置输入，而不是直接吞进 `SubTask 8.9`。

## 四、生成型输出

### 批次 G1：第一性原理学习模式链路

| 批次 | 范围 | 文件数 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---:|---|---|---|
| G1 | `first-principles-learning-mode-analysis` 产物及其 `.agents/docs` 镜像链路 | 10+ | `.trae/specs/retrospectives-insights/first-principles-learning-mode-analysis/task2-output.md`、`task5-output.md`、`task10-output.md`，以及 `.agents/docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/*.md` | 大量裸节点、裸边标签、裸 `subgraph`、style warning | 先确认“源头文件是谁”；只修 canonical source，镜像文件通过重生成或同步更新，不做双份手工修复 |

说明：

- 这是最明显的“源头-镜像重复治理”场景。
- 如果直接两边都手修，后续极易再次漂移。

### 批次 G2：单次分析输出文件

| 批次 | 范围 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---|---|---|
| G2 | 任务输出型 Markdown | `.trae/specs/retrospectives-insights/analyze-douyin-vibecoding-guide/task3-output.md`、`task4-output.md`、`task6-output.md`、`task7-output.md`、`minitest-ecosystem-insight-report.md`、`learn-volcengine-mobileuse-agent/analysis-result.md` | 输出阶段直接写入不安全 Mermaid | 判断是否需要长期保留可渲染；若是则修源模板/生成流程，否则考虑豁免或排除 |

### 批次 G3：历史报告类生成物

| 批次 | 范围 | 主要文件 | 主要问题 | 建议动作 |
|---|---|---|---|---|
| G3 | `.agents/docs/retrospective/reports/` 下历史报告与 task report | `retrospective-first-principles-pattern-split-20260709/analysis-report.md`、`retrospective-architecture-priority-20260629/README.md`、`retrospective-viitorvoice-tts-learning-20260703/insight-extraction.md` | 多为历史生成写法，复用价值低、维护成本高 | 统一在 `SubTask 8.10` 决定是“保留修复”还是“历史归档豁免” |

说明：

- 生成型输出不是不能修，而是必须先做“是否值得修”的治理决策。
- 若未来要继续保留这些产物进入校验范围，应优先修生成模板或产出流程，而不是逐份补锅。

## 建议执行顺序

1. `SubTask 8.8`：先做 `C1`，随后做 `C2`，最后收掉 `C3`。
2. `SubTask 8.9`：先做 `H1` 与 `H3`，再做 `H2`，最后处理 `H4` 长尾。
3. `SubTask 8.10`：集中处理 `S1/S2/G1/G2/G3` 的“修复 / 豁免 / 排除”口径，先定 canonical source，再决定是否需要重生成。
4. `SubTask 8.11`：在核心规范与高价值人类文档收敛后复跑 `repo-check all`，确认失败面是否只剩已决策的历史/生成类文件。

## 交付边界

- 本文件是 `SubTask 8.7` 的治理清单，不包含 Mermaid 实际修复。
- `tasks.md` 本轮不修改。
- 后续若进入修复阶段，建议每一批都遵循“目录簇修复 → 局部复扫 → 全仓复扫”的节奏，避免修复面与验证面脱节。
