# 03 状态管理：生产级Agent的分水岭（Part 2）

状态管理定义了 Agent 执行过程中的可变数据如何表示、持久化、版本化和恢复。协议视角下，状态管理还要决定哪些状态可以被外部看见：Thread history、Task status、Artifact、State Snapshot、Trace metadata，分别暴露给不同类型的客户端。

## 通用概念

**子概念**：
- **状态表示 (State Schema)**：数据的形状——类型化的结构（TypedDict）、消息列表、JSON blob
- **状态持久化 (Persistence)**：数据存到哪——内存、数据库、服务端托管
- **状态版本化 (Versioning)**：能否查看/回滚历史——快照链、消息追加、无版本
- **状态作用域 (Scope)**：数据对谁可见——全局、Agent 级、Channel 级
- **增量更新 (Update Mechanism)**：如何修改状态——Reducer 函数、直接覆盖、追加消息

## 持久化光谱

各框架在状态持久化上的立场差异巨大，形成了一条光谱：

- **最左端（无持久化）**：内存状态，进程退出即丢失。代表：Claude SDK、Agents SDK、AutoGen默认
- **中间层（自建持久化）**：开发者自行实现Checkpointer，可选择PG/Redis/SQLite。代表：LangGraph
- **最右端（服务端托管）**：状态完全由平台管理，开发者看不到内部结构。代表：OpenAI Assistants

> 状态持久化从"进程内临时状态"到"服务端托管状态"形成一条光谱，生产 Agent 必须明确自己站在哪一段。

## 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **状态表示** | TypedDict + Channel级Reducer | Thread（消息列表+元数据） | RunContext（Python对象） | ChatCompletionContext + 共享状态 | 对话历史（隐式） |
| **持久化** | Checkpointer（PG/Redis/SQLite） | 服务端托管（不透明） | 无（手动 save_state/load_state） | 无内置 | 无内置 |
| **版本控制** | Checkpoint链（parent_id，类Git） | Thread 消息历史（追加制） | 无 | 无 | 无 |
| **状态作用域** | Channel 级（每个字段独立Reducer） | Thread 级 | Agent 级 | Agent/Team 级 | Session 级 |
| **增量更新** | Annotated[list, add_messages] 等Reducer | 追加消息 | 直接修改 | 追加消息 | 直接修改 |

## 状态五层分层：不要把所有东西都叫Memory

Agent 领域最容易混淆的词是 Memory。更清晰的做法是把状态拆成五层：

| 层级 | 典型名称 | 内容 | 主要问题 |
|------|---------|------|---------|
| **Conversation** | Messages / Thread | 用户、模型、工具消息 | 上下文窗口、裁剪、摘要 |
| **Run State** | State / Context | 当前执行的结构化变量 | 类型、Reducer、并发更新 |
| **Checkpoint** | Snapshot / Savepoint | 某一步之后的完整可恢复状态 | 存储、版本、回滚 |
| **Artifact** | File / Report / Code diff | Agent 产出的外部结果 | 生命周期、权限、可追溯 |
| **Semantic Memory** | Long-term Memory | 跨会话沉淀的用户偏好或知识 | 检索、污染、遗忘 |

> 很多框架说自己支持 Memory，实际只支持其中一层。生产设计必须先问清楚：要保存的是对话、运行状态、可恢复快照、文件产物，还是长期记忆？

## Session/Thread/Run/Step/Checkpoint/Artifact边界关系

- **Session/Thread**：长期上下文边界，回答"这是谁的哪段任务"
- **Run**：一次执行边界，回答"这次具体跑了什么"
- **Step**：最小可观测执行单元，回答"哪一步调用了模型或工具"
- **Checkpoint**：恢复边界，回答"失败后从哪里继续"
- **Artifact**：产物边界，回答"结果在哪里、由哪次执行产生"

OpenAI Assistants 把 Thread 和 Run 显式暴露出来；LangGraph 把 Thread 作为 configurable.thread_id，把 Run 隐含在一次 invoke/stream 中；Agents SDK 更强调 Runner 和 Session。名字不同，但边界是相同的。

如果所有 Runtime 都能基于统一 Agent Protocol 表达 Thread -> Run -> Step -> Artifact 这条链路，那么控制台、前端、评测系统、审计系统就不需要理解每个框架的内部状态结构。

## 并发Run五种策略对比

并发会话处理的关键，是不要把 Thread / Session 和 Run 混成一个概念。Thread / Session 是长期上下文边界，Run 是一次执行边界；同一个用户可以有多个 Thread，同一个 Thread 也可能在短时间内收到多个 Run 请求。

生产 Runtime 必须明确一个问题：**同一个 Thread 上是否允许多个 Run 同时执行？**

| 策略 | 行为 | 优势 | 代价 | 典型场景 |
|------|------|------|------|---------|
| **串行队列** | 同一 Thread 的 Run 按顺序排队执行 | 语义最稳定，消息顺序清晰 | 延迟增加，长任务会阻塞后续输入 | 多轮对话、客服、需要强上下文连续性的任务 |
| **拒绝新 Run** | Thread 已有运行中 Run 时直接返回 conflict/busy | 实现简单，避免状态冲突 | 用户体验生硬，需要前端解释和重试 | 后台任务、审批流、一次只允许一个执行的场景 |
| **取消并覆盖** | 新 Run 到来时取消旧 Run，用最新输入重新执行 | 交互体验直接，适合"以最后一次为准" | 旧 Run 的部分进度和副作用需要可追溯或可回滚 | 搜索、草稿生成、用户频繁改需求的交互 |
| **分叉新 Run** | 从同一个 Checkpoint 分叉出多个 Run 并行执行 | 适合 A/B 测试、方案比较、探索式任务 | 需要清晰标记分支、Artifact 归属和最终采纳关系 | Prompt对比、策略实验、研究任务 |
| **乐观并发** | Run 开始时记录 state version，提交时检查是否冲突 | 并发度高，适合低冲突写入 | 冲突检测和合并逻辑复杂 | 多Agent并行写不同state channel |

这些策略没有绝对优劣，关键是把语义放进协议和 Runtime 状态机里。客户端需要知道新 Run 是被排队、拒绝、取消旧任务、创建分支，还是等待冲突解决；观测系统也要能把每个事件、Artifact 和错误归属到具体 Run。

## 五类并发冲突

并发写状态时，Runtime 至少要处理五类冲突：

- **消息顺序冲突**：两个 Run 同时向同一个 Thread 追加消息，最终历史如何排序
- **状态版本冲突**：两个 Run 基于同一份 State Snapshot 修改同一个字段，谁覆盖谁
- **Artifact 归属冲突**：多个 Run 生成同名文件或报告，哪个是正式产物
- **Workspace 副作用冲突**：多个 Run 同时改同一份代码、浏览器页面或外部系统资源
- **事件流归属冲突**：前端同时订阅多个 Run 时，如何用 run_id、step_id、event_id 恢复和去重

> Thread 不应该被简单当成一把全局锁。更稳的设计是：Thread 承载上下文，Run 承载执行，Checkpoint 承载版本，Event 承载进展，Artifact 承载产物；并发控制策略则明确写进 Run 创建语义和状态迁移规则。

## 状态迁移与Schema演进

持久化一旦进入生产，就会遇到 Schema 演进问题：今天保存的 Checkpoint，三个月后代码升级还能不能恢复？

生产 Runtime 需要考虑：

- **状态版本号**：每个快照记录 schema version
- **迁移函数**：加载旧快照时转换到新结构
- **兼容窗口**：保留多久的旧状态可恢复
- **失败策略**：迁移失败时是终止、降级，还是创建新 Run

这也是服务端托管状态和自建 Checkpoint 的核心差异：托管方案隐藏迁移复杂度，但也隐藏了控制权；自建方案控制力强，但必须承担 schema 演进成本。

## LangGraph Checkpoint模型 vs OpenAI Thread模型

### LangGraph Checkpoint模型（最完整方案）

- 每个节点执行后自动快照（不需要手动调用 save）
- 快照具备链式结构，支持"时间旅行"（任意节点回滚、重放）
- Content-addressed blob 存储，类似 git 的存储方式，大状态只存一次
- **允许运行时修改 Agent 的上下文信息**——意味着可以运行时让 Agent 自进化

**代价**：学习曲线陡峭，Reducer 函数的语义需要理解，Checkpoint 存储占空间。

### OpenAI Thread模型（另一极端）

- 你不需要（也无法）管理状态——服务端全包
- 状态只能通过追加消息来修改，不能直接改内部状态
- 没有回滚——你只能创建新 Thread

**代价**：零控制权。调试困难，无法做"如果当时走了另一条路"的分析。

### AutoGen/Claude SDK/Agents SDK

基本没有内置持久化，把这个问题留给开发者。对于短生命周期的 Agent 这没问题，但一旦需要跨请求保持状态（如人机协作工作流、事后评测、版本管理等），就必须自己搭建。

## 本章结论

状态管理回答"Run 执行到一半时，哪些东西必须被保存，以及多个 Run 同时发生时如何保持一致"。它承接上一章的 Runtime Loop，也直接支撑后面的中断恢复、错误回滚、并发会话和执行回放。

> **状态持久化是区分"玩具"和"生产"的分水岭。** 没有持久化的 Agent 无法在进程崩溃后恢复，无法支持真正的 Human-in-the-Loop，无法调试"为什么 Agent 走了这条路"，也无法从同一个状态分叉执行不同策略。并发 Run 进一步要求 Runtime 明确队列、拒绝、取消覆盖、分叉和乐观并发等策略。

真正难的不是保存，而是恢复。恢复要求状态 schema、工具副作用、外部资源、权限上下文都能重新对齐；只把 messages 存进数据库，并不等于具备生产级状态管理。

---
