---
id: create-okf-kit-wiki-tutorial-spec
title: "okf-kit 完整 Wiki 教程 — 规格说明"
date: "2026-08-18"
category: "standards-tools"
tags: ["okf-kit", "wiki", "tutorial", "okf", "knowledge-bundle", "agent", "llm", "rag"]
---

# okf-kit 完整 Wiki 教程 — 规格说明

## 1. 问题陈述

okf-kit 是一个将任意网站转换为可移植的、AI Agent 可直接读取的 OKF（Open Knowledge Format）知识包的 Python 工具。它支持网站爬取、增量同步、LLM 对话、MCP 服务、本地 HTTP API 等功能，且核心爬取路径无需 API Key 即可运行。当前项目仅有 README.md 作为文档，缺乏系统性的中文教程，导致：

- 新用户需要阅读源码才能理解完整功能
- 核心架构设计（BFS 爬取、URL 映射、目录索引、Agent 导航）缺乏中文讲解
- 命令行参数、配置选项、扩展功能没有系统的参考文档
- 与 Agent/LLM 生态的集成方式（MCP、Chat、Serve）缺乏实践指南

## 2. 目标用户

| 角色 | 典型需求 |
|------|---------|
| **AI 应用开发者** | 将文档网站转换为 Agent 可用的知识库，构建本地 RAG 系统 |
| **Claude Code / Cursor 用户** | 通过 MCP 让编程助手读取最新文档 |
| **Python 工具开发者** | 学习 okf-kit 的架构设计，扩展或二次开发 |
| **知识工程实践者** | 理解 OKF 格式规范，构建可移植知识包 |
| **离线/私有部署用户** | 零 API Key 构建本地知识库，使用 Ollama 离线对话 |

## 3. 目标

- 基于 okf-kit v0.3.3 源码和官方文档，系统性学习项目架构与功能
- 使用七概念方法论（R→I→E 知识沉淀链路）生成结构化中文 wiki 教程
- 产出原子化的 wiki 章节文档，每个章节聚焦单一主题
- 覆盖从安装、核心命令、架构设计到高级集成的完整知识体系

## 4. 非目标

- 不修改 okf-kit 源码（该目录为第三方库，位于 `.chaos/libs/`）
- 不将教程提交到 okf-kit 上游仓库
- 不构建可执行的 okf-kit 扩展或插件
- 不重复翻译 README.md 已有内容，而是进行深度扩展和结构化重组

## 5. 功能需求

### FR1: 教程结构完整性
- 采用编号原子化章节结构（00-overview, 01-installation, ...）
- 每个章节为独立 Markdown 文件，包含 YAML frontmatter
- 章节之间有清晰的导航链接（上一章/下一章/返回目录）
- 提供阅读路径建议（初学者/CI集成/Agent开发者）

### FR2: 内容覆盖完整性
教程必须覆盖以下核心主题：
1. **概述与背景**：OKF 格式、okf-kit 定位、核心特性、与其他方案对比
2. **安装与配置**：pip/uv 安装、可选依赖（chat/js/mcp/serve/enrich）、虚拟环境建议
3. **CLI 命令参考**：build/sync/validate/zip/list/get/chat/visualize/serve-mcp/serve 全部命令
4. **OKF 格式规范**：Bundle 目录结构、frontmatter 字段、index.md 导航机制、state.json
5. **核心架构**：BFS 爬取器、URL→路径映射、Fetcher 抽象（HttpFetcher/BrowserFetcher）、Writer 流程
6. **增量同步机制**：content hash 比对、delta 更新、安全阈值、post_sync 钩子
7. **Chat 对话系统**：Agent 导航循环、Provider 抽象（OpenAI/Ollama/Anthropic）、零 Key 检索回退
8. **MCP 服务**：stdio MCP 协议、工具暴露（list_bundles/list_directory/read_concept/search_bundle）
9. **本地 HTTP API**：FastAPI 服务、端点说明、GUI 集成方式
10. **Registry 机制**：bundle 发布与发现、awesome-okf-kit 注册表
11. **可视化与图谱**：graph.html 生成、内部链接边计算
12. **扩展与开发**：源码结构、测试、自定义 Fetcher、calknowledge 生态
13. **FAQ 与排错**：常见问题、JS 渲染站点处理、robots.txt、连接问题
14. **总结与资源**：术语表、速查表、生态链接

### FR3: 代码示例与实践
- 每个命令提供实际可运行的示例
- 关键架构部分配 Mermaid 图表
- 包含典型使用场景的端到端示例
- 提供常见错误的诊断与解决步骤

### FR4: 术语表与可访问性
- 首次出现的专业术语提供一句话解释
- 开头提供 ≥15 个核心术语的术语表
- 避免循环定义（用专业术语解释专业术语）

## 6. 非功能需求

### NFR1: 文档质量
- 所有内容基于源码分析，不臆测功能
- 命令参数、配置项、路径与实际代码一致
- 中文表达规范，使用标准书面语
- 代码示例可直接复制运行

### NFR2: 格式一致性
- 遵循现有 wiki 教程的格式规范（参考 open-code-review-wiki）
- YAML frontmatter 包含 id/title/source/date/category/tags 字段
- 使用 kebab-case 英文文件名
- Mermaid 图表遵循安全编码规范

### NFR3: 方法论合规
- 严格遵循七概念方法论的知识沉淀链路（R→I→E）
- 通过 G1（事实无因果词）、G2（洞察四元组完整）、G3（模式可迁移）质量门
- 产出物包含方法论执行记录（seven-concepts-report.md）

## 7. 约束条件

- **内容来源**：以 `d:\AI\.chaos\libs\okf-kit\` 源码为权威来源，辅以 README.md 和官方文档
- **输出位置**：`docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/`
- **语言**：简体中文
- **格式**：Markdown + YAML frontmatter
- **章节数量**：12-15 个原子化章节文件

## 8. 依赖与假设

### 依赖
- 源码目录 `d:\AI\.chaos\libs\okf-kit\` 可读且版本为 v0.3.3
- 现有 wiki 格式参考位于 `docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/`

### 假设
- 用户具备 Python 基础和命令行使用经验
- 用户对 LLM/Agent/RAG 概念有基本了解（教程中会解释 OKF 相关术语）

## 9. 验收标准

### Rule 类型（客观可验证）

- **AC-R1**：教程目录存在于 `docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/`
- **AC-R2**：包含 ≥12 个编号章节文件（00- 到 13-），每个为独立 .md 文件
- **AC-R3**：每个 .md 文件包含有效的 YAML frontmatter（id/title/date/category/tags）
- **AC-R4**：所有命令、参数、路径与 `d:\AI\.chaos\libs\okf-kit\okf_kit/cli.py` 中定义一致
- **AC-R5**：所有文件使用 kebab-case 英文命名，无中文文件名
- **AC-R6**：Bundle 结构描述与 `okf_kit/writer.py` 中 `write_bundle_meta` 函数实现一致
- **AC-R7**：包含 seven-concepts-report.md 记录方法论执行过程
- **AC-R8**：00-overview.md 包含 ≥15 个核心术语的术语表

### Rubric 类型（质量评估）

- **AC-RU1：内容准确性（0-3）**
  - 3：所有技术描述与源码完全一致，无错误或臆测
  - 2：核心功能描述准确，次要细节有少量偏差
  - 1：存在明显的功能描述错误
  - 0：大量内容与源码不符
  - **通过阈值**：≥2

- **AC-RU2：结构清晰度（0-3）**
  - 3：章节组织逻辑清晰，导航完善，阅读路径建议实用
  - 2：结构基本合理，导航可用
  - 1：章节划分混乱，导航缺失
  - 0：无法按顺序阅读
  - **通过阈值**：≥2

- **AC-RU3：示例实用性（0-3）**
  - 3：每个命令配有可运行示例，包含典型场景端到端演示
  - 2：主要命令有示例
  - 1：示例很少或不可运行
  - 0：无代码示例
  - **通过阈值**：≥2

- **AC-RU4：架构理解深度（0-3）**
  - 3：Mermaid 架构图准确反映代码结构，核心设计决策有解释
  - 2：架构描述基本正确
  - 1：架构描述肤浅或有误
  - 0：无架构分析
  - **通过阈值**：≥2
