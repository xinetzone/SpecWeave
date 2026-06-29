# Trae 边界情况处理团队模块 Spec

## Why

在论坛自动化全工作流中，AI 智能体在 Trae 生态下遇到了多种边界情况：IDE 集成浏览器的沙箱限制、PowerShell 编码陷阱、论坛登录状态过期、DOM 结构变化、agent-browser CLI 权限不足、外部工具链（Discourse API/MCP）可用性不确定等。这些边界情况分散在不同会话中处理，缺乏统一的判断标准、处理流程和适配策略，导致每次遇到边界情况都要重新探索，效率低且容易遗漏。

## What Changes

- 在 `.agents/teams/` 目录下新增 `trae-edge-case-handler.md` 规范文档，定义 Trae 边界情况处理的统一标准
- 更新 `.agents/teams/README.md` 索引，将新模块纳入目录结构和职责矩阵
- 新增四大边界场景的分类体系：Trae IDE 集成边界、Trae 论坛操作边界、Trae 外部工具链边界、Trae Work 边界
- 定义边界条件判断标准、异常处理流程、特殊场景适配策略
- 定义该模块与其他 `.agents/` 模块的接口规范

## Impact

- Affected specs: 无直接影响的已完成 spec（所有 36 个 spec 已完成）
- Affected code: 
  - `.agents/teams/trae-edge-case-handler.md`（新增）
  - `.agents/teams/README.md`（修改：索引更新）
  - `AGENTS.md`（修改：团队管理索引补充说明）

## ADDED Requirements

### Requirement: Trae 边界情况分类体系

系统 SHALL 提供覆盖 Trae 生态四大边界场景的分类体系，每个场景定义明确的边界条件判断标准。

#### Scenario: Trae IDE 集成边界识别

- **WHEN** 智能体在 Trae IDE 内使用 integrated_browser MCP 执行操作
- **THEN** 系统 SHALL 识别以下边界条件：沙箱文件系统限制、MCP 工具可用性波动、集成浏览器登录状态依赖、IDE 内终端会话隔离
- **AND** 为每个边界条件提供判断方法和处理策略

#### Scenario: Trae 论坛操作边界识别

- **WHEN** 智能体执行 forum.trae.cn 论坛自动化操作
- **THEN** 系统 SHALL 识别以下边界条件：登录状态过期、DOM 结构变化、频率限制触发、草稿残留堆积、帖子审核状态不确定、回复分页导航异常
- **AND** 为每个边界条件提供检测信号和恢复策略

#### Scenario: Trae 外部工具链边界识别

- **WHEN** 智能体使用 agent-browser CLI、Discourse REST API、@discourse/mcp 等外部工具链
- **THEN** 系统 SHALL 识别以下边界条件：工具安装失败、API Key 缺失、工具版本不兼容、跨平台编码差异（PowerShell vs bash）、网络可达性不确定
- **AND** 为每个边界条件提供替代方案和降级策略

#### Scenario: Trae Work 边界识别

- **WHEN** 智能体通过 Trae 生态进行工作协作（飞书消息、文档、任务等）
- **THEN** 系统 SHALL 识别以下边界条件：授权 Token 过期、API 限流、消息链接权限限制、飞书应用范围不足
- **AND** 为每个边界条件提供重新授权流程和降级方案

### Requirement: 边界条件判断标准

系统 SHALL 为每类边界情况提供结构化的判断标准，包含检测信号、判断阈值和确认方法。

#### Scenario: 多信号组合检测

- **WHEN** 智能体需要判断是否处于边界情况
- **THEN** 系统 SHALL 使用多信号组合检测模式（参考 multi-signal-detection.md），提供至少 2 个独立信号源
- **AND** 信号源按可靠性排序，反向信号辅助确认
- **AND** 在 DEBUG 模式下输出完整的判断诊断信息

#### Scenario: 边界条件分级

- **WHEN** 边界条件被识别后
- **THEN** 系统 SHALL 按严重程度分级：致命（阻断操作）、警告（降级操作）、提示（记录但继续）
- **AND** 每个级别定义对应的处理策略

### Requirement: 异常处理流程

系统 SHALL 定义标准化的异常处理流程，覆盖从检测到恢复的完整链路。

#### Scenario: 致命边界处理

- **WHEN** 检测到致命级边界条件（如沙箱限制阻断操作）
- **THEN** 系统 SHALL 执行以下流程：记录诊断日志 → 尝试替代方案 → 若无替代方案则优雅退出 → 通知用户并提供手动操作指引
- **AND** 退出码非零，日志包含完整的边界条件诊断信息

#### Scenario: 警告级边界处理

- **WHEN** 检测到警告级边界条件（如登录状态即将过期）
- **THEN** 系统 SHALL 执行以下流程：记录警告日志 → 执行降级操作（如重新登录） → 验证恢复结果 → 继续原操作
- **AND** 降级操作须遵循 dry-run-first 原则（参考 dry-run-first.md）

#### Scenario: 提示级边界处理

- **WHEN** 检测到提示级边界条件（如 DOM 结构轻微变化但选择器仍有效）
- **THEN** 系统 SHALL 记录提示日志，继续原操作，在操作完成后汇总报告边界情况

### Requirement: 特殊场景适配策略

系统 SHALL 为已知的特殊场景提供预定义的适配策略，避免每次遇到时重新探索。

#### Scenario: 沙箱限制适配

- **WHEN** 智能体在 Trae IDE 沙箱中无法访问用户目录或安装依赖
- **THEN** 系统 SHALL 按以下优先级适配：优先使用 Trae 集成浏览器（已登录无沙箱限制） → 其次使用 `dangerouslyDisableSandbox` 绕过（需用户确认） → 最后回退到手动操作指引

#### Scenario: PowerShell 编码适配

- **WHEN** 智能体在 Windows PowerShell 环境下执行命令遇到编码或引号问题
- **THEN** 系统 SHALL 按以下策略适配：多行文本使用 `-F` 文件参数而非 `-m` 内联参数 → 中文输出乱码不影响实际内容时忽略 → 编码冲突时显式设置 `chcp 65001`

#### Scenario: 论坛登录状态过期适配

- **WHEN** 智能体检测到论坛登录状态过期（Cookie 失效）
- **THEN** 系统 SHALL 按以下流程适配：检测多信号确认过期 → 提示用户重新执行 login 命令 → 重新登录后恢复操作 → 记录过期频率用于优化

#### Scenario: DOM 结构变化适配

- **WHEN** 智能体检测到论坛 DOM 结构变化导致选择器失效
- **THEN** 系统 SHALL 按以下策略适配：优先使用语义定位（文本/role/label） → 其次使用多选择器备选链 → 最后使用 JavaScript DOM 查询兜底 → 记录新 DOM 结构用于更新选择器常量

### Requirement: 模块接口规范

系统 SHALL 定义 trae-edge-case-handler 模块与其他 `.agents/` 模块的接口规范。

#### Scenario: 与团队管理模块的接口

- **WHEN** trae-edge-case-handler 模块需要与其他团队管理模块协作
- **THEN** 系统 SHALL 遵循以下接口规范：
  - 输入接口：接收 orchestrator 的边界情况报告
  - 输出接口：向调用方返回处理决策（继续/降级/退出）和诊断信息
  - 日志接口：所有边界判断结果写入结构化日志（参考 SG-LOG 格式）
  - 验证接口：边界处理操作须遵循 admin-verification.md 的验证分级

#### Scenario: 与脚本模块的接口

- **WHEN** `.agents/scripts/` 下的脚本需要调用边界处理规范
- **THEN** 系统 SHALL 提供以下接口约定：
  - 脚本须在核心分支调用边界检查函数
  - 边界检查函数遵循 check-and-restore.md 模式（检查不改变状态）
  - 边界处理结果通过返回值传递，不通过副作用

### Requirement: 边界情况验证清单

系统 SHALL 提供结构化的验证清单，用于验证边界处理规范的有效性（替代单元测试，因本模块为纯规范文档）。

#### Scenario: 规范完整性验证

- **WHEN** 验证 trae-edge-case-handler.md 规范的完整性
- **THEN** 验证清单 SHALL 覆盖：四大边界场景均有判断标准、每个边界条件有检测信号、每个异常处理流程有完整链路、每个特殊场景有预定义策略、接口规范定义清晰

#### Scenario: 规范一致性验证

- **WHEN** 验证 trae-edge-case-handler.md 与现有规范的一致性
- **THEN** 验证清单 SHALL 确认：引用的模式（multi-signal-detection/dry-run-first/check-and-restore）存在且成熟度达标、与 teams/README.md 的模块职责矩阵一致、与 AGENTS.md 的团队管理索引一致
