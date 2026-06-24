+++
id = "retrospective-report-code-wiki-generation-project-overview"
date = "2026-06-24"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-code-wiki-generation.md#一"
+++

# 一、项目概述

## 1.1 项目背景

用户提出"分析并理解这个项目仓库，生成结构化的完整的 Code Wiki 文档(md文件)"，要求覆盖项目整体架构、主要模块职责、关键类与函数说明、依赖关系以及项目运行方式等关键信息。

该任务发生在一个文档与代码混合型仓库中。仓库主体是一套 AI 智能体开发规范体系，同时包含 `prompt_extraction/` Python 子项目。因此，Code Wiki 不能只描述代码文件，也需要同时解释规范体系、知识库、复盘体系和自动化治理脚本之间的关系。

## 1.2 项目目标

| 目标 | 说明 | 完成情况 |
|---|---|---|
| 理解项目整体结构 | 识别仓库的主要目录、入口文件与资产分层 | 已完成 |
| 分析项目整体架构 | 解释 `AGENTS.md`、`.agents/`、`docs/`、`prompt_extraction/` 的关系 | 已完成 |
| 梳理主要模块职责 | 覆盖规范体系、文档体系、Python 子项目与自动化脚本 | 已完成 |
| 说明关键类与函数 | 聚焦 `PromptRecord`、`Pipeline`、输入解析、清洗、特征提取、评估、优化、UI | 已完成 |
| 梳理依赖关系 | 覆盖 Python 依赖、模块依赖、文档资产依赖与脚本依赖 | 已完成 |
| 说明运行与验证方式 | 提供 Streamlit、pytest、治理脚本等运行命令 | 已完成 |
| 导出 Markdown 文档 | 在 `docs/code-wiki/` 生成结构化文档集 | 已完成 |
| 验证文档链接 | 对 Code Wiki 目录执行链接检查 | 已完成 |

## 1.3 交付物清单

| 文件 | 类型 | 说明 |
|---|---|---|
| `docs/code-wiki/README.md` | Code Wiki 入口 | 文档目录、阅读路径、核心结论 |
| `docs/code-wiki/project-overview.md` | 总览文档 | 项目定位、目录职责、设计原则 |
| `docs/code-wiki/architecture.md` | 架构文档 | 入口路由、规范体系、流水线、UI、验证架构 |
| `docs/code-wiki/modules.md` | 模块文档 | 顶层模块、`.agents/`、`docs/`、`prompt_extraction/`、脚本职责 |
| `docs/code-wiki/key-apis.md` | API 文档 | 数据模型、流水线、解析、清洗、提取、评分、优化、UI 关键函数 |
| `docs/code-wiki/dependencies.md` | 依赖文档 | Python 依赖、模块依赖、规范依赖、测试依赖 |
| `docs/code-wiki/runtime.md` | 运行指南 | 安装、运行、测试、验证、输入格式和导出说明 |

---

> **关联模块**：[execution-retrospective.md](execution-retrospective.md)、[insight-extraction.md](insight-extraction.md)、[export-suggestions.md](export-suggestions.md)