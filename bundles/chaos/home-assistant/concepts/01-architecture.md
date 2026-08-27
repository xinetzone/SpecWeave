---
type: Concept
title: 三层架构：核心-集成-平台
description: 理解 Home Assistant 的三层架构设计，核心层、集成层与平台层的职责划分、交互方式和设计理念
tags: [home-assistant, smart-home, architecture, core, integration, platform]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 集成源码
  - id: helpers-util-source
    resource: "/references/helpers-util-source.md"
    title: Home Assistant Helpers 与 Util 源码
---

# 三层架构：核心-集成-平台

## 架构设计理念

Home Assistant 面对的核心挑战是：如何让数百种通信协议、数千种设备在一个系统中协同工作，同时保持代码的可维护性和可扩展性？

HA 的答案是**三层分离架构**：

1. **核心层（Core）**：提供与设备无关的运行时基础设施
2. **集成层（Integration）**：实现与具体设备/服务的通信逻辑
3. **平台层（Platform）**：定义标准化实体类型和服务接口

这种分层遵循了关注点分离原则：核心层不关心设备是什么，集成层不关心实体如何被使用，平台层不关心数据从哪里来。每一层都有明确的契约，层与层之间通过定义良好的接口交互。

## 核心层（Core）

### 定位

核心层是 HA 的运行时内核，位于 `homeassistant/` 根目录。它不包含任何设备特定逻辑，而是提供所有集成共用的基础设施。核心层的代码必须保持稳定，因为 2000+ 集成都依赖它的 API。

### 核心组件

核心层由 `HomeAssistant` 类（定义于 `core.py:379`）统一持有以下子系统：

| 子系统 | 类 | 职责 |
|--------|-----|------|
| 事件总线 | `EventBus` | 发布-订阅消息传递，系统内部所有通信的基础 |
| 状态机 | `StateMachine` | 存储和查询实体当前状态，状态变更时触发事件 |
| 服务注册中心 | `ServiceRegistry` | 注册和调用服务，服务是跨集成操作的主要方式 |
| 配置对象 | `Config` | 运行时核心配置（位置、时区、单位、白名单等） |
| 认证管理器 | `AuthManager` | 用户认证、令牌管理、权限控制 |
| 配置条目 | `ConfigEntries` | 管理集成的配置实例及其生命周期 |

### 核心层的设计特点

**事件驱动**：核心层不直接调用集成的方法，而是通过事件总线发布事件。集成订阅感兴趣的事件并响应。这种松耦合意味着核心层不需要知道哪些集成在监听。

**异步优先**：整个核心层基于 `asyncio`。所有 I/O 操作（网络请求、文件读写、设备通信）都是异步的，避免阻塞事件循环。CPU 密集型任务通过 `HassJob` 调度到线程池执行。

**单线程模型**：HA 在单个事件循环线程中运行所有集成代码。这消除了多线程锁的复杂性，但要求集成开发者不能阻塞事件循环。`block_async_io.py` 会在事件循环线程中检测阻塞调用。

**线程安全的数据共享**：`hass.data`（`HassDict` 类型）是集成间共享数据的标准方式，通过 `HassKey` 提供类型安全的数据存取。

## 集成层（Integration）

### 定位

集成层位于 `homeassistant/components/`，每个子目录是一个集成。集成是 HA 与外部世界（设备、服务、协议）的桥梁。它负责：

- 建立与设备/服务的连接
- 将设备数据转换为 HA 能理解的格式
- 创建实体并注册到平台
- 处理服务调用并转发到设备
- 管理配置和认证

### 集成的自描述机制

每个集成通过 `manifest.json` 文件自描述。加载器（`loader.py:667` 的 `Integration` 类）解析这个文件，获取集成的元数据：

```json
{
  "domain": "tuya",
  "name": "Tuya",
  "integration_type": "hub",
  "iot_class": "cloud_push",
  "config_flow": true,
  "dependencies": ["ffmpeg"],
  "requirements": ["tuya-device-sharing-sdk==0.2.10"],
  "codeowners": ["@Tuya"],
  "zeroconf": [],
  "dhcp": [{"hostname": "tuya_gw_*"}]
}
```

关键字段说明：

- `domain`：集成的唯一标识符，决定了目录名和实体 ID 前缀
- `integration_type`：集成类型（hub/service/entity/system/device/hardware/helper/virtual）
- `iot_class`：通信模式（cloud_push/local_push/cloud_polling/local_polling 等）
- `dependencies`：必须在本集成之前加载的其他集成
- `requirements`：需要安装的 Python 包
- 发现字段（`zeroconf`/`dhcp`/`ssdp`/`usb`/`bluetooth`）：自动设备发现规则

### 集成类型

不同类型的集成承担不同角色：

- **hub（枢纽型）**：连接一个中心设备/服务，然后将其子设备转发到多个平台。例如 Tuya 集成连接 Tuya 云，将灯转发到 light 平台、开关转发到 switch 平台、传感器转发到 sensor 平台。
- **service（服务型）**：提供 API 服务供其他集成使用。例如 MQTT 提供消息发布/订阅能力，其他集成可以依赖它。
- **entity（实体型）**：直接创建实体，不需要额外的 hub 连接。
- **system（系统型）**：提供 HA 内部功能。例如 `default_config` 通过依赖声明加载一组核心集成，`assist_pipeline` 提供语音助手管道。
- **virtual（虚拟型）**：不包含代码，通过 `supported_by` 字段指向实际实现的集成。

### 集成的设置流程

集成通过标准函数与核心交互：

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = MyCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

核心层在启动时根据依赖关系图确定加载顺序，然后调用 `async_setup_component()`（`setup.py:148`）初始化每个集成。设置有超时保护：Stage 0 子阶段 60 秒，Stage 1 120 秒，Stage 2 300 秒。

## 平台层（Platform）

### 定位

平台层定义了标准化的实体类型。如果说集成层解决"如何连接设备"，平台层解决"设备能做什么"。平台抽象使得上层应用（自动化、前端、API）可以用统一的方式操作不同品牌的同类设备。

每个平台对应一种设备能力类别，由一个全局常量标识：

```python
Platform.LIGHT      # 灯光：开关、亮度、颜色
Platform.SENSOR     # 传感器：数值、单位
Platform.SWITCH     # 开关：二元状态
Platform.CLIMATE    # 温控：温度、模式
Platform.COVER      # 窗帘：开合、位置
Platform.CAMERA     # 摄像头：视频流、截图
```

### 平台实体基类

每个平台提供一个实体基类，定义在 `homeassistant/components/<platform>/__init__.py` 或 `homeassistant/helpers/` 中：

```text
Entity（helpers/entity.py）
├── ToggleEntity（支持开关）
│   ├── LightEntity（灯光：亮度、颜色、色温）
│   ├── SwitchEntity（开关）
│   └── AutomationEntity（自动化）
├── SensorEntity（传感器：数值 + 单位）
├── BinarySensorEntity（二元传感器）
├── ClimateEntity（温控器）
├── CoverEntity（窗帘）
├── Camera（摄像头）
├── MediaPlayerEntity（媒体播放器）
├── SelectEntity（下拉选择）
├── NumberEntity（数字调节）
└── ButtonEntity（按钮）
```

所有实体继承自 `Entity` 基类（`helpers/entity.py`），它提供了统一的生命周期和属性接口：

```python
class MyLight(LightEntity):
    _attr_has_entity_name = True
    _attr_name = "客厅主灯"

    @property
    def is_on(self) -> bool:
        return self._state

    async def async_turn_on(self, **kwargs):
        await self._device.turn_on(brightness=kwargs.get("brightness"))
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._device.turn_off()
        self._state = False
        self.async_write_ha_state()
```

### 平台服务

每个平台除了定义实体接口，还注册标准化服务。例如 light 平台注册 `light.turn_on`、`light.turn_off`、`light.toggle` 三个服务。这些服务由 `EntityComponent`（`helpers/entity_component.py`）管理，自动路由到目标实体的对应方法。

服务调用流程：

```text
用户/自动化调用 light.turn_on
    → ServiceRegistry 查找服务
    → EntityComponent 遍历目标 entity_id
    → 调用每个实体的 async_turn_on(**data)
    → 实体更新状态 → StateMachine 写入 → state_changed 事件
```

### EntityComponent 与 EntityPlatform

平台层有两个关键管理类：

- **`EntityComponent`**（`helpers/entity_component.py`）：每个平台全局唯一实例，负责服务注册、实体添加/移除、平台级配置。在 `async_setup` 时创建并存入 `hass.data[DATA_COMPONENT]`。
- **`EntityPlatform`**（`helpers/entity_platform.py`）：每个集成-平台组合一个实例，负责将集成创建的实体连接到 `EntityComponent`，管理实体的生命周期和平台设置。

当集成调用 `async_forward_entry_setups(entry, [Platform.LIGHT, Platform.SENSOR])` 时，核心层为每个平台创建一个 `EntityPlatform`，调用集成的 `light.py`/`sensor.py` 中的 `async_setup_entry`，后者创建实体并通过 `EntityPlatform` 添加到系统中。

## 三层交互流程

以"用户打开 Tuya 灯"为例，展示三层如何协作：

1. **集成层**：Tuya 集成连接 Tuya 云，发现设备，创建 `TuyaLight(LightEntity)` 实例，注册到 light 平台
2. **平台层**：light 平台的 `EntityComponent` 注册了 `light.turn_on` 服务，实体 `light.tuya_living_room` 进入状态机
3. **核心层**：用户通过前端/API 调用 `light.turn_on`，`ServiceRegistry` 路由到 `EntityComponent`
4. **平台层**：`EntityComponent` 找到目标 `TuyaLight`，调用其 `async_turn_on`
5. **集成层**：`TuyaLight.async_turn_on` 调用 Tuya SDK 发送命令到云端
6. **核心层**：设备确认后，实体更新状态，`StateMachine` 写入新状态，`EventBus` 发布 `state_changed` 事件
7. **核心层**：前端通过 WebSocket 收到状态变更，更新 UI

```text
用户操作 → Core(ServiceRegistry) → Platform(EntityComponent)
    → Integration(TuyaLight.async_turn_on) → 设备/云
    → Platform(实体状态更新) → Core(StateMachine + EventBus)
    → 前端/自动化响应
```

## 设计优势

### 可扩展性

新增一个设备品牌只需创建一个集成，不需要修改核心层。新增一种设备类型只需添加一个平台，不影响已有集成。这使得 HA 能够支持 2000+ 集成和 20+ 平台而不导致代码混乱。

### 可替换性

同一个灯实体可以来自 Hue、Tuya 或 Zigbee，对自动化和前端完全透明。更换设备品牌后，自动化规则通常无需修改。

### 可测试性

三层都有独立的测试基础设施。核心层有单元测试，集成可以使用 `MockEntity`/`MockConfigEntry` 测试，平台有标准化的实体测试模式。

### 并行加载

核心层根据依赖图并行加载无依赖关系的集成（通过 `asyncio.gather`），加快启动速度。Stage 0/1/2 的分阶段设计确保基础设施先于业务集成就绪。

## 延伸阅读

- [HA 概览](/concepts/00-overview.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)
- [事件总线](/concepts/06-event-bus.md)

## 相关概念

- [HomeAssistant 核心对象](/concepts/03-core-object.md) — 核心层根对象，持有事件总线、状态机、服务注册表等子系统
- [实体模型](/concepts/09-entity-model.md) — 平台层的 Entity 基类体系与标准化实体抽象
- [集成架构](/concepts/14-component-architecture.md) — 集成层的目录结构、manifest 契约与生命周期三函数
- [平台开发模式](/concepts/16-platform-pattern.md) — 平台实体基类选择、EntityDescription 声明式模式与服务注册
