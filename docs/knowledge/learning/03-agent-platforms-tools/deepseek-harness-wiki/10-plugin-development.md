---
id: deepseek-harness-wiki-10
title: DeepSeek Harness Wiki - 插件开发入门
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
  - external/libs/cordis/packages/core/src/context.ts
  - external/libs/cordis/packages/core/src/service.ts
  - external/libs/cordis/packages/core/src/fiber.ts
  - external/libs/cordis/packages/core/src/events.ts
  - external/libs/cordis/packages/core/src/registry.ts
date: 2026-08-17
tags:
  - deepseek
  - agent
  - harness
  - plugin
  - cordis
  - development
  - events
  - reversible-effects
  - creator-mode
  - community
category: learning
maturity: L1
---

# 10 插件开发入门

DeepSeek Harness 的核心设计哲学是「一切皆插件」——从模型适配器、工具注册表，到 Agent 循环本身，没有任何特权内核代码，所有能力都通过插件提供。写插件是扩展 dsh 能力的唯一方式，也是最自然的方式。本章带你入门 dsh 插件开发。

## 插件开发前提：理解 Cordis 概念

dsh 的插件系统底层由 **Cordis** 元框架驱动。写 dsh 插件不需要你深入理解 Cordis 的所有实现细节，但几个核心概念必须先搞清楚。

### Cordis 是什么

Cordis 是一套为「时空可组合性」设计的插件元框架，来自论文《A Programming Paradigm for Spatiotemporal Composability》。你不需要读那篇论文，只需要理解 Cordis 对插件的三个核心承诺：

1. **共享上下文（Context）**：所有插件都挂载到同一个上下文对象上，通过上下文互相通信、注册服务、监听事件
2. **可逆效应（Reversible Effects）**：插件注册的一切（服务、事件监听器、命令）在插件卸载时会自动撤销，不会留下垃圾
3. **配置叠加（Configuration Patching）**：插件树通过层层叠加补丁构建，每一层都可以覆盖或扩展上一层的配置

对于插件开发者来说，最直观的感受是：**你只需要在启动时注册你想做的事情，框架会在卸载时帮你清理干净——前提是你正确使用 `ctx.effect()` 或返回 disposer。**

### 开发环境准备

开发 dsh 插件需要：

| 工具 | 版本要求 |
|------|----------|
| Node.js | ^22.19 \|\| >=24 |
| pnpm | 推荐最新版（dsh 本身用 pnpm） |
| TypeScript | 5.0+（推荐，有完整类型定义） |
| 代码编辑器 | VS Code（有官方类型提示） |

**从源码运行 dsh 方便调试：**

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

这样你可以在源码中打断点调试自己的插件。

## 插件三种形态

Cordis 支持三种等价的插件形态，本质上都是向 Context 注册服务、事件监听和可逆效应，你可以根据场景选择最合适的写法：

### 形态 1：函数形态（最常用）

最简洁直接的写法，适合大多数简单插件：

```typescript
import { Context } from '@deepseek-ai/dsh';

interface MyPluginConfig {
  greeting?: string;
}

// 函数本身就是插件入口
export default function myPlugin(ctx: Context, config: MyPluginConfig) {
  ctx.logger.info(config.greeting ?? 'Hello from my plugin!');
  
  // 在这里注册服务、监听事件、添加工具...
  ctx.tools.register(/* ... */);
}

// 声明依赖（可选）：本插件需要 ctx.tools 和 ctx.llm 就绪后才能启动
myPlugin.inject = ['tools', 'llm'];
```

### 形态 2：Service 子类形态（适合有状态服务）

继承 `Service` 基类，适合封装有内部状态、需要生命周期管理的复杂服务：

```typescript
import { Context, Service } from '@deepseek-ai/dsh';

declare module '@deepseek-ai/dsh' {
  interface Context {
    myService: MyService;
  }
}

class MyService extends Service {
  // 静态属性声明依赖
  static inject = ['database', 'logger'];
  
  // 声明本服务提供的名称（对应 ctx.myService）
  static provide = 'myService';

  constructor(ctx: Context) {
    super(ctx, 'myService');
    // 构造函数中依赖已就绪，可以安全使用
    this.ctx.logger.info('MyService initialized');
  }

  // 服务方法
  doSomething() {
    // ...
  }

  // 可选：启动逻辑（构造后调用）
  [Symbol.for('cordis.init')]() {
    // 服务启动时执行
  }
}

export default MyService;
```

Service 子类的生命周期完全由 Cordis 管理：依赖就绪后自动实例化，插件卸载时自动清理注册的效应。

### 形态 3：普通对象形态（最灵活）

带 `apply` 方法的普通对象，适合需要额外元数据或需要组合多个逻辑的场景：

```typescript
import { Context, Plugin } from '@deepseek-ai/dsh';

const myPlugin: Plugin = {
  name: 'my-plugin',
  inject: ['tools', 'llm'],
  
  apply(ctx: Context, config: MyPluginConfig) {
    // 和函数形态完全一样的逻辑
    ctx.tools.register(/* ... */);
    
    // 可选：返回 disposer 处理自定义资源清理
    return () => {
      ctx.logger.info('my-plugin unloaded');
    };
  }
};

export default myPlugin;
```

> **三种形态本质等价**：Cordis 内部会统一处理——函数直接作为 apply 调用，Service 子类通过 `new` 实例化，对象形态调用其 `apply` 方法。你可以根据团队习惯和插件复杂度自由选择。

### 依赖注入（inject）的作用

不管哪种形态，`inject` 依赖数组都能让你**不需要手动编排插件启动顺序**：Cordis 会自动按依赖拓扑排序加载，保证你的插件启动时，声明的依赖一定已经就绪。

```typescript
// 声明依赖：本插件需要 ctx.tools 和 ctx.llm 就绪后才能启动
export default function myPlugin(ctx: Context, config: MyPluginConfig) {
  // ✅ 到这里时，ctx.tools 和 ctx.llm 一定可用
  // 不需要写 if (!ctx.tools) { wait... } 这种防御代码
  ctx.tools.register(/* ... */);
  ctx.llm.chat(/* ... */);
}
myPlugin.inject = ['tools', 'llm'];
```

依赖注入的好处：
- 自动拓扑排序，无需关心插件加载顺序
- 依赖未就绪时自动等待，不会出现竞态条件
- 依赖重载时自动重启本插件（配合 HMR）
- 类型系统可以基于 inject 推导 ctx 上可用的服务

### Fiber 生命周期

每个插件加载时都会创建一个 **Fiber**（纤程）来管理其生命周期，Cordis 的 epoch 机制驱动状态自动切换：

| 状态 | 说明 |
|------|------|
| **PENDING** | 初始状态，等待依赖就绪 |
| **LOADING** | 插件正在加载，执行插件入口函数 |
| **ACTIVE** | 插件正常运行，服务可用，效应已注册 |
| **FAILED** | 插件加载失败（配置错误或异常） |
| **UNLOADING** | 插件正在卸载，执行所有 disposer |
| **DISPOSED** | 插件已完全卸载，资源已清理 |

你通常不需要手动操作这些状态——Cordis 会根据依赖变化、配置更新、卸载请求自动切换状态。

## 插件基本结构

一个最简化的 dsh 插件就是一个 TypeScript 文件，导出上述三种形态之一。

### Hello World 插件

创建文件 `my-first-plugin.ts`：

```typescript
// 函数形态的 Hello World 插件
export default function myFirstPlugin(ctx) {
  console.log('Hello from my first plugin!');

  // 在这里注册服务、监听事件、添加工具...
}

myFirstPlugin.inject = []; // 无依赖，立即启动
```

就这么简单。插件加载时，函数会被调用，传入上下文对象 `ctx`，所有操作都通过 `ctx` 进行。

### 插件能做什么

在插件函数中，你可以做任何你想做的事情，包括但不限于：

| 能力 | API |
|------|-----|
| 注册自定义工具 | `ctx.tools.register(tool)` |
| 实现新的 Service Provider | `ctx.services.register(ServiceDef, provider)` |
| 监听事件 | `ctx.on('event-name', handler)` / `ctx.waterfall('waterfall-event', handler)` |
| 拦截和修改消息 | `ctx.waterfall('agent/pre-step', handler)` |
| 添加 Slash 命令 | `ctx.commands.register(command)` |
| 添加 UI 面板 | `ctx.ui.registerPanel(panel)` |
| 注册新的 Skill | `ctx.skills.register(skill)` |
| 访问其他服务 | `ctx.services.get(ServiceDef)` |
| 读写配置 | `ctx.config.get/set(path, value)` |

## 注册到插件树方法

写好插件后，需要让 dsh 加载它。有几种方式可以把插件挂载到插件树上。

### 方式 1：命令行临时加载（开发调试用）

使用 `--plugin` 参数临时加载插件，适合快速调试：

```bash
pnpm dsh web --plugin ./my-first-plugin.ts
```

插件会被即时编译加载，不需要重启整个构建流程。修改插件代码后需要重启命令，但不需要重新 build dsh 源码。

### 方式 2：用户目录全局插件（个人使用）

把插件放到 `~/.dsh/plugins/` 目录下，dsh 启动时会自动加载该目录下的所有插件：

```
~/.dsh/
  plugins/
    my-first-plugin.js   # 或者编译后的 .js，或者 .ts（需要支持）
    my-other-plugin/
      index.js
      package.json
```

这种方式安装的插件对你所有项目生效，不需要每次命令行加参数。

### 方式 3：项目级插件（随项目走）

在项目根目录创建 `.dsh/plugins/` 目录，放在这里的插件只对当前项目生效：

```
your-project/
  .dsh/
    plugins/
      project-specific-plugin.ts
  src/
  package.json
```

这适合团队共享——把 `.dsh/plugins/` 提交到项目仓库，团队成员拉取代码后自动使用同一套插件。

### 方式 4：通过 cordis.patch.yml 挂载（正式配置）

最灵活的方式是在 `~/.dsh/cordis.patch.yml` 中配置插件，可以控制加载顺序、启用条件、传入配置：

```yaml
# 在插件树中插入我们的插件
- id: my-first-plugin
  after: core/agent-loop  # 在 core/agent-loop 之后加载（有 inject 就不需要手动指定）
  plugin:
    path: ./plugins/my-first-plugin.ts
    config:
      greeting: '你好世界'
      enableFeatureX: true
```

插件中可以通过 `ctx.config` 获取传入的配置：

```typescript
export default function myPlugin(ctx) {
  const greeting = ctx.config.get('greeting') ?? 'Hello';
  console.log(greeting);
}
```

## 事件系统详解

事件是插件扩展 dsh 行为最常用的方式。Cordis 提供了五种核心事件分发模式（源码 `events.ts` 中 `DispatchMode` 类型定义），每种适用于不同场景。

### 五种事件分发模式

| 模式 | 特点 | 同步/异步 | 返回值 | 短路条件 | 典型使用场景 |
|------|------|----------|--------|---------|-------------|
| **`emit`** | 纯通知，按顺序触发所有监听器，不等待，不阻塞 | 同步 | `void` | 无（全部执行） | 日志、指标收集、UI更新通知、纯观察型事件 |
| **`bail`** | 按顺序调用监听器，第一个返回非 `null`/`undefined` 的结果获胜 | 同步 | 获胜监听器的返回值 | 返回非 null/undefined | 同步注册表查找、内部 listener 拦截、第一个匹配处理器获胜 |
| **`parallel`** | 并行执行所有异步监听器，等待全部完成 | 异步 | `Promise<void>` | 无（全部执行） | 多个独立的遥测上报、并行后处理、批量扇出通知 |
| **`serial`** | 按顺序 await 监听器，第一个返回非 `null`/`undefined` 的结果获胜 | 异步 | `Promise<any>` | await 后返回非 null/undefined | Agent turn-stopping 投票、异步串行校验器链、顺序查找异步处理器 |
| **`waterfall`** | 环绕中间件链式处理，必须调用 `next()` 才能继续下游，可以修改参数甚至中断流程 | 取决于监听器 | 最后一个 `next()` 的返回值 | 不调用 `next()` 即短路 | 权限检查、请求改写、结果转换、参数校验、中间件管道模式（如 `agent/pre-step`、`tools/execute`） |

> `bail` 和 `serial` 是同一逻辑的同步/异步版本；dsh 内部注册监听器时使用 `ctx.on()` → 内部通过 `bail('internal/listener', ...)` 实现拦截机制。

### 事件监听正确示例

#### 1. `emit` 事件：纯观察，不需要响应

```typescript
// 纯观察用 emit：监听会话事件做日志记录
ctx.on('session/event', (event) => {
  console.log('会话事件:', event.type, event.timestamp);
  // 没有 next，也不需要返回值，做记录即可
  // 不会阻塞主流程
});
```

适用场景：日志记录、指标收集、UI 状态同步、审计日志。

#### 2. `waterfall` 事件：拦截、修改、短路流程

```typescript
// waterfall 事件必须调用 next()，否则会中断流程
ctx.on('agent/pre-step', async (session, next) => {
  // 可以修改 session 上下文——比如注入自定义系统指令
  session.context.push({ 
    role: 'system', 
    content: '记住：所有代码必须通过我司的 lint 规则。' 
  });
  
  // ✅ 必须调用 next() 继续流程！
  // 如果不调用 next()，本次 step 会被拒绝/中断
  await next();
});
```

你也可以在 `next()` 前后做环绕处理：

```typescript
ctx.on('llm/request', async (request, next) => {
  const start = Date.now();
  // 调用 next() 前：修改请求
  request.model = 'deepseek-chat';
  
  // 执行后续处理链
  const response = await next();
  
  // 调用 next() 后：修改响应或做后处理
  ctx.metrics.timing('llm.latency', Date.now() - start);
  response.metadata = { ...response.metadata, processedBy: 'my-plugin' };
  
  return response; // 必须返回（可能被修改过的）响应
});
```

适用场景：权限检查、请求改写、结果转换、参数校验、中间件环绕逻辑。

#### 3. `serial` 事件：按顺序投票/检查，短路返回

```typescript
// serial 事件没有 next()，按顺序执行直到有人返回真值
// 例子：agent/turn-stopping - 投票决定是否停止当前 turn
ctx.on('agent/turn-stopping', async (session) => {
  // 返回 true/false 表示「应该停止/应该继续」
  // 第一个返回 true 的监听器会终止循环
  if (session.hasPendingToolCalls) {
    return false; // 还有工具调用没完成，继续
  }
  if (session.turnCount > 10) {
    return true; // 超过 10 轮，强制停止
  }
  // 返回 undefined/false/null 表示「我不决定，继续问下一个」
});
```

适用场景：多插件投票决定是否终止、串行校验器链（第一个失败就返回错误）、按优先级查找处理器。

#### 4. `parallel` 事件：独立任务并行执行

```typescript
// parallel 事件：多个独立的观察者并行执行，等待全部完成
ctx.on('session/complete', async (session) => {
  // 这些上报任务互不依赖，可以并行做
  // Promise.all 会等它们全部完成
  await Promise.all([
    ctx.telemetry.reportUsage(session),
    ctx.audit.logSession(session),
    ctx.notifications.sendCompletionEmail(session.user),
  ]);
});
```

适用场景：多个独立遥测上报、并行后处理任务、批量通知不互相依赖的观察者。

### 事件监听示例：监听 agent/pre-step 修改提示词

我们来写一个实际的例子：在每一步模型请求前，自动在系统提示词里注入当前 git 分支信息。

```typescript
import { Context } from '@deepseek-ai/dsh';
import { execSync } from 'child_process';

function gitBranchPlugin(ctx: Context) {
  // 监听 agent/pre-step 瀑布事件
  ctx.on('agent/pre-step', async (step, next) => {
    try {
      // 获取当前 git 分支名
      const branch = execSync('git rev-parse --abbrev-ref HEAD', {
        encoding: 'utf-8',
        cwd: ctx.workspace.path
      }).trim();

      // 获取最近 5 条 commit 信息
      const recentCommits = execSync('git log --oneline -5', {
        encoding: 'utf-8',
        cwd: ctx.workspace.path
      }).trim();

      // 在系统提示词末尾追加信息
      step.messages.push({
        role: 'system',
        content: [
          '当前 Git 上下文：',
          `当前分支：${branch}`,
          '最近 5 条提交：',
          recentCommits
        ].join('\n')
      });

      ctx.logger.info(`注入了 git 分支信息：${branch}`);
    } catch (e) {
      // 如果不在 git 仓库中，忽略错误
      ctx.logger.debug('不是 git 仓库，跳过 git 信息注入');
    }

    // ✅ 必须调用 next() 继续流程！不调用就会中断这一步
    await next();
  });
}

gitBranchPlugin.inject = ['workspace', 'logger'];
export default gitBranchPlugin;
```

### 关键点说明

1. **瀑布事件必须调用 `next()`**：如果你忘了调用 `next()`，整个 Agent 循环会卡在这里——不会发请求，不会有任何报错，就像卡住了一样。这是新手最常犯的错误。
2. **修改 step 对象**：`step` 是 mutable 的，你可以直接修改它的 `messages`、`tools`、`model` 等字段，后续流程会使用修改后的值。
3. **错误处理**：插件代码要自己处理异常，抛出未捕获的异常会中断整个会话。
4. **使用 ctx.logger**：不要直接 `console.log`，用 `ctx.logger` 打日志，日志会自动进入会话事件流，在 Trajectory 里可以看到。
5. **事件监听自动绑定到 Fiber**：`ctx.on()` 返回的 disposer 会自动注册到当前 Fiber，插件卸载时自动移除监听器——你不需要手动 `ctx.off()`！

### 这个插件的效果

加载这个插件后，每一次模型请求前，系统提示词里都会自动带上当前分支和最近提交，模型可以根据这些信息回答问题，比如你问「我最近在做什么」，它能通过最近 commit 知道。而且——

- 你不需要修改任何核心代码
- 不需要告诉模型「先看一下 git 状态」，它自动就知道
- 不需要的时候禁用插件即可，没有侵入性
- 所有注入的内容都会记录在会话日志里，Trajectory 能看到

## 自定义工具插件示例概念说明

添加自定义工具是插件最常见的用途之一。我们来做一个概念性示例：添加一个查询当前天气的工具。

### 工具定义结构

dsh 工具使用 Zod 定义参数 schema，自动生成 JSON Schema 给模型：

```typescript
import { Context, Tool } from '@deepseek-ai/dsh';
import { z } from 'zod';

// 定义工具
const weatherTool = Tool.define({
  // 工具名称，模型用这个名字调用
  name: 'get_weather',
  // 工具描述，模型靠这个知道什么时候用这个工具（非常重要！）
  description: '查询指定城市的当前天气。当用户问天气相关问题时使用这个工具。',
  // 参数定义，用 Zod
  parameters: z.object({
    city: z.string().describe('要查询天气的城市名称，比如"北京"、"上海"'),
    units: z.enum(['celsius', 'fahrenheit'])
      .optional()
      .default('celsius')
      .describe('温度单位，默认摄氏度')
  }),
  // 工具执行函数
  async execute(ctx, { city, units }) {
    // 这里调用真实的天气 API
    // 示例中我们返回模拟数据
    ctx.logger.info(`查询天气：${city}`);

    return {
      city,
      temperature: units === 'celsius' ? 25 : 77,
      condition: '晴',
      humidity: '45%',
      wind: '东北风 3 级',
      units
    };
  }
});

function weatherPlugin(ctx: Context) {
  // 注册工具——ctx.effect 或直接注册都会自动管理生命周期
  ctx.tools.register(weatherTool);
  ctx.logger.info('天气工具已注册');
}

weatherPlugin.inject = ['tools', 'logger'];
export default weatherPlugin;
```

### 关键点说明

1. **描述非常非常重要**：模型是靠 `description` 来判断什么时候该用这个工具的。描述写得不好，模型要么该用的时候不用，要么不该用的时候乱用。
2. **参数 describe 也很重要**：每个参数的描述会告诉模型这个参数是干嘛的、该填什么格式。
3. **返回值自动序列化**：你返回 JavaScript 对象，框架会自动转成模型能理解的格式。
4. **可以访问 ctx**：在 execute 里可以访问上下文，调用其他工具、查日志、读配置等。
5. **工具自动出现在 Trajectory**：工具调用和结果会自动记录在会话日志，不需要你做任何事。

加载这个插件后，模型就能回答「北京今天天气怎么样」这类问题了，和内置工具没有任何区别。

## 可逆效应实现要点

Cordis 最强大的特性之一是**可逆效应**——插件卸载时，你注册的所有东西都会自动撤销。但你需要理解它是怎么工作的，才能写出符合预期的插件。

### 什么是可逆效应

当你在插件中调用 `ctx.tools.register()`、`ctx.on()`、`ctx.services.register()` 这些 API 时，它们内部都会通过 `ctx.effect()` 注册 disposer，插件卸载时这些注册会自动撤销：

- 注册的工具会从工具列表移除
- 事件监听器会被移除
- 注册的服务会被注销
- 添加的命令会被移除
- UI 面板会被隐藏

```typescript
export default function myPlugin(ctx) {
  // 注册一个工具，返回 disposable（也自动绑定到当前 Fiber）
  const disposable = ctx.tools.register(myTool);

  // 如果你想提前注销，可以手动调用 .dispose()
  // disposable(); // 注意：disposer 是函数，不是 .dispose() 方法

  // 但大多数情况下你不需要管，插件卸载时自动 dispose
}
```

### `ctx.effect()`：手动管理可逆效应

如果你创建了框架管理之外的资源（比如启动了服务器、打开数据库连接、设置了原生定时器），需要用 `ctx.effect()` 来确保它们被正确清理。

`ctx.effect()` 支持四种 disposer 返回形式：

#### 形式 1：返回清理函数（最常见）

```typescript
ctx.effect(() => {
  // === 注册阶段 ===
  const listener = (e) => console.log('收到事件:', e.type);
  ctx.on('some-custom-event', listener);
  const timer = setInterval(() => doHeartbeat(), 60000);
  const server = http.createServer(/* ... */).listen(9999);
  
  // === 返回清理函数：卸载时调用 ===
  return () => {
    server.close();
    clearInterval(timer);
    // ctx.on() 本身已经返回 disposer，但如果在一个 effect 中
    // 做多个注册，用统一的清理函数更清晰
    ctx.off('some-custom-event', listener);
  };
}, 'my-custom-resources'); // 第二个参数是 label，方便调试
```

> 提示：`ctx.on()` 本身会返回一个 disposer 函数，并且自动注册到当前 Fiber。只有当你有**多个自定义资源**需要一起清理时，才需要手动包一层 `ctx.effect()`。

#### 形式 2：返回 Generator（分段清理）

```typescript
ctx.effect(function* () {
  // yield 之前是注册
  const timer = setInterval(() => console.log('tick'), 1000);
  yield; // <-- 这里分隔注册和清理
  
  // yield 之后是清理——卸载时执行
  clearInterval(timer);
  console.log('timer cleared');
});
```

Generator 形式适合需要「先拿句柄，再注册清理」的场景，代码结构更清晰。

#### 形式 3：返回 Promise（异步初始化）

```typescript
ctx.effect(async () => {
  // 异步初始化：比如连接数据库
  const db = await connectToDatabase(ctx.config.get('dbUrl'));
  ctx.database = db;
  
  // 返回异步清理函数
  return async () => {
    await db.close();
  };
});
```

#### 形式 4：返回 AsyncGenerator（异步分段）

```typescript
ctx.effect(async function* () {
  const ws = new WebSocket(ctx.config.get('wsUrl'));
  await new Promise(resolve => ws.on('open', resolve));
  ws.on('message', handleMessage);
  
  yield; // 等待卸载信号
  
  ws.close();
  await new Promise(resolve => ws.on('close', resolve));
});
```

### 可逆效应的重要性——最常见的坑

⚠️ **忘记返回 disposer 是插件开发最常见的 bug！**

后果包括：
- **内存泄漏**：插件卸载后闭包和引用还在，GC 无法回收
- **重复注册**：热重载后旧的监听器还在，事件被处理 N 次
- **卸载后残留**：定时器还在跑、服务器端口还被占用、连接还没关
- **幽灵行为**：插件禁用了但日志还在打、UI 还在更新

Creator/Cordis 模式的**热重载（HMR）完全依赖正确的 disposer 实现**——每次热重载都会先卸载旧 Fiber（执行所有 disposer），再加载新 Fiber。如果 disposer 不对，改一次代码就多一份残留，很快你就会看到各种诡异的重复行为。

写插件时要记住一个原则：**凡是在 effect/插件入口中打开/创建/启动的东西，都要确保在 disposer 中能正确关闭/销毁/停止。**

### 老 API 兼容：onDeactivate

在一些旧代码中你可能看到 `ctx.onDeactivate()`，它的功能和在 effect 中返回清理函数等价：

```typescript
// 旧写法（仍然支持）
const server = http.createServer(/* ... */).listen(9999);
ctx.onDeactivate(() => server.close());

// 等价的新写法（推荐）
ctx.effect(() => {
  const server = http.createServer(/* ... */).listen(9999);
  return () => server.close();
});
```

推荐使用 `ctx.effect()`，因为它支持 Promise/Generator 等更丰富的形式，并且有 label 和 effect 层级结构方便调试。

## Creator 模式运行时试验

dsh 的 **Creator 模式** 是专门为插件开发者设计的运行模式，支持运行时自省、在内存中试验插件，是开发插件的最佳伴侣。

### 启动 Creator 模式

```bash
pnpm dsh web --profile creator
```

或者在 Web UI 左下角模式切换中选 **Creator**。

### Creator 模式提供的能力

| 功能 | 说明 |
|------|------|
| **插件树查看器** | 可视化查看当前加载的所有插件、它们的依赖关系、注册的服务和工具，以及每个 Fiber 的状态（PENDING/LOADING/ACTIVE/FAILED） |
| **Effect 检查器** | 查看每个 Fiber 注册的所有 effect 和 disposer，可视化 effect 层级，方便找内存泄漏 |
| **运行时插件加载** | 在 UI 中直接粘贴代码或指定路径，即时加载插件，不需要重启 |
| **Cordis REPL** | 内置 REPL，可以直接操作 ctx 对象，调用 API 看效果 |
| **事件监控** | 实时查看所有事件流，看事件触发顺序、payload 内容、是哪种分发模式 |
| **服务检查器** | 查看已注册的服务、它们的 Provider、调用方法测试 |
| **配置编辑器** | 可视化编辑 cordis 补丁，实时看到配置变化对插件树的影响 |
| **Preset 导出** | 试验满意后可以导出为 profile 或 bundle 保存下来 |

### 典型开发流程用 Creator 模式

1. 启动 Creator 模式
2. 在代码编辑器里写插件，保存文件
3. 在 Creator UI 中点击「Reload plugin」热重载插件
4. 打开事件监控，发一条消息触发插件逻辑
5. 观察事件流、effect 列表和日志，看是否符合预期
6. 如果有问题，改代码，热重载，再试——整个循环不需要刷新页面或重启服务
7. 调试满意后，把插件放到正式插件目录

Creator 模式让插件开发的反馈循环从「改代码→重启→测试」变成「改代码→热重载→测试」，速度快了一个数量级。热重载时如果看到重复日志或行为异常，第一时间检查是不是忘记写 disposer 了。

## 社区插件生态

DeepSeek Harness 开源后，社区插件生态爆发式增长——发布当天就有 **300+** 社区插件涌现，这在开源工具历史上是相当罕见的。

### 社区插件分类

发布当天涌现的插件覆盖了非常广泛的场景，其中比较有趣的几类：

| 类别 | 代表插件 | 说明 |
|------|----------|------|
| **UI 皮肤/美化** | XP 皮肤、深色主题、赛博朋克主题、Terminal 复古主题 | 给 Web UI 换皮，很多人第一时间写了皮肤插件 |
| **表情包/趣味** | dsh-meme、emoji-reactor、egg-pet | 给 Agent 加表情包回复、桌面宠物蛋、趣味交互 |
| **绘图集成** | DSH-OpenPencil、dsh-midjourney、stable-diffusion | 集成 AI 绘图能力，Agent 可以画图 |
| **记忆增强** | dsh-longterm-memory、mem0-provider、graph-memory | 各种长期记忆实现，弥补官方基础实现的不足 |
| **压缩优化** | adaptive-compaction、small-model-compressor | 更智能的上下文压缩策略 |
| **工具集成** | dsh-github、slack-integration、jira-connector | 接入各种第三方服务 API |
| **模型 Provider** | ollama-provider、llama.cpp-provider、vllm-provider | 各种本地模型和自托管模型接入 |
| **工作流** | dsh-git-workflow、code-review-bot、test-writer | 面向特定场景的工作流自动化 |
| **调试增强** | better-trajectory、timeline-view、cost-tracker | 增强可观测性，成本统计 |

> **趣闻**：开源后第一个破 1k star 的第三方插件居然是「Windows XP Bliss 皮肤插件」，把整个 UI 换成 Windows XP 经典 Bliss 壁纸和 Luna 主题，引起了一波「文艺复兴」热潮。这也从侧面说明 dsh 的 UI 扩展能力确实强。

### dsh-plugin 标签与发现

官方推荐所有社区插件在 GitHub 仓库打上 `dsh-plugin` 标签，方便检索：

```
https://github.com/topics/dsh-plugin
```

你可以在 GitHub Topics 上浏览所有社区插件，官方也会定期整理优质插件列表放到官网。

安装第三方插件通常只需要：

```bash
cd ~/.dsh/plugins
git clone https://github.com/作者名/插件名.git
cd 插件名
pnpm install
pnpm run build
```

然后重启 dsh 即可。

## 官方 PR 政策：暂不接受外部 PR，鼓励独立插件开发

关于贡献代码，官方的态度非常明确，也非常有意思。

### 官方 PR 政策

在 README 和 Issue 模板中，官方明确说明：

> **当前阶段，主仓库暂不接受外部 Pull Request。**

这不是因为官方封闭，而是出于架构设计的考量：

1. **核心还在快速迭代**：v0.1 是开发者预览版，核心插件和接口都会快速演化，这时候合并外部 PR 会拖慢迭代速度
2. **没有「官方特权」**：官方反复强调「主仓库里的包并不比社区包更重要」——核心插件和你写的第三方插件在插件树上是完全平等的，没有特权
3. **生态分散化更健康**：官方不希望所有好功能都被「收编」进主仓库，而是希望形成一个分散的、多样化的插件生态，就像 VS Code 那样
4. **避免维护瓶颈**：如果所有功能都进主仓库，官方团队会成为维护瓶颈，反而限制生态发展

### 对开发者意味着什么

- 你有一个好想法？直接写插件发布，不需要等官方合并
- 你觉得官方某个工具做得不好？自己写一个更好的版本替换掉（通过 Capability Seam），完全不用改官方代码
- 你写的插件和官方插件有冲突？用户可以选择用哪个，或者通过 profile 配置切换
- 你不需要签 CLA，不需要遵守官方的代码风格（当然还是推荐写得好一点），完全自由

### 官方对社区的支持

虽然不合并 PR，但官方对社区插件提供支持：
- 保持核心接口稳定，尽量不做破坏性变更（即使做也会有详细迁移指南）
- 在官方文档中列出优质社区插件
- 帮助宣传优质插件
- 在核心接口设计上会听取社区反馈
- 回答 Discussions 中的插件开发问题

### 这一政策的启示

dsh 选择了一条和很多开源项目相反的路：不是「我做核心，大家帮我补功能」，而是「我搭好地基，大家在上面盖自己的房子，我不抢你们的功劳」。

这种设计从第一天就鼓励生态独立发展，而不是培养「等官方实现」的心态。开源当天就有 300+ 插件出现，和这种开放的生态政策是分不开的——开发者知道自己写的插件不会被官方「抄」进核心然后把第三方插件废掉，所以有动力投入。

理解了插件开发基础，你就可以开始扩展 dsh 的能力了。下一章我们将介绍 dsh 如何与 Claude Code、Codex、MCP 等现有生态互操作，让你过去的投资不会浪费。

---

← [09 工具系统](09-tools-capability-seam.md) | → [11 生态互操作](11-ecosystem-interop.md)
