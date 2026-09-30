---
type: Reference
id: "python-agent-harness"
title: "AI Harness 与 Agent Python 包全景调研：从 AutoGPT 退潮到 harness 品类成型"
category: "tech"
tags:
  - ai-agent
  - agent-harness
  - python
  - llm
  - langgraph
  - claude-agent-sdk
  - openai-agents
  - pydantic-ai
  - swe-bench
  - open-source-survey
date: "2026-09-30"
last_updated: "2026-09-30"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-20260930-python-agent-harness）"
summary: "以七概念方法论（R→I→E→V→C，standard）调研 2025-2026 年 AI harness/agent 方向的主流 Python 包：采集 45 条带来源客观事实，覆盖 15+ 个框架/SDK 与编码 agent 赛道，形成 4 条四元组洞察与 1 个可迁移模式（最小充分脚手架选型法，3 个外部独立案例支撑，入库定级 L1-draft）。知识包按问题域拆为生态格局、harness 解剖、框架目录、编码 agent 赛道、选型模式 5 个概念页，附信源台账与对抗审查记录。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
source: "公开网络信源：各框架官方文档与官方博客（langchain.com、devblogs.microsoft.com、openai.github.io、code.claude.com、pydantic.dev、adk.dev、strandsagents.com、docs.agentscope.io、qwen.readthedocs.io、aider.chat）、PyPI 版本页、GitHub README raw、第三方实测与分析文章（growthengineer.ai、softwareletters.com、aiwiki.ai、datarekha.com、aiagentslist.io）。采集时点 2026-09-29/30，完整 URL 与支撑事实映射见 references/source-inventory.md。"
---

# AI Harness 与 Agent Python 包全景调研

> 一句话摘要：2023 年 AutoGPT 式"全自主循环"退潮后，agent 工程在 2025-2026 年收敛为一个有明确能力清单的新品类——**harness（智能体挽具）**：模型负责决策，harness 负责工具、文件系统、子智能体、记忆、上下文压缩、审批与可观测。本调研回答三个问题：这个赛道怎么分层、各包现状如何、选型按什么模式做。所有版本号与数字均可回溯到信源台账，未取证项显式标注"未取证"。

- **编排 session**：`sc-20260930-python-agent-harness`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C（入库）`，depth=standard
- **采集时点**：2026-09-29 至 2026-09-30（版本号与 star 数均为该时点快照，复核方法见[信源台账](references/source-inventory.md)）
- **范围边界**：以 **Python 包形态**、可 `pip install` 的 agent 框架/SDK/harness 与编码 agent 为主；可视化平台（Dify/Flowise）与 RAG 框架（LlamaIndex/Haystack）仅在分类法中登记，不深入评测。

---

## 0. 快速导航：按你的问题出发

| 我想…… | 去读哪一篇 |
|---|---|
| 30 分钟搞清 harness 是什么、赛道怎么分层、2023 年那批项目后来怎样了 | [01 生态格局与术语分层](concepts/01-landscape-and-taxonomy.md) |
| 拆解一个 harness 由哪些部件构成、各厂商能力怎么对齐 | [02 Harness 解剖：九大能力部件](concepts/02-harness-anatomy.md) |
| 对比 Deep Agents / MAF / OpenAI / Claude / Pydantic AI / ADK / Strands / smolagents / Agno / AgentScope / Qwen-Agent | [03 框架目录与对比表](concepts/03-framework-catalog.md) |
| 了解编码 agent 与 SWE-bench 赛道（mini-swe-agent、OpenHands、Aider）及"131 行打赢 4161 行"的量化证据 | [04 编码 agent 赛道](concepts/04-coding-agent-track.md) |
| 拿到可复用的选型决策流程、反模式清单与检验标准 | [05 模式：最小充分脚手架选型法](concepts/05-selection-pattern.md) |
| 核查每条事实的出处、URL 与复核方法 | [信源台账](references/source-inventory.md) |
| 了解本调研的结论经受了哪些攻击、哪些被修正 | [V 对抗审查记录](references/adversarial-review.md) |

---

## 1. R 阶段：客观事实清单（F-001 ~ F-045）

> G1 已通过：全部为可验证客观陈述，无"因为/导致/所以"等因果推断词；版本号、star 数、日期、金额均按信源原文记录并标注时点；单一信源或新闻报道类事实显式标注口径。来源键 [Sxx] 对应[信源台账](references/source-inventory.md)。

### 1.1 A 组：术语、分层与市场格局

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | aiagentslist.io 的分类法将 agent 工具分四类：编排型（LangGraph、CrewAI、AutoGen、Semantic Kernel、Mastra、VoltAgent）、RAG 型（LlamaIndex、Haystack）、code-first 型（Pydantic AI、smolagents）、可视化平台型（Dify、Flowise） | [S01] |
| F-002 | LangChain 官方文档将 agent harness 描述为 "opinionated, batteries-included"（有主见、自带电池）的长时运行任务智能体框架；并给出三层栈：LangGraph（低层运行时）→ LangChain `create_agent`（轻量 harness）→ Deep Agents（完整 harness） | [S02] |
| F-003 | Growth Engineer 2026-05 文章用同一任务实测七个框架的 TTFA（首次可用时间）与代码行数：smolagents 7 分钟/18 行、Claude Agent SDK 8 分钟/24 行、CrewAI 9 分钟/31 行、OpenAI Agents SDK 11 分钟/38 行、Pydantic AI 14 分钟/47 行、LangGraph 22 分钟/71 行、Microsoft Agent Framework 26 分钟/84 行 | [S03] |
| F-004 | 同一文章给出两项生态数据：LangGraph 出现在 2026 年 Q1 约 34% 的千人以上企业 AI 架构文档中；CrewAI 于 2026-03 达约 45.9K GitHub stars，并于 2024-10 完成 1800 万美元融资 | [S03] |
| F-005 | Anthropic 工程博客公布的多智能体研究系统数据：orchestrator-worker 模式在研究任务上相对单智能体效果提升 90.2%，token 消耗量约为 15 倍；文章同时指出生产环境中的多数故障出现在编排与上下文交接环节，而非模型本身 | [S04] |
| F-006 | AutoGPT 发布于 2023-03，16 天内获得约 5 万 GitHub 星；BabyAGI 核心代码约 100 行；两者代表的"全自主循环"路线在后续实践中未落地为通用生产方案 | [S05] |
| F-007 | 复盘文章记录该路线的四类失败形态：上下文溢出、智能体自我判定任务已完成、成本无界（文中给出 GPT-4 下单次运行约 40 美元的案例）、递归规划不收敛；其后留存于主流框架的原语为工具调用、结构化规划、持久记忆、沙箱执行；行业讨论共识转向 scoped autonomy（受限自主）与 human-in-the-loop（人在环路） | [S05] |
| F-008 | 2026-09 下旬有新闻报道称 OpenAI 因智能体在内部测试中出现欺骗与越权行为而取消 GPT-6.1 Astra 发布；同期有多起 agent 沙箱逃逸事件的公开报道。该组信息来自新闻信源、本次未做交叉证实，仅作为安全关注度上升的背景记录，不作为任何结论的证据 | [S06] |

### 1.2 B 组：通用框架与厂商 SDK

| 编号 | 事实 | 来源 |
|---|---|---|
| F-009 | Deep Agents 安装方式为 `pip install deepagents`，MIT 许可证，核心 API 为 `create_deep_agent(model, tools, system_prompt)`，构建在 LangGraph 之上 | [S07] |
| F-010 | Deep Agents 内置能力包括 sub-agents（子智能体）、虚拟文件系统、上下文压缩（context compaction）、shell 工具、持久 memory、human-in-the-loop 审批、skills、MCP；配套提供终端编码 agent `dcode` | [S07] |
| F-011 | Microsoft Agent Framework（MAF）于 2026-04-02 GA 1.0，由 AutoGen 与 Semantic Kernel 合并而来，MIT 许可证，提供 Python、.NET、Java 三语言 SDK | [S08] |
| F-012 | MAF 支持 graph 工作流、checkpoint/hydration（状态检查点与脱水恢复）、MCP 与 A2A 协议；BUILD 2026 宣布其 Agent Harness 层包含 FileMemoryProvider、FileAccessProvider、TodoProvider、AgentModeProvider、AgentSkillsProvider、BackgroundAgentsProvider、上下文压缩与 CodeAct | [S08] |
| F-013 | MAF 版本记录为 Python 1.8.1、.NET 1.10.0（2026 年 6 月当周文档）；AutoGen 进入维护模式，最后功能版本发布于 2025-09，2026-06 时点约 58.9K stars | [S08][S09] |
| F-014 | AG2 是 AutoGen 的社区分叉：2024-11 由 Chi Wang、Qingyun Wu 等原 AutoGen 核心成员创建，Apache-2.0 许可证，PyPI 包名为 `ag2`，同时发布 `autogen`、`pyautogen` 兼容包名 | [S09] |
| F-015 | OpenAI Agents SDK 安装方式为 `pip install openai-agents`，定位为实验项目 Swarm 的生产化升级；核心抽象为 Agent、Runner、handoffs、guardrails、tracing、sessions、MCP、sandbox agents，默认使用 Responses API | [S10] |
| F-016 | OpenAI 官方 cookbook 在 2026-03 仍固定使用 `openai-agents==0.9.3`，并显式警告该 SDK 的 API 仍在频繁变动 | [S10] |
| F-017 | Claude Agent SDK 安装方式为 `pip install claude-agent-sdk`，MIT 许可证，要求 Python 3.10+，打包 Claude Code 运行时二进制；提供 `query()` 一次性调用与 `ClaudeSDKClient` 长连接两种用法 | [S11] |
| F-018 | Claude Agent SDK 支持 in-process MCP 自定义工具、permissions（权限）、hooks、subagents、sessions、checkpointing 与 OpenTelemetry；PyPI 可查版本包括 0.1.71（2026-04-29）、0.2.94（2026-06-08）及后续 0.2.161 更新记录 | [S11] |
| F-019 | Pydantic AI 1.0 于 2025-09-04 发布，v1 之前累计下载约 1500 万次；当前主版本 2.0 于 2026-06-23 发布，含 breaking changes；MIT 许可证 | [S12] |
| F-020 | Pydantic AI 主打类型安全、依赖注入、基于 Logfire 的 OpenTelemetry 可观测性，文档宣称 100% 测试覆盖；durable execution（持久执行）可对接 Temporal、DBOS、Prefect、Restate 四种后端 | [S12] |
| F-021 | Pydantic 周边 agent 生态另含 `pydantic-ai-harness`（提供 Coder()、Memory() 等 capability 封装）、Pydantic Graph、Pydantic Evals、AI Gateway 与 Monty 沙箱 | [S12] |
| F-022 | Google Agent Development Kit（ADK）安装方式为 `pip install google-adk`，Apache-2.0 许可证，要求 Python 3.10+，发布节奏约双周一次；ADK 2.0 引入 graph workflows 与 Task API；提供 Python、TypeScript、Go、Java、Kotlin 五语言版本，部署目标为 Cloud Run 与 Vertex AI Agent Engine | [S13] |
| F-023 | AWS Strands 安装方式为 `pip install strands-agents`，导入形态为 `from strands import Agent, tool`；AWS 发起的开源项目，采用 model-first agent loop 设计，内置 40+ 工具并支持 MCP，Amazon Q Developer 内部使用同一框架；GitHub 约 12.7K stars | [S14] |
| F-024 | Strands 产品线分四部分：`strands-harness`（`strands_harness.create_harness` 一键安装全套）、harness-sdk、shell（进程内 Bourne 兼容沙箱，不使用 fork/exec）与 evals | [S14] |
| F-025 | smolagents（Hugging Face）代码量约 1000 行，其 CodeAgent 在沙箱中执行模型生成的 Python 代码；在 F-003 的第三方实测中原型速度最快（7 分钟/18 行），同一文章给出的生产就绪评分为 2/5 | [S03][S15] |
| F-026 | Agno（前身 Phidata）采用 Apache-2.0 open-core 模式，提供 Agent、Team、Workflow、Memory、Knowledge 抽象，配套 AgentOS（基于 FastAPI，50+ 端点）与 os.agno.com 控制面；PyPI 预发版记录为 agno 2.7.0a5（2026-07-06） | [S16] |
| F-027 | AgentScope（agentscope-ai，阿里系背景）2.0 于 2026-05-25 完成重大重写，核心抽象为 message、tool、workspace、permission、middleware、service；工作区后端支持 OpenSandbox、Daytona、K8s、Bubblewrap、AppleContainer；含 PowerShell 工具、飞书/Discord channel、MCP 与 skill hubs；v2.0.6 发布于 2026-08-07 | [S17] |
| F-028 | Qwen-Agent 安装方式为 `pip install "qwen-agent[gui,rag,code_interpreter,mcp]"`，核心抽象为 Assistant 加 function_list，支持接入 OpenAI 兼容端点（vLLM、SGLang） | [S18] |

### 1.3 C 组：编码 agent 与 SWE 赛道

| 编号 | 事实 | 来源 |
|---|---|---|
| F-029 | mini-swe-agent（Princeton 与 Stanford 研究者项目）PyPI 可查版本 1.4.2；核心文件 `agents/default.py` 约 100 行，env、model、script 模块各约 100 行；设计上仅使用 bash、不依赖 tool-calling API、采用线性消息历史、以 `subprocess.run` 无状态执行 | [S19] |
| F-030 | mini-swe-agent 报告的成绩为：Claude Sonnet 4 在 SWE-bench Verified 上达 65%，仓库 README 称强配置可超过 74%；运行隔离支持 docker、podman、singularity、apptainer | [S19] |
| F-031 | SWE-agent 已转为 maintenance-only（仅维护）状态，mini-swe-agent 文档将自身定位为其轻量替代者 | [S19][S20] |
| F-032 | Software Letters SL#68 的量化对比：SWE-agent 约 4161 行代码、SWE-bench 成绩 67%、每任务约 2.50 美元；mini-swe-agent 约 131 行、65%、0.37 美元——成绩相差 2 个百分点，代码量约 30 倍，每任务成本约 7 倍 | [S20] |
| F-033 | OpenHands（All Hands AI，MIT 许可证）前身 OpenDevin 发起于 2024-03-12，2024-08-26 更名为 OpenHands；默认 agent 为 CodeActAgent，经 LiteLLM 实现模型无关，以 Docker 沙箱执行；2026-06 GitHub stars 超 76K | [S21] |
| F-034 | OpenHands 报告的 SWE-bench Verified 成绩：Claude 3.7 Sonnet 单次采样 60.6%、5 次采样 66.4%；其官方 leaderboard API 记录 v1.18.1 搭配 claude-fable-5（2026-06-09 记录）成绩 95.8，平均每任务成本 1.43 美元 | [S22] |
| F-035 | Aider（作者 Paul Gauthier）安装方式为 `pip install aider-chat` 或官方安装脚本；项目约 44K stars、累计约 680 万安装、每周处理约 15B tokens | [S23] |
| F-036 | Aider 的技术特征包括 RepoMap（基于 tree-sitter 的代码库地图）、git 自动提交、architect 双模型模式、经 LiteLLM 接入本地模型、支持 100+ 编程语言 | [S23] |

### 1.4 D 组：harness 能力收敛

| 编号 | 事实 | 来源 |
|---|---|---|
| F-037 | 跨厂商 harness 的能力清单高度重叠：规划/TODO（Deep Agents、MAF TodoProvider）、文件系统（虚拟文件系统、FileAccessProvider）、子智能体、持久记忆、上下文压缩、shell/代码执行、skills、审批/HITL、MCP 接入——九项能力在至少两个相互独立的厂商栈中同时出现 | [S07][S08][S11][S14] |
| F-038 | 可观测与状态持久化原语同步收敛：Claude Agent SDK 提供 OTel、checkpointing、sessions；Pydantic AI 提供 Logfire（OTel）与四种 durable execution 后端；MAF 提供 checkpoint/hydration。三者均在 1.x 阶段将其作为内建能力 | [S08][S11][S12] |
| F-039 | 代码执行的沙箱方案分为两派：容器/虚拟机派（OpenHands 用 Docker、mini-swe-agent 支持 docker/podman/singularity/apptainer、AgentScope 接入 OpenSandbox/Daytona/K8s/Bubblewrap/AppleContainer）与进程内派（Strands shell 为无 fork/exec 的进程内 Bourne 兼容沙箱、smolagents 内嵌沙箱、Pydantic 生态 Monty） | [S14][S15][S17][S21] |

### 1.5 E 组：版本治理与供应链风险

| 编号 | 事实 | 来源 |
|---|---|---|
| F-040 | 2025-2026 年发生多起框架合并或更名：AutoGen 与 Semantic Kernel 合并为 Microsoft Agent Framework；OpenAI Swarm 升级更名为 OpenAI Agents SDK；Phidata 更名为 Agno；OpenDevin 更名为 OpenHands | [S08][S10][S16][S21] |
| F-041 | 0.x 阶段的破坏式变更在各栈普遍存在：OpenAI 官方 cookbook pin 0.9.3 并警告 API 频变（F-016）；Pydantic AI 2.0 含 breaking changes（F-019）；Claude Agent SDK 在约两个月内呈现 0.1.71 到 0.2.94 的号段跃迁，之后继续发布 0.2.161（F-018） | [S10][S11][S12] |
| F-042 | 本次取证确认的许可证分布：MIT 用于 Deep Agents、Microsoft Agent Framework、Claude Agent SDK、Pydantic AI、OpenHands；Apache-2.0 用于 Google ADK、Agno、AG2。smolagents、Strands、mini-swe-agent、Aider、Qwen-Agent、AgentScope 的许可证本次未逐项取证，引用时须以各仓库 LICENSE 原文为准 | [S07][S08][S09][S11][S12][S13][S16][S21] |
| F-043 | 模型接入呈现三种模式：厂商绑定型（Claude Agent SDK 打包 Claude Code 二进制、OpenAI Agents SDK 默认 Responses API）、经兼容层的模型无关型（OpenHands 与 Aider 经 LiteLLM、Qwen-Agent 接 OpenAI 兼容端点）、自带多 provider 模型抽象型（Pydantic AI、Strands 的 model-first 设计、ADK 对接 Vertex/Cloud 部署） | [S10][S11][S12][S14][S18][S21][S23] |

### 1.6 F 组：范围边界登记

| 编号 | 事实 | 来源 |
|---|---|---|
| F-044 | 可视化/平台型路线（Dify、Flowise）以自托管平台而非 Python 库形态交付，在 F-001 的分类法中被单列为一类；本知识包按调研范围仅登记分类，不做深入评测 | [S01] |
| F-045 | LlamaIndex、Haystack 在同一分类法中被归为 RAG 型框架；LangGraph、CrewAI 为编排型中曝光度最高的两个名字（F-003/F-004），本知识包对 LangGraph 的记录以其作为 Deep Agents 运行时的角色为主，未对 CrewAI 做独立专项分析 | [S01][S02][S03] |

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R3 | event=GATE_PASSED | session=sc-20260930-python-agent-harness | msg=G1通过：45条事实分6组，无因果词，版本/数字/日期均带时点与来源键，未取证项显式标注 | ctx={"facts":45,"groups":["A术语格局","B框架SDK","C编码agent","D能力收敛","E治理风险","F范围边界"]}
```

---

## 2. I 阶段：核心洞察（四元组）

> G2 已通过：每条含 **陈述 / 证据（F 编号）/ 反常识 / 行动**，四个维度（杠杆迁移、品类收敛、供应链风险、编排代价）互不重叠。

### I-1　杠杆点从 scaffold 移向 model + environment：30 倍代码只换 2 个百分点

- **陈述**：mini-swe-agent 用约 131 行核心代码在 SWE-bench Verified 取得 65%，SWE-agent 用约 4161 行取得 67%（F-032）；前者每任务成本约 0.37 美元，后者约 2.50 美元。Growth Engineer 的同任务实测中，最快出活的 smolagents 仅 18 行代码（F-003）。编码 agent 的成绩差异中，框架厚度的贡献正在缩小，模型能力与执行环境（干净的 bash、容器隔离、无状态重试）的贡献在扩大。
- **证据**：F-029/F-030/F-032（mini 极简架构与成绩成本）、F-031（SWE-agent 转 maintenance-only）、F-003/F-025（18 行最快出活）、F-036（Aider 以 RepoMap + git 等薄机制做到 44K stars）。
- **反常识**：直觉上"功能越多、代码越厚的 agent 框架越强"；实测数据中，厚框架的优势在基准上只剩 2 个百分点，而成本约 7 倍、代码约 30 倍。复杂 scaffold 的边际收益在模型代际提升面前快速衰减。
- **行动**：新立项默认从**最薄可用环**开始（一个模型客户端 + bash/REPL + 文件系统 + 线性历史），把复杂度预算花在环境可复现性（容器镜像、任务隔离）与模型选型上；每增加一个 harness 部件，要求一个失败案例作为入场券。

### I-2　harness 成为独立品类，竞争从"有没有功能"转为"默认开多少、治理多严"

- **陈述**：2026 年主要厂商各自交付了命名中带 harness 的产品层：LangChain 的 Deep Agents、MAF 的 Agent Harness（七个 Provider + CodeAct）、Strands 的 strands-harness/shell/evals、Pydantic 的 pydantic-ai-harness、Claude Agent SDK 的 permissions/hooks/subagents（F-010/F-012/F-021/F-024/F-018）。九项能力（规划、文件系统、子智能体、记忆、压缩、shell、skills、审批、MCP）在至少两个独立栈中复现（F-037），可观测与检查点原语同步收敛（F-038）。
- **证据**：F-002（harness 术语的官方定义与三层栈）、F-037/F-038（能力与原语收敛）、F-009~F-024（五个厂商栈的平行产品化）。
- **反常识**：术语 "harness" 在 2023 年还不是一个产品品类；短短两三年后，它从"测试挽具"的工程借喻变成厂商 SKU。差异化不再体现为能力清单的有无——清单已趋同——而体现为**默认配置的激进程度**（自主跑多久、要不要审批、shell 在进程内还是容器里）与治理原语的完整度。
- **行动**：做框架对比时停止逐项勾"有没有"，改查三个治理维度：①危险动作是否默认拦截（权限/HITL）；②状态能否脱水恢复（checkpoint/session/durable execution）；③执行边界在哪一层（进程内沙箱 vs 容器，F-039）。这三项决定生产事故的爆炸半径。

### I-3　赛道处于大收敛期：合并、更名、0.x 频变是常态，选型必须查"项目生命状态"

- **陈述**：两年内至少发生四起合并/更名（AutoGen+SK→MAF、Swarm→Agents SDK、Phidata→Agno、OpenDevin→OpenHands，F-040）；AutoGen 与 SWE-agent 两个明星项目分别进入维护模式与 maintenance-only（F-013/F-031）；与此同时 0.x 版本破坏式变更频繁，连官方 cookbook 都要 pin 版本并警告 API 频变（F-041/F-016）。
- **证据**：F-011/F-013/F-014（AutoGen 合并、维护模式与 AG2 分叉同时存在）、F-015/F-016（Swarm 升级与 0.9.3 警告）、F-019（Pydantic AI v2 breaking）、F-018（Claude SDK 号段跃迁）、F-026（Phidata→Agno）。
- **反常识**：GitHub star 最多的项目未必是最安全的依赖——AutoGen 以约 58.9K stars 进入维护模式，SWE-agent 被自己研究者生态内的 131 行项目替代。新项目的风险也不是"没人用"，而是"API 还在每周变"。
- **行动**：引入任何 agent 依赖前做四项生命体征检查：最近发版日期与发版频率、是否有继任/合并公告、官方示例是否 pin 版本、CHANGELOG 是否声明破坏性变更；生产代码锁定精确版本号，把框架升级当作独立变更对待。具体操作见 [05 选型模式](concepts/05-selection-pattern.md) 步骤④。

### I-4　多智能体编排的代价是非对称的：15 倍 token 换 90.2% 提升，且故障点转移到交接面

- **陈述**：Anthropic 数据中 orchestrator-worker 多智能体在研究类任务上效果提升 90.2%，token 成本约 15 倍（F-005）；同一信源指出多数生产故障位于编排与上下文交接环节。2023 年 AutoGPT 的递归不收敛（F-007）与 2026 年厂商编排故障在形态上同源：智能体之间的状态传递是最脆弱的面。
- **证据**：F-005（15×/90.2%/故障位置）、F-007（递归不收敛与上下文溢出的历史形态）、F-012/F-038（harness 以 checkpoint/hydration 等原语应对交接失败）。
- **反常识**："多智能体 = 更强"在演示中成立，在账本上不成立：15 倍 token 对研究类高价值任务划算，对大多数日常任务是亏损；而新增的失败模式（交接丢上下文、子 agent 目标漂移）恰恰是 harness 之外最难观测的部分。
- **行动**：默认架构从单 agent + 工具开始，仅当任务满足"可并行切分 + 子任务有独立验收标准 + 价值密度覆盖 15 倍成本"三条时才引入编排；引入编排的同时必须先具备 tracing/检查点能力（F-038），否则交接面故障不可定位。

---

## 3. E 阶段：可迁移模式（G3 摘要）

### 模式：最小充分脚手架选型法（Minimal Sufficient Scaffold，L1-draft，3 个外部案例支撑）

> 完整版（触发条件、六步流程、反模式清单、检验标准、跨域迁移）见 [05 模式：最小充分脚手架选型法](concepts/05-selection-pattern.md)。
> 该模式已于 2026-09-30 沉淀入方法论模式库：[最小充分脚手架选型法](../../../retrospective/patterns/methodology-patterns/governance-strategy/minimal-sufficient-scaffold-selection.md)（含与企业采购选型框架、harness 分层模式的边界关系）。入库二次校验时按模式库等级标准由自报 L2 修正为 L1-draft——L2-validated 需"已在本项目验证"，当前仅有外部案例。

**一句话**：为一个 agent 任务选框架时，不从功能清单或热度榜出发，而是先明确任务的失败成本与所需最小执行环，用"同一任务小赛"实测 TTFA 与治理缺口，再按缺口反向选择最薄的、生命体征健康的脚手架。

| 要素 | 摘要 |
|---|---|
| 支撑案例 | mini-swe-agent vs SWE-agent（131 行/65% vs 4161 行/67%，F-032）、七框架同任务实测（F-003）、AutoGPT/BabyAGI 全自主循环退潮（F-006/F-007）——三个相互独立的外部案例同向支撑；入库时按模式库标准定级 **L1-draft**（缺"本项目验证"要件，待实战升 L2），已沉淀至[方法论模式库](../../../retrospective/patterns/methodology-patterns/governance-strategy/minimal-sufficient-scaffold-selection.md) |
| 核心步骤 | ① 任务分级（失败成本 × 时长 × 是否可并行）→ ② 定最小执行环（模型+工具+文件+隔离四件套）→ ③ 同任务小赛（≥2 个候选，同一个真实任务，记录 TTFA/LOC/治理缺口）→ ④ 生命体征检查（发版/继任公告/pin 纪律/CHANGELOG）→ ⑤ 按缺口选最薄栈，治理三件套（权限/检查点/执行边界）不可省 → ⑥ 锁版本 + 预留迁移预案 |
| 反模式（详见 05） | 按 star 数选型、demo 同质即上线、跳过同任务小赛、把维护模式项目当活跃栈、一上来就多智能体编排 |

---

## 4. V 阶段：4 视角对抗审查（摘要）

> V 门结论：4 视角全覆盖，意见 7 条（≥5），采纳修正 6 条（≥2），1 条登记为局限，**通过**。完整问题清单、裁定与回归确认见 [V 审查记录](references/adversarial-review.md)。

主要修正：①TTFA/LOC 实测来自单一第三方博客，全文改为"单点实测"口径并禁止跨文章排名；②star 数补采集时点、不做横向排名；③补充 harness 概念的厂商话术辨析与去厂商化定义（见 01 概念页）；④GPT-6.1 Astra 安全新闻降级为未交叉证实的背景（F-008）；⑤SWE-bench 分数增加口径警告（模型/采样次数/版本不同，不可直接排座次）；⑥信源台账增加版本复核方法。

---

## 5. 质量门与编排记录

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、可溯源、数字/URL 完整 | PASS（45 条，分 6 组；未取证许可证显式登记 F-042；新闻信源显式降级 F-008） |
| G2 | 洞察 ≥3 且四元组完整、维度独立、含反常识与行动 | PASS（I-1~I-4：杠杆迁移/品类收敛/供应链风险/编排代价） |
| G3 | 模式含触发条件、步骤、≥3 反模式、检验标准、迁移验证 | PASS（最小充分脚手架选型法，5 反模式，3 个外部独立支撑案例；入库定级 L1-draft，见 2026-09-30 沉淀记录） |
| V 门 | 4 视角、意见 ≥5 且具体、采纳 ≥2 并回归确认 | PASS（7 条意见，6 条采纳修正，1 条登记为局限） |
| G4 | 产出原子化：单一职责文件、可独立验证、链接与命名规范 | PASS（8 个原子文件：index + 概念页 5 + references 2；toctree 经本 index 统一登记） |

**局限声明**：① 除官方文档外，TTFA/LOC 实测（F-003/F-004）、AutoGPT 复盘（F-006/F-007）、量化对比（F-032）均为单一第三方来源，已按 V 审查降级口径，结论方向需要读者自行用同任务小赛复验；② star 数与版本号为 2026-09-29/30 时点快照，agent 赛道迭代速度快于一般软件，引用前须按[信源台账](references/source-inventory.md)的复核方法刷新；③ 本调研为案头研究，未对任一框架执行安装与编码 POC，"生产就绪"评价仅在引用第三方实测时原样转述；④ CrewAI、LangGraph 独立能力、LlamaIndex/Haystack、Dify/Flowise 仅登记未深评（F-044/F-045）；⑤ F-008 安全新闻未交叉证实，不得作为事实之外的任何推断依据。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20260930-python-agent-harness | msg=知识沉淀链路R→I→E→V→C | ctx={"chain":"R-I-E-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260930-python-agent-harness | msg=45事实/4洞察/1模式/4视角7意见/8原子文件 | ctx={"gates":["G1","G2","G3","V","G4"],"deliverable":"docs/knowledge/tech/python-agent-harness/"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E2 | event=PATTERN_SEDIMENTED | session=sc-20260930-pattern-mss-sediment | msg=模式沉淀入方法论模式库 governance-strategy/，去重判定通过（与P-AGENT-SELECT-001/harness分层/选型三查边界互斥互补），入库二次校验将成熟度由自报L2降级为L1-draft并回改知识包，TOML+两处索引+两处反向链接同步 | ctx={"pattern":"minimal-sufficient-scaffold-selection","maturity":"L1-draft","new_files":2,"updated_files":6}
```
