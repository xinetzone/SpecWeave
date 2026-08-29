---
type: Concept
title: 服务注册表
description: 掌握 Home Assistant 服务注册表机制，包括 Service/ServiceCall/ServiceRegistry 的结构、async_register/async_call 方法、实体服务装饰器、响应支持模式和服务描述系统
tags: [home-assistant, smart-home, service-registry, service, service-call, core]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: helpers-util-source
    resource: "/references/helpers-util-source.md"
    title: Home Assistant Helpers 与 Util 源码
  - id: facts-core
    resource: "/references/facts-core.md"
    title: Home Assistant Core 事实清单
---

# 服务注册表

服务注册表（ServiceRegistry）是 Home Assistant 中管理所有可调用服务的核心子系统。服务是 HA 对外暴露操作能力的标准方式——打开灯光、调用脚本、触发自动化，都通过服务调用完成。服务注册表通过 `hass.services` 访问，与[事件总线](/concepts/06-event-bus.md)和[状态机](/concepts/07-state-machine.md)并列为三大核心子系统。

## 核心概念

### Service

`Service` 类定义于 `core.py:2488`，是已注册服务的内部表示：

```python
class Service:
    __slots__ = ("description_placeholders", "job", "schema", "supports_response")

    def __init__(self, func, job_type=None, schema=None,
                 description_placeholders=None, supports_response=SupportsResponse.NONE):
        self.job = HassJob(func, f"service {domain}.{service}")
        self.schema = schema
        self.supports_response = supports_response
```

- `job`：`HassJob` 实例，包装服务处理函数，自动判断执行方式（协程/回调/线程池）
- `schema`：voluptuous 验证模式，用于校验和强制转换服务调用参数
- `supports_response`：服务响应支持模式
- `description_placeholders`：描述中的占位符变量

### SupportsResponse

`SupportsResponse` 是 `StrEnum`（`core.py:2475-2485`），定义服务对响应数据的支持级别：

```python
class SupportsResponse(StrEnum):
    NONE = "none"        # 不支持响应（默认）
    OPTIONAL = "optional"  # 可选返回响应
    ONLY = "only"        # 只读服务，调用方必须请求响应
```

- `NONE`：服务执行操作但不返回数据，如 `light.turn_on`
- `OPTIONAL`：服务可返回数据，调用方可选择是否请求，如 `calendar.get_events`
- `ONLY`：服务仅查询数据且必须返回，调用时必须设置 `return_response=True`

### ServiceCall

`ServiceCall` 类定义于 `core.py:2522`，封装一次服务调用的所有上下文：

```python
class ServiceCall:
    __slots__ = ("context", "data", "domain", "hass", "return_response", "service")

    domain: str           # 服务域，如 "light"
    service: str          # 服务名，如 "turn_on"
    data: ReadOnlyDict    # 服务参数（只读）
    context: Context      # 调用上下文
    return_response: bool # 是否请求响应数据
```

ServiceCall 构造时，data 被包装为 `ReadOnlyDict` 防止修改；若未提供 context，自动创建新 Context。

### ServiceResponse

类型别名定义于 `core.py:126-127`：

```python
ServiceResponse = JsonObjectType | None
EntityServiceResponse = dict[str, ServiceResponse]
```

`EntityServiceResponse` 用于实体服务（见下文），以 entity_id 为键映射每个实体的响应。

## ServiceRegistry 实现

`ServiceRegistry` 类定义于 `core.py:2556`，在 `HomeAssistant.__init__` 中通过 `self.services = ServiceRegistry(self)` 创建。

### 内部存储

```python
class ServiceRegistry:
    __slots__ = ("_hass", "_services")

    def __init__(self, hass):
        self._hass = hass
        self._services: dict[str, dict[str, Service]] = {}
```

服务按两级字典组织：`domain -> service_name -> Service`。例如 `light.turn_on` 存储在 `_services["light"]["turn_on"]`。

### 注册服务

`async_register()` 方法（`core.py:2649`）注册新服务：

```python
async def async_register(
    self,
    domain: str,
    service: str,
    service_func: Callable,
    schema: vol.Schema | None = None,
    *,
    supports_response: SupportsResponse = SupportsResponse.NONE,
    description_placeholders: dict[str, str] | None = None,
) -> None:
```

注册流程：

1. 验证当前线程为事件循环线程（`verify_event_loop_thread`）
2. domain 和 service 名都转小写
3. 创建 `Service` 实例包装处理函数
4. 存入 `_services` 字典
5. 触发 `EVENT_SERVICE_REGISTERED` 事件

注册示例：

```python
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
import voluptuous as vol

DOMAIN = "my_integration"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    async def handle_reboot(call: ServiceCall) -> None:
        device_id = call.data["device_id"]
        await reboot_device(device_id)

    hass.services.async_register(
        DOMAIN,
        "reboot",
        handle_reboot,
        schema=vol.Schema({
            vol.Required("device_id"): str,
            vol.Optional("delay", default=0): int,
        }),
    )
    return True
```

注册后，前端和 WebSocket API 自动发现该服务，用户可在开发者工具中调用。

### 移除服务

`async_remove()` 方法（`core.py:2734`）从注册表删除服务并触发 `EVENT_SERVICE_REMOVED` 事件。集成卸载时应清理其注册的服务。

### 调用服务

`async_call()` 方法（`core.py:2791`）是服务调用的核心入口：

```python
async def async_call(
    self,
    domain: str,
    service: str,
    service_data: dict | None = None,
    blocking: bool = False,
    context: Context | None = None,
    target: ServiceTarget | None = None,
    return_response: bool = False,
) -> ServiceResponse | None:
```

完整调用流程：

1. **查找 handler**：先按原名查找，再转小写查找；找不到抛出 `ServiceNotFound`
2. **响应验证**：
   - `return_response=True` 要求 `blocking=True`，否则抛出 `ServiceValidationError`
   - handler 为 `SupportsResponse.NONE` 但请求了 response → 错误
   - handler 为 `SupportsResponse.ONLY` 但未请求 response → 错误
3. **参数校验**：若 handler 有 schema，通过 schema 校验和强制转换 service_data
4. **触发事件**：调用前发布 `EVENT_CALL_SERVICE` 事件，携带 domain/service/service_data
5. **执行 handler**：
   - 非阻塞调用：通过 `async_create_task_internal` 在后台执行，异常被捕获并记录
   - 阻塞调用：await 协程完成，若请求 response 则验证返回值为 dict

### _execute_service：执行调度

`_execute_service()` 根据 `HassJob.job_type` 决定执行方式（`core.py:2929-2937`）：

- `Coroutinefunction`：直接 `await` 协程
- `Callback`：在事件循环中同步调用
- `Executor`：提交到线程池执行（用于阻塞 I/O 操作）

这使得服务处理函数可以是协程函数、回调函数或普通同步函数，框架自动选择正确的执行方式。

### 查询服务

- `async_services()`（`core.py:2571-2580`）：返回注册表的深拷贝，包含所有 domain 和 service
- `async_services_internal()`（`core.py:2592-2603`）：直接返回内部字典引用，仅供内部性能关键路径使用
- `has_service(domain, service)`（`core.py:2605-2610`）：检查服务是否存在

## 实体服务（Entity Service）

实体服务是 HA 中最常见的服务模式。一个服务调用可以同时作用于多个实体（通过 entity_id、device_id 或 area_id 定位），框架自动将调用分发给每个匹配的实体。

### entity_service 装饰器

`helpers/service.py` 中的 `entity_service` 装饰器（事实 #143）将普通函数包装为实体服务处理器：

```python
from homeassistant.helpers.service import entity_service

@entity_service
async def _async_turn_on(entity, **kwargs):
    await entity.async_turn_on(**kwargs)

hass.services.async_register(DOMAIN, "turn_on", _async_turn_on, schema=...)
```

装饰器自动完成：

1. 从 ServiceCall 中解析 target（entity_id/device_id/area_id）
2. 通过注册表展开为实体引用列表
3. 对每个实体调用被装饰函数
4. 若函数请求响应，收集每个实体的返回值为 `EntityServiceResponse`

装饰器支持参数：

- `required_features`：要求实体支持特定功能标志（`LightEntityFeature.TRANSITION` 等），不支持的实体被跳过
- `filter`：自定义实体过滤函数

### EntityComponent 注册

平台集成通常通过 `EntityComponent.async_register_entity_service()` 注册实体服务（事实 #214）：

```python
component.async_register_entity_service(
    SERVICE_TURN_ON,
    LIGHT_TURN_ON_SCHEMA,
    "async_turn_on",
    [LightEntityFeature.TRANSITION],
)
```

第三个参数可以是字符串（实体方法名）或可调用对象。这种方式自动关联到平台管理的所有实体。

## 服务调用示例

### 基本调用

```python
await hass.services.async_call(
    "light", "turn_on",
    service_data={
        "entity_id": "light.living_room",
        "brightness": 255,
        "color_name": "red",
    },
    blocking=True,
)
```

### 请求响应

```python
result = await hass.services.async_call(
    "calendar", "get_events",
    service_data={
        "entity_id": "calendar.work",
        "duration": {"hours": 24},
    },
    blocking=True,
    return_response=True,
)
events = result["events"]
```

### 通过 target 指定目标

```python
from homeassistant.helpers.service import ServiceTarget

await hass.services.async_call(
    "light", "turn_off",
    target=ServiceTarget(area_id="living_room"),
    blocking=True,
)
```

框架自动将区域展开为该区域内所有灯光实体。

## 服务描述系统

服务不仅需要代码注册，还需要提供人类可读的描述信息。

### services.yaml

每个集成在 `services.yaml` 文件中定义服务的描述、字段说明和目标选择器。hassfest 的 services 验证器（`script/hassfest/services.py`）会检查：

- 注册了服务但没有 services.yaml 描述 → 报错
- services.yaml 中定义了但代码未注册的服务 → 报错
- 核心集成的服务必须在 `strings.json` 中有翻译条目
- 核心集成的每个服务必须在 `icons.json` 中有对应图标

### 编程式描述

`helpers/service.py` 提供描述管理函数（事实 #145-147）：

- `async_get_all_descriptions(hass)`：获取所有服务的完整描述
- `async_get_descriptions(hass, domain)`：获取指定域的服务描述
- `async_set_descriptions(hass, domain, descriptions)`：编程式设置描述

这些函数用于支持通过 ConfigEntry 动态注册服务的集成，其描述可能不适合静态 YAML 文件。

### 管理员服务

`async_register_admin_service()`（事实 #148）注册需要管理员权限的服务。普通用户无法调用管理员服务，WebSocket API 和 REST API 都会进行权限检查。

## 服务调用事件流

```text
调用方 → hass.services.async_call("light", "turn_on", {...})
    │
    ├─ 1. 查找 Service handler
    ├─ 2. 验证 response/blocking 约束
    ├─ 3. schema 校验/转换 service_data
    │
    ├─ 4. bus.async_fire("call_service", {domain, service, service_data})
    │       └─ 日志记录、审计、自动化监听
    │
    └─ 5. _execute_service(handler, call)
            ├─ [协程] await func(call)
            ├─ [回调] func(call)
            └─ [线程池] run_in_executor(func, call)
                    │
                    ▼
            实体状态变化 → StateMachine.async_set()
                    │
                    ▼
            EventBus 发布 state_changed
```

`EVENT_CALL_SERVICE` 在服务执行**之前**触发，这使得日志系统可以记录所有服务调用，自动化可以监听服务调用作为触发器。

## 辅助函数

### async_call_from_config

`helpers/service.py` 中的 `async_call_from_config()`（事实 #141）从配置字典调用服务，解析 `service`、`target`、`data`、`entity_id` 字段。这是脚本和自动化执行服务调用动作的内部实现。

### async_extract_from_service

`async_extract_from_service()`（事实 #144）从服务调用中提取实体引用列表，支持展开实体组（Group）。这对于需要在服务执行前后操作实体的场景非常有用。

## 延伸阅读

- [事件总线](/concepts/06-event-bus.md)
- [状态机](/concepts/07-state-machine.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [实体模型](/concepts/09-entity-model.md)

## 相关概念

- [事件总线](/concepts/06-event-bus.md) — 服务调用前后发布 call_service 事件的通信通道
- [状态机](/concepts/07-state-machine.md) — 实体服务执行后状态变化通过 StateMachine 持久化
- [实体模型](/concepts/09-entity-model.md) — async_register_entity_service 将服务注册到 Entity 平台
- [平台开发模式](/concepts/16-platform-pattern.md) — 各平台通过 async_register_entity_service 暴露平台专属服务
