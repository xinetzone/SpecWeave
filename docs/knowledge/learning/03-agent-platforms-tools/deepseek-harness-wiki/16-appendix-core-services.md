---
id: deepseek-harness-wiki-16
title: DeepSeek Harness Wiki - 附录：核心服务速查表
source:
  - external/libs/deepseek-harness/docs/capability-seams.zh.md
  - external/libs/deepseek-harness/docs/architecture.zh.md
  - external/libs/deepseek-harness/packages/
date: 2026-08-17
tags:
  - deepseek
  - agent
  - harness
  - reference
  - services
  - ctx-api
  - appendix
category: learning
maturity: L2
---

# 附录：核心服务速查表

本附录列出 dsh 运行时上下文中所有核心 `ctx.*` 服务的快速参考，方便插件开发时查阅。基于源码自动生成的能力图整理。

## 角色说明

- **seam**：可替换能力接口，可以切换不同 Provider 实现
- **core**：核心主干服务，通常不建议替换
- **bundle**：由 Bundle 提供的具体实现，不是抽象接口

## 服务速查表

| ctx 键 | 角色 | 职责 | 内置实现 |
|---|---|---|---|
| `ctx.sessions` | core | 仅追加的 SessionEvent 日志和内存存储 | 无（内置） |
| `ctx.systemPrompt` | core | 提示词片段与工具 schema 的组装注册 | 无（内置） |
| `ctx.tools` | core | 作用域化的工具注册表和带把关的执行流水线 | 无（内置） |
| `ctx.agents` | core | Agent 接口、活跃 Agent 注册表和 `agent/*` 事件 | 无（内置） |
| `ctx.agentLoop` | bundle | 默认的 ReactLoop 循环驱动器 | `core/agent-loop` |
| `ctx.llm` | seam | LLM 消息流式接口、适配器注册 | `llm-deepseek`, `llm-pi-ai`, `llm-replay` |
| `ctx.tokenMeter` | core | 按会话隔离的 Token 测量折叠区 | 无（内置） |
| `ctx.toolResultPruner` | core | 压缩前工具结果表层替换 | 无（内置） |
| `ctx.invariants` | core | 运行时不变量断言注册表 | 无（内置） |
| `ctx.sessionPersistence` | seam | 会话持久化后端 | `session-persistence-jsonl`, `session-persistence-sqlite` |
| `ctx.sessionQuery` | seam | 会话读取、追踪、过滤、搜索 | `session-query-sqlite` |
| `ctx.sessionTitle` | seam | 会话标题生成 | `session-title-first-prompt-llm`, `session-title-all-prompts-llm` |
| `ctx.sessionTelemetry` | seam | 会话遥测脱敏上报 | `session-telemetry-otel` |
| `ctx.sessionProjections` | core | 状态驱动折叠单元注册 | 无（内置） |
| `ctx.sessionProjectionCache` | core | 投影检查点持久缓存 | 无（内置） |
| `ctx.sessionReferenceResolver` | core | 跨会话快照投影 | 无（内置） |
| `ctx.attachments` | seam | 二进制附件持久存储 | `attachment-local` |
| `ctx.credentials` | seam | 凭据管理与脱敏存储 | `credentials-local` |
| `ctx.settings` | seam | 用户分层设置 | `settings-file` |
| `ctx.storage` | seam | 非会话 KV 存储 | `storage-json`, `storage-sqlite` |
| `ctx.storageDomain` | core | 领域类型化持久状态 | 无（内置） |
| `ctx.messageFeedback` | core | 逐消息反馈（不进会话历史） | 无（内置） |
| `ctx.workspaceRegistry` | core | Workspace 实体注册表 | 无（内置） |
| `ctx.fs` | seam | 文件系统抽象 | `fs-local`, `fs-sandbox`, `fs-e2b` |
| `ctx.subprocess` | seam | 子进程 spawn、进程树、stdio 管理 | `subprocess-local`, `subprocess-e2b` |
| `ctx.shell` | seam | Shell 命令执行（bash/pwsh） | `bash-local`, `bash-sandbox`, `pwsh-local` |
| `ctx.shellEnv` | core | DSH_* 环境变量管理 | 无（内置） |
| `ctx.terminals` | seam | 持久化 PTY 终端会话 | `terminal-bash` |
| `ctx.sandbox` | seam | 进程沙箱包装 | `sandbox-local` |
| `ctx.sandboxPolicy` | core | 沙箱默认模式和根目录配置 | 无（内置） |
| `ctx.approval` | seam | 权限审批请求分发 | `acp` |
| `ctx.permissionPresets` | core | 用户权限预设组合 | 无（内置） |
| `ctx.codeRuntime` | seam | 模型代码异步执行 | `code-runtime-worker` |
| `ctx.subagents` | seam | 子 Agent 委派与延续 | `spawn-in-process`, `fork-in-process`, `subagent-acp`, `subagent-codex`, `subagent-claude-code`, `subagent-dsh-sdk` |
| `ctx.web` | seam | 网页搜索和 HTTP 抓取 | `web-search-exa`, `web-search-perplexity`, `web-search-deepseek`, `web-fetch-http` |
| `ctx.jobs` | seam | 后台任务注册与管理 | `jobs-local` |
| `ctx.skills` | seam | Skill 技能目录提供方 | `skill-filesystem`, `skill-badge` |
| `ctx.lsp` | seam | 语言服务器协议导航 | `lsp-local` |
| `ctx.compaction` | seam | 上下文压缩 | `compaction-basic` |
| `ctx.goals` | core | 同会话目标状态折叠 | 无（内置） |
| `ctx.planMode` | core | 计划协作状态 | 无（内置） |
| `ctx.agentPresets` | core | Agent Preset 配置发现 | 无（内置） |
| `ctx.agentDefaultModel` | core | 默认模型选择 | 无（内置） |
| `ctx.commands` | core | 用户斜杠命令注册 | 无（内置） |
| `ctx.userQuestions` | seam | 人类问答交互（tool-ask-user） | UI 提供方 |
| `ctx.spillStore` | seam | 大文本溢出存储 | `spill-local` |
| `ctx.directoryPicker` | seam | 工作目录选择交互 | `directory-picker-native`, `directory-picker-browse` |
| `ctx.webServer` | core | HTTP 路由注册 | 无（内置） |
| `ctx.clientModules` | core | 客户端插件图 HMR | 无（内置） |
| `ctx.workflowEngine` | seam | 工作流脚本引擎 | `workflow-worker-thread` |
| `ctx.e2b` | core | E2B 远程沙箱共享句柄 | 无（内置） |
| `ctx.apiProxy` | core | Host 浏览器 API 网关 | 无（内置） |
| `ctx.dynamicCordisRunner` | core | 动态 Cordis 插件 VM 沙箱运行器 | 无（内置） |
| `ctx.cordisInspect` | core | 运行时 Cordis 自省查询 | 无（内置） |
| `ctx.typert` | core | 运行时 zod 类型注册表 | 无（内置） |
| `ctx.typertGateway` | core | Typert Host RPC 网关 | 无（内置） |

## 常用扩展点速查

| 你想做什么 | 用哪个服务/事件 |
|---|---|
| 添加一个面向模型的工具 | `ctx.tools.register()` |
| 添加一个新的模型提供商 | `ctx.llm.registerAdapter()` |
| 拦截/修改工具执行 | 监听 `tools/pre-execute` / `tools/post-execute` waterfall |
| 拦截/修改模型请求 | 监听 `agent/request` waterfall |
| 在模型看到内容前注入指令 | 监听 `agent/pre-step` waterfall |
| 判断 Turn 是否结束 | 监听 `agent/turn-stopping` serial |
| 添加一个自定义 Shell 后端 | 注册 `ctx.shell` Provider |
| 添加一个自定义文件系统后端 | 注册 `ctx.fs` Provider |
| 添加一个子 Agent 委派目标 | 注册 `ctx.subagents` Provider |
| 添加一个斜杠命令 | `ctx.commands.register()` |
| 添加一个后台任务类型 | `ctx.jobs.register()` + `tool-jobs` |
| 读写结构化持久状态 | `ctx.storageDomain` |
| 注入上下文到下一次请求 | `ctx.agents.inject()` |
| Fork 一个会话 | `ctx.sessions.fork()` |
| 限定注册只在某个 Agent 生效 | 使用该 Agent 的 `agent.ctx` |

## 事件分发模式速查

| 模式 | 方法 | 是否 await | 有返回值 | 用途 |
|---|---|---|---|---|
| 通知 | `ctx.emit()` | 否 | 否 | 日志、指标、纯观察 |
| 瀑布中间件 | `ctx.waterfall()` | 否 | 是 | 拦截、改写、短路、权限检查 |
| 并行扇出 | `ctx.parallel()` | 是 | 否 | 多个独立后处理、遥测上报 |
| 串行执行 | `ctx.serial()` | 是 | 是 | 校验链、投票聚合（如 turn-stopping） |
| 同步早退 | `ctx.bail()` | 否 | 是 | 第一个返回非 null 的监听器获胜 |

---

← [15 生态与资源](15-ecosystem-resources.md) | 回到[00 总览](00-overview.md)
