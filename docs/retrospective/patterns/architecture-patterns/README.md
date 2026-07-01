+++
description = "架构模式索引 - 可复用的架构级解决方案模式"
layer = "architecture"
+++

# 架构模式索引（architecture-patterns）

本目录存放架构级可复用模式，聚焦于文件依赖拓扑、级联更新策略、系统结构设计等中观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [dual-interface-repository.md](dual-interface-repository.md) | AI Skill 仓库的双界面架构：根目录面向人类，子目录面向 AI Agent | L2 已验证 | AI Skill/Plugin/Tool 项目的仓库结构设计 |
| [cascade-update-topology.md](cascade-update-topology.md) | 多对多文件级联更新的拓扑排序，最小跳数优先原则 | L2 已验证 | 新建规范文件后的索引级联更新 |
| [cascade-update-prerequisite-check.md](cascade-update-prerequisite-check.md) | 级联更新拓扑的前提检查，目标目录索引文件存在性验证 | L1 实验性 | 模式入库前的目录状态检查 |
| [multi-agent-parallel-execution.md](multi-agent-parallel-execution.md) | 多智能体并行执行的任务拆分与冲突避免策略 | L2 已验证 | 复杂任务的多Agent协作执行 |
| [lifecycle-protocol-three-phase.md](lifecycle-protocol-three-phase.md) | 智能体生命周期协议三阶段：感知/决策/执行 | L2 已验证 | Agent角色定义与生命周期管理 |
| [incremental-regression-verification.md](incremental-regression-verification.md) | 增量式回归验证，每次变更后验证受影响范围 | L2 已验证 | 文档/代码修改后的质量保障 |
| [perception-check-report-model.md](perception-check-report-model.md) | 感知-检查-报告三层诊断模型 | L2 已验证 | 问题诊断与状态感知 |
| [five-layer-document-architecture.md](five-layer-document-architecture.md) | 文档五层架构：规格→决策→质量→交付→萃取，AI协作项目通用骨架 | L2 已验证 | AI协作项目的文档体系搭建 |
| [iot-device-wrapper-pattern.md](iot-device-wrapper-pattern.md) | IoT 设备数据包装器模式，将 DP Code 抽象为类型安全的统一接口 | L1 实验性 | IoT 设备集成开发、多协议设备统一接口 |
| [iot-event-driven-state-update.md](iot-event-driven-state-update.md) | IoT 事件驱动状态更新，通过 MQTT + dispatcher 实现实时同步 | L1 实验性 | IoT 设备状态同步、大规模设备管理 |
| [iot-device-category-mapping.md](iot-device-category-mapping.md) | IoT 设备分类到平台映射，实现设备自动发现和实体创建 | L1 实验性 | IoT 平台设备发现、多设备类型支持 |
| [iot-quirks-extension-mechanism.md](iot-quirks-extension-mechanism.md) | IoT Quirks 扩展机制，无需修改核心代码的设备定制化支持 | L1 实验性 | 非标准设备适配、用户自定义设备处理 |
| [staged-startup-integration-loading.md](staged-startup-integration-loading.md) | 分阶段集成加载：stage 启动 + 并发装配 + 超时推进，优先确保基础能力可用 | L1 实验性 | 插件/集成数量多的系统冷启动治理 |
| [submodule-metadata-externalization.md](submodule-metadata-externalization.md) | Git Submodule元数据外置：元数据放在submodule目录外，避免dirty状态和版本冲突 | L1 实验性 | Git子模块管理、跨项目协作、vendor目录治理 |
| [tuyaopen-layered-porting-model.md](tuyaopen-layered-porting-model.md) | TuyaOpen 分层移植模型（TKL/TAL/TDD/TDL）作为移植与阅读的主索引 | L1 实验性 | 嵌入式 SDK 阅读、平台移植、驱动分层定位 |
| [meta-capability-inversion.md](meta-capability-inversion.md) | 元能力依赖倒置：先实现原子能力再构建上层编排，避免框架先行导致的空中楼阁 | L2 已验证 | 自治理系统架构设计、AI Agent能力建设、平台型产品开发排期 |

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
