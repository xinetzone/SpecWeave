# 联合创始角色特殊标记 Spec

## Why
当前 `.agents/roles` 角色管理模块中所有角色（orchestrator/architect/developer/reviewer/tester）采用同质化呈现，无法区分项目初创阶段的"联合创始"角色与普通角色。需要为联合创始角色引入特殊标记机制，在角色数据模型、索引清单与详情页面中保持一致的高辨识度视觉呈现，并通过权限声明约束其查看与管理范围。

## What Changes
- 在角色数据模型（TOML frontmatter）中新增 `tier` 标识字段，取值为 `co-founder`（联合创始）或 `standard`（普通，默认可省略）
- 新增 `[permissions]` 表，声明联合创始角色的查看与管理权限边界
- 新增联合创始角色定义文件 `co-founder.md`，承载联合创始角色职责
- 在 `README.md` 角色职责矩阵中新增"层级"列与视觉徽章（🏛️），并追加联合创始角色行
- 在角色详情文件标题中应用统一文字前缀 `[联合创始]` 与徽章标记
- 在 `README.md` 中补充权限控制说明章节，明确联合创始角色的查看/管理权限要求
- **BREAKING**：TOML frontmatter 新增可选字段 `tier` 与 `[permissions]` 表，现有角色文件未声明时按 `standard` 默认值处理，向后兼容

## Impact
- Affected specs:
  - `create-agents-md-and-config`（角色定义体系基础规范）
  - `sync-agents-md-with-agents-folder`（AGENTS.md 与 .agents 同步规范）
- Affected code:
  - `.agents/roles/README.md`（角色索引与职责矩阵）
  - `.agents/roles/co-founder.md`（新增联合创始角色文件）
  - `.agents/roles/*.md`（现有角色文件需评估是否补充 tier 声明，保持一致性）
  - `AGENTS.md`（角色定义索引表需同步新增联合创始角色行）

## ADDED Requirements

### Requirement: 联合创始角色标识字段
系统 SHALL 在角色数据模型（TOML frontmatter）中提供 `tier` 字段，用于区分联合创始角色与普通角色。当 `tier = "co-founder"` 时，该角色被标记为联合创始角色。

#### Scenario: 联合创始角色声明
- **WHEN** 角色文件 frontmatter 中声明 `tier = "co-founder"`
- **THEN** 该角色在索引与详情页中被识别为联合创始角色并应用特殊视觉标记

#### Scenario: 普通角色默认值
- **WHEN** 角色文件 frontmatter 未声明 `tier` 字段
- **THEN** 系统按 `tier = "standard"` 默认值处理，不应用联合创始特殊标记

### Requirement: 联合创始角色权限声明
系统 SHALL 在联合创始角色文件的 TOML frontmatter 中提供 `[permissions]` 表，声明该角色的查看与管理权限边界。

#### Scenario: 权限声明存在性
- **WHEN** 角色被标记为 `tier = "co-founder"`
- **THEN** 该角色文件 frontmatter 必须包含 `[permissions]` 表，声明 `view` 与 `manage` 权限范围

### Requirement: 联合创始角色视觉标记
系统 SHALL 在角色索引（README.md 职责矩阵）与角色详情文件中应用统一的视觉标记（🏛️ 徽章 + `[联合创始]` 文字前缀），确保在所有相关用户界面中保持一致性与高辨识度。

#### Scenario: 索引清单视觉标记
- **WHEN** 用户查看 `.agents/roles/README.md` 角色职责矩阵
- **THEN** 联合创始角色行在"层级"列显示 🏛️ 徽章与"联合创始"文字标识

#### Scenario: 详情页视觉标记
- **WHEN** 用户打开联合创始角色详情文件
- **THEN** 文件标题以 `[联合创始] 🏛️` 前缀起始，与索引清单标记保持一致

### Requirement: 联合创始角色权限控制说明
系统 SHALL 在 `.agents/roles/README.md` 中提供权限控制说明章节，明确联合创始角色的查看与管理权限要求，确保只有具备相应权限的用户能够查看或管理带有此特殊标记的角色。

#### Scenario: 权限说明可读性
- **WHEN** 用户查阅角色索引文档
- **THEN** 文档包含"权限控制"章节，说明联合创始角色的查看与管理权限边界

## MODIFIED Requirements

### Requirement: 角色职责矩阵
`.agents/roles/README.md` 中的角色职责矩阵 SHALL 新增"层级"列，展示每个角色的 tier 标识（联合创始角色显示 🏛️ 联合创始，普通角色显示"标准"），并追加联合创始角色行。

## REMOVED Requirements
无移除项。
