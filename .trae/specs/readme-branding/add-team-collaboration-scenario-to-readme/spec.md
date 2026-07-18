# 角色自动组队协作场景 README 集成 Spec

## Why

当前 README.md 已描述 5 个核心角色的定义与系统规划，但缺少一个具体场景展示角色如何**自动发起组队请求并带领团队协作完成工作**，以及角色之间如何**相互 @ 直接发起协作请求**。添加此场景可让读者直观理解多智能体协作的运行模式，验证角色体系与协作协议的实际可用性，并体现去中心化的协作灵活性。

## What Changes

- 在 README.md 的「系统规划」与「文档导航」之间新增「角色协作场景」章节
- 详细描述由 `.agents/roles/` 目录下的角色自动发起组队请求的完整流程
- **支持两种协作发起模式**：
  - **中心化模式**：orchestrator 主导组队，带领团队协作
  - **去中心化模式**：任意角色可相互 @ 直接发起协作请求
- 包含六个要素：触发条件、团队成员选择机制、协作流程、任务分配方式、角色相互 @ 机制、预期工作成果
- 使用 Mermaid 流程图可视化两种协作模式
- 确保场景与 [.agents/roles/](../../../../.agents/roles/README.md) 角色定义和 [.agents/protocols/](../../../../.agents/protocols/README.md) 协作协议保持一致

## Impact

- Affected specs: 
  - [add-system-planning-to-readme](../add-system-planning-to-readme/spec.md)（章节相邻）
  - [optimize-readme-with-blueprint](../optimize-readme-with-blueprint/spec.md)（README 结构）
- Affected code: 
  - [README.md](../../../../README.md)（新增章节，约 100-140 行）
- 不修改 .agents/roles/ 下任何角色定义文件
- 不修改 .agents/protocols/ 下任何协议文件

## ADDED Requirements

### Requirement: 角色协作场景章节

系统 SHALL 在 README.md 中新增「角色协作场景」章节，位于「系统规划」与「文档导航」之间，描述由 `.agents/roles/` 目录下的角色自动发起组队请求并带领团队协作完成工作的具体场景，并支持角色之间相互 @ 直接发起协作请求。

#### Scenario: orchestrator 发起组队请求（中心化模式）

- **WHEN** orchestrator 接收到一个复杂任务（如"实现新功能模块"），且该任务超出单角色能力范围
- **THEN** orchestrator 依据角色职责矩阵自动识别所需角色（architect、developer、reviewer、tester），发起组队请求

#### Scenario: 角色相互 @ 发起协作（去中心化模式）

- **WHEN** 任意角色（如 developer）在执行任务过程中遇到超出自身职责边界的问题（如架构决策、代码审查、测试验证）
- **THEN** 该角色可直接 @ 对应角色（如 @architect、@reviewer、@tester）发起协作请求，无需经过 orchestrator 中转
- **AND** 被 @ 的角色依据自身 Responsibilities 判断是否接受协作请求

#### Scenario: 团队成员选择机制

- **WHEN** orchestrator 发起组队请求或角色相互 @ 发起协作
- **THEN** 系统依据任务类型与角色 `Responsibilities` 字段匹配所需角色，依据 `Non-Goals` 字段排除不相关角色，形成最小必要团队

#### Scenario: 协作流程执行

- **WHEN** 团队组建完成（中心化或去中心化模式）
- **THEN** 按照「任务分解→架构设计→代码实现→代码审查→测试验证→交付集成」流程协作，每个环节由对应角色主导
- **AND** 任意环节的角色可 @ 上下游角色进行实时协作与反馈

#### Scenario: 任务分配方式

- **WHEN** orchestrator 分配任务
- **THEN** 依据角色 frontmatter 的 `bindings.rules` 绑定的协作协议（handoff/messaging/conflict-resolution）进行任务交接与消息传递
- **AND** 角色相互 @ 时遵循 messaging 协议进行直接通信

#### Scenario: 预期工作成果

- **WHEN** 协作流程完成
- **THEN** 交付完整功能模块，包含架构方案、实现代码、审查报告、测试用例与技术文档

## MODIFIED Requirements

### Requirement: README 章节结构

README.md 章节顺序调整为：

1. 快速开始
2. 项目亮点
3. 项目蓝图
4. 系统规划
5. **角色协作场景**（新增）
6. 文档导航
7. 许可证
8. 联系方式
9. 折叠索引

## REMOVED Requirements

无移除项。
