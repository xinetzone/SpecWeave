---
id: "analyze-omniroute-ai-gateway-07"
title: "MCP与A2A协议支持"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 7
created: "2026-07-09"
---

# MCP与A2A协议支持

## MCP(Model Context Protocol)服务器内置

OmniRoute内置MCP服务器，提供95个工具，覆盖30个scope，让MCP兼容客户端可以直接调用网关的管理功能。

## 三种传输方式

MCP服务器支持三种传输方式：stdio、HTTP、SSE，适应不同客户端的接入需求。

## 支持的客户端

兼容Claude Desktop、Cursor等所有MCP兼容客户端，客户端可以直接调用OmniRoute的管理功能。

## A2A(Agent-to-Agent)协议支持

OmniRoute支持A2A协议，实现AI代理之间的互操作。

## AI代理自管理能力

通过A2A协议，AI代理可以实现自管理：
- 路由切换
- 提供商切换
- 查询额度
- 调整压缩策略

## Claude Code集成

Claude Code可以通过 `mcp add-server` 命令接入OmniRoute的全套工具集，实现深度集成。
