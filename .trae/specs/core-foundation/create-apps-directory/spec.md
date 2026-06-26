# 创建 apps/ 新应用开发工作空间 Spec

## Why
当前项目缺乏一个专门用于开发新应用的独立工作空间。现有目录（`.agents/`、`docs/`、`prompt_extraction/` 等）各有其专有用途，不适宜承载新应用的代码与资源。需要规划一个符合项目目录结构规范的 `apps/` 目录，为新应用的开发提供隔离、清晰的基础环境，同时需要在 `.agents/` 中建立相应的管理规范，约束应用开发从 `.temp/` 暂存区逐步迁移至 `apps/` 的流程。

## What Changes
- 在项目根目录下创建 `apps/` 目录作为新应用开发专用工作空间
- 在 `apps/` 下创建必要的子目录结构，支持多应用并存、资源隔离与统一管理
- 提供 `apps/README.md` 说明目录用途、使用规范以及 `.temp/` → `apps/` 迁移流程
- 在 `.agents/protocols/` 下新增 `app-development-workflow.md`，定义应用开发的生命周期管理（含 `.temp/` 暂存开发 → `apps/` 稳定迁移的规则）
- 更新 `AGENTS.md` 上下文路由表与协作协议概要，添加对 `apps/` 管理规范的引用
- 更新 `docs/project-structure.md`，补充 `apps/` 目录的说明
- 将 `apps/` 纳入 Git 版本控制（不作为忽略项）

## Impact
- Affected specs: 无现有 spec 受影响
- Affected code: `docs/project-structure.md`（需新增条目）、`AGENTS.md`（需新增上下文路由条目与协议概要条目）

## ADDED Requirements

### Requirement: 创建 apps/ 根目录
系统应在项目根目录下创建 `apps/` 目录，作为所有新应用的顶层容器。

#### Scenario: 目录创建成功
- **WHEN** 执行创建操作
- **THEN** 项目根目录下存在 `apps/` 目录

### Requirement: apps/ 子目录结构
`apps/` 目录应具备清晰的层级划分，至少包含以下子目录：

- `apps/shared/` — 存放多个应用之间可共享的公共模块、工具库、通用组件等
- `apps/.gitkeep` — 在各空子目录中放置 `.gitkeep` 文件以确保 Git 能追踪空目录结构

#### Scenario: 子目录结构完整
- **WHEN** 检查 `apps/` 目录
- **THEN** `apps/shared/` 子目录存在，且各空子目录内含 `.gitkeep` 文件

### Requirement: apps/README.md 使用说明
`apps/README.md` 应说明以下内容：
- `apps/` 目录的用途与定位
- 子目录结构及其职责
- 新应用创建规范（命名约定、目录结构模板、依赖管理原则）
- `.temp/` → `apps/` 迁移流程说明（先在 `.temp/` 中进行初期开发，达到稳定状态后迁移至 `apps/`）
- 与项目其他目录的关系（特别是 `.temp/`、`vendor/`、`docs/`、`.agents/`）

#### Scenario: README 内容完整
- **WHEN** 审阅 `apps/README.md`
- **THEN** 包含用途说明、子目录职责、新应用创建规范（含迁移流程）、目录关系说明五个方面的内容

### Requirement: .agents/ 中新增 app-development-workflow 协议
系统应在 `.agents/protocols/` 下创建 `app-development-workflow.md`，定义新应用开发的完整生命周期规范，至少涵盖以下内容：

- **暂存开发阶段**：新应用须先在 `.temp/<app-name>/` 中进行初期开发与验证，说明暂存目录的组织方式与命名规范
- **稳定迁移阶段**：应用达到功能稳定、测试通过、代码审查完成等条件后，从 `.temp/<app-name>/` 迁移至 `apps/<app-name>/`
- **清理阶段**：迁移完成后清理 `.temp/<app-name>/` 中的残留文件
- **与现有协议的衔接**：与 `dependency-management.md` 中 `.temp/` 目录使用规范的关系说明

#### Scenario: app-development-workflow 协议内容完整
- **WHEN** 审阅 `.agents/protocols/app-development-workflow.md`
- **THEN** 包含暂存开发、稳定迁移、清理三个阶段的生命周期定义，以及与 `dependency-management.md` 的关系说明

### Requirement: AGENTS.md 上下文路由更新
`AGENTS.md` 应添加对 `apps/` 管理规范的引用，包括：
- 上下文路由表中新增 "应用开发生命周期" 任务的入口，指向 `.agents/protocols/app-development-workflow.md`
- 协作协议概要表中新增 `app-development-workflow` 条目

#### Scenario: AGENTS.md 路由完整
- **WHEN** 查看 `AGENTS.md` 的上下文路由表
- **THEN** 包含应用开发生命周期的路由条目
- **WHEN** 查看 `AGENTS.md` 的协作协议概要
- **THEN** 包含 app-development-workflow 条目

### Requirement: Git 版本控制
`apps/` 目录及其下的应用代码应纳入 Git 版本控制进行跟踪管理。

#### Scenario: Git 可追踪
- **WHEN** 在 `apps/` 下创建文件后执行 `git status`
- **THEN** 文件显示为未跟踪状态（未被 `.gitignore` 忽略）

### Requirement: 项目结构文档更新
`docs/project-structure.md` 应包含 `apps/` 目录的条目，说明其用途与面向对象。

#### Scenario: 文档包含 apps 条目
- **WHEN** 查看 `docs/project-structure.md` 的目录树与职责说明表格
- **THEN** 均包含 `apps/` 目录的相关描述
