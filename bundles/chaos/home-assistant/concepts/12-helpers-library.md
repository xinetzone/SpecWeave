---
type: Concept
title: Helpers 工具库
description: 掌握 Home Assistant helpers 工具库，包括 Template 模板引擎、event helpers 状态跟踪、Debouncer 防抖、signal dispatcher 信号分发、Storage Store 持久化、Selector 选择器、config_validation 验证器和 intent/llm 集成
tags: [home-assistant, smart-home, helpers, template, debouncer, storage, selector, config-validation]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: helpers-util-source
    resource: "/references/helpers-util-source.md"
    title: Home Assistant Helpers 与 Util 源码
  - id: facts-helpers
    resource: "/references/facts-helpers.md"
    title: Home Assistant Helpers 事实清单
---

# Helpers 工具库

`homeassistant/helpers/` 是 Home Assistant 框架的核心工具层，为集成开发者提供可复用的高级抽象。与底层的 `util/` 不同，helpers 依赖 `HomeAssistant` 实例和事件循环，实现模板渲染、状态跟踪、防抖、持久化存储、配置验证等框架级功能。几乎所有集成都直接或间接使用 helpers。本文档介绍最常用的 helpers 模块。

## Template 模板引擎

模板引擎位于 `helpers/template/` 包（事实 #81），是对 Jinja2 模板的 HA 封装。模板广泛用于自动化条件、脚本变量、传感器值模板和 MQTT 负载模板。

### Template 类

```python
from homeassistant.helpers.template import Template

template = Template("{{ states('sensor.temperature') | float > 25 }}", hass)

# 异步渲染（推荐，在事件循环中使用）
result = await template.async_render()

# 同步渲染（仅在非事件循环线程中使用）
result = template.render()
```

`Template` 类维护一个 Jinja2 `Environment`（事实 #82-83），配置了自定义分隔符、扩展和 HA 专用全局函数。模板编译结果被缓存（`_compiled_code`，事实 #92），避免重复编译开销。

### TemplateState

`TemplateState` 类封装实体状态，提供模板中的便捷访问接口（事实 #86-88）：

```jinja2
{{ states.sensor.temp.state }}
{{ states.sensor.temp.attributes.unit_of_measurement }}
{{ states.sensor.temp.last_changed }}
{{ states.sensor.temp.state_with_unit }}
```

### 全局函数

模板环境注册了大量 HA 专用全局函数（事实 #89）：

| 函数 | 说明 |
|------|------|
| `states(entity_id)` | 获取实体状态字符串 |
| `is_state(entity_id, state)` | 判断实体是否处于指定状态 |
| `state_attr(entity_id, name)` | 获取实体属性值 |
| `is_state_attr(entity_id, name, val)` | 判断属性是否等于指定值 |
| `has_value(entity_id)` | 检查实体是否有非 unknown/unavailable 值 |
| `now()` / `utcnow()` | 当前本地/UTC 时间 |
| `relative_time(datetime)` | 相对时间（"5 minutes ago"） |
| `as_timestamp(datetime)` | 转换为 Unix 时间戳 |
| `distance(lat1, lon1, lat2, lon2)` | 计算两点距离 |

### RenderInfo 与自动更新

`RenderInfo` 类跟踪模板渲染过程中访问的实体（事实 #95-96），用于自动化和模板传感器的自动更新触发：

```python
template = Template("{{ states('sensor.temp') > 25 }}", hass)
result = template.async_render()
info = template.render_info

print(info.entities)    # 访问的实体集合
print(info.domains)     # 访问的域
print(info.all_states)  # 是否访问了所有状态
print(info.has_time)    # 是否包含时间函数
```

自动化根据 RenderInfo 知道模板依赖哪些实体，只在相关实体变化时重新评估模板条件。

### 有限模式

`Template` 支持 `limited` 模式（事实 #91），限制模板可访问的变量和函数，用于渲染不可信模板（如用户提供的 MQTT 模板），防止沙箱逃逸。

### result_as_boolean

`result_as_boolean()` 函数（事实 #93）将模板渲染结果智能转换为布尔值，识别 `true/false`、`1/0`、`on/off`、`yes/no` 等字符串。

## Event Helpers：事件辅助

`helpers/event.py` 提供高级事件跟踪函数（事实 #155-171），封装了在[事件总线](/concepts/06-event-bus.md)上手动注册监听器的常见模式。

### async_track_state_change

跟踪实体状态变更（事实 #156）：

```python
from homeassistant.helpers.event import async_track_state_change

def state_changed(entity_id, old_state, new_state):
    if new_state is None:
        return
    print(f"{entity_id}: {old_state.state} -> {new_state.state}")

unsub = async_track_state_change(
    hass, "light.living_room", state_changed,
    from_state="off", to_state="on",
)
entry.async_on_unload(unsub)
```

支持跟踪单个实体 ID、实体 ID 列表，以及 `from_state`/`to_state` 状态过滤。

### async_track_state_change_event

与上一个类似，但回调接收完整的 `Event` 对象（事实 #157），可以访问 context 等更多信息：

```python
from homeassistant.helpers.event import async_track_state_change_event

@callback
def on_change(event):
    entity_id = event.data["entity_id"]
    new_state = event.data["new_state"]

unsub = async_track_state_change_event(hass, ["sensor.temp"], on_change)
```

### async_track_time_interval

按固定间隔执行回调（事实 #159）：

```python
from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval

async def refresh(now):
    await coordinator.async_refresh()

unsub = async_track_time_interval(hass, refresh, timedelta(minutes=5))
```

内部使用 `async_call_later` 链式调度，确保回调不会重叠执行（事实 #160）。

### async_call_later

延迟执行一次性回调（事实 #161）：

```python
from homeassistant.helpers.event import async_call_later

def delayed_action(now):
    print("10 秒后执行")

unsub = async_call_later(hass, 10, delayed_action)
```

### TrackTemplate

跟踪模板结果变化（事实 #166-170）：

```python
from homeassistant.helpers.event import TrackTemplate

template = Template("{{ states('sensor.temp') | float > 25 }}", hass)

def template_changed(event, updates):
    if updates["result"]:
        print("温度超限！")

tracker = TrackTemplate(hass, template, template_changed)
unsub = await tracker.async_start()
```

这是自动化模板触发器的底层实现。

### 时间点跟踪

- `async_track_point_in_time(hass, action, point_in_time)`：在指定本地时间点触发（事实 #163）
- `async_track_point_in_utc_time(hass, action, point_in_time)`：UTC 版本（事实 #164）
- `async_track_sunrise` / `async_track_sunset`：跟踪日出/日落，支持 offset（事实 #165）

## Debouncer：防抖器

`helpers/debounce.py` 提供 `Debouncer` 类（事实 #257-262），用于合并频繁触发的异步调用。

### 使用场景

当多个实体快速连续变化时，如果每个变化都触发数据刷新，会导致大量重复请求。Debouncer 在冷却期内将多次调用合并为一次。

### API

```python
from datetime import timedelta
from homeassistant.helpers.debounce import Debouncer

debouncer = Debouncer(
    hass,
    logger,
    cooldown=timedelta(seconds=5),
    immediate=True,  # True=首次立即执行，后续调用在冷却期内被合并
                     # False=延迟执行，冷却期结束后执行最后一次调用
    function=refresh_data,
)

# 触发调用
result = await debouncer.async_call()

# 取消待执行调用
debouncer.async_cancel()
```

- `immediate=True`（前导防抖）：首次调用立即执行，冷却期内的后续调用返回 None
- `immediate=False`（尾部防抖）：所有调用延迟到冷却期结束后执行最后一次

Debouncer 内部使用 `async_call_later` 调度延迟执行，并通过 `asyncio.Event` 跟踪正在进行的调用。这是数据协调器（DataUpdateCoordinator）的核心组件之一。

## Storage Store：JSON 持久化

`helpers/storage.py` 的 `Store` 类（事实 #244-256）是注册表和其他需要持久化的组件的底层存储。

### 基本用法

```python
from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
STORAGE_KEY = "my_integration.settings"

# 创建 Store
store = Store(hass, STORAGE_VERSION, STORAGE_KEY, private=True)

# 加载数据
data = await store.async_load()
if data is None:
    data = {"default_key": "default_value"}

# 保存数据（延迟写入）
await store.async_save(data)

# 延迟保存（合并时间窗口内多次写入）
store.async_delay_save(lambda: data, delay=1.0)

# 删除存储
await store.async_remove()
```

### 关键特性

1. **延迟写入**：`async_save` 不立即写盘，通过 `async_call_later` 调度，合并短时间内的多次保存
2. **原子写入**：先写临时文件再 `os.replace` 重命名，防止写入中断导致数据损坏
3. **版本迁移**：子类可重写 `async_migrate(old_version, old_data)` 处理旧版本数据
4. **次版本支持**：`minor_version` 支持向后兼容的小版本升级，无需完整迁移
5. **私有模式**：`private=True` 设置文件权限为仅当前用户可读
6. **存储位置**：文件位于 `.storage/<key>`，如 `.storage/core.entity_registry`

### 测试替身

测试中使用 `StoreWithoutWriteLoad`（不写入不加载的替身，事实 #181）或 `mock_storage()` 上下文管理器（事实 #199）模拟存储层，避免测试产生实际文件。

## Selector：选择器体系

`helpers/selector.py` 提供配置 UI 选择器（事实 #221-243），用于在 ConfigFlow、OptionsFlow 和自动化 UI 中生成结构化的输入控件。

### 基类

```python
from homeassistant.helpers.selector import (
    Selector, EntitySelector, NumberSelector, TextSelector,
)

class MySelector(Selector):
    CONFIG_SCHEMA = vol.Schema({...})

    def __call__(self, value):
        return value  # 验证并转换
```

`Selector` 基类提供：
- `__call__(value)`：验证并转换用户输入
- `serialize()`：序列化为前端可用的 JSON 配置

### 常用选择器

```python
# 实体选择器
entity_sel = EntitySelector(
    domain=["light", "switch"],
    device_class=BinarySensorDeviceClass.MOTION,
    multiple=True,
)

# 数字选择器
number_sel = NumberSelector(
    NumberSelectorConfig(
        min=0, max=255, step=1,
        mode=NumberSelectorMode.SLIDER,
        unit_of_measurement="%",
    )
)

# 文本选择器
text_sel = TextSelector(
    TextSelectorConfig(type=TextSelectorType.PASSWORD, multiline=False)
)

# 下拉选择器
select_sel = SelectSelector(
    SelectSelectorConfig(
        options=["low", "medium", "high"],
        multiple=False, custom_value=False,
    )
)

# 目标选择器（实体/设备/区域）
target_sel = TargetSelector()

# 模板选择器
template_sel = TemplateSelector()

# 动作/条件/触发器选择器
action_sel = ActionSelector()
condition_sel = ConditionSelector()
trigger_sel = TriggerSelector()
```

其他选择器包括：AreaSelector、DeviceSelector、BooleanSelector、ColorSelector、ObjectSelector、TimeSelector、DateSelector、DateTimeSelector、DurationSelector、IconSelector、MediaSelector、ThemeSelector、LocationSelector、CategorySelector、FileSelector、BackupLocationSelector、LanguageSelector（事实 #226-242）。

## config_validation：配置验证器

`helpers/config_validation.py` 基于 `voluptuous` 库提供 HA 专用验证器集合（事实 #101-138），是所有配置 schema 的基础。

### 基础类型验证器

```python
from homeassistant.helpers import config_validation as cv

# 布尔值：接受 True/False/"true"/"false"/"yes"/"no"/"on"/"off"/1/0
cv.boolean("on")  # → True

# 路径：转换为 pathlib.Path
cv.path("/config/file.yaml")

# 实体 ID
cv.entity_id("light.kitchen")

# 实体 ID 列表
cv.entity_ids(["light.a", "switch.b"])

# 端口号（1-65535）
cv.port(8080)

# 纬度/经度
cv.latitude(45.5)
cv.longitude(-122.5)

# URL
cv.url("https://example.com")
```

### 时间验证器

```python
# 时间周期：支持字典 {"hours": 1, "minutes": 30} 和字符串 "01:30:00"、"PT1H"
cv.time_period_str("01:30:00")
cv.time_period_seconds({"minutes": 5})  # → 300
cv.positive_time_period_dict({"hours": 2})
```

### 逻辑组合器

```python
# 至少包含一个键
cv.has_at_least_one_key("host", "socket")

# 最多包含一个键
cv.has_at_most_one_key("username", "token")

# 值匹配任一验证器
cv.any_of(cv.string, cv.ensure_list)

# 值匹配所有验证器
cv.all_of(cv.string, cv.matches_regex(r"^[a-z]+$"))
```

### 模板与服务验证器

```python
# 模板：验证并返回 Template 实例
cv.template("{{ states('sensor.x') }}")

# 服务目标：验证 entity_id/device_id/area_id
cv.service_target({"entity_id": "light.living_room"})
```

## Intent：意图处理

`helpers/intent.py` 协调用户意图处理（事实 #191-200），是语音助手（Assist/Alexa/Google Assistant）的后端框架。

### 核心抽象

```python
from homeassistant.helpers.intent import IntentHandler, intent_handler, Intent

class MyIntentHandler(IntentHandler):
    async def async_handle(self, intent):
        slots = intent.slots
        response = intent.create_response()
        response.async_set_speech(f"已处理，参数：{slots}")
        return response

# 或使用装饰器
@intent_handler(slot_schema=...)
async def handle_my_intent(intent, **kwargs):
    ...
```

### 内置意图

HA 预定义了通用设备控制意图（事实 #198）：

- `HassTurnOn`：打开设备（映射到 `light.turn_on` 等服务）
- `HassTurnOff`：关闭设备
- `HassToggle`：切换设备
- `HassSetCoverage`：设置覆盖率（窗帘/百叶窗位置）

`ServiceIntentHandler` 类将意图自动映射到服务调用（事实 #200），`async_match_targets()` 根据槽位匹配目标实体/设备/区域（事实 #199）。

## LLM：大语言模型工具

`helpers/llm.py` 为大语言模型集成提供工具抽象（事实 #201-211），支持 Assist 对话和外部 LLM API。

### Tool 抽象

```python
from homeassistant.helpers.llm import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "执行自定义操作"
    parameters = {...}  # JSON Schema

    async def async_call(self, **kwargs):
        return {"result": "done"}
```

### API 与工具注册

```python
from homeassistant.helpers.llm import async_get_api, async_get_tools

# 获取默认 LLM API 实例
api = await async_get_api(hass)

# 获取所有已注册工具
tools = await async_get_tools(hass)
```

内置工具包括：
- `IntentTool`：将意图处理暴露为 LLM 可调用工具（事实 #206）
- `ScriptTool`：将脚本执行暴露为 LLM 工具（事实 #207）
- `AssistConversationTool`：支持 Assist 语音助手（事实 #208）

`LLMContext` 数据类携带平台、上下文、用户提示、语言和设备 ID 等信息（事实 #209）。`ToolInput` 类封装工具调用的输入参数（事实 #210）。

## 其他重要 Helpers

### signal dispatcher

`helpers/signal.py` 提供系统信号处理（事实 #264）：

- `async_register_signal_handlers(hass)`：注册 SIGTERM、SIGINT、SIGHUP 处理器，分别触发 HA 停止或重载

此外，HA 内部使用基于 dispatcher 的消息发送模式（`async_dispatcher_send`/`async_dispatcher_connect`），在同进程内实现松耦合通信，常用于注册表更新通知和配置条目变更信号。

### frame 调用栈分析

`helpers/frame.py`（事实 #265-269）分析调用栈，定位调用来自哪个集成：

- `get_integration_frame()`：找到第一个属于 `homeassistant.components.*` 的栈帧
- `report()`：报告集成代码中的不当使用，记录日志或抛出异常
- `report_usage()`：报告已弃用的 API 使用

这是 HA 实施 API 治理和集成质量管控的底层机制。

### group 实体组

`helpers/group.py`（事实 #280-283）提供实体分组功能：
- `Group` 基类、`GenericGroup`（任意域实体）、`IntegrationSpecificGroup`（特定集成）
- `async_expand_entity_ids()`：递归展开组引用为成员实体 ID

### start 启动任务

`helpers/start.py`（事实 #285-286）：
- `async_at_started(hass, callback)`：在 HA 完全启动后执行（若已启动则立即执行）
- `async_at_start(hass, callback)`：在启动阶段（started 之前）执行

### state 状态工具

`helpers/state.py`（事实 #301-304）：
- `async_reproduce_state()`：重现历史状态（调用对应服务恢复状态）
- `state_as_number()`：将 State 的 state 转换为数字，处理 unknown/unavailable
- `async_reproduce_states()`：批量重现状态列表

## 延伸阅读

- [实体模型](/concepts/09-entity-model.md)
- [事件总线](/concepts/06-event-bus.md)
- [Util 工具集](/concepts/13-utilities.md)
- [服务注册表](/concepts/08-service-registry.md)

## 相关概念

- [事件总线](/concepts/06-event-bus.md) — async_track_state_change 等事件跟踪 helper 的底层通信通道
- [实体模型](/concepts/09-entity-model.md) — Entity 基类、EntityComponent、EntityPlatform 等 helper 提供实体管理框架
- [Util 工具集](/concepts/13-utilities.md) — 底层无状态工具函数（dt、json、yaml），helpers 在其上构建有状态抽象
- [配置流](/concepts/15-config-flow.md) — Selector、config_validation 等 helper 为 ConfigFlow 提供表单构建支持
