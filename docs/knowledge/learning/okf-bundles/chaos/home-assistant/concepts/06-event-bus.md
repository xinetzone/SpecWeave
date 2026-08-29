---
type: Concept
title: 事件总线
description: 掌握 Home Assistant 事件总线机制，包括 Event 对象、EventBus 发布订阅、监听/触发模式和内置事件类型
tags: [home-assistant, smart-home, event-bus, event, state-changed, beginner]
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

# 事件总线

## 事件驱动模型

事件总线（EventBus）是 Home Assistant 内部通信的核心机制。HA 是一个事件驱动系统：设备状态变化产生事件，服务调用产生事件，系统生命周期变化产生事件。所有组件通过事件总线松耦合通信，不需要直接引用彼此。

事件总线定义于 `homeassistant/core.py:1442` 的 `EventBus` 类，通过 `hass.bus` 访问。它实现了经典的发布-订阅（Pub/Sub）模式：

- **发布者（Publisher）**：通过 `fire()` 发布事件，不需要知道谁在监听
- **订阅者（Subscriber）**：通过 `async_listen()` 注册监听器，只关心自己感兴趣的事件类型
- **事件总线（EventBus）**：负责将事件路由到所有匹配的监听器

这种设计使得系统组件之间高度解耦，新增监听器不需要修改发布者代码。

## Event 对象

`Event` 类定义于 `core.py:1295`，是所有事件的载体。它使用 `@final` 装饰器禁止子类化，通过泛型 `Generic[_DataT]` 支持类型化的事件数据。

### 结构

```python
class Event(Generic[_DataT]):
    event_type: str              # 事件类型（如 "state_changed"）
    data: _DataT                 # 事件数据（字典）
    origin: EventOrigin          # 事件来源
    time_fired: datetime         # 触发时间（UTC）
    context: Context             # 上下文（用户追踪、因果链）
```

### EventOrigin

`EventOrigin` 枚举（`core.py:1277`）标识事件来源：

```python
class EventOrigin(enum.Enum):
    local = "LOCAL"      # 本地触发
    remote = "REMOTE"    # 远程触发（来自其他 HA 实例）
```

### Context

每个 Event 携带一个 `Context` 对象（`core.py:1218`），包含：

- `id`：ULID 格式的唯一标识，可按时间排序
- `user_id`：触发事件的用户 ID（用户操作时设置）
- `parent_id`：父事件 ID，用于追踪事件因果链

Context 对于审计追踪和自动化循环检测非常重要。例如，自动化触发的服务调用会继承自动化的 Context，如果该服务调用又触发了同一自动化，可以通过 Context 链检测到循环。

### 创建事件

通常不需要手动创建 Event 对象，`EventBus.fire()` 会自动创建：

```python
from homeassistant.core import EventBus, Context

# 事件数据通过字典传入，Event 对象自动创建
hass.bus.async_fire("my_custom_event", {"key": "value"})

# 指定上下文（如由特定用户触发）
hass.bus.async_fire(
    "my_custom_event",
    {"key": "value"},
    context=Context(user_id=user.id),
)
```

## 监听事件

### async_listen

注册事件监听器：

```python
from homeassistant.core import Event, callback

def handle_event(event: Event) -> None:
    """处理事件的普通函数（在线程池中执行）。"""
    print(f"收到事件: {event.event_type}, 数据: {event.data}")

@callback
def handle_event_fast(event: Event) -> None:
    """快速处理事件的回调函数（在事件循环中同步执行）。"""
    print(f"快速处理: {event.data}")

# 注册监听器，返回取消函数
unsub = hass.bus.async_listen("state_changed", handle_event)

# 使用 @callback 装饰的监听器在事件循环中直接执行，无协程调度开销
unsub_fast = hass.bus.async_listen("state_changed", handle_event_fast)

# 后续取消监听
unsub()
```

监听器的执行方式由 `HassJob` 自动判定：
- `async def` 函数：作为协程在事件循环中执行
- `@callback` 装饰的函数：在事件循环中同步立即执行（最快）
- 普通函数：调度到线程池执行（适用于阻塞操作）

### async_listen_once

只监听一次，事件触发后自动移除监听器：

```python
def on_started(event: Event) -> None:
    print("HA 启动完成！")

hass.bus.async_listen_once("homeassistant_started", on_started)
```

这在集成设置中非常常见，用于在 HA 完全启动后执行延迟初始化。

### 通配符监听

使用 `MATCH_ALL = "*"`（`const.py`）监听所有事件：

```python
@callback
def log_all_events(event: Event) -> None:
    print(f"[{event.time_fired}] {event.event_type}: {event.data}")

unsub = hass.bus.async_listen(MATCH_ALL, log_all_events)
```

通配符监听器会收到所有事件，包括高频的 `state_changed`，应谨慎使用以避免性能问题。

### 事件过滤

监听器通常需要过滤事件数据。HA 提供了专门的状态跟踪辅助函数，但也可以在监听器中手动过滤：

```python
@callback
def on_light_state_changed(event: Event) -> None:
    """只处理灯的状态变更。"""
    entity_id = event.data["entity_id"]
    if not entity_id.startswith("light."):
        return
    new_state = event.data["new_state"]
    if new_state is not None:
        print(f"{entity_id} -> {new_state.state}")

hass.bus.async_listen("state_changed", on_light_state_changed)
```

对于状态变更跟踪，推荐使用 `helpers/event.py` 中的高级辅助函数（见下文）。

## 触发事件

### async_fire

发布事件到事件总线：

```python
hass.bus.async_fire(
    event_type="my_integration_event",
    event_data={
        "device_id": "abc123",
        "action": "button_pressed",
        "battery": 85,
    },
)
```

`async_fire` 是线程安全的，可以在事件循环之外（如线程池中的函数）调用。它将事件调度到事件循环中分发给监听器。

### fire（同步版本）

`fire()` 是同步方法，内部通过 `run_callback_threadsafe` 将调用调度到事件循环。在异步代码中应始终使用 `async_fire`。

### 事件分发机制

事件分发遵循以下流程：

1. `async_fire()` 将事件加入分发队列
2. 事件循环批量取出事件
3. 对每个事件，查找匹配的监听器（精确匹配 event_type + 通配符）
4. 按注册顺序依次调用监听器
5. 协程监听器创建 Task，回调监听器同步执行，普通函数提交到线程池

为防止无限递归，事件嵌套触发有上限：`_MAX_QUEUED_EVENT_DISPATCHES = 10000`（`core.py:1439`）。如果事件监听器触发的事件再次触发同一监听器形成循环，达到上限后停止分发并记录警告。

## 内置事件类型

HA 定义了一系列内置事件类型，全部以常量形式定义于 `const.py`：

### 系统生命周期事件

| 常量 | 值 | 触发时机 |
|------|-----|---------|
| `EVENT_HOMEASSISTANT_START` | `"homeassistant_start"` | HA 开始启动（在集成加载后、运行前） |
| `EVENT_HOMEASSISTANT_STARTED` | `"homeassistant_started"` | HA 完全启动完成 |
| `EVENT_HOMEASSISTANT_STOP` | `"homeassistant_stop"` | HA 开始停止 |
| `EVENT_HOMEASSISTANT_FINAL_WRITE` | `"homeassistant_final_write"` | 停止前最终写入阶段 |
| `EVENT_HOMEASSISTANT_CLOSE` | `"homeassistant_close"` | HA 完全关闭 |
| `EVENT_CORE_CONFIG_UPDATE` | `"core_config_updated"` | 核心配置变更 |

### 组件与服务事件

| 常量 | 值 | 触发时机 |
|------|-----|---------|
| `EVENT_COMPONENT_LOADED` | `"component_loaded"` | 集成加载完成 |
| `EVENT_SERVICE_REGISTERED` | `"service_registered"` | 新服务注册 |
| `EVENT_SERVICE_REMOVED` | `"service_removed"` | 服务移除 |
| `EVENT_CALL_SERVICE` | `"call_service"` | 服务被调用 |

### 状态事件

| 常量 | 值 | 触发时机 |
|------|-----|---------|
| `EVENT_STATE_CHANGED` | `"state_changed"` | 实体状态发生变化 |
| `EVENT_STATE_REPORTED` | `"state_reported"` | 实体上报状态（值可能未变） |

### state_changed 事件

`state_changed` 是 HA 中最频繁触发的事件，每当实体状态变化时由 `StateMachine` 发布：

```python
{
    "entity_id": "light.living_room",
    "old_state": <State>,   # 变化前的状态对象（首次设置时为 None）
    "new_state": <State>,   # 变化后的状态对象（移除时为 None）
}
```

State 对象包含：
- `state`：状态值（如 `"on"`/`"off"`/`"21.5"`）
- `attributes`：属性字典（亮度、颜色、单位等）
- `last_changed`：上次状态值变更时间
- `last_updated`：上次更新时间（包括属性变更）
- `context`：上下文

注意：只有当状态值（`state`）实际变化时才触发 `state_changed`。如果设置相同的状态值（即使属性变化），触发的是 `state_reported`。属性变化但状态值不变时，`last_updated` 更新但 `last_changed` 不变。

### call_service 事件

每当服务被调用时触发：

```python
{
    "domain": "light",
    "service": "turn_on",
    "service_data": {"entity_id": "light.living_room", "brightness": 255},
}
```

此事件在服务执行之前触发。服务执行完成后不自动发布完成事件，但服务可能在执行过程中触发其他事件（如状态变更）。

## 事件辅助工具

`homeassistant/helpers/event.py` 提供了高级事件跟踪工具，封装了常见的监听模式。

### async_track_state_change

跟踪特定实体的状态变更，支持 from/to 过滤：

```python
from homeassistant.helpers.event import async_track_state_change

def state_changed_listener(entity_id, old_state, new_state):
    """实体状态变更时调用。"""
    if new_state is None:
        print(f"{entity_id} 已移除")
    else:
        print(f"{entity_id}: {old_state.state} -> {new_state.state}")

# 跟踪单个实体
unsub = async_track_state_change(
    hass, "light.living_room", state_changed_listener
)

# 跟踪多个实体，指定 from/to 状态
unsub = async_track_state_change(
    hass,
    ["light.living_room", "light.kitchen"],
    state_changed_listener,
    from_state="off",
    to_state="on",
)
```

### async_track_state_change_event

与 `async_track_state_change` 类似，但回调接收完整的 Event 对象：

```python
from homeassistant.helpers.event import async_track_state_change_event

@callback
def on_state_change(event):
    entity_id = event.data["entity_id"]
    new_state = event.data["new_state"]
    old_state = event.data["old_state"]

unsub = async_track_state_change_event(
    hass, ["sensor.temperature"], on_state_change
)
```

### async_track_time_interval

按固定时间间隔触发回调：

```python
from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval

async def refresh_data(now):
    """每 5 分钟刷新数据。"""
    await coordinator.async_refresh()

unsub = async_track_time_interval(hass, refresh_data, timedelta(minutes=5))
```

### async_call_later

延迟触发一次性回调：

```python
from homeassistant.helpers.event import async_call_later

def delayed_action(now):
    """10 秒后执行。"""
    print("延迟操作执行")

unsub = async_call_later(hass, 10, delayed_action)
```

### async_track_point_in_time

在指定时间点触发：

```python
from datetime import datetime, timedelta
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util.dt import utcnow

target_time = utcnow() + timedelta(hours=1)

def at_target_time(now):
    print("目标时间到达")

unsub = async_track_point_in_time(hass, at_target_time, target_time)
```

### TrackTemplate

跟踪模板结果变更：

```python
from homeassistant.helpers.event import TrackTemplate

template = Template("{{ states('sensor.temperature') | float > 25 }}", hass)

def template_changed(event, updates):
    result = updates.pop("result")
    if result:
        print("温度超过 25 度！")

tracker = TrackTemplate(hass, template, template_changed)
unsub = tracker.async_setup()
```

## 自定义事件

集成可以定义自己的事件类型，用于内部或跨集成通信：

```python
DOMAIN = "my_integration"
EVENT_BUTTON_PRESSED = f"{DOMAIN}_button_pressed"

async def async_setup(hass, config):
    # 设备按钮被按下时触发自定义事件
    def on_button_pressed(device_id):
        hass.bus.async_fire(EVENT_BUTTON_PRESSED, {
            "device_id": device_id,
            "timestamp": time.time(),
        })

    device.register_callback(on_button_pressed)
    return True
```

其他集成或自动化可以通过 `event_data` 触发条件监听自定义事件：

```yaml
automation:
  - alias: "按钮被按下"
    trigger:
      - platform: event
        event_type: my_integration_button_pressed
        event_data:
          device_id: "abc123"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

## 事件总线与状态机的关系

事件总线和状态机紧密协作：

```text
实体更新状态（entity.async_write_ha_state）
    │
    ▼
StateMachine.async_set(entity_id, new_state, ...)
    │
    ├─ 状态值是否变化？
    │   ├─ 是 → 更新 States 集合
    │   │       └─ EventBus.async_fire("state_changed", {...})
    │   └─ 否 → 仅更新 last_updated
    │           └─ EventBus.async_fire("state_reported", {...})
    │
    ▼
监听器接收事件（自动化、WebSocket、前端等）
```

WebSocket API 将 `state_changed` 事件实时推送到前端和移动 App，这是前端实时更新 UI 的基础机制。Recorder 监听这些事件并写入数据库，形成历史记录。

## 最佳实践

### 监听器清理

所有事件监听器返回一个取消函数。集成在卸载时必须调用这些函数，防止内存泄漏和已卸载组件的回调被触发：

```python
async def async_setup_entry(hass, entry):
    unsub = hass.bus.async_listen("state_changed", handle_event)
    entry.async_on_unload(unsub)  # 自动在卸载时调用
    return True
```

`entry.async_on_unload()` 和 `entity.async_on_remove()` 是注册清理回调的标准方式。

### 使用 @callback

对于不需要 I/O 且不耗时的事件处理器，使用 `@callback` 装饰器可以避免协程调度开销：

```python
@callback
def fast_handler(event: Event) -> None:
    """在事件循环中同步执行，不要在此处进行 I/O 操作。"""
    process_data(event.data)
```

但回调中绝对不能执行阻塞操作（网络请求、文件 I/O、`time.sleep` 等），否则会阻塞整个事件循环。

### 避免在监听器中触发高开销操作

`state_changed` 事件非常高频（可能每秒数百次）。监听器应：
- 尽早过滤不相关的实体
- 避免在每次事件中执行 I/O
- 使用 `Debouncer`（`helpers/debounce.py`）合并频繁的事件
- 对于定期任务，使用 `async_track_time_interval` 而非在 state_changed 中处理

### 事件类型命名

自定义事件类型应使用集成 domain 作为前缀（如 `my_integration_button_pressed`），避免命名冲突。

## 延伸阅读

- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [三层架构](/concepts/01-architecture.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)

## 相关概念

- [HomeAssistant 核心对象](/concepts/03-core-object.md) — EventBus 作为 hass.bus 子系统的持有者与生命周期
- [状态机](/concepts/07-state-machine.md) — 状态变更时通过 EventBus 发布 state_changed 事件的紧密协作者
- [服务注册表](/concepts/08-service-registry.md) — 服务调用前后通过 EventBus 发布 call_service 事件
- [Helpers 工具库](/concepts/12-helpers-library.md) — async_track_state_change 等高级事件跟踪封装
