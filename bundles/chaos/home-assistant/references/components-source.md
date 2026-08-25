---
type: Reference
title: Home Assistant Components 集成源码
description: Home Assistant 组件集成层源码登记，包含 manifest.json 规范、实体平台、ConfigFlow、服务发现与代表性集成
tags: [home-assistant, smart-home, components, integrations, source, reference, python]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-components
    resource: "/references/facts-components.md"
    title: Home Assistant Components 集成模式事实清单
---

# Home Assistant Components 集成源码

## 概述

`homeassistant/components/` 是 Home Assistant 的集成层，包含 2000+ 设备和服务集成。每个集成是一个以 domain 命名的目录，通过 `manifest.json` 自描述，由 `loader.Integration` 加载，经 `setup.py` 初始化。

## 集成目录标准结构

每个集成目录 `<domain>/` 典型包含：

| 文件 | 必需 | 说明 |
|------|------|------|
| `manifest.json` | 是 | 集成清单（domain/name/documentation/codeowners 等） |
| `__init__.py` | 是 | 集成入口，定义 `async_setup` 和/或 `async_setup_entry` |
| `const.py` | 否 | 域内常量（DOMAIN、PLATFORM 列表等） |
| `config_flow.py` | 条件 | ConfigFlow 配置向导（manifest 声明 config_flow 时必需） |
| `strings.json` | 条件 | 翻译字符串（核心集成必需） |
| `services.yaml` | 条件 | 服务描述（注册了服务时必需） |
| `quality_scale.yaml` | 否 | 质量等级规则状态 |
| `<platform>.py` | 否 | 平台实现（light.py/sensor.py/switch.py 等） |
| `coordinator.py` | 否 | 数据更新协调器 |
| `entity.py` | 否 | 实体基类定义 |
| `translations/` | 否 | 自定义集成翻译文件（en.json 等） |

## manifest.json 字段规范

| 字段 | 必需 | 类型 | 说明 |
|------|------|------|------|
| `domain` | 是 | string | 集成唯一标识，小写蛇形，须与目录名一致 |
| `name` | 是 | string | 人类可读名称 |
| `documentation` | 是 | string | 文档 URL，须为 `https://www.home-assistant.io/integrations/<domain>` |
| `codeowners` | 是 | string[] | GitHub 用户名/团队，须以 `@` 开头 |
| `integration_type` | 否 | string | hub/service/entity/system/hardware/helper/device/virtual，默认 hub |
| `iot_class` | 条件 | string | cloud_push/local_push/cloud_polling/local_polling/assumed_state/calculated |
| `config_flow` | 否 | bool | 是否支持 GUI 配置 |
| `dependencies` | 否 | string[] | 硬依赖（先于本集成加载） |
| `after_dependencies` | 否 | string[] | 软依赖（在本集成之前加载，若存在） |
| `requirements` | 否 | string[] | Python 依赖包（版本锁定） |
| `zeroconf` | 否 | list | mDNS/DNS-SD 发现规则 |
| `dhcp` | 否 | list | DHCP 发现规则（MAC/hostname） |
| `ssdp` | 否 | list | SSDP/UPnP 发现规则 |
| `usb` | 否 | list | USB 设备发现规则（vid/pid） |
| `bluetooth` | 否 | list | 蓝牙发现规则 |
| `quality_scale` | 否 | string | bronze/silver/gold/platinum/internal/custom/no_score/legacy |
| `single_config_entry` | 否 | bool | 是否仅允许单个配置条目 |
| `loggers` | 否 | string[] | 集成使用的 Python logger 名称 |
| `version` | 条件 | string | 自定义集成必需，符合 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 |
| `issue_tracker` | 条件 | string | 自定义集成问题追踪 URL |
| `import_executor` | 否 | bool | 是否在线程池中导入代码 |

## integration_type 分类

| 类型 | 说明 | 代表集成 |
|------|------|---------|
| `hub` | 中心枢纽型，连接设备并转发到多个平台 | tuya, hue, zwave_js, mqtt |
| `service` | 服务型，提供 API 服务 | mqtt, anthropic |
| `entity` | 实体平台型，直接提供实体 | conversation |
| `system` | 系统内置型 | assist_pipeline, default_config, automation |
| `device` | 设备型 | - |
| `hardware` | 硬件型 | - |
| `helper` | 辅助型 | - |
| `virtual` | 虚拟集成，不包含代码，指向 supported_by | - |

## iot_class 通信类别

| 类别 | 说明 | 代表集成 |
|------|------|---------|
| `cloud_push` | 云端推送 | tuya |
| `local_push` | 本地推送 | mqtt, hue, zwave_js |
| `cloud_polling` | 云端轮询 | anthropic |
| `local_polling` | 本地轮询 | - |
| `assumed_state` | 假设状态 | - |
| `calculated` | 计算状态 | - |

## 实体平台（Platform）

平台定义标准化实体类型和服务。每个平台在 `async_setup` 中创建 `EntityComponent` 实例。

### 核心平台列表

| 平台域 | 基类 | 扫描间隔 | 注册服务 |
|--------|------|---------|---------|
| `light` | `LightEntity(ToggleEntity)` | 30s | turn_on/turn_off/toggle |
| `sensor` | `SensorEntity(Entity)` | 30s | - |
| `binary_sensor` | `BinarySensorEntity(Entity)` | 30s | - |
| `switch` | `SwitchEntity(ToggleEntity)` | 30s | turn_on/turn_off/toggle |
| `climate` | `ClimateEntity(Entity)` | 60s | set_hvac_mode/set_temperature 等 10 个 |
| `cover` | `CoverEntity(Entity)` | 15s | open/close/stop/set_position 等 10 个 |
| `camera` | `Camera(Entity)` | 30s | snapshot/play_stream/record 等 7 个 |
| `media_player` | `MediaPlayerEntity(Entity)` | 10s | play/pause/volume 等 |
| `select` | `SelectEntity(Entity)` | 30s | select_option 等 5 个 |
| `number` | `NumberEntity(Entity)` | 30s | set_value |
| `button` | `ButtonEntity(RestoreEntity)` | 30s | press |
| `automation` | `AutomationEntity(ToggleEntity, RestoreEntity)` | - | trigger/toggle/reload 等 5 个 |
| `fan` | - | - | - |
| `lock` | - | - | - |
| `alarm_control_panel` | - | - | - |
| `humidifier` | - | - | - |
| `siren` | - | - | - |
| `vacuum` | - | - | - |
| `valve` | - | - | - |
| `update` | - | - | - |
| `event` | - | - | - |
| `image` | - | - | - |
| `scene` | - | - | - |
| `script` | - | - | - |

### Light 平台关键抽象

| 名称 | 类型 | 说明 |
|------|------|------|
| `ColorMode` | Enum | UNKNOWN/ONOFF/BRIGHTNESS/COLOR_TEMP/HS/XY/RGB/RGBW/RGBWW/WHITE |
| `LightEntityFeature` | IntFlag | EFFECT=4, FLASH=8, TRANSITION=32 |
| `LightEntityDescription` | dataclass | 继承 ToggleEntityDescription |
| `ATTR_BRIGHTNESS` | 常量 | 亮度 0..255 |
| `ATTR_RGB_COLOR` | 常量 | RGB 三元组 |
| `ATTR_COLOR_TEMP_KELVIN` | 常量 | 色温（开尔文） |
| `DEFAULT_MIN_KELVIN` | 常量 | 2000（500 mireds） |
| `DEFAULT_MAX_KELVIN` | 常量 | 6535（153 mireds） |
| `filter_supported_color_modes` | 函数 | 过滤不兼容的颜色模式组合 |

### Sensor 平台关键抽象

| 名称 | 类型 | 说明 |
|------|------|------|
| `SensorDeviceClass` | StrEnum | 60+ 设备类（TEMPERATURE/HUMIDITY/POWER/ENERGY 等） |
| `SensorStateClass` | StrEnum | MEASUREMENT/TOTAL/TOTAL_INCREASING/MEASUREMENT_ANGLE |
| `SensorEntityDescription` | dataclass | device_class/state_class/native_unit_of_measurement 等 |
| `UNIT_CONVERTERS` | 字典 | 设备类到单位转换器映射 |
| `NON_NUMERIC_DEVICE_CLASSES` | 集合 | DATE/ENUM/TIMESTAMP/UPTIME |

### Climate 平台关键抽象

| 名称 | 类型 | 说明 |
|------|------|------|
| `HVACMode` | StrEnum | OFF/HEAT/COOL/HEAT_COOL/AUTO/DRY/FAN_ONLY |
| `HVACAction` | StrEnum | COOLING/HEATING/IDLE/OFF 等 8 种 |
| `ClimateEntityFeature` | IntFlag | TARGET_TEMPERATURE=1, FAN_MODE=8, PRESET_MODE=16 等 |
| `DEFAULT_MIN_TEMP` | 常量 | 7°C |
| `DEFAULT_MAX_TEMP` | 常量 | 35°C |

## 集成设置函数模式

每个集成通过以下函数与核心交互：

### YAML 配置入口

```python
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
```

- 在 bootstrap 阶段调用
- 创建 `EntityComponent` 实例并存入 `hass.data[DATA_COMPONENT]`
- 返回 True 表示成功

### ConfigEntry 入口

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
```

- ConfigFlow 完成后调用
- 建立设备连接、创建协调器
- 通过 `async_forward_entry_setups(entry, PLATFORMS)` 转发到平台
- 返回 True 表示成功

### 卸载入口

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
```

- 清理连接、取消订阅
- 通过 `async_unload_platforms(entry, PLATFORMS)` 卸载平台
- 返回 True 表示成功

### 标准设置流程

```python
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR, ...]

async def async_setup_entry(hass, entry):
    coordinator = MyCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

## 代表性集成

### Tuya（云端 IoT 平台）

| 属性 | 值 |
|------|-----|
| domain | `tuya` |
| integration_type | `hub` |
| iot_class | `cloud_push` |
| config_flow | true |
| requirements | `tuya-device-sharing-sdk==0.2.10`, `tuya-device-handlers==0.0.24` |
| 转发平台数 | 18（alarm_control_panel/binary_sensor/button/camera/climate/cover/event/fan/humidifier/light/number/scene/select/sensor/siren/switch/vacuum/valve） |
| 发现方式 | DHCP（11 条 MAC 前缀规则） |

### MQTT（消息协议）

| 属性 | 值 |
|------|-----|
| domain | `mqtt` |
| integration_type | `service` |
| iot_class | `local_push` |
| requirements | `paho-mqtt==2.1.0` |
| 支持平台数 | 31（ENTITY_PLATFORMS） |
| quality_scale | `platinum` |
| single_config_entry | true |
| 关键函数 | `async_subscribe`, `async_publish` |

### Philips Hue

| 属性 | 值 |
|------|-----|
| domain | `hue` |
| integration_type | `hub` |
| iot_class | `local_push` |
| requirements | `aiohue==4.8.1` |
| 发现方式 | zeroconf (`_hue._tcp.local.`), homekit (`BSB002`) |

### Z-Wave JS

| 属性 | 值 |
|------|-----|
| domain | `zwave_js` |
| integration_type | `hub` |
| iot_class | `local_push` |
| requirements | `zwave-js-server-python==0.72.0` |
| 转发平台数 | 16 |
| 发现方式 | USB（4 条规则）, zeroconf |
| 连接超时 | 10 秒 |

### default_config（元集成）

| 属性 | 值 |
|------|-----|
| domain | `default_config` |
| integration_type | `system` |
| 机制 | `async_setup` 直接返回 True，通过 dependencies 拉取 21 个核心集成 |
| 包含 | assist_pipeline, bluetooth, cloud, conversation, energy, history, mobile_app, stream, sun, zeroconf 等 |

### Anthropic（AI 服务）

| 属性 | 值 |
|------|-----|
| domain | `anthropic` |
| integration_type | `service` |
| iot_class | `cloud_polling` |
| requirements | `anthropic==0.108.0` |
| 转发平台 | ai_task, conversation |
| 特性 | ConfigSubentry 多 API key 管理，版本迁移 2.1→2.2→2.3 |

### assist_pipeline（语音助手）

| 属性 | 值 |
|------|-----|
| domain | `assist_pipeline` |
| integration_type | `system` |
| iot_class | `local_push` |
| 依赖 | conversation, stt, tts, wake_word |
| requirements | `pymicro-vad==1.0.1`, `pyspeex-noise==1.0.2` |

## 系统集成

### API（REST API）

| 属性 | 值 |
|------|-----|
| domain | `api` |
| 功能 | 13 个 HTTP 视图（状态/事件/服务/配置/模板等） |
| SSE 心跳 | 50 秒 |
| 服务超时 | 10 秒 |

### WebSocket API

| 属性 | 值 |
|------|-----|
| domain | `websocket_api` |
| URL | `/api/websocket` |
| 依赖 | `http` |
| 最大待处理消息 | 4096 |
| 装饰器 | `@websocket_command`, `@async_response`, `@require_admin`, `@ws_require_user` |

### Frontend

| 属性 | 值 |
|------|-----|
| domain | `frontend` |
| 功能 | Web UI、主题管理、面板注册 |
| 服务 | set_theme, reload_themes |
| 默认主题色 | `#2980b9` |

### Automation

| 属性 | 值 |
|------|-----|
| domain | `automation` |
| 三要素 | triggers, conditions, actions |
| 实体基类 | `AutomationEntity(ToggleEntity, RestoreEntity)` |
| 服务 | trigger, toggle, turn_on, turn_off, reload |
| 事件 | `automation_triggered`, `automation_reloaded` |
| 特性 | Blueprint 支持 |

## ConfigFlow 与发现

| 来源常量 | 值 | 说明 |
|---------|-----|------|
| `SOURCE_USER` | `"user"` | 用户手动配置 |
| `SOURCE_DISCOVERY` | `"discovery"` | 通用发现 |
| `SOURCE_ZEROCONF` | `"zeroconf"` | mDNS 发现 |
| `SOURCE_DHCP` | `"dhcp"` | DHCP 发现 |
| `SOURCE_SSDP` | `"ssdp"` | SSDP 发现 |
| `SOURCE_BLUETOOTH` | `"bluetooth"` | 蓝牙发现 |
| `SOURCE_USB` | `"usb"` | USB 发现 |
| `SOURCE_HASSIO` | `"hassio"` | Hass.io addon |
| `SOURCE_HOMEKIT` | `"homekit"` | HomeKit 发现 |
| `SOURCE_MQTT` | `"mqtt"` | MQTT 发现 |
| `SOURCE_IMPORT` | `"import"` | YAML 导入 |
| `SOURCE_REAUTH` | `"reauth"` | 重新认证 |
| `SOURCE_RECONFIGURE` | `"reconfigure"` | 重新配置 |
| `SOURCE_IGNORE` | `"ignore"` | 用户忽略 |

### ConfigFlow 结果类型

| FlowResultType | 说明 |
|---------------|------|
| `FORM` | 显示表单 |
| `CREATE_ENTRY` | 创建配置条目 |
| `ABORT` | 中止流程 |
| `EXTERNAL_STEP` | 外部跳转（如 OAuth） |
| `EXTERNAL_STEP_DONE` | 外部步骤完成 |
| `SHOW_PROGRESS` | 显示进度 |
| `SHOW_PROGRESS_DONE` | 进度完成 |
| `MENU` | 显示菜单 |

## 生成文件（homeassistant/generated/）

hassfest 从 manifest.json 收集发现规则，自动生成以下文件：

| 文件 | 来源字段 | 说明 |
|------|---------|------|
| `dhcp.py` | `dhcp` | DHCP 发现规则 |
| `zeroconf.py` | `zeroconf` + `homekit` | mDNS 发现规则 |
| `ssdp.py` | `ssdp` | SSDP 发现规则 |
| `usb.py` | `usb` | USB 发现规则 |
| `bluetooth.py` | `bluetooth` | 蓝牙发现规则 |
| `mqtt.py` | MQTT 相关 | MQTT 发现规则 |
| `labs.py` | 实验性功能 | 实验室特性 |
