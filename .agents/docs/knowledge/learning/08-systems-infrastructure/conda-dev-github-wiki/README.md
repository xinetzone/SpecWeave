---
id: conda-dev-github-wiki-index
title: "conda .github 元仓库 Wiki 教程"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/README.toml"
source: "spec:create-conda-dev-github-wiki-tutorial"
category: "learning"
tags: ["conda", "github-meta-repo", "org-governance", "github-actions", "issue-template", "wiki-tutorial"]
date: "2026-08-20"
status: "stable"
author: "SpecWeave"
summary: "conda .github 组织级元仓库的系统学习教程：仓库结构、7 个工作流、4 个 Issue 模板、社区健康文件与中央同步模型"
---
# conda .github 元仓库 Wiki 教程

本教程系统学习 conda 组织的组织级元仓库 `conda/.github`（本地镜像 `external/libs/conda-dev/.github`），解析其文件夹结构、全部配置文件（7 个 GitHub Actions 工作流、4 个 Issue Form 模板、社区健康文件）与功能实现（Issue Sorting、标签体系、`conda/infrastructure` 中央同步模型），并提供常见操作指南、最佳实践与注意事项，帮助开发人员快速掌握组织级 `.github` 元仓库的搭建、使用与维护。

## 适用读者

- **开源组织维护者**：希望借鉴 conda 的"元仓库 + 中央同步"模式统一组织协作规范
- **GitHub 高级用户**：想深入理解组织级 `.github` 仓库、Issue Form、组织主页等平台能力的组合用法
- **DevOps / 平台工程人员**：关注模板同步体系与自动化工作流的规模化实践
- **对 conda 生态感兴趣的学习者**：从治理侧视角了解 conda 组织的运作方式

<!-- README_INDEX_START -->
## 📄 章节列表

| 编号 | 文件 | 章节标题 | 核心内容 |
|------|------|---------|---------|
| 00 | [00-overview.md](00-overview.md) | 教程总览与导航索引 | 教程引言、组织治理栈定位图、章节导航、目标读者与阅读路径 |
| 01 | [01-repository-structure.md](01-repository-structure.md) | 仓库整体架构 | 完整目录树、文件/目录职责、组织级 `.github` 与普通仓库 `.github/` 对比、同步体系定位 |
| 02 | [02-workflows-deep-dive.md](02-workflows-deep-dive.md) | GitHub Actions 工作流详解 | cla/issues/labels/lock/project/stale/update 七个工作流的触发/权限/步骤/配置语义 |
| 03 | [03-issue-templates.md](03-issue-templates.md) | Issue 模板详解 | 0_bug/1_feature/2_documentation/epic 四个 Issue Form 模板的字段与校验 |
| 04 | [04-community-files.md](04-community-files.md) | 社区健康文件详解 | CODE_OF_CONDUCT / HOW_WE_USE_GITHUB / profile-README / .gitignore |
| 05 | [05-infrastructure-sync-model.md](05-infrastructure-sync-model.md) | 中央同步模型 | template-files/config.yml 映射清单、conda/infrastructure 角色、update.yml+sync.yml 双通道 |
| 06 | [06-issue-sorting-labeling.md](06-issue-sorting-labeling.md) | Issue Sorting 与标签体系 | Sorting 概念、[category::topic] 标签语法、Roadmap Board 流转、自动化汇总 |
| 07 | [07-operations-guide.md](07-operations-guide.md) | 常见操作指南 | 配置修改、功能扩展、问题排查三个场景及可复制示例 |
| 08 | [08-best-practices.md](08-best-practices.md) | 最佳实践与注意事项 | 可迁移治理模式、安全最佳实践、5 个反模式与检验标准 |
| 09 | [09-resources.md](09-resources.md) | 术语表与参考资料 | 术语表、权威资料链接与按难度分级的阅读建议 |

<!-- README_INDEX_END -->

## 📖 阅读路径建议

- **快速入门**：先读 [01-repository-structure.md](01-repository-structure.md) 掌握仓库全貌，再按需跳读感兴趣的章节
- **系统学习者**：按 `00 → 01 → … → 09` 顺序通读，从结构到机制逐步深入
- **关注治理模式**：重点阅读 [05-infrastructure-sync-model.md](05-infrastructure-sync-model.md) 与 [06-issue-sorting-labeling.md](06-issue-sorting-labeling.md)，理解"定义一次、全组织生效"的设计哲学
- **关注技术实现**：重点阅读 [02-workflows-deep-dive.md](02-workflows-deep-dive.md) 与 [03-issue-templates.md](03-issue-templates.md)，研究具体的 YAML/工作流写法

## 🔗 关联文档（扩展阅读）

- [系统基础设施目录索引](../README.md)：本分类下其他技术主题 Wiki
- [📘 Git 高级命令 Wiki 教程](../git-advanced-wiki/README.md)：`git clone --no-local --bare` 等高级参数，理解元仓库 Git 操作底层行为
- [🔄 Git+百度网盘跨设备同步方案](../git-baidu-sync/README.md)：基于 git clone 高级参数的跨设备私有仓库同步实战

---

- [🏠 返回上级：系统基础设施](../README.md)
