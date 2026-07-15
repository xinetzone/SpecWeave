---
version: "1.0"
source: "../agent-communication-protocols-wiki.md#07-技术实现要点与代码示例"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols/07-implementation.toml"
id: "implementation-guide"
title: "07、技术实现要点与代码示例"
---
# 07、技术实现要点与代码示例

## 7.1 本章导读

本章是面向开发者的实践指南，提供可直接参考的代码示例和API调用范式。通过本章，你将掌握：

- 各协议的Agent Card/元数据格式规范
- MCP/A2A/ACP的核心消息格式和调用示例
- 使用curl直接与协议端点交互的方法
- Python/TypeScript SDK的极简示例
- 消息结构的详细说明与多模态示例
- 安全认证配置要点
- 常见集成陷阱与最佳实践

> 注：SDK示例基于各协议官方文档编写，API可能随版本演进，请参考官方文档获取最新API。部分示例使用伪代码标注概念模式。

## 7.2 Agent Card格式详解

Agent Card是Agent能力描述的核心元数据，不同协议有不同的实现方式。

### 7.2.1 A2A Agent Card

A2A通过标准Well-Known URI发布Agent Card：`/.well-known/agent.json`

**完整字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | Agent唯一标识名称 |
| `description` | string | 是 | 人类可读的功能描述 |
| `url` | string | 是 | A2A服务端点URL |
| `version` | string | 是 | Agent语义化版本号 |
| `capabilities` | object | 是 | 支持的协议特性 |
| `capabilities.streaming` | boolean | 否 | 是否支持SSE流式 |
| `capabilities.pushNotifications` | boolean | 否 | 是否支持Webhook推送 |
| `capabilities.stateTransitionHistory` | boolean | 否 | 是否返回状态变更历史 |
| `skills` | array | 是 | Agent具备的技能列表 |
| `skills[].id` | string | 是 | 技能唯一ID |
| `skills[].name` | string | 是 | 技能显示名称 |
| `skills[].description` | string | 是 | 技能详细描述 |
| `skills[].inputModes` | array | 否 | 支持的输入模态 |
| `skills[].outputModes` | array | 否 | 支持的输出模态 |
| `authentication` | object | 否 | 认证方式配置 |
| `defaultInputModes` | array | 否 | 默认输入模态 |
| `defaultOutputModes` | array | 否 | 默认输出模态 |
| `organization` | string | 否 | 所属组织 |
| `contactUrl` | string | 否 | 联系信息URL |

**完整JSON示例：**

```json
{
  "name": "expense-report-agent",
  "description": "企业报销处理Agent，支持报销单提交、发票识别、审批流程跟踪",
  "url": "https://api.example.com/a2a/expense",
  "version": "2.1.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "skills": [
    {
      "id": "submit-expense",
      "name": "提交报销单",
      "description": "上传发票图片和报销信息，提交报销申请",
      "inputModes": ["text", "image"],
      "outputModes": ["text", "json"]
    },
    {
      "id": "query-status",
      "name": "查询报销状态",
      "description": "根据报销单号查询当前审批状态和进度",
      "inputModes": ["text"],
      "outputModes": ["text", "json"]
    },
    {
      "id": "upload-receipt",
      "name": "上传发票凭证",
      "description": "支持批量上传发票图片，自动OCR识别金额和日期",
      "inputModes": ["image"],
      "outputModes": ["json"]
    }
  ],
  "authentication": {
    "schemes": ["oauth2"],
    "oauth2": {
      "authorizationUrl": "https://auth.example.com/authorize",
      "tokenUrl": "https://auth.example.com/token",
      "scopes": ["expense:read", "expense:write", "receipt:upload"]
    }
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "organization": "Example Financial Services",
  "contactUrl": "https://example.com/support/expense-agent"
}
```

### 7.2.2 ACP Agent Cards/元数据格式

ACP的Agent Card设计更轻量，支持静态分发和离线发现。

**核心特点：**

- 更简洁的字段结构
- 支持mDNS本地广播发现
- 可静态打包到Docker镜像、K8s配置中
- Agent未运行时也能被发现（离线发现）
- 支持多种传输端点声明

**ACP Agent Card示例：**

```json
{
  "name": "image-processor",
  "version": "1.0.0",
  "description": "图像处理Agent，支持缩放、裁剪、格式转换、滤镜",
  "endpoints": {
    "rest": "http://localhost:8081",
    "grpc": "localhost:8082"
  },
  "capabilities": ["resize", "crop", "convert", "filter", "ocr"],
  "inputTypes": ["image/png", "image/jpeg", "image/webp"],
  "outputTypes": ["image/png", "image/jpeg", "image/webp", "application/json"],
  "mdnsServiceType": "_acp-agent._tcp.local.",
  "authentication": {
    "type": "did"
  }
}
```

### 7.2.3 A2A与ACP Agent Card对比

| 对比维度 | A2A Agent Card | ACP Agent Card |
|---------|---------------|---------------|
| 发布方式 | `/.well-known/agent.json` HTTP端点 | HTTP端点/mDNS广播/静态文件 |
| 发现时机 | 需要Agent运行中 | 支持离线发现（未运行时） |
| 字段复杂度 | 丰富（capabilities/skills/authentication等） | 简洁（capabilities/endpoints） |
| 技能描述 | 结构化skills数组，含inputModes/outputModes | 简单capabilities字符串数组 |
| 认证配置 | 完整OAuth2端点配置 | 轻量类型声明 |
| 多传输支持 | 仅HTTP/HTTPS | REST/gRPC/ZeroMQ/IPC多端点 |
| 网络范围 | 公网/跨域 | 本地子网/内网 |
| 典型大小 | 1-3KB | 200-500B |

## 7.3 MCP实现示例

MCP基于JSON-RPC 2.0，消息格式简单清晰。

### 7.3.1 MCP JSON-RPC消息格式回顾

MCP使用标准JSON-RPC 2.0消息结构：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id-123",
  "method": "method-name",
  "params": {}
}
```

响应格式：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id-123",
  "result": {}
}
```

错误响应格式：

```json
{
  "jsonrpc": "2.0",
  "id": "request-id-123",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {}
  }
}
```

### 7.3.2 工具注册（tools/list响应）

Client调用`tools/list`获取Server提供的所有工具：

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-tools-list",
  "method": "tools/list",
  "params": {}
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-tools-list",
  "result": {
    "tools": [
      {
        "name": "read_file",
        "description": "读取文件内容，返回文本字符串",
        "inputSchema": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "文件的绝对路径"
            }
          },
          "required": ["path"]
        }
      },
      {
        "name": "write_file",
        "description": "写入内容到文件，覆盖现有内容",
        "inputSchema": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "文件的绝对路径"
            },
            "content": {
              "type": "string",
              "description": "要写入的内容"
            }
          },
          "required": ["path", "content"]
        }
      },
      {
        "name": "list_directory",
        "description": "列出目录下的文件和子目录",
        "inputSchema": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "目录的绝对路径"
            }
          },
          "required": ["path"]
        }
      }
    ]
  }
}
```

### 7.3.3 工具调用（tools/call）

#### 同步调用示例

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-call-add",
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 123.45,
      "b": 678.90
    }
  }
}
```

**响应（成功）：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-call-add",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "802.35"
      }
    ],
    "isError": false
  }
}
```

**响应（错误）：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-call-divide",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: Division by zero"
      }
    ],
    "isError": true
  }
}
```

#### 流式调用示例（通过notifications）

MCP流式响应通过Notification消息推送进度：

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "token-123",
    "progress": 45,
    "total": 100,
    "message": "Processing chunk 45/100..."
  }
}
```

最终完成时发送标准Response。

### 7.3.4 资源读取（resources/read）

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-read-resource",
  "method": "resources/read",
  "params": {
    "uri": "file:///home/user/projects/README.md"
  }
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-read-resource",
  "result": {
    "contents": [
      {
        "uri": "file:///home/user/projects/README.md",
        "mimeType": "text/markdown",
        "text": "# My Project\n\nThis is a sample project README file.\n\n## Installation\n\nRun `npm install` to install dependencies."
      }
    ]
  }
}
```

### 7.3.5 curl调用MCP Server示例

#### stdio模式说明

stdio模式下MCP Server作为子进程运行，通过stdin/stdout通信，无法直接用curl调用。Client（如Claude Desktop）启动Server子进程，通过管道传递JSON-RPC消息。

启动stdio MCP Server的典型配置（如Claude Desktop配置）：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    }
  }
}
```

#### HTTP模式curl命令

对于Streamable HTTP或SSE模式的MCP Server，可以直接用curl调用：

```bash
# 初始化连接
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "init-1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }'

# 调用工具
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "call-1",
    "method": "tools/call",
    "params": {
      "name": "list_directory",
      "arguments": {
        "path": "/home/user/documents"
      }
    }
  }'

# 列出工具
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "list-tools",
    "method": "tools/list",
    "params": {}
  }'
```

### 7.3.6 Python SDK极简示例

使用官方MCP Python SDK（内置FastMCP）创建MCP Server：

**环境要求**：Python >= 3.10

**安装依赖**：

```bash
pip install mcp>=1.26.0
```

> 注：以下示例基于MCP官方Python SDK（[GitHub](https://github.com/modelcontextprotocol/python-sdk)），FastMCP 1.0已整合进官方SDK。具体API请参考[官方文档](https://modelcontextprotocol.io/)获取最新版本。

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator", version="1.0.0")

@mcp.tool()
def add(a: float, b: float) -> float:
    """计算两个数的和"""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """计算两个数的乘积"""
    return a * b

@mcp.resource("config://app/settings")
def get_settings() -> str:
    """获取应用配置"""
    return '{"theme": "dark", "language": "zh-CN"}'

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 7.3.7 TypeScript SDK极简示例

使用官方MCP TypeScript SDK注册工具：

**安装依赖**：

```bash
npm install @modelcontextprotocol/sdk
```

> 注：以下示例基于MCP官方TypeScript SDK（[GitHub](https://github.com/modelcontextprotocol/typescript-sdk)）。具体API请参考[官方文档](https://modelcontextprotocol.io/)获取最新版本。

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "weather-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_weather",
      description: "获取指定城市的天气信息",
      inputSchema: {
        type: "object",
        properties: {
          city: { type: "string", description: "城市名称" }
        },
        required: ["city"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_weather") {
    const city = request.params.arguments?.city as string;
    return {
      content: [{
        type: "text",
        text: `${city}：晴，25°C，湿度60%`
      }]
    };
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
```

## 7.4 A2A实现示例

A2A基于JSON-RPC 2.0 over HTTP，原生支持SSE流式和Webhook推送。

### 7.4.1 tasks/send任务提交

发送消息并等待任务完成（同步模式）：

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-send-001",
  "method": "tasks/send",
  "params": {
    "id": "task-expense-2025-001",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "查询报销单EXP-2025-12345的审批状态"
        }
      ]
    },
    "configuration": {
      "acceptedOutputModes": ["text", "json"]
    }
  }
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-send-001",
  "result": {
    "id": "task-expense-2025-001",
    "status": {
      "state": "completed"
    },
    "history": [
      {
        "role": "user",
        "parts": [{"type": "text", "text": "查询报销单EXP-2025-12345的审批状态"}]
      },
      {
        "role": "agent",
        "parts": [{"type": "text", "text": "已为您查询到报销单状态："}]
      }
    ],
    "artifacts": [
      {
        "name": "报销单状态详情",
        "description": "EXP-2025-12345的完整审批流程信息",
        "parts": [
          {
            "type": "data",
            "data": {
              "expenseId": "EXP-2025-12345",
              "amount": 2580.00,
              "status": "approved",
              "currentApprover": "财务部门",
              "submittedAt": "2025-03-10T09:30:00Z",
              "approvedAt": "2025-03-12T14:20:00Z"
            }
          }
        ]
      }
    ]
  }
}
```

### 7.4.2 tasks/get状态查询

查询任务当前状态：

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-get-001",
  "method": "tasks/get",
  "params": {
    "id": "task-expense-2025-001"
  }
}
```

**响应（任务进行中）：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-get-001",
  "result": {
    "id": "task-expense-2025-001",
    "status": {
      "state": "working",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "正在识别发票信息，已完成3/5张..."
          }
        ]
      }
    },
    "history": [],
    "artifacts": []
  }
}
```

**Task状态字段说明：**

| 状态值 | 说明 |
|--------|------|
| `submitted` | 任务已提交，等待Agent接受 |
| `working` | 任务执行中 |
| `input-required` | 需要用户补充信息 |
| `completed` | 任务成功完成 |
| `failed` | 任务执行失败 |
| `canceled` | 任务被取消 |
| `rejected` | Agent拒绝接受任务 |
| `unknown` | 状态未知 |

### 7.4.3 SSE流式消息格式

A2A使用标准`text/event-stream`格式推送实时更新：

```
event: message
data: {"jsonrpc":"2.0","method":"tasks/status","params":{"id":"task-001","status":{"state":"submitted"}}}

event: message
data: {"jsonrpc":"2.0","method":"tasks/status","params":{"id":"task-001","status":{"state":"working"}}}

event: message
data: {"jsonrpc":"2.0","method":"tasks/message","params":{"id":"task-001","message":{"role":"agent","parts":[{"type":"text","text":"正在查询数据库..."}]}}}

event: message
data: {"jsonrpc":"2.0","method":"tasks/artifact","params":{"id":"task-001","artifact":{"name":"初步结果","parts":[{"type":"text","text":"找到3条相关记录"}]}}}

event: task-update
data: {"jsonrpc":"2.0","method":"tasks/status","params":{"id":"task-001","status":{"state":"completed"},"final":true}}
```

### 7.4.4 tasks/sendSubscribe流式请求

开启SSE流式订阅任务更新：

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-subscribe-001",
  "method": "tasks/sendSubscribe",
  "params": {
    "id": "task-long-001",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "生成Q1季度财务分析报告，包含图表和趋势分析"
        }
      ]
    },
    "configuration": {
      "acceptedOutputModes": ["text", "json", "image"]
    }
  }
}
```

请求发送后，Server保持HTTP连接打开，通过SSE持续推送事件，直到任务完成。

### 7.4.5 curl调用A2A Agent完整示例

```bash
# 1. 首先获取Agent Card发现能力
curl https://api.example.com/.well-known/agent.json

# 2. （如果需要OAuth认证，先获取token）
# TOKEN=$(获取OAuth2 Access Token的流程)

# 3. 发送同步任务
curl -X POST https://api.example.com/a2a \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": "curl-001",
    "method": "tasks/send",
    "params": {
      "id": "task-curl-demo-001",
      "message": {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "你好，请介绍一下你能做什么"
          }
        ]
      }
    }
  }'

# 4. 查询任务状态
curl -X POST https://api.example.com/a2a \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": "curl-get-001",
    "method": "tasks/get",
    "params": {
      "id": "task-curl-demo-001"
    }
  }'
```

### 7.4.6 Python SDK最小可运行示例

**环境要求**：Python >= 3.10

**安装依赖**：

```bash
pip install a2a-sdk
```

> 注：以下示例基于A2A官方Python SDK（[GitHub](https://github.com/google/a2a-python)），为便于理解采用简化伪代码风格。实际SDK使用 `AgentExecutor` 抽象类实现Agent逻辑，具体API请参考[官方示例](https://github.com/google/a2a-python/tree/main/examples)。

**Server端（伪代码示意）：**

```python
from a2a.server import A2AServer, AgentCard, Skill
from a2a.types import Message, TextPart, Task, TaskStatus

agent_card = AgentCard(
    name="echo-agent",
    description="简单的回显Agent，返回用户发送的消息",
    url="http://localhost:8000/a2a",
    version="1.0.0",
    skills=[
        Skill(
            id="echo",
            name="回显",
            description="返回用户发送的消息",
            input_modes=["text"],
            output_modes=["text"]
        )
    ]
)

app = A2AServer(agent_card=agent_card)

@app.task_handler
async def handle_task(task: Task) -> Task:
    user_message = task.history[-1]
    user_text = next(
        part.text for part in user_message.parts 
        if part.type == "text"
    )
    
    response_text = f"收到消息：{user_text}\n（这是回显Agent的响应）"
    
    task.status = TaskStatus(state="completed")
    task.history.append(Message(
        role="agent",
        parts=[TextPart(text=response_text)]
    ))
    return task

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

**Client端调用：**

```python
import asyncio
from a2a.client import A2AClient

async def main():
    client = A2AClient(url="http://localhost:8000/a2a")
    
    task = await client.send_message(
        message="你好，A2A！",
        task_id="client-test-001"
    )
    
    print(f"Task ID: {task.id}")
    print(f"Status: {task.status.state}")
    
    for msg in task.history:
        role = msg.role
        for part in msg.parts:
            if part.type == "text":
                print(f"[{role}]: {part.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 7.4.7 Webhook推送通知配置示例

创建任务时指定Webhook回调URL，Server在状态变更时主动推送：

**创建任务请求（含webhookUrl）：**

```json
{
  "jsonrpc": "2.0",
  "id": "req-webhook-001",
  "method": "tasks/create",
  "params": {
    "id": "task-async-001",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "处理这份大型数据集并生成报告"}]
    },
    "webhookUrl": "https://your-service.com/webhooks/a2a-notifications",
    "configuration": {
      "acceptedOutputModes": ["json"]
    }
  }
}
```

**Webhook回调请求（Server发送到Client）：**

```json
{
  "taskId": "task-async-001",
  "status": {
    "state": "completed"
  },
  "eventType": "task.completed",
  "timestamp": "2025-03-15T10:30:00Z",
  "artifactCount": 1
}
```

Client端收到Webhook后，可以调用`tasks/get`获取完整结果。

## 7.5 ACP实现示例

ACP采用REST原生设计，零SDK依赖，用任何HTTP客户端都能直接交互。

### 7.5.1 POST /tasks任务创建

**请求：**

```http
POST /tasks HTTP/1.1
Host: localhost:8081
Content-Type: application/json
```

```json
{
  "taskId": "task-resize-img-001",
  "operation": "resize",
  "input": {
    "width": 1024,
    "height": 768,
    "maintainAspectRatio": true,
    "sourceImageUrl": "https://example.com/images/photo.jpg",
    "outputFormat": "webp"
  },
  "priority": "normal",
  "callbackUrl": "http://localhost:8082/callbacks/image-processed"
}
```

**响应：**

```json
{
  "taskId": "task-resize-img-001",
  "status": "created",
  "createdAt": "2025-03-15T10:30:00Z",
  "estimatedDuration": 3,
  "_links": {
    "self": "/tasks/task-resize-img-001",
    "cancel": "/tasks/task-resize-img-001"
  }
}
```

### 7.5.2 任务状态轮询（GET /tasks/{id}）

**请求：**

```http
GET /tasks/task-resize-img-001 HTTP/1.1
Host: localhost:8081
```

**响应（执行中）：**

```json
{
  "taskId": "task-resize-img-001",
  "status": "running",
  "createdAt": "2025-03-15T10:30:00Z",
  "progress": 65,
  "message": "正在应用滤镜..."
}
```

**响应（已完成）：**

```json
{
  "taskId": "task-resize-img-001",
  "status": "completed",
  "createdAt": "2025-03-15T10:30:00Z",
  "completedAt": "2025-03-15T10:30:02Z",
  "output": {
    "resultUrl": "http://localhost:8081/results/task-resize-img-001/resized.webp",
    "format": "image/webp",
    "width": 1024,
    "height": 768,
    "size": 128456
  }
}
```

**ACP任务状态：**

| 状态 | 说明 |
|------|------|
| `created` | 任务已创建，等待执行 |
| `running` | 任务执行中 |
| `completed` | 任务成功完成 |
| `failed` | 任务执行失败 |

### 7.5.3 curl直接调用ACP Agent示例

ACP的零SDK特性让curl调用异常简洁：

```bash
# 1. 获取Agent能力卡片
curl http://localhost:8081/agent-card

# 2. 创建图像处理任务
curl -X POST http://localhost:8081/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "resize",
    "input": {
      "width": 1024,
      "height": 768,
      "sourceImageUrl": "https://picsum.photos/2048/1536"
    }
  }'

# 3. 轮询任务状态（假设返回taskId为task-uuid-123）
curl http://localhost:8081/tasks/task-uuid-123

# 4. 列出所有任务
curl http://localhost:8081/tasks

# 5. 获取Agent健康状态（如果支持）
curl http://localhost:8081/health
```

### 7.5.4 mDNS发现说明（概念级）

ACP使用mDNS（组播DNS）实现零配置局域网发现，概念流程如下：

1. **Agent启动时**：通过mDNS广播服务，服务类型通常为`_acp-agent._tcp.local.`
2. **广播内容**：包含Agent名称、IP地址、端口、版本等信息
3. **客户端发现**：客户端发送mDNS查询请求，监听局域网内的服务广播
4. **服务列表**：收集到所有可用Agent的地址和能力信息
5. **离线检测**：Agent停止时发送mDNS goodbye包，自动从发现列表移除

mDNS类似AirPrint发现打印机、Chromecast发现电视的体验，完全零配置，无需DNS服务器。

### 7.5.5 多MIME类型消息示例

#### 纯文本消息

```bash
curl -X POST http://localhost:8081/messages \
  -H "Content-Type: text/plain" \
  -d "你好，请问能处理PNG格式图片吗？"
```

#### JSON结构化数据

```bash
curl -X POST http://localhost:8081/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "analyze",
    "parameters": {
      "detectObjects": true,
      "confidence": 0.8
    }
  }'
```

#### 二进制文件上传（使用multipart/form-data）

```bash
curl -X POST http://localhost:8081/tasks \
  -F "operation=ocr" \
  -F "language=zh-CN" \
  -F "file=@./document.pdf;type=application/pdf"
```

## 7.6 消息结构详解

A2A定义了标准的消息结构，MCP/ACP在各自场景下使用类似概念。

### 7.6.1 Message统一格式

Message是对话交互的基本单元：

```json
{
  "role": "user",
  "parts": [],
  "metadata": {},
  "messageId": "msg-001"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `role` | string | 是 | 消息发送方角色：`user`或`agent` |
| `parts` | array | 是 | 消息内容组成部分数组 |
| `metadata` | object | 否 | 自定义元数据，用于扩展 |
| `messageId` | string | 否 | 消息唯一标识符 |

### 7.6.2 Part三种类型对比

Part是Message的内容单元，支持三种基础类型，可混合使用。

| 类型 | 字段 | 用途 | 适用场景 |
|------|------|------|---------|
| **TextPart** | `type: "text"`, `text: string` | 纯文本内容 | 对话、说明、代码、普通文本 |
| **DataPart** | `type: "data"`, `data: object` | 结构化JSON数据 | 结构化结果、参数、配置、数据记录 |
| **FilePart** | `type: "file"`, `mimeType: string`, `bytes?: string`, `uri?: string`, `name?: string` | 文件内容（二进制） | 图片、文档、音频、视频、任意二进制文件 |

#### TextPart示例

```json
{
  "type": "text",
  "text": "分析结果显示，本季度销售额同比增长15%，主要来自华东区域。"
}
```

#### DataPart示例

```json
{
  "type": "data",
  "data": {
    "quarter": "Q1-2025",
    "totalRevenue": 12500000,
    "growthRate": 0.15,
    "regions": {
      "east": 5200000,
      "south": 3100000,
      "north": 2800000,
      "west": 1400000
    },
    "topProducts": ["产品A", "产品B", "产品C"]
  }
}
```

#### FilePart示例（Base64内嵌，小文件）

```json
{
  "type": "file",
  "name": "小图标.png",
  "mimeType": "image/png",
  "bytes": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
}
```

#### FilePart示例（URI引用，大文件推荐）

```json
{
  "type": "file",
  "name": "完整报告.pdf",
  "mimeType": "application/pdf",
  "uri": "https://example.com/reports/q1-2025-analysis.pdf"
}
```

### 7.6.3 Artifact结构

Artifact是Task产出的结果工件，结构与Message类似但附加了语义标识：

```json
{
  "name": "Q1季度销售分析报告",
  "description": "包含详细数据分析、趋势图表、区域对比的完整报告",
  "parts": [],
  "metadata": {
    "pageCount": 15,
    "generatedAt": "2025-03-15T10:30:00Z"
  },
  "artifactId": "artifact-001"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 产物名称 |
| `description` | string | 否 | 产物详细描述 |
| `parts` | array | 是 | 产物内容（与Message parts结构相同） |
| `metadata` | object | 否 | 自定义元数据 |
| `artifactId` | string | 否 | 产物唯一ID |

**Artifact与Message的关系：**

- Message：对话过程中的消息，代表交互过程中的话语
- Artifact：任务完成时的产出物，代表最终结果或中间产物
- 一个Task可以有多个Artifact（如报告文档+图表+原始数据）
- Artifact使用与Message相同的Part类型系统，支持多模态内容

### 7.6.4 完整多模态消息JSON示例

以下是一个包含文本说明和图像FilePart的完整多模态消息示例（使用URI引用方式避免大段base64）：

```json
{
  "role": "user",
  "messageId": "msg-multimodal-001",
  "metadata": {
    "sentAt": "2025-03-15T14:22:00Z",
    "clientVersion": "1.2.0"
  },
  "parts": [
    {
      "type": "text",
      "text": "请识别这张发票图片中的金额、日期和商家名称，然后将信息以JSON格式返回。"
    },
    {
      "type": "file",
      "name": "餐饮发票.jpg",
      "mimeType": "image/jpeg",
      "uri": "https://example.com/uploads/receipt-2025-03-15.jpg"
    },
    {
      "type": "data",
      "data": {
        "requestId": "req-ocr-001",
        "priority": "high",
        "returnFields": ["amount", "date", "merchant", "items"]
      }
    }
  ]
}
```

## 7.7 安全认证配置要点

### 7.7.1 MCP OAuth 2.1配置流程概述

MCP远程部署（HTTP/SSE模式）强制使用OAuth 2.1认证，配置流程概述：

1. **注册MCP Server**：在身份提供商（IdP）注册Server，获取client_id和client_secret
2. **配置Agent Card/发现文档**：在Server能力声明中包含OAuth授权端点和token端点
3. **Client发现认证要求**：Client通过initialize或发现文档获取OAuth配置
4. **Authorization Code Flow + PKCE**：Client启动OAuth授权流程，用户在浏览器中登录授权
5. **获取Access Token**：授权通过后，Client获取短期Access Token和Refresh Token
6. **请求携带Token**：后续JSON-RPC请求在Authorization Header中携带Bearer Token
7. **Token刷新**：Access Token过期时使用Refresh Token自动刷新

> 注：stdio模式下MCP运行在本地进程中，不需要OAuth认证。

### 7.7.2 A2A OAuth2 Bearer Token认证示例

A2A推荐使用OAuth 2.0 Bearer Token认证，Token通过标准HTTP Header传递：

```bash
curl -X POST https://api.example.com/a2a \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "jsonrpc": "2.0",
    "id": "auth-test-001",
    "method": "tasks/send",
    "params": {
      "id": "task-auth-001",
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "查询我的账户信息"}]
      }
    }
  }'
```

**API Key认证（简单集成/测试场景）：**

```bash
curl -X POST https://api.example.com/a2a \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-abcdef1234567890" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tasks/send",...}'
```

### 7.7.3 ACP DID认证概念说明

ACP支持W3C DID（Decentralized Identifier，去中心化标识符）作为Agent身份标识，适用于本地/内网去中心化场景：

- **自主身份**：Agent可本地生成DID，无需向中央CA申请
- **DID Document**：每个DID对应一个DID Document，包含公钥、服务端点等信息
- **可验证凭证**：使用DID私钥签名消息，接收方用公钥验证签名
- **本地信任网络**：在信任边界内（如企业内网），可通过预共享DID建立信任
- **轻量级**：相比OAuth的完整流程，DID认证更适合本地低延迟场景

> 注：DID认证是概念性功能，具体实现请参考ACP最新规范和W3C DID标准。

### 7.7.4 API Key认证通用模式

API Key是最简单的认证方式，适用于内部服务、测试环境、简单集成场景：

| 传递方式 | Header示例 | 适用场景 |
|---------|-----------|---------|
| Authorization Header | `Authorization: Bearer <key>` | 通用，推荐 |
| 自定义Header | `X-API-Key: <key>` | 常见模式 |
| 查询参数 | `?api_key=<key>` | 不推荐（会记录在日志中） |

**安全最佳实践：**

- API Key应使用足够的随机熵（≥32字节）
- 不同环境使用不同的Key（开发/测试/生产隔离）
- 定期轮换Key，设置过期时间
- 服务端记录Key使用日志，监控异常使用
- 不要将Key提交到代码仓库，使用环境变量或密钥管理服务

### 7.7.5 TLS/HTTPS传输安全要求

| 协议 | 传输安全要求 |
|------|-------------|
| **MCP stdio** | 本地进程通信，天然安全，无需TLS |
| **MCP HTTP/SSE** | 生产环境强制HTTPS/TLS 1.2+ |
| **A2A** | 强制HTTPS/TLS 1.2+，跨网场景建议TLS 1.3 |
| **ACP本地** | 本地/IPC通信无需TLS；内网HTTP可选TLS |
| **ACP跨网** | 跨不可信网络时强制HTTPS |

**TLS配置最佳实践：**

- 使用TLS 1.2或更高版本，禁用SSLv3/TLS 1.0/1.1
- 使用强密码套件，禁用弱加密算法
- 证书由受信任CA签发（生产环境），内网可使用内部CA
- 启用HSTS（HTTP Strict Transport Security）防止降级攻击
- 定期更新证书和密钥

## 7.8 常见集成陷阱与最佳实践

### 7.8.1 陷阱1：混淆MCP和A2A的职责

**典型错误：**

- 尝试用MCP连接两个Agent进行跨Agent协作
- 尝试用A2A调用数据库、文件系统等工具
- 在MCP Server中实现复杂的Agent自主决策逻辑

**正确理解：**

| 协议 | 正确用途 | 错误用法 |
|------|---------|---------|
| **MCP** | Agent连接工具/数据库/API（纵向） | Agent↔Agent通信 |
| **A2A** | 跨厂商/跨组织Agent协作（横向跨域） | 连接本地工具、短平快函数调用 |
| **ACP** | 本地/内网Agent低延迟通信（横向本地） | 跨公网、跨组织服务调用 |

**记忆口诀：**
- 连工具 → MCP
- 连本地Agent → ACP
- 连外部Agent → A2A

### 7.8.2 陷阱2：忽视长任务状态管理

**典型问题：**

- SSE连接断开后没有重连机制，导致任务状态丢失
- 长任务只使用同步请求/响应模式，导致HTTP超时
- 没有处理`input-required`状态，任务卡住无响应
- 任务完成后没有主动获取结果，依赖推送的不完整数据

**解决方案：**

1. **SSE连接带自动重连**：断开后指数退避重连，使用Last-Event-ID恢复
2. **长任务使用Webhook或SSE**：避免同步HTTP长连接超时
3. **轮询兜底机制**：即使有SSE/Webhook，也定期轮询tasks/get作为兜底
4. **处理所有终态和中间态**：明确处理completed/failed/canceled/rejected/input-required
5. **设置合理超时**：根据任务类型设置客户端超时，不要无限等待

**SSE重连伪代码：**

```python
async def connect_sse_with_retry(task_id, max_retries=5):
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"/tasks/{task_id}/stream") as resp:
                    async for event in resp.content:
                        yield parse_sse_event(event)
            return
        except ConnectionError:
            wait_time = (2 ** attempt) * 1
            await asyncio.sleep(wait_time)
    raise Exception("Failed to connect after retries")
```

### 7.8.3 陷阱3：Agent Card信息不完整导致发现失败

**典型问题：**

- Agent Card缺少必填字段（name/description/url/version）
- skills数组为空或技能描述过于简略，Client无法判断能力
- url填写错误或端口不对，导致Client连接失败
- 没有声明authentication信息，Client认证失败
- capabilities配置错误（如声明支持streaming但实际不支持）

**检查清单：**

发布Agent Card前检查：
- [ ] name是唯一的、有意义的标识
- [ ] description清晰描述Agent能做什么、不能做什么
- [ ] url是可访问的完整URL（含https://、端口、路径）
- [ ] version符合语义化版本规范
- [ ] skills数组中每个技能都有清晰的id/name/description
- [ ] authentication配置与实际认证方式一致
- [ ] capabilities开关与实际实现匹配（streaming/pushNotifications等）
- [ ] 通过`curl https://your-domain/.well-known/agent.json`可正常访问
- [ ] JSON格式合法，没有语法错误

### 7.8.4 陷阱4：大文件直接嵌入Part

**典型问题：**

- 将几MB甚至几十MB的图片/PDF直接Base64编码嵌入FilePart.bytes
- 消息体过大导致JSON解析失败、内存溢出、网络超时
- Base64编码膨胀约33%，进一步增大消息体积
- 大消息在SSE流中被截断或分片导致解析错误

**最佳实践：**

| 文件大小 | 推荐方式 |
|---------|---------|
| < 100KB（小图标、缩略图） | Base64直接嵌入bytes字段 |
| 100KB - 10MB | 上传到对象存储，使用URI引用 |
| > 10MB | 分块上传 + URI引用 + 按需下载 |

**URI引用方式：**

1. 先将文件上传到可访问的存储（HTTP/HTTPS URL）
2. FilePart只传递uri，不传递bytes
3. 接收方按需通过HTTP GET下载文件
4. 如果需要安全访问，使用预签名URL（带过期时间的签名URL）

### 7.8.5 最佳实践列表

#### 版本协商

- 支持协议版本协商，在initialize/握手阶段交换版本信息
- 向前兼容：新版本Server能处理旧版本Client的请求
- 向后兼容：新版本Client能降级使用旧版本Server的功能
- 版本号使用语义化版本（SemVer）：MAJOR.MINOR.PATCH

#### 错误处理

- 使用标准错误码，不要自创无意义的错误码
- 错误信息应包含：错误码、人类可读消息、可选的调试信息（trace_id/request_id）
- 区分客户端错误（4xx）和服务端错误（5xx）
- 对可重试错误（网络超时、503）实现指数退避重试
- 记录错误上下文（请求ID、任务ID、时间戳）便于排查

#### 幂等性

- 创建任务时使用客户端生成的taskId，服务端对同一taskId返回相同结果
- 所有写操作支持幂等性：重复发送同一请求不会产生副作用
- 使用Idempotency-Key头（类似Stripe API）保证请求幂等
- 取消任务、查询任务等操作天然幂等

#### 超时设置

| 操作类型 | 建议超时 |
|---------|---------|
| 简单工具调用（MCP） | 30秒 |
| A2A同步短任务 | 60秒 |
| A2A长任务（使用SSE/Webhook） | 不设置HTTP超时，依赖状态管理 |
| ACP快速操作 | 30秒 |
| 发现请求（Agent Card） | 10秒 |

- 客户端总是设置合理超时，不要无限等待
- 超时后根据场景选择：重试、回退、返回错误给用户
- 超时错误带上任务ID，便于后续查询状态

#### 日志与可观测性

- 每个请求/任务分配唯一ID，贯穿整个调用链
- 记录关键事件：任务创建、状态变更、错误、完成
- 敏感信息（Token、个人数据）在日志中脱敏
- 记录耗时指标：队列等待时间、执行时间、总时间
- 暴露健康检查端点（/health）用于监控

## 7.9 章节导航

| 导航 | 链接 |
|------|------|
| 返回总览 | [Agent通信协议总览](../agent-communication-protocols-wiki.md) |
| 上一章 | [06、典型交互流程与场景模式](./06-flows.md) |
| **下一章** | [08、应用场景与选型指南](./08-scenarios.md) |
