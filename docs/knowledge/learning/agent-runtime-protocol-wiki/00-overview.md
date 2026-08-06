# Agent Runtime Protocol 总览

> 生产级 Agent 运行时协议对象与八大维度完整解析：框架会更迭，协议对象更稳定

## 这是什么？

本文系统梳理了微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）的核心内容，以 **Agent Protocol** 为主线，将 Agent Runtime 拆解为一组可协议化的对象、操作和状态机。

Agent 框架层出不穷：LangGraph 讲 Checkpoint，OpenAI 讲 Thread 和 Run，A2A 讲 Task，AG-UI 讲 Event，Deep Agents 又引入 Todo、Subagent 和 Virtual Filesystem。名字越来越多，API 越来越像一套套独立世界观。

> **框架名词在变，但底层问题始终围绕任务、上下文、步骤、事件、状态和产物展开。**

## 核心问题

所有 Agent 框架都在回答同一个底层问题：

> **一个 Agent 任务，如何被启动、携带上下文、持续观测、中断恢复，以足够低的使用成本完成执行，并最终产生产物？**

换成协议视角：

> **一个生产级 Agent Protocol 应该包括什么？为什么这些协议对象会比具体框架 API 更稳定？**

## 六大核心协议对象

理解 Agent Runtime Protocol 的入口是这 6 个核心对象：

| 对象 | 人话解释 | 它回答的问题 |
|------|---------|-------------|
| **Thread / Session** | 一段长期上下文 | 这是谁的哪段任务？ |
| **Run / Task** | 一次具体执行 | 这次具体跑了什么？ |
| **Step** | 执行中的一个可观测步骤 | 哪一步调用了模型、工具或子 Agent？ |
| **Event** | 执行过程中的进展变化 | 现在发生了什么？ |
| **Artifact** | Agent 产出的正式结果 | 结果在哪里，由哪次执行产生？ |
| **Checkpoint** | 可以恢复的执行快照 | 失败或中断后从哪里继续？ |

围绕这 6 个对象，生产级 Agent Protocol 至少还要表达 `stream / interrupt / resume / cancel / retry` 这些生命周期操作。

## 作者五个核心观点

1. **Agent Runtime 的核心不是模型调用，而是任务生命周期管理** —— Runtime 是模型调用之外的那层执行系统，负责任务如何开始、运行、暂停、恢复、结束。

2. **Thread/Run/Step/Event/Artifact/Checkpoint 会成为跨框架的稳定对象** —— 不同标准和框架正在围绕这六个对象收敛。

3. **执行模型不会统一**：Runtime Loop 承载方式和编排协议会长期分层演进 —— 图式/代码式/托管式 Runtime 会按场景并存；ReAct、Plan-and-Execute 等编排协议也会长期共存。

4. **真正区分玩具 Agent 和生产 Agent 的，是状态持久化、中断恢复、可观测性和可评测性** —— 没有持久化的 Agent 无法在进程崩溃后恢复，无法支持真正的 Human-in-the-Loop。

5. **值得看的不是某个框架 API，而是协议边界和 Runtime 抽象** —— 理解 Protocol 和 Runtime 的关系后，再看新框架时就能快速判断它的价值。

## 三层概念边界

讨论 Agent Protocol 时，最容易把三层东西混在一起：

| 层级 | 例子 | 解决的问题 |
|------|------|-----------|
| **具体协议标准** | A2A、AG-UI、LangChain Agent Protocol、AITP、ACP | 不同系统如何通信，如何描述任务、消息、事件和产物 |
| **通用协议对象** | Thread、Run、Step、Event、Artifact、Checkpoint | 外部世界如何稳定理解一次 Agent 任务 |
| **Runtime 实现能力** | 状态持久化、中断恢复、可恢复流、权限控制、可观测性 | Runtime 内部如何兑现这些对象和状态机 |

本文重点讨论**第二层：通用协议对象**。具体协议标准和框架实现只作为证据，用来说明这些对象正在跨系统收敛。

## Runtime 的五类管理职责

Agent Runtime 不是"一次模型调用"，而是模型调用之外的那层执行系统。它至少要管理五类事情：

- **生命周期**：一次任务如何开始、运行、暂停、恢复、结束
- **上下文**：哪些消息、文件、状态、外部资源对当前执行可见
- **调度**：下一步调用模型、工具、子 Agent，还是等待人类
- **控制面**：权限、Guardrail、取消、超时、预算、并发限制
- **数据面**：状态快照、事件流、Trace、Artifact、成本数据如何流动

## Wiki 导航

| 章节 | 内容 |
|------|------|
| [01 Protocol边界与最小生命周期](01-protocol-boundary-lifecycle.md) | 三层概念区分、Runtime Protocol定义、最小生命周期、现有协议收敛对比 |
| [02 执行模型（Part 1）](02-execution-model.md) | Runtime Loop承载方式、编排协议模式、Agent Harness、跨框架映射、Workspace/Sandbox |
| [03 状态管理（Part 2）](03-state-management.md) | 持久化光谱、状态五层分层、并发Run策略、Checkpoint模型对比、Schema演进 |
| [04 中断与错误恢复](04-interrupt-error-recovery.md) | Human-in-the-Loop基础设施、Error-as-Data哲学、Checkpoint回滚机制 |
| [05 工具协议与流式输出（Part 3）](05-tools-streaming.md) | MCP详解、工具协议独立分层、可恢复流、任务事件流vs token打字机 |
| [06 多Agent协作（Part 4）](06-multi-agent.md) | 五种编排模式对比、跨框架映射、设计决策分析、"先做好单Agent"建议 |
| [07 可观测性与可评测性](07-observability-evaluation.md) | Trace最小语义模型、三类观测数据、评测闭环、质量改进链路 |
| [08 Protocol对象映射与设计原则](08-protocol-design-principles.md) | 完整对象映射表、九条设计原则、Protocol与Runtime边界划分 |
| [09 框架对比：九条设计原则遵循度评估](09-framework-comparison.md) | 五大框架星级评分对比、选型决策矩阵、实践启示 |
| [10 企业级选型指南](10-enterprise-selection-guide.md) | 企业级五大公理、五大扩展维度、分层选型架构、典型场景推荐、可交互决策矩阵 |
| [11 跨维度分析与行业趋势](09-cross-dimensional-analysis.md) | 设计决策持久性判断、收敛趋势预测、开发者投入方向建议、从零设计建议 |
| [12 内容评估与个人见解](10-content-evaluation.md) | 原文价值评估、Agent基础设施演进趋势思考 |
| [13 总结、FAQ与资源](11-summary-faq-resources.md) | 核心要点总结、10个常见问题、术语对照表、完整资源链接 |

## 阅读路径建议

全文按任务生命周期组织阅读：
1. **创建任务** → Thread/Run/Task → 第01章
2. **携带上下文** → Message/State/Workspace → 第02、03章
3. **执行步骤** → Step/Action/Tool call → 第02、05章
4. **观察事件** → Event/Stream/Trace → 第05、07章
5. **中断恢复** → Interrupt/Resume/Checkpoint → 第04章
6. **产生产物** → Artifact/Final output → 第03章
7. **评测审计** → Trace/Eval/Feedback → 第07章

---

**原文参考**：https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg
**来源**：微信公众号「阿里云开发者」
**日期**：2026-07-04
