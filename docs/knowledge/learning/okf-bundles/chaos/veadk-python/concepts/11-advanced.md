---
type: Concept
title: 高级特性
description: A2A 协议、多模态系统、认证体系、Prompt 管理、Harness 扩展与运行时抽象等高级能力
tags: [veadk, a2a, multimodal, auth, prompt, harness, runtime]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# 高级特性

本文档汇总 veadk-python 中超越基础 Agent/Runner 抽象的高级能力：A2A（Agent-to-Agent）协议、多模态媒体管理、认证体系、Prompt 管理、Harness 扩展和多运行时抽象。这些特性使 veadk 能够支撑生产级 Agent 部署场景。

## A2A（Agent-to-Agent）协议

veadk 集成 Google A2A SDK（`a2a-sdk==0.3.7`）[F-006]，支持 Agent 间的标准化通信。

### AgentCard 生成

`get_agent_card(agent, url, version, provider)` 函数生成 A2A 协议的 `AgentCard` [F-113]：

- 创建默认 skill：`id="0"`、`name="chat"`、`description="Basically chat with user."`、`tags=["chat", "talk"]`
- 设置 `defaultInputModes=["text"]`、`defaultOutputModes=["text"]`
- 包含 Agent 名称、描述、版本、提供商信息

### Agent 元数据提取

`veadk/agent_metadata.py` 提供三个函数提取 Agent 能力信息 [F-114]：

- `agent_search_sources(agent) -> list[str]`：返回智能搜索来源列表，可能包含 `"web"`、`"knowledge"`、`"memory"`
- `agent_skill_summaries(agent) -> list[dict[str, str]]`：返回去重后的技能摘要
- `agent_component_summaries(agent) -> list[dict[str, str]]`：返回挂载组件列表（knowledgebase、memory、prompt_manager、example_store、run_processor、tracer、toolset、plugin）

### 组件搜索

`search_agent_component(agent, source, query, *, app_name, user_id)` 异步函数支持跨组件搜索 [F-115]：

- `source="knowledge"`：通过 `asyncio.to_thread(knowledgebase.search, query)` 异步搜索知识库
- `source="memory"`：调用 `memory.search_memory(app_name, user_id, query)` 搜索长期记忆（需要 user_id）
- 返回结构包含 `mounted`、`sourceName`、`sourceType`、`results`

### RemoteVeAgent

`RemoteVeAgent`（`veadk/a2a/remote_ve_agent.py`）允许将远程 A2A Agent 作为本地子代理使用，在 AgentBuilder 的 `AGENT_TYPES` 中注册 [F-042]。A2A 模块还包含服务端（`ve_a2a_server.py`）、执行器（`ve_agent_executor.py`）和注册表客户端（`registry_client.py`）。

## 多模态系统

多模态系统定义于 `veadk/multimodal/`，提供媒体文件的上传、存储、检索和服务能力。

### MediaRef 数据类

```python
@dataclass(frozen=True)
class MediaRef:
    app_name: str
    user_id: str
    session_id: str
    media_id: str
```

`MediaRef` 使用 `veadk-media://` URI scheme 标识媒体资源 [F-116]：

- `uri` 属性生成格式：`veadk-media://apps/<app>/users/<user>/sessions/<session>/media/<id>`（各段 URL 编码）
- `from_uri(uri: str) -> MediaRef | None`：类方法，解析 URI；scheme 不匹配时返回 `None`
- URI scheme 常量：`MEDIA_URI_SCHEME = "veadk-media"`

### MediaRecord 数据类

```python
@dataclass(frozen=True)
class MediaRecord:
    ref: MediaRef
    file_name: str
    mime_type: str
    size_bytes: int
    sha256: str
    origin: str
    created_at: str
```

`MediaRecord` 记录媒体文件的完整元数据 [F-117]：

- `create()` 类方法自动生成 UTC ISO 时间戳
- `to_dict()`：序列化为存储格式（包含 uri）
- `to_api_dict()`：前端 camelCase 格式（id、uri、name、mimeType、sizeBytes、sha256、origin、createdAt）
- `from_dict(data)`：反序列化

### FastAPI 路由挂载

`mount_media_routes(app: FastAPI, service: MediaService)` 函数挂载以下 HTTP 端点 [F-118]：

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/web/media/capabilities` | 返回 maxFileBytes、mimeTypes、storage 类型 |
| POST | `/web/media` | 上传媒体（Form 参数：app_name、user_id、session_id、file） |
| GET | `/web/media/.../{media_id}` | 获取媒体元数据 |
| GET | `/web/media/.../{media_id}/content` | 获取媒体内容（本地 FileResponse，远程 307 重定向） |
| DELETE | `/web/media/.../{media_id}` | 删除单个媒体 |
| DELETE | `/web/media/.../{session_id}` | 删除会话所有媒体 |

上传大小限制通过 `service.max_file_bytes`，超限返回 413。存储类型由环境变量 `VEADK_MEDIA_STORAGE` 控制（默认 `"local"`）[F-118]。

Runner 在消息拦截阶段可将内联媒体数据上传到 TOS（`upload_inline_data_to_tos=True`），通过 `MediaMessage` 类型支持图像和视频输入。

## 认证体系

认证系统定义于 `veadk/auth/`，提供多层认证能力。

### BaseAuth 抽象基类

```python
class BaseAuth:
    def __init__(self) -> None: ...
    def _fetch_token(self) -> str | dict: ...
    @property
    def token(self) -> str | dict: ...
```

定义于 `veadk/auth/base_auth.py` [F-112]。`token` 属性通过 `_fetch_token` 获取令牌，子类实现具体的认证逻辑。

### OAuth2 中间件

`veadk/auth/middleware/oauth2_auth.py` 提供 OAuth2 认证中间件。`veadk web` 命令通过 `_patch_adkwebserver_oauth2` 猴子补丁将其集成到 ADK Web Server [F-081]，支持 VeIdentity User Pool 的用户认证。

### VeCredentialService

`veadk/auth/ve_credential_service.py` 实现 ADK 的 `CredentialService` 接口，为 Agent 工具调用提供令牌管理。

### VeAuth 子系统

`veadk/auth/veauth/` 包含多个服务的认证器：`ark_veauth`、`opensearch_veauth`、`postgresql_veauth`、`viking_mem0_veauth`、`vesearch_veauth`、`cozeloop_veauth`、`mse_veauth`、`prompt_pilot_veauth`、`speech_veauth`、`apmplus_veauth`。这些认证器为各火山引擎服务提供统一的凭证管理。

## Prompt 管理

Prompt 管理系统定义于 `veadk/prompts/`。

### BasePromptManager 抽象类

```python
class BasePromptManager(ABC):
    @abstractmethod
    def get_prompt(self, context: ReadonlyContext, **kwargs) -> str: ...
```

定义于 `veadk/prompts/prompt_manager.py` [F-109]。Agent 在 `model_post_init` 中若检测到 `prompt_manager`，将 `self.instruction` 替换为 `prompt_manager.get_prompt` 可调用对象 [F-030]。这使得系统指令可以在每次 Agent 运行时动态生成。

### CozeloopPromptManager

`CozeloopPromptManager` 从 CozeLoop 平台获取 Prompt [F-110]：

- 构造参数：`cozeloop_workspace_id`、`cozeloop_token`、`prompt_key`、`version`（默认空）、`label`（默认空）
- 通过 `cozeloop.new_client(workspace_id=..., api_token=...)` 创建客户端
- `get_prompt` 调用 `client.get_prompt(prompt_key, version, label)`，返回第一条消息内容
- 获取失败时回退到 `DEFAULT_INSTRUCTION`

### 默认 Prompt

`DEFAULT_INSTRUCTION` 定义 Agent 擅长数据科学、文档编写、编程和工具使用 [F-111]。`DEFAULT_DESCRIPTION` 为 `"An AI agent developed by the VeADK team, specialized in data science, documentation, and software development."`

## Harness 扩展

Harness 扩展定义于 `veadk/extensions/harness/`，为 Agent 运行提供插件化增强。

### HarnessExtensionConfig

```python
class HarnessExtensionConfig(HarnessBaseModel):
    enabled: bool = True
    components: list[str] = ["invocation_context", "compactor", "response_verification"]
    profile: str = "default"
```

来源：[F-122]

默认启用三个组件：调用上下文、压缩器、响应验证。

### HarnessExtension 类

`HarnessExtension` 是扩展的主入口 [F-123]：

- 构造参数：`enabled`、`components`、`profile`、`store`、`context_config`、`compaction_config`、`verifier_config`、`env`
- `from_env(cls, env=None) -> HarnessExtension`：类方法，从环境变量创建实例
- `plugins() -> list[BasePlugin]`：构建插件列表，供 `Runner(..., plugins=...)` 使用
- `enabled=False` 时 `plugins()` 返回空列表

### 插件组件

`veadk/extensions/harness/plugins/` 目录包含以下插件：

| 插件 | 功能 |
|------|------|
| `invocation_context` | 调用上下文构建与注入 |
| `compactor` | 工具结果压缩（支持 headroom 提供商） |
| `response_verification` | 最终响应验证 |
| `builder` | 插件工厂 |
| `long_run_control` | 长时间运行控制 |

`veadk/harness.py` 提供便捷函数 `build_harness_plugins(*, components=None, profile="default")`，委托给扩展模块构建插件列表 [F-124]。

## 运行时抽象

运行时系统定义于 `veadk/runtime/`，允许替换 Agent 的内部推理循环。

### BaseRuntime 抽象类

```python
class BaseRuntime(ABC):
    name: str = "base"

    @abstractmethod
    async def run_async(
        self, agent: "Agent", ctx: "InvocationContext"
    ) -> AsyncGenerator["Event", None]: ...
```

来源：[F-119]

运行时替换 Agent 的内部推理+工具循环，而 Runner 仍负责多租户、会话、记忆和 tracing [F-119]。

### 三种运行时

| 运行时 | 说明 |
|--------|------|
| `"adk"`（默认） | 使用 Google ADK 的 `BaseLlmFlow` |
| `"codex"` | 基于 Claude Code SDK 的运行时（`veadk/runtime/codex/`） |
| `"piagent"` | PiAgent 运行时（`veadk/runtime/piagent/`） |

Agent 的 `_run_async_impl` 方法根据 `self.runtime` 字段调度：`"adk"` 委托父类，其他通过 `veadk.runtime.get_runtime(self.runtime).run_async(self, ctx)` 桥接到外部 harness [F-039]。

### 系统提示词构建

`base_runtime.py` 提供两个函数构建运行时系统提示词 [F-120][F-121]：

- `build_system_append(agent) -> str`：将 agent 的 name、description、instruction（仅字符串类型）组合为文本块
- `resolve_system_append(agent, ctx) -> tuple[str, str]`：异步解析，返回 `(base_parts, developer_parts)`，支持 `InstructionProvider` 可调用对象、状态注入和三层指令解析（global_instruction、static_instruction、instruction）

## 技能系统

技能系统定义于 `veadk/skills/`，支持动态加载工具能力。

- `enable_dynamic_load_skills=True` 时启用动态技能加载 [F-019]
- 技能模式由 `AGENTKIT_TOOL_ID` 环境变量判定：无环境变量为 `"local"`（已弃用），有则为 `"skills_sandbox"` 或 `"aio_sandbox"` [F-035]
- 技能可从本地目录或云端加载
- `enable_skills_checklist=True` 时注册检查清单回调

## 隧道工具

`enable_tunnel=True` 时追加 `TunnelToolset`，支持 MCP 协议隧道（`veadk/tunnel/`），包含连接器、注册表、服务端和工具集 [F-033]。

## A2UI（Agent 驱动 UI）

`enable_a2ui=True` 时追加 A2UI 工具集，`a2ui_catalog` 字段接受 catalog JSON 路径、`BaseA2UICatalog`、`A2uiCatalog` 或预构建元组 [F-022]。

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [Runner 运行器](/concepts/05-runner.md)
- [记忆系统](/concepts/06-memory-system.md)
- [知识库](/concepts/08-knowledgebase.md)
- [CLI 工具集](/concepts/10-cli-tools.md)
- [veadk-python 概览](/concepts/00-overview.md)
