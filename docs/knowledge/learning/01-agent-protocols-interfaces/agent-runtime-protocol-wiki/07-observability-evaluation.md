---
id: "agent-runtime-protocol-wiki-07"
title: "可观测性与可评测性：看见问题与评价质量"
source: "微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki/07-observability-evaluation.toml"
---
# 07 可观测性与可评测性：看见问题与评价质量

可观测性和可评测性是质量改进闭环的两个支柱：前者让你看见"发生了什么"，后者让你评价"做得好不好"。

## 两者关系

- **可观测性（Observability）**：偏运行时——你能不能在 Agent 执行时看到它在做什么？出问题时能不能追溯原因？
- **可评测性（Evaluation）**：偏事后——这次执行质量如何？好在哪里、差在哪里？如何改进？

没有可观测性，评测就没有数据来源；没有评测，观测数据就无法转化为改进信号。两者共同构成质量改进闭环：**看见问题 → 评价质量 → 归因分析 → 优化策略**。

## 第一部分：可观测性

### 通用概念

**子概念**：
- **Tracing**：一次执行的完整因果链——LLM 调用、工具调用、状态变更、Handoff
- **Logging**：结构化事件日志——每个 Step 的输入输出、耗时、Token 用量
- **Metrics**：聚合指标——成功率、平均延迟、Token 成本、工具调用频率
- **State Snapshot**：任意时刻的状态快照——用于调试"为什么走了这条路"
- **Event Stream**：实时事件流——用于前端展示、监控告警

### 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **Tracing** | LangSmith（一等公民） | Run Steps（有限） | SDK Traces | Console 日志 | 无内置 |
| **事件日志** | 结构化事件 | Run 事件 | 回调 Hook | 消息日志 | Event stream |
| **Token 统计** | Callback 回调 | `Usage` 对象 | Usage tracking | Usage tracking | Response 中的 usage |
| **执行回放** | **Checkpoint history** | Thread 消息历史 | 不支持 | 不支持 | 不支持 |
| **成本追踪** | LangSmith | OpenAI Dashboard | 手动 | 手动 | 手动 |

### Trace 最小语义模型：7 类 Span

要让 Trace 真正可用，至少需要标准化 7 类 Span：

| Span 类型 | 代表什么 | 关键属性 |
|---------|---------|---------|
| **Run Span** | 一次完整执行 | run_id、thread_id、agent_id、status、start/end_time |
| **Agent Span** | Agent 决策步骤 | agent_name、model、input_messages、output |
| **Generation Span** | 一次 LLM 调用 | model、prompt_tokens、completion_tokens、latency |
| **Tool Span** | 一次工具调用 | tool_name、input_args、output、error、latency |
| **Handoff Span** | Agent 切换 | from_agent、to_agent、reason、context_passed |
| **Guardrail Span** | 安全检查 | check_type、input/output、passed、action_taken |
| **Interrupt Span** | 中断暂停 | interrupt_type、payload、wait_time、resume_value |

这比普通日志强很多，因为它保留了父子关系和因果链。你不只是知道"调用了工具"，而是知道它属于哪次 Run、由哪个 Agent 触发、消耗多少、失败后是否重试、最终是否影响输出。

OpenTelemetry GenAI 正在朝这个方向标准化，但目前还在早期阶段，各框架的 Trace 格式互不兼容。

### 三类观测数据对比

Agent Runtime 的可观测性不能只看 Trace，还要同时看事件和状态：

| 数据类型 | 用途 | 实时性 | 粒度 | 存储 | 典型消费者 |
|---------|------|-------|------|------|----------|
| **Trace** | 调试、根因分析 | 事后 | 极细（Span 级） | 持久化（数据库） | 开发者、Debugger |
| **Event Stream** | 实时展示、监控 | 实时 | 中等（事件级） | 可丢弃（SSE） | 前端 UI、监控系统 |
| **State Snapshot** | 状态调试、回放 | 按需 | 完整状态 | 持久化（Checkpoint） | 开发者、重放工具 |

这三类数据解决不同问题：
- Trace 回答"这次执行内部发生了什么因果链"
- Event Stream 回答"现在正在发生什么"
- State Snapshot 回答"在这一时刻所有东西是什么状态"

> **Trace 解释因果，Event Stream 展示实时进展，State Snapshot 支持恢复和调试；三者打通后才能支撑评测闭环。**

### 当前框架可观测性三个薄弱点

1. **跨框架 Trace 语义不统一**：LangSmith 的 Trace、OpenAI 的 Run Steps、AutoGen 的日志格式完全不同，无法用同一个工具分析
2. **多 Agent Trace 断裂**：Handoff 和 Subagent 调用时，Trace 链经常断裂，无法跟踪完整任务流
3. **State 快照不可访问**：托管式 Runtime（OpenAI Assistants）完全不暴露内部状态，调试时只能猜

## 第二部分：可评测性

### 评测需要回答的五个问题

一个生产级 Agent 的评测系统，至少需要回答：

1. **结果好不好？**（Result Quality）——最终产物是否满足需求？
2. **过程对不对？**（Process Quality）——执行路径是否合理？有没有走弯路？
3. **成本值不值？**（Cost Efficiency）——Token、时间、工具调用量是否在预算内？
4. **哪里出了错？**（Error Attribution）——失败是因为 Prompt、工具、模型还是流程？
5. **如何改进？**（Actionable Feedback）——评测结果能不能指导下一次优化？

### 评测闭环需要的四类支撑

| 支撑类型 | 作用 | 当前状态 |
|---------|------|---------|
| **评测协议** | 标准化的评测输入输出格式 | 几乎空白，各框架自建 |
| **归因工具** | 把失败归因到具体 Step/工具/Prompt | 弱，主要靠人工看 Trace |
| **反馈机制** | 收集用户/人工对结果的反馈 | 有（Thumb up/down）但未闭环 |
| **Badcase 库** | 积累失败案例形成回归测试集 | 最薄弱，缺乏标准化 |

### 评测数据来源

评测不是凭空打分，需要以下数据支撑：
- **Trace 数据**：每一步的输入输出和决策理由
- **Artifact 数据**：最终产物的质量评估
- **人工反馈**：用户对结果的满意度、修正记录
- **对比数据**：同一个任务不同版本的结果对比（A/B 测试）

### 质量改进闭环

```
   ┌─────────────────────────────────────────────────┐
   │                                                 │
   ▼                                                 │
观测(Trace) ──► 评测(Score) ──► 归因(Analysis) ──► 优化(Fix)
   │                              │
   │                              └──► Badcase 入库
   │
   └──► 回归测试(Regression) ◄── 策略更新
```

这个闭环和传统软件测试的根本区别是：Agent 的错误不一定是 Bug，可能是模型判断失误、Prompt 歧义、工具描述不清等。评测的目标不是"通过/不通过"，而是持续发现改进点。

## 本章结论

可观测性回答"你能不能看见 Run 里发生了什么"，可评测性回答"你能不能判断这次 Run 做得好不好"。它们是质量改进闭环的基础——Trace 让问题可见，评测让质量可衡量，归因让改进有方向。

当前各框架在可观测性上差异巨大：LangGraph + LangSmith 是最完整的方案，OpenAI Assistants 提供有限的 Run Steps，AutoGen 和 Claude SDK 基本需要自建。可评测性更是普遍薄弱——缺乏标准化协议、归因工具和 Badcase 管理机制。

OpenTelemetry GenAI 正在推动 Trace 语义标准化，但距离生产可用还有距离。在此之前，团队需要自行建立 Trace、评测和 Badcase 闭环。

> **看见问题 → 评价质量 → 归因分析 → 优化策略**——这个闭环跑不起来，Agent 永远停留在"看起来很厉害但不敢用"的 Demo 阶段。

---

- 上一章：[多 Agent 协作](06-multi-agent.md)
- [下一章：Protocol 对象映射与设计原则](08-protocol-design-principles.md) →
