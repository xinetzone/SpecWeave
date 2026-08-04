# AReaL 官方完整实战教程 Wiki - The Implementation Plan

## [x] Task 1: 深度内容提取与整理（安装/快速开始/核心概念）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从本地代码仓库提取安装相关文档（installation.md、Dockerfile、pyproject.toml）
  - 提取快速开始指南（quickstart.md、gsm8k_rl.py、gsm8k_grpo.yaml）
  - 提取核心概念解释（Trainer/Engine/Workflow/Rollout/Weight Versioning）
  - 整理为结构化笔记，包含可直接复制的命令和配置
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `human-judgement` TR-1.1: 安装章节硬件/软件要求列表完整，Docker/源码两种方式命令准确
  - `human-judgement` TR-1.2: 快速开始命令与仓库中examples/math/实际一致
  - `human-judgement` TR-1.3: 核心概念定义准确，与AGENTS.md和代码注释一致
- **Notes**: 参考 docs/en/tutorial/installation.md、docs/en/tutorial/quickstart.md、external/tools/AReaL/AGENTS.md

## [x] Task 2: 深度内容提取与整理（算法/引擎/后端矩阵）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 提取算法支持列表（README.md中算法表格、examples/math/下所有yaml配置）
  - 提取训练引擎对比（FSDP2/Megatron/Archon并行策略、模型支持矩阵）
  - 提取推理后端对比（SGLang/vLLM、并行支持、切换方法）
  - 整理为对比表格，包含配置示例链接
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-2.1: 算法列表至少15种，每种有对应yaml配置文件路径
  - `human-judgement` TR-2.2: 三大训练引擎并行策略表格与README.md一致
  - `human-judgement` TR-2.3: 模型支持矩阵与areal/models/目录实际一致
  - `human-judgement` TR-2.4: SGLang/vLLM切换方法说明正确（pyproject.toml替换步骤）
- **Notes**: 参考 README.md 中 Support Matrix 章节、docs/en/tutorial/megatron.md、docs/en/tutorial/archon.md

## [x] Task 3: 深度内容提取与整理（v2.0微服务架构）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 提取Agent Service完整文档（areal/v2/agent_service/README.md、各组件app.py）
  - 提取Inference Service、Training Service、Weight Update结构（代码目录分析）
  - 提取AgentRunnable协议、AgentRequest/AgentResponse类型定义
  - 整理组件交互流程图、HTTP API端点列表
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-3.1: Gateway/Router/DataProxy/Worker四组件职责描述与README.md一致
  - `human-judgement` TR-3.2: AgentRunnable协议代码示例与protocol.py/types.py一致
  - `human-judgement` TR-3.3: HTTP API端点列表与各组件app.py中路由一致
  - `human-judgement` TR-3.4: 代码组织目录结构与areal/v2/实际一致
- **Notes**: 重点分析 areal/v2/agent_service/、areal/v2/inference_service/、areal/v2/training_service/、areal/v2/weight_update/ 目录

## [x] Task 4: 深度内容提取与整理（Online RL在线训练）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 提取Online RL完整文档（docs/en/tutorial/online_proxy.md）
  - 提取三种模式（inline/subproc/online）对比
  - 提取API参考（start_session/chat/completions/set_reward/end_session）
  - 提取认证机制、错误码、Python SDK示例
  - 参考examples/openclaw/和examples/hermes/代码
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: 三种模式对比表清晰准确
  - `human-judgement` TR-4.2: 6步快速开始流程完整，curl命令示例正确
  - `human-judgement` TR-4.3: API端点与online_proxy.md文档一致
  - `human-judgement` TR-4.4: 双层认证机制说明清楚（admin key/session key）
  - `human-judgement` TR-4.5: 错误码表完整（200/401/409/429/502）
- **Notes**: 参考 docs/en/tutorial/online_proxy.md、examples/openclaw/、examples/hermes/

## [x] Task 5: 深度内容提取与整理（CLI/代码结构/示例解析）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 提取areal CLI命令（areal/v2/cli/目录下所有命令）
  - 提取代码仓库结构解析（areal/各子模块、examples/分类）
  - 提取关键示例解析（hermes/swe/math/openclaw/tau2/tir）
  - 提取配置覆盖语法说明
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-5.1: agent/inference/training/logs子命令说明与cli目录代码一致
  - `human-judgement` TR-5.2: 配置覆盖语法（key=value和+key=value）说明正确
  - `human-judgement` TR-5.3: areal/目录子模块说明与实际目录结构一致
  - `human-judgement` TR-5.4: examples/分类说明准确，关键示例有README链接
- **Notes**: 参考 areal/v2/cli/、areal/__init__.py、examples/各目录README.md

## [x] Task 6: 深度内容提取与整理（最佳实践/FAQ/术语表）
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 提取最佳实践文档（algo_perf.md、workflow.md、debugging.md、handling_oom.md）
  - 基于常见问题整理FAQ（安装问题、训练问题、性能问题、分布式问题、Online RL问题、v2.0问题）
  - 基于代码和文档整理术语表（30+术语）
  - 提取资源链接（论文、模型、社区）
- **Acceptance Criteria Addressed**: AC-9, AC-13
- **Test Requirements**:
  - `human-judgement` TR-6.1: 最佳实践章节覆盖算法性能、调试、OOM处理
  - `human-judgement` TR-6.2: FAQ至少20个问题，覆盖安装/训练/性能/分布式/Online RL/v2.0
  - `human-judgement` TR-6.3: 术语表至少30个术语，定义准确
- **Notes**: 参考 docs/en/best_practices/、examples/各目录常见问题

## [x] Task 7: 委派子代理创建完整Wiki文档
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 将前面6个任务整理的结构化内容交给子代理
  - 子代理按照十大章节结构创建完整Wiki：
    1. 概述与前置准备
    2. 环境安装（Docker/源码/vLLM切换/验证）
    3. 快速开始（单节点/分布式/SkyPilot）
    4. 核心概念与架构（Trainer/Engine/Workflow/Rollout）
    5. 算法、训练引擎与推理后端（支持矩阵对比）
    6. v2.0微服务架构详解（四大服务+Agent Service）
    7. Online RL在线训练实战（三种模式+API+示例）
    8. CLI命令参考与配置指南
    9. 代码仓库结构与示例解析
    10. 最佳实践、FAQ、术语表、资源链接
  - frontmatter包含正确的title/source/date/tags/x-toml-ref
  - 文件名：areal-official-practical-wiki.md
  - 存放路径：.agents/docs/knowledge/learning/03-agent-platforms-tools/
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9
- **Test Requirements**:
  - `human-judgement` TR-7.1: 文档结构完整，十大章节齐全
  - `human-judgement` TR-7.2: frontmatter格式正确，字段完整
  - `human-judgement` TR-7.3: 文件路径正确：.agents/docs/knowledge/learning/03-agent-platforms-tools/areal-official-practical-wiki.md
  - `human-judgement` TR-7.4: 文件名kebab-case纯英文
  - `human-judgement` TR-7.5: 标题层级从h1开始，无跳级
  - `human-judgement` TR-7.6: 所有代码块和命令与官方文档/代码一致
  - `human-judgement` TR-7.7: 与现有areal-agent-rl-wiki.md有交叉引用链接
  - `programmatic` TR-7.8: 文档行数约1522行（内容完整，略超预期）
- **Notes**: 子代理必须严格基于提供的结构化内容创建，不得编造内容；关键命令和API必须与本地代码仓库一致

## [x] Task 8: 主代理5点验收检查
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 主代理对子代理产出进行5点强制检查：
    1. frontmatter分隔符正确（--- YAML，不是+++ TOML）
    2. 字段完整且顺序正确（title/source/date/tags/x-toml-ref）
    3. 标题层级从h1开始，无跳级
    4. 文件名合规（kebab-case纯英文：areal-official-practical-wiki.md）
    5. source溯源字段存在，指向官网/文档/代码仓库
  - 随机抽取10个命令/API/配置项，与本地代码仓库交叉验证准确性
  - 检查表格格式、链接格式
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-8.1: 5点强制检查全部通过
  - `human-judgement` TR-8.2: 随机抽取的10个命令/API全部准确
  - `human-judgement` TR-8.3: 表格列数对齐，无语法错误
- **Notes**: 发现错误立即要求子代理修正，不得直接合并不准确内容

## [x] Task 9: 更新知识库索引
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 在 .agents/docs/knowledge/learning/03-agent-platforms-tools/README.md 中新增条目
  - 添加与概念篇areal-agent-rl-wiki.md的交叉引用
  - 确保tags准确：areal、rl-training、agentic-rl、online-rl、llm-alignment、distributed-training、pytorch、sglang、vllm、fsdp、megatron
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgement` TR-9.1: 03-agent-platforms-tools/README.md新增条目，格式与现有一致
  - `human-judgement` TR-9.2: 条目标题、摘要、日期、标签正确
  - `human-judgement` TR-9.3: 与现有概念篇Wiki有互相引用链接
- **Notes**: 参考现有条目格式（如octo-platform-wiki.md、echobird-wiki.md的条目格式）

## [x] Task 10: 质量验证与收尾
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 运行文件名规范检查（人工验证，因为check-filename-convention.py参数问题）
  - 检查工作区无临时文件
  - 确认文档中无编造的API或配置项
  - 确认客观说明限制条件（Linux/CUDA/GPU要求）
  - 更新tasks.md和checklist.md标记所有任务完成
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `human-judgement` TR-10.1: 文件名合规（人工验证：areal-official-practical-wiki.md，kebab-case纯英文）
  - `human-judgement` TR-10.2: 工作区无临时文件（已删除4个临时笔记文件）
  - `human-judgement` TR-10.3: 所有客观限制条件已说明（Linux/CUDA 12.8/NVIDIA GPU/H800/A100等）
  - `human-judgement` TR-10.4: checklist.md所有检查项标记完成
