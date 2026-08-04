---
id: "eve-framework-wiki-tutorial-spec"
title: "Vercel Eve 开源 Agent 框架 Wiki 教程"
source: "multi-source: nixapi博客 + 知乎两篇 + 掘金 + vercel.com/eve"
x-toml-ref: "../../../../.meta/toml/.trae/specs/eve-framework-wiki-tutorial/spec.toml"
version: "1.0"
date: "2026-08-04"
scenario: "learning-wiki"
---

# Vercel Eve 开源 Agent 框架 Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于七概念方法论（R-I-E-V 知识沉淀链路），对 5 个 Eve 框架来源（nixapi 深度解析博客、知乎两篇分析、掘金工程化解读、Vercel 官方产品页）进行系统性学习与交叉对比，生成一份完整、原子化、可维护的 Infrastructure Wiki 教程，沉淀至 `knowledge/learning/03-agent-platforms-tools/eve-wiki/`。
- **Purpose**: 帮助前端开发者、AI 应用开发者、架构师系统理解 Eve 框架的定位（"Next.js for Agents"）、核心设计（目录即 Agent）、九大生产级能力（指令/工具/技能/沙箱/渠道/连接/子Agent/定时/评测/持久化）、与 Mastra/LangGraph 的对比、生产落地建议，以及其反映的 Agent 工程化趋势。
- **Target Users**: 前端开发者、AI 应用开发者、技术架构师、技术决策者、AI Agent 领域研究者

## 来源清单（5个）
| # | 来源 | 侧重点 | 状态 |
|---|------|--------|------|
| S1 | nixapi 博客：Vercel Eve 深度解析（Next.js for Agents） | 架构设计、平台对比、七大能力、生产部署建议 | ✅ 已抓取 |
| S2 | 知乎：Eve 深度解析（生产级 Agent Harness） | 生产级痛点、Durable/Sandbox/Approvals/Subagents 深度推演、AI 内容运营团队实战系列 | ✅ 已抓取 |
| S3 | 知乎：Eve 发布解读（开源 Agent 框架） | 定位辨析、目录即 Agent、文件系统即创作接口 | ✅ 已抓取 |
| S4 | 掘金：让 AI Agent 像写 Web 应用一样简单 | 工程化视角、工具/技能/沙箱/调度/可视化调试 | ✅ 已抓取 |
| S5 | Vercel 官方产品页：https://vercel.com/eve | 官方九步上手、九大能力、代码示例、Vercel 原语集成 | ✅ 已抓取 |

## Goals
- ✅ 完整学习并交叉对比 5 个来源，提取核心共识与差异化信息
- ✅ 理解 Eve 的核心设计哲学："一个 Agent 就是一个目录"（filesystem-first）
- ✅ 系统梳理 Eve 的九大生产级能力：instructions.md / agent.ts / tools / skills / sandbox / channels / connections / subagents / schedules / evals / durable execution
- ✅ 分析 Eve 与 Mastra、LangGraph 的对比，给出选型建议与适用边界
- ✅ 洞察 Eve 反映的 Agent 工程化趋势（从 Demo 到生产、从模型竞争到工程底座竞争）
- ✅ 生成原子化、导航清晰、交叉引用完整的 Wiki 教程（10章）
- ✅ 更新 03-agent-platforms-tools 索引

## Non-Goals (Out of Scope)
- 不对 Eve 进行实际安装、测试或代码编写（仅基于公开资料分析）
- 不开发基于 Eve 的应用或示例
- 不进行商业决策或投资建议
- 不逐字翻译官方文档，而是形成结构化知识体系

## Functional Requirements
- **FR-1**: 定义 Eve 的产品定位与核心设计哲学（"Next.js for Agents"、目录即 Agent）
- **FR-2**: 梳理 Eve 的目录结构与九大核心能力模块，每个模块说明功能、技术实现、解决的问题
- **FR-3**: 提供快速上手指南（基于 S5 官方九步流程 + S1 五步 + S2 最小指令先行）
- **FR-4**: 分析 Eve 的生产级特性（durable execution、sandbox、approvals、evals、tracing）
- **FR-5**: 对比 Eve / Mastra / LangGraph，给出选型建议与适用团队边界
- **FR-6**: 提炼 Eve 的工程化理念与行业趋势洞察
- **FR-7**: 形成 FAQ、术语表、参考资源
- **FR-8**: 教程采用原子化多文件结构，含 README 总览、00 总览、各章正文件、交叉引用矩阵

## Non-Functional Requirements
- **NFR-1**: 技术准确性：符合各来源意图，专业术语准确
- **NFR-2**: 结构清晰：逻辑层次分明，覆盖 "技术理解 / 工程实践 / 趋势洞察" 三层
- **NFR-3**: 完整性：覆盖 5 个来源的核心信息，不遗漏关键数据与能力
- **NFR-4**: 专业性：准确使用 Agent 工程化术语，语言规范
- **NFR-5**: 可读性：未读过原文的开发者能理解 Eve 的核心价值
- **NFR-6**: 可维护性：遵循现有 wiki 模板规范（frontmatter、导航表、交叉引用）
- **NFR-7**: 交叉引用完整性：README 索引、章节导航、03-agent-platforms-tools 索引更新无断链

## Constraints
- **Technical**: 纯 Markdown，frontmatter 使用 YAML，遵循现有 wiki 模板规范
- **Business**: 产出用于学习与知识沉淀，不涉及商业决策
- **Dependencies**: 基于已抓取的 5 个来源内容（S1-S5），无需额外抓取
- **Methodology**: 遵循七概念知识沉淀链路（R→I→E），参照现有 infrastructure wiki 教程（如 volcengine-agentkit-wiki）的格式与结构

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 已理解 wiki 模板规范
- **When**: 创建 eve-wiki 目录
- **Then**: 目录含 README.md + 00 总览 + 各章正文件 + 交叉引用，遵循现有 wiki 原子化结构
- **Verification**: `human-judgment`

### AC-2: 核心设计阐述到位
- **Given**: 已学习 5 个来源
- **When**: 定义 Eve 定位
- **Then**: 准确阐述"Next.js for Agents"类比、"一个 Agent 就是一个目录"（filesystem-first）、"文件系统即创作接口"的哲学
- **Verification**: `human-judgment`

### AC-3: 九大能力模块梳理完整
- **Given**: 已完成来源学习
- **When**: 梳理核心能力
- **Then**: 完整覆盖 instructions.md / agent.ts / tools / skills / sandbox / channels / connections / subagents / schedules / evals / durable execution，每个模块说明功能与实现
- **Verification**: `human-judgment`

### AC-4: 生产级特性分析到位
- **Given**: 已理解各能力模块
- **When**: 分析生产级特性
- **Then**: 深入阐述 durable execution（checkpoint/暂停/恢复）、sandbox（沙箱隔离）、human-in-the-loop approvals（审批边界）、evals（回归评测）、tracing（OpenTelemetry 可观测）
- **Verification**: `human-judgment`

### AC-5: 竞品对比与选型建议清晰
- **Given**: 已理解 Eve 优势与局限
- **When**: 进行竞品对比
- **Then**: 完整对比 Eve / Mastra / LangGraph（语言/部署/持久化/沙箱/审批/MCP/多通道/追踪/许可证/生产验证），给出各团队适用建议
- **Verification**: `human-judgment`

### AC-6: 趋势洞察深刻
- **Given**: 已完成技术分析
- **When**: 进行趋势洞察
- **Then**: 挖掘 Agent 工程化趋势（从 Demo 到生产、从模型竞争到工程底座竞争、Agent 框架化时代），洞察前端工程化经验向 AI 领域迁移
- **Verification**: `human-judgment`

### AC-7: 教程格式与索引符合规范
- **Given**: 已完成教程内容
- **When**: 检查格式与索引
- **Then**: 每章含 YAML frontmatter、章节导航表、术语表、交叉引用；README 索引与 03-agent-platforms-tools 索引已更新，链接检查无断链
- **Verification**: `human-judgment`

## Open Questions
- 无（来源已全部抓取，任务范围明确）