# OKF 规范本体知识包（`bundles/okf-spec/`）- 验证清单

> 本清单由独立验证子代理在实现完成后逐项黑盒检查。每项必须给出"通过/失败"结论与证据（文件路径、命令输出或抽查引文）。任一项失败即视为整体未通过，需返工后重新验证。

## 一、OKF v0.2 格式合规性

- [x] **C1.1**：`bundles/okf-spec/` 根目录存在 `index.md` 与 `log.md`，且含 `concepts/`、`examples/`、`references/` 三个子目录。
- [x] **C1.2**：根 `index.md` frontmatter 含 `okf_version: "0.2"`。
- [x] **C1.3**：每个子目录含 `index.md`（子目录 index 无 frontmatter）。
- [x] **C1.4**：所有非保留 `.md` 文件（即非 index.md/log.md）均含以 `---` 分隔的 YAML frontmatter 块，且 YAML 可被解析无语法错误。
- [x] **C1.5**：每个非保留 `.md` 文件 frontmatter 含非空 `type` 字段；`type` 值为 PascalCase 描述性命名。
- [x] **C1.6**：`log.md` 按 `YYYY-MM-DD` 日期倒序排列，含 Creation 条目。
- [x] **C1.7**：无文件使用 `index.md`/`log.md` 之外的保留文件名。

## 二、规范章节覆盖度

- [x] **C2.1**：`concepts/` 下存在 §1-§13 对应的 15 个规范概念：motivation、terminology、bundle-structure、concept-documents、provenance-sources、trust-generated-verified、lifecycle-status-stale、cross-linking-paths、actor-convention、index-files、log-files、attested-computations、conformance、versioning、changes-from-v0.1。
- [x] **C2.2**：`examples/` 下存在 concept-resource-bound（§4.3）、concept-unbound（§4.4）、income-statement（附录 A）3 个示例概念。
- [x] **C2.3**：`references/` 下存在 `okf-spec.md` 信源概念（`type: Reference`），`resource` 指向 vendor SPEC.md。
- [x] **C2.4**：概念文件总数（不含 index/log）≥ 18。

## 三、翻译忠实性与术语一致性

- [x] **C3.1**：抽查 ≥10 处关键规范性语句中英对照，MUST→必须、SHOULD→应当、MAY→可以 语义等值，无增删改规范语义。
- [x] **C3.2**：同一英文术语全文译名一致（bundle/concept/provenance/trust/lifecycle/attested computation/frontmatter/source/receipt 等），无一词多译。
- [x] **C3.3**：代码块、YAML/frontmatter 示例、字段名、type 取值、保留文件名保留英文原文，零翻译。
- [x] **C3.4**：关键英文术语首次出现附英文原文。

## 四、溯源性

- [x] **C4.1**：抽查 ≥10 处规范性断言（跨至少 5 个概念），均带 `[^okf-spec]` 脚注，`sources[].id = okf-spec` 存在对应条目。
- [x] **C4.2**：`references/okf-spec.md` 的 `resource` 指向 `../../../vendor/knowledge-catalog/okf/SPEC.md`（正确相对路径，指向真实不出售文件）。
- [x] **C4.3**：无空 `resource`、无伪造引用；`sources` 中无"待核"残留于 `resource` 关键字段。

## 五、无臆造内容（V 对抗审查）

- [x] **C5.1**：正文不出现 SPEC.md 之外的规范断言、字段名、约束或版本号。
- [x] **C5.2**：无"编造"的 MUST/SHOULD/MAY 条款；转译严格对应原文。
- [x] **C5.3**：若有补充说明/编者注释，显式标注，不冒充规范条款。
- [x] **C5.4**：附录 A 的 v0.1 旧格式示例被标注为历史形态，与 v0.2 区分，不造成"v0.1 仍有效"的误导。

## 六、交叉链接与可遍历性

- [x] **C6.1**：规范概念间存在互链（如 §5 三概念互链、attested-computations ↔ trust/cross-linking、changes-from-v0.1 ↔ provenance/trust）。
- [x] **C6.2**：示例概念链回对应规范概念（§4/§5/§10）。
- [x] **C6.3**：≥80% 概念有出链或入链，不形成孤立文件。
- [x] **C6.4**：链接路径为 POSIX 相对或 bundle-relative（`/` 开头），无 Windows 反斜杠、无 `file:///` 绝对路径。

## 七、信任与生命周期元数据

- [x] **C7.1**：每个概念 frontmatter 含 `generated: { by, at }`，`by` 符合 actor 约定，`at` 为 ISO 8601 datetime。
- [x] **C7.2**：每个概念含 `verified`（至少一条）；`status` 为 `draft`/`stable`/`deprecated` 之一。
- [x] **C7.3**：`stale_after` 统一设为可复核日期（2027-12-31）。
- [x] **C7.4**：`tags` 为 YAML 列表，语义合理（如 `[okf, spec, provenance]`）。

## 八、Vendor 边界与项目约定

- [x] **C8.1**：`vendor/knowledge-catalog/` 无任何新增或修改文件（`git -C vendor/knowledge-catalog status` 干净）。
- [x] **C8.2**：所有文件 UTF-8 编码、无 BOM、换行符一致。
- [x] **C8.3**：bundle 内无硬编码 `file:///` 绝对路径；对外部 vendor SPEC 的引用为相对路径。

## 九、最终交付物可读性

- [x] **C9.1**：根 `index.md` 人类可读，含 bundle 简介、概念分组清单、OKF 版本声明、概念数量统计。
- [x] **C9.2**：每个概念正文使用结构化 Markdown（标题、表格、列表、代码块），无大段无结构散文。
- [x] **C9.3**：抽查任意 1 个规范概念（如 `provenance-sources.md`），从 frontmatter 到正文到脚注到 sources 全链路可独立阅读，不依赖英文原文即可理解。