# 事实清单 — 2026 AI Agent 框架选型

> 主信源：DEV Community 转载（2026-07-18），原文 eCorpIT《AI agent frameworks compared for production (2026)》，最后更新 2026-07-19。
> 事实编号 F-001 ~ F-081；F-069 起为核验阶段补充/勘误事实。
> 标记：✅ 已核验 / ⚠️ 部分或口径差异 / ❌ 源文错误 / 📝 作者观点 / 🏷️ 厂商或作者自述 / — 元信息。

## 元信息与信源性质（F-001 ~ F-008）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-001 | 文章标题《2026 AI agent frameworks compared: LangGraph vs CrewAI vs Microsoft Agent Framework vs Pydantic AI》，作者 Manu Shukla，DEV 页面标注 Posted on Jul 18 | 元信息 | ✅ |
| F-002 | 原文发布于 eCorpIT，页面标注 Last updated: July 19, 2026 | 元信息 | ✅ |
| F-003 | 原文摘要称：到 2026 年 7 月，问题已从“哪个最新”变成“哪个能在生产活下来” | 作者观点 | 📝 |
| F-004 | 对比覆盖五个框架：LangGraph、CrewAI、Microsoft Agent Framework、Pydantic AI、LlamaIndex Workflows | 范围 | ✅ |
| F-005 | 选型主张：从“主导约束”出发，而不是从 Star 数出发 | 作者观点 | 📝 |
| F-006 | eCorpIT 是 2021 年成立于印度古尔冈的 AI 开发服务公司，文章含服务推销段落 | 信源性质 | ✅ |
| F-007 | 原文声明“Researched with AI assistance and reviewed by our editorial team”，并称 eCorpIT 可能出现在自己的文章中 | 信源性质 | ✅ |
| F-008 | 原文免责声明：一般信息，非专业/法律/财务/医疗建议，行动前请自行核实 | 信源性质 | ✅ |

## 五框架全景（F-009 ~ F-015）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-009 | LangGraph 自 2025 年 10 月起为 1.0，语言为 Python、JavaScript，定位“精确控制与持久长运行 Agent” | 版本/定位 | ✅ |
| F-010 | CrewAI 定位生产可用的角色型多 Agent，语言为 Python，适合快速搭建角色团队 | 定位 | ✅ |
| F-011 | Microsoft Agent Framework 1.0 于 2026 年 4 月 3 日发布，语言为 .NET、Python，适合微软技术栈企业 | 版本/定位 | ✅ |
| F-012 | Pydantic AI V2 于 2026 年 6 月 23 日稳定，语言为 Python，适合类型安全、可校验的 Agent 逻辑 | 版本/定位 | ✅ |
| F-013 | LlamaIndex Workflows 1.0 被原文称为 2026 年 6 月 22 日发布，语言为 Python、TypeScript，适合对索引数据做推理 | 版本/定位 | ❌ 年份有误，见 F-072 |
| F-014 | 原文称五框架的差异在控制力、速度、语言支持与状态存放位置，应把总览表读成“约束地图”而非排行榜 | 作者观点 | 📝 |
| F-015 | 原文用“支付公司需要长而可审计的工作流”对比“两人创业公司下周要交付 Demo”说明选型随约束变化 | 作者观点 | 📝 |

## LangGraph：控制与持久化（F-016 ~ F-023）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-016 | LangGraph 是低层编排框架，把 Agent 建模为节点与边构成的图 | 架构 | ✅ |
| F-017 | 图模型提供确定性路由与类型化状态，而不是依赖提示词循环“碰运气” | 架构 | ✅ |
| F-018 | 其标志性生产特性是持久执行：每次节点执行都作为 checkpoint 写入后端存储 | 能力 | ✅ |
| F-019 | LangGraph Platform 默认使用 Postgres，本地运行使用内存存储 | 能力 | ✅ |
| F-020 | 进程中途死亡时，运行时重放事件历史并从最后一个 checkpoint 恢复，而不是整单重跑 | 能力 | ✅ |
| F-021 | 原文称 LangGraph 在生产中用于 Uber、Klarna、LinkedIn、Replit、Elastic、AppFolio | 用户 | ⚠️ Replit 未在官方客户页确认，见 F-075 |
| F-022 | 代价是啰嗦：比角色型框架写更多连接代码，学习曲线真实存在 | 取舍 | 📝 |
| F-023 | 适用条件：失败运行代价高、需要 human-in-the-loop 中断、审计要问清“哪一步跑了、为什么” | 选型 | 📝 |

## CrewAI：速度与角色团队（F-024 ~ F-029）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-024 | CrewAI 不做图，而是描述一个由 researcher、writer、reviewer 等角色组成的 crew，由框架编排协作 | 架构 | ✅ |
| F-025 | 原文称它是最容易上手的多 Agent 团队搭建方式 | 评价 | 📝 |
| F-026 | 原文称团队反馈从想法到生产不到一周，原因是抽象确实压低了搭建成本 | 成效 | 🏷️ 无独立出处，见 F-080 |
| F-027 | 取舍是控制力：角色 crew 行为异常时，可用的精确杠杆少于图模型 | 取舍 | 📝 |
| F-028 | 复杂分支逻辑会与角色抽象“打架” | 取舍 | 📝 |
| F-029 | 适合 PoC、内部工具、角色能自然映射问题的流程；常见路径是先 CrewAI 原型，再把需要持久化的部分迁到 LangGraph，并为重写留预算 | 选型 | 📝 |

## Microsoft Agent Framework：企业合并（F-030 ~ F-039）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-030 | MAF 1.0 于 2026 年 4 月 3 日发布，结束了 Semantic Kernel 与 AutoGen 的分叉 | 版本/事件 | ✅ |
| F-031 | 微软把企业向的 Semantic Kernel 与研究向的 AutoGen 合并为一个 SDK | 事件 | ✅ |
| F-032 | 微软表述为把“Semantic Kernel 的企业级基础”与“AutoGen 的创新编排”合并为稳定 API，并提供长期支持 | 官方引语 | ✅ |
| F-033 | 架构上 Semantic Kernel 作为基础层，提供会话状态、类型安全、中间件与遥测 | 架构 | ✅ |
| F-034 | 在基础层之上放置 AutoGen 风格的图工作流，用于显式多 Agent 编排 | 架构 | ✅ |
| F-035 | .NET 与 Python 一等公民对齐，C# 团队不再落后于 Python 功能集 | 语言 | ✅ |
| F-036 | MCP 与 A2A 在 1.0 原生支持，不是后装插件 | 协议 | ⚠️ A2A 1.0 支持当时为“coming soon”，见 F-074 |
| F-037 | 开箱支持六个模型提供方：Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini、Ollama | 模型 | ✅ |
| F-038 | 原文称切换模型接近“一行代码” | 能力 | 🏷️ 宣传性表述 |
| F-039 | 已运行 Azure 与 .NET 的组织应把它视为默认选项 | 选型 | 📝 |

## Pydantic AI V2：类型安全与 Harness（F-040 ~ F-047）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-040 | Pydantic AI V2 于 2026 年 6 月 23 日稳定，采用 harness-first 重构 | 版本/架构 | ✅ |
| F-041 | 核心原语是 capability：把工具、指令、生命周期钩子与模型设置打包为一个可复用单元 | 架构 | ✅ |
| F-042 | Agent 由 capability 组装，而不是手工逐项接线 | 架构 | ✅ |
| F-043 | 一等方包 Harness 提供记忆、护栏与沙箱代码执行等预置能力 | 能力 | ✅ |
| F-044 | Pydantic AI 集成 MCP 与 human-in-the-loop 工具审批 | 协议/能力 | ✅ |
| F-045 | 选它的理由是校验：结构化数据在步骤间传递时，用编译器与 Pydantic schema 在进入下游系统前拦截畸形输出 | 选型 | 📝 |
| F-046 | 仅支持 Python；作为 V2 比 LangGraph 作为 1.0 更年轻，示例生态更薄 | 边界 | ✅ |
| F-047 | 当痛点是“输出不可预测、未校验”而不是“编排复杂”时，类型安全路径很快回本 | 选型 | 📝 |

## LlamaIndex Workflows：数据层（F-048 ~ F-053）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-048 | 原文称 LlamaIndex Workflows 1.0 于 2026 年 6 月 22 日发布，是轻量、事件驱动、async-first、基于 step 的框架 | 版本/架构 | ❌ 发布日期错误，见 F-072 |
| F-049 | 提供 Python 与 TypeScript 两种语言 | 语言 | ✅ |
| F-050 | 其血统是数据层，最强处是当 Agent 的主要工作是对索引私有数据做推理时，检索与工作流在同一处 | 定位 | 📝 |
| F-051 | Workflows 有意对编排保持不预设立场：想要轻事件核心是优点，想要开箱多 Agent 模式是缺点 | 取舍 | 📝 |
| F-052 | 适用条件：RAG over 自有文档是产品中心，Agent 逻辑次要 | 选型 | 📝 |
| F-053 | 检索框架 + 独立编排层的双框架栈很常见，只要边界清晰即可 | 选型 | 📝 |

## 选型矩阵与生产就绪（F-054 ~ F-058）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-054 | 决策表按五种主导约束给首选：控制/恢复→LangGraph；角色任务速度→CrewAI；微软/.NET→MAF；类型安全→Pydantic AI V2；索引数据推理→LlamaIndex Workflows | 决策表 | 📝 |
| F-055 | 资深团队的常见模式：先用最快的方式原型（通常 CrewAI 或 Pydantic AI），再把必须可靠运行的工作流硬化到 LangGraph 或 MAF | 模式 | 📝 |
| F-056 | 迁移是真实工作量，应尽早判断负载是 Demo 还是 system of record | 模式 | 📝 |
| F-057 | 生产就绪表中：LangGraph 持久执行=checkpoint/resume；CrewAI=平台运行时；MAF=会话状态；Pydantic=Harness 能力；LlamaIndex=事件驱动 | 对比 | ✅ 概念正确，个别实现细节需查官方文档 |
| F-058 | 五框架现在都说 MCP，因此按 MCP 建的工具集成可跨框架移植，降低后续迁移成本 | 生态 | ⚠️ 原文断言，未逐框架核验 |

## 成本与建议（F-059 ~ F-068）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-059 | 框架免费，token 不免费 | 成本 | ✅ |
| F-060 | 多步推理并调用工具的 Agent 会比单次 completion 消耗更多 token | 成本 | ✅ |
| F-061 | 前沿模型在 2026 年中期约为每 100 万输入 token 1~5 美元 | 价格 | ⚠️ 区间随模型/档位变化，无单一官方价，见 F-080 |
| F-062 | 每一步都重发完整上下文的“话痨型”多 Agent crew 是最快制造意外账单的方式 | 成本 | 📝 |
| F-063 | 支持 prompt caching、可限制每步推理、用结构化状态保持上下文紧凑的框架，更能控制花费 | 成本 | 📝 |
| F-064 | 增长的费用项通常是模型成本而非框架许可 | 成本 | ✅ |
| F-065 | 原文默认建议双框架立场：CrewAI/Pydantic AI 原型，LangGraph（Python 优先）或 MAF（.NET/Azure）承载不能失败的工作负载 | 建议 | 📝 |
| F-066 | LlamaIndex Workflows 在产品本质是对私有数据检索时占一席 | 建议 | 📝 |
| F-067 | 真实成本很少是框架，几乎总是迁移与评测 harness | 建议 | 📝 |
| F-068 | 对印度团队的三条约束：Python 人才充足、卢比偏弱使美元 token 支出敏感、DPDP Act 2023 管辖 Agent 日志与检索到的个人数据 | 区域 | ✅ 法案存在，见 F-080 口径说明 |

## 核验补充与勘误（F-069 ~ F-080）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-069 | LangGraph GitHub 1.0.0 于 2025-10-17 发布（published_at），与“2025 年 10 月”一致 | 版本日期 | ✅ |
| F-070 | 微软官方博客《Microsoft Agent Framework Version 1.0》标注 April 3rd, 2026，同时覆盖 .NET 与 Python；GitHub 1.0.0 标签发布于 2026-04-02 UTC | 版本日期 | ✅ |
| F-071 | Pydantic AI v2.0.0 GitHub 发布与官方文章日期均为 2026-06-23 | 版本日期 | ✅ |
| F-072 | PyPI 显示 llama-index-workflows 1.0.0 上传于 2025-06-25；截至 2026-10-21 最新版为 2.26.1。原文“2026-06-22 发布 1.0”应为年份错误 | 勘误 | ❌ 已确认 |
| F-073 | 微软 1.0 公告列出的连接器为 Microsoft Foundry、Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini、Ollama | 模型/服务 | ✅ |
| F-074 | 同公告写明 A2A 协议支持“A2A 1.0 support coming soon”，即 1.0 时 A2A 尚未完全就绪；原文“A2A native at 1.0”属过度表述 | 勘误 | ⚠️ |
| F-075 | LangChain 官方 Built with LangGraph 页面列出 LinkedIn、Uber、Klarna、Elastic、AppFolio；未列 Replit | 用户名单 | ⚠️ 5/6 确认 |
| F-076 | LlamaIndex 官方文档确认 Workflows 为事件驱动、step-based、async-first，支持状态序列化与恢复、可观测性 | 能力 | ✅ |
| F-077 | Pydantic AI 官方文档确认 Harness 以 capability 形式提供记忆、护栏、子 Agent、规划、上下文压缩、持久化与 coding agent；沙箱代码执行由 Monty 等组件承担 | 能力 | ✅ |
| F-078 | Microsoft Learn 2026-10 版本新增 Go 公开预览，连接器以 Microsoft Foundry 为第一方入口；.NET/Python 对齐仍成立 | 时效更新 | ✅ |
| F-079 | DEV 页面显示 Jul 18，原文最后更新 2026-07-19；两者相差一天，属转载/更新时差 | 元信息 | ✅ |
| F-080 | “不到一周上线”“一行代码切换模型”“每 100 万 token 1~5 美元”均无可独立复核的单一出处，分别按作者自述/厂商宣传/价格区间处理 | 口径 | 🏷️ |
| F-081 | 原文明确：没有框架能让 Agent 默认安全；提示注入、工具误用、未校验输出仍是使用者的责任，护栏/输入校验/工具权限应作为独立设计层 | 安全 | ✅ |
