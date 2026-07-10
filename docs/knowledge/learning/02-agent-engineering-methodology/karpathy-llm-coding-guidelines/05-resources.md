---
id: "karpathy-llm-coding-guidelines-resources"
title: "资源与参考链接"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, resources, references, repository-structure, multica, multica-cli]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "相关资源链接：三个官方仓库（karpathy-skills/multica/multica-cli）的文件结构、分发格式说明、Karpathy原帖、中文报道、Multica平台相关资源等参考资料。"
source: "https://github.com/multica-ai/andrej-karpathy-skills + https://github.com/multica-ai/multica + https://github.com/multica-ai/multica-cli"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.toml"
---
# 资源与参考链接

## 官方仓库文件结构

仓库采用**多格式分发**策略，同一套原则以不同格式服务于不同工具：

```
andrej-karpathy-skills/
├── CLAUDE.md                              # Claude Code 项目根目录配置
├── CURSOR.md                              # Cursor 使用说明文档
├── EXAMPLES.md                            # 真实代码正反例
├── README.md                              # 英文 README
├── README.zh.md                           # 中文 README
├── .cursor/
│   └── rules/
│       └── karpathy-guidelines.mdc        # Cursor 项目规则（alwaysApply: true）
├── .claude-plugin/
│   ├── plugin.json                        # Claude Code 插件元数据
│   └── marketplace.json                   # 插件市场注册信息
└── skills/
    └── karpathy-guidelines/
        └── SKILL.md                       # Agent Skill 格式（可复用技能包）
```

### 关键文件对照表

| 文件 | Frontmatter字段 | 特殊说明 |
|------|----------------|---------|
| `CLAUDE.md` | 无 | Claude Code 自动读取，末尾包含 "These guidelines are working if" 效果评估段 |
| `.cursor/rules/*.mdc` | `description`, `alwaysApply: true` | mdc = Markdown Cursor Rules，`alwaysApply: true` 自动应用 |
| `skills/.../SKILL.md` | `name`, `description`, `license` | Skill 标准格式，description 决定触发场景 |
| `.claude-plugin/plugin.json` | JSON 格式 | 声明插件名称、版本、技能路径 |
| `.claude-plugin/marketplace.json` | JSON 格式 | 插件市场注册信息，category: "workflow" |

---

## 官方资源

| 资源 | 链接 | 说明 |
|------|------|------|
| GitHub 仓库 | https://github.com/multica-ai/andrej-karpathy-skills | 官方仓库，包含所有格式文件 |
| CLAUDE.md 原文 | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md | Claude Code 根目录配置格式 |
| SKILL.md 原文 | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md | Agent Skill 格式 |
| Cursor Rules 原文 | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/.cursor/rules/karpathy-guidelines.mdc | Cursor .mdc 规则格式 |
| CURSOR.md 使用说明 | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CURSOR.md | Cursor 集成详细说明 |
| 中文 README | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/README.zh.md | 官方中文说明文档 |
| 代码示例 | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/EXAMPLES.md | 真实世界正反例代码 |

---

## 原始来源

| 资源 | 链接 | 说明 |
|------|------|------|
| Karpathy 原帖 | https://x.com/karpathy/status/2015883857489522876 | 2026年1月26日，Karpathy 在 X 上的长帖，吐槽 AI 编程 Agent 的各种毛病 |
| Jiayuan Zhang 的 X | https://x.com/jiayuan_jy | 作者 Jiayuan Zhang（forrestchang）的 X 账号 |

---

## Multica 主平台仓库（monorepo）

```
multica/
├── CLAUDE.md                              # Claude Code 仓库规范
├── AGENTS.md                              # AI Agent 仓库指南（指针文件）
├── CLI_AND_DAEMON.md / CLI_INSTALL.md     # CLI 和 Daemon 文档
├── README.md / README.zh-CN.md            # 中英文 README
├── SELF_HOSTING.md                        # 自部署指南
├── apps/
│   ├── web/                               # Next.js Web 应用
│   ├── desktop/                           # Electron 桌面应用
│   ├── mobile/                            # Expo/React Native iOS 应用
│   └── docs/                              # 官方文档网站（Nextra）
├── packages/
│   ├── core/                              # 无头业务逻辑（Zustand stores、React Query、API client）
│   ├── ui/                                # 原子 UI 组件（shadcn/Base UI）
│   └── views/                             # 共享业务页面/组件
├── server/                                # Go 后端（Chi router、sqlc、gorilla/websocket）
│   └── cmd/                               # CLI 命令（multica 子命令）
├── docker/                                # Docker 配置
├── deploy/helm/                           # Kubernetes Helm Chart
├── scripts/                               # 安装/开发脚本
├── docs/                                  # 产品文档（product-overview.md 等）
└── e2e/                                   # Playwright 端到端测试
```

技术栈：Go 1.26+ 后端 + Next.js 16 前端 + PostgreSQL 17 (pgvector) + Electron 桌面端 + React Native 移动端。

---

## multica-cli Skill 仓库结构

```
multica-cli/
├── README.md / README.zh.md               # 中英文 README
├── CURSOR.md                              # Cursor 使用说明
├── EXAMPLES.md                            # 具体使用示例
├── LICENSE                                # MIT 协议
├── .cursor/rules/
│   └── multica-cli.mdc                    # Cursor 项目规则
├── .claude-plugin/
│   ├── plugin.json                        # Claude Code 插件元数据
│   └── marketplace.json                   # 插件市场注册
└── skills/multica-cli/
    ├── SKILL.md                           # Agent Skill 主文件（含完整命令参考）
    └── agents/
        └── openai.yaml                    # Agent 配置示例
```

---

## Multica 相关项目

| 资源 | 链接 | 说明 |
|------|------|------|
| Multica 主项目 | https://github.com/multica-ai/multica | 开源 Managed Agents 平台（monorepo：Go 后端 + Next.js Web + Electron 桌面 + 移动端） |
| multica-cli Skill | https://github.com/multica-ai/multica-cli | 让外部 Agent 通过 multica CLI 安全操作平台的 Skill |
| Multica 官网 | https://multica.ai | 官方网站（云服务） |
| Multica Discord | https://discord.gg/W8gYBn226t | 社区 Discord |
| Multica X | https://x.com/MulticaAI | 官方 X/Twitter |
| Karpathy Skills | https://github.com/multica-ai/andrej-karpathy-skills | 本教程的主角仓库 |
| Multica 组织 | https://github.com/multica-ai | Multica 的 GitHub 组织页面 |

> Multica 项目介绍：Your next 10 hires won't be human.
> 把 Claude Code、OpenCode、Codex CLI 这些 AI 编程 Agent 统一管理起来，像真正的团队成员一样分配任务、汇报进展、交付代码。他们公司代码 100% 由 AI 编写，每天消耗 token 超过 1 亿。

---

## 中文报道

| 资源 | 链接 | 说明 |
|------|------|------|
| 36氪报道 | https://www.36kr.com/p/3774954488349441 | 本文档的中文来源文章（新智元授权发布） |
| 新智元公众号 | https://mp.weixin.qq.com/s/iHFAIbedBdVvWuxR3ENsIg | 原始中文报道来源 |

---

## SpecWeave 项目内资源

| 资源 | 链接 | 说明 |
|------|------|------|
| AI 编码行为准则（规则文档） | [ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md) | 本项目整合后的完整规则，含一分钟速查表 |
| 全局核心规则 | [global-core-rules.md](../../../../../.agents/global-core-rules.md) | 包含"歧义主动澄清"原则 |
| 开发者角色定义 | [developer.md](../../../../../.agents/roles/developer.md) | 包含"外科手术式精确编辑"要求 |
| 开发规范 | [development-standards.md](../../../../development-standards.md) | 包含"简约设计原则"章节 |
| 本教程目录 | [.](./README.md) | 你正在阅读的教程文档集合 |

---

## 相关概念

### Karpathy 准则相关
- **Agentic Engineering（智能体工程）**：把 AI 当做需要明确目标、清晰边界和严格测试的协作伙伴来对待的工程学科。
- **YAGNI 原则**：You Aren't Gonna Need It——不要添加你认为将来可能需要但当前不需要的功能。
- **Slopacolypse（低质量内容灾难）**：Karpathy 预言的 2026 年现象——GitHub、arXiv、社交媒体上会涌出大量 AI 生成的低质量内容。生产力是真的，质量垮塌的风险也是真的。
- **MDC 格式**：Cursor Rules 使用的 Markdown 格式，文件扩展名为 `.mdc`，通过 frontmatter 中的 `alwaysApply: true` 控制自动应用。
- **Agent Skill 格式**：Claude Code 插件系统和 Multica 平台使用的技能格式，`SKILL.md` 通过 `name` 和 `description` 元数据描述，支持跨项目复用；description 决定触发场景。

### Multica 平台相关
- **Managed Agents（托管智能体）**：Multica 的核心理念——将 Agent 作为团队一等公民管理，分配任务、跟踪进度、积累技能，类似人类员工管理。
- **Polymorphic Actor（多态行动者）**：Multica 的设计范式，`actor_type` (member/agent) + `actor_id` 让 Agent 和人在同一套数据模型中平等存在。
- **Runtime（运行时）**：Agent 实际执行的环境，可以是用户本地机器（通过 Daemon 连接）或云端实例。一个 Runtime = 一台能跑 Agent 的机器。
- **Daemon（守护进程）**：用户本地运行的后台程序，自动探测 Agent CLI、注册 Runtime、轮询认领任务、隔离执行、流式上报。
- **Session Resumption（会话恢复）**：同一对 (Agent, Issue) 的下一次任务自动复用上次的 session_id 和工作目录，历史对话和文件状态保留。
- **Autopilot（自动驾驶）**：定时/Webhook/API 触发的自动化规则，自动创建 Issue 分配给 Agent（日报、Bug Triage、安全扫描等）。
- **Squad（小队）**：多个 Agent + 人类组成的团队，由 Leader Agent 路由任务，用 `@前端组` 代替 `@小张或小李或小王`。
- **Mention Side Effects（提及副作用）**：Multica 中 `@agent` 和 `@squad` 链接触发任务入队，不是纯装饰；`@member` 只是人员链接，`@issue` 是安全交叉引用。
- **MCP（Model Context Protocol）**：Anthropic 提出的工具调用协议，每个 Agent 可配置自己的 MCP 服务器列表扩展工具能力。

---

## 关键语录

> "模型会代你做错误假设，然后不假思索地执行。它们不管理自身的困惑，不寻求澄清，不呈现矛盾，不展示权衡，在应该提出异议时也不反驳。"
> —— Andrej Karpathy

> "一个 Markdown 文件冲上趋势榜第一，说明现在的瓶颈不在模型，而在模型周围的脚手架。这些'胶水'才是产品本身。"
> —— Kraggich

> "模型选错了分支，运行了 40 分钟，最后碰壁失败。而提前澄清只需要 30 秒。"
> —— Surajdotdot7

> "LLM 非常擅长循环执行直到达成特定目标……不要告诉它该做什么，给它成功标准，然后看着它完成。"
> —— Andrej Karpathy

> "好代码是简单地解决今天的问题，而不是提前解决明天的问题。"
> —— Karpathy 准则核心思想

> "说到底，Karpathy 不再只是一个你读的人，而是一个你的 Agent 可以直接继承行为的人。"
> —— 36氪报道
