---
version: "1.0"
---

# GitHub CLI Wiki 教程 Spec

## Why

GitHub CLI（`gh`）是 GitHub 官方提供的命令行工具，让开发者无需离开终端即可完成 Issues、Pull Requests、Actions、Releases、Gists 等全流程 GitHub 操作。当前项目知识库缺少对 `gh` 的系统性教程，而 `gh` 是 AI 辅助开发工作流中不可或缺的工具——从 Spec 驱动的开发流程（issue 创建、PR 管理）到 CI/CD 触发（Actions 调用），`gh` 贯穿整个开发生命周期。

本教程旨在系统学习 [GitHub CLI 中文手册](https://cli.githubdocs.cn/manual/)、[GitHub CLI 官方文档](https://cli.github.com/) 和 [GitHub CLI 源码](https://github.com/cli/cli) 三个权威来源，萃取出结构清晰、内容详实的 wiki 教程，填补知识库在这一领域的空白。

## What Changes

- **新增** 8 个原子化 Markdown 文档，构成完整的 GitHub CLI wiki 教程，放置于 `docs/knowledge/learning/github-cli-wiki/` 目录
- **新增** 教程总览与导航索引（`00-overview.md`）
- **新增** 安装与配置指南（`01-installation.md`），覆盖 Windows/macOS/Linux 三平台安装、认证配置、Shell 补全
- **新增** 基础命令全览（`02-basic-commands.md`），覆盖 repo/clone/fork、issue/pr 创建与管理、gist 操作
- **新增** Pull Request 工作流（`03-pr-workflow.md`），覆盖 PR 创建、审查、checkout、merge、status 全流程
- **新增** Actions 与 CI/CD（`04-actions-cicd.md`），覆盖 workflow 查看/触发/重跑、run/log 管理、secret 变量
- **新增** 高级用法与扩展（`05-advanced-usage.md`），覆盖 API 调用、别名（alias）、配置管理、扩展（extensions）、JSON 格式化输出
- **新增** 常见问题与故障排查（`06-faq-troubleshooting.md`），覆盖认证问题、权限错误、网络代理、版本升级等
- **新增** 命令速查表与最佳实践（`07-cheatsheet.md`），覆盖常用命令速查 + 工作流最佳实践建议
- **不修改** 任何现有文档

## Impact

- **Affected specs**: 无（独立新增 wiki 教程）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/learning/github-cli-wiki/00-overview.md` ~ `07-cheatsheet.md` 共 8 个文件
- **Related wikis**: 无直接关联现有 wiki（独立知识领域）

## Background & Context

GitHub CLI（`gh`）由 GitHub 官方维护，使用 Go 语言编写，于 2020 年 1 月发布 1.0 版本。截至 2026 年，已覆盖 GitHub 平台几乎所有核心功能：

- **仓库管理**：`gh repo`（clone/create/fork/view/list）
- **Issues**：`gh issue`（create/list/view/status/close/reopen/comment）
- **Pull Requests**：`gh pr`（create/list/view/checkout/merge/review/diff/status）
- **Actions**：`gh run`（list/view/watch/rerun/download）、`gh workflow`（list/view/enable/disable/run）
- **Releases**：`gh release`（create/list/view/download/upload/delete）
- **Gists**：`gh gist`（create/list/view/edit/delete）
- **扩展生态**：`gh extension`（install/list/remove/search/create）
- **API 能力**：`gh api`（直接调用 GitHub REST/GraphQL API）
- **认证与配置**：`gh auth`（login/logout/status/token）、`gh config`

本教程采用原子化文档结构，每个文件聚焦单一主题，遵循项目已有的 wiki 规范（参考 `interface-api-abi-protocol-wiki` 和 `ffi-wiki` 的文件组织、YAML frontmatter、导航链接模式）。

## ADDED Requirements

### Requirement: GitHub CLI Wiki 教程目录与总览

The system SHALL provide a `00-overview.md` file at `docs/knowledge/learning/github-cli-wiki/` containing a complete tutorial overview with reading guide, chapter navigation table, and Mermaid concept hierarchy diagram.

#### Scenario: 用户访问 GitHub CLI wiki 入口

- **WHEN** 用户打开 `docs/knowledge/learning/github-cli-wiki/00-overview.md`
- **THEN** 文档包含：教程简介、8 章导航表、GitHub CLI 功能架构图（Mermaid）、目标读者说明、阅读路径建议、与 SpecWeave 开发工作流的关联指引

### Requirement: 安装与配置指南

The system SHALL provide a `01-installation.md` file covering installation on Windows/macOS/Linux, authentication setup (`gh auth login`), shell completion, and configuration management.

#### Scenario: 用户在任意平台完成 gh 安装与认证

- **WHEN** 用户按文档操作
- **THEN** 文档包含：Windows（winget/scoop/msi）、macOS（brew）、Linux（apt/yum/dnf/pacman）安装命令、HTTPS/SSH 认证选择指南、`gh auth status` 验证方法、Shell 补全配置（bash/zsh/fish/powershell）、`gh config` 配置管理

### Requirement: 基础命令全览

The system SHALL provide a `02-basic-commands.md` file covering repo management, issue creation/management, and gist operations.

#### Scenario: 用户掌握 gh 核心日常命令

- **WHEN** 用户按文档学习
- **THEN** 文档包含：`gh repo`（clone/create/fork/view/list）、`gh issue`（create/list/view/status/comment）、`gh gist`（create/list/view/edit/delete）的完整参数说明、使用示例和常见场景

### Requirement: Pull Request 工作流

The system SHALL provide a `03-pr-workflow.md` file covering the complete PR lifecycle from creation to merge.

#### Scenario: 用户完成 PR 全流程操作

- **WHEN** 用户按文档学习 PR 工作流
- **THEN** 文档包含：`gh pr create`（含 --web/--fill/--draft 等选项）、`gh pr checkout`、`gh pr review`（approve/comment/request-changes）、`gh pr merge`（--squash/--rebase/--merge）、`gh pr status`、`gh pr checks`、`gh pr diff`、`gh pr view` 的完整工作流示例

### Requirement: Actions 与 CI/CD

The system SHALL provide a `04-actions-cicd.md` file covering GitHub Actions management via gh CLI.

#### Scenario: 用户通过 gh 管理 CI/CD 工作流

- **WHEN** 用户按文档操作
- **THEN** 文档包含：`gh workflow list/view/enable/disable/run`、`gh run list/view/watch/rerun/download`、`gh secret`（list/set/remove）、`gh variable`（list/set/remove）的完整说明与使用场景

### Requirement: 高级用法与扩展

The system SHALL provide a `05-advanced-usage.md` file covering advanced features including API calls, aliases, extensions, and JSON output formatting.

#### Scenario: 用户掌握 gh 高级功能

- **WHEN** 用户按文档学习
- **THEN** 文档包含：`gh api`（REST/GraphQL 调用 + `--paginate`/`--jq`/`--template` 等选项）、`gh alias`（创建/列出/删除别名）、`gh extension`（浏览/安装/管理扩展）、`gh search`（搜索仓库/issue/PR）、`--json` 输出与 `jq` 组合使用的完整示例

### Requirement: 常见问题与故障排查

The system SHALL provide a `06-faq-troubleshooting.md` file covering common issues, error scenarios, and troubleshooting steps.

#### Scenario: 用户遇到问题能自行排查

- **WHEN** 用户查阅 FAQ 文档
- **THEN** 文档包含：认证失败（token 过期/权限不足）、网络代理配置（HTTP_PROXY/HTTPS_PROXY）、版本升级（`gh upgrade`）、SSH 密钥问题、API 限流处理、`gh auth refresh` 等不少于 10 个常见问题及解决方案

### Requirement: 命令速查表与最佳实践

The system SHALL provide a `07-cheatsheet.md` file containing a quick-reference command table and workflow best practices.

#### Scenario: 用户快速查找命令

- **WHEN** 用户需要速查命令
- **THEN** 文档包含：按功能分类的命令速查表（仓库/Issue/PR/Actions/Release/Gist/API/Auth/Config/Extension/Secret）、SpecWeave 开发工作流最佳实践（Spec 驱动开发中的 gh 使用模式）、原子化提交工作流中的 gh 集成示例

## Data Sources

学习材料来源：

1. [GitHub CLI 中文手册](https://cli.githubdocs.cn/manual/) — 中文版命令参考，覆盖所有子命令的参数说明
2. [GitHub CLI 官方文档](https://cli.github.com/) — 英文版官方文档，含安装指南、快速入门、最佳实践
3. [GitHub CLI 源码仓库](https://github.com/cli/cli) — Go 源码，了解实现细节、扩展机制、贡献指南

<!-- changelog -->
<!--
- 2026-07-24 | initial | 初始版本，定义 8 个原子化文档的完整 Requirements
-->