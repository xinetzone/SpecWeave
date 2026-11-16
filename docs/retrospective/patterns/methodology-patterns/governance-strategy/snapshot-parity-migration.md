---
type: Pattern
id: "snapshot-parity-migration"
source: "../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/delivery/2026-09-16-delivery-summary.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/snapshot-parity-migration.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "format-evidence-over-memory-pattern"
  - "large-scale-duplication-elimination"
  - "no-touch-list"
  - "batched-creation-independent-review"
  - "vendor-lifecycle-governance"
tags:
  - parity
  - snapshot
  - migration
  - characterization-testing
---
# 快照对拍迁移法

## 模式类型

方法论模式 → 治理策略（对等性证明与迁移门禁）

## 成熟度

L1（单案例：xuan-compose 对 podman-compose v1.6.0 的翻译式搬迁，2026-09-16）。
同一案例内存在三种独立应用形态——argparse parser 树 JSON 快照、AST 符号盘点、
上游测试集对拍（484 例 ≥ 上游 478 例），但按多案例原则，跨项目验证缺失前标 L1。
配套执行技能 [vendor-snapshot-parity](../../../../../.agents/skills/vendor-snapshot-parity/SKILL.md) 已存在。

## 一句话

把"与上游逐字段对等"从人肉断言变成机器日常对拍：快照的**生成**（接触上游）与
**消费**（日常测试，不接触上游）严格解耦。

## 适用场景

**适用于：**

- 将第三方/fork 单体的 CLI 参数表、配置 schema、序列化结构迁入自有分层包，
  要求与 pinned 基线逐字段对等；
- CI 需要长期守护对等性，但环境不保证检出上游源码；
- 升级基线时，要求一次脚本得到字段级差异而非重新人肉通读。

**不适用于：**

- 纯行为重写（不追求对等）；
- 仅少量函数或符号迁移、输入输出可直接比较——直接移植上游测试即可，四件套属过度工程；
- 对等对象含大量运行时行为（回调、惰性状态、并发时序），无法确定地序列化为纯数据——
  需改用行为级特征测试（characterization tests），快照只能覆盖可序列化部分。

## 问题背景

对等性主张有两种典型失效方式：一是依赖人肉通读，结论随人走、无法日常复跑；
二是让测试直接 import 上游，CI 被上游检出状态与版本漂移绑架。
快照对拍以"一次性生成、长期消费"的入库 JSON 同时规避两者。

## 核心做法（6 步）

1. **冻结基线**：pinned commit 写入快照 `meta` 与署名；确认上游工作树洁净
   （CRLF 翻转可用 `git diff --ignore-cr-at-eol` 判定为零语义差异）。
2. **先写 vendor 无关序列化器**：即不引用上游、只依赖待测对象公开结构的纯数据转换器。
   逐字段显式枚举行为相关维度，禁用 `vars()`/`__dict__` 全量倾倒；不可 JSON 化的值
   显式归一化；豁免字段（如 argparse 的 `prog`）以白名单声明并注明依据。
3. **写一次性生成脚本，严格复刻上游真实装配顺序**（不是"等价重写"构造逻辑），
   产出含 `meta` 的快照；入库前以第二证据核对（命令数、注册顺序直接对照上游），
   防止快照被一致地生成错。
4. **写对拍测试**：新库提供无副作用纯函数构造器，两侧共用同一序列化器，
   逐节点深度对比；失败时输出"节点→字段→上游值 vs 当前值"的字段级差异。
5. **固化消费纪律**：日常门禁只跑对拍测试，不 import、不路径依赖上游；
   用 subtest 参数化使每个节点都有独立证据。
6. **设重生成纪律**（写进生成脚本 docstring）：快照仅在主动升级基线时由维护者
   重生成并人工研判，禁止为让测试变绿刷新快照；红测试处置顺序为"回代码核对是漂移
   还是有意变更 → 有意变更先登记差异并更新验收标准 → 再谈基线"。

## 反模式（均来自实际教训）

- ❌ **每个对拍测试都 import 上游**：检出状态与版本漂移即红，快照价值全部丧失。
- ❌ **为变绿把关键维度（default/nargs/required/choices）排除在序列化器外**：
  "零差异"不可信；豁免必须显式、有验收依据。
- ❌ **生成脚本"等价重写"上游构造**：挂载/注册顺序差异不会暴露，快照会一致地错。
- ❌ **`vars()` 全量倾倒**：混入易变字段与内部状态，噪音淹没差异，也无法字段级豁免。
- ❌ **快照无 meta 溯源**：基线锚点丢失，对等声明失效。
- ❌ **测试失败先改快照**：快照是被对拍的基准，不是可随手更新的产物。
- ❌ **把快照固化的上游怪癖当成设计契约**：怪癖须同时在怪癖台账中显式标注
  （参见 [no-touch-list](no-touch-list.md) 的边界管理），避免后续误读。

## 失败案例

该文反模式章节自述「均来自实际教训」，其中两类是可直接复述的失败：

| 失败形态 | 表现 | 失败根因 | 后果 |
|---|---|---|---|
| 对拍失败先改快照 | 测试红→更新基准→测试绿 | 把快照当可随手更新的产物，而不是被对拍的基准 | 真实偏差被"洗"成通过，门禁失效 |
| 去重与对等核对留到最后 | 过程中重复翻译、同名实现贯穿多个 Task | 门禁只设在收尾 | 返工面最大，且缺陷无法归属到单一切片 |

**共同失败根因**：把"基准"与"产物"混为一谈，或把门禁后置——两者都会让失败在最贵的位置才暴露。

## 反目标用户/场景

| 反目标对象 | 为何不适用 | 应改用 |
|---|---|---|
| 一次性数据搬迁、无长期对拍需求 | 构建对拍基线的成本高于收益 | 抽样人工核对 |
| 上游快照本身不稳定（频繁合法变更） | 噪声会淹没真实偏差 | 先稳定上游或改用语义断言 |
| 无法冻结基准的环境 | 对拍失去参照物 | 记录基准版本号并显式声明漂移 |
| 小规模、可逐项人工核验的迁移 | 工程化成本倒挂 | 人工清单逐项签收 |

## 检验标准

- 四件套齐备（vendor 无关序列化器 / 一次性生成脚本 / 含 `meta` 的 JSON 快照 / 对拍测试），
  序列化器被两侧共用；
- 对拍测试在**不检出上游**的环境独立通过；
- 快照 `meta` 中 commit 与冻结基线一致，节点数、注册顺序已用第二证据核对；
- 对拍失败可输出字段级差异；
- 豁免字段全部显式列入文档并有验收依据。

## 迁移示例

- **ETL/数据仓库迁移（同域跨技术）**：旧库表结构与新 schema 以同一份结构序列化器
  生成快照对拍，字段、类型、约束逐节点比较；日常调度只跑消费侧。
- **制度/法规条文改版（非软件领域）**：冻结旧版条款编号，逐条款映射对拍，
  豁免条款（如已废止条目）白名单登记；新版发布前的"对等性"以对拍记录为据。
- **待验证方向**：会计科目表迁移、教材改版习题映射。

## 失效条件与演进

- 上游构造模型发生剧变时，快照维度需重新设计，旧快照仅作历史档案；
- 快照对拍是过渡形态：当对等关系长期稳定后，可演进为契约测试或属性测试，
  降低快照维护负担；
- 出现跨项目验证案例后可升 L2。

## 参考实现与关联

- 源案例：[交付总结](../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/delivery/2026-09-16-delivery-summary.md)、
  [六则模式](../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/patterns/2026-09-16-refactor-patterns.md)（xuanspace 子模块内）；
- 执行技能：[vendor-snapshot-parity](../../../../../.agents/skills/vendor-snapshot-parity/SKILL.md)；
- 上位原则：[format-evidence-over-memory-pattern](format-evidence-over-memory-pattern.md)（证据优先于记忆的一般原则）；
- 时序变体关系：[large-scale-duplication-elimination](../document-architecture/large-scale-duplication-elimination.md)
  管辖终态去重，本模式的片内盘点是其增量预防形态；
- 配套边界：[no-touch-list](no-touch-list.md)（不夹带修改的纪律）、
  [batched-creation-independent-review](../ai-collaboration/batched-creation-independent-review.md)（创作者不自审原则）、
  [vendor-lifecycle-governance](vendor-lifecycle-governance.md)。
