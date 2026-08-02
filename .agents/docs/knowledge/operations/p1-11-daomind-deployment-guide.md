---
id: p1-11-daomind-deployment-guide
title: DaoMind 部署上线指南摘要
source: d:\spaces\chaos\daoApps\DaoMind\DEPLOYMENT-GUIDE.md
source_type: file
category: operations
tags:
  - daomind
  - deployment
  - github-pages
  - npm-publish
  - ci-cd
  - workspace-operations
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:50:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 DaoMind/DEPLOYMENT-GUIDE.md、正文为部署操作摘要、元数据与 operations 分类映射核对通过
summary: DaoMind 部署上线操作手册，覆盖 GitHub Pages 文档站部署、create-daomind CLI 的 npm 发布、部署验证、上线后监控与常见排错速查。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-11-daomind-deployment-guide.md
archived_at: 2026-08-02T03:24:58Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:24:58Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p1-11-daomind-deployment-guide.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-11-daomind-deployment-guide.md
---

# DaoMind 部署上线指南摘要

## 来源

- 源文件：[DaoMind/DEPLOYMENT-GUIDE.md](file:///d:/spaces/chaos/daoApps/DaoMind/DEPLOYMENT-GUIDE.md)
- 项目概览：[p1-09-daomind-project-overview.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/tech/p1-09-daomind-project-overview.md)
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

### 前置条件

- 代码：CLI 工具（create-daomind）、VitePress 文档站、GitHub Actions 工作流均已就绪并提交
- 账户：GitHub 仓库管理员权限 + npm 账户

### 路径一：文档站点部署到 GitHub Pages

1. 在仓库 Settings → Pages → Source 选择 **GitHub Actions**
2. 触发方式：push `enter-main` 分支、修改 `docs/site/**`，或 Actions 页面手动 Run workflow
3. 验证：等待绿色 ✅（约 2-3 分钟），访问 `https://xinetzone.github.io/DaoMind/`

### 路径二：发布 CLI 工具到 npm

1. `npm login` 并验证 `npm whoami`
2. 发布前测试：`pnpm build`、`pnpm pack --dry-run`（确认含 `dist/` 与 4 个 `templates/`）
3. 发布：`cd packages/create-daomind && pnpm publish --access public`（scoped 包需 `--access public`；首次建议 `2.0.0-beta.1`）
4. 验证：`npm view create-daomind`，再 `pnpm create daomind my-new-project`
5. 发布后：添加 npm badge、更新文档、打 tag `create-daomind-v2.0.0`

### 验证清单（部署后）

- 文档站：首页/Logo/导航/搜索/深浅色切换/移动端响应式/代码高亮
- CLI：`pnpm create daomind`、`npm create daomind@latest`、`yarn create daomind` 均能交互创建

### 常见排错速查

| 现象 | 处理 |
|---|---|
| Actions 页面无工作流 | Settings → Actions 允许 all actions |
| 构建失败找不到 vitepress | 检查 pnpm 版本与依赖安装 |
| GitHub Pages 404 | 首次部署等待 5-10 分钟；确认 base URL（非根域名需 `base: '/DaoMind/'`） |
| npm 发布失败需登录 | 运行 `npm login` 输入凭据 |
| npm 发布失败包名已存在 | 更改包名或改用 scoped package |
| CLI 创建项目失败 | 检查模板目录是否在发布包中（`npm pack --dry-run`） |

## 动作边界

本轮为 P1 运维条目。正式归档时以部署前置条件、两条发布路径、验证清单与排错速查为核心正文，不搬运手册中的推广文案与社交模板。
