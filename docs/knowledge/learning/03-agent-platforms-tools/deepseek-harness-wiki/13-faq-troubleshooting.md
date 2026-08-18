---
id: deepseek-harness-wiki-13
title: DeepSeek Harness Wiki - 常见问题与故障排查
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/03-deepseek-official.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - faq
  - troubleshooting
  - 故障排查
  - 常见问题
category: learning
maturity: L1
---

# 13 常见问题与故障排查

本章收集了 dsh v0.1 预览版阶段用户最常遇到的问题，每个问题都给出「症状→原因→解决方案」的完整排查路径。遇到问题时先来这里查一查，90% 的问题都能快速解决。

如果这里找不到你的问题，或者解决方案没用，可以到 GitHub Discussions 提问——本章最后有获取帮助的渠道说明。

## 问题 1：Node 版本错误（ERR_UNSUPPORTED_ENGINE）

### 症状

启动时出现类似下面的错误：

```
npm error code ERR_UNSUPPORTED_ENGINE
npm error Unsupported engine
npm error Not compatible with your version of node/npm: @deepseek-ai/dsh@0.1.0-rc.6
npm error Required: {"node":">=20.0.0"}
npm error Got: {"node":"v18.20.4"}
```

或者 npx 直接报错退出，提示 Node 版本不兼容。

### 原因

dsh 基于最新的 Node.js 特性开发，要求 **Node.js 20.x 或更高版本**。如果你的系统 Node 版本低于 20，就会出现这个错误。

这是硬性要求——dsh 用到了 Node 20 才有的原生 Fetch API、Web Streams、更好的 ESM 支持等特性，无法在旧版本上运行。

### 解决方案

**方案一：升级 Node.js（推荐）**

访问 [Node.js 官网](https://nodejs.org/) 下载 20.x 或更高的 LTS 版本，直接安装覆盖即可。

如果你用 nvm（Node Version Manager）：

```bash
# 安装 Node 20
nvm install 20

# 切换到 Node 20
nvm use 20

# 设置为默认版本
nvm alias default 20
```

验证版本：

```bash
node --version
# 应该输出 v20.x.x 或更高
```

**方案二：用 Python SDK（不需要系统装 Node）**

如果你不想升级系统 Node，或者没有权限，可以直接用 Python SDK——它自带打包好的 Node 运行时，不依赖系统 Node：

```bash
pip install deepseek-harness-sdk
```

然后在 Python 代码里用 SDK 调用 dsh，具体用法见 [12 无头模式与 SDK](12-headless-sdk.md)。

---

## 问题 2：3080 端口被占用

### 症状

启动 Web UI 时报错：

```
Error: listen EADDRINUSE: address already in use :::3080
    at Server.setupListenHandle [as _listen2] (net.js:...)
    ...
✖ 无法启动服务：端口 3080 已被占用
```

或者启动后浏览器打开是一个完全不相关的网站。

### 原因

dsh 的 Web UI 默认监听 `http://localhost:3080`。如果这个端口已经被其他程序占用（可能是另一个 dsh 实例没关，也可能是其他完全不相关的服务），就会启动失败。

### 解决方案

**方案一：指定其他端口启动（最简单）**

用 `--port` 参数换一个端口：

```bash
npx @deepseek-ai/dsh --port 3081
```

启动后浏览器会自动打开 `http://localhost:3081`。

**方案二：找到并关闭占用端口的程序**

如果你想继续用 3080，可以先找到是谁占用了它：

**Windows**：

```powershell
# 查找占用 3080 端口的进程
netstat -ano | findstr :3080

# 最后一列是 PID，用 taskkill 杀掉（把 <PID> 换成实际数字）
taskkill /PID <PID> /F
```

**macOS/Linux**：

```bash
# 查找并杀掉占用 3080 的进程
lsof -ti:3080 | xargs kill -9
```

常见的占用者：
- 另一个没关的 dsh 实例（最常见）
- 本地开发的其他 Web 服务
- 某些 VPN 或代理软件

---

## 问题 3：MISSING_CREDENTIAL 错误

### 症状

发送任务后很快失败，错误信息类似：

```
❌ 错误：MISSING_CREDENTIAL
No API key found for provider 'deepseek'.
Please configure your API key in settings or environment variable.
```

### 原因

dsh 找不到对应模型 Provider 的 API Key。第一次使用时，你需要至少配置一个模型的 API Key。

dsh 查找 API Key 的顺序是：
1. 会话/启动参数里指定的 key
2. 环境变量（`DEEPSEEK_API_KEY`、`OPENAI_API_KEY` 等）
3. `~/.dsh/settings.yaml` 里保存的配置
4. 系统环境变量或其他 CLI 配置（比如 Codex/OpenAI CLI 的配置）

如果以上地方都没有，就会报这个错。

### 解决方案

**方案一：在 Web UI 里配置（推荐）**

1. 启动 dsh 打开 Web UI
2. 点击左下角的「设置」图标（齿轮）
3. 选择「模型提供商」
4. 找到你要用的提供商（比如 DeepSeek）
5. 粘贴你的 API Key，点击「测试连接」
6. 连接成功后点「保存」，Key 会加密保存在 `~/.dsh/` 下

**方案二：用环境变量（适合 CI/无头模式）**

```bash
# DeepSeek API Key
export DEEPSEEK_API_KEY="sk-xxx"

# OpenAI API Key（如果你用 OpenAI 模型）
export OPENAI_API_KEY="sk-xxx"

# 然后启动 dsh
npx @deepseek-ai/dsh
```

Windows PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="sk-xxx"
npx @deepseek-ai/dsh
```

**方案三：首次启动向导**

如果你是第一次启动 dsh，它会自动弹出「欢迎向导」，第一步就是让你配置 API Key——跟着向导走就行，不会漏掉。

> **提示**：DeepSeek API Key 可以在 [platform.deepseek.com](https://platform.deepseek.com/) 申请注册获取。

---

## 问题 4：UNKNOWN_MODEL 错误

### 症状

选择模型时找不到，或者运行时报错：

```
❌ 错误：UNKNOWN_MODEL
Model 'deepseek-v4-pro' is not configured or not found in enabled providers.
```

或者模型下拉列表是空的，或者只有很少几个模型。

### 原因

有几种可能的原因：

1. **模型 ID 写错了**：比如你手动指定模型名，拼错了
2. **对应 Provider 没启用**：你选了 OpenAI 的模型，但没配置 OpenAI Provider
3. **API Key 对应的账号没有该模型权限**：比如你用的是旧的 API Key，没有新模型的访问权限
4. **自定义模型没添加**：如果你用本地模型或第三方代理，需要手动添加模型配置

### 解决方案

**步骤 1：检查模型 ID 是否正确**

确认模型 ID 拼写正确。常用模型 ID：

| 模型 | 正确 ID |
|------|---------|
| DeepSeek V4 Pro | `deepseek-v4-pro` |
| DeepSeek V4 Flash | `deepseek-v4-flash` |
| DeepSeek V3 | `deepseek-chat` |
| GPT-4o | `gpt-4o` |
| Claude 3.5 Sonnet | `claude-3-5-sonnet-20241022` |

**步骤 2：确认 Provider 已启用且配置正确**

在 Web UI → 设置 → 模型提供商里，检查对应提供商的开关是打开的，并且 API Key 配置正确。可以点「测试连接」确认能正常访问。

**步骤 3：添加自定义/本地模型**

如果你用本地模型（比如 Ollama）或第三方兼容 API，需要手动添加：

1. 在模型提供商页面选择「添加自定义 Provider」
2. 填写 API Base URL（比如 Ollama 是 `http://localhost:11434/v1`）
3. 添加模型 ID 和名称
4. 保存后就能在模型列表里看到了

---

## 问题 5：输入框灰色无法输入

### 症状

打开 Web UI 后，底部的输入框是灰色的，点不动也输不进去字，好像被禁用了。

### 原因

这是新用户最常遇到的「不是 bug 的 bug」。输入框被禁用有两个常见原因：

1. **没选择工作区（Workspace）**：dsh 需要知道在哪个目录工作，没选工作区就不能开始任务
2. **没选择模型**：你需要至少选一个可用的模型，Agent 才能开始工作

这两个条件都满足后，输入框才会变成可输入状态。

### 解决方案

看界面右上角（或左上角，取决于版本）：

1. **选择工作区**：点击「选择文件夹」或工作区下拉框，选择你要让 Agent 工作的目录（可以是任何一个本地文件夹）
2. **选择模型**：点击模型下拉框，选择一个你配置好的模型（比如 `deepseek-v4-pro`）

两个都选好之后，输入框会立即变成可输入状态，就可以发任务了。

> **提示**：如果你用命令行启动时指定了工作区（`--workspace ./my-project`），工作区会自动选好，只需要再选模型就行。

---

## 问题 6：--host 0.0.0.0 局域网访问被拒绝

### 症状

你想在局域网里访问 dsh（比如从另一台电脑连你的机器），启动时加了参数：

```bash
npx @deepseek-ai/dsh --host 0.0.0.0
```

但从其他机器访问 `http://你的IP:3080` 时，要么连接超时，要么被拒绝，要么打开了但功能不正常。

### 原因

这**不是 bug**，而是 dsh 的**故意设计**。

dsh 从一开始就被设计为**本地优先（Local-First）的单机工具**，不是可以直接暴露到网络的 SaaS 服务。它默认只监听 `localhost`（127.0.0.1），并且做了很多安全假设（比如信任本地所有请求、没有用户认证、没有权限隔离）。

如果你直接把它绑定到 `0.0.0.0` 暴露到局域网甚至公网，会有严重的安全风险——同一网络下的任何人都能访问你的 dsh，让它执行任意代码、访问你所有文件，这相当于直接把你的机器权限给了别人。

所以即使你加了 `--host 0.0.0.0`，dsh 也会检测并阻止非 localhost 的访问，或者在功能上做限制。

### 解决方案

首先想清楚你**为什么需要局域网访问**：

**如果只是想从同一台机器的浏览器访问**：
- 不需要加 `--host`，直接用 `http://localhost:3080` 就行，这是支持的。

**如果想在团队里共享使用**：
- dsh 目前（v0.1）没有团队协作、多用户、远程访问的设计
- 不要直接把它暴露到网络
- 等官方未来的企业/团队版本，或者你自己在前面加一层带认证的反向代理（但要自己承担安全风险）

**如果是远程开发场景（比如 SSH 到服务器用）**：
- 用 SSH 端口转发，而不是直接暴露端口：

```bash
# 在你本地机器执行，把服务器的 3080 转发到本地 3080
ssh -L 3080:localhost:3080 user@your-server
```

然后在你本地浏览器打开 `http://localhost:3080`，安全又方便。

**如果你确实知道风险，就要在局域网用（仅在受信任的私有网络）**：
- 官方文档不推荐这么做，但你可以通过环境变量强制关闭本地检查：

```bash
DSH_DISABLE_LOCALHOST_CHECK=1 npx @deepseek-ai/dsh --host 0.0.0.0
```

⚠️ **再次警告**：这会让局域网内所有人都能访问你的 dsh，能执行任意代码、访问你所有文件。**绝对不要在公网这么做，也不要在不可信的网络这么做**，出了安全问题自己负责。

---

## 问题 7：Windows PTY 不可用

### 症状

在 Windows（特别是原生 CMD/PowerShell）上运行时，终端输出乱码，或者交互式命令（比如需要用户输入的命令、top、vim 这类 TUI 程序）无法正常工作，或者看到类似警告：

```
[WARN] Windows PTY not available, falling back to ConPTY...
[WARN] 终端交互功能受限，建议使用 WSL2 获得完整体验
```

### 原因

dsh 的终端模拟功能依赖 POSIX 风格的 PTY（伪终端）。虽然 Windows 10/11 有 ConPTY，但兼容性还是不如 Linux/macOS 的原生 PTY，特别是：
- 复杂的 TUI 程序（vim、htop、less 等）显示可能异常
- 部分需要实时交互的命令会卡住
- ANSI 转义序列解析可能有问题
- 颜色和格式可能不对

这是 Windows 平台的已知限制，不是 dsh 的 bug。

### 解决方案

**推荐方案：使用 WSL2（Windows Subsystem for Linux 2）**

这是在 Windows 上用 dsh 体验最好的方式：

1. 安装 WSL2（微软官方文档有一键安装命令：`wsl --install`）
2. 在 WSL2 里安装 Node.js 20+
3. 在 WSL2 里运行 dsh
4. 用 Windows 的浏览器访问 WSL2 里的 dsh（WSL2 会自动转发端口，直接打开 `http://localhost:3080` 就行）

WSL2 里的 dsh 拥有和 Linux/macOS 完全一致的完整体验，没有任何功能限制。

**临时方案：不用交互式命令**

如果你暂时不想装 WSL2，可以：
- 避免让 Agent 运行交互式命令（vim、top、需要输入的脚本等）
- 在提示词里告诉 Agent「不要运行交互式命令，用非交互参数」
- 大部分编程任务不需要交互式命令，基本还是能用的

**不推荐：用 Git Bash 或 Cygwin**

这些环境能部分改善体验，但还是会有各种奇怪问题，不如直接用 WSL2。

---

## 问题 8：图片/视觉输入不工作

### 症状

你在输入框里上传了图片（或者拖拽图片进去），但：
- 图片发出去后模型好像没看见
- 模型说「我看不到图片」或者「你没有提供图片」
- 或者输入框根本就不让你粘贴/上传图片

### 原因

视觉（图片）输入不是所有模型都支持的，即使模型支持，也可能没在 dsh 配置里开启。dsh 默认的输入配置是 `text`（只支持文本），需要手动开启图片输入。

### 解决方案

**步骤 1：确认你用的模型支持视觉**

支持视觉的模型：
- ✅ DeepSeek V4 Pro / V4 Flash
- ✅ GPT-4o、GPT-4V
- ✅ Claude 3.5 Sonnet、Claude 3 Opus
- ❌ 纯文本模型（比如 DeepSeek V3、旧的 GPT-4 等）不支持

**步骤 2：在 settings.yaml 里开启图片输入**

打开 `~/.dsh/settings.yaml`（如果不存在就创建），添加或修改：

```yaml
# ~/.dsh/settings.yaml
input:
  - text
  - image  # 添加这一行，开启图片输入
```

或者更完整的配置：

```yaml
model:
  default: deepseek-v4-pro
  providers:
    deepseek:
      apiKey: "sk-xxx"
      models:
        - id: deepseek-v4-pro
          input: [text, image]  # 该模型支持文本和图片
```

**步骤 3：重启 dsh**

修改配置后需要重启 dsh 才能生效。重启后你应该能：
- 在输入框看到图片上传按钮
- 能粘贴/拖拽图片进去
- 模型能正确识别图片内容

---

## 问题 9：升级后旧会话无法读取

### 症状

你升级了 dsh 版本（比如从 rc.5 升到 rc.6），打开 Web UI 后发现：
- 旧的会话列表还在，但点进去打不开
- 报错：「无法解析会话日志，格式版本不兼容」
- 或者会话能打开但 Trajectory 显示异常、事件丢失

### 原因

v0.1 是开发者预览版，**会话日志格式和存储结构还在快速演化**。官方目前**不承诺不同预览版之间的会话格式兼容性**——升级后旧版本的会话可能无法在新版本中正常读取。

这是预览版的正常现象，不是你的数据丢了。

### 解决方案

**方案一：接受现状（推荐）**

预览版阶段的会话主要是用来临时调试的，不建议把重要数据长期存在会话里。升级前如果有特别重要的会话内容，可以手动导出保存。

**方案二：不自动升级，固定版本使用**

如果你需要长期保留会话，可以固定使用一个版本，不要随便升级：

```bash
# 不升级，固定用 rc.5 版本
npx @deepseek-ai/dsh@0.1.0-rc.5
```

**方案三：手动降级回旧版本**

如果确实需要读旧会话，可以临时降级回原来的版本：

```bash
# 比如回到 rc.5
npx @deepseek-ai/dsh@0.1.0-rc.5
```

旧版本能正常读取它自己创建的会话。你可以把需要的内容复制出来，再升回新版本。

> **说明**：等 v1.0 正式版发布后，官方会开始承诺版本间的会话格式兼容性，到时候就不会有这个问题了。现在预览版阶段，建议把会话当作临时数据看待。

---

## 问题 10：Token 消耗比预期高

### 症状

跑一个看起来不大的任务，结果 Token 消耗比你预期的高很多；或者你感觉同样的任务，dsh 比其他 Agent 工具费 Token。

### 原因

这是 v0.1 预览版阶段的已知问题，有几个原因：

1. **系统提示词比较长**：dsh 的插件系统、工具描述、Capability Seam 等框架本身需要一定的上下文开销
2. **上下文压缩还在优化**：v0.1 的上下文压缩/裁剪算法是基础实现，不够激进，会保留比较多的上下文
3. **工具调用比较详细**：dsh 的工具调用返回结果默认会带比较多的元数据和上下文，方便 Trajectory 记录和调试
4. **没有做激进的历史裁剪**：默认配置下 dsh 会保留比较完整的对话历史，不会过早丢弃

官方说 Token 效率优化是 v0.2 版本的重点之一，后续会有明显改善。

### 解决方案

**临时缓解方法**：

1. **用 Minimal 模式跑简单任务**：Minimal 模式的系统提示词和工具集最小，Token 开销最低
   ```bash
   npx @deepseek-ai/dsh --profile minimal
   ```

2. **在设置里调小上下文窗口保留策略**：编辑 `~/.dsh/settings.yaml`：
   ```yaml
   context:
     maxTokens: 8000  # 根据你的模型调整，不要设太大
     compressionThreshold: 0.7  # 更早触发压缩
     aggressivePruning: true  # 开启激进裁剪
   ```

3. **及时开新会话**：一个会话跑太久，历史会越来越长，Token 消耗会增加。任务做完了就开新会话，不要在一个超长会话里一直聊。

4. **用更便宜的模型做简单任务**：简单任务用 `deepseek-v4-flash`，复杂任务再切到 V4 Pro，能省不少钱。

5. **关掉不需要的插件**：你装的每个插件都会贡献自己的提示词和工具描述，不用的插件就禁用掉。

**预期改善**：官方已经明确 Token 优化是 v0.2 的核心目标之一，等版本更新后这个问题会有明显改善。

---

## ~/.dsh/ 配置文件位置速查表

所有 dsh 的配置、缓存、会话数据都存在用户目录下的 `.dsh/` 文件夹里。不同操作系统的位置：

| 操作系统 | 路径 |
|----------|------|
| **Windows** | `C:\Users\<你的用户名>\.dsh\` |
| **macOS** | `/Users/<你的用户名>/.dsh/` 或 `~/.dsh/` |
| **Linux** | `/home/<你的用户名>/.dsh/` 或 `~/.dsh/` |
| **WSL2** | `/home/<你的用户名>/.dsh/`（WSL 内的 Linux 路径） |

### ~/.dsh/ 目录结构速查

| 文件/目录 | 作用 | 能删吗？ |
|-----------|------|----------|
| `settings.yaml` | 主配置文件，包含 API Key、模型设置、全局配置 | ❌ 删了要重新配置 |
| `profiles/` | 各个 Profile 的配置文件 | ❌ 删了自定义 Profile 会丢 |
| `plugins/` | 你安装的第三方插件 | ⚠️ 删了插件要重装 |
| `sessions/` | 所有历史会话日志和 Trajectory 数据 | ✅ 可以删，删了历史会话没了 |
| `cache/` | 模型列表、插件索引等缓存 | ✅ 可以删，会自动重新生成 |
| `logs/` | dsh 运行时的调试日志 | ✅ 可以删，不影响使用 |
| `mcp.json` | 全局 MCP 服务器配置 | ❌ 删了 MCP 配置会丢 |
| `AGENTS.md` | 全局 Agent 规则文件 | ❌ 删了全局规则没了 |

> **提示**：如果你想「重置 dsh 到干净状态」，可以先备份 `settings.yaml` 和 `mcp.json`，然后删掉整个 `.dsh/` 目录，重启 dsh 会重新生成默认配置。

---

## 获取帮助的渠道

如果上面的 FAQ 没解决你的问题，可以通过以下渠道获取帮助：

### 1. GitHub Discussions（推荐）

- 地址：[github.com/deepseek-ai/deepseek-harness/discussions](https://github.com/deepseek-ai/deepseek-harness/discussions)
- 这是官方推荐的提问渠道，有核心开发者和社区用户活跃
- 提问前先搜索一下有没有人问过同样的问题
- 提问时请带上：dsh 版本号、操作系统、Node 版本、完整的错误信息、复现步骤

### 2. GitHub Issues

- 地址：[github.com/deepseek-ai/deepseek-harness/issues](https://github.com/deepseek-ai/deepseek-harness/issues)
- **只有确认是 bug 才提 Issue**，使用问题请到 Discussions
- 提 Issue 同样要带上完整的复现信息和环境

### 3. 插件相关问题

如果你在开发或使用第三方插件：
- 在 GitHub 搜索标签 `dsh-plugin`，很多插件作者会在自己的仓库提供支持
- 在 Discussions 的「Plugins」分类下提问

### 4. 调试模式获取更多日志

提问前可以先用调试模式启动，获取更详细的日志：

```bash
# Linux/macOS
DEBUG=dsh:* npx @deepseek-ai/dsh

# Windows PowerShell
$env:DEBUG="dsh:*"
npx @deepseek-ai/dsh
```

这会打印非常详细的调试日志，能帮你（和帮你解决问题的人）快速定位问题。

---

掌握了常见问题的排查方法，你应该能解决 90% 以上的使用问题了。下一章我们来聊聊 dsh 目前适合用在哪些场景，不适合用在哪些场景，以及你必须知道的风险提示——**这章非常重要，特别是如果你想在工作中用 dsh 的话，请一定要读**。

---

← [12 无头模式](12-headless-sdk.md) | → [14 适用场景与风险](14-use-cases-limitations.md)
