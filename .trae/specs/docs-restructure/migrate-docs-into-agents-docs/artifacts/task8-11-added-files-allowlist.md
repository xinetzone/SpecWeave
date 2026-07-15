---
source:
  - "artifacts/task8-1-new-files-triage.md"
  - "artifacts/task8-2-resolution.md"
  - "artifacts/task8-11-final-verification.md"
generated_at: "2026-07-15"
task: "SubTask 8.11"
type: "added-files-allowlist"
status: "completed"
scope: ".agents/docs"
---

# Task 8.11 正式 added-files allowlist

## 目标

- 将 `SubTask 8.1`、`8.2` 与 `8.11` 已完成判定的新增 `.agents/docs` 文件整理为正式 allowlist 产物。
- 明确区分“纳入迁移主基线的正式资产”与“允许保留但需单独标注的导出件”。
- 为后续完整性复核重算基线或接入 allowlist 提供单一依据，避免继续在复验文档中重复人工判定。

## 主 allowlist（25）

以下文件应视为迁移后新增但**正式保留**的 `.agents/docs` 资产；后续无论采用“重生成基线”还是“脚本消费 allowlist”，都应纳入主口径。

### A. `SubTask 8.2` 已确认保留的目录入口 README（15）

1. `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/README.md`
2. `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/README.md`
3. `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/resources/README.md`
4. `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/syntax/README.md`
5. `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/templates/README.md`
6. `.agents/docs/knowledge/learning/07-vendor-product-learning/openai/README.md`
7. `.agents/docs/retrospective/archives/xinet/core/README.md`
8. `.agents/docs/retrospective/archives/xinet/reference/README.md`
9. `.agents/docs/retrospective/archives/xinet/temporary/README.md`
10. `.agents/docs/retrospective/reports/competitive-analysis/README.md`
11. `.agents/docs/retrospective/reports/insight-extraction/external-learning/README.md`
12. `.agents/docs/retrospective/reports/insight-extraction/iot-ecosystem/README.md`
13. `.agents/docs/retrospective/reports/insight-extraction/meta-methodology/README.md`
14. `.agents/docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/README.md`
15. `.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/README.md`

### B. `SubTask 8.11` 新增正式资产（10）

| 文件 | 资产类型 | 保留依据 |
|---|---|---|
| `.agents/docs/retrospective/patterns/analysis-cards/css-stacking-context-overflow-clipping.md` | 分析卡片 | 已形成独立知识卡片，目录归属正确，补入 `analysis-cards/README.md` 后可被发现 |
| `.agents/docs/retrospective/patterns/code-patterns/overflow-protruding-element-isolation.md` | 代码模式 | 已被 `code-patterns/README.md` 收录，并由任务复盘正文回链引用 |
| `.agents/docs/retrospective/reports/incident-reports/README.md` | incident 分类索引入口 | 已明确为 `incident-reports/` 一级分类索引，承担目录边界声明与报告发现入口职责，语义上与其他 README 入口类资产一致 |
| `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/README.md` | incident 报告入口 | 属于事件复盘标准目录结构的入口文件 |
| `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/execution-retrospective.md` | incident 执行复盘 | 与同目录 `README.md` 共同构成原子化报告单元 |
| `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/export-suggestions.md` | incident 导出建议 | 属于事件复盘标准四件套之一，不是独立导出件 |
| `.agents/docs/retrospective/reports/incident-reports/retrospective-ui-beautification-failure-20260714/insight-extraction.md` | incident 洞察萃取 | 属于事件复盘标准四件套之一 |
| `.agents/docs/retrospective/reports/project-governance/documentation-governance/agents-manifest-changelog-archive.md` | 治理归档 | 已被多处正式入口显式引用，属于治理档案资产 |
| `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/README.md` | task 报告入口 | 已被 `task-reports/README.md` 收录，承担目录入口职责 |
| `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-ui-beautification-20260714.md` | 单文件 task 复盘 | 已被 `reports/README.md` 归入 `task-reports` 清单 |

## 单独标注的导出件（1）

以下文件允许保留，但**不纳入主 allowlist**，应作为“导出件例外”单独处理：

| 文件 | 标记 | 说明 |
|---|---|---|
| `.agents/docs/retrospective/reports/task-reports/retrospective-sidebar-collapse-occlusion-20260714/exports/sidebar-collapse-occlusion-report.md` | `derived-export` | 位于 `exports/` 子目录，frontmatter `type: export`，语义上属于派生产物而非迁移主基线资产 |

## 不再纳入口径的已处理项

- `SubTask 8.2` 已清理的 `3` 个错放 `.toml` 副本不属于本 allowlist 范围。
- 本文件只定义“允许保留的新增 `.agents/docs` 资产”，不替代迁移脚本的基线文件，也不自动修改完整性比对结果。

## 使用约定

1. 若后续选择重生成基线，主 allowlist 中的 `25` 个文件应被视为新的规范内资产。
2. 若后续选择脚本消费 allowlist，本文件可直接作为人工判定依据转写为机器可读配置。
3. `derived-export` 项应继续保留单独标签，避免与正式迁移资产混淆。
