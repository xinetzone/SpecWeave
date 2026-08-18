---
id: deepseek-harness-wiki-05
title: DeepSeek Harness Wiki - 核心架构：一切皆插件
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
  - external/libs/deepseek-harness源码
  - external/libs/cordis源码
date: 2026-08-17
tags:
  - deepseek
  - agent
  - harness
  - architecture
  - cordis
  - plugin
  - bundle
  - profile
category: learning
maturity: L1
---

# 05 核心架构：一切皆插件

「一切皆插件」是 DeepSeek Harness 最核心的设计哲学。与传统框架将核心逻辑硬编码在主干中不同，dsh 从底层元框架到上层 Agent 循环、工具、UI，所有组件都是地位平等的插件，没有任何特权内核存在。本章深入解读这一架构设计。

## 设计哲学深度解读

大多数 Agent 框架的架构是「内核 + 扩展点」模式：
- 存在一个不可修改的特权内核，包含核心循环、调度逻辑
- 预留若干 hook/扩展点，允许开发者在特定节点插入自定义逻辑
- 要修改核心行为必须 fork 源码、改动主干

dsh 完全抛弃了这种模式，选择了**彻底的插件化**：
- 不存在特权内核，没有任何一部分逻辑是「内置不可修改」的
- 模型适配器、工具注册表、会话日志、Agent 循环本身，乃至整个 UI 层，都是普通插件
- 插件之间通过统一的上下文（Context）和事件系统通信，地位完全平等
- 你可以替换任何一个组件，包括别人以为是「核心」的那部分

这一设计带来的直接结果是：**扩展 dsh 不需要「打补丁」或修改源码**——你只需要把自己的插件挂载到插件树上，不需要的插件直接卸载即可。

## Cordis 元框架：一切皆插件的地基

dsh 的底层由一个名为 **Cordis** 的元框架驱动。

### 论文来源

Cordis 的设计思路源自学术论文《A Programming Paradigm for Spatiotemporal Composability》（时空可组合性的编程范式）：
- 论文地址：[https://github.com/cordiverse/paper/blob/main/paper.pdf](https://github.com/cordiverse/paper/blob/main/paper.pdf)
- 代码仓库：[https://github.com/cordiverse/cordis](https://github.com/cordiverse/cordis)（已作为 `external/libs/cordis` 引入）

Cordis 不是一个 Agent 框架，它是一个更底层的**插件化元框架**——定义了插件如何注册、如何通信、如何叠加、如何撤销的一套通用机制，dsh 是在这套元框架上构建出来的 Agent 运行时。

### Cordis 五种核心概念

Cordis 的世界观由五个核心概念构成，缺一不可：

#### 1. 插件：实现 Service 的对象

插件有三种合法形态，本质都是向 Context 贡献服务：

```typescript
// 形态 1：函数插件（带可选 inject 和 apply）
const myPlugin = (ctx: Context) => {
  // 插件逻辑
};
myPlugin.inject = ['tools', 'llm']; // 声明依赖的服务
myPlugin.apply = (ctx: Context) => { /* 自定义应用逻辑 */ };

// 形态 2：Service 子类
class MyService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'myService'); // 注册到 ctx.myService
  }
}

// 形态 3：普通对象
const plainPlugin = {
  inject: ['config'],
  apply(ctx: Context) {
    // 对象形式插件逻辑
  }
};
```

#### 2. 上下文：服务容器

Context 是插件运行的容器，每个服务占据稳定的 `ctx.<key>` 命名空间：
- 例如 `ctx.tools`、`ctx.llm`、`ctx.sessions` 都是稳定的服务键
- 插件通过 key 查找服务，而不是通过模块导入
- 这意味着服务可以被替换，只要保持相同的 key 和接口契约

#### 3. inject：声明式服务依赖

插件通过 `inject` 字段声明自己依赖哪些服务：
- Cordis 保证所声明的依赖服务全部就绪后才启动插件
- 加载顺序由依赖关系自动推导，不需要手动编排
- 循环依赖会在启动时被检测并报错

#### 4. 类型化事件：五种分发模式

Cordis 提供五种事件分发模式，覆盖不同场景：

| 模式 | 签名 | 行为 | 典型场景 |
|------|------|------|----------|
| `emit` | `ctx.emit(name, ...args)` | 同步执行，不 await，监听器按注册顺序观察，无返回值 | 纯通知、日志广播、状态更新 |
| `bail` | `ctx.bail(name, ...args)` | 同步执行，按注册顺序调用监听器，第一个返回非 `null`/`undefined` 的结果直接返回，短路后续监听器 | 注册表查找、第一个匹配处理器获胜 |
| `parallel` | `ctx.parallel(name, ...args)` | await 所有监听器**并行**执行，无返回值 | 扇出通知、多监听器独立并行处理、遥测上报 |
| `serial` | `ctx.serial(name, ...args)` | await 监听器按注册顺序**串行**执行，有返回值 | 责任链、顺序校验、结果投票（如 `agent/turn-stopping`） |
| `waterfall` | `ctx.waterfall(name, ...args, next)` | 环绕中间件模式，监听器接收 `(...args, next)`，**必须**调用 `next()` 才能继续执行下游，不调用则短路流程 | 请求拦截改写、权限校验、中间件管道（如 `agent/pre-step`、`tools/execute`） |

> **重要修正**：早期文档只提到 waterfall，实际 Cordis 源码（`events.ts` 中 `DispatchMode` 类型定义）提供以上五种分发模式，dsh 中五类事件都有使用。事件的分发模式通过 TypeScript JSDoc 的 `@mode` 标签标注。

#### 5. 注册是可逆副作用

所有通过 Context 进行的注册（事件监听、服务注册、配置修改）都是可逆的：
- 通过 `ctx.effect()` 或 `ctx.on()` 安装的副作用，会在 reload/teardown 时自动撤销
- 不需要手动管理清理逻辑，插件卸载即恢复原状

### 无特权内核设计原则

无特权内核是 Cordis 最重要的设计原则：
- 不存在一个「特殊」的内核插件拥有更高权限
- 框架启动时，最先加载的也只是一个普通插件
- 你可以卸载任何插件，包括别人认为是「系统核心」的组件
- 所有插件遵循完全相同的接口规范和生命周期

这意味着：官方发布的默认插件集合只是一种「出厂配置」，而不是「唯一正确的形态」。

## 可逆效应：插件卸载自动清理

可逆效应（Reversible Effects）是 Cordis 保证插件干净卸载的核心机制。

### 问题的提出

传统插件系统经常遇到「卸载不干净」的问题：
- 插件注册了事件监听，卸载后没有移除，导致内存泄漏
- 插件修改了全局配置，卸载后没有还原，影响后续运行
- 插件在文件系统写入了文件，卸载后留下垃圾文件
- 插件注册了服务，卸载后服务仍在注册表中导致冲突

### 可逆效应的解决方式

Cordis 要求插件在产生任何副作用时，都必须同时注册对应的「撤销函数（disposer）」：
- 监听事件时，`ctx.on()` 自动返回一个取消监听的 disposer
- 注册服务时，返回一个注销服务的 disposer
- 修改配置时，记录修改前的值，返回还原 disposer
- 创建资源时，返回释放资源的 disposer

`ctx.effect()` 是通用副作用注册 API，支持四种 disposer 形式：

| disposer 类型 | 说明 |
|---------------|------|
| 函数 `() => void` | 同步清理函数，最常用 |
| Generator | 可暂停的清理流程 |
| Promise | 异步清理，await 完成 |
| AsyncGenerator | 异步可暂停的清理流程 |

**执行顺序**：所有 disposer 按注册逆序执行（栈顺序，LIFO），保证依赖的资源先释放——例如如果插件 B 依赖插件 A，那么 B 先卸载，A 后卸载，避免依赖悬空。

当插件被卸载时，Cordis 会自动执行该插件注册过的所有撤销函数，将系统恢复到插件加载前的状态——就像这个插件从来没有存在过一样。

这就是「可逆效应」的含义：**插件产生的所有效应都是可逆的，卸载即清理，不留痕迹**。

### 实际价值

可逆效应机制让 dsh 的插件组合变得极其安全：
- 你可以大胆试验新插件，不满意直接卸载，不会污染系统
- 可以动态切换实现（换模型适配器、换沙箱、换循环），不需要重启
- 不存在「卸载了插件但还有残留」的灵异问题
- 插件组合是可预测的，不会因为加载顺序产生难以调试的副作用

## Bundle：能力捆绑包分发格式

**Bundle** 是 dsh 的插件分发格式，相当于「插件包」。

### Bundle 是什么

一个 Bundle 是一个可分发的单元，通常包含：
- 一组 Cordis 配置行（声明要注册哪些服务、监听哪些事件、挂载哪些插件）
- 配置行要挂载的实际代码（JavaScript/TypeScript 模块）
- 元数据（名称、版本、描述、依赖等）

你可以把 Bundle 理解为「一份可安装的能力清单 + 实现代码」。

### Bundle 的关键特性

Bundle 最重要的特性是：**Bundle 插入的任何内容，仍然可以被上层继续打补丁（Patch）**。

也就是说，Bundle 不是「最终配置」——它只是「基础配置」，上层可以随时覆盖或修改 Bundle 提供的任何配置行。这是分层叠加机制的基础。

### 常见内置 Bundle

dsh 默认提供多个内置 Bundle，例如：
- `core/model-adapters`：模型适配器 Bundle，包含 DeepSeek、OpenAI、Anthropic 等适配器
- `core/tools`：核心工具 Bundle，包含文件操作、Shell 执行、编辑等基础工具
- `core/session-log`：会话日志 Bundle，实现 append-only 事件流
- `core/agent-loop`：默认 Agent 循环实现
- `web/ui`：Web UI 层 Bundle

## Profile：命名组合清单

**Profile** 是存放在本地的一份「命名组合清单」，定义了「我要加载哪些 Bundle、应用哪些补丁」。

### Profile 是什么

如果说 Bundle 是「零件」，那么 Profile 就是「组装说明书」：
- Profile 是一个有名字的配置（如 `web`、`headless`、`minimal`、`creator`）
- 它按顺序罗列自己要叠加哪些 Bundle
- 它可以安装 Bundle 之外的树外插件
- 它保存该 Profile 专属的补丁配置
- Profile 文件存放在 `~/.dsh/profiles/` 目录下

### 内置 Profile 模板

dsh 出厂时自带两个预置 Profile 模板：

| Profile | 用途 | 对应模式 |
|---------|------|----------|
| `web` | 带 Web UI 的完整模式，默认配置 | Standard 模式 |
| `headless` | 无头模式，无 UI，适合命令行一次性执行任务 | 无头运行 |

四种运行模式本质上是基于这两个基础 Profile 叠加补丁而来的。

### 用户自定义 Profile

你可以创建自己的 Profile：
1. 在 `~/.dsh/profiles/` 下新建一个目录，目录名就是 Profile 名称
2. 在目录中编写 `profile.yml`，声明要加载的 Bundle 列表
3. 添加你自己的补丁文件
4. 启动时用 `--profile 你的profile名` 即可使用

通过自定义 Profile，你可以组合出完全属于自己的 Agent 形态。

## 分层叠加机制与补丁系统

dsh 启动时，并不是简单地加载一个固定配置，而是**按固定顺序分层叠加**，最终构建出运行时的插件树。

### 五层叠加精确顺序

运行时配置从空条目列表开始，从下到上依次叠加，上层覆盖下层：

```
第 1 层：dsh-base 基础层
  ↓（每个 profile 的第一层：模型适配器、工具、持久化、沙箱与审批、设置、凭据、遥测）
第 2 层：Profile Bundle 层
  ↓（按 profile 列出的顺序应用每个组合包，如 dsh-web-app 增加浏览器应用；dsh-headless 增加一次性运行器且无服务器）
第 3 层：Profile 补丁层
  ↓（应用 profile 自己的 cordis.patch.yml）
第 4 层：Home 级补丁层
  ↓（应用 ~/.dsh/ 目录下的 cordis.patch.yml 全局补丁）
第 5 层：命令行 Overlay 层
    （应用任意 --patch 命令行参数传入的临时补丁）
```

每一层都可以修改、覆盖、插入下层的任意配置行，最终叠加结果就是实际运行的配置。

### 补丁（Patch）机制详解

补丁是分层叠加的核心单元。补丁的工作原理是：

1. **按 id 定位配置条目**：每一条 Cordis 配置条目都有唯一的 id
2. **支持两种操作**：
   - **替换（Replace）**：用新的配置整体替换原有条目（不是局部修改，是整个 config 替换）
   - **插入（Insert）**：插入新条目
3. **补丁只声明差异**：你不需要写完整配置，只需要写你要改的那部分

举个例子，如果你想把默认的 DeepSeek 模型适配器换成你自己实现的版本，只需要写一个补丁：

```yaml
patch:
  - replace:
      id: core/model-adapters/deepseek
      with:
        # 你自己的适配器配置
        import: ./my-custom-deepseek-adapter.ts
        config:
          apiEndpoint: "https://your-custom-endpoint.example.com"
```

不需要改源码，不需要重新编译，只需要把这个补丁放在对应层，重启即可生效。

### `--dump-config`：查看实际启动的配置树

你可以用 `--dump-config` 命令查看当前配置叠加后的最终结果：

```bash
npx @deepseek-ai/dsh --profile web --dump-config
```

这条命令会打印出：
- 最终加载的所有插件列表
- 每一条配置条目的最终值
- 每个配置条目的来源（来自哪个 Bundle、被哪个补丁修改过）
- 完整的服务注册表和事件监听器

打印出来的任意一行，你都可以写补丁替换掉。这是调试配置、理解系统结构的最重要工具。

## 事件三大域

dsh 在 Cordis 事件系统基础上，将事件划分为三大域，承担不同职责：

### 1. 会话事件（Session Events）

- 追加到会话日志并通过 `session/event` 广播的持久事实
- 重启后仍然存在，因为它们被写入 append-only 日志
- 例如：用户消息、助手回复、工具调用、工具结果、Agent 状态变更
- 用于审计、回放、UI 渲染

### 2. Agent 事件（agent/*）

- 命名空间：`agent/inbox`、`agent/step`、`agent/status`、`agent/request`、`agent/validate`、`agent/continue`
- 携带活跃 Agent 引用，用于观察/拦截进行中的工作
- 是拦截和修改 Agent 行为的主要扩展点
- 例如：在 `agent/request` 上挂载 waterfall 中间件可以在模型调用前修改请求

### 3. 能力事件（Capability Seam Events）

- 命名空间：`fs/*`、`tools/*`、`telemetry/*` 等
- 无需导入循环即可向 capability seam 附加策略和适配器
- 例如：监听 `fs/read` 可以审计所有文件读取；监听 `tools/before-execute` 可以做工具调用审批
- 这是实现横切关注点（安全审计、限流、日志）的推荐方式

## 核心服务分类概览

dsh 的所有核心能力都通过 `ctx` 上的稳定服务键暴露，按角色可分为三类：

| ctx 键 | 角色 | 职责 |
|--------|------|------|
| `ctx.sessions` | core | 仅追加 SessionEvent 日志和内存存储 |
| `ctx.systemPrompt` | core | 提示词片段与工具 schema 组装 |
| `ctx.tools` | core | 作用域化工具注册表和带把关的执行流水线 |
| `ctx.agents` | core | Agent 接口、活跃 agent 注册表和 agent/* 事件 |
| `ctx.agentLoop` | bundle | 默认循环驱动器（唯一具体循环插件） |
| `ctx.llm` | seam | 消息与流式词汇表、适配器注册 |
| `ctx.fs` | seam | 文件系统提供方 |
| `ctx.shell` | seam | Bash 执行器 |
| `ctx.subprocess` | seam | 子进程 spawn |
| `ctx.terminals` | seam | 持久化 PTY 会话 |
| `ctx.sandbox` | seam | 进程沙箱 |
| `ctx.approval` | seam | 权限审批 |
| `ctx.credentials` | seam | 凭据管理 |
| `ctx.subagents` | seam | 子 Agent 提供方 |
| `ctx.web` | seam | 网页搜索和抓取 |
| `ctx.jobs` | seam | 后台任务注册表 |
| `ctx.goals` | core | 同会话目标管理 |
| `ctx.skills` | seam | Skill 提供方注册 |
| `ctx.lsp` | seam | 语言服务器导航 |
| `ctx.mcp` | - | MCP 客户端桥接 |
| `ctx.workflowEngine` | seam | 工作流脚本引擎 |

**角色说明**：
- **core**：框架核心服务，定义了 dsh 的基本骨架，通常不建议替换
- **bundle**：具体实现 Bundle，可以替换
- **seam**：能力接缝（Capability Seam），是扩展和定制的主要位置

## 扩展指南：新行为归属位置决策表

当你想为 dsh 添加新能力时，根据目标选择正确的注册位置：

| 目标 | 机制 |
|------|------|
| 添加模型提供方 | 在 `ctx.llm` 上注册适配器 |
| 添加面向模型的能力 | 在 `ctx.tools` 上注册 |
| 添加 shell 执行 | 注册 `ctx.shell` 后端 |
| 添加持久化终端 | 注册 `ctx.terminals` 后端 + `dsh-tool-terminal` |
| 添加用户命令 | 在 `ctx.commands` 上注册（无需模型轮次） |
| 添加后台工作 | 在 `ctx.jobs` 上注册，`job_*` 工具收集/停止 |
| 添加文件系统访问/策略 | 注册 `ctx.fs` 提供方或监听 `fs/*` 事件 |
| 限制启动进程 | 使用 `ctx.sandbox` 后端 |
| 拦截请求/工具/轮次 | 使用 `agent/*` 或 `tools/*` 事件 |
| 添加模型可见上下文 | 调用 `agent.inject()` |
| 添加 UI/编辑器集成 | 驱动 `ctx.agents` 并从 `session/event` 渲染 |
| 管理同会话目标 | 使用 `ctx.goals` |
| fork 活跃会话 | `ctx.sessions.fork(source, boundary?, childId?)` |
| 将注册限定到单个 agent | 使用该 agent 的 `agent.ctx` |

## 架构价值：从改代码到改配置

「一切皆插件」架构带来的最大价值是：**换模型、换工具、换沙箱、换循环——这些原本需要改代码的操作，现在都变成了改配置**。

### 传统框架 vs dsh

| 操作 | 传统框架 | dsh |
|------|----------|-----|
| 换一个模型提供商 | 修改模型适配层代码，重新编译，可能破坏其他功能 | 写一个补丁替换模型适配器 Bundle，一行配置搞定 |
| 添加一个自定义工具 | 实现工具接口，注册到工具注册表，修改框架初始化代码 | 写一个插件，在 `ctx.tools` 注册，不需要改其他地方 |
| 替换沙箱实现 | 重构文件系统和子进程调用，侵入式修改 | 替换 Capability Seam 的 Provider，一次替换处处生效 |
| 完全改写 Agent 循环逻辑 | fork 整个项目，大改核心循环，难以合并上游更新 | 卸载默认 `core/agent-loop` 插件，挂载自己的循环插件 |
| 定制 UI 界面 | 修改前端源码，重新构建 | 替换 `web/ui` Bundle，或者写插件扩展 UI |

### 架构带来的生态可能性

这种架构为生态繁荣留出了巨大空间：
- 官方只负责定义接口和提供默认实现
- 社区可以开发更好的模型适配器、更智能的上下文压缩插件、更强大的记忆系统
- 企业可以开发内部专属的工具 Bundle 和安全审计插件
- 研究者可以快速替换循环逻辑，试验新的 Agent 范式
- 不同团队可以根据自己的需求组合出完全不同的 Agent 形态，却运行在同一个运行时上

官方明确表示：**主仓库里的包并不比社区的包更重要**——这不是一句客套话，而是架构本身的性质决定的：既然所有插件地位平等，官方插件没有任何特权，自然也就不存在「官方实现必须被使用」的情况。

理解了「一切皆插件」的架构，你就理解了 dsh 与其他 Agent 框架最本质的区别。下一章我们将深入这一架构中最核心的部分：Agent 循环与事件模型。

---

← [04 四种模式](04-four-modes.md) | → [06 Agent 循环与事件](06-agent-loop-events.md)
