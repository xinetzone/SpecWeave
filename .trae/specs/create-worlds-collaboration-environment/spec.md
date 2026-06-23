# worlds/ 协作与环境管理子目录 Spec

## Why

当前 `.agents/` 目录已建立角色、提示词、工具、协议、工作流、模板、脚本与团队管理模块，但缺少一个统一的「工作空间（World）」抽象层来承载**团队协作执行**与**多环境管理**两大场景。现有的 `teams/` 模块聚焦于团队组织结构与权限治理（谁在团队、有什么角色），而 `worlds/` 需要解决「团队在哪个工作空间协作、协作过程如何追踪、运行在何种环境之上」的运行时问题。建立 `worlds/` 子目录可补齐协作执行与环境治理的最后一公里，形成「组织（teams）→ 工作空间（worlds）→ 协议（protocols）→ 工作流（workflows）」的完整闭环。

## What Changes

- 在 `.agents/` 下新增 `worlds/` 子目录，作为团队协作执行与环境管理的规范容器
- 新增 `.agents/worlds/README.md`：目录说明、结构索引、使用流程与与其他模块的关系
- 新增 `worlds/collaboration/` 子目录：团队协作支持规范
  - `README.md`：协作模块索引
  - `permissions.md`：多用户权限管理（基于 RBAC 扩展，与 `.agents/teams/permission-system.md` 衔接）
  - `collaborative-editing.md`：协作编辑机制（锁机制、冲突解决、合并策略）
  - `change-tracking.md`：变更追踪（审计日志、操作留痕、可追溯链路）
  - `version-control.md`：版本控制集成（Git 工作流、分支策略、标签管理）
- 新增 `worlds/environments/` 子目录：环境管理规范
  - `README.md`：环境模块索引
  - `multi-environment.md`：多环境配置与切换（开发/测试/生产）
  - `variables.md`：环境变量管理（集中管理、加密存储、注入机制）
  - `resource-isolation.md`：资源隔离（命名空间、配额、网络隔离）
  - `status-monitoring.md`：环境状态监控（健康检查、指标采集、告警机制）
- 同步更新 `.agents/README.md`：在目录结构中新增 `worlds/` 条目与职责说明
- 同步更新 `AGENTS.md`：在上下文路由表中新增 `worlds/` 入口

## Impact

- Affected specs:
  - [create-agents-md-and-config](../create-agents-md-and-config/spec.md)（`.agents/` 目录结构扩展）
  - [add-team-collaboration-scenario-to-readme](../add-team-collaboration-scenario-to-readme/spec.md)（协作场景的运行时承载层）
- Affected code:
  - [.agents/README.md](../../../.agents/README.md)（新增 worlds/ 目录条目）
  - [AGENTS.md](../../../AGENTS.md)（上下文路由表新增条目）
- 与现有模块的关系：
  - `teams/`：组织治理层（谁在团队、有什么角色）→ `worlds/`：运行时协作层（团队在哪里协作、如何协作）
  - `protocols/`：`worlds/` 的协作机制遵循 `protocols/` 中定义的交接、消息传递、冲突解决协议
  - `workflows/`：`worlds/` 提供工作空间承载，`workflows/` 定义工作流程
  - `tools/`：`worlds/` 的环境管理依赖 `tools/` 中的文件操作与代码执行规范

## ADDED Requirements

### Requirement: worlds/ 目录结构

系统 SHALL 在 `.agents/` 下建立 `worlds/` 子目录，作为团队协作执行与环境管理的规范容器，包含 `collaboration/` 与 `environments/` 两个子模块，并提供 `README.md` 作为目录索引与使用指引。

#### Scenario: 目录结构完整性

- **WHEN** 智能体查看 `.agents/worlds/` 目录
- **THEN** 必须存在 `README.md`、`collaboration/`、`environments/` 三个条目
- **AND** `collaboration/` 下必须包含 `README.md`、`permissions.md`、`collaborative-editing.md`、`change-tracking.md`、`version-control.md`
- **AND** `environments/` 下必须包含 `README.md`、`multi-environment.md`、`variables.md`、`resource-isolation.md`、`status-monitoring.md`

#### Scenario: 目录索引同步

- **WHEN** `worlds/` 目录创建完成
- **THEN** `.agents/README.md` 的目录结构与职责说明表必须同步新增 `worlds/` 条目
- **AND** `AGENTS.md` 的上下文路由表必须新增 `worlds/` 入口

### Requirement: 团队协作支持

系统 SHALL 在 `.agents/worlds/collaboration/` 下定义团队协作支持规范，涵盖多用户权限管理、协作编辑、变更追踪与版本控制四个核心能力，确保多智能体在同一工作空间内可安全协作、可追溯变更、可版本回滚。

#### Scenario: 多用户权限管理

- **WHEN** 智能体申请加入某个 world 工作空间
- **THEN** 系统依据 `permissions.md` 中定义的 RBAC 模型校验用户角色与权限
- **AND** 权限校验遵循 `.agents/teams/permission-system.md` 的 L1/L2/L3 分级体系
- **AND** 权限分配与回收操作必须留痕，记录操作者、时间、目标用户、权限变更内容

#### Scenario: 协作编辑

- **WHEN** 多个智能体同时编辑同一资源（如配置文件、文档）
- **THEN** 系统依据 `collaborative-editing.md` 中定义的锁机制或乐观并发控制策略解决冲突
- **AND** 冲突解决遵循 `.agents/protocols/conflict-resolution.md` 的仲裁规则
- **AND** 编辑操作必须可回滚至任意历史版本

#### Scenario: 变更追踪

- **WHEN** 智能体在工作空间内执行任何写操作（创建、修改、删除）
- **THEN** 系统依据 `change-tracking.md` 记录审计日志，包含操作者、时间戳、操作类型、目标资源、变更前后内容
- **AND** 审计日志不可篡改，支持按时间、操作者、资源类型检索

#### Scenario: 版本控制

- **WHEN** 智能体提交变更
- **THEN** 系统依据 `version-control.md` 将变更纳入 Git 版本控制，支持分支、合并、标签
- **AND** 提交信息遵循 Conventional Commits 规范（`type(scope): subject`）
- **AND** 支持基于标签的环境快照（如 `env/dev-v1.0`、`env/prod-v2.3`）

### Requirement: 环境管理功能

系统 SHALL 在 `.agents/worlds/environments/` 下定义环境管理规范，支持开发环境、测试环境、生产环境的多环境配置与切换，包含环境变量管理、资源隔离与环境状态监控三个核心能力。

#### Scenario: 多环境配置与切换

- **WHEN** 智能体需要切换当前工作空间的目标环境（dev/test/prod）
- **THEN** 系统依据 `multi-environment.md` 加载对应环境的配置文件
- **AND** 环境切换必须经过权限校验，生产环境切换需 L3 特权验证
- **AND** 切换操作必须记录审计日志

#### Scenario: 环境变量管理

- **WHEN** 智能体需要读取或写入环境变量
- **THEN** 系统依据 `variables.md` 从集中式环境变量存储中加载或更新变量
- **AND** 敏感变量（如密钥、令牌）必须加密存储，解密需对应权限
- **AND** 环境变量注入遵循最小暴露原则，仅注入当前任务所需变量

#### Scenario: 资源隔离

- **WHEN** 多个环境并行运行
- **THEN** 系统依据 `resource-isolation.md` 通过命名空间、配额、网络隔离等机制确保环境间互不干扰
- **AND** 资源配额可配置，支持按环境分配 CPU、内存、存储等资源上限

#### Scenario: 环境状态监控

- **WHEN** 环境运行过程中
- **THEN** 系统依据 `status-monitoring.md` 持续采集环境健康指标（可用性、资源利用率、错误率）
- **AND** 指标异常时触发告警，告警渠道可配置（日志、消息、邮件）
- **AND** 监控数据保留周期可配置，支持历史趋势查询

### Requirement: 使用文档

系统 SHALL 在 `.agents/worlds/README.md` 中提供清晰的使用文档，说明目录功能、结构索引、使用流程、与其他模块的关系及使用约束。

#### Scenario: 文档完整性

- **WHEN** 智能体或人类读者查看 `.agents/worlds/README.md`
- **THEN** 文档必须包含：目录说明、目录结构图、各子模块职责矩阵、核心概念关系图（Mermaid）、使用流程示例、与其他模块的关系表、使用约束

## MODIFIED Requirements

### Requirement: .agents/ 目录结构

`.agents/` 目录结构在原有 8 个子目录（roles、modules、prompts、tools、protocols、workflows、templates、scripts、teams）基础上，新增 `worlds/` 子目录，作为团队协作执行与环境管理的规范容器。

### Requirement: AGENTS.md 上下文路由表

`AGENTS.md` 的上下文路由表新增一行：

| 任务类型 | 必读入口 |
|---|---|
| 团队协作执行、环境管理 | .agents/worlds/ |

## REMOVED Requirements

无移除项。
