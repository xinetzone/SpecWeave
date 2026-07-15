---
source:
  - "tasks.md#Task 8"
  - "artifacts/task8-10-mermaid-disposition-policy.md"
  - "artifacts/task8-9-docs-mermaid-fixes.md"
  - "artifacts/task8-6-textual-fixes.md"
  - "artifacts/task8-2-resolution.md"
  - "artifacts/docs-post-task8-baseline-summary.json"
generated_at: "2026-07-15"
task: "SubTask 8.11"
type: "final-verification"
status: "blocked"
---

# Task 8.11 最终复验

## 目标

- 基于 `task8-10-mermaid-disposition-policy.md` 的处置口径，复跑当前工作树下的 `repo-check all`。
- 对 `SubTask 8.8`、`8.9` 已治理的高价值 Mermaid 目录做必要抽样，确认此前修复未回退。
- 复验迁移专项仍关心的 `.agents/docs` 链接/frontmatter 门禁与基线覆盖情况。
- 判断本 spec 是否已满足回填 `tasks.md`、`checklist.md` 的最终收尾条件。

## 执行记录

| 检查项 | 命令/方法 | 结果 | 结论 |
|---|---|---|---|
| 全仓复验 | `python .agents/scripts/repo-check.py all` | 失败；Mermaid 子项报 `70` 个问题文件、`725` 个错误、`166` 个警告 | 未达到“只剩已决策历史/生成债务” |
| Git 忽略规则 | `python .agents/scripts/repo-check.py gitignore` | 通过 | 非 Mermaid 子项正常 |
| vendor 合规 | `python .agents/scripts/repo-check.py vendor` | 通过 | 非 Mermaid 子项正常 |
| 高价值目录簇抽样 A | `python .agents/scripts/check-mermaid.py --path ".agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki"` | `15` 文件，`0` 错误，`0` 警告 | `SubTask 8.9` 已治理目录保持稳定 |
| 高价值目录簇抽样 B | `python .agents/scripts/check-mermaid.py --path ".agents/docs/retrospective/patterns/methodology-patterns/governance-strategy"` | `109` 文件，`0` 错误，`0` 警告 | `SubTask 8.9` 已治理目录保持稳定 |
| 迁移专项链接/frontmatter 复验 | `python .agents/scripts/check-links.py --path .agents/docs --check-frontmatter-paths` | 通过；本地断链 `0`、frontmatter 路径问题 `0`、目录链接 warning `0` | 迁移专项自动化门禁已恢复通过 |
| 基线覆盖复验 | 读取 `docs-baseline-manifest.json` 并重算 `.agents/docs` 当前文件集合 | 基线 `2683` 文件 `0 missing`；当前文件 `2708`；新增文件 `25` | 物理迁移覆盖仍成立，但新增文件未稳定收敛 |
| Mermaid 收尾定向复验（`core`） | 逐文件调用 Mermaid 检查器验证 `13` 个 `core` 残留文件，并复跑 `python .agents/scripts/check-mermaid.py --path .agents` | `13` 个目标文件全部 `0 error`；`.agents` 全量复扫为 `0` 错误、`5` 警告 | 本文列出的 `core` 规范层 Mermaid `error` 已关闭，仅剩 warning |
| Mermaid 收尾定向复验（`.agents/docs`） | 逐文件调用 Mermaid 检查器验证 `2` 个回顾文档，并复跑 `python .agents/scripts/check-mermaid.py --path .agents/docs` | `2` 个目标文件全部 `0 error`；`.agents/docs` 全量复扫为 `0` 错误、`7` 警告 | 本文列出的 `.agents/docs` Mermaid `error` 已关闭，仅剩 warning |
| 第二轮全仓复验 | `python .agents/scripts/repo-check.py all` | 失败；当前为 `56` 个问题文件、`647` 个错误、`166` 个警告 | 仍未全绿，但失败面已明显收缩，需按是否属于迁移范围重新解读 |
| 第二轮 `.agents/docs` 链接/frontmatter 复验 | `python .agents/scripts/check-links.py --path .agents/docs --check-frontmatter-paths` | 通过；扫描 `2674` 个 Markdown，所有本地链接与 frontmatter 路径均有效 | 迁移专项自动化门禁继续保持通过 |
| 第二轮 `.agents/docs` Mermaid 全量复验 | `python .agents/scripts/check-mermaid.py --path .agents/docs` | `25` 个问题文件、`118` 个错误、`140` 个警告 | 失败面仍在，但主要落于 `8.10` 已定义的“排除/重生成”历史报告与镜像家族 |
| 第二轮基线/allowlist 对齐复验 | 按 `docs-baseline-manifest.json` 映射到 `.agents/docs/` 并比对 `task8-11-added-files-allowlist.md` | 基线 `2683`、当前 `2709`、`0 missing`、`26 extra`；`26` 个均已被 allowlist 覆盖 | 迁移覆盖已稳定，新增项人工判定已全部收敛，剩余问题仅为 allowlist/基线的机器化接入 |
| post-task8 基线产物生成 | 重算当前 `.agents/docs` 全量文件并生成 `docs-post-task8-baseline-manifest.json`、`docs-post-task8-baseline-summary.json` | `2709` 文件、`86862916` Bytes；相对原基线 `0 missing`、`26 extra`；`25` 个 formal allowlist + `1` 个 `derived-export` 全部入摘要 | 在不覆盖原 `docs-baseline-manifest.json` 的前提下，补齐了可直接消费的当前 `.agents/docs` 收尾基线 |

## Mermaid 失败面复分类

使用 `repo-check mermaid` 同一检查器对当前失败文件重新按 `8.7` / `8.10` 口径归类，结果如下：

| 类别 | 问题文件数 | 错误 | 警告 | 说明 |
|---|---:|---:|---:|---|
| `core` 规范层 | 14 | 53 | 2 | 仍有核心规范文档与模板未清零，不属于 `8.10` 历史/生成口径 |
| `.agents/docs` | 12 | 31 | 116 | 其中仅 2 个文件仍有 `error`，其余为 warning |
| 历史 spec 产物 | 9 | 74 | 0 | 与 `task8-10` 的 spec 处置口径一致 |
| 生成型输出 | 35 | 567 | 48 | 与 `task8-10` 的生成型输出口径一致 |
| 合计 | 70 | 725 | 166 | 当前全仓 Mermaid 失败面 |

### 结论一：`8.10` 口径只覆盖了部分失败面

`task8-10-mermaid-disposition-policy.md` 处理的是“历史 spec + 生成型输出”两大类债务；但本轮复验显示，当前工作树仍残留以下 **非 `8.10` 口径** 的 Mermaid `error` 文件：

#### A. `core` 规范层残留 `error`

1. `.agents/protocols/prompt-bootstrap.md`
2. `.agents/protocols/workspace-discovery.md`
3. `.agents/rules/data-security/cross-border-assessment/03-approval-dpa.md`
4. `.agents/rules/data-security/security-monitoring/01-overview-architecture.md`
5. `.agents/rules/meta-document-priority-principle.md`
6. `.agents/rules/three-stage-universal-principle.md`
7. `.agents/templates/design-review-standards.md`
8. `.agents/templates/mermaid-templates/flowchart-decision.md`
9. `.agents/templates/mermaid-templates/flowchart-top-bottom.md`
10. `.agents/templates/mermaid-templates/safe-starter.md`
11. `.agents/templates/new-user-first-quota-onboarding.md`
12. `.agents/templates/preflight-exploration-template.md`
13. `.agents/templates/two-stage-parallel-context-template.md`

另有 `.agents/rules/skill-five-elements-mindmap.md` 仅剩 warning。

#### B. `.agents/docs` 残留 `error`

1. `.agents/docs/retrospective/2026-07-12-io-safety-architecture-evolution.md`
2. `.agents/docs/retrospective/2026-07-13-task0-workspace-protocols.md`

其余 `.agents/docs` 命中文件当前仅剩 warning，主要集中在 `openai/chatgpt-codex-wiki/` 系列。

### 结论一补记：2026-07-15 Mermaid 收尾后，本文列出的 `.agents` / `.agents/docs` 阻断已关闭

- 已按最小修复收掉上文列出的 `13` 个 `core` 规范层文件与 `2` 个 `.agents/docs` 回顾文档的 Mermaid `error`。
- 精确逐文件复验结果：这 `15` 个目标文件当前均为 `0 error`。
- `.agents` 全量复扫当前仅剩 `4` 个问题文件、`0` 错误、`5` 警告；warning 分布在 `chatgpt-codex-wiki/` 系列与 `skill-five-elements-mindmap.md`。
- `.agents/docs` 全量复扫当前仅剩 `2` 个问题文件、`0` 错误、`7` 警告；warning 分布在 `insight-2-openai.md` 与 `case-3-openai-skills/SKILL.md`。

### 结论一再复验：上段只代表“定向收尾目标已关闭”，不代表 `.agents/docs` 全量 Mermaid 已清零

- 第二轮使用 `python .agents/scripts/check-mermaid.py --path .agents/docs` 做真正的 `.agents/docs` 全量复验后，结果为 `25` 个问题文件、`118` 个错误、`140` 个警告。
- 当前失败文件主要集中在两类：
  1. `task8-10-mermaid-disposition-policy.md` 已定义的 **P2 历史报告排除项**，例如 `task-reports/2026-07-04-knowledge-sedimentation-workflow-retrospective.md`、`retrospective-first-principles-pattern-split-20260709/`、`retrospective-architecture-priority-20260629/` 等；
  2. `8.10` 已定义的 **R1 downstream mirror**，即 `first-principles-learning-mode/01/02/03/04/08-*.md` 这组应随 `.trae/specs` 源头家族重生成的镜像文档。
- 因此，先前“`.agents/docs` 全量复扫为 `0 error`”的表述不再成立；更准确的结论应为：**本文原先点名的 `15` 个目标文件已清零，但 `.agents/docs` 范围仍存在属于 `8.10` 排除/重生成口径的历史 Mermaid 债务**。

### 结论二：`8.9` 已治理的高价值目录未回退

虽然全仓 Mermaid 仍失败，但抽样复扫显示至少以下两类高价值目录簇保持清零：

- `harness-seven-components-wiki/`：`15` 文件，`0` 错误，`0` 警告
- `governance-strategy/`：`109` 文件，`0` 错误，`0` 警告

这说明此前高价值目录的治理结果没有回退；当前 `repo-check all` 的 Mermaid 失败面，也**不再**来自本文先前列出的 `.agents` / `.agents/docs` 长尾文件。

## 迁移完整性复验

## 1. 覆盖性

- 基线 `2683` 文件在 `.agents/docs/` 下仍然 **无缺失**。
- 这一点说明“`docs/` → `.agents/docs/` 的物理搬迁覆盖”没有回退。

## 2. 新增文件收敛情况

相较 `migration-integrity-report-20260715.json` 中的 `18` 个新增文件：

- 已按 `SubTask 8.2` 处理并消失的旧新增项：`3`
- 仍保留的旧新增项：`15`
- 2026-07-15 报告之后新增的当前 extra file：`10`
- 当前 `.agents/docs` 总新增文件数：`25`

本轮新进入 extra 集合的样本包括：

1. `.agents/docs/retrospective/patterns/analysis-cards/css-stacking-context-overflow-clipping.md`
2. `.agents/docs/retrospective/patterns/code-patterns/overflow-protruding-element-isolation.md`
3. `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/README.md`
4. `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/execution-retrospective.md`
5. `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/export-suggestions.md`
6. `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/insight-extraction.md`
7. `.agents/docs/retrospective/reports/project-governance/documentation-governance/agents-manifest-changelog-archive.md`
8. `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/README.md`
9. `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/exports/sidebar-collapse-occlusion-report.md`
10. `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-ui-beautification-20260714.md`

### 2.1 10 个新增文件处置判定

| 文件 | 判定 | 依据 | 后续动作 |
|---|---|---|---|
| `patterns/analysis-cards/css-stacking-context-overflow-clipping.md` | 纳入 allowlist / 新基线 | 内容是从侧边栏遮挡复盘萃取出的独立知识卡片，目录归属与 frontmatter 语义均正确，属于正式知识资产而非迁移噪音 | 可保留；建议后续补录到 `analysis-cards/README.md` 索引 |
| `patterns/code-patterns/overflow-protruding-element-isolation.md` | 纳入 allowlist / 新基线 | 已被 `code-patterns/README.md` 收录，且被任务复盘正文回链引用，属于已落库的正式代码模式 | 可直接纳入 |
| `reports/incident-reports/retrospective-ui-beautification-failure-20260714/README.md` | 纳入 allowlist / 新基线 | 符合复盘目录四文件标准结构中的入口文件角色；`incident-reports/` 在仓库内已有先例，不是孤例脏数据 | 可保留；需补 incident 分类总索引/上级 README 说明 |
| `reports/incident-reports/retrospective-ui-beautification-failure-20260714/execution-retrospective.md` | 纳入 allowlist / 新基线 | 属于 incident 目录标准四件套之一，执行层内容完整且与 README 构成同一原子化报告单元 | 随目录整体纳入 |
| `reports/incident-reports/retrospective-ui-beautification-failure-20260714/export-suggestions.md` | 纳入 allowlist / 新基线 | 属于 incident 目录标准四件套之一，不是额外导出件 | 随目录整体纳入 |
| `reports/incident-reports/retrospective-ui-beautification-failure-20260714/insight-extraction.md` | 纳入 allowlist / 新基线 | 属于 incident 目录标准四件套之一，承接根因与模式提炼 | 随目录整体纳入 |
| `reports/project-governance/documentation-governance/agents-manifest-changelog-archive.md` | 纳入 allowlist / 新基线 | 已被 `AGENTS.md` 历史归档入口、`project-governance/README.md` 与 `documentation-governance/README.md` 三处显式引用，是正式治理归档资产 | 可直接纳入 |
| `reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/README.md` | 纳入 allowlist / 新基线 | 已被 `task-reports/README.md` 收录，且承担该任务复盘目录入口职责 | 可直接纳入 |
| `reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/exports/sidebar-collapse-occlusion-report.md` | 标注为派生产物，暂不纳入新基线 | 位于 `exports/` 子目录、frontmatter `type: export`，语义上更接近派生导出件；当前未被目录 README 或总索引收录，不宜直接作为迁移主基线资产 | 保留文件可接受，但应在后续 allowlist 中单独标注为导出件，或转出到更明确的 artifacts/export 区域 |
| `reports/task-reports/retrospective-sidebar-ui-beautification-20260714.md` | 纳入 allowlist / 新基线 | 已被 `reports/README.md` 归入 `task-reports` 清单，属于单文件任务复盘正式资产 | 可直接纳入 |

### 2.2 收敛结论

- 这 `10` 个新增文件中，建议 **`9` 个纳入 allowlist / 新基线**，`1` 个（`exports/sidebar-collapse-occlusion-report.md`）标注为派生产物，暂不作为迁移主基线资产。
- 因此，`task8-2-resolution.md` 中“新增文件应从 `18` 收敛到 `15`”的预期，**并非被证明错误**，而是被后续新增的正式文档资产扩展了口径。
- 当前真正未完成的已从“人工判定”转为“自动化接入”：这些保留项已形成正式 allowlist 与目录索引，但尚未被完整性脚本消费为新基线。

### 2.3 2026-07-15 落地产物

- 已创建正式 allowlist：`artifacts/task8-11-added-files-allowlist.md`
- 已补齐 `incident-reports/README.md`，将 `incident-reports/` 明确为复盘报告一级分类并建立目录索引
- 已补录 `analysis-cards/README.md` 中的 `css-stacking-context-overflow-clipping.md` 条目
- 已在 `reports/README.md` 中补充 `incident-reports/` 的上级分类说明，避免该目录继续表现为“孤立新增项”

### 2.4 第二轮 allowlist / 索引对齐结论

- 以 `docs-baseline-manifest.json` 映射到 `.agents/docs/` 的统一口径重算后，当前结果为：基线 `2683`、当前文件 `2709`、`0 missing`、`26 extra`。
- 这 `26` 个 extra 已全部被 `task8-11-added-files-allowlist.md` 覆盖，其中补录了 `.agents/docs/retrospective/reports/incident-reports/README.md` 这一一级目录索引入口。
- `incident-reports/README.md` 的语义与 allowlist 中其他 README 入口类资产一致，应视为正式保留的目录索引，而不是新的迁移异常。
- 换言之，新增文件问题已不再存在“未判定项”；当前剩余事项只剩 allowlist/基线接入是否机器化落地。

### 2.5 post-task8 基线产物与用途

- 已新增 `artifacts/docs-post-task8-baseline-manifest.json`：记录当前 `.agents/docs` 的全量文件清单（`2709` 项，字段与原 `docs-baseline-manifest.json` 保持同类风格：`relative_path`、`size_bytes`、`sha256`）。
- 已新增 `artifacts/docs-post-task8-baseline-summary.json`：记录当前快照摘要、与原基线的对比结果，以及 `task8-11-added-files-allowlist.md` 的对齐状态。
- 这对产物的设计目标不是替换“迁移前 `docs/` 原始基线”，而是**在保留原基线不变的前提下**，补一份“迁移收尾后的 `.agents/docs` 当前态基线”。
- 使用约定应明确区分两类基线：
  1. `docs-baseline-manifest.json` / `docs-baseline-summary.json`：保留为“迁移前原始 `docs/` 基线”，用于证明物理迁移覆盖是否回退；
  2. `docs-post-task8-baseline-manifest.json` / `docs-post-task8-baseline-summary.json`：作为“Task 8 收尾后的 `.agents/docs` 当前态基线”，用于后续完整性复核、人工对账或脚本切换接入。
- 当前 `docs-post-task8-baseline-summary.json` 已把 `26` 个 extra 全量结构化为：`25` 个正式保留资产 + `1` 个 `derived-export` 例外，且 `uncovered_extra_count = 0`，因此新增文件问题已从“人工判定阶段”推进到“可直接消费的机器读快照阶段”。

## 3. 链接与 frontmatter 门禁

`python .agents/scripts/check-links.py --path .agents/docs --check-frontmatter-paths` 当前通过：

- 本地断链：`0`
- frontmatter 路径问题：`0`
- 目录链接 warning：`0`

本轮已收敛的代表性问题包括：

1. `retrospective-sidebar-collapse-occlusion-20260714/README.md` 与其导出报告中的 `file:///d:/AI/...` 绝对路径已改为非断链写法
2. `retrospective-sidebar-collapse-occlusion-20260714/README.md` 中两条模式链接的层级错误已修正
3. 多个 `code-patterns` / `methodology-patterns` 文档的 `source`、`x-toml-ref` 及外部 TOML 路径已回填为当前仓库可验证路径

因此，Task 7 时成立的“`.agents/docs` 链接/frontmatter 校验通过”结论，**对当前工作树再次成立**。

## 最终判断

## 可确认成立

1. 迁移物理覆盖仍然成立：基线 `2683` 文件 `0 missing`
2. `SubTask 8.9` 已治理的高价值 Mermaid 目录簇抽样未回退
3. `.agents/docs` 的链接/frontmatter 自动化门禁已恢复通过
4. `repo-check all` 中 `gitignore`、`vendor`、`filename`、`roles` 非 Mermaid 子项未见新的阻断

## 当前不成立

1. `repo-check all` 仍未通过；第二轮结果为 `56` 个问题文件、`647` 个错误、`166` 个警告
2. `.agents/docs` 虽然链接/frontmatter 已通过，但 Mermaid 全量复验仍不通过；不过其失败面已可按 `8.10` 口径解释为历史报告排除项与下游镜像重生成项，而非本次迁移新增的 canonical 文档问题
3. 默认完整性流程尚未自动切换到 `docs-post-task8-baseline-*.json`；虽然新基线产物已生成，但脚本是否消费该快照仍需在后续收尾中显式决定

## 结论

第二轮复验后，可以将 `SubTask 8.11` 的阻断重新收敛为两类：

1. **迁移范围外的 Mermaid 债务**：
   - `.agents/docs` 中剩余的 Mermaid `error` 主要落在 `8.10` 已定义的历史报告排除项（P2）与 downstream mirror 重生成项（R1b）；
   - 全仓 `repo-check all` 中的其他失败面也主要位于 `.trae/specs` 活跃/历史 spec 家族与生成型输出，例如 `analyze-script-merging/report.md`、`learn-volcengine-mobileuse-agent/analysis-result.md` 等，不属于本次 `docs -> .agents/docs` 迁移本体。
2. **迁移收尾型基线接入问题**：
   - 迁移覆盖仍为 `0 missing`；
   - `.agents/docs` 链接/frontmatter 门禁持续通过；
   - 当前 `26` 个 extra 已全部完成 allowlist 判定，且已沉淀为 `docs-post-task8-baseline-manifest.json` / `docs-post-task8-baseline-summary.json` 两个机器可读产物；剩余工作只是在完整性流程中决定是否默认切换到这套新快照。

据此，本次迁移专项本体已基本复验完成；当前不宜再把 `repo-check all` 的红灯直接解释为“迁移未闭环”。更准确的判断是：**迁移内阻断已收敛，新增文件与基线收尾已具备机器可读快照，剩余阻断主要来自超出本次迁移范围的 Mermaid 治理，以及默认流程是否切换到 post-task8 基线的收尾决策**。若严格以“`repo-check all` 全绿 + 默认流程已切换新基线”作为完成定义，状态仍应暂记为 `blocked`；但其阻断性质已不再是迁移内容本身未通过。

## 建议下一步

1. 评估是否让迁移完整性复核流程默认消费 `artifacts/docs-post-task8-baseline-manifest.json` 与 `artifacts/docs-post-task8-baseline-summary.json`；若暂不切换，也应继续将 `artifacts/task8-11-added-files-allowlist.md` 与这对 JSON 一并作为人工复核的当前态基线保留
2. 把 `.agents/docs` 中剩余 Mermaid 失败文件按 `8.10` 的 `排除 / 重生成` 口径显式落地为默认排除基线或独立治理任务，避免继续以迁移阻断名义悬挂
3. 将 `.trae/specs` 中仍需处理的 `修复 / 重生成` 家族转交到迁移专项之外的 Mermaid 治理队列
