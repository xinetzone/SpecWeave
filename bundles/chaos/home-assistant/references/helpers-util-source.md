---
type: Reference
title: Home Assistant Helpers 与 Util 源码
description: Home Assistant 辅助工具库源码登记，包含实体基类、设备注册表、模板引擎、存储系统、事件辅助、配置验证、选择器与通用工具
tags: [home-assistant, smart-home, helpers, util, source, reference, python]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-helpers
    resource: "/references/facts-helpers.md"
    title: Home Assistant Helpers 与 Util 事实清单
---

# Home Assistant Helpers 与 Util 源码

## 概述

Home Assistant 的辅助代码分为两个层次：`helpers/` 面向组件开发者，提供实体抽象、注册表、模板引擎等高级基础设施；`util/` 提供底层通用工具函数（时间、JSON、YAML、异步原语等），不依赖 HA 运行时。

| 目录 | 定位 | 依赖方向 |
|------|------|---------|
| `homeassistant/helpers/` | 组件内部辅助方法，依赖 `HomeAssistant` 实例 | 可引用 core.py |
| `homeassistant/util/` | 通用工具函数，无 HA 运行时依赖 | 不引用 core.py |

## helpers/ 核心文件

路径：`homeassistant/helpers/`

### 实体与设备

| 文件 | 职责 |
|------|------|
| `entity.py` | `Entity` 基类、`EntityDescription`、`EntityCategory`、实体生命周期 |
| `entity_component.py` | `EntityComponent`：管理单一平台下所有实体的添加/移除/轮询 |
| `entity_platform.py` | `EntityPlatform`：实体平台，连接集成与实体 |
| `device.py` | `DeviceInfo` TypedDict、设备 ID 解析、设备-实体关联查询 |
| `entity_registry.py` | `EntityRegistry`：实体注册表，继承 `BaseRegistry` |
| `device_registry.py` | `DeviceRegistry`：设备注册表，继承 `BaseRegistry` |
| `area_registry.py` | `AreaRegistry`：区域注册表 |
| `restore_state.py` | `RestoreEntity`：状态恢复混入，实体重启后恢复上次状态 |
| `update_coordinator.py` | `DataUpdateCoordinator`：数据轮询协调器，通用数据获取模式 |

### 模板与脚本

| 文件 | 职责 |
|------|------|
| `template/` | Jinja2 模板引擎封装包（`__init__.py` 为入口） |
| `script.py` | `Script` 类：脚本执行引擎，支持顺序/并行/条件/等待/重复 |
| `condition.py` | 条件验证工具集（数值状态、模板条件、时间条件等） |
| `trigger.py` | 触发器平台基础设施 |

### 事件与服务

| 文件 | 职责 |
|------|------|
| `event.py` | 事件监听辅助：`async_track_state_change`、`async_track_time_interval`、`TrackTemplate` |
| `service.py` | 服务调用工具：`async_call_from_config`、`entity_service` 装饰器 |
| `start.py` | 启动任务辅助：`async_at_started`、`async_at_start` |
| `reload.py` | 平台重载：`async_reload_integration_platforms` |
| `signal.py` | 系统信号处理：SIGTERM/SIGINT/SIGHUP |

### 配置与存储

| 文件 | 职责 |
|------|------|
| `config_validation.py` | 基于 voluptuous 的配置验证器库（`cv` 别名） |
| `storage.py` | `Store` 类：JSON 文件持久化，延迟写入、版本迁移 |
| `selector.py` | 配置 UI 选择器体系（`EntitySelector`、`DeviceSelector` 等 30+ 种） |
| `debounce.py` | `Debouncer`：防抖调用协程函数 |
| `instance_id.py` | 实例 ID 管理 |

### 其他辅助

| 文件 | 职责 |
|------|------|
| `__init__.py` | 通用辅助：`slugify`、`convert`、`Throttle`、`repr_helper`、`snakecase` |
| `intent.py` | 意图处理框架：`IntentHandler`、`intent_handler` 装饰器、内置意图 |
| `llm.py` | LLM 工具框架：`API`、`Tool` 抽象基类 |
| `json.py` | HA 对象 JSON 序列化：`JSONEncoder`、`json_bytes` |
| `network.py` | 网络辅助：IP 判定、内部请求检测 |
| `frame.py` | 调用栈帧分析：`get_integration_frame`、`report` |
| `group.py` | 实体组：`GenericGroup`、`async_expand_entity_ids` |
| `sensor.py` | `SensorEntity` 基类、`SensorDeviceClass`、`SensorStateClass` |
| `icon.py` | 图标辅助：电池/信号/功率等级图标 |
| `typing.py` | 类型别名：`ConfigType`、`StateType`、`TemplateVarsType` |
| `state.py` | 状态重现：`async_reproduce_state`、`state_as_number` |
| `location.py` | 位置检测：`async_detect_location_info` |
| `httpx_client.py` | httpx 异步客户端封装 |
| `aiohttp_client.py` | aiohttp 客户端封装 |
| `singleton.py` | 单例装饰器 |
| `ratelimit.py` | 速率限制 |
| `redact.py` | 敏感数据脱敏 |
| `trace.py` | 执行追踪 |
| `target.py` | 目标解析（entity_id/device_id/area_id） |
| `sun.py` | 太阳事件计算 |
| `discovery.py` | 设备发现 |
| `http.py` | HTTP 辅助 |
| `hassio.py` | Hass.io 集成辅助 |
| `importlib.py` | 模块导入工具 |
| `recorder.py` | Recorder 辅助 |

## util/ 核心文件

路径：`homeassistant/util/`

### 核心工具

| 文件 | 职责 |
|------|------|
| `__init__.py` | 与 helpers 共享的基础函数：`slugify`、`convert`、`Throttle`、`raise_if_invalid_filename` |
| `dt.py` | 日期时间处理：`utcnow`、`parse_datetime`、`parse_duration`、`as_timestamp`、时区管理 |
| `json.py` | JSON 序列化（底层 orjson）：`json_loads`、`load_json`、`SerializationError` |
| `yaml/` | YAML 加载器包：`load_yaml`、`parse_yaml`、`Secrets`、`!secret` 处理 |
| `async_.py` | asyncio 工具：`create_eager_task`、`run_callback_threadsafe`、`gather_with_limited_concurrency` |
| `thread.py` | 线程工具：`deadlock_safe_shutdown`、`async_raise` |
| `executor.py` | `InterruptibleThreadPoolExecutor`：可中断线程池 |
| `timeout.py` | 超时管理器：`TimeoutManager` |
| `hass_dict.py` | `HassDict`：类型安全字典，配合 `HassKey` |
| `ulid.py` | ULID 生成：`ulid_now`、`ulid_at_time` |
| `location.py` | 地理位置计算：距离、经纬度验证 |
| `network.py` | 网络工具：IP 地址判定 |
| `unit_system.py` | 单位系统：公制/英制转换 |
| `color.py` | 颜色空间转换：RGB/HS/XY/色温 |
| `temperature.py` | 温度转换 |
| `logging.py` | 日志工具 |
| `package.py` | 包安装检测 |
| `file.py` | 文件操作 |
| `decorator.py` | 装饰器工具 |
| `enum.py` | 枚举工具 |
| `ssl.py` | SSL 上下文 |
| `uuid.py` | UUID 生成 |
| `percentage.py` | 百分比转换 |
| `scaling.py` | 数据缩放 |
| `variance.py` | 方差计算 |
| `aiohttp.py` | aiohttp 工具 |
| `collection.py` | 集合工具 |
| `enum.py` | 枚举辅助 |
| `language.py` | 语言代码 |
| `process.py` | 进程管理 |
| `resource.py` | 系统资源 |
| `signal_type.py` | 信号类型 |
| `system_info.py` | 系统信息 |
| `loop.py` | 事件循环工具 |
| `event_type.py` | 事件类型 |

## 关键类与函数

### Entity 基类体系（helpers/entity.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `Entity` | 类 | 所有实体抽象基类，30+ 标准属性 |
| `EntityDescription` | frozen dataclass | 实体元数据描述，字段含 key/device_class/entity_category/icon/name 等 |
| `EntityCategory` | StrEnum | `CONFIG`/`DIAGNOSTIC` 两种实体分类 |
| `ToggleEntity` | 类 | 可开关实体基类，添加 `is_on`/`async_turn_on`/`async_turn_off`/`async_toggle` |
| `RestoreEntity` | 混入 | 状态恢复能力 |
| `EntityPlatformState` | Enum | 实体平台状态 |
| `Entity.async_added_to_hass` | 方法 | 实体添加时生命周期钩子 |
| `Entity.async_will_remove_from_hass` | 方法 | 实体移除前生命周期钩子 |
| `Entity.async_update_ha_state` | 方法 | 触发状态更新写入状态机 |
| `Entity.schedule_update_ha_state` | 方法 | 调度状态更新到事件循环 |
| `Entity.async_on_remove` | 方法 | 注册实体移除时清理回调 |

### DeviceInfo 与注册表（helpers/device.py, helpers/registry.py）

| 名称 | 类型 | 文件 | 说明 |
|------|------|------|------|
| `DeviceInfo` | TypedDict | device.py | 设备信息：identifiers/connections/manufacturer/model 等 |
| `DeviceConnection` | 类型别名 | device.py | `(connection_type, identifier)` 元组 |
| `DeviceIdentifier` | 类型别名 | device.py | `(integration_domain, unique_id)` 元组 |
| `BaseRegistry` | 抽象类 | registry.py | 注册表基类，Store 持久化、延迟写入 |
| `BaseRegistryItems` | 泛型类 | registry.py | 注册表条目集合，字典+反向索引 |
| `EntityRegistry` | 类 | entity_registry.py | 实体注册表 |
| `DeviceRegistry` | 类 | device_registry.py | 设备注册表 |
| `AreaRegistry` | 类 | area_registry.py | 区域注册表 |
| `async_entries_for_config_entry` | 协程 | device.py | 按配置条目查询设备 |
| `async_device_info_to_dr_device_info` | 协程 | device.py | DeviceInfo 转换为注册表格式 |

### 模板引擎（helpers/template/）

| 名称 | 类型 | 说明 |
|------|------|------|
| `Template` | 类 | Jinja2 模板封装，`async_render`/`render`/`ensure_valid` |
| `TemplateState` | 类 | 模板中的实体状态访问对象 |
| `RenderInfo` | 类 | 跟踪模板渲染访问的实体和时间信息 |
| `result_as_boolean` | 函数 | 模板结果转布尔值 |
| `TEMPLATE_PARALLEL_UPDATES` | 常量 | 模板并发更新数 |

### 存储（helpers/storage.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `Store` | 类 | JSON 文件持久化核心类 |
| `Store.async_load` | 协程 | 从磁盘加载数据 |
| `Store.async_save` | 协程 | 保存数据（延迟写入合并） |
| `Store.async_remove` | 协程 | 删除存储文件 |
| `Store.async_delay_save` | 协程 | 延迟保存，合并时间窗口内多次请求 |
| `Store.async_migrate` | 方法 | 版本迁移（子类实现） |

### 事件辅助（helpers/event.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `async_track_state_change` | 协程 | 跟踪实体状态变更（带 from/to 过滤） |
| `async_track_state_change_event` | 协程 | 跟踪状态变更事件（接收完整 Event） |
| `async_track_time_interval` | 函数 | 固定时间间隔回调 |
| `async_call_later` | 函数 | 延迟回调 |
| `async_track_point_in_time` | 函数 | 指定时间点触发 |
| `async_track_sunrise`/`async_track_sunset` | 函数 | 日出/日落触发 |
| `TrackTemplate` | 类 | 模板结果变更跟踪 |
| `async_track_template` | 协程 | 跟踪模板布尔结果变化 |

### 配置验证（helpers/config_validation.py，别名 cv）

| 验证器 | 说明 |
|--------|------|
| `boolean` | 转换多种布尔表示为 Python bool |
| `entity_id`/`entity_ids` | 实体 ID 格式验证 |
| `template`/`dynamic_template` | 模板验证 |
| `positive_int`/`positive_float` | 正整数/正浮点数 |
| `latitude`/`longitude` | 经纬度范围验证 |
| `port` | 端口号 1-65535 |
| `url` | URL 格式验证 |
| `time_period_str`/`time_period_seconds` | 时间周期解析 |
| `icon` | 图标格式 `prefix:name` |
| `ensure_list`/`ensure_list_csv` | 列表包装 |
| `multi_select` | 多 schema 选择 |
| `matches_regex`/`is_regex` | 正则验证 |
| `service_target` | 服务目标验证 |
| `PLATFORM_SCHEMA` | 平台配置基础 schema |
| `PLATFORM_SCHEMA_BASE` | 平台配置基础 schema（扩展版） |

### 选择器（helpers/selector.py）

| 选择器类 | 说明 |
|---------|------|
| `Selector` | 所有选择器基类 |
| `EntitySelector` | 实体选择器（支持 domain/device_class 过滤） |
| `DeviceSelector` | 设备选择器 |
| `AreaSelector` | 区域选择器 |
| `TextSelector` | 文本选择器（multiline/type） |
| `NumberSelector` | 数字选择器（min/max/step/mode） |
| `SelectSelector` | 下拉选择器 |
| `BooleanSelector` | 布尔选择器 |
| `ColorSelector` | 颜色选择器 |
| `TimeSelector`/`DateSelector`/`DateTimeSelector` | 时间日期选择器 |
| `DurationSelector` | 时长选择器 |
| `TargetSelector` | 目标选择器（实体/设备/区域） |
| `TemplateSelector` | 模板选择器 |
| `ActionSelector`/`ConditionSelector`/`TriggerSelector` | 自动化元素选择器 |
| `CategorySelector` | 分类选择器 |
| `FileSelector`/`IconSelector`/`ThemeSelector`/`MediaSelector` | 其他选择器 |

### 通用工具（helpers/__init__.py, util/__init__.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `slugify` | 函数 | 文本转 slug，空文本返回 `"unknown"` |
| `convert[_T, _U]` | 泛型函数 | 安全类型转换，失败返回默认值 |
| `ensure_unique_string` | 函数 | 生成唯一字符串，冲突追加 `_2`/`_3` |
| `get_random_string` | 函数 | 密码学安全随机字符串 |
| `snakecase` | 函数 | 驼峰转蛇形 |
| `Throttle` | 类 | 方法节流装饰器，`min_time` 间隔内返回 None |
| `repr_helper` | 函数 | 对象的可读表示 |
| `raise_if_invalid_filename` | 函数 | 文件名安全校验 |
| `raise_if_invalid_path` | 函数 | 路径安全校验 |

### 日期时间（util/dt.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `utcnow` | partial | 当前 UTC 时间 |
| `now` | 函数 | 指定时区当前时间 |
| `as_utc` | 函数 | 转 UTC |
| `as_local` | 函数 | 转本地时区 |
| `as_timestamp` | 函数 | datetime 转 Unix 时间戳 |
| `parse_datetime` | 函数 | 解析 ISO 8601 日期时间（ciso8601 快速路径） |
| `parse_date` | 函数 | 解析 `YYYY-MM-DD` |
| `parse_duration` | 函数 | 解析多种持续时间格式 |
| `parse_time` | 函数 | 解析 `HH:MM:SS` |
| `get_time_zone`/`async_get_time_zone` | 函数 | 同步/异步获取 ZoneInfo |
| `get_age`/`get_time_remaining` | 函数 | 人类可读的时间差 |
| `DEFAULT_TIME_ZONE` | 变量 | 默认时区（初始 UTC） |

### JSON 与 YAML（util/json.py, util/yaml/）

| 名称 | 类型 | 说明 |
|------|------|------|
| `json_loads` | 函数 | JSON 解析（orjson） |
| `load_json` | 函数 | 从文件加载 JSON |
| `load_json_array`/`load_json_object` | 函数 | 加载并确保数组/对象类型 |
| `json_bytes` | 函数 | 序列化为 JSON 字节串（helpers/json.py） |
| `SerializationError` | 异常 | JSON 序列化失败 |
| `load_yaml` | 函数 | 加载 YAML 文件 |
| `load_yaml_dict` | 函数 | 加载 YAML 并确保顶层为字典 |
| `parse_yaml` | 函数 | 解析 YAML 字符串 |
| `Secrets` | 类 | `!secret` 引用管理 |
| `YamlTypeError` | 异常 | YAML 顶层非字典 |

### 异步与线程（util/async_.py, util/thread.py, util/executor.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `create_eager_task` | 函数 | 创建立即调度的 asyncio Task |
| `run_callback_threadsafe` | 函数 | 线程安全提交回调到事件循环 |
| `gather_with_limited_concurrency` | 协程 | 带并发限制的 gather |
| `shutdown_run_callback_threadsafe` | 函数 | 设置关闭标记 |
| `deadlock_safe_shutdown` | 函数 | 安全关闭非守护线程 |
| `InterruptibleThreadPoolExecutor` | 类 | 可中断线程池执行器 |

### Sensor 辅助（helpers/sensor.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `SensorEntity` | 类 | 传感器实体基类 |
| `SensorEntityDescription` | dataclass | 传感器实体描述 |
| `SensorDeviceClass` | StrEnum | 60+ 设备类（TEMPERATURE/HUMIDITY/POWER/ENERGY 等） |
| `SensorStateClass` | StrEnum | MEASUREMENT/TOTAL/TOTAL_INCREASING/MEASUREMENT_ANGLE |
| `UNIT_CONVERTERS` | 字典 | 设备类到单位转换器映射 |

### 脚本与自动化（helpers/script.py, helpers/condition.py, helpers/trigger.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `Script` | 类 | 脚本执行引擎 |
| `ScriptMode` | Enum | PARALLEL/QUEUED/RESTART/SINGLE |
| `Script.async_run` | 协程 | 异步运行脚本 |
| `async_validate_condition_config` | 协程 | 条件配置验证 |
| `async_initialize_triggers` | 协程 | 初始化触发器 |
| `Debouncer` | 类 | 防抖器（helpers/debounce.py） |

### 意图与 LLM（helpers/intent.py, helpers/llm.py）

| 名称 | 类型 | 说明 |
|------|------|------|
| `IntentHandler` | 抽象类 | 意图处理器基类 |
| `intent_handler` | 装饰器 | 注册意图处理器 |
| `Intent` | 类 | 意图请求对象 |
| `IntentResponse` | 类 | 意图响应对象 |
| `API` | 类 | LLM API 实例 |
| `Tool` | 抽象类 | LLM 工具基类 |
| `async_register_tool`/`async_register_api` | 函数 | 注册工具和 API |
