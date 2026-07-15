---
source:
  - "tasks.md#Task 8"
  - "artifacts/task8-10-mermaid-disposition-policy.md"
  - "artifacts/task8-9-docs-mermaid-fixes.md"
  - "artifacts/task8-6-textual-fixes.md"
  - "artifacts/task8-2-resolution.md"
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

### 结论二：`8.9` 已治理的高价值目录未回退

虽然全仓 Mermaid 仍失败，但抽样复扫显示至少以下两类高价值目录簇保持清零：

- `harness-seven-components-wiki/`：`15` 文件，`0` 错误，`0` 警告
- `governance-strategy/`：`109` 文件，`0` 错误，`0` 警告

这说明本轮阻断项不是已治理目录回退，而是 **尚未纳入或未彻底收敛的 core/docs 长尾文件**。

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

因此，`task8-2-resolution.md` 中“新增文件应从 `18` 收敛到 `15`”的预期，**在当前工作树上不再成立**。这不等于迁移丢文件，但意味着新增项基线/allowlist 还未稳定。

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

1. `repo-check all` 失败面 **并未** 收敛到“只剩 `8.10` 已决策的历史 spec / 生成型输出”
2. 新增文件集合 **并未** 稳定收敛到 `8.2` 预期的 `15` 个保留项

## 结论

`SubTask 8.11` 已完成复验与结论文档化，但 **验证未通过**，当前应维持 `blocked` 状态，暂不将 `Task 8` 或 `SubTask 8.11` 回填为完成。

## 建议下一步

1. 先补收尾 `core` 规范层残留 Mermaid `error`，尤其是 `.agents/protocols/`、`.agents/templates/`
2. 再收掉 `.agents/docs` 中仍有 `error` 的 2 个回顾文档，并单独决定 `chatgpt-codex-wiki/` 系列 warning 是否纳入治理范围
3. 为 2026-07-15 之后新增的 10 个 `.agents/docs` 文件补做 allowlist 或新基线决策，再重跑完整性复核
