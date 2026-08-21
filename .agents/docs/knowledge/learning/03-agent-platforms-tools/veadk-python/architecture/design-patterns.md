---
id: veadk-python-design-patterns
title: 架构模式：核心设计模式解析
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 设计模式
- 继承扩展
- 策略模式
- 装饰器模式
- 单例模式
- 回调链
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 7个核心设计模式深度解析：继承扩展模式、条件插件挂载、回调链、运行时策略、配置降级、RunProcessor装饰器链、凭证服务单例
wiki_version: '1.0'
---


# 架构模式：核心设计模式解析

VeADK 在保持与 Google ADK 生态兼容的同时，运用了一系列经典且实用的设计模式来解决框架扩展问题。本文档基于代码库的深入分析，提炼出 7 个核心设计模式，每个模式包含问题背景、实现方式、代码位置引用和使用注意事项。

---

## 模式 1：继承扩展模式（Inheritance Extension Pattern）

### 解决什么问题

在不 fork 原有框架、不破坏生态兼容性的前提下，增量添加企业级能力。Google ADK 已经提供了成熟的 Agent、Runner、Tool 抽象和执行引擎，如果从头重写会导致生态割裂，用户无法复用现有工具和示例。

### 实现方式

**核心思想**：直接继承 Google ADK 的核心类，在子类的 `model_post_init`（Pydantic 后置初始化钩子）中增量挂载 VeADK 扩展能力，不重写父类的核心执行逻辑。

**类继承关系**：

```python
# google.adk.agents.LlmAgent 是父类
from google.adk.agents import LlmAgent

class Agent(LlmAgent):
    """VeADK Agent，继承 LlmAgent 并添加火山引擎能力"""
    # VeADK 新增字段
    knowledgebase: Optional[KnowledgeBase] = None
    short_term_memory: Optional[ShortTermMemory] = None
    long_term_memory: Optional[LongTermMemory] = None
    tracers: list[BaseTracer] = []
    enable_authz: bool = False
    runtime: Literal["adk", "codex", "piagent"] = "adk"
    # ... 更多扩展字段

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(None)  # 第一步：确保父类初始化完成
        # 后续步骤：挂载 VeADK 扩展能力
```

**代码位置**：[veadk/agent.py:72](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L72)

Runner 同样采用此模式：

```python
from google.adk.runners import Runner as ADKRunner

class Runner(ADKRunner):
    """VeADK Runner，继承 ADK Runner"""
    def __init__(self, agent, short_term_memory=None, ...):
        # 增量添加 VeADK 特有逻辑
        super().__init__(...)
```

**代码位置**：[veadk/runner.py:329](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L329-L329)

### 关键特征

1. **`super().model_post_init(None)` 优先调用**：第 215 行首先确保父类初始化完成，再进行扩展
2. **不重写核心执行方法**：`_run_async_impl` 中 `"adk"` runtime 直接调用 `super()._run_async_impl(ctx)`，完全复用父类执行循环
3. **通过新增字段开关能力**：所有 VeADK 新增能力都有默认值（`None`/`False`/`"adk"`），保持与父类行为一致
4. **扩展点在初始化时挂载**：工具、回调、记忆等在 `model_post_init` 中通过 `self.tools.append()` 注入

### 使用注意事项

- ✅ **兼容保证**：所有为 Google ADK 编写的代码可在 VeADK 中直接运行
- ⚠️ **工具列表副作用**：初始化后 `self.tools` 会被自动追加工具，用户传入的初始 tools 列表会被修改
- ⚠️ **方法重写风险**：如需重写父类方法，务必调用 `super()` 并保持接口兼容
- ⚠️ **版本兼容**：VeADK 包含 ADK 版本判断逻辑（[veadk/agent.py:743-751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L743-L751)），升级 ADK 版本时需注意兼容性

---

## 模式 2：条件插件挂载模式（Conditional Plugin Mounting Pattern）

### 解决什么问题

框架提供了丰富的可选能力（知识库、长期记忆、A2UI、Tunnel、授权检查等），但不是每个 Agent 都需要全部功能。如何让用户"开箱即用"而又不强制加载所有依赖？

### 实现方式

**核心思想**：在 `model_post_init` 中通过一系列 `if` 条件判断，仅当用户传入对应实例或设置 enable 标志位为 True 时，才**延迟导入**对应模块并挂载工具/回调。

**典型实现代码**：

```python
# 模式：if 条件判断 → 延迟导入 → 实例化 → append 到 tools/callbacks

# 示例1：knowledgebase 条件挂载（第306-324行）
if self.knowledgebase:
    from veadk.tools.builtin_tools.load_knowledgebase import (
        LoadKnowledgebaseTool,
    )  # 延迟导入，避免不需要 kb 时引入依赖
    load_knowledgebase_tool = LoadKnowledgebaseTool(knowledgebase=self.knowledgebase)
    self.tools.append(load_knowledgebase_tool)  # 挂载到工具列表

# 示例2：enable_authz 标志位挂载（第335-349行）
if self.enable_authz:
    from veadk.tools.builtin_tools.agent_authorization import (
        check_agent_authorization,
    )
    # 回调链双形态处理（详见模式3）
    if self.before_agent_callback:
        if isinstance(self.before_agent_callback, list):
            self.before_agent_callback.append(check_agent_authorization)
        else:
            self.before_agent_callback = [
                self.before_agent_callback,
                check_agent_authorization,
            ]
    else:
        self.before_agent_callback = check_agent_authorization

# 示例3：enable_tunnel 标志位挂载（第418-422行）
if self.enable_tunnel:
    logger.info("Tunnel enabled")
    from veadk.tunnel import TunnelToolset
    self.tools.append(TunnelToolset(agent_name=self.name))
```

**代码位置**：[veadk/agent.py:306-438](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L306-L438)

### 挂载条件类型汇总

| 条件类型 | 示例 | 挂载位置 |
|---|---|---|
| **实例传入** | `knowledgebase=kb_instance` | 传入非 None 对象即启用 |
| **布尔标志位** | `enable_authz=True` | 显式设置 True 才启用 |
| **列表非空** | `skills=["skill1", "skill2"]` | 列表有元素时触发加载 |

### 使用注意事项

- ✅ **零配置开箱即用**：`Agent(name="demo")` 即可工作，无需手动配置工具
- ✅ **可选依赖隔离**：延迟导入使得 codex/piagent/飞书等可选依赖在未使用时不会触发 ImportError
- ⚠️ **隐式行为**：工具列表被自动修改，初始化后建议检查 `agent.tools` 确认实际挂载的工具
- ⚠️ **对象传入即启用**：`knowledgebase=kb` 和 `long_term_memory=ltm` 只要传入非 None 就会自动挂载对应工具，无需额外 enable 标志
- ⚠️ **条件分支调试**：某个功能未按预期启用时，需要逐条件检查对应标志位或实例是否正确设置

---

## 模式 3：回调链模式（Callback Chain Pattern）

### 解决什么问题

多个功能模块都需要在 Agent 执行前后、工具调用前后插入逻辑（授权检查、动态技能加载、会话自动保存、数据集生成等），如何让这些回调有序执行而不互相冲突？如何同时支持"简单场景传单个函数"和"复杂场景传函数列表"两种 API 形态？

### 实现方式

**核心思想**：支持单函数/列表双形态自适应，每次添加回调时自动进行形态归一化——单函数自动升级为列表，新回调 append 到链尾。

**回调挂载逻辑模板**（在 `model_post_init` 中重复出现 4 次）：

```python
if self.before_agent_callback:
    if isinstance(self.before_agent_callback, list):
        # 已是列表：直接 append
        self.before_agent_callback.append(new_callback)
    else:
        # 是单函数：升级为 [原回调, 新回调] 列表
        self.before_agent_callback = [
            self.before_agent_callback,
            new_callback,
        ]
else:
    # 不存在：直接赋值为单个函数（保持简单场景API简洁）
    self.before_agent_callback = new_callback
```

**代码位置示例**（authz 回调）：[veadk/agent.py:340-349](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L340-L349)

### 三个回调点

| 回调点 | 触发时机 | VeADK 挂载的回调 | 代码位置 |
|---|---|---|---|
| `before_agent_callback` | Agent 执行前 | `check_agent_authorization`、动态技能加载回调 | [veadk/agent.py:340-349](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L340-L349)、[veadk/agent.py:603-612](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L603-L612) |
| `before_tool_callback` | 每个工具调用前 | 技能清单检查回调 `init_skill_check_list` | [veadk/agent.py:388-397](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L388-L397) |
| `after_agent_callback` | Agent 执行后 | `save_session_to_long_term_memory`、`dataset_auto_gen_callback` | [veadk/agent.py:364-375](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L364-L375)、[veadk/agent.py:429-438](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L429-L438) |

### "宽容输入、严格输出" API 设计策略

| 用户传入形态 | 内部存储形态 | 适用场景 |
|---|---|---|
| 单个函数 `callback=my_func` | 单个函数或列表 | 简单场景，只有一个回调 |
| 列表 `callback=[func1, func2]` | 列表 | 复杂场景，多回调有序执行 |

框架接受宽松的输入形态，内部自动归一化处理，降低 API 使用门槛。

### 使用注意事项

- ✅ **简单易用**：单回调场景无需创建列表，直接传函数即可
- ⚠️ **执行顺序隐式**：框架内部自动添加的回调 append 顺序决定执行顺序，用户无法显式控制
  - `before_agent_callback` 顺序：authz → dynamic_load_skills
- ⚠️ **无去重逻辑**：同一回调函数被多次添加会重复执行，自定义回调应做好幂等性设计
- ⚠️ **类型不一致**：运行时回调字段类型可能是函数或列表，遍历执行前需 `isinstance(callback, list)` 判断
- 💡 **建议**：如需精确控制顺序，直接传入列表形式，初始化后检查回调链

---

## 模式 4：运行时策略模式（Runtime Strategy Pattern）

### 解决什么问题

不同场景需要不同的 Agent 执行引擎：
- 默认场景使用 Google ADK 原生 LlmFlow（最稳定、功能最完整）
- 代码生成场景需要使用 OpenAI Codex SDK
- 本地编程助手场景需要调用 PiAgent 本地二进制

如何在不修改上层代码（Runner、会话管理、Tracing）的前提下，灵活切换底层执行循环？

### 实现方式

**核心思想**：经典策略模式 + 桥接模式 + 工厂模式组合：
1. **策略接口**：`BaseRuntime` 抽象基类定义统一的 `run_async()` 接口
2. **具体策略**：`CodexRuntime`、`PiAgentRuntime` 实现接口，桥接外部执行引擎
3. **策略工厂**：`get_runtime()` 工厂函数根据名称创建并缓存（`@lru_cache`）运行时实例
4. **上下文分发**：Agent 根据 `runtime` 字段分发到对应策略，`"adk"` 直接走父类实现

**策略分发代码**：

```python
# veadk/agent.py:733-741
if self.runtime == "adk":
    # 默认策略：直接使用父类 ADK 原生执行循环
    async for event in super()._run_async_impl(ctx):
        yield event
    return

# 其他策略：通过工厂获取对应 runtime 桥接
from veadk.runtime import get_runtime
async for event in get_runtime(self.runtime).run_async(self, ctx):
    yield event
```

**代码位置**：[veadk/agent.py:733-741](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L733-L741)

**工厂函数带缓存和可选依赖隔离**：

```python
# veadk/runtime/__init__.py:32-64
from functools import lru_cache

@lru_cache(maxsize=None)  # 单例缓存，避免重复创建运行时
def get_runtime(name: str) -> BaseRuntime:
    if name == "codex":
        try:
            from veadk.runtime.codex import CodexRuntime
        except ModuleNotFoundError as e:
            raise ImportError(
                f"The 'codex' runtime requires extra dependencies (missing: {e.name}). "
                "Install them with: pip install openai-codex fastapi uvicorn"
            ) from e
        return CodexRuntime()
    if name == "piagent":
        from veadk.runtime.piagent import PiAgentRuntime
        return PiAgentRuntime()
    raise ValueError(f"Unknown runtime: {name!r}")
```

**代码位置**：[veadk/runtime/__init__.py:32-64](file:///d:/AI/.chaos/libs/veadk-python/veadk/runtime/__init__.py#L32-L64)

**策略接口定义**：

```python
# veadk/runtime/base_runtime.py
class BaseRuntime(ABC):
    @abstractmethod
    async def run_async(
        self, agent: Agent, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """统一接口：输入 Agent 和上下文，输出 ADK 标准 Event 流"""
        ...
```

### 桥接模式价值

`BaseRuntime` 作为桥接层，将**变化的执行循环**（Codex SDK、PiAgent 二进制）与**不变的外围设施**（Runner 会话管理、ShortTermMemory、Tracing、RunProcessor）解耦。所有 runtime 最终都输出 ADK 标准 Event 流，上层代码无需感知底层切换。

### 使用注意事项

- ✅ **扩展性好**：新增 runtime 只需继承 `BaseRuntime` 并在 `get_runtime` 中注册
- ✅ **依赖隔离**：codex 的 ImportError 被捕获并给出明确安装提示，未安装 codex 不影响其他功能
- ✅ **性能优化**：`@lru_cache` 确保 runtime 实例只创建一次
- ⚠️ **功能差异**：非 adk runtime 不经过 ADK 原生 LlmFlow，部分高级特性（如 sub_agents 复杂编排）行为可能不一致
- ⚠️ **版本兼容**：ADK 1.x 和 2.x 的 run 方法签名有差异，框架包含版本判断逻辑
- 💡 **建议**：生产环境固定 runtime 类型，默认使用 `"adk"` 获得最完整功能支持

---

## 模式 5：配置降级模式（Configuration Fallback Chain Pattern）

### 解决什么问题

API Key、模型配置、云凭证等在不同部署环境下有不同的配置来源：本地开发用 `.env` 文件、容器部署用环境变量、企业级场景用密钥轮换服务、快速原型用配置文件默认值。如何让一套代码适配所有场景？

### 实现方式

**核心思想**：建立严格的优先级链，高优先级配置存在时直接使用，不存在时自动降级到下一级，直到找到可用配置。每一级降级都有明确的适用场景。

**API Key 四级优先级链**（最典型的例子）：

```python
# veadk/agent.py:223-232
if not self.model_api_key:
    env_key = os.getenv("MODEL_AGENT_API_KEY")
    if env_key:
        # 优先级2：环境变量注入（容器化/CI-CD 场景）
        self.model_api_key = env_key
    elif self.model_api_key_name:
        # 优先级3：ARK Token 服务（企业级密钥轮换场景）
        from veadk.auth.veauth.ark_veauth import get_ark_token
        self.model_api_key = get_ark_token(api_key_name=self.model_api_key_name)
    else:
        # 优先级4：配置文件默认值（快速原型场景）
        self.model_api_key = settings.model.api_key
# 优先级1（最高）：显式传入的 model_api_key 参数（多租户动态切换场景）
```

**代码位置**：[veadk/agent.py:223-232](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L223-L232)

### 优先级链对照表

| 优先级 | 配置来源 | 适用场景 | 示例 |
|---|---|---|---|
| 1（最高） | 显式构造参数 | 多租户动态切换、运行时动态 key | `Agent(model_api_key="sk-xxx")` |
| 2 | 环境变量 | 容器化部署、CI/CD、12-Factor 应用 | `MODEL_AGENT_API_KEY=sk-xxx` |
| 3 | ARK Token 服务（key_name） | 企业级密钥轮换、细粒度权限控制 | `Agent(model_api_key_name="my-key")` |
| 4（最低） | `settings.model.api_key` 配置文件 | 本地快速原型开发 | `config.yaml` 中的默认值 |

### 其他降级链示例

**云服务凭证链**（与 API Key 模式一致）：
1. 显式传入 `access_key`/`secret_key` 参数
2. `VOLCENGINE_ACCESS_KEY`/`VOLCENGINE_SECRET_KEY` 环境变量
3. VEFAAS IAM 角色自动获取（含 `session_token`）

**代码位置**：[veadk/agent.py:477-490](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L477-L490)

**模型 Fallback 链**（故障转移）：
- `model_name` 为列表时，第一个为主模型，其余为 fallback 模型
- 主模型限流/故障时自动切换到 fallback 模型

**代码位置**：[veadk/agent.py:258-273](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L258-L273)

**BytePlus 环境变量自动映射**：
- `BYTEPLUS_ACCESS_KEY` → `VOLCENGINE_ACCESS_KEY`
- `BYTEPLUS_SECRET_KEY` → `VOLCENGINE_SECRET_KEY`

**代码位置**：[veadk/config.py:54-61](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L54-L61)

### 使用注意事项

- ✅ **灵活适配**：不同部署环境使用不同配置方式，代码无需改动
- ✅ **生产安全**：推荐生产环境用环境变量注入，避免硬编码密钥
- ⚠️ **调试困难**：认证失败时需按优先级反向排查（显式参数 → 环境变量 → ARK 服务 → 配置文件）
- ⚠️ **get_ark_token 网络依赖**：第三级需要调用 ARK API，网络故障会导致初始化失败
- 💡 **建议**：认证失败时开启 debug 日志，确认当前生效的配置来源

---

## 模式 6：RunProcessor 装饰器链（Decorator Chain / Middleware Pattern）

### 解决什么问题

认证（OAuth2 流程）、日志、监控、重试等属于**横切关注点**——它们不直接参与 Agent 业务逻辑，但需要在每次执行时介入。如何在不修改 Agent/Runner 核心代码的前提下，透明地拦截和处理执行流？

### 实现方式

**核心思想**：Python 装饰器模式在异步生成器层面的变体，类似 WSGI/ASGI 中间件。`process_run()` 返回一个高阶函数（装饰器），该装饰器接收原始事件生成器函数，返回包装后的新生成器。包装器可以在事件流前后执行逻辑、注入事件、过滤事件、甚至暂停等待用户输入。

**抽象基类定义**：

```python
# veadk/processors/base_run_processor.py:27-88
from abc import ABC, abstractmethod
from typing import Callable, AsyncGenerator

class BaseRunProcessor(ABC):
    @abstractmethod
    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[
        [Callable[[], AsyncGenerator]],
        Callable[[], AsyncGenerator]
    ]:
        """返回一个装饰器函数，用于包装事件生成器"""
        pass
```

**NoOp 默认实现**（恒等装饰器，无开销）：

```python
# veadk/processors/base_run_processor.py:91-120
class NoOpRunProcessor(BaseRunProcessor):
    def process_run(self, runner, message, **kwargs):
        def decorator(event_generator_func):
            return event_generator_func  # 直接返回原函数，无任何包装
        return decorator
```

**Runner 中的应用点**（使用 Python `@decorator` 语法糖）：

```python
# veadk/runner.py:541-553
@(run_processor or self.run_processor).process_run(
    runner=self, message=converted_message
)
async def event_generator():
    async for event in self.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=converted_message,
        run_config=run_config,
    ):
        yield event

async for event in event_generator():
    # 处理事件...
```

**代码位置**：[veadk/runner.py:541-553](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L541-L553)

**三级 RunProcessor 优先级**：

1. `runner.run(message, run_processor=...)` 方法参数（单次运行临时覆盖）
2. `Runner(..., run_processor=...)` 构造参数
3. `Agent(run_processor=...)` 实例配置
4. 默认 `NoOpRunProcessor`

**代码位置**：[veadk/runner.py:406-414](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L406-L414)

### 实际应用案例：OAuth2 认证处理器

`AuthRequestProcessor` 实现了完整的"对话中断-认证-恢复"流程：

```python
# 伪代码示意（实际实现在 veadk/integrations/ve_identity/auth_processor.py）
class AuthRequestProcessor(BaseRunProcessor):
    def process_run(self, runner, message, **kwargs):
        def decorator(event_generator_func):
            async def wrapper():
                # 前置：检测是否需要认证
                if need_auth(message):
                    # 注入认证请求事件（不调用原始生成器）
                    yield AuthRequestEvent(...)
                    # 循环轮询等待用户完成 OAuth 授权
                    while not auth_completed():
                        await asyncio.sleep(1)
                        yield AuthPendingEvent(...)
                # 认证通过后，恢复执行原始事件流
                async for event in event_generator_func():
                    yield event
            return wrapper
        return decorator
```

**代码位置**：[veadk/integrations/ve_identity/auth_processor.py:271-286](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/auth_processor.py#L271-L286)

### 使用注意事项

- ✅ **解耦彻底**：认证/日志/监控等横切逻辑与业务代码完全分离
- ✅ **事件注入能力**：Processor 可以 yield 自定义 Event 实现交互流程
- ✅ **透明包装**：包装后的 `event_generator` 对外接口与原始一致，Runner 主流程无感知
- ⚠️ **事件转发必须完整**：自定义 Processor 务必使用 `async for event in event_generator_func(): yield event` 转发所有事件，避免事件丢失
- ⚠️ **异步生成器调试复杂**：嵌套的装饰器 wrapper 会增加异常栈深度
- 💡 **建议**：单次运行临时启用 Processor 时，通过 `run_processor` 参数传入，不污染全局配置

---

## 模式 7：凭证服务单例模式（Credential Service Singleton）

### 解决什么问题

OAuth token、API Key 等凭证需要在整个应用中按 `app_name` + `user_id` 隔离存储和访问，避免重复创建服务实例，提供统一的凭证存取接口。

### 实现方式

**核心思想**：继承 Google ADK 的 `BaseCredentialService`，扩展支持按 `app_name`/`user_id` 直接访问的三层字典存储结构。虽然不是经典的 GoF 单例（通过类变量强制唯一实例），但在 Runner 中作为统一入口被所有组件共享使用，逻辑上是单例。

**类定义**：

```python
# veadk/auth/ve_credential_service.py:36-80
from google.adk.auth.credential_service.base_credential_service import (
    BaseCredentialService,
)

class VeCredentialService(BaseCredentialService):
    """支持按 app_name/user_id 直接访问的内存凭证服务"""

    def __init__(self):
        super().__init__()
        # 三层字典存储：{app_name: {user_id: {credential_key: AuthCredential}}}
        self._credentials: dict[str, dict[str, dict[str, AuthCredential]]] = {}

    async def set_credential(
        self,
        app_name: str,
        user_id: str,
        credential_key: str,
        credential: AuthCredential,
    ) -> None:
        """直接按 app_name/user_id 设置凭证"""
        if app_name not in self._credentials:
            self._credentials[app_name] = {}
        if user_id not in self._credentials[app_name]:
            self._credentials[app_name][user_id] = {}
        self._credentials[app_name][user_id][credential_key] = credential

    async def get_credential(
        self,
        app_name: str,
        user_id: str,
        credential_key: str,
    ) -> Optional[AuthCredential]:
        """直接按 app_name/user_id 获取凭证"""
        return self._credentials.get(app_name, {}).get(user_id, {}).get(credential_key)
```

**代码位置**：[veadk/auth/ve_credential_service.py:36-100](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/ve_credential_service.py#L36-L100)

**ADK 标准接口兼容**：

`load_credential`/`save_credential` 方法从 `CallbackContext` 中提取 `app_name` 和 `user_id`，再委托给 `get_credential`/`set_credential`，保持与 ADK 生态的兼容：

```python
@override
async def load_credential(self, auth_config, callback_context):
    app_name = callback_context._invocation_context.app_name
    user_id = callback_context._invocation_context.user_id
    return await self.get_credential(app_name, user_id, auth_config.credential_key)
```

**代码位置**：[veadk/auth/ve_credential_service.py:82-100](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/ve_credential_service.py#L82-L100)

### 存储结构

```
_credentials = {
    "my_app": {                     # app_name 隔离
        "user_123": {               # user_id 隔离
            "bearer_token": AuthCredential(...),
            "oauth_refresh": AuthCredential(...),
        },
        "user_456": {
            "bearer_token": AuthCredential(...),
        }
    },
    "another_app": { ... }
}
```

### 使用注意事项

- ✅ **双层隔离**：app_name + user_id 双层 key 天然支持多租户场景
- ✅ **ADK 兼容**：同时支持标准 ADK 接口和 VeADK 扩展的直接访问接口
- ⚠️ **内存存储**：当前实现使用进程内字典存储，重启丢失数据；生产环境如需持久化，可继承扩展
- ⚠️ **线程安全**：异步环境下多协程并发访问需注意竞态条件（当前依赖 asyncio 单线程事件循环模型）
- 💡 **建议**：生产环境如需跨进程/跨副本凭证共享，需替换为 Redis/数据库持久化实现

---

## 设计模式总结

| 模式名称 | 类型 | 解决的核心问题 | 关键代码位置 |
|---|---|---|---|
| 继承扩展模式 | 结构型 | 保持生态兼容的同时增量扩展能力 | [veadk/agent.py:72](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L72) |
| 条件插件挂载模式 | 行为型 | 可选能力按需启用、延迟导入隔离依赖 | [veadk/agent.py:306-438](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L306-L438) |
| 回调链模式 | 行为型 | 多回调有序执行、双形态自适应 API | [veadk/agent.py:340-349](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L340-L349) |
| 运行时策略模式 | 行为型 | 多执行引擎可切换、上层代码无感知 | [veadk/runtime/__init__.py:32-64](file:///d:/AI/.chaos/libs/veadk-python/veadk/runtime/__init__.py#L32-L64) |
| 配置降级模式 | 行为型 | 多部署环境配置适配、多级 fallback | [veadk/agent.py:223-232](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L223-L232) |
| RunProcessor 装饰器链 | 结构型 | 横切关注点中间件、事件流拦截注入 | [veadk/processors/base_run_processor.py:27-88](file:///d:/AI/.chaos/libs/veadk-python/veadk/processors/base_run_processor.py#L27-L88) |
| 凭证服务单例模式 | 创建型 | 多租户凭证统一存储、双层隔离 | [veadk/auth/ve_credential_service.py:36-100](file:///d:/AI/.chaos/libs/veadk-python/veadk/auth/ve_credential_service.py#L36-L100) |

这些设计模式共同体现了 VeADK 的架构哲学：**兼容优先、渐进式复杂度、容错设计、约定优于配置**。简单场景使用默认值开箱即用，高级场景通过模式提供的扩展点自定义，API 形态随需求自然升级。

---

## 下一步阅读

- [架构概览](overview.md)：回到整体架构总览
- [Agent 生命周期与执行流程](agent-lifecycle.md)：了解 19 步初始化和 Runner 执行机制
- [模块依赖关系](module-dependencies.md)：了解分层架构和模块依赖约束
