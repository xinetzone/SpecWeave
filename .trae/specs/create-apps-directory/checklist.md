# 创建 apps/ 新应用开发工作空间 — 验收清单

- [x] `apps/` 目录已存在于项目根目录下
- [x] `apps/shared/` 子目录已创建
- [x] `apps/shared/.gitkeep` 文件已创建
- [x] `apps/README.md` 文件已创建并包含：(a) 用途与定位说明、(b) 子目录结构及职责说明、(c) 新应用创建规范、(d) `.temp/` → `apps/` 迁移流程说明、(e) 与项目其他目录的关系说明
- [x] `.agents/protocols/app-development-workflow.md` 已创建，包含暂存开发、稳定迁移、清理三个阶段的完整生命周期定义
- [x] `app-development-workflow.md` 说明了与 `dependency-management.md` 的关系
- [x] `AGENTS.md` 上下文路由表已包含 "应用开发生命周期" 条目，指向 `.agents/protocols/app-development-workflow.md`
- [x] `AGENTS.md` 协作协议概要表已包含 `app-development-workflow` 条目
- [x] `apps/` 目录未被 `.gitignore` 忽略（新增文件可被 `git status` 检测到）
- [x] `docs/project-structure.md` 的目录树章节已包含 `apps/` 条目
- [x] `docs/project-structure.md` 的目录职责说明表格已包含 `apps/` 行
