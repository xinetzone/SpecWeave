---
type: Concept
title: Agent 核心类与生命周期
description: Agent 类的字段体系、model_post_init 生命周期、模型实例化、工具挂载与 _llm_flow 流程选择
tags: [veadk, agent, lifecycle, llm, tools]
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

# Agent 核心类与生命周期

`Agent` 是 veadk-python 的核心类，定义于 `veadk/agent.py`，继承自 Google ADK 的 `LlmAgent` [F-013]。它通过 Pydantic 模型字段声明所有可配置项，并在 `model_post_init` 生命周期方法中完成模型实例化、工具挂载、回调注册等"能力装配"工作。理解 Agent 的生命周期是掌握 veadk 的关键。

## 类定义与 Pydantic 配置

```python
class Agent(LlmAgent):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
```

`model_config` 允许任意类型字段（如 LLM 客户端实例），且 `extra="allow"` 意味着传入未声明的字段不会报错 [F-014]。模块导入时自动执行 `patch_tracer()`、`patch_asyncio()`、`patch_mcp_session_retry()` 三个补丁函数 [F-013]。

## 核心字段体系

Agent 的字段可分为五大类：

### 身份与指令字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `id` | `str` | `uuid4().split("-")[0]` | 8 字符短 ID [F-015] |
| `name` | `str` | `"veAgent"` | Agent 名称 [F-060] |
| `description` | `str` | `DEFAULT_DESCRIPTION` | 描述，用于 A2A 场景 [F-111] |
| `instruction` | `str \| InstructionProvider` | `DEFAULT_INSTRUCTION` | 系统指令，可为可调用对象 [F-015] |

### 模型配置字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_name` | `str \| list[str]` | `settings.model.name` | 模型名，列表时首为主模型其余为 fallback [F-016] |
| `model_provider` | `str` | `settings.model.provider` | 模型提供商 |
| `model_api_base` | `str` | `settings.model.api_base` | API 基础 URL |
| `model_api_key` | `str` | `""` | 显式 API Key |
| `model_api_key_name` | `str` | `settings.model.api_key_name` | ARK Key 名称 |
| `model_extra_config` | `dict` | `{}` | 额外请求配置 |

### 工具与子代理字段

- `tools: list[ToolUnion] = []`：工具列表 [F-017]
- `sub_agents: list[BaseAgent] = []`：子代理列表（`exclude=True`，不序列化）[F-017]

### 扩展组件字段

- `prompt_manager: Optional[BasePromptManager]`：Prompt 管理器 [F-018]
- `knowledgebase: Optional[KnowledgeBase]`：知识库 [F-018]
- `short_term_memory: Optional[ShortTermMemory]`：短期记忆 [F-018]
- `long_term_memory: Optional[LongTermMemory]`：长期记忆 [F-018]
- `tracers: list[BaseTracer]`：追踪器列表 [F-018]
- `run_processor: Optional[BaseRunProcessor]`：运行处理器（`exclude=True`）[F-018]
- `example_store: Optional[BaseExampleProvider]`：示例存储 [F-018]

### 功能开关字段

Agent 提供十余个布尔开关，在 `model_post_init` 中根据开关值自动挂载对应能力 [F-019]：

- `enable_responses`：Ark Responses API
- `enable_responses_cache`：多轮 `previous_response_id` 复用（默认 `True`）
- `enable_authz`：授权检查
- `auto_save_session`：自动保存到长期记忆
- `enable_supervisor`：监督者流程
- `enable_ghostchar`：幽灵字符
- `enable_dataset_gen`：数据集生成
- `enable_dynamic_load_skills`：动态技能加载
- `enable_skills_checklist`：技能检查清单
- `enable_a2ui`：Agent 驱动 UI
- `enable_tunnel`：隧道工具

## 生命周期：model_post_init

`model_post_init(self, __context: Any) -> None` 是 Pydantic v2 提供的后初始化钩子，Agent 在其中按固定顺序完成装配 [F-023]：

### 第一步：API Key 解析

API Key 按四级优先级解析 [F-024]：

1. 显式传入的 `model_api_key` 参数
2. 环境变量 `MODEL_AGENT_API_KEY`
3. `model_api_key_name` 指定的 ARK Key 名称（通过 `get_ark_token` 按名称解析）
4. `settings.model.api_key`（账户首个 ARK Key）

### 第二步：默认请求头与 Body 构建

`extra_headers` 包含 `x-is-encrypted`、`veadk-source`、`veadk-version`、`User-Agent`、`X-Client-Request-Id` 等默认头 [F-026]。`extra_body` 包含 `caching.type`（默认 `enabled`）和 `expire_at`（当前时间 + 3600 秒）。用户配置通过 `|=` 运算符合并到默认值。

### 第三步：模型实例化

根据 `enable_responses` 开关选择 LLM 实现 [F-025]：

- `enable_responses=True`：创建 `ArkLlm` 实例（Ark Responses API）
- `enable_responses=False`（默认）：创建 `LiteLlm` 实例（LiteLLM 统一网关）

模型名格式为 `f"{model_provider}/{model_name}"`。当 `model_name` 为列表时，首个元素作为主模型，其余作为 `fallbacks` 传入，实现主备自动切换。

### 第四步：工具与回调自动挂载

这是 `model_post_init` 的核心，按组件有无和开关状态自动追加工具和注册回调：

| 条件 | 挂载动作 |
|------|---------|
| `knowledgebase` 存在 | 追加 `LoadKnowledgebaseTool`；`enable_profile=True` 时额外追加 `load_kb_queries` [F-027] |
| `long_term_memory` 存在 | 追加 ADK 的 `load_memory` 工具，设置 `custom_metadata["backend"]` [F-028] |
| `enable_authz=True` | 注册 `check_agent_authorization` 到 `before_agent_callback` [F-029] |
| `prompt_manager` 存在 | 将 `self.instruction` 替换为 `prompt_manager.get_prompt` 可调用对象 [F-030] |
| `auto_save_session=True` + LTM | 注册 `save_session_to_long_term_memory` 到 `after_agent_callback` [F-031] |
| `skills` 非空 | 调用 `self.load_skills()` 加载技能 [F-032] |
| `enable_skills_checklist=True` | 注册 `create_init_skill_check_list_callback` 到 `before_tool_callback` [F-032] |
| `example_store` 存在 | 追加 `ExampleTool` [F-033] |
| `enable_ghostchar=True` | 追加 `GhostcharTool`，在指令后追加 `<` 字符要求 [F-033] |
| `enable_a2ui=True` | 追加 `build_a2ui_toolset(catalog=self.a2ui_catalog)` [F-033] |
| `enable_tunnel=True` | 追加 `TunnelToolset(agent_name=self.name)` [F-033] |
| `enable_dataset_gen=True` | 注册 `dataset_auto_gen_callback` 到 `after_agent_callback` [F-033] |

### 第五步：Tracers 初始化

调用 `_prepare_tracers()` 方法，通过环境变量 `ENABLE_APMPLUS`、`ENABLE_COZELOOP`、`ENABLE_TLS` 启用对应 exporter [F-037]。无 tracer 时创建默认的 `OpentelemetryTracer`。支持 APMPlus、Cozeloop、TLS 三个 exporter，并初始化全局 `meter_uploader`。

## 流程选择：_llm_flow

`_llm_flow` 是一个属性，返回 `BaseLlmFlow` 实例，决定 Agent 的推理流程 [F-038]：

- 无子代理且禁止转移时：返回 `SingleFlow`（或 `SupervisorSingleFlow`）
- 否则：返回 `AutoFlow`（或 `SupervisorAutoFlow`）
- `enable_supervisor=True` 时使用监督者版本的 Flow

`SingleFlow` 适用于单 Agent 直接调用 LLM 的场景；`AutoFlow` 适用于有子代理需要自动转移的场景。

## 运行时调度：_run_async_impl

```python
async def _run_async_impl(self, ctx: "InvocationContext") -> AsyncGenerator["Event", None]
```

当 `runtime == "adk"`（默认）时，委托给父类 `LlmAgent._run_async_impl` [F-039]。其他运行时（`"codex"` 或 `"piagent"`）通过 `veadk.runtime.get_runtime(self.runtime).run_async(self, ctx)` 调度到替代运行时实现 [F-039]。这使得 Agent 可以在 ADK 原生推理循环和外部 Agent harness（如 Claude Code SDK）之间切换。

在 ADK 1.x 版本中，`run` 方法抛出 `NotImplementedError`，提示使用 `runner.run_async` [F-040]。

## 技能加载机制

`load_skills()` 方法负责技能的动态加载 [F-035]：

1. **模式判定**：无 `AGENTKIT_TOOL_ID` 环境变量时为 `"local"` 模式（已标记弃用警告）；否则通过 AgentKit API 获取工具类型，判定为 `"skills_sandbox"` 或 `"aio_sandbox"`
2. **技能来源**：本地模式从目录加载（`load_skills_from_directory`），沙箱模式从云端加载（`load_skills_from_cloud`）
3. **指令增强**：将技能名称和描述追加到 `instruction`
4. **工具挂载**：追加 `SkillsToolset(self.skills_dict, self.skills_mode)` 到 tools

## 模型更新

`update_model(self, model_name: str)` 方法通过 Pydantic 的 `model_copy` 更新底层模型实例：

```python
self.model = self.model.model_copy(update={"model": f"{self.model_provider}/{model_name}"})
```

这允许在运行时切换模型而不重建 Agent [F-034]。

## 相关概念

- [veadk-python 概览](/concepts/00-overview.md)
- [AgentBuilder 与 YAML 配置驱动](/concepts/02-agent-builder.md)
- [Agent 类型体系](/concepts/03-agent-types.md)
- [Runner 运行器](/concepts/05-runner.md)
- [LLM 模型抽象](/concepts/07-llm-models.md)
