---
id: agent-module
title: Agent 类完整 API 参考
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# Agent 类完整 API 参考

## 类签名与继承关系

```python
class Agent(LlmAgent):
```

**继承链**：`Agent` → `LlmAgent`（google.adk.agents）→ `BaseAgent`（google.adk.agents.base_agent）

`Agent` 类是 VeADK 框架的核心类，基于 Google ADK 的 `LlmAgent` 扩展，集成了火山引擎 AI 能力，支持记忆模块、子 Agent、追踪器、知识库等高级功能，适用于 A2A（Agent-to-Agent）或面向用户的场景。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L751)

---

## 公开属性列表

### 标识与基本信息

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | `str` | `Field(default_factory=lambda: str(uuid.uuid4()).split("-")[0])` | Agent 唯一标识符，自动生成短 UUID |
| `name` | `str` | `DEFAULT_AGENT_NAME` | Agent 名称 |
| `description` | `str` | `DEFAULT_DESCRIPTION` | Agent 描述，在 A2A 场景中有用 |
| `instruction` | `Union[str, InstructionProvider]` | `DEFAULT_INSTRUCTION` | Agent 指令或指令提供者 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L107-L110](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L107-L110)

### 模型配置

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `model_name` | `Union[str, list[str]]` | `Field(default_factory=lambda: settings.model.name)` | Agent 使用的模型名称，支持字符串或模型列表（用于 fallback） |
| `model_provider` | `str` | `Field(default_factory=lambda: settings.model.provider)` | 模型提供商（如 openai） |
| `model_api_base` | `str` | `Field(default_factory=lambda: settings.model.api_base)` | 模型 API 基础 URL |
| `model_api_key` | `str` | `""` | 访问模型的 API 密钥。初始化时若为空，将按以下优先级解析：显式 `model_api_key` > `MODEL_AGENT_API_KEY` 环境变量 > `model_api_key_name`/`MODEL_AGENT_API_KEY_NAME`（按名称解析）> 账户中第一个 ARK 密钥 |
| `model_api_key_name` | `str` | `Field(default_factory=lambda: settings.model.api_key_name)` | ARK API 密钥名称（默认从环境变量 `MODEL_AGENT_API_KEY_NAME` 获取）。当设置了 `model_api_key` 或 `MODEL_AGENT_API_KEY` 环境变量时，此参数被忽略 |
| `model_extra_config` | `dict` | `Field(default_factory=dict)` | 模型请求的额外配置，包含 `extra_headers` 和 `extra_body` |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L112-L124](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L112-L124)

### 工具与子 Agent

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tools` | `list[ToolUnion]` | `[]` | Agent 可用的工具列表 |
| `sub_agents` | `list[BaseAgent]` | `Field(default_factory=list, exclude=True)` | 该 Agent 管理的子 Agent 列表 |
| `skills` | `list[str]` | `Field(default_factory=list)` | 为 Agent 配备特定能力的技能列表 |
| `skills_mode` | `Optional[Literal["skills_sandbox", "aio_sandbox", "local"]]` | `None` | 技能运行模式 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L126-L128](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L126-L128), [file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L168-L170](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L168-L170)

### Prompt 管理

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `prompt_manager` | `Optional[BasePromptManager]` | `None` | Prompt 管理器，用于动态生成指令 |
| `example_store` | `Optional[BaseExampleProvider]` | `None` | 示例存储，用于提供问答示例 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L130](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L130), [file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L172](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L172)

### 记忆模块

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `knowledgebase` | `Optional[KnowledgeBase]` | `None` | 附加到 Agent 的知识库 |
| `short_term_memory` | `Optional[ShortTermMemory]` | `None` | 会话级短期记忆，用于临时上下文 |
| `long_term_memory` | `Optional[LongTermMemory]` | `None` | 跨会话长期记忆，用于持久化用户上下文 |
| `auto_save_session` | `bool` | `False` | 是否自动将会话保存到长期记忆 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L132-L135](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L132-L135), [file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L166](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L166)

### 追踪与可观测性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tracers` | `list[BaseTracer]` | `[]` | 用于遥测和监控的追踪器列表 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L137](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L137)

### 模型响应配置

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_responses` | `bool` | `False` | 是否启用 Ark Responses API |
| `enable_responses_cache` | `bool` | `True` | Ark Responses API 是否应复用 `previous_response_id` 和缓存以支持多轮延续 |
| `context_cache_config` | `Optional[ContextCacheConfig]` | `None` | 上下文缓存配置 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L139-L142](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L139-L142)

### 运行时处理器

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `run_processor` | `Optional[BaseRunProcessor]` | `None` | 可选的运行处理器，用于拦截和处理 Agent 执行流程。可用于实现横切关注点，如认证流程（OAuth2 via VeIdentity）、请求/响应日志、错误处理和重试逻辑、性能监控。若未提供，默认使用 `NoOpRunProcessor` |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L144-L162](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L144-L162)

### 授权与安全

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_authz` | `bool` | `False` | 是否启用 Agent 授权检查 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L164](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L164)

### 功能开关

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_supervisor` | `bool` | `False` | 是否启用监督者流程 |
| `enable_ghostchar` | `bool` | `False` | 是否启用影子角色 |
| `enable_dataset_gen` | `bool` | `False` | 是否启用数据集生成 |
| `enable_dynamic_load_skills` | `bool` | `False` | 是否启用技能动态加载 |
| `enable_skills_checklist` | `bool` | `False` | 是否启用技能检查清单 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L174-L181](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L174-L181)

### 运行时后端

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `runtime` | `Literal["adk", "codex", "piagent"]` | `"adk"` | Agent 运行时后端。`"adk"`（默认）使用 Google ADK 内置 LLM 流程；`"codex"` 将内部 Agent 循环委托给 OpenAI Codex SDK；`"piagent"` 通过 RPC 模式将内部 Agent 循环委托给本地 Pi 编码 Agent 二进制文件。非 `"adk"` 运行时在 `veadk.runtime` 模块下实现 |
| `codex_runtime_config` | `Optional[Any]` | `None` | 可选的 Codex 运行时配置（`veadk.runtime.codex.config.CodexRuntimeConfig` 或匹配的 dict）。Codex 默认采用故障关闭和调用隔离策略 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L184-L193](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L184-L193)

### A2UI 与 Tunnel

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_a2ui` | `bool` | `False` | 启用 A2UI（Agent 驱动 UI）。为 True 时，会追加 `SendA2uiToClientToolset`，使 Agent 可以用客户端渲染的声明式 UI 回复。需要可选依赖 `a2ui-agent-sdk`（`pip install veadk-python[a2ui]`） |
| `a2ui_catalog` | `Optional[Any]` | `None` | 可选的 A2UI 目录。接受目录 JSON 路径（字符串；相对路径相对于 Agent 目录解析，绝对路径按原样使用）、`veadk.a2ui.BaseA2UICatalog`、`A2uiCatalog` 或预构建的 `(A2uiCatalog, examples)` 元组。为 None 时，自动在 Agent 旁边发现 `catalog.json`，回退到捆绑的基本目录。仅在 `enable_a2ui=True` 时使用 |
| `enable_tunnel` | `bool` | `False` | 启用 Tunnel。为 True 时，追加 `TunnelToolset`，使通过 `veadk.tunnel` 连接的本地资源服务器（如 MCP 服务器）显示为该 Agent 的工具。云应用还必须通过 `veadk.tunnel.mount_tunnel`/`mount_tunnel_if_enabled` 挂载 tunnel 路由 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L195-L212](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L195-L212)

---

## 回调机制

Agent 继承自 `LlmAgent`，支持 4 个回调参数：

| 回调参数 | 触发时机 | 签名 |
|----------|----------|------|
| `before_agent_callback` | Agent 执行前触发 | `Callable[[InvocationContext], None]` 或回调列表 |
| `after_agent_callback` | Agent 执行后触发 | `Callable[[InvocationContext], None]` 或回调列表 |
| `before_tool_callback` | 工具调用前触发 | `Callable[[InvocationContext, Tool, dict], None]` 或回调列表 |
| `after_tool_callback` | 工具调用后触发 | `Callable[[InvocationContext, Tool, dict, Any], None]` 或回调列表 |

> **注意**：这 4 个回调参数继承自 Google ADK 的 `LlmAgent` 基类，不在 Agent 类中显式定义为 Pydantic 字段，但可以在构造函数中传入。

### 回调使用示例

```python
from veadk import Agent, Runner

async def before_agent(ctx):
    print(f"Agent 开始执行，session: {ctx.session_id}")

async def after_agent(ctx):
    print(f"Agent 执行完成")

def before_tool(ctx, tool, args):
    print(f"调用工具: {tool.name}, 参数: {args}")

def after_tool(ctx, tool, args, result):
    print(f"工具 {tool.name} 返回: {result}")

agent = Agent(
    name="callback-demo",
    instruction="You are a helpful assistant.",
    before_agent_callback=before_agent,
    after_agent_callback=after_agent,
    before_tool_callback=before_tool,
    after_tool_callback=after_tool,
)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L335-L350](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L335-L350)（授权检查回调注册示例）

---

## 核心方法

### `__init__`

Agent 使用 Pydantic 模型，构造函数参数与上述公开属性完全一致。所有参数均有默认值，可以不传任何参数创建一个默认 Agent。

```python
def __init__(**data: Any) -> None
```

Pydantic 模型会自动处理所有字段的初始化和验证。

---

### `model_post_init`

```python
def model_post_init(self, __context: Any) -> None
```

Pydantic 模型初始化后自动调用的方法，执行完整的初始化流程：

1. **API Key 解析**：按优先级解析 model_api_key（显式值 > 环境变量 > key_name 解析 > 默认 ARK key）
2. **RunProcessor 初始化**：若未提供则使用 `NoOpRunProcessor`
3. **模型配置合并**：合并用户配置与 VeADK 默认配置（headers/body）
4. **模型客户端创建**：根据 `enable_responses` 创建 `ArkLlm` 或 `LiteLlm` 客户端，支持模型 fallback 列表
5. **追踪器准备**：根据环境变量（`ENABLE_APMPLUS`/`ENABLE_COZELOOP`/`ENABLE_TLS`）初始化 OpenTelemetry 追踪器
6. **工具依赖验证**：检查并自动补全依赖工具（如 video_generate 和 video_task_query）
7. **知识库工具注册**：若配置了 knowledgebase，自动添加 `LoadKnowledgebaseTool` 和 profile 查询工具
8. **长期记忆工具注册**：若配置了 long_term_memory，添加 `load_memory` 工具
9. **授权回调注册**：若 `enable_authz=True`，注册授权检查回调
10. **PromptManager 处理**：若设置了 prompt_manager，将 instruction 设置为其 get_prompt 方法
11. **会话自动保存**：若 `auto_save_session=True` 且配置了长期记忆，注册保存回调
12. **技能加载**：若配置了 skills，调用 `load_skills()` 加载技能
13. **示例工具注册**：若配置了 example_store，添加 ExampleTool
14. **Ghostchar 启用**：若 `enable_ghostchar=True`，添加 GhostcharTool 并修改指令
15. **A2UI 工具注册**：若 `enable_a2ui=True`，添加 A2UI 工具集
16. **Tunnel 工具注册**：若 `enable_tunnel=True`，添加 TunnelToolset
17. **数据集生成回调注册**：若 `enable_dataset_gen=True`，注册数据集生成回调

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L214-L445](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L214-L445)

---

### `update_model`

```python
def update_model(self, model_name: str) -> None
```

更新 Agent 使用的模型。

**参数**：
- `model_name: str` - 新的模型名称

**说明**：此方法会复制现有模型配置并更新 model 字段，保持其他配置（api_key, api_base 等）不变。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L447-L451](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L447-L451)

---

### `load_skills`

```python
def load_skills(self) -> None
```

加载技能。此方法在 `model_post_init` 中自动调用（当 skills 非空时）。

**功能**：
1. 自动检测 skills_mode（若未设置）：通过环境变量判断是本地模式还是云端沙箱模式
2. 遍历 skills 列表：
   - 若为本地目录路径，从目录加载技能
   - 否则从云端加载技能
3. 将技能信息添加到 Agent 指令中
4. 根据 skills_mode 添加对应的执行工具（execute_skills 或 skills_tool）
5. 若 `enable_dynamic_load_skills=True`，注册技能检查回调

**技能模式**：
- `"local"`：本地模式（已废弃，用于旧版本地技能加载）
- `"skills_sandbox"`：技能沙箱模式
- `"aio_sandbox"`：All-in-one 沙箱模式

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L453-L612](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L453-L612)

---

### `run`（仅 google-adk < 2.0.0）

```python
async def run(self, **kwargs)
```

> **已废弃**：自版本 0.5.6 起，VeADK Agent 的 run 方法已废弃。请使用 `runner.run_async` 替代。参考：https://agentkit.gitbook.io/docs/runner/overview

在 google-adk 2.x 中，`BaseAgent.run` 是 `@final` 异步生成器，工作流引擎内部调用；覆盖它会破坏 NodeRunner 执行。因此仅在 google-adk 1.x 版本中提供此方法，但会直接抛出 `NotImplementedError`。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L743-L751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L743-L751)

---

## RunProcessor 扩展点说明

`RunProcessor` 是 VeADK 提供的强大扩展机制，允许拦截和修改 Agent 执行流程。

### BaseRunProcessor 接口

```python
from veadk.processors import BaseRunProcessor

class BaseRunProcessor(ABC):
    @abstractmethod
    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:
        pass
```

`process_run` 方法返回一个装饰器，该装饰器包装事件生成器函数，可以：
1. 拦截来自 runner.run_async 的事件
2. 处理或修改事件
3. 注入额外事件（如认证请求）
4. 控制执行流程（如重试循环）

### 使用示例

```python
from veadk import Agent, Runner
from veadk.processors import BaseRunProcessor

class LoggingProcessor(BaseRunProcessor):
    def process_run(self, runner, message, **kwargs):
        def decorator(event_generator_func):
            async def wrapper():
                print(f"[Before Run] Message: {message.parts[0].text}")
                async for event in event_generator_func():
                    print(f"[Event] Author: {event.author}")
                    yield event
                print("[After Run] Completed")
            return wrapper
        return decorator

agent = Agent(
    name="processor-demo",
    run_processor=LoggingProcessor(),
)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/processors/base_run_processor.py#L27-L120](file:///d:/AI/.chaos/libs/veadk-python/veadk/processors/base_run_processor.py#L27-L120)

---

## 完整使用示例

### 基础示例

```python
import asyncio
from veadk import Agent, Runner

async def main():
    # 创建 Agent
    agent = Agent(
        name="quickstart_agent",
        description="A friendly assistant that answers in one short paragraph.",
        instruction="You are a helpful assistant. Answer concisely in the user's language.",
    )

    # 创建 Runner
    runner = Runner(agent=agent, app_name="quickstart")

    # 运行对话
    answer = await runner.run(
        messages="用一句话介绍火山引擎（Volcengine）。",
        session_id="demo-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

> 示例来源：[file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py)

### 带自定义工具的示例

```python
import asyncio
from veadk import Agent, Runner
from google.adk.tools import FunctionTool

def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间"""
    from datetime import datetime
    import pytz
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

async def main():
    agent = Agent(
        name="tool-demo",
        instruction="You are a helpful assistant. Use tools when needed.",
        tools=[FunctionTool(get_current_time)],
    )

    runner = Runner(agent=agent, app_name="tool-demo")
    answer = await runner.run(
        messages="现在几点了？",
        session_id="tool-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 模型 fallback 示例

```python
agent = Agent(
    name="fallback-demo",
    model_name=["doubao-pro-32k", "doubao-lite-32k"],
    model_provider="openai",
    model_api_base="https://ark.cn-beijing.volces.com/api/v3/",
)
```

### 多模型列表 fallback 说明

当 `model_name` 为列表时，第一个模型作为主模型，后续模型作为 fallback。例如 `model_name=["model-a", "model-b", "model-c"]` 时：
- 优先使用 model-a
- 若 model-a 调用失败，自动尝试 model-b
- 若 model-b 也失败，尝试 model-c

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L257-L266](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L257-L266)
