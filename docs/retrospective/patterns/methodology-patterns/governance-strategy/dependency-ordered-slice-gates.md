---
type: Pattern
id: "dependency-ordered-slice-gates"
source: "../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/patterns/2026-09-16-refactor-patterns.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/dependency-ordered-slice-gates.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "snapshot-parity-migration"
  - "large-scale-duplication-elimination"
  - "behavior-characterization-freeze"
  - "orchestration-execution-layering"
  - "three-stage-content-validation"
tags:
  - refactoring
  - migration
  - dependency-order
  - slice
  - quality-gate
---
# 依赖序切片门禁法

## 模式类型

治理策略（执行类）。单体拆分时按依赖图确定切片顺序，并为每一片设独立门禁。

## 成熟度

L1（单案例：xuan-compose T1-T12 单文件拆包，2026-09-16）。
源案例含 12 片、每片独立门禁；跨项目验证缺失前标 L1。

## 一句话

单体拆包沿**目标架构依赖图的逆拓扑序**自底向上切片，每片执行
"冻结行号→翻译登记→移植上游测试→补真实分支测试→片内符号盘点"，片门禁不绿
不开下一片；原子提交按片/按职责拆批。

## 适用场景

**适用于：**

- 把第三方/自有单体翻译式搬迁为分层包，要求全程可证明对等；
- 源系统有可借用的测试基线，可逐层移植；
- 拆包工作量大、可能跨会话，需要每片都能独立定位缺陷、独立回退。

**不适用于：**

- 少量文件的增量修改——直接改即可；
- 全新功能开发，不存在"上游"与对等目标；
- 待拆单体无任何测试基线且行为不可快速取证——应先用
  [behavior-characterization-freeze](behavior-characterization-freeze.md) 补行为安全网，
  否则片门禁无内容；
- 切片间无清晰依赖关系（网状互调）——先做依赖解耦或接口抽取，再谈切片。

## 问题背景

单体拆包有两种典型失控：多层并进后统一测试，失败时缺陷归属跨层、定位成本最高；
把去重、对等核对只放在最后审计，过程中产生的重复翻译与偏离要到收尾才暴露。
依赖序切片以"顺序由依赖图决定、每片自带门禁"使每个失败都被锁在单一片内。

## 核心做法（8 步）

1. **先定目标分层与依赖图**：明确目标包的分层与层间单向依赖；切片顺序取依赖图的
   逆拓扑——被依赖的基础层先行（源案例顺序：基础→规范→执行→翻译→引擎→命令→
   CLI→门禁→审计→对抗审查，仅作示例）。
2. **开片冻结**：记录该片对应上游行号区间与基线 commit；声明本片职责边界。
3. **片内翻译**：按冻结行号逐段翻译，差异逐条登记；禁止顺手重写算法。
   遭遇与直觉冲突的行为，走 [behavior-characterization-freeze](behavior-characterization-freeze.md)。
4. **移植该片上游测试**：将该层对应的上游单测平移到本片，断言不削弱。
5. **补真实分支测试**：为上游测试未覆盖、但本片实际存在的逻辑分支补测。
6. **片内符号盘点（强制，每片执行）**：用 AST（无工具时以编号表格人工枚举）核对
   "上游符号→目标模块"映射；发现同名符号跨模块出现，立即停手去重，不进入下一步。
   本纪律对应源案例 D13：T4 已迁入 dependencies.py 的 check_dep_conditions，
   T7 按 handler 区域又逐字节重译一份，至 T11 盘点才暴露——单案例孤证，作为
   反模式提示而非统计结论。
7. **片门禁**：运行**片内范围**的测试（非全量集成），全绿才开下一片；红则留在
   本片修复。门禁证据与冻结行号、差异登记一并归档。
8. **原子交付**：提交按片、再按职责拆批（翻译/测试/文档分开）；跨会话中断后凭
   冻结记录与门禁状态恢复。

## 反模式

- ❌ **多层并进后统一测试**：失败跨层，定位需要同时持有多层上下文。
- ❌ **去重核对只放最后审计**：重复翻译、同名实现贯穿多个 Task，返工面最大。
- ❌ **每片跑全量测试**：单切片成本失控，流程必然被走样；也不允许只跑冒烟，
  证据强度不足以支撑开片。
- ❌ **片内顺手重写**：无法证明对等，偏离登记失去意义。
- ❌ **片门禁红绿未决就开下一片**：缺陷跨片传播后不再有低成本定位。
- ❌ **切片顺序按文件大小/熟悉度排**：依赖未就绪的层会临时制造桩与反向依赖。

## 检验标准

- 切片顺序可由目标分层依赖图机械推出，无循环依赖；
- 每片有冻结行号、差异登记、移植测试、补测、符号盘点五项记录；
- 片门禁在片内范围全绿；任一失败能被唯一归属到某片；
- 提交历史与切片边界可对应；
- 全流程结束时，对等结论可由各片门禁证据拼装复现。

## 迁移示例

- **组织/部门职能搬迁**：按业务流程的依赖序切（前置职能先搬），每职能片冻结原
  职责清单→平移原考核项→补新场景核对→盘点职责重名；一片不稳不动下一片。
- **数据库迁移**：按外键依赖序自底向上切表组，每组做结构与数据对拍、补触发器/
  视图测试、盘点同名对象；下游表组只在上游组门禁通过后开始。
- **待验证方向**：教材分册改版、微服务从单体的绞杀式抽取。

## 失效条件与演进

- 源单体行为面无法被测试基线覆盖时，片门禁空心化，需先补特征测试；
- 全部搬迁完成后，过程纪律使命结束，保留的是分层架构与各层回归门禁；
  去重职能交回终态审计（见 [large-scale-duplication-elimination](../document-architecture/large-scale-duplication-elimination.md)）；
- 出现跨项目验证案例后可升 L2。

## 参考实现与关联

- 源案例：[单体重构可复用模式六则](../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/patterns/2026-09-16-refactor-patterns.md)、
  [交付总结](../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/delivery/2026-09-16-delivery-summary.md)；
- 片内单维对拍工具：[snapshot-parity-migration](snapshot-parity-migration.md)；
- 怪癖行为处置：[behavior-characterization-freeze](behavior-characterization-freeze.md)；
- 委托执行分工（本模式决定"切什么、什么序"，分层法决定"谁来做"）：
  [orchestration-execution-layering](orchestration-execution-layering.md)；
- 验证时序的一般原则：[three-stage-content-validation](three-stage-content-validation.md)；
- 终态去重：[large-scale-duplication-elimination](../document-architecture/large-scale-duplication-elimination.md)。
