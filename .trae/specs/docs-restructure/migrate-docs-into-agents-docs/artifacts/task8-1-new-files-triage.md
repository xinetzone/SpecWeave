---
source:
  - "artifacts/migration-integrity-report-20260715.md"
  - "tasks.md"
generated_at: "2026-07-15"
task: "SubTask 8.1"
type: "new-files-triage-report"
status: "completed"
---

# Task 8.1 新增文件分类完整性报告

## 目标

对 `migration-integrity-report-20260715.md` 中列出的 `18` 个“当前额外新增文件”进行三分归类，形成：

1. `纳入新基线`
2. `移位`
3. `删除`

本报告只给出分类结论与后续建议，不修改 `tasks.md`。

## 判定口径

1. 若文件承担迁移后新增的目录入口、导航、边界声明或归档说明职责，且当前目录结构已依赖该文件，则归入 `纳入新基线`。
2. 若文件本身合理，但当前落位与正文中的 `x-toml-ref`、目录语义或 `.meta` 约定不一致，则归入 `移位`。
3. 若文件既无正文引用、又不承担目录入口职责，且明显属于迁移噪音或误生成物，则归入 `删除`。
4. 本轮优先采用“保守保留”策略：有明确用途的新增入口文档先保留并纳入新基线；只有路径明显错误的派生元数据进入 `移位`；没有发现必须直接删除的样本。

## 结论总览

| 分类 | 数量 | 结论 |
|---|---:|---|
| 纳入新基线 | 15 | 均为新增的目录入口/导航型 `README.md`，属于迁移后治理补强 |
| 移位 | 3 | 均为 `.toml` 派生元数据，当前路径与 `x-toml-ref` 或目录语义不一致 |
| 删除 | 0 | 本轮未发现必须直接删除的新增文件 |

## 纳入新基线（15）

这些文件的共同特征是：

- 文件名均为 `README.md`
- 位于原先缺少目录入口说明的子目录
- 内容以“目录定位 / 子目录导航 / 相关资源 / 使用说明”为主
- 作用是补足迁移后的人类可读导航与边界声明，不属于噪音

| 文件 | 判定理由 | 建议 |
|---|---|---|
| `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/README.md` | 新增子目录索引，承担导航入口 | 纳入新基线 |
| `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/README.md` | 新增子目录索引，承担导航入口 | 纳入新基线 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/resources/README.md` | 为空壳资源目录补充入口说明 | 纳入新基线 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/syntax/README.md` | 为语法子目录补充入口说明 | 纳入新基线 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/templates/README.md` | 为模板子目录补充入口说明 | 纳入新基线 |
| `.agents/docs/knowledge/learning/07-vendor-product-learning/openai/README.md` | 为 `openai` 学习目录建立一级入口 | 纳入新基线 |
| `.agents/docs/retrospective/archives/xinet/core/README.md` | 为归档分层目录补充边界说明 | 纳入新基线 |
| `.agents/docs/retrospective/archives/xinet/reference/README.md` | 为归档分层目录补充边界说明 | 纳入新基线 |
| `.agents/docs/retrospective/archives/xinet/temporary/README.md` | 为归档分层目录补充边界说明 | 纳入新基线 |
| `.agents/docs/retrospective/reports/competitive-analysis/README.md` | 为报告分类目录建立人类可读入口 | 纳入新基线 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/README.md` | 为高频使用分类目录建立入口 | 纳入新基线 |
| `.agents/docs/retrospective/reports/insight-extraction/iot-ecosystem/README.md` | 为专题分类目录建立入口 | 纳入新基线 |
| `.agents/docs/retrospective/reports/insight-extraction/meta-methodology/README.md` | 为专题分类目录建立入口 | 纳入新基线 |
| `.agents/docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/README.md` | 为原子化报告目录补充入口 | 纳入新基线 |
| `.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/README.md` | 为专题分类目录建立入口 | 纳入新基线 |

## 移位（3）

这 3 个文件都不是“应删除”的噪音，而是“应存在但放错位置”的派生元数据：

| 当前文件 | 问题 | 建议目标路径 | 建议 |
|---|---|---|---|
| `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/first-principles-insight.toml` | `first-principles-insight.md` 的 `x-toml-ref` 指向 `.../insights/first-principles-insight.toml`，当前文件少了一层 `insights/` | `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/insights/first-principles-insight.toml` | 移位后纳入新基线 |
| `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task6-cowork-data-insights.toml` | 当前落在 `retrospective/.meta/toml/.trae/specs/...`，但正文 `task6-cowork-data-insights.md` 的 `x-toml-ref` 指向 `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task6-cowork-data-insights.toml` | `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task6-cowork-data-insights.toml` | 移位后纳入新基线 |
| `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task7-industry-insights.toml` | 当前落在 `retrospective/.meta/toml/.trae/specs/...`，但正文 `task7-industry-insights.md` 的 `x-toml-ref` 指向 `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task7-industry-insights.toml` | `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task7-industry-insights.toml` | 移位后纳入新基线 |

## 删除（0）

本轮未发现必须直接删除的新增文件。

原因：

- 15 个 `README.md` 明确承担目录入口或边界声明职责
- 3 个 `.toml` 文件虽落位错误，但都能映射到明确的正文文件或元数据目标路径
- 因此当前更合适的动作是“保留并归正”，而不是直接删除

## 建议

1. 在 `SubTask 8.2` 中优先处理低争议项：将 15 个 `README.md` 统一视为迁移后新增入口文档，补入新基线。
2. 对 3 个 `.toml` 采用“先移位、再复验”的处理方式，不建议直接删除后重建，以免丢失已有 `id/title` 元数据。
3. 移位完成后，复查对应正文文件中的 `x-toml-ref` 是否全部命中目标路径；若仍不一致，再决定是修正文档引用还是重生成 `.toml`。
4. 重新生成完整性报告时，可将本报告作为 `added files allowlist` 的人工判定依据：`15 保留 + 3 归正后保留 + 0 删除`。

## 给 SubTask 8.2 的执行顺序建议

1. 先将 15 个 `README.md` 标记为“纳入新基线”。
2. 再处理 3 个 `.toml` 的移位与旧路径清理。
3. 最后复跑完整性比对，确认 `added files` 从 `18` 收敛到 `0` 或只剩可解释项。
