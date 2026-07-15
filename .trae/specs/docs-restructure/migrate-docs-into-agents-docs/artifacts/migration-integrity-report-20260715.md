---
source: "artifacts/docs-baseline-manifest.json + .temp/backup/docs-before-agents-docs-20260715/ + .agents/docs/"
generated_at: "2026-07-15 10:23:13"
task: "Task 7.4"
type: "migration-integrity-report"
---

# 迁移完整性报告（2026-07-15）

## 结论摘要

- 基线文件总数：`2683`
- 完全一致：`330`
- 预期路径修复改动：`2315`
- 疑似内容损坏/结构性改动：`38`
- 缺失文件：`0`
- 当前额外新增文件：`18`
- 当前判定：`pending-manual-review`

结论：基线 `2683` 个文件已全部映射到 `.agents/docs/`，不存在缺失；此前 `2353` 个哈希差异中，按本报告口径可将 `2315` 个判定为“仅路径修复副作用”，剩余 `38` 个文件仍需人工复核，另有 `18` 个当前新增文件需确认是否纳入新基线。

## Task 7.4 校验口径

1. `完全一致`：当前文件 SHA256 与基线完全一致。
2. `预期路径修复改动`：SHA256 不一致，但将当前内容中的 `.agents/docs` 根路径折返为 `docs` 后，或屏蔽承载路径的行后，文本与基线一致。
3. `疑似内容损坏/结构性改动`：不满足上面两条，说明变更超出纯路径修复范围，可能涉及正文、frontmatter 溯源、README 结构或文案改写。
4. `缺失文件`：基线文件在 `.agents/docs/` 下找不到。
5. `当前额外新增文件`：当前 `.agents/docs/` 存在但原 `docs/` 基线不存在的文件；不直接视为损坏，但必须在复验前确认是否应纳入新基线。

## 分布情况

- 疑似改动分布：`README.md` → `1` 个
- 疑似改动分布：`knowledge` → `7` 个
- 疑似改动分布：`retrospective` → `28` 个
- 疑似改动分布：`reuse-and-generalization.md` → `1` 个
- 疑似改动分布：`standards` → `1` 个

## 代表性疑似样本

| 文件 | 现象 | 初步判断 |
|---|---|---|
| `.agents/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.md` | `@@ -5,3 +5,3 @@
 / -x-toml-ref: "../../../.meta/toml/docs/knowledge/best-practices/l2-progressive-disclosure-optimiza...` | 除 frontmatter 层级修正外还伴随正文链接/文案变更 |
| `.agents/docs/knowledge/best-practices/pdf-export-mermaid-automation-insights.md` | `@@ -3,3 +3,3 @@
 / -x-toml-ref: "../../../.meta/toml/docs/knowledge/best-practices/pdf-export-mermaid-automation-insi...` | frontmatter source 被回填为 README，疑似溯源退化 |
| `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md` | `@@ -3,3 +3,3 @@
 / -x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agen...` | 除 frontmatter 层级修正外还伴随正文链接/文案变更 |
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md` | `@@ -8,3 +8,2 @@
 / -  x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/ha...` | frontmatter 调整之外仍有非纯路径差异 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.md` | `@@ -3,4 +3,4 @@
 / -x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-...` | 除 frontmatter 层级修正外还伴随正文链接/文案变更 |
| `.agents/docs/knowledge/learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md` | `@@ -11,3 +11,3 @@
 / -x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/first-principles/15-cross-domain...` | 除 frontmatter 层级修正外还伴随正文链接/文案变更 |
| `.agents/docs/knowledge/operations/vendor-flexloop-integration-guide.md` | `@@ -3,3 +3,3 @@
 / -x-toml-ref: "../../../.meta/toml/docs/knowledge/operations/vendor-flexloop-integration-guide.toml...` | 除 frontmatter 层级修正外还伴随正文链接/文案变更 |
| `.agents/docs/README.md` | `@@ -1,4 +1,55 @@
 / -# 项目文档 / +# docs 文档边界说明` | 根 README 被重写为边界说明，属于结构性改写 |
| `.agents/docs/retrospective/patterns/code-patterns/command-injection-prevention.md` | `@@ -2,3 +2,3 @@
 / -source: ".agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md" / ...` | frontmatter source 被回填为 README，疑似溯源退化 |
| `.agents/docs/retrospective/patterns/code-patterns/defensive-config-cache-deepcopy.md` | `@@ -2,3 +2,3 @@
 / -source: ".agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md" / ...` | frontmatter source 被回填为 README，疑似溯源退化 |
| `.agents/docs/retrospective/patterns/code-patterns/dynamic-path-derivation.md` | `@@ -2,3 +2,3 @@
 / -source: ".agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md" / ...` | frontmatter source 被回填为 README，疑似溯源退化 |
| `.agents/docs/retrospective/patterns/code-patterns/exception-precision-guards.md` | `@@ -2,3 +2,3 @@
 / -source: ".agents/insights/infrastructure/dev-env-adversarial-review-20260709/code-patterns.md" / ...` | frontmatter source 被回填为 README，疑似溯源退化 |

## 需人工复核文件（38 个）

- `.agents/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/knowledge/best-practices/pdf-export-mermaid-automation-insights.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md`：frontmatter 调整之外仍有非纯路径差异
- `.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/knowledge/learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/knowledge/operations/vendor-flexloop-integration-guide.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/README.md`：根 README 被重写为边界说明，属于结构性改写
- `.agents/docs/retrospective/patterns/code-patterns/command-injection-prevention.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/code-patterns/defensive-config-cache-deepcopy.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/code-patterns/dynamic-path-derivation.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/code-patterns/exception-precision-guards.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/code-patterns/idempotent-shell-config.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/code-patterns/ring-buffer-streaming-output.md`：frontmatter source 被回填为 README，疑似溯源退化
- `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/defensive-programming-first-principles.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/depth-reference-table.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/execution-retrospective.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/action-items.md`：frontmatter 调整之外仍有非纯路径差异
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task2-core-points.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task3-argument-logic.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task4-key-concepts.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task5-quality-assessment.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task6-industry-insights.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-karpathy-agent-fallacy-20260707/README.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/export-suggestions.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/README.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/execution-retrospective.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/execution-retrospective.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/insight-extraction.md`：frontmatter 调整之外仍有非纯路径差异
- `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/README.md`：frontmatter 调整之外仍有非纯路径差异
- `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-project-comprehensive-20260626/report.md`：frontmatter 调整之外仍有非纯路径差异
- `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/execution-retrospective.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/export-suggestions.md`：存在无法归入纯路径修复的正文或元数据变更
- `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/insight-action-backlog.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/README.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/01-phase1-facts.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/reuse-and-generalization.md`：除 frontmatter 层级修正外还伴随正文链接/文案变更
- `.agents/docs/standards/README.md`：存在无法归入纯路径修复的正文或元数据变更

## 当前新增文件（18 个）

- `.agents/docs/.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/first-principles-insight.toml`
- `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/README.md`
- `.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/README.md`
- `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/resources/README.md`
- `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/syntax/README.md`
- `.agents/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/templates/README.md`
- `.agents/docs/knowledge/learning/07-vendor-product-learning/openai/README.md`
- `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task6-cowork-data-insights.toml`
- `.agents/docs/retrospective/.meta/toml/.trae/specs/retrospectives-insights/analyze-wechat-article-nglw6zYVjFEzM6boqn6uyg/task7-industry-insights.toml`
- `.agents/docs/retrospective/archives/xinet/core/README.md`
- `.agents/docs/retrospective/archives/xinet/reference/README.md`
- `.agents/docs/retrospective/archives/xinet/temporary/README.md`
- `.agents/docs/retrospective/reports/competitive-analysis/README.md`
- `.agents/docs/retrospective/reports/insight-extraction/external-learning/README.md`
- `.agents/docs/retrospective/reports/insight-extraction/iot-ecosystem/README.md`
- `.agents/docs/retrospective/reports/insight-extraction/meta-methodology/README.md`
- `.agents/docs/retrospective/reports/insight-extraction/standalone/first-principles-learning-mode/README.md`
- `.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/README.md`

## 建议下一步

1. 先逐项复核上述 38 个疑似文件，优先处理 `source:` 被改写、根 README 重写、正文链接被替换为纯文本或路径被异常规范化的样本。
2. 对 18 个新增文件判定“应保留并纳入新基线”还是“迁移过程派生噪音应清理”。
3. 在 38 个疑似项与 18 个新增项处理完后，重新生成基线或补充 allowlist，再执行 Task 7.5 的 `check-links.py`、`ci-check.ps1` 与迁移完整性复验。

## 机器明细

- JSON 明细：`.trae/specs/docs-restructure/migrate-docs-into-agents-docs/artifacts/migration-integrity-report-20260715.json`
