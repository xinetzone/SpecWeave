# 07 可观测性与可评测性：看见问题与评价质量

可观测性和可评测性是质量改进闭环的两个支柱：前者让你看见"发生了什么"，后者让你评价"做得好不好"。

## 两者关系

- **可观测性（Observability）**：偏运行时——你能不能在Agent执行时看到它在做什么？出问题时能不能追溯原因？
- **可评测性（Evaluation）**：偏事后——这次执行质量如何？好在哪里、差在哪里？如何改进？

没有可观测性，评测就没有数据来源；没有评测，观测数据就无法转化为改进信号。两者共同构成质量改进闭环：**看见问题 → 评价质量 → 归因分析 → 优化策略**。

## 第一部分：可观测性

### 通用概念

**子概念**：
- **Tracing**：一次执行的完整因果链——LLM调用、工具调用、状态变更、Handoff
- **Logging**：结构化事件日志——每个Step的输入输出、耗时、Token用量
- **Metrics**：聚合指标——成功率、平均延迟、Token成本、工具调用频率
- **State Snapshot**：任意时刻的状态快照——用于调试"为什么走了这条路"
- **Event Stream**：实时事件流——用于前端展示、监控告警

### 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen |
|------|-----------|------------------|------------|---------|
| **Tracing** | LangSmith（一等公民） | Run Steps（有限） | SDK Traces | Console日志 |
| **Logging** | 结构化事件 | Run事件 | 回调Hook | 消息日志 |
| **Metrics** | LangSmith监控 | 平台提供 | 需自建 | 需自建 |
| **State Snapshot** | Checkpoint + get_state | Thread消息（不透明） | 无内置 | 需手动保存 |
| **Event Stream** | 多模式stream | SSE | StreamEvent | 异步生成器 |

### Trace最小语义模型

要让Trace真正可用，至少需要标准化7类Span：

| Span类型 | 代表什么 | 关键属性 |
|---------|---------|---------|
| **Run** | 一次完整执行 | run_id、thread_id、agent_id、status、start/end_time |
| **Agent** | Agent决策步骤 | agent_name、model、input_messages、output |
| **Generation** | LLM调用 | model、prompt_tokens、completion_tokens、latency |
| **Tool** | 工具调用 | tool_name、input_args、output、error、latency |
| **Handoff** | Agent切换 | from_agent、to_agent、reason、context_passed |
| **Guardrail** | 安全检查 | check_type、input/output、passed、action_taken |
| **Interrupt** | 中断暂停 | interrupt_type、payload、wait_time、resume_value |

OpenTelemetry GenAI正在朝这个方向标准化，但目前还在早期阶段，各框架的Trace格式互不兼容。

### 三类观测数据对比

| 数据类型 | 用途 | 实时性 | 粒度 | 存储 | 典型消费者 |
|---------|------|-------|------|------|----------|
| **Trace** | 调试、根因分析 | 事后 | 极细（Span级） | 持久化（数据库） | 开发者、Debugger |
| **Event Stream** | 实时展示、监控 | 实时 | 中等（事件级） | 可丢弃（SSE） | 前端UI、监控系统 |
| **State Snapshot** | 状态调试、回放 | 按需 | 完整状态 | 持久化（Checkpoint） | 开发者、重放工具 |

这三类数据解决不同问题：
- Trace回答"这次执行内部发生了什么因果链"
- Event Stream回答"现在正在发生什么"
- State Snapshot回答"在这一时刻所有东西是什么状态"

### 当前框架可观测性三个薄弱点

1. **跨框架Trace语义不统一**：LangSmith的Trace、OpenAI的Run Steps、AutoGen的日志格式完全不同，无法用同一个工具分析
2. **多Agent Trace断裂**：Handoff和Subagent调用时，Trace链经常断裂，无法跟踪完整任务流
3. **State快照不可访问**：托管式Runtime（OpenAI Assistants）完全不暴露内部状态，调试时只能猜

## 第二部分：可评测性

### 评测需要回答的五个问题

一个生产级Agent的评测系统，至少需要回答：

1. **结果好不好？**（Result Quality）——最终产物是否满足需求？
2. **过程对不对？**（Process Quality）——执行路径是否合理？有没有走弯路？
3. **成本值不值？**（Cost Efficiency）——Token、时间、工具调用量是否在预算内？
4. **哪里出了错？**（Error Attribution）——失败是因为Prompt、工具、模型还是流程？
5. **如何改进？**（Actionable Feedback）——评测结果能不能指导下一次优化？

### 评测闭环需要的四类支撑

| 支撑类型 | 作用 | 当前状态 |
|---------|------|---------|
| **评测协议** | 标准化的评测输入输出格式 | 几乎空白，各框架自建 |
| **归因工具** | 把失败归因到具体Step/工具/Prompt | 弱，主要靠人工看Trace |
| **反馈机制** | 收集用户/人工对结果的反馈 | 有（Thumb up/down）但未闭环 |
| **Badcase库** | 积累失败案例形成回归测试集 | 最薄弱，缺乏标准化 |

### 评测数据来源

评测不是凭空打分，需要以下数据支撑：
- **Trace数据**：每一步的输入输出和决策理由
- **Artifact数据**：最终产物的质量评估
- **人工反馈**：用户对结果的满意度、修正记录
- **对比数据**：同一个任务不同版本的结果对比（A/B测试）

### 质量改进闭环

```
   ┌─────────────────────────────────────────────────┐
   │                                                 │
   ▼                                                 │
观测(Trace) ──► 评测(Score) ──► 归因(Analysis) ──► 优化(Fix)
   │                              │
   │                              └──► Badcase入库
   │
   └──► 回归测试(Regression) ◄── 策略更新
```

这个闭环和传统软件测试的根本区别是：Agent的错误不一定是Bug，可能是模型判断失误、Prompt歧义、工具描述不清等。评测的目标不是"通过/不通过"，而是持续发现改进点。

## 本章结论

可观测性回答"你能不能看见Run里发生了什么"，可评测性回答"你能不能判断这次Run做得好不好"。它们是质量改进闭环的基础——Trace让问题可见，评测让质量可衡量，归因让改进有方向。

当前各框架在可观测性上差异巨大：LangGraph + LangSmith 是最完整的方案，OpenAI Assistants 提供有限的Run Steps，AutoGen和Claude SDK基本需要自建。可评测性更是普遍薄弱——缺乏标准化协议、归因工具和Badcase管理机制。

OpenTelemetry GenAI 正在推动Trace语义标准化，但距离生产可用还有距离。在此之前，团队需要自行建立Trace、评测和Badcase闭环。

> **看见问题 → 评价质量 → 归因分析 → 优化策略**——这个闭环跑不起来，Agent永远停留在"看起来很厉害但不敢用"的Demo阶段。

---
