# Datawhale 社区项目 OKF Wiki 教程 Spec

## Why

[Datawhale（datawhalechina）](https://github.com/datawhalechina) 是国内最大的开源 AI 学习社区之一，`external/libs/ai/datawhalechina` 目录下已收录其 18 个仓库（LLM 教程、RAG、Agent、向量数据库、推荐系统、机器学习理论等）。这些项目内容优质但分布零散，缺乏统一的源码级中文教程索引。本任务将其系统化学习并转译为符合 OKF v0.2 规范的知识束（bundle），沉淀到 `projects/awesome-okf-xs/bundles/` 中。

## What Changes

- 在 `projects/awesome-okf-xs/bundles/` 下新建 `datawhale/` 分组，作为 Datawhale 社区生态的顶层分组。
- 为全部 18 个项目各生成一个独立知识束（bundle），每个 bundle 遵循 `concepts/` + `examples/` + `references/` 三层结构。
- 采用 `source-code-to-okf-wiki` 技能的 R→I→E→V→C 五阶段链路：事实采集 → 架构洞察 → 批量生成 → 独立验证 → 模式沉淀。
- 每个 bundle 前置生产 `facts.md`（零推测事实清单）与 `insights.md`（核心洞察四元组）作为生成信源。
- 在 `bundles/index.md` 总索引中登记 `datawhale` 分组，新增 16+1 组。

## Impact

- Affected specs: 无既有 spec 冲突（grep 确认 `datawhale` 关键词在 `.trae/specs` 与 `awesome-okf-xs` 中均无匹配）
- Affected code: `projects/awesome-okf-xs/bundles/`（新增 `datawhale/` 分组目录）、`projects/awesome-okf-xs/bundles/index.md`（总索引更新）
- 内容敏感度：**Public**（GitHub 公开开源项目），标准工作流，产出物存放于 `bundles/datawhale/`

## 项目清单与分类

18 个项目按内容性质分为两类，决定 R 阶段事实采集的对象（代码框架采 API/类/方法，教程书籍采章节结构/核心概念/代码示例）：

### 代码框架类（源码驱动，R 阶段 Grep 验证 API 真实性）

| 项目 | 语言/形态 | 核心内容 |
|------|----------|---------|
| torch-rechub | Python/PyTorch | 推荐系统框架：30+ 模型（DSSM/DeepFM/DIN/MMoE 等）、CTR/Match/MTL 三类 Trainer、ONNX 导出 |
| deepagents | TypeScript+Rust+Go | 多语言 Agent 平台 monorepo：libs/（acp/cli/code/evals/talon）+ openwiki |

### 教程书籍类（文档驱动，R 阶段采集章节结构与理论概念）

| 项目 | 主题 |
|------|------|
| base-llm | 从 NLP 到 LLM 全栈教程（分词/Word2Vec/RNN/Transformer/BERT/GPT/LoRA/RLHF/量化/部署） |
| happy-llm | 从零构建大模型（Transformer/PLM/LLaMA2 手写/GRPO/RAG/Agent） |
| hello-agents | 从零构建智能体（16 章节：ReAct/低代码平台/框架开发/记忆/上下文工程/通信协议/Agentic-RL） |
| all-in-rag | RAG 技术全栈（数据准备/索引构建/检索进阶/生成评估/项目实战） |
| easy-vecdb | 向量数据库原理与实践（IVF/PQ/HNSW/LSH/Annoy/Faiss/Milvus） |
| easy-vibe | Vibe coding 教程（多语言文档站） |
| handy-n8n | n8n 工作流自动化教程（c01-c06） |
| handy-ollama | Ollama 本地大模型部署教程 |
| key-book | 机器学习理论钥匙书（可学性/复杂度/泛化界/稳定性/一致性/收敛率/遗憾界） |
| pumpkin-book | 南瓜书（西瓜书公式推导伴读） |
| tiny-universe | 大模型白盒子构建指南（TinyDiffusion/TinyRAG/TinyAgent/TinyLLM 手搓） |
| vibe-vibe | Vibe 开发教程（Basic/zh/en 多文档站） |
| code-your-own-llm | 手写 LLM（仅 README，参考 AGENTS.md 与 index.html） |
| Agent-Learning-Hub | Agent 学习路线（仅 README+index.html） |
| deepagents-in-action | deepagents 实战（仅 README） |
| members-visualization | Datawhale 成员可视化（仅 .npmrc，占位收录） |

## ADDED Requirements

### Requirement: datawhale 顶层分组

系统 SHALL 在 `projects/awesome-okf-xs/bundles/datawhale/` 建立分组目录，并生成符合 OKF v0.2 的 `index.md`，其 frontmatter 含 `okf_version`、`type: category`、`total_bundles`、`generated`/`verified` 字段。

#### Scenario: 分组索引可导航
- **WHEN** 用户打开 `bundles/datawhale/index.md`
- **THEN** 能按「代码框架」与「教程书籍」两类定位到 18 个知识束，并获取每个 bundle 的一句话简介

### Requirement: 每个项目生成独立知识束

系统 SHALL 为 18 个项目各生成一个 `datawhale/<project>/` 知识束，每个 bundle 包含：
- `index.md`（根索引，含完整 frontmatter）
- `log.md`（变更日志）
- `concepts/` 目录 + `concepts/index.md`（概念文档，无 frontmatter 的导航索引）
- `examples/` 目录 + `examples/index.md`（示例文档）
- `references/` 目录 + `references/index.md`（信源登记）

#### Scenario: 代码框架类 bundle 含源码级概念
- **WHEN** 查看 torch-rechub / deepagents 的 concepts/
- **THEN** 每个概念文档引用的类名/方法名均经 Grep 源码验证存在，API 调用与 facts.md 事实一致

#### Scenario: 教程书籍类 bundle 含章节转译
- **WHEN** 查看 base-llm / hello-agents 等教程类 bundle 的 concepts/
- **THEN** 概念文档按教程章节结构转译核心概念，附来源章节链接，交叉链接使用 `/` 开头的 bundle-relative 路径

### Requirement: 事实与洞察信源前置

系统 SHALL 在每个 bundle 的 R 阶段产出 `spec/facts.md`（编号事实清单 F-xxx，零推测）与 I 阶段产出 `spec/insights.md`（3-5 个核心洞察四元组），作为 E 阶段批量生成的唯一事实依据。

#### Scenario: 事实清单零推测
- **WHEN** 检查任一 bundle 的 facts.md
- **THEN** 其中不出现「用于」「目的是」「设计为」等推断性表述，每个事实指向源码文件路径或文档章节位置

### Requirement: 总索引登记

系统 SHALL 更新 `projects/awesome-okf-xs/bundles/index.md`，新增 `datawhale` 分组条目（分组导航表 + 分组详情表），并将 `total_bundles` 与 `groups` 计数相应递增。

#### Scenario: 总索引计数一致
- **WHEN** 完成全部 bundle 后检查总索引
- **THEN** `groups` 由 16 增至 17，`total_bundles` 由 110 增至 128，分组导航表含 `datawhale` 行

## REMOVED Requirements

无。