---
id: "dual-track-progressive-evolution"
source: "../../../reports/project-reports/retrospective-xuanspace-comprehensive-20260826/insight-extraction.md#第二节模式文档"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-track-progressive-evolution.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "legacy-integration-dual-track"
  - "dual-track-sdk-strategy-framework"
  - "dual-mode-submodule-governance"
  - "four-negatives-external-dependency"
---

# 双轨演进制：依赖成熟度渐进切换模式

> 提炼自 [xuanspace 全面复盘洞察萃取](../../../reports/project-reports/retrospective-xuanspace-comprehensive-20260826/insight-extraction.md) 第二节（G3 PASS）

## 模式类型

- **领域**：方法论（methodology）
- **层级**：治理策略（governance-strategy）
- **成熟度**：L1 实验性（单案例验证，待二次案例确认升级 L2）

## 适用场景

- **场景**：monorepo 初始化与主链路打通阶段
- **适用条件**：
  1. 外部依赖存在可用性/稳定性风险（上游库未就绪、子模块未初始化、构建链不统一）
  2. 主链路关键路径依赖这些外部组件
  3. 内部已具备替代实现（或可快速搭建内聚实现）的能力
- **不适用**：已进入稳态迭代、外部依赖稳定可依赖的成熟仓库

## 问题背景

- 在依赖生态尚不成熟的阶段（上游库未发版、子模块未初始化、标准构建工具链未统一），外部依赖的可用性与稳定性存在风险。
- 若强行等待外部依赖就绪再推进主链路，会导致空窗期延长、开发节奏被打断。
- 若强行提前接入未就绪的外部依赖，则会阻塞主链路正常演进。

## 核心思想

采用"内部化实现先行、外部依赖后置"的双轨策略：先在本仓库内以自研/内聚方式打通主链路，待外部依赖（上游库、子模块、标准构建工具链）成熟后再切换轨道，两条轨道按依赖成熟度渐进切换。

```mermaid
flowchart LR
    A["盘点外部依赖成熟度<br/>标记高风险轨道"] --> B["仓库内部铺设<br/>内聚实现轨道"]
    B --> C["契约测试先行<br/>锁定轨道接口"]
    C --> D["渐进切换<br/>就绪一项切换一项"]
    D --> E["记录切换台账<br/>供后续审计"]
```

## 核心做法（5 步）

1. **盘点外部依赖成熟度**：标记高风险的依赖轨道（子模块、上游库、构建链）
2. **铺设内聚实现轨道**：对高风险依赖，先在仓库内部铺设内聚实现（如自研 COW 切片路径、内部构建后端统一）
3. **契约（测试）先行**：以端到端/边界测试锁定轨道接口，再推进机制实现
4. **渐进切换**：外部依赖就绪一项、切换一项，切换以全量测试通过为准入条件
5. **记录切换台账**：登记每项依赖的初始化/切换日期与验收依据，供后续审计

## 反模式（4 个）

1. **外部依赖先行**：依赖未就绪即强推接入，导致阻塞主链路（空窗期延长）
2. **双轨并行永不合轨**：内部实现完成后未及时切换，长期维护两套轨道
3. **切换无验收**：外部依赖就绪后未经测试即切换，引入行为漂移
4. **轨道未记录**：切换过程无台账，事后无法追溯"为什么 x 用了内部实现"

## 检验标准

- 主链路可在外部依赖缺失状态下持续演进（构建可运行、测试可通过）
- 每一轨道切换均有对应测试全量通过证据与台账记录
- 仓库骨架（构建后端、目录结构、多包管理）先行统一，再叠功能开发

## 跨场景迁移

- **前端 monorepo**：组件库 + 业务包的初始化阶段，若图标库/UI 基础库未发版，先在仓库内以内部组件兜底，依赖发版后按接口契约切换
- **微服务架构**：核心服务依赖的上游 SDK 未稳定时，先以内部桩/适配层打通链路，上游稳定后替换为正式 SDK，以契约测试保证切换安全

## 实际案例

- **xuanspace（L1 单案例）**：scikit-build-core 构建后端统一先行 → COW/Backward 机制采用内部实现 → 三子模块（libs/tvm-book、vendor/caffe、vendor/tvm-ffi）后置初始化，主链路在子模块缺失状态下仍持续演进（322 commits，测试覆盖率双基线达标）。

## 边界区分（与既有双轨类模式）

| 模式 | 关注点 |
|------|--------|
| **双轨演进制（本模式）** | 依赖成熟度渐进切换：内部化实现先行、外部依赖后置，按就绪度切换轨道 |
| [legacy-integration-dual-track](../../architecture-patterns/legacy-integration-dual-track.md) | 存量系统接入方式双轨：新旧两套接入路径并存 |
| [dual-track-sdk-strategy-framework](../../analysis-cards/dual-track-sdk-strategy-framework.md) | 平台 SDK 战略观察分析卡片：观察商业 SDK 与开源方案双轨 |

## 验证计划

- 详细验证计划见 [双轨演进制模式验证计划（L1→L2）](../../../reports/project-reports/retrospective-xuanspace-comprehensive-20260826/pattern-verification-plan-dual-track-progressive.md)：含 5 命题、5 场景、检验清单 C1-C10、升级 DoD 与失败降级路径。