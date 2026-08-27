---
type: Concept
title: 配置流
description: 掌握 ConfigFlow 状态机模型、多步表单实现、async_step_user/discovery/reauth 步骤、OptionsFlow 选项配置、async_migrate_entry 版本迁移与 ConfigSubentry 子条目机制
tags: [home-assistant, smart-home, config-flow, config-entry, options-flow, data-entry-flow, oauth, migration]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 源码
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: facts-components
    resource: "/references/facts-components.md"
    title: Home Assistant Components 事实清单
---

# 配置流

ConfigFlow 是 Home Assistant 的现代配置框架，将集成配置过程建模为多步状态机。用户通过 Web UI 分步填写表单、完成 OAuth 授权、确认设备发现，最终创建持久化的 `ConfigEntry`。与传统 YAML 配置相比，ConfigFlow 支持输入验证、动态选项、设备自动发现、重新认证和在线迁移，是现代 HA 集成的标准配置方式。

## 状态机模型

ConfigFlow 构建在 `data_entry_flow` 模块之上，核心是 `FlowResultType` 枚举（data_entry_flow.py:27-37），定义了 8 种步骤结果类型：

| 结果类型 | 值 | 含义 |
|----------|-----|------|
| `FORM` | `"form"` | 显示表单给用户填写，流程未完成 |
| `CREATE_ENTRY` | `"create_entry"` | 配置完成，创建 ConfigEntry |
| `ABORT` | `"abort"` | 流程中止（已配置、不支持等） |
| `EXTERNAL_STEP` | `"external"` | 跳转到外部步骤（如 OAuth 授权页） |
| `EXTERNAL_STEP_DONE` | `"external_done"` | 外部步骤完成，返回流程 |
| `SHOW_PROGRESS` | `"progress"` | 显示进度（等待设备/后台任务） |
| `SHOW_PROGRESS_DONE` | `"progress_done"` | 进度任务完成 |
| `MENU` | `"menu"` | 显示选择菜单 |

`FLOW_NOT_COMPLETE_STEPS` 集合包含 FORM、EXTERNAL_STEP、EXTERNAL_STEP_DONE、SHOW_PROGRESS、SHOW_PROGRESS_DONE、MENU 六种未完成状态（data_entry_flow.py:44-51）。只有 CREATE_ENTRY 和 ABORT 终止流程。

每个 ConfigFlow 步骤是一个 `async_step_<name>` 异步方法，接收用户输入（首次调用时为 `None`），返回上述结果类型之一的字典。`FlowManager`（data_entry_flow.py:174）管理流程的生命周期——创建、推进、中止。`AbortFlow` 异常（data_entry_flow.py:106）用于在步骤内部中止流程并携带原因码。

## ConfigFlow 基类

`ConfigFlow` 继承自 `ConfigEntryBaseFlow`（config_entries.py:3013），通过 `domain` 关键字参数自动注册到 `HANDLERS` 注册表：

```python
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

class MyConfigFlow(ConfigFlow, domain="my_integration"):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("host"): str}),
        )
```

`VERSION` 类属性定义配置条目的数据结构版本，用于后续迁移。当 `__init_subclass__` 检测到 `domain` 参数时，自动将类注册到 HANDLERS（config_entries.py:3017-3021），使核心能按 domain 找到对应的 ConfigFlow 类。

### 核心辅助方法

ConfigFlow 提供了多个 `@callback` 修饰的辅助方法用于构造结果：

- `async_show_form(step_id, data_schema, errors, description_placeholders, last_step)`：返回 FORM 结果
- `async_create_entry(title, data)`：返回 CREATE_ENTRY 结果，创建 ConfigEntry
- `async_abort(reason, description_placeholders)`：抛出 AbortFlow 中止流程
- `async_show_progress(progress_action, description_placeholders)`：显示进度
- `async_external_step(url, description_placeholders)`：跳转到外部 URL
- `async_external_step_done(next_step_id)`：外部步骤完成
- `async_show_menu(menu_options, description_placeholders)`：显示选择菜单

### unique_id 与去重

ConfigFlow 的 `unique_id` 属性（config_entries.py:3024-3029）从 `context["unique_id"]` 读取。设备发现流程应设置 unique_id 以实现去重：

```python
async def async_step_zeroconf(self, discovery_info):
    await self.async_set_unique_id(discovery_info.properties["id"])
    self._abort_if_unique_id_configured()
    return await self.async_step_user()
```

`_abort_if_unique_id_configured`（config_entries.py:3116）检查 unique_id 是否已被其他 ConfigEntry 使用，若是则中止流程（reason 为 `"already_configured"`）。可选的 `updates` 参数在已配置时更新现有条目的数据，`reload_on_update` 控制是否自动重载。

`_abort_if_unique_id_mismatch`（config_entries.py:3095）用于重新认证/重新配置场景，确保 unique_id 与原条目匹配，防止用户对错误的设备重新认证。

hassfest 的 config_flow 验证器检查所有可发现配置流（含 `async_step_discovery`/`bluetooth`/`hassio`/`homekit`/`mqtt`/`ssdp`/`zeroconf`/`dhcp`/`usb` 方法）是否设置了 unique_id（事实 #93），少数豁免集成列在 `UNIQUE_ID_IGNORE` 集合中（事实 #94）。

## 步骤类型

### async_step_user：用户发起

`async_step_user` 是用户手动添加集成时的入口步骤。典型实现（以 Tuya 为参考，config_flow.py:38-72）：

```python
async def async_step_user(self, user_input=None):
    errors = {}
    if user_input is not None:
        try:
            info = await self._validate_input(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

    return self.async_show_form(
        step_id="user",
        data_schema=vol.Schema({
            vol.Required("host", default=user_input.get("host", "")): str,
            vol.Required("api_key"): str,
        }),
        errors=errors,
    )
```

首次调用 `user_input` 为 `None`，显示空表单；用户提交后 `user_input` 包含表单数据，验证成功则创建条目，失败则重新显示表单并附带 `errors` 字典。错误键 `"base"` 对应表单级错误，字段名对应字段级错误，错误消息在 `strings.json` 中定义。

### 发现步骤

当 manifest 声明了 zeroconf/dhcp/ssdp/usb/bluetooth 发现规则时，HA 自动检测到设备并启动对应的发现步骤。常见发现方法包括：

- `async_step_zeroconf`：mDNS 发现
- `async_step_dhcp`：DHCP 发现
- `async_step_ssdp`：SSDP/UPnP 发现
- `async_step_usb`：USB 设备发现
- `async_step_bluetooth`：蓝牙发现
- `async_step_homekit`：HomeKit 发现
- `async_step_hassio`：Hass.io addon 发现
- `async_step_mqtt`：MQTT 发现

发现方法接收一个 `discovery_info` 对象，包含设备的服务信息。发现步骤通常设置 unique_id、确认设备类型，然后委托给 `async_step_user` 或显示确认表单。

### async_step_reauth：重新认证

当集成在运行中检测到认证失败（如 API token 过期）时，抛出 `ConfigEntryAuthFailed` 触发重新认证流程。HA 自动启动 source 为 `SOURCE_REAUTH = "reauth"`（config_entries.py:126）的 ConfigFlow：

```python
async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
    """Handle reauth."""
    return await self.async_step_reauth_confirm()

async def async_step_reauth_confirm(self, user_input=None):
    if user_input is not None:
        return self.async_update_reload_and_abort(
            self._get_reauth_entry(),
            data={**current_data, "password": user_input["password"]},
        )
    return self.async_show_form(
        step_id="reauth_confirm",
        data_schema=vol.Schema({vol.Required("password"): str}),
    )
```

`_get_reauth_entry()` 返回触发重新认证的 ConfigEntry。`async_update_reload_and_abort` 更新条目数据并重载，然后中止流程。`_abort_if_unique_id_mismatch` 确保重新认证的设备与原条目一致。

### async_step_reconfigure：重新配置

`SOURCE_RECONFIGURE = "reconfigure"`（config_entries.py:129）允许用户修改已有配置条目（不同于选项，reconfigure 修改的是 `data` 而非 `options`）。适用于需要变更服务器地址、设备 ID 等核心配置的场景。`_get_reconfigure_entry()` 返回当前重新配置的条目。

## OptionsFlow：选项配置

OptionsFlow 允许用户在集成设置后修改非核心选项，存储在 `ConfigEntry.options` 中而非 `data` 中。ConfigFlow 通过 `async_get_options_flow` 静态方法返回 OptionsFlow 实例（config_entries.py:3031-3035）：

```python
from homeassistant.config_entries import ConfigFlow, OptionsFlow

class MyConfigFlow(ConfigFlow, domain="my_integration"):
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MyOptionsFlow(config_entry)

class MyOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("scan_interval", default=30): int,
            }),
        )
```

`OptionsFlow` 继承自 `ConfigEntryBaseFlow`（config_entries.py:3962），与 ConfigFlow 共享相同的表单/中止/创建条目机制。`async_supports_options_flow` 类方法（config_entries.py:3038）检查 ConfigFlow 是否重写了 `async_get_options_flow`。

`OptionsFlowWithConfigEntry`（config_entries.py:4012）是旧基类，自动维护 `config_entry` 和 `options` 副本，但在核心集成中已被标记为弃用（`ReportBehavior.ERROR`），新代码应直接继承 `OptionsFlow`。`OptionsFlowWithReload`（config_entries.py:4036）在选项变更时自动重载 ConfigEntry。

选项变更后通常需要重载集成才能生效。Anthropic 的做法是注册 `entry.add_update_listener(async_update_options)`，在选项变更时调用 `hass.config_entries.async_reload(entry.entry_id)`（事实 #212-213）。

## ConfigSubentryFlow：子条目

ConfigSubentry 是较新的机制，允许一个 ConfigEntry 下管理多个子配置（如多个 API key、多个设备配置文件）。`ConfigSubentryFlow` 继承自 `FlowHandler`（config_entries.py:3723），handler 类型为 `tuple[str, str]`（domain, subentry_type）。

`async_create_entry` 在 ConfigSubentryFlow 中要求 source 必须是 `SOURCE_USER`（config_entries.py:3745-3746），并支持 `unique_id` 参数。`_async_update` 方法（config_entries.py:3760）更新子条目的 title/data/data_updates。

Anthropic 集成是 ConfigSubentry 的典型应用（事实 #223）：它使用子条目（`subentry_type="conversation"`）将多个 API key 条目合并为一个带子条目的父条目，每个子条目代表一个对话配置。`async_migrate_entry` 从版本 1 迁移到版本 2.3 时，通过 `ConfigSubentry` 将旧的独立条目重组为父子结构。

## 配置条目迁移

`async_migrate_entry(hass, entry)` 函数在 ConfigEntry 版本升级时调用，负责将旧格式数据迁移到新格式。版本号由 ConfigFlow 的 `VERSION` 和 `MINOR_VERSION` 控制。

### 迁移模式

每个迁移步骤检查当前版本并执行增量升级（以 Anthropic 为参考，__init__.py:177-243）：

```python
async def async_migrate_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Migrate config entry."""
    if entry.version == 1:
        # v1 → v2: 重构数据结构
        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            version=2,
            minor_version=1,
        )

    if entry.version == 2 and entry.minor_version == 1:
        # v2.1 → v2.2: 修复字段
        hass.config_entries.async_update_entry(entry, minor_version=2)

    if entry.version == 2 and entry.minor_version == 2:
        # v2.2 → v2.3: 清理废弃字段
        hass.config_entries.async_update_entry(entry, minor_version=3)

    return True
```

MQTT 的迁移（事实 #221）从版本 1.x 迁移到 2.1，涉及配置结构的重大变更。迁移函数返回 `True` 表示成功，返回 `False` 表示迁移失败（条目将进入 `MIGRATION_ERROR` 状态）。

### 迁移注意事项

- 迁移按版本号顺序执行，每个 if 块处理一个版本跨度
- 使用 `hass.config_entries.async_update_entry` 更新数据和版本号
- 迁移中可操作 DeviceRegistry 和 EntityRegistry（如 Anthropic 迁移实体和设备的 config_entry 关联）
- 禁用的条目不执行迁移（Anthropic 代码注释明确了这一限制）
- 迁移逻辑必须有测试覆盖

## 外部步骤与 OAuth

对于需要 OAuth2 授权的集成，ConfigFlow 使用 `EXTERNAL_STEP` 将用户重定向到授权服务器：

```python
async def async_step_user(self, user_input=None):
    if not self._oauth_data:
        return self.async_external_step(
            step_id="user",
            url=authorization_url,
        )
    # OAuth 回调后继续
    return self.async_create_entry(title="My Service", data=self._oauth_data)
```

`async_external_step` 返回 EXTERNAL_STEP 结果，前端打开外部 URL。授权完成后，外部服务重定向回 HA 的回调 URL，HA 推进流程到同名步骤（此时用户输入包含回调数据）。MQTT ConfigFlow 支持 TLS 证书配置，导入 `cryptography` 库处理 PEM/DER 格式私钥和证书（事实 #217），并支持 Hass.io addon 发现。

## 配置来源常量

ConfigEntry 的 `source` 字段标识配置创建方式（facts-core 中定义）：

| 常量 | 值 | 说明 |
|------|-----|------|
| `SOURCE_USER` | `"user"` | 用户手动添加 |
| `SOURCE_ZEROCONF` | `"zeroconf"` | mDNS 发现 |
| `SOURCE_DHCP` | `"dhcp"` | DHCP 发现 |
| `SOURCE_SSDP` | `"ssdp"` | SSDP 发现 |
| `SOURCE_USB` | `"usb"` | USB 发现 |
| `SOURCE_BLUETOOTH` | `"bluetooth"` | 蓝牙发现 |
| `SOURCE_HOMEKIT` | `"homekit"` | HomeKit 发现 |
| `SOURCE_HASSIO` | `"hassio"` | Hass.io addon |
| `SOURCE_MQTT` | `"mqtt"` | MQTT 发现 |
| `SOURCE_DISCOVERY` | `"discovery"` | 通用发现 |
| `SOURCE_REAUTH` | `"reauth"` | 重新认证 |
| `SOURCE_RECONFIGURE` | `"reconfigure"` | 重新配置 |
| `SOURCE_IGNORE` | `"ignore"` | 被忽略的发现 |

`DISCOVERY_SOURCES` 集合包含所有发现类来源。核心在 `async_init` 中检查同一来源的活跃流程，避免重复创建（config_entries.py:1504-1505）。

## 翻译与 strings.json

ConfigFlow 中所有用户可见的字符串（步骤标题、描述、错误消息、中止原因、字段标签）都通过 `strings.json`（核心集成）或 `translations/<lang>.json`（自定义集成）定义。hassfest 的 translations 验证器检查翻译键格式（事实 #102）——只允许小写字母数字、连字符、下划线，不允许前后连字符/下划线或连续双连字符。

典型的 strings.json 结构：

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to device",
        "description": "Enter connection details",
        "data": { "host": "Host", "api_key": "API Key" }
      }
    },
    "error": {
      "cannot_connect": "Unable to connect",
      "invalid_auth": "Invalid authentication"
    },
    "abort": {
      "already_configured": "Device is already configured"
    }
  }
}
```

## 最佳实践

1. **始终设置 unique_id**：发现流程必须设置 unique_id 并调用 `_abort_if_unique_id_configured`，hassfest 会强制检查。
2. **用户输入验证**：在步骤方法中验证输入，网络错误映射到 `cannot_connect`，认证错误映射到 `invalid_auth`，其他错误使用语义化键。
3. **数据与选项分离**：核心连接信息（host/api_key）存入 `data`，用户可调偏好（scan_interval/update_interval）存入 `options`。
4. **版本迁移向前兼容**：每次修改 data 结构时递增 VERSION 并实现 `async_migrate_entry`，迁移逻辑按版本号顺序编写。
5. **使用 Selector**：复杂输入使用 `homeassistant.helpers.selector` 提供的选择器（EntitySelector、DeviceSelector、TextSelector 等），获得更好的前端渲染。
6. **ConfigFlow 类以 domain 注册**：使用 `class MyFlow(ConfigFlow, domain="my_domain")` 自动注册，无需手动导入。

## 延伸阅读

- [集成架构](/concepts/14-component-architecture.md)
- [平台开发模式](/concepts/16-platform-pattern.md)
- [配置系统](/concepts/05-configuration.md)
- [hassfest 工具链](/concepts/17-hassfest-tooling.md)

## 相关概念

- [集成架构](/concepts/14-component-architecture.md) — ConfigFlow 是集成的配置入口，ConfigEntry 驱动 async_setup_entry
- [配置系统](/concepts/05-configuration.md) — ConfigEntry 与 YAML 配置并存，存储在 .storage/core.config_entries
- [平台开发模式](/concepts/16-platform-pattern.md) — ConfigEntry 转发到各平台的 async_setup_entry
- [测试模式](/concepts/18-testing-patterns.md) — MockConfigEntry 用于在测试中模拟配置条目的加载与卸载
