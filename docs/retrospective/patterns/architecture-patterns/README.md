---
id: "architecture-patterns-readme"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/README.toml"
---
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
| [metadata-layering.md](metadata-layering.md) | 元数据分层模式：核心标识内联+复杂索引元数据外部化，内容-元数据二分法判断字段归属 | L2 已验证 | 文档frontmatter管理、配置文件分层、API定义元数据设计 |
| [tuyaopen-layered-porting-model.md](tuyaopen-layered-porting-model.md) | TuyaOpen 分层移植模型（TKL/TAL/TDD/TDL）作为移植与阅读的主索引 | L1 实验性 | 嵌入式 SDK 阅读、平台移植、驱动分层定位 |
| [meta-capability-inversion.md](meta-capability-inversion.md) | 元能力依赖倒置：先实现原子能力再构建上层编排，避免框架先行导致的空中楼阁 | L2 已验证 | 自治理系统架构设计、AI Agent能力建设、平台型产品开发排期 |
| [three-layer-parser-generator.md](three-layer-parser-generator.md) | IDL/DSL工具三层+Profile架构：Parser→Validator→Generator分层+Profile横切变体 | L1 实验性 | 标记语言解析器、代码生成器、多类型文档处理工具 |
| [script-generator-pattern.md](script-generator-pattern.md) | 脚本生成器模式：Python 拼接 + Shell 执行的混合架构，各司其职，可调试性强 | L1 实验性 | 容器内多步构建、远程部署、CI/CD流水线 |
| [full-process-defense-depth.md](full-process-defense-depth.md) | 全流程纵深防御三层架构：事前预防+事中守护+事后追溯的"筛子模型" | L1 实验性 | 安全系统设计、AI Agent安全、企业应用、金融支付 |
| [scenario-based-security-matrix.md](scenario-based-security-matrix.md) | 场景化安全矩阵：按典型使用场景配置差异化安全特性组合，避免一刀切 | L1 实验性 | 安全架构设计、权限系统、AI Agent工具授权、SaaS/云服务安全 |
| [ipkvm-bypass-control.md](ipkvm-bypass-control.md) | IPKVM硬件旁路远控：HDMI采集+USB-HID仿真+独立网络链路+旁路部署，实现BIOS级无侵入远控 | L2 已验证 | 无网远控硬件、KVM over IP、物理隔离运维、BIOS级控制 |
| [multi-mode-network-redundancy.md](multi-mode-network-redundancy.md) | 多模网络冗余接入：有线/WiFi/4G/5G/蓝牙多模并存+优先级切换+断网续连+近场兜底 | L2 已验证 | 工业控制设备、医疗设备、高可靠远控、无人值守设备 |
| [usb-hid-emulation-plug-and-play.md](usb-hid-emulation-plug-and-play.md) | USB-HID仿真即插即用：枚举为标准USB键盘/鼠标，OS自带驱动免安装，BIOS级可用 | L2 已验证 | KVM/远控硬件、跨平台外设、即插即用型硬件、嵌入式控制 |
| [agent-physical-actuator-paradigm.md](agent-physical-actuator-paradigm.md) | Agent物理执行器范式：五大设计原则（原子接口/感知闭环/场景协同/消费级易用/多层安全），AI通过已有智能硬件作用于物理世界 | L2 已验证 | AIoT智能家居、远程运维、无人值守、Agent硬件化、MCP化设备控制 |
| [four-layer-ai-capability-architecture.md](four-layer-ai-capability-architecture.md) | AI开发者生态四层架构：MCP协议层→Skill封装层→CLI工具层→UI Locator视觉层，分层服务不同用户群体 | L1 实验性 | AI能力开放平台、MCP生态建设、SaaS平台AI化、远程控制AI能力设计 |
| [zero-update-client-design.md](zero-update-client-design.md) | 被控端零更新设计：新能力在控制端/服务端实现，被控端通过已有远控协议（画面+键鼠）复用能力，无需升级 | L1 实验性 | 远控软件AI升级、IoT平台新功能兼容存量设备、SaaS新API兼容旧客户端 |
| [normalized-coordinate-abstraction.md](normalized-coordinate-abstraction.md) | 归一化坐标抽象：使用[0.0,1.0]区间坐标替代绝对像素，从控制协议剥离分辨率变量，实现跨分辨率指令统一 | L2 已验证 | 远程桌面控制、UI自动化测试、RPA机器人、跨设备交互 |
| [multi-agent-closed-loop-execution.md](multi-agent-closed-loop-execution.md) | 多智能体闭环执行与自动重规划：观察-思考-行动循环+Convergence收敛点+失败自动replan，从失败点恢复而非从零开始 | L1 实验性 | UI自动化、机器人控制、API编排、RPA、任何不确定环境下的Agent任务执行 |
| [three-layer-capability-openness.md](three-layer-capability-openness.md) | 三层能力开放体系：GUI（终端用户）→CLI（开发者/脚本）→API/MCP（AI Agent）分层覆盖不同用户群，CLI是连接人类与机器的关键桥梁 | L1 实验性 | 平台型产品设计、开发者生态构建、AI Agent集成、SaaS能力开放 |

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
