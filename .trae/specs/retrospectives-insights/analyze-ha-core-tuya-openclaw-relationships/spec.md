# Home Assistant Core 与 Tuya OpenClaw Skills 关系分析 Spec

## Why

当前工作区中同时存在 `d:\AI\.temp\libs\home-assistant\core`（Home Assistant Core）与 `d:\AI\.temp\libs\tuya-openclaw-skills`（Tuya/OpenClaw 技能仓库）两份代码资产，但二者的架构层级定位、技术依赖与业务关联关系未被结构化说明，导致后续做集成选型、代码复用、版本升级与风险评估时缺少可追溯依据。

## What Changes

- 新增一份“关系说明文档”（实现阶段产出：`relationship-report.md`），覆盖：
  - 项目层级关系与主从依赖判定
  - 双向代码调用/依赖扫描结果（含证据链）
  - 核心能力与复用点清单（若不存在则明确“未发现”与验证方法）
  - 版本管理与构建/发布协作关系分析（绑定发布 vs 独立迭代）
  - 依赖拓扑图与核心交互流程图（Mermaid）
- 明确本次任务为“只读分析”：不得修改上述两份外部仓库内容。

## Impact

- Affected specs: 无（新增一份关系分析报告，不修改现有规范与能力）
- Affected code: 无（不改动业务代码；仅新增 spec 目录与实现阶段报告文件）
- 影响范围：分析将引用两份外部仓库的关键文件路径与行号，以便复核与追溯

## ADDED Requirements

### Requirement: 架构层级定位与依赖方向判定

系统 SHALL 输出两份仓库在当前工作区内的层级定位与依赖方向结论，并明确结论依据（目录位置、仓库元数据、包管理/构建入口）。

#### Scenario: 判断是否存在主从依赖
- **WHEN** 对 `home-assistant/core` 与 `tuya-openclaw-skills` 的仓库属性与构建入口进行比对
- **THEN** 能得出并论证二者是否存在主从依赖、是否存在跨模块调用的设计逻辑；若结论为“无直接依赖”，必须同时给出“可能的业务关联”与“无代码级依赖的证据”

### Requirement: Core 侧可复用基础能力清单

系统 SHALL 检查 `home-assistant/core` 中是否存在被 `tuya-openclaw-skills` 可直接依赖的核心工具类、基础库或公共服务组件，并以“可复用点清单”形式输出。

#### Scenario: 检查核心工具类/公共服务
- **WHEN** 对 `home-assistant/core` 执行关键字检索与入口模块（如 `homeassistant/` 与 `homeassistant/components/tuya/`）结构梳理
- **THEN** 输出潜在可复用点清单；若未发现 `tuya-openclaw-skills` 的直接依赖点，明确“未发现”的范围、检索策略与结论边界

### Requirement: Tuya OpenClaw Skills 侧对 Core 能力的调用验证

系统 SHALL 验证 `tuya-openclaw-skills` 是否需要调用 `home-assistant/core` 的能力实现业务功能，并列出具体调用链路与依赖项；若不存在，必须以可验证方式证明“不需要/未调用”。

#### Scenario: 验证调用链路
- **WHEN** 对 `tuya-openclaw-skills` 执行对 `homeassistant.*` / `Home Assistant` / `hass` 等关键符号的检索与依赖文件比对
- **THEN** 输出“调用链路清单”或“未发现调用”的证据链（至少包含检索范围、关键查询、命中结果统计与代表性文件定位）

### Requirement: 版本管理与构建发布协作关系分析

系统 SHALL 说明两份仓库的版本管理模式（独立仓库/子模块/拷贝引入等）以及构建打包入口，并判定是否存在绑定发布或独立迭代的设计。

#### Scenario: 确认是否绑定发布
- **WHEN** 对两份仓库的 Git 元数据（分支/remote/工作树特征）、构建配置（如 `pyproject.toml`/requirements/脚本入口）进行分析
- **THEN** 输出“版本管理关系”与“构建发布关系”的结论与证据；若为独立迭代，需明确各自发布对象与迭代节奏不互锁的依据

### Requirement: 可验证可追溯的关系说明文档

系统 SHALL 产出一份可复核的关系说明文档，包含依赖拓扑图、核心交互流程与技术关联点清单，并保证读者可按文档步骤复现关键结论。

#### Scenario: 读者复核结论
- **WHEN** 读者按文档中的“验证方法”章节复现检索与定位步骤
- **THEN** 能得到一致的命中/未命中结果，并能通过文件路径与行号快速定位关键证据

## MODIFIED Requirements

无

## REMOVED Requirements

无

