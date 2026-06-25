# Trae 项目适配优化方案 Spec

## Why

当前项目已经形成以 AGENTS.md、`.agents/`、`.trae/specs/`、知识库与复盘体系为核心的 AI 协作规范，但 Trae 在项目中的使用方式仍以通用 IDE 能力和手动规范遵循为主。需要系统化分析 Trae 的现有使用场景、局限性与优化路径，将 Trae 从“执行工具”提升为“规范感知、流程驱动、知识复用”的项目协作入口。

## What Changes

- 新增一份面向本项目的 Trae 应用优化分析与实施指南，覆盖当前使用场景、局限性、配置优化、功能扩展与最佳实践。
- 明确 Trae 与 AGENTS.md 启动协议、Spec 模式、Rules、Skills、Slash 命令、子代理、MCP、知识库和复盘体系之间的协作关系。
- 提出可操作的配置优化方案，包括规则分层、上下文路由、工具使用约束、规格文档模板、验证脚本与工作区设置建议。
- 提出功能扩展建议，包括项目专属 Skill、短指令库、规格一致性检查、知识检索入口、复盘自动化与 Trae 使用指标沉淀。
- 输出最佳实践指南，指导后续在 Trae 中进行规格驱动开发、文档生成、代码修改、复盘萃取和验证闭环。

## Impact

- Affected specs: 新增 `optimize-trae-project-adaptation` 规格，不修改既有功能规格。
- Affected code: 主要影响文档与配置建议；后续实施可能涉及 `AGENTS.md`、`.agents/`、`.trae/specs/`、`docs/knowledge/`、`docs/retrospective/`、`.agents/scripts/` 等。

## ADDED Requirements

### Requirement: Trae 使用场景分析

系统 SHALL 提供本项目中 Trae 当前使用场景的结构化分析，至少覆盖规格驱动开发、规则路由、代码与文档编辑、知识库检索、复盘萃取、验证脚本执行、MCP/Skill 调用、子代理协作八类场景。

#### Scenario: 识别项目内 Trae 使用入口

- **WHEN** 用户阅读优化方案
- **THEN** 用户能够理解 Trae 在本项目中承担的主要职责、触发入口和产出物类型

#### Scenario: 区分 Trae 原生能力与项目自建规范

- **WHEN** 文档描述 Trae 能力
- **THEN** 文档 SHALL 明确区分 Trae 原生能力、项目规则层和项目自动化脚本，避免将项目自建能力误写为 Trae 平台内置能力

### Requirement: Trae 使用局限性分析

系统 SHALL 提供 Trae 当前在本项目中的局限性分析，至少覆盖上下文优先级冲突、规则分散、Skill 触发竞争、规格与实现脱节、验证依赖人工执行、历史经验复用成本、子代理边界不稳定、Windows 命令环境约束八类问题。

#### Scenario: 定位关键阻塞点

- **WHEN** 用户希望提升 Trae 工作效率
- **THEN** 文档 SHALL 给出局限性、影响范围、根因与对应优化方向

### Requirement: 配置优化方案

系统 SHALL 提供可执行的 Trae 配置优化方案，覆盖工作区 Rules、AGENTS.md 启动协议、Spec 模式模板、工具调用约束、上下文路由、Slash 命令、Skill 触发、MCP 使用、终端环境和验证门禁。

#### Scenario: 优化启动协议

- **WHEN** Trae 开启新任务或新会话
- **THEN** 方案 SHALL 要求优先读取 AGENTS.md，并按上下文路由表读取相关 `.agents/` 规范和知识库入口

#### Scenario: 优化规则分层

- **WHEN** 项目规则需要被 Trae 加载
- **THEN** 方案 SHALL 将规则拆分为全局强约束、任务路由规则、角色规则、工具规则和验证规则，避免单一大段规则导致注意力竞争

#### Scenario: 优化验证门禁

- **WHEN** Trae 完成文档、配置或代码修改
- **THEN** 方案 SHALL 要求根据任务类型执行对应检查，包括规格一致性、链接检查、路径迁移检查、Git 忽略规则检查或相关测试

### Requirement: 功能扩展建议

系统 SHALL 提供 Trae 在本项目中的功能扩展建议，至少包括项目专属 Skill、短指令库、规则一致性检查器、知识库检索入口、复盘生成工作流、任务总结沉淀、Trae 使用指标统计和多代理协作模板。

#### Scenario: 建议项目专属 Skill

- **WHEN** 用户需要减少重复提示词输入
- **THEN** 方案 SHALL 建议将高频工作流封装为项目专属 Skill，并说明触发条件、输入、输出和验证方式

#### Scenario: 建议短指令库

- **WHEN** 用户需要快速触发固定流程
- **THEN** 方案 SHALL 建议建设 `/复盘`、`/洞察`、`/萃取`、`/验证`、`/同步规格` 等短指令，并映射到现有 `.agents/commands/` 与知识库资产

### Requirement: 最佳实践指南

系统 SHALL 提供 Trae 在本项目中的最佳实践指南，覆盖任务开始、规格设计、上下文读取、工具选择、文件编辑、代码实现、验证、复盘和知识沉淀的端到端流程。

#### Scenario: 执行新功能或文档任务

- **WHEN** 用户在 Trae 中发起新任务
- **THEN** 指南 SHALL 给出从需求确认、规格创建、任务分解、子代理执行、检查清单验证到复盘沉淀的标准流程

#### Scenario: 避免常见错误

- **WHEN** 用户或智能体执行任务
- **THEN** 指南 SHALL 明确禁止跳过 AGENTS.md、禁止未读文件直接修改、禁止 shell 替代专用文件工具、禁止将临时依赖提交到 Git、禁止在规格阶段直接写实现代码

### Requirement: 可操作性与优先级

系统 SHALL 将优化建议按优先级和落地成本组织，至少分为立即可做、短期配置、中期扩展和长期度量四类。

#### Scenario: 制定执行路线

- **WHEN** 用户希望按步骤改进 Trae 使用效果
- **THEN** 文档 SHALL 提供每项建议的目标、操作步骤、涉及文件、验证方式和预期收益

### Requirement: 与项目既有资产对齐

系统 SHALL 引用并对齐项目既有资产，包括 AGENTS.md、`.agents/` 角色和工具规范、Spec-driven 方法论、知识库排错经验、复盘模式库和已有 Trae 相关洞察。

#### Scenario: 避免重复建设

- **WHEN** 方案提出新增配置或功能
- **THEN** 方案 SHALL 说明可复用的既有文件或模式，优先扩展现有体系而非另起一套规则

## MODIFIED Requirements

无。

## REMOVED Requirements

无。
