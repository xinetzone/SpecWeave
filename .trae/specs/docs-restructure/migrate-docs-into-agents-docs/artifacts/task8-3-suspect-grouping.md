---
source:
  - "migration-integrity-report-20260715.md"
  - "../tasks.md"
generated_at: "2026-07-15"
task: "SubTask 8.3"
type: "suspect-grouping-report"
status: "completed"
---

# Task 8.3 疑似改动四类分组报告

## 目标

将 `migration-integrity-report-20260715.md` 中 `38` 个“疑似内容损坏/结构性改动”样本按类型分组，形成后续治理输入，供 `SubTask 8.4`、`8.5`、`8.6` 继续处理。

本报告只给出分组结论、样本清单与后续建议，不修改 `tasks.md`。

## 分组口径

1. **README / 入口级结构性改写**：目录入口、边界说明或总览页被整体重写，不能按“纯路径修复”处理。
2. **frontmatter 溯源退化**：`source`、`x-toml-ref` 或多源列表被回填、摘要化、外部化，导致可追溯性下降。
3. **正文链接或文案变更**：正文中的 Markdown 链接、路径写法、代码片段或措辞被改写，但不属于入口页重构，也不以溯源退化为主。
4. **复盘报告派生改动**：位于 `retrospective/reports/` 下的派生产物，疑似来自导出、原子化或迁移后二次规范化，适合按报告目录成批复核。

## 结论总览

| 分类 | 数量 | 主要风险 | 后续建议 |
|---|---:|---|---|
| README / 入口级结构性改写 | 3 | 入口语义被重构，可能是应保留的迁移后新设计，也可能误覆盖原入口 | 交给 `SubTask 8.5` 单独复核，按“保留语义重构 / 回滚到基线”二分判断 |
| frontmatter 溯源退化 | 9 | `source` 与 `x-toml-ref` 可追溯性下降，后续会影响溯源校验与知识图谱 | 交给 `SubTask 8.4` 优先处理，优先恢复基线中的精确 `source` 与多源列表 |
| 正文链接或文案变更 | 6 | 链接被去链接化、路径文本被字面化、示例字符被改坏 | 在 `SubTask 8.6` 做最小修复，区分“必要路径纠正”和“误改正文” |
| 复盘报告派生改动 | 20 | 样本量最大，但高度集中在复盘报告目录，适合批量处理 | 按报告目录分批复核，优先处理 `source` 相对路径、`.agents/`/`docs/` 漂移与去链接化 |

## 第一类：README / 入口级结构性改写（3）

这类文件不是局部路径修复，而是入口职责、读者导向或目录边界被重新组织。它们与 `SubTask 8.5` 的复核对象直接对应。

| 文件 | 归类原因 | 备注 |
|---|---|---|
| `.agents/docs/README.md` | 根 README 从“项目文档”改写为“docs 文档边界说明”，属于整体入口重构 | 高优先级，需判断是否保留迁移后的统一入口设计 |
| `.agents/docs/standards/README.md` | 入口页中的权威规范链接由 `.agents/rules/` 语义切换为 `rules/` 相对路径体系 | 需确认是否只是路径修正，还是读者边界被改写 |
| `.agents/docs/reuse-and-generalization.md` | 虽不是 README，但承担入口级总览作用，正文中入口链接和系统说明被改写 | 建议与 README 一并视作“入口级结构改写”处理 |

**后续建议**

1. 在 `SubTask 8.5` 中逐个与基线对照，先判断“结构重写是否服务于迁移后统一入口设计”。
2. 若新增结构满足 `.agents/docs/README.md` 最小五章节与边界声明要求，则优先保留语义重构，仅回补误改链接。
3. 若重写导致原入口信息丢失，再从基线回补缺失内容，而不是整文件回滚。

## 第二类：frontmatter 溯源退化（9）

这类样本的共同特征是：`source` 从具体文件路径退化为 `README.md`、`external:` 摘要或合并后的描述字符串，或多源列表被压缩成单行摘要。它们对迁移完整性、溯源检查和后续自动化最敏感。

| 文件 | 归类原因 | 备注 |
|---|---|---|
| `.agents/docs/knowledge/best-practices/pdf-export-mermaid-automation-insights.md` | `source` 被改写为 `external: 不存在-...README.md`，原始来源不再可直接定位 | 伴随少量正文字符改动，但主风险仍是溯源退化 |
| `.agents/docs/retrospective/patterns/code-patterns/command-injection-prevention.md` | `source` 从具体源文件退化为 `README.md` | 明确应恢复 |
| `.agents/docs/retrospective/patterns/code-patterns/defensive-config-cache-deepcopy.md` | `source` 从具体源文件退化为 `README.md` | 明确应恢复 |
| `.agents/docs/retrospective/patterns/code-patterns/dynamic-path-derivation.md` | `source` 退化为 `README.md` | 另含 Windows 路径示例被改写 |
| `.agents/docs/retrospective/patterns/code-patterns/exception-precision-guards.md` | `source` 退化为 `README.md` | 明确应恢复 |
| `.agents/docs/retrospective/patterns/code-patterns/idempotent-shell-config.md` | `source` 退化为 `README.md` | 另含 `printf '%s\n'` 示例字符疑似被误改 |
| `.agents/docs/retrospective/patterns/code-patterns/ring-buffer-streaming-output.md` | `source` 退化为 `README.md` | 明确应恢复 |
| `.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/defensive-programming-first-principles.md` | `source` 被抽象成 `external:` 摘要文本，不再指向可验证源头 | 需人工确认是否确实不存在原文件 |
| `.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/depth-reference-table.md` | 多源 `source` 列表被压缩为摘要字符串 | 应优先恢复多源列表而非继续摘要化 |

**后续建议**

1. 在 `SubTask 8.4` 中优先复核这 9 个文件，直接以基线 frontmatter 为恢复锚点。
2. 恢复顺序建议为：先恢复 `source`，再校验 `x-toml-ref`，最后处理附带的正文误改。
3. 对确实找不到原始源文件的样本，单独标记为“待人工判断”，不要继续用 `README.md` 或摘要字符串占位。

## 第三类：正文链接或文案变更（6）

这类样本主要表现为正文中的链接被改成纯文本、路径被异常标准化、示例命令字符被替换，或文案被顺手调整。它们大多不是目录结构问题，而是迁移过程中的“内容层误差”。

| 文件 | 归类原因 | 备注 |
|---|---|---|
| `.agents/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.md` | 多处正文链接从 `.agents/scripts/...` 改写到 `scripts/...` 相对路径体系 | 需确认是正确相对路径还是误去前缀 |
| `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md` | 正文中一处源码链接被改成纯文本目录说明 | 属于典型“去链接化” |
| `.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-loop-engineering-article-analysis.md` | 报告仅捕获到 frontmatter 异动，但未证明正文受损 | 低置信度样本，建议先做精确 diff 再决定是否修复 |
| `.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.md` | 多处外部源码链接被改成纯文本路径，Windows 路径分隔符被异常规范化 | 需恢复可点击引用 |
| `.agents/docs/knowledge/learning/first-principles/15-cross-domain-cases/freedom-illusion-ai-era.md` | 章节末尾的多条内部导航链接被改写或删减 | 可能影响学习路径完整性 |
| `.agents/docs/knowledge/operations/vendor-flexloop-integration-guide.md` | 表格内多个链接被改为纯文本或错误相对路径 | 兼有 `.agents/` 前缀漂移问题 |

**后续建议**

1. 在 `SubTask 8.6` 中对这 6 个文件执行最小修复，优先恢复 Markdown 链接可点击性。
2. 对 `harness-loop-engineering-article-analysis.md` 先做一次精确 diff；若只是 frontmatter 行重排，可从疑似样本中移除。
3. 对示例代码或命令中的字符误改，按“示例必须可复制”原则回到基线写法。

## 第四类：复盘报告派生改动（20）

这类样本全部位于 `.agents/docs/retrospective/reports/`，疑似来自导出、原子化、二次规范化或迁移后批量修订。它们虽然数量最多，但高度集中，适合按目录批处理而不是逐文件散修。

| 文件 | 归类原因 | 备注 |
|---|---|---|
| `.agents/docs/retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/execution-retrospective.md` | 复盘报告正文中链接写法与文案被轻微改写 | 低风险，适合批量复核 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/action-items.md` | 复盘派生产物中“受众分层”文案从 `.agents/docs` 漂移为 `docs` | 属于迁移语义漂移 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task2-core-points.md` | `source` 从同目录文件改成 `../article-content.md` | 更像派生产物相对路径规范化 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task3-argument-logic.md` | `source` 相对路径被改写 | 同上 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task4-key-concepts.md` | `source` 相对路径被改写 | 同上 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task5-quality-assessment.md` | `source` 相对路径被改写 | 同上 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-cursor-cloud-agents-analysis-20260713/execution/task6-industry-insights.md` | `source` 相对路径被改写 | 同上 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-karpathy-agent-fallacy-20260707/README.md` | 复盘 README 中 `.temp` 链接被改为纯路径文本 | 去链接化 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/export-suggestions.md` | 多个 spec 路径层级被改写 | 需核实是否正确加深一级 |
| `.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/README.md` | `docs/superpowers/specs/` 与 `.agents/docs/...` 语义发生漂移 | 需确认基线意图 |
| `.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/execution-retrospective.md` | 路径与行内代码格式被联动改写 | 低至中风险 |
| `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/execution-retrospective.md` | `.agents/docs/apps` 被改为 `docs/apps`，规则链接前缀发生漂移 | 语义级风险较高 |
| `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/insight-extraction.md` | 核心区路径从 `.agents/docs/apps` 漂移为 `docs/apps` | 语义级风险较高 |
| `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/README.md` | 统计口径行被改写 | 与同目录报告应一起看 |
| `.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-project-comprehensive-20260626/report.md` | `apps/.../.agents/docs/insights/` 漂移为 `apps/.../docs/insights/` | 语义级风险较高 |
| `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/execution-retrospective.md` | 多个 spec、vendor、仓库根路径层级被批量改写 | 建议整目录复核 |
| `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/export-suggestions.md` | 表格内多个链接被去链接化或改为新相对路径 | 建议整目录复核 |
| `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/insight-action-backlog.md` | 产出物链接多处被纯文本化 | 建议整目录复核 |
| `.agents/docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/README.md` | 同目录 README 中多条入口链接体系被改写 | 与上面三文件联动 |
| `.agents/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/01-phase1-facts.md` | 模块表中的多个源码链接被改成纯文本路径 | 典型派生产物去链接化 |

**后续建议**

1. 先按报告目录批处理，而不是 20 个文件逐个散修；建议优先顺序为：`full-lifecycle`、`vendor-flexloop-governance-adjustment`、`cursor-cloud-agents-analysis`、其余单文件目录。
2. 对 `cursor-cloud-agents-analysis` 这 5 个执行子文件，重点确认 `source: ../article-content.md` 是否其实是正确修复；若是正确的，应纳入 allowlist 而非回滚。
3. 对 `full-lifecycle`、`full-project-comprehensive`、`vendor-flexloop-governance-adjustment` 这些包含 `.agents/docs`/`docs` 语义漂移的样本，优先对照原任务语境决定保留哪一套术语。
4. 对同目录内重复出现的“链接变纯文本”模式，可批量恢复，避免逐条手改。

## 推荐执行顺序

1. `SubTask 8.4` 先处理第二类 `frontmatter 溯源退化`，因为这类问题最确定、也最影响自动化校验。
2. `SubTask 8.5` 再单独复核第一类 `README / 入口级结构性改写`，确认哪些属于迁移后应保留的语义重构。
3. `SubTask 8.6` 最后对第三类和第四类执行最小修复，优先收敛高确定性的去链接化和术语漂移问题。

## 分组统计核对

| 分类 | 数量 |
|---|---:|
| README / 入口级结构性改写 | 3 |
| frontmatter 溯源退化 | 9 |
| 正文链接或文案变更 | 6 |
| 复盘报告派生改动 | 20 |
| 合计 | 38 |
