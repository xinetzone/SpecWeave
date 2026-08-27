---
type: Concept
title: Awesun 远程控制 Skill 实战
description: awesun-skill 通过 MCPExecutor 桥接向日葵 MCP 服务器的实战架构，22 工具三类映射、mcp-config.json 配置与安装流程
tags: [agent-skills, awesun, remote-control, mcp, executor, skill]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
  - id: awesun-mcp-source
    resource: "/references/awesun-mcp-source.md"
    title: awesun-mcp 源码
---

# Awesun 远程控制 Skill 实战

awesun-skill 是"MCP 工具 + Skill 知识包"混合架构的典型实践。它不重新实现远程控制能力，而是通过 SKILL.md 组织工具知识，通过 executor.py（MCPExecutor 类）桥接已有的 awesun-mcp 服务器，为 Claude Code、OpenCode、OpenClaw 等支持 Skills 的 AI 工具提供渐进式披露的远程控制能力。

## 三层架构

```text
┌─────────────────────────────────────────────┐
│  AI Agent（Claude Code / OpenCode）          │
│    读取 SKILL.md → 理解 22 个工具的能力       │
│    决定调用 → 执行 executor.py               │
└──────────────────┬──────────────────────────┘
                   │ stdio（subprocess）
┌──────────────────▼──────────────────────────┐
│  executor.py（MCPExecutor）                  │
│    读取 mcp-config.json                      │
│    StdioServerParameters → stdio_client      │
│    ClientSession → call_tool                 │
└──────────────────┬──────────────────────────┘
                   │ stdio / HTTP
┌──────────────────▼──────────────────────────┐
│  awesun-mcp-server（向日葵客户端内置）         │
│    22 个工具：device_* / control_* / desktop_*│
│    连接向日葵本地 API（127.0.0.1:8908）       │
└─────────────────────────────────────────────┘
```

## SKILL.md 的工具组织

SKILL.md 正文将 22 个工具按操作域分为三类，每类列出工具名、功能描述、必填参数和可选参数：

### Device 类（7 个）

设备生命周期管理：`device_add`、`device_info`、`device_remove`、`device_search`、`device_shutdown`、`device_update`、`device_wakeup`。

AI 首先通过 `device_search`（支持 keyword 模糊搜索和 limit 分页）查找设备，获取 remote_id，再用 remote_id 调用 info/update/remove/shutdown/wakeup 等操作。`device_add` 成功后可通过 device_search 查询新设备。

### Control 类（6 个）

远控会话管理：`control_connect`、`control_disconnect`、`control_portforward`、`control_screenshot`、`control_sessions`、`control_command`。

典型的工作流是：`control_connect`（建立会话，指定 type）→ 获取 session_id → `control_screenshot`（查看屏幕）或 `control_command`（执行命令）→ `control_disconnect`（终止会话）。

`control_connect` 的 type 参数决定了远控模式：
- `desktop`：完整远程桌面控制
- `desktop_view`：仅观看模式
- `cmd2`：Windows CMD 命令行
- `ssh`：Linux/Mac SSH 会话
- `file`：远程文件管理
- `newcamera`：摄像头查看
- `forward`：端口转发

### Desktop 类（9 个）

桌面输入模拟：`desktop_click_mouse`、`desktop_move_mouse`、`desktop_drag_mouse`、`desktop_scroll_mouse` 等。

这些工具需要先建立 desktop 类型的会话。所有坐标使用归一化值（0.0-1.0），通过 `x_pixel / 屏幕宽度` 计算。

## MCPExecutor 实现细节

### 连接管理

`connect()` 方法的关键步骤：

1. 验证 `server_config` 包含非空的 `command` 和 `env` 字段
2. 创建 `StdioServerParameters`（command、args、env）
3. 使用 `AsyncExitStack` 管理资源生命周期
4. 通过 `stdio_client(server_params)` 建立 stdio 传输
5. 创建 `ClientSession(read_stream, write_stream)`
6. 调用 `session.initialize()` 完成 MCP 握手

AsyncExitStack 确保在 close() 时按逆序清理 ClientSession 和 stdio 传输，即使发生异常也不会泄漏进程。

### 工具发现与调用

| 方法 | MCP 协议调用 | 返回值 |
|------|-------------|--------|
| `list_tools()` | `session.list_tools()` | `[{name, description}]` |
| `describe_tool(name)` | `session.list_tools()` 后过滤 | `{name, description, inputSchema}` |
| `call_tool(name, args)` | `session.call_tool(name, args)` | `response.content` |

`describe_tool` 不调用单独的 MCP 接口，而是从 list_tools 结果中匹配工具名并返回完整 inputSchema。这是因为 MCP 协议的 list_tools 响应已包含所有工具的完整 Schema。

### 可选依赖设计

```python
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
```

mcp 包通过 try/except 可选导入。如果未安装，`MCPExecutor.__init__` 抛出 `ImportError("mcp package required: pip install mcp")`。这种设计使得 SKILL.md 的其他部分（工具文档）在不安装 mcp 包时仍可被 AI 读取，只有实际执行工具时才需要依赖。

### CLI 入口

```bash
# 列出所有工具
python executor.py --list

# 查看 device_search 的参数 schema
python executor.py --describe device_search

# 搜索设备
python executor.py --call '{"tool": "device_search", "arguments": {"limit": 10, "keyword": "server"}}'
```

配置加载逻辑：先尝试 `mcpServers.awesun-mcp-server` 嵌套格式，回退到顶级格式。这兼容了标准 MCP 配置格式和简化格式。

## mcp-config.json 配置

配置文件定义了 MCP 服务器的连接参数：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `name` | `awesun-mcp-server` | 服务器名称 |
| `command` | macOS 路径 | MCP 服务器可执行文件路径 |
| `env.AWESUN_API_URL` | `http://127.0.0.1:8908` | 向日葵本地 API 地址 |
| `env.AWESUN_API_TOKEN` | 占位符 | MCP 服务认证令牌 |

### 跨平台配置

默认 command 是 macOS 路径。Windows 用户需要修改为向日葵安装目录下的 mcp-server 可执行文件路径。AWESUN_API_TOKEN 需要从向日葵客户端的 MCP 设置中获取。

## 安装与配置

### 安装路径

| AI 工具 | 全局安装 | 项目安装 |
|---------|---------|---------|
| Claude Code | `~/.claude/skills/awesun-remote-control/` | `.claude/skills/awesun-remote-control/` |
| OpenCode | `~/.opencode/skills/awesun-remote-control/` | `.opencode/skills/awesun-remote-control/` |

### 配置步骤

1. 安装 Python MCP 依赖：`pip install mcp`（或通过 package.json 的 setup 脚本自动安装）
2. 确保向日葵客户端 16.3.2+ 运行并启用 MCP 服务（Stdio 模式）
3. 复制 awesun-remote-control 目录到技能路径
4. 编辑 mcp-config.json，替换 command 路径和 AWESUN_API_TOKEN

### package.json

```json
{
  "name": "skill-awesun-remote-control",
  "version": "1.0.0",
  "description": "Claude Skill for awesun-remote-control MCP server",
  "scripts": {
    "setup": "pip install mcp"
  }
}
```

## 典型使用场景

### 远程运维自动化

AI 读取 SKILL.md 后，可按以下流程自主操作：
1. `device_search` 查找目标服务器
2. `control_connect` 建立 cmd2 会话
3. `control_command` 执行诊断命令（查看日志、重启服务）
4. `control_screenshot` 截图确认结果
5. `control_disconnect` 关闭会话

### 自动化 UI 测试

结合 awesun-ui-locator 技能：
1. `control_connect` 建立 desktop 会话
2. `control_screenshot` 获取远程屏幕截图
3. awesun-ui-locator 分析截图定位 UI 元素坐标
4. `desktop_click_mouse` 使用归一化坐标点击
5. 重复截图-定位-操作循环

## 与 MCP 直连的对比

awesun-skill 的桥接模式相比 AI 客户端直连 MCP 服务器的优势：

| 维度 | 直连 MCP | Skill 桥接 |
|------|---------|-----------|
| Token 消耗 | 22 工具全量 Schema 注入 | SKILL.md 按需加载 |
| 工具选择 | AI 自行解析 Schema | SKILL.md 提供分类和使用场景 |
| 兼容性 | 需客户端支持 MCP | 任何支持 Skills 的客户端 |
| 配置复杂度 | 客户端 MCP 配置 | 技能内 mcp-config.json |

代价是多了一层 executor.py 进程，但 Stdio 通信的延迟开销可以忽略。

## 相关概念

- [MCP 协议与工具集成](/concepts/04-mcp-protocol.md)
- [UI 定位器模式](/concepts/07-ui-locator-pattern.md)
- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
