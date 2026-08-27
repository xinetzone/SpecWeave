---
type: Concept
title: 启动流程
description: 详解 Home Assistant 的 bootstrap 启动阶段、组件加载顺序、依赖解析、Stage 0/1/2 分阶段加载机制
tags: [home-assistant, smart-home, bootstrap, lifecycle, startup, beginner]
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
---

# 启动流程

## 启动流程概览

Home Assistant 的启动是一个精心编排的多阶段过程。核心入口是 `bootstrap.py` 中的 `async_setup_hass()` 协程（`bootstrap.py:309`），它接收 `RuntimeConfig`，按照严格的顺序初始化各个子系统和集成。

理解启动流程有助于：
- 排查启动失败和慢启动问题
- 理解集成间依赖关系
- 正确编写集成的初始化代码
- 理解 ConfigEntry 和 YAML 配置的加载时机

## 完整启动链路

```text
runner.py: run()
  │
  ├─ 1. ensure_single_execution()        # 文件锁
  ├─ 2. HassEventLoopPolicy              # 事件循环策略
  ├─ 3. setup_and_run_hass()             # 进入异步
  │
  └─ bootstrap.py: async_setup_hass()
       │
       ├─ Stage A: 环境准备
       │   ├─ 检查 Python 版本
       │   ├─ 加载 config 目录
       │   ├─ 配置日志
       │   └─ 创建 HomeAssistant 实例
       │
       ├─ Stage 0: 核心基础设施
       │   ├─ 加载 auth, http, api, websocket_api
       │   └─ 加载 recorder, cloud 等
       │
       ├─ Stage 1: 基础服务
       │   ├─ 加载 frontend
       │   ├─ 加载发现服务（zeroconf/dhcp/ssdp）
       │   └─ 加载 system_health, logbook 等
       │
       ├─ Stage 2: 用户集成
       │   ├─ 加载 YAML 配置的集成
       │   └─ 加载所有 ConfigEntry
       │
       └─ 启动完成
           ├─ hass.async_start()
           ├─ EVENT_HOMEASSISTANT_STARTED
           └─ 运行事件循环
```

## Stage A：环境准备

在进入分阶段集成加载之前，`async_setup_hass()` 完成以下准备工作：

### 1. Python 版本检查

```python
if sys.version_info[:3] < REQUIRED_PYTHON_VER:
    raise HomeAssistantError(
        f"Home Assistant requires at least Python {'.'.join(map(str, REQUIRED_PYTHON_VER))}"
    )
```

HA 要求 Python 3.14.2+。版本不满足时直接拒绝启动。

### 2. 配置目录初始化

- 验证配置目录存在且可写
- 如果 `configuration.yaml` 不存在，从 `DEFAULT_CONFIG` 模板创建
- 设置 `hass.config.config_dir`
- 初始化 `secrets.yaml` 加载器

### 3. 日志配置

根据 `RuntimeConfig` 配置日志系统：
- 设置日志级别（`--verbose` → DEBUG）
- 配置日志文件和轮转（`--log-file`、`--log-rotate-days`）
- 配置日志格式和颜色
- 集成通过 `manifest.json` 的 `loggers` 字段注册自己的 logger 名称

### 4. 创建 HomeAssistant 实例

```python
hass = HomeAssistant(runtime_config.config_dir)
```

此时 `hass.state` 为 `CoreState.NOT_RUNNING`。四大子系统（EventBus、StateMachine、ServiceRegistry、Config）已就绪，但尚未加载任何集成。

### 5. AuthManager 初始化

通过 `auth_manager_from_config()` 创建 `AuthManager`，加载用户数据和刷新令牌。AuthStore 使用延迟加载，首次访问时从磁盘读取。

## Stage 0：核心基础设施

Stage 0 加载 HA 运行所必需的核心集成。这些集成必须最先就绪，因为后续所有集成都可能依赖它们。

### STAGE_0_INTEGRATIONS

`STAGE_0_INTEGRATIONS`（`bootstrap.py:183`）是一个有序元组，定义了 Stage 0 的集成加载顺序。关键集成包括：

| 集成 | 说明 |
|------|------|
| `homeassistant` | HA 自身，注册核心服务（重启、停止、重载配置） |
| `auth` | 认证系统（已通过 AuthManager 初始化） |
| `http` | HTTP 服务器（aiohttp），API 和前端的基础 |
| `api` | REST API |
| `websocket_api` | WebSocket API |
| `recorder` | 历史记录数据库 |
| `cloud` | Nabu Casa 云服务 |
| `ffmpeg` | FFmpeg 工具（摄像头/媒体依赖） |
| `logger` | 日志管理服务 |

### 加载机制

Stage 0 的集成按顺序加载，每个子阶段有 60 秒超时（`STAGE_0_SUBSTAGE_TIMEOUT = 60`，`bootstrap.py:145`）。

部分集成通过 `async_load_base_functionality()`（`bootstrap.py:484`）并行加载，这些是注册表和基础服务：

- `entity_registry`：实体注册表
- `device_registry`：设备注册表
- `area_registry`：区域注册表
- `floor_registry`：楼层注册表
- `category_registry`：分类注册表
- `config_entries`：配置条目管理器
- `trace`：执行追踪
- `restore_state`：状态恢复

注册表数据从 `.storage/` 目录加载，是后续集成创建设备和实体的前提。

## Stage 1：基础服务

Stage 1 加载用户界面和发现服务。这些不是核心运行所必需的，但通常需要在用户集成之前就绪。

### STAGE_1_INTEGRATIONS

`STAGE_1_INTEGRATIONS`（`bootstrap.py:200`）包括：

| 集成 | 说明 |
|------|------|
| `frontend` | Web UI（关键集成，失败则进入恢复模式） |
| `zeroconf` | mDNS/DNS-SD 设备发现 |
| `dhcp` | DHCP 设备发现 |
| `ssdp` | SSDP/UPnP 设备发现 |
| `usb` | USB 设备发现 |
| `bluetooth` | 蓝牙设备发现 |
| `system_health` | 系统健康信息 |
| `logbook` | 日志记录器 |
| `stream` | 视频流服务 |
| `sun` | 太阳位置计算 |
| `sensor` | 传感器平台基础设施 |

Stage 1 的超时为 120 秒（`STAGE_1_TIMEOUT = 120`，`bootstrap.py:146`）。

### frontend 的关键地位

`frontend` 被标记为 `CRITICAL_INTEGRATIONS = {"frontend"}`（`bootstrap.py:280`）。如果它加载失败，HA 自动进入恢复模式，因为没有前端用户无法通过 UI 修复问题。恢复模式仍然加载核心功能，允许用户通过 API 或直接编辑配置文件进行修复。

### 发现服务

发现服务（zeroconf/dhcp/ssdp/usb/bluetooth）在 Stage 1 启动后，会在 Stage 2 用户集成加载期间持续监听网络。当发现新设备时，它们发布发现事件，触发对应集成的 ConfigFlow。

发现规则由 `hassfest` 从各集成的 `manifest.json` 收集，生成到 `homeassistant/generated/` 目录：
- `generated/zeroconf.py`
- `generated/dhcp.py`
- `generated/ssdp.py`
- `generated/usb.py`
- `generated/bluetooth.py`

## Stage 2：用户集成

Stage 2 加载用户实际配置的所有集成。这是启动过程中最耗时的阶段，超时为 300 秒（`STAGE_2_TIMEOUT = 300`，`bootstrap.py:147`）。

Stage 2 的加载由 `_async_set_up_integrations()`（`bootstrap.py:907`）协调。

### 集成来源

Stage 2 加载的集成来自三个来源：

1. **YAML 配置**：`configuration.yaml` 中声明的集成（如 `switch:`、`light:`）
2. **ConfigEntry**：通过 ConfigFlow 创建的配置条目（存储在 `.storage/core.config_entries`）
3. **依赖传递**：其他集成的 `dependencies` 和 `after_dependencies` 声明

### DEFAULT_INTEGRATIONS

`DEFAULT_INTEGRATIONS`（`bootstrap.py:215`）是一组始终加载的默认集成，包括：
- `onboarding`（首次启动向导）
- `lovelace`（仪表盘）
- `mobile_app`（移动端 App 支持）
- `persistent_notification`（持久通知）
- `diagnostics`（诊断信息下载）
- `analytics`（使用分析）
- 其他核心服务

如果配置中包含 `default_config:`，还会额外加载 21 个核心集成（energy、history、cloud、conversation 等）。

### 依赖解析

`_async_set_up_integrations()` 使用 `async_setup_component()`（`setup.py:148`）加载集成，该函数处理依赖关系：

1. 检查集成是否已加载（在 `hass.config.components` 中）
2. 解析 `dependencies`（硬依赖）：递归加载，必须在本集成之前完成
3. 解析 `after_dependencies`（软依赖）：如果已配置则先加载，但不强制要求
4. 调用集成的 `async_setup(hass, config)` 或 `async_setup_entry(hass, entry)`
5. 等待设置完成或超时

```text
集成 A (dependencies=[B, C])
    │
    ├─ 递归加载 B ─→ B 的 dependencies...
    ├─ 递归加载 C ─→ C 的 dependencies...
    │
    └─ B、C 都完成后，加载 A
```

### 并行加载

无依赖关系的集成通过 `asyncio.gather` 并行加载，加快启动速度。但同一集成的设置是串行的（通过 `async_setup_component_locks` 防止重复加载）。

### ConfigEntry 加载顺序

ConfigEntry 按以下逻辑排序：
1. 按 `domain` 的字母顺序
2. 同一 domain 内按创建时间

每个 ConfigEntry 调用其集成的 `async_setup_entry()`。如果返回 `ConfigEntryNotReady`，触发指数退避重试（最大等待 600 秒，`SETUP_RETRY_MAX_WAIT`）。如果返回 `ConfigEntryAuthFailed`，触发重新认证流程。

### 慢设置警告

组件设置超过 10 秒（`SLOW_SETUP_WARNING = 10`，`setup.py:84`）时记录警告日志，超过 300 秒（`SLOW_SETUP_MAX_WAIT = 300`，`setup.py:85`）时强制超时。

## 启动完成

所有 Stage 2 集成加载完成后：

### 1. hass.async_start()

```python
await hass.async_start()
```

这将状态转为 `CoreState.RUNNING`，触发：
- `EVENT_HOMEASSISTANT_START`（`"homeassistant_start"`）
- `EVENT_HOMEASSISTANT_STARTED`（`"homeassistant_started"`）

### 2. 启动事件

集成可以监听启动事件执行延迟初始化：

```python
from homeassistant.core import HomeAssistant, callback

async def async_setup(hass: HomeAssistant, config):
    @callback
    def on_started(event):
        """HA 完全启动后执行。"""
        hass.async_create_task(background_refresh())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, on_started)
    return True
```

### 3. started Future

`hass.started` 是一个 `asyncio.Future`，在启动完成后 resolve。集成可以 `await hass.started` 等待 HA 完全就绪。

## 组件设置的内部机制

### async_setup_component

`async_setup_component()`（`setup.py:148`）是公共设置入口，内部调用 `_async_setup_component()`（`setup.py:280`）。设置过程经历多个阶段（`SetupPhases` 枚举，`setup.py:665`）：

| 阶段 | 说明 |
|------|------|
| `LOADING` | 正在加载集成的 Python 模块 |
| `PREPARE` | 准备依赖（requirements 安装等） |
| `SETUP` | 调用 `async_setup` / `async_setup_entry` |
| `SETUP_DONE` | 设置完成 |
| `WAIT_SETUP` | 等待设置完成 |
| `WAIT_IMPORT` | 等待模块导入 |

### 平台转发

当集成调用 `async_forward_entry_setups(entry, PLATFORMS)` 时：

1. 为每个 platform 创建 `EntityPlatform`
2. 调用集成的 `<platform>.py` 中的 `async_setup_entry()`
3. 该函数创建实体并通过 `EntityPlatform.async_add_entities()` 注册
4. `EntityPlatform` 将实体批量添加到 `EntityComponent`
5. 实体状态写入 `StateMachine`

### 设置完成回调

集成可以通过 `async_when_setup()`（`setup.py:591`）注册其他集成设置完成的回调：

```python
from homeassistant.setup import async_when_setup

async def async_setup(hass, config):
    async def mqtt_setup(hass, component):
        """MQTT 加载完成后执行。"""
        await subscribe_to_topics(hass)

    async_when_setup(hass, "mqtt", mqtt_setup)
    return True
```

## 恢复模式与安全模式

### 恢复模式（Recovery Mode）

触发条件：
- `frontend` 集成加载失败
- 使用 `--recovery-mode` 命令行参数启动

恢复模式下：
- 仅加载 Stage 0 核心基础设施和 frontend
- 不加载用户配置的集成
- 前端显示恢复界面，允许用户修复问题

### 安全模式（Safe Mode）

触发条件：
- 使用 `--safe-mode` 命令行参数启动

安全模式下：
- 加载所有核心集成
- 不加载 `custom_components/` 中的自定义集成
- 用于排查第三方集成导致的启动问题

## 启动日志分析

典型的启动日志关键字：

```log
INFO homeassistant.bootstrap: Setting up homeassistant
INFO homeassistant.bootstrap: Setting up auth
INFO homeassistant.bootstrap: Setting up http
INFO homeassistant.setup: Setting up component mqtt
INFO homeassistant.setup: Setup of domain mqtt took 1.2 seconds
WARNING homeassistant.setup: Setup of slow_integration is taking over 10 seconds
ERROR homeassistant.setup: Error setting up integration my_integration
INFO homeassistant.bootstrap: Home Assistant initialized in 12.3 seconds
INFO homeassistant.core: Starting Home Assistant
```

通过日志中的 `Setting up` 和 `Setup of domain ... took ... seconds` 可以追踪每个集成的加载耗时。

## 延伸阅读

- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [配置系统](/concepts/05-configuration.md)
- [事件总线](/concepts/06-event-bus.md)
- [安装与启动](/concepts/02-installation-runner.md)

## 相关概念

- [HomeAssistant 核心对象](/concepts/03-core-object.md) — 启动过程中创建的根对象及其 CoreState 状态机
- [配置系统](/concepts/05-configuration.md) — Stage A 加载的 configuration.yaml 与 Config 对象
- [集成架构](/concepts/14-component-architecture.md) — Stage 2 加载的集成依赖解析、平台转发与生命周期函数
