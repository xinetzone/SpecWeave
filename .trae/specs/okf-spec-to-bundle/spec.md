# OKF 规范本体知识包（`bundles/okf-spec/`）- 产品需求文档（PRD）

## Overview
- **Summary**：在 `bundles/okf-spec/` 下构建一个符合 OKF v0.2 规范的开放知识包，将 [vendor/knowledge-catalog/okf/SPEC.md](../../../vendor/knowledge-catalog/okf/SPEC.md)（Open Knowledge Format v0.2 英文规范）**格式转换 + 中文翻译**为结构化、可机读、可溯源的 OKF bundle。SPEC.md 原本是英语定义 OKF 的规范文档，本任务"用 OKF 自身的格式来承载 OKF 规范"（dogfooding/自举），把 §1-§13 与附录 A 的规范性内容原子化为独立概念文档，每条概念携带 YAML frontmatter（`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`sources`），正文以中文忠实转译，关键规范断言以脚注 `[^okf-spec]` 溯源至唯一信源 SPEC.md。
- **Purpose**：使 OKF v0.2 规范成为一个"活的、可被 agent 与人类共同消费"的知识资产——既证明 OKF 格式的自洽性（用 OKF 描述 OKF），又为后续任何 bundle 的产出者提供一个规范的中文机读参考实现。区别于 `vendor/` 下的英文原始 SPEC（只读第三方），本 bundle 位于主权区，可维护、可演进、可被索引与交叉引用。
- **Target Users**：需要查阅/引用 OKF v0.2 规范的 AI 智能体、知识图谱消费者、构建 OKF bundle 的开发者与内容生产者。

## Goals
- 将 SPEC.md 的 13 个规范章节 + 附录 A 完整、忠实地转译为中文，并按 OKF v0.2 格式原子化为 ~19 个概念文档（16 个规范概念 + 3 个示例概念），无遗漏、无新增、无臆造。
- 每个概念 frontmatter 含 `type`（PascalCase 描述性命名）、`title`、`description`、`tags`、`generated`、`verified`、`status`、`sources`；根 `index.md` 声明 `okf_version: "0.2"`。
- 正文以中文为主，但**代码块、字段名、YAML/frontmatter 示例、保留文件名、type 取值等机器可读元素保留英文原文**；关键术语首次出现附英文原文（如 provenance 溯源、attested computation 可认证计算、freshness 新鲜度）。
- 运用七概念方法论（场景 4 知识沉淀 + 原子化）**R → A → I → V → C** 链路：R 忠实转译采集、A 按章节原子化拆分、I 提炼跨章节设计意图、V 对抗审查翻译忠实性与格式合规性。
- Bundle 通过 OKF v0.2 §11 一致性三项检查（frontmatter 可解析、`type` 非空、保留文件合规）。

## Non-Goals (Out of Scope)
- 不修改 `vendor/knowledge-catalog/`（third_party 只读子模块）；仅在主权区 `bundles/okf-spec/` 新建。
- 不新增或改写 OKF 规范本身的内容（不补充规范、不修正规范、不扩展规范）；只做"格式转换 + 忠实翻译"。
- 不实现 OKF 的工具链 / SDK / viewer / attestation runtime（§10 的运行时协议属 deferred，仅忠实记录其规范文本）。
- 不构建真正的 Attested Computation 代码（`references/` 下的 `attesters/*.py` 等实现不在范围内）；附录 A 的示例 SQL/dbt 代码作为**示例文本**保留，不执行。
- 不引入任何 Python/JS 依赖或构建步骤；纯 Markdown + YAML frontmatter。

## Background & Context
- **格式依据**：[vendor/knowledge-catalog/okf/SPEC.md](../../../vendor/knowledge-catalog/okf/SPEC.md) 是 OKF v0.2 的唯一权威定义。SPEC §3 明确 bundle 可作为 "larger repository 中的子目录" 存在，故主权区 `bundles/okf-spec/` 是合规位置。
- **位置与边界约束**：`vendor/knowledge-catalog/` 在 vendor 体系中登记为 third_party 只读子模块（见 [vendor/AGENTS.md](../../../vendor/AGENTS.md)），严禁写入。SPEC.md 本体亦不能复制进 vendor；bundle 通过 `references/okf-spec.md` 以相对路径 `../../../vendor/knowledge-catalog/okf/SPEC.md` 引用信源（OKF §6.2 允许相对路径）。
- **先例**：`bundles/laozi-lineage/` 已示范本仓库的 OKF bundle 范式（frontmatter 约定、`sources`+脚注溯源、`index.md`/`log.md` 结构、七概念质量门），本任务沿用同一套约定以保证仓库内 bundle 风格一致。
- **方法论依据**：七概念场景 4（知识沉淀）标准链路 R→I→E→V，叠加 A（原子化）拆分大文档。由于本任务的信源是**单一权威规范**（而非多案例），E（萃取新可复用模式）退化为"忠实承载既有规范"——不发明新模式，故链路裁剪为 **R → A → I → V → C**（F/E 不适用：无新抽象需推导、无新模式需沉淀）。
- **内容敏感度**：OKF 规范为公开开源内容（LICENSE 见 vendor 目录），属 AGENTS.md 步骤 2.3 的"公开内容（Public）"，走标准工作流，Spec 目录位于 `.trae/specs/`。
- **语言决策**：用户确认"翻译为中文"。转译原则：规范性语义（MUST/SHOULD/MAY）需准确对应中文"必须/应当/可以"；机器可读元素（字段名、代码、YAML、type 值、保留文件名 `index.md`/`log.md`）保留英文原文；术语翻译建立统一映射表以避免前后不一致。

## Functional Requirements
- **FR-1**：`bundles/okf-spec/` 根目录含 `index.md`（frontmatter 含 `okf_version: "0.2"`）与 `log.md`，按 `concepts/`、`examples/`、`references/` 三个子目录组织。
- **FR-2**：`concepts/` 下至少 15 个规范概念，忠实对应 SPEC 章节：
  - `motivation.md`（§1 Motivation）
  - `terminology.md`（§2 Terminology）
  - `bundle-structure.md`（§3 Bundle structure + reserved filenames）
  - `concept-documents.md`（§4 Concept documents：frontmatter + body）
  - `provenance-sources.md`（§5.1 Provenance: `sources`）
  - `trust-generated-verified.md`（§5.2-5.3 Trust: `generated`/`verified` + trust tiers）
  - `lifecycle-status-stale.md`（§5.4-5.5 Lifecycle: `status`/`stale_after`）
  - `cross-linking-paths.md`（§6 Cross-linking and paths + `references/` 约定）
  - `actor-convention.md`（§7 Actor convention）
  - `index-files.md`（§8 Index files）
  - `log-files.md`（§9 Log files）
  - `attested-computations.md`（§10 Attested Computations，10.1-10.6）
  - `conformance.md`（§11 Conformance）
  - `versioning.md`（§12 Versioning）
  - `changes-from-v0.1.md`（§13 Changes from v0.1）
- **FR-3**：`examples/` 下至少 3 个示例概念：`concept-resource-bound.md`（§4.3）、`concept-unbound.md`（§4.4）、`income-statement.md`（附录 A 的 v0.1→v0.2 迁移示例）。示例中的 YAML/frontmatter/SQL/dbt 代码块保留英文原文，仅叙述性 prose 译为中文。
- **FR-4**：`references/` 下含 `okf-spec.md` 信源概念：`type: Reference`，`resource` 指向 `../../../vendor/knowledge-catalog/okf/SPEC.md`，记录版本 v0.2、作者/来源、许可（如可查），简述该规范的内容范围与适用边界。
- **FR-5**：每个概念文档 frontmatter 含 `type`（必填，PascalCase，如 `Rationale`/`Glossary`/`Specification`/`Changelog`/`Example`/`Reference`）、`title`、`description`、`tags`、`generated: { by, at }`、`verified`、`status`、`sources`（含 `id: okf-spec`）。
- **FR-6**：所有概念正文的规范性断言（"→ must/should/may"对应的转译）以脚注 `[^okf-spec]` 标注，脚注 label 与 `sources[].id` = `okf-spec` 对应；正文不得出现原文没有的规范内容或臆造字段/约束。
- **FR-7**：关键英文术语首次出现附英文原文，并保持全文一致（如 bundle=知识包、concept=概念、provenance=溯源、trust=信任、lifecycle=生命周期、attested computation=可认证计算、frontmatter=前置元数据、source=信源、re­ceipt=回执等）。
- **FR-8**：概念间通过 bundle-relative 路径（`/concepts/xxx.md` 或 `../concepts/xxx.md`）交叉链接（如 §5 各概念互链、`attested-computations.md` 链到 `trust-generated-verified.md`、示例链到对应规范概念）。
- **FR-9**：`log.md` 按 ISO 8601 日期倒序，含 Creation 与各阶段 Update 条目。
- **FR-10**：V 对抗审查显式记录——对翻译忠实性（抽查关键规范性语句中英对照）、术语一致性、OKF §11 合规性、无臆造内容进行审查，产出审查结论并在需要时修正。

## Non-Functional Requirements
- **NFR-1（可机读）**：所有 frontmatter 为合法 YAML，可被任意 YAML 解析器读取；`type` 非空且采用 PascalCase。
- **NFR-2（翻译忠实）**：规范性动词 MUST/SHOULD/MAY 分别对应"必须/应当/可以"，无歧义；不歪曲、不增删规范语义；代码/YAML/字段名零翻译。
- **NFR-3（术语一致）**：建立并遵守统一术语映射，同一英文术语全文使用同一中文译名。
- **NFR-4（一致性）**：通过 OKF §11 三项检查（frontmatter 可解析、`type` 非空、保留文件 `index.md`/`log.md` 结构合规）。
- **NFR-5（原子性）**：每个概念文件单一职责（对应单一 SPEC 章节/子章节），不混合多个主题；文件体积适中。
- **NFR-6（无外部依赖）**：bundle 可被 `cat`/`git clone` 直接消费，无需 SDK 或构建步骤（对 vendor SPEC.md 的引用为同仓库相对路径）。
- **NFR-7（可维护）**：`stale_after` 统一设为 `2027-12-31`（约一年半后复核，若 SPEC 升级触发重译）；`status` 默认 `stable`，`verified.by` 采用 `process:seven-concepts-V`。

## Constraints
- **Technical**：纯 UTF-8 Markdown + YAML frontmatter；POSIX 相对路径；代码块/YAML 示例保留英文；不引入 HTML/JS。
- **Vendor 边界**：严禁写入 `vendor/knowledge-catalog/` 任何文件（SPEC.md 只读引用）。
- **Dependencies**：格式依赖 `vendor/knowledge-catalog/okf/SPEC.md`；方法论依赖 `.agents/commands/seven-concepts.md` 场景 4 + `atomization-cmd`。
- **Location**：`bundles/okf-spec/`（用户确认目录名）。

## Assumptions
- "转成 OKF" 的语义是"格式转换 + 忠实翻译"，而非对规范本身的增删改（Non-Goals 已界定）。
- 我（agent）作为 `generated.by`（actor 约定形如 `reference_agent/trae-glm`），翻译与原子化由 agent 完成，V 阶段由 agent 以 `process:seven-concepts-V` 身份自检，最终 `human:<user>` 审阅后升级为 human-reviewed。
- SPEC.md 全文（§1-§13 + 附录 A）均需覆盖，无选择性省略；附录 A 的 v0.1 旧格式示例作为"历史形态"保留，标注其已被 v0.2 取代。
- 术语映射表在实现阶段一次性建立并跨文件复用，避免同一术语多种译名。

## Acceptance Criteria

### AC-1: Bundle 结构合规
- **Given**：`bundles/okf-spec/` 已创建
- **When**：检查目录结构
- **Then**：根目录含 `index.md`、`log.md` 与 `concepts/`、`examples/`、`references/` 三个子目录，每个子目录含 `index.md`
- **Verification**: `programmatic`

### AC-2: OKF v0.2 一致性通过
- **Given**：bundle 下所有非保留 `.md` 文件
- **When**：逐个解析 YAML frontmatter
- **Then**：每个文件含可解析 frontmatter、非空 `type` 字段；根 `index.md` 含 `okf_version: "0.2"`；子目录 `index.md` 与 `log.md` 无 frontmatter（或无违规字段）；无文件违反保留文件名
- **Verification**: `programmatic`

### AC-3: 规范章节覆盖完整
- **Given**：`concepts/` 目录
- **When**：对照 SPEC.md §1-§13
- **Then**：§1-§13 每个章节均有对应概念文档，无遗漏；`examples/` 覆盖 §4.3、§4.4 与附录 A
- **Verification**: `programmatic` + `human-judgment`

### AC-4: 翻译忠实且术语一致
- **Given**：任意概念的正文与对应 SPEC.md 原文
- **When**：抽查 ≥10 处关键规范性语句中英对照
- **Then**：语义等值（MUST→必须、SHOULD→应当、MAY→可以），无增删改规范语义；同一术语全文译名一致；代码/YAML/字段名零翻译
- **Verification**: `human-judgment`

### AC-5: 溯源性
- **Given**：任意概念正文
- **When**：扫描规范性断言与脚注
- **Then**：关键断言带 `[^okf-spec]` 脚注，`sources[].id = okf-spec` 且 `resource` 指向 vendor SPEC.md；无空 `resource`、无伪造引用
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 七概念质量门
- **Given**：R/A/I/V 各阶段产出
- **When**：按对应质量门检查
- **Then**：G1（R 转译忠实、无臆造、无因果词混入规范陈述）通过；原子化符合 A 单一职责；V 对抗审查有实质结论（翻译/合规/无臆造三项核查）并完成修正
- **Verification**: `human-judgment`

### AC-7: 无臆造内容
- **Given**：所有概念正文
- **When**：通读核对原文
- **Then**：正文不出现 SPEC.md 之外的规范性断言、字段名、约束或版本号；无"编者按"伪装成规范条款（如有补充说明须显式标注）
- **Verification**: `human-judgment`

### AC-8: 交叉链接连通
- **Given**：bundle 概念图
- **When**：遍历链接
- **Then**：规范概念间、示例↔规范、信源↔引用者存在有意义的交叉链接；≥80% 概念有出链或入链，不形成孤立文件
- **Verification**: `programmatic` + `human-judgment`

### AC-9: 信任与生命周期元数据完整
- **Given**：每个概念 frontmatter
- **When**：检查 `generated`/`verified`/`status`
- **Then**：`generated.by` 非空且符合 actor 约定；`verified` 至少一条；`status` 为 `draft`/`stable`/`deprecated` 之一；`stale_after` 统一可复核
- **Verification**: `programmatic`

### AC-10: log.md 与 vendor 边界
- **Given**：`log.md` 与 vendor 目录
- **When**：检查格式与 git 状态
- **Then**：`log.md` 日期倒序、含 Creation 条目；`vendor/knowledge-catalog/` 无任何新增/修改文件
- **Verification**: `programmatic`

## Open Questions
- [ ] `type` 取值是否需在 `references/` 或根 `index.md` 中登记一份"本 bundle 使用的 type 清单"（便于消费者路由）？当前方案暂不额外登记，依赖 PascalCase 自解释。
- [ ] 是否需要本 bundle 自带 `viz.html`（OKF viewer 可视化）？当前 Non-Goal；若用户希望可视化规范结构可追加。
- [ ] SPEC.md 若未来升级到 v0.3，本 bundle 的升级策略（重译 + `changes-from-vX.md` 追加）是否需在 `log.md` 中预留约定？当前仅设 `stale_after` 触发复核。