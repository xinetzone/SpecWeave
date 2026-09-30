# 02 Harness 解剖：九大能力部件

> 读完本文你会知道：一个"满配"agent harness 由哪些部件构成、每个部件解决 2023 年的哪类失败、五个厂商栈分别用什么名字提供这些部件、选型时该在每个部件上问什么问题。

## 2.1 九大部件总览

下列九项能力在至少两个相互独立的厂商栈中同时出现（F-037），可视为 2026 年 harness 的事实标准件：

| # | 部件 | 解决的问题 | 主要提问 |
|---|---|---|---|
| 1 | 规划 / TODO | 目标漂移、递归不收敛 | 规划是否结构化、深度有无上限 |
| 2 | 文件系统 | 长任务的中间产物放哪 | 虚拟 fs 还是宿主 fs，如何隔离 |
| 3 | 子智能体 | 上下文污染、任务并行 | handoff 时哪些状态被传递/丢弃 |
| 4 | 持久记忆 | 跨会话/跨任务的知识留存 | 记忆存哪、可否审查与删除 |
| 5 | 上下文压缩 | 上下文溢出（F-007 失败形态①） | 压缩触发策略与信息损失可见吗 |
| 6 | Shell / 代码执行 | 让模型真正"动手" | 进程内还是容器，默认权限多大 |
| 7 | Skills | 可复用的过程性知识打包 | 格式是否开放、能否自带 |
| 8 | 审批 / HITL | 自我判定完成、危险动作（F-007 失败形态②） | 哪些动作默认拦截，可否细粒度配 |
| 9 | MCP 接入 | 工具生态的标准化 | 支持 in-process server 吗，仅远程吗 |

另有两个横切原语虽未计入九件，却是生产上线的前置条件：**可观测性**（OTel/tracing）与**状态持久化**（checkpoint/session/durable execution），见 2.3。

## 2.2 五栈部件对照表

> 表中"✓"表示官方文档明确提供；空白表示本次信源未取证，**不等于没有**。所有引述对应 index.md 的事实编号。

| 部件 | Deep Agents | MAF（1.0+） | Claude Agent SDK | Strands | Pydantic 生态 |
|---|---|---|---|---|---|
| 规划 / TODO | ✓（内置任务规划） | ✓ TodoProvider（F-012） | 经 subagents/sessions 组合 | ✓（harness 装配） | 经 pydantic-graph 组合 |
| 文件系统 | ✓ 虚拟文件系统（F-010） | ✓ FileAccessProvider（F-012） | 借 Claude Code 文件工具 | ✓（harness 装配） | 经 pydantic-ai-harness Coder()（F-021） |
| 子智能体 | ✓ sub-agents（F-010） | ✓ graph 工作流编排（F-012） | ✓ subagents（F-018） | ✓（agent 组合） | ✓ 多 agent 组合 |
| 持久记忆 | ✓ 持久 memory（F-010） | ✓ FileMemoryProvider（F-012） | sessions（F-018） | ✓（harness 装配） | ✓ Memory() capability（F-021） |
| 上下文压缩 | ✓ context compaction（F-010） | ✓ context compaction（F-012） | 隐式（Claude 运行时内建） | — | — |
| Shell / 代码执行 | ✓ shell（F-010） | ✓ CodeAct（F-012） | shell 借 Claude Code 二进制 | ✓ strands-shell，**进程内无 fork/exec**（F-024） | ✓ Monty 沙箱（F-021） |
| Skills | ✓ skills（F-010） | ✓ AgentSkillsProvider（F-012） | skills（subagents/hooks 体系） | — | — |
| 审批 / HITL | ✓ human-in-the-loop（F-010） | ✓ AgentModeProvider（F-012） | ✓ permissions + hooks（F-018） | ✓（权限模型） | — |
| MCP | ✓（F-010） | ✓ MCP + A2A（F-012） | ✓ **in-process MCP**（F-018） | ✓ MCP（F-023） | 经插件 |
| 可观测 | 经 LangSmith | OpenTelemetry 生态 | ✓ OpenTelemetry（F-018） | 与 AWS 观测集成 | ✓ Logfire（OTel）（F-020） |
| 检查点 / 恢复 | LangGraph checkpoint | ✓ checkpoint/hydration（F-012） | ✓ checkpointing（F-018） | — | ✓ Temporal/DBOS/Prefect/Restate（F-020） |
| 后台/长任务 | 子 agent 派生 | ✓ BackgroundAgentsProvider（F-012） | ClaudeSDKClient 长连接（F-017） | — | durable execution 后端 |

读表方法：

- **看命名也能看设计哲学**：MAF 把一切做成可替换的 Provider（依赖注入风格，企业可替换文件/记忆实现）；Claude Agent SDK 把运行时打成一个二进制，harness 能力围绕它配置（ batteries 来自 Claude Code 自身）；Deep Agents 居中，作为 LangGraph 之上的一组固定装配。
- **空白格不是差评，是未取证**。本次为案头调研（见 index 局限声明③），尽调时应以官方文档重新核对。
- **"有"之外还要问"默认"**：审批部件默认开还是默认关、shell 默认能碰宿主吗——这是 I-2 所说"默认开多少"的竞争维度。

## 2.3 两个横切原语：看不见但决定能否上线

### 可观测性（observability）

三栈独立选择了同一个标准——OpenTelemetry：Claude Agent SDK 内建 OTel（F-018），Pydantic AI 用自家 Logfire 承载 OTel（F-020），MAF 融入微软可观测生态。原因是 F-005 记录的生产事实：多智能体系统的多数故障位于编排与交接环节，没有 trace 就无法定位是哪一次 handoff 丢了上下文。

选型提问：① 每次工具调用、模型调用、handoff 是否各有独立 span？② token 与成本是否进 trace？③ trace 能否离线导出（厂商锁定检查）？

### 检查点与恢复（checkpoint / hydration / durable execution）

三种命名、同一诉求：长任务跑到第 40 分钟进程挂了，能否从最近状态续跑，而不是重烧一遍 token。

- MAF 叫 checkpoint/hydration（状态脱水/补水）（F-012）；
- Claude Agent SDK 叫 checkpointing + sessions（F-018）；
- Pydantic AI 不自己做，而是对接 Temporal、DBOS、Prefect、Restate 四种 durable execution 后端（F-020）。

第三条路线值得注意：**把恢复问题外包给专门的持久工作流引擎**。它代表了一种架构取向——harness 只做 agent 语义，工程可靠性复用既有基础设施。

## 2.4 执行边界：容器派与进程内派

shell/代码执行部件是唯一存在明确路线之争的部件（F-039）：

| 派别 | 实现 | 隔离强度 | 代价 |
|---|---|---|---|
| 容器/虚拟机派 | OpenHands（Docker，F-033）、mini-swe-agent（docker/podman/singularity/apptainer，F-030）、AgentScope（OpenSandbox/Daytona/K8s/Bubblewrap/AppleContainer，F-027） | 高：独立内核命名空间/系统沙箱 | 镜像重、冷启动慢、CI 成本高 |
| 进程内派 | Strands shell（Bourne 兼容、无 fork/exec，F-024）、smolagents 内嵌沙箱（F-025）、Monty（F-021） | 中：语言运行时/解释器层限制 | 逃逸面更大，依赖沙箱实现质量 |

判断依据不是"哪个更先进"，而是失败成本：执行不可信代码（用户上传的仓库、互联网抓取的脚本）优先容器派；执行框架自己生成的受控代码且追求低延迟，进程内派可接受，但必须与审批部件（#8）组合使用。2026 年公开报道的多起 agent 沙箱逃逸事件（F-008，**新闻信源未交叉证实**）至少说明这一部件的失效模式已被公开讨论。

## 2.5 用九大部件给任意 harness 做体检

拿到一个新框架，不必通读文档，按下面顺序做部件体检即可在 30 分钟内判断其成熟度：

1. 找**执行与权限**：shell 在哪一层执行？危险命令默认拦截还是放行？
2. 找**状态与恢复**：进程杀掉后会话能否恢复？状态格式是开放的还是黑盒？
3. 找**上下文策略**：长对话怎么压缩？压缩事件在 trace 里可见吗？
4. 找**子 agent 边界**：handoff 是共享全量上下文还是显式传参？
5. 找**工具扩展面**：MCP 支持远程还是也支持 in-process（F-018 的 in-process 形态免去了起独立 MCP server 的运维成本）？
6. 找**观测出口**：OTel exporter 能指向我自己的后端吗？

六项有四项答得清楚，属于生产候选；六项都含糊，只适合做原型——这与 [05 选型模式](05-selection-pattern.md)步骤⑤的"治理三件套不可省"直接衔接。

---

上一篇：[01 生态格局与术语分层](01-landscape-and-taxonomy.md) ｜ 下一篇：[03 框架目录与对比表](03-framework-catalog.md)
