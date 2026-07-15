---
source:
  - "artifacts/task8-3-suspect-grouping.md"
  - "artifacts/task8-4-frontmatter-traceability-review.md"
  - ".temp/backup/docs-before-agents-docs-20260715/"
generated_at: "2026-07-15"
task: "SubTask 8.6"
type: "textual-fixes-review"
status: "completed"
---

# Task 8.6 正文链接/文案样本最小修复与复核

## 处理范围

- 仅复核 `task8-3-suspect-grouping.md` 中“正文链接或文案变更”分类的 6 个样本。
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。
- 处理原则：只修复明确的“去链接化/正文误改”，对迁移后正确的相对路径层级调整予以保留。

## 处理结果

| 文件 | 动作 | 说明 | 复核结果 |
|---|---|---|---|
| `.agents/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.md` | 已修复 | 将 `.agents/.cache/spec-loader.json` 从纯文本恢复为可点击链接；保留其余已适配到 `.agents/` 新层级的相对路径 | 目标 `../../../.cache/spec-loader.json` 存在 |
| `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md` | 已修复 | 将 `skills-ref/src/skills_ref/` 从纯文本恢复为可点击链接；保留 `.agents/skills/` 等迁移后正确路径 | 目标 `../../../../../../external/agentskills/skills-ref/src/skills_ref/`、`../../../../../skills/README.md` 均存在 |
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md` | 复核后不改 | 差异仅表现为 `x-toml-ref` 层级调整与 frontmatter 排序；未发现正文链接/文案受损 | 现有 `x-toml-ref` 指向存在，不纳入本轮修复 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.md` | 已修复 | 将开头 `weasyprint/` 目录引用从纯文本恢复为可点击链接；保留后续已适配的新相对路径 | 目标 `../../../../../../external/WeasyPrint/weasyprint/` 存在 |
| `.agents/docs/knowledge/learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md` | 复核后不改 | 当前章节末尾内部导航、`AGENTS.md`、`rules/` 路径均能解析到真实目标，判定为迁移后的必要路径修正 | 6 条目标路径均存在，不纳入本轮修复 |
| `.agents/docs/knowledge/operations/vendor-flexloop-integration-guide.md` | 已修复 | 将 `.agents/scripts/tests/` 从纯文本恢复为可点击链接；保留其余已适配到 `.agents/` 新层级的相对路径 | 目标 `../../../scripts/tests/` 存在 |

## 复核方法

1. 逐个对比当前文件与 `.temp/backup/docs-before-agents-docs-20260715/` 基线差异。
2. 对疑似正文改动逐项判断：是“迁移后必要路径修正”还是“正文去链接化/误改”。
3. 对已修复与保留的关键目标路径做存在性检查，确认链接解析到真实文件或目录。
4. 对本轮实际编辑的 4 个文件运行编辑器诊断，确认无新增诊断问题。

## 备注

- 本轮 6 个样本中，4 个需要最小修复，2 个经复核确认为误报或合理迁移差异。
- 复核过程中发现 `vendor-flexloop-integration-guide.md` 另有一个预存的断链 `../../../vendor/flexloop/apps/chaos/.agents/rules/python.md`，但不属于本轮 6 个样本的最小修复范围，保持未动。
