---
source:
  - "../tasks.md#Task 8"
  - "task8-7-mermaid-batches.md"
  - "task8-8-core-mermaid-fixes.md"
  - "task8-9-docs-mermaid-fixes.md"
generated_at: "2026-07-15"
task: "SubTask 8.10"
type: "mermaid-disposition-policy"
status: "completed"
---

# Task 8.10：历史 spec 与生成型输出 Mermaid 处置口径

## 目标

- 基于 `repo-check mermaid` 当前剩余失败面，给历史 spec 与生成型输出建立统一处置口径。
- 避免把“应修的 canonical source”和“应排除的历史归档”“应重生成的派生产物”混成一锅手工补丁。
- 为 `SubTask 8.11` 提供可执行的后续动作顺序，而不是继续用全仓红灯阻塞迁移收尾。

## 扫描基线

- 扫描方式：使用 `python .agents/scripts/repo-check.py mermaid` 的同一检查引擎，对全仓 Markdown 重新做结构化复扫。
- 扫描口径：延续 `task8-7-mermaid-batches.md` 的四类划分，但本文件只聚焦：
  - 历史 spec 产物
  - 生成型输出
- 当前剩余失败面（仅本子任务关注范围）：

| 范围 | 文件数 | 错误 | 警告 | 说明 |
|---|---:|---:|---:|---|
| 历史 spec 产物（S1 + S2） | 15 | 220 | 0 | 含活跃 spec、完成态研究 spec、任务拆解文档 |
| 生成型输出（G1 + G2 + G3） | 29 | 421 | 48 | 含 task output、analysis result、历史报告镜像 |
| 合计 | 44 | 641 | 48 | 属于本次 `8.10` 的处置对象 |

> 注：全仓仍有 core/human docs 范围的其他 Mermaid 失败，但不属于本文件处置范围。

## 四类动作定义

| 动作 | 适用条件 | 对 `repo-check mermaid` 的影响 | 执行原则 |
|---|---|---|---|
| 修复 | 文件仍是 canonical source，且被当前规范/入口直接消费，手工修复成本低 | 继续保留在默认校验范围内 | 直接最小修复，不改图意 |
| 豁免 | 文件仍可见、偶尔被引用，但不值得在本轮单独拆开修；下次触碰该家族时必须先修 | 当前作为已知债务记录，不作为本轮阻塞项 | 只做文档化豁免，不做双份手修 |
| 排除 | 文件属于历史冻结产物/归档报告，Mermaid 可渲染性不再值得进入日常门禁 | 应移出默认 `repo-check mermaid` 噪音面 | 优先按目录或 spec family 排除，不做逐文件补锅 |
| 重生成 | 文件是生成型输出，或存在“源头-镜像”关系，手工修两份会再次漂移 | 源头重生成后再回归校验 | 永远先找 canonical source，再同步镜像 |

## 总体结论

| 处置 | 文件数 | 错误 | 警告 | 处理重点 |
|---|---:|---:|---:|---|
| 修复 | 2 | 8 | 0 | 留在默认校验范围内，适合直接清零 |
| 豁免 | 1 | 12 | 0 | 记录为家族级刷新前的短期已知债务 |
| 排除 | 22 | 165 | 0 | 从默认门禁噪音中移走，按历史归档看待 |
| 重生成 | 19 | 456 | 48 | 不做双份手修，先修/重跑源头，再同步镜像 |

## 一、修复

### F1：仍被主动消费的 canonical 文档

| 文件 | 错误 | 原因 | 结论 |
|---|---:|---|---|
| `.trae/specs/agent-app-marketplace/spec.md` | 6 | 该 spec 已作为 `.agents/protocols/workspace-discovery.md` 与 `.agents/protocols/prompt-bootstrap.md` 的 `source` 来源，仍属活跃 canonical source | 修复 |
| `.trae/specs/standards-tools/analyze-script-merging/report.md` | 2 | 仅有两个 `end` 保留字冲突，修复成本极低，且位于 `standards-tools` 活跃主题下 | 修复 |

### 修复口径

1. 只做 Mermaid 安全写法修复，不改动正文结论。
2. 修完后继续纳入默认 `repo-check mermaid` 范围。
3. 不把这类“低成本真问题”转移成排除项。

## 二、豁免

### E1：等待家族级刷新，不做单点拆修

| 文件 | 错误 | 原因 | 结论 |
|---|---:|---|---|
| `.trae/specs/retrospectives-insights/first-principles-learning-mode-analysis/tasks.md` | 12 | 该文件仍被多个复盘 README 直接引用，但其 Mermaid 问题与同 family 的 `task*-output.md` 存在强耦合；若现在单独手修，后续 family 重生成时仍会重复返工 | 豁免 |

### 豁免口径

1. `豁免` 不是永久放弃，而是“等待同 family 的重生成/刷新窗口一起处理”。
2. 该类文件不应在 `8.10` 单独手修，也不应被粗暴归入历史排除。
3. 一旦再次触碰 `first-principles-learning-mode-analysis/` 家族，先消化此豁免，再做内容编辑。

## 三、排除

### P1：已完成的历史研究 spec family

以下目录/文件的共同特征是：

- 位于 `.trae/specs/retrospectives-insights/`
- 已完成、低复用、无明确当前 canonical 入口职责
- Mermaid 错误主要是旧写法遗留，而不是当前流程继续扩散的问题

| family / 文件 | 文件数 | 错误 | 原因 | 结论 |
|---|---:|---:|---|---|
| `analyze-ai-hardware-design-tools/`（`analysis-report.md` + `task4-8-output.md`） | 2 | 68 | 历史专题分析，非当前路由入口 | 排除 |
| `analyze-ems-energy-management-article/tasks.md` | 1 | 8 | 完成态任务文档，保留记录价值高于 Mermaid 治理价值 | 排除 |
| `analyze-github-speckit-article/analysis-report.md` | 1 | 1 | 仅历史分析留档，不值得单独起修复 | 排除 |
| `analyze-mem0-agent-memory-framework/`（`analysis-report.md` + `task2/3/4`） | 4 | 14 | 方法分析 family，当前无活跃治理任务承接 | 排除 |
| `analyze-wechat-article-1nNIr/task2-methodology-analysis.md` | 1 | 32 | 历史专题拆解，不是当前模板/规范源头 | 排除 |
| `analyze-wechat-article-E2FXmFb/`（`analysis-report.md` + `task4-tech-evolution.md`） | 2 | 2 | 历史专题分析，单独修复收益低 | 排除 |
| `analyze-yihuakaitian-meeting-record/tasks.md` | 1 | 8 | 已完成会议分析任务单，非当前复用资产 | 排除 |

### P2：`.agents/docs/retrospective/reports/` 下的历史报告产物

以下文件虽然仍可被 README/索引引用，但其主要价值是“保留历史内容”，不是“持续维护 Mermaid 可渲染性”：

| 目录/文件簇 | 文件数 | 错误 | 原因 | 结论 |
|---|---:|---:|---|---|
| `task-reports/2026-07-04-knowledge-sedimentation-workflow-retrospective.md` | 1 | 1 | 单次任务复盘，不应污染默认门禁 | 排除 |
| `task-reports/retrospective-first-principles-pattern-split-20260709/` | 2 | 11 | 历史 task report，被后续报告引用但不应继续手工补锅 | 排除 |
| `insight-extraction/external-learning/retrospective-architecture-priority-20260629/` | 1 | 5 | 历史外部学习报告；其下 insight 内容已被模式库吸收，README 自身不再是当前 Mermaid canonical source | 排除 |
| `insight-extraction/external-learning/retrospective-skills-article-learning-20260629/` | 2 | 3 | 历史学习报告派生物，低维护价值 | 排除 |
| `insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/insights/SEVEN-CONCEPTS-INDEX.md` | 1 | 6 | 历史洞察索引，不是当前模板源 | 排除 |
| `insight-extraction/external-learning/retrospective-firecrawl-learning-20260629/insights/insight-1-keyless.md` | 1 | 2 | 历史洞察条目，非持续维护资产 | 排除 |
| `competitive-analysis/retrospective-viitorvoice-tts-learning-20260703/insight-extraction.md` | 1 | 3 | 历史报告派生物 | 排除 |
| `atomization/retrospective-meta-atomization-full-chain-20260624/export-suggestions.md` | 1 | 1 | 历史导出建议，不值得留在 Mermaid 默认门禁 | 排除 |

### 排除口径

1. `排除` 的对象必须是“冻结历史产物”，不是当前规范入口。
2. 未来若重新打开这些目录做内容升级，应先把对应目录临时移回校验范围，再顺手修 Mermaid。
3. `repo-check mermaid` 当前只原生支持 `--exclude` 路径，不支持文件级“豁免”。因此 `排除` 应尽量按目录族或 spec family 落地，而不是靠临时口头约定。

## 四、重生成

### R1：`first-principles-learning-mode-analysis` 源头-镜像链路

这是本轮最典型的“不要双份手修”场景。

#### R1a：canonical source（应重生成）

| 文件簇 | 文件数 | 错误 | 警告 | 结论 |
|---|---:|---:|---:|---|
| `.trae/specs/retrospectives-insights/first-principles-learning-mode-analysis/task2-output.md` 等 8 个 `task*-output.md` | 8 | 172 | 22 | 重生成 |

#### R1b：downstream mirror（随源头同步）

| 文件簇 | 文件数 | 错误 | 警告 | 结论 |
|---|---:|---:|---:|---|
| `.agents/docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/01/02/03/04/08-*.md` | 5 | 86 | 24 | 不手修，随源头重生成/重同步 |

### R2：单次任务输出型 Markdown

| 文件簇 | 文件数 | 错误 | 警告 | 原因 | 结论 |
|---|---:|---:|---:|---|---|
| `.trae/specs/retrospectives-insights/analyze-douyin-vibecoding-guide/task3/4/6/7-output.md` | 4 | 105 | 2 | 明显属于输出阶段直接写入不安全 Mermaid，手修无法阻止下次再生成同类问题 | 重生成 |
| `.trae/specs/standards-tools/learn-volcengine-mobileuse-agent/analysis-result.md` | 1 | 24 | 0 | 典型分析结果页，问题集中于生成时未套安全模板 | 重生成 |
| `.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/minitest-ecosystem-insight-report.md` | 1 | 69 | 0 | 虽被扫描器按 S2 命名规则归类，但语义上是最终生成报告，应按“生成型输出”治理 | 重生成 |

### 重生成口径

1. 先修源模板/提示词/生成流程，再重跑产物。
2. 如果同时存在 `.trae/specs` 源头与 `.agents/docs` 镜像，永远只在源头家族上动刀。
3. 重生成完成前，对 mirror 文件不做双份手工修复。

## Canonical Source 决策规则

后续遇到同类问题，统一按以下顺序判断：

1. **先看是否被当前规范直接引用**：
   - 若像 `agent-app-marketplace/spec.md` 一样已成为 `.agents/` 规范的 `source`，优先归为 `修复`。
2. **再看是否为生成链路源头**：
   - 若存在 `task*-output.md` → `.agents/docs/...` 镜像链路，优先归为 `重生成`。
3. **再看是否只是冻结历史归档**：
   - 若只承担“历史保留”职责，不再作为模板/入口/流程源，归为 `排除`。
4. **最后才考虑豁免**：
   - 只用于“仍可见且仍被少量引用，但必须等待家族级刷新一起处理”的少数文件。

## 对 `SubTask 8.11` 的执行建议

1. 先把 `修复` 队列作为下一轮最小补丁收掉：
   - `.trae/specs/agent-app-marketplace/spec.md`
   - `.trae/specs/standards-tools/analyze-script-merging/report.md`
2. 将 `排除` 队列整理为明确目录/文件族清单，作为 `repo-check mermaid` 的默认排除基线。
3. 将 `重生成` 队列拆成独立治理主题，不与迁移收尾混做：
   - first-principles family
   - douyin family
   - learn-volcengine
   - minitest
4. 保留 `豁免` 清单作为“下一次触碰前必修”的已知债务，不阻塞本次迁移专项闭环。

## 最终口径

- **当前仍被主动消费的 canonical 文档**：修复。
- **成批生成的输出链路**：重生成，不做双份手修。
- **冻结的历史 spec / 报告归档**：排除出默认 Mermaid 门禁。
- **极少数需要等家族级刷新一起处理的可见文件**：豁免，但保留明确回收条件。
