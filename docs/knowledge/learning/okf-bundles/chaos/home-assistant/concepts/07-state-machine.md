---
type: Concept
title: 状态机
description: 深入理解 Home Assistant 状态机机制，包括 State 对象结构、StateMachine 的 async_set/async_remove 方法、STATE_CHANGED 与 STATE_REPORTED 事件的区别，以及状态恢复原理
tags: [home-assistant, smart-home, state-machine, state, state-changed, core]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: facts-core
    resource: "/references/facts-core.md"
    title: Home Assistant Core 事实清单
---

# 状态机

状态机（StateMachine）是 Home Assistant 中存储和管理所有实体当前状态的核心子系统。每个实体——无论是灯光、传感器还是媒体播放器——在状态机中都有一条对应的 State 记录。状态机通过 `hass.states` 访问，与[事件总线](/concepts/06-event-bus.md)紧密协作，在状态变化时发布事件。

## State 对象

`State` 类定义于 `core.py:1792`，是不可变的状态快照对象。它使用 `__slots__` 优化内存，包含以下公开属性：

```python
class State:
    entity_id: str          # 实体 ID，如 "light.living_room"
    domain: str             # 域，如 "light"
    object_id: str          # 对象 ID，如 "living_room"
    state: str              # 状态值，如 "on"、"21.5"
    attributes: ReadOnlyDict  # 属性字典（只读）
    last_changed: datetime  # 上次状态值变更时间
    last_reported: datetime # 上次上报时间
    last_updated: datetime  # 上次更新时间
    context: Context        # 上下文（追踪因果链）
```

### 构造与校验

创建 State 对象时，构造函数会执行以下处理（`core.py:1856-1875`）：

- 若 `validate_entity_id=True`，校验实体 ID 格式，无效则抛出 `InvalidEntityFormatError`
- 非字符串的 state 值通过 `str()` 转换
- attributes 若非 `ReadOnlyDict` 则包装为只读字典
- `last_reported` 默认为 `dt_util.utcnow()`，`last_updated` 和 `last_changed` 默认与之相同
- 通过 `split_entity_id()` 将 entity_id 拆分为 domain 和 object_id

实体 ID 格式遵循 `<domain>.<object_id>` 正则，两者均为 slug 格式（`core.py:178-181`）。`split_entity_id()` 和 `valid_entity_id()` 都使用 `lru_cache` 缓存结果以提升性能。

### name 属性

`State.name` 是缓存属性（`core.py:1891-1896`），返回 attributes 中的 `friendly_name`；若未设置，则将 object_id 中的下划线替换为空格。例如 `light.living_room` 的默认名称为 `"Living Room"`。

### 压缩序列化

`State.as_compressed_state` 属性（`core.py:1987-2014`）构建紧凑字典，键缩写为 `s`（state）、`a`（attributes）、`c`（context）、`lc`（last_changed）、`lu`（last_updated）。当 context 无 parent_id 和 user_id 时，压缩状态中 context 仅为 id 字符串，大幅减小 WebSocket 传输体积。

`State.from_dict()` 类方法（`core.py:2026-2060`）支持从字典反序列化，解析 ISO 格式时间字符串。

### expire 机制

`State.expire()` 方法（`core.py:2062-2078`）用相同 id 的新 Context 替换原 context，允许旧 context 被垃圾回收。当状态被更新时，旧 State 对象会调用此方法，防止长时间持有过期引用导致内存泄漏。

## States 集合

`States` 类继承 `UserDict[str, State]`（`core.py:2091-2101`），维护两级索引：

- 主字典：`entity_id -> State`
- 域索引：`domain -> dict[entity_id, State]`

这种二级索引使得按域查询实体状态非常高效：

```python
# 获取所有 light 域的实体 ID
light_ids = hass.states.async_entity_ids("light")

# 获取所有 sensor 域的 State 对象
sensor_states = hass.states.async_all("sensor")
```

`States.__setitem__` 和 `__delitem__` 会同时更新主字典和域索引（`core.py:2109-2119`），保证数据一致性。

## StateMachine 核心实现

`StateMachine` 类定义于 `core.py:2136`，通过 `HomeAssistant.__init__` 中 `self.states = StateMachine(self.bus, self.loop)` 创建。

### 内部结构

```python
class StateMachine:
    __slots__ = ("_bus", "_loop", "_reservations", "_states", "_states_data")
```

- `_states`：`States` 实例，存储所有状态
- `_states_data`：缓存的 `_states.data` 引用，加速直接字典访问
- `_bus`：事件总线引用，用于发布状态事件
- `_reservations`：预留的 entity_id 集合，防止竞态条件

### 状态预留

`async_reserve()` 方法（`core.py:2299-2314`）为即将添加的实体预留 entity_id。当集成正在异步初始化实体时，预留可以防止其他组件抢占相同的 entity_id。`async_available()` 方法（`core.py:2316-2322`）检查 entity_id 是否既不在状态机中也不在预留中。

### async_set：设置状态

`async_set()` 是状态机最核心的方法（`core.py:2324-2354`）。完整签名为：

```python
async def async_set(
    self,
    entity_id: str,
    new_state: str,
    attributes: dict[str, Any] | None = None,
    force_update: bool = False,
    context: Context | None = None,
    *,
    timestamp: datetime | None = None,
) -> None:
```

该方法首先调用 `validate_state()` 检查状态值长度不超过 255 字符（`MAX_LENGTH_STATE_STATE`），然后委托给 `async_set_internal()` 执行实际逻辑。

### async_set_internal 决策逻辑

`async_set_internal()`（`core.py:2357`）是状态写入的决策核心，其行为取决于新旧状态的对比：

**情况一：状态值和属性均未变化**

若 state 和 attributes 都未改变，且 `force_update=False`，则：
- 更新 `last_reported` 为当前时间
- 触发 `EVENT_STATE_REPORTED` 事件（而非 `STATE_CHANGED`）
- 不创建新的 State 对象

这种情况发生在设备定期上报相同状态时（如温度传感器每 30 秒上报相同读数），避免了不必要的状态对象创建和高频事件。

**情况二：状态值或属性发生变化**

当 state 值变化或 attributes 变化时：
- 创建新的 State 对象
- 旧 State 调用 `expire()` 释放 context
- `last_updated` 更新为当前时间
- 若 state 值变化，`last_changed` 也更新；若仅 attributes 变化，`last_changed` 保持不变
- 触发 `EVENT_STATE_CHANGED` 事件

**情况三：force_update=True**

即使状态值和属性都未变化，也强制创建新 State 对象并触发 `EVENT_STATE_CHANGED`。适用于需要每次上报都触发更新的场景。

**超长状态处理**：若新 state 超过 255 字符，记录错误并回退为 `STATE_UNKNOWN`（`core.py:2435-2443`）。

### STATE_CHANGED vs STATE_REPORTED

这两个事件有本质区别，理解它们对编写高效自动化至关重要：

| 特性 | `state_changed` | `state_reported` |
|------|----------------|------------------|
| 触发条件 | state 值或 attributes 变化 | 状态上报（值可能未变） |
| 事件数据 | `entity_id`, `old_state`, `new_state` | `entity_id`, `new_state`, `old_last_reported`, `last_reported` |
| 频率 | 较低（仅变化时） | 较高（每次上报） |
| 新 State 对象 | 是 | 否 |
| match_all 监听 | 正常派发 | 必须提供 event_filter |

特别需要注意：`EVENT_STATE_REPORTED` 事件被排除在 `MATCH_ALL` 通配符监听之外（`core.py:161-164`），且监听时必须提供 `event_filter`（callback 装饰的函数），否则抛出 `HomeAssistantError`（`core.py:1674-1678`）。这是因为 `state_reported` 事件频率极高，无过滤的监听会严重影响性能。

```python
# 正确：监听 state_reported 必须带 filter
@callback
def _filter_state_reported(event: Event) -> bool:
    return event.data["entity_id"] == "sensor.temperature"

hass.bus.async_listen(
    EVENT_STATE_REPORTED,
    handler,
    event_filter=_filter_state_reported,
)
```

### async_remove：移除状态

`async_remove()` 方法（`core.py:2246-2272`）删除实体的状态记录：

1. 从 States 集合中删除 entity_id
2. 触发 `EVENT_STATE_CHANGED` 事件，其中 `new_state` 为 `None`
3. 若 entity_id 在预留集合中，同时移除预留

这在实体被移除或集成卸载时发生。监听 `state_changed` 的自动化可以通过检查 `new_state is None` 来检测实体移除。

### 状态查询

- `get(entity_id)`（`core.py:2220-2227`）：先按原 entity_id 查找，再按小写查找，返回 State 或 None
- `is_state(entity_id, state)`（`core.py:2229-2235`）：检查实体是否存在且处于指定状态
- `async_entity_ids(domain_filter=None)`：返回匹配域的实体 ID 列表
- `async_all(domain_filter=None)`：返回匹配域的所有 State 对象

## 状态写入流程

实体通常不直接调用 `hass.states.async_set()`，而是通过 Entity 基类的方法间接写入：

```text
Entity.async_write_ha_state()
    │
    ├─ 收集 state、attributes、available 等属性
    ├─ 构建属性字典
    │
    ▼
hass.states.async_set(entity_id, state, attributes, ...)
    │
    ├─ validate_state() 校验长度
    │
    ▼
async_set_internal()
    │
    ├─ 对比旧状态
    │
    ├─ [未变化] → 更新 last_reported
    │              └─ bus.async_fire(EVENT_STATE_REPORTED)
    │
    └─ [已变化] → 创建新 State
                   ├─ old_state.expire()
                   └─ bus.async_fire(EVENT_STATE_CHANGED)
```

`Entity.async_update_ha_state()` 方法（`helpers/entity.py`）会强制刷新实体属性后写入，而 `schedule_update_ha_state()` 将写入调度到事件循环下一次迭代，允许批量更新合并。

## 状态恢复

Home Assistant 重启后，实体状态默认全部重置为 `unknown`。但通过 `RestoreEntity` 基类（`helpers/restore_state.py`），实体可以恢复上次的状态：

1. HA 停止前，Recorder 将所有 State 写入数据库
2. 重启时，`RestoreEntity` 集成从 Recorder 获取上次状态
3. 实体在 `async_added_to_hass()` 中调用 `await self.async_get_last_state()` 获取恢复数据
4. 实体使用恢复的数据初始化自身状态

ButtonEntity 和 ConversationEntity 等平台默认继承 `RestoreEntity`，因为按钮按下等事件不具备持续性状态，恢复可以避免重启后状态丢失。

测试中可使用 `mock_restore_cache()` 和 `mock_restore_cache_with_extra_data()` 模拟状态恢复（`tests/common.py:1326-1378`）。

## 基础状态常量

HA 定义了一组通用状态值常量（`const.py:295-300`）：

```python
STATE_ON = "on"
STATE_OFF = "off"
STATE_HOME = "home"
STATE_NOT_HOME = "not_home"
STATE_UNKNOWN = "unknown"
STATE_OPEN = "open"
```

`STATE_UNKNOWN` 用于实体尚未获取到有效状态时。除了这些基础常量，各平台定义自己的状态值（如 ClimateEntity 的 HVACMode、CoverEntity 的 CoverState）。

## 延伸阅读

- [事件总线](/concepts/06-event-bus.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)

## 相关概念

- [事件总线](/concepts/06-event-bus.md) — 状态变更时发布 state_changed 和 state_reported 事件的底层通道
- [服务注册表](/concepts/08-service-registry.md) — 服务调用可修改状态，状态变更也会触发服务响应
- [实体模型](/concepts/09-entity-model.md) — Entity 通过 async_write_ha_state 向 StateMachine 写入状态
