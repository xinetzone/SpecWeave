# AGENTS.md、README.md 与 .agents 文件夹一致性同步 Spec

## Why

AGENTS.md 作为智能体最高优先级入口，README.md 作为面向人类读者的项目入口，两者的索引与路由应准确反映 `.agents/` 文件夹的实际内容。经对比发现：AGENTS.md 的索引覆盖不完整（scripts 目录仅列出 1 个脚本，实际 7 个；modules/tools/workflows/templates/prompts 目录缺少详细文件索引表）；README.md 的规范体系文档索引缺少 scripts 目录条目。需双向同步，确保三个入口（AGENTS.md、README.md、.agents/）内容一致。

## What Changes

### AGENTS.md 更新

- 更新上下文路由表，补充 scripts 目录下所有脚本的说明（新增 6 个）
- 新增「自我演进模块索引」表，列出 8 个模块
- 新增「工具规范索引」表，列出 4 个工具规范文件
- 新增「标准工作流索引」表，列出 3 个工作流文件
- 新增「模板索引」表，列出 2 个模板文件
- 新增「提示词索引」表，列出 5 个角色提示词
- 确保所有索引表格式与现有「角色定义索引」和「协作协议概要」一致

### README.md 更新

- 在规范体系文档索引（折叠区域）中补充 scripts 目录条目
- 确保 README.md 中所有 .agents/ 引用与实际文件一致
- 确保 README.md 中提到的脚本（如 check-gitignore.py）与实际存在的脚本一致

### 约束

- 不修改 .agents/ 下任何文件（单向同步：AGENTS.md 和 README.md 追随 .agents/ 实际内容）

## Impact

- Affected specs: 
  - [create-agents-md-and-config](../create-agents-md-and-config/spec.md)（原始创建 spec）
  - [add-team-collaboration-scenario-to-readme](../add-team-collaboration-scenario-to-readme/spec.md)（README 章节）
- Affected code: 
  - [AGENTS.md](../../../AGENTS.md)（新增 5 个索引表，更新路由表）
  - [README.md](../../../README.md)（更新规范体系文档索引）
- 不修改 .agents/ 下任何文件

## ADDED Requirements

### Requirement: AGENTS.md 自我演进模块索引表

系统 SHALL 在 AGENTS.md 中新增「自我演进模块索引」表，列出 .agents/modules/ 下的 8 个模块，格式与角色定义索引一致。

#### Scenario: 模块索引完整

- **WHEN** 智能体查询自我演进模块
- **THEN** AGENTS.md 提供完整的 8 个模块索引表，包含模块名称、ID、所属层级、入口路径

### Requirement: AGENTS.md 工具规范索引表

系统 SHALL 在 AGENTS.md 中新增「工具规范索引」表，列出 .agents/tools/ 下的 4 个工具规范文件。

#### Scenario: 工具索引完整

- **WHEN** 智能体查询工具调用规范
- **THEN** AGENTS.md 提供完整的 4 个工具规范索引表，包含工具名称、用途、入口路径

### Requirement: AGENTS.md 标准工作流索引表

系统 SHALL 在 AGENTS.md 中新增「标准工作流索引」表，列出 .agents/workflows/ 下的 3 个工作流文件。

#### Scenario: 工作流索引完整

- **WHEN** 智能体查询标准工作流
- **THEN** AGENTS.md 提供完整的 3 个工作流索引表，包含工作流名称、用途、入口路径

### Requirement: AGENTS.md 模板索引表

系统 SHALL 在 AGENTS.md 中新增「模板索引」表，列出 .agents/templates/ 下的 2 个模板文件。

#### Scenario: 模板索引完整

- **WHEN** 智能体查询任务与交接模板
- **THEN** AGENTS.md 提供完整的 2 个模板索引表，包含模板名称、用途、入口路径

### Requirement: AGENTS.md 提示词索引表

系统 SHALL 在 AGENTS.md 中新增「提示词索引」表，列出 .agents/prompts/ 下的 5 个角色提示词。

#### Scenario: 提示词索引完整

- **WHEN** 智能体查询系统提示词与 few-shot
- **THEN** AGENTS.md 提供完整的 5 个角色提示词索引表，包含角色名称、提示词文件、入口路径

### Requirement: AGENTS.md scripts 路由表更新

系统 SHALL 更新 AGENTS.md 上下文路由表中 scripts 相关条目，补充所有验证与工具脚本的说明。

#### Scenario: 脚本路由完整

- **WHEN** 智能体查询验证脚本
- **THEN** AGENTS.md 上下文路由表列出所有 7 个脚本及其用途

### Requirement: README.md 规范体系文档索引更新

系统 SHALL 在 README.md 的规范体系文档索引（折叠区域）中补充 scripts 目录条目。

#### Scenario: README 索引完整

- **WHEN** 读者查看 README.md 规范体系文档索引
- **THEN** 索引包含 .agents/scripts/README.md 条目，说明验证与工具脚本

## MODIFIED Requirements

### Requirement: AGENTS.md 上下文路由表

AGENTS.md 上下文路由表更新为：

| 任务类型 | 必读入口 |
|---|---|
| 角色定义、职责分工 | .agents/roles/ |
| 自我演进模块定义 | .agents/modules/ |
| 系统提示词、few-shot | .agents/prompts/ |
| 工具调用规范 | .agents/tools/ |
| 协作协议、通信机制 | .agents/protocols/ |
| 标准工作流 | .agents/workflows/ |
| 任务与交接模板 | .agents/templates/ |
| Git 忽略规则验证 | .agents/scripts/check-gitignore.py |
| 链接有效性验证 | .agents/scripts/check-links.py |
| 文件路径迁移 | .agents/scripts/check-move.py |
| 派生产物溯源 | .agents/scripts/check-source-traceability.py |
| 规格一致性验证 | .agents/scripts/check-spec-consistency.py |
| 导航表生成 | .agents/scripts/generate-nav.py |
| CI 综合检查 | .agents/scripts/ci-check.ps1 / ci-check.sh |
| 技术知识库查阅 | docs/knowledge/README.md |
| 复盘体系与可复用模式 | docs/retrospective/README.md |
| 提示词工程模式 | docs/retrospective/prompt-extraction.md |

### Requirement: README.md 规范体系文档索引

README.md 规范体系文档索引补充 scripts 目录条目：

| 脚本索引 | [.agents/scripts/README.md](../../../.agents/scripts/README.md) | 验证与工具脚本 |

## REMOVED Requirements

无移除项。
