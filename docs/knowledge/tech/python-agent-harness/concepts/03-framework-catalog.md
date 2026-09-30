# 03 框架目录与对比表：11 个通用 Python 栈逐个登记

> 读完本文你会知道：除编码专用 agent（见 [04](04-coding-agent-track.md)）之外，主流通用 agent Python 包各自的维护方、许可证、版本时点、模型绑定方式与适用场景。每个条目都标注事实编号，可回溯到 [index 事实清单](../index.md) 第 1 节与 [信源台账](../references/source-inventory.md)。

## 3.1 速查总表

> 时点声明：版本与 star 数为 2026-09-29/30 信源快照，**不做横向排名**；"许可证"列仅登记本次已取证项，未取证者写"未取证"，采用前必须以仓库 LICENSE 原文复核。

| 包（pip 名） | 维护方 | 许可证（已取证） | 版本时点证据 | 模型绑定 | 一句话定位 |
|---|---|---|---|---|---|
| `deepagents` | LangChain | MIT（F-009） | 未记录具体版本号（F-009） | 接 LangChain 模型抽象 | LangGraph 之上的满配 harness，九件齐（F-010） |
| Microsoft Agent Framework（`microsoft-agent-framework` 系包名以官方文档为准） | Microsoft | MIT（F-011） | GA 1.0 = 2026-04-02；Py 1.8.1 / .NET 1.10.0（2026-06 周）（F-011/F-013） | 多 provider | AutoGen+SK 合并体，Provider 可替换的企业 harness（F-012） |
| `openai-agents` | OpenAI | 未取证 | cookbook 2026-03 pin 0.9.3，警告 API 频变（F-016） | 默认 Responses API（F-015） | Swarm 生产化，handoff/guardrail 为核心抽象（F-015） |
| `claude-agent-sdk` | Anthropic | MIT（F-017） | 0.1.71（04-29）→0.2.94（06-08）→0.2.161（F-018） | 打包 Claude Code 二进制（F-017） | 把 Claude Code 的 harness 能力以 SDK 形态开放（F-017/F-018） |
| `pydantic-ai` | Pydantic 团队 | MIT（F-019） | v1.0 = 2025-09-04；v2.0 = 2026-06-23 含破坏性变更（F-019） | 多 provider 抽象 | 类型安全 + DI + Logfire，durable 接四后端（F-020） |
| `google-adk` | Google | Apache-2.0（F-022） | ADK 2.0（graph workflows + Task API），双周发布（F-022） | 对接 Gemini/Vertex 生态，五语言 | 与 Vertex AI Agent Engine/Cloud Run 部署直通（F-022） |
| `strands-agents` | AWS | 未取证 | 未记录具体版本号；GitHub 约 12.7K stars（F-023） | model-first（多模型）（F-023） | Amazon Q Developer 同源，harness/shell/evals 产品线（F-023/F-024） |
| `smolagents` | Hugging Face | 未取证 | 代码量约 1000 行（F-025） | 经 HF 生态多模型 | 约 1000 行的 CodeAgent，原型最快、生产就绪评分 2/5（F-025） |
| `agno`（原 phidata） | Agno 团队 | Apache-2.0（F-026） | 2.7.0a5（2026-07-06 预发版）（F-026） | 多 provider | Agent/Team/Workflow + AgentOS 50+ 端点，open-core（F-026） |
| AgentScope（包名以官方文档为准） | agentscope-ai（阿里系背景） | 未取证 | 2.0 重写 2026-05-25；v2.0.6 = 2026-08-07（F-027） | 多模型 | workspace 抽象 + 五种执行后端，企业 IM channel（F-027） |
| `qwen-agent` | Qwen 团队 | 未取证 | 未记录具体版本号 | OpenAI 兼容端点（vLLM/SGLang）（F-028） | Assistant + function_list，GUI/RAG/解释器/MCP extras（F-028） |

## 3.2 满配 harness 档

### Deep Agents（LangChain）

- **安装与 API**：`pip install deepagents`；`create_deep_agent(model, tools, system_prompt)`（F-009）。
- **部件清单**：sub-agents、虚拟文件系统、上下文压缩、shell、持久 memory、HITL 审批、skills、MCP（F-010），另有配套终端编码 agent `dcode`（F-010）。
- **适用**：已在 LangGraph/LangSmith 生态内、想要九件齐的默认装配、愿意接受其"有主见"姿势的团队。
- **注意**：harness 的固定姿势同时是锁定面——部件替换不如 MAF 的 Provider 模型自由；版本号本次未取证，采用前查 PyPI。

### Microsoft Agent Framework（MAF）

- **身世**：2026-04-02 GA 1.0，AutoGen 与 Semantic Kernel 合并而来，Python/.NET/Java 三语言（F-011）。AutoGen 进入维护模式（最后功能版 2025-09，约 58.9K stars）（F-013）；社区分叉 AG2（2024-11，Chi Wang/Qingyun Wu 等，Apache-2.0，PyPI 名 `ag2`/`autogen`/`pyautogen`）独立继续（F-014）。
- **harness 部件**：FileMemoryProvider、FileAccessProvider、TodoProvider、AgentModeProvider、AgentSkillsProvider、BackgroundAgentsProvider 七个 Provider + 上下文压缩 + CodeAct；graph 工作流、checkpoint/hydration、MCP、A2A（F-012）。
- **适用**：.NET/Azure 存量企业、需要可替换 Provider 与状态脱水恢复的长时工作流。
- **注意**：版本号仍在快速滚动（Py 1.8.1，F-013）；从 AutoGen 迁移需评估合并期 API 差异；AG2 是想留在 AutoGen 编程模型上的替代路径。

### Claude Agent SDK（Anthropic）

- **形态**：`pip install claude-agent-sdk`，Python 3.10+，MIT；打包 Claude Code 运行时二进制，`query()` 一次调用或 `ClaudeSDKClient` 长连接（F-017）。
- **治理原语**：in-process MCP 自定义工具、permissions、hooks、subagents、sessions、checkpointing、OTel（F-018）。
- **适用**：以 Claude 为主力模型、想直接复用 Claude Code 在真实工程中打磨过的文件/git/终端姿势。
- **注意**：厂商绑定最深的一档（运行时二进制）；号段在两个月内 0.1.71→0.2.94→0.2.161（F-018），升级纪律要严。

### AWS Strands

- **形态**：`pip install strands-agents`，`from strands import Agent, tool`；model-first agent loop、40+ 工具、MCP；Amazon Q Developer 内部同源使用；约 12.7K stars（F-023）。
- **产品线**：`strands-harness`（`create_harness` 全装）、harness-sdk、shell（进程内 Bourne 兼容、无 fork/exec）、evals（F-024）。
- **适用**：AWS 服务为主要工具面、认同进程内沙箱换取低延迟路线的团队。
- **注意**：许可证与具体版本本次未取证；进程内 shell 的逃逸面评估见 [02 Harness 解剖](02-harness-anatomy.md) §2.4。

## 3.3 框架 / 轻 harness 档

### OpenAI Agents SDK

- **形态**：`pip install openai-agents`，Swarm 的生产化升级；Agent/Runner/handoffs/guardrails/tracing/sessions/MCP/sandbox agents，默认 Responses API（F-015）。
- **适用**：以 OpenAI 平台为主、需要 handoff 与 guardrail 作为一等抽象。
- **注意**：0.x 频变——2026-03 官方 cookbook 仍 pin 0.9.3 并警告 API 变动（F-016），生产代码必须精确锁版本。

### Pydantic AI

- **时点**：v1.0 = 2025-09-04（v1 前约 1500 万下载）；v2.0 = 2026-06-23，含破坏性变更（F-019）。
- **特征**：类型安全、依赖注入、Logfire（OTel）、文档宣称 100% 测试覆盖；durable execution 对接 Temporal/DBOS/Prefect/Restate（F-020）；周边 `pydantic-ai-harness`（Coder()/Memory()）、Pydantic Graph、Pydantic Evals、AI Gateway、Monty 沙箱（F-021）。
- **适用**：Python 类型纪律严格的团队、要把 agent 嵌进既有 Pydantic/FastAPI 服务、恢复语义外包给持久工作流引擎。
- **注意**：v2 迁移有破坏面（F-019）；第三方实测 TTFA 14 分钟/47 行，属于"中等装配成本"档（F-003，单点实测口径）。

### Google ADK

- **形态**：`pip install google-adk`，Apache-2.0，Python 3.10+，双周发布；ADK 2.0 引入 graph workflows 与 Task API；Py/TS/Go/Java/Kotlin 五语言；部署直通 Cloud Run 与 Vertex AI Agent Engine（F-022）。
- **适用**：GCP/Vertex 生态、多语言团队、想要从开发到托管的厂商内闭环。

### smolagents（Hugging Face）

- **形态**：约 1000 行；CodeAgent 在沙箱中执行模型生成的 Python（F-025）。
- **实测口径**：第三方同任务实测中 7 分钟/18 行最快出活，但生产就绪评分 2/5（F-003/F-025，**单一来源**）。
- **适用**：快速原型、教学、一次性脚本；生产使用前需自行补齐 [02](02-harness-anatomy.md) 的治理部件。

### Agno（原 Phidata）

- **形态**：Apache-2.0 open-core；Agent/Team/Workflow/Memory/Knowledge；AgentOS 为 FastAPI 的 50+ 端点运行面，os.agno.com 为控制面；预发版 2.7.0a5（2026-07-06）（F-026）。
- **适用**：需要"框架 + 一键起服务 + 云控制面"垂直体验的小团队。
- **注意**：open-core 模式下部分高级能力在商业侧；预发版号意味着 API 仍可能变（与 F-041 同类风险）。

### AgentScope（agentscope-ai）

- **形态**：2.0 于 2026-05-25 重大重写（message/tool/workspace/permission/middleware/service 六抽象）；工作区后端 OpenSandbox、Daytona、K8s、Bubblewrap、AppleContainer；含 PowerShell 工具、飞书/Discord channel、MCP/skill hubs；v2.0.6 = 2026-08-07（F-027）。
- **适用**：需要丰富执行后端选择（含企业 K8s 与桌面容器）、需要对接国内 IM 平台（飞书）的团队。

### Qwen-Agent

- **形态**：`pip install "qwen-agent[gui,rag,code_interpreter,mcp]"`；Assistant + function_list；可接 OpenAI 兼容端点（vLLM/SGLang）（F-028）。
- **适用**：Qwen 模型本地化部署（vLLM/SGLang）场景，extras 直接覆盖 GUI/RAG/代码解释/MCP 四类常见需求。

## 3.4 按模型绑定方式分组（避免被"开源"二字误导）

许可证开源不等于模型中立（F-043）：

| 绑定模式 | 包 | 架构含义 |
|---|---|---|
| 厂商运行时绑定 | Claude Agent SDK（Claude Code 二进制）、OpenAI Agents SDK（默认 Responses API） | 换模型等于换框架，谈判筹码在模型价格与性能 |
| 兼容层模型无关 | OpenHands、Aider（LiteLLM）、Qwen-Agent（OpenAI 兼容端点） | 可自由换模型端，但治理能力依赖框架自身 |
| 自带多 provider 抽象 | Pydantic AI、Strands（model-first）、ADK、Deep Agents、smolagents、Agno、AgentScope、MAF | 模型是配置项，但 provider 支持深度参差，需实测 |

## 3.5 登记但未深评的条目

- **CrewAI**：编排型代表之一，2026-03 约 45.9K stars、2024-10 融资 1800 万美元（F-004），第三方实测 9 分钟/31 行（F-003）；本次未做独立专项分析。
- **LangGraph**：本知识包主要记录其作为 Deep Agents 运行时的角色（F-002）；第三方数据称其出现在 2026 Q1 约 34% 的千人企业架构文档中（F-004，单一来源），实测 TTFA 22 分钟/71 行为七者最慢（F-003，单一来源）——慢的另一面是抽象层最完整。
- **LlamaIndex / Haystack**：RAG 型，按范围仅登记（F-045）。
- **Dify / Flowise**：可视化平台型，非 pip 库形态，仅登记（F-044）。

---

上一篇：[02 Harness 解剖](02-harness-anatomy.md) ｜ 下一篇：[04 编码 agent 赛道](04-coding-agent-track.md)
