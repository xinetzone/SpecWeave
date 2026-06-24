+++
id = "retrospective-report-cofounder-role-marker-project-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-cofounder-role-marker.md#一"
+++

# 一、项目概述

## 1.1 项目背景

项目 `.agents/roles` 角色管理模块中现有五个角色（orchestrator、architect、developer、reviewer、tester）采用同质化呈现，无法区分项目初创阶段的"联合创始"角色与普通角色。需要为联合创始角色引入特殊标记机制，在角色数据模型、索引清单与详情页面中保持一致的高辨识度视觉呈现，并通过权限声明约束其查看与管理范围。

## 1.2 项目目标

- 在角色数据模型（TOML frontmatter）中新增 `tier` 标识字段与 `[permissions]` 权限表
- 新增联合创始角色定义文件 `co-founder.md`
- 在 `README.md` 角色职责矩阵中新增"层级标记"列与视觉徽章（🏛️）
- 在角色详情文件标题中应用统一文字前缀 `[联合创始] 🏛️`
- 在 `README.md` 中补充权限控制说明章节
- 同步 `AGENTS.md` 角色定义索引表

## 1.3 交付物清单

| 类别 | 文件 | 说明 |
|------|------|------|
| 规格文档 | `.trae/specs/add-cofounder-role-marker/spec.md` | 任务规格说明 |
| 任务清单 | `.trae/specs/add-cofounder-role-marker/tasks.md` | 主任务 5 项 + 子任务 12 项 |
| 检查清单 | `.trae/specs/add-cofounder-role-marker/checklist.md` | 验证检查项 16 项 |
| 角色文件 | `.agents/roles/co-founder.md` | 新建联合创始角色定义 |
| 索引更新 | `.agents/roles/README.md` | 新增层级标记列、联合创始行、权限控制章节 |
| 全局契约 | `AGENTS.md` | 角色定义索引表追加联合创始角色行 |
| 复盘报告 | `docs/retrospective/reports/retrospective-report-cofounder-role-marker.md` | 本报告 |
| **合计** | **7 个文件** | 3 新建 + 4 修改 |

---