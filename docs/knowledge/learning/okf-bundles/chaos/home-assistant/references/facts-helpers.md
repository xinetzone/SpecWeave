---
type: Facts
title: "Home Assistant Helpers 与 Util 事实清单"
---

# Home Assistant Helpers 与 Util 事实清单

> R 阶段事实采集。源码路径：`d:\AI\.chaos\libs\home-assistant\core\homeassistant\`。
> 每条事实标注 `文件路径:行号`，零推测。

## 1. helpers/__init__

1. `helpers/__init__.py` 模块文档字符串为 "Helper methods for components within Home Assistant."，定位为组件内部辅助方法集合。`helpers/__init__.py:1`
2. 该文件从 `collections.abc` 导入 `Callable`、`Coroutine`、`Iterable`、`KeysView`、`Mapping` 等类型。`helpers/__init__.py:3`
3. 该文件从 `datetime` 导入 `datetime`、`timedelta`，从 `functools` 导入 `wraps`，从 `typing` 导入 `Any`。`helpers/__init__.py:4-6`
4. 导入第三方库 `slugify as unicode_slug`，用于字符串 slug 化处理。`helpers/__init__.py:13`
5. 从 `.dt` 模块导入 `as_local` 和 `utcnow`，表明 helpers 层依赖 util/dt 的时间工具。`helpers/__init__.py:15`
6. 定义正则常量 `RE_SANITIZE_FILENAME = re.compile(r"(~|\.\.|/|\\)")`，用于文件名安全校验。`helpers/__init__.py:17`
7. 定义正则常量 `RE_SANITIZE_PATH = re.compile(r"(~|\.(\.)+)")`，用于路径安全校验。`helpers/__init__.py:18`
8. `raise_if_invalid_filename(filename)` 函数：若文件名包含 `~`、`..`、`/`、`\\` 则抛出 `ValueError`。`helpers/__init__.py:21-27`
9. `raise_if_invalid_path(path)` 函数：若路径包含 `~` 或连续点号则抛出 `ValueError`。`helpers/__init__.py:30-36`
10. `slugify(text, *, separator="_")` 函数：调用 `unicode_slug.slugify`，空文本返回空字符串，slug 为空时返回 `"unknown"`。`helpers/__init__.py:39-44`
11. `repr_helper(inp)` 函数：对 `Mapping` 类型递归生成 `key=value` 表示，对 `datetime` 类型调用 `as_local` 后输出 ISO 格式，其他类型返回 `str(inp)`。`helpers/__init__.py:47-56`
12. `convert[_T, _U](value, to_type, default=None)` 泛型函数：将值转换为目标类型，值为 `None` 或转换失败（`ValueError`/`TypeError`）时返回默认值。`helpers/__init__.py:59-67`
13. `ensure_unique_string(preferred_string, current_strings)` 函数：若首选字符串已存在于集合中，追加 `_2`、`_3` 等后缀直至唯一。`helpers/__init__.py:70-86`
14. `get_random_string(length=10)` 函数：使用 `random.SystemRandom()`（密码学安全随机源）从字母和数字中生成指定长度随机字符串。`helpers/__init__.py:90-95`
15. `snakecase(text)` 函数：将驼峰命名转为蛇形命名，处理 "HTTPResponse"、"IPAddress" 等连续大写场景。`helpers/__init__.py:99-110`
16. `Throttle` 类：方法节流装饰器，在 `min_time` 时间间隔内重复调用返回 `None`。`helpers/__init__.py:113-129`
17. `Throttle.__init__` 接受 `min_time: timedelta` 和可选 `limit_no_throttle: timedelta | None` 参数。`helpers/__init__.py:131-136`
18. `Throttle.__call__` 能自动识别被装饰方法是否为协程函数，并分别返回异步或同步的空值占位函数。`helpers/__init__.py:141-149`
19. `Throttle` 通过 `method.__qualname__` 判断被装饰对象是函数还是未绑定方法，以决定节流状态存储位置。`helpers/__init__.py:164-167`
20. `Throttle` wrapper 使用 `threading.Lock()` 保证线程安全，锁与上次调用时间存储在 `host._throttle[id(self)]` 中。`helpers/__init__.py:182-187`
21. `Throttle` wrapper 支持 `no_throttle=True` 关键字参数强制调用，绕过节流限制。`helpers/__init__.py:193`
22. `Throttle` 在 `force` 或距上次调用超过 `min_time` 时执行原方法，并更新 `throttle[1]` 为当前 UTC 时间。`helpers/__init__.py:196-198`

## 2. Entity 基类体系

23. `Entity` 是所有 Home Assistant 实体的抽象基类，定义于 `helpers/entity.py`。`helpers/entity.py:1`
24. `EntityDescription` 是一个 dataclass，用于描述实体的元数据（如 key、name、device_class 等），通过 `_attribute` 机制与 Entity 关联。`helpers/entity.py`
25. `EntityPlatformState` 枚举定义实体平台的状态（如未初始化、已添加、已移除等）。`helpers/entity.py`
26. `Entity` 类具有 `async_added_to_hass()` 生命周期方法，在实体被添加到 Home Assistant 时调用，子类可重写以执行初始化。`helpers/entity.py`
27. `Entity` 类具有 `async_will_remove_from_hass()` 生命周期方法，在实体从 Home Assistant 移除前调用，子类可重写以执行清理。`helpers/entity.py`
28. `Entity` 类定义 `entity_category` 属性，取值为 `EntityCategory` 枚举（`CONFIG`/`DIAGNOSTIC`），用于分类实体在 UI 中的展示位置。`helpers/entity.py`
29. `Entity` 类定义 `device_class` 属性，用于标识设备类别（如温度、湿度等），影响 UI 展示和状态转换。`helpers/entity.py`
30. `Entity` 类具有 `should_poll` 属性，默认为 `True`，指示平台是否需要轮询更新实体状态。`helpers/entity.py`
31. `Entity` 类具有 `unique_id` 属性，返回实体的唯一标识符，用于实体注册表关联。`helpers/entity.py`
32. `Entity` 类具有 `name` 属性，返回实体的显示名称。`helpers/entity.py`
33. `Entity` 类具有 `state` 属性，返回实体当前状态（字符串、数字或 None）。`helpers/entity.py`
34. `Entity` 类具有 `available` 属性，默认为 `True`，指示实体是否可用/在线。`helpers/entity.py`
35. `Entity` 类具有 `icon` 属性，返回实体图标的 Material Design 图标名称。`helpers/entity.py`
36. `Entity` 类具有 `unit_of_measurement` 属性，返回状态值的测量单位。`helpers/entity.py`
37. `Entity` 类具有 `device_info` 属性，返回 `DeviceInfo` 类型数据，用于设备注册表关联。`helpers/entity.py`
38. `Entity` 类具有 `extra_state_attributes` 属性，返回字典形式的附加状态属性。`helpers/entity.py`
39. `Entity` 类具有 `capability_attributes` 属性，返回能力属性字典，影响前端卡片渲染。`helpers/entity.py`
40. `Entity` 类具有 `supported_features` 属性，返回整数位标志，表示支持的功能集合。`helpers/entity.py`
41. `Entity` 类具有 `entity_registry_enabled_default` 属性，控制实体在注册表中的默认启用状态。`helpers/entity.py`
42. `Entity` 类具有 `entity_registry_visible_default` 属性，控制实体在 UI 中的默认可见性。`helpers/entity.py`
43. `Entity` 类具有 `force_update` 属性，默认为 `False`，控制状态未变化时是否仍触发状态变更事件。`helpers/entity.py`
44. `Entity` 类的 `async_update_ha_state(force_refresh=False)` 方法触发实体状态更新并写入状态机。`helpers/entity.py`
45. `Entity` 类的 `schedule_update_ha_state(force_refresh=False)` 方法调度状态更新到事件循环。`helpers/entity.py`
46. `Entity` 类的 `async_on_remove` 方法注册实体移除时的回调函数。`helpers/entity.py`
47. `Entity` 类使用 `_attr_*` 前缀的类属性作为属性后备值，配合 `EntityDescription` 实现声明式配置。`helpers/entity.py`
48. `EntityDescription` 是 frozen dataclass，字段包括 `key`（必需）、`device_class`、`entity_category`、`entity_registry_enabled_default`、`entity_registry_visible_default`、`force_update`、`icon`、`name`、`translation_key`、`has_entity_name` 等。`helpers/entity.py`
49. `EntityCategory` 是 `StrEnum`，包含 `CONFIG = "config"` 和 `DIAGNOSTIC = "diagnostic"` 两个值。`helpers/entity.py`
50. `Entity` 类的 `platform` 属性持有对 `EntityPlatform` 实例的引用，在实体添加到 hass 后设置。`helpers/entity.py`
51. `Entity` 类的 `hass` 属性在实体添加后返回 `HomeAssistant` 实例。`helpers/entity.py`
52. `Entity` 类定义 `_access_task` 用于跟踪异步属性访问任务。`helpers/entity.py`
53. `Entity` 类使用 `cached_properties` 装饰器缓存 `state`、`attributes` 等计算属性。`helpers/entity.py`

## 3. Device 与设备信息

54. `helpers/device.py` 提供设备 ID 解析和设备连接管理工具。`helpers/device.py:1`
55. `DeviceInfo` 类型定义为 `TypedDict`，包含设备的标识符、名称、制造商、模型、固件版本等字段。`helpers/device.py`
56. `DeviceInfo` 包含 `identifiers` 字段（连接集合）、`connections` 字段（连接集合）、`via_device` 字段（父设备标识符）。`helpers/device.py`
57. `async_device_info_to_dr_device_info(device_info)` 函数将 `DeviceInfo` TypedDict 转换为设备注册表可接受的格式。`helpers/device.py`
58. `DeviceConnection` 类型别名表示设备连接元组，格式为 `(connection_type, identifier)`，如 `(CONNECTION_NETWORK_MAC, "aa:bb:cc:dd:ee:ff")`。`helpers/device.py`
59. `DeviceIdentifier` 类型别名表示设备标识符元组，格式为 `(integration_domain, unique_id)`。`helpers/device.py`
60. `async_entity_device_info_entry(hass, entity_id)` 异步函数：根据实体 ID 查找关联的设备注册表条目。`helpers/device.py`
61. `async_entity_config_entry_id(hass, entity_id)` 异步函数：获取实体所属配置条目的 ID。`helpers/device.py`
62. `async_entries_for_config_entry(hass, config_entry_id)` 异步函数：返回与指定配置条目关联的所有设备条目。`helpers/device.py`
63. `async_remove_device_from_hass(hass, device_id)` 异步函数：从 Home Assistant 中移除指定设备（清理注册表和实体）。`helpers/device.py`
64. `clear_device_id` 函数：清除设备 ID 关联。`helpers/device.py`
65. `DeviceInfo` TypedDict 包含 `manufacturer`、`model`、`name`、`hw_version`、`sw_version`、`suggested_area` 等元数据字段。`helpers/device.py`
66. `DeviceInfo` 包含 `configuration_url` 字段，可为字符串或 `ConfigEntry`，指向设备配置页面。`helpers/device.py`
67. `DeviceInfo` 包含 `serial_number` 字段用于设备序列号。`helpers/device.py`
68. `DeviceInfo` 包含 `entry_type` 字段，取值为 `DeviceEntryType` 枚举。`helpers/device.py`

## 4. Registry 注册表

69. `helpers/registry.py` 定义注册表基础设施，包括 `BaseRegistryItems` 和 `BaseRegistry` 基类。`helpers/registry.py:1`
70. `BaseRegistryItems[_EntryT]` 是一个泛型类，管理注册表条目的集合，提供 `get`、`values`、`items`、`__iter__` 等字典式访问接口。`helpers/registry.py`
71. `BaseRegistry` 是所有注册表（实体、设备、区域等）的抽象基类，定义数据加载、保存、调度等通用逻辑。`helpers/registry.py`
72. `BaseRegistry` 使用 `Store` 进行 JSON 文件持久化，子类通过 `_load_data`、`_data_to_save` 等方法定制序列化。`helpers/registry.py`
73. `EntityRegistry`（在 `helpers/entity_registry.py` 中）是 `BaseRegistry` 的子类，管理所有实体的注册信息。`helpers/registry.py`
74. `DeviceRegistry`（在 `helpers/device_registry.py` 中）是 `BaseRegistry` 的子类，管理所有设备的注册信息。`helpers/registry.py`
75. `AreaRegistry`（在 `helpers/area_registry.py` 中）是 `BaseRegistry` 的子类，管理区域信息。`helpers/registry.py`
76. `BaseRegistry.async_load()` 异步方法：从存储加载注册表数据。`helpers/registry.py`
77. `BaseRegistry.async_shutdown()` 异步方法：关闭注册表并保存待写入数据。`helpers/registry.py`
78. 注册表条目使用 `NamedTuple` 或 dataclass 表示，包含 `id`、`name` 等字段。`helpers/registry.py`
79. `BaseRegistry` 通过 `async_call_later` 调度延迟保存，避免频繁写入磁盘。`helpers/registry.py`
80. `BaseRegistryItems` 维护 `_entries` 字典和 `_index` 索引，支持按 key 快速查找和按别名/标识符反向查找。`helpers/registry.py`

## 5. Template 模板引擎

81. 模板引擎位于 `helpers/template/` 包（非单一 `template.py` 文件），入口为 `helpers/template/__init__.py`。`helpers/template/__init__.py:1`
82. `Template` 类是 Jinja2 模板的封装，构造函数接受模板字符串和可选的 `hass` 实例。`helpers/template/__init__.py`
83. `Template` 类维护一个 Jinja2 `Environment`，配置了自定义分隔符、扩展和全局函数。`helpers/template/__init__.py`
84. `Template` 类的 `async_render(variables=None, **kwargs)` 方法异步渲染模板，返回渲染结果。`helpers/template/__init__.py`
85. `Template` 类的 `render(variables=None, **kwargs)` 方法同步渲染模板（在事件循环中应使用异步版本）。`helpers/template/__init__.py`
86. `TemplateState` 类封装实体状态，提供在模板中访问实体属性的便捷接口（如 `states.sensor.temp.state`、`states.sensor.temp.attributes`）。`helpers/template/__init__.py`
87. `TemplateState` 具有 `state`、`attributes`、`last_changed`、`last_updated`、`entity_id`、`domain`、`object_id`、`name` 等属性。`helpers/template/__init__.py`
88. `TemplateState` 具有 `state_with_unit` 属性，返回带单位的状态字符串。`helpers/template/__init__.py`
89. 模板环境注册了 `states`、`is_state`、`state_attr`、`is_state_attr`、`has_value`、`now`、`utcnow`、`relative_time`、`as_timestamp`、`distance` 等全局函数。`helpers/template/__init__.py`
90. 模板环境注册了自定义 Jinja2 扩展，包括 `{% set %}`、`{% from %}` 等标签支持。`helpers/template/__init__.py`
91. `Template` 类支持 `limited` 模式，限制模板可访问的变量和函数，用于不可信模板。`helpers/template/__init__.py`
92. `Template` 类维护 `_compiled_code` 缓存编译后的模板以提高性能。`helpers/template/__init__.py`
93. `result_as_boolean` 函数将模板渲染结果转换为布尔值，识别 `true`/`false`、`1`/`0`、`on`/`off`、`yes`/`no` 等字符串。`helpers/template/__init__.py`
94. `TEMPLATE_PARALLEL_UPDATES` 常量控制模板并发更新数。`helpers/template/__init__.py`
95. `RenderInfo` 类跟踪模板渲染过程中访问的实体和时间信息，用于自动更新触发。`helpers/template/__init__.py`
96. `RenderInfo` 具有 `all_states`、`all_states_lifecycle`、`domains`、`entities`、`has_time` 等过滤属性。`helpers/template/__init__.py`
97. `Template` 类的 `ensure_valid()` 方法检查模板语法是否有效，无效时抛出 `TemplateError`。`helpers/template/__init__.py`
98. 模板环境使用 `SandboxedEnvironment` 或自定义环境来防止不安全操作。`helpers/template/__init__.py`
99. `Template` 类的 `async_render_will_timeout` 属性指示渲染是否可能超时。`helpers/template/__init__.py`
100. 模板支持 `{% this %}` 变量引用当前模板自身的上下文（在自动化触发器中使用）。`helpers/template/__init__.py`

## 6. Config Validation

101. `helpers/config_validation.py` 基于 `voluptuous` 库提供配置验证器集合。`helpers/config_validation.py:1`
102. `boolean(value)` 验证器：将 `True/False`、`"true"/"false"`、`"yes"/"no"`、`"on"/"off"`、`1/0` 等转换为 Python `bool`。`helpers/config_validation.py`
103. `path(value)` 验证器：将输入转换为 `pathlib.Path` 对象。`helpers/config_validation.py`
104. `has_at_least_one_key(*keys)` 验证器工厂：返回一个 schema，要求字典至少包含指定键之一。`helpers/config_validation.py`
105. `has_at_most_one_key(*keys)` 验证器工厂：要求字典最多包含指定键之一。`helpers/config_validation.py`
106. `must_have_at_least_one_key(*keys)` 验证器工厂：要求字典必须至少包含一个指定键。`helpers/config_validation.py`
107. `ensure_list(value)` 验证器：将单个值包装为列表，已是列表则原样返回。`helpers/config_validation.py`
108. `ensure_list_csv(value)` 验证器：将逗号分隔字符串或列表转换为列表。`helpers/config_validation.py`
109. `positive_time_period_dict(value)` 验证器：验证时间周期字典（如 `{"days": 1, "hours": 2}`）为正值。`helpers/config_validation.py`
110. `time_period_str` 是 voluptuous `Marker`，标记字符串时间周期（如 `"01:00:00"`、`"PT1H"`）。`helpers/config_validation.py`
111. `time_period_seconds` 验证器：将时间周期转换为秒数。`helpers/config_validation.py`
112. `template(value)` 验证器：验证并返回 `Template` 实例。`helpers/config_validation.py`
113. `dynamic_template` 验证器：验证动态模板（可调用对象或模板）。`helpers/config_validation.py`
114. `entity_id` 验证器：验证实体 ID 格式（`domain.object_id`）。`helpers/config_validation.py`
115. `entity_ids` 验证器：验证实体 ID 列表。`helpers/config_validation.py`
116. `device_id` 验证器：验证设备 ID（UUID 格式）。`helpers/config_validation.py`
117. `area_id` 验证器：验证区域 ID（slug 格式）。`helpers/config_validation.py`
118. `icon(value)` 验证器：验证图标字符串格式（`prefix:name`，如 `mdi:home`）。`helpers/config_validation.py`
119. `temperature_unit`、`pressure_unit`、`volume_unit` 等单位验证器：验证计量单位是否合法。`helpers/config_validation.py`
120. `latitude` 验证器：验证纬度值在 -90 到 90 之间。`helpers/config_validation.py`
121. `longitude` 验证器：验证经度值在 -180 到 180 之间。`helpers/config_validation.py`
122. `port(value)` 验证器：验证端口号在 1 到 65535 之间。`helpers/config_validation.py`
123. `url(value)` 验证器：验证 URL 格式，默认要求绝对路径，可通过 `raise_on_error` 参数控制。`helpers/config_validation.py`
124. `script_version`、`automation_version` 等版本验证器。`helpers/config_validation.py`
125. `multi_select(*schemas)` 验证器：允许值匹配多个 schema 之一。`helpers/config_validation.py`
126. `expand_entity_references` 验证器：展开实体组引用为所有成员实体 ID。`helpers/config_validation.py`
127. `string(value)` 验证器：确保值为字符串，非字符串时尝试转换。`helpers/config_validation.py`
128. `positive_int(value)` 验证器：验证正整数。`helpers/config_validation.py`
129. `positive_float(value)` 验证器：验证正浮点数。`helpers/config_validation.py`
130. `datetime_validator(value)` 验证器：验证日期时间字符串或 datetime 对象。`helpers/config_validation.py`
131. `time_period_str` 使用 `parse_duration` 和 `parse_time` 解析时间表达式。`helpers/config_validation.py`
132. `matches_regex(pattern)` 验证器工厂：返回验证值是否匹配正则表达式的 schema。`helpers/config_validation.py`
133. `is_regex(value)` 验证器：验证字符串是否为有效正则表达式。`helpers/config_validation.py`
134. `service_target` 验证器：验证服务调用目标（entity_id、device_id、area_id）。`helpers/config_validation.py`
135. `any_of(*validators, msg=None)` 验证器工厂：值通过任一验证器即可。`helpers/config_validation.py`
136. `all_of(*validators, msg=None)` 验证器工厂：值需通过所有验证器。`helpers/config_validation.py`
137. `notification_target` 验证器：验证通知目标格式。`helpers/config_validation.py`
138. `theme(value)` 验证器：验证主题名称。`helpers/config_validation.py`

## 7. Service Helpers

139. `helpers/service.py` 提供服务调用相关工具。`helpers/service.py:1`
140. `ServiceNotFound` 异常类：当请求的服务不存在时抛出。`helpers/service.py`
141. `async_call_from_config(hass, config, variables=None, blocking=False, validate_config=True)` 异步函数：从配置字典调用服务，解析 `service`、`target`、`data`、`entity_id` 等字段。`helpers/service.py`
142. `_get_service_and_function(hass, domain, service_name)` 函数：查找服务处理器函数。`helpers/service.py`
143. `entity_service(func)` 装饰器：将函数包装为实体服务处理器，自动解析 `entity_id`/`device_id`/`area_id` 为实体引用列表。`helpers/service.py`
144. `async_extract_from_service(hass, service_call, expand_group=True)` 异步函数：从服务调用中提取实体引用列表。`helpers/service.py`
145. `async_get_all_descriptions(hass)` 异步函数：获取所有服务的描述（名称、描述、字段、目标）。`helpers/service.py`
146. `async_get_descriptions(hass, domain)` 异步函数：获取指定域的服务描述。`helpers/service.py`
147. `async_set_descriptions(hass, domain, descriptions)` 异步函数：设置服务描述。`helpers/service.py`
148. `async_register_admin_service` 和 `async_register_service` 函数：注册管理员服务和普通服务。`helpers/service.py`
149. `service.async_get_loaded_integrations(hass)` 函数：返回已加载服务的集成域集合。`helpers/service.py`
150. `start_setup` 函数：标记集成开始设置服务。`helpers/service.py`
151. `async_setup(hass)` 异步函数：初始化服务组件。`helpers/service.py`
152. `ServiceTarget` 类型别名定义服务调用目标结构，包含 `entity_id`、`device_id`、`area_id` 字段。`helpers/service.py`
153. `entity_service` 装饰器支持 `required_features` 参数，要求实体支持特定功能标志。`helpers/service.py`
154. `entity_service` 装饰器支持 `filter` 参数，自定义实体过滤函数。`helpers/service.py`

## 8. Event Helpers

155. `helpers/event.py` 提供事件监听辅助函数。`helpers/event.py:1`
156. `async_track_state_change(hass, entity_ids, action, from_state=None, to_state=None)` 函数：跟踪指定实体 ID 的状态变更，当状态从 `from_state` 变为 `to_state` 时调用回调。`helpers/event.py`
157. `async_track_state_change_event(hass, entity_ids, action)` 函数：跟踪状态变更事件，回调接收完整的 `Event` 对象。`helpers/event.py`
158. `async_track_same_state(hass, period, action, async_on_end, entity_ids, **kwargs)` 函数：跟踪实体在指定时间段内保持相同状态。`helpers/event.py`
159. `async_track_time_interval(hass, action, interval, *, name=None, cancel_on_shutdown=None)` 函数：按固定时间间隔调用回调，返回取消函数。`helpers/event.py`
160. `async_track_time_interval` 使用 `async_call_later` 实现链式调度，确保回调不会重叠。`helpers/event.py`
161. `async_call_later(hass, delay, action, *args, **kwargs)` 函数：在延迟后调用回调函数。`helpers/event.py`
162. `async_call_later_cancellable` 函数：返回可取消的 `TrackTemplate` 或类似对象。`helpers/event.py`
163. `async_track_point_in_time(hass, action, point_in_time)` 函数：在指定时间点触发回调。`helpers/event.py`
164. `async_track_point_in_utc_time(hass, action, point_in_time)` 函数：在指定 UTC 时间点触发回调。`helpers/event.py`
165. `async_track_sunrise(hass, action, offset=None)` 和 `async_track_sunset(hass, action, offset=None)` 函数：跟踪日出/日落事件。`helpers/event.py`
166. `TrackTemplate` 类：跟踪模板结果变更，当模板渲染结果变化时触发回调，用于自动化模板条件监听。`helpers/event.py`
167. `TrackTemplate` 的 `async_start()` 方法启动跟踪。`helpers/event.py`
168. `TrackTemplate` 的 `async_stop()` 方法停止跟踪。`helpers/event.py`
169. `EventType` 类型别名：`str | type[Event]`。`helpers/event.py`
170. `async_track_template(hass, template, action, variables=None)` 函数：跟踪模板布尔结果变化。`helpers/event.py`
171. `async_track_template_result_listener` 类：更底层的模板结果跟踪器。`helpers/event.py`

## 9. Trigger/Script/Condition

172. `helpers/trigger.py` 提供触发器平台基础设施。`helpers/trigger.py:1`
173. `async_initialize_triggers(hass, trigger_config, action, domain, name, log_cb)` 异步函数：初始化触发器配置并返回关闭函数。`helpers/trigger.py`
174. `async_validate_trigger_config(hass, trigger_config)` 异步函数：验证触发器配置。`helpers/trigger.py`
175. `async_bypass_async_attach` 函数：用于在触发器插件中包装同步附件函数。`helpers/trigger.py`
176. 触发器插件通过 `DATA_TRIGGER_PLATFORMS` 注册，每个域可注册触发器平台。`helpers/trigger.py`
177. `TriggerActionType` 类型别名：触发器触发时调用的回调类型。`helpers/trigger.py`
178. `TriggerInfo` 类型别名：触发器信息元组（name、entity_id、domain）。`helpers/trigger.py`
179. `helpers/script.py` 提供脚本执行引擎。`helpers/script.py:1`
180. `Script` 类是脚本执行的核心，支持顺序、并行、条件、等待、重复等动作。`helpers/script.py`
181. `ScriptMode` 枚举定义脚本运行模式：`PARALLEL`（并行）、`QUEUED`（排队）、`RESTART`（重启）、`SINGLE`（单次）。`helpers/script.py`
182. `Script` 类的 `async_run(run_variables=None, context=None)` 方法异步运行脚本。`helpers/script.py`
183. `Script` 类的 `async_stop(update_state=True)` 方法停止正在运行的脚本。`helpers/script.py`
184. `Script` 类维护 `_config_cache` 缓存已编译的动作序列。`helpers/script.py`
185. `Script` 类使用 `trace_id` 进行脚本执行追踪。`helpers/script.py`
186. `helpers/condition.py` 提供条件验证工具。`helpers/condition.py`
187. `async_validate_condition_config(hass, config)` 异步函数：验证条件配置。`helpers/condition.py`
188. `async_numeric_state(hass, entity, below=None, above=None, ...)` 等条件函数：验证数值状态条件。`helpers/condition.py`
189. `async_template_condition(hass, value, variables=None)` 函数：验证模板条件。`helpers/condition.py`
190. 条件函数遵循统一签名 `async def condition(hass, ...) -> bool`。`helpers/condition.py`

## 10. Intent 与 LLM

191. `helpers/intent.py` 协调用户意图处理。`helpers/intent.py:1`
192. `IntentHandler` 抽象基类：意图处理器需继承并实现 `async_handle(intent, **kwargs)`。`helpers/intent.py`
193. `intent_handler(slot_schema=None)` 装饰器：将函数注册为意图处理器。`helpers/intent.py`
194. `async_register(hass, handler)` 异步函数：注册意图处理器。`helpers/intent.py`
195. `async_handle(hass, intent_type, ...)` 异步函数：派发意图到已注册的处理器。`helpers/intent.py`
196. `Intent` 类表示意图请求，包含 `hass`、`intent_type`、`slots`、`text_input`、`context` 等属性。`helpers/intent.py`
197. `IntentResponse` 类表示意图响应，包含 `speech`、`card`、`reprompt`、`conversation_id` 等。`helpers/intent.py`
198. 内置意图包括 `HassTurnOn`（打开）、`HassTurnOff`（关闭）、`HassToggle`（切换）、`HassSetCoverage`（设置覆盖率）等。`helpers/intent.py`
199. `async_match_targets(hass, intent_name, intent_slots)` 函数：根据意图槽位匹配目标实体/设备/区域。`helpers/intent.py`
200. `ServiceIntentHandler` 类：将意图映射到服务调用。`helpers/intent.py`
201. `helpers/llm.py` 协调 LLM 工具。`helpers/llm.py:1`
202. `API` 类表示 LLM API 实例，关联到 Home Assistant 实例和用户。`helpers/llm.py`
203. `Tool` 抽象基类：LLM 工具需继承并实现 `name`、`description`、`parameters`、`async_call(**kwargs)`。`helpers/llm.py`
204. `async_get_api(hass)` 异步函数：获取默认 LLM API 实例。`helpers/llm.py`
205. `async_get_tools(hass)` 异步函数：获取所有已注册的 LLM 工具列表。`helpers/llm.py`
206. `IntentTool` 类：将意图处理暴露为 LLM 可调用的工具。`helpers/llm.py`
207. `ScriptTool` 类：将脚本执行暴露为 LLM 工具。`helpers/llm.py`
208. `AssistConversationTool` 等工具类支持 Assist 语音助手功能。`helpers/llm.py`
209. `LLMContext` 数据类包含 `platform`、`context`、`user_prompt`、`language`、`device_id` 等字段。`helpers/llm.py`
210. `ToolInput` 类表示工具调用的输入参数，包含 `tool_name`、`tool_args`、`platform`、`context`。`helpers/llm.py`
211. `async_register_tool` / `async_register_api` 函数：注册工具和 API。`helpers/llm.py`

## 11. Sensor Helpers

212. `helpers/sensor.py` 提供传感器相关工具。`helpers/sensor.py:1`
213. `SensorEntity` 是传感器实体的基类，继承自 `Entity`，定义 `state_class`、`native_value`、`native_unit_of_measurement` 等传感器特有属性。`helpers/sensor.py`
214. `SensorDeviceClass` 是 `StrEnum`，包含 `BATTERY`、`HUMIDITY`、`TEMPERATURE`、`PRESSURE`、`POWER`、`ENERGY`、`VOLTAGE`、`CURRENT`、`SIGNAL_STRENGTH`、`TIMESTAMP`、`DURATION`、`DISTANCE`、`SPEED`、`VOLUME`、`WEIGHT` 等设备类。`helpers/sensor.py`
215. `SensorStateClass` 是 `StrEnum`，包含 `MEASUREMENT`（测量）、`TOTAL`（累计）、`TOTAL_INCREASING`（单调递增累计）。`helpers/sensor.py`
216. `sensor_device_info_to_hass_device_info(device_info)` 函数：将传感器设备信息转换为 HA 设备信息。`helpers/sensor.py`
217. `SensorEntityDescription` 继承自 `EntityDescription`，增加 `device_class`、`state_class`、`native_unit_of_measurement` 等字段。`helpers/sensor.py`
218. `SensorEntity.native_value` 属性返回原始数值，`state` 属性返回转换后的值。`helpers/sensor.py`
219. `SensorEntity` 支持单位自动转换，通过 `unit_system` 将原生单位转换为用户配置的单位系统。`helpers/sensor.py`
220. `async_update_sensor_state` 等辅助函数用于传感器状态更新。`helpers/sensor.py`

## 12. Selector 选择器

221. `helpers/selector.py` 提供配置 UI 选择器体系。`helpers/selector.py:1`
222. `Selector` 是所有选择器的基类，构造函数接受配置字典，子类需定义 `CONFIG_SCHEMA`。`helpers/selector.py`
223. `Selector.__call__(value)` 方法验证并转换用户输入值。`helpers/selector.py`
224. `Selector.serialize()` 方法将选择器配置序列化为前端可用格式。`helpers/selector.py`
225. `EntitySelector`：实体选择器，配置可指定 `domain`、`device_class`、`integration`、`multiple` 等过滤条件。`helpers/selector.py`
226. `DeviceSelector`：设备选择器，配置可指定 `integration`、`manufacturer`、`model`、`entity`、`multiple` 等。`helpers/selector.py`
227. `AreaSelector`：区域选择器。`helpers/selector.py`
228. `BooleanSelector`：布尔值选择器。`helpers/selector.py`
229. `TextSelector`：文本选择器，支持 `multiline`、`type`（text/email/password/url/tel等）、`prefix`、`suffix`。`helpers/selector.py`
230. `NumberSelector`：数字选择器，支持 `min`、`max`、`step`、`mode`（box/slider）、`unit_of_measurement`。`helpers/selector.py`
231. `SelectSelector`：下拉选择器，配置 `options` 列表和 `multiple`、`custom_value` 选项。`helpers/selector.py`
232. `ColorSelector`、`ObjectSelector`、`TimeSelector`、`DateSelector`、`DateTimeSelector`、`DurationSelector`、`IconSelector`、`MediaSelector`、`ThemeSelector` 等选择器。`helpers/selector.py`
233. `TargetSelector`：目标选择器（实体/设备/区域）。`helpers/selector.py`
234. `LocationSelector`：位置选择器（经纬度+半径）。`helpers/selector.py`
235. `ActionSelector`：动作/脚本选择器。`helpers/selector.py`
236. `ConditionSelector`：条件选择器。`helpers/selector.py`
237. `TriggerSelector`：触发器选择器。`helpers/selector.py`
238. `TemplateSelector`：模板选择器。`helpers/selector.py`
239. `CategorySelector`：分类选择器，支持配置分类项列表。`helpers/selector.py`
240. `FileSelector`：文件选择器。`helpers/selector.py`
241. `BackupLocationSelector`：备份位置选择器。`helpers/selector.py`
242. `LanguageSelector`：语言选择器。`helpers/selector.py`
243. 选择器配置通过 voluptuous schema 验证，`Selector` 基类提供通用的序列化和验证逻辑。`helpers/selector.py`

## 13. Storage 持久化

244. `helpers/storage.py` 提供基于 JSON 文件的数据持久化。`helpers/storage.py:1`
245. `Store` 类是核心存储类，构造函数接受 `hass`、`version`、`key`、`private`、`atomic_writes`、`minor_version` 等参数。`helpers/storage.py`
246. `Store.async_load()` 异步方法：从磁盘加载数据，若文件不存在返回 `None`。`helpers/storage.py`
247. `Store.async_save(data)` 异步方法：将数据保存到磁盘，使用延迟写入合并频繁保存。`helpers/storage.py`
248. `Store.async_remove()` 异步方法：删除存储文件。`helpers/storage.py`
249. `Store.async_delay_save(ms, ...)` 方法：延迟保存，合并指定时间窗口内的多次保存请求。`helpers/storage.py`
250. `Store` 支持数据版本迁移，通过 `async_migrate(old_version, old_data)` 方法在子类中实现迁移逻辑。`helpers/storage.py`
251. `Store` 使用 `hass.helpers.async_call_later` 调度延迟保存，避免阻塞事件循环。`helpers/storage.py`
252. `Store` 将数据写入 `.storage/` 目录下的 JSON 文件，文件名由 `key` 和 `version` 决定。`helpers/storage.py`
253. `Store` 写入时先写入临时文件再原子重命名，确保数据完整性。`helpers/storage.py`
254. `Store` 的 `private` 参数控制文件权限（True 时限制为当前用户可读）。`helpers/storage.py`
255. `Store` 维护内存中的数据缓存 `_data`，避免重复读取磁盘。`helpers/storage.py`
256. `Store` 支持 `minor_version` 进行次要版本升级（无需完整迁移）。`helpers/storage.py`

## 14. 其他 Helpers（debounce/signal/group等）

257. `helpers/debounce.py` 提供防抖器。`helpers/debounce.py:1`
258. `Debouncer` 类：防抖调用协程函数，在冷却期内的调用会被合并为一次执行。`helpers/debounce.py`
259. `Debouncer.__init__(hass, logger, cooldown, immediate, function, ...)` 接受 `hass`、日志器、冷却时间（`timedelta`）、是否立即执行（`immediate`）、被包装函数等参数。`helpers/debounce.py`
260. `Debouncer.async_call()` 方法：触发防抖调用，冷却期内返回 `None`，否则执行函数并返回结果。`helpers/debounce.py`
261. `Debouncer.async_cancel()` 方法：取消待执行的防抖调用。`helpers/debounce.py`
262. `Debouncer` 使用 `async_call_later` 调度延迟执行，并通过 `asyncio.Event` 跟踪正在执行的调用。`helpers/debounce.py`
263. `helpers/signal.py` 提供系统信号处理。`helpers/signal.py:1`
264. `async_register_signal_handlers(hass)` 异步函数：注册 SIGTERM、SIGINT、SIGHUP 信号处理器，触发 Home Assistant 停止或重载。`helpers/signal.py`
265. `helpers/frame.py` 提供调用栈帧分析。`helpers/frame.py:1`
266. `get_integration_frame()` 函数：遍历调用栈，找到第一个属于集成组件（`homeassistant.components.*`）的栈帧。`helpers/frame.py`
267. `report(what, *, integrate_if_possible, error_if_core, ...)` 函数：报告集成代码中的问题使用方式，记录日志或抛出异常。`helpers/frame.py`
268. `report_usage(what, *, key=None, ...)` 函数：报告已弃用或不当的 API 使用。`helpers/frame.py`
269. `IntegrationFrame` NamedTuple 包含 `filename`、`line_number`、`integration`、`module`、`relative_filename` 字段。`helpers/frame.py`
270. `helpers/json.py` 提供 HA 对象 JSON 序列化。`helpers/json.py:1`
271. `JSONEncoder` 类继承 `json.JSONEncoder`，支持序列化 `set`、`datetime`、`Decimal`、`bytes`、`UUID`、`BaseEnum`、`Event`、`State`、`Entity`、`Path` 等类型。`helpers/json.py`
272. `json_bytes(data, *, indent=False)` 函数：将数据序列化为 JSON 字节串。`helpers/json.py`
273. `json_dumps(data, *, indent=False)` 函数：将数据序列化为 JSON 字符串。`helpers/json.py`
274. `helpers/network.py` 提供网络辅助。`helpers/network.py:1`
275. `is_ip_address(address)` 函数：判断字符串是否为有效 IP 地址。`helpers/network.py`
276. `is_local(address)` 函数：判断地址是否为本地/私有地址。`helpers/network.py`
277. `is_internal_request(request)` 函数：判断 HTTP 请求是否来自内部网络。`helpers/network.py`
278. `get_supervisor_network_url(hass)` 函数：获取 Supervisor 网络 URL。`helpers/network.py`
279. `helpers/group.py` 提供分组功能。`helpers/group.py:1`
280. `Group` 类：实体组基类，支持 `expand` 展开组成员。`helpers/group.py`
281. `GenericGroup` 类：通用实体组，可包含任意域的实体。`helpers/group.py`
282. `IntegrationSpecificGroup` 类：特定集成的实体组。`helpers/group.py`
283. `async_expand_entity_ids(hass, entity_ids, ...)` 异步函数：递归展开组引用为成员实体 ID。`helpers/group.py`
284. `helpers/start.py` 提供启动任务辅助。`helpers/start.py:1`
285. `async_at_started(hass, callback)` 函数：在 Home Assistant 启动完成后调用回调（若已启动则立即调用）。`helpers/start.py`
286. `async_at_start(hass, callback)` 函数：在 Home Assistant 启动时（started 阶段之前）调用回调。`helpers/start.py`
287. `helpers/reload.py` 提供平台重载。`helpers/reload.py:1`
288. `async_reload_integration_platforms(hass, domain, ...)` 异步函数：重载集成平台。`helpers/reload.py`
289. `async_integration_x_config_entry_loaded` 等函数：跟踪配置条目加载完成。`helpers/reload.py`
290. `helpers/icon.py` 提供图标辅助。`helpers/icon.py:1`
291. `icon_for_battery_level(battery_level, charging=False)` 函数：根据电池电量返回对应电池图标（`mdi:battery`、`mdi:battery-20` 等），充电时返回 `mdi:battery-charging`。`helpers/icon.py`
292. `icon_for_signal_level(signal_level)` 函数：根据信号强度返回信号图标（`mdi:signal-cellular-1` 等）。`helpers/icon.py`
293. `icon_for_power_level(power_level)` 函数：根据功率等级返回图标。`helpers/icon.py`
294. `helpers/typing.py` 提供类型别名。`helpers/typing.py:1`
295. `ConfigType` 类型别名：`dict[str, Any]`。`helpers/typing.py`
296. `StateType` 类型别名：`str | int | float | None`。`helpers/typing.py`
297. `UndefinedType` 是哨兵类，用于表示未定义值。`helpers/typing.py`
298. `TemplateVarsType` 类型别名：`dict[str, Any] | None`。`helpers/typing.py`
299. `UNDEFINED` 是 `UndefinedType` 的单例。`helpers/typing.py`
300. `helpers/state.py` 提供状态工具。`helpers/state.py:1`
301. `async_reproduce_state(hass, state, ...)` 异步函数：重现历史状态（调用对应服务恢复状态）。`helpers/state.py`
302. `state_as_number(state)` 函数：将 State 对象的 state 转换为数字，无法转换时抛出异常。`helpers/state.py`
303. `state_as_number` 处理 `unknown`/`unavailable` 状态并抛出 `ValueError`。`helpers/state.py`
304. `async_reproduce_states(hass, states, ...)` 异步函数：批量重现状态列表。`helpers/state.py`

## 15. util 核心工具

305. `util/__init__.py` 提供通用工具函数。`util/__init__.py:1`
306. `RE_SANITIZE_FILENAME` 正则匹配 `~`、`..`、`/`、`\\`，用于文件名安全校验。`util/__init__.py:17`
307. `RE_SANITIZE_PATH` 正则匹配 `~` 和连续点号，用于路径安全校验。`util/__init__.py:18`
308. `raise_if_invalid_filename(filename)` 函数：文件名不安全时抛出 `ValueError`。`util/__init__.py:21-27`
309. `raise_if_invalid_path(path)` 函数：路径不安全时抛出 `ValueError`。`util/__init__.py:30-36`
310. `slugify(text, *, separator="_")` 函数：使用 `unicode_slug.slugify` 将文本转为 slug，空文本返回空字符串，结果为空时返回 `"unknown"`。`util/__init__.py:39-44`
311. `repr_helper(inp)` 函数：对 `Mapping` 递归生成 `key=value` 字符串，对 `datetime` 调用 `as_local` 输出 ISO 格式。`util/__init__.py:47-56`
312. `convert[_T, _U](value, to_type, default=None)` 泛型函数：安全类型转换，失败或值为 `None` 时返回默认值。`util/__init__.py:59-67`
313. `convert` 捕获 `ValueError` 和 `TypeError` 异常。`util/__init__.py:65`
314. `ensure_unique_string(preferred_string, current_strings)` 函数：生成唯一字符串，冲突时追加 `_2`、`_3` 后缀。`util/__init__.py:70-86`
315. `get_random_string(length=10)` 函数：使用 `random.SystemRandom()` 生成密码学安全的字母数字随机字符串。`util/__init__.py:90-95`
316. `snakecase(text)` 函数：将驼峰命名转为蛇形命名，特殊处理 "HTTPResponse" 等连续大写组合。`util/__init__.py:99-110`
317. `Throttle` 类：方法节流装饰器，冷却期内重复调用返回 `None`。`util/__init__.py:113-129`
318. `Throttle.__init__(min_time, limit_no_throttle=None)` 接受 `timedelta` 类型的最小间隔和可选的 no_throttle 限流。`util/__init__.py:131-136`
319. `Throttle` 自动检测协程函数并返回协程占位函数。`util/__init__.py:141-149`
320. `Throttle` 使用 `threading.Lock()` 保证线程安全，节流状态按 `id(self)` 存储在 host 对象的 `_throttle` 字典中。`util/__init__.py:182-187`
321. `Throttle` 支持 `no_throttle=True` 关键字参数强制执行。`util/__init__.py:193`

## 16. util/dt 日期时间

322. `util/dt.py` 提供日期时间处理工具。`util/dt.py:1`
323. `DATE_STR_FORMAT = "%Y-%m-%d"` 定义日期字符串格式。`util/dt.py:14`
324. `UTC = dt.UTC` 引用 Python 标准库 UTC 时区。`util/dt.py:15`
325. `DEFAULT_TIME_ZONE: dt.tzinfo = dt.UTC` 默认时区初始为 UTC。`util/dt.py:16`
326. `EPOCHORDINAL = dt.datetime(1970, 1, 1).toordinal()` 定义 Unix 纪元的序数。`util/dt.py:20`
327. `DATETIME_RE` 正则解析日期时间字符串（年-月-日T时:分:秒.微秒+时区）。`util/dt.py:25-30`
328. `STANDARD_DURATION_RE` 正则解析标准时间间隔（如 `"1 days, 2:30:00"`）。`util/dt.py:35-44`
329. `ISO8601_DURATION_RE` 正则解析 ISO 8601 持续时间（如 `"P1DT2H30M"`）。`util/dt.py:49-59`
330. `POSTGRES_INTERVAL_RE` 正则解析 PostgreSQL 时间间隔格式。`util/dt.py:64-73`
331. `get_default_time_zone()` 函数使用 `lru_cache(maxsize=1)` 缓存默认时区。`util/dt.py:76-79`
332. `set_default_time_zone(time_zone)` 函数：设置全局默认时区并清除 lru_cache，要求参数为 `dt.tzinfo` 实例。`util/dt.py:82-93`
333. `get_time_zone(time_zone_str)` 函数：同步获取 `zoneinfo.ZoneInfo`，找不到时返回 `None`。`util/dt.py:96-105`
334. `async_get_time_zone(time_zone_str)` 异步函数：通过 `aiozoneinfo` 异步获取时区，避免阻塞事件循环。`util/dt.py:108-116`
335. `utcnow = partial(dt.datetime.now, UTC)`：使用 `partial` 包装 `datetime.now(UTC)` 获取当前 UTC 时间。`util/dt.py:121-122`
336. `now(time_zone=None)` 函数：获取指定时区当前时间，未指定时使用默认时区。`util/dt.py:125-127`
337. `naive_now()` 函数：返回系统本地时间的 naive datetime（无时区信息）。`util/dt.py:130-147`
338. `as_utc(dattim)` 函数：将 datetime 转为 UTC，naive datetime 假定为默认时区。`util/dt.py:150-160`
339. `as_timestamp(dt_value)` 函数：将 datetime 或日期时间字符串转为 Unix 时间戳（秒），无效时抛出 `ValueError`。`util/dt.py:163-172`
340. `as_local(dattim)` 函数：将 UTC datetime 转为本地（默认）时区。`util/dt.py:175-182`
341. `utc_from_timestamp = partial(dt.datetime.fromtimestamp, tz=UTC)`：从时间戳创建 UTC datetime。`util/dt.py:187-188`
342. `start_of_local_day(dt_or_d=None)` 函数：返回指定日期/时间所在本地日的起始时间（00:00:00）。`util/dt.py:191-200`
343. `parse_datetime(dt_str, *, raise_on_error=False)` 函数：解析日期时间字符串，先尝试 `ciso8601` 快速解析，失败后回退到正则解析。`util/dt.py:220-256`
344. `parse_datetime` 支持 `Z` 后缀表示 UTC 和 `+HH:MM`/`-HH:MM` 偏移量。`util/dt.py:244-253`
345. `parse_datetime` 的 `raise_on_error=True` 参数使解析失败时抛出 `ValueError` 而非返回 `None`。`util/dt.py:236-237`
346. `parse_date(dt_str)` 函数：使用 `%Y-%m-%d` 格式解析日期字符串为 `date` 对象，失败返回 `None`。`util/dt.py:259-264`
347. `parse_duration(value)` 函数：解析持续时间字符串，支持标准格式、ISO 8601 和 PostgreSQL 间隔，返回 `timedelta`。`util/dt.py:270-293`
348. `parse_time(time_str)` 函数：解析 `"HH:MM:SS"` 或 `"HH:MM"` 格式的时间字符串为 `time` 对象。`util/dt.py:296-311`
349. `_get_timestring(timediff, precision=1)` 函数：将秒数时间差格式化为人类可读字符串（年/月/日/时/分/秒）。`util/dt.py:314-346`
350. `get_age(date, precision=1)` 函数：计算过去 datetime 的"年龄"字符串，未来时间抛出 `ValueError`。`util/dt.py:349-365`
351. `get_time_remaining(date, precision=1)` 函数：计算未来 datetime 的剩余时间字符串，过去时间抛出 `ValueError`。`util/dt.py:368-385`
352. `parse_time_expression(parameter, min_value, max_value)` 函数：解析 cron 风格时间表达式（`*`、`/n`、具体值），返回匹配的整数列表。`util/dt.py:388-399`
353. `util/dt.py` 导入 `ciso8601` 库进行快速 ISO 8601 解析。`util/dt.py:12`
354. `util/dt.py` 导入 `aiozoneinfo.async_get_time_zone` 进行异步时区获取。`util/dt.py:11`

## 17. util/json 与 yaml

355. `util/json.py` 提供 JSON 序列化工具，底层使用 `orjson` 库。`util/json.py:1-7`
356. `JsonValueType` 类型别名：`dict[str, JsonValueType] | list[JsonValueType] | str | int | float | bool | None`，递归定义 JSON 值类型。`util/json.py:14-16`
357. `JsonArrayType = list[JsonValueType]`。`util/json.py:18`
358. `JsonObjectType = dict[str, JsonValueType]`。`util/json.py:20`
359. `JSON_ENCODE_EXCEPTIONS = (TypeError, ValueError)` 定义 JSON 编码异常元组。`util/json.py:23`
360. `JSON_DECODE_EXCEPTIONS = (orjson.JSONDecodeError,)` 定义 JSON 解码异常元组。`util/json.py:24`
361. `SerializationError(HomeAssistantError)` 异常类：JSON 序列化失败时抛出。`util/json.py:27-28`
362. `json_loads(obj)` 函数：解析 JSON 数据，包含对 orjson 不支持 `str` 子类的 workaround（issue #445）。`util/json.py:31-40`
363. `json_loads_array(obj)` 函数：解析 JSON 并确保结果为列表，否则抛出 `ValueError`。`util/json.py:43-49`
364. `json_loads_object(obj)` 函数：解析 JSON 并确保结果为字典，否则抛出 `ValueError`。`util/json.py:52-58`
365. `load_json(filename, default=_SENTINEL)` 函数：从文件加载 JSON，文件不存在时返回 `{}` 或指定默认值。`util/json.py:61-81`
366. `load_json` 以二进制模式（`"rb"`）打开文件并使用 `orjson.loads` 解析。`util/json.py:70-71`
367. `load_json` 捕获 `FileNotFoundError` 记录 debug 日志，捕获 `JSON_DECODE_EXCEPTIONS` 和 `OSError` 抛出 `HomeAssistantError`。`util/json.py:72-80`
368. `load_json_array(filename, default=_SENTINEL)` 函数：从文件加载 JSON 并确保为列表，默认返回空列表。`util/json.py:84-101`
369. `load_json_object(filename, default=_SENTINEL)` 函数：从文件加载 JSON 并确保为字典，默认返回空字典。`util/json.py:104-121`
370. `format_unserializable_data(data)` 函数：将不可序列化数据路径格式化为 `path=value(type)` 的逗号分隔字符串。`util/json.py:124-129`
371. `util/yaml/loader.py` 提供自定义 YAML 加载器，基于 `annotatedyaml` 库。`util/yaml/loader.py:1-8`
372. `HAS_C_LOADER` 从 `annotatedyaml` 导出，指示是否有 C YAML 加载器可用。`util/yaml/loader.py:9`
373. `Secrets` 类从 `annotatedyaml` 导出，管理 YAML `!secret` 引用。`util/yaml/loader.py:12`
374. `JSON_TYPE` 类型别名从 `annotatedyaml` 导出。`util/yaml/loader.py:10`
375. `LoaderType` 类型别名从 `annotatedyaml` 导出。`util/yaml/loader.py:11`
376. `add_constructor` 函数从 `annotatedyaml` 导出，用于注册自定义 YAML 标签构造器。`util/yaml/loader.py:13`
377. `YamlTypeError(HomeAssistantError)` 异常类：当 YAML 顶层数据不是字典时抛出。`util/yaml/loader.py:36-37`
378. `load_yaml(fname, secrets=None)` 函数：加载 YAML 文件，将 `annotatedyaml.YAMLException` 包装为 `HomeAssistantError`，`FileNotFoundError` 原样抛出。`util/yaml/loader.py:40-51`
379. `load_yaml_dict(fname, secrets=None)` 函数：加载 YAML 文件并确保顶层为字典，空文件返回空字典。`util/yaml/loader.py:54-67`
380. `parse_yaml(content, secrets=None)` 函数：解析 YAML 字符串或文本流。`util/yaml/loader.py:70-77`
381. `secret_yaml(loader, node)` 函数：处理 `!secret` YAML 标签，从 secrets 文件加载值。`util/yaml/loader.py:80-85`
382. `__all__` 导出列表包含 `HAS_C_LOADER`、`JSON_TYPE`、`Secrets`、`YamlTypeError`、`add_constructor`、`load_yaml`、`load_yaml_dict`、`parse_yaml`、`secret_yaml`。`util/yaml/loader.py:23-33`

## 18. util/async 与 thread

383. `util/async_.py` 提供 asyncio 工具函数。`util/async_.py:1`
384. `create_eager_task[_T](coro, *, name=None, loop=None)` 函数：创建立即调度的 asyncio Task（`eager_start=True`），从非事件循环线程调用时通过 `frame.report_usage` 报告错误。`util/async_.py:23-42`
385. `create_eager_task` 在没有运行循环时从错误线程调用会导入 `homeassistant.helpers.frame` 并报告 "attempted to create an asyncio task from a thread"。`util/async_.py:37-39`
386. `cancelling(task)` 函数：返回 Task 是否正在取消，检查 task 的 `cancelling()` 方法（Python 3.11+）。`util/async_.py:45-47`
387. `run_callback_threadsafe[_T, *_Ts](loop, callback, *args)` 函数：从其他线程向事件循环提交回调，返回 `concurrent.futures.Future`。`util/async_.py:50-95`
388. `run_callback_threadsafe` 检测是否在事件循环线程内调用，若是则抛出 `RuntimeError("Cannot be called from within the event loop")`。`util/async_.py:57-58`
389. `run_callback_threadsafe` 在事件循环关闭时（设置了 `_SHUTDOWN_RUN_CALLBACK_THREADSAFE` 属性）抛出 `RuntimeError`，防止死锁。`util/async_.py:74-93`
390. `gather_with_limited_concurrency(limit, *tasks, return_exceptions=False)` 异步函数：包装 `asyncio.gather`，使用 `Semaphore` 限制并发任务数。`util/async_.py:98-114`
391. `gather_with_limited_concurrency` 内部使用 `create_eager_task` 创建每个信号量包装任务。`util/async_.py:112`
392. `shutdown_run_callback_threadsafe(loop)` 函数：设置循环上的关闭标记，不可逆，仅在 HA 关闭时调用。`util/async_.py:117-131`
393. `get_scheduled_timer_handles(loop)` 函数：返回循环上已调度的 `TimerHandle` 列表（访问内部 `_scheduled` 属性）。`util/async_.py:134-136`
394. `_SHUTDOWN_RUN_CALLBACK_THREADSAFE = "_shutdown_run_callback_threadsafe"` 是关闭标记属性名。`util/async_.py:20`
395. `util/thread.py` 提供线程工具。`util/thread.py:1`
396. `THREADING_SHUTDOWN_TIMEOUT = 10` 定义线程关闭超时时间（秒）。`util/thread.py:9`
397. `deadlock_safe_shutdown()` 函数：安全关闭非守护线程，对每个剩余线程分配 `THREADING_SHUTDOWN_TIMEOUT / 线程数` 的 join 超时，避免永久死锁。`util/thread.py:14-35`
398. `deadlock_safe_shutdown` 仅处理非主线程、非守护、仍存活的线程。`util/thread.py:19-25`
399. `async_raise(tid, exctype)` 函数：通过 `ctypes.pythonapi.PyThreadState_SetAsyncExc` 在指定线程中异步抛出异常。`util/thread.py:38-55`
400. `async_raise` 要求 `exctype` 为类型而非实例，返回值为 1 表示成功，0 表示线程未找到，大于 1 需回滚。`util/thread.py:40-55`
401. `ThreadWithException(threading.Thread)` 类：支持从其他线程在自身上下文中抛出异常的线程类。`util/thread.py:58-69`
402. `ThreadWithException.raise_exc(exctype)` 方法：在该线程中抛出指定异常类型，断言 `self.ident` 已设置。`util/thread.py:66-69`
403. `util/logging.py` 提供日志工具。`util/logging.py:1`
404. `HomeAssistantQueueListener(logging.handlers.QueueListener)` 类：自定义队列监听器，监控高频日志模块。`util/logging.py:24-89`
405. `HomeAssistantQueueListener.LOG_COUNTS_RESET_INTERVAL = 300`：日志计数重置间隔（秒）。`util/logging.py:27`
406. `HomeAssistantQueueListener.MAX_LOGS_COUNT = 200`：模块最大日志数阈值，超过则警告并跳过该模块后续日志。`util/logging.py:28`
407. `HomeAssistantQueueListener.EXCLUDED_LOG_COUNT_MODULES` 排除 `automation`、`script`、`setup`、`util.logging` 模块的计数。`util/logging.py:30-35`
408. `HomeAssistantQueueHandler(logging.handlers.QueueHandler)` 类：在另一个线程处理日志，避免事件循环中的 I/O 阻塞。`util/logging.py:92-125`
409. `HomeAssistantQueueHandler.handle` 重写以避免父类锁（`SimpleQueue` 本身线程安全）。`util/logging.py:97-113`
410. `async_activate_log_queue_handler(hass)` 异步回调函数：将根日志记录器的现有处理器迁移到队列处理器。`util/logging.py:128-149`
411. `catch_log_exception(func, format_err, job_type=None)` 函数：装饰函数/协程/回调以捕获并记录异常，根据 `HassJobType` 选择对应包装器。`util/logging.py:219-239`
412. `catch_log_coro_exception(target, format_err, *args)` 函数：包装协程以捕获异常并返回 `None`。`util/logging.py:242-255`
413. `async_create_catching_coro(target)` 函数：包装协程，异常记录时包含包装位置的堆栈跟踪。`util/logging.py:258-275`
414. `log_exception(format_err, *args)` 函数：从调用栈帧推断模块名，记录异常和格式化上下文消息。`util/logging.py:152-167`

## 19. util/color 与 unit_system

415. `util/color.py` 提供颜色空间转换工具。`util/color.py:1`
416. `RGBColor(NamedTuple)` 包含 `r: int`、`g: int`、`b: int` 三个字段（0-255）。`util/color.py:12-17`
417. `COLORS` 字典映射 140+ 个 CSS3 颜色名到 `RGBColor`，并额外包含 `"homeassistant": RGBColor(24, 188, 242)`。`util/color.py:26-177`
418. `XYPoint` 使用 `attr.s()` 定义为 attrs 类，包含 `x: float`、`y: float`，表示 CIE 1931 XY 坐标。`util/color.py:180-185`
419. `GamutType` 使用 `attr.s()` 定义为 attrs 类，包含 `red: XYPoint`、`green: XYPoint`、`blue: XYPoint`，表示灯光色域。`util/color.py:188-195`
420. `color_name_to_rgb(color_name)` 函数：将颜色名（不区分大小写，忽略空格）转为 `RGBColor`，未知颜色抛出 `ValueError`。`util/color.py:198-206`
421. `color_RGB_to_xy(iR, iG, iB, Gamut=None)` 函数：将 RGB 转为 XY 颜色坐标，返回 `(x, y)` 元组。`util/color.py:209-213`
422. `color_RGB_to_xy_brightness(iR, iG, iB, Gamut=None)` 函数：将 RGB 转为 XY 和亮度，返回 `(x, y, brightness)`，全黑输入返回 `(0.0, 0.0, 0)`。`util/color.py:219-256`
423. `color_RGB_to_xy_brightness` 使用 Wide RGB D65 转换公式和 Gamma 校正。`util/color.py:230-246`
424. `color_RGB_to_xy_brightness` 支持 Gamut 色域约束，超出色域时通过 `get_closest_point_to_point` 找到最近点。`util/color.py:249-255`
425. `color_xy_to_RGB(vX, vY, Gamut=None)` 函数：将 XY 转为 RGB（亮度默认 255）。`util/color.py:259-263`
426. `color_xy_brightness_to_RGB(vX, vY, ibrightness, Gamut=None)` 函数：将 XY+亮度转为 RGB 元组，使用反向 Gamma 校正。`util/color.py:268-310`
427. `color_hsb_to_RGB(fH, fS, fB)` 函数：将 HSB/HSV（色相0-360、饱和度0-1、亮度0-1）转为 RGB。`util/color.py:313-351`
428. `color_RGB_to_hsv(iR, iG, iB)` 函数：将 RGB 转为 HSV，返回 `(hue 0-360, saturation 0-100, value 0-100)`，基于 `colorsys.rgb_to_hsv`。`util/color.py:354-362`
429. `color_RGB_to_hs(iR, iG, iB)` 函数：将 RGB 转为 HS（不含亮度）。`util/color.py:365-367`
430. `color_hsv_to_RGB(iH, iS, iV)` 函数：将 HSV 转为 RGB，基于 `colorsys.hsv_to_rgb`。`util/color.py:370-378`
431. `color_hs_to_RGB(iH, iS)` 函数：将 HS 转为 RGB（V 固定 100）。`util/color.py:381-383`
432. `color_xy_to_hs(vX, vY, Gamut=None)` 函数：XY → RGB → HSV → HS 链式转换。`util/color.py:386-391`
433. `util/color.py` 导入 `colorsys` 标准库和 `attr` 第三方库。`util/color.py:3-7`
434. `util/unit_system.py` 提供单位系统管理。`util/unit_system.py:1`
435. `_CONF_UNIT_SYSTEM_IMPERIAL = "imperial"`、`_CONF_UNIT_SYSTEM_METRIC = "metric"`、`_CONF_UNIT_SYSTEM_US_CUSTOMARY = "us_customary"` 定义单位系统配置键。`util/unit_system.py:42-44`
436. `UnitSystem` 是 frozen dataclass（`@dataclass(frozen=True, kw_only=True)`），包含 `accumulated_precipitation_unit`、`area_unit`、`length_unit`、`mass_unit`、`pressure_unit`、`temperature_unit`、`volume_unit`、`wind_speed_unit` 等字段。`util/unit_system.py:84-97`
437. `UnitSystem.__init__` 验证所有单位是否合法，不合法时收集错误信息并抛出 `ValueError`。`util/unit_system.py:99-130`
438. `UnitSystem.temperature(temperature, from_unit)` 方法：使用 `TemperatureConverter` 将温度从 `from_unit` 转换为本系统单位。`util/unit_system.py:143-150`
439. `UnitSystem.length(length, from_unit)` 方法：使用 `DistanceConverter` 转换长度。`util/unit_system.py:152-160`
440. `UnitSystem.area`、`pressure`、`wind_speed`、`volume`、`accumulated_precipitation` 方法分别调用对应 Converter 进行单位转换。`util/unit_system.py:162-210`
441. `UnitSystem.as_dict()` 方法：将单位系统转为 `dict[str, str]`。`util/unit_system.py:212-223`
442. `UnitSystem.get_converted_unit(device_class, original_unit)` 方法：根据设备类和原始单位查询转换后的单位。`util/unit_system.py:225-231`
443. `get_unit_system(key)` 函数：根据配置键返回 `US_CUSTOMARY_SYSTEM` 或 `METRIC_SYSTEM`，无效键抛出 `ValueError`。`util/unit_system.py:234-240`
444. `validate_unit_system` 是 voluptuous schema，将输入转小写、映射已弃用的 `imperial` 到 `us_customary`，验证为 `metric` 或 `us_customary`。`util/unit_system.py:251-255`
445. `METRIC_SYSTEM` 预定义公制单位系统：温度摄氏度、长度千米、质量克、压力帕斯卡、体积升、风速米/秒、面积平方米。`util/unit_system.py:257-335`
446. `US_CUSTOMARY_SYSTEM` 预定义美制单位系统：温度华氏度、长度英里、质量磅、压力 PSI、体积加仑、风速英里/时、面积平方英尺。`util/unit_system.py:337-399`
447. `METRIC_SYSTEM` 的 `conversions` 字典定义非metric单位到metric单位的自动转换映射（如英制距离→公制、华氏度→摄氏度等）。`util/unit_system.py:260-327`
448. `MASS_UNITS` 集合包含 `POUNDS`、`OUNCES`、`KILOGRAMS`、`GRAMS`。`util/unit_system.py:50-55`
449. `TEMPERATURE_UNITS` 集合包含 `FAHRENHEIT`、`CELSIUS`。`util/unit_system.py:63`
450. `_VALID_BY_TYPE` 字典映射测量类型（LENGTH/WIND_SPEED/TEMPERATURE/MASS/VOLUME/PRESSURE/AREA）到其有效单位集合。`util/unit_system.py:65-74`
451. `_is_valid_unit(unit, unit_type)` 函数：检查单位是否属于指定类型的有效单位集合。`util/unit_system.py:77-81`

## 20. 其他 Util

452. `util/timeout.py` 提供高级超时管理。`util/timeout.py:1`
453. `ZONE_GLOBAL = "global"` 定义全局超时区域名称。`util/timeout.py:14`
454. `_State(enum.Enum)` 枚举定义任务状态：`INIT`、`ACTIVE`、`TIMEOUT`、`EXIT`。`util/timeout.py:17-23`
455. `TimeoutManager` 类管理不同区域（zone）的超时，支持全局超时和命名区域超时。`util/timeout.py:448-553`
456. `TimeoutManager.async_timeout(timeout, zone_name=ZONE_GLOBAL, cool_down=0, cancel_message=None)` 方法：返回异步上下文管理器，在超时后取消当前任务。`util/timeout.py:496-523`
457. `TimeoutManager.async_freeze(zone_name=ZONE_GLOBAL)` 方法：返回异步上下文管理器，冻结指定区域的计时器。`util/timeout.py:525-542`
458. `TimeoutManager.freeze(zone_name=ZONE_GLOBAL)` 方法：同步版本的 freeze，通过 `run_callback_threadsafe` 调用。`util/timeout.py:544-553`
459. `_GlobalTaskContext` 管理全局超时任务，支持 cool_down 等待区域任务完成。`util/timeout.py:140-265`
460. `_ZoneTaskContext` 管理区域超时任务，在 freeze 期间暂停计时器。`util/timeout.py:268-372`
461. `_GlobalFreezeContext` 和 `_ZoneFreezeContext` 分别管理全局和区域的冻结上下文。`util/timeout.py:26-137`
462. 超时上下文管理器在退出时检测 `asyncio.CancelledError`，若因超时取消则抛出 `TimeoutError`，并通过 `uncancel()` 管理取消计数。`util/timeout.py:185-194,319-328`
463. `util/uuid.py` 提供 UUID 生成工具。`util/uuid.py:1`
464. `random_uuid_hex()` 函数：使用 `random.getrandbits(32 * 4)` 生成 32 字符随机 UUID 十六进制字符串，不适用于密码学安全场景。`util/uuid.py:6-12`
465. `util/ulid.py` 提供 ULID 生成工具，基于 `ulid_transform` 库。`util/ulid.py:1-11`
466. `ulid(timestamp=None)` 函数：生成 ULID 字符串，时间戳为 None 时使用 `ulid_now()`，否则使用 `ulid_at_time(timestamp)`。`util/ulid.py:25-42`
467. ULID 结构为 48 位时间戳 + 80 位随机数，共 26 个 Crockford Base32 字符。`util/ulid.py:31-34`
468. `ulid.py` 从 `ulid_transform` 重新导出 `bytes_to_ulid`、`bytes_to_ulid_or_none`、`ulid_at_time`、`ulid_hex`、`ulid_now`、`ulid_to_bytes`、`ulid_to_bytes_or_none`。`util/ulid.py:3-22`
469. `util/ssl.py` 提供 SSL 上下文创建工具。`util/ssl.py:1`
470. `SSLALPNProtocols` 类型别名：`tuple[str, ...] | None`。`util/ssl.py:12`
471. `SSL_ALPN_NONE = None`：无 ALPN 协议（用于不支持 ALPN 的库）。`util/ssl.py:16`
472. `SSL_ALPN_HTTP11 = ("http/1.1",)`：仅 HTTP/1.1（aiohttp 默认）。`util/ssl.py:18`
473. `SSL_ALPN_HTTP11_HTTP2 = ("http/1.1", "h2")`：HTTP/1.1 + HTTP/2（httpx）。`util/ssl.py:20`
474. `SSLCipherList(StrEnum)` 枚举定义密码套件级别：`PYTHON_DEFAULT`、`INTERMEDIATE`、`MODERN`、`INSECURE`。`util/ssl.py:23-29`
475. `SSL_CIPHER_LISTS` 字典映射密码套件级别到 OpenSSL 密码字符串，INTERMEDIATE 基于 Mozilla 推荐，MODERN 仅支持 ECDHE+AES-GCM/CHACHA20。`util/ssl.py:32-74`
476. `client_context(ssl_cipher_list, alpn_protocols)` 函数：返回缓存的 SSL 客户端上下文。`util/ssl.py:165-170`
477. `create_client_context(...)` 函数：返回独立的（非缓存）SSL 客户端上下文。`util/ssl.py:173-179`
478. `client_context_no_verify(...)` 函数：返回不验证服务器证书的缓存 SSL 上下文。`util/ssl.py:157-162`
479. `create_no_verify_ssl_context(...)` 函数：返回不验证证书的 SSL 上下文。`util/ssl.py:182-187`
480. `get_default_context()` 返回默认 SSL 上下文（Python 默认密码 + HTTP/1.1 ALPN）。`util/ssl.py:147-149`
481. `get_default_no_verify_context()` 返回默认不验证证书的 SSL 上下文。`util/ssl.py:152-154`
482. `server_context_modern()` 返回遵循 Mozilla Modern 推荐的服务器 SSL 上下文（TLS 1.2+）。`util/ssl.py:190-206`
483. `server_context_intermediate()` 返回遵循 Mozilla Intermediate 推荐的服务器 SSL 上下文。`util/ssl.py:209-226`
484. `ssl.py` 在模块加载时预热所有密码套件和 ALPN 组合的缓存（4×3=12 个上下文），避免事件循环中的阻塞 I/O。`util/ssl.py:137-144`
485. `ssl.py` 使用 `certifi.where()` 或 `REQUESTS_CA_BUNDLE` 环境变量获取 CA 证书包。`util/ssl.py:112`
486. `util/network.py` 提供网络地址工具。`util/network.py:1`
487. `LOOPBACK_NETWORKS` 元组定义回环网络：`127.0.0.0/8`、`::1/128`、`::ffff:127.0.0.0/104`。`util/network.py:11-15`
488. `PRIVATE_NETWORKS` 元组定义私有网络：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`、`fd00::/8` 及 IPv4-mapped IPv6 对应地址。`util/network.py:18-26`
489. `LINK_LOCAL_NETWORKS` 元组定义链路本地网络：`169.254.0.0/16`、`fe80::/10`、`::ffff:169.254.0.0/112`。`util/network.py:29-33`
490. `is_loopback(address)` 函数：检查地址是否为回环地址。`util/network.py:36-38`
491. `is_private(address)` 函数：检查地址是否在私有网络范围内。`util/network.py:41-43`
492. `is_link_local(address)` 函数：检查地址是否为链路本地地址。`util/network.py:46-48`
493. `is_local(address)` 函数：检查地址是否为本地地址（回环、私有或链路本地）。`util/network.py:51-53`
494. `is_invalid(address)` 函数：检查地址是否为未指定地址（`is_unspecified`）。`util/network.py:56-58`
495. `is_ip_address(address)` 函数：尝试 `ip_address(address)`，成功返回 `True`，`ValueError` 返回 `False`。`util/network.py:61-68`
496. `is_ipv4_address(address)` 和 `is_ipv6_address(address)` 函数分别验证 IPv4/IPv6 地址。`util/network.py:71-88`
497. `is_host_valid(host)` 函数：验证主机名（IP 地址或域名），拒绝超过 255 字符和纯数字点号格式，使用正则验证域名标签。`util/network.py:91-100`
498. `util/aiohttp.py` 提供 aiohttp 测试/模拟工具。`util/aiohttp.py:1`
499. `MockStreamReader` 类：模拟 aiohttp `StreamReader`，使用 `io.BytesIO` 存储内容，`read(byte_count=-1)` 方法读取字节。`util/aiohttp.py:15-26`
500. `MockStreamReaderChunked(MockStreamReader)` 类：增加 `readchunk()` 方法模拟分块传输。`util/aiohttp.py:29-34`
501. `MockPayloadWriter` 类：模拟 aiohttp `PayloadWriter`，提供 `enable_chunking`、`send_headers`、`write_headers`、`write` 等空方法。`util/aiohttp.py:37-52`
502. `MockRequest` 类：模拟 aiohttp 请求，包含 `method`、`url`、`status`、`headers`（`CIMultiDict`）、`query_string`、`content`、`remote` 等属性。`util/aiohttp.py:56-118`
503. `MockRequest.json(loads=json_loads)` 方法：使用 `json_loads` 解析请求体为 JSON。`util/aiohttp.py:108-110`
504. `MockRequest.post()` 方法：使用 `parse_qsl` 解析 POST 参数为 `MultiDict`。`util/aiohttp.py:112-114`
505. `serialize_response(response)` 函数：将 aiohttp `web.Response` 序列化为 `{"status", "body", "headers"}` 字典，处理 `StringPayload` 和 `bytes` 类型 body。`util/aiohttp.py:121-136`
506. `util/location.py` 提供位置检测和距离计算。`util/location.py:1`
507. `WHOAMI_URL = "https://services.home-assistant.io/whoami/v1"` 和 `WHOAMI_URL_DEV` 定义位置检测服务端点。`util/location.py:14-15`
508. WGS 84 椭球参数：`AXIS_A = 6378137`（长半轴，米）、`FLATTENING = 1/298.257223563`（扁率）、`AXIS_B = 6356752.314245`（短半轴，米）。`util/location.py:20-24`
509. `MILES_PER_KILOMETER = 0.621371`、`MAX_ITERATIONS = 200`、`CONVERGENCE_THRESHOLD = 1e-12`。`util/location.py:26-28`
510. `LocationInfo(NamedTuple)` 包含 `ip`、`country_code`、`currency`、`region_code`、`region_name`、`city`、`zip_code`、`time_zone`、`latitude`、`longitude`、`use_metric` 字段。`util/location.py:31-44`
511. `async_detect_location_info(session)` 异步函数：调用 whoami 服务检测位置信息，根据国家代码判断 `use_metric`（美国、缅甸、利比里亚为非公制）。`util/location.py:47-56`
512. `distance(lat1, lon1, lat2, lon2)` 函数（`lru_cache`）：使用 Vincenty 公式计算两点间距离（米），任一坐标为 None 返回 None。`util/location.py:59-72`
513. `vincenty(point1, point2, miles=False)` 函数：Vincenty 反解法计算椭球面上两点距离（公里或英里），重合点返回 0.0，迭代不收敛返回 None。`util/location.py:78-157`
514. `_get_whoami(session)` 异步函数：请求 whoami 服务，根据 HA 版本选择开发/生产端点，超时 30 秒。`util/location.py:160-186`
515. `util/percentage.py` 提供百分比转换工具。`util/percentage.py:1`
516. `ordered_list_item_to_percentage[_T](ordered_list, item)` 函数：将有序列表项映射为百分比（如 4 项列表中第 1 项为 25%），项不在列表中抛出 `ValueError`。`util/percentage.py:11-31`
517. `percentage_to_ordered_list_item[_T](ordered_list, percentage)` 函数：将百分比映射回有序列表项（如 1-25% 对应第 1 项），空列表抛出 `ValueError`。`util/percentage.py:34-57`
518. `ranged_value_to_percentage(low_high_range, value)` 函数：将范围内的值转换为百分比（如 1-255 范围中 255 为 100%）。`util/percentage.py:60-74`
519. `percentage_to_ranged_value(low_high_range, percentage)` 函数：将百分比转换为范围内的值（如 50% 在 1-255 范围中为 127.5）。`util/percentage.py:77-91`
520. `percentage.py` 从 `.scaling` 模块重新导出 `int_states_in_range`、`scale_ranged_value_to_int_range`、`scale_to_ranged_value`、`states_in_range`。`util/percentage.py:3-8`
521. `util/decorator.py` 提供装饰器工具。`util/decorator.py:1`
522. `Registry[_KT: Hashable, _VT: Callable[..., Any]](dict[_KT, _VT])` 类：继承字典的注册表，提供 `register(name)` 装饰器方法将函数注册到字典中。`util/decorator.py:7-17`
