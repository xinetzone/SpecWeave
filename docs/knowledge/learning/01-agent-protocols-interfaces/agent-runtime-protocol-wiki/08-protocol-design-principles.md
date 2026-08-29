---
id: "agent-runtime-protocol-wiki-08"
title: "Protocol 对象映射与设计原则"
source: "微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki/08-protocol-design-principles.toml"
---
# 08 Protocol 对象映射与设计原则

## Protocol 对象完整映射表

| Protocol 对象/操作 | 外部契约（客户端能看到什么） | Runtime 能力（内部如何兑现） | 对应章节 |
|-----------------|--------------------------|------------------------|---------|
| **Agent/Assistant** | Agent Card、能力声明、工具列表 | Agent 注册、能力发现、权限边界 | [第01章](01-protocol-boundary-lifecycle.md) |
| **Thread/Session** | thread_id、创建/查询、历史消息 | 上下文边界、消息追加、状态关联 | [第03章](03-state-management.md) |
| **Run/Task** | run_id、状态机、创建/取消/重试 | Loop 执行、调度、超时、资源隔离 | [第02章](02-execution-model.md) |
| **Step** | step_id、类型（model/tool/handoff）、耗时 | 节点执行、Span 追踪、进度统计 | [第02章](02-execution-model.md)、[第07章](07-observability-evaluation.md) |
| **Message/Part** | 消息列表、角色、内容、附件 | 上下文窗口管理、裁剪、摘要 | [第03章](03-state-management.md) |
| **Tool** | 工具定义（JSON Schema）、调用参数/结果 | 工具执行、错误处理、权限检查 | [第05章](05-tools-streaming.md) |
| **Event** | 事件类型、payload、顺序、event_id | 事件流生成、SSE 推送、可恢复性 | [第05章](05-tools-streaming.md) |
| **Artifact** | artifact_id、类型、归属 Run、版本 | 文件存储、产物追踪、版本管理 | [第03章](03-state-management.md) |
| **Checkpoint** | checkpoint_id、parent_id、状态快照 | 快照存储、版本链、回滚恢复 | [第03章](03-state-management.md)、[第04章](04-interrupt-error-recovery.md) |
| **Interrupt** | 中断载荷、等待类型（input/approval） | 暂停执行、保存状态、等待恢复 | [第04章](04-interrupt-error-recovery.md) |
| **Resume** | resume 指令、恢复值 | 从快照加载、继续执行 | [第04章](04-interrupt-error-recovery.md) |
| **Stream** | SSE 端点、Last-Event-ID | 事件持久化、Catch-up、多订阅者 | [第05章](05-tools-streaming.md) |
| **Trace** | Trace ID、Span 树、属性 | Span 创建、上下文传播、导出 | [第07章](07-observability-evaluation.md) |

## 九条协议设计原则

基于全文分析，提炼出九条 Agent Protocol 设计原则：

### 原则一：对象先于 API

Thread/Run/Step/Event/Artifact/Checkpoint 这六个对象的语义边界，比任何具体 API 方法名更持久。设计 Protocol 时先定义对象和它们的生命周期，再设计 API。

### 原则二：Run 是执行边界

所有和"一次具体执行"相关的概念（超时、取消、成本、权限、Trace、错误、产物归属）都应该挂在 Run 上，而不是 Thread 上。Thread 承载上下文，Run 承载执行。

### 原则三：Checkpoint 是恢复契约

Checkpoint 不只是"保存对话历史"，而是"可以从这里继续执行"的契约。这要求状态、工具副作用、外部资源、权限上下文都能重新对齐。

### 原则四：Event 是一等公民

不要只在最后返回结果。状态变更、工具调用、产物增量、错误都应该以 Event 形式实时推送。前端和监控系统依赖的是事件流，不是最终答案。

### 原则五：错误优先作为数据

工具错误和 LLM 可处理的失败应该作为 Error-as-Data 返回给模型，而不是默认抛异常。只有模型无法处理的系统级故障才打断执行流。

### 原则六：控制面与数据面分离

权限、Guardrail、预算、审批是控制面；状态、事件、Trace、Artifact 是数据面。控制面决定"能不能做"，数据面决定"做了什么"。

### 原则七：工具协议与 Runtime 解耦

工具定义、发现、调用应该独立于具体的 Runtime Loop 承载方式。MCP 的价值正在于此——一个工具应该能被图式、代码式、托管式 Runtime 复用。

### 原则八：并发语义必须显式定义

同一个 Thread 上多个 Run 如何处理？排队？拒绝？取消？分叉？乐观并发？Protocol 必须明确写进 Run 创建语义，不能留给实现自行决定。

### 原则九：可观测性从 Day 1 开始

Trace ID、Run ID、Step ID 应该贯穿所有 Event、Log 和 Artifact。没有可观测性的 Protocol，一旦出问题就是黑盒。

## Protocol 与 Runtime 边界划分

| 层面 | Protocol 规定什么 | Runtime 负责什么 |
|------|----------------|----------------|
| **对象** | 对象名称、ID、生命周期状态机 | 对象的内部表示、存储方式 |
| **操作** | 有哪些操作（create/cancel/resume/stream） | 操作的具体实现、调度算法 |
| **事件** | 事件类型、格式、顺序保证 | 事件生成时机、传输方式 |
| **错误** | 错误类型、错误码语义 | 错误检测、重试策略、回滚逻辑 |
| **流式** | SSE 端点、事件格式、Last-Event-ID 协议 | 事件持久化、Catch-up 实现 |
| **扩展** | 自定义事件/元数据的扩展点 | 扩展能力的具体实现 |

> **最好的协议是低约束的**——只规定必要的对象、状态机和事件格式，给 Runtime 留出最大实现自由度。
> **最好的 Runtime 是高内聚的**——在 Protocol 边界内把状态持久化、中断恢复、可观测性、控制面都做到位。

这也解释了为什么"哪个框架最好"是个伪问题——框架是 Runtime 实现，Protocol 才是应该长期投资的知识。理解 Protocol 边界后，你可以选择任何适合场景的 Runtime，甚至自己实现。

## 延伸阅读

九条设计原则的落地情况如何？五大主流框架在每条原则上的遵循程度星级评分、选型决策矩阵、关键发现分析，请见：

- [09 框架对比：九条设计原则遵循度评估](09-framework-comparison.md)
- [10 企业级 Agent Runtime 选型指南](10-enterprise-selection-guide.md)
- [11 跨维度分析与行业趋势](11-cross-dimensional-analysis.md)
- [12 内容评估与个人见解](12-content-evaluation.md)

---

- 上一章：[可观测性与可评测性](07-observability-evaluation.md)
- [下一章：框架对比](09-framework-comparison.md) →
