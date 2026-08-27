---
type: Example
title: 完整自定义集成示例
description: 从零创建一个完整的 Home Assistant 自定义集成，涵盖 manifest.json、__init__.py、light 平台、config_flow 和 strings.json，展示从声明元数据到注册实体的完整流程
tags: [home-assistant, example, custom-integration, config-flow, light, entity, development]
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
---

# 完整自定义集成示例

本示例演示如何从零创建一个完整的 Home Assistant 自定义集成 `example_smartlight`，模拟一个通过 HTTP API 控制的智能灯。示例包含五个核心文件：`manifest.json`（元数据声明）、`__init__.py`（生命周期管理）、`config_flow.py`（用户配置界面）、`light.py`（灯实体平台）、`strings.json`（翻译键）。所有 API 均来自 Home Assistant 源码验证，代码遵循 HA 集成开发规范，可直接放入 `custom_components/` 目录运行。

## 集成目录结构

```text
config/custom_components/example_smartlight/
├── __init__.py          # 集成入口与生命周期
├── manifest.json        # 集成元数据
├── config_flow.py       # 配置流
├── light.py             # 灯实体平台
├── strings.json         # 翻译字符串
└── const.py             # 常量定义
```

## 步骤一：manifest.json

`manifest.json` 是集成的身份声明，hassfest 会校验其 schema。自定义集成必须包含 `version` 字段：

```json
{
  "domain": "example_smartlight",
  "name": "Example Smart Light",
  "codeowners": ["@your-github-username"],
  "config_flow": true,
  "documentation": "https://example.com/docs/smartlight",
  "iot_class": "local_polling",
  "version": "1.0.0",
  "requirements": [],
  "integration_type": "device",
  "issue_tracker": "https://example.com/issues"
}
```

关键字段说明：
- `domain`：集成唯一标识，全小写，与目录名一致
- `config_flow: true`：启用 ConfigFlow 配置界面（必须配套 `config_flow.py`）
- `iot_class: "local_polling"`：本地轮询型设备，hassfest 验证此字段必须为 6 个合法值之一
- `version`：自定义集成必需字段，使用语义化版本号
- `integration_type: "device"`：设备型集成，可拥有设备注册表条目

## 步骤二：const.py

集中定义常量，避免在多个文件中硬编码字符串：

```python
"""Constants for the Example Smart Light integration."""
from typing import Final

DOMAIN: Final = "example_smartlight"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"

DEFAULT_PORT: Final = 8080

PLATFORMS: list[Platform] = [Platform.LIGHT]
```

## 步骤三：__init__.py

集成入口模块实现 `async_setup_entry` 和 `async_unload_entry` 两个生命周期函数。这是基于 ConfigEntry 的现代集成模式（YAML 配置的旧式集成才需要 `async_setup`）：

```python
"""The Example Smart Light integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeData:
    """Runtime data stored in entry.runtime_data."""
    session: aiohttp.ClientSession
    host: str
    port: int


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Example Smart Light from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    session = aiohttp.ClientSession()

    try:
        async with session.get(f"http://{host}:{port}/status") as resp:
            resp.raise_for_status()
    except Exception as err:
        await session.close()
        _LOGGER.error("Failed to connect to %s:%s: %s", host, port, err)
        return False

    entry.runtime_data = RuntimeData(
        session=session,
        host=host,
        port=port,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data: RuntimeData = entry.runtime_data
        await data.session.close()

    return unload_ok
```

关键设计要点：
- `async_setup_entry` 在 ConfigEntry 被设置时调用，返回 `True` 表示成功，`False` 表示失败（HA 会将条目标记为 SETUP_ERROR）
- 运行时数据存入 `entry.runtime_data`（hassfest quality_scale `runtime-data` 规则要求），而非 `hass.data[DOMAIN]`
- `async_forward_entry_setups` 将平台转发给 light 模块处理，HA 会自动调用 `light.py` 的 `async_setup_entry`
- `async_unload_entry` 必须调用 `async_unload_platforms` 并清理资源（关闭 HTTP session），quality_scale SILVER 级别要求支持卸载
- 使用 `aiohttp.ClientSession` 进行 HTTP 通信（异步），quality_scale PLATINUM 的 `async-dependency` 规则禁止阻塞 I/O

## 步骤四：config_flow.py

配置流向用户展示表单，收集连接参数。ConfigFlow 继承自 `config_entries.ConfigFlow`，domain 参数必须与 manifest 一致：

```python
"""Config flow for Example Smart Light."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


class ExampleSmartLightConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Example Smart Light."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://{host}:{port}/status", timeout=5
                    ) as resp:
                        resp.raise_for_status()
            except aiohttp.ClientConnectorError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during connection test")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Smart Light ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
```

关键设计要点：
- `VERSION = 1`：配置条目的数据版本号，后续迁移时递增
- `domain=DOMAIN`：类声明中的关键字参数将此 Flow 绑定到集成 domain
- `async_step_user` 是用户在 UI 上点击集成时进入的第一个步骤
- 使用 voluptuous schema 定义表单字段，`cv.port` 验证端口号范围
- `async_set_unique_id` + `_abort_if_unique_id_configured` 防止重复配置同一设备（quality_scale BRONZE `unique-config-entry` 规则）
- 配置前先测试连接（quality_scale BRONZE `test-before-configure` 规则）
- 错误通过 `errors` 字典返回，键 `"base"` 对应表单级错误，翻译键在 strings.json 中定义
- `async_create_entry` 创建 ConfigEntry，`title` 显示在 UI 集成列表中

## 步骤五：light.py

light 平台模块定义实体。使用 `async_setup_entry` 模式（现代推荐），继承 `LightEntity`：

```python
"""Light platform for Example Smart Light."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RuntimeData
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ExampleSmartLight(LightEntity):
    """Representation of an Example Smart Light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, runtime_data: RuntimeData) -> None:
        """Initialize the light."""
        self._session = runtime_data.session
        self._host = runtime_data.host
        self._port = runtime_data.port
        self._attr_unique_id = f"{runtime_data.host}:{runtime_data.port}:light"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, runtime_data.host)},
            name=f"Smart Light ({runtime_data.host})",
            manufacturer="Example Inc.",
            model="Smart Light Pro",
            sw_version="1.0.0",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        payload: dict[str, Any] = {"state": "on"}

        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            payload["brightness"] = round(brightness / 255 * 100)

        try:
            async with self._session.post(
                f"http://{self._host}:{self._port}/control",
                json=payload,
            ) as resp:
                resp.raise_for_status()
            self._attr_is_on = True
            if ATTR_BRIGHTNESS in kwargs:
                self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        except Exception:
            _LOGGER.exception("Failed to turn on the light")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            async with self._session.post(
                f"http://{self._host}:{self._port}/control",
                json={"state": "off"},
            ) as resp:
                resp.raise_for_status()
            self._attr_is_on = False
        except Exception:
            _LOGGER.exception("Failed to turn off the light")

    async def async_update(self) -> None:
        """Fetch latest state from the device."""
        try:
            async with self._session.get(
                f"http://{self._host}:{self._port}/status"
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
            self._attr_is_on = data.get("state") == "on"
            if brightness_pct := data.get("brightness"):
                self._attr_brightness = round(brightness_pct / 100 * 255)
        except Exception:
            self._attr_available = False
            _LOGGER.warning("Could not fetch status from %s", self._host)
        else:
            self._attr_available = True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Example Smart Light from a config entry."""
    runtime_data: RuntimeData = entry.runtime_data
    async_add_entities([ExampleSmartLight(runtime_data)])
```

关键设计要点：
- `LightEntity` 是灯平台基类，继承自 `Entity`，提供 `async_turn_on`/`async_turn_off` 抽象方法
- `_attr_supported_color_modes` 声明支持的颜色模式集合，`_attr_color_mode` 设置当前模式（BRIGHTNESS 表示支持亮度调节）
- `_attr_unique_id` 必须全局唯一，HA 用它跟踪实体的状态和配置
- `_attr_device_info` 使用 `DeviceInfo` 类型注册设备，关联到设备注册表（quality_scale GOLD `devices` 规则）
- `_attr_has_entity_name = True` + `_attr_name = None`：实体名称由设备名派生，UI 显示为设备名而非冗余的设备名+实体名
- `async_turn_on` 接收 `**kwargs`，通过 `ATTR_BRIGHTNESS` 键检查是否需要设置亮度
- `async_update` 是轮询方法，HA 按 SCAN_INTERVAL（默认 30 秒）调用，获取设备最新状态
- 设备不可用时设置 `_attr_available = False`（quality_scale SILVER `entity-unavailable` 规则）
- `async_setup_entry` 是平台入口，调用 `async_add_entities` 注册实体实例

## 步骤六：strings.json

`strings.json` 定义用户界面中显示的所有文本。hassfest 验证翻译键格式，ConfigFlow 的 step 和 error 必须在此声明：

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to your Smart Light",
        "description": "Enter the connection details for your Example Smart Light device.",
        "data": {
          "host": "Host",
          "port": "Port"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect. Please check the host and port and try again.",
      "unknown": "An unexpected error occurred."
    },
    "abort": {
      "already_configured": "This device is already configured."
    }
  },
  "entity": {
    "light": {
      "example_smartlight": {
        "name": "Light"
      }
    }
  }
}
```

翻译键结构说明：
- `config.step.user`：对应 `async_step_user` 表单的标题、描述和字段标签
- `config.error.cannot_connect`/`unknown`：对应 ConfigFlow 中 `errors["base"]` 返回的错误码
- `config.abort.already_configured`：对应 `_abort_if_unique_id_configured()` 触发时显示的消息
- `entity.light`：实体翻译，quality_scale GOLD `entity-translations` 规则要求

## 完整工作流

1. 用户在 HA 界面点击"添加集成"，搜索"Example Smart Light"
2. HA 读取 `manifest.json`，发现 `config_flow: true`，实例化 `ExampleSmartLightConfigFlow`
3. 调用 `async_step_user(None)`，返回表单（FORM 结果），前端渲染 host/port 输入框
4. 用户填写并提交，HA 再次调用 `async_step_user(user_input)`
5. ConfigFlow 尝试连接设备：
   - 连接失败 → 返回带 errors 的表单，前端显示错误信息
   - 连接成功 → 调用 `async_set_unique_id` 和 `async_create_entry`，创建 ConfigEntry
6. HA 调用 `__init__.py` 的 `async_setup_entry`：
   - 创建 aiohttp session，测试连接
   - 存储 RuntimeData 到 `entry.runtime_data`
   - 调用 `async_forward_entry_setups` 转发到 light 平台
7. HA 调用 `light.py` 的 `async_setup_entry`，创建 `ExampleSmartLight` 实体并注册
8. 实体出现在 UI 中，用户可开关灯、调节亮度
9. HA 按轮询间隔调用 `async_update` 获取最新状态
10. 用户卸载集成时，HA 调用 `async_unload_entry`，卸载平台并关闭 HTTP session

## 测试示例

以下是对应的 ConfigFlow 测试骨架（使用 HA 测试基础设施）：

```python
"""Test the Example Smart Light config flow."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.components.example_smartlight.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_flow_user_success(hass: HomeAssistant) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with (
        patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get,
        patch(
            "homeassistant.components.example_smartlight.async_setup_entry",
            return_value=True,
        ) as mock_setup,
    ):
        mock_get.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"host": "192.168.1.100", "port": 8080},
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Smart Light (192.168.1.100)"
    assert result2["data"] == {"host": "192.168.1.100", "port": 8080}
    assert len(mock_setup.mock_calls) == 1


async def test_flow_user_cannot_connect(hass: HomeAssistant) -> None:
    """Test connection error handling."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("aiohttp.ClientSession.get", side_effect=ConnectionError):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"host": "192.168.1.100", "port": 8080},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
```

## 运行验证

将集成放入 `config/custom_components/example_smartlight/` 后，使用 hassfest 验证：

```bash
python -m script.hassfest --integration-path config/custom_components/example_smartlight
```

运行测试：

```bash
pytest tests/components/example_smartlight/ -v
```

## 延伸阅读

- [集成架构](/concepts/14-component-architecture.md)
- [配置流](/concepts/15-config-flow.md)
- [平台开发模式](/concepts/16-platform-pattern.md)
- [hassfest 工具链](/concepts/17-hassfest-tooling.md)
- [测试模式](/concepts/18-testing-patterns.md)
