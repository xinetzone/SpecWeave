---
id: deepseek-harness-wiki-09
title: DeepSeek Harness Wiki - 工具系统与 Capability Seam
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - tools
  - capability-seam
  - provider
  - consumer
  - service-definition
  - subagent
  - goals
category: learning
maturity: L1
---

# 09 工具系统与 Capability Seam

工具是 Agent 与外部世界交互的手和脚。DeepSeek Harness 没有把工具做成一组写死的函数集合，而是通过 **Capability Seam** 抽象将工具的「接口定义」「实现」「使用」三者彻底分离，实现了真正的「一次替换，全局生效」。这是 dsh 架构设计中最精妙的部分之一。

## Standard 模式内置工具清单

Standard 模式是日常开发使用的默认模式，提供了完整的编程 Agent 工具集。开箱即用的工具可以分为以下几类：

### 文件与代码操作

| 工具名称 | 功能说明 | 审批要求 |
|----------|----------|----------|
| `str_replace_editor` | 精确的字符串替换文件编辑，支持查看、创建、编辑文件 | 写入/修改文件需要审批 |
| `read_file` | 读取文件内容，支持按行范围读取 | 无（只读操作） |
| `search_files` | 文件名搜索，支持 glob 模式 | 无 |
| `grep_search` | 文件内容搜索，支持正则表达式 | 无 |
| `list_directory` | 列出目录内容 | 无 |

### 命令执行

| 工具名称 | 功能说明 | 审批要求 |
|----------|----------|----------|
| `bash` | 持久化 Shell 会话，执行任意命令，支持 cd、环境变量、工作目录保持 | 危险命令（rm -rf、sudo 等）需要审批 |
| `pty` | 伪终端，用于运行交互式命令（如 vim、top、ssh） | 同 bash |

### 信息检索

| 工具名称 | 功能说明 | 审批要求 |
|----------|----------|----------|
| `web_search` | 网页搜索，使用配置的搜索引擎（默认 DuckDuckGo） | 无 |
| `web_fetch` | 抓取网页内容并转换为 Markdown | 无 |
| `file_search` | 在工作区内进行语义搜索（需要嵌入模型配置） | 无 |

### Agent 核心能力

| 工具名称 | 功能说明 | 审批要求 |
|----------|----------|----------|
| `skills` | 调用技能库中的预定义技能（Skills） | 技能本身的权限决定 |
| `plan` | 创建和管理任务计划，维护步骤清单和完成状态 | 无 |
| `goals` | 目标管理，设置长短期目标，跟踪目标完成进度 | 无 |
| `spawn_subagent` | 启动子 Agent，委派子任务，子 Agent 有独立会话和工具集 | 子 Agent 创建需要确认 |
| `workflow` | 调用预定义工作流，编排多步骤任务 | 无 |

### 工具审批机制

所有可能产生副作用的工具（修改文件、执行命令、发送网络请求等）默认都会触发审批弹窗，你可以：
- 点击 **Allow once** 只允许这一次
- 点击 **Allow always for this tool** 这个工具后续不再询问
- 点击 **Deny** 拒绝执行
- 在 Settings 中配置自动审批规则（比如信任特定目录、特定命令模式）

## Capability Seam 抽象设计背景

在理解 Capability Seam 之前，先看看传统 Agent 框架在工具系统上的问题。

### 传统工具系统的痛点

大多数 Agent 框架的工具是这样实现的：

```typescript
// 传统方式：工具直接绑定具体实现
const tools = {
  bash: {
    name: 'bash',
    description: '执行 shell 命令',
    async execute(command: string) {
      // 直接调用本地 child_process
      const result = await child_process.exec(command);
      return result;
    }
  },
  readFile: {
    name: 'read_file',
    description: '读取文件',
    async execute(path: string) {
      // 直接调用本地 fs.readFile
      return fs.readFile(path, 'utf-8');
    }
  }
};
```

这种设计的问题在于：
1. **实现写死**：bash 工具只能在本地执行，要支持远程沙箱必须重写 bash 工具
2. **重复适配**：文件系统换了，不仅 readFile 要改，writeFile、editFile、listDir 都要一个个改
3. **状态不一致**：bash 的当前目录和文件操作的工作目录可能不同步
4. **无法全局切换**：想把整个 Agent 从本地迁移到沙箱里跑，需要改几十个工具的代码

### Capability Seam 的解决思路

dsh 的设计者意识到：问题不在于工具本身，而在于工具背后共享的「能力」——bash、pty、lsp 这些工具本质上都共享同一个「执行世界」；readFile、writeFile、edit 这些工具共享同一个「文件系统」。

**Capability Seam 就是把这些共享能力抽象成独立的层，工具只依赖抽象接口，不依赖具体实现。**

换一个文件系统实现，所有文件相关的工具自动使用新的文件系统；换一个执行环境，所有命令执行相关的工具自动迁移过去——不需要改任何工具代码。这就是「一次替换，全局生效」的本质。

## Service Definition / Provider / Consumer 三角色详解

每一个 Capability Seam 都由三个角色组成，三者缺一不可。理解这三个角色是理解整个 dsh 工具系统的关键。

### 角色 1：Service Definition（服务定义）

Service Definition 是能力的「接口契约」，只定义「能做什么」，不定义「怎么做」。它是纯类型定义，没有任何实现代码。

**示例：文件系统服务定义**

```typescript
// 这是 Service Definition，只定义接口
interface FileSystemService {
  // 读取文件
  readFile(path: string, options?: { encoding?: string }): Promise<Buffer | string>;
  // 写入文件
  writeFile(path: string, content: string | Buffer): Promise<void>;
  // 列出目录
  readdir(path: string): Promise<Dirent[]>;
  // 文件是否存在
  exists(path: string): Promise<boolean>;
  // stat 信息
  stat(path: string): Promise<Stats>;
  // 监听文件变化
  watch(path: string, callback: (event: string, filename: string) => void): Disposable;
}

// 服务的唯一标识符，用于依赖注入
const FileSystemService = Service.define<FileSystemService>('filesystem');
```

Service Definition 的特点：
- **稳定**：一旦发布尽量不修改，修改必须保持向后兼容
- **最小化**：只定义必要的方法，不要把实现细节暴露在接口里
- **可组合**：一个服务可以依赖其他服务（比如执行服务依赖文件服务来获取当前目录）
- **类型安全**：全链路 TypeScript 类型，编译时就能发现不兼容

dsh 内置的核心 Service Definition 包括：

| 服务 ID | 说明 |
|---------|------|
| `filesystem` | 文件系统操作 |
| `execution` | 命令执行、Shell、PTY |
| `subagent` | 子 Agent 管理 |
| `goals` | 目标管理 |
| `search` | 搜索（文件/网页） |
| `telemetry` | 遥测与日志 |
| `compaction` | 上下文压缩 |
| `memory` | 长期记忆 |
| `secrets` | 凭证管理 |

### 角色 2：Provider（服务提供者）

Provider 是 Service Definition 的**具体实现**。一个服务可以有多个 Provider，运行时选择使用哪一个。

**示例：本地文件系统 Provider**

```typescript
// 这是 Provider，实现 FileSystemService 接口
class LocalFileSystemProvider implements FileSystemService {
  async readFile(path: string, options?: { encoding?: string }) {
    return fs.promises.readFile(path, options);
  }
  async writeFile(path: string, content: string | Buffer) {
    return fs.promises.writeFile(path, content);
  }
  // ... 实现所有接口方法
}

// 注册到插件系统
ctx.services.register(FileSystemService, new LocalFileSystemProvider());
```

**示例：远程沙箱文件系统 Provider**

```typescript
// 这是另一个 Provider，同样实现 FileSystemService 接口
class RemoteSandboxFileSystemProvider implements FileSystemService {
  constructor(private sandboxClient: SandboxClient) {}

  async readFile(path: string) {
    // 通过 HTTP/gRPC 调用远程沙箱的 API
    return this.sandboxClient.readFile(path);
  }
  async writeFile(path: string, content: string | Buffer) {
    return this.sandboxClient.writeFile(path, content);
  }
  // ... 同样实现所有接口方法
}

// 可以切换到这个 Provider，不需要改任何其他代码
ctx.services.register(FileSystemService, new RemoteSandboxFileSystemProvider(client));
```

Provider 的特点：
- **可替换**：同一个服务的多个 Provider 可以互相替换
- **隔离**：Provider 之间互不影响，可以同时存在多个实例
- **可配置**：Provider 可以有自己的配置参数（比如远程沙箱的地址、认证信息）
- **生命周期**：Provider 有自己的初始化和销毁逻辑，由插件系统管理

### 角色 3：Consumer（服务消费者）

Consumer 是**使用**服务的一方，通常是工具（Tool）或者其他插件。Consumer 只依赖 Service Definition 接口，永远不依赖具体的 Provider 实现。

**示例：read_file 工具作为 Consumer**

```typescript
// 这是 Consumer，只依赖接口，不知道具体是本地还是远程
const readFileTool = Tool.define({
  name: 'read_file',
  description: '读取文件内容',
  parameters: z.object({
    path: z.string().describe('文件路径')
  }),
  async execute(ctx, { path }) {
    // 从上下文获取 FileSystemService，不关心是谁实现的
    const fs = ctx.services.get(FileSystemService);
    // 直接调用接口方法，不管后面是本地 fs 还是远程沙箱
    const content = await fs.readFile(path, { encoding: 'utf-8' });
    return content;
  }
});
```

Consumer 的特点：
- **面向接口编程**：只关心接口能做什么，不关心怎么做的
- **零修改迁移**：Provider 换了，Consumer 代码一行都不用改
- **可测试性**：测试时可以注入 Mock Provider，不需要真的读写文件或执行命令
- **组合能力**：一个 Consumer 可以使用多个服务，一个服务也可以被多个 Consumer 使用

三者关系可以用下面的表格总结：

| 角色 | 关心什么 | 变化频率 | 数量 |
|------|----------|----------|------|
| Service Definition | 能力的接口契约 | 低（稳定） | 一个服务一个 |
| Provider | 能力的具体实现 | 中（可以有多个实现） | 一个服务可以有多个 Provider |
| Consumer | 使用能力完成任务 | 高（工具很多） | 一个服务可以被很多 Consumer 使用 |

## 「一次替换，全局生效」机制与示例

三角色分离带来的最震撼的效果就是：**换一个 Provider，所有使用这个服务的 Consumer 自动全部切换到新实现，不需要改一行 Consumer 代码。**

### 示例 1：从本地环境迁移到远程沙箱

这是官方文档中给出的经典示例。

**本地环境默认配置：**
- FileSystem Provider → LocalFileSystemProvider（操作本地磁盘）
- Execution Provider → LocalExecutionProvider（本地 child_process）
- 这两个 Provider 共享同一个「本地执行世界」

**现在要把整个 Agent 放到远程沙箱里运行，只需要两步：**

1. 把 FileSystem Provider 换成 RemoteSandboxFileSystemProvider
2. 把 Execution Provider 换成 RemoteSandboxExecutionProvider（同一个沙箱实例）

**发生了什么？**
- `str_replace_editor` 工具的文件编辑操作，自动变成在远程沙箱里编辑文件
- `bash` 工具执行命令，自动变成在远程沙箱里执行
- `pty` 伪终端，自动连接到远程沙箱的 PTY
- `lsp` 语言服务器（如果启用），自动在远程沙箱里启动，访问远程文件
- 所有文件监听、目录列表、搜索操作，全部自动变成远程的
- **你不需要改任何工具代码，不需要重新配置工具，甚至不需要重启会话（如果是运行时切换）**

这就是「一次替换，全局生效」——本来要改十几个工具、几十处代码的迁移工作，现在只需要换两个 Provider。

**为什么这么神奇？**
因为所有这些工具（bash/pty/lsp/edit/read/search）都是 Consumer，它们只依赖 `filesystem` 和 `execution` 这两个 Service Definition 接口。你换了 Provider，Consumer 拿到的服务实例自动变成新的，它们调用接口方法时自然就走到新的实现上了。

而且因为文件系统和执行服务是同一个 Provider 实例提供的，它们天然共享同一个执行世界——在 bash 里 `cd` 到某个目录，下一次文件操作默认就在那个目录下，不会出现「bash 的工作目录和文件操作的工作目录不一致」的经典 bug。

### 示例 2：子 Agent Provider 切换

子 Agent 是另一个极好的例子，展示了 Seam 抽象的灵活性。

`subagent` 服务定义了一个简单的接口：

```typescript
interface SubagentService {
  spawn(task: string, options?: SubagentOptions): Promise<SubagentResult>;
}
```

就这一个方法，但你可以有完全不同的 Provider 实现：

| Provider 实现 | 行为 |
|--------------|------|
| **LocalSubagentProvider**（默认） | 在本地拉起一个新的 dsh 子 Agent 实例，独立会话，执行完返回结果 |
| **ClaudeCodeDelegationProvider** | 把任务委托给本机安装的 Claude Code 执行，用 Claude Code 跑这个任务，结果返回 |
| **CodexDelegationProvider** | 把任务委托给本机 Codex CLI 执行 |
| **RemoteWorkerProvider** | 把任务发送到远程 Worker 集群执行，适合并行跑多个子任务 |
| **MockTestingProvider** | 测试用，不真的执行，返回预设结果 |

**切换效果：**
你在插件中把 `subagent` 服务的 Provider 从默认的 LocalSubagentProvider 换成 ClaudeCodeDelegationProvider，然后——
- 模型调用 `spawn_subagent` 工具时，不会再拉起新的 dsh 实例了
- 自动变成启动 Claude Code，把任务传给它，等它执行完拿回结果
- `spawn_subagent` 工具的参数格式没变，模型不需要知道背后实现变了
- Trajectory 里仍然会记录子 Agent 的执行过程，只是执行引擎从 dsh 变成了 Claude Code
- 所有上层逻辑（计划、并行、错误处理）都不需要修改

**这就是 Seam 的力量：你可以在运行时改变 Agent 的整个行为模式，而模型和上层工具完全感知不到变化。**

## ctx.goals 与 subagent seam 扩展点

在核心 Seam 之外，dsh 还预留了两个面向高级场景的扩展点，它们本身也是 Seam 设计的。

### ctx.goals：目标管理扩展点

`ctx.goals` 是目标管理服务的入口，负责维护 Agent 的长短期目标、跟踪进度、调整优先级。

**默认实现提供的能力：**
- 创建短期目标（当前会话内要完成的）
- 创建长期目标（跨会话持续跟踪的）
- 标记目标完成/失败/阻塞
- 目标分解：把大目标拆成小目标
- 进度汇报：在每一步自动回顾目标完成情况
- 自动提醒：如果偏离目标太远会发出提醒

**扩展方式：**
你可以通过替换 Goals Provider 实现：
- **持久化目标**：把目标存到数据库或文件，重启后继续跟踪
- **团队目标**：多 Agent 共享目标池，协作完成
- **OKR 集成**：同步到公司 OKR 系统，Agent 任务对齐业务目标
- **人类审批工作流**：目标变更需要人类确认
- **目标优先级自动调整**：根据截止时间、依赖关系自动重排优先级

**模型如何使用：**
模型通过 `goals` 工具与目标系统交互——它可以查询当前目标、添加新目标、更新进度。因为这是标准工具，不管你换成什么 Provider，模型使用方式都不变。

### subagent seam：多 Agent 扩展点

`subagent` 服务我们在上一节已经提到，它是多 Agent 架构的核心扩展点。默认实现只是简单拉起本地子 Agent，但通过自定义 Provider 你可以实现几乎任何多 Agent 拓扑：

**场景 1：多模型路由**
```
子任务分析 → 判断需要什么模型
  ├─ 简单代码任务 → 派给 v4-flash（快、省钱）
  ├─ 复杂推理任务 → 派给 v4-pro（质量高）
  └─ 视觉相关任务 → 派给 GPT-4o（视觉好）
```

**场景 2：Agent 团队**
```
主控 Agent（规划）
  ├─ 研究员 Agent（负责搜索、收集信息）
  ├─ 程序员 Agent（负责写代码）
  ├─ 测试员 Agent（负责写测试、运行测试）
  └─ 审查员 Agent（负责审查代码质量）
```
每个角色可以是不同模型，甚至是不同产品（研究员用 Claude、程序员用 DeepSeek）。

**场景 3：弹性分布式执行**
```
本地 dsh
  └─ 把任务派到 Kubernetes 集群
      ├─ Pod 1: 跑代码搜索子任务
      ├─ Pod 2: 跑测试子任务
      └─ Pod 3: 跑文档生成子任务
  ← 所有结果汇总返回
```

**场景 4：A/B 测试**
同一个任务同时派给两个不同模型跑，对比结果选更好的那个，或者人工审核。

所有这些场景都不需要修改 dsh 核心代码，只需要写一个 Subagent Provider 插件即可。

### 扩展点设计原则

dsh 的扩展点设计遵循几个原则：
1. **接口最小化**：接口方法尽量少，方便第三方实现
2. **默认实现可用**：即使你不扩展，默认实现也能工作得很好
3. **可选实现**：新 Provider 不需要实现所有功能，可以只实现自己需要的（抛出 not supported 即可）
4. **组合而非继承**：新 Provider 可以包装旧 Provider，增加功能而不是完全替换（装饰器模式）
5. **模型透明**：Provider 切换对模型透明，模型不需要知道背后是什么

理解了 Capability Seam，你就理解了 dsh 「一切皆插件」架构的核心精髓。下一章我们将正式进入插件开发，教你如何写第一个自己的 dsh 插件。

---

← [08 模型配置](08-model-configuration.md) | → [10 插件开发入门](10-plugin-development.md)
