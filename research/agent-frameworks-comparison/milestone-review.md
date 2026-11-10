# Agent Harness 框架里程碑复盘报告（七概念）

> **对象**：LangGraph / CrewAI / AutoGen / Claude Agent SDK
> **报告类型**：里程碑复盘 + 深度洞察
> **快照日期**：2026-11-10 — 框架迭代极快，关键日期已交叉验证，少数有出入处已标注区间。

---

## 一、执行摘要（TL;DR）

2025–2026 是 Agent 框架从"实验玩具"走向"生产底座"的分水岭。四个框架沿**三条不同的架构范式**各自走到 1.0/GA：

- **LangGraph** 率先以"**可持久化运行时**"定义生产标准（1.0 GA，2025-10-22）。
- **AutoGen** 退出历史舞台：进入维护模式，v0.4+ 并入 **Microsoft Agent Framework 1.0**（2026-04）。
- **Claude Agent SDK** 开辟"**coding harness 复用**"新范式：把成熟 agent loop 开放给通用 Agent（2025-09-29）。
- **CrewAI** 守住"**最快出活的角色型多 Agent**"心智位，持续活跃迭代。

**一句话洞察**：竞争焦点已从"谁的 API 优雅"转向"**状态活在哪、谁负责别把它弄丢**"——即 durable execution 与 runtime 归属。

---

## 二、里程碑时间线（Milestone Timeline）

| 时间 | 框架 | 里程碑事件 | 意义 |
|---|---|---|---|
| 2024 | LangGraph / CrewAI | 两者相继发布 | 图范式 vs 角色范式确立 |
| 2025-01 | AutoGen | v0.4 重写：actor 模型 + 事件驱动核心 | 从对话式转向分布式事件架构 |
| 2025-09-29 | Claude Agent SDK | 随 Sonnet 4.5 发布，由 Claude Code SDK 更名 | coding harness 首次产品化开放 |
| 2025-10 | AutoGen | 进入**维护模式**，社区接管 | 官方投入转向 MAF |
| 2025-10-22 | LangGraph | **1.0 GA**：durable execution + checkpoint + 一等 HITL | 定义"可持久化 Agent 运行时"标准 |
| 2026-Q1 | LangGraph | Postgres / Redis checkpoint 包产线稳定 | 生产级持久化落地 |
| 2026-04（2–7，各源有出入） | Microsoft | **MAF 1.0 GA**：Semantic Kernel + AutoGen 合并 | 结束 Microsoft 内部双框架内耗 |
| 2026-04（beta） | Anthropic | Claude Managed Agents（托管版）beta | runtime 归属进一步上移到厂商侧 |
| 2026-06（BUILD 2026） | Microsoft | MAF Agent Harness / Hosted Agents / CodeAct | MAF 也补齐 coding-harness 能力 |
| 2026-10 | LangGraph | 1.2.x 持续迭代（1.2.16） | v1 线保持无破坏性演进 |

> ⚠️ **考据提示**：MAF GA 日期各来源分别写 4-2 / 4-3 / 4-7，官方 BUILD 博客为 **4-2**，主流二手源多为 **4-3**。此处采信官方口径区间，不强行取单一日期。

---

## 三、七概念对比总表（延续上一版）

| # | 概念维度 | LangGraph | CrewAI | AutoGen | Claude Agent SDK |
|---|---|---|---|---|---|
| ① | 核心架构范式 | 显式有向图状态机 | 角色型多 Agent | 事件驱动对话式消息传递 | 自主 Agent Loop（复用 Claude Code harness） |
| ② | 状态与持久化 | 一等公民·每步 checkpoint | 弱·需 Flows+`@persist` | 弱·手动 save/load_state | 会话态·自动 Compaction |
| ③ | 控制流/编排 | 显式画图·可测 | 顺序/层级 manager | 对话轮次涌现 | 模型自主工具循环 |
| ④ | 多 Agent 协作 | 子图+supervisor | 原生强 | 原生强（群聊/辩论） | 单 harness+subagent |
| ⑤ | Human-in-the-Loop | 强·interrupt | 有限 | 中·UserProxyAgent | 权限系统+AskUserQuestion |
| ⑥ | 模型/运行时锁定 | 模型中立 | 模型中立 | 模型中立 | **锁定 Claude** |
| ⑦ | 成熟度/场景 | 最高·复杂可审计生产 | 中·快速多Agent原型 | 转型中·并入 MAF | 高·代码/文件自主 Agent |

---

## 四、四项深度洞察（Insights）

### 洞察 ①：真正的分界线是"状态归属"，不是功能表
四个框架把同一个"research→draft→review"流程连起来，代码几乎一样。差异在崩溃那一刻显现：
- **LangGraph** 从上一个 checkpoint 重放恢复；
- **Claude Managed Agents** 状态从不在你机器上，thread 永不丢；
- **CrewAI / 裸 AutoGen** 从零重启。

→ 选型第一问应是：**"失败一次有多贵？需要可恢复/可审计吗？"** 而非 star 数。

### 洞察 ②："coding harness 复用"正成为独立新范式
Thoughtworks Technology Radar（2026-11）已把 **"Coding harness for general-purpose agents"** 列为值得尝试的技术：非编码类 Agent（文档处理、运维、迁移规划）直接复用成熟 coding agent 的 runtime（Claude Agent SDK / Codex SDK / MAF Agent Harness）。
- **收益**：context compaction、session 持久化、headless 执行开箱即用；
- **代价**：牺牲控制力换取久经考验的 runtime；内置 prompt 偏向"写代码+跑代码"，需为自身领域改写；token 消耗高。

→ 这解释了为什么 Claude Agent SDK 和 MAF Agent Harness 在 2026 快速补位。

### 洞察 ③：Microsoft 的"收敛"是本轮最具结构性的事件
MAF 1.0 终结了 Semantic Kernel（企业）与 AutoGen（研究）的双线内耗：
- SK 作底座（session 状态、中间件、遥测），AutoGen 的多 Agent 概念重建为**类型化图工作流**；
- 控制流从"对话涌现"转为"typed edges 按输入就绪激活 executor"——本质上向 LangGraph 的显式图范式靠拢；
- .NET + Python 双一等公民 + 原生 MCP/A2A，是 Azure/.NET 阵营的默认选择。

→ **范式趋同信号**：对话式编排在生产场景败给显式图编排。

### 洞察 ④：MCP 成为跨框架"去锁定"的通用层
四者（及 MAF）现在均原生支持 **MCP**；MCP 已于 2025-12 捐给 Linux 基金会下的 Agentic AI Foundation。
- 含义：针对 MCP 构建的工具集成在框架间**可移植**，降低了后续迁移成本；
- 但 MCP 不解决安全：prompt 注入、工具滥用、未校验输出仍是使用方责任。

---

## 五、选型决策矩阵

| 你的主约束 | 首选 | 理由 |
|---|---|---|
| 精确控制 + 故障恢复 + 审计 | **LangGraph** | checkpoint durable execution，确定性路由 |
| 角色型任务的团队速度 | **CrewAI** | 角色抽象，一周内从想法到上线 |
| Microsoft / .NET / Azure 栈 | **MAF**（AutoGen 继任） | C#/Python 对等，原生 MCP+A2A，Azure 治理 |
| 代码/文件/终端型自主 Agent、押注 Claude | **Claude Agent SDK** | 复用 Claude Code agent loop + 沙箱 + 权限 |
| 非编码通用 Agent 想复用成熟 runtime | **coding harness 方案** | 开箱即用的 compaction/session/headless |

**常见落地路径**：CrewAI/Claude SDK 快速验证 → 需要 durable state/审计时迁移到 LangGraph 或 MAF。迁移是真实工作量，早定"demo 还是 system of record"。

---

## 六、风险与盲点

1. **日期与版本漂移**：MAF GA 日期、各框架 star 数、CrewAI 版本号在不同来源不一致，本报告已标注区间，落地前以官方 release note 为准。
2. **AutoGen 存量风险**：维护模式下仅收关键修复；GroupChat/actor 代码迁移到 MAF 接近架构重写，非线性移植。
3. **Claude Agent SDK 锁定**：1 session ≈ 1 子进程，需把 subprocess、workspace、沙箱、横向扩容纳入容量规划；模型锁定 Claude。
4. **成本盲点**：Agent loop 每任务 10–20 次 LLM 调用；coding harness 内置大 prompt 每轮累加，token 成本常被低估。
5. **安全非默认**：没有框架让 Agent"默认安全"，护栏需作为独立设计层。

---

## 七、参考来源

- JetBrains《LangGraph vs AutoGen vs CrewAI》[ref_1]
- LangChain 官方《LangChain vs. AutoGen 2026》[ref_2]
- Anthropic 官方 Agent SDK 文档《How the agent loop works》[ref_3]
- Microsoft DevBlogs《MAF at BUILD 2026》《MAF 1.0》[ref_4]
- Thoughtworks Technology Radar《Coding harness for general-purpose agents》(2026-11)[ref_5]
- DEV Community / gamut.so / developersdigest 多篇 2026 框架对比 [ref_6]

---

*本报告为证据驱动综合，关键事实已跨源交叉验证；框架状态随时变化，建议每季度复核官方 release note。*
