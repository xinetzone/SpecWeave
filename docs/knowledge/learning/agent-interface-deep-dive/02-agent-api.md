---
id: "agent-api-chapter"
title: "Agent API：可调用方法层"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-interface-deep-dive/02-agent-api.toml"
source: "spec:agent-interface-deep-dive"
category: "learning"
tags: ["agent", "api", "json-rpc", "mcp", "a2a", "rest"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "Agent视角的API：JSON-RPC 2.0作为Agent API标准，MCP/ACP/A2A的API设计与调用案例"
---

# Agent API：可调用方法层

## 什么是Agent API？

**Agent API是Interface的具体可调用暴露方式**——Interface声明"能做什么"，API定义"怎么调用"。如果说Tool Interface是能力契约，API就是执行这个契约的具体方法端点。

Agent生态的API事实标准是**JSON-RPC 2.0**——它轻量、语言无关、天然支持请求响应模式，完美适配Agent工具调用场景。

> 💡 **基础概念回顾**：如果你对通用API设计（REST、GraphQL、SOAP、gRPC）不熟悉，请先阅读[通用Wiki - API章节](../interface-api-abi-protocol-wiki/02-api.md)。

## Agent API的核心特征

| 特征 | 说明 |
|------|------|
| **请求响应模型** | 所有API调用遵循标准请求→响应模式，支持同步和异步（SSE流式） |
| **方法名标识** | 通过字符串方法名（如`tools/call`）标识要调用的操作，而非HTTP路径 |
| **参数序列化** | 所有参数序列化为JSON，遵循Tool Interface定义的Schema |
| **结构化错误** | 统一错误码和错误消息格式，便于Agent Runtime处理异常 |
| **版本协商** | 通过initialize握手协商协议版本和能力支持 |

## Agent API的三种主要形态

### 1. MCP JSON-RPC API

MCP协议以JSON-RPC 2.0为基础定义了一套标准API方法：

| 方法分类 | 方法名 | 功能 |
|---------|--------|------|
| 生命周期 | `initialize` | 握手协商版本和能力 |
| Tool | `tools/list` | 获取所有Tool Interface列表 |
| Tool | `tools/call` | 调用指定Tool |
| Resource | `resources/list` / `resources/read` | 资源管理 |
| Prompt | `prompts/list` / `prompts/get` | 提示词模板管理 |

**案例1：MCP tools/call JSON-RPC请求响应**

```json
// → 请求：调用calculate工具
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "calculate",
    "arguments": {
      "expression": "2 + 3 * 4",
      "precision": 2
    }
  }
}

// ← 响应：计算结果
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "14.00"
      }
    ]
  }
}
```

错误响应示例：

```json
// ← 错误响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "reason": "expression must be a valid math expression"
    }
  }
}
```

### 2. ACP RESTful API

ACP（Agent Communication Protocol）采用更传统的RESTful API设计，用于本地Agent消息通信。

### 3. A2A Task API

A2A协议围绕Task生命周期设计API：

| 方法 | 功能 |
|------|------|
| `tasks/send` | 发送任务给另一个Agent |
| `tasks/get` | 查询任务状态和结果 |
| `tasks/cancel` | 取消运行中的任务 |
| `tasks/subscribe` | 通过SSE订阅任务更新 |

## 通过HTTP调用MCP Server

MCP支持STDIO和HTTP两种传输方式。使用HTTP传输时可以直接用curl/fetch调用：

**案例2：curl调用MCP Server over HTTP**

```bash
# 调用MCP Server的tools/call方法
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "calculate",
      "arguments": {
        "expression": "2 + 3 * 4"
      }
    }
  }'
```

TypeScript fetch调用示例：

```typescript
async function callMcpTool(
  serverUrl: string,
  toolName: string,
  args: Record<string, unknown>
) {
  const response = await fetch(`${serverUrl}/mcp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: { name: toolName, arguments: args }
    })
  });
  return response.json();
}
```

## Agent API vs 通用Web API

| 维度 | REST API | Agent JSON-RPC API |
|------|----------|-------------------|
| 操作标识 | HTTP方法 + URL路径 | 字符串方法名 |
| 发现方式 | OpenAPI/Swagger | `tools/list` 运行时发现 |
| 参数位置 | URL/Body/Query | 统一在`params`对象 |
| Schema约束 | 可选JSON Schema | 强制遵循Tool Interface Schema |
| 主要消费者 | 前端/其他服务 | LLM/Agent Runtime |

## 章节导航

| 章节 | 链接 |
|------|------|
| 总览 | [00 - 总览](00-overview.md) |
| 上一章 | [01 - Agent Interface](01-agent-interface.md) |
| 下一章 | [03 - Agent ABI](03-agent-abi.md) |
| 对比分析 | [05 - 对比分析](05-agent-comparison.md) |

---

**上一章**：[01 - Agent Interface：能力契约层](01-agent-interface.md) | **下一章**：[03 - Agent ABI：跨语言边界层](03-agent-abi.md)
