# AReaL 官方完整实战教程 Wiki - Product Requirement Document

## Overview
- **Summary**: 基于 AReaL 官网（https://areal-ai.io/）、官方文档（https://areal-ai.io/docs/en/intro.html）和本地代码仓库（d:\AI\external\tools\AReaL），生成一份完整的实战教程 Wiki。涵盖从环境安装、快速开始、算法选择、训练引擎配置、推理后端选择、v2.0 微服务架构（Agent Service / Inference Service / Training Service / Weight Update）、Online RL 在线训练模式、CLI 命令参考、代码示例解析、调试技巧、最佳实践到贡献指南的完整内容。

- **Purpose**: 弥补现有 Wiki（仅基于公众号文章）的不足，提供一份面向开发者的可操作实战教程。让用户能够跟随文档从 0 到 1 搭建 AReaL 环境、运行第一个 RL 训练任务、理解微服务架构、实现在线 RL 闭环、掌握常见问题排查方法。

- **Target Users**: 
  - 希望使用 AReaL 进行 LLM 强化学习训练的算法工程师
  - 需要搭建自演进 Agent 在线 RL 基础设施的平台工程师
  - 研究大规模异步 RL 系统架构的研究人员
  - 希望贡献代码到 AReaL 开源社区的开发者

## Goals
- 完整覆盖 AReaL 官方文档核心内容（安装、快速开始、算法、引擎、后端、v2.0架构）
- 补充代码仓库实际结构解析（目录结构、核心模块、关键API）
- 提供可直接运行的命令和配置示例
- 详细讲解 v2.0 微服务架构四大服务（Agent / Inference / Training / Weight Update）
- 完整讲解 Online RL 在线训练模式的 API 和使用流程
- 提供 CLI 命令速查表
- 包含算法矩阵、模型支持、后端对比等参考表格
- 补充调试、性能优化、OOM 处理等最佳实践
- 客观说明系统要求、硬件配置、已知限制
- 与现有基于公众号文章的 Wiki 形成互补（概念→实战）

## Non-Goals (Out of Scope)
- 不翻译所有官方文档为中文（保持技术术语准确性，关键概念配中文解释）
- 不深入讲解 RL 算法理论（GRPO/PPO/DPO 等算法原理参考论文）
- 不覆盖昇腾 NPU 的所有细节（提供安装指引链接）
- 不提供生产环境部署方案（Docker/SkyPilot 给出基础指引）
- 不重复公众号文章中已有的行业背景和趋势分析（参考现有 areal-agent-rl-wiki.md）

## Background & Context
- 现有 Wiki [areal-agent-rl-wiki.md](file:///d:/.agents/docs/knowledge/learning/03-agent-platforms-tools/areal-agent-rl-wiki.md) 仅基于微信公众号文章，侧重行业背景和概念介绍
- 用户提供了三个学习资源：官网、官方文档、本地代码仓库（v2.0版本，2026年7月发布）
- 本地代码仓库位于 d:\AI\external\tools\AReaL，是完整的 AReaL 2.0 源码
- v2.0 是重大架构升级，从单体训练框架重构为微服务架构
- 官方文档包含完整的安装指南、快速开始、CLI参考、算法文档、最佳实践
- 目标是创建一份实战导向的教程，与现有概念导向的 Wiki 形成系列

## Functional Requirements
- **FR-1**: 环境安装章节，包含硬件要求、软件依赖、Docker 方式、源码方式、vLLM/SGLang 切换、flash-attn 预编译 wheel、验证安装
- **FR-2**: 快速开始章节，包含单节点 GSM8K GRPO 训练、配置修改方法、分布式训练（Ray/Slurm）、SkyPilot 云部署
- **FR-3**: 核心概念章节，解释 Trainer / Engine / Workflow / Rollout / Weight Versioning 等核心抽象
- **FR-4**: 算法支持章节，包含 15+ 种 RL 算法列表（GRPO/GSPO/PPO/DAPO/LitePPO/DrGRPO/REINFORCE++/RLOO/SAPO/IcePop/KPop/M2PO/DPO/RW/SFT/Distillation），每种算法的配置示例
- **FR-5**: 训练引擎章节，对比 FSDP2 / Megatron / Archon 三大引擎，并行策略支持矩阵，模型适配表
- **FR-6**: 推理后端章节，对比 SGLang / vLLM，并行支持，切换方法
- **FR-7**: v2.0 微服务架构详解，四大服务（Agent Service / Inference Service / Training Service / Weight Update），组件交互图，各组件 HTTP API
- **FR-8**: Agent Service 章节，Gateway/Router/DataProxy/Worker 四组件详解，AgentRunnable 协议，多轮对话流程，代码组织
- **FR-9**: Online RL 在线训练章节，三种模式对比（inline/subproc/online），架构图，6步快速开始，API 参考（start_session/chat/completions/set_reward/end_session），认证机制，错误处理
- **FR-10**: CLI 命令参考章节，areal CLI 子命令（agent ps/run/status/stop, inference ps/run/stop, training run, logs），配置覆盖语法
- **FR-11**: 代码仓库结构解析，areal/ 目录下各子模块说明（api/dataset/engine/experimental/infra/models/reward/tools/trainer/utils/workflow/v2）
- **FR-12**: 示例解析章节，hermes（在线RL）、swe（编程Agent）、math（数学推理）、openclaw（黑盒Agent）、tau2（客服）、tir（工具集成推理）
- **FR-13**: 最佳实践章节，算法性能诊断、Agent 工作流编写、调试指南、OOM 处理、性能 profiling
- **FR-14**: 常见问题 FAQ，20+ 个常见问题（安装、训练、性能、分布式、Online RL、v2.0 相关）
- **FR-15**: 术语表，30+ 个技术术语定义
- **FR-16**: 资源链接章节，官方资源、论文、模型、社区、示例代码

## Non-Functional Requirements
- **NFR-1**: 所有代码示例和命令必须经过验证，基于本地仓库实际内容
- **NFR-2**: 文档结构清晰，目录导航完整，章节间有交叉引用
- **NFR-3**: 配置示例使用 YAML 格式，与仓库中实际 config 文件一致
- **NFR-4**: 客观说明限制条件（Linux 要求、CUDA 版本、GPU 型号、已知问题）
- **NFR-5**: 技术术语保持英文原文，首次出现时给出中文解释
- **NFR-6**: 文件名使用 kebab-case：areal-official-practical-wiki.md
- **NFR-7**: frontmatter 使用 YAML（---）格式，包含 title/source/date/tags/x-toml-ref
- **NFR-8**: 文档长度预估 800-1200 行，与现有 octo-platform-wiki.md 相当
- **NFR-9**: 放置在 .agents/docs/knowledge/learning/03-agent-platforms-tools/ 目录下

## Constraints
- **Technical**: 基于本地代码仓库（v2.0）和官方文档内容，不编造API或配置项
- **Business**: 文档日期为 2026-08-04（今天日期）
- **Dependencies**: 
  - 现有知识库存放位置规范
  - YAML frontmatter 格式要求
  - 文件名 kebab-case 规范
  - 学习分类：learning/03-agent-platforms-tools/

## Assumptions
- 用户已了解 AReaL 的基本概念（参考现有 areal-agent-rl-wiki.md）
- 用户具备基础的 Python、PyTorch、分布式训练知识
- 用户有 Linux 环境和 NVIDIA GPU（A100/H100/H800 等）
- 文档主要面向开发者，而非完全零基础用户

## Acceptance Criteria

### AC-1: 文档格式规范
- **Given**: Wiki 文档创建完成
- **When**: 检查 frontmatter 和文件格式
- **Then**: 
  - 使用 YAML frontmatter（--- 分隔）
  - 包含 title、source、date（2026-08-04）、tags、x-toml-ref 字段
  - 文件名为 areal-official-practical-wiki.md（kebab-case纯英文）
  - 标题层级从 h1 开始，无跳级
  - 表格格式正确，列数对齐
- **Verification**: `human-judgment`

### AC-2: 安装指南完整可操作
- **Given**: 读者阅读安装章节
- **When**: 按照文档步骤操作
- **Then**:
  - 明确列出硬件要求（GPU/CPU/内存/网络/存储）
  - 提供 Docker 和源码两种安装方式
  - 说明 SGLang 和 vLLM 的切换方法
  - 包含 flash-attn 预编译 wheel 安装说明
  - 提供安装验证命令
  - 包含昇腾 NPU 安装指引链接
- **Verification**: `human-judgment`

### AC-3: 快速开始可复现
- **Given**: 读者按照快速开始操作
- **When**: 运行文档中的命令
- **Then**:
  - 单节点 GSM8K GRPO 训练命令完整正确
  - 配置修改方法说明清晰（YAML编辑 + 命令行覆盖）
  - Ray/Slurm 分布式启动命令示例正确
  - SkyPilot 云部署指引清晰
  - backend 并行配置语法正确（如 sglang:d12p1t1）
- **Verification**: `human-judgment`

### AC-4: v2.0 微服务架构详解完整
- **Given**: 读者阅读 v2.0 架构章节
- **When**: 理解四大服务组件
- **Then**:
  - Agent Service 的 Gateway/Router/DataProxy/Worker 四组件职责清晰
  - AgentRunnable 协议代码示例完整
  - 多轮对话流程图清晰
  - 各组件 HTTP API 端点列表完整
  - 代码组织目录结构与仓库实际一致
  - 与 v1.0 单体架构的区别说明清楚
- **Verification**: `human-judgment`

### AC-5: Online RL 在线训练章节完整
- **Given**: 读者阅读 Online RL 章节
- **When**: 按照步骤搭建在线RL服务
- **Then**:
  - 三种模式（inline/subproc/online）对比表清晰
  - 架构图文字描述准确
  - 6步快速开始流程完整（配置→启动服务→创建session→交互→设置奖励→批量采样）
  - API 端点完整（start_session/chat/completions/set_reward/end_session）
  - 双层认证机制说明清楚（admin key / session key）
  - 错误码表完整（200/401/409/429/502）
  - Python OpenAI SDK 调用示例正确
- **Verification**: `human-judgment`

### AC-6: 算法与引擎矩阵完整
- **Given**: 读者查看算法支持和引擎对比
- **When**: 选择适合的算法和引擎
- **Then**:
  - 至少包含15种RL算法，每种有配置文件链接
  - 三大训练引擎（FSDP2/Megatron/Archon）并行策略对比表正确
  - 模型支持矩阵与仓库实际一致（Qwen2/3, Qwen3-MoE, Qwen-VL等）
  - 两大推理后端（SGLang/vLLM）并行支持对比正确
- **Verification**: `human-judgment`

### AC-7: CLI 命令参考准确
- **Given**: 读者使用 areal CLI
- **When**: 查阅CLI章节
- **Then**:
  - agent 子命令（ps/run/status/stop）说明正确
  - inference 子命令说明正确
  - training 子命令说明正确
  - logs 命令说明正确
  - 配置覆盖语法说明正确（`key=value` 和 `+key=value`）
- **Verification**: `human-judgment`

### AC-8: 代码仓库结构解析准确
- **Given**: 读者浏览代码仓库
- **When**: 对照仓库结构章节
- **Then**:
  - areal/ 目录下各子模块说明与实际一致
  - v2/ 微服务代码目录结构正确
  - examples/ 分类说明准确（Math/Agentic/VLM/Alignment）
  - 核心入口文件说明正确
- **Verification**: `human-judgment`

### AC-9: FAQ 和术语表充分
- **Given**: 读者遇到问题或不理解术语
- **When**: 查阅 FAQ 和术语表
- **Then**:
  - FAQ 包含至少 20 个常见问题
  - 术语表包含至少 30 个技术术语
  - 术语定义准确，与代码和文档一致
- **Verification**: `human-judgment`

### AC-10: 知识库索引更新
- **Given**: Wiki 文档创建完成
- **When**: 检查知识库索引
- **Then**:
  - learning/03-agent-platforms-tools/README.md 中新增条目
  - 条目格式与现有条目一致
  - tags 准确（areal、rl-training、agentic-rl、online-rl、llm-alignment、distributed-training、pytorch、sglang、vllm、fsdp、megatron）
  - 与现有 areal-agent-rl-wiki.md 形成系列链接（概念→实战）
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要包含中文文档内容（docs/zh/）还是主要基于英文文档？（决策：主要基于英文文档，技术术语保持英文）
- [ ] 是否需要与现有 areal-agent-rl-wiki.md 合并还是作为独立的实战篇？（决策：独立成篇，形成「概念篇+实战篇」系列，互相引用）
