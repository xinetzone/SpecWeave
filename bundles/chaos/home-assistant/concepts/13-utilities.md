---
type: Concept
title: Util 工具集
description: 掌握 Home Assistant util 工具集，包括 dt 日期时间处理、json（orjson）序列化、yaml（!secret）加载、async_ 异步工具、color 颜色空间转换、unit_system 单位系统、timeout 超时管理、ulid 标识符和 network 网络工具
tags: [home-assistant, smart-home, util, datetime, json, yaml, color, unit-system, async, utilities]
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

# Util 工具集

`homeassistant/util/` 是 Home Assistant 的底层工具库，提供与框架无关的纯 Python 实用函数。与依赖 `HomeAssistant` 实例的 [Helpers 工具库](/concepts/12-helpers-library.md)不同，util 模块不依赖事件循环或 HA 运行时，可以在任何上下文中安全导入。util 覆盖日期时间处理、JSON/YAML 序列化、异步工具、颜色空间转换、单位系统、超时管理、标识符生成和网络工具等领域，是整个 HA 代码库的基础积木。

## util 通用工具（`util/__init__.py`）

在介绍各专用模块之前，先看 `util/__init__.py` 中的通用工具函数（事实 #305-321）。

### 文件名与路径安全

```python
from homeassistant.util import (
    raise_if_invalid_filename,
    raise_if_invalid_path,
    slugify,
    sanitize_filename,
)

# 校验文件名，拒绝 ~、..、/、\
raise_if_invalid_filename("../../etc/passwd")  # 抛出 ValueError

# 生成 URL/文件友好的 slug
slugify("Living Room Light!")  # → "living_room_light"
slugify("")                    # → ""
slugify("!!!")                 # → "unknown"
```

`RE_SANITIZE_FILENAME` 正则匹配 `~`、`..`、`/`、`\\`（事实 #306），`RE_SANITIZE_PATH` 匹配 `~` 和连续点号（事实 #307），防止路径遍历攻击。

### 类型转换与字符串工具

```python
from homeassistant.util import convert, ensure_unique_string, get_random_string, snakecase

# 安全类型转换，失败返回默认值
convert("25.5", float, default=0.0)  # → 25.5
convert("abc", float, default=0.0)   # → 0.0
convert(None, int, default=-1)       # → -1

# 生成唯一字符串，冲突时追加后缀
ensure_unique_string("light", ["light", "light_2"])  # → "light_3"

# 密码学安全的随机字符串
get_random_string(length=16)  # → "aB3xK9mP..."

# 驼峰转蛇形
snakecase("HTTPResponse")  # → "http_response"
snakecase("LivingRoom")    # → "living_room"
```

`convert` 是泛型函数（事实 #312），捕获 `ValueError` 和 `TypeError`，用于解析配置文件中的字符串值。

### Throttle 节流装饰器

`Throttle` 类（事实 #317-321）限制方法调用频率，冷却期内重复调用返回 `None`：

```python
from homeassistant.util import Throttle
from datetime import timedelta

class MyDataCoordinator:
    @Throttle(timedelta(minutes=5))
    async def async_update(self):
        await self._fetch_data()

coordinator = MyDataCoordinator()
await coordinator.async_update()  # 执行
await coordinator.async_update()  # 冷却期内，返回 None
await coordinator.async_update(no_throttle=True)  # 强制执行
```

Throttle 自动检测协程函数并返回协程占位函数（事实 #319），使用 `threading.Lock()` 保证线程安全（事实 #320），节流状态存储在 host 对象的 `_throttle` 字典中。

## dt：日期时间处理（`util/dt.py`）

`util/dt.py` 是 HA 中使用最频繁的工具模块之一（事实 #322-354），处理时区、日期解析、持续时间和时间格式化。

### 时区管理

```python
from homeassistant.util import dt as dt_util

# UTC 时区常量
utc_now = dt_util.utcnow()  # datetime.now(UTC)

# 获取/设置全局默认时区
tz = dt_util.get_default_time_zone()          # lru_cache 缓存
dt_util.set_default_time_zone(zone)           # 清除缓存，全局生效

# 异步获取时区（避免在事件循环中阻塞 I/O）
tz = await dt_util.async_get_time_zone("Asia/Shanghai")

# 当前时间
dt_util.now()              # 默认时区当前时间
dt_util.now(tz)            # 指定时区当前时间
dt_util.naive_now()        # 系统本地 naive 时间
```

`set_default_time_zone` 要求参数为 `dt.tzinfo` 实例（事实 #332），使用 `zoneinfo.ZoneInfo`（Python 3.9+）。异步版本通过 `aiozoneinfo` 获取时区（事实 #334, #354），避免读取时区数据库文件时阻塞事件循环。

### 时间转换

```python
# naive → UTC（naive 假定为默认时区）
utc_dt = dt_util.as_utc(local_naive_dt)

# UTC → 本地时间
local_dt = dt_util.as_local(utc_dt)

# datetime/字符串 → Unix 时间戳
ts = dt_util.as_timestamp("2026-08-23T12:00:00+00:00")

# 时间戳 → UTC datetime
dt = dt_util.utc_from_timestamp(1787444124)

# 本地日起始时间
start = dt_util.start_of_local_day()  # 今天 00:00:00
```

`as_utc` 对 naive datetime 假定其属于默认时区（事实 #338），`as_timestamp` 对无效输入抛出 `ValueError`（事实 #339）。

### 日期时间解析

`parse_datetime` 支持多种格式（事实 #343-345）：

```python
# 优先使用 ciso8601 快速解析，失败后回退正则
dt = dt_util.parse_datetime("2026-08-23T12:00:00Z")
dt = dt_util.parse_datetime("2026-08-23T12:00:00+08:00")

# 解析失败返回 None，raise_on_error=True 抛出 ValueError
dt = dt_util.parse_datetime("invalid", raise_on_error=True)

# 日期解析
date = dt_util.parse_date("2026-08-23")

# 时间解析
time = dt_util.parse_time("14:30:00")
time = dt_util.parse_time("14:30")
```

`DATETIME_RE` 正则解析 `年-月-日T时:分:秒.微秒+时区` 格式（事实 #327），支持 `Z` 后缀和 `+HH:MM`/`-HH:MM` 偏移量（事实 #344）。

### 持续时间解析

```python
# 支持三种格式
dt_util.parse_duration("1 days, 2:30:00")   # 标准格式 → timedelta(days=1, hours=2, minutes=30)
dt_util.parse_duration("PT1H30M")           # ISO 8601 → timedelta(hours=1, minutes=30)
dt_util.parse_duration("1 day 2 hours")     # PostgreSQL 间隔
```

三个正则分别处理标准格式（`STANDARD_DURATION_RE`，事实 #328）、ISO 8601（`ISO8601_DURATION_RE`，事实 #329）和 PostgreSQL 间隔（`POSTGRES_INTERVAL_RE`，事实 #330）。

### 人类可读时间

```python
# 计算年龄（过去时间）
age = dt_util.get_age(past_datetime, precision=1)   # → "5 hours ago"

# 计算剩余时间（未来时间）
remaining = dt_util.get_time_remaining(future_dt)   # → "in 2 days"
```

`get_age` 对未来时间抛出 `ValueError`（事实 #350），`get_time_remaining` 对过去时间抛出 `ValueError`（事实 #351）。两者内部使用 `_get_timestring` 将秒数格式化为年/月/日/时/分/秒字符串（事实 #349）。

## json：JSON 序列化（`util/json.py`）

`util/json.py` 基于高性能的 `orjson` 库（事实 #355），提供 JSON 编码解码和文件加载功能。

### 类型定义

```python
from homeassistant.util.json import (
    JsonValueType, JsonObjectType, JsonArrayType,
    json_loads, json_loads_object, json_loads_array,
    load_json, load_json_object, load_json_array,
    SerializationError, JSON_ENCODE_EXCEPTIONS, JSON_DECODE_EXCEPTIONS,
)
```

`JsonValueType` 是递归类型别名（事实 #356）：

```python
JsonValueType = dict[str, JsonValueType] | list[JsonValueType] | str | int | float | bool | None
```

### 解析与加载

```python
# 解析 JSON 字符串（含 orjson str 子类 workaround）
data = json_loads('{"key": "value"}')

# 解析并确保类型为 dict/object
obj = json_loads_object('{"name": "HA"}')   # 非 dict 抛出 ValueError

# 解析并确保类型为 list/array
arr = json_loads_array('[1, 2, 3]')         # 非 list 抛出 ValueError

# 从文件加载
config = load_json("/config/data.json")              # 文件不存在返回 {}
config = load_json("/config/data.json", default=None) # 自定义默认值

# 从文件加载并确保类型
settings = load_json_object("settings.json")  # 默认空 dict
items = load_json_array("items.json")         # 默认空 list
```

`load_json` 以二进制模式打开文件（`"rb"`）并使用 `orjson.loads` 解析（事实 #366），捕获 `FileNotFoundError` 记录 debug 日志，捕获解码错误和 `OSError` 抛出 `HomeAssistantError`（事实 #367）。`json_loads` 包含针对 orjson 不支持 `str` 子类的 workaround（issue #445，事实 #362）。

### helpers/json.py

框架层的 `helpers/json.py` 在 util/json 之上提供 HA 对象的序列化能力（事实 #270-273）：

- `JSONEncoder` 继承 `json.JSONEncoder`，支持序列化 `set`、`datetime`、`Decimal`、`bytes`、`UUID`、`BaseEnum`、`Event`、`State`、`Entity`、`Path` 等类型（事实 #271）
- `json_bytes(data, indent=False)` 序列化为字节串（事实 #272）
- `json_dumps(data, indent=False)` 序列化为字符串（事实 #273）

## yaml：YAML 加载（`util/yaml/`）

`util/yaml/loader.py` 基于 `annotatedyaml` 库（事实 #371），提供自定义 YAML 加载器，支持 `!secret` 标签。

### 加载函数

```python
from homeassistant.util.yaml import (
    load_yaml, load_yaml_dict, parse_yaml,
    Secrets, YamlTypeError, add_constructor,
    HAS_C_LOADER,
)

# 加载 YAML 文件
data = load_yaml("/config/configuration.yaml")

# 加载并确保顶层为字典（空文件返回空 dict）
config = load_yaml_dict("/config/configuration.yaml")

# 解析 YAML 字符串
data = parse_yaml("name: Home Assistant\nlatitude: 45.5")
```

- `load_yaml` 将 `annotatedyaml.YAMLException` 包装为 `HomeAssistantError`，`FileNotFoundError` 原样抛出（事实 #378）
- `load_yaml_dict` 在顶层非字典时抛出 `YamlTypeError`（事实 #379）
- `HAS_C_LOADER` 指示是否有 C YAML 加载器可用（事实 #372）

### !secret 标签

`secret_yaml` 函数处理 `!secret` YAML 标签（事实 #381），从 secrets 文件加载敏感值：

```yaml
# configuration.yaml
http:
  api_password: !secret http_password
```

`Secrets` 类从 `annotatedyaml` 导出（事实 #373），管理 secrets 文件的加载和缓存。`add_constructor` 函数允许注册自定义 YAML 标签构造器（事实 #376），HA 使用它注册 `!include`、`!include_dir_list`、`!include_dir_merge_list`、`!include_dir_named`、`!include_dir_merge_named` 等指令来拆分配置文件。

## async_：异步工具（`util/async_.py`）

`util/async_.py` 提供 asyncio 增强工具（事实 #383-394）。

### create_eager_task

```python
from homeassistant.util.async_ import create_eager_task

# 创建立即调度的 Task（eager_start=True），减少调度延迟
task = create_eager_task(fetch_data(), name="fetch")
```

与 `asyncio.create_task` 不同，`create_eager_task` 使用 `eager_start=True`（事实 #384），任务在创建时立即开始执行直到第一个 await 点，减少了一次事件循环调度开销。从非事件循环线程调用时，会通过 `frame.report_usage` 报告错误（事实 #385）。

### run_callback_threadsafe

```python
from homeassistant.util.async_ import run_callback_threadsafe

# 从其他线程向事件循环提交回调
future = run_callback_threadsafe(hass.loop, update_ui, "data")
result = future.result(timeout=5)
```

该函数（事实 #387）：
- 检测是否在事件循环线程内调用，若是则抛出 `RuntimeError`（事实 #388）
- 在事件循环关闭时抛出 `RuntimeError` 防止死锁（事实 #389）
- 返回 `concurrent.futures.Future`，可同步等待结果

### gather_with_limited_concurrency

```python
from homeassistant.util.async_ import gather_with_limited_concurrency

# 限制并发数为 5
results = await gather_with_limited_concurrency(
    5, *[fetch(i) for i in range(20)],
    return_exceptions=True,
)
```

内部使用 `asyncio.Semaphore` 限制并发任务数（事实 #390），每个任务通过 `create_eager_task` 创建（事实 #391），适用于批量 API 调用等需要限流的场景。

### 其他工具

- `cancelling(task)`：返回 Task 是否正在取消（Python 3.11+ `cancelling()` 方法，事实 #386）
- `shutdown_run_callback_threadsafe(loop)`：设置循环关闭标记，不可逆，仅在 HA 关闭时调用（事实 #392）
- `get_scheduled_timer_handles(loop)`：返回循环上已调度的 `TimerHandle` 列表（事实 #393）

## color：颜色空间转换（`util/color.py`）

`util/color.py` 提供灯光控制所需的颜色空间转换（事实 #415-433），主要被 `light` 集成使用。

### 数据类型

```python
from homeassistant.util.color import (
    RGBColor, XYPoint, GamutType,
    color_name_to_rgb, color_RGB_to_xy, color_xy_to_RGB,
    color_hsb_to_RGB, color_RGB_to_hsv,
)

# RGB 颜色（0-255）
rgb = RGBColor(255, 128, 0)

# CIE 1931 XY 坐标
xy = XYPoint(0.5, 0.4)

# 灯光色域（Philips Hue 等支持色域约束）
gamut = GamutType(
    red=XYPoint(0.704, 0.296),
    green=XYPoint(0.2151, 0.7106),
    blue=XYPoint(0.138, 0.08),
)
```

`RGBColor` 是 `NamedTuple`（事实 #416），`XYPoint` 和 `GamutType` 使用 `attr.s()` 定义（事实 #418-419）。`COLORS` 字典包含 140+ 个 CSS3 颜色名映射，并额外包含 `"homeassistant": RGBColor(24, 188, 242)`（事实 #417）。

### 颜色转换

```python
# 颜色名 → RGB
rgb = color_name_to_rgb("deep sky blue")  # 不区分大小写，忽略空格

# RGB → XY 坐标
x, y = color_RGB_to_xy(255, 128, 0)
x, y, brightness = color_RGB_to_xy_brightness(255, 128, 0, Gamut=gamut)

# XY → RGB
r, g, b = color_xy_to_RGB(x, y)
r, g, b = color_xy_brightness_to_RGB(x, y, brightness=200, Gamut=gamut)

# HSV → RGB
r, g, b = color_hsb_to_RGB(240, 1.0, 1.0)  # H: 0-360, S: 0-1, B: 0-1
r, g, b = color_hsv_to_RGB(240, 100, 100)  # H: 0-360, S: 0-100, V: 0-100

# RGB → HSV
h, s, v = color_RGB_to_hsv(255, 0, 0)  # → (0, 100, 100)
h, s = color_RGB_to_hs(255, 0, 0)      # 不含亮度
```

转换使用 Wide RGB D65 转换公式和 Gamma 校正（事实 #423），支持 Gamut 色域约束——超出色域时通过 `get_closest_point_to_point` 找到最近点（事实 #424）。HSV 转换基于 Python 标准库 `colorsys`（事实 #428, #430）。

## unit_system：单位系统（`util/unit_system.py`）

`util/unit_system.py` 管理公制和美制单位系统（事实 #434-451），负责传感器数据的自动单位转换。

### UnitSystem 类

`UnitSystem` 是 frozen dataclass（事实 #436），包含所有测量类型的单位字段：

```python
@dataclass(frozen=True, kw_only=True)
class UnitSystem:
    temperature_unit: str
    length_unit: str
    mass_unit: str
    pressure_unit: str
    volume_unit: str
    wind_speed_unit: str
    area_unit: str
    accumulated_precipitation_unit: str
```

### 单位转换

```python
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM, get_unit_system

# 预定义单位系统
metric = METRIC_SYSTEM         # °C, km, g, Pa, L, m/s, m²
us = US_CUSTOMARY_SYSTEM       # °F, mi, lb, PSI, gal, mph, ft²

# 按配置键获取
system = get_unit_system("metric")       # 或 "us_customary"

# 温度转换
celsius = METRIC_SYSTEM.temperature(72, UnitOfTemperature.FAHRENHEIT)

# 长度转换
km = METRIC_SYSTEM.length(10, UnitOfLength.MILES)

# 压力转换
hpa = METRIC_SYSTEM.pressure(29.92, UnitOfPressure.INHG)

# 序列化为字典
d = METRIC_SYSTEM.as_dict()
```

`UnitSystem.__init__` 验证所有单位是否合法，不合法时收集错误并抛出 `ValueError`（事实 #437）。转换方法使用 `TemperatureConverter`、`DistanceConverter` 等转换器（事实 #438-440）。`get_converted_unit(device_class, original_unit)` 根据设备类查询转换后的单位（事实 #442）。

### 配置验证

`validate_unit_system` 是 voluptuous schema（事实 #444），将输入转小写、映射已弃用的 `"imperial"` 到 `"us_customary"`，验证为 `"metric"` 或 `"us_customary"`。`METRIC_SYSTEM` 的 `conversions` 字典定义非 metric 单位到 metric 单位的自动转换映射（事实 #447），传感器实体根据此映射自动转换上报值。

## timeout：超时管理（`util/timeout.py`）

`util/timeout.py` 提供高级异步超时管理（事实 #452-462），比 `asyncio.timeout` 增加了冻结（freeze）和冷却（cool_down）能力。

### TimeoutManager

```python
from homeassistant.util.timeout import TimeoutManager

manager = TimeoutManager()

# 带超时的操作
async with manager.async_timeout(30):
    await long_running_operation()

# 冻结计时器（暂停超时倒计时）
async with manager.async_freeze():
    # 在此期间不计入超时
    await paused_operation()
```

`TimeoutManager.async_timeout(timeout, zone_name, cool_down, cancel_message)` 返回异步上下文管理器（事实 #456），在超时后取消当前任务。`async_freeze(zone_name)` 冻结指定区域的计时器（事实 #457），在测试和调试中很有用。

### 全局与区域超时

- `ZONE_GLOBAL = "global"` 定义全局超时区域（事实 #453）
- `_GlobalTaskContext` 管理全局超时任务，支持 cool_down 等待区域任务完成（事实 #459）
- `_ZoneTaskContext` 管理命名区域超时，在 freeze 期间暂停计时器（事实 #460）
- 超时上下文管理器在退出时检测 `CancelledError`，若因超时取消则抛出 `TimeoutError`，并通过 `uncancel()` 管理取消计数（事实 #462）

## ulid：ULID 标识符（`util/ulid.py`）

`util/ulid.py` 基于 `ulid_transform` 库生成 ULID（Universally Unique Lexicographically Sortable Identifier）（事实 #465-468）。

```python
from homeassistant.util.ulid import ulid, ulid_now, ulid_at_time, ulid_to_bytes

# 生成 ULID（基于当前时间）
id = ulid()  # → "01HXYZ..."（26 字符 Crockford Base32）

# 指定时间戳生成
id = ulid_at_time(1787444124.123)

# ULID → bytes
raw = ulid_to_bytes(id)
```

ULID 结构为 48 位时间戳 + 80 位随机数，共 26 个字符（事实 #467），具有以下特性：
- **字典序可排序**：按时间戳排序，适合作为数据库主键
- **URL 安全**：使用 Crockford Base32 编码（无特殊字符）
- **大小写不敏感**：无大小写歧义字符
- **比 UUID 更短**：26 字符 vs UUID 的 36 字符

HA 中 Context ID、日志条目等广泛使用 ULID。`random_uuid_hex()`（`util/uuid.py`，事实 #464）生成 32 字符随机 UUID 十六进制字符串，但不适用于密码学安全场景。

## network：网络工具（`util/network.py`）

`util/network.py` 提供 IP 地址分类和验证（事实 #486-497）。

### 网络范围常量

```python
from homeassistant.util.network import (
    is_loopback, is_private, is_link_local, is_local,
    is_ip_address, is_ipv4_address, is_ipv6_address,
    is_invalid, is_host_valid,
    LOOPBACK_NETWORKS, PRIVATE_NETWORKS, LINK_LOCAL_NETWORKS,
)
```

三个网络元组定义了（事实 #487-489）：
- `LOOPBACK_NETWORKS`：`127.0.0.0/8`、`::1/128`、IPv4-mapped IPv6 回环
- `PRIVATE_NETWORKS`：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`、`fd00::/8`
- `LINK_LOCAL_NETWORKS`：`169.254.0.0/16`、`fe80::/10`

### 地址判断

```python
is_loopback("127.0.0.1")     # True
is_private("192.168.1.1")    # True
is_link_local("169.254.1.1") # True
is_local("10.0.0.5")         # True（回环+私有+链路本地）

is_ip_address("192.168.1.1")    # True
is_ipv4_address("::1")          # False
is_ipv6_address("::1")          # True
is_invalid("0.0.0.0")           # True（未指定地址）

# 主机名验证
is_host_valid("example.com")    # True
is_host_valid("192.168.1.1")    # True
is_host_valid("a" * 256)        # False（超过 255 字符）
```

`is_ip_address` 尝试 `ip_address(address)`，成功返回 True，`ValueError` 返回 False（事实 #495）。`is_host_valid` 拒绝超过 255 字符和纯数字点号格式，使用正则验证域名标签（事实 #497）。`helpers/network.py` 在 util 之上提供 `is_internal_request(request)` 和 `get_supervisor_network_url(hass)` 等框架级网络辅助（事实 #277-278）。

## 其他实用模块

### percentage：百分比转换

`util/percentage.py`（事实 #515-520）在百分比和数值范围之间转换：

```python
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
    ranged_value_to_percentage,
    percentage_to_ranged_value,
)

# 有序列表项 ↔ 百分比（如风扇速度档位）
pct = ordered_list_item_to_percentage(["low", "medium", "high"], "medium")  # → 66
item = percentage_to_ordered_list_item(["low", "medium", "high"], 33)       # → "low"

# 数值范围 ↔ 百分比（如亮度 1-255）
pct = ranged_value_to_percentage((1, 255), 128)   # → 50
val = percentage_to_ranged_value((1, 255), 50)     # → 127.5
```

### ssl：SSL/TLS 上下文

`util/ssl.py`（事实 #469-485）提供安全的 SSL 上下文创建：

```python
from homeassistant.util.ssl import (
    client_context, create_client_context, get_default_context,
    SSLCipherList, SSL_ALPN_HTTP11, SSL_ALPN_HTTP11_HTTP2,
    server_context_modern, server_context_intermediate,
)

# 缓存的客户端 SSL 上下文
ctx = client_context(SSLCipherList.MODERN, SSL_ALPN_HTTP11_HTTP2)
```

模块在加载时预热所有密码套件和 ALPN 组合的缓存（4×3=12 个上下文，事实 #484），避免事件循环中的阻塞 I/O。使用 `certifi.where()` 获取 CA 证书包（事实 #485）。

### location：位置检测

`util/location.py`（事实 #506-514）提供基于 IP 的位置检测和地理距离计算：

- `LocationInfo` NamedTuple 包含 IP、国家代码、城市、时区、经纬度等（事实 #510）
- `async_detect_location_info(session)` 调用 whoami 服务检测位置（事实 #511）
- `distance(lat1, lon1, lat2, lon2)` 使用 Vincenty 公式计算椭球面距离（事实 #512），带 `lru_cache`
- Vincenty 反解法迭代最多 200 次，收敛阈值 1e-12（事实 #509, #513）

### decorator：注册表装饰器

`util/decorator.py` 的 `Registry` 类（事实 #522）继承字典，提供 `register(name)` 装饰器方法，用于插件注册模式：

```python
from homeassistant.util.decorator import Registry

handlers = Registry()

@handlers.register("light")
def handle_light(...):
    ...
```

## thread：线程工具（`util/thread.py`）

`util/thread.py` 提供线程安全关闭和异常注入工具（事实 #395-402）：

- `deadlock_safe_shutdown()`：安全关闭非守护线程，对每个线程分配超时避免永久死锁（事实 #397）
- `async_raise(tid, exctype)`：通过 `ctypes.pythonapi.PyThreadState_SetAsyncExc` 在指定线程异步抛出异常（事实 #399）
- `ThreadWithException`：支持从其他线程在自身上下文中抛出异常的线程类（事实 #401）

## logging：日志工具（`util/logging.py`）

`util/logging.py` 提供高性能异步日志（事实 #403-414）：

- `HomeAssistantQueueHandler` 在另一个线程处理日志 I/O，避免阻塞事件循环（事实 #408）
- `HomeAssistantQueueListener` 监控高频日志模块，单模块超过 200 条/5分钟则跳过后续日志（事实 #404-406）
- `catch_log_exception` 装饰函数/协程以捕获并记录异常（事实 #411）
- `async_create_catching_coro` 包装协程，异常记录时包含包装位置的堆栈跟踪（事实 #413）

## 延伸阅读

- [Helpers 工具库](/concepts/12-helpers-library.md)
- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [启动流程](/concepts/04-bootstrap-lifecycle.md)
- [实体模型](/concepts/09-entity-model.md)

## 相关概念

- [Helpers 工具库](/concepts/12-helpers-library.md) — 在 util 无状态工具之上构建的有状态框架级抽象
- [配置系统](/concepts/05-configuration.md) — yaml 加载、!secret 标签、JSON 序列化等 util 模块为配置系统提供底层支持
- [集成架构](/concepts/14-component-architecture.md) — 集成开发广泛使用 dt、json、async_ 等 util 工具处理时间、序列化与并发
