---
type: Reference
title: awesun-skill 源码
description: 向日葵 Awesun Skill 源码登记，含 SKILL.md 三层结构、MCPExecutor 执行器、mcp-config.json 配置与安装方式
tags: [agent-skills, awesun, skill, source, reference, mcp]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-awesun-skill
    resource: "/references/facts-awesun-skill.md"
    title: awesun-skill 事实清单
---

# awesun-skill 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | 向日葵 (Awesun) Skill |
| 定位 | 基于向日葵 MCP 服务为支持 Skills 的 AI Agent 提供渐进式披露的工具调用 |
| 源码路径 | `d:\AI\.chaos\libs\awesun-skill\` |
| 支持 AI 工具 | Claude Code、Open Code、OpenClaw |
| Python 要求 | 3.7 以上 |
| 客户端要求 | 向日葵客户端 16.3.2 以上并启用 MCP 服务（Stdio 模式） |
| 技能名称 | `awesun-remote-control` |
| 版本 | 1.0 |

## 目录结构

```text
awesun-remote-control/
├── SKILL.md          # 技能主入口（frontmatter + 工具清单）
├── executor.py       # MCP Skill 执行器（MCPExecutor 类）
├── mcp-config.json   # MCP 服务器连接配置
└── package.json      # 包元数据与 setup 脚本
```

## SKILL.md frontmatter

```yaml
---
name: awesun-remote-control
description: 向日葵远程控制(awesun-remote-control) 提供 22 个工具。使用场景包括：控制命令、控制连接、控制断开。关键词：远程控制，设备管理，桌面控制，远程CMD，远程电源管理。
version: 1.0
---
```

正文按三类列出全部 22 个工具：
- **Device（7 个）**：device_add、device_info、device_remove、device_search、device_shutdown、device_update、device_wakeup
- **Control（6 个）**：control_connect、control_disconnect、control_portforward、control_screenshot、control_sessions、control_command
- **Desktop（9 个）**：desktop_click_mouse、desktop_move_mouse、desktop_drag_mouse、desktop_scroll_mouse 等

每个工具包含功能描述、必填参数、可选参数。`control_connect` 支持 file/desktop/cmd2/ssh/desktop_view/newcamera/forward 七种远控类型。

## executor.py 执行器

`executor.py` 是 MCP Skill 执行器，文件头声明为 "MCP Skill Executor - Dynamic tool invocation"。

### MCPExecutor 类

| 方法 | 功能 |
|------|------|
| `__init__(server_config)` | 初始化，检查 mcp 包可用性（HAS_MCP 标志） |
| `connect()` | 验证 server_config 含 command 和 env 字段，通过 StdioServerParameters + stdio_client 连接，AsyncExitStack 管理生命周期，调用 session.initialize() |
| `list_tools()` | 返回可用工具列表，每项含 name 和 description |
| `describe_tool(tool_name)` | 获取特定工具的详细 inputSchema |
| `call_tool(tool_name, arguments)` | 执行工具调用，返回 response.content |
| `close()` | 通过 AsyncExitStack.aclose() 关闭连接 |

mcp 包通过 try/except ImportError 可选导入，缺失时抛出 ImportError 提示 `pip install mcp`。

### CLI 入口

`main()` 函数支持三个参数：
- `--list`：列出所有可用工具
- `--describe <tool>`：获取指定工具的 schema
- `--call <json>`：执行 JSON 格式的工具调用

配置从同目录 `mcp-config.json` 加载，支持 `mcpServers.awesun-mcp-server` 嵌套格式或顶级格式。

## mcp-config.json 配置

```json
{
  "name": "awesun-mcp-server",
  "command": "/Applications/AweSun.app/Contents/Helpers/awesun-mcp-server",
  "env": {
    "AWESUN_API_URL": "http://127.0.0.1:8908",
    "AWESUN_API_TOKEN": "your-mcp-server-token"
  }
}
```

| 字段 | 说明 |
|------|------|
| `name` | MCP 服务器名称 |
| `command` | MCP 服务器可执行文件路径（默认 macOS 路径） |
| `env.AWESUN_API_URL` | 向日葵本地 API 地址（默认 http://127.0.0.1:8908） |
| `env.AWESUN_API_TOKEN` | MCP 服务认证令牌（需替换为实际 token） |

## package.json

| 属性 | 值 |
|------|-----|
| name | `skill-awesun-remote-control` |
| version | `1.0.0` |
| description | "Claude Skill for awesun-remote-control MCP server" |
| setup 脚本 | `pip install mcp` |

## 安装方式

| AI 工具 | 全局路径 | 项目路径 |
|---------|---------|---------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenCode | `~/.opencode/skills/` | `.opencode/skills/` |

配置步骤：编辑 `mcp-config.json`，替换 command 路径（Windows 路径需指向向日葵安装目录下的 mcp-server）和 AWESUN_API_TOKEN。
