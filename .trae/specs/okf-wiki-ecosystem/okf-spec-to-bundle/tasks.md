# OKF 规范本体知识包（`bundles/okf-spec/`）- 实现计划

> 方法论链路：七概念场景 4（知识沉淀）+ 原子化，裁剪为 **R → A → I → V → C**。
> 执行约定：每个任务委托单个子代理完成，一次只推进一个任务；任务完成后由独立验证子代理按 checklist.md 黑盒验证，通过后再标记 completed。

## [x] Task 1: Bundle 脚手架、术语映射表与信源登记
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 建立术语映射（中文译名 ↔ 英文原文，如 bundle=知识包、concept=概念、provenance=溯源、trust=信任、lifecycle=生命周期、attested computation=可认证计算、frontmatter=前置元数据、source=信源、receipt=回执），在实现中全文件复用。
  - 在 `bundles/okf-spec/` 创建目录结构：`concepts/`、`examples/`、`references/`。
  - 创建根 `index.md`（`---\nokf_version: "0.2"\n---` frontmatter，按三个子目录分组列出占位条目）。
  - 创建根 `log.md`（`## 2026-08-20` 下含 `**Creation**` 条目）。
  - 创建 `references/okf-spec.md`（`type: Reference`）：`resource: ../../../vendor/knowledge-catalog/okf/SPEC.md`，记录版本 v0.2、标题 "Open Knowledge Format (OKF)"、来源性质（vendored 第三方规范）、许可（如可查），简述该规范范围。
  - 创建三个子目录的 `index.md`（无 frontmatter，分组占位）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录树存在 3 个子目录且每个含 `index.md`；根 `index.md` frontmatter 含 `okf_version: "0.2"`。
  - `programmatic` TR-1.2: `references/okf-spec.md` frontmatter 可解析，`type: Reference`，`resource` 非空且路径指向 vendor SPEC.md。
  - `human-judgment` TR-1.3: 术语映射表覆盖 SPEC 高频繁术语，译名准确统一；抽查 3 条术语映射合理。

## [x] Task 2: R+A 阶段 — 规范基础概念（§1-§4，5 个）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `concepts/motivation.md`（`type: Rationale`，§1）：动机 + Goals + Non-goals，中文转译。
  - 创建 `concepts/terminology.md`（`type: Glossary`，§2）：12+ 术语表，术语/定义中文转译，术语本身附英文原词。
  - 创建 `concepts/bundle-structure.md`（`type: Specification`，§3）：bundle 目录树、分发方式、保留文件名 `index.md`/`log.md` 表格。
  - 创建 `concepts/concept-documents.md`（`type: Specification`，§4）：frontmatter（必填 `type`、推荐 `title`/`description`/`resource`/`tags`、扩展规则）+ body（`# Schema`/`# Examples`/`# Computation` 约定标题）。
  - 每个概念：G1 忠实转译（无臆造、规范断言脚注 `[^okf-spec]`）；`sources` 含 `id: okf-spec`；YAML/frontmatter 示例保留英文。
  - 交叉链接：`concept-documents.md` 链到 §5 相关概念（容忍暂未创建的断链）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 5 个文件存在，frontmatter 可解析，`type` 分别为 `Rationale`/`Glossary`/`Specification`，`sources` 含 `okf-spec`。
  - `human-judgment` TR-2.2: 抽查 §2 术语（bundle/concept/provenance/trust/lifecycle）中文译名与映射表一致；§3 保留文件名表格准确。
  - `human-judgment` TR-2.3: 无臆造字段/约束；代码块与 frontmatter 示例保留英文原文。

## [x] Task 3: R+A 阶段 — 溯源/信任/生命周期概念（§5，3 个）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `concepts/provenance-sources.md`（`type: Specification`，§5.1）：`sources` 字段、条目字段（`resource`/`id`/`title`）、可信度信号（`author`/`usage_count`/`last_modified`/`usage_window`）、逐断言脚注归因机制。
  - 创建 `concepts/trust-generated-verified.md`（`type: Specification`，§5.2-5.3）：`generated`/`verified` 字段、actor 约定、trust tiers（unverified/machine-confirmed/human-reviewed）。
  - 创建 `concepts/lifecycle-status-stale.md`（`type: Specification`，§5.4-5.5）：`status`（draft/stable/deprecated）、`stale_after` 绝对日期。
  - 三者互链（provenance ↔ trust ↔ lifecycle），并链到 `actor-convention.md`。
  - G1 忠实转译 + 脚注溯源；YAML 示例保留英文。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: 3 个文件存在，`type: Specification`，`sources` 含 `okf-spec`，存在三者间互链。
  - `human-judgment` TR-3.2: `verified` 裸映射=单元素列表、trust tiers 三级判定的转译准确；`stale_after` 的"绝对日期"语义正确。
  - `human-judgment` TR-3.3: 无臆造；`usage_count` 的"粗粒度信号"定位（alive vs dead，不作跨类精确排名）如实转译。

## [x] Task 4: R+A 阶段 — 路径/actor/索引/日志概念（§6-§9，4 个）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `concepts/cross-linking-paths.md`（`type: Specification`，§6）：链接两形式（bundle-relative `/x.md` vs 相对）、路径值字段、`references/` 约定。
  - 创建 `concepts/actor-convention.md`（`type: Specification`，§7）：`<producer>/<version>`、`human:<id>`、`process:<id>` 三形态及 trust 分类依据。
  - 创建 `concepts/index-files.md`（`type: Specification`，§8）：index.md 结构、无 frontmatter 例外（根可含 `okf_version`）、渐进披露。
  - 创建 `concepts/log-files.md`（`type: Specification`，§9）：log.md 日期倒序、扁平条目、标题居中约定。
  - 交叉链接：`actor-convention.md` 被 §5 概念引用；`index-files.md`/`log-files.md` 与 bundle-structure 互链。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-4.1: 4 个文件存在，`type: Specification`，`sources` 含 `okf-spec`。
  - `human-judgment` TR-4.2: §6 的 bundle-relative（`/` 开头）vs 相对路径区别转译准确；§8 的"index 无 frontmatter（根例外）"转译准确。
  - `human-judgment` TR-4.3: actor 三形态与 trust 分类（key off `human:` 前缀）转译准确，无歧义。

## [x] Task 5: R+A 阶段 — 可认证计算与合规性概念（§10-§11，2 个）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `concepts/attested-computations.md`（`type: Specification`，§10，10.1-10.6）：独立计算概念、契约字段（`runtime`/`parameters`/`computation`/`executor`/`attester`）、内联 vs 文件计算、消费者五步用法、verification vs attestation 区别。SQL/dbt 代码块保留英文。
  - 创建 `concepts/conformance.md`（`type: Specification`，§11）：合规三项、消费者软约束、不得拒绝的清单。
  - 交叉链接：`attested-computations.md` 链到 `trust-generated-verified.md`、`cross-linking-paths.md`；`conformance.md` 链到 `concept-documents.md` 等。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-5.1: 2 个文件存在，`type: Specification`，`sources` 含 `okf-spec`。
  - `human-judgment` TR-5.2: §10.6 verification vs attestation 的区别（doc-level 慢 vs per-run 运行时）转译准确；§10.3 "agent 只能填参、不得改写计算" 转译准确。
  - `human-judgment` TR-5.3: §11 的"不得拒绝"清单（缺可选字段/未知 type/断链/缺 index）完整转译。

## [x] Task 6: R+A 阶段 — 版本策略与变更记录（§12-§13，2 个）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `concepts/versioning.md`（`type: Specification`，§12）：`<major>.<minor>` 语义、`okf_version` 声明、considered and deferred 列表。
  - 创建 `concepts/changes-from-v0.1.md`（`type: Changelog`，§13）：两个 breaking change（`timestamp`→`generated.at`、`# Citations`→`sources`）+ 全部 additive changes，含向后兼容 fallback。
  - 交叉链接：`changes-from-v0.1.md` 链到 `trust-generated-verified.md`、`provenance-sources.md`。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 2 个文件存在，`type` 分别为 `Specification`/`Changelog`，`sources` 含 `okf-spec`。
  - `human-judgment` TR-6.2: §13.1 breaking change 与 §13.2 additive change 分类准确；`timestamp` 的 fallback 语义转译准确。
  - `human-judgment` TR-6.3: `versioning.md` 的 deferred 四条目（runtime protocol/attester ABI/attestation caching/semantic-layer templates）完整转译。

## [x] Task 7: R+A 阶段 — 示例概念（§4.3/§4.4/附录 A，3 个）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 `examples/concept-resource-bound.md`（`type: Example`，§4.3 BigQuery Table "Customer Orders" 示例）。
  - 创建 `examples/concept-unbound.md`（`type: Example`，§4.4 Playbook 示例）。
  - 创建 `examples/income-statement.md`（`type: Example`，附录 A）：v0.1 单文档形态 → v0.2 拆分形态的迁移，保留三个 v0.2 概念（`metrics/income-statement.md`、`computations/revenue.md`、`computations/profit.md`）的 frontmatter + 正文代码块；示例 YAML/SQL/dbt 保留英文，叙述性 prose 译为中文。
  - 各示例链回对应规范概念（§4、§5、§10）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-7.1: 3 个文件存在，`type: Example`，`sources` 含 `okf-spec`。
  - `human-judgment` TR-7.2: §4.3/§4.4 示例 frontmatter 与 code 保留英文；附录 A 的 v0.1（`timestamp`/`# Citations`）→ v0.2（`generated`/`sources`）迁移对照清晰。
  - `human-judgment` TR-7.3: 示例中的 YAML/frontmatter/SQL 零翻译。

## [x] Task 8: I+V 阶段 — 翻译忠实审查、交叉链接补全与最终一致性
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - I 阶段：提炼跨章节设计意图（如"provenance/trust/lifecycle 均可从 frontmatter 回答""领域无关的目录结构""单一 `type` 即合规的最小概念"），必要时在根 `index.md` 用一句话概述，不新增概念。
  - V 阶段对抗审查（3 项核查并修正）：① 翻译忠实性——抽查 ≥10 处关键规范性语句中英对照；② 术语一致性——全文同一术语同译名；③ 无臆造——正文无 SPEC 之外的规范断言/字段/版本号。
  - 回填交叉链接：§5 各概念、示例→规范、信源→引用者；确认关键链接不断。
  - 重新生成三个子目录 `index.md` 与根 `index.md` 最终清单（含 bundle 简介、OKF 版本、概念数量统计）。
  - 更新 `log.md`：追加各任务 Update 条目（日期倒序）。
  - 运行 OKF §11 一致性自查 + 脚注溯源自查（`[^okf-spec]` ↔ `sources[].id`）+ 链接自查。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: 扫描所有 `.md`，frontmatter 解析率 100%、`type` 非空率 100%、无文件违反保留文件名。
  - `programmatic` TR-8.2: 所有 `[^okf-spec]` 脚注在 `sources[].id` 中匹配（孤立脚注=0）；bundle 内关键相对链接目标存在。
  - `human-judgment` TR-8.3: 通读根/子目录 `index.md`，描述准确、分组合理、无遗漏；`log.md` 日期倒序且完整。
  - `human-judgment` TR-8.4: 最终概念总数 ≥ 18（15 规范 + 3 示例 + 1 信源），加 4 个 index + 1 log ≈ 24 文件。

## Task Dependencies
- Task 1 → Task 2（脚手架与信源先立）
- Task 2 → Task 3 → Task 4 → Task 5 → Task 6（规范概念按章节顺序，后依赖前）
- Task 2 → Task 7（示例依赖基础概念）
- Task 3+4+5+6+7 → Task 8（V 审查与收尾依赖全部概念）