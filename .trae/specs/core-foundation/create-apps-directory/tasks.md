# 创建 apps/ 新应用开发工作空间 — 任务列表

- [x] Task 1: 创建 apps/ 目录结构
  - [x] 在项目根目录下创建 `apps/` 目录
  - [x] 在 `apps/` 下创建 `shared/` 子目录
  - [x] 在 `apps/shared/` 下放置 `.gitkeep` 文件

- [x] Task 2: 编写 apps/README.md 使用说明
  - [x] 编写 `apps/README.md`，包含用途定位、子目录职责、新应用创建规范（含 `.temp/` → `apps/` 迁移流程）、与项目其他目录的关系

- [x] Task 3: 创建 .agents/protocols/app-development-workflow.md 协议
  - [x] 创建 `app-development-workflow.md`，定义暂存开发（`.temp/`）、稳定迁移（→ `apps/`）、清理三个阶段的生命周期规范
  - [x] 说明与 `dependency-management.md` 中 `.temp/` 目录使用规范的关系

- [x] Task 4: 更新 AGENTS.md 上下文路由与协作协议概要
  - [x] 在上下文路由表中新增 "应用开发生命周期" 任务类型入口，指向 `.agents/protocols/app-development-workflow.md`
  - [x] 在协作协议概要表中新增 `app-development-workflow` 条目

- [x] Task 5: 更新项目结构文档
  - [x] 更新 `docs/project-structure.md` 的目录树，添加 `apps/` 条目
  - [x] 更新 `docs/project-structure.md` 的目录职责说明表格，添加 `apps/` 行

# Task Dependencies
- Task 2 无依赖，可与 Task 1 并行执行
- Task 3 无依赖，可与 Task 1、Task 2 并行执行
- Task 4 无依赖，可与 Task 1、Task 2、Task 3 并行执行
- Task 5 无依赖，可与 Task 1、Task 2、Task 3、Task 4 并行执行
