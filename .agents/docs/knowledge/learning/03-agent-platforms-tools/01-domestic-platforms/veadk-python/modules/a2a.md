---
id: a2a-module
title: Agent2Agent(A2A)协议支持
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# Agent2Agent(A2A)协议支持

## 概述

VeADK 完整支持 Agent2Agent（A2A）协议，实现了 Agent 之间的互操作能力。A2A 是由 Google 提出的开放协议，允许不同厂商、不同框架实现的 Agent 之间通过标准化 JSON-RPC 接口互相调用、传递消息和协作。VeADK 提供了从服务端暴露、AgentCard 生成、Hub 注册到客户端调用的完整四层架构支持。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/](#)

---

## A2A协议简介

A2A（Agent-to-Agent）协议定义了 Agent 之间通信的标准方式，核心概念包括：

- **AgentCard**：Agent 的能力描述卡片，包含名称、描述、技能列表、端点 URL、认证方式等元数据
- **Task**：异步任务单元，支持状态追踪（submitted/working/completed/failed/canceled/rejected）
- **Message**：消息单元，包含角色（user/agent）和多部分内容（text/data/file）
- **JSON-RPC 2.0**：底层传输协议，基于 HTTP POST

**标准 JSON-RPC 方法：**
- `message/send`：发送消息（支持同步/异步）
- `tasks/get`：查询任务状态
- `tasks/cancel`：取消任务
- `tasks/resubscribe`：重新订阅任务更新

---

## VeADK A2A 实现架构

VeADK 采用四层架构实现 A2A 协议支持：

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer (客户端调用层)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  registry_client.py - AgentKit A2A Registry 客户端   │   │
│  │  search_agent_cards() / create_task() / poll_task() │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Hub Layer (注册中心层)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AgentKit A2A Registry (火山引擎 AgentKit 服务)       │   │
│  │  - Agent 注册与发现                                   │   │
│  │  - 基于语义搜索 Agent                                 │   │
│  │  - 任务路由与转发                                     │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Card Layer (能力描述层)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  agent_card.py - AgentCard 生成                      │   │
│  │  get_agent_card() - 根据 Agent 元数据生成标准卡片     │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Server Layer (服务端暴露层)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ve_a2a_server.py - VeA2AServer                      │   │
│  │  - FastAPI 应用构建                                  │   │
│  │  - A2aAgentExecutor 集成                             │   │
│  │  - InMemoryTaskStore 任务存储                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心类详解

### 1. VeA2AServer - A2A 服务端

`VeA2AServer` 是将 VeADK Agent 暴露为 A2A 服务的核心类，封装了 FastAPI 应用构建、请求处理和任务管理。

**类定义：**
```python
class VeA2AServer:
    def __init__(
        self,
        agent: Agent,
        url: str,
        app_name: str,
        short_term_memory: ShortTermMemory,
        credential_service: BaseCredentialService | None = None,
    ):
```

**核心组件：**
- `self.agent_card`: AgentCard 实例，由 `get_agent_card()` 生成
- `self.agent_executor`: `A2aAgentExecutor` 实例，包装 VeADK Runner 执行 Agent 逻辑
- `self.task_store`: `InMemoryTaskStore` 实例，内存中存储任务状态
- `self.request_handler`: `DefaultRequestHandler` 实例，处理 A2A JSON-RPC 请求

**build() 方法：**
```python
def build(self) -> FastAPI:
    app_application = A2AFastAPIApplication(
        agent_card=self.agent_card,
        http_handler=self.request_handler,
    )
    app = app_application.build()
    return app
```

构建 FastAPI 应用，自动挂载以下端点：
- `GET /.well-known/agent.json`：返回 AgentCard
- `POST /`：A2A JSON-RPC 端点（处理 message/send、tasks/get 等）

> 源码位置：[ve_a2a_server.py#L31-L64](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/ve_a2a_server.py#L31-L64)

---

### 2. get_agent_card() - AgentCard 生成

`get_agent_card()` 函数根据 VeADK Agent 实例生成符合 A2A 标准的 AgentCard。

**函数签名：**
```python
def get_agent_card(
    agent: Agent,
    url: str,
    version: str = VERSION,
    provider: str = "veadk"
) -> AgentCard:
```

**生成的 AgentCard 字段：**

| 字段 | 来源 | 说明 |
|------|------|------|
| `name` | `agent.name` | Agent 名称 |
| `description` | `agent.description` | Agent 描述 |
| `version` | VeADK VERSION | 版本号 |
| `url` | 传入参数 | A2A 服务端点 URL |
| `provider` | "veadk" | 提供商标识 |
| `capabilities` | `AgentCapabilities()` | Agent 能力（默认空） |
| `skills` | 内置 chat 技能 | 技能列表（默认包含 chat 技能） |
| `defaultInputModes` | `["text"]` | 默认输入模式 |
| `defaultOutputModes` | `["text"]` | 默认输出模式 |

**默认技能：**
```python
AgentSkill(
    id="0",
    name="chat",
    description="Basically chat with user.",
    tags=["chat", "talk"],
)
```

> 源码位置：[agent_card.py#L21-L45](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/agent_card.py#L21-L45)

---

### 3. init_app() - 快速初始化应用

`init_app()` 是便捷函数，快速创建并返回 A2A FastAPI 应用。

**函数签名：**
```python
def init_app(
    server_url: str,
    app_name: str,
    agent: Agent,
    short_term_memory: ShortTermMemory,
    credential_service: BaseCredentialService | None = None,
) -> FastAPI:
```

**使用示例：**
```python
from veadk.a2a import init_app
from veadk import Agent
from veadk.memory import InMemoryShortTermMemory

agent = Agent(name="my-agent", description="A helpful assistant.")
stm = InMemoryShortTermMemory()

app = init_app(
    server_url="http://localhost:8000/",
    app_name="my-app",
    agent=agent,
    short_term_memory=stm,
)

# 使用 uvicorn 运行
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

> 源码位置：[ve_a2a_server.py#L67-L93](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/ve_a2a_server.py#L67-L93)

---

### 4. RegistryClient - AgentKit A2A 注册中心客户端

`registry_client.py` 提供了与火山引擎 AgentKit A2A Registry 交互的完整客户端，支持 Agent 搜索、任务创建和轮询。

**配置类 AgentKitA2ARegistryConfig：**

| 字段 | 默认值 | 环境变量 | 说明 |
|------|--------|----------|------|
| `space_id` | "" | `REGISTRY_SPACE_ID` | 工作空间 ID |
| `endpoint` | `http://volcengineapi.byted.org/` | `REGISTRY_ENDPOINT` | API 端点 |
| `version` | `2025-10-30` | `REGISTRY_VERSION` | API 版本 |
| `service_name` | `agentkit` | `REGISTRY_SERVICE_NAME` | 服务名 |
| `region` | `cn-beijing` | `REGISTRY_REGION` | 区域 |
| `top_k` | 3 | `REGISTRY_TOP_K` | 搜索返回数量 |
| `timeout_ms` | 60000 | `REGISTRY_TIMEOUT_MS` | 超时时间（毫秒） |
| `poll_interval_ms` | 5000 | `REGISTRY_POLL_INTERVAL_MS` | 轮询间隔（毫秒） |

> 源码位置：[registry_client.py#L61-L73](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L61-L73)

---

#### 4.1 search_agent_cards() - 语义搜索 Agent

根据用户提示词语义搜索最匹配的 Agent。

**函数签名：**
```python
def search_agent_cards(
    prompt: str,
    top_k: int | None = None,
    config: AgentKitA2ARegistryConfig | None = None,
    *,
    strip_prompt: bool = True,
) -> dict[str, Any]:
```

**返回结构：**
```python
{
    "outcome": "success",
    "agents": [
        {
            "name": "weather-agent",
            "description": "查询天气信息",
            "version": "1.0.0",
            "protocol_version": "...",
            "preferred_transport": "...",
            "registration_type": "...",
            "skills": [{"id": "...", "name": "...", "description": "...", "tags": [...]}]
        }
    ],
    "total_count": 5,
    "diagnostics": {
        "search_request_id": "...",
        "request_duration_ms": 123,
        "duration_ms": 456
    }
}
```

**异常：**
- `RegistryError("INVALID_ARGUMENT", ...)`：prompt 为空
- `RegistryError("CONFIG_MISSING", ...)`：缺少 space_id 配置
- `RegistryError("AGENT_NOT_FOUND", ...)`：未找到匹配的 Agent

> 源码位置：[registry_client.py#L139-L190](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L139-L190)

---

#### 4.2 create_task() - 创建远程任务

向指定 Agent 发送消息，创建异步任务。

**函数签名：**
```python
def create_task(
    agent_name: str,
    input_text: str,
    task_id: str | None = None,
    config: AgentKitA2ARegistryConfig | None = None,
) -> dict[str, Any]:
```

**返回结构（同步完成）：**
```python
{
    "outcome": "success",
    "selected_agent": {...},  # sanitized AgentCard
    "task": None,
    "response": {"text": "Agent 的回复内容"},
    "diagnostics": {...}
}
```

**返回结构（异步任务）：**
```python
{
    "outcome": "success",
    "selected_agent": {...},
    "task": {"id": "task-uuid", "status": "submitted"},
    "diagnostics": {...}
}
```

**工作流程：**
1. 调用 `GetA2aAgent` API 获取 AgentCard 和运行时信息
2. 检查 Agent 状态是否为 `running`
3. 清理 AgentCard URL（去除引号等包装字符）
4. 构造 A2A message（JSON-RPC 2.0 格式）
5. 根据 AgentCard security 配置添加认证头
6. 发送 `message/send` 请求
7. 如返回 401 且有 OAuth2 配置，自动重试 M2M 认证
8. 返回结果或任务信息

> 源码位置：[registry_client.py#L202-L229](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L202-L229)

---

#### 4.3 poll_task() - 轮询任务状态

轮询异步任务直到完成或失败。

**函数签名：**
```python
def poll_task(
    agent_name: str,
    task_id: str,
    history_length: int = 10,
    config: AgentKitA2ARegistryConfig | None = None,
) -> dict[str, Any]:
```

**返回结构（任务进行中）：**
```python
{
    "outcome": "success",
    "task": {"id": "task-uuid", "status": "working"},
    "is_terminal": False,
    "diagnostics": {
        "duration_ms": 123,
        "sleep_seconds": 5.0,
        "next_action": "call a2a_registry_task_poll again until task status is terminal"
    }
}
```

**返回结构（任务完成）：**
```python
{
    "outcome": "success",
    "task": {"id": "task-uuid", "status": "completed"},
    "is_terminal": True,
    "response": {"text": "任务完成后的最终回复"},
    "diagnostics": {"duration_ms": 456}
}
```

**终态状态：**
- `completed`：任务成功完成
- `failed`：任务执行失败
- `canceled`：任务被取消
- `rejected`：任务被拒绝

> 源码位置：[registry_client.py#L232-L248](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L232-L248)

---

## 认证机制

RegistryClient 支持多种认证方式，自动从 AgentCard 的 security 配置中解析：

### API Key 认证
当 AgentCard 定义 API Key 安全方案时，自动添加对应的 HTTP 头。

### OAuth2 认证
当 AgentCard 定义 OAuth2 安全方案时：
1. 优先使用上游传入的 `Authorization` header（透传用户 token）
2. 如无上游 token 或 401 重试，自动使用 Client Credentials 流程获取 M2M token
3. 自动从 VeIdentity 查询 MACHINE_TO_MACHINE 客户端
4. 自动缓存 token（过期前 60 秒刷新）

### TIP Token
支持通过 `X-Ve-Tip-Token` 头传递 TIP token，用于追踪请求链路。

### 凭证解析优先级
Access Key / Secret Key 按以下顺序查找：
1. 显式传入 config
2. 环境变量：`AGENTKIT_ACCESS_KEY` / `AGENTKIT_SECRET_KEY`
3. 环境变量：`A2A_REGISTRY_ACCESS_KEY` / `A2A_REGISTRY_SECRET_KEY`
4. 环境变量：`ACCESS_KEY` / `SECRET_KEY`
5. 环境变量：`VOLCENGINE_ACCESS_KEY` / `VOLCENGINE_SECRET_KEY`
6. VeFaaS IAM 角色（运行在 VeFaaS 环境时）

> 源码位置：[registry_client.py#L305-L347](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L305-L347)

---

## 如何将 Agent 暴露为 A2A 服务

### 方式一：使用 CLI 部署

```bash
# 初始化项目时选择 A2A 部署模式
veadk init
# 在交互式配置中选择 "A2A/MCP Server" 模式

# 部署到 VeFaaS
veadk deploy --vefaas-app-name my-a2a-agent
```

### 方式二：编程方式创建 FastAPI 应用

```python
from fastapi import FastAPI
from veadk import Agent, tool
from veadk.a2a import init_app
from veadk.memory import InMemoryShortTermMemory

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}今天晴朗，25°C"

root_agent = Agent(
    name="weather-agent",
    description="一个可以查询天气的助手",
    tools=[get_weather],
)

app = init_app(
    server_url="http://localhost:8000/",
    app_name="weather-app",
    agent=root_agent,
    short_term_memory=InMemoryShortTermMemory(),
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 方式三：自定义 VeA2AServer

```python
from veadk import Agent
from veadk.a2a.ve_a2a_server import VeA2AServer
from veadk.memory import InMemoryShortTermMemory

agent = Agent(name="custom-agent", description="自定义 Agent")

server = VeA2AServer(
    agent=agent,
    url="https://my-agent.example.com/",
    app_name="custom-app",
    short_term_memory=InMemoryShortTermMemory(),
)

app = server.build()
# 可以在 app 上添加自定义路由或中间件
```

启动后访问：
- `http://localhost:8000/.well-known/agent.json` 查看 AgentCard
- `POST http://localhost:8000/` 发送 A2A 请求

> 源码位置：[ve_a2a_server.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/ve_a2a_server.py)

---

## 如何调用其他 A2A Agent

### 基础使用流程

```python
import os
from veadk.a2a.registry_client import (
    AgentKitA2ARegistryConfig,
    search_agent_cards,
    create_task,
    poll_task,
)

# 1. 配置
os.environ["REGISTRY_SPACE_ID"] = "your-space-id"
os.environ["VOLCENGINE_ACCESS_KEY"] = "your-ak"
os.environ["VOLCENGINE_SECRET_KEY"] = "your-sk"

config = AgentKitA2ARegistryConfig()

# 2. 搜索 Agent
result = search_agent_cards(
    prompt="帮我查询北京明天的天气",
    top_k=3,
    config=config,
)

print("找到的 Agent:", [a["name"] for a in result["agents"]])

# 3. 选择合适的 Agent 并创建任务
agent_name = result["agents"][0]["name"]
task_result = create_task(
    agent_name=agent_name,
    input_text="北京明天天气如何？",
    config=config,
)

if task_result.get("response"):
    # 同步完成，直接获取结果
    print("回复:", task_result["response"]["text"])
elif task_result.get("task"):
    # 异步任务，需要轮询
    task_id = task_result["task"]["id"]
    while True:
        poll_result = poll_task(
            agent_name=agent_name,
            task_id=task_id,
            config=config,
        )
        if poll_result["is_terminal"]:
            if poll_result.get("response"):
                print("回复:", poll_result["response"]["text"])
            break
        print(f"任务状态: {poll_result['task']['status']}，等待中...")
```

### 作为工具集成到 Agent

VeADK 提供了内置工具，可以将 A2A 调用封装为 Agent 可用的工具：

```python
from veadk import Agent
from veadk.tools import a2a_registry_search, a2a_registry_task_create, a2a_registry_task_poll

agent = Agent(
    name="router-agent",
    description="可以路由到其他专业 Agent 的总控 Agent",
    tools=[
        a2a_registry_search,
        a2a_registry_task_create,
        a2a_registry_task_poll,
    ],
)
```

这些内置工具会自动处理认证、错误重试和结果解析。

---

## A2A JSON-RPC 协议细节

### 发送消息 (message/send)

**请求：**
```json
{
    "jsonrpc": "2.0",
    "id": "request-uuid",
    "method": "message/send",
    "params": {
        "message": {
            "kind": "message",
            "messageId": "msg-uuid",
            "role": "user",
            "parts": [{"kind": "text", "text": "你好"}]
        },
        "configuration": {"blocking": false}
    }
}
```

**同步响应：**
```json
{
    "jsonrpc": "2.0",
    "id": "request-uuid",
    "result": {
        "kind": "message",
        "messageId": "response-uuid",
        "role": "agent",
        "parts": [{"kind": "text", "text": "你好！有什么可以帮你的？"}]
    }
}
```

**异步响应：**
```json
{
    "jsonrpc": "2.0",
    "id": "request-uuid",
    "result": {
        "id": "task-uuid",
        "status": {"state": "submitted"}
    }
}
```

### 查询任务 (tasks/get)

**请求：**
```json
{
    "jsonrpc": "2.0",
    "id": "request-uuid",
    "method": "tasks/get",
    "params": {
        "id": "task-uuid",
        "historyLength": 10
    }
}
```

> 协议实现参考：[registry_client.py#L691-L737](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L691-L737)

---

## 错误处理

RegistryClient 使用结构化的 `RegistryError` 异常：

```python
class RegistryError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        diagnostics: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.diagnostics = diagnostics or {}
```

**常见错误码：**

| 错误码 | 说明 |
|--------|------|
| `INVALID_ARGUMENT` | 参数无效（如 prompt 为空） |
| `CONFIG_MISSING` | 配置缺失（如 space_id、AK/SK） |
| `AGENT_NOT_FOUND` | 未找到匹配的 Agent |
| `AGENT_NOT_RUNNING` | Agent 未运行 |
| `AGENT_URL_MISSING` | AgentCard 缺少 url 字段 |
| `AGENT_AUTH_MISSING` | Agent 需要认证但未提供凭证 |
| `AGENTKIT_OPENAPI_FAILED` | AgentKit OpenAPI 请求失败 |
| `AGENTKIT_OPENAPI_ERROR` | AgentKit 返回业务错误 |
| `AGENTKIT_RESPONSE_PARSE_FAILED` | AgentKit 响应解析失败 |
| `A2A_HTTP_FAILED` | A2A 端点 HTTP 请求失败 |
| `A2A_REMOTE_ERROR` | A2A 端点返回 JSON-RPC 错误 |
| `A2A_TASK_CREATE_FAILED` | 任务创建失败 |
| `AGENT_OAUTH_CONFIG_INVALID` | OAuth2 配置无效 |
| `AGENT_OAUTH_CLIENT_MISSING` | OAuth2 客户端不存在 |
| `AGENT_OAUTH_TOKEN_FAILED` | OAuth2 token 获取失败 |

使用 `failure()` 函数可以安全地构造错误返回：
```python
from veadk.a2a.registry_client import failure, RegistryError

try:
    result = create_task(...)
except RegistryError as e:
    return failure(e.code, e.message, e.diagnostics)
```

> 源码位置：[registry_client.py#L49-L58](file:///d:/AI/.chaos/libs/veadk-python/veadk/a2a/registry_client.py#L49-L58)

---

## 目录结构

```
veadk/a2a/
├── __init__.py              # 包导出
├── ve_a2a_server.py         # VeA2AServer 服务端实现
├── agent_card.py            # AgentCard 生成
└── registry_client.py       # AgentKit A2A Registry 客户端
```
