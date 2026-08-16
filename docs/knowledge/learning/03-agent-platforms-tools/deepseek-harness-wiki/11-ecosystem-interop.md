---
id: deepseek-harness-wiki-11
title: DeepSeek Harness Wiki - 与 Claude Code/Codex/MCP 生态互操作
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - claude-code
  - codex
  - mcp
  - hooks
  - interop
  - migration
  - ecosystem
category: learning
maturity: L1
---

# 11 与 Claude Code/Codex/MCP 生态互操作

Agent 生态不是零和博弈。DeepSeek Harness 在设计之初就把「降低用户迁移成本、避免生态冷启动」作为核心目标之一——它不要求你抛弃已有的工具和习惯，而是通过无缝的互操作层，让你过去在 Claude Code、Codex、MCP 上的投资可以平滑复用。dsh 是来加入这个生态，而不是来重新发明一切的。

## 生态兼容策略：降低迁移成本，避免冷启动

在 dsh 开源之前，Claude Code 和 Codex 已经积累了大量用户和生态资源——hooks 脚本、规则文件、MCP 服务器、工作流配置等等。如果 dsh 采用「我们有全新的更好的标准，你们都重新来一遍」的态度，结果必然是生态冷启动，用户也会因为迁移成本太高而却步。

dsh 团队选择了更务实的兼容策略，可以总结为三句话：

1. **能直接复用的就直接复用**：hooks.json、AGENTS.md/CLAUDE.md、MCP 服务器这些不需要任何修改直接能用
2. **需要适配的就做桥接层**：不是要求用户改配置适配 dsh，而是 dsh 去适配现有生态的格式和约定
3. **互补而非替代**：你不需要卸载 Claude Code/Codex，它们可以和 dsh 共存，甚至互相调用

### 为什么这很重要

这种兼容策略带来的好处是实实在在的：
- **零成本试用**：你可以今天就装 dsh 试试，不需要改任何现有配置，不需要迁移你的规则和 hooks
- **技能复用**：你之前学的 Claude Code 技巧、写的规则、积累的工作流，大部分在 dsh 里直接生效
- **渐进式迁移**：你可以先在个人项目试用 dsh，同时继续用 Claude Code 处理工作项目，慢慢过渡
- **生态借力**：dsh 从第一天起就有 MCP 生态里成百上千个现成工具可用，不需要等社区重新开发

这和很多「NIH 综合症（Not Invented Here）」严重的开源项目形成了鲜明对比——dsh 选择站在已有生态的肩膀上，而不是推倒重来。

## Claude Code hooks 桥接：复用 hooks.json

Hooks 是 Claude Code 最受欢迎的扩展机制之一，很多用户都积累了自己的 `hooks.json` 和配套脚本。dsh 原生支持 Claude Code hooks 格式，不需要任何修改。

### 什么是 Claude Code hooks

如果你用过 Claude Code，你应该已经熟悉 hooks：它允许你在特定事件（如工具调用前/后、会话开始/结束等）触发自定义脚本，用来做权限控制、通知、审计、额外校验等等。

典型的 Claude Code `hooks.json` 长这样：

```json
{
  "hooks": {
    "before-tool-call": [
      {
        "matcher": "bash",
        "command": "python scripts/approve-command.py"
      }
    ],
    "after-tool-call": [
      {
        "matcher": "*",
        "command": "node scripts/log-to-audit.js"
      }
    ],
    "session-start": [
      {
        "command": "echo '会话开始了' && say 'Agent started'"
      }
    ]
  }
}
```

### dsh 如何支持 hooks

dsh 内置了 Claude Code hooks 桥接插件，默认启用。它的工作原理是：

1. 启动时自动查找项目根目录下的 `.claude/hooks.json` 和 `~/.claude/hooks.json`
2. 把 Claude Code 的 hook 事件映射到 dsh 对应的 Cordis 事件上
3. 在对应事件触发时，按照 Claude Code 相同的语义调用你的脚本
4. 脚本的 stdin/stdout、环境变量、退出码语义完全和 Claude Code 保持一致

**事件映射关系：**

| Claude Code Hook 事件 | dsh 对应事件 | 语义一致吗？ |
|----------------------|--------------|--------------|
| `before-tool-call` | `tools/before-call`（瀑布事件） | ✅ 完全一致，可以拒绝工具调用 |
| `after-tool-call` | `tools/after-call`（广播事件） | ✅ 完全一致，拿到工具结果 |
| `session-start` | `session/start` | ✅ 完全一致 |
| `session-end` | `session/end` | ✅ 完全一致 |
| `user-message` | `user/message` | ✅ 完全一致 |
| `assistant-message` | `assistant/message` | ✅ 完全一致 |

### 实际效果

这意味着什么？
- 你现有的 `hooks.json` 不用改一个字，dsh 里直接生效
- 你之前写的 hooks 脚本（权限校验、通知、审计等）不需要重写
- 同样的 hooks 配置可以同时在 Claude Code 和 dsh 中工作，你用哪个都可以

**示例：命令审批 hook**

如果你有一个 hook 用来拦截危险命令，它在 Claude Code 里工作，在 dsh 里也会同样工作——dsh 调用 bash 工具前会触发你的 `before-tool-call` hook，如果你的脚本返回非零退出码，dsh 会拒绝执行命令，和 Claude Code 的行为完全一致。

### 启用/禁用 Hooks 桥接

如果你不想用 Claude Code hooks，可以在设置中关闭：

```yaml
# ~/.dsh/settings.yaml
interop:
  claudeCode:
    enableHooks: false
```

或者通过环境变量 `DSH_DISABLE_CLAUDE_HOOKS=1` 临时关闭。

## Codex 兼容：OpenAI Responses API 原生支持、一键配置脚本

Codex 是 OpenAI 推出的代码 Agent，同样拥有一批用户。dsh 对 Codex 的支持体现在两个层面：API 协议原生兼容，以及一键配置脚本。

### OpenAI Responses API 原生支持

Codex 使用 OpenAI 最新的 **Responses API**，而不是传统的 Chat Completions API。dsh 的模型抽象层原生支持 Responses API 协议：

- 添加 OpenAI Provider 时，支持 Responses API 的模型会自动使用新协议
- 完整支持 Responses API 的特性：内置推理内容分离、多轮工具调用状态管理、结构化输出等
- 工具调用格式和语义与 Codex 保持一致，不需要做格式转换

这意味着如果你用 OpenAI 的模型（特别是 o1、o3、GPT-4o 等针对 Responses API 优化的模型），在 dsh 里能获得和 Codex 一样的模型调用质量，不会因为协议转换导致效果下降。

### 一键配置 Codex

如果你已经安装并配置了 Codex CLI，dsh 提供了一键配置命令，可以自动导入 Codex 的配置：

```bash
npx @deepseek-ai/dsh setup-codex
```

这个命令会自动完成以下操作：
1. 检测你本机是否安装了 Codex CLI（`codex --version`）
2. 读取 Codex 的配置文件（通常在 `~/.codex/config.json`）
3. 提取 API Key、模型设置、API Base URL 等配置
4. 在 dsh 中自动添加 OpenAI Provider，配置好 Codex 模型
5. 导入 Codex 的自定义指令和工具配置
6. 设置好适当的参数默认值（上下文窗口、输出限制等）

整个过程不需要你手动复制粘贴任何信息，一条命令搞定。

### Codex 专属模型预设

导入后，dsh 会自动配置 Codex 常用模型的优化参数：

| 模型 | 预设参数 |
|------|----------|
| `codex-mini` | 针对快速编码任务优化，低延迟，低成本 |
| `codex-standard` | 默认平衡配置，适合大多数任务 |
| `codex-pro` | 针对复杂任务优化，高推理强度，长输出 |

这些预设参数和 Codex 官方默认值保持一致，所以你在 dsh 里用 Codex 模型的体验会和直接用 Codex CLI 非常接近。

## MCP 客户端支持

MCP（Model Context Protocol）是 Anthropic 推出的开放工具协议，已经被越来越多的 Agent 工具支持，生态里已经有数百个 MCP 服务器可用。dsh 内置 MCP 客户端支持，可以直接使用所有现成的 MCP 服务器。

### 什么是 MCP

简单来说，MCP 是一个标准化协议，让 Agent 可以以统一方式接入外部工具和数据源。你不需要为每个 Agent 框架单独写工具适配器——只要工具实现了 MCP 服务器接口，所有支持 MCP 的 Agent 都能直接用。

常见的 MCP 服务器包括：
- 文件系统、数据库连接器
- GitHub、GitLab、Jira、Slack 等 SaaS 服务集成
- 浏览器自动化、代码解释器
- 各种内部工具和 API 封装

### dsh 中配置 MCP

dsh 原生支持读取标准的 MCP 配置文件，不需要插件。

**步骤 1：创建 MCP 配置文件**

在项目根目录或 `~/.dsh/` 下创建 `mcp.json`，格式和 Claude Code/Cursor 等工具完全兼容：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-github-token-here>"
      }
    },
    "postgres": {
      "command": "uvx",
      "args": ["mcp-server-postgres", "--connection-string", "<postgres-connection-string>"]
    }
  }
}
```

**步骤 2：重启 dsh（或在 Creator 模式下热重载）**

dsh 启动时会自动加载 `mcp.json`，启动所有配置的 MCP 服务器，把它们提供的工具自动注册到 dsh 工具系统中。

### 使用 MCP 工具

MCP 工具加载后，和 dsh 原生工具没有任何区别：
- 模型可以像调用内置工具一样调用 MCP 工具
- 工具调用和结果会完整记录在会话日志和 Trajectory 中
- 权限审批机制同样适用于 MCP 工具
- MCP 工具出问题有完整的错误日志和调试信息
- 你可以在 Creator 模式的插件树中查看已加载的 MCP 服务器和工具

**关键优势：因为 MCP 支持是作为标准 Capability Seam Provider 实现的，所以你从 Claude Code 迁移到 dsh 时，原来用的 MCP 工具一个都不用丢。**

## AGENTS.md/CLAUDE.md 自动读取规则

AGENTS.md 和 CLAUDE.md 是项目级的「Agent 说明书」，用来告诉 Agent 项目的约定、代码风格、常用命令、注意事项等。这是 Claude Code 用户非常熟悉的约定，dsh 完全兼容并扩展了这一机制。

### 什么是 AGENTS.md/CLAUDE.md

简单来说，AGENTS.md（或 CLAUDE.md）就是放在项目根目录（或子目录）下的 Markdown 文件，里面写着给 Agent 看的项目说明：

```markdown
# 项目说明

## 代码风格
- 使用 TypeScript，严格模式
- 缩进用 2 空格，不要 tab
- 函数必须有 JSDoc 注释

## 常用命令
- 安装依赖：pnpm install
- 启动开发：pnpm dev
- 运行测试：pnpm test
- 构建：pnpm build

## 注意事项
- 不要修改 src/generated/ 目录下的文件，这些是自动生成的
- 提交前必须跑 lint 和测试
- API 密钥不要硬编码，用环境变量
```

Agent 启动时会自动读取这些文件，作为上下文的一部分，所以它从一开始就「了解」项目的规矩。

### dsh 中的自动读取规则

dsh 会按照以下顺序自动查找和读取规则文件：

1. **全局规则**：`~/.dsh/AGENTS.md`，对所有项目生效
2. **用户主目录 .claude 规则**：`~/.claude/CLAUDE.md`，兼容 Claude Code 全局规则
3. **项目根目录**：`<workspace>/AGENTS.md` 和 `<workspace>/CLAUDE.md`
4. **目录级联**：进入子目录时，如果子目录有自己的 AGENTS.md/CLAUDE.md，也会被读取
5. **Git 子模块**：如果你在子模块目录里工作，子模块根目录的规则文件也会被读取

所有这些文件的内容会被合并，注入到系统提示词中。

### 读取优先级和合并规则

当多个规则文件都存在时，合并规则是：
- 越具体的规则优先级越高（子目录规则覆盖父目录规则）
- 项目规则覆盖全局规则
- AGENTS.md 优先级高于 CLAUDE.md（dsh 原生格式优先）
- 冲突时以优先级高的文件为准，不会报错

### 为什么同时支持 AGENTS.md 和 CLAUDE.md

- 如果你的项目已经有 CLAUDE.md 了，不需要重命名或复制，直接生效
- 新项目推荐用 AGENTS.md，这是更中立的名字（未来会有更多工具支持）
- 你可以两者都有，通用约定写 CLAUDE.md（兼容 Claude Code），dsh 专属的高级配置写 AGENTS.md

**注入位置**：这些规则文件的内容会在 `agent/pre-step` 阶段被注入到系统提示词中，你可以在 Trajectory 视图里看到完整的注入内容，包括来自哪个文件。

## 任务委托机制：委托给本机 Claude Code/Codex

互操作不止于「复用配置」——dsh 甚至可以把任务直接委托给本机安装的 Claude Code 或 Codex 执行，自己作为协调者。这个功能默认关闭，但你可以选择性开启。

### 委托机制的工作原理

这是 Capability Seam 设计威力的又一个绝佳展示。我们在第 9 章讲过 Subagent Seam——子 Agent 服务的 Provider 是可替换的。dsh 内置了两个可选的 Subagent Provider：

| Provider | 作用 |
|----------|------|
| **LocalSubagentProvider**（默认） | 启动新的 dsh 子 Agent 实例执行任务 |
| **ClaudeCodeDelegationProvider** | 把任务委托给本机 Claude Code CLI 执行 |
| **CodexDelegationProvider** | 把任务委托给本机 Codex CLI 执行 |

当你启用委托 Provider 后，模型调用 `spawn_subagent` 工具时，就会启动对应的外部 Agent 来执行任务，而不是拉起新的 dsh 实例。

### 启用委托

默认关闭，需要在配置中手动开启：

```yaml
# ~/.dsh/settings.yaml
interop:
  delegation:
    # 允许委托给 Claude Code（需要已安装 claude 命令）
    claudeCode:
      enabled: true
      # 可选：指定 Claude Code 可执行文件路径
      # path: /usr/local/bin/claude
      # 可选：传给 Claude Code 的额外参数
      # args: ["--model", "claude-3-5-sonnet"]

    # 允许委托给 Codex（需要已安装 codex 命令）
    codex:
      enabled: true
      # 可选：指定 Codex 可执行文件路径
      # path: /usr/local/bin/codex
```

### 使用场景

什么时候需要把任务委托给其他 Agent？几个典型场景：

1. **模型能力互补**：
   - 主控用 DeepSeek V4 Pro 做规划和架构设计
   - 某个子任务特别适合 Claude Sonnet 处理（比如长文档理解），就委托给 Claude Code
   - 快速批量小任务委托给 Codex 或 v4-flash

2. **生态工具复用**：
   - Claude Code 上有个你特别喜欢的 MCP 工具或插件，暂时还没有 dsh 版本
   - 把需要那个工具的子任务委托给 Claude Code 跑，结果拿回来继续

3. **A/B 对比**：
   - 同一个任务同时派给 dsh、Claude Code、Codex 三方跑
   - 对比结果选最好的，或者做模型输出投票

4. **渐进式迁移**：
   - 你已经深度使用 Claude Code 了，但想试试 dsh
   - 可以先用 dsh 作为主控，大部分任务还是委托给 Claude Code 做
   - 慢慢把更多任务迁移到 dsh 原生执行，平滑过渡

### 委托是如何实现的

当任务被委托时：
1. dsh 把任务描述、上下文、相关文件信息传给外部 Agent CLI
2. 外部 Agent 在自己的进程中执行任务，可以使用它自己的所有工具和能力
3. dsh 实时流式获取外部 Agent 的输出和工具调用日志
4. 所有执行过程（包括外部 Agent 的输出）都记录在 dsh 的会话日志中
5. 在 Trajectory 视图里，你可以看到「委托给 Claude Code」这样的节点，展开可以看到 Claude Code 的完整执行过程
6. 任务完成后，外部 Agent 的输出被返回，作为子任务结果交给主控 dsh 继续处理

整个过程是透明的，你在 Trajectory 里能看到所有细节，不会变成「黑盒」。

> **安全提示**：委托功能意味着 dsh 可以启动其他程序并传数据给它们。请只在你信任的环境中启用，并且不要把 dsh 暴露为对外服务（本来它也被设计为只服务本机）。

## 共存策略：互补而非替代

说了这么多互操作能力，核心其实是一个态度：**dsh 不追求替代 Claude Code 或 Codex，它们各有所长，可以共存、互补、协同工作。**

### 三者的定位差异

我们客观对比一下三个工具的定位：

| 维度 | DeepSeek Harness | Claude Code | Codex |
|------|-----------------|-------------|-------|
| **本质** | 造 Agent 的框架 + 可用成品 | 成熟的商用 Agent 产品 | OpenAI 官方 Agent CLI |
| **开源程度** | 完全开源 MIT | 闭源 CLI | 半开源（SDK 开源，CLI 部分闭源） |
| **扩展能力** | 极强（一切皆插件，循环都能换） | 中等（hooks + MCP） | 中等（插件体系还在发展） |
| **可观测性** | 极强（Trajectory、完整日志、分叉回放） | 一般 | 一般 |
| **多模型支持** | 原生多模型，任意厂商 | 主要优化 Claude | 主要优化 OpenAI 模型 |
| **成熟度** | 开发者预览版，迭代快 | 生产可用，稳定 | 生产可用，稳定 |
| **UI** | 本地 Web UI + 无头模式 | 终端 UI | 终端 UI |
| **适合场景** | 深度定制、研究、二次开发、多模型切换 | 日常编程、开箱即用、稳定可靠 | OpenAI 生态用户、Responses API 场景 |

没有谁「更好」，而是谁更适合你的场景。

### 推荐的共存方式

对于大多数开发者，推荐这样的组合方式：

1. **日常简单任务**：用你最顺手的那个（比如 Claude Code），没必要强行换
2. **需要可观测性/调试/复盘的复杂任务**：用 dsh，Trajectory 帮你省很多调试时间
3. **需要多模型对比/切换**：用 dsh，灵活切换 DeepSeek/Anthropic/OpenAI/本地模型
4. **想做自定义扩展/写插件/搭内部工具**：用 dsh，框架给你最大的自由度
5. **团队/公司标准化 Agent 平台**：用 dsh 做底座，基于它搭内部工具，因为它完全可控可定制
6. **MCP 工具、hooks、规则文件**：不用改，所有工具都能用

它们可以同时安装在你的机器上，互不干扰——你完全可以早上用 Claude Code 写代码，下午用 dsh 调试一个复杂的多步骤问题，晚上用 Codex 跑批量重构，三者共享同一套项目规则和 MCP 配置。

## 迁移注意事项

如果你决定从 Claude Code 或 Codex 迁移到 dsh（或者部分迁移），这里有几个实际的注意事项：

### 不需要迁移的东西（直接复用）

✅ 你的 AGENTS.md/CLAUDE.md 规则文件
✅ 你的 hooks.json 和 hooks 脚本
✅ 你的 mcp.json 和所有 MCP 服务器
✅ 你的项目约定和工作流习惯
✅ 你对工具调用、权限审批这些核心概念的理解

### 需要调整的东西

🔄 **快捷键和 UI 操作**：dsh 主要是 Web UI，快捷键和 Claude Code/Codex 的终端快捷键不完全一样，需要熟悉一下
🔄 **模型配置**：你需要在 dsh 里重新配置 API Key（或者用 `setup-codex` 一键导入）
🔄 **部分高级 hooks**：特别复杂的 hooks 如果依赖 Claude Code 特定的环境变量或行为，可能需要小调整
🔄 **自定义命令**：Claude Code 的 `/command` 自定义命令需要转成 dsh 的命令插件（格式很相似，迁移不难）

### 暂时缺失的能力（v0.1 阶段）

⚠️ 自动更新检查和提示（后续版本会加）
⚠️ IDE 插件（VS Code 插件还在开发中，现在只能用 Web UI）
⚠️ 部分高级记忆/压缩功能（官方只给了基础实现，等社区插件或后续版本）
⚠️ 移动端支持（设计上只考虑桌面端）

### 迁移建议：渐进式，不要一刀切

不要第一天就把 Claude Code/Codex 卸载了全换成 dsh——这是开发者预览版，还在快速迭代，会有 bug 和不完整的功能。推荐的迁移节奏：

1. **第一周**：安装 dsh，在个人玩具项目试试，感受一下 UI、Trajectory、多模型切换，不用改任何配置
2. **第二周**：开始在一些非核心工作项目用 dsh，遇到问题记下来，用 Claude Code 兜底
3. **一个月后**：评估 dsh 是否满足你的需求，决定是否把主要工作流迁移过去
4. **长期**：两者（或三者）共存，根据任务选择最合适的工具

记住：工具是用来帮你解决问题的，不是用来站队的。哪个好用用哪个，能解决问题就行——这也是 dsh 团队做生态兼容的初衷。

理解了 dsh 的生态互操作能力，你就可以放心尝试它，不用担心过去的投资浪费，也不用担心被锁死在一个工具上。下一章我们将介绍 dsh 的无头模式和 SDK，看看如何把 dsh 嵌入到你自己的程序和工作流中。

---

← [10 插件开发](10-plugin-development.md) | → [12 无头模式与 SDK](12-headless-sdk.md)
