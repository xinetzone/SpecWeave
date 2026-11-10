# Microsoft Agent Framework 事实登记（R 阶段）

> 信源：
> - **S1** Build 2026 公告博文：https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/（Shawn Henry，2026-06-03）
> - **S2** Microsoft Learn 中文文档（agent-framework 文档中心，页面更新时间 2026-10 ~ 2026-11）：https://learn.microsoft.com/zh-cn/agent-framework/
> - **S3** GitHub 仓库 README（main 分支）与 Releases API：https://github.com/microsoft/agent-framework
>
> 登记规则：客观事实与作者/厂商自述分开；所有数字、日期、包名、API 名可回溯到上述信源之一。

## 一、框架定位与版本（F-001 ~ F-012）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-001 | Microsoft Agent Framework（MAF）是微软开源的 SDK 与运行时，用于构建 AI 代理（agents）与多代理工作流（multi-agent workflows）。 | S1 |
| F-002 | MAF 于 2026-04-02 发布 1.0 GA；GitHub Releases 中 `python-1.0.0` 与 `dotnet-1.0.0` 的发布时间均为 2026-04-02（UTC）。 | S1/S3 |
| F-003 | 1.0 是 AutoGen 与 Semantic Kernel 两条产品线的收敛：由同一团队打造，合并 AutoGen 的代理抽象与 Semantic Kernel 的企业能力（会话状态、类型安全、过滤器/中间件、遥测、模型与嵌入支持），并新增基于图的工作流。 | S1/S2 |
| F-004 | MAF 围绕四个领域组织：Agents（代理）、Harness agents（工具套件代理）、Workflows（工作流）、Integrations（集成）；底层构件包括模型客户端、AgentSession 状态管理、上下文提供程序、中间件与 MCP 客户端。 | S2 |
| F-005 | 官方定位语言：.NET 与 Python 提供一致的概念与 API；Go SDK 以公共预览版提供，要求 Go 1.26+，且声明性代理、CodeAct、功能工作流尚未在 Go 中实现。 | S1/S2/S3 |
| F-006 | Python 安装元包为 `agent-framework`；`agent-framework-foundry` 安装 core 加 Foundry 集成；`agent-framework` 元包还会安装 core 与许多可选集成。 | S2 |
| F-007 | .NET 包为 `Microsoft.Agents.AI`；Foundry 集成需 `Microsoft.Agents.AI.Foundry`，并配合 `Azure.AI.Projects` 与 `Azure.Identity`。 | S2/S3 |
| F-008 | 截至 2026-11，GitHub Releases 最新为 `python-1.21.0`（2026-10-08）与 `dotnet-1.21.0`（2026-09-11）。 | S3 |
| F-009 | MAF 不会自动加载 `.env` 文件；Python 需在启动时调用 `load_dotenv()` 或直接设置环境变量。 | S2 |
| F-010 | 文档明确建议：若能写一个函数完成该任务，就应写函数，而不是使用 AI 代理。 | S2 |
| F-011 | Agent 与 Workflow 的选择判据：任务开放/对话式、需要自主工具使用与规划、单次 LLM 调用足够 → Agent；流程步骤明确、需要显式控制执行顺序、多个代理或函数需协调 → Workflow。 | S2 |
| F-012 | README 将 MAF 描述为“开放的、多语言框架”，用于在 .NET 与 Python 中构建生产级 AI 代理与多代理工作流，并给出跨 Python/.NET/Go 的一致基础。 | S3 |

## 二、快速开始与代理运行时（F-013 ~ F-032）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-013 | Python 最小代理：`Agent(client=FoundryChatClient(project_endpoint=..., model=..., credential=AzureCliCredential()), instructions=...)`，再 `await agent.run(...)`。 | S2 |
| F-014 | .NET 最小代理：`new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential()).AsAIAgent(model: ..., instructions: ..., name: ...)`，再 `await agent.RunAsync(...)`。 | S2 |
| F-015 | 非流式用 `run`/`RunAsync`，流式用 `RunStreamingAsync`（.NET）或流式响应序列；`ResponseStream` 可先迭代展示，再取聚合后的完整响应且不重复迭代。 | S2 |
| F-016 | 运行选项可在构造时设为默认值，也可在单次运行时覆盖；提供程序专用选项可用强类型类（如 `OpenAIChatOptions`）获得 IDE 补全。 | S2 |
| F-017 | Agent 把代理抽象、模型或远程代理连接、指令、工具、中间件、上下文提供程序与会话状态组合在同一运行接口之后。 | S2 |
| F-018 | .NET 的 `ChatClientAgent` 可包装任何实现 `Microsoft.Extensions.AI.IChatClient` 的推理客户端；所有代理实现共享 `AIAgent` 抽象。 | S2 |
| F-019 | Python 的标准 `Agent` 接受任何实现 `SupportsChatGetResponse` 的客户端；`FoundryAgent`、`A2AAgent`、`GitHubCopilotAgent`、`ClaudeAgent` 等直接类型用于托管或远程代理运行时。 | S2 |
| F-020 | Python 中当客户端或 MCP 工具管理异步资源时应使用 `async with agent`；也可显式 `await agent.open()` / `await agent.close()`。`close()` 会发布运行期间延迟连接的 MCP 工具。 | S2 |
| F-021 | 代理管道分三层：代理中间件层、上下文层（ChatHistoryProvider + AIContextProviders）、聊天客户端层（IChatClient + 客户端中间件）。 | S2 |
| F-022 | 执行流：代理中间件 → 历史记录提供程序加载历史 → 上下文提供程序注入消息/工具/指令 → 聊天客户端中间件 → LLM → 响应沿原层返回 → 提供程序收到新消息通知。 | S2 |
| F-023 | Python `Agent` 类由 `AgentMiddlewareLayer`、`AgentTelemetryLayer` 与 `RawAgent` 组合；聊天客户端侧由 FunctionInvocation、聊天中间件与 `RawChatClient` 组成。 | S2 |
| F-024 | 中间件分三类：代理运行中间件、函数调用中间件、IChatClient 中间件；同类多个实例形成链，每个实例通过 `next` 调用下一个。 | S2 |
| F-025 | .NET 建议同时提供 `runFunc` 与 `runStreamingFunc`；只提供非流式中间件时，流式调用会退化为非流式以满足中间件语义。 | S2 |
| F-026 | 中间件可在代理级或运行级注册；可终止管道、改写结果；上下文提供程序可经 `SessionContext.extend_middleware()` 为单次调用附加聊天或函数中间件。 | S2 |
| F-027 | `AgentSession` 是跨多次运行复用的会话状态容器；C# 为抽象基类 + `StateBag`，Python 含 `session_id`、`service_session_id`、`state`，Go 为类型化键值容器。 | S2 |
| F-028 | 会话可序列化为 JSON 并恢复；会话专用于特定代理/提供程序，跨配置复用可能导致上下文失效。 | S2 |
| F-029 | 服务托管历史时，`service_session_id` / `previous_response_id` / `conversation_id` 默认只限定到 API key 或项目；多用户共用同一 key/project 时不得把服务端 ID 当作最终用户授权边界，应在服务端存储并校验归属。 | S2 |
| F-030 | 默认聊天历史存储在 `InMemoryChatHistoryProvider`（或由基础 AI 服务托管），可通过 `ChatHistoryProvider` 替换为自定义存储。 | S2 |
| F-031 | 代理运行可注入消息；响应由消息与内容项组成，内容可以是纯文本或多类型内容。 | S2 |
| F-032 | 默认情况下 `ChatClientAgent` 会为聊天客户端添加函数调用支持；`UseProvidedChatClientAsIs = true` 可跳过该包装。 | S2 |

## 三、Harness 代理（F-033 ~ F-044）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-033 | Agent Harness 是“代理工具/运行时基架”：驱动模型与工具调用、管理聊天状态与上下文、应用审批策略，并支撑多步骤长任务。 | S2 |
| F-034 | Harness 不是独立运行时，而是由聊天客户端、聊天管道、代理与上下文提供程序、中间件与修饰器、应用 UX 组合而成。 | S2 |
| F-035 | 生成结果仍是普通 Agent Framework 代理：.NET 为派生自 `AIAgent` 的 `HarnessAgent`，Python 为 `create_harness_agent` 返回的 `Agent`，Go 为 `harness.AgentConfig` 配置的 `*agent.Agent`。 | S2 |
| F-036 | Harness 开箱能力包括：函数调用与迭代上限、每次服务调用的历史记录持久化、压缩、待办事项、计划/执行模式、文件记忆与文件访问、工具审批、OpenTelemetry、Web 搜索、智能体技能、后台代理。 | S1/S2 |
| F-037 | 压缩在 .NET/Python 中需提供令牌限制或自定义策略才启用；Go 需显式组合 provider。 | S2 |
| F-038 | 默认配置：待办跟踪默认启用；计划与执行模式默认启用；会话文件记忆默认启用；共享文件访问需手动启用；工具审批默认启用；可观测性默认启用；Web 搜索在所选客户端支持时默认添加。 | S2 |
| F-039 | 技能在 .NET 与 Go 中默认启用，在 Python 中需通过提供程序或路径选择加入；后台代理由 .NET/Python 可选启用，Go 无打包的后台代理提供程序。 | S2 |
| F-040 | 博文列出的 Harness 构建块：FileMemoryProvider（会话级文件记忆，存于 `agent-file-memory/{session}/`）、FileAccessProvider、TodoProvider、AgentModeProvider、AgentSkillsProvider、BackgroundAgentsProvider、托管 Web 搜索（可用 `DisableWebSearch` 关闭）、Shell 执行（仅 .NET，沙箱化 `ShellExecutor`）。 | S1 |
| F-041 | 博文列出的 Harness 中间件与定制：`ToolApprovalAgent`（“不再询问”审批规则）、`OpenTelemetryAgent`（自动 OpenTelemetry Semantic Conventions 追踪）、可插拔存储后端（任何 `AgentFileStore` 实现）。 | S1 |
| F-042 | 指令合并顺序：Harness 指令在前，自定义代理指令在后。 | S1 |
| F-043 | Harness 在工具调用循环中的每次模型调用后持久保存聊天历史，而不仅在外部代理运行结束后保存；默认历史提供程序为 `InMemoryChatHistoryProvider` / `InMemoryHistoryProvider`。 | S2 |
| F-044 | Harness 会话跨轮次保留计划、待办、历史、审批与上下文提供程序状态；进程重启前需序列化会话。 | S2 |

## 四、工具、技能与 MCP（F-045 ~ F-056）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-045 | 工具类型包括：函数工具、代码解释器、文件搜索、Web 搜索、托管 MCP 工具、本地 MCP 工具、Microsoft Foundry 工具箱、Shell 工具；另列图像生成、本机计算机使用、Shell、Bing Grounding、Bing 自定义搜索、Azure AI 搜索、SharePoint、Microsoft Fabric、内存搜索、计算机使用预览与浏览器自动化。 | S2 |
| F-046 | 工具调用与参数由模型生成；应用代码执行副作用前必须验证与授权，高风险工具应使用审批与最小权限执行。 | S2 |
| F-047 | 支持“代理作为函数工具”：把一个代理包装成另一个代理可调用的工具。 | S2 |
| F-048 | 智能体技能是指令、脚本与资源的可移植包，遵循开放规范并实现渐进式披露。 | S2 |
| F-049 | 技能目录结构：`SKILL.md`（必需，frontmatter + 指令），可选 `scripts/`、`references/`、`assets/`。 | S2 |
| F-050 | `SKILL.md` frontmatter：`name`（≤64 字符，小写字母/数字/连字符，须与父目录同名）、`description`（≤1024，含触发关键词）、`license`、`compatibility`（≤500）、`metadata`、`allowed-tools`（实验性）。 | S2 |
| F-051 | 渐进式披露四阶段：宣告（每技能约 100 tokens）→ 加载 `load_skill`（建议 <5000 tokens）→ 按需 `read_skill_resource` → 按需 `run_skill_script`。 | S2 |
| F-052 | `load_skill` 始终暴露；`read_skill_resource` 仅当至少一个技能有资源时暴露；`run_skill_script` 仅当至少一个技能有脚本时暴露。 | S2 |
| F-053 | 长时运行的 Python 代理可用 `UnloadSkillsCompactionStrategy` 在相关工作完成后卸载技能说明与资源。 | S2 |
| F-054 | 技能支持基于文件、代码定义与基于类三种形态；支持多个技能目录、自定义资源与脚本发现、脚本执行。 | S2 |
| F-055 | 技能可指定 `allowed-tools` 预批准工具列表，但该字段为实验性，支持度因代理实现而异。 | S2 |
| F-056 | 代理技能可由 Harness 直接使用；编码代理侧的 `agent-framework-builder-python` 是开发期引导技能，不是运行时提供程序。 | S2 |

## 五、记忆、RAG 与安全（F-057 ~ F-070）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-057 | RAG 通过上下文提供程序实现：在模型调用或搜索工具之前注入检索内容。 | S2 |
| F-058 | `TextSearchProvider` 是 RAG 上下文提供程序的现成实现，支持“每次调用前搜索”与“以函数工具形式按需搜索”等模式，并可保留聊天历史滚动窗口（如 6 条）。 | S2 |
| F-059 | `TextSearchResult` 的 `SourceName` 与 `SourceLink` 可选，但若代理要引用来源则建议提供。 | S2 |
| F-060 | 搜索适配器可接任意搜索技术（Azure AI 搜索、Web 搜索引擎等）；文档另列 Graph RAG 与 Go 中的 RAG 支持。 | S2 |
| F-061 | 提示注入被列为 OWASP LLM Top 10 的首要风险；防御性系统提示与人工维护允许列表都是启发式的，不具备确定性。 | S2 |
| F-062 | FIDES（Flow Integrity Deterministic Enforcement System）是 Agent Framework 中的一级信息流控制中间件：每个内容带完整性标签（受信任/不受信任）与机密性标签（公共/专用/用户标识），标签随工具调用传播，并在敏感工具运行之前执行策略。 | S2 |
| F-063 | FIDES 基于 Costa 等人的 FIDES 论文，以实验性功能随 `agent-framework-core` 发布，默认隐藏在 `agent_framework.security` 之后；目前仅 Python，.NET 无该 API。 | S2 |
| F-064 | FIDES 四个组件：`ContentLabel`（完整性 + 机密性）、`LabelTrackingFunctionMiddleware`（传播最严格标签）、`PolicyEnforcementFunctionMiddleware`（阻止/提示审批/允许）、`quarantined_llm` + `ContentVariableStore`（隔离无工具模型处理不受信任内容）。 | S2 |
| F-065 | FIDES 与 CodeAct 存在明确边界：Hyperlight/Monty 等 CodeAct 提供程序内生成代码中的宿主工具调用绕过函数的中间件管道，FIDES 的策略执行与标签跟踪不覆盖嵌套调用或中间值；宿主工具必须自行执行授权与目标限制。 | S2 |
| F-066 | FIDES 示例：GitHub issue 分流代理读取含 `[SYSTEM]` 注入指令的 issue 后，一旦不受信任内容在作用域内，`post_comment` 等特权接收器调用被拒绝，但代理仍可总结与分类。 | S2 |
| F-067 | 安全文档将 FIDES 定位为启发式最佳实践的确定性补充，而非替代工具审批、输入验证与信任边界设计。 | S2 |
| F-068 | 后台代理让父代理把独立任务委派给命名子代理；每个任务在独立子代理会话中并发运行，父代理保留任务 ID 以等待、取回、继续或释放。 | S2 |
| F-069 | 后台代理处于实验阶段；与“后台响应”（提供程序请求可轮询/恢复）不是同一概念。 | S2 |
| F-070 | `BackgroundAgentsProvider` 的 `wait_timeout_seconds` 默认 300 秒，超时后工具正常返回并保留任务运行，父代理可再次等待；Go 无打包后台代理提供程序。 | S2 |

## 六、工作流与编排（F-071 ~ F-084）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-071 | 工作流定义显式、可检查的执行路径，用于协调代码、代理、状态、事件与人工输入。 | S2 |
| F-072 | 所有 SDK 都支持基于图的工作流；Python 额外提供实验性的函数式工作流 API（`@workflow` / `@step`，使用原生控制流）。 | S2 |
| F-073 | .NET 使用 `WorkflowBuilder` 图 API，通过边与条件连接类型化执行器，支持扇出/扇入、工作流与执行器事件，并在超级步边界创建检查点。 | S2 |
| F-074 | 函数式与图 API 的取舍：控制流（Python 原生 vs 边与条件）、并行（`asyncio.gather` vs 并行边组与超步）、可观测性（逐步事件 vs 每执行器事件）、HITL（`ctx.request_info()` vs `RequestInfoExecutor`）、检查点（每步结果缓存 vs 超级步边界）、代理包装（均支持 `.as_agent()`）。 | S2 |
| F-075 | 图运行时原语：执行器接收输入并发出输出；边路由值；事件暴露生命周期与执行活动；状态管理负责持久化与运行级状态。 | S2 |
| F-076 | 高级执行能力：代理执行器、流式/非流式执行模式、可重置执行器、子工作流。 | S2 |
| F-077 | 工作流功能面：工作流中的代理、工作流作为代理、声明性工作流、HITL、检查点与恢复、可观测性、可视化、编排。 | S2 |
| F-078 | 检查点在超级步边界创建；可从检查点恢复、解除冻结、保存执行器状态；`Pickle` 序列化与存储位置存在安全责任。 | S2 |
| F-079 | HITL 通过请求/响应机制暂停并恢复执行；多次 `run` 调用之间状态不隔离，状态会保留；检查点可与请求结合。 | S2 |
| F-080 | 内置编排模式：顺序（sequential）、并发（concurrent）、移交（handoff）、群组聊天（group chat）、Magentic。 | S2 |
| F-081 | 编排通过工具审批与请求信息支持 HITL：代理可使用需审批的工具，在執行前暂停工作流供人工评审。 | S2 |
| F-082 | 工作流可通过标准代理接口暴露（.NET `AsAIAgent()`、Python `.as_agent()`、Go `agentworkflow.NewAgent(...)`）。 | S2 |
| F-083 | 工作流可视化可呈现与导出拓扑；可观测性可导出工作流范围、指标、事件与传递状态。 | S2 |
| F-084 | 声明性工作流可通过声明性配置定义受支持的工作流。 | S2 |

## 七、托管、协议与运维（F-085 ~ F-098）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-085 | 托管模型的选择是“谁运行基础设施”的运维决策，与客户端访问协议相互独立。 | S2 |
| F-086 | Foundry 托管代理已正式发布（GA）；Python 自托管软件包处于预发布阶段；.NET 托管包为预发行版。 | S2 |
| F-087 | Foundry 托管代理开箱能力：缩容到零（空闲不计费，下次请求拉起）、缩容后文件系统与会话身份保留、每会话 VM 隔离沙箱、OpenTelemetry 追踪零接线流入 Application Insights、版本化。 | S1 |
| F-088 | 把本地代理变成托管代理只需少量代码：.NET `AddFoundryResponses(agent)` + `MapFoundryResponses()`；Python `ResponsesHostServer(agent).run()`。 | S1 |
| F-089 | 自托管在自有 ASP.NET Core 应用、容器、服务或运行时中运行代理/工作流；应用控制路由、身份、授权、请求策略、存储、部署与扩缩容。 | S2 |
| F-090 | 自托管助手：`AddAIAgent` 注册命名代理、`AddWorkflow` 注册命名工作流、`AddAsAIAgent` 暴露为标准代理、`IHostedAgentBuilder` 配置托管服务、`AgentSessionStore` 按延续 ID 加载/保存会话。 | S2 |
| F-091 | 协议选项：OpenAI 兼容端点（Responses / Chat Completions）、A2A、AG-UI、Telegram 机器人、MCP 工具；Foundry 托管还支持 Microsoft 365 频道 Activity 协议。 | S2 |
| F-092 | Durable Extension 为代理、多代理编排与工作流提供持久执行：持久化会话、检查点、故障恢复、跨分布式主机扩展、暂停等待人工或外部事件、会话 TTL、可靠流式。 | S2 |
| F-093 | Durable Extension 支持两种托管模型：Azure Functions 与自带计算/自承载；支持 C# 与 Python；Go 走 A2A 托管与 Go 仓库。 | S2 |
| F-094 | 集成按提供程序覆盖：Microsoft Foundry、Microsoft Azure、OpenAI、Anthropic、AWS Bedrock、Google Vertex、Ollama、Mistral、TypeSafe AI。 | S2 |
| F-095 | 集成按组件覆盖：模型提供程序、代理服务、工具、上下文提供程序、向量存储、中间件、评估、UI（AG-UI、ChatKit、DevUI）。 | S2 |
| F-096 | 模型提供程序比较矩阵覆盖函数工具、结构化输出、代码解释器、文件搜索、MCP 工具与后台响应；各提供程序支持度不同。 | S2 |
| F-097 | UI 框架集成 AG-UI、ChatKit、DevUI 均处于预览状态；中间件集成列 Microsoft Purview；评估集成列 Microsoft Foundry。 | S2 |
| F-098 | README 列出关键特性：多提供程序、中间件、图工作流（含检查点、流式、HITL、time-travel）、Foundry 托管代理、OpenTelemetry、声明性 YAML 代理、Agent Skills、AF Labs、DevUI。 | S3 |

## 八、Build 2026 公告与 CodeAct（F-099 ~ F-112）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-099 | 博文发布于 2026-06-03，作者 Shawn Henry（Principal Group Product Manager），主题为 BUILD 2026 的 MAF 公告汇总。 | S1 |
| F-100 | Agent Harness 扩展可用“一个方法”把任意聊天客户端变成完整 Harness 代理（.NET `AsHarnessAgent`，Python `create_harness_agent`）。 | S1/S2 |
| F-101 | 自动上下文压缩监视令牌用量，在循环中途压缩聊天历史，防止长工具调用链溢出上下文窗口。 | S1 |
| F-102 | CodeAct 的动机：许多代理的瓶颈不是模型质量而是编排开销；每次小工具调用都是一次独立模型回合，抬高延迟与 token 用量。 | S1 |
| F-103 | CodeAct 让模型写一段短 Python 程序，通过 `call_tool(...)` 调用工具，在沙箱中运行一次并返回汇总结果，从而把多回合压缩为一回合。 | S1 |
| F-104 | CodeAct 随 `agent-framework-hyperlight`（alpha）包发布，每次调用在全新的本地隔离 Hyperlight micro-VM 中运行模型生成代码。 | S1 |
| F-105 | 博文给出的代表性多步工作负载基准：传统方式 27.81s / 6,890 tokens；CodeAct 13.23s / 2,489 tokens；提升 52.4% 时间、63.9% tokens。该数据为厂商自述、单源，未在文档或仓库中找到独立复现。 | S1 |
| F-106 | `agent-framework-hyperlight` 的安装方式为 `pip install agent-framework-hyperlight --pre`；后端当前支持 Linux x86_64 与 Windows AMD64 上的 Python 3.11–3.15。 | S3 |
| F-107 | `HyperlightCodeActProvider` 会自动注入 `execute_code` 工具与 CodeAct 指令；注册到提供程序的工具在沙箱内通过 `call_tool(...)` 可用，但不作为直接代理工具暴露。 | S3 |
| F-108 | GitHub Copilot SDK 集成在 Build 2026 达到 1.0：Python `GitHubCopilotAgent`、.NET `CopilotClient.AsAIAgent()`；支持工具、指令、流式、会话、MCP 与 OpenTelemetry。 | S1 |
| F-109 | Handoff 编排达到 1.0：开发者声明代理与有向边，框架为每个代理注入移交工具；拓扑与护栏由开发者掌握，路由决策由代理掌握。 | S1 |
| F-110 | Handoff 代码形态：.NET `AgentWorkflowBuilder.CreateHandoffBuilderWith(triage).WithHandoff(triage, billing)...Build()`；Python `HandoffBuilder(participants=[...]).with_start_agent(...).add_handoff(...).build()`。 | S1 |
| F-111 | BUILD 2026 相关 session：BRK243（Claw 与 agent harness）、BRK241（原型到生产）、DEM361（可观测性与评估）、DEM333（Foundry 与开源框架集成）、DEM312（三代理三框架）、BRK250（跨框架观测与控制）。 | S1 |
| F-112 | 博文结尾给出 GitHub 仓库、官方文档、开发者博客与 Discord 入口。 | S1 |

## 九、迁移与生态（F-113 ~ F-120）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-113 | 提供从 Semantic Kernel 与 AutoGen 迁移的官方指南。 | S2 |
| F-114 | SK 迁移指南自述收益：简化 API、更好性能（对象创建与内存优化）、跨提供程序统一接口、更直观可发现的开发者体验。 | S2 |
| F-115 | SK → MAF 命名空间变化：`Microsoft.SemanticKernel` / `Microsoft.SemanticKernel.Agents` → `Microsoft.Extensions.AI` + `Microsoft.Agents.AI`。 | S2 |
| F-116 | AutoGen 迁移指南覆盖模型客户端、AgentSession 聊天状态、流式、消息类型、工具、托管工具、MCP、代理即工具、中间件、自定义代理、工作流 vs GraphFlow、群组聊天与 Magentic 模式映射。 | S2 |
| F-117 | MAF 支持把工作流、代理、MCP 工具以多种协议对外暴露，形成“构建一次、多协议访问”的集成面。 | S2 |
| F-118 | 社区维护的集成与微软官方指南分开列出。 | S2 |
| F-119 | 官方为编码代理提供 `agent-framework-builder-python` 技能，可通过 `gh skill install microsoft/agent-framework agent-framework-builder-python@main` 或 `npx skills add ...` 安装。 | S2/S3 |
| F-120 | 文档站中文版页面更新时间集中在 2026-10-23 至 2026-11-06，晚于 Build 2026 博文约五个月，因此文档包含博文未覆盖的 Go 预览与新页面。 | S2 |

## 十、源码核验补充（F-121 ~ F-170）

> 信源 S4：本地源码检出 `D:\spaces\SpecWeave\external\dao\action\agent-framework`，commit `098214127`，`git describe` = `dotnet-1.28.0-19-g098214127`（2026-11-10）。下列事实均由源码文件/脚本计数直接核验；路径均相对仓库根。

| 编号 | 事实 | 信源 |
|------|------|------|
| F-121 | 本地源码检出 commit 为 `098214127`，`git describe --tags` 输出 `dotnet-1.28.0-19-g098214127`，提交时间 2026-11-10 00:31:58 +0000。 | S4 |
| F-122 | 仓库顶层目录包含 `python/`、`dotnet/`、`go/`、`declarative-agents/`、`skills/`、`docs/`、`.github/`、`.devcontainer/`、`.vscode/`。 | S4 |
| F-123 | `python/packages/` 下有 44 个包目录（脚本计数）。 | S4 |
| F-124 | `python/packages/core/pyproject.toml` 的 `name = "agent-framework-core"`、`version = "1.25.0"`。 | S4 |
| F-125 | `dotnet/nuget/nuget-package.props` 的 `<VersionPrefix>1.28.0</VersionPrefix>`。 | S4 |
| F-126 | `dotnet/src/` 下有 38 个项目目录（脚本计数），含 `Microsoft.Agents.AI`、`.Harness`、`.Workflows`、`.Hyperlight`、`.LocalCodeAct`、`.Tools.Shell`、`.Hosting` 等。 | S4 |
| F-127 | `go/` 目录仅含 `README.md`，正文指向 `https://github.com/microsoft/agent-framework-go/`。 | S4 |
| F-128 | `python/packages/core/agent_framework/` 顶层有 24 个 `.py` 文件（脚本计数），含 `_agents.py`、`_clients.py`、`_middleware.py`、`_sessions.py`、`_compaction.py`、`_skills.py`、`security.py`、`observability.py`。 | S4 |
| F-129 | `_agents.py` 定义 `SupportsAgentRun`（Protocol）、`BaseAgent`、`RawAgent`、`Agent`。 | S4 |
| F-130 | `Agent` 继承 `AgentMiddlewareLayer`、`AgentTelemetryLayer`、`RawAgent[OptionsCoT]`；类文档称其为“推荐的代理类”，`RawAgent` 为最小实现。 | S4 |
| F-131 | `Agent.run` 的签名包含 `messages`、`stream`、`session`、`middleware`、`tools`、`options`、`compaction_strategy`、`tokenizer`、`function_invocation_kwargs`、`client_kwargs`。 | S4 |
| F-132 | `_middleware.py` 定义 `AgentMiddleware`、`FunctionMiddleware`、`ChatMiddleware`、`MiddlewareBundle`、`AgentMiddlewarePipeline`、`FunctionMiddlewarePipeline`、`ChatMiddlewarePipeline`、`ChatMiddlewareLayer`、`AgentMiddlewareLayer`。 | S4 |
| F-133 | `_middleware.py` 定义 `MiddlewareTermination` 与 `MiddlewareFailure` 两个异常类型。 | S4 |
| F-134 | `_sessions.py` 定义 `SessionContext`、`ContextProvider`、`HistoryProvider`、`MessageInjectionMiddleware`、`_RunPersistenceGate`。 | S4 |
| F-135 | `SessionContext` 提供 `extend_messages`、`extend_instructions`、`extend_tools`、`extend_middleware`、`get_messages`；`ContextProvider` 提供 `before_run` 与 `after_run` 钩子。 | S4 |
| F-136 | `_compaction.py` 定义 `CompactionStrategy` 协议与 `TokenizerProtocol`，并包含 `TruncationStrategy`、`SlidingWindowStrategy`、`SelectiveToolCallCompactionStrategy`、`ToolResultCompactionStrategy`、`SummarizationStrategy`、`TokenBudgetComposedStrategy`、`ContextWindowCompactionStrategy`、`AgentTriggeredCompactionStrategy`、`UnloadSkillsCompactionStrategy`。 | S4 |
| F-137 | `_compaction.py` 定义 `CompactionProvider(ContextProvider)`，把压缩接入上下文提供程序管道。 | S4 |
| F-138 | `_harness/_agent.py` 的 `create_harness_agent` 组装 `Agent`，文档列出其自动接线：函数调用、每次服务调用历史持久化、压缩、TodoProvider、AgentModeProvider、FileMemoryProvider、FileAccessProvider、SkillsProvider、BackgroundAgentsProvider、工具审批、循环。 | S4 |
| F-139 | `create_harness_agent` 参数包含 `max_context_window_tokens`、`max_output_tokens`、`disable_compaction`、`before_compaction_strategy`、`after_compaction_strategy`、`disable_todo`、`disable_mode`、`disable_file_memory`、`skills_provider`、`skills_paths`、`background_agents`、`shell_executor`、`disable_web_search`。 | S4 |
| F-140 | `create_harness_agent` 区分 `harness_instructions` 与 `agent_instructions`；`harness_instructions` 为 `None` 时使用 `DEFAULT_HARNESS_INSTRUCTIONS`。 | S4 |
| F-141 | `_harness/_loop.py` 定义 `DEFAULT_MAX_ITERATIONS = 10`。 | S4 |
| F-142 | `_harness/_background_agents.py` 定义 `DEFAULT_BACKGROUND_AGENTS_WAIT_TIMEOUT_SECONDS = 300`。 | S4 |
| F-143 | `_harness/_loop.py` 定义 `AgentLoopMiddleware`、`JudgeVerdict`、`background_tasks_running`、`todos_remaining` 等循环控制构件。 | S4 |
| F-144 | `_harness/` 下存在 `_file_memory.py`、`_file_access.py`、`_todo.py`、`_mode.py`、`_tool_approval.py`、`_background_agents.py`、`_memory.py`、`_loop.py`。 | S4 |
| F-145 | `_harness/_agent.py` 从 `agent_framework_tools.shell` 导入 `ShellEnvironmentProviderOptions` 与 `ShellExecutor`，并在 `shell_executor` 非空时装配 `ShellEnvironmentProvider`。 | S4 |
| F-146 | `python/packages/tools/pyproject.toml` 的 `name = "agent-framework-tools"`、`version = "1.0.0b261106"`。 | S4 |
| F-147 | `_workflows/` 运行时文件包含 `_workflow.py`、`_workflow_builder.py`、`_runner.py`、`_runner_context.py`、`_edge_runner.py`、`_executor.py`、`_checkpoint.py`、`_functional.py`。 | S4 |
| F-148 | `WorkflowBuilder` 提供 `add_edge`、`add_fan_out_edges`、`add_switch_case_edge_group`、`add_multi_selection_edge_group`、`add_fan_in_edges`、`add_chain`、`build`。 | S4 |
| F-149 | `Workflow` 提供 `run`、`get_start_executor`、`get_output_executors`、`get_intermediate_executors`、`get_executors_list`；`WorkflowRunResult` 提供 `get_outputs`、`get_intermediate_outputs`、`get_request_info_events`、`status_timeline`。 | S4 |
| F-150 | `_runner.py` 的 `RunnerImpl` 提供 `run_until_convergence`、`_run_iteration`、`create_checkpoint_if_enabled`、`restore_from_checkpoint`、`build_checkpoint`、`restore_checkpoint`。 | S4 |
| F-151 | `_checkpoint.py` 定义 `WorkflowCheckpoint`、`CheckpointStorage`（协议：`save`/`load`/`list_checkpoints`）、`InMemoryCheckpointStorage`、`FileCheckpointStorage`。 | S4 |
| F-152 | `_workflows/_functional.py` 定义 `FunctionalWorkflow`、`FunctionalWorkflowAgent`、`RunContext`、`StepWrapper`、`FunctionalWorkflowDefinition`。 | S4 |
| F-153 | `security.py` 定义 `IntegrityLabel`、`ConfidentialityLabel`、`ContentLabel`、`ContentVariableStore`、`LabelTrackingFunctionMiddleware`、`PolicyEnforcementFunctionMiddleware`、`SecureAgentConfig`、`SecureMCPToolProxy`。 | S4 |
| F-154 | `SecureAgentConfig` 是 `ContextProvider`；文档字符串说明它向代理注入安全工具、指令与中间件，安全状态存放在 `AgentSession`。 | S4 |
| F-155 | `dotnet/src` 全目录 `.cs` 文件检索 `IntegrityLabel|Fides|FIDES` 零命中。 | S4 |
| F-156 | `python/packages/hyperlight/agent_framework_hyperlight/` 定义 `HyperlightCodeActProvider(ContextProvider)` 与 `HyperlightExecuteCodeTool(FunctionTool)`。 | S4 |
| F-157 | `HyperlightCodeActProvider` 参数包含 `tools`、`approval_mode`、`workspace_root`、`file_mounts`、`allowed_domains`、`max_output_files`、`max_output_file_bytes`、`max_output_total_bytes`、`backend`（默认 `"wasm"`）、`module`。 | S4 |
| F-158 | `python/packages/hyperlight/tests/hyperlight/` 含 `test_hyperlight_codeact.py` 与 fake sandbox/runtime 测试替身。 | S4 |
| F-159 | `dotnet/src/Microsoft.Agents.AI.Harness/` 含 `HarnessAgent.cs`、`HarnessAgentOptions.cs`、`ChatClientHarnessExtensions.cs`。 | S4 |
| F-160 | `HarnessAgentOptions` 公开 `MaxContextWindowTokens`、`MaxOutputTokens`、`CompactionStrategy`、`DisableCompaction`、`HarnessInstructions`、`ChatHistoryProvider`、`AIContextProviders`、`LoopEvaluators`、`LoopAgentOptions`、`MaximumIterationsPerRequest`、`DisableToolAutoApproval`。 | S4 |
| F-161 | `dotnet/src/Microsoft.Agents.AI.Workflows/` 含 `CheckpointManager.cs`、`CheckpointInfo.cs`、`Executor.cs`、`Edge.cs`、`AgentWorkflowBuilder.cs`、`ConcurrentWorkflowBuilder.cs`、`FanOutEdgeData.cs`、`FanInEdgeData.cs`。 | S4 |
| F-162 | `dotnet/src` 项目清单含 `Microsoft.Agents.AI.Hyperlight`、`Microsoft.Agents.AI.LocalCodeAct`、`Microsoft.Agents.AI.Tools.Shell`、`Microsoft.Agents.AI.Workflows.Declarative`。 | S4 |
| F-163 | 源码 1.25.0 的 Harness 在 Python 侧提供 `shell_executor` 参数，Shell 能力通过预发布包 `agent-framework-tools` 提供；文档（F-040）写“Shell 执行仅 .NET”。 | S4 |
| F-164 | 源码 `agent-framework-core` 版本 1.25.0 高于 GitHub Releases 最新稳定 `python-1.21.0`（F-008），说明本次检出位于 1.21 之后的 main 分支。 | S4 |
| F-165 | `RawAgent` 提供 `as_mcp_server` 方法；`BaseAgent` 提供 `as_tool` 方法。 | S4 |
| F-166 | `SessionContext` 提供 `response` 属性，用于读取本次运行的 `AgentResponse`。 | S4 |
| F-167 | `python/packages/core/agent_framework/_harness/__init__.py` 为 0 字节文件；`create_harness_agent` 定义在 `_harness/_agent.py`。 | S4 |
| F-168 | `dotnet/src` 同时含 `Microsoft.Agents.AI.Abstractions`、`Microsoft.Agents.AI`、`Microsoft.Agents.AI.Harness`、`Microsoft.Agents.AI.Workflows`、`Microsoft.Agents.AI.Hosting` 与多家 provider 项目目录。 | S4 |
| F-169 | `python/packages/` 同时包含 `declarative`、`devui`、`lab`、`orchestrations`、`hosting-*` 与多家模型 provider（`openai`、`anthropic`、`gemini`、`bedrock`、`ollama`、`mistral` 等）。 | S4 |
| F-170 | 仓库顶层含 `skills/` 与 `declarative-agents/` 两个目录。 | S4 |
