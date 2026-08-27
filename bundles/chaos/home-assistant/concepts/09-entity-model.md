---
type: Concept
title: 实体模型
description: 深入理解 Home Assistant 实体模型，包括 Entity 基类、ToggleEntity、EntityDescription 声明式配置、EntityCategory 分类、_attr_ 属性后备机制、cached_properties 缓存和生命周期方法
tags: [home-assistant, smart-home, entity, entity-model, toggle-entity, entity-description, core]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: helpers-util-source
    resource: "/references/helpers-util-source.md"
    title: Home Assistant Helpers 与 Util 源码
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 源码
  - id: facts-helpers
    resource: "/references/facts-helpers.md"
    title: Home Assistant Helpers 事实清单
  - id: facts-components
    resource: "/references/facts-components.md"
    title: Home Assistant Components 事实清单
---

# 实体模型

实体（Entity）是 Home Assistant 中对设备能力的抽象表示。一个智能灯泡可能同时是一个 `light` 实体（开关与亮度）和一个 `sensor` 实体（用电量监控）。每个实体在[状态机](/concepts/07-state-machine.md)中有一条状态记录，通过[服务注册表](/concepts/08-service-registry.md)暴露可调用的操作。实体模型定义于 `helpers/entity.py`，是所有平台实体（LightEntity、SensorEntity 等）的共同根基。

## Entity 基类

`Entity` 是所有 HA 实体的抽象基类（`helpers/entity.py`）。它定义了实体的核心契约——子类通过重写属性和方法来描述自身状态和行为。

### 核心属性

Entity 类定义了以下关键属性（事实 #26-53）：

| 属性 | 类型 | 说明 |
|------|------|------|
| `entity_id` | `str` | 实体唯一标识，格式 `domain.object_id` |
| `name` | `str \| None` | 显示名称 |
| `state` | `StateType` | 当前状态值（str/int/float/None） |
| `available` | `bool` | 是否可用/在线，默认 `True` |
| `should_poll` | `bool` | 是否需要轮询更新，默认 `True` |
| `unique_id` | `str \| None` | 全局唯一标识符，用于注册表关联 |
| `device_class` | `str \| None` | 设备类别（影响 UI 展示） |
| `entity_category` | `EntityCategory \| None` | 实体分类 |
| `icon` | `str \| None` | Material Design 图标名称 |
| `unit_of_measurement` | `str \| None` | 测量单位 |
| `device_info` | `DeviceInfo \| None` | 设备注册表关联信息 |
| `extra_state_attributes` | `dict \| None` | 附加状态属性 |
| `capability_attributes` | `dict \| None` | 能力属性（影响前端卡片） |
| `supported_features` | `int \| None` | 功能标志位 |
| `force_update` | `bool` | 状态未变时是否仍触发事件，默认 `False` |
| `entity_registry_enabled_default` | `bool` | 注册表中默认是否启用 |
| `entity_registry_visible_default` | `bool` | UI 中默认是否可见 |

### hass 与 platform 引用

实体添加到 HA 后，可以通过 `self.hass` 获取 `HomeAssistant` 实例，通过 `self.platform` 获取所属的 `EntityPlatform` 引用。这些属性在实体生命周期内被设置，在实体构造时不可用。

## _attr_ 属性后备机制

Entity 类使用 `_attr_*` 前缀的类属性作为属性的后备值（事实 #47）。这种设计允许子类通过两种方式定义属性：

**方式一：重写属性（动态计算）**

```python
class MySensor(SensorEntity):
    @property
    def native_value(self) -> float | None:
        return self._temperature  # 每次访问都计算
```

**方式二：设置 _attr_ 类属性（静态声明）**

```python
class MySensor(SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
```

基类属性的 getter 会检查 `_attr_<name>` 是否存在。例如，`should_poll` 属性的默认实现返回 `getattr(self, "_attr_should_poll", True)`。这种模式结合了声明式简洁性和动态灵活性。

## EntityDescription：声明式配置

`EntityDescription` 是一个 frozen dataclass（事实 #48），用于集中描述实体的元数据。它将原本散落在 `_attr_*` 中的配置聚合为一个不可变对象：

```python
@dataclass(frozen=True)
class EntityDescription:
    key: str                                    # 必需，唯一键
    device_class: str | None = None
    entity_category: EntityCategory | None = None
    entity_registry_enabled_default: bool = True
    entity_registry_visible_default: bool = True
    force_update: bool = False
    icon: str | None = None
    name: str | None = None
    translation_key: str | None = None
    has_entity_name: bool = False
```

### 使用模式

每个平台都有自己的 EntityDescription 子类，扩展平台特有字段：

```python
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        translation_key="temperature",
    ),
    SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
)

class MySensor(SensorEntity):
    def __init__(self, description: SensorEntityDescription):
        self.entity_description = description
        self._attr_unique_id = f"{self._device_id}_{description.key}"
```

EntityDescription 通过 `_attribute` 机制与 Entity 关联——Entity 的属性 getter 会检查 `self.entity_description` 是否有同名字段，有则返回描述中的值，否则回退到 `_attr_*`。这实现了"描述优先、属性后备"的分层配置。

### 平台描述类层次

各平台的描述类形成继承链（事实 #48-49）：

- `EntityDescription` → `ToggleEntityDescription` → `LightEntityDescription` / `SwitchEntityDescription`
- `EntityDescription` → `SensorEntityDescription`
- `EntityDescription` → `BinarySensorEntityDescription`

描述类使用 `frozen_or_thawed=True` 参数支持可变/不可变双模式。

## EntityCategory：实体分类

`EntityCategory` 是 `StrEnum`（事实 #49），控制实体在 UI 中的展示位置：

```python
class EntityCategory(StrEnum):
    CONFIG = "config"        # 配置实体（如设置阈值）
    DIAGNOSTIC = "diagnostic"  # 诊断实体（如信号强度、IP 地址）
```

- 普通实体（无 category）显示在设备的主仪表板上
- `CONFIG` 实体归入配置区域，表示主要用于配置而非日常监控
- `DIAGNOSTIC` 实体归入诊断区域，显示设备技术参数

部分平台对 entity_category 有限制。例如 SensorEntity 和 BinarySensorEntity 不允许 `EntityCategory.CONFIG`，否则抛出 `HomeAssistantError`。

## ToggleEntity：可开关实体

`ToggleEntity` 是 `Entity` 的子类（事实 #47），为具有开关状态的实体提供标准化能力。灯光（LightEntity）、开关（SwitchEntity）、自动化（BaseAutomationEntity）等都继承自它。

### 核心成员

```python
class ToggleEntity(Entity):
    @property
    def is_on(self) -> bool | None:
        """返回实体是否处于开启状态。"""
        ...

    async def async_turn_on(self, **kwargs) -> None:
        """打开实体。子类应重写。"""
        ...

    async def async_turn_off(self, **kwargs) -> None:
        """关闭实体。子类应重写。"""
        ...

    async def async_toggle(self, **kwargs) -> None:
        """切换状态。默认实现根据 is_on 调用 turn_on/turn_off。"""
        if self.is_on:
            await self.async_turn_off(**kwargs)
        else:
            await self.async_turn_on(**kwargs)

    @property
    def state(self) -> str:
        """ToggleEntity 的 state 直接映射 is_on。"""
        return STATE_ON if self.is_on else STATE_OFF
```

`ToggleEntity` 自动将 `is_on` 映射为 `STATE_ON`/`STATE_OFF` 状态值，并注册 `turn_on`、`turn_off`、`toggle` 三个标准服务。

## cached_properties：属性缓存

Entity 子类使用 `cached_properties` 元类参数声明需要缓存的计算属性（事实 #50, #53）。这来自 `propcache.api.cached_property`，替代标准库的 `functools.cached_property`（事实 #368）。

```python
class LightEntity(ToggleEntity, cached_properties=CACHED_PROPERTIES_WITH_ATTR_):
    _attr_brightness: int | None = None
    _attr_color_mode: ColorMode | None = None

    @cached_property
    def brightness(self) -> int | None:
        return self._attr_brightness

    @cached_property
    def color_mode(self) -> ColorMode | None:
        return self._attr_color_mode
```

`CACHED_PROPERTIES_WITH_ATTR_` 是一个特殊标记，元类据此自动将带有 `_attr_` 后备的属性标记为可缓存。缓存的属性在 `async_write_ha_state()` 时自动清除并重新计算，确保状态一致性，同时避免在一次状态写入周期内重复计算。

LightEntity 缓存了大量属性（事实 #83）：`brightness`、`color_mode`、`hs_color`、`xy_color`、`rgb_color`、`rgbw_color`、`rgbww_color`、`color_temp_kelvin`、`min_color_temp_kelvin`、`max_color_temp_kelvin`、`effect_list`、`effect`、`supported_color_modes`、`supported_features`。

## 生命周期

实体从创建到移除经历明确的生命周期阶段。

### async_added_to_hass

实体被添加到 HomeAssistant 时调用（事实 #26）：

```python
async def async_added_to_hass(self) -> None:
    """实体已添加到 hass。"""
    # 重写以执行异步初始化
    await self._api.subscribe(self._on_update)
    self.async_on_remove(self._cleanup)
```

此时 `self.hass` 和 `self.platform` 已可用。这是注册事件监听器、建立连接、恢复状态的正确位置。对于继承 `RestoreEntity` 的实体，应在此方法中调用 `await self.async_get_last_state()` 恢复上次状态。

### async_will_remove_from_hass

实体从 HomeAssistant 移除前调用（事实 #27）：

```python
async def async_will_remove_from_hass(self) -> None:
    """实体即将从 hass 移除。"""
    # 重写以执行清理
    await self._api.disconnect()
```

此时实体仍在状态机中。重写此方法以关闭连接、取消订阅、释放资源。

### async_on_remove

注册实体移除时的清理回调（事实 #46）：

```python
def async_on_remove(self, func: CALLBACK_TYPE) -> None:
```

所有通过此方法注册的回调函数会在实体移除时按注册相反顺序调用。这是比重写 `async_will_remove_from_hass` 更灵活的清理方式，特别适合在初始化过程中逐步注册清理逻辑：

```python
async def async_added_to_hass(self) -> None:
    self.async_on_remove(
        async_track_state_change(self.hass, "...", self._on_change)
    )
    self.async_on_remove(self.coordinator.async_add_listener(self._on_data))
```

## 状态写入

实体通过两种方法将自身状态写入状态机：

### async_write_ha_state

立即收集实体属性并写入状态机：

```python
def async_write_ha_state(self) -> None:
```

此方法在事件循环中同步执行：
1. 清除 cached_properties 缓存
2. 读取 state、attributes、available 等属性
3. 若不可用，将 state 设为 `STATE_UNAVAILABLE`
4. 调用 `hass.states.async_set()` 写入

### schedule_update_ha_state

将状态更新调度到事件循环下一次迭代：

```python
def schedule_update_ha_state(self, force_refresh: bool = False) -> None:
```

这允许在短时间内发生多次属性变更时合并为一次状态写入，避免中间状态触发不必要的事件。

### async_update_ha_state

```python
async def async_update_ha_state(self, force_refresh: bool = False) -> None:
```

先调用 `async_update()`（如果 should_poll=True），然后写入状态。`force_refresh=True` 会传递给状态机的 `force_update` 参数。

## 实体继承层次

各平台实体类的继承关系（事实 #34-50）：

```text
Entity
├── ToggleEntity
│   ├── LightEntity
│   ├── SwitchEntity
│   └── BaseAutomationEntity → AutomationEntity (with RestoreEntity)
├── SensorEntity
├── BinarySensorEntity
├── ClimateEntity
├── CoverEntity
├── Camera
├── SelectEntity
├── NumberEntity
└── RestoreEntity (mixin)
    ├── ButtonEntity
    └── ConversationEntity
```

`RestoreEntity` 是一个 mixin，为需要状态恢复的实体提供 `async_get_last_state()` 和 `async_get_last_extra_data()` 方法。ButtonEntity 和 ConversationEntity 默认继承它。

## 实体平台与 EntityComponent

实体不直接注册到 HA，而是通过 `EntityPlatform` 和 `EntityComponent` 管理。每个平台集成在 `async_setup` 中创建 `EntityComponent` 实例：

```python
async def async_setup(hass, config):
    component = EntityComponent[LightEntity](logger, DOMAIN, hass, SCAN_INTERVAL)
    hass.data[DATA_COMPONENT] = component
    await component.async_setup(config)
    return True
```

`EntityComponent` 负责：
- 管理平台的所有实体实例
- 处理 ConfigEntry 的 setup/unload
- 协调轮询间隔
- 注册实体级服务
- 与实体注册表和设备注册表交互

## 最佳实践

### unique_id 与注册表

每个实体应提供稳定的 `unique_id`。它是实体与 EntityRegistry 关联的键，使得用户可以在 UI 中修改实体 ID、禁用实体、设置区域。没有 unique_id 的实体无法被注册表管理，重启后自定义设置会丢失。

### available 与轮询

- 对于推送型集成（`iot_class="local_push"`/`"cloud_push"`），设置 `_attr_should_poll = False`，在数据到达时调用 `schedule_update_ha_state()`
- 对于轮询型集成，保持 `should_poll = True` 并重写 `async_update()` 执行数据获取
- 设备离线时将 `available` 设为 `False`，状态自动变为 `unavailable`

### 异步初始化

所有 I/O 操作（网络请求、文件读取）应在 `async_added_to_hass` 中以协程方式执行，或通过 `hass.async_add_executor_job` 调度到线程池。不要在 `__init__` 中执行阻塞操作。

## 延伸阅读

- [状态机](/concepts/07-state-machine.md)
- [服务注册表](/concepts/08-service-registry.md)
- [注册表](/concepts/10-registries.md)
- [三层架构](/concepts/01-architecture.md)

## 相关概念

- [状态机](/concepts/07-state-machine.md) — Entity 通过 async_write_ha_state 将状态写入 StateMachine
- [注册表](/concepts/10-registries.md) — unique_id 关联 EntityRegistry，实现实体 ID 自定义与禁用管理
- [平台开发模式](/concepts/16-platform-pattern.md) — 各平台 Entity 子类（LightEntity、SensorEntity 等）继承自 Entity
- [集成架构](/concepts/14-component-architecture.md) — 集成通过 async_setup_entry 创建 Entity 并添加到 Home Assistant
