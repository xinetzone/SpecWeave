---
id: deepseek-harness-wiki-12
title: DeepSeek Harness Wiki - 无头模式与 SDK 使用
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/03-deepseek-official.md
  - .temp/deepseek-harness-sources/04-deepseek-official-www.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - headless
  - sdk
  - python
  - json-rpc
  - acp
  - automation
category: learning
maturity: L1
---

# 12 无头模式与 SDK 使用

前 11 章我们主要介绍了 dsh 的 Web UI 交互模式——打开浏览器、选择工作区、配置模型、在输入框里发任务。但很多场景下你不需要 UI：你可能想在 CI/CD 流水线里跑自动化任务，或者想把 dsh 嵌入到你自己的应用、IDE 插件、内部平台里。这时候就需要用到 dsh 的无头（Headless）模式和各种 SDK。

dsh 的设计从一开始就考虑了嵌入场景——无头模式不是事后加上的补丁，而是一等公民。事实上，Web UI 本身就是建立在无头运行时之上的一个前端壳。

## Headless 模式：一次性执行，无 UI 自动化

Headless（无头）模式是 dsh 最简单的非交互式运行方式：你在命令行里传入任务描述，dsh 启动后一次性执行任务，把结果打印到 stdout，然后直接退出，不启动 Web 服务器，不打开浏览器。

### Headless 模式适用场景

什么时候应该用 Headless 模式而不是 Web UI？几个典型场景：

1. **自动化脚本与 CI/CD**：
   - 在 GitHub Actions/GitLab CI 里跑代码审查、自动修复 lint 错误
   - 批量处理多个仓库的重构任务
   - 定时任务：每天晚上自动检查依赖更新、生成 changelog

2. **批量任务处理**：
   - 给 100 个代码文件批量加注释
   - 批量转换项目里的图片格式
   - 批量生成测试用例

3. **快速单次任务**：
   - 不想开浏览器，只想快速让 Agent 帮你做一件小事
   - 比如 `npx @deepseek-ai/dsh --profile headless "帮我把当前目录下所有 .js 文件转成 .ts"`
   - 类似命令行工具的使用体验

4. **服务器环境**：
   - 在没有图形界面的 Linux 服务器上运行
   - SSH 远程到服务器执行任务，不需要端口转发看 UI

### Headless 启动命令

Headless 模式的启动非常简单，使用 `--profile headless` 参数：

```bash
npx @deepseek-ai/dsh --profile headless "你的任务描述"
```

#### 常用参数示例

**指定工作目录**：

```bash
npx @deepseek-ai/dsh --profile headless --workspace /path/to/project "重构这个目录下的所有 Python 模块"
```

**指定模型**：

```bash
npx @deepseek-ai/dsh --profile headless --model deepseek-v4-pro "写一个快速排序的单元测试"
```

**从文件读取任务**：

```bash
# 把任务写在 task.txt 里，通过 stdin 传入
cat task.txt | npx @deepseek-ai/dsh --profile headless
```

**非交互模式（不需要人工审批）**：

```bash
# 注意：这会自动批准所有工具调用，只在完全信任的环境使用
npx @deepseek-ai/dsh --profile headless --yes "自动修复所有 ESLint 错误"
```

**指定输出格式**：

```bash
# JSON 格式输出，方便程序解析
npx @deepseek-ai/dsh --profile headless --output json "列出当前目录所有文件，输出 JSON"
```

### Headless 模式特点

Headless 模式有几个关键特点，理解它们能帮你更好地使用：

| 特点 | 说明 |
|------|------|
| **一次性执行** | 任务完成后进程直接退出，不会驻留后台 |
| **无 Web UI** | 不启动 HTTP 服务器（默认 3080 端口），不占用端口 |
| **结果打印到 stdout** | 最终输出直接打印到标准输出，方便脚本捕获 |
| **日志到 stderr** | 执行过程、工具调用等日志输出到 stderr，不污染 stdout |
| **退出码语义** | 0 = 任务成功，非 0 = 执行出错（模型错误、工具失败等） |
| **共享配置** | 和 Web 模式完全共享 `~/.dsh/` 下的所有配置、API Key、模型设置 |
| **会话留存** | 执行的会话同样会被保存到 `~/.dsh/sessions/`，可以事后在 Web UI 里查看 Trajectory |

**重要提示**：即使是无头模式执行的任务，你事后打开 `npx @deepseek-ai/dsh` 启动 Web UI，在历史会话里依然能看到它的完整轨迹，可以回放、分叉、debug——这对于排查自动化任务失败特别有用。

### 简单的 Bash 自动化示例

这是一个在 CI 里用 dsh 自动修复 lint 错误的示例脚本：

```bash
#!/bin/bash
set -e

echo "🔍 运行 ESLint 检查..."
npx eslint src/ --format json > eslint-errors.json || true

if [ -s eslint-errors.json ]; then
    echo "🤖 发现 lint 错误，调用 dsh 自动修复..."
    npx @deepseek-ai/dsh --profile headless --yes \
      "当前目录有 eslint-errors.json 包含 ESLint 错误。请逐个修复这些错误，修改对应的源文件，确保修复后代码逻辑不变。修复完成后再次运行 eslint 验证。"
    
    echo "✅ Lint 修复完成"
else
    echo "✅ 没有 lint 错误"
fi
```

## Python SDK：最方便的嵌入方式

如果你想在自己的 Python 应用里嵌入 dsh 能力，官方提供了 **Python SDK**，这是最推荐的嵌入方式。

### Python SDK 最大特点：自带 Node 运行时

这是 Python SDK 最贴心的设计：**它自带了一个打包好的 Node.js 运行时**，目标机器不需要预先安装 Node.js 或 npx。

这解决了嵌入场景最大的痛点之一：
- 你不需要要求你的用户先装 Node 才能用你的工具
- 不会因为用户系统的 Node 版本不对导致各种诡异问题
- SDK 会自动管理 dsh 版本和 Node 版本，保证兼容性

### 安装 Python SDK

安装非常简单，用 pip 就行：

```bash
pip install deepseek-harness-sdk
```

安装包大小大约 80MB（因为包含了 Node 运行时和 dsh 本体），这是一次性成本。

### Python SDK 核心概念

Python SDK 的 API 设计非常简洁，核心概念只有几个：

1. **DshRuntime**：dsh 运行时实例，管理 dsh 进程的生命周期
2. **DshSession**：一次会话，对应一个任务执行
3. **DshEvent**：执行过程中的事件流（模型输出、工具调用、状态变化等）

### 最简单的使用示例

```python
from deepseek_harness_sdk import DshRuntime

# 创建运行时（会自动下载/启动内置的 dsh）
runtime = DshRuntime()

# 执行一个任务
result = runtime.run(
    task="帮我写一个计算斐波那契数列的 Python 函数，带缓存优化",
    workspace="./my-project",  # 可选：指定工作目录
    model="deepseek-v4-pro",   # 可选：指定模型
)

# 打印最终结果
print("任务结果：")
print(result.output)

# 查看是否成功
if result.success:
    print(f"✅ 任务完成，Token 消耗：{result.token_usage}")
else:
    print(f"❌ 任务失败：{result.error}")
```

### 流式获取执行过程

如果你想实时看到执行过程（像 Web UI 里那样流式输出），可以用流式 API：

```python
from deepseek-harness-sdk import DshRuntime

runtime = DshRuntime()

for event in runtime.run_stream(
    task="解释一下什么是 Capability Seam，用通俗的语言",
):
    match event.type:
        case "assistant_message":
            # 模型正在输出内容
            print(event.content, end="", flush=True)
        case "tool_call":
            # 模型调用了工具
            print(f"\n🔧 调用工具：{event.tool_name}")
        case "tool_result":
            # 工具返回结果
            print(f"📦 工具结果长度：{len(event.result)}")
        case "complete":
            print("\n✅ 任务完成")
        case "error":
            print(f"\n❌ 错误：{event.error}")
```

### 配置管理

Python SDK 默认使用和 CLI 完全相同的 `~/.dsh/` 配置目录，所以你在 Web UI 或 CLI 里配置的 API Key、模型、Profile 都能直接用，不需要重复配置。

如果你想使用独立的配置目录（比如多租户场景），可以指定：

```python
runtime = DshRuntime(
    config_dir="/path/to/separate/.dsh",  # 使用独立配置目录
    workspace="/path/to/workspace",
)
```

### 适合的嵌入场景

Python SDK 特别适合这些场景：

| 场景 | 为什么用 Python SDK |
|------|---------------------|
| **内部 Agent 平台** | 你的公司用 Python 搭内部工具平台，想把 dsh 作为执行引擎嵌入进去 |
| **IDE 插件后端** | 你在做 VS Code/JetBrains 插件，后端用 Python，需要调用 Agent 能力 |
| **自动化工作流引擎** | Airflow/Prefect 等工作流系统里的 Agent 节点 |
| **Jupyter Notebook 集成** | 在 Notebook 里直接调用 dsh 帮你做数据分析、写代码 |
| **批量评测脚本** | 写模型评测脚本时，用 Python 控制 dsh 批量跑测试用例 |

## JSON-RPC SDK：跨语言进程间通信

如果你用的不是 Python（比如 Go、Java、Rust、C#），或者你需要把 dsh 作为一个独立的常驻进程运行，通过协议和它通信，那么可以使用 **JSON-RPC SDK**。

### JSON-RPC 是什么

JSON-RPC 是一个轻量级的远程过程调用协议，dsh 可以作为一个 JSON-RPC 服务器启动，通过 stdio 或 TCP 暴露服务。任何支持 JSON-RPC 的语言都能和它通信。

### 启动 JSON-RPC 服务

```bash
# 通过 stdio 启动 JSON-RPC 服务（默认，适合子进程通信）
npx @deepseek-ai/dsh --rpc

# 通过 TCP 端口启动 JSON-RPC 服务（适合跨进程/跨机器）
npx @deepseek-ai/dsh --rpc --rpc-port 9000
```

### JSON-RPC 核心方法

dsh 的 JSON-RPC API 提供以下核心方法：

| 方法 | 作用 |
|------|------|
| `dsh.startSession` | 启动一个新会话，传入任务、工作区、模型等参数 |
| `dsh.sendEvent` | 向会话发送事件（比如用户追加消息） |
| `dsh.getSession` | 获取会话当前状态 |
| `dsh.cancelSession` | 取消正在运行的会话 |
| `dsh.listSessions` | 列出历史会话 |
| `dsh.subscribe` | 订阅会话事件流（流式输出） |

### 简单的调用示例（Node.js 客户端）

虽然 SDK 本身是 Node 写的，但你可以从任何语言调用它。这里是一个概念性的例子：

```typescript
// 这是概念示例，实际 SDK 会提供更封装好的客户端
import { createJsonRpcClient } from '@deepseek-ai/dsh-json-rpc-client';

const client = createJsonRpcClient({
  transport: 'stdio',  // 或 { type: 'tcp', port: 9000 }
});

// 启动会话
const session = await client.call('dsh.startSession', {
  task: '帮我重构这个函数',
  workspace: '/path/to/code',
  model: 'deepseek-v4-pro',
});

// 订阅事件
client.subscribe(`session.${session.id}`, (event) => {
  if (event.type === 'assistant_message') {
    process.stdout.write(event.content);
  }
});
```

### JSON-RPC vs Python SDK：怎么选

| 维度 | Python SDK | JSON-RPC |
|------|-----------|----------|
| **语言限制** | 只能 Python | 任何语言 |
| **部署模式** | 嵌入到进程内 | 独立常驻进程 |
| **自带 Node** | ✅ 是 | ❌ 需要系统装 Node |
| **性能开销** | 低（直接管理子进程） | 略高（有序列化/网络开销） |
| **多会话共享** | 每次 run 启动新进程 | 一个进程可以同时跑多个会话 |
| **适合场景** | 简单嵌入、脚本、单会话 | 服务端、多租户、多语言环境 |

## ACP 服务端：Agent 通信协议兼容

除了自己的 JSON-RPC 协议，dsh 还支持 **ACP（Agent Communication Protocol）**——这是一个正在兴起的 Agent 间通信开放标准，目标是让不同的 Agent 框架可以互相发现、互相调用、协同工作。

### 什么是 ACP

你可以把 ACP 理解为「Agent 世界的 HTTP 协议」。如果说 MCP 是 Agent 调用工具的标准协议，那么 ACP 就是 Agent 和 Agent 之间通信的标准协议。

- 你的 dsh Agent 可以作为 ACP 服务端对外提供能力
- 其他支持 ACP 的 Agent（不管用什么框架写的）可以发现并调用你的 dsh Agent
- 你也可以在 dsh 里通过 ACP 调用其他外部 Agent

### 启动 ACP 服务端

```bash
npx @deepseek-ai/dsh --acp
```

启动后，dsh 会：
1. 在本地启动 ACP 服务
2. 通过 mDNS（组播 DNS）在局域网广播自己的存在
3. 其他支持 ACP 的 Agent 可以自动发现并连接它

### ACP 服务端的用途

ACP 目前还在早期阶段，但它指向了一个很有意思的未来：

1. **多 Agent 协同**：你可以在一台机器上跑多个不同的 Agent（dsh 负责写代码、另一个 Agent 负责做设计、第三个负责写文档），它们通过 ACP 互相通信协作
2. **团队共享 Agent**：在公司局域网里，你可以在一台强大的服务器上跑一个配置好所有工具和模型的 dsh 实例，团队成员通过 ACP 连接使用，不需要每个人都配置一遍
3. **异构 Agent 编排**：用专门的 Agent 编排框架（比如 LangGraph、AutoGen）作为主控，把具体编码任务通过 ACP 交给 dsh 执行，把搜索任务交给另一个专用 Agent

目前 ACP 支持还比较基础，但这是 dsh 面向未来的一个重要布局——它不希望自己是一个孤岛，而是未来 Agent 生态里的一个一等公民节点。

## 嵌入应用的典型场景

把 dsh 嵌入到自己的应用里，能做什么？这里举几个真实的应用场景，帮你打开思路：

### 1. 内部 Agent 平台

很多公司想搭自己的内部编程 Agent 平台，但从 0 写一个 Agent 运行时成本太高——要处理工具调用、上下文管理、会话日志、权限控制、多模型支持等等。

用 dsh 作为底座是个很好的选择：
- 前端做你自己公司的 UI（对接企业 SSO、审批流、内部工具）
- 后端用 Python SDK 或 JSON-RPC 调用 dsh 作为执行引擎
- 所有复杂的 Agent 运行时逻辑 dsh 已经帮你做好了
- 你只需要专注在业务逻辑和企业定制上

### 2. IDE 插件

VS Code 或 JetBrains 的 AI 编程插件，后端完全可以用 dsh：
- 前端是 IDE 原生的聊天界面、代码 lens、内联补全
- 后端在本地启动 dsh 运行时，通过 JSON-RPC 通信
- 直接复用 dsh 的所有能力：多模型、MCP、插件、Trajectory 调试
- 用户不需要额外装 Node，因为 Python/Node SDK 自带运行时

### 3. 自动化工作流节点

在 CI/CD 或数据工作流里：
- 代码提交后，自动触发 dsh 做代码审查，评论到 PR
- 数据管道出错时，dsh 自动拉取日志、分析原因、尝试修复
- 版本发布前，dsh 自动生成 release notes，更新 changelog

### 4. 模型评测与基准测试

dsh 的 Minimal 模式 + Headless 模式是做模型评测的绝佳组合：
- Minimal 模式提供干净、可控的工具面，所有模型面对完全相同的工具环境
- Headless 模式可以批量跑评测用例
- 完整的 SessionLog 记录了每一次工具调用和输出，方便事后分析对比
- 你可以一次跑 10 个不同模型在同一个评测集上，横向对比结果

这也是为什么很多模型团队在内部评测时优先考虑 dsh——它的可控性和可观测性比黑盒的 CLI 工具强太多。

### 5. 自定义 CLI 工具

你可以基于 dsh 封装自己领域特定的 CLI 工具：

```bash
# 比如你做了一个「项目初始化器」的 dsh 插件
mycli init my-new-project --template react-ts

# 底层调用的是：
# npx @deepseek-ai/dsh --profile headless --load-plugin mycli-plugin "初始化一个 react-ts 项目到 my-new-project"
```

用户不需要知道背后是 dsh，他们用的是你的专属 CLI，但你不用自己写 Agent 逻辑。

## 配置共享：和 Web 模式无缝衔接

不管你用哪种嵌入方式（Headless、Python SDK、JSON-RPC、ACP），它们都**完全共享同一个配置目录 `~/.dsh/`**：

| 配置项 | 是否共享 |
|--------|----------|
| API Key（所有 Provider） | ✅ 完全共享 |
| 模型配置与自定义模型 | ✅ 完全共享 |
| Profile 配置 | ✅ 完全共享（包括 headless profile） |
| MCP 服务器配置 | ✅ 完全共享 |
| 插件安装与配置 | ✅ 完全共享 |
| AGENTS.md 规则 | ✅ 按工作目录读取，规则一致 |
| 历史会话记录 | ✅ 所有模式产生的会话都保存在同一个地方 |

这带来了一个非常棒的体验：

1. 你先在 Web UI 里调通一个任务，把工具、模型、权限都配置好，确认能跑通
2. 然后把同样的任务放到 Headless 模式或 Python SDK 里跑，行为完全一致
3. 如果自动化任务出问题了，你打开 Web UI，在历史会话里能看到无头模式跑的那次完整轨迹，debug 体验和交互式任务完全一样
4. 你不需要在 SDK 里再配一遍 API Key——一次配置，处处生效

> **提示**：如果你确实需要隔离配置（比如测试环境和生产环境分开），所有 SDK 和 CLI 都支持通过 `--config-dir` 参数或环境变量 `DSH_CONFIG_DIR` 指定独立的配置目录。

理解了无头模式和各种 SDK，你就可以把 dsh 从一个「交互式工具」变成你自己系统里的一个「Agent 引擎组件」。下一章我们来整理使用过程中最常见的问题和故障排查方法——遇到问题时先来这里找找答案。

---

← [11 生态互操作](11-ecosystem-interop.md) | → [13 常见问题](13-faq-troubleshooting.md)
