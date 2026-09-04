# PocketFlow 极简 LLM Agent 框架 OKF Wiki 教程 - Implementation Plan

## Task Dependencies

```
Phase 0: Setup → Phase 1: R+I (per bundle) → Phase 2: E (per bundle, references→concepts→examples→indexes) → Phase 3: V (per bundle) → Phase 4: Category + Bundles Index → Phase 5: Independent Review
```

Bundle processing order: pocketflow-core/ → pocketflow-patterns/ → tutorial-codebase-knowledge/ → tutorial-wan-video/ → tutorial-video-qa/

Rationale: pocketflow-core/ 是框架本体，所有其他 bundle 都依赖其核心抽象（Node/Flow/BatchNode等）；pocketflow-patterns/ 基于核心抽象解析 cookbook 设计模式；教程应用（codebase-knowledge/wan-video/video-qa）作为实战案例放在最后，它们是 PocketFlow 框架的具体应用。

---

## Phase 0: Setup & Scaffolding

### Task 1: 创建 PocketFlow 生态分类目录和 bundle 脚手架
- **Priority**: high
- **Depends On**: None
- **ACs Addressed**: [AC-1, AC-2]
- **Description**:
  - 创建 `bundles/pocketflow/` 目录及 `index.md`（含 okf_version frontmatter 和生态概览占位）
  - 创建 5 个子 bundle 目录的空脚手架：`pocketflow-core/`, `pocketflow-patterns/`, `tutorial-codebase-knowledge/`, `tutorial-wan-video/`, `tutorial-video-qa/`
  - 每个 bundle 创建 `concepts/`, `examples/`, `references/`, `spec/` 空目录
  - 创建 `.trae/specs/okf-wiki-ecosystem/pocketflow-okf-wiki/` 下的各 bundle 工作子目录
- **Test Requirements**:
  - `rule` TR-1.1: 目录结构存在且完整（1个category + 5个bundle × 4个子目录 = 21个目录）
  - `rule` TR-1.2: category index.md 包含 okf_version: "0.2"

---

## Phase 1: R+I 阶段（事实采集与架构洞察）

### Task 2: pocketflow-core/ 框架核心 - R阶段事实采集
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7, AC-9]
- **Description**:
  - 深度阅读 PocketFlow 核心源码和测试：
    - `pocketflow/__init__.py`：12 个类（BaseNode/Node/BatchNode/Flow/BatchFlow/AsyncNode/AsyncBatchNode/AsyncParallelBatchNode/AsyncFlow/AsyncBatchFlow/AsyncParallelBatchFlow/_ConditionalTransition），100 行核心代码
    - `tests/`：11 个测试文件（test_flow_basic/test_flow_composition/test_batch_node/test_batch_flow/test_async_flow/test_async_batch_node/test_async_batch_flow/test_async_parallel_batch_node/test_async_parallel_batch_flow/test_fall_back）
    - 运算符重载：`__rshift__`（>>）、`__sub__`（-）、DSL 条件转移
    - cookbook 中的基础示例：pocketflow-hello-world（最小示例）、pocketflow-flow（流组合）、pocketflow-async-basic（异步基础）
  - 提取 ≥40 条编号事实（F-001起），写入 `.trae/specs/okf-wiki-ecosystem/pocketflow-okf-wiki/pocketflow-core/facts.md`，同时复制到 `bundles/pocketflow/pocketflow-core/spec/facts.md`
  - 事实覆盖：BaseNode 生命周期、Node 重试机制、Flow 编排循环、条件转移 DSL、BatchNode/Flow 批量模型、AsyncNode 异步模型、AsyncParallelBatch 并行模型、AsyncFlow 混合编排、copy.copy 隔离设计、warnings 策略、继承层次（MRO）
- **Test Requirements**:
  - `rule` TR-2.1: 事实数量 ≥40 条，编号连续
  - `rule` TR-2.2: 事实无"用于"/"目的是"/"设计为"等推断词（G1 质量门）
  - `rule` TR-2.3: 每个事实标注源码路径和行号
  - `rule` TR-2.4: 覆盖 __init__.py 中所有 12 个类

### Task 3: pocketflow-core/ 框架核心 - I阶段架构洞察
- **Priority**: high
- **Depends On**: Task 2
- **ACs Addressed**: [AC-7, AC-9]
- **Description**:
  - 基于 facts.md 提炼 4-5 个核心架构洞察（四元组：陈述+证据(F-xxx)+反常识+行动）
  - 关键洞察方向：
    1. "100行极简"背后的工程权衡——为何不用复杂抽象基类/装饰器/配置对象
    2. copy.copy 节点隔离——为何在 _orch 中 copy.copy 每个节点而非直接复用
    3. 运算符重载 DSL——>>/- 如何实现声明式流定义而不引入额外 DSL 解析器
    4. 异步/同步统一模型——AsyncNode 如何通过 isinstance 判断混合编排同步/异步节点
    5. 继承 MRO 设计——AsyncBatchNode(AsyncNode,BatchNode) 和 AsyncParallelBatchFlow(AsyncFlow,BatchFlow) 的多继承协作
  - 设计知识地图：文档分组（入门基础/核心机制/异步并行/设计哲学/错误处理）、学习路径、概念文档覆盖的事实编号
  - 写入 `bundles/pocketflow/pocketflow-core/spec/insights.md`
- **Test Requirements**:
  - `rule` TR-3.1: 洞察数量 ≥4 条
  - `rule` TR-3.2: 每条洞察包含陈述/证据/反常识/行动四元组（G2 质量门）
  - `rule` TR-3.3: 知识地图覆盖所有计划的 concepts 文档（10-12篇）

### Task 4: pocketflow-patterns/ 设计模式 - R阶段事实采集 + I阶段洞察
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 cookbook 示例，按设计模式分类选取典型代表：
    - Agent 模式：pocketflow-agent/nodes.py, pocketflow-thinking/nodes.py
    - Multi-Agent 模式：pocketflow-supervisor/nodes.py, pocketflow-a2a/nodes.py+common/
    - RAG 模式：pocketflow-agentic-rag/nodes.py, pocketflow-chat-memory/nodes.py+utils/
    - MapReduce 模式：pocketflow-batch/main.py, pocketflow-batch-flow/nodes.py, pocketflow-batch-node/nodes.py
    - Workflow/HITL 模式：pocketflow-cli-hitl/nodes.py, pocketflow-gradio-hitl/nodes.py, pocketflow-fastapi-hitl/nodes.py
    - Tool Use 模式：pocketflow-tool-search/nodes.py+tools/, pocketflow-browser-agent/nodes_dom.py+nodes_vision.py
    - 特殊应用：pocketflow-deep-research/nodes.py, pocketflow-tracing/tracing/
    - 模块化组织：每个 cookbook 的 flow.py/nodes.py/main.py 三文件分离模式
  - 提取 ≥30 条事实，写入 `bundles/pocketflow/pocketflow-patterns/spec/facts.md`
  - 提炼 3-4 个洞察 + 知识地图，写入 `insights.md`
- **Test Requirements**:
  - `rule` TR-4.1: 事实 ≥30 条，覆盖 6 大模式
  - `rule` TR-4.2: 洞察 ≥3 条，四元组完整

### Task 5: tutorial-codebase-knowledge/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读代码库知识生成器源码：
    - `nodes.py`（880行）：FetchRepo/IdentifyAbstractions/AnalyzeRelationships/OrderChapters/WriteChapters(BatchNode)/CombineTutorial 六个节点
    - `flow.py`/`main.py`：入口和流定义
    - `utils/crawl_github_files.py`/`crawl_local_files.py`/`call_llm.py`：工具函数
  - 提取 ≥25 条事实，写入 `spec/facts.md`
  - 提炼 3 个洞察 + 知识地图，写入 `insights.md`
  - 关键洞察方向：BatchNode 渐进式上下文累积（WriteChapters.chapters_written_so_far）、YAML 结构化 LLM 输出校验、多语言支持设计
- **Test Requirements**:
  - `rule` TR-5.1: 事实 ≥25 条，覆盖 6 个节点
  - `rule` TR-5.2: 洞察 ≥3 条，四元组完整

### Task 6: tutorial-wan-video/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读万相视频生成器源码：
    - `nodes.py`（267行）：GenerateScenes/GenerateScript(self-loop)/GenerateImage(Batch)/GenerateAudio(Batch)/AnimateVideo(Batch)/Combine 六个节点
    - `flow.py`/`main.py`：入口和流定义
    - `utils/ali_api.py`/`audio.py`/`ffmpeg.py`：媒体工具
  - 提取 ≥20 条事实，写入 `spec/facts.md`
  - 提炼 3 个洞察 + 知识地图，写入 `insights.md`
  - 关键洞察方向：自环节点（self-loop via action="next"/"done"）、BatchNode 状态共享（self._shared）、ffprobe 时长驱动的视频生成、多阶段媒体管线
- **Test Requirements**:
  - `rule` TR-6.1: 事实 ≥20 条，覆盖 6 个节点
  - `rule` TR-6.2: 洞察 ≥3 条，四元组完整

### Task 7: tutorial-video-qa/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读视频生成 QA 应用源码：
    - `nodes.py`（25行）：GetQuestionNode/AnswerNode 双节点
    - `flow.py`/`main.py`：入口和流定义
    - `docs/`：技术知识库目录结构（llm/rl/math/stats/system/ui/game 等）
    - `utils/call_llm.py`：LLM 调用
  - 提取 ≥10 条事实，写入 `spec/facts.md`
  - 提炼 2 个洞察 + 知识地图，写入 `insights.md`
- **Test Requirements**:
  - `rule` TR-7.1: 事实 ≥10 条
  - `rule` TR-7.2: 洞察 ≥2 条，四元组完整

---

## Phase 2: E 阶段（批量生成 OKF 文档）

> **E 阶段铁律**：references/ 先生成（信源先行），每批 ≤7 文件，index 最后写。

### Task 8: pocketflow-core/ - 生成 references/ 信源文档
- **Priority**: high
- **Depends On**: Task 3
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - 基于 facts.md 和 insights.md 的知识地图，生成 3-4 个 references/ 信源文档
  - 文档列表：
    1. `core-source.md` - 核心源码信源（__init__.py 100行逐类注释解析）
    2. `test-suite.md` - 测试套件信源（11个测试文件覆盖场景索引）
    3. `dsl-operators.md` - 运算符重载信源（>>/- 转移DSL机制详解）
    4. `async-model.md` - 异步模型信源（async/await、asyncio.gather、混合编排）
- **Test Requirements**:
  - `rule` TR-8.1: 信源文档数量 3-4 个
  - `rule` TR-8.2: 每个信源文档 frontmatter 完整（type: reference）
  - `rule` TR-8.3: 每个信源包含关键事实 F-xxx 引用和源码路径行号

### Task 9: pocketflow-core/ - 生成 concepts/ 概念文档（批次1：入门基础篇，5篇）
- **Priority**: high
- **Depends On**: Task 8
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第一批概念文档（入门基础，≤5篇）：
    1. `00-introduction.md` - PocketFlow 简介、100行哲学、与重量级框架对比、安装快速开始
    2. `01-core-abstraction.md` - 核心抽象：Node 的 prep/exec/post 三阶段生命周期、shared 状态、params 参数
    3. `02-node-lifecycle.md` - Node 生命周期：max_retries 重试、wait 退避、exec_fallback 容错、cur_retry 计数
    4. `03-flow-orchestration.md` - Flow 编排：start 入口、get_next_node 路由、_orch 编排循环、copy.copy 节点隔离
    5. `04-transition-dsl.md` - 条件转移 DSL：>> 默认转移、-action>> 条件转移、_ConditionalTransition 实现
  - 每篇含：概述、核心机制（配 Mermaid 流程图/sequenceDiagram）、代码示例（≤10行）、相关概念链接
- **Test Requirements**:
  - `rule` TR-9.1: 文档数量 5 篇
  - `rule` TR-9.2: frontmatter 完整（type: concept, sources 指向 references/ 和 facts 编号）
  - `rule` TR-9.3: 代码示例中引用的 API 在 references/ 信源中有对应事实
  - `rule` TR-9.4: 至少 2 篇包含 Mermaid 图

### Task 10: pocketflow-core/ - 生成 concepts/ 概念文档（批次2：异步并行与高级篇，5-7篇）+ examples/（4-6篇）
- **Priority**: high
- **Depends On**: Task 9
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第二批概念文档（异步并行+高级，≤7篇）：
    1. `05-batch-processing.md` - 批量处理：BatchNode 串行批处理、BatchFlow 批量流、items 迭代
    2. `06-async-node.md` - 异步节点：AsyncNode 的 async prep/exec/post、asyncio 重试、run_async
    3. `07-async-parallel.md` - 异步并行：AsyncParallelBatchNode 的 asyncio.gather、AsyncParallelBatchFlow 并行流
    4. `08-async-flow.md` - 异步流编排：AsyncFlow._orch_async、同步/异步混合、isinstance 判断
    5. `09-design-philosophy.md` - 设计哲学：100行极简主义、图结构抽象、copy.copy 隔离、为何不用复杂基类
    6. `10-error-handling.md` - 错误处理：warnings.warn 非中断、exec_fallback 降级、重试策略
    7. `11-testing-patterns.md` - 测试模式：从 tests/ 提取核心测试策略
  - examples/（4-6篇）：
    1. `hello-world.md` - 最小可运行示例
    2. `retry-fallback.md` - 重试与容错实战
    3. `conditional-routing.md` - 条件分支路由
    4. `batch-processing.md` - 批量节点/批量流实战
    5. `async-parallel.md` - 异步并行处理实战
    6. `composition.md` - 流组合（Flow 嵌套 Node）
  - 注意：concepts 和 examples 总数可能超过7，需分两小批生成（先 concepts 05-08，再 concepts 09-11 + examples）
- **Test Requirements**:
  - `rule` TR-10.1: 概念文档总计 10-12 篇，示例文档 4-6 篇
  - `rule` TR-10.2: 每篇 example 含可运行的代码示例（基于 facts.md 中验证过的 API）
  - `rule` TR-10.3: frontmatter 完整（example 类型的 sources 指向相关 concepts 和 references）
  - `rule` TR-10.4: 代码块控制在 10 行以内，分段解析

### Task 11: pocketflow-core/ - 生成 index.md 和 log.md
- **Priority**: high
- **Depends On**: Task 10
- **ACs Addressed**: [AC-2, AC-4, AC-9]
- **Description**:
  - 生成 concepts/index.md、examples/index.md、references/index.md（子目录索引，无 frontmatter）
  - 生成根 index.md（含 okf_version、知识包概述、快速导航表格、学习路径推荐 Mermaid 图、核心洞察摘要、版本信息）
  - 生成 log.md（变更日志，记录创建日期和各阶段完成情况）
- **Test Requirements**:
  - `rule` TR-11.1: 子目录 index.md 列出对应目录下所有文档
  - `rule` TR-11.2: 根 index.md 含 okf_version: "0.2" frontmatter、学习路径图、核心洞察
  - `rule` TR-11.3: log.md 包含 2026-08-23 日期记录

### Task 12: pocketflow-patterns/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: high
- **Depends On**: Task 4
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（3-4篇）：cookbook-index（40+示例分类索引）、agent-examples（Agent类关键片段）、tool-examples（工具类关键片段）、workflow-examples（工作流类关键片段）
  - concepts/（8-10篇，分两批，每批≤5篇）：
    - 批次1：00-pattern-overview、01-agent-pattern、02-multi-agent-pattern、03-rag-pattern、04-mapreduce-pattern
    - 批次2：05-workflow-pattern、06-tool-use-pattern、07-special-apps、08-flow-composition
  - examples/（3-4篇）：agent-chat、multi-agent-supervisor、rag-memory、batch-image-processing
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-12.1: references 3-4 篇
  - `rule` TR-12.2: concepts 8-10 篇，分批生成
  - `rule` TR-12.3: examples 3-4 篇
  - `rule` TR-12.4: index.md 和 log.md 完整

### Task 13: tutorial-codebase-knowledge/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 5
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：nodes-source（6个节点完整解析）、flow-source（flow.py/main.py入口）、utils-crawler（爬虫工具）
  - concepts/（5-7篇，分1-2批）：
    00-app-overview、01-fetch-repo、02-identify-abstractions、03-analyze-relationships、04-order-chapters、05-write-chapters-batch、06-combine-tutorial
  - examples/（2-3篇）：generate-github-tutorial、generate-local-tutorial、multi-language-tutorial
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-13.1: references 2-3 篇
  - `rule` TR-13.2: concepts 5-7 篇
  - `rule` TR-13.3: examples 2-3 篇
  - `rule` TR-13.4: index 和 log 完整

### Task 14: tutorial-wan-video/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 6
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：nodes-source（6个节点解析）、flow-source（flow.py/main.py入口）、utils-media（媒体工具ali_api/audio/ffmpeg）
  - concepts/（5-7篇，分1-2批）：
    00-app-overview、01-generate-scenes、02-generate-script-selfloop、03-generate-image-batch、04-generate-audio-batch、05-animate-video-batch、06-combine-video
  - examples/（2篇）：generate-educational-video、custom-characters
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-14.1: references 2-3 篇
  - `rule` TR-14.2: concepts 5-7 篇
  - `rule` TR-14.3: examples 2 篇
  - `rule` TR-14.4: index 和 log 完整

### Task 15: tutorial-video-qa/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 7
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（1-2篇）：nodes-source（nodes.py信源）、knowledge-base-index（docs/知识库索引）
  - concepts/（3-4篇，1批）：00-app-overview、01-question-answer-flow、02-knowledge-base
  - examples/（1篇）：interactive-qa
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-15.1: references 1-2 篇
  - `rule` TR-15.2: concepts 3-4 篇
  - `rule` TR-15.3: examples 1 篇
  - `rule` TR-15.4: index 和 log 完整

---

## Phase 3: V 阶段（独立验证）

### Task 16: pocketflow-core/ - V阶段验证与修复
- **Priority**: high
- **Depends On**: Task 11
- **ACs Addressed**: [AC-4, AC-5, AC-6, AC-7, AC-9]
- **Description**:
  - 结构检查：所有文件存在、frontmatter 完整
  - Grep API 验证：随机抽取 ≥12 个类名/方法名（覆盖全部12个类），在源码中验证存在性
  - 链接检查：所有交叉引用目标文件存在
  - 核心代码覆盖检查：验证 __init__.py 中所有 12 个类和关键方法均在文档中被引用
  - 修复发现的问题
  - 更新 verified 字段
- **Test Requirements**:
  - `rule` TR-16.1: 结构检查 100% 通过
  - `rule` TR-16.2: Grep 验证 ≥12 个 API（覆盖12个类），命中率 100%
  - `rule` TR-16.3: 链接检查无断链
  - `rule` TR-16.4: 12个类和关键方法（prep/exec/post/_run/_orch/next/>>/-）均被引用
  - `rule` TR-16.5: 所有问题修复完成

### Task 17: pocketflow-patterns/ ~ tutorial-video-qa/ - V阶段验证与修复（4个bundle）
- **Priority**: high
- **Depends On**: Task 12, Task 13, Task 14, Task 15
- **ACs Addressed**: [AC-4, AC-5, AC-6, AC-7]
- **Description**:
  - 对 4 个 bundle 逐一执行 V 阶段验证
  - 每个 bundle：结构检查 + Grep 验证（patterns≥10个API, 其他≥8个API）+ 链接检查 + 修复
- **Test Requirements**:
  - `rule` TR-17.1: 4 个 bundle 全部通过结构检查
  - `rule` TR-17.2: 每个 bundle Grep 验证 ≥8 个 API，命中率 100%
  - `rule` TR-17.3: 无断链
  - `rule` TR-17.4: 问题修复完成

---

## Phase 4: 分类索引更新

### Task 18: 完善 pocketflow/ 分类 index.md 并更新 bundles/index.md
- **Priority**: high
- **Depends On**: Task 16, Task 17
- **ACs Addressed**: [AC-1, AC-8]
- **Description**:
  - 完善 `bundles/pocketflow/index.md`：添加生态关系概览图（Mermaid flowchart）、各 bundle 简介表格、推荐学习路径、PocketFlow 与 ai-agent 框架的定位对比
  - 更新 `bundles/index.md`：
    - 新增"⚡ PocketFlow 极简LLM应用框架"分组
    - 更新 total_bundles（44→49）和 groups（11→12）
    - 在生态关系概览图中添加 PocketFlow 节点（与 ai-agent 并列，代表极简路线）
    - 在推荐入门路径中添加 PocketFlow 学习节点（在 ai-agent 之前或并行）
    - 在分组导航表和分组详情中添加 PocketFlow 条目
- **Test Requirements**:
  - `rule` TR-18.1: category index.md 列出全部 5 个 bundle 并含简要说明和 Mermaid 生态图
  - `rule` TR-18.2: bundles/index.md 新增 PocketFlow 分组条目，计数正确（49 bundles / 12 groups）
  - `rule` TR-18.3: 生态关系图和推荐路径已更新

---

## Phase 5: 独立审查

### Task 19: 独立审查（Independent Review）
- **Priority**: high
- **Depends On**: Task 18
- **ACs Addressed**: [AC-1~AC-10]
- **Description**:
  - 委派一个独立 reviewer（fresh context）对所有产出物进行审查
  - Reviewer 检查：结构完整性、frontmatter 合规、API 真实性（抽样 Grep ≥10个/核心bundle）、链接有效性、文档质量、核心代码100%覆盖
  - 产出 review.md 报告
  - 如发现 actionable findings，返回 Implement 阶段修复后重新审查
- **Test Requirements**:
  - `rule` TR-19.1: review.md 存在，包含 pass/fail/blocked 结论
  - `rule` TR-19.2: 所有 rule 类型 AC 有独立通过证据
  - `rule` TR-19.3: AC-9 核心代码覆盖验证（12个类全部引用）通过
  - `rubric` TR-19.4: 文档质量评分 ≥1.5/2

---

## Task Summary

| Phase | Tasks | 数量 | 说明 |
|-------|-------|------|------|
| Phase 0: Setup | Task 1 | 1 | 目录脚手架 |
| Phase 1: R+I | Task 2-7 | 6 | 5个bundle的事实采集+洞察（core/分2个task） |
| Phase 2: E | Task 8-15 | 8 | 5个bundle的文档生成（core/分4个task：ref+2批concept/example+index） |
| Phase 3: V | Task 16-17 | 2 | 5个bundle的验证修复 |
| Phase 4: Index | Task 18 | 1 | 分类索引+总索引更新 |
| Phase 5: Review | Task 19 | 1 | 独立审查 |
| **Total** | | **19** | |
