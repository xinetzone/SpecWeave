---
id: "zleap-agent-wiki-workspace-context"
title: "Workspace 隔离与上下文组装"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "workspace", "context-assembly", "cache-breakpoint", "kernel", "routing", "main-space", "work-space"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent Workspace 隔离机制与上下文组装：main/work 空间、数据库为唯一真源、when/notFor 路由提示、persona、toolIds；Kernel 经 switchWorkspace 路由；Context 稳定/半稳定/可变三块组装与缓存断点不变量。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 02 Workspace 隔离与上下文组装

本章是 Zleap-Agent 的核心，讲清楚"Workspace 隔离"在代码层面到底如何实现，以及 Context 如何被组装成运行时布局。

## 2.1 Workspace 的代码模型

运行时的 Workspace 形状定义在 `packages/agent/src/workspaces/index.ts` 的 `WorkspaceSpec`：

```ts
type WorkspaceSpec = {
  id: string;
  label: string;
  icon?: string;
  kind?: 'main' | 'work';      // 'main'=常驻主空间；'work'=派发子空间
  description: string;
  when: string;                 // 一行路由提示，供内核路由使用
  notFor?: string;              // 边界提示，让路由更精准
  persona: string;              // 进入该空间时注入的系统提示词
  toolIds: string[];            // 该空间允许使用的工具 id 白名单
  status?: 'ready' | 'planned';
};
```

关键点：

| 字段 | 含义 |
|------|------|
| `kind` | `main` = 常驻主空间，其运行时 id 为 `session`；`work` = 派发子空间。 |
| `persona` | 该空间专属的系统提示词，进入空间时注入。 |
| `toolIds` | 工具白名单，隔离"该空间能做什么"。 |
| `when` / `notFor` | 路由提示与边界提示，用于让路由分发更精准。 |

## 2.2 数据库是唯一真源（零硬编码）

> **核心法则：代码中没有硬编码的 Workspace 定义。** 空间存放在数据库（唯一真源），内置默认由 seed 派生，用户自建空间在 Web UI 配置并从 store 读取。

`packages/agent/src/workspaces/index.ts` 注释明确写道：

> "There are NO hardcoded workspace definitions in code: spaces live in the database (the single source of truth). Built-in defaults are derived from the default seed so the agent is usable out of the box; user-created workspaces are configured in the web UI and read from the store at dispatch time."

`packages/core/src/workspace.ts` 的 `WorkSpaceRegistry` 只是一个内存注册表（`spaces: Map<string, WorkSpaceDefinition>`），用于运行时查找，真正的持久化定义在数据库中。

### 架构洞察

> **洞察 3：数据库真源 + 代码零硬编码，让"可配置空间"与"内置默认"统一。** 内置默认 `main` 空间通过 `defaultMainWorkspaceSpec()` 从 `createDefaultSuperAgentSeed()` 派生，与 `seedSuperAgentDefaults` 写入数据库的数据一致，因此运行时兜底与数据库永远对齐（来源：`packages/agent/src/workspaces/index.ts`）。

## 2.3 内核路由：Main → Work

内核（`packages/agent/src/kernel/kernel.ts`）是整个 workspace 入口的调度核心：

- 每条回复都先进入常驻 `session` 主空间（`main`）。
- 由**会话模型自身**调用 `switchWorkspace(space, task)` 路由到某个子空间。
- 内核不再预先挑选子空间，它只负责运行 `session` 并携带身份（identity）、记忆策略（memory policy）与召回（recall）。
- **Main→Work 深度保持在 1**（运行时工具层）。

```ts
// Kernel.dispatch 的运行目标固定是主空间
this.runtime.run({
  spaces: [spec.id],          // 只跑主空间
  goal,
  toolIds: spec.toolIds,      // 主空间允许的工具
  context: input,
  agent: this.agent,
  memory: this.memory,
});
```

### 架构洞察

> **洞察 4：Main→Work 深度为 1，路由交给模型而非硬编码。** 内核不层层递归，而是让会话模型在 `session` 空间内通过 `switchWorkspace` 自行决定进入哪个子空间——这既保持了路由的灵活性，又避免了嵌套过深导致的上下文失控（来源：`packages/agent/src/kernel/kernel.ts`）。

## 2.4 Context 布局与组装

Zleap-Agent 把上下文视为一种运行时布局：

```text
Context = System Prompt + Workspace Prompt + Tools + Memory + History
```

组装逻辑集中在 `packages/core/src/context/assembly.ts` 的 `assembleContext`，它是一个**纯排序函数**——只负责排布三块内容并声明缓存断点，不负责取记忆或生成内容（输入由 surface 层准备）。

### 三块结构

```text
stable       → systemPrompt = persona + rules + space + impressions(人)
semiStable   → 有界事件窗口 + 保留轮次
variable     → 近期轮次 + 匹配召回(老 event ∪ experience)
```

- **stable（稳定块）**：系统提示词，由 persona + rules + space instructions + impressions 组成。
- **semiStable（半稳定块）**：有界事件窗口 + 保留轮次。
- **variable（可变块）**：近期轮次 + 匹配召回（event 与 experience 的并集）。

### 缓存断点与不变量

```ts
const breakpoints: CacheBreakpoint[] = [
  { after: 'stable', messageIndex: 0 },
  { after: 'semiStable', messageIndex: input.semiStable.length },
];
```

- 稳定块没有 event/experience 文本的槽位，因此**结构性保证了"变化的记忆永不进入缓存前缀"**这一不变量。
- 缓存断点让支持的 provider 能在稳定块/半稳定块之后做 KV 缓存，从而降低重复前缀的 token 成本。

### 架构洞察

> **洞察 5：把"易变内容"从"缓存前缀"中结构性隔离，是降低成本的关键。** 通过把记忆/事件这类易变内容放在 stable 块之外，并声明缓存断点，Zleap-Agent 让每次请求尽可能复用缓存前缀（来源：`packages/core/src/context/assembly.ts`）。

## 2.5 回合循环（Turn Loop）

`packages/agent/src/workspace-turn/turnLoop.ts` 定义了单回合的边界：

- `runWorkspaceTurn(runtime, input)`：调用一次 `runModelTurn`，若工具调用达到上限则标记 `max-tool-calls`。
- 停止原因：`completed` / `max-tool-calls` / `model-stopped`。
- 工具循环上限：`MAX_TOOL_ITERATIONS`（默认 25，见 `turnLoop.ts`）限制单回合工具调用次数，防止失控循环。

## 本章小结

- Workspace 是上下文与动作的**隔离边界**，由 `persona`（系统提示词）、`toolIds`（工具白名单）、`when`/`notFor`（路由提示）刻画。
- **数据库是唯一真源**，代码零硬编码；内置默认由 seed 派生。
- 内核运行 `session` 主空间，由会话模型经 `switchWorkspace` 路由到子空间，Main→Work 深度为 1。
- Context 按 **stable / semiStable / variable** 三块组装，缓存断点 + "变化的记忆永不进入缓存前缀"不变量共同撑起低成本上下文。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [01 核心架构与技术栈](./01-core-architecture.md) | [README](./README.md) | → [03 分区记忆系统](./03-memory-system.md) |