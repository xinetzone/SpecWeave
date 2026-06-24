+++
id = "retrospective-report-agents-spec-system-project-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-agents-spec-system.md#一"
+++

# 一、项目概述

## 1.1 项目背景

在 AI 辅助开发日益普及的背景下，多智能体协作已成为提升开发效率的重要手段。然而，缺乏统一的角色定义、协作协议与开发规范，将导致智能体间职责不清、交接混乱、输出质量参差不齐等问题。本项目旨在建立一套自包含的智能体协作开发体系，使 AI 智能体能够在明确的规则框架下高效协作，确保代码质量、沟通效率与项目可维护性。

## 1.2 项目目标

本项目的核心目标包括以下五个方面：

1. **创建全局契约文件**（`AGENTS.md`）：作为所有智能体的最高优先级入口，定义全局核心规则、角色索引、能力边界声明、协作协议概要及上下文路由表。
2. **建立** **`.agents/`** **配置目录**：作为智能体规范的容器，承载角色定义、系统提示词、工具调用规范、协作协议、标准工作流与模板资产。
3. **纳入 Git 版本控制**：配置 `.gitignore` 规则、建立 pre-commit hook 自动化检查机制，确保临时依赖与中间产物不被意外提交。
4. **目录重命名**：将 `libs/` 重命名为 `vendor/`，统一第三方依赖管理命名约定。
5. **完善临时依赖管理**：制定临时依赖管理流程文档、团队规范、Git hooks 与验证脚本，形成完整的依赖管理闭环。

## 1.3 交付物清单

| 类别        | 交付物                                  | 数量     | 说明                                                                                 |
| --------- | ------------------------------------ | ------ | ---------------------------------------------------------------------------------- |
| 全局契约      | `AGENTS.md`                          | 1      | 项目根目录，智能体最高优先级入口                                                                   |
| 目录说明      | `.agents/README.md`                  | 1      | `.agents/` 目录骨架说明                                                                  |
| 角色定义      | `.agents/roles/*.md`                 | 6      | 5 个核心角色定义 + 1 个 README                                                             |
| 系统提示词     | `.agents/prompts/{role}/*.md`        | 11     | 5 角色 × 2 文件（system-prompt + few-shot） + 1 个 README                                 |
| 工具规范      | `.agents/tools/*.md`                 | 5      | 4 类工具规范 + 1 个 README                                                               |
| 协作协议      | `.agents/protocols/*.md`             | 5      | 4 个协议 + 1 个 README                                                                 |
| 标准工作流     | `.agents/workflows/*.md`             | 4      | 3 个工作流 + 1 个 README                                                                |
| 模板资产      | `.agents/templates/*.md`             | 3      | 2 个模板 + 1 个 README                                                                 |
| 自动化脚本     | `.agents/scripts/check-gitignore.py` | 1      | Git 忽略规则验证脚本                                                                       |
| Git 配置    | `.gitignore`                         | 1      | 项目根目录，10 类忽略规则                                                                     |
| Git Hooks | `.git/hooks/pre-commit`              | 1      | 提交前自动检查脚本                                                                          |
| **合计**    | <br />                               | **39** | 35 个 `.md` 文件 + 1 个 `.gitignore` + 1 个 pre-commit hook + 1 个验证脚本 + 1 个 `AGENTS.md` |

---

> **关联模块**：[execution-retrospective.md](execution-retrospective.md)、[insight-extraction.md](insight-extraction.md)、[export-suggestions.md](export-suggestions.md)