+++
description = "架构模式索引 - 可复用的架构级解决方案模式"
layer = "architecture"
+++

# 架构模式索引（architecture-patterns）

本目录存放架构级可复用模式，聚焦于文件依赖拓扑、级联更新策略、系统结构设计等中观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [cascade-update-topology.md](cascade-update-topology.md) | 多对多文件级联更新的拓扑排序，最小跳数优先原则 | L2 已验证 | 新建规范文件后的索引级联更新 |
| [cascade-update-prerequisite-check.md](cascade-update-prerequisite-check.md) | 级联更新拓扑的前提检查，目标目录索引文件存在性验证 | L1 实验性 | 模式入库前的目录状态检查 |
| [multi-agent-parallel-execution.md](multi-agent-parallel-execution.md) | 多智能体并行执行的任务拆分与冲突避免策略 | L2 已验证 | 复杂任务的多Agent协作执行 |
| [lifecycle-protocol-three-phase.md](lifecycle-protocol-three-phase.md) | 智能体生命周期协议三阶段：感知/决策/执行 | L2 已验证 | Agent角色定义与生命周期管理 |
| [incremental-regression-verification.md](incremental-regression-verification.md) | 增量式回归验证，每次变更后验证受影响范围 | L2 已验证 | 文档/代码修改后的质量保障 |
| [perception-check-report-model.md](perception-check-report-model.md) | 感知-检查-报告三层诊断模型 | L2 已验证 | 问题诊断与状态感知 |
| [five-layer-document-architecture.md](five-layer-document-architecture.md) | 文档五层架构：规格→决策→质量→交付→萃取，AI协作项目通用骨架 | L2 已验证 | AI协作项目的文档体系搭建 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解拓扑结构与规则
3. 按模式规则执行级联更新
4. 验证后更新模式成熟度（若适用）
