---
title: "Open Code Review 项目学习与 Wiki 教程文档"
source: "微信公众号文章《阿里开源 AI 代码评审工具 Open Code Review》"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/open-code-review-learning-wiki/spec.toml"
date: "2026-07-04"
tags: ["open-code-review", "ai-code-review", "alibaba", "cli", "agent", "aacr-bench", "code-quality", "devops"]
---
# Open Code Review 项目学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章介绍的阿里开源 AI 代码评审工具 Open Code Review（OCR），理解其核心设计理念（确定性工程 × Agent 混合驱动）、关键优化策略（假阴性/假阳性/定位/Token）、使用方法（CLI/scan/Claude Code/CI 集成）以及质量评估体系（AACR-Bench），基于学习成果创建一份结构清晰、内容详实的原子化 wiki 教程文档。
- **Purpose**: 为开发者提供 Open Code Review 项目的完整学习资料，帮助代码评审负责人、DevOps 工程师、AI Agent 技术爱好者理解和使用该 AI 代码评审工具。
- **Target Users**: 代码评审负责人、DevOps/SRE 工程师、AI Agent 技术爱好者、研发效率工具开发者、希望引入 AI 代码评审的团队负责人。

## Goals
- 创建包含目录导航系统的原子化 wiki 教程文档（索引页 + 多章节原子文件）
- 解释 Open Code Review 的核心设计理念：确定性工程 × Agent 混合驱动
- 详细介绍两类核心命令：ocr review（diff 评审）与 ocr scan（全量扫描）
- 解析四大关键优化方向：假阴性、假阳性、定位准确率、Token 消耗
- 提供 CLI 安装、配置与使用的分步指南
- 说明 Claude Code 集成与 GitHub/GitLab CI 流水线集成方式
- 阐述四层规则穿透机制与自定义评审规则
- 介绍 AACR-Bench 行业基准与质量评估方法论
- 客观说明项目局限性，整理常见问题解答
- 汇总相关资源链接

## Non-Goals (Out of Scope)
- 不包含 Open Code Review 源码的深度代码分析
- 不涉及 AACR-Bench 数据集的完整使用教程
- 不提供 Qwen3-30B-A3B 反思模型的训练细节
- 不进行 Open Code Review 与其他商业代码评审产品的全面对比
- 不包含 OpenTelemetry 的完整部署教程

## Background & Context
- Open Code Review 是阿里开源的 AI 驱动代码评审 CLI 工具
- 前身是阿里集团内部官方 AI 代码评审助手，服务数万开发者，识别数百万代码缺陷
- 核心设计理念：确定性工程 × Agent 混合驱动，各司其职
- 解决通用 Agent + Skills 方案在代码评审场景的三大问题：覆盖不全、位置漂移、效果不稳定
- 内部数据：2万月活、370万次评审任务、30%+ 采纳率、近80% AI 评论占比、97%+ 位置准确率
- 开源评测：基于50个开源仓库200个PR、10种编程语言、80+工程师交叉标注
- 实践案例：用 Claude Code 以 Go 语言重写开源版本，106次变更中发现145个有效问题
- 开源地址：https://github.com/alibaba/open-code-review
- 原文参考：https://mp.weixin.qq.com/s/WSicyyMEIXnNVDoWuz0jrw

## Functional Requirements
- **FR-1**: 创建原子化 wiki 教程文档结构（索引页 + 11个章节原子文件），包含完整的目录导航系统
- **FR-2**: 编写概述章节，介绍 AI 代码评审的背景、Open Code Review 的定位与学习目标
- **FR-3**: 编写核心概念章节，解析"确定性工程 × Agent 混合驱动"设计理念及通用 Agent 方案的三大问题
- **FR-4**: 编写安装配置章节，提供 npm 安装、LLM 配置的分步指南
- **FR-5**: 编写使用流程章节，演示 ocr review 与 ocr scan 两类核心命令的完整工作流
- **FR-6**: 编写关键优化章节，详细解析假阴性、假阳性、定位准确率、Token 消耗四大优化方向
- **FR-7**: 编写集成与高级用法章节，说明 Claude Code 集成、CI/CD 流水线集成、四层规则穿透、OpenTelemetry 可观测性、Web 视图
- **FR-8**: 编写效果验证与质量评估章节，介绍内部数据、开源评测对比、实践案例与 AACR-Bench 行业基准
- **FR-9**: 编写局限性章节，客观说明项目当前的不足、适用边界与对比
- **FR-10**: 编写总结与展望章节，回顾核心要点并介绍未来规划
- **FR-11**: 编写 FAQ 章节，整理常见问题及解答
- **FR-12**: 编写资源链接章节，汇总 GitHub 仓库、论文、规则文档等
- **FR-13**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口
- **FR-14**: 为每个原子文件创建对应的 TOML 元数据文件

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（开发者/DevOps/技术管理者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据
- **NFR-3**: 文档结构清晰，便于阅读和导航，章节间有递进关系
- **NFR-4**: 文档格式符合项目规范（Markdown 格式，kebab-case 命名，YAML frontmatter）
- **NFR-5**: 技术术语准确，关键概念提供清晰解释
- **NFR-6**: 遵循 MDI v1.0 规范，YAML frontmatter 配合 x-toml-ref 引用外部 TOML 元数据

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，原子文件放置在 docs/knowledge/learning/open-code-review-wiki/ 目录下，索引页为 docs/knowledge/learning/open-code-review-wiki.md
- **Business**: 基于公开文章内容创建，不得添加未验证的信息，客观说明项目局限性
- **Dependencies**: 依赖已获取的网页内容（.temp/open-code-review-raw.md），无需额外网络请求

## Assumptions
- 用户具备基本的 Git 和命令行操作经验
- 用户了解基本的代码评审（Code Review）概念
- 用户了解 AI Agent 和大语言模型的基本使用方式
- 用户可以访问互联网安装 npm 包和配置 LLM 端点

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 教程文档包含概述、核心概念、安装配置、使用流程、关键优化、集成用法、效果验证、局限性、总结展望、FAQ 和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/open-code-review-wiki/ 目录下，索引页为 open-code-review-wiki.md

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程索引页
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节文件
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 相对路径链接实现

### AC-3: 核心设计理念阐述清晰
- **Given**: 用户阅读核心概念章节
- **When**: 用户理解 Open Code Review 的设计思路
- **Then**: 用户能够说明通用 Agent 方案的三大问题（覆盖不全、位置漂移、效果不稳定）以及"确定性工程 × Agent 混合驱动"的核心设计理念
- **Verification**: `human-judgment`
- **Notes**: 引用原文中的设计理念描述

### AC-4: 两类核心命令解析完整
- **Given**: 用户阅读使用流程章节
- **When**: 用户理解两类命令的差异
- **Then**: 用户能够区分 ocr review（diff 评审）与 ocr scan（全量扫描）的适用场景、参数差异与多阶段流程
- **Verification**: `human-judgment`
- **Notes**: 包含命令示例和参数说明

### AC-5: 四大优化方向详解完整
- **Given**: 用户阅读关键优化章节
- **When**: 用户理解四大优化策略
- **Then**: 用户能够解释假阴性优化（文件打包/Plan阶段/Agent动态召回）、假阳性优化（反思模型/规则模板/上下文隔离）、定位准确率（三层递进式定位）、Token 优化（分治/压缩/预过滤）的工作原理
- **Verification**: `human-judgment`
- **Notes**: 每个优化方向需包含技术要点和实际效果数据

### AC-6: 安装指南步骤明确
- **Given**: 用户按照安装指南执行
- **When**: 用户完成所有步骤
- **Then**: 用户能够成功安装 ocr CLI 并配置 LLM 端点
- **Verification**: `human-judgment`
- **Notes**: 包含 npm install 和 ocr config 命令

### AC-7: 集成方案说明清晰
- **Given**: 用户阅读集成与高级用法章节
- **When**: 用户理解 Claude Code 集成与 CI/CD 集成方式
- **Then**: 用户能够描述 Command/Skills 两种 Claude Code 集成方式的差异，以及 GitHub Actions/GitLab CI 的集成要点
- **Verification**: `human-judgment`
- **Notes**: 包含安装命令和核心配置说明

### AC-8: 效果验证数据完整
- **Given**: 用户阅读效果验证与质量评估章节
- **When**: 用户了解 Open Code Review 的实际表现
- **Then**: 用户能够说出内部数据（2万月活/370万任务/30%采纳率/97%位置准确率）、评测对比结论（准确率/召回率/F1/资源开销）、AACR-Bench 三大优势
- **Verification**: `human-judgment`
- **Notes**: 数据需准确引用原文

### AC-9: 局限性说明客观准确
- **Given**: 用户阅读局限性章节
- **When**: 用户了解项目当前的不足
- **Then**: 用户能够说出至少4个局限性或适用边界（如召回率不如 Claude Code、规则边际效益递减、需配置 LLM 端点、内部版特性未完全开源等）
- **Verification**: `human-judgment`
- **Notes**: 客观说明，不夸大也不贬低

### AC-10: FAQ 章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅 FAQ 章节
- **Then**: 用户能够找到对应的解决方案或解释
- **Verification**: `human-judgment`
- **Notes**: FAQ 应覆盖常见问题

### AC-11: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含 GitHub 项目地址、AACR-Bench、原文链接

### AC-12: 知识库索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: 学习分类中新增 Open Code Review 教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

### AC-13: TOML 元数据文件配套完整
- **Given**: 原子化 wiki 文档创建完成
- **When**: 查看 .meta/toml/docs/knowledge/learning/open-code-review-wiki/ 目录
- **Then**: 每个原子文件都有对应的 TOML 元数据文件
- **Verification**: `programmatic`
- **Notes**: 使用 fix-x-toml-ref.py --create-toml 自动创建

## Open Questions
- [ ] 是否需要补充 GitHub 仓库的 README 分析？
- [ ] 是否需要为 AACR-Bench 单独创建一份学习 wiki？

---

## 🔍 原子化决策（必须明确选择）

### 判断标准评估

| 判断维度 | 拆分阈值 | 本 wiki 预估 |
|---------|---------|-----------|
| 内容长度 | 预计>300行建议拆分，<200行可保持单文件 | 预计约 800-1000 行（11章节） |
| 章节独立性 | 各章节是否可单独阅读/引用？ | ✅ 是（核心概念、使用流程、优化策略等可独立阅读） |
| 未来扩展 | 是否预期会持续新增章节/内容？ | ✅ 是（项目仍在积极开源，未来有 Ultra 模式/IDE 插件/MCP 集成等） |
| 复用需求 | 单个章节是否会被其他文档引用？ | ✅ 是（AACR-Bench 评估方法论、四层规则穿透机制等可被引用） |

### 决策结果

- [x] **需要原子化拆分**：采用"索引页(open-code-review-wiki.md) + 目录(open-code-review-wiki/) + 数字前缀原子文件"结构，进入 L5 原子化拆分阶段
- [ ] 保持单文件

**理由**：内容预计超过 800 行，章节独立性强，且项目仍在积极开发中，未来可能新增章节。采用原子化结构便于维护、复用和扩展。

### 章节划分

| 文件 | 章节标题 | 核心内容 |
|------|---------|---------|
| 00-overview.md | 概述与学习目标 | 背景、核心主题、学习目标、前置知识、文档导航 |
| 01-core-concepts.md | 核心概念与设计理念 | 通用 Agent 方案三大问题、确定性工程×Agent 混合驱动、四层架构 |
| 02-installation.md | 安装与配置指南 | npm 安装、LLM 配置、验证安装 |
| 03-usage.md | 使用流程与命令详解 | ocr review（diff 评审）、ocr scan（全量扫描）、参数说明 |
| 04-optimizations.md | 关键技术优化 | 假阴性优化、假阳性优化、定位准确率、Token 消耗优化 |
| 05-integrations.md | 集成与高级用法 | Claude Code 集成、CI/CD 流水线、四层规则穿透、OpenTelemetry、Web 视图 |
| 06-effectiveness.md | 效果验证与质量评估 | 内部数据、开源评测对比、实践案例、AACR-Bench 行业基准 |
| 07-limitations.md | 局限性与对比 | 适用边界、已知问题、与 Claude Code/Codex 对比 |
| 08-summary.md | 总结与展望 | 核心要点回顾、关键 takeaway、未来规划 |
| 09-faq.md | 常见问题（FAQ） | 7-10 个常见问题及解答 |
| 10-resources.md | 资源链接 | 原始资源、官方资源、相关学习资源、本项目内相关 wiki |
