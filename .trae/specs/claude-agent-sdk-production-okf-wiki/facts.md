# F 编号事实登记 —— Claude Agent SDK 生产级智能体构建指南

> **本表不含推断。** 每条为源文（Stackademic 2026-09-26 页面）明示内容，或经 Anthropic 官方新闻、官方工程文章、Agent SDK 文档、PyPI/npm 登记信息核验的事实。
> 口径类型枚举：`博文元信息` / `博文声明` / `作者观点` / `方法论建议` / `独立核验` / `时效核验`。
> 本表与 bundle `references/article-source.md` **双份登记**，编号集合必须逐字一致、连续无跳号。

- **主源文 URL**：https://stackademic.com/blog/building-production-ai-agents-with-anthropic-s-claude-agent-sdk
- **主源文标题**：Building Production AI Agents with Anthropic's Claude Agent SDK
- **发布方**：Stackademic（页面未署名个人作者）
- **页面标注时间**：2026-09-26
- **采集时间**：2026-11-10
- **采集通道**：web_fetch 抓取完整 HTML 转 Markdown（8,733 字符），无截断

---

## A. 元信息与发布时间线

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-001 | 文章标题为《Building Production AI Agents with Anthropic's Claude Agent SDK》，发布方为 Stackademic，页面栏目为 programming。 | 博文页头 | 博文元信息 | 单源 |
| F-002 | 页面署名为 Stackademic，未标注个人作者。 | 博文页头 | 博文元信息 | 单源 |
| F-003 | 正文称 Anthropic 于 2025-09-29 随 Claude Sonnet 4.5 一同发布 Claude Agent SDK。 | 正文第 2 段 | 博文声明 | 通过（官方新闻 + 工程文章日期） |
| F-004 | 页面标注日期为 2026-09-26。 | 博文页头 | 博文元信息 | 单源 |
| F-005 | Anthropic 官方新闻《Introducing Claude Sonnet 4.5》宣布 Claude Agent SDK，并称其与 Sonnet 4.5 同日提供。 | 官方新闻 Claude Agent SDK 段 | 独立核验 | 通过 |
| F-006 | Anthropic 官方工程文章《Building agents with the Claude Agent SDK》标注日期为 2025-09-29。 | 官方工程文章页眉 | 独立核验 | 通过 |
| F-007 | 官方工程文章称 Claude Code SDK 更名为 Claude Agent SDK。 | 官方工程文章第 3 段 | 独立核验 | 通过 |
| F-008 | 官方新闻称 Anthropic 在开放底层基础设施前，用超过六个月为 Claude Code 发布更新。 | 官方新闻 Claude Agent SDK 段 | 独立核验 | 通过 |

## B. SDK 能力与定位

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-009 | 文章称 SDK 提供处理多轮推理与工具调用的 agent loop。 | What You Get 第 1 条 | 博文声明 | 通过（官方文档能力表） |
| F-010 | 文章称 SDK 内置文件操作、搜索、代码执行与 Web 访问工具。 | What You Get 第 2 条 | 博文声明 | 通过（官方文档能力表） |
| F-011 | 文章称 SDK 提供权限系统，用于在 agent 自主性与用户控制之间分配控制权。 | What You Get 第 3 条 | 博文声明 | 通过（官方文档权限页） |
| F-012 | 文章称 SDK 提供上下文管理，面向超出上下文窗口的长任务。 | What You Get 第 4 条 | 博文声明 | 通过（官方文档能力表） |
| F-013 | 文章称 SDK 提供子代理协调，用于把子任务委派给专用 agent。 | What You Get 第 5 条 | 博文声明 | 通过（官方文档能力表） |
| F-014 | 文章称 SDK 提供跨扩展会话的记忆管理。 | What You Get 第 6 条 | 博文声明 | 通过（官方文档 Sessions/Skills/Memory 条目） |
| F-015 | 官方文档列出 SDK 能力：内置工具、Hooks、子代理、MCP、权限、Sessions、Skills/commands/memory、Plugins。 | Agent SDK overview Capabilities 表 | 独立核验 | 通过 |
| F-016 | 官方文档称 Agent SDK 以 Python 与 TypeScript 提供 Claude Code 的工具、agent loop 与上下文管理。 | Agent SDK overview 首段 | 独立核验 | 通过 |
| F-017 | 官方文档称 Agent SDK 是运行 Claude Code 二进制的库，运行在开发者自己运营的进程中。 | Agent SDK overview Compare 表 | 独立核验 | 通过 |
| F-018 | 官方文档区分四种接入方式：Agent SDK（嵌入自有应用）、Claude Code CLI（终端交互）、Client SDK（直接调用 Claude API）、Managed Agents（Anthropic 托管 agent harness）。 | Agent SDK overview Compare 表 | 独立核验 | 通过 |

## C. 安装与运行环境

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-019 | 文章给出 TypeScript 安装命令：npm install @anthropic-ai/claude-agent-sdk。 | Installation | 博文声明 | 通过（npm registry + 官方 quickstart） |
| F-020 | 文章给出 Python 安装命令：pip install claude-agent-sdk。 | Installation | 博文声明 | 通过（PyPI + 官方 quickstart） |
| F-021 | 文章称 Python SDK 要求 Python 3.10+。 | Installation | 博文声明 | 通过（PyPI classifiers + 官方 quickstart） |
| F-022 | 文章称 TypeScript SDK 打包原生 Claude Code 二进制。 | Installation | 博文声明 | 通过（官方 quickstart 注记） |
| F-023 | 文章称 Python SDK 自动包含 CLI，无需单独安装。 | Installation | 博文声明 | 通过（官方 quickstart；有源码分发例外） |
| F-024 | 文章要求设置 ANTHROPIC_API_KEY 环境变量。 | Installation | 博文声明 | 通过（官方 quickstart） |
| F-025 | 官方 quickstart 前置条件为 Node.js 18.14+ 或 Python 3.10+，以及 Anthropic 账号。 | Quickstart Prerequisites | 独立核验 | 通过 |
| F-026 | 官方 quickstart 称 TypeScript 与 Python SDK 都打包原生 Claude Code 二进制；pip 源码分发（例如 ARM64 Windows）与跳过 npm optional dependencies 的安装不含二进制。 | Quickstart Install 注记 | 独立核验 | 通过 |
| F-027 | npm registry 显示 @anthropic-ai/claude-agent-sdk 最新版为 0.3.322，engines 要求 node >=18.14.0（2026-11-10 查询）。 | npm registry latest | 时效核验 | 通过 |
| F-028 | PyPI 项目页显示 claude-agent-sdk 版本为 0.2.180，classifiers 包含 Python 3.10–3.13 与 Development Status 3 - Alpha（2026-11-10 查询）。 | PyPI 项目页 | 时效核验 | 通过 |
| F-029 | 官方 quickstart 称 SDK 不自动加载 .env 文件，API key 从运行 agent 的进程环境读取。 | Quickstart Set your API key | 独立核验 | 通过 |
| F-030 | 官方文档称，除非事先获批，Anthropic 不允许第三方开发者在其产品中提供 claude.ai 登录或速率限制，包括基于 Claude Agent SDK 构建的 agent；应使用 API key 认证。 | Agent SDK overview NOTE | 独立核验 | 通过 |

## D. 最小 Agent 与配置项

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-031 | 文章示例从 claude_agent_sdk 导入 query 与 ClaudeAgentOptions。 | A Minimal Agent | 博文声明 | 通过（官方 quickstart 同类写法） |
| F-032 | 文章示例调用 query(prompt=..., options=ClaudeAgentOptions(...))，并以 async for 消费消息。 | A Minimal Agent | 博文声明 | 通过（官方 quickstart） |
| F-033 | 文章示例设置 allowed_tools=["Read", "Edit", "Bash"]。 | A Minimal Agent | 博文声明 | 通过（官方 quickstart 使用同类参数） |
| F-034 | 文章示例设置 permission_mode="acceptEdits"。 | A Minimal Agent | 博文声明 | 通过（官方 quickstart） |
| F-035 | 文章称 query 函数创建 agentic loop；调用方提供 prompt、配置可用工具并流式接收消息。 | A Minimal Agent 后段 | 博文声明 | 通过（官方 quickstart） |
| F-036 | 文章列出 allowed_tools/allowedTools：预批准 Read、Edit、Bash、Glob、Grep、WebSearch 等工具。 | Key Configuration Options | 博文声明 | 通过（官方权限页） |
| F-037 | 文章列出 permission_mode/permissionMode：控制权限请求处理方式，示例值包括 acceptEdits、ask。 | Key Configuration Options | 博文声明 | 通过（官方权限页；模式列表更完整） |
| F-038 | 文章列出 model：指定 Claude 模型，并建议 claude-sonnet-4-5 作为最新模型。 | Key Configuration Options | 博文声明 | ⚠️ 时效冲突（2026-11 已非最新） |
| F-039 | 文章列出 cwd：设置文件操作的工作目录。 | Key Configuration Options | 博文声明 | 通过（PyPI README） |
| F-040 | 文章列出 max_turns/maxTurns：限制对话轮数。 | Key Configuration Options | 博文声明 | 通过（PyPI README） |
| F-041 | 文章列出 system_prompt：自定义系统指令。 | Key Configuration Options | 博文声明 | 通过（官方 quickstart） |
| F-042 | 文章列出 mcp_servers：连接 Model Context Protocol 服务器以扩展工具访问。 | Key Configuration Options | 博文声明 | 通过（官方文档 MCP 条目） |
| F-043 | 官方 quickstart 的 Python 示例导入 query、ClaudeAgentOptions、AssistantMessage、ResultMessage。 | Quickstart Build an agent | 独立核验 | 通过 |
| F-044 | 官方 quickstart 示例使用 allowed_tools=["Read", "Edit", "Glob"] 与 permission_mode="acceptEdits"。 | Quickstart Build an agent | 独立核验 | 通过 |
| F-045 | 官方 quickstart 称示例 agent 会依次读取文件、分析逻辑、编辑文件，并在完成后输出 Done: success。 | Quickstart Run your agent | 独立核验 | 通过 |

## E. 权限与 Hooks

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-046 | 文章称 SDK 支持在工具执行前拦截工具使用的 hooks。 | Hooks for Control | 博文声明 | 通过（官方 hooks 文档） |
| F-047 | 文章称 PreToolUse hook 可以执行策略，例如限制文件写入目录或阻止特定 bash 命令。 | Hooks for Control | 博文声明 | 通过（官方 hooks 文档） |
| F-048 | 文章称 hooks 用于在默认权限系统之外增加生产护栏。 | Hooks for Control | 博文声明 | 通过（官方 hooks 文档） |
| F-049 | PyPI README 示例使用 HookMatcher(matcher="Bash") 与 PreToolUse，返回 permissionDecision="deny" 阻止匹配命令。 | PyPI README Hooks 示例 | 独立核验 | 通过 |
| F-050 | 官方 hooks 文档列出五类用途：阻止危险操作、记录与审计工具调用、转换输入输出、要求人工批准敏感操作、跟踪会话生命周期。 | Agent SDK hooks 首段 | 独立核验 | 通过 |
| F-051 | 官方权限文档给出六步评估顺序：Hooks → 拒绝规则 → 询问规则 → 权限模式 → 允许规则 → canUseTool 回调。 | Configure permissions How permissions are evaluated | 独立核验 | 通过 |
| F-052 | 官方权限文档列出的权限模式包括 default、acceptEdits、plan、dontAsk、auto、bypassPermissions。 | Configure permissions Permission modes | 独立核验 | 通过 |
| F-053 | 官方权限文档称 allowed_tools 是自动批准清单，未列出的工具仍然存在，需要批准的调用会继续走权限模式与 canUseTool。 | Configure permissions Allow/deny rules | 独立核验 | 通过 |
| F-054 | 官方权限文档称 disallowed_tools 会移除工具定义或拒绝匹配调用；带作用域的规则只拒绝匹配调用。 | Configure permissions Allow/deny rules | 独立核验 | 通过 |
| F-055 | 官方权限文档称被前序步骤自动批准的工具调用不会进入 canUseTool；要审计这些调用应使用 PreToolUse hook。 | Configure permissions WARNING | 独立核验 | 通过 |
| F-056 | 官方权限文档称 PreToolUse hook 的拒绝在 bypassPermissions 模式下同样生效。 | Configure permissions Hooks 步骤 | 独立核验 | 通过 |
| F-057 | 官方 hooks 文档提示：Write/Edit matcher 不会在 Claude 通过 Bash 写入文件时触发；该场景需配合沙箱配置。 | Agent SDK hooks WARNING | 独立核验 | 通过 |

## F. 模型、定价与可用性

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-058 | 文章称 Anthropic 推荐所有 agent 用例使用 Claude Sonnet 4.5。 | Claude Sonnet 4.5 as the Engine | 博文声明 | ⚠️ 转述范围差异（官方原文为 all uses） |
| F-059 | 文章称 Sonnet 4.5 是 Sonnet 4 的 drop-in replacement，价格相同，为每百万 token $3/$15。 | Claude Sonnet 4.5 as the Engine | 博文声明 | 通过（官方新闻） |
| F-060 | 官方新闻称 Sonnet 4.5 定价与 Sonnet 4 相同，为每百万 token $3/$15。 | 官方新闻 Pricing 段 | 独立核验 | 通过 |
| F-061 | 官方新闻称 Sonnet 4.5 是 drop-in replacement，并推荐升级到 Sonnet 4.5 用于所有用途。 | 官方新闻 Further information | 独立核验 | 通过 |
| F-062 | 文章称 Claude apps 的所有付费计划均提供代码执行与文件创建。 | Claude Sonnet 4.5 as the Engine | 博文声明 | 通过（官方新闻） |
| F-063 | 官方新闻称 Claude apps 的所有付费计划提供代码执行与文件创建。 | 官方新闻 Further information | 独立核验 | 通过 |
| F-064 | 文章称 Agent SDK 在 Claude Developer Platform 对所有开发者可用。 | Claude Sonnet 4.5 as the Engine | 博文声明 | 通过（官方新闻） |
| F-065 | 官方新闻称 Claude Developer Platform 的更新（包括 Claude Agent SDK）对所有开发者可用。 | 官方新闻 Further information | 独立核验 | 通过 |
| F-066 | 官方 model-config 文档显示 Anthropic API 上 sonnet 别名解析为 Sonnet 5.5，opus 为 Opus 5.5，haiku 为 Haiku 5.5；Fable 5.2 为单独可选模型（2026-11-10 查询）。 | Claude Code Model configuration 别名表 | 时效核验 | 通过 |
| F-067 | 官方 model-config 文档称 Sonnet 5.5 需要 Claude Code v2.1.284+，Opus 5.5 需要 v2.1.280+。 | Claude Code Model configuration NOTE | 时效核验 | 通过 |

## G. 生产实践与选型边界

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-068 | 文章建议把 agent 放入沙箱，在隔离环境中运行，不接触生产系统。 | Production Considerations | 方法论建议 | 方法论观点 |
| F-069 | 文章引用 Darktrace 研究，称有 agent 攻击自己的测试环境。 | Production Considerations | 博文声明 | ⚠️ 未核验（仅博文单源） |
| F-070 | 文章建议记录所有 agent 动作，并持久化 SDK 消息流作为审计记录。 | Production Considerations | 方法论建议 | 方法论观点 |
| F-071 | 文章建议从只读工具开始，在验证 agent 行为后再扩大权限。 | Production Considerations | 方法论建议 | 方法论观点 |
| F-072 | 文章建议主动测试权限边界，尝试让 agent 执行未授权动作。 | Production Considerations | 方法论建议 | 方法论观点 |
| F-073 | 文章称多步自主工作适合 Agent SDK，包括代码审查、修 bug、研究任务、数据分析流水线。 | When to Use the Agent SDK vs. Raw API | 作者观点 | 作者观点 |
| F-074 | 文章称单轮响应、结构化输出、逐步严格控制适合 raw Claude API。 | When to Use the Agent SDK vs. Raw API | 作者观点 | 作者观点 |
| F-075 | 文章称 Agent SDK 是 Claude Code 基础的可移植化。 | 结尾段 | 博文声明 | 通过（官方工程文章同义表述） |

## H. 补充核验（权限细节与迁移）

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-076 | 官方权限文档称 dontAsk 模式把每个会提示的调用转为拒绝。 | Configure permissions Permission modes | 独立核验 | 通过 |
| F-077 | 官方权限文档称 acceptEdits 模式批准其列出的文件操作。 | Configure permissions Permission modes | 独立核验 | 通过 |
| F-078 | 官方权限文档称 bypassPermissions 模式批准到达该步骤的调用，但任何模式都不自动批准的动作除外。 | Configure permissions Permission modes | 独立核验 | 通过 |
| F-079 | 官方权限文档称 allowed_tools 不约束 bypassPermissions；在该模式下未列出的工具调用仍会被批准。 | Configure permissions WARNING | 独立核验 | 通过 |
| F-080 | 官方权限文档称 disallowed_tools=["*"] 匹配所有工具，带 mcp__ 前缀的 glob 可匹配某服务器的全部工具。 | Configure permissions Allow/deny rules | 独立核验 | 通过 |
| F-081 | 官方 Agent SDK overview 提供从 Claude Code SDK 包迁移到 Agent SDK 的 migration guide 链接。 | Agent SDK overview Next steps | 独立核验 | 通过 |
| F-082 | 官方工程文章称 SDK 的 compact 功能在上下文接近上限时自动总结先前消息。 | 官方工程文章 Compaction 段 | 独立核验 | 通过 |
| F-083 | 官方工程文章称子代理使用各自隔离的上下文窗口，只把相关信息回传给编排者。 | 官方工程文章 Subagents 段 | 独立核验 | 通过 |
| F-084 | 官方 quickstart 称 SDK 负责编排、工具执行、上下文管理与重试，调用方消费消息流。 | Quickstart Build an agent 后段 | 独立核验 | 通过 |
| F-085 | 官方 quickstart 的工具组合表列出三档：Read/Glob/Grep 只读分析、Read/Edit/Glob 分析并修改代码、Read/Edit/Bash/Glob/Grep 全自动化。 | Quickstart Key concepts Tools 表 | 独立核验 | 通过 |
| F-086 | 官方 PyPI README 称 Claude Code 在会话首次请求时构建并记录系统提示，后续请求复用；修改 custom prompt 需新会话或 compaction，除非设置 snapshot=False。 | PyPI README System Prompt 段 | 独立核验 | 通过 |
| F-087 | 官方 quickstart 称在项目文件夹运行 SDK 时，agent 默认可以访问该目录及其子目录中的文件。 | Quickstart Setup 第 1 步 | 独立核验 | 通过 |

---

## 统计

- 事实总数：87
- 编号范围：F-001 至 F-087
