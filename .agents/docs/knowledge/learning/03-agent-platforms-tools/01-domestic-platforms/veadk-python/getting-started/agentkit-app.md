---
id: veadk-python-agentkit-app
title: AgentKit 应用工厂使用指南
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- AgentKit
- FastAPI
- Web服务
- 部署
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: AgentKit 应用工厂 create_agentkit_app 使用指南，介绍如何将 VeADK Agent 包装为生产级 Web 服务
wiki_version: '1.0'
---


# AgentKit 应用工厂使用指南

本文档介绍 VeADK 提供的 `create_agentkit_app` 应用工厂函数，用于将 Agent 快速包装为生产级 Web 服务。

---

## AgentKitApp 是什么

`create_agentkit_app` 是 VeADK 提供的一个应用工厂函数（定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1051-L1105](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1051-L1105)），用于将一个 VeADK Agent 包装为符合 AgentKit 规范的 FastAPI Web 应用。

该函数基于 `agentkit-sdk-python` 的 `AgentkitAgentServerApp` 构建，自动集成以下能力：

| 能力 | 说明 |
|------|------|
| AgentKit 对话 API | 标准的 `/run`、`/run_sse`、`/invoke` 等对话接口 |
| 健康检查端点 | `/ping` 端点用于存活检测 |
| Agent 拓扑端点 | `/web/agent-info/{app_name}`、`/web/agent-graph` 等内省接口 |
| 内置 Web UI | 自动挂载 VeADK 自带的 Web 对话界面 |
| 本地短期记忆兜底 | 未配置记忆时自动创建内存版 ShortTermMemory |
| 可选飞书渠道 | `enable_feishu=True` 时启动飞书机器人后台线程 |
| Session 能力路由 | 会话能力检查和动态 Agent 构建 |
| 动态 A2A 路由 | 根据提示词动态挂载远程 A2A Agent 工具 |
| 运行时身份绑定 | 支持 AgentKit Runtime Identity 边界验证 |

设计意图是将平台路由、生命周期管理、健康检查等基础设施代码与 Agent 业务逻辑解耦，让开发者只需关注 Agent 本身的定义。

---

## 与直接创建 Agent 的区别

直接使用 `Agent` + `Runner` 是编程式 API，适合脚本、批处理、集成到现有 Python 应用中；而 `create_agentkit_app` 是服务式 API，适合将 Agent 部署为独立 Web 服务。

| 维度 | 直接使用 Agent + Runner | create_agentkit_app |
|------|-------------------------|---------------------|
| 使用方式 | 代码中直接调用 `runner.run()` | 启动 HTTP 服务，通过 API 调用 |
| 会话管理 | 手动控制 session_id | 自动管理，支持多用户并发 |
| 协议支持 | Python 内部调用 | HTTP/JSON-RPC、SSE 流式输出 |
| Web UI | 无 | 内置 Web 对话界面 |
| 健康检查 | 无 | `/ping` 端点 |
| 部署场景 | 脚本、集成到现有应用 | 独立微服务、容器化部署 |
| 飞书集成 | 需手动配置 Extension | `enable_feishu=True` 一键启用 |
| Agent 元数据 | 无 | `/web/agent-info` 端点暴露 |
| 多应用支持 | 需自行实现 | ADK 多应用服务器支持 |

**简单理解**：
- **学习/测试/脚本场景**：使用 `Agent` + `Runner`
- **部署为 Web 服务/AgentKit 平台场景**：使用 `create_agentkit_app`

---

## 使用示例

### 最小示例

以下是一个最小可运行的 AgentKit 应用（参考 [file:///d:/AI/.chaos/libs/veadk-python/README.md#L89-L95](file:///d:/AI/.chaos/libs/veadk-python/README.md#L89-L95)）：

```python
"""
最小 AgentKit 应用示例
"""
from veadk import Agent
from veadk.integrations.agentkit import create_agentkit_app, run_agentkit_app

# 1. 创建根 Agent
root_agent = Agent(
    name="customer_support",
    description="客服助手，回答用户关于产品的常见问题",
    instruction="你是一个专业的客服助手，用友好、专业的语气回答用户问题。",
)

# 2. 创建 AgentKit 应用
app = create_agentkit_app(root_agent)

# 3. 运行应用
if __name__ == "__main__":
    run_agentkit_app(app, host="0.0.0.0", port=8000)
```

将代码保存为 `app.py`，运行：

```bash
python app.py
```

服务启动后：
- 访问 http://localhost:8000/ 打开 Web UI
- 访问 http://localhost:8000/ping 进行健康检查
- 访问 http://localhost:8000/web/agent-info/customer_support 查看 Agent 元数据

### 带飞书渠道的示例

```python
"""
带飞书机器人的 AgentKit 应用
"""
from veadk import Agent
from veadk.integrations.agentkit import create_agentkit_app, run_agentkit_app

root_agent = Agent(
    name="feishu_bot",
    instruction="你是一个飞书群聊助手，回答群成员的问题。",
)

# 启用飞书渠道，需要设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET
app = create_agentkit_app(
    root_agent,
    enable_feishu=True,
)

if __name__ == "__main__":
    run_agentkit_app(app)
```

飞书渠道使用环境变量 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 进行认证（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L338-L339](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L338-L339)），在独立后台线程中自动重连。

### 带子 Agent 的多智能体示例

```python
"""
多智能体 AgentKit 应用示例
"""
from veadk import Agent
from veadk.integrations.agentkit import create_agentkit_app, run_agentkit_app

# 创建专业子 Agent
weather_agent = Agent(
    name="weather_expert",
    description="天气查询专家，负责回答天气相关问题",
    instruction="你是天气查询专家，回答用户关于天气的问题。",
)

finance_agent = Agent(
    name="finance_expert",
    description="金融专家，负责回答金融理财相关问题",
    instruction="你是金融专家，回答用户关于股票、基金、理财的问题。",
)

# 创建根 Agent，挂载子 Agent
root_agent = Agent(
    name="router_agent",
    description="智能路由助手，根据问题类型分发到对应专家",
    instruction="你是一个智能路由助手，根据用户问题类型将任务分发给对应的专家子 Agent。",
    sub_agents=[weather_agent, finance_agent],
)

# 配置显示名称映射（技术名 → 用户友好名）
display_names = {
    "router_agent": "智能助手",
    "weather_expert": "天气专家",
    "finance_expert": "金融专家",
}

app = create_agentkit_app(
    root_agent,
    display_names=display_names,
)

if __name__ == "__main__":
    run_agentkit_app(app)
```

`display_names` 参数用于在 Web UI 和元数据端点中显示用户友好的名称，而非技术名称。

### 使用 uvicorn 直接运行

如果你需要更精细控制 uvicorn 配置（如 SSL、workers 等），可以直接使用 uvicorn：

```python
"""
使用 uvicorn 直接运行
"""
import uvicorn
from veadk import Agent
from veadk.integrations.agentkit import create_agentkit_app

root_agent = Agent(name="my_agent")
app = create_agentkit_app(root_agent)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        # ssl_keyfile="./key.pem",
        # ssl_certfile="./cert.pem",
    )
```

---

## API 参考

### create_agentkit_app 函数签名

```python
def create_agentkit_app(
    root_agent: BaseAgent,
    display_names: Mapping[str, str] | None = None,
    *,
    agent_draft: Mapping[str, Any] | None = None,
    enable_feishu: bool = False,
    identity: RuntimeIdentity | None = None,
) -> FastAPI:
```

定义位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1051-L1105](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1051-L1105)

**参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `root_agent` | `BaseAgent` | 是 | - | 根 Agent 实例，可以是 VeADK Agent 或 Google ADK BaseAgent |
| `display_names` | `Mapping[str, str] \| None` | 否 | `None` | Agent 显示名称映射，key 为 Agent name，value 为用户友好名称 |
| `agent_draft` | `Mapping[str, Any] \| None` | 否 | `None` | 可选的构建器草稿数据，用于只读编辑元数据 |
| `enable_feishu` | `bool` | 否 | `False` | 是否启用飞书机器人渠道后台线程 |
| `identity` | `RuntimeIdentity \| None` | 否 | `None` | AgentKit 运行时身份边界，需要 agentkit-sdk-python >= 0.8.2 |

**返回值**：配置完成的 FastAPI 应用实例。

### run_agentkit_app 函数签名

```python
def run_agentkit_app(
    app: FastAPI,
    *,
    host: str | None = None,
    port: int | None = None,
) -> None:
```

定义位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1108-L1120](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1108-L1120)

**参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `app` | `FastAPI` | 是 | - | `create_agentkit_app` 返回的应用 |
| `host` | `str \| None` | 否 | `None` | 监听地址，默认读 `HOST` 环境变量或 `"0.0.0.0"` |
| `port` | `int \| None` | 否 | `None` | 监听端口，默认读 `PORT` 环境变量或 `8000` |

---

## 内置 API 端点

`create_agentkit_app` 创建的应用自动挂载以下端点：

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/ping` | 健康检查，返回 `{"status": "ok"}` |

### Agent 内省端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/web/agent-info/{app_name}` | 获取指定 Agent 的元数据（模型、工具、技能、子 Agent 等） |
| GET | `/web/agent-graph` | 获取 Agent 拓扑图（嵌套子 Agent 结构） |
| GET | `/web/search` | 搜索 Agent 组件（知识库或长期记忆） |

### AgentKit 标准对话端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/run` | 同步对话接口，返回完整事件列表 |
| POST | `/run_sse` | SSE 流式对话接口，实时输出事件流 |
| POST | `/invoke` | 简化调用接口，接收纯文本 prompt |

### Harness/Studio 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/harness/capabilities/tools` | 获取工具能力列表 |
| GET | `/harness/skills/spaces` | 获取技能空间列表 |
| GET | `/harness/skills/spaces/{space_id}/skills` | 获取空间内技能列表 |
| POST | `/harness/run_sse` | 带会话能力检查的 SSE 运行接口 |

### Web UI

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/`、`/webui`、`/webui/{path}` | Web 对话界面（如 webui 目录存在） |

---

## 适用场景

`create_agentkit_app` 适用于以下场景：

### 1. 生产环境 Web 服务部署

将 Agent 作为独立微服务部署，通过 HTTP API 提供对话能力，适合：
- 容器化部署（Docker/Kubernetes）
- 与前端应用集成
- 负载均衡和水平扩展

### 2. AgentKit 平台集成

部署到火山引擎 AgentKit 平台时，平台要求应用暴露标准的 AgentKit API，`create_agentkit_app` 自动满足此要求。

### 3. 快速原型验证

需要一个带 Web UI 的对话界面来快速验证 Agent 效果时，`create_agentkit_app` 内置了 Web UI，无需额外开发前端。

### 4. 飞书机器人开发

需要快速搭建飞书群聊机器人时，设置 `enable_feishu=True` 并配置飞书凭证即可，无需手动处理 WebSocket 连接和重连逻辑。

### 5. 多智能体系统可视化

开发多智能体系统时，`/web/agent-graph` 端点可以可视化 Agent 拓扑结构，便于调试和监控。

---

## 不适用场景

以下场景建议直接使用 `Agent` + `Runner`，而非 `create_agentkit_app`：

1. **脚本和批处理**：一次性任务、数据处理脚本
2. **Jupyter Notebook 探索**：交互式数据分析和实验
3. **集成到现有 Web 应用**：已有 FastAPI/Flask/Django 应用，需将 Agent 作为路由之一挂载
4. **单元测试**：编写 Agent 逻辑的单元测试

---

## 完整部署示例

### 项目结构

```
my-agent-app/
├── .env                # 环境变量（API Key 等）
├── app.py              # AgentKit 应用入口
├── requirements.txt    # 依赖
└── Dockerfile          # 容器化配置（可选）
```

### requirements.txt

```
veadk-python[extensions]>=0.5.0
uvicorn>=0.20.0
```

### .env 文件

```env
MODEL_AGENT_API_KEY=your-ark-api-key
VOLCENGINE_ACCESS_KEY=your-ak
VOLCENGINE_SECRET_KEY=your-sk
HOST=0.0.0.0
PORT=8000
```

### app.py

```python
"""
生产级 AgentKit 应用示例
"""
from veadk import Agent
from veadk.integrations.agentkit import create_agentkit_app, run_agentkit_app

root_agent = Agent(
    name="production_agent",
    description="生产环境助手",
    instruction="你是一个专业的AI助手，为用户提供准确、有帮助的回答。",
)

app = create_agentkit_app(root_agent)

if __name__ == "__main__":
    run_agentkit_app(app)
```

### Dockerfile（可选）

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

构建和运行：
```bash
docker build -t my-veadk-app .
docker run -p 8000:8000 --env-file .env my-veadk-app
```

---

## 注意事项

### 1. 短期记忆默认配置

如果 `root_agent` 未设置 `short_term_memory`，`create_agentkit_app` 会自动创建一个内存版 `ShortTermMemory(backend="local")`（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1079-L1081](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L1079-L1081)）。**内存版记忆在服务重启后会丢失**，生产环境建议配置数据库支持的短期记忆（PostgreSQL/MySQL/Redis）。

### 2. 飞书渠道线程模型

`enable_feishu=True` 时，飞书连接在独立后台线程中运行，包含自动重连逻辑（每 5 秒重试）（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L289-L334](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L289-L334)）。应用关闭时会自动尝试优雅断开连接。

### 3. 路由优先级

`create_agentkit_app` 会调整路由优先级，确保平台核心路由（`/ping`、`/run_sse`、Web UI 等）优先于其他路由（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L508-L539](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L508-L539)）。如果你需要添加自定义路由，建议在 `create_agentkit_app` 返回 app 之后再挂载，避免被平台路由覆盖。

### 4. Runtime Identity 版本要求

使用 `identity` 参数需要 `agentkit-sdk-python >= 0.8.2`，否则会抛出 RuntimeError（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L89-L95](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L89-L95)）。

### 5. Web UI 条件挂载

Web UI 仅在 `veadk/webui/index.html` 存在时才会挂载（[file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L486-L505](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/agentkit/app.py#L486-L505)）。某些最小化安装可能不包含 Web UI 文件，此时不会影响 API 功能。

---

## 相关资源

- [快速入门](quickstart.md) - Agent + Runner 基础用法
- [配置指南](configuration.md) - 配置 API Key 和其他参数
- [examples/basic-app/](file:///d:/AI/.chaos/libs/veadk-python/examples/basic-app/) - 完整可部署示例
- [AgentKit 官方文档](https://github.com/volcengine/veadk-python) - 更多部署和集成文档

---

> **版本说明**：本文档基于 VeADK-Python 代码库分析生成，对应 Wiki 版本 1.0。如发现文档内容与实际代码不符，请参考源代码为准。
