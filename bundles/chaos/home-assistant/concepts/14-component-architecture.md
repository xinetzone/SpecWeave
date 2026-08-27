---
type: Concept
title: 集成架构
description: 深入理解 Home Assistant 集成目录结构、manifest.json 字段契约、integration_type 与 iot_class 分类、async_setup/async_setup_entry/async_unload_entry 三函数生命周期以及依赖解析机制
tags: [home-assistant, smart-home, integration, manifest, component-architecture, setup, dependencies, iot-class, integration-type]
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
  - id: facts-tooling
    resource: "/references/facts-tooling.md"
    title: Home Assistant 工具链与测试事实清单
---

# 集成架构

集成（integration，源码中也称 component）是 Home Assistant 连接外部设备与服务的基本单元。每个集成是 `homeassistant/components/<domain>/` 下的一个 Python 包，通过 `manifest.json` 声明显式契约，由核心加载器动态发现、依赖解析和初始化。理解集成架构是开发 HA 集成的第一步——它决定了代码如何组织、何时加载、如何与核心及其他集成协作。

## 集成目录结构

一个现代集成的标准目录结构如下：

```text
homeassistant/components/my_integration/
├── __init__.py          # 集成入口：async_setup / async_setup_entry / async_unload_entry
├── manifest.json        # 集成清单（必需）
├── const.py             # 常量定义（DOMAIN、PLATFORMS、配置键等）
├── config_flow.py       # ConfigFlow 配置向导（manifest 中 config_flow=true 时需要）
├── strings.json         # 翻译字符串（核心集成）
├── services.yaml        # 服务描述（如果注册了服务）
├── quality_scale.yaml   # 质量等级规则状态
├── light.py             # light 平台实现（可选）
├── sensor.py            # sensor 平台实现（可选）
├── switch.py            # switch 平台实现（可选）
├── coordinator.py       # 数据协调器（可选，推荐使用 DataUpdateCoordinator）
├── entity.py            # 实体基类（可选）
└── diagnostics.py       # 诊断信息（可选，gold+ 要求）
```

并非所有文件都是必需的。最小集成只需 `manifest.json` 和 `__init__.py`。如果 manifest 声明 `config_flow: true`，则必须存在 `config_flow.py`（hassfest 的 config_flow 验证器会检查这一点）。如果集成注册了服务，必须有 `services.yaml` 描述服务参数。

## manifest.json：声明式契约

`manifest.json` 是集成的自描述文件，核心在不导入集成代码的情况下即可解析依赖图、安装 Python 包、生成服务发现索引。

### 必需字段

根据 hassfest 的 `INTEGRATION_MANIFEST_SCHEMA`（事实 #57），核心集成的 manifest 必须包含四个字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `domain` | 集成唯一标识符，小写蛇形命名，必须与目录名一致 | `"tuya"` |
| `name` | 人类可读名称 | `"Tuya"` |
| `documentation` | 文档 URL，核心集成必须以 `https://www.home-assistant.io/integrations/` 开头 | `"https://www.home-assistant.io/integrations/tuya"` |
| `codeowners` | GitHub 用户名/团队列表，SILVER 及以上等级必须提供 | `["@Tuya", "@zlinoliver"]` |

### 核心可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `config_flow` | `bool` | 是否支持 ConfigFlow GUI 配置，默认 `false` |
| `dependencies` | `list[str]` | 必须在本集成之前加载的集成 domain 列表 |
| `after_dependencies` | `list[str]` | 在本集成之前加载（若已配置），但不强制加载的集成 |
| `requirements` | `list[str]` | Python 依赖包，含版本锁定（如 `"aiohue==4.8.1"`） |
| `integration_type` | `str` | 集成类型，默认 `"hub"` |
| `iot_class` | `str` | IoT 通信类别 |
| `quality_scale` | `str` | 质量等级（bronze/silver/gold/platinum/internal 等） |
| `loggers` | `list[str]` | 集成使用的 Python logger 名称 |
| `single_config_entry` | `bool` | 是否只允许单个配置条目 |
| `version` | `str` | 自定义集成必需，核心集成不需要 |
| `issue_tracker` | `str` | 自定义集成的问题追踪 URL |
| `import_executor` | `bool` | 自定义集成是否在执行器中导入 |

### 服务发现字段

manifest 还支持多种自动发现字段，hassfest 会收集这些字段并生成 `homeassistant/generated/` 下的 Python 文件（事实 #83-89）：

- `zeroconf`：mDNS/DNS-SD 服务类型列表，如 hue 的 `["_hue._tcp.local."]`
- `homekit`：HomeKit 设备发现配置，如 hue 的 `{"models": ["BSB002"]}`
- `dhcp`：DHCP 发现规则列表，支持 `macaddress`（大写+通配符）、`hostname`、`registered_devices`
- `ssdp`：SSDP/UPnP 发现规则字典列表
- `usb`：USB 设备发现规则，含 `vid`/`pid`/`serial_number`/`manufacturer`/`description`/`known_devices`
- `bluetooth`：蓝牙发现规则，支持 `service_uuid`/`local_name`/`manufacturer_id` 等

### 自定义集成的差异

自定义集成（不在 core 仓库中的集成）的 manifest schema 在核心 schema 基础上扩展（事实 #66-67）：
- 必需额外的 `version` 字段，版本号必须符合 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 之一
- 可选 `issue_tracker` 和 `import_executor` 字段
- 文档 URL 使用 HTTPS 且不指向核心文档站点

## integration_type：集成类型

`IntegrationType` 是 StrEnum（事实 #43），支持 8 种类型：

| 类型 | 说明 | 典型示例 |
|------|------|----------|
| `hub` | 中心枢纽型，连接一个设备/服务并转发到多个平台 | tuya、hue、zwave_js |
| `service` | 服务型，提供云服务或平台能力 | mqtt、anthropic |
| `entity` | 实体平台型，直接提供实体 | conversation |
| `system` | 系统内置型，核心基础设施 | assist_pipeline、default_config |
| `device` | 设备型 | 单设备集成 |
| `hardware` | 硬件型 | 硬件板级支持 |
| `helper` | 辅助型，由用户创建的模板/辅助实体 | template、group |
| `virtual` | 虚拟集成，不包含代码，通过 `supported_by` 指向实际集成 | 品牌别名 |

`integration_type` 默认为 `"hub"`（事实 #41）。虚拟集成使用独立的 `VIRTUAL_INTEGRATION_MANIFEST_SCHEMA`，要求 `integration_type` 为 `"virtual"`，并使用 `vol.Exclusive` 确保 `iot_standards` 和 `supported_by` 互斥（事实 #65）。

## iot_class：通信类别

`iot_class` 描述集成与设备/服务的通信方式，影响 UI 展示和发现行为（事实 #50）。共有 6 种合法值：

| iot_class | 说明 | 示例 |
|-----------|------|------|
| `local_push` | 本地推送，设备主动上报状态变化 | mqtt、hue、zwave_js |
| `local_polling` | 本地轮询，定期请求设备状态 | 多数本地 HTTP API 集成 |
| `cloud_push` | 云端推送，通过云连接接收实时更新 | tuya |
| `cloud_polling` | 云端轮询，定期请求云端 API | anthropic |
| `assumed_state` | 假定状态，命令发出后不确定设备是否执行 | 单向红外遥控 |
| `calculated` | 计算型，状态由其他实体计算得出 | template、statistics |

并非所有集成都需要 `iot_class`。hassfest 维护了一个 `NO_IOT_CLASS` 列表（事实 #51），包含所有平台 domain（如 light、sensor）和 auth/automation/frontend 等系统集成——这些集成不应有 `iot_class` 字段。其他集成（虚拟集成除外）必须声明 `iot_class`，否则 hassfest 报错。

zeroconf 发现的 `always_discover` 标志基于 `iot_class` 通过 `homekit_always_discover()` 函数确定（事实 #85）——`local_push`/`local_polling` 类集成总是自动发现，云端类集成需要用户确认。

## 生命周期三函数

集成的初始化和清理通过三个标准异步函数完成。这些函数定义在集成的 `__init__.py` 中，由核心在适当的时机调用。

### async_setup：YAML 配置入口

```python
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from YAML configuration."""
    return True
```

`async_setup` 是传统的 YAML 配置入口（事实 #195）。它接收全局 `config` 字典（包含 `configuration.yaml` 中所有集成的配置），在集成的 ConfigEntry 设置之前调用。返回 `True` 表示初始化成功，返回 `False` 表示失败。

现代集成通常不在 `async_setup` 中做实际工作，而是声明仅支持 ConfigEntry：

```python
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
```

这告诉 HA 该集成不通过 YAML 配置，所有配置通过 ConfigFlow 完成（事实 #205）。Tuya 和 Anthropic 都使用这种模式。系统集成如 api、websocket_api、default_config 使用 `cv.empty_config_schema(DOMAIN)` 表示空配置（事实 #215）。

`async_setup` 仍然适合执行一次性全局初始化，例如注册自定义服务类型或执行配置迁移（Anthropic 在 `async_setup` 中调用 `async_migrate_integration` 处理旧版数据结构，事实 #211）。

### async_setup_entry：ConfigEntry 入口

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    return True
```

`async_setup_entry` 是现代集成的主要初始化入口（事实 #199）。它在用户通过 ConfigFlow 创建配置条目后调用，接收一个 `ConfigEntry` 对象，包含用户配置的 `data`、`options`、`unique_id`、`version` 等。

典型的 `async_setup_entry` 执行以下步骤（以 Tuya 和 Anthropic 为参考，事实 #201、#211）：

1. **创建运行时对象**：建立 API 客户端、数据协调器或设备监听器
2. **初始化连接**：在 executor 中执行阻塞初始化（如 Tuya 的 `listener.initialize`）
3. **存储运行时数据**：将运行时对象存入 `entry.runtime_data`
4. **注册设备**：将发现的设备注册到 DeviceRegistry
5. **转发平台设置**：调用 `hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)` 批量转发到多个平台

```python
PLATFORMS = [Platform.LIGHT, Platform.SENSOR, Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True
```

Tuya 在 executor 中初始化 `DeviceListener`（因为底层 SDK 是阻塞的），注册设备后转发到 18 个平台（事实 #201-202）。Anthropic 创建 `AnthropicCoordinator`，首次刷新后转发到 `ai_task` 和 `conversation` 两个平台，并注册选项变更监听器（事实 #211-212）。

如果设备暂时不可用，抛出 `ConfigEntryNotReady` 触发指数退避重试（最大等待 600 秒）。如果认证失败，抛出 `ConfigEntryAuthFailed` 触发重新认证流程。

### async_unload_entry：清理入口

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

`async_unload_entry` 在配置条目被卸载或重载时调用（事实 #200）。它必须清理 `async_setup_entry` 中分配的所有资源——关闭连接、停止订阅、移除监听器。标准模式是先调用 `async_unload_platforms` 卸载平台实体，成功后再清理集成级资源：

```python
async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = entry.runtime_data
        await coordinator.async_shutdown()
    return unload_ok
```

Tuya 在卸载平台后停止 MQ 连接并移除设备监听器（事实 #203）。`entry.async_on_unload()` 注册的回调会在卸载时自动调用，用于注册清理函数比手动重写 `async_unload_entry` 更安全。

### async_remove_entry：移除入口

可选的 `async_remove_entry` 在配置条目被完全删除时调用（事实 #204）。与 `async_unload_entry` 不同，后者在重载时也会调用，而 `async_remove_entry` 仅在用户删除集成时触发。适合执行撤销凭证、删除云端资源等不可逆操作。Tuya 在此函数中创建 Manager 并调用 `manager.unload()` 撤销 Tuya 云端凭证。

## 平台转发机制

hub 型集成通过平台转发将设备能力暴露为标准化实体。核心方法是 `async_forward_entry_setups`（事实 #224）：

```python
from homeassistant.const import Platform

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
]

await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
```

核心依次导入每个平台模块（如 `my_integration/light.py`），调用其 `async_setup_entry` 函数，并传入 `async_add_entities` 回调。平台模块负责创建实体实例并通过回调注册：

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(MyLight(coordinator, device) for device in coordinator.devices)
```

Tuya 转发到 18 个平台（事实 #226），是支持平台最多的集成之一。MQTT 更支持 31 个平台（事实 #227），并使用自定义的 `async_forward_entry_setup_and_setup_discovery` 函数在转发的同时设置 MQTT discovery（事实 #228）。

卸载时使用对应的 `async_unload_platforms`（事实 #225），传入相同的 PLATFORMS 列表。

## 依赖解析

manifest 中的 `dependencies` 和 `after_dependencies` 字段控制集成加载顺序：

- **`dependencies`**：强依赖。这些集成必须在本集成之前成功加载，否则本集成加载失败。例如 websocket_api 依赖 `http`（事实 #290），assist_pipeline 依赖 `conversation`、`stt`、`tts`、`wake_word`（事实 #306）。
- **`after_dependencies`**：弱依赖/顺序提示。如果这些集成已配置，在本集成之前加载；但即使它们不存在或加载失败，本集成仍可加载。例如 mqtt 的 `after_dependencies` 包含 `hassio`（事实 #13）——如果 Hass.io 可用，MQTT 可以自动发现 addon，但不是必需的。

hassfest 的 dependencies 验证器使用 AST 解析（`ImportCollector` 类，事实 #122）静态分析每个集成的 Python 导入，检测三类问题（事实 #126）：
1. **未声明的依赖**：代码中导入了其他集成，但 manifest 未声明
2. **重复依赖**：同时出现在 `dependencies` 和 `after_dependencies` 中
3. **循环依赖**：A 依赖 B，B 又依赖 A

`ImportCollector` 忽略 `TYPE_CHECKING` 块中的导入（事实 #123），因为类型注解导入不构成运行时依赖。验证器使用 `multiprocessing.Pool` 并行解析数千个 Python 文件（事实 #125），是 hassfest 中计算量最大的插件之一。

`CORE_INTEGRATIONS = {"homeassistant", "persistent_notification"}` 不能被其他集成声明为依赖（事实 #128）——它们始终可用，无需声明。

`default_config` 集成通过 `dependencies` 一次性拉取 20 个核心集成（事实 #25），包括 bluetooth、cloud、conversation、dhcp、energy、history、mobile_app、stream、sun、zeroconf 等。它本身的 `async_setup` 直接返回 `True`（事实 #343），仅作为依赖聚合器。

## runtime_data：类型安全的运行时存储

`ConfigEntry.runtime_data` 是存储集成运行时对象（API 客户端、协调器、设备管理器）的标准位置。现代 HA 推荐定义类型化的 ConfigEntry 别名：

```python
type MyConfigEntry = ConfigEntry[MyCoordinator]
```

这使得 `entry.runtime_data` 在类型检查器中被推断为 `MyCoordinator`，避免 `Any` 类型。Tuya 定义了 `TuyaConfigEntry`（事实 #201），Anthropic 定义了 `AnthropicConfigEntry`（事实 #211）。hassfest 的 `runtime_data` 验证器会检查集成是否正确使用了 `runtime_data`（事实 #81）。

## 最佳实践

1. **优先使用 ConfigFlow**：现代集成应使用 `cv.config_entry_only_config_schema(DOMAIN)` 而非 YAML 配置。ConfigFlow 提供更好的用户体验，支持发现、OAuth、重新认证。
2. **使用 DataUpdateCoordinator**：对于轮询型集成，使用 `DataUpdateCoordinator` 管理数据获取，避免每个实体独立轮询。
3. **在 executor 中执行阻塞调用**：底层 SDK 如果是同步的，使用 `hass.async_add_executor_job()` 包装，绝不在事件循环中阻塞。
4. **声明稳定的 unique_id**：每个 ConfigEntry 和实体都应有稳定的唯一 ID，使用设备序列号、MAC 地址或 UUID。
5. **正确处理卸载**：使用 `entry.async_on_unload()` 注册清理回调，确保连接、订阅、定时器都被正确释放。
6. **requirements 版本锁定**：所有 Python 依赖必须锁定精确版本（`package==x.y.z`），hassfest 会验证格式。
7. **codeowners 必须以 @ 开头**：hassfest 验证每个 codeowner 以 `@` 开头（事实 #119），SILVER 及以上等级必须有 codeowners（事实 #72）。

## 延伸阅读

- [配置流](/concepts/15-config-flow.md)
- [平台开发模式](/concepts/16-platform-pattern.md)
- [hassfest 工具链](/concepts/17-hassfest-tooling.md)
- [测试模式](/concepts/18-testing-patterns.md)
- [三层架构](/concepts/01-architecture.md)
- [实体模型](/concepts/09-entity-model.md)

## 相关概念

- [三层架构：核心-集成-平台](/concepts/01-architecture.md) — 集成层在三层架构中的定位与平台转发机制
- [配置流](/concepts/15-config-flow.md) — ConfigFlow 为集成提供 GUI 配置向导，生成 ConfigEntry
- [平台开发模式](/concepts/16-platform-pattern.md) — 集成通过 platform 模块创建各领域 Entity 子类
- [实体模型](/concepts/09-entity-model.md) — 集成的 async_setup_entry 创建 Entity 并注册到平台
