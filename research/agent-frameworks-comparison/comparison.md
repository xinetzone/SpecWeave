# Agent Harness 框架架构对比（七概念）

> **对比对象**：LangGraph / CrewAI / AutoGen / Claude Agent SDK
> **快照日期**：2026-11-10 — 这些框架迭代极快，选型前请以当前官方文档为准。

---

## 一、七概念总览表

| # | 概念维度 | LangGraph | CrewAI | AutoGen | Claude Agent SDK |
|---|---|---|---|---|---|
| ① | **核心架构范式** | 显式有向图状态机：节点 + 条件边，支持循环 | 角色型多 Agent：role/goal/backstory + Crew/Task | 事件驱动的对话式消息传递（GroupChat） | 自主 Agent Loop：evaluate→act→observe，复用 Claude Code harness |
| ② | **状态与持久化** | 一等公民：类型化 State + Checkpointer，每步自动快照（Memory/SQLite/Postgres/Redis） | 弱：Crew 内隐式传递；需用 Flows + `@persist` 显式管理 | 弱：默认内存会话历史；`save_state()`/`load_state()` 手动快照 | 服务端/会话态：Session 维护历史与上下文，自动 Compaction 压缩 |
| ③ | **控制流 / 编排** | 开发者显式画图，分支/循环/并行全部可见可测 | 顺序（sequential）或层级（hierarchical manager）；Flows 补确定性 | 对话轮次驱动（RoundRobin / Selector GroupChat），结构涌现 | 模型自主决定工具调用顺序，循环到无工具调用为止 |
| ④ | **多 Agent 协作** | 子图（subgraph）+ supervisor 模式，强 | 原生强项：多角色 Crew 协作 | 原生强项：多 Agent 群聊/辩论/评审 | 单 harness 为主 + Subagent 委派（非多-Agent-first） |
| ⑤ | **Human-in-the-Loop** | 强：interrupt 节点，在 checkpoint 暂停/审批/恢复 | 有限：回调/Flows 手动实现 | 中：UserProxyAgent 介入 | 有：权限系统（canUseTool）+ AskUserQuestion 工具 |
| ⑥ | **模型 / 运行时锁定** | 模型中立（任意 LLM / 本地模型） | 模型中立 | 模型中立 | **锁定 Claude**；1 session ≈ 1 子进程 |
| ⑦ | **生产成熟度 / 适用场景** | 最高：复杂、可审计、长运行、状态型生产系统 | 中（成长中）：快速多-Agent 原型、业务自动化 | 中：离线、质量优先的对话/评审；v0.4+ 已并入 Microsoft Agent Framework | 高（安全优先）：代码/文件/终端型自主 Agent、Claude 原生应用 |

---

## 二、一句话定位

- **LangGraph**（LangChain）：优化**控制力** — 你决定每一次状态转移。最强编排底座。
- **CrewAI**：优化**协作** — Agent 以团队方式工作，心智模型最直观，上手最快。
- **AutoGen**（Microsoft）：优化**对话涌现** — 适合辩论/评审类流程；新项目建议转向 Microsoft Agent Framework 1.0。
- **Claude Agent SDK**（Anthropic）：优化**自主性** — 给 Agent 一台"电脑"，复用 Claude Code 的成熟 agent loop + 工具 + 沙箱 + 权限。

---

## 三、选型决策要点

| 你的核心诉求 | 首选 |
|---|---|
| 复杂分支、可审计、状态持久化、故障恢复、HITL 审批 | **LangGraph** |
| 快速搭建角色型多 Agent、业务自动化 PoC | **CrewAI** |
| 离线、质量敏感的多 Agent 对话/评审（已有存量代码） | **AutoGen / AG2 / MAF** |
| 代码库操作、文件/终端型自主 Agent、押注 Claude | **Claude Agent SDK** |

**关键分界线不是"谁 Star 多"，而是你的应用更接近哪种运行时范式**：显式状态机 / 角色型多 Agent / 对话涌现 / 长程自主 harness。四者非互斥，常见组合是 LangGraph 做编排底座、特定节点内嵌 CrewAI 或 Claude Agent SDK。

---

## 四、2026 关键状态提示（易过时，需复核）

- **AutoGen**：2025-10 进入维护模式；v0.4+ 已并入 **Microsoft Agent Framework 1.0**（2026-04 发布）。新建项目优先用 MAF。社区分支 AG2 仍维护。
- **Claude Agent SDK**：2025-09-29 随 Sonnet 4.5 发布，由 Claude Code SDK 更名而来；Python + TypeScript 双一等公民。另有托管版 Claude Managed Agents（2026-04 beta）运行时在 Anthropic 侧。
- **CrewAI**：已是独立框架（不再依赖 LangChain）；率先原生支持 A2A 协议。
- **LangGraph**：被官方定位为**低层 orchestration runtime**，而非高层 Agent 模板；Deep Agents 是其上的开箱即用长程 harness。

---

## 主要参考来源
- JetBrains《LangGraph vs AutoGen vs CrewAI》[ref_1]
- spinny.dev / menuagentic 四框架架构对比 [ref_2]
- DEV Community（heu.ai）生产级架构对比 [ref_3]
- Anthropic 官方 Agent SDK 文档《How the agent loop works》[ref_4]
- Stackademic《Building Production AI Agents with Claude Agent SDK》[ref_5]
