---
source:
  - "artifacts/task8-1-new-files-triage.md"
  - "artifacts/migration-integrity-report-20260715.md"
  - ".agents/docs/"
  - ".meta/toml/"
generated_at: "2026-07-15"
task: "SubTask 8.2"
type: "resolution-summary"
status: "completed"
---

# Task 8.2 低争议新增文件处理结果

## 结论摘要

- `15` 个新增 `README.md` 已确认为迁移后应保留的目录入口文档，作为“纳入新基线”样本记录。
- `3` 个新增 `toml` 异常项已完成归正：确认正文实际使用的规范路径位于仓库根 `.meta/toml/`，并清理 `.agents/docs/` 下的错放副本。
- 额外补做 `2` 处索引修正，使 `standalone/first-principles-learning-mode/README.md` 可从父级入口被发现。
- `tasks.md` 未修改。

## 一、纳入新基线的 README（15）

以下文件已确认为迁移后新增但合理的目录入口/边界说明文档，应在后续基线重生成或 allowlist 补录时视为“保留项”：

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

## 二、3 个 toml 的归正结果

### 处理原则

- 先核对对应正文文件的 `x-toml-ref`。
- 若规范目标路径已存在有效 `.toml`，则将 `.agents/docs/` 下的重复副本视为“错放副本”而非“缺失待移动文件”。
- 以正文真实引用的 canonical 路径为准，避免把文件移动到无人引用的新位置。

### 实际核对结果

| 正文文件 | 正文 `x-toml-ref` 指向 | 处理结果 |
|---|---|---|
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/insights/first-principles-insight.md` | `.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/insights/first-principles-insight.toml` | 仓库根 `.meta/toml/` 下目标文件已存在；删除 `.agents/docs/.meta/.../first-principles-insight.toml` 错放副本 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task6-cowork-data-insights.md` | `.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task6-cowork-data-insights.toml` | 仓库根 `.meta/toml/` 下目标文件已存在；删除 `.agents/docs/retrospective/.meta/.../task6-cowork-data-insights.toml` 错放副本 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task7-industry-insights.md` | `.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-gpt56-industry-shift-20260708/task7-industry-insights.toml` | 仓库根 `.meta/toml/` 下目标文件已存在；删除 `.agents/docs/retrospective/.meta/.../task7-industry-insights.toml` 错放副本 |

### 说明

`task8-1-new-files-triage.md` 中给出的“建议目标路径”采用了 `.agents/docs/.meta/...` 口径，但实际正文引用与仓库现状均表明 canonical 位置是仓库根 `.meta/toml/...`。因此本次按“引用真实命中优先”执行归正，未额外制造第二套 `.meta` 目录。

## 三、索引/说明修正

为保证新增 README 真正可发现，本次补了以下索引：

1. 更新 `.agents/docs/retrospective/reports/insight-extraction/standalone/README.md`，新增 `first-principles-learning-mode/README.md` 入口。
2. 更新 `.agents/docs/retrospective/reports/README.md`，将 `standalone/` 小节从“仅独立洞察卡片”扩展为“独立洞察卡片 + 原子化补充目录”，并加入 `first-principles-learning-mode/` 条目。

其余 14 个 README 的父级导航已存在可达入口，本轮未做额外改写。

## 四、执行清单

- 已删除错放副本：
  - `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/first-principles-insight.toml`
  - `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task6-cowork-data-insights.toml`
  - `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task7-industry-insights.toml`
- 已更新索引：
  - `.agents/docs/retrospective/reports/insight-extraction/standalone/README.md`
  - `.agents/docs/retrospective/reports/README.md`

## 五、后续建议

1. 在后续 `SubTask 8.11` 或完整性复验阶段，基于本文件与 `task8-1-new-files-triage.md` 生成正式 allowlist 或新基线快照。
2. 重新生成迁移完整性报告时，应将“当前额外新增文件”从 `18` 收敛为 `15`，剩余项均为本次确认保留的 README。
3. 如需彻底消除报告中的新增项，下一步应更新基线/allowlist，而不是继续改动这 15 个 README 本身。
