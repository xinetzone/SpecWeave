# 竹简悟道 — 新增哲思引导者角色 Spec

## Why

竹简悟道项目当前处于洞察库建设期，核心工作是撰写、维护和审查基于帛书《老子》的哲学洞察。现有 `.agents/` 目录下缺乏角色分工体系，所有洞察相关工作均由通用 Agent 执行，缺乏针对哲学内容生成和质量把关的专职角色。需要新增「哲思引导者 (philosopher)」角色，专注于从帛书《老子》哲学根基出发生成和审查洞察内容。

## What Changes

- 在 `.agents/roles/` 下创建 `philosopher.md` 角色定义文件
- 参考根项目 `.agents/roles/` 的角色模式（TOML frontmatter + 三段式正文）
- 参考根项目 `.temp/skills/ian-xiaohei-illustrations` 的参考目录模式，创建 `references/` 子目录存放辅助材料
- 角色需内嵌竹简悟道的核心约束（三不原则：不给予答案、不做出评价、不引导特定方向）
- 更新 `AGENTS.md` 的路由索引，添加新角色入口

## Impact

- Affected specs: 无（此为新增角色，不影响现有 spec）
- Affected code: `AGENTS.md`（路由索引更新）、`.agents/roles/philosopher.md`（新增）、`.agents/roles/README.md`（新增角色索引）、`.agents/roles/references/`（辅助参考目录）

## ADDED Requirements

### Requirement: 哲思引导者角色定义

系统 SHALL 在竹简悟道项目的 `.agents/roles/` 目录下提供一个完整的哲思引导者角色定义文件 `philosopher.md`，该角色专注于基于帛书《老子》的哲学洞察生成与审查。

#### Scenario: 角色文件结构完整性

- **WHEN** 读取 `.agents/roles/philosopher.md`
- **THEN** 文件应包含 TOML frontmatter（`id`、`domain`、`layer`、`tier`、`[bindings]`）和 Markdown 正文（`# 哲思引导者`、`## 核心定位`、`## 职责`、`## 非目标`）
- **AND** TOML frontmatter 中 `id = "philosopher"`, `domain = "content"`, `layer = "generation"`, `tier = "standard"`
- **AND** `[bindings]` 应声明引用的规则、参考文件和工作流

#### Scenario: 职责覆盖核心工作流

- **WHEN** 角色处理洞察相关任务
- **THEN** 职责应覆盖：洞察撰写与编号、交叉引用维护、统计更新、复盘报告同步
- **AND** 应与 [workflows.md §工作流一](../../../../apps/zhujian-wudao/.agents/workflows.md) 和 [workflows.md §工作流二](../../../../apps/zhujian-wudao/.agents/workflows.md) 保持对齐

#### Scenario: 内嵌三不原则约束

- **WHEN** 角色生成或审查洞察内容
- **THEN** 必须遵守竹简悟道核心约束（不给予答案、不做出评价、不引导特定方向）
- **AND** 不得声称"老子的原意是……"（C-05）
- **AND** 不得引入知识承诺式表述（C-06）

#### Scenario: 遵循项目命名与引用规范

- **WHEN** 角色在职责描述中引用项目文件
- **THEN** 必须使用相对路径引用（遵循 [conventions.md §交叉引用格式](../../../../apps/zhujian-wudao/.agents/conventions.md)）
- **AND** 文件命名使用 kebab-case

### Requirement: 角色索引文件

系统 SHALL 在 `.agents/roles/` 目录下提供 `README.md` 角色索引文件，登记哲思引导者角色并描述其定位。

#### Scenario: 索引文件结构

- **WHEN** 读取 `.agents/roles/README.md`
- **THEN** 文件应包含角色概述、目录结构说明和文件列表
- **AND** 应遵循根项目角色索引的结构模式

### Requirement: 辅助参考目录

系统 SHALL 在 `.agents/roles/references/` 下提供辅助参考文件，帮助哲思引导者角色更准确地执行洞察撰写任务。

#### Scenario: 参考文件内容

- **WHEN** 哲思引导者需要查阅规范进行洞察撰写
- **THEN** `references/` 目录应至少包含一份核心参考文件
- **AND** 参考文件应摘录核心概念词典（体道四法、体道链、玄同、恒德等）和洞察撰写标准结构

### Requirement: 路由索引更新

系统 SHALL 更新 `AGENTS.md`，在路由索引和文件地图中体现新增的角色定义入口。

#### Scenario: 路由索引完整性

- **WHEN** 查看 `AGENTS.md`
- **THEN** 文件地图应包含 `.agents/roles/` 目录
- **AND** 路由索引应包含指向 `philosopher.md` 的条目
