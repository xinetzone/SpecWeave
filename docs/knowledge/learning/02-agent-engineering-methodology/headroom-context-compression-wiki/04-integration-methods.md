---
id: "headroom-wiki-04"
title: "四种接入方式详解"
source: "https://mp.weixin.qq.com/s/7zT5-9WDp8zi4naCC2EmOg?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/headroom-context-compression-wiki/04-integration-methods.toml"
---
## 五、四种接入方式详解

Headroom提供了四种灵活的接入方式，从几行代码集成到零代码开箱即用，覆盖不同用户的需求。

### 5.1 Library方式：代码级集成

如果你在自己开发Python或TypeScript应用，想要在代码中直接集成压缩能力，Library方式是最直接的选择。只需要几行代码就能完成接入。

**Python示例：**

```python
from headroom import compress

messages = [
    {"role": "user", "content": "这里是大量的工具输出、文件内容..."},
    # ... 更多消息
]

compressed_messages = compress(messages)
# 然后把compressed_messages发给LLM即可
```

**TypeScript示例：**

```typescript
import { compress } from 'headroom-ai';

const messages = [
  { role: 'user', content: '这里是大量的工具输出、文件内容...' },
  // ... 更多消息
];

const compressedMessages = await compress(messages);
// 然后把compressedMessages发给LLM即可
```

**适用场景**：
- 自己开发Agent应用
- 需要在代码中精细控制压缩时机
- 想要把压缩能力集成到现有工作流中

### 5.2 Proxy方式：零代码代理

如果你已经有了OpenAI兼容的客户端，不想改任何代码，Proxy方式是最方便的选择。只需要启动一个本地代理，然后把客户端的API地址指向这个代理即可，零代码改动。

**启动命令：**

```bash
headroom proxy --port 8787
```

然后把你的OpenAI客户端配置改成：
- API Base URL: `http://localhost:8787`
- API Key: （保持原来的key不变，Headroom只是本地代理，不会窃取你的key）

**工作原理**：
Headroom Proxy在本地启动一个兼容OpenAI API格式的HTTP代理服务，所有发往这个代理的请求都会被Headroom先压缩处理，然后转发给真正的LLM API，返回结果再原样返回给客户端。

**适用场景**：
- 使用任何OpenAI兼容的客户端（包括各种GUI工具、第三方客户端）
- 不想修改任何代码
- 需要快速试用Headroom效果

### 5.3 Agent Wrap方式：一条命令包住主流编程Agent

对于使用Claude Code、Codex、Cursor、Aider、Copilot等主流编程Agent的用户，Headroom提供了更简单的Wrap方式——一条命令直接把Agent包住，自动启用压缩。

**用法：**

```bash
headroom wrap claude
# 或者
headroom wrap codex
headroom wrap cursor
headroom wrap aider
headroom wrap copilot
```

运行这个命令后，Headroom会启动一个包装层，Agent的所有LLM调用都会自动经过Headroom压缩，你正常使用Agent即可，不需要做任何其他配置。

**支持的Agent列表**：
- Claude Code
- OpenAI Codex
- Cursor
- Aider
- GitHub Copilot

这是普通用户最推荐的入门方式——安装完Headroom，跑一条`headroom wrap claude`，然后像平常一样用Claude Code就行，Token已经悄悄给你省下来了。

**适用场景**：
- 使用主流编程Agent的普通用户
- 想要零配置上手
- 不想折腾代码或网络配置

### 5.4 MCP Server方式：通过MCP协议灵活控制

如果你的客户端支持MCP（Model Context Protocol），Headroom可以作为MCP Server注册到客户端中，提供三个工具供模型主动调用。这种方式最灵活，模型可以自己决定什么时候压缩、什么时候取回原文。

**注册后提供的三个工具：**

#### 1. headroom_compress

主动压缩指定内容。

**功能**：将传入的内容按类型进行智能压缩。

**使用场景**：模型有一大段内容想要压缩后再使用时主动调用。

#### 2. headroom_retrieve

取回原始内容（CCR机制的核心工具）。

**功能**：根据压缩内容的标识，从本地缓存中取回原始未压缩内容。

**使用场景**：模型发现压缩后的上下文信息不足，需要查看细节时主动调用。这就是CCR机制中"R"的入口。

#### 3. headroom_stats

查看压缩统计数据。

**功能**：返回当前会话的压缩统计，包括：
- 原始Token总数
- 压缩后Token总数
- 节省的Token数量
- 压缩率
- 各算法使用情况

**使用场景**：用户或模型想要了解压缩效果时调用。你也可以在命令行用`headroom perf`命令查看。

**适用场景**：
- 使用支持MCP的客户端（如Claude Desktop、支持MCP的IDE等）
- 想要模型能够主动控制压缩和检索
- 需要最灵活的使用方式

### 5.5 选型建议

不同场景下推荐的接入方式：

| 使用场景 | 推荐接入方式 | 理由 |
|----------|--------------|------|
| 我是开发者，要在自己的Python/TS应用里用 | Library | 最灵活，代码级控制 |
| 我用现成的OpenAI兼容客户端，不想改代码 | Proxy | 零代码，改个API地址就行 |
| 我用Claude Code/Codex/Cursor编程 | Agent Wrap | 一条命令搞定，零配置 |
| 我用支持MCP的客户端，想要模型主动控制 | MCP Server | 最灵活，模型可主动Retrieve |
| 第一次用，想先试试效果 | Agent Wrap 或 Proxy | 上手最简单 |

对于大多数用户来说，推荐从`headroom wrap claude`（或你常用的Agent）开始，这是最快体验到Headroom效果的方式。

---

[返回目录](../headroom-context-compression-wiki.md)
