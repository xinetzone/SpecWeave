---
id: "retrospective-claude-code-agnes-proxy"
title: "Claude Code + Agnes API 本地代理配置指南"
date: "2026-08-26"
type: "technical-guide"
source: "Trae 会话：Claude Code 模型白名单绕过 + Agnes API 接入 + 七概念复盘"
scope: "task"
category: "environment-setup"
tags: ["claude-code", "agnes-api", "proxy", "llm-configuration", "security-hardening"]
version: "2.0"
---

# Claude Code + Agnes API 本地代理配置指南

> **主题**：通过本地 HTTP 代理让 Claude Code 使用免费的 Agnes 模型（agnes-2.5-flash）
> **日期**：2026-08-26
> **版本**：v2.0（安全脱敏版）
> **关键问题**：Claude Code 客户端硬编码模型白名单（仅接受 `claude-*` 前缀），无法直接使用第三方模型

***

## 一、问题背景

Claude Code（Anthropic 官方 CLI 工具）在发送请求前进行客户端模型名校验，仅允许以 `claude-` 开头的模型名。直接在 `settings.json` 中配置非 Claude 模型名（如 `agnes-2.5-flash`）会报错：

```
There's an issue with the selected model (agnes-2.5-flash).
It may not exist or you may not have access to it.
```

此校验发生在请求发出之前，与 API 端点、认证 Token 均无关。

## 二、解决方案：本地代理层

核心思路：在本地启动一个 HTTP 代理，对 Claude Code 伪装成 Anthropic API，在转发请求时：

1. **模型名翻译**：将 `claude-sonnet-4-20250514`（Claude Code 认可的模型名）替换为 `agnes-2.5-flash`（真实目标模型）
2. **路径归一化**：自动处理 `/v1` 前缀重复问题（`ANTHROPIC_BASE_URL` 含 `/v1` + Claude Code 自动追加 `/v1` 导致路径 404）
3. **非流式响应**：使用 `stream=False` + 显式 `Content-Length` 头避免 Python 简单 HTTP 服务器的分块编码问题
4. **Token 安全**：API 密钥通过 `.env` 文件/环境变量注入，不硬编码在代码中

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Claude Code  │────▶│  Local Proxy     │────▶│  Agnes API      │
│  model:      │     │  127.0.0.1:18080 │     │  agnes-2.5-     │
│  claude-     │     │  ─ 模型名转换    │     │  flash          │
│  sonnet-4    │     │  ─ 路径归一化    │     │                 │
│              │     │  ─ 非流式响应    │     │                 │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

## 三、文件清单与安装位置

所有代理相关文件统一放在独立子目录中：

```
~/.claude/
├── settings.json                     # Claude Code 配置（指向本地代理）
└── agnes-proxy/                      # 代理独立目录
    ├── agnes_proxy.py                # 代理服务脚本（Python 标准库，零依赖）
    ├── start-agnes-proxy.bat         # Windows 一键启动脚本
    ├── .env                          # 私有配置（含 Token，勿分享/提交）
    ├── .env.example                  # 配置模板（无真实 Token）
    └── README.md                     # 使用文档
```

### 3.1 settings.json 配置

在 `~/.claude/settings.json` 中配置（已脱敏）：

```json
{
    "env": {
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:18080",
        "ANTHROPIC_AUTH_TOKEN": "any",
        "ANTHROPIC_MODEL": "claude-sonnet-4-20250514",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-sonnet-4-20250514",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-20250514",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-sonnet-4-20250514",
        "CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-20250514",
        "API_TIMEOUT_MS": "3000000",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
    }
}
```

> **注意**：`ANTHROPIC_AUTH_TOKEN` 设为任意值即可，真实 Agnes API Token 存储在代理的 `.env` 文件中。

### 3.2 .env 配置模板（.env.example）

```env
# Agnes Proxy Configuration
# Copy this file to .env and fill in your actual token.
# NEVER commit .env to version control!

AGNES_TOKEN=your-agnes-api-token-here
AGNES_MODEL=agnes-2.5-flash
AGNES_PROXY_PORT=18080
# AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
```

## 四、快速开始

### 步骤 1：配置 Token

首次使用前，将 `.env.example` 复制为 `.env` 并填入真实 API Token：

```powershell
Copy-Item ~/.claude/agnes-proxy/.env.example ~/.claude/agnes-proxy/.env
# 然后编辑 .env，将 your-agnes-api-token-here 替换为真实 Token
```

### 步骤 2：启动代理

**Windows（推荐）**：双击 `start-agnes-proxy.bat`

**命令行**：
```powershell
python ~/.claude/agnes-proxy/agnes_proxy.py
```

**macOS/Linux**：
```bash
python3 ~/.claude/agnes-proxy/agnes_proxy.py
```

启动成功标志：
```
==================================================
  Agnes Proxy for Claude Code
==================================================
  Listen on:   http://127.0.0.1:18080
  Target model: agnes-2.5-flash
  Agnes API:    https://apihub.agnes-ai.com/v1
  Token:        sk-xxxx...xxxx (loaded from .env)
  Health check: http://127.0.0.1:18080/health
==================================================
```

### 步骤 3：启动 Claude Code

**新开终端窗口**（代理窗口保持打开）：
```powershell
claude
```

### 步骤 4：验证代理

```powershell
# 健康检查
curl http://127.0.0.1:18080/health
# 预期返回：{"status":"ok","service":"agnes-proxy",...}
```

## 五、配置参考

### 5.1 配置优先级

命令行参数 > 环境变量 > `.env` 文件 > 内置默认值

### 5.2 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `AGNES_TOKEN` | ✅ | - | Agnes API 密钥 |
| `AGNES_MODEL` | ❌ | `agnes-2.5-flash` | 目标模型 |
| `AGNES_PROXY_PORT` | ❌ | `18080` | 代理监听端口 |
| `AGNES_BASE_URL` | ❌ | `https://apihub.agnes-ai.com/v1` | API 地址 |

### 5.3 可用模型

| 模型 ID | 说明 |
|---------|------|
| `agnes-2.0-flash` | 快速版 |
| `agnes-2.5-flash` | 免费推荐 ⭐ |
| `agnes-2.5-pro` | 专业版（可能收费） |
| `agnes-2.5-pro-alpha` | 测试版 |

### 5.4 命令行参数

```bash
python agnes_proxy.py [OPTIONS]

选项：
  --model MODEL        目标模型 (默认: agnes-2.5-flash)
  --port PORT          监听端口 (默认: 18080)
  --base-url URL       API 地址
  --token TOKEN        API Token（不推荐，优先用环境变量/.env）
  --debug              启用调试日志
  --help               显示帮助
```

## 六、关键技术细节

### 6.1 模型白名单绕过

Claude Code v2.1.77 在客户端维护了一个模型名白名单，仅允许 `claude-*` 前缀。代理使用固定的伪装模型 ID `claude-sonnet-4-20250514`，在转发到 Agnes API 时替换为真实模型名。`/v1/models` 端点返回包含该伪装 ID 的模型列表。

### 6.2 路径去重

`ANTHROPIC_BASE_URL` 设置为 `http://127.0.0.1:18080`（不含 `/v1`），代理在内部处理路径前缀，避免 `/v1/v1/messages` 404 错误。

### 6.3 非流式响应处理

最初使用 `stream=True` + `iter_content` 转发流式响应，但 Python `http.server` 基类在处理分块传输编码时存在 `IncompleteRead` 错误。改为 `stream=False` 收集完整响应后一次性返回，并显式设置 `Content-Length` 头。

### 6.4 API 格式选择

Agnes API 同时支持 Anthropic Messages API 和 OpenAI Chat Completions 格式。实测：
- **Anthropic 格式**（`/v1/messages`）：`content[0].text` 返回完整文本 ✅
- **OpenAI 格式**（`/v1/chat/completions`）：`content` 为空，`reasoning_content` 有思考链内容 ❌

代理使用 Anthropic 格式转发请求。

## 七、安全加固（v2.0）

v2.0 相比初版的安全改进：

1. **零硬编码 Token**：API 密钥完全从环境变量/`.env` 文件读取，缺失时报错退出
2. **独立目录隔离**：所有代理文件放在 `~/.claude/agnes-proxy/` 子目录，不混在 Claude Code 配置根目录
3. **.env 模板机制**：提供 `.env.example` 模板，`.env` 含真实密钥且不应被提交到版本控制
4. **Token 脱敏显示**：启动 banner 仅显示 Token 前8后4位预览，不打印完整值
5. **分层配置**：CLI 参数 > 环境变量 > `.env` > 默认值，灵活且安全
6. **本地绑定**：代理仅监听 `127.0.0.1`，不暴露到局域网

### 安全最佳实践

1. 永远不要将 `.env` 文件提交到 Git
2. 避免在命令行使用 `--token` 参数（会在 shell 历史中留下记录）
3. 定期轮换 API Token
4. 代理仅监听 127.0.0.1，禁止修改为 `0.0.0.0`

## 八、故障排除

| 错误 | 原因 | 解决 |
|------|------|------|
| `AGNES_TOKEN not set` | 未配置 API Token | 编辑 `.env` 文件填入 `AGNES_TOKEN` |
| `There's an issue with the selected model` | 代理未启动或配置错误 | 确认代理运行中，访问 `/health` 检查 |
| `Address already in use` | 端口被占用 | `--port 18081` 换端口，同步修改 settings.json |
| Claude Code 无响应 | 启动顺序错误 | 先启动代理，再启动 Claude Code |
| 404 Invalid URL | 路径重复问题 | 确保 `ANTHROPIC_BASE_URL` 不含 `/v1` 后缀 |
| 503/403 from upstream | 网络或 Token 问题 | 检查 Token 有效性、网络连接 |

## 九、开机自启（Windows）

通过任务计划程序实现开机自启：

1. `Win + R` → `taskschd.msc`
2. 创建基本任务 → 名称：Agnes Proxy
3. 触发器：计算机启动时
4. 操作：启动程序
   - 程序/脚本：`python`
   - 添加参数：`%USERPROFILE%\.claude\agnes-proxy\agnes_proxy.py`
   - 起始于：`%USERPROFILE%\.claude\agnes-proxy`
5. 勾选"不管用户是否登录都要运行"

## 十、代理端点说明

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查，返回代理状态和配置信息 |
| `/v1/models` | GET | 返回伪装模型列表（供 Claude Code 校验） |
| `/v1/messages` | POST | Anthropic Messages API 转发端点（核心功能） |

***

*报告生成时间：2026-08-26 | 方法论：seven-concepts（I→F→A→V→C）*
