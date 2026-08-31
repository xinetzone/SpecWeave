---
type: Wiki Tutorial

id: "codewhale-wiki-readme"
title: "CodeWhale 知识库"
source: "https://github.com/Hmbown/CodeWhale"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/codewhale-wiki/README.toml"
---
# CodeWhale 知识库

> **"潜入深海，你不必亲自下潜。"**

CodeWhale 是一个基于 Rust 构建的终端 AI 编程助手，支持 36 个 LLM 提供商路由，提供 Plan（只读）、Act（多步骤）、Operate（多任务调度）三种运行模式，以及 TUI、exec、Web、Runtime API+MCP、Fleet 五种运行时。本知识库系统地整理了 CodeWhale 的技术架构、安装使用、进阶主题等核心内容。

## 一、章节导航

| 章节 | 标题 | 内容 |
|------|------|------|
| [00-overview.md](00-overview.md) | 项目概述 | CodeWhale 定位、核心价值主张、技术栈、架构概览与差异化定位 |
| [01-quickstart.md](01-quickstart.md) | 安装与首次使用 | 多平台安装、中国用户镜像加速、宪法优先设置、首次启动流程 |
| [02-features.md](02-features.md) | 核心功能详解 | Route Resolver 模型路由、Nested Constitution 嵌套宪法、三种运行模式与 Fleet 多智能体工作流 |
| [03-deploy.md](03-deploy.md) | 安装渠道与提供商配置 | 安装渠道对比、提供商配置示例、生命周期 Hook、搜索后端、沙箱安全配置 |
| [04-changelog.md](04-changelog.md) | 版本演进记录 | 从 deepseek-tui 到 CodeWhale 的演进历程、关键版本变更与未来路线图 |
| [05-comparison.md](05-comparison.md) | 核心功能对比表 | 核心速览、竞品全面对比、运行模式矩阵、私有化部署深度对比 |
| [06-domain.md](06-domain.md) | 终端 AI 编程助手领域知识 | 终端优先交互哲学、模型无关设计理念、开源社区演进与工程化挑战 |
| [07-topics.md](07-topics.md) | 设计哲学与行业洞察 | 模型路由战略意义、硬编码安全 vs Prompt 工程、终端宣言、竞争格局 |

## 二、快速开始

如果你是新用户，建议按以下路径快速上手：

1. **了解项目** → 阅读 [项目概述](00-overview.md)，理解 CodeWhale 的定位与核心价值
2. **安装运行** → 跟随 [安装与首次使用指南](01-quickstart.md)，完成环境搭建与第一个任务
3. **深入功能** → 阅读 [核心功能详解](02-features.md)，理解模型路由、嵌套宪法等核心机制
4. **拓展阅读** → 浏览 [领域知识](06-domain.md) 与 [设计哲学](07-topics.md)，深入理解终端 AI 编程助手生态

## 三、重点阅读推荐

| 文档 | 适合人群 | 说明 |
|------|---------|------|
| [项目概述](00-overview.md) | 所有用户 | 理解定位与核心价值 |
| [安装与首次使用指南](01-quickstart.md) | 新用户 | 完成环境搭建 |
| [核心功能详解](02-features.md) | 开发者 | 理解模型路由与嵌套宪法 |
| [安装渠道与提供商配置](03-deploy.md) | 运维/配置者 | 完成提供商配置 |
| [终端AI编程助手领域知识](06-domain.md) | 架构师 | 深入理解设计理念 |
| [设计哲学与行业洞察](07-topics.md) | 研究者 | 理解行业格局与趋势 |