---
type: Facts
title: "awesun-skill 事实清单"
---

# awesun-skill 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\awesun-skill\
> 采集日期：2026-08-23

## 项目概述

- F-001: 项目名称为"向日葵(Awesun) Skill"，基于向日葵 MCP 服务为支持 Skills 的 AI Agent 提供渐进式披露的工具调用 — 源码：`README.md:1-3`
- F-002: 支持的 AI 工具包括 Claude Code、Open Code、OpenClaw — 源码：`README.md:3`
- F-003: 依赖 Python 执行环境，建议版本 3.7 以上 — 源码：`README.md:7`
- F-004: 需要向日葵客户端 16.3.2 以上版本并启用 MCP 服务（Stdio 模式） — 源码：`README.md:11-13`
- F-005: Python MCP 依赖通过 `pip install mcp` 安装 — 源码：`README.md:24`

## SKILL.md 结构

- F-006: SKILL.md frontmatter 包含 name（awesun-remote-control）、description、version（1.0）三个字段 — 源码：`awesun-remote-control/SKILL.md:1-5`
- F-007: description 声明提供 22 个工具，关键词包括远程控制、设备管理、桌面控制、远程 CMD、远程电源管理 — 源码：`awesun-remote-control/SKILL.md:3`
- F-008: SKILL.md 按 Device、Control、Desktop 三类列出全部 22 个工具，每个工具包含功能描述、必填参数、可选参数 — 源码：`awesun-remote-control/SKILL.md:11-80`

## 工具清单（22 个）

- F-009: Device 类 7 个工具：device_add、device_info、device_remove、device_search、device_shutdown、device_update、device_wakeup — 源码：`awesun-remote-control/SKILL.md:13-42`
- F-010: Control 类 6 个工具：control_connect、control_disconnect、control_portforward、control_screenshot、control_sessions、control_command — 源码：`awesun-remote-control/SKILL.md:44-69`
- F-011: Desktop 类 9 个工具（SKILL.md 中列出 click、drag 等） — 源码：`awesun-remote-control/SKILL.md:71-80`
- F-012: control_connect 支持的远控类型包括 file、desktop、cmd2（Windows）、ssh（Linux/Mac）、desktop_view、newcamera、forward — 源码：`awesun-remote-control/SKILL.md:46-48`
- F-013: 桌面操作工具的坐标使用归一化值（0.0-1.0），通过 x_pixel/屏幕宽度计算 — 源码：`awesun-remote-control/SKILL.md:73`

## executor.py 执行器

- F-014: executor.py 是 MCP Skill 执行器，实现动态工具调用，文件头部声明为 "MCP Skill Executor - Dynamic tool invocation" — 源码：`awesun-remote-control/executor.py:1-2`
- F-015: 定义 MCPExecutor 类，通过 StdioServerParameters 和 stdio_client 连接 MCP 服务器 — 源码：`awesun-remote-control/executor.py:18,29-55`
- F-016: connect() 方法验证 server_config 包含必填的 command 和 env 字段，缺失时抛出 ValueError — 源码：`awesun-remote-control/executor.py:33-37`
- F-017: list_tools() 方法返回可用工具列表，每个工具包含 name 和 description — 源码：`awesun-remote-control/executor.py:57-69`
- F-018: describe_tool() 方法获取特定工具的详细 schema — 源码：`awesun-remote-control/executor.py:71-80`
- F-019: 使用 AsyncExitStack 管理 MCP 会话生命周期，连接后调用 session.initialize() — 源码：`awesun-remote-control/executor.py:45-55`
- F-020: mcp 包通过 try/except ImportError 可选导入，HAS_MCP 标志控制可用性 — 源码：`awesun-remote-control/executor.py:10-15`

## mcp-config.json 配置

- F-021: mcp-config.json 定义 MCP 服务器连接配置，包含 name、command、env 三个顶级字段 — 源码：`awesun-remote-control/mcp-config.json:1-8`
- F-022: 默认 command 为 macOS 路径 `/Applications/AweSun.app/Contents/Helpers/awesun-mcp-server` — 源码：`awesun-remote-control/mcp-config.json:3`
- F-023: env 包含 AWESUN_API_URL（默认 http://127.0.0.1:8908）和 AWESUN_API_TOKEN（占位符 your-mcp-server-token） — 源码：`awesun-remote-control/mcp-config.json:4-7`

## package.json

- F-024: package.json 名称为 skill-awesun-remote-control，版本 1.0.0 — 源码：`awesun-remote-control/package.json:2-3`
- F-025: 描述为 "Claude Skill for awesun-remote-control MCP server" — 源码：`awesun-remote-control/package.json:4`
- F-026: 定义 setup 脚本执行 `pip install mcp` — 源码：`awesun-remote-control/package.json:5-7`

## 安装方式

- F-027: Claude Code 安装：将 awesun-remote-control 目录复制到 ~/.claude/skills/（全局）或项目 .claude/skills/ — 源码：`README.md:54-63`
- F-028: OpenCode 安装：复制到 ~/.opencode/skills/（全局）或项目 .opencode/skills/ — 源码：`README.md:69-78`
- F-029: 配置步骤：编辑 mcp-config.json，替换 command 路径和 AWESUN_API_TOKEN — 源码：`README.md:43-47`
