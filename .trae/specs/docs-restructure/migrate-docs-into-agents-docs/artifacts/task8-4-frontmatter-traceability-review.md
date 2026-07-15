---
source:
  - "artifacts/task8-3-suspect-grouping.md"
  - "artifacts/migration-integrity-report-20260715.md"
  - ".temp/backup/docs-before-agents-docs-20260715/"
generated_at: "2026-07-15"
task: "SubTask 8.4"
type: "frontmatter-traceability-review"
status: "completed"
---
# Task 8.4 frontmatter 溯源退化处理清单

## 处理范围

- 仅处理 `task8-3-suspect-grouping.md` 中归类为“frontmatter 溯源退化”的 9 个样本。
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。
- 处理策略：优先按基线恢复 `source`；仅当 `x-toml-ref` 也出现退化时才回补 `x-toml-ref`。

## 已修复（9）

| 文件 | 处理动作 | 依据 |
|---|---|---|
| `.agents/docs/knowledge/best-practices/pdf-export-mermaid-automation-insights.md` | 将 `source` 从 `external: 不存在-...` 恢复为基线中的具体 README 路径 | `.temp/backup/docs-before-agents-docs-20260715/knowledge/best-practices/pdf-export-mermaid-automation-insights.md` |
| `.agents/docs/retrospective/patterns/code-patterns/command-injection-prevention.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/command-injection-prevention.md` |
| `.agents/docs/retrospective/patterns/code-patterns/defensive-config-cache-deepcopy.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/defensive-config-cache-deepcopy.md` |
| `.agents/docs/retrospective/patterns/code-patterns/dynamic-path-derivation.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/dynamic-path-derivation.md` |
| `.agents/docs/retrospective/patterns/code-patterns/exception-precision-guards.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/exception-precision-guards.md` |
| `.agents/docs/retrospective/patterns/code-patterns/idempotent-shell-config.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/idempotent-shell-config.md` |
| `.agents/docs/retrospective/patterns/code-patterns/ring-buffer-streaming-output.md` | 将 `source` 从 `README.md` 恢复为基线中的原始模式汇总文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/code-patterns/ring-buffer-streaming-output.md` |
| `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/defensive-programming-first-principles.md` | 将 `source` 从 `external:` 摘要恢复为基线中的具体原则文件 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/methodology-patterns/governance-strategy/defensive-programming-first-principles.md` |
| `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/depth-reference-table.md` | 将摘要化单行 `source` 恢复为基线中的双来源列表 | `.temp/backup/docs-before-agents-docs-20260715/retrospective/patterns/methodology-patterns/tools-automation/depth-reference-table.md` |

## 待人工判断（0）

- 本轮 9 个样本均能从备份基线直接恢复到更精确的 `source`，未留下需人工判断项。

## 备注

- 本轮未改动任何 `x-toml-ref`：9 个样本中现有 `x-toml-ref` 均未出现新的退化，保持迁移后的正确层级。
- 附带的正文差异不在 `SubTask 8.4` 处理范围内，保留给后续 `SubTask 8.6` 最小修复。
