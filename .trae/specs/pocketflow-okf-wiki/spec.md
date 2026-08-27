---
id: pocketflow-okf-wiki-spec
title: PocketFlow 极简 LLM Agent 框架 OKF Wiki 教程生成 - PRD
date: 2026-08-23
category: spec
maturity: L0-draft
---

# PocketFlow 极简 LLM Agent 框架 OKF Wiki 教程 - Product Requirement Document

## Problem Statement

PocketFlow 是一个仅 100 行核心代码的极简 LLM Agent 框架，以 Node-Flow 图结构为核心抽象，支持同步/异步、批量/并行处理，配套 40+ cookbook 示例和 3 个完整教程应用（代码库知识生成器、视频生成 QA、万相视频生成）。其设计哲学"少即是多"与 LangChain/CrewAI 等重量级框架形成鲜明对比，但缺乏系统化的中文源码级教程。现有官方 README 仅提供 API 速查和简单示例，缺少从架构设计角度对核心抽象、设计模式、异步模型、批量并行机制的深度解析，导致开发者难以理解其极简设计背后的工程权衡，也难以基于 cookbook 示例举一反三构建复杂应用。

## Users

- **LLM 应用开发者**：需要理解极简 Agent 框架的核心抽象（Node/Flow）以快速构建 LLM 应用
- **AI Agent 框架学习者**：希望通过 100 行核心代码理解 Agent 框架的本质，对比重量级框架（LangGraph/CrewAI/AutoGen）的设计差异
- **异步/并发编程学习者**：需要理解 asyncio 在 Agent 编排中的应用模式（AsyncNode/AsyncParallelBatchFlow）
- **PocketFlow cookbook 用户**：使用官方示例构建应用时需要理解设计模式（Agent/RAG/Multi-Agent/MapReduce/Workflow/Structure 等）的实现原理
- **教程/内容生成开发者**：需要理解三个教程应用（代码库知识/视频QA/万相视频）的流水线设计模式

## Goals

- 使用 `source-code-to-okf-wiki` 技能（R→I→E→V→C 五阶段链路）系统化学习 `external/libs/ai/ThePocket/` 下所有子项目源码
- 在 `projects/awesome-okf-xs/bundles/pocketflow/` 下创建 OKF v0.2 规范的知识束（Bundle）分类目录，产出结构化中文源码教程
- 通过 `seven-concepts-cmd` 方法论编排知识沉淀链路，确保质量门 G1-G4 全部通过
- 核心框架知识束深度解析 100 行核心代码的 12 个类和运算符重载机制
- 设计模式知识束分类解析 cookbook 中的 6 大设计模式（Agent/Multi-Agent/RAG/MapReduce/Workflow/Structure）和工具链
- 教程应用知识束解析 3 个完整应用的节点流水线设计
- 每个知识束遵循 concepts/examples/references 三层结构，frontmatter 完整，交叉引用正确
- 所有文档中的 API/类名/方法名经过 Grep 级源码验证，杜绝虚构内容

## Non-Goals (Out of Scope)

- 不做 PocketFlow 官方 README 的完整翻译或复述
- 不逐一解析 40+ cookbook 示例的全部代码（按设计模式分类，每个模式选取 1-2 个典型代表深入分析）
- 不深入 .cursor/rules/ 目录下的 AI 编辑器规则文件（非框架代码）
- 不解析教程应用中 utils/ 目录下的外部 API 封装（call_llm/crawl_github_files/generate_image 等为外部服务调用，非 PocketFlow 框架核心）
- 不修改 awesome-okf-xs 子项目的 `.agents/` 规范文件（走子项目流程）
- 不生成 git 提交（用户未要求）
- 不对比 LangChain/LangGraph 等其他框架的源码实现（可在概念文档中做简要设计哲学对比，但不做深度源码级比较）

## Source Code Inventory

源码根目录：`d:\spaces\SpecWeave\external\libs\ai\ThePocket\`

| 子项目 | 语言 | 代码规模 | 包含级别 | 说明 |
|--------|------|---------|---------|------|
| PocketFlow/ | Python | 极小（核心100行 + tests + cookbook） | Tier 1 | 框架核心：BaseNode/Node/BatchNode/Flow/BatchFlow/AsyncNode/AsyncBatchNode/AsyncParallelBatchNode/AsyncFlow/AsyncBatchFlow/AsyncParallelBatchFlow + _ConditionalTransition，配套 40+ cookbook 示例 |
| PocketFlow-Tutorial-Codebase-Knowledge/ | Python | 中（核心nodes.py 880行 + utils/ + docs/） | Tier 2 | 代码库知识生成器：FetchRepo→IdentifyAbstractions→AnalyzeRelationships→OrderChapters→WriteChapters(BatchNode)→CombineTutorial 六节点流水线，自动爬取代码并生成教程文档 |
| PocketFlow-Tutorial-Video-Generator/ | Python | 小（核心nodes.py 25行 + utils/ + docs/） | Tier 3 | 视频生成 QA 应用：GetQuestion→Answer 简单双节点流，配合 docs/ 下的技术知识库 |
| PocketFlow-Tutorial-Wan-Video/ | Python | 中（核心nodes.py 267行 + utils/） | Tier 2 | 万相视频生成应用：GenerateScenes→GenerateScript(self-loop)→GenerateImage(Batch)→GenerateAudio(Batch)→AnimateVideo(Batch)→Combine 六节点流水线，含自环和批量并行处理 |

**核心源码清单**（PocketFlow 框架）：
- `pocketflow/__init__.py`：全部 12 个类，100 行核心代码
- `tests/`：11 个测试文件，覆盖同步/异步/批量/并行/回退/组合等场景
- `cookbook/`：40+ 示例目录，每个包含 flow.py/nodes.py/main.py，分属不同设计模式

**cookbook 设计模式分类**：
| 模式 | 示例目录 |
|------|---------|
| Agent（单智能体） | pocketflow-agent, pocketflow-agent-skills, pocketflow-thinking |
| Multi-Agent（多智能体） | pocketflow-supervisor, pocketflow-judge, pocketflow-tao, pocketflow-a2a |
| RAG（检索增强生成） | pocketflow-agentic-rag, pocketflow-chat-memory |
| MapReduce（分治处理） | pocketflow-batch, pocketflow-batch-node, pocketflow-batch-flow |
| Workflow（工作流/HITL） | pocketflow-workflow, pocketflow-cli-hitl, pocketflow-gradio-hitl, pocketflow-fastapi-hitl, pocketflow-fastapi-websocket, pocketflow-fastapi-background |
| Tool Use（工具调用） | pocketflow-tool-search, pocketflow-tool-pdf-vision, pocketflow-tool-embeddings, pocketflow-tool-database, pocketflow-tool-crawler, pocketflow-browser-agent |
| Special Applications | pocketflow-chat, pocketflow-chat-guardrail, pocketflow-deep-research, pocketflow-code-generator, pocketflow-text2sql, pocketflow-voice-chat, pocketflow-lead-generation, pocketflow-invoice, pocketflow-heartbeat, pocketflow-google-calendar, pocketflow-hello-world, pocketflow-flow, pocketflow-async-basic, pocketflow-visualization, pocketflow-tracing |

## Functional Requirements

### FR-1: 创建 PocketFlow 生态分类目录
- 在 `bundles/pocketflow/` 下创建分类索引 `index.md`，列出所有知识束
- 分类索引包含 `okf_version: "0.2"` frontmatter 和生态关系概览图
- 更新 `bundles/index.md` 总索引，新增"⚡ PocketFlow 极简LLM应用框架"分组

### FR-2: pocketflow-core/ 框架核心知识束（Tier 1，最高深度）
- 创建 `bundles/pocketflow/pocketflow-core/` 目录
- **concepts/**（10-12 篇）：
  - 00-introduction：PocketFlow 是什么、100行哲学、与重量级框架对比、安装快速开始
  - 01-core-abstraction：核心抽象——Node 的 prep/exec/post 三阶段生命周期、shared 状态传递、params 参数机制
  - 02-node-lifecycle：Node 生命周期详解、max_retries 重试机制、wait 退避、exec_fallback 容错
  - 03-flow-orchestration：Flow 编排——start 入口节点、get_next_node 路由、_orch 编排循环、copy.copy 节点隔离
  - 04-transition-dsl：条件转移 DSL——>> 运算符（默认转移）、-action>> 运算符（条件转移）、_ConditionalTransition 实现
  - 05-batch-processing：批量处理——BatchNode 串行批处理、BatchFlow 批量流、items 迭代机制
  - 06-async-node：异步节点——AsyncNode 的 async prep/exec/post、asyncio 重试、run_async 入口
  - 07-async-parallel：异步并行——AsyncParallelBatchNode 的 asyncio.gather 并行、AsyncParallelBatchFlow 并行流
  - 08-async-flow：异步流编排——AsyncFlow 的 _orch_async、同步/异步节点混合编排、isinstance 类型判断
  - 09-design-philosophy：设计哲学——100行极简主义、图结构抽象、copy.copy 隔离设计、为何不用复杂基类
  - 10-error-handling：错误处理——warnings.warn 非中断式警告、exec_fallback 降级、重试策略
  - 11-testing-patterns：测试模式——从 tests/ 提取的核心测试策略和验证方法
- **examples/**（4-6 篇）：
  - hello-world：最小可运行示例（Hello World 节点+流）
  - retry-fallback：重试与容错实战
  - conditional-routing：条件分支路由（多 action 转移）
  - batch-processing：批量节点/批量流实战
  - async-parallel：异步并行处理实战
  - composition：流组合（Flow 作为 Node 嵌套）
- **references/**（3-4 篇）：
  - core-source：核心源码信源（__init__.py 100行全文注释）
  - test-suite：测试套件信源（核心测试用例索引）
  - dsl-operators：运算符重载信源（>>/-/rshift 机制详解）
  - async-model：异步模型信源（async/await 与 asyncio.gather 机制）

### FR-3: pocketflow-patterns/ 设计模式知识束（Tier 2）
- 创建 `bundles/pocketflow/pocketflow-patterns/` 目录
- **concepts/**（8-10 篇）：
  - 00-pattern-overview：设计模式总览——6大模式分类、cookbook 生态导航
  - 01-agent-pattern：Agent 模式——单节点决策循环、工具调用集成、思考节点（thinking）、技能扩展（agent-skills）
  - 02-multi-agent-pattern：多 Agent 模式——Supervisor 监督者、Judge 裁判、A2A 通信、Tao 编排
  - 03-rag-pattern：RAG 模式——Agentic RAG 检索增强、Chat Memory 记忆管理、向量化检索
  - 04-mapreduce-pattern：MapReduce 模式——BatchNode 映射、BatchFlow 规约、批量图片处理、并行翻译
  - 05-workflow-pattern：Workflow/HITL 模式——CLI/Gradio/FastAPI 人机交互、后台任务、WebSocket 流式
  - 06-tool-use-pattern：工具使用模式——Search/PDF/Vision/Embeddings/Database/Crawler 工具集成、Browser Agent DOM+Vision 双模式
  - 07-special-apps：特殊应用模式——Deep Research 深度研究、Code Generator 代码生成、Text2SQL、Voice Chat 语音、Tracing 链路追踪
  - 08-flow-composition：流组合模式——Flow 嵌套 Node、模块化 flow.py/nodes.py 分离、共享状态设计
- **examples/**（3-4 篇）：
  - agent-chat：Agent 聊天机器人实战（thinking + tool use）
  - multi-agent-supervisor：Supervisor 多 Agent 编排实战
  - rag-memory：带记忆的 RAG 聊天实战
  - batch-image-processing：批量图片处理（MapReduce 模式）
- **references/**（3-4 篇）：
  - cookbook-index：Cookbook 全量索引（40+示例分类索引）
  - agent-examples：Agent 类示例信源（nodes.py 关键片段）
  - tool-examples：工具类示例信源（tool pattern 关键片段）
  - workflow-examples：工作流类示例信源（HITL 关键片段）

### FR-4: tutorial-codebase-knowledge/ 代码库知识生成器知识束（Tier 2）
- 创建 `bundles/pocketflow/tutorial-codebase-knowledge/` 目录
- **concepts/**（5-7 篇）：
  - 00-app-overview：应用概览——六节点流水线设计、YAML 驱动的结构化输出、LLM 代码理解
  - 01-fetch-repo：FetchRepo 节点——GitHub/本地文件爬取、文件模式过滤、大小限制
  - 02-identify-abstractions：IdentifyAbstractions 节点——LLM 抽象识别、YAML 解析验证、多语言支持
  - 03-analyze-relationships：AnalyzeRelationships 节点——关系分析、Mermaid 图生成、索引验证
  - 04-order-chapters：OrderChapters 节点——教学顺序编排、依赖拓扑排序
  - 05-write-chapters-batch：WriteChapters BatchNode——批量章节生成、上下文累积、渐进式写作
  - 06-combine-tutorial：CombineTutorial 节点——教程组装、Mermaid 关系图、文件输出
- **examples/**（2-3 篇）：
  - generate-github-tutorial：从 GitHub 仓库生成教程
  - generate-local-tutorial：从本地目录生成教程
  - multi-language-tutorial：多语言教程生成（中文/英文）
- **references/**（2-3 篇）：
  - nodes-source：nodes.py 信源（6个节点完整源码解析）
  - flow-source：flow.py/main.py 入口信源
  - utils-crawler：utils/ 爬虫工具信源

### FR-5: tutorial-wan-video/ 万相视频生成知识束（Tier 2）
- 创建 `bundles/pocketflow/tutorial-wan-video/` 目录
- **concepts/**（5-7 篇）：
  - 00-app-overview：应用概览——六节点视频生成流水线、丁丁狗&米娅角色设定、教育动画生成
  - 01-generate-scenes：GenerateScenesNode——场景规划、角色对话交替规则、YAML 场景描述
  - 02-generate-script-selfloop：GenerateScriptNode 自环——逐场景脚本生成、上下文累积、next/done 条件路由
  - 03-generate-image-batch：GenerateImageNode(BatchNode)——批量图像生成、参考图风格一致性、IMGE_STYLE 提示词工程
  - 04-generate-audio-batch：GenerateAudioNode(BatchNode)——批量语音生成、角色音色
  - 05-animate-video-batch：AnimateVideoNode(BatchNode)——批量动画生成、ffprobe 时长检测、动画提示词
  - 06-combine-video：CombineNode——音视频合并、ffmpeg 拼接、final.mp4 输出
- **examples/**（2 篇）：
  - generate-educational-video：从 Markdown 文章生成教育动画
  - custom-characters：自定义角色视频生成
- **references/**（2-3 篇）：
  - nodes-source：nodes.py 信源（6个节点源码解析）
  - flow-source：flow.py/main.py 入口信源
  - utils-media：utils/ 媒体工具信源（ali_api/audio/ffmpeg）

### FR-6: tutorial-video-qa/ 视频生成 QA 知识束（Tier 3，轻量）
- 创建 `bundles/pocketflow/tutorial-video-qa/` 目录
- **concepts/**（3-4 篇）：
  - 00-app-overview：应用概览——最简双节点问答流、docs/ 技术知识库
  - 01-question-answer-flow：问答流设计——GetQuestion→Answer 线性流、input() 交互式输入
  - 02-knowledge-base：知识库组织——docs/ 下的分类技术文档（llm/rl/math/stats/system/ui 等）
- **examples/**（1 篇）：
  - interactive-qa：交互式技术问答
- **references/**（1-2 篇）：
  - nodes-source：nodes.py 信源
  - knowledge-base-index：docs/ 知识库索引

### FR-7: 每个知识束的 OKF 结构完整性
- 每个 bundle 包含：`index.md`（根索引，含 frontmatter）、`log.md`（变更日志）、`concepts/index.md`（概念索引，无 frontmatter）、`examples/index.md`（示例索引）、`references/index.md`（信源索引）、`spec/` 目录（存放 facts.md 和 insights.md）
- 每个内容文档包含完整 YAML frontmatter：`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`
- 子目录 `index.md` 不含 frontmatter

### FR-8: 方法论遵循
- 每个知识束严格遵循 source-code-to-okf-wiki 五阶段流程：R（事实采集）→ I（架构洞察）→ E（批量生成）→ V（独立验证）→ C（模式沉淀）
- 通过 seven-concepts-cmd 编排知识沉淀场景链路（R→I→E）
- R 阶段：每个子项目提取编号事实清单（F-xxx），写入各 bundle 的 `spec/facts.md`，零推测
- I 阶段：每个子项目提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组），写入 `spec/insights.md`
- E 阶段：信源先行（references/ 先生成）、分批生成（每批≤7 文件）、index 最后写
- V 阶段：Grep 级 API 真实性验证、链接检查、frontmatter 检查
- 所有事实和洞察的中间产物存放于 `.trae/specs/pocketflow-okf-wiki/` 和各 bundle 的 `spec/` 目录

### FR-9: 更新 bundles 总索引
- 在 `bundles/index.md` 中新增"⚡ PocketFlow 极简LLM应用框架"分组
- 更新 total_bundles（44→49，新增5个bundle）和 groups（11→12）计数
- 在生态关系概览图中添加 PocketFlow 位置（位于 ai-agent 旁边，代表极简主义 Agent 框架路线）
- 在推荐入门路径中添加 PocketFlow 学习节点

## Non-Functional Requirements

- **NFR-1（语言）**：所有文档正文使用中文，技术术语保留英文并在首次出现时括号注释
- **NFR-2（文件命名）**：文件名使用 kebab-case 纯英文，概念文档按学习路径编号（00-xxx.md, 01-xxx.md, ...）
- **NFR-3（路径引用）**：交叉引用使用 `/` 开头的 bundle-relative 绝对路径
- **NFR-4（溯源）**：每个文档的 `sources` 字段指向对应 references/ 信源文件和事实编号
- **NFR-5（真实性）**：所有引用的类名、方法名、API 签名必须能在源码中通过 Grep 验证存在
- **NFR-6（代码示例）**：代码块标注语言，Python 代码示例基于实际源码 API 编写，不凭记忆编造；代码块控制在 10 行以内，过长则分段解析
- **NFR-7（原子性）**：每个概念文档聚焦单一主题，控制在合理长度（避免单文件过长）
- **NFR-8（stale_after）**：统一设置为 `2027-06-30`（PocketFlow 核心架构极简且稳定，大版本变更需重新评估）
- **NFR-9（Mermaid 图）**：核心概念文档使用 Mermaid 图（flowchart/sequenceDiagram）辅助理解，节点数不超过 7 个

## Constraints

- **规范约束**：产出物必须符合 OKF v0.2 规范（参考 `bundles/meta/okf-spec/`）和 awesome-okf-xs frontmatter 规范
- **格式参考**：以现有 `bundles/katex/katex/` 为内容格式范本，以 `bundles/onnx/` 为分类目录格式范本
- **源码路径**：源码位于 `external/libs/ai/ThePocket/`，为第三方代码（禁止修改）
- **目标路径**：产出物位于 `projects/awesome-okf-xs/bundles/pocketflow/`，该子项目是 git submodule
- **禁止修改范围**：不修改 awesome-okf-xs 子项目的 `.agents/` 目录、AGENTS.md 等规范文件
- **分批约束**：E 阶段每批生成不超过 7 个文件，防止上下文过载
- **验证约束**：V 阶段必须对每个文档中引用的关键类名/方法名执行 Grep 验证
- **Cookbook 范围**：40+ cookbook 示例不逐一展开，按设计模式分类后选取典型代表分析

## Dependencies

- `source-code-to-okf-wiki` Skill：提供 R→I→E→V→C 五阶段工作流和质量门
- `seven-concepts-cmd` Skill：提供知识沉淀场景的方法论编排
- 现有 OKF 规范文档：`bundles/meta/okf-spec/` 作为格式标准
- 现有 KaTeX bundle：`bundles/katex/katex/` 作为内容格式参考范本
- 现有 ONNX 分类：`bundles/onnx/` 作为分类目录格式参考范本

## Assumptions

- 源码目录 `external/libs/ai/ThePocket/` 已通过 git submodule 初始化，代码可读取
- PocketFlow 使用 MIT 许可证，文档生成属于合理使用
- 用户已有 Python 基础和基本的 LLM/AI Agent 概念
- 不需要安装 PocketFlow 或运行代码（静态源码分析为主），V 阶段通过 Grep 验证而非运行时测试
- cookbook 中的工具函数（call_llm、crawl_github_files、generate_image 等）调用外部 API，不深入解析其实现
- pocketflow-core 预计产出 17-22 个内容文档，pocketflow-patterns 预计 14-18 个，tutorial-codebase-knowledge 预计 9-13 个，tutorial-wan-video 预计 9-12 个，tutorial-video-qa 预计 5-7 个，总计约 54-72 个内容文档

## Acceptance Criteria

### AC-1: PocketFlow 生态分类目录创建
- **type**: rule
- **Pass condition**: `bundles/pocketflow/index.md` 存在，包含 `okf_version: "0.2"` frontmatter，列出所有 5 个子项目知识束，含生态关系概览图
- **Evidence source**: 文件系统检查 + 文件内容检查

### AC-2: 5 个子项目知识束结构完整
- **type**: rule
- **Pass condition**: 每个 `bundles/pocketflow/<project>/` 目录包含 index.md、log.md、concepts/、examples/、references/、spec/ 六个必要部分，子目录下均有 index.md
- **Evidence source**: 文件系统检查（5 bundles × 6 结构要素 = 30 项）

### AC-3: 内容文档数量达标
- **type**: rule
- **Pass condition**:
  - pocketflow-core/: ≥17 内容文档（≥10 concepts + ≥4 examples + ≥3 references）
  - pocketflow-patterns/: ≥14 内容文档（≥8 concepts + ≥3 examples + ≥3 references）
  - tutorial-codebase-knowledge/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - tutorial-wan-video/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - tutorial-video-qa/: ≥5 内容文档（≥3 concepts + ≥1 examples + ≥1 references）
- **Evidence source**: 文件系统统计

### AC-4: Frontmatter 规范合规
- **type**: rule
- **Pass condition**: 每个非 index.md/log.md 的 .md 文件包含可解析的 YAML frontmatter，含 type/title/description/tags/generated/verified/status/stale_after/sources 字段；type 值为 concept/example/reference 之一
- **Evidence source**: 逐文件 frontmatter 检查

### AC-5: 无虚构 API（Grep 验证）
- **type**: rule
- **Pass condition**: 每个知识束随机抽取 ≥10 个引用的类名/方法名/函数名在源码中 Grep 验证，命中率 100%；对于发现虚构的情况必须修正
- **Evidence source**: Grep 命令验证记录

### AC-6: 交叉引用无断链
- **type**: rule
- **Pass condition**: 所有内部交叉引用（/concepts/xxx.md, /examples/xxx.md, /references/xxx.md）目标文件存在
- **Evidence source**: 链接检查

### AC-7: 七概念质量门通过
- **type**: rule
- **Pass condition**:
  - G1（R 阶段）：每个子项目 facts.md 存在，事实编号 F-xxx，无"用于"/"目的是"等推断词
  - G2（I 阶段）：每个子项目 insights.md 存在，洞察包含陈述/证据/反常识/行动四元组
  - G3（E 阶段）：references/ 先于 concepts/ 生成，分批≤7 文件，index 最后写
  - G4（V 阶段）：Grep 验证、链接检查、frontmatter 检查全部通过
- **Evidence source**: 各阶段质量门检查记录

### AC-8: bundles 总索引更新
- **type**: rule
- **Pass condition**: `bundles/index.md` 中新增 PocketFlow 生态分组，total_bundles 和 groups 计数正确（49 bundles / 12 groups），生态关系图和推荐路径更新
- **Evidence source**: 文件内容检查

### AC-9: 核心代码 100% 覆盖验证
- **type**: rule
- **Pass condition**: pocketflow/__init__.py 中定义的所有 12 个类（BaseNode, Node, BatchNode, Flow, BatchFlow, AsyncNode, AsyncBatchNode, AsyncParallelBatchNode, AsyncFlow, AsyncBatchFlow, AsyncParallelBatchFlow, _ConditionalTransition）和关键方法（prep/exec/post/_run/_orch/_exec/next/set_params/>>/-）均在文档中被引用和解释
- **Evidence source**: Grep 验证每个类名/方法名在文档中的出现

### AC-10: 文档质量（中文表达与结构清晰度）
- **type**: rubric
- **Dimension**: 文档可读性、结构清晰度、知识地图合理性、代码示例准确性
- **Scale**: 0-2
  - 0: 文档结构混乱、中文表达不通顺、概念排列无逻辑、代码示例与源码不符
  - 1: 文档基本可读，概念排列有基本逻辑，但有少量表述不清或跳跃
  - 2: 文档结构清晰、中文表达流畅、概念按学习路径递进、有 Mermaid 图/表格辅助理解、代码示例可运行
- **Pass threshold**: ≥1.5（平均每个 bundle 的抽评文档）
- **Evidence source**: 独立审查抽评

## Open Questions

1. cookbook 中部分示例（pocketflow-a2a、pocketflow-voice-chat、pocketflow-visualization、pocketflow-tracing）包含独立子模块或复杂工具链，是否需要在 patterns 中单独展开？（当前方案：归入"特殊应用模式"概念文档，选取关键节点解析，不逐一展开）
2. 是否需要在 pocketflow-core 中包含 .cursor/rules/ 下的设计模式规则文档解析？（当前方案：不解析，这些是 AI 编辑器辅助文件，非框架代码，但可在 references 中提及作为扩展阅读）
3. PocketFlow 的 cookbook 示例更新频繁（40+），stale_after 设置为 2027-06-30 是否合适？（当前方案：核心框架稳定，但 cookbook 可能新增示例，设置约10个月后过期检查）
