---
type: Concept
title: 配置系统
description: 掌握 Home Assistant 配置系统，包括 configuration.yaml 结构、Config 类、核心配置项、secrets 管理和 YAML 验证
tags: [home-assistant, smart-home, configuration, yaml, config, beginner]
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

# 配置系统

## 配置系统概述

Home Assistant 支持两种配置方式：**YAML 配置文件**和 **ConfigFlow GUI 配置**。两者可以共存，分别适用于不同场景：

- **YAML** 适合声明式的、可版本管理的配置（如自动化、脚本、自定义），通过 `configuration.yaml` 管理
- **ConfigFlow** 适合设备连接配置（如 OAuth 认证、设备发现），通过 Web UI 引导用户完成，数据存储在 `.storage/` 目录的 JSON 文件中

核心配置（位置、时区、单位等）可以通过两种方式设置，最终统一由 `Config` 对象（`core_config.py:534`）管理。

## configuration.yaml

### 文件位置

主配置文件为 `configuration.yaml`（常量 `YAML_CONFIG_FILE`，定义于 `config.py:39`），位于配置目录的根目录。默认配置目录：

- Linux: `~/.homeassistant/`
- Docker: `/config/`
- HA OS: `/config/`
- 开发模式: 可通过 `-c` 参数指定

如果文件不存在，HA 首次启动时从 `DEFAULT_CONFIG` 模板自动创建。

### 基本结构

`configuration.yaml` 是一个 YAML 字典，顶层键为集成 domain 或核心配置键：

```yaml
# 核心配置
homeassistant:
  name: 我的家
  latitude: 39.9042
  longitude: 116.4074
  elevation: 43
  unit_system: metric
  time_zone: Asia/Shanghai
  language: zh-Hans
  country: CN

# 集成配置
light:
  - platform: hue
    host: 192.168.1.100
    token: YOUR_TOKEN

sensor:
  - platform: systemmonitor
    resources:
      - type: processor_use
      - type: memory_use_percent

# 自动化（引用外部文件）
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# 自定义集成
customize: !include customize.yaml
```

### DEFAULT_CONFIG 模板

`DEFAULT_CONFIG`（定义于 `config.py:52`）是首次创建配置文件时的模板：

```python
DEFAULT_CONFIG = {
    "homeassistant": {},
    "frontend": {},
    "http": {},
    "history": {},
    "logbook": {},
    "mobile_app": {},
    "person": {},
    "ssdp": {},
    "sun": {},
    "updater": {},
    "zeroconf": {},
}
```

这确保了 HA 首次启动时包含基本功能（前端、历史、发现等）。

## Config 类

`Config` 类定义于 `homeassistant/core_config.py:534`，是核心配置的运行时对象。它在 `HomeAssistant.__init__` 中创建，通过 `hass.config` 访问。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `config_dir` | `str` | 配置目录的绝对路径 |
| `data_dir` | `str` | 数据目录（默认为 `<config_dir>/.storage`） |
| `latitude` | `float` | 纬度（-90 到 90） |
| `longitude` | `float` | 经度（-180 到 180） |
| `elevation` | `int` | 海拔（米） |
| `time_zone` | `str` | 时区（IANA 名称，如 `Asia/Shanghai`） |
| `units` | `UnitSystem` | 单位系统（公制/英制） |
| `location_name` | `str` | 位置名称（默认为 `"Home"`） |
| `language` | `str` | 界面语言（如 `zh-Hans`、`en`） |
| `country` | `str` | 国家代码（ISO 3166-1 alpha-2，如 `CN`） |
| `currency` | `str` | 货币代码（ISO 4217，如 `CNY`） |
| `whitelist_external_dirs` | `set[str]` | 允许访问的外部目录白名单 |
| `allowlist_external_dirs` | `set[str]` | 同上（新名称） |
| `allowlist_external_urls` | `set[str]` | 允许访问的外部 URL 白名单 |
| `components` | `_ComponentSet` | 已加载的集成集合（通过 `hass.config.components` 访问） |
| `version` | `str` | HA 版本号 |

### 配置来源

`ConfigSource` 枚举标记每个配置项的来源：

| 来源 | 说明 |
|------|------|
| `DEFAULT` | 默认值 |
| `STORAGE` | 从 `.storage/` 加载（通过 ConfigFlow 设置） |
| `YAML` | 从 `configuration.yaml` 加载 |
| `DISCOVERED` | 通过设备发现自动设置 |

YAML 配置优先于存储配置，存储配置优先于默认值。核心配置变更时触发 `EVENT_CORE_CONFIG_UPDATE` 事件。

### 更新配置

核心配置可以通过服务 `homeassistant.set_location`、`homeassistant.set_core_config` 或 WebSocket API 更新：

```python
# 通过代码更新
await hass.config.async_update(
    location_name="我的家",
    latitude=39.9042,
    longitude=116.4074,
    time_zone="Asia/Shanghai",
)
```

配置更新后自动持久化到 `.storage/core.config` 文件。

## 核心配置项

### homeassistant 键

`homeassistant:` 是 HA 自身的配置块：

```yaml
homeassistant:
  name: 我的家                    # 位置名称
  latitude: 39.9042               # 纬度
  longitude: 116.4074             # 经度
  elevation: 43                   # 海拔（米）
  unit_system: metric             # metric 或 us_customary
  time_zone: Asia/Shanghai        # IANA 时区
  language: zh-Hans               # 界面语言
  country: CN                     # 国家代码
  currency: CNY                   # 货币代码
  external_url: https://ha.example.com  # 外部访问 URL
  internal_url: http://192.168.1.10:8123  # 内部访问 URL
  allowlist_external_dirs:        # 允许访问的目录
    - /config/www
  allowlist_external_urls:        # 允许访问的 URL
    - https://api.example.com
  media_dirs:                     # 媒体目录映射
    local: /media
    music: /mnt/music
```

### 单位系统

`unit_system` 影响温度、距离、压力、风速等单位的显示：

| 单位系统 | 温度 | 距离 | 压力 | 风速 | 体积 |
|---------|------|------|------|------|------|
| `metric` | 摄氏度 | 千米 | 毫巴 | 米/秒 | 升 |
| `us_customary` | 华氏度 | 英里 | 英寸汞柱 | 英里/小时 | 加仑 |

### 时区

时区使用 IANA 时区数据库名称，如 `Asia/Shanghai`、`America/New_York`、`Europe/London`。可通过以下方式查看可用时区：

```python
from homeassistant.util.dt import get_time_zone
tz = get_time_zone("Asia/Shanghai")
```

时区影响太阳事件计算、时间触发器和时间戳显示。

## secrets 管理

### secrets.yaml

敏感信息（密码、API key、token）不应直接写入 `configuration.yaml`，而应使用 `!secret` 引用：

```yaml
# configuration.yaml
light:
  - platform: hue
    host: 192.168.1.100
    token: !secret hue_token
```

```yaml
# secrets.yaml（不纳入版本控制）
hue_token: "your-long-token-string"
```

`!secret` 由 `homeassistant/util/yaml/` 中的 `Secrets` 类处理。加载 YAML 时，`Secrets` 实例从 `secrets.yaml` 读取键值对，遇到 `!secret key` 时替换为对应值。

### 多环境 secrets

HA 会依次搜索以下位置加载 secrets：
1. 配置目录下的 `secrets.yaml`
2. 配置目录的父目录（允许在同一主目录下管理多个 HA 实例）
3. 更深的父目录（直到文件系统根目录）

这种设计允许将共享的 secrets 放在上层目录，特定实例的 secrets 放在配置目录中。

## YAML 高级特性

### !include 指令

HA 支持多种 `!include` 指令将配置拆分到多个文件：

```yaml
# 包含单个文件
automation: !include automations.yaml

# 包含目录下所有文件（合并为列表）
automation manual: !include_dir_merge_list automations/

# 包含目录下所有文件（合并为字典）
sensor: !include_dir_merge_named sensors/

# 包含目录下每个文件作为列表项
sensor: !include_dir_list sensors/

# 包含目录下每个文件作为字典项
sensor: !include_dir_named sensors/
```

`!include` 指令由 `homeassistant/util/yaml/` 加载器实现，路径相对于配置目录。

### YAML 加载流程

1. `load_yaml(path)` 读取文件（`util/yaml/__init__.py`）
2. 使用 PyYAML 解析，自定义 `!secret`、`!include` 等构造器
3. 返回 Python 字典/列表
4. 通过 voluptuous schema 验证配置结构
5. 验证失败抛出 `HomeAssistantError`，在前端显示错误

### YAML 类型安全

HA 使用 voluptuous 进行配置验证。每个集成定义自己的 `PLATFORM_SCHEMA` 或 `CONFIG_SCHEMA`：

```python
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_PORT, default=80): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})
```

`config_validation.py`（别名 `cv`）提供了丰富的验证器：`boolean`、`entity_id`、`template`、`positive_int`、`latitude`、`longitude`、`port`、`time_period_str` 等。

## ConfigFlow 配置

### 与 YAML 的区别

| 特性 | YAML | ConfigFlow |
|------|------|-----------|
| 配置方式 | 手动编辑文件 | Web UI 向导 |
| 数据存储 | `configuration.yaml` | `.storage/*.json` |
| 发现支持 | 无 | 自动发现设备 |
| OAuth 支持 | 手动填 token | 完整 OAuth 流程 |
| 重新配置 | 手动编辑 | UI 重新配置 |
| 版本迁移 | 无 | 内置版本迁移 |
| 输入验证 | voluptuous | voluptuous + UI 反馈 |

### ConfigEntry

ConfigFlow 完成后创建一个 `ConfigEntry` 对象（`config_entries.py`），包含：

```python
class ConfigEntry:
    entry_id: str              # 唯一 ID（ULID）
    domain: str                # 集成 domain
    title: str                 # 用户可见标题
    data: dict                 # 连接配置（host/token 等）
    options: dict              # 用户选项
    state: ConfigEntryState    # 当前状态
    source: str                # 配置来源（user/dhcp/zeroconf 等）
    unique_id: str | None      # 唯一标识，防止重复配置
    version: int               # 配置版本
    minor_version: int         # 次版本号
    runtime_data: Any          # 运行时数据（协调器等，不持久化）
```

### ConfigEntryState 状态机

`ConfigEntryState` 枚举定义了 8 种状态：

| 状态 | 说明 |
|------|------|
| `LOADED` | 已成功加载并运行 |
| `SETUP_ERROR` | 设置过程出错 |
| `MIGRATION_ERROR` | 配置版本迁移失败 |
| `SETUP_RETRY` | 设置未就绪，等待重试 |
| `NOT_LOADED` | 未加载（已卸载或尚未加载） |
| `FAILED_UNLOAD` | 卸载失败 |
| `REAUTH` | 需要重新认证 |
| `MIGRATING` | 正在进行版本迁移 |

### 配置存储

ConfigEntry 数据存储在 `.storage/core.config_entries` 文件中，由 `Store` 类（`helpers/storage.py`）管理。`Store` 提供：
- 延迟写入（合并短时间内的多次保存）
- 版本迁移（`async_migrate`）
- 原子写入（先写临时文件再重命名）
- 文件损坏保护（备份 `.corruption`）

## 配置重载

部分配置变更不需要重启 HA：

```python
# 重载核心配置
await hass.services.async_call("homeassistant", "reload_core_config")

# 重载 YAML 集成配置（如果集成支持）
await hass.services.async_call("light", "reload")

# 重载所有 YAML 配置
await hass.services.async_call("homeassistant", "reload_all_yaml")
```

在前端：**开发者工具 → YAML → 重载配置**。

注意：不是所有集成都支持热重载。ConfigEntry 配置的重载通过 `config_entries.async_reload(entry_id)` 实现。

## 配置目录文件

### 关键文件

| 文件 | 用途 |
|------|------|
| `configuration.yaml` | 主配置文件 |
| `secrets.yaml` | 敏感信息 |
| `automations.yaml` | 自动化（YAML 模式） |
| `scripts.yaml` | 脚本 |
| `scenes.yaml` | 场景 |
| `groups.yaml` | 分组 |
| `customize.yaml` | 实体属性自定义 |
| `known_devices.yaml` | 已知设备（旧版） |
| `home-assistant.log` | 日志文件 |
| `home-assistant_v2.db` | Recorder 数据库（SQLite） |

### .storage 目录

`.storage/` 目录包含 ConfigFlow 和核心服务的 JSON 存储文件：

| 文件 | 内容 |
|------|------|
| `core.config_entries` | 所有 ConfigEntry |
| `core.entity_registry` | 实体注册表 |
| `core.device_registry` | 设备注册表 |
| `core.area_registry` | 区域注册表 |
| `core.config` | 核心配置（位置/时区等） |
| `auth` | 用户和凭证 |
| `auth_module` | 认证模块数据 |
| `restore_state` | 实体状态恢复数据 |
| `frontend.*` | 前端主题和面板 |
| `websocket_api` | WebSocket 刷新令牌 |

> 警告：`.storage/` 目录中的文件由 HA 自动管理，不应手动编辑。手动编辑可能导致数据损坏。需要修改配置时应通过 Web UI 或服务调用。

## 延伸阅读

- [启动流程](/concepts/04-bootstrap-lifecycle.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [三层架构](/concepts/01-architecture.md)

## 相关概念

- [启动流程](/concepts/04-bootstrap-lifecycle.md) — 配置在 bootstrap Stage A 中的加载时机与初始化过程
- [配置流](/concepts/15-config-flow.md) — ConfigFlow GUI 配置向导与 ConfigEntry 持久化存储
- [注册表](/concepts/10-registries.md) — 存储在 .storage/ 目录的实体、设备、区域注册表
