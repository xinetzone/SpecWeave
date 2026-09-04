---
id: okf-ecosystem-infrastructure-learning
title: OKF 生态基建系统学习与知识补充 - 产品需求文档
type: Spec
timestamp: 2026-08-06
updated: 2026-08-06
author: AI Assistant
status: proposed
---

# OKF 生态基建系统学习与知识补充 Spec

## Why

现有 okf-wiki 已覆盖 OKF v0.2 规范通用教程（8篇）、官方工具链（knowledge-catalog-wiki）、中文生态项目深度分析（awesome-okf-analysis）。但 OKF 的**生态基建层**——上游生态资源图谱、bundle 分发与注册机制、工程化 bundle 发布模板——尚未形成系统知识沉淀。本次任务系统学习四个 OKF 相关文件夹，将 "如何消费、如何发布、如何工程化管理 OKF bundle" 的完整基建知识补充进 okf-wiki，填补生态基建知识空白，便于后续查阅与复用。

## What Changes

- **新增** okf-wiki 子目录 `okf-ecosystem-wiki/`，承载 OKF 生态基建系统知识（含 README 导航 + 若干主题文档）
- **内容来源**：四个文件夹的深度分析（R阶段已完成）：
  - `d:\AI\.chaos\libs\awesome-okf`（上游英文版）→ 生态资源图谱 + "awesome 列表批转合规范 bundle" 的 dogfooding 工程实现
  - `d:\AI\.chaos\libs\awesome-okf-kit` → bundle 分发注册机制（registry.yaml 机器可读索引 + 消费流程）
  - `d:\AI\.chaos\libs\okf-bundle-template` → bundle 工程化发布模板（CI 自动化构建/同步/发布工作流）
  - `d:\AI\vendor\awesome-okf`（中文版）→ 已有 awesome-okf-analysis 覆盖，本次仅做交叉引用，不重复
- **更新** okf-wiki/README.md 文档索引表、07-resources-and-glossary.md 交叉引用表格，添加生态基建知识入口
- **建立双向链接**：okf-ecosystem-wiki 与 okf-wiki 通用教程、awesome-okf-analysis 案例研究互链

## Impact

- **Affected specs**: okf-wiki（`01-agent-protocols-interfaces/okf-wiki/`）知识体系
- **Affected code**: 无源代码变更；仅新增知识文档 + 更新 okf-wiki 索引/交叉引用
- **不修改**: `.chaos/libs/` 与 `vendor/awesome-okf` 下的任何源文件（只读分析）

## ADDED Requirements

### Requirement: 系统学习四个 OKF 相关文件夹
系统 SHALL 深度分析四个文件夹的核心功能、实现原理、API/接口及使用方法：
- _awesome-okf_：生态资源分类图谱（官方工具/参考实现/示例bundle/社区工具/相关格式/LLM-wiki模式）、`scripts/build-okf-bundle.mjs` 批转实现原理与 OKF v0.2 frontmatter 生成规则
- _awesome-okf-kit_：`registry.yaml` 字段 Schema（name/source_url/description/license/download/category/publisher/repo/okf_version/pages/tags）、`okf get` 消费流程、`scripts/validate_registry.py` 校验规则
- _okf-bundle-template_：`build.yml`（手动触发构建+release）与 `sync.yml`（每周同步+重打包）两个 GitHub Actions 工作流、`okf build/sync/zip/chat/visualize` 命令
- _vendor/awesome-okf_：中文版插件/Skill/提案，交叉引用已有 awesome-okf-analysis

#### Scenario: 学习覆盖完整性
- **WHEN** 四个文件夹均被深度阅读
- **THEN** 每个文件夹的核心功能、实现原理、API接口、使用方法均被准确记录并有文件路径/命令证据支撑

### Requirement: 生成 OKF 生态基建知识文档
系统 SHALL 在 `okf-wiki/okf-ecosystem-wiki/` 下生成结构化知识文档，遵循 okf-wiki 现有 frontmatter 风格（YAML + 相对路径 + kebab-case 命名）：
- README.md：生态基建导航总览
- 主题文档覆盖：生态资源图谱、bundle 分发注册机制、bundle 工程化模板、okf-kit CLI 命令速查

#### Scenario: 知识文档可用性
- **WHEN** 用户查阅 okf-ecosystem-wiki
- **THEN** 能快速理解 OKF 生态的消费/发布/工程化全链路，且命令与路径可直接复用

### Requirement: 建立 okf-wiki 双向链接
系统 SHALL 更新 okf-wiki/README.md 与 07-resources-and-glossary.md，添加生态基建知识入口，并建立 okf-ecosystem-wiki ↔ okf-wiki 通用教程/awesome-okf-analysis 的双向链接。

#### Scenario: 链接可达性
- **WHEN** 运行链接检查脚本
- **THEN** 所有新增链接可达，无断链

## MODIFIED Requirements

（无——本任务为纯新增知识补充，不修改既有 OKF 规范内容）

## REMOVED Requirements

（无）