---
type: Concept
title: 平台开发模式
description: 掌握各平台实体基类（Light/Sensor/Switch/BinarySensor/Climate/Cover 等）的使用、PLATFORM_SCHEMA、async_forward_entry_setups 转发、EntityDescription 声明式模式、async_register_entity_service 实体服务注册与 supported_features 位标志
tags: [home-assistant, smart-home, platform, entity, light, sensor, switch, climate, cover, entity-description, platform-schema]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 源码
  - id: facts-components
    resource: "/references/facts-components.md"
    title: Home Assistant Components 事实清单
  - id: facts-helpers
    resource: "/references/facts-helpers.md"
    title: Home Assistant Helpers 事实清单
---

# 平台开发模式

平台（platform）是 Home Assistant 对设备能力的标准化抽象。每个平台定义一类实体的状态模型、属性、服务和设备类别。集成开发者通过继承平台实体基类（如 `LightEntity`、`SensorEntity`）创建设备实体，并通过平台转发机制注册到 HA。本文聚焦"如何开发平台实体"，涵盖基类选择、EntityDescription 模式、平台 schema、服务注册和能力声明。

## 实体继承层次

所有平台实体最终继承自 `Entity` 基类（helpers/entity.py）。[实体模型](/concepts/09-entity-model.md)已详细介绍了 Entity 的属性体系和生命周期。平台层在此基础上扩展平台特有的状态、属性和服务。

```text
Entity
├── ToggleEntity (is_on / async_turn_on / async_turn_off / async_toggle)
│   ├── LightEntity
│   ├── SwitchEntity
│   └── BaseAutomationEntity → AutomationEntity (+ RestoreEntity)
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

`ToggleEntity`（事实 #47）是可开关实体的中间基类，添加了 `is_on` 抽象属性和 `async_turn_on`/`async_turn_off`/`async_toggle` 方法，自动将 `is_on` 映射为 `STATE_ON`/`STATE_OFF`。`RestoreEntity` 是 mixin，提供 `async_get_last_state()` 和 `async_get_last_extra_data()` 用于实体重启后恢复状态。

## 平台模块结构

每个平台模块（如 `light.py`、`sensor.py`）在集成目录中实现一个标准入口函数：

```python
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MyConfigEntry

async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        MyLight(coordinator, device)
        for device in coordinator.devices
        if device.has_light
    )
```

`async_setup_entry` 是 ConfigEntry 模式下的平台入口（对比平台自身的 `async_setup` 是 YAML 入口）。它接收三个参数：`hass` 实例、`config_entry` 和 `async_add_entities` 回调。回调用于向平台注册实体实例，可以一次性传入列表或生成器，也可以在设备发现后延迟调用。

Tuya 的 light 平台使用动态发现模式（light.py:370-400）：在 `async_setup_entry` 中注册 `async_discover_device` 回调，当新设备发现时通过信号触发回调创建实体。这是推送型集成的典型模式——实体不是一次性全部创建，而是在设备上线时动态添加。

## PLATFORM_SCHEMA：YAML 平台配置

每个平台模块定义 `PLATFORM_SCHEMA`，用于验证 YAML 配置中的平台参数（事实 #53、#78）：

```python
from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=55443): cv.port,
})
```

`PLATFORM_SCHEMA` 本身引用 `cv.PLATFORM_SCHEMA`（light/__init__.py:46），后者是所有平台共享的基础 schema，包含 `platform` 字段（指定集成 domain）和可选的通用字段（名称、扫描间隔等）。`PLATFORM_SCHEMA_BASE` 是更基础的版本，不包含实体名称等可选字段。

现代集成优先使用 ConfigFlow，通常不需要扩展 PLATFORM_SCHEMA。ConfigEntry 模式下配置通过 ConfigFlow 收集并存储在 `entry.data` 中，平台模块直接从 entry 读取。

## EntityDescription 声明式模式

EntityDescription 是声明实体元数据的推荐方式（事实 #48）。每个平台提供自己的 EntityDescription 子类，扩展平台特有字段。

### LightEntityDescription

```python
@dataclass(frozen=True)
class LightEntityDescription(ToggleEntityDescription):
    color_mode: ColorMode | None = None
    supported_color_modes: set[ColorMode] | None = None
    ...
```

`LightEntityDescription` 继承自 `ToggleEntityDescription`，使用 `frozen_or_thawed=True` 参数（light/__init__.py:719）支持可变/不可变双模式。LightEntity 的缓存属性集合包含 14 个属性（事实 #83）：`brightness`、`color_mode`、`hs_color`、`xy_color`、`rgb_color`、`rgbw_color`、`rgbww_color`、`color_temp_kelvin`、`min_color_temp_kelvin`、`max_color_temp_kelvin`、`effect_list`、`effect`、`supported_color_modes`、`supported_features`。

### SensorEntityDescription

```python
class SensorEntityDescription(EntityDescription):
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit_of_measurement: str | None = None
    suggested_unit_of_measurement: str | None = None
    suggested_display_precision: int | None = None
    options: list[str] | None = None
    last_reset: datetime | None = None
```

Sensor 实体的状态通过 `native_value` 属性提供（而非直接设置 `_attr_state`），`state` 属性由基类从 `native_value` 计算并做单位转换（sensor/__init__.py:197-205）。子类不应直接设置 `_attr_state`，而应设置 `_attr_native_value`。

### 自定义描述类

集成可以扩展平台描述类添加自定义字段。Tuya 定义了 `TuyaLightEntityDescription`（light.py:34-44），添加了 `brightness`/`color_data`/`color_mode`/`color_temp` 等 DPCode 字段，用于映射 Tuya 设备的数据点：

```python
@dataclass(frozen=True)
class TuyaLightEntityDescription(LightEntityDescription):
    brightness_max: DPCode | None = None
    brightness_min: DPCode | None = None
    brightness: DPCode | tuple[DPCode, ...] | None = None
    color_data: DPCode | tuple[DPCode, ...] | None = None
    color_mode: DPCode | None = None
    color_temp: DPCode | tuple[DPCode, ...] | None = None
```

然后以 `DeviceCategory` 为键建立描述映射表（light.py:47），创建设备实体时按设备类别查找对应的描述元组。

## 平台特有抽象

### Light 平台

Light 平台是最复杂的平台之一，定义了颜色模式、亮度、色温、效果等丰富能力（事实 #51-91）：

- `ColorMode` 枚举：`UNKNOWN`、`ONOFF`、`BRIGHTNESS`、`COLOR_TEMP`、`HS`、`XY`、`RGB`、`RGBW`、`RGBWW`、`WHITE`（事实 #56）
- `LightEntityFeature(IntFlag)`：`EFFECT=4`、`FLASH=8`、`TRANSITION=32`（事实 #63）
- `capability_attributes` 返回 `supported_color_modes`、`min/max_color_temp_kelvin`、`effect_list`（事实 #86）
- 注册了 `turn_on`、`turn_off`、`toggle` 三个实体服务（事实 #87）

灯光实体必须至少支持一种颜色模式。`filter_supported_color_modes` 函数过滤不一致的模式组合——若 `ONOFF` 或 `BRIGHTNESS` 与其他模式共存则移除（事实 #88），因为这两个模式必须是唯一支持的模式（事实 #57-58）。

### Sensor 平台

Sensor 平台提供 50+ 种设备类（事实 #94-104），分为非数值类（DATE、ENUM、TIMESTAMP、UPTIME）和数值类（TEMPERATURE、HUMIDITY、POWER、ENERGY 等）。`SensorStateClass`（事实 #106）定义状态统计语义：

- `MEASUREMENT`：当前时刻测量值（如温度）
- `MEASUREMENT_ANGLE`：角度测量值
- `TOTAL`：总量（如净能耗，可增减）
- `TOTAL_INCREASING`：单调递增总量（如消耗燃气量）

`UNIT_CONVERTERS` 字典将设备类映射到单位转换器（事实 #119），Sensor 实体根据用户配置的单位系统自动转换 `native_value`。Sensor 和 BinarySensor 实体不允许 `entity_category=CONFIG`（事实 #120、#139），否则抛出 `HomeAssistantError`——配置类参数应使用 switch/number/select 等可写平台。

### Switch/BinarySensor 平台

Switch 继承 ToggleEntity，定义 `SwitchDeviceClass`（OUTLET/SWITCH），注册 `turn_on`/`turn_off`/`toggle` 服务（事实 #121-125）。

BinarySensor 是只读二值传感器，`_attr_is_on` 为 `bool | None`（事实 #137），定义 28 种设备类（事实 #128），包括 DOOR（开/关）、MOTION（检测/清除）、OCCUPANCY（有人/无人）、PROBLEM（问题/正常）、CONNECTIVITY（连接/断开）等。每种设备类的 On/Off 语义在文档注释中明确定义（事实 #129-136）。

### Climate 平台

Climate 平台定义 HVAC 控制抽象（事实 #141-155）：

- `HVACMode`：OFF、HEAT、COOL、HEAT_COOL、AUTO、DRY、FAN_ONLY
- `HVACAction`：COOLING、HEATING、IDLE、OFF 等当前运行动作
- `ClimateEntityFeature(IntFlag)`：TARGET_TEMPERATURE=1、FAN_MODE=8、PRESET_MODE=16、SWING_MODE=32、TURN_ON=256 等
- 注册了 10 个服务，包括 `set_hvac_mode`、`set_temperature`、`set_preset_mode`、`set_fan_mode`、`set_swing_mode` 等

`ClimateEntity.state` 返回 `hvac_mode.value`（事实 #155），默认温度范围 7-35°C，湿度范围 30-99%（事实 #152-153）。

### Cover 平台

Cover 平台定义窗帘/卷帘/车库门等位置可控实体（事实 #156-161）：

- `CoverDeviceClass`：AWNING、BLIND、CURTAIN、DOOR、GARAGE、GATE、SHADE、SHUTTER、WINDOW、DAMPER
- `CoverEntityFeature(IntFlag)`：OPEN=1、CLOSE=2、SET_POSITION=4、STOP=8、OPEN_TILT=16、CLOSE_TILT=32、STOP_TILT=64、SET_TILT_POSITION=128
- `CoverState`：CLOSED、CLOSING、OPEN、OPENING
- 注册了 10 个服务，包括位置控制和倾斜控制

### 其他平台

- **Select**：下拉选择实体，`SelectEntityDescription` 含 `options` 列表，注册 `select_option`/`select_first`/`select_last`/`select_next`/`select_previous` 五个服务（事实 #171-176）
- **Number**：数值输入实体，支持 AUTO/BOX/SLIDER 三种模式（`NumberMode`），默认范围 0.0-100.0，注册 `set_value` 服务（事实 #177-182）
- **Button**：按钮实体，继承 `RestoreEntity`，`_attr_should_poll=False`，注册 `press` 服务，支持 IDENTIFY/RESTART/UPDATE 三种设备类（事实 #183-187）
- **Camera**：摄像头实体，`_attr_should_poll=False`，支持 ON_OFF/STREAM 特性，注册 `snapshot`/`play_stream`/`record` 等 7 个服务（事实 #188-194）
- **MediaPlayer**：媒体播放器，支持 TV/SPEAKER/RECEIVER/PROJECTOR 设备类，定义 PLAYING/PAUSED/IDLE/OFF 等状态和 PAUSE/VOLUME_SET/PLAY_MEDIA 等丰富特性标志（事实 #162-170）

## async_register_entity_service：实体级服务

平台通过 `EntityComponent.async_register_entity_service` 注册实体级服务（事实 #214）。这类服务自动解析服务调用中的 `entity_id` 目标，对匹配的实体调用指定方法：

```python
component.async_register_entity_service(
    SERVICE_TURN_ON,
    vol.All(cv.make_entity_service_schema(LIGHT_TURN_ON_SCHEMA), preprocess_data),
    async_handle_light_on_service,
)
```

四个参数分别是：
1. 服务名称
2. 服务参数 schema（voluptuous）
3. 处理函数（async，接收实体实例和 ServiceCall）
4. 可选的所需特性列表（`supported_features` 位掩码），只有具备这些特性的实体才会被调用

Light 平台注册服务时使用 `preprocess_data` 预处理函数（light/__init__.py:495-505），将 `entity_id`/`device_id`/`area_id` 等目标字段提取出来，剩余字段作为 `params` 传给处理函数。`filter_turn_on_params`/`filter_turn_off_params` 根据实体的 `supported_features` 过滤不支持的参数。

集成开发者通常不需要直接调用 `async_register_entity_service`——平台基类已注册标准服务。但如果需要注册自定义实体服务，可以在平台的 `async_setup` 中通过 `component.async_register_entity_service` 添加。

## supported_features：能力位标志

每个平台使用 `IntFlag` 枚举定义实体支持的可选功能。实体通过 `_attr_supported_features` 声明能力：

```python
from homeassistant.components.light import LightEntity, LightEntityFeature, ColorMode

class MyLight(LightEntity):
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION | LightEntityFeature.FLASH
```

位标志允许组合多个特性（使用 `|` 运算符）。服务调用时，平台检查实体是否具备所需特性，不具备的实体会被跳过或返回错误。`capability_attributes` 属性将 supported_features 暴露给前端，前端据此显示或隐藏相关控件。

## 轮询与推送

实体有两种数据更新模式：

**轮询模式（默认）**：`_attr_should_poll = True`，平台按 `SCAN_INTERVAL` 定期调用实体的 `async_update()` 方法。每个平台定义默认扫描间隔：Light/Sensor/Switch/BinarySensor/Select/Number/Button 为 30 秒，Climate 为 60 秒，Cover 为 15 秒，MediaPlayer 为 10 秒（事实 #55、#93、#122、#163、#172、#178、#184、#142、#157、#189、#203）。Switch 和 Select 还有 `MIN_TIME_BETWEEN_SCANS = 10 秒` 的最小间隔限制（事实 #140）。

**推送模式**：`_attr_should_poll = False`，实体在数据到达时主动调用 `schedule_update_ha_state()` 或 `async_write_ha_state()`。适用于 MQTT、WebSocket、云端推送等实时通信场景。Button 和 Camera 默认不轮询（事实 #186、#192）。

## 实体创建最佳实践

1. **使用 EntityDescription 声明元数据**：将设备类、状态类、单位、翻译键等静态信息聚合到 EntityDescription 中，避免散落的 `_attr_*` 赋值。
2. **提供稳定 unique_id**：使用设备序列号、MAC 地址或 UUID 拼接平台键，如 `f"{device.id}_{description.key}"`。
3. **正确设置 device_info**：至少提供一组 `identifiers={(DOMAIN, device.id)}`，关联到设备注册表。
4. **推送型实体禁用轮询**：设置 `_attr_should_poll = False`，在回调中更新状态。
5. **使用 coordinator 模式**：多实体共享数据时使用 `DataUpdateCoordinator`，避免 N 个实体独立轮询。
6. **异步初始化在 async_added_to_hass**：不在 `__init__` 中执行 I/O，连接建立和订阅注册放在 `async_added_to_hass` 中。
7. **清理资源**：通过 `self.async_on_remove()` 注册取消订阅、关闭连接等清理回调。
8. **声明 supported_features**：根据设备实际能力精确声明，不要声明不支持的特性。
9. **使用标准设备类和单位**：从平台的 `const` 模块导入 `SensorDeviceClass`、`UnitOfTemperature` 等常量，而非硬编码字符串。

## 延伸阅读

- [实体模型](/concepts/09-entity-model.md)
- [集成架构](/concepts/14-component-architecture.md)
- [配置流](/concepts/15-config-flow.md)
- [Helpers 工具库](/concepts/12-helpers-library.md)
- [注册表](/concepts/10-registries.md)
- [hassfest 工具链](/concepts/17-hassfest-tooling.md)

## 相关概念

- [集成架构](/concepts/14-component-architecture.md) — 平台模块由集成的 async_setup_entry 通过 platform.async_forward_entry_setups 转发加载
- [实体模型](/concepts/09-entity-model.md) — 各平台 Entity 子类（LightEntity、SensorEntity 等）继承自 Entity 基类
- [配置流](/concepts/15-config-flow.md) — ConfigEntry 为平台实体提供配置数据和运行时数据
- [hassfest 工具链](/concepts/17-hassfest-tooling.md) — hassfest 验证平台代码规范、supported_features 和翻译键完整性
