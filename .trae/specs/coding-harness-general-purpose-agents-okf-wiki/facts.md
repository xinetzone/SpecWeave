---
type: facts
title: "Coding Harness for General-Purpose Agents 事实登记"
source_url: "https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents"
generated_at: "2026-11-10"
---

# 事实登记（F-001 ~ F-047）

| 编号 | 事实或声明 | 来源层级 | 核验 |
|---|---|---|---|
| F-001 | 页面标题为 “Coding harness for general-purpose agents”，位于 Thoughtworks Technology Radar 的 Techniques 象限。 | 博文元信息 | 单源 |
| F-002 | 该 blip 发布于 2026-11-04。 | 博文元信息 | 通过（Radar 页面） |
| F-003 | 该 blip 属于 Technology Radar Vol 35（2026 年 11 月）。 | 博文元信息 | 通过（Radar 首页与 PDF 链接） |
| F-004 | 该 blip 的评级为 Trial（试验）。 | 博文元信息 | 通过（Radar 页面） |
| F-005 | 从事非编码工作的团队（如文档处理、运营支持、迁移规划）通常从 agent framework 起步，并自行组装 agent loop。 | 博文声明 | 作者观察 |
| F-006 | 越来越多团队改为构建 “coding harness for general-purpose agents”，复用成熟编码 agent 的运行时。 | 博文主结论 | 作者观察 |
| F-007 | 文章点名 Claude Agent SDK 作为以编程方式暴露编码 agent 运行时的入口。 | 博文声明 | 通过（官方文档） |
| F-008 | 文章点名 Codex 的 SDK 与 app-server 作为编程入口。 | 博文声明 | 通过（官方仓库） |
| F-009 | 文章点名 OpenCode 的 server 与 SDK 作为编程入口。 | 博文声明 | 通过（官方文档） |
| F-010 | 文章点名 Pi 的 SDK 与 RPC 模式作为编程入口。 | 博文声明 | 通过（官方文档） |
| F-011 | 这些 harness 已处理长任务中的上下文压缩（compacting context）。 | 博文声明 | 通过（Claude/Pi 文档支持） |
| F-012 | 这些 harness 已处理会话持久化（persisting sessions）。 | 博文声明 | 通过（四家文档均有会话机制） |
| F-013 | 这些 harness 可无头运行（headlessly），并复用交互式编码会话中的 agent skills、子代理与指令。 | 博文声明 | 通过（官方文档支持） |
| F-014 | 与 agent framework 相比，coding harness 的取舍是控制力更少，换取已被广泛测试的运行时。 | 博文判断 | 作者观点 |
| F-015 | Thoughtworks 用该方法构建了一个 .NET 应用迁移的内部加速器。 | 博文案例 | 厂商自述（无公开证据） |
| F-016 | 不同 harness 的能力并不相同。 | 博文判断 | 通过（官方能力表差异） |
| F-017 | Codex 与 Claude Agent SDK 提供沙箱（sandboxing）与审批策略（approval policies）。 | 博文声明 | 通过（口径见 E-1） |
| F-018 | Pi 刻意把护栏（guardrails）留给扩展（extensions）。 | 博文判断 | 通过（官方定位支持，措辞见 E-2） |
| F-019 | Pi 因此更容易适配，但需要更多工作量。 | 博文判断 | 作者观点 |
| F-020 | 这些运行时为软件开发而设计，其系统提示与内置工具倾向把 agent 引导到编写和运行代码。 | 博文判断 | 作者观点 |
| F-021 | 团队应针对目标领域审查这些默认值。 | 博文建议 | 方法论建议 |
| F-022 | 团队应监控成本。 | 博文建议 | 方法论建议 |
| F-023 | coding-agent loop 可能消耗大量 token。 | 博文判断 | 作者经验 |
| F-024 | 大型内置提示会增加到每一轮请求中。 | 博文判断 | 作者经验 |
| F-025 | 这是 Pi 这类最小 harness 具有吸引力的原因之一。 | 博文判断 | 作者观点 |
| F-026 | 相关 blip “Agent Skills” 评级为 Trial，发布于 2026-04-15，且不在 2026 年 11 月这一期雷达上。 | 相关 blip | 通过（Radar 页面） |
| F-027 | Radar Vol 35 将 “Agent sandboxing” 列为 Adopt。 | 相关 blip | 通过（Radar 页面） |
| F-028 | Radar Vol 35 将 “Managed agents runtime” 列为 Trial。 | 相关 blip | 通过（Radar 页面） |
| F-029 | Radar Vol 35 将 “Enterprise harness” 列为 Assess。 | 相关 blip | 通过（Radar 页面） |
| F-030 | Radar Vol 35 将 “Harness quality evaluation” 列为 Assess。 | 相关 blip | 通过（Radar 页面） |
| F-031 | Radar Vol 35 将 “Agent plugin marketplace” 列为 Trial。 | 相关 blip | 通过（Radar 页面） |
| F-032 | Enterprise harness 是组织级、由编码 agent 集体消费的层，包含 skills、工具、内部上下文连接器、批准技术、架构决策记录、path-to-production 指南、hooks 与安全策略。 | 相关 blip | 通过（Radar 页面） |
| F-033 | Harness quality evaluation 认为 harness 同时包含确定性与非确定性组件；非确定性部分可用 PluginEval 评估，确定性部分可用 redproof 测试套件做 TDD 式验证，并建议按夜间或 CI 节奏定期运行。 | 相关 blip | 通过（Radar 原文；工具仓库未逐一核验） |
| F-034 | Agent sandboxing 建议所有 agent 默认在隔离环境运行，采用基于威胁建模的风险分级方法，并遵循最小权限原则。 | 相关 blip | 通过（Radar 页面） |
| F-035 | Managed agents runtime 指由平台托管 agent 的执行、基础设施与运维，提供沙箱计算、触发器、凭证处理、会话状态与可观测性。 | 相关 blip | 通过（Radar 页面） |
| F-036 | Agent Skills 是模块化上下文的开放标准，按描述按需加载指令、脚本与资源，以降低 token 消耗。 | 相关 blip | 通过（Radar 页面） |
| F-037 | Claude Agent SDK 官方文档称其提供与 Claude Code 相同的工具、agent loop 与上下文管理，可用 Python 与 TypeScript 编程。 | 官方文档 | 通过（Agent SDK overview） |
| F-038 | Claude Agent SDK 能力表列出内置工具、hooks、subagents、MCP、permissions、sessions、skills/commands/memory 与 plugins。 | 官方文档 | 通过（Agent SDK overview） |
| F-039 | Codex TypeScript SDK 包装 `codex` CLI，通过 stdin/stdout 交换 JSONL 事件；npm 包为 `@openai/codex-sdk`，要求 Node.js 18+。 | 官方文档 | 通过（Codex SDK README） |
| F-040 | Codex app-server 使用 JSON-RPC，并包含线程管理、审批请求与记忆摘要等接口。 | 官方文档 | 通过（app-server README） |
| F-041 | OpenCode 的 `opencode serve` 启动无头 HTTP server，暴露 OpenAPI 3.1 规范；SDK 由该规范生成，npm 包为 `@opencode-ai/sdk`。 | 官方文档 | 通过（Server/SDK 文档） |
| F-042 | Pi 的 SDK 包 `@earendil-works/pi-coding-agent` 在 Node.js 或 Bun 进程内嵌入 Pi；RPC 模式保持进程长驻，以 JSONL 双向传输命令、响应与事件。 | 官方文档 | 通过（SDK/CLI Integration 文档） |
| F-043 | Pi 官方 README 自述为 “minimal, extensible agent harness”，默认跳过 sub-agents 与 plan mode 等功能，鼓励通过扩展、技能、提示模板与主题定制。 | 官方文档 | 通过（Pi README） |
| F-044 | OpenCode 权限规则支持 allow、deny、ask 三种效果；无规则匹配时默认 ask。 | 官方文档 | 通过（Permissions 文档） |
| F-045 | Claude Agent SDK 的托管文档称 SDK 会为每个会话启动 `claude` CLI 子进程，会话记录默认落在本地磁盘，容器化沙箱属于一种托管方式。 | 官方文档 | 通过（Hosting 文档） |
| F-046 | Codex SDK 的配置示例包含 `sandbox_workspace_write` 与 `default_permissions: "audit"`，表明沙箱与权限配置可通过 SDK 传入。 | 官方文档 | 通过（Codex SDK README） |
| F-047 | Thoughtworks 将 Technology Radar 描述为一年两次的技术 landscape 快照，基于其全球团队的项目经验。 | 相关页面 | 通过（Radar 首页） |
