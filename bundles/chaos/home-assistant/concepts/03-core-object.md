---
type: Concept
title: HomeAssistant 核心对象
description: 深入理解 HomeAssistant 根对象的属性、方法、生命周期与 CoreState 状态机，掌握 HA 运行时核心
tags: [home-assistant, smart-home, core-object, HomeAssistant, lifecycle, beginner]
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
---

# HomeAssistant 核心对象

## HomeAssistant 类概述

`HomeAssistant` 类定义于 `homeassistant/core.py:379`，是整个 Home Assistant 系统的根对象。在 HA 进程的整个生命周期中，存在且仅存在一个 `HomeAssistant` 实例，所有集成、平台和辅助代码都通过依赖注入接收这个实例（通常命名为 `hass`）。

`HomeAssistant` 采用组合模式，将各项职责委托给专门的子系统对象。它本身不实现业务逻辑，而是充当子系统的容器和协调者。理解 `HomeAssistant` 对象是理解 HA 运行时的关键。

## 核心属性

### 子系统引用

`HomeAssistant` 持有四大核心子系统的引用：

```python
class HomeAssistant:
    bus: EventBus                    # 事件总线
    states: StateMachine             # 状态机
    services: ServiceRegistry        # 服务注册中心
    config: Config                   # 核心配置
```

这四个属性在 `__init__` 中创建，在整个生命周期中不可替换。

| 属性 | 类型 | 定义位置 | 职责 |
|------|------|---------|------|
| `bus` | `EventBus` | `core.py:1442` | 事件发布与订阅 |
| `states` | `StateMachine` | `core.py:2136` | 实体状态存储与查询 |
| `services` | `ServiceRegistry` | `core.py:2556` | 服务注册与调用 |
| `config` | `Config` | `core_config.py:534` | 核心运行时配置 |

### 运行时状态

```python
class HomeAssistant:
    state: CoreState                 # 当前运行状态
    auth: AuthManager                # 认证管理器
    data: HassDict                   # 集成共享数据
```

- **`state`**：`CoreState` 枚举值，表示 HA 当前所处的生命周期阶段。
- **`auth`**：`AuthManager` 实例，管理用户、令牌和权限。在 bootstrap 阶段通过 `set_auth_manager()` 设置。
- **`data`**：`HassDict` 类型，是集成之间共享运行时数据的标准方式。集成将数据存入 `hass.data[DOMAIN]` 或 `hass.data[HassKey(...)]`。

### 其他重要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `config_entries` | `ConfigEntries` | 配置条目管理器（在 bootstrap 中设置） |
| `config.components` | `_ComponentSet` | 已加载的集成 domain 集合（通过 `hass.config.components` 访问） |
| `started` | `asyncio.Future` | HA 启动完成后 resolve 的 Future |
| `stop_track_task` | 任务引用 | 停止跟踪任务 |

## CoreState 状态机

`CoreState` 枚举定义于 `core.py:363`，描述 HA 的运行时状态：

```python
class CoreState(enum.Enum):
    not_running = "NOT_RUNNING"
    starting = "STARTING"
    running = "RUNNING"
    stopping = "STOPPING"
    final_write = "FINAL_WRITE"
    stopped = "STOPPED"
```

状态转换路径：

```text
not_running
    │
    ▼
starting ─────────────────────────┐
    │                              │
    ▼                              │
running ──stop()──→ stopping       │
    │                    │         │
    │                    ▼         │
    │              final_write     │
    │                    │         │
    │                    ▼         │
    └──────────────→ stopped ◄─────┘
```

| 状态 | 说明 |
|------|------|
| `not_running` | 初始状态，实例已创建但尚未开始启动 |
| `starting` | 正在执行 bootstrap，加载集成 |
| `running` | 完全启动，所有集成已加载，正在运行 |
| `stopping` | 收到停止信号，正在关闭集成 |
| `final_write` | 集成执行最后的数据写入（如保存状态） |
| `stopped` | 完全停止，事件循环即将关闭 |

状态通过 `state` 属性存储，外部只读访问。状态变更通过内部方法 `set_state()` 完成，该方法同时清除 `is_running`/`is_stopping` 缓存属性。

## 关键方法

### 生命周期方法

#### `async_start()`

```python
async def async_start(self) -> None:
```

将状态从 `not_running` 转为 `starting`，然后执行内部启动逻辑。完成后状态转为 `running`，并触发 `EVENT_HOMEASSISTANT_STARTED` 事件。

此方法由 `bootstrap.py` 中的启动流程调用，不应由集成直接调用。

#### `async_stop()`

```python
async def async_stop(self, exit_code: int = 0, *, force: bool = False) -> None:
```

优雅停止 HA。`exit_code` 设置进程退出码，参数 `force` 为 `True` 时跳过正常关闭流程。关闭过程：

1. 状态转为 `stopping`，触发 `EVENT_HOMEASSISTANT_STOP`
2. 等待集成清理完成
3. 状态转为 `final_write`，触发 `EVENT_HOMEASSISTANT_FINAL_WRITE`
4. 等待所有待写操作完成（最多 `TIMEOUT_EVENT_START` = 15 秒）
5. 状态转为 `stopped`，触发 `EVENT_HOMEASSISTANT_CLOSE`
6. 关闭事件总线和状态机

#### `async_block_till_done()`

```python
async def async_block_till_done(self) -> None:
```

等待事件循环中的所有待处理回调完成。这在测试中特别有用，用于确保所有异步操作都已执行完毕。内部通过循环检测事件循环的待处理任务数，直到为零。

### 事件与状态访问

`HomeAssistant` 不提供事件总线的代理方法，而是直接暴露子系统对象，通过 `hass.bus`、`hass.states`、`hass.services` 访问：

```python
hass.bus.async_fire("my_event", {"key": "value"})
unsub = hass.bus.async_listen("my_event", handler)
hass.bus.async_listen_once("homeassistant_started", on_started)
```

### 状态便捷属性

```python
@property
def is_running(self) -> bool:
    """检查 HA 是否处于 starting 或 running 状态"""

@property
def is_stopping(self) -> bool:
    """检查 HA 是否正在停止（stopping 或 final_write）"""
```

这两个属性是 `cached_property`，在集成代码中频繁使用，用于判断当前是否可以安全执行操作。状态变更时缓存自动失效。

### 组件集合

已加载的集成 domain 集合通过 `hass.config.components` 访问（类型为 `_ComponentSet`），而非 `hass.components`。集成可以通过 `"mqtt" in hass.config.components` 检查依赖是否可用。

### 数据共享：hass.data

`hass.data` 是 `HassDict` 类型，它扩展了标准字典，支持通过 `HassKey` 进行类型安全的数据存取：

```python
from homeassistant.core import HomeAssistant
from homeassistant.util.hass_dict import HassKey

DOMAIN = "my_integration"
DATA_KEY = HassKey[MyCoordinator]("my_integration_coordinator")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = MyCoordinator(hass)
    hass.data[DATA_KEY] = coordinator  # 类型安全存储
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = hass.data[DATA_KEY]  # 类型安全读取
    await coordinator.shutdown()
    del hass.data[DATA_KEY]
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

传统方式使用字符串 key：`hass.data[DOMAIN]`，但 `HassKey` 提供了更好的类型检查和 IDE 支持。

### 任务创建

```python
def async_create_task(self, target, *, name: str | None = None) -> asyncio.Task:
    """创建事件循环任务（内部使用 create_eager_task）"""
```

`async_create_task` 是创建后台任务的推荐方式。它使用 `create_eager_task`（定义于 `util/async_.py`），该函数在创建任务时立即开始执行到第一个 await 点，减少了任务调度延迟。

### 执行器调度

```python
async def async_add_executor_job(self, target, *args) -> Any:
    """在默认线程池中执行阻塞函数"""
```

当集成需要调用同步的阻塞函数（如文件 I/O、同步网络库）时，必须通过此方法将其调度到线程池，避免阻塞事件循环：

```python
def blocking_read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

async def async_setup(hass: HomeAssistant, config):
    content = await hass.async_add_executor_job(blocking_read_file, "/path/to/file")
```

## Context 上下文

`Context` 类定义于 `core.py:1218`，用于追踪操作的来源和因果关系。每个事件和服务调用都携带一个 Context：

```python
class Context:
    user_id: str | None       # 触发操作用户的 ID
    parent_id: str | None      # 父上下文 ID（事件链追踪）
    id: str                    # ULID 唯一标识
```

Context 的 ID 使用 ULID（Universally Unique Lexicographically Sortable Identifier），比 UUID 具有更好的时间排序性。ULID 生成函数 `ulid_now` 定义于 `util/ulid.py`。

Context 的用途：
- **审计追踪**：知道哪个用户触发了哪个操作
- **事件链**：通过 `parent_id` 追踪事件因果链
- **权限检查**：AuthManager 根据 `user_id` 验证权限
- **自动化去重**：识别由自动化触发的事件，避免循环

创建新 Context：

```python
from homeassistant.core import Context

# 用户操作的上下文
context = Context(user_id=user.id)

# 系统操作的上下文
system_context = Context()

# 继承父上下文
child_context = Context(parent_id=parent_context.id, user_id=parent_context.user_id)
```

## HassJob 作业包装

`HassJob` 类定义于 `core.py:295`，是 HA 对可调用对象的包装。它自动检测函数类型并决定执行方式：

```python
class HassJobType(Enum):
    Coroutinefunction = 1  # async def 函数，在事件循环中执行
    Callback = 2           # @callback 装饰的函数，在事件循环中立即执行
    Executor = 3           # 普通函数，调度到线程池执行
```

`@callback` 装饰器（`core.py:209`）标记函数为事件循环安全。被标记的函数必须：
- 不包含 I/O 操作
- 不调用阻塞函数
- 不使用 await

回调函数在事件循环中同步执行，没有协程调度开销，适合状态变更监听器等高频场景。

```python
from homeassistant.core import callback

@callback
def handle_state_change(event):
    """同步处理状态变更，在事件循环中立即执行。"""
    entity_id = event.data["entity_id"]
    new_state = event.data["new_state"]
    print(f"{entity_id} changed to {new_state.state}")

hass.bus.async_listen("state_changed", handle_state_change)
```

## 线程局部实例访问

在事件循环之外（如线程池中的同步函数），可以通过 `async_get_hass()`（`core.py:242`）获取 HA 实例：

```python
from homeassistant.core import async_get_hass

def some_blocking_function():
    hass = async_get_hass()  # 从线程局部变量获取
    # 注意：在非事件循环线程中，只能通过 run_coroutine_threadsafe 调用异步方法
```

此函数通过 `contextvars.ContextVar` 存储当前 HA 实例，使集成代码无需在函数参数中层层传递 `hass`。

## 典型使用模式

### 集成中的 hass 使用

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # 1. 创建协调器并存入 hass.data
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN] = coordinator

    # 2. 转发到平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 3. 注册一次性启动任务
    hass.async_create_task(coordinator.async_background_refresh())

    # 4. 监听事件
    entry.async_on_unload(
        hass.bus.async_listen("state_changed", coordinator.handle_event)
    )
    return True
```

### 测试中的 hass

测试框架通过 `async_test_home_assistant`（`tests/common.py`）创建测试实例：

```python
async def test_my_integration(hass):
    """hass fixture 自动创建测试用 HomeAssistant 实例。"""
    assert hass.state == CoreState.running

    # 添加实体
    hass.states.async_set("light.test", "on")
    state = hass.states.get("light.test")
    assert state.state == "on"

    # 等待所有异步操作完成
    await hass.async_block_till_done()
```

测试环境中的 `hass` 实例禁用了网络访问（通过 pytest_socket），使用模拟的认证和存储，确保测试隔离。

## 延伸阅读

- [事件总线](/concepts/06-event-bus.md)
- [启动流程详解](/concepts/04-bootstrap-lifecycle.md)
- [三层架构](/concepts/01-architecture.md)

## 相关概念

- [启动流程](/concepts/04-bootstrap-lifecycle.md) — HomeAssistant 实例从创建到运行的完整生命周期阶段
- [事件总线](/concepts/06-event-bus.md) — hass.bus 子系统的发布-订阅机制与 Event 对象结构
- [状态机](/concepts/07-state-machine.md) — hass.states 子系统的 State 对象存储与状态变更事件
- [服务注册表](/concepts/08-service-registry.md) — hass.services 子系统的服务注册、调用与实体服务模式
