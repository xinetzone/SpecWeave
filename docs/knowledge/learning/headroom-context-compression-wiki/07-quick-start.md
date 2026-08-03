---
id: headroom-wiki-07-quick-start
title: "Headroom — 快速上手指南"
source: "https://mp.weixin.qq.com/s/7zT5-9WDp8zi4naCC2EmOg?from=industrynews&color_scheme=light#rd"
date: "2026-08-03"
category: "learning"
tags: ["headroom", "quickstart", "installation", "getting-started", "docker"]
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/learning/headroom-context-compression-wiki/07-quick-start.toml"
---

# Headroom — 快速上手指南

> 本章提供从0到1的快速上手流程：环境要求、三种安装方式（pip/npm/Docker）、三步快速体验、各接入方式验证方法，以及常见安装问题排查，帮助你在5分钟内体验Headroom的压缩效果。

---

## 1. 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| **Python** | 3.10+ | Python SDK、CLI工具、Proxy、MCP Server均需要Python环境 |
| **Node.js** | 18+ | 仅使用TypeScript/JavaScript SDK时需要 |
| **Docker** | 20.10+ | 仅使用Docker方式部署时需要 |
| **操作系统** | macOS 12+ / Windows 10+ / Linux (Ubuntu 20.04+) | 全平台支持 |
| **网络** | 可访问LLM API（OpenAI/Anthropic等） | 压缩本身本地运行，但最终仍需调用LLM |

> **注意**：Headroom的压缩逻辑完全在本地运行，不会把你的代码或数据发送到第三方服务器（除了正常的LLM API调用）。

---

## 2. 安装命令

Headroom提供三种安装方式，选择最适合你的即可。

### 方式一：pip安装（推荐，包含CLI和所有功能）

这是最推荐的安装方式，包含完整的CLI工具、Proxy、Agent Wrap、MCP Server和Python SDK：

```bash
# 安装完整版（包含所有可选依赖，推荐）
pip install "headroom-ai[all]"

# 或者只安装核心版本（不含向量数据库等可选依赖）
pip install headroom-ai
```

安装完成后，验证安装：
```bash
headroom --version
# 输出类似：headroom, version 0.3.0
```

### 方式二：npm安装（仅TypeScript/JavaScript SDK）

如果你只需要在Node.js项目中使用Headroom SDK：

```bash
npm install headroom-ai

# 或者使用yarn/pnpm
yarn add headroom-ai
pnpm add headroom-ai
```

> **注意**：npm包只包含JavaScript/TypeScript SDK，不包含CLI工具、Proxy等服务端功能。如果需要完整功能，请使用pip安装。

### 方式三：Docker安装（零依赖部署）

如果你不想在本地安装Python/Node环境，可以直接使用Docker镜像：

```bash
# 拉取最新镜像
docker pull ghcr.io/chopratejas/headroom:latest

# 验证镜像
docker run --rm ghcr.io/chopratejas/headroom:latest --version
```

---

## 3. 三步快速上手

无论你用哪种方式安装，都可以通过"安装→选接法→验证"三步快速体验Headroom效果。

### 第一步：安装（已完成则跳过）

参考上文选择合适的安装方式，确保`headroom --version`命令能正常输出版本号。

### 第二步：选择接入方式

根据你的使用场景选择最简单的接入方式（推荐先从Agent Wrap开始体验）：

| 如果你... | 选择 | 操作 |
|-----------|------|------|
| 日常用Claude Code/Cursor/Aider | **Agent Wrap** | 直接用`headroom wrap`包住你常用的工具 |
| 想零代码给现有项目加压缩 | **Proxy** | 启动Proxy，改一下base_url |
| 用Claude Desktop/Windsurf | **MCP Server** | 配置MCP即可 |
| 自己写Python/JS代码调用LLM | **Library** | 在代码中导入Headroom SDK |

### 第三步：验证效果（headroom perf）

Headroom提供了一个专门的性能验证命令，可以快速看到压缩效果：

```bash
# 运行内置性能测试
headroom perf

# 或者指定测试场景
headroom perf --scenario code-search  # 代码搜索场景
headroom perf --scenario logs          # 日志压缩场景
headroom perf --scenario json          # JSON API响应场景
headroom perf --scenario all           # 所有场景（默认）
```

运行后你会看到类似这样的输出：
```
🚀 Headroom Performance Test
============================

📊 Scenario: Code Search (50个搜索结果)
→ Original tokens: 10,144
→ Compressed tokens: 1,260
→ Compression ratio: 87.6%
→ Quality score: 0.94 (1.0 = 与原文完全一致)
→ Estimated cost saving: 87.6%

📊 Scenario: Server Logs (1000行INFO/ERROR日志)
→ Original tokens: 8,542
→ Compressed tokens: 986
→ Compression ratio: 88.5%
→ Quality score: 0.97
→ Estimated cost saving: 88.5%

✅ All scenarios passed! Average compression ratio: 85.2%
```

看到类似输出说明Headroom安装成功、工作正常！

---

## 4. 各接入方式快速验证

### 4.1 Agent Wrap方式验证（最简单，推荐先试这个）

以包装Claude Code为例：

```bash
# 1. 启动包装后的Claude Code
headroom wrap claude

# 2. 在Claude Code中做一件容易产生长上下文的事，比如：
#    - 让它读一个大文件并分析
#    - 让它搜索代码
#    - 让它看一段长日志

# 3. 正常使用即可，退出Claude Code后会自动打印统计：
📊 Session Statistics:
→ Original tokens: 32,450
→ Compressed tokens: 5,820
→ Tokens saved: 26,630 (82.1%)
→ Estimated cost saved: $0.35
```

### 4.2 Proxy方式验证

```bash
# 1. 启动Proxy（终端窗口A）
headroom proxy --port 8787 --dashboard

# 2. 新开终端窗口B，设置环境变量并运行你的代码
export OPENAI_BASE_URL=http://localhost:8787/v1
python your_script_that_calls_openai.py

# 3. 打开Dashboard查看实时压缩效果
#    浏览器访问：http://localhost:8787/dashboard
```

### 4.3 MCP Server方式验证（Claude Desktop为例）

1. 按照[第四章](04-integration-methods.md#5-mcp-server标准工具协议)配置好MCP
2. 重启Claude Desktop
3. 在对话框中输入："帮我看看headroom的统计数据"
4. Claude会自动调用`headroom_stats`工具，你会看到压缩统计信息

如果能正常返回统计数据，说明MCP配置成功。

### 4.4 Library方式验证（Python）

创建一个测试文件`test_headroom.py`：

```python
from headroom import Headroom

# 初始化
headroom = Headroom()

# 测试用的长文本（模拟代码搜索结果）
test_content = """
[
  {"id": 1, "file": "auth.py", "content": "import os\\nimport jwt\\n..."},
  {"id": 2, "file": "auth.py", "content": "def verify_token(token):\\n    try:\\n..."},
  // ... 想象这里还有48个类似的搜索结果
]
""" * 20  # 重复20次制造长文本

# 压缩
messages = [{"role": "user", "content": test_content}]
compressed = headroom.compress(messages)

# 计算token数（简单估算，实际用tiktoken更准确）
original_tokens = len(test_content.split())
compressed_tokens = len(str(compressed).split())

print(f"Original (approx): {original_tokens} tokens")
print(f"Compressed (approx): {compressed_tokens} tokens")
print(f"Ratio: {(1 - compressed_tokens/original_tokens)*100:.1f}%")
print("✅ Headroom Library works!")
```

运行：
```bash
python test_headroom.py
```

---

## 5. 常见安装问题排查

### Q1: pip install 报错 "Python version is too old"

**症状**：安装时提示Python版本不满足要求。

**解决方案**：
- 确认Python版本：`python3 --version`（需要3.10+）
- 如果系统默认Python版本太低，可以用pyenv/conda管理多版本：
  ```bash
  # 用conda创建新环境
  conda create -n headroom python=3.11
  conda activate headroom
  pip install "headroom-ai[all]"
  ```

### Q2: `headroom` 命令找不到（command not found）

**症状**：安装成功但输入`headroom`提示命令不存在。

**解决方案**：
- 检查pip安装路径是否在PATH中：
  ```bash
  python3 -m pip show headroom-ai | grep Location
  # 通常是 ~/.local/bin 或类似路径
  ```
- 把pip bin目录加入PATH：
  ```bash
  # bash/zsh
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
  
  # 或者直接用python -m方式运行
  python3 -m headroom --version
  ```

### Q3: Docker拉取镜像失败

**症状**：`docker pull`时报网络错误或超时。

**解决方案**：
- 检查网络连接，确认可以访问ghcr.io
- 如果在国内网络环境，可以配置Docker镜像加速器
- 或者换用pip安装方式，不需要Docker

### Q4: 启动Proxy时提示端口被占用

**症状**：`headroom proxy --port 8787`提示"Address already in use"。

**解决方案**：
- 换一个端口：`headroom proxy --port 8788`
- 或者杀掉占用端口的进程：
  ```bash
  # macOS/Linux
  lsof -ti:8787 | xargs kill -9
  
  # Windows
  netstat -ano | findstr :8787
  taskkill /PID <进程ID> /F
  ```

### Q5: 运行`headroom perf`时LLM API报错

**症状**：性能测试过程中提示API key错误或网络错误。

**解决方案**：
- 确认OpenAI API key已设置：`echo $OPENAI_API_KEY`
- 如果没有设置，先配置：
  ```bash
  export OPENAI_API_KEY=sk-xxx
  ```
- `headroom perf`需要调用LLM来评估压缩质量，如果只是想快速验证安装，可以跳过perf，直接用Agent Wrap方式体验

### Q6: Windows上MCP配置不生效

**症状**：配置了MCP但Claude Desktop里看不到headroom工具。

**解决方案**：
- 确认配置文件路径正确：`%APPDATA%\Claude\claude_desktop_config.json`
- 确认JSON格式正确（可以用JSONLint校验）
- 确认`headroom`命令在系统PATH中（可以在cmd里直接运行`headroom --version`测试）
- 重启Claude Desktop（完全退出再重新打开）
- 如果还是不行，尝试在MCP配置中写headroom的完整路径：
  ```json
  {
    "mcpServers": {
      "headroom": {
        "command": "C:\\Users\\<你的用户名>\\AppData\\Roaming\\Python\\Python311\\Scripts\\headroom.exe",
        "args": ["mcp"]
      }
    }
  }
  ```

### Q7: 压缩后模型好像不知道要调用headroom_retrieve

**症状**：压缩后模型回答不完整，好像不知道可以取回原文。

**解决方案**：
- 确认使用的是OpenAI兼容格式，且tools参数正确传递
- 如果用Library方式，确保调用时传入了`headroom.getTools()`作为tools参数
- 如果用Proxy/Wrap方式，这是自动处理的，不需要手动配置
- 刚开始使用时模型可能需要1-2轮对话适应，多试几次就会熟练使用取回功能了

---

## 6. 安装后下一步

安装验证成功后，建议按以下路径继续：

1. **体验效果**：用Agent Wrap包一下你日常用的AI工具，用半天看看能省多少Token
2. **选择合适的接法**：参考[第四章：四种接入方式详解](04-integration-methods.md)，确定长期使用的接入方式
3. **了解原理**：阅读[第三章：CCR可逆机制](03-ccr-mechanism.md)，理解为什么压缩不会丢信息
4. **查看数据**：用`headroom stats`命令看累计省了多少Token、多少钱
5. **进阶功能**：体验[第六章的跨Agent记忆和自学习功能](06-advanced-features.md)

如果遇到问题，先查看[第九章：FAQ与资源链接](09-faq-resources.md)，或者去GitHub提Issue。

---

- ← [上一章：进阶功能：跨Agent记忆与自学习](06-advanced-features.md)
- [下一章：深度洞察与模式萃取](08-insights-patterns.md) →
