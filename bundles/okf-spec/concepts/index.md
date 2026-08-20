# 规范概念

* [OKF 规范动机](motivation.md) - OKF 的动机：人可读、可解析、可 diff、可移植，以及溯源、信任、新鲜度、生命周期、认证成为一级字段的理由。
* [OKF 术语表](terminology.md) - OKF v0.2 核心术语的中英对照与定义（知识包、概念、溯源、可信度信号、信任层级、可认证计算等）。
* [知识包结构](bundle-structure.md) - OKF v0.2 知识包的目录树结构、三种分发方式，以及保留文件名（index.md、log.md）。
* [概念文档](concept-documents.md) - OKF v0.2 概念文档结构：YAML frontmatter（必填 type，推荐 title/description/resource/tags）与正文约定标题。
* [溯源与信源（sources）](provenance-sources.md) - OKF v0.2 §5.1：`sources` 字段记录概念据以派生的信源，通过客观可信度信号（而非评分）推断信任。
* [信任：generated 与 verified 及信任层级](trust-generated-verified.md) - OKF v0.2 §5.2-§5.3：`generated` 记录内容如何产生，`verified` 记录核验事件，并由此派生三级信任层级。
* [生命周期：status 与 stale_after](lifecycle-status-stale.md) - OKF v0.2 §5.4-§5.5：`status` 标记概念状态（draft/stable/deprecated），`stale_after` 以绝对日期标记过期。
* [交叉链接与路径](cross-linking-paths.md) - 概念间的两种链接形式（bundle-relative 与相对路径）、路径值字段清单，以及 references/ 子目录约定。
* [参与者约定](actor-convention.md) - 记录身份字段所用的统一参与者约定：`<producer>/<version>`、`human:<id>`、`process:<id>` 三种形态及其信任分类用途。
* [索引文件](index-files.md) - `index.md` 的渐进披露用途、无 frontmatter 的默认约定（仅根 index.md 可含 okf_version），以及分组标题 + 条目列表格式。
* [日志文件](log-files.md) - `log.md` 的层级位置、日期分组扁平列表（最新在前）、`YYYY-MM-DD` 日期标题与前导粗体词约定。
* [可认证计算（Attested Computations）](attested-computations.md) - OKF v0.2 可认证计算概念：runtime/parameters/computation/executor/attester 契约字段、内联与文件两种计算方式、消费者的用法，以及 verification 与 attestation 之别。
* [合规性（Conformance）](conformance.md) - OKF v0.2 合规三要件，以及消费者对 trust/lifecycle/provenance/computation 字段族的处理要求与“不得拒绝”清单。
* [版本控制](versioning.md) - OKF v0.2 版本规则：<major>.<minor> 格式、次版本为向后兼容增量、主版本为破坏性变更，以及知识包声明目标版本方式与已推迟事项。
* [相对 v0.1 的变更](changes-from-v0.1.md) - OKF v0.2 相对 v0.1 的两处破坏性变更（timestamp 与 # Citations 的取代）与全部增量变更（新字段族、Attested Computation、# Computation、actor 约定）。