# Tasks: GitHub CLI Wiki 教程

> 按七概念方法论 R→I→E→C 链路组织；每个任务对应一次原子提交。

## Phase 1: R（复盘）— 学习与事实采集

- [x] Task 1: 学习 GitHub CLI 中文手册（cli.githubdocs.cn/manual/）
  - [x] 1.1 浏览全部命令分类，记录命令概览结构
  - [x] 1.2 重点学习 `gh auth`、`gh repo`、`gh issue`、`gh pr` 命令的参数与用法
  - [x] 1.3 学习 `gh run`、`gh workflow`、`gh api`、`gh extension` 等高级命令
  - [x] 1.4 提取中文手册中的安装说明、常见问题等实用信息

- [x] Task 2: 学习 GitHub CLI 官方英文文档（cli.github.com/）
  - [x] 2.1 学习安装指南（各平台安装方法）
  - [x] 2.2 学习快速入门（Quickstart）和最佳实践
  - [x] 2.3 学习 Manual 中所有命令的官方参数说明
  - [x] 2.4 提取官方文档中的使用技巧和注意事项

- [x] Task 3: 学习 GitHub CLI 源码仓库（github.com/cli/cli）
  - [x] 3.1 了解项目结构、扩展机制设计
  - [x] 3.2 学习 `gh extension` 的创建方式
  - [x] 3.3 了解认证机制（OAuth/Token）的底层实现

## Phase 2: I（洞察）— 知识组织与结构设计

- [x] Task 4: 整理学习笔记，设计教程结构
  - [x] 4.1 整理三来源的学习笔记，提取共性知识点
  - [x] 4.2 设计 8 章节原子化文档结构，定义每章核心内容
  - [x] 4.3 确定章节间的交叉引用关系

## Phase 3: E（萃取）— 编写 Wiki 教程

- [x] Task 5: 编写 00-overview.md（教程总览与导航）
  - [x] 5.1 教程简介与目标读者
  - [x] 5.2 8 章导航表
  - [x] 5.3 Mermaid 功能架构图
  - [x] 5.4 阅读路径建议

- [x] Task 6: 编写 01-installation.md（安装与配置指南）
  - [x] 6.1 Windows/macOS/Linux 安装命令
  - [x] 6.2 `gh auth login` 认证流程（HTTPS/SSH）
  - [x] 6.3 Shell 补全配置
  - [x] 6.4 `gh config` 配置管理

- [x] Task 7: 编写 02-basic-commands.md（基础命令全览）
  - [x] 7.1 `gh repo` 仓库管理
  - [x] 7.2 `gh issue` Issue 管理
  - [x] 7.3 `gh gist` Gist 操作

- [x] Task 8: 编写 03-pr-workflow.md（Pull Request 工作流）
  - [x] 8.1 PR 创建（create/web/fill/draft）
  - [x] 8.2 PR 审查（review/approve/comment）
  - [x] 8.3 PR 合并（merge/squash/rebase）
  - [x] 8.4 PR 状态管理（status/checks/diff/view）

- [x] Task 9: 编写 04-actions-cicd.md（Actions 与 CI/CD）
  - [x] 9.1 Workflow 管理（list/view/enable/disable/run）
  - [x] 9.2 Run 管理（list/view/watch/rerun/download）
  - [x] 9.3 Secret 和 Variable 管理

- [x] Task 10: 编写 05-advanced-usage.md（高级用法与扩展）
  - [x] 10.1 `gh api` REST/GraphQL 调用
  - [x] 10.2 `gh alias` 别名管理
  - [x] 10.3 `gh extension` 扩展生态
  - [x] 10.4 `gh search` 搜索功能
  - [x] 10.5 `--json` + `jq` 格式化输出

- [x] Task 11: 编写 06-faq-troubleshooting.md（常见问题与故障排查）
  - [x] 11.1 认证相关问题（token 过期/权限不足）
  - [x] 11.2 网络代理配置
  - [x] 11.3 版本升级
  - [x] 11.4 不少于 10 个常见问题及解决方案

- [x] Task 12: 编写 07-cheatsheet.md（命令速查表与最佳实践）
  - [x] 12.1 按功能分类的命令速查表
  - [x] 12.2 SpecWeave 工作流集成最佳实践
  - [x] 12.3 原子化提交工作流集成示例

## Phase 4: C（原子提交）— 交付

- [x] Task 13: 原子化提交所有文档
  - [x] 13.1 每个 Task（5-12）独立提交，提交信息遵循 Conventional Commits 规范
  - [x] 13.2 每个提交仅包含单一文档文件，确保提交历史清晰可追溯

# Task Dependencies

- Task 4 依赖 Task 1-3（学习完成后才能设计结构）
- Task 5-12 依赖 Task 4（结构设计完成后才能编写）
- Task 5-12 之间无强依赖，可并行编写
- Task 13 依赖 Task 5-12（所有文档编写完成后才能提交）