---
okf_version: "0.2"
title: "Jira Skill 教程"
description: "基于源码 v3.29.0 的 jira-skill 系统性技术教程，涵盖双技能架构、CLI 使用、JQL 查询、最佳实践与故障排查。"
tags: ["jira", "claude-code", "agent-skill", "cli", "tutorial"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
---

# Jira Skill 教程

本知识包是对 [jira-skill](https://github.com/netresearch/jira-skill) v3.29.0 的系统性技术教程，以源码为权威事实来源，按 OKF v0.2 规范组织。

jira-skill 是一个面向 Claude Code 的开源插件，通过两个专业化技能为 AI 智能体提供完整的 Jira 集成能力：

- **jira-communication**：通过 Python CLI 脚本执行 Jira API 操作（搜索、创建、流转、评论、工时等）
- **jira-syntax**：提供 Jira wiki markup 语法参考、模板和提交前校验

## 快速开始

1. [安装与配置](/concepts/02-installation.md) — 完成环境准备
2. [快速开始](/concepts/03-quickstart.md) — 上手常用命令
3. [基础 CLI 使用示例](/examples/basic-cli-usage.md) — 实操演练

## 概念文档

### 入门篇

| 文档 | 内容 |
|------|------|
| [教程总览](/concepts/00-overview.md) | 插件定位、核心特性、版本演进与章节导航 |
| [架构设计](/concepts/01-architecture.md) | 双技能架构、三层脚本体系、数据流与设计决策 |
| [安装与配置](/concepts/02-installation.md) | 六种安装方式、凭证配置、Cloud/Server 认证差异 |

### 核心篇

| 文档 | 内容 |
|------|------|
| [快速开始](/concepts/03-quickstart.md) | 搜索、创建、流转、评论、工时等命令速查 |
| [jira-communication 技能](/concepts/04-jira-communication.md) | API 操作技能详解、意图动词机制、三层脚本 |
| [jira-syntax 技能](/concepts/05-jira-syntax.md) | Wiki markup 语法、模板、提交前校验 |
| [JQL 查询语言](/concepts/06-jql.md) | 操作符、函数、常见查询与 Cloud/DC 差异 |

### 高级篇

| 文档 | 内容 |
|------|------|
| [最佳实践与反模式](/concepts/07-best-practices.md) | 意图动词优先、dry-run、安全实践 |
| [故障排查](/concepts/08-troubleshooting.md) | 认证、依赖、字段设置等常见问题 |
| [术语表与资源](/concepts/09-glossary.md) | 核心术语解释与参考资料 |

## 示例文档

| 文档 | 内容 |
|------|------|
| [基础 CLI 使用示例](/examples/basic-cli-usage.md) | 搜索、获取、创建、评论、工时、附件 |
| [工作流自动化示例](/examples/workflow-automation.md) | 意图动词、多步转换、QA 聚合、版本管理 |
| [语法模板示例](/examples/syntax-templates.md) | Bug/特性模板填充、验证和提交 |

## 参考信源

| 文档 | 内容 |
|------|------|
| [源码结构](/references/source-code.md) | 目录结构、模块划分、版本信息 |
| [CLI API 参考](/references/api-reference.md) | 所有脚本的子命令、选项和参数 |
| [官方文档](/references/official-docs.md) | Jira REST API、Agent Skills 标准、Wiki Markup |

## 变更日志

详见 [log.md](/log.md)。
