+++
id = "retrospective-report-create-apps-directory-project-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-create-apps-directory.md#一"
+++

# 一、项目概述

## 1.1 项目背景

项目现有的顶级目录（`.agents/`、`docs/`、`prompt_extraction/`、`vendor/`、`.temp/`）各有其专有用途，缺乏一个专门用于开发新应用的独立工作空间。用户要求规划并创建 `apps/` 目录，确保其符合项目既有目录结构规范，具备清晰的层级划分，并为后续新应用开发提供必要的基础环境支持。

用户在第一版规格反馈中提出两项关键补充：(1) `.agents/` 也需要添加对 `apps/` 的管理规范；(2) 新应用须先在 `.temp/` 暂存区开发，再逐步迁移至 `apps/`。

## 1.2 项目目标

1. 在项目根目录下创建 `apps/` 目录作为新应用开发专用工作空间
2. 建立 `apps/shared/` 共享模块子目录
3. 编写 `apps/README.md` 说明使用规范与迁移流程
4. 在 `.agents/protocols/` 下创建 `app-development-workflow.md` 生命周期协议
5. 更新 `AGENTS.md` 上下文路由表与协作协议概要
6. 更新 `docs/project-structure.md` 目录树与职责表格
7. 确保 `apps/` 未被 `.gitignore` 忽略，可纳入版本控制

## 1.3 交付物清单

| 类别 | 文件 | 说明 |
|---|---|---|
| 新增 | `apps/` | 应用开发工作空间根目录 |
| 新增 | `apps/shared/.gitkeep` | 保证空目录被 Git 追踪 |
| 新增 | `apps/README.md` | 目录使用说明（5 节完整内容） |
| 新增 | `.agents/protocols/app-development-workflow.md` | 应用开发生命周期规范（含 Mermaid 状态图 + 流程图） |
| 修改 | `AGENTS.md` | 协作协议概要 + 上下文路由表各新增 1 行 |
| 修改 | `docs/project-structure.md` | 目录树 + 职责说明表格各新增 1 条目 |

**统计**：新增 4 个文件（含目录），修改 2 个文件，共计 6 个文件变更。

---