# 智能体开发规范体系 Spec

## Why

项目根目录缺少统一的智能体开发规范入口与配置资产目录，导致多智能体协作时职责不清、通信机制缺失、提示词与工具调用规范分散。需要在项目根目录建立 `AGENTS.md` 全局契约与 `.agents/` 配置目录，形成自包含的智能体协作开发体系，支持多智能体明确分工与协同工作。同时项目需要纳入 git 版本控制系统，将第三方库依赖存放目录排除在 git 跟踪范围之外，确保其余所有文件和目录均受版本控制管理。此外，现有 `libs/` 目录命名不够描述性，需重命名为 `vendor/` 以符合行业命名惯例（PHP Composer、Go modules、Node.js 等生态的第三方依赖目录标准），提升代码可读性与项目可维护性。

## What Changes

- 新增 `AGENTS.md`（项目根目录）：智能体全局契约入口，包含角色定义、能力边界、协作协议、开发规范与测试要求
- 新增 `.agents/` 目录（项目根目录）：按功能分类存放智能体配置资产
  - `roles/`：智能体角色定义（含 TOML frontmatter 元数据）
  - `prompts/`：系统提示词与 few-shot 示例（按角色分子目录）
  - `tools/`：工具调用规范（文件操作、代码执行、搜索、通信）
  - `protocols/`：协作协议（任务交接、消息传递、冲突解决）
  - `workflows/`：标准工作流（功能开发、代码审查、测试流程）
  - `templates/`：任务与交接模板
- 新增 `.agents/README.md`：目录说明与使用指引
- **重命名 `libs/` 为 `vendor/`**：将第三方库依赖存放目录从 `libs/` 重命名为 `vendor/`，符合行业命名惯例，准确反映目录用途（存放 vendored 第三方依赖）
- **新增 `.gitignore`（项目根目录）**：将 `vendor/` 目录及其所有子文件、子目录排除在 git 跟踪范围之外
- **初始化 git 仓库**（若尚未初始化）：在项目根目录 `d:\AI\` 执行 `git init`，确保项目纳入版本控制

## Impact

- Affected specs: 无（新建规范体系，不修改现有 specs）
- Affected code: 无（纯文档与配置资产，不涉及代码逻辑修改）
- 与 `vendor/flexloop/apps/chaos/.agents/` 的关系：项目根目录体系为自包含的独立实现，遵循相同的开放标准（AGENTS.md 标准），但面向项目根目录的通用智能体协作场景；不修改 flexloop 子项目内已有的 `.agents/` 结构
- **目录重命名影响**：`libs/` 重命名为 `vendor/` 后，需同步更新所有引用 `libs/` 路径的文件（当前仅 `.trae/specs/` 下的规格文档引用了该路径，flexloop 内部引用的是 "ai-libs" 概念而非目录路径，无需修改）
- **git 版本控制影响**：`vendor/` 目录作为第三方库依赖存放位置，将被 `.gitignore` 排除；项目根目录下其余所有文件和目录（包括 `AGENTS.md`、`.agents/`、`.trae/`、`.gitignore` 等）均纳入 git 跟踪范围

## ADDED Requirements

### Requirement: AGENTS.md 全局契约

系统 SHALL 在项目根目录提供 `AGENTS.md` 文件，作为所有智能体的最高优先级入口与上下文路由，包含全局核心规则、角色定义索引、能力边界声明、协作协议概要、开发规范与测试要求。

#### Scenario: 智能体启动路由

- **WHEN** 智能体接收到任务
- **THEN** 必须先读取 `AGENTS.md`，根据任务类型路由到 `.agents/` 下对应规范，再执行任务

#### Scenario: 全局核心规则遵循

- **WHEN** 智能体执行任何任务
- **THEN** 必须遵循沟通语言（中文）、按需读取、上下文节省、Mermaid 优先等全局核心规则

### Requirement: 角色定义体系

系统 SHALL 在 `.agents/roles/` 目录下定义至少 5 个核心智能体角色，每个角色包含 TOML frontmatter 元数据（id、domain、layer、bindings）与 Markdown 正文（Description、Responsibilities、Non-Goals）。

#### Scenario: 角色定义完整性

- **WHEN** 查看任意角色定义文件
- **THEN** 文件必须包含 TOML frontmatter（id、domain、layer、bindings）与 Markdown 正文（Description、Responsibilities、Non-Goals 三个章节）

#### Scenario: 核心角色覆盖

- **WHEN** 检查 `.agents/roles/` 目录
- **THEN** 必须包含以下角色：编排协调者（orchestrator）、架构师（architect）、开发者（developer）、代码审查者（reviewer）、测试工程师（tester）

### Requirement: 系统提示词与 Few-shot 示例

系统 SHALL 在 `.agents/prompts/` 目录下按角色分子目录存放系统提示词与 few-shot 示例，每个角色子目录包含 `system-prompt.md`（系统提示词）与 `few-shot.md`（少样本示例）。

#### Scenario: 提示词资产组织

- **WHEN** 查看 `.agents/prompts/` 目录
- **THEN** 每个角色必须有独立的子目录，且子目录内包含 `system-prompt.md` 与 `few-shot.md` 两个文件

#### Scenario: 系统提示词内容

- **WHEN** 读取任意角色的 `system-prompt.md`
- **THEN** 内容必须包含角色定位、能力描述、行为约束、输出格式要求四个部分

### Requirement: 工具调用规范

系统 SHALL 在 `.agents/tools/` 目录下定义工具调用规范，覆盖文件操作、代码执行、搜索、通信四类工具，每类工具规范包含工具名称、输入参数 schema、输出格式、使用约束。

#### Scenario: 工具规范覆盖

- **WHEN** 检查 `.agents/tools/` 目录
- **THEN** 必须包含 `file-operations.md`、`code-execution.md`、`search.md`、`communication.md` 四个规范文件

#### Scenario: 工具规范内容

- **WHEN** 读取任意工具规范文件
- **THEN** 内容必须包含工具清单、输入参数 schema（表格形式）、输出格式、使用约束与示例

### Requirement: 协作协议

系统 SHALL 在 `.agents/protocols/` 目录下定义协作协议，包含任务交接协议、消息传递协议、冲突解决协议，支持多智能体明确分工与协同工作。

#### Scenario: 协作协议覆盖

- **WHEN** 检查 `.agents/protocols/` 目录
- **THEN** 必须包含 `handoff.md`（任务交接）、`messaging.md`（消息传递）、`conflict-resolution.md`（冲突解决）三个协议文件

#### Scenario: 任务交接协议

- **WHEN** 智能体 A 需要将任务交接给智能体 B
- **THEN** 必须遵循 `handoff.md` 定义的交接格式，包含任务上下文、已完成工作、待办事项、风险提示四个字段

#### Scenario: 消息传递协议

- **WHEN** 智能体之间需要通信
- **THEN** 必须使用 `messaging.md` 定义的消息格式，包含发送方、接收方、消息类型、内容、优先级五个字段

### Requirement: 标准工作流

系统 SHALL 在 `.agents/workflows/` 目录下定义标准工作流，包含功能开发流程、代码审查流程、测试流程，每个工作流使用 Mermaid 流程图描述步骤与角色参与。

#### Scenario: 工作流覆盖

- **WHEN** 检查 `.agents/workflows/` 目录
- **THEN** 必须包含 `feature-development.md`、`code-review.md`、`testing.md` 三个工作流文件

#### Scenario: 工作流可视化

- **WHEN** 读取任意工作流文件
- **THEN** 内容必须包含至少 1 张 Mermaid 流程图，展示步骤流转与角色参与

### Requirement: 模板资产

系统 SHALL 在 `.agents/templates/` 目录下提供任务模板与交接模板，标准化多智能体协作的产物格式。

#### Scenario: 模板覆盖

- **WHEN** 检查 `.agents/templates/` 目录
- **THEN** 必须包含 `task-template.md`（任务模板）与 `handoff-template.md`（交接模板）两个文件

### Requirement: 目录说明文档

系统 SHALL 在 `.agents/README.md` 提供目录说明与使用指引，包含目录结构图、各子目录职责说明、使用流程示例。

#### Scenario: 目录说明完整性

- **WHEN** 读取 `.agents/README.md`
- **THEN** 内容必须包含目录结构树状图、各子目录职责说明表、从任务到执行的完整使用流程示例

### Requirement: 多智能体协作支持

系统 SHALL 通过角色定义、协作协议、工作流的组合，支持多智能体协作开发，每个智能体有明确的职责分工与通信机制。

#### Scenario: 职责分工明确

- **WHEN** 检查任意两个角色的 Non-Goals 章节
- **THEN** 必须存在显式的职责边界声明，避免角色间职责重叠

#### Scenario: 通信机制可用

- **WHEN** 多个智能体需要协作完成任务
- **THEN** 必须能通过 `protocols/messaging.md` 定义的消息格式进行通信，并通过 `protocols/handoff.md` 定义交接格式完成任务转移

### Requirement: Git 版本控制与 .gitignore 配置

系统 SHALL 在项目根目录初始化 git 仓库（若尚未初始化），并创建 `.gitignore` 文件将 `vendor/` 目录及其所有子文件、子目录明确排除在 git 跟踪范围之外，同时确保项目其他所有必要文件和目录均能正常被 git 管理和版本控制。

#### Scenario: Git 仓库初始化

- **WHEN** 项目根目录 `d:\AI\` 不存在 `.git` 目录
- **THEN** 必须执行 `git init` 初始化仓库，使项目纳入版本控制

#### Scenario: .gitignore 排除 vendor 目录

- **WHEN** 检查项目根目录的 `.gitignore` 文件
- **THEN** 文件必须包含 `vendor/` 规则，将 `vendor/` 目录及其所有子文件、子目录排除在 git 跟踪范围之外

#### Scenario: 其余文件正常跟踪

- **WHEN** 执行 `git status` 检查仓库状态
- **THEN** `vendor/` 目录下的文件不应出现在未跟踪文件列表中，而项目根目录下的其他文件和目录（如 `AGENTS.md`、`.agents/`、`.trae/`、`.gitignore` 等）应正常显示为未跟踪或已跟踪状态

### Requirement: 临时依赖 Git 忽略规则完善

系统 SHALL 在 `.gitignore` 文件中添加针对临时依赖文件、目录的完整忽略规则，覆盖所有临时依赖相关路径，确保外部临时依赖不被 Git 直接管理。

#### Scenario: 临时依赖忽略规则覆盖

- **WHEN** 检查 `.gitignore` 文件内容
- **THEN** 必须包含以下忽略规则：`vendor/`（第三方库依赖）、`.temp/`（任务中间产物）、`__pycache__/`（Python 缓存）、`*.pyc`（Python 编译文件）、`.venv/`（虚拟环境）、`node_modules/`（Node.js 依赖）、`.env`（环境变量）、`*.log`（日志文件）、`.DS_Store`（macOS 系统文件）、`Thumbs.db`（Windows 系统文件）

#### Scenario: 临时依赖不出现在 Git 命令结果

- **WHEN** 执行 `git status` 或 `git add .` 命令
- **THEN** 临时依赖文件和目录不应出现在命令结果中，且不会被纳入版本控制历史

### Requirement: 临时依赖管理流程文档

系统 SHALL 在 `.agents/protocols/` 目录下建立临时依赖管理流程文档，规定临时依赖的存放位置、使用规范及清理机制。

#### Scenario: 临时依赖管理流程文档存在

- **WHEN** 检查 `.agents/protocols/` 目录
- **THEN** 必须包含 `dependency-management.md` 文件，定义临时依赖的存放位置（`vendor/`）、使用规范（按需引入、版本锁定）、清理机制（定期清理无用依赖）

#### Scenario: 临时依赖管理流程内容完整

- **WHEN** 读取 `dependency-management.md` 文件
- **THEN** 内容必须包含存放位置规范、使用规范、清理机制、禁止提交条款四个部分

### Requirement: 团队开发规范禁止提交临时依赖

系统 SHALL 在 AGENTS.md 的开发规范章节中补充相关条款，明确禁止将临时依赖提交至 Git 仓库。

#### Scenario: 禁止提交条款存在

- **WHEN** 读取 AGENTS.md 的开发规范章节
- **THEN** 必须包含明确条款："禁止将 `vendor/`、`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖和中间产物提交至 Git 仓库"

### Requirement: Git Hooks 自动化检查

系统 SHALL 通过 Git hooks 添加自动化检查，防止临时依赖被意外提交。

#### Scenario: pre-commit hook 存在且有效

- **WHEN** 检查 `.git/hooks/` 目录或项目配置的 hooks 路径
- **THEN** 必须存在 `pre-commit` hook 脚本，检查暂存区是否包含 `vendor/`、`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖路径，若包含则阻止提交并提示错误

#### Scenario: 临时依赖提交被阻止

- **WHEN** 开发者尝试执行 `git commit` 且暂存区包含临时依赖文件
- **THEN** pre-commit hook 应阻止提交，输出错误信息提示哪些临时依赖文件被阻止，并建议从暂存区移除

### Requirement: 临时依赖规则有效性验证

系统 SHALL 提供验证机制，确保更新后的 Git 忽略规则有效，临时依赖文件不会出现在 git status、git add 等命令的结果中，且不会被纳入版本控制历史。

#### Scenario: 验证脚本存在

- **WHEN** 检查项目验证脚本
- **THEN** 必须存在验证脚本（如 `.agents/scripts/check-gitignore.py`），用于检查 `.gitignore` 规则是否覆盖所有临时依赖路径，并验证 `git status` 输出中不包含临时依赖文件

#### Scenario: 验证通过

- **WHEN** 执行验证脚本
- **THEN** 脚本应输出验证通过信息，确认所有临时依赖路径已被 `.gitignore` 覆盖，且 `git status` 输出中不包含临时依赖文件

### Requirement: 目录重命名 libs/ 为 vendor/

系统 SHALL 将项目根目录下的 `libs/` 目录重命名为 `vendor/`，并同步更新所有引用旧路径的文件，确保项目能够正常编译和运行。

#### Scenario: 目录重命名执行

- **WHEN** 执行目录重命名操作
- **THEN** `d:\AI\libs\` 目录应变为 `d:\AI\vendor\`，原 `libs/flexloop/` 内容完整迁移至 `vendor/flexloop/`

#### Scenario: 引用路径同步更新

- **WHEN** 重命名完成后检查所有引用 `libs/` 路径的文件
- **THEN** 所有引用必须更新为 `vendor/`，确保无残留的旧路径引用

#### Scenario: 项目正常运行验证

- **WHEN** 重命名与路径更新完成后
- **THEN** 项目应能正常访问 `vendor/flexloop/` 下的内容，无因路径变更导致的引用错误
