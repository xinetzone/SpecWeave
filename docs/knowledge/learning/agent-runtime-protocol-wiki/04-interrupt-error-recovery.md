# 04 中断与错误恢复

## 第一部分：中断与恢复——Human-in-the-Loop的真正基础设施

中断与恢复定义了 Agent 执行如何暂停（通常等待人类输入）以及如何从暂停点继续。这是 Human-in-the-Loop 的基础设施。

### 通用概念

**子概念**：
- **中断触发 (Interrupt Trigger)**：什么条件下暂停——到达特定节点、需要工具审批、主动请求人类输入
- **中断状态 (Interrupt State)**：暂停时保存了什么——完整状态快照、对话历史、什么都没保存
- **中断载荷 (Interrupt Payload)**：暴露给人类的信息——"Agent 想调用这个工具，你同意吗？"
- **恢复机制 (Resume Mechanism)**：人类如何提供输入并让 Agent 继续——提交数据、选择选项、直接回复

### 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **中断触发** | `interrupt()` / `interrupt_before` / `interrupt_after` | `requires_action`（仅工具审批） | Guardrail 拦截 | `HandoffTermination` | `client.interrupt()` |
| **中断状态** | Checkpoint（完整快照+pending_writes） | 服务端Thread（不透明） | 无持久化 | 对话历史（手动save） | 无持久化 |
| **中断载荷** | 任意JSON（`interrupt(payload)`） | `tool_calls`列表 | Guardrail错误信息 | `HandoffMessage` | 无 |
| **恢复机制** | `Command(resume=value)` | `submit_tool_outputs()` | 代码手动恢复 | 重新`run_stream(task=input)` | 新`query()` |
| **多点中断** | 支持（多节点设置interrupt_before） | 不支持 | 不支持 | 不支持 | 不支持 |

### 中断/恢复通用流程

不管框架如何实现，中断/恢复的通用流程是一样的：

```
Agent 执行 ──► 到达中断点 ──► 保存执行状态 ──► 向前端暴露中断载荷
                                                         │
                                                         ▼
                                                    人类查看/决策
                                                         │
                                                         ▼
Agent 恢复 ◄── 从快照加载状态 ◄── 接收人类输入 ◄── 前端提交
```

> **关键约束**：真正的中断/恢复**需要状态持久化**。如果框架没有持久化能力（Claude SDK、Agents SDK），就只能做同步的"ask and wait"——进程不能退出，用户必须立即回复。

### LangGraph interrupt/Command方案详解

LangGraph 的方案是目前最完整的，代码示例：

```python
# 节点内主动中断，传递任意载荷
def review_node(state):
    decision = interrupt({
        "question": "要发布这篇文章吗？",
        "draft": state["draft"],
        "options": ["发布", "修改", "丢弃"]
    })
    # decision 是人类通过 Command(resume=...) 传入的值
    if decision == "发布":
        return {"status": "published"}

# 人类回复
graph.invoke(Command(resume="发布"), config)
```

### 四种中断方案设计决策对比

| 方案 | 优势 | 劣势 |
|------|------|------|
| **LangGraph：通用 interrupt + Command** | 任意节点、任意载荷、完整状态保存 | 需要Checkpointer，学习成本高 |
| **OpenAI：requires_action** | 简单，服务端托管状态 | 只能审批工具调用，不能主动问用户问题 |
| **AutoGen：HandoffTermination** | 用Handoff统一了人机和Agent间交互 | 状态需手动保存，恢复不是从断点继续 |
| **Claude SDK：interrupt()** | 极简——发信号停止 | 没有恢复，只能重新开始 |

### 中断恢复本章结论

中断/恢复回答"任务暂停后能否从原位置继续"。它不是独立能力，而是状态管理的直接延伸：只有 Runtime 能保存精确状态，才可能几小时后从同一个断点继续。

中断/恢复是各框架实现差距最大的维度。LangGraph 的方案领先，是因为它把 Checkpoint 和 Interrupt 深度整合；其他框架要么只支持工具审批，要么只能做同步等待或重新开始。

> **Human-in-the-Loop 的基础设施不是一个 ask-user API，而是"状态快照 + 中断载荷 + 恢复指令 + 权限上下文"的组合能力。**

---

## 第二部分：错误恢复——Agent应该先把错误当数据看

错误恢复定义了 Agent 执行过程中发生故障时，Runtime 如何检测、表示和处理错误。

### 通用概念

**子概念**：
- **错误检测 (Detection)**：在哪一层发现错误——工具执行、LLM调用、状态更新
- **错误表示 (Representation)**：错误以什么形式存在——Exception、错误数据、状态标记
- **恢复策略 (Recovery Strategy)**：如何处理错误——重试、回滚、跳过、交给LLM
- **部分进度保留 (Partial Progress)**：失败时已完成的步骤是否保留

### 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen |
|------|-----------|------------------|------------|---------|
| **错误表示** | Exception → pending_writes | Run status = failed | Python Exception | Exception in message |
| **重试** | RetryPolicy（per-node配置） | 自动（不透明） | 手动 | 手动 |
| **回滚** | **Checkpoint回滚** | N/A（服务端托管） | N/A | N/A |
| **部分进度** | **Checkpoint保留** | Thread消息保留 | 丢失 | 对话保留 |
| **错误传播** | 可配置（error-as-data或raise） | 事件通知 | 抛给调用者 | 消息传给GroupChat |

### 两种错误哲学：Error-as-Data vs Error-as-Exception

```
Error-as-Exception (传统)              Error-as-Data (Agent原生)
工具调用 ──► 失败 ──► 抛异常          工具调用 ──► 失败 ──► 返回错误信息
                  │                                        │
                  ▼                                        ▼
         框架/开发者 try/catch                        LLM 看到错误信息
         决定重试/放弃                           LLM 自主决定下一步
                                              (重试/换工具/告知用户)
```

> Agent Runtime 更适合把可理解的工具错误作为数据返回给模型，而不是默认打断执行。即 Error-as-Data，因为**LLM 有足够的推理能力来处理工具错误**。这个假设在旗舰级别的模型上是成立的——它们能理解"API返回429限频"并决定等待后重试。

### LangGraph Checkpoint回滚机制

LangGraph 是唯一支持 **Checkpoint回滚**的框架：

1. 节点A执行成功 → 自动保存Checkpoint A
2. 节点B执行失败 → 异常被记录到pending_writes
3. 重新invoke时 → 从Checkpoint A恢复，只重试节点B
4. 已完成的节点A **不会重新执行**

这对长时间运行的工作流至关重要。一个10步的Agent在第8步失败了，你不需要重跑前7步。

### 错误恢复本章结论

错误恢复回答"失败是否会抹掉已有进度"。它同样依赖状态管理：没有Checkpoint，失败只能重跑；有Checkpoint，Runtime才能保留已完成步骤并只重试失败部分。

Agent Runtime 应默认采用 Error-as-Data。Agent 的核心价值是自主决策，工具错误也应该优先作为可理解的数据交给模型处理；只有模型无法处理的系统级故障，才应该作为Exception向上抛。

> **Checkpoint回滚是生产环境的明确缺口。** 长任务执行到后半段失败时，是否能从最近稳定状态恢复，直接决定这个Runtime能否承载真实业务流程。

---
