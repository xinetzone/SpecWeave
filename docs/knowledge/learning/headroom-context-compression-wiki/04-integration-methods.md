---
id: headroom-wiki-04-integration-methods
title: "Headroom — 四种接入方式详解"
source: "https://mp.weixin.qq.com/s/7zT5-9WDp8zi4naCC2EmOg?from=industrynews&color_scheme=light#rd"
date: "2026-08-03"
category: "learning"
tags: ["headroom", "integration", "library", "proxy", "mcp", "agent-wrap"]
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/learning/headroom-context-compression-wiki/04-integration-methods.toml"
---

# Headroom — 四种接入方式详解

> 本章详细介绍Headroom支持的四种接入方式：Library（API调用）、Proxy（零代码代理）、Agent Wrap（一键包装主流Agent）、MCP Server（标准工具协议），并提供选型建议表格帮助不同类型用户快速上手。

---

## 1. 接入方式总览

Headroom在设计上遵循"**渐进式接入**"原则——从最简单的零代码方式到深度集成的API方式，用户可以根据自己的需求和技术能力选择最合适的接入路径，无需一开始就做大规模改造。

| 接入方式 | 改造成本 | 技术要求 | 灵活度 | 适合人群 |
|---------|---------|---------|-------|---------|
| **Proxy** | ⭐ 零代码 | 会改base_url就行 | ⭐⭐ | 所有终端用户（最快体验） |
| **Agent Wrap** | ⭐ 一条命令 | 会用命令行 | ⭐⭐⭐ | 主流AI Coding工具用户 |
| **MCP Server** | ⭐⭐ 配置即可 | 了解MCP协议 | ⭐⭐⭐⭐ | Claude Desktop/Cursor等支持MCP的工具 |
| **Library** | ⭐⭐⭐⭐ 代码集成 | 会写Python/TS | ⭐⭐⭐⭐⭐ | 自建Agent的开发者 |

**建议路径**：先用Proxy体验效果 → 用Agent Wrap包日常使用的工具 → 如果是开发者再用Library深度集成。

---

## 2. Library：API调用方式

Library方式适合**自建AI Agent的开发者**，通过Python或TypeScript SDK直接调用compress函数，在自己的代码中精确控制压缩逻辑。

### Python SDK使用示例

#### 安装

```bash
pip install headroom-ai
```

#### 基础使用：compress(messages)

```python
from headroom import Headroom

# 初始化Headroom
headroom = Headroom()

# 你的原始消息列表（OpenAI格式）
messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "帮我看一下这个搜索结果"},
    {"role": "tool", "tool_call_id": "search_1", "name": "search_code", "content": """
[
  {"id": 1, "file": "auth.py", "path": "/src/auth.py", "size": 4521, "language": "python", "content": "import os\\nimport jwt\\nfrom typing import Optional..."},
  {"id": 2, "file": "auth.py", "path": "/src/auth.py", "size": 4521, "language": "python", "content": "..."},
  // ... 还有47个搜索结果
]
"""}
]

# 一键压缩
compressed_messages = headroom.compress(messages)

# 压缩后的messages直接传给OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=compressed_messages,
    tools=tools  # Headroom自动注入headroom_retrieve工具
)
```

#### 高级配置

```python
headroom = Headroom(
    compression_level=0.7,  # 0-1，越高压缩越激进
    cache_dir="~/.my-headroom-cache",  # 自定义缓存位置
    algorithms={  # 针对不同类型内容的算法配置
        "json": "smartcrusher",
        "code": "codecompressor",
        "natural_language": "kompress-v2-base"
    },
    retrieve_enabled=True  # 启用按需取回
)
```

#### 单独压缩不同内容类型

```python
# 压缩代码
compressed_code = headroom.compress_code(python_code, language="python")

# 压缩JSON
compressed_json = headroom.compress_json(api_response)

# 压缩日志
compressed_logs = headroom.compress_logs(server_logs, filter_level="WARN")
```

### TypeScript SDK使用示例

#### 安装

```bash
npm install @headroom-ai/sdk
```

#### 基础使用

```typescript
import { Headroom } from '@headroom-ai/sdk';
import OpenAI from 'openai';

const headroom = new Headroom();

const messages = [
  { role: 'system', content: 'You are a helpful coding assistant.' },
  { role: 'user', content: 'Analyze these search results' },
  { role: 'tool', tool_call_id: 'search_1', name: 'search_code', content: largeSearchResults }
];

// 压缩
const compressedMessages = await headroom.compress(messages);

// 调用LLM
const openai = new OpenAI();
const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: compressedMessages,
  tools: headroom.getTools()  // 获取包含headroom_retrieve的工具列表
});
```

### Library方式的优势

- **最灵活**：可以精确控制在哪个环节压缩、压缩哪些内容
- **可定制**：可以替换压缩算法、自定义压缩规则
- **性能最好**：没有代理层的网络开销
- **适合深度集成**：将压缩逻辑嵌入自己的Agent框架

---

## 3. Proxy：零代码代理方式

Proxy方式是**所有接入方式中最简单的**——一条命令启动本地代理，然后把OpenAI SDK的base_url改成代理地址，零代码改动即可享受压缩。

### 快速开始

#### 1. 启动Proxy

```bash
headroom proxy --port 8787
```

启动后你会看到：
```
Headroom Proxy running on http://localhost:8787
→ Compression enabled: all requests will be automatically compressed
→ CCR enabled: original data cached locally
→ Dashboard available at http://localhost:8787/dashboard
```

#### 2. 修改base_url

**Python OpenAI SDK**：
```python
from openai import OpenAI

# 只需要改base_url，其他完全不动
client = OpenAI(
    base_url="http://localhost:8787/v1"  # 原来可能是https://api.openai.com/v1
)

# 下面的代码和原来一模一样，不需要任何修改
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)
```

**环境变量方式**（不改代码）：
```bash
export OPENAI_BASE_URL=http://localhost:8787/v1
# 然后正常运行你的程序，所有请求自动经过Headroom压缩
```

**TypeScript/JavaScript**：
```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://localhost:8787/v1'
});
```

### Proxy工作原理

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  你的代码    │────→│  Headroom Proxy  │────→│  OpenAI API      │
│  (无改动)    │←────│  端口8787        │←────│  (真实API)       │
└─────────────┘     └──────────────────┘     └──────────────────┘
                          ↓
                    ┌──────────────┐
                    │ 本地缓存存储  │
                    └──────────────┘
```

1. 你的代码把请求发给Headroom Proxy（以为是OpenAI）
2. Proxy拦截请求，对messages和tools进行压缩
3. Proxy自动注入`headroom_retrieve`工具定义
4. Proxy把压缩后的请求转发给真实OpenAI API
5. 如果模型返回`headroom_retrieve`工具调用，Proxy在本地处理，不转发给OpenAI
6. 取回内容后，Proxy把内容注入上下文，继续转发请求
7. 最终响应原样返回给你的代码

### Proxy常用配置

```bash
# 指定上游API地址（支持Azure OpenAI、Anthropic等兼容接口）
headroom proxy --port 8787 --upstream https://your-azure-openai-endpoint.openai.azure.com

# 设置压缩级别
headroom proxy --port 8787 --compression-level 0.8

# 指定API key（避免从环境变量读取）
headroom proxy --port 8787 --api-key sk-xxx

# 启用详细日志（查看压缩效果）
headroom proxy --port 8787 --verbose

# 启用Dashboard查看统计
headroom proxy --port 8787 --dashboard
```

### Proxy方式的优势

- **真正零代码**：除了改base_url，不需要改一行代码
- **即开即用**：一条命令启动，立刻看到Token节省效果
- **兼容性好**：任何使用OpenAI兼容接口的库/工具都能用
- **可观测**：内置Dashboard可以看压缩率、Token节省统计
- **支持隔离**：团队可以部署一个共享Proxy给所有人用

---

## 4. Agent Wrap：一条命令包装主流Agent

如果你日常使用Claude Code、Codex、Cursor、Aider、GitHub Copilot等AI Coding工具，Agent Wrap方式是最方便的——不需要改任何配置，一条命令就能"包住"这些工具，自动享受压缩。

### 支持的Agent

| 工具 | 命令 | 说明 |
|------|------|------|
| **Claude Code** | `headroom wrap claude` | 包装Anthropic官方Claude CLI |
| **OpenAI Codex CLI** | `headroom wrap codex` | 包装OpenAI Codex命令行工具 |
| **Cursor** | `headroom wrap cursor` | 包装Cursor编辑器（命令行启动模式） |
| **Aider** | `headroom wrap aider` | 包装aider AI pair programming工具 |
| **GitHub Copilot CLI** | `headroom wrap copilot` | 包装GitHub Copilot命令行 |
| **自定义命令** | `headroom wrap -- <your-command>` | 包装任何OpenAI兼容的命令行工具 |

### 使用示例

#### 包装Claude Code

```bash
# 原来启动Claude Code
claude

# 用Headroom包装启动（效果一样，但自动压缩）
headroom wrap claude
```

启动后会看到提示：
```
🚀 Headroom wrapping claude...
→ Compression enabled for all conversations
→ Original data cached at ~/.headroom/cache
→ Run 'headroom stats' to see token savings
```

然后你正常使用Claude Code就行，所有的工具输出、代码读取、对话历史都会被自动压缩，模型需要时自动取回原文。

#### 包装Aider

```bash
# 原来启动aider
aider --model gpt-4o

# 用Headroom包装
headroom wrap aider -- --model gpt-4o
```

#### 包装任意自定义命令

```bash
# 包装你自己写的Python脚本
headroom wrap -- python my_agent.py

# 包装任何OpenAI兼容的CLI工具
headroom wrap -- npx @openai/codex
```

### Wrap工作原理

Agent Wrap本质上是**透明的进程包装器**：
1. 设置环境变量`OPENAI_BASE_URL=http://localhost:xxxx`（自动启动随机端口的Proxy）
2. 启动被包装的Agent进程
3. Agent进程的所有OpenAI API调用自动经过Headroom Proxy压缩
4. Agent退出时，自动关闭Proxy并打印本次会话的Token节省统计

会话结束后，你会看到类似这样的统计：
```
📊 Session Statistics:
→ Original tokens: 45,230
→ Compressed tokens: 8,921
→ Tokens saved: 36,309 (80.3%)
→ Estimated cost saved: $0.47
```

### Agent Wrap的优势

- **零配置**：不需要记Proxy端口，不需要改环境变量
- **自动清理**：用完自动关闭Proxy，不会留后台进程
- **会话统计**：每次用完都能看到省了多少Token、多少钱
- **即包即用**：想给哪个工具加压缩就包哪个，不影响其他工具

---

## 5. MCP Server：标准工具协议

MCP（Model Context Protocol）是Anthropic推出的开放工具协议，Headroom作为MCP Server提供三个标准工具，任何支持MCP的客户端（Claude Desktop、Cursor、Windsurf等）都可以直接接入。

### MCP提供的三个工具

Headroom MCP Server暴露三个标准工具：

| 工具名 | 功能 |
|-------|------|
| `headroom_compress` | 主动压缩指定内容 |
| `headroom_retrieve` | 从本地缓存取回原始内容（CCR核心） |
| `headroom_stats` | 查看当前压缩统计、Token节省数据 |

### 配置方法

#### Claude Desktop配置

编辑Claude Desktop的配置文件：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

添加Headroom MCP配置：

```json
{
  "mcpServers": {
    "headroom": {
      "command": "headroom",
      "args": ["mcp"],
      "env": {
        "HEADROOM_CACHE_DIR": "~/.headroom/cache"
      }
    }
  }
}
```

重启Claude Desktop，你会在工具列表中看到headroom的三个工具。

#### Cursor配置

在Cursor中：
1. 打开Settings → Features → MCP
2. 点击"Add New MCP Server"
3. 填写：
   - Name: `headroom`
   - Command: `headroom mcp`
4. 保存，即可在Cursor中使用headroom工具

### 工具使用示例

#### headroom_compress

用户可以主动让模型压缩内容：
```
用户：帮我把这个文件读一下，太长了先压缩一下
模型：我来用headroom_compress压缩这个文件内容...
[调用headroom_compress(content=file_content)]
```

或者Headroom可以配置为自动压缩所有读取的文件内容。

#### headroom_retrieve

当模型需要看细节时（和CCR机制配合）：
```
模型：这个函数的签名我看到了，让我取回具体实现看一下...
[调用headroom_retrieve(content_id="file_abc123", focus="process_user_data function")]
```

#### headroom_stats

你可以随时问模型：
```
用户：今天省了多少Token？
模型：让我查一下统计数据...
[调用headroom_stats()]
→ 今日累计：原始Token 156,420，压缩后32,180，节省79.4%
```

### MCP方式的优势

- **标准协议**：一次配置，所有支持MCP的工具都能用
- **主动/被动结合**：既可以自动压缩，也可以让用户主动调用
- **统一体验**：在不同工具中使用Headroom的方式保持一致
- **生态兼容**：未来新出的MCP客户端可以无缝接入

---

## 6. 选型建议表格

根据你的用户类型和使用场景，参考下表选择最合适的接入方式：

| 用户类型 | 典型场景 | 推荐接入方式 | 上手命令/步骤 |
|---------|---------|------------|-------------|
| **非技术用户** | 用Claude/Cursor写代码，想省Token | **Agent Wrap** | `headroom wrap claude` 或 `headroom wrap cursor` |
| **AI Coding爱好者** | 用aider/Codex等工具，想快速体验 | **Proxy** 或 **Agent Wrap** | 1. `headroom proxy --port 8787`<br>2. 改base_url即可；<br>或者直接`headroom wrap aider` |
| **开发者（自己用）** | 自己写脚本调用LLM，不想改代码 | **Proxy** | `headroom proxy --port 8787` + `export OPENAI_BASE_URL=...` |
| **Claude Desktop用户** | 用Claude Desktop做各种任务 | **MCP Server** | 按上文配置MCP即可，零代码侵入 |
| **团队/企业用户** | 团队多人使用，想统一压缩和统计 | **Proxy（共享部署）** | 部署在内部服务器，团队共用一个endpoint |
| **Agent框架开发者** | 自建Agent框架，想深度集成压缩逻辑 | **Library** | `pip install headroom-ai`，在代码中调用`compress()` |
| **MCP生态用户** | 已经在用MCP工具，想统一管理 | **MCP Server** | 直接在MCP配置中加入headroom |

### 混合使用建议

你可以同时使用多种接入方式，它们共享同一个本地缓存：

- 日常用Cursor IDE → 用MCP方式
- 命令行用aider → 用`headroom wrap aider`
- 自己跑脚本 → 用Proxy方式
- 开发新Agent功能 → 用Library方式

所有方式的压缩数据、缓存内容、统计信息都是互通的，因为它们都指向同一个本地Headroom实例。

---

## 7. 接入方式对比总结

| 特性 | Library | Proxy | Agent Wrap | MCP Server |
|------|---------|-------|-----------|-----------|
| 改代码量 | 需要写代码 | 只改base_url | 零代码 | 配置文件 |
| 启动方式 | 代码中初始化 | 手动启动/后台服务 | 自动启动 | 随客户端启动 |
| 灵活度 | 最高（完全控制） | 高（配置参数） | 中（命令行参数） | 中（通过工具调用） |
| 性能 | 最好（进程内调用） | 很好（本地环回网络） | 很好（本地Proxy） | 好（MCP协议开销） |
| 适合集成深度 | 深度集成 | 透明代理 | 即开即用 | 生态兼容 |
| 自动压缩 | 要手动调用compress | 自动压缩所有请求 | 自动压缩被包装进程 | 可配置自动/手动 |
| CCR支持 | ✅ | ✅ | ✅ | ✅ |
| 统计面板 | 需要自己实现 | 内置Dashboard | 会话后自动打印 | 通过headroom_stats查看 |

**核心原则**：从最简单的方式开始，不够用了再升级到更灵活的方式。Headroom的设计让你可以无痛升级——你在Proxy方式下积累的缓存，换成Library方式照样用。

---

- ← [上一章：CCR可逆机制深度解析](03-ccr-mechanism.md)
- [下一章：效果验证与数据分析](05-performance-data.md) →
