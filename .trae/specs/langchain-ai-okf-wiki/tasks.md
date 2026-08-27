# LangChain-AI 开源项目 OKF Wiki 教程生成 - Implementation Plan

## Task 1: 创建 langchain-ai 分组目录结构和分组索引（占位）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `bundles/langchain-ai/` 目录
  - 创建 `bundles/langchain-ai/index.md`（含 okf_version frontmatter、分组描述、生态关系概览、知识束导航占位）
  - 为 20 个子项目创建 bundle 目录骨架（index.md 占位 + concepts/ examples/ references/ spec/ 子目录）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: `bundles/langchain-ai/index.md` 存在且含 `okf_version: "0.2"`；evidence: 文件读取验证
  - `rule` TR-1.2: 20 个 bundle 目录骨架完整；evidence: 目录列表验证

## Task 2: langchain（Python 核心框架）- R 阶段事实采集
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 `langchain/` monorepo：libs/core 核心抽象（runnables、prompts、chat_models、tools、output_parsers、retrievers、schema/messages、callbacks）、libs/partners 生态结构、pyproject 结构
  - 提取编号事实 F-lc-001~F-lc-xxx，写入 `bundles/langchain-ai/langchain/spec/facts.md`
  - 事实零推测，每条指向具体文件路径
- **Acceptance Criteria Addressed**: AC-2, AC-6, NFR-1, NFR-2
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 无"用于"/"目的是"/"设计为"等推断词；evidence: 关键词搜索
  - `rule` TR-2.2: 每条事实含源码文件路径；evidence: 抽样验证路径存在性
  - `rubric` TR-2.3: 事实覆盖完整性（Runnable/Message/Tool/ChatModel 等核心抽象全覆盖）；scale 1-5；threshold >= 4

## Task 3: langchain（Python 核心框架）- I 阶段架构洞察
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 facts.md 提炼 3-5 个核心架构洞察（Runnable 组合协议、消息类型体系、工具调用协议、Prompt 抽象分层、回调机制）
  - 设计知识地图与学习路径，确定 concepts/examples/references 文档清单
  - 写入 `bundles/langchain-ai/langchain/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: 洞察四元组完整（陈述/证据/反常识/行动）；evidence: 结构化检查
  - `rubric` TR-3.2: 知识地图合理性；scale 1-5；threshold >= 4

## Task 4: langchain（Python 核心框架）- E 阶段文档生成
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 4a. 生成 references/ 信源文件（信源先行，≥4 篇：core-abstractions/messages-tools/prompts-output/runnables-callbacks）
  - 4b. 分批生成 concepts/ 概念文档（每批≤7，≥10 篇：入门→核心抽象→消息与工具→Prompt→输出→Runnable 链式→回调→检索）
  - 4c. 生成 examples/ 示例（≥3 篇）
  - 4d. 生成各级 index.md 和 log.md（最后）
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: references/ 先于 concepts/ 生成；每批≤7；index 最后生成
  - `rule` TR-4.2: concepts/ ≥10、examples/ ≥3、references/ ≥4
  - `rule` TR-4.3: 所有文档 frontmatter 完整

## Task 5: langchain - V 阶段独立验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 结构检查 + frontmatter 检查 + 链接检查
  - Grep 验证关键类（Runnable/ChatModel/BaseMessage/BaseTool/PromptTemplate 等）在源码中存在的存在性
  - 修复发现问题
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: Grep 验证通过率 100%
  - `rule` TR-5.2: 链接 0 断链、frontmatter 全合规

## Task 6: langgraph（Python 编排框架）- R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 langgraph 执行完整 R→I→E→V 五阶段。聚焦 libs/ 下 graph 抽象（StateGraph/Graph/节点/边/条件边）、State/Schema、checkpoint（持久化）、message 管理、cli。采用分层采样，不逐包解析全 monorepo。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 同 TR-2.1/2.2/4.1-4.3/5.1-5.2；concepts/ ≥8、references/ ≥3、examples/ ≥2
  - `rubric` TR-6.2: 文档质量评分 >= 4

## Task 7: langchainjs（JS 核心框架）- R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 langchainjs 执行完整 R→I→E→V。聚焦 libs/langchain-core（Runnable/messages/tools/prompts）、libs/langchain 组装、pnpm+turbo 工作区布局。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 同 TR-2.1/2.2/4.1-4.3/5.1-5.2；concepts/ ≥8、references/ ≥3、examples/ ≥2
  - `rubric` TR-7.2: 文档质量评分 >= 4

## Task 8: langgraphjs（JS 编排框架）- R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 langgraphjs 执行完整 R→I→E→V。聚焦 StateGraph/节点/边/checkpoint/通道、与 langchainjs 的集成。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-8.1: 同 TR-2.1/2.2/4.1-4.3/5.1-5.2；concepts/ ≥6、references/ ≥2、examples/ ≥2
  - `rubric` TR-8.2: 文档质量评分 >= 4

## Task 9: langchain-google - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 langchain-google 执行 R→I→E→V。聚焦 Google GenAI/VertexAI ChatModel 与 Embeddings 集成、provider 抽象与鉴权。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-9.2: 文档质量评分 >= 4

## Task 10: langchain-mongodb - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 langchain-mongodb 执行 R→I→E→V。聚焦 MongoDB VectorStore 与 Atlas Vector Search 集成、集合索引与文档写入。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-10.2: 文档质量评分 >= 4

## Task 11: langsmith-sdk - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 langsmith-sdk 执行 R→I→E→V。聚焦可观测性核心：trace/run/feedback 上报、js/ 与 python/ 双语言 SDK 结构、评测（evaluation）接口。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-11.1: concepts/ ≥4、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-11.2: 文档质量评分 >= 4

## Task 12: langsmith-cli - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 langsmith-cli（Go）执行 R→I→E→V。聚焦 CLI 命令结构（eval/trace/run 等）、Go 语言实现与 LangSmith API 对接。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-12.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-12.2: 文档质量评分 >= 4

## Task 13: deepagents + lca-deepagents - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 deepagents 执行 R→I→E→V，lca-deepagents 作为变体整合进 deepagents bundle 的 references/examples。聚焦深度研究 Agent 的 planning/sub-agent/todo/context 管理（libs/acp、libs/cli）。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-13.1: deepagents concepts/ ≥4、examples/ ≥1、references/ ≥1；lca-deepagents 内容已整合；frontmatter 完整、Grep 100%
  - `rubric` TR-13.2: 文档质量评分 >= 4

## Task 14: deepagentsjs - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 deepagentsjs（TypeScript）执行 R→I→E→V。聚焦 JS 版深度研究 Agent 的实现与 deepagents（Python）的对应关系。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-14.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-14.2: 文档质量评分 >= 4

## Task 15: open-swe - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 open-swe 执行 R→I→E→V。聚焦 SWE Agent 架构（agent/ dispatch/reviewer/reconcile/scheduler）、基于 langgraph 的编排、UI（ui/）与 desktop（desktop/）。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-15.1: concepts/ ≥4、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-15.2: 文档质量评分 >= 4

## Task 16: openevals - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 openevals 执行 R→I→E→V。聚焦 LLM 评测器（exact/llm-as-judge/types/utils）js/ 与 python/ 双语言实现与评判协议。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-16.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-16.2: 文档质量评分 >= 4

## Task 17: openwiki - R→I→E→V 全流程
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 openwiki（TypeScript）执行 R→I→E→V。聚焦 Wiki/文档 Agent（src/agent、src/cli、src/config、认证与 token 管理）。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-17.1: concepts/ ≥3、examples/ ≥1、references/ ≥1；frontmatter 完整、链接 0 断链、Grep 100%
  - `rubric` TR-17.2: 文档质量评分 >= 4

## Task 18: 轻量项目 bundle 生成（openwork / chat-langchain / social-media-agent）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 为 openwork、chat-langchain、social-media-agent 生成轻量 bundle：项目概述 + 核心概念（≥1 篇）+ 信源参考 + log.md。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-18.1: 3 个 bundle 各含 index.md、concepts/（≥1）、references/（≥1）、log.md；frontmatter 完整、链接 0 断链

## Task 19: 基础设施/文档仓库参考 bundle 生成（docs / helm / terraform）
- **Status**: `completed`
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 为 docs（文档站 + src/*.mdx 结构索引）、helm、terraform 生成参考型 bundle：项目概述 + references/ 信源目录索引 + log.md，无深度概念文档。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-19.1: 3 个 bundle 各含 index.md、references/ 信源索引、log.md；frontmatter 完整、链接 0 断链

## Task 20: 分组索引与总导航更新
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
- **Description**:
  - 完善 `bundles/langchain-ai/index.md`：替换占位符为实际知识束链接，补齐生态关系图与推荐学习路径
  - 更新 `bundles/index.md`：groups 16→17、total_bundles 110→130；分组导航表添加 langchain-ai 行；生态关系图添加 langchain-ai 分组；分组详情添加 langchain-ai 节
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-20.1: bundles/langchain-ai/index.md 所有知识束链接指向存在文件；evidence: 链接检查
  - `rule` TR-20.2: bundles/index.md 含 langchain-ai 分组，groups: 17、total_bundles: 130；evidence: frontmatter 字段验证

## Task 21: 全局最终验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 20
- **Description**:
  - 对所有 20 个 bundle 执行全局 frontmatter 检查、链接检查、API 真实性 Grep 抽查、index 完整性检查
  - 确认文件名 kebab-case、正文中文、交叉链接 / 开头
  - 统计总文件数与内容文档数
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-21.1: 全局零断链、frontmatter 全合规；evidence: 全局检查输出
  - `rubric` TR-21.2: 整体文档质量一致性；scale 1-5；threshold >= 4；evidence: 全局审查