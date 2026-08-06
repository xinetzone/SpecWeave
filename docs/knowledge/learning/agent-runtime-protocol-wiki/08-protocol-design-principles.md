# 08 Protocol对象映射与设计原则

## Protocol对象完整映射表

| Protocol对象/操作 | 外部契约（客户端能看到什么） | Runtime能力（内部如何兑现） | 对应章节 |
|-----------------|--------------------------|------------------------|---------|
| **Agent/Assistant** | Agent Card、能力声明、工具列表 | Agent注册、能力发现、权限边界 | 第01章 |
| **Thread/Session** | thread_id、创建/查询、历史消息 | 上下文边界、消息追加、状态关联 | 第03章 |
| **Run/Task** | run_id、状态机、创建/取消/重试 | Loop执行、调度、超时、资源隔离 | 第02章 |
| **Step** | step_id、类型（model/tool/handoff）、耗时 | 节点执行、Span追踪、进度统计 | 第02、07章 |
| **Message/Part** | 消息列表、角色、内容、附件 | 上下文窗口管理、裁剪、摘要 | 第03章 |
| **Tool** | 工具定义（JSON Schema）、调用参数/结果 | 工具执行、错误处理、权限检查 | 第05章 |
| **Event** | 事件类型、payload、顺序、event_id | 事件流生成、SSE推送、可恢复性 | 第05章 |
| **Artifact** | artifact_id、类型、归属Run、版本 | 文件存储、产物追踪、版本管理 | 第03章 |
| **Checkpoint** | checkpoint_id、parent_id、状态快照 | 快照存储、版本链、回滚恢复 | 第03、04章 |
| **Interrupt** | 中断载荷、等待类型（input/approval） | 暂停执行、保存状态、等待恢复 | 第04章 |
| **Resume** | resume指令、恢复值 | 从快照加载、继续执行 | 第04章 |
| **Stream** | SSE端点、Last-Event-ID | 事件持久化、Catch-up、多订阅者 | 第05章 |
| **Trace** | Trace ID、Span树、属性 | Span创建、上下文传播、导出 | 第07章 |

## 九条协议设计原则

基于全文分析，提炼出九条Agent Protocol设计原则：

### 原则一：对象先于API

Thread/Run/Step/Event/Artifact/Checkpoint 这六个对象的语义边界，比任何具体API方法名更持久。设计Protocol时先定义对象和它们的生命周期，再设计API。

### 原则二：Run是执行边界

所有和"一次具体执行"相关的概念（超时、取消、成本、权限、Trace、错误、产物归属）都应该挂在Run上，而不是Thread上。Thread承载上下文，Run承载执行。

### 原则三：Checkpoint是恢复契约

Checkpoint不只是"保存对话历史"，而是"可以从这里继续执行"的契约。这要求状态、工具副作用、外部资源、权限上下文都能重新对齐。

### 原则四：Event是一等公民

不要只在最后返回结果。状态变更、工具调用、产物增量、错误都应该以Event形式实时推送。前端和监控系统依赖的是事件流，不是最终答案。

### 原则五：错误优先作为数据

工具错误和LLM可处理的失败应该作为Error-as-Data返回给模型，而不是默认抛异常。只有模型无法处理的系统级故障才打断执行流。

### 原则六：控制面与数据面分离

权限、Guardrail、预算、审批是控制面；状态、事件、Trace、Artifact是数据面。控制面决定"能不能做"，数据面决定"做了什么"。

### 原则七：工具协议与Runtime解耦

工具定义、发现、调用应该独立于具体的Runtime Loop承载方式。MCP的价值正在于此——一个工具应该能被图式、代码式、托管式Runtime复用。

### 原则八：并发语义必须显式定义

同一个Thread上多个Run如何处理？排队？拒绝？取消？分叉？乐观并发？Protocol必须明确写进Run创建语义，不能留给实现自行决定。

### 原则九：可观测性从Day 1开始

Trace ID、Run ID、Step ID应该贯穿所有Event、Log和Artifact。没有可观测性的Protocol，一旦出问题就是黑盒。

## Protocol与Runtime边界划分

| 层面 | Protocol规定什么 | Runtime负责什么 |
|------|----------------|----------------|
| **对象** | 对象名称、ID、生命周期状态机 | 对象的内部表示、存储方式 |
| **操作** | 有哪些操作（create/cancel/resume/stream） | 操作的具体实现、调度算法 |
| **事件** | 事件类型、格式、顺序保证 | 事件生成时机、传输方式 |
| **错误** | 错误类型、错误码语义 | 错误检测、重试策略、回滚逻辑 |
| **流式** | SSE端点、事件格式、Last-Event-ID协议 | 事件持久化、Catch-up实现 |
| **扩展** | 自定义事件/元数据的扩展点 | 扩展能力的具体实现 |

> **最好的协议是低约束的**——只规定必要的对象、状态机和事件格式，给Runtime留出最大实现自由度。
> **最好的Runtime是高内聚的**——在Protocol边界内把状态持久化、中断恢复、可观测性、控制面都做到位。

这也解释了为什么"哪个框架最好"是个伪问题——框架是Runtime实现，Protocol才是应该长期投资的知识。理解Protocol边界后，你可以选择任何适合场景的Runtime，甚至自己实现。

## 延伸阅读：跨框架遵循度评估

九条设计原则的落地情况如何？五大主流框架（LangGraph、OpenAI Assistants、Agents SDK、AutoGen、Claude SDK）在每条原则上的遵循程度星级评分、选型决策矩阵、关键发现分析，请见：

→ **[09 框架对比：九条设计原则遵循度评估](09-framework-comparison.md)**

---
