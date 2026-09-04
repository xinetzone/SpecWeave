# docs/ 全量转换为 OKF v0.2 Wiki 教程 - 验证清单

## R 阶段验证

- [x] Checkpoint 1: facts.md 存在且覆盖 docs/ 下全部 280 个 .md 文件，文件计数与文件系统一致
- [x] Checkpoint 2: facts.md 中每个文件条目包含 path、has_frontmatter、frontmatter_fields、internal_links_count 四个字段
- [x] Checkpoint 3: facts.md 中无推断性表述（"用于"/"目的是"/"设计为"等关键词在事实描述中出现次数为 0）

## I 阶段验证

- [x] Checkpoint 4: bundle-mapping.md 存在且全部 280 个文件均有 Bundle 归属和 type 分配
- [x] Checkpoint 5: 31 个 Bundle 每个均有 index.md 和 log.md 生成计划
- [x] Checkpoint 6: spec.md 中 5 个 Open Questions（Q1-Q5）均有明确决策记录
- [x] Checkpoint 7: 链接转换映射表覆盖所有内部链接，无悬空映射

## E 阶段验证 — 试点批次（Task 3）

- [x] Checkpoint 8: 3 个试点 Bundle（python314-stdlib-wiki、deepseek-harness-wiki、github-cli-wiki）目录结构合规
- [x] Checkpoint 9: 每个 Bundle 根 index.md 包含 `okf_version: "0.2"` frontmatter
- [x] Checkpoint 10: 每个 Bundle 存在 concepts/ 子目录且包含无 frontmatter 的 index.md
- [x] Checkpoint 11: references/ 子目录存在（如有信源文件）且包含无 frontmatter 的 index.md
- [x] Checkpoint 12: log.md 存在且使用 ISO 8601 日期标题格式
- [x] Checkpoint 13: 所有 Concept 文件 frontmatter 包含 type/title/description/tags/generated/verified/status/stale_after 字段
- [x] Checkpoint 14: generated.by 为 `process:docs-to-okf-conversion`，verified.by 为 `process:seven-concepts-v`
- [x] Checkpoint 15: 所有内部链接以 `/` 开头（Bundle 绝对路径）且目标文件存在
- [x] Checkpoint 16: 正文内容与原始文件一致（仅 frontmatter 和链接路径变更）
- [x] Checkpoint 17: 现有 frontmatter 字段（id/date/category/tags/source/maturity）均被保留

## E 阶段验证 — 批次 2-4（Wiki Bundle，Task 4-6）

- [x] Checkpoint 18: 11 个 Wiki Bundle（agency-agents、cordis、okf-kit、open-code-review、agent-runtime-protocol、ai-engineering-milestones、baidu-ocr、book-to-skill、headroom、minit2i、python314-cpython）全部结构合规
- [x] Checkpoint 19: seven-concepts-report.md 等方法论文件已移入 references/ 且 type 为 Report
- [x] Checkpoint 20: HTML 文件（interactive-selection-matrix.html、python314-cheatsheet.html）保持原位未被移动
- [x] Checkpoint 21: 所有文件 frontmatter 完整、链接无断链、正文保真

## E 阶段验证 — 批次 5（分析报告，Task 7）

- [x] Checkpoint 22: 5 个微信文章分析 Bundle 结构合规
- [x] Checkpoint 23: article-content.md 位于 references/ 且 type 为 Reference
- [x] Checkpoint 24: analysis-report.md 位于 concepts/ 且 type 为 Report
- [x] Checkpoint 25: 所有文件 frontmatter 完整、链接无断链、正文保真

## E 阶段验证 — 批次 6（其他知识主题，Task 8）

- [x] Checkpoint 26: 5 个知识主题 Bundle 结构合规
- [x] Checkpoint 27: codewhale 的 concepts/ 下保留 general/domain、tech、topics 子目录结构
- [x] Checkpoint 28: atomic-emergence 的 HTML 文件保持原位
- [x] Checkpoint 29: 所有文件 frontmatter 完整、链接无断链、正文保真

## E 阶段验证 — 批次 7（项目文档，Task 9）

- [x] Checkpoint 30: 4 个项目文档 Bundle 结构合规
- [x] Checkpoint 31: tech/ 下原来无 frontmatter 的文件均已补全 OKF frontmatter
- [x] Checkpoint 32: four-layer-logging-pattern.md 的 type 为 Pattern
- [x] Checkpoint 33: 所有文件 frontmatter 完整、链接无断链、正文保真

## E 阶段验证 — 批次 8（复盘内容，Task 10）

- [x] Checkpoint 34: 3 个复盘内容 Bundle 结构合规
- [x] Checkpoint 35: methodology-patterns 中所有文件 type 为 Pattern
- [x] Checkpoint 36: retrospective-reports 的 concepts/ 下保留 adversarial-review/competitive-analysis/knowledge/milestone 子目录
- [x] Checkpoint 37: TOML frontmatter（`+++` 包裹）中的字段被保留为 YAML 扩展字段（实测无 TOML frontmatter 文件，0/16）
- [x] Checkpoint 38: 所有文件 frontmatter 完整、链接无断链、正文保真

## E 阶段验证 — 批次 9（根级导航，Task 11）

- [x] Checkpoint 39: docs/index.md 包含 `okf_version: "0.2"` frontmatter
- [x] Checkpoint 40: 根级导航文件中的内部链接指向正确的新路径
- [x] Checkpoint 41: knowledge/learning/ 下的散文件均有明确归属（anthropic/octo/three-ai-tools 已归入对应Bundle，okf-topic-index 保留为知识库索引），无悬空文件
- [x] Checkpoint 42: docs/README.md 与 index.md 导航内容同步

## V 阶段全量验证（Task 12-14）

- [x] Checkpoint 43: 全部 368 个 .md 文件通过 frontmatter 验证——246 个内容文件均有非空 type 字段，0 个缺失
- [x] Checkpoint 44: 所有子目录 index.md 无 frontmatter（仅根 index.md 可含 okf_version）
- [x] Checkpoint 45: 所有 Bundle 根 index.md 包含 okf_version: "0.2"
- [x] Checkpoint 46: 所有 log.md 使用 ISO 8601 日期标题（`## YYYY-MM-DD`）
- [x] Checkpoint 47: 所有 Bundle 内部链接（`/` 开头）目标文件存在，断链数为 0（3 个预存断链除外）
- [x] Checkpoint 48: 无遗漏的相对路径内部链接（index.md 中的同目录 `./` 导航链接为可接受格式）
- [x] Checkpoint 49: 图片链接目标文件存在，断链数为 0
- [x] Checkpoint 50: 正文 diff 中仅允许链接路径变更，无其他文字增删改（抽样验证通过）
- [x] Checkpoint 51: 原有 frontmatter 字段值 100% 保留
- [x] Checkpoint 52: 代码块和表格内容一致（1 个预存嵌套代码块问题除外）
- [x] Checkpoint 53: 抽样 10% 文件（25 个）人工复核正文内容完整性
- [x] Checkpoint 54: type 映射经人工审查合理（Tutorial/Concept/Reference/Pattern/Report/Example 与内容匹配）

## C 阶段验证（Task 15）

- [x] Checkpoint 55: 模式文档包含触发条件（8个）、核心步骤（R→I→E→V→C五阶段）、反模式（9个，≥5）
- [x] Checkpoint 56: 模式文档入库到 docs/retrospective/patterns/methodology-patterns/concepts/ 正确目录
- [x] Checkpoint 57: 模式文档包含迁移验证（5步独立完成路径）
- [x] Checkpoint 58: source-code-to-okf-wiki Skill 的 L2 模式文档已更新"非源码文档转换"场景（v1.1.0）

## 提交与追溯

- [ ] Checkpoint 59: 每个 Batch 对应一个原子提交，提交信息遵循 Conventional Commits（`feat(docs): ...`）
- [ ] Checkpoint 60: Git 提交历史可追溯，每个提交可独立回滚
- [x] Checkpoint 61: 验证报告（verification-report.md）已生成并存放在 supporting-analysis/ 目录
