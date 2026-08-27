---
type: Concept
title: MCP 协议与工具集成
description: Model Context Protocol 的工具协议范式，awesun-mcp 的 22 工具三类划分、Stdio/HTTP 双模式，以及 Skill 通过 MCPExecutor 桥接 MCP 的架构
tags: [agent-skills, mcp, protocol, tool-integration, awesun, stdio]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: awesun-mcp-source
    resource: "/references/awesun-mcp-source.md"
    title: awesun-mcp 源码
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
---

# MCP 协议与工具集成

MCP（Model Context Protocol）是 AI 与外部工具通信的开放协议。它定义了 AI 客户端如何发现工具、获取工具 Schema、调用工具并接收结果的标准化方式。本概念以 awesun-mcp（向日葵远程控制 MCP 服务器）和 awesun-skill（MCP 的 Skill 封装）为案例，解析 MCP 的工具集成范式及其与 Skill 知识包的协作架构。

## MCP 的核心抽象

MCP 将工具能力抽象为三个要素：

| 要素 | 说明 |
|------|------|
| **Tool** | 一个可调用的能力，有名称、描述和 JSON Schema 定义的输入参数 |
| **Server** | 暴露一组 Tool 的进程，通过 stdio 或 HTTP 与客户端通信 |
| **Client** | AI 助手侧，连接 Server、列出工具、调用工具 |

MCP 的工作流程：
1. 客户端启动/连接 Server
2. 客户端调用 `list_tools()` 获取所有工具的名称和描述
3. AI 根据工具描述决定调用哪个工具
4. 客户端调用 `call_tool(tool_name, arguments)` 执行
5. Server 返回结果内容

## awesun-mcp 的工具组织

awesun-mcp 将向日葵远程控制能力组织为 **22 个工具**，按功能分为三大类：

### 设备管理（7 个）

管理向日葵设备列表的 CRUD 操作：

| 工具 | 功能 | 必填参数 |
|------|------|---------|
| `device_add` | 添加设备到列表 | name |
| `device_search` | 模糊搜索设备 | limit（最大 100） |
| `device_info` | 查询设备完整信息 | remote_id |
| `device_update` | 修改设备名称/描述 | remote_id |
| `device_remove` | 移除设备 | remote_id |
| `device_wakeup` | 远程开机（需 WOL/开机棒） | remote_id |
| `device_shutdown` | 远程关机 | remote_id |

`device_search` 返回的设备对象包含 22 个字段，涵盖硬件配置（CPU、内存、硬盘、显卡）、网络信息（IP、MAC、局域网 IP）、系统版本和在线状态。`device_info` 额外返回 plugins 字段（支持的远控插件列表）。

### 远控会话（6 个）

管理远程控制会话的生命周期：

| 工具 | 功能 |
|------|------|
| `control_connect` | 发起远控连接，支持 file/desktop/cmd2/ssh/desktop_view/newcamera/forward 七种类型 |
| `control_sessions` | 查询所有活跃会话 |
| `control_disconnect` | 终止指定会话 |
| `control_command` | 在 CMD 会话中执行命令（Windows），返回退出码/stdout/stderr |
| `control_screenshot` | 桌面截图（Base64 编码），仅支持 desktop/desktop_view |
| `control_portforward` | 配置端口转发，仅支持 forward 类型 |

`control_connect` 的 `type` 参数是理解远控能力的关键：`file` 是远程文件管理，`desktop` 是完整远程桌面，`cmd2` 是 Windows 命令行，`ssh` 是 Linux/Mac 的 SSH，`desktop_view` 是仅观看模式，`newcamera` 是摄像头，`forward` 是端口转发。

### 桌面操作（9 个）

在已建立的远程桌面会话上模拟输入操作：

| 工具 | 功能 |
|------|------|
| `desktop_click_mouse` | 鼠标点击（left/right/middle，支持双击） |
| `desktop_move_mouse` | 移动光标 |
| `desktop_drag_mouse` | 鼠标拖拽（沿路径移动） |
| `desktop_scroll_mouse` | 滚轮滚动 |
| `desktop_press_keys` | 精确控制按键按下或释放 |
| `desktop_typing_keys` | 执行组合快捷键（如复制、粘贴、保存） |
| `desktop_typing_text` | 逐字符输入短文本 |
| `desktop_paste_text` | 通过剪贴板粘贴长文本（比逐字符更高效） |
| `desktop_waiting` | 在操作序列中插入暂停等待 |

桌面操作的坐标系统使用**归一化坐标**：所有坐标值在 0.0 到 1.0 之间，通过 `x_pixel / 屏幕宽度` 计算。左上角为 (0.0, 0.0)，右下角为 (1.0, 1.0)。这使得操作指令与屏幕分辨率无关——同一条点击指令在不同分辨率的远程桌面上都能定位到相对位置。

## 双模式通信

awesun-mcp 支持两种通信模式：

| 模式 | 传输方式 | 适用场景 | 延迟 |
|------|---------|---------|------|
| **Stdio** | 标准输入/输出（本地子进程） | AI 客户端与向日葵在同一台机器 | 低 |
| **HTTP** | HTTP 协议（网络请求） | AI 客户端远程访问向日葵 | 取决于网络 |

MCP 服务器内置于向日葵客户端（版本 16.2.3.28762+），无需额外安装服务端。在向日葵设置中一键启用后自动生成 MCP 配置。

## MCP 的 Token 成本问题

MCP 协议的设计带来一个工程问题：**工具 Schema 的全量注入**。当 AI 客户端连接 MCP 服务器时，`list_tools()` 返回所有工具的完整 JSON Schema，这些 Schema 会持续占用上下文窗口。

jira-skill 的 PRD 记录了真实数据：mcp-atlassian 的 ~25 个工具加载消耗 **8,000-12,000 Token/会话**。而 126 个调试会话的使用分析显示，5 个工具占 80% 使用量：

| 工具 | 使用占比 |
|------|---------|
| jira_add_worklog | 22.8% |
| jira_get_issue | 18.6% |
| jira_search | 10.7% |
| jira_update_issue | 8.1% |
| jira_create_issue | 7.3% |

这意味着大量 Token 被花在注入从未使用的工具 Schema 上。这一发现直接推动了 jira-skill 从 MCP 向脚本架构的迁移。

## Skill 桥接 MCP：MCPExecutor

awesun-skill 展示了另一种路径：不放弃 MCP，而是用 Skill 知识包封装 MCP 工具，通过渐进式披露降低 Token 消耗。

### 架构

```text
AI Agent
  │
  ├── 读取 SKILL.md（第二层：22 个工具的功能描述和参数摘要）
  │
  ├── 决定调用工具
  │
  └── 调用 executor.py --call '<json>'
        │
        └── MCPExecutor
              ├── 读取 mcp-config.json（command + env）
              ├── StdioServerParameters 建立 stdio 连接
              ├── stdio_client 传输
              ├── ClientSession 会话管理
              └── session.call_tool(tool_name, arguments)
                    │
                    └── awesun-mcp-server（向日葵客户端内置）
```

### MCPExecutor 类

`executor.py` 中的 `MCPExecutor` 类是桥接核心：

| 方法 | 功能 |
|------|------|
| `__init__(server_config)` | 初始化，检查 mcp 包是否安装（HAS_MCP 标志） |
| `connect()` | 验证配置含 command 和 env，创建 StdioServerParameters，通过 AsyncExitStack 建立 stdio_client + ClientSession，调用 session.initialize() |
| `list_tools()` | 返回 `[{name, description}]` 列表 |
| `describe_tool(tool_name)` | 返回特定工具的完整 inputSchema |
| `call_tool(tool_name, arguments)` | 执行工具调用，返回 response.content |
| `close()` | 通过 AsyncExitStack.aclose() 清理资源 |

关键设计：
- **AsyncExitStack 管理生命周期**：确保 stdio 传输和 ClientSession 在连接关闭时正确清理。
- **可选导入**：mcp 包通过 try/except ImportError 导入，HAS_MCP 标志控制可用性，缺失时给出明确安装提示。
- **配置验证**：connect() 检查 server_config 包含必填的 command 和 env 字段，缺失时抛出 ValueError。

### mcp-config.json

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

`command` 是 MCP 服务器可执行文件路径（默认 macOS 路径，Windows 需修改为向日葵安装目录下的对应路径）。`env` 配置向日葵本地 API 地址和认证 Token。

### CLI 接口

executor.py 提供三种调用方式：

```bash
# 列出所有工具
python executor.py --list

# 查看特定工具的 schema
python executor.py --describe device_search

# 调用工具
python executor.py --call '{"tool": "device_search", "arguments": {"limit": 10}}'
```

## MCP vs Skill 脚本：选择指南

| 维度 | MCP 服务器 | Skill 脚本 |
|------|-----------|-----------|
| 工具发现 | 自动（list_tools） | 手动（SKILL.md 描述） |
| Token 消耗 | 高（全量 Schema 注入） | 低（渐进式披露） |
| 跨客户端通用 | 是（协议标准） | 取决于 Skill 标准兼容性 |
| 延迟 | 服务器启动+协议握手 | 直接进程调用 |
| 部署复杂度 | 需运行 MCP 服务器 | uv run 直接执行（PEP 723） |
| 适合场景 | 工具多、参数复杂、需多客户端共享 | 高频工具集中、追求低延迟 |

awesun-skill 的混合模式（MCP 服务器 + Skill 封装）在通用性和 Token 效率之间取得了平衡：MCP 负责底层通信，Skill 负责知识组织和按需加载。

## 安全机制

awesun-mcp 的安全基于向日葵成熟的远控安全体系：
- 设备验证码或已信任设备才能建立连接
- MCP 服务通过 AWESUN_API_TOKEN 认证
- 本地 API 默认仅监听 127.0.0.1:8908（Stdio 模式下无网络暴露）
- HTTP 模式需额外配置网络安全策略

## 相关概念

- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [Awesun 远程控制 Skill 实战](/concepts/06-awesun-remote-control.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
- [AI Agent Skills 生态概览](/concepts/00-overview.md)
