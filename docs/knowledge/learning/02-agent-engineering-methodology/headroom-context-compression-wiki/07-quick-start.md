---
id: "headroom-wiki-07"
title: "快速上手指南"
source: "https://mp.weixin.qq.com/s/7zT5-9WDp8zi4naCC2EmOg?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/headroom-context-compression-wiki/07-quick-start.toml"
---

## 八、快速上手指南

Headroom的上手非常简单，最快几分钟就能体验到Token节省的效果。本章带你一步步完成安装和初次使用。

### 8.1 环境要求

使用Headroom之前，请确保你的环境满足：

- **Python版本**：Python 3.10 或更高版本
- **Node.js版本**（如果使用TypeScript/JavaScript SDK）：Node.js 18+ 推荐
- **操作系统**：Windows、macOS、Linux 都支持
- **Docker**（可选）：如果用Docker方式部署，需要安装Docker

### 8.2 三种安装方式

Headroom提供三种安装方式，选择最适合你的一种即可。

#### 方式1：pip安装（Python用户推荐）

这是最推荐的安装方式，包含所有功能：

```bash
pip install "headroom-ai[all]"
```

安装完成后，你就可以在命令行使用`headroom`命令，也可以在Python代码中`import headroom`。

#### 方式2：npm安装（Node.js/TypeScript用户）

如果你使用TypeScript或JavaScript开发，可以用npm安装：

```bash
npm install headroom-ai
```

安装完成后可以在JS/TS代码中引入，同时也会提供`headroom` CLI命令。

#### 方式3：Docker安装（容器化部署）

如果你喜欢用Docker，也可以直接拉取官方镜像：

```bash
docker pull ghcr.io/chopratejas/headroom:latest
```

Docker方式适合需要容器化部署、或者不想在本地装Python/Node环境的用户。

### 8.3 三步快速上手

安装完成后，只需要三步就能开始使用Headroom。

#### 第一步：安装

按照上面的方式之一安装好Headroom。安装完成后，可以先验证一下是否安装成功：

```bash
headroom --version
```

如果能输出版本号，说明安装成功。

#### 第二步：选择一种接入方式

对于第一次使用的用户，**推荐从Agent Wrap方式开始**，这是最简单、零配置的方式。

如果你用Claude Code：

```bash
headroom wrap claude
```

然后像平常一样使用Claude Code就行——Headroom已经在后台自动帮你压缩所有上下文了。

如果你用Codex：

```bash
headroom wrap codex
```

其他支持的Agent：
```bash
headroom wrap cursor   # Cursor编辑器
headroom wrap aider    # Aider编程助手
headroom wrap copilot  # GitHub Copilot
```

如果你想给自己的OpenAI兼容客户端用，可以选Proxy方式：

```bash
headroom proxy --port 8787
```

然后把你的客户端API Base URL改成`http://localhost:8787`即可。

#### 第三步：查看压缩效果

用了一段时间后，你可以用`headroom perf`命令查看压缩效果统计：

```bash
headroom perf
```

这个命令会显示：
- 累计节省了多少Token
- 平均压缩率是多少
- 各类型内容的压缩情况
- 相当于省了多少钱

看到这些数字，你就能直观感受到Headroom带来的价值。

### 8.4 各接入方式的具体命令示例

这里汇总了四种接入方式的快速启动命令，方便你查阅：

| 接入方式 | 启动命令 | 后续操作 |
|----------|----------|----------|
| **Agent Wrap（推荐新手）** | `headroom wrap claude` | 正常使用Claude Code即可 |
| **Proxy** | `headroom proxy --port 8787` | 客户端API地址改为`http://localhost:8787` |
| **Library（Python）** | `pip install "headroom-ai[all]"` | 代码中`from headroom import compress` |
| **Library（TS）** | `npm install headroom-ai` | 代码中`import { compress } from 'headroom-ai'` |
| **MCP Server** | 在MCP配置中添加headroom | 三个工具自动可用：compress/retrieve/stats |
| **Docker** | `docker run -p 8787:8787 ghcr.io/chopratejas/headroom:latest proxy --port 8787` | 同Proxy方式 |

### 8.5 验证接入成功

怎么知道Headroom确实在工作呢？有几个方法：

1. **看perf统计**：运行`headroom perf`，如果有数据显示（不是全零），说明压缩正在工作
2. **看Token消耗对比**：对比开启Headroom前后类似任务的Token用量，应该能看到明显下降
3. **看日志（可选）**：Headroom有verbose模式，可以看到每次压缩的详细信息（需要时查文档开启）

最简单的验证方式就是：先跑一个你熟悉的任务（比如让Agent读一个大文件并回答问题），看看`headroom perf`里的统计数字，再对比一下平时不用Headroom时的Token消耗，效果一目了然。

### 8.6 下一步

- 想了解各种接入方式的详细用法，看[第四章：四种接入方式详解](04-integration-methods.md)
- 想知道CCR可逆机制的原理，看[第三章：CCR可逆机制深度解析](03-ccr-mechanism.md)
- 想了解压缩算法怎么选，看[第二章：六种压缩算法详解](02-compression-algorithms.md)
- 想探索跨Agent记忆和自动学习，看[第六章：跨Agent记忆与自动学习](06-advanced-features.md)

---

[返回目录](../headroom-context-compression-wiki.md)
