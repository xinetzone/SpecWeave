---
type: Facts
title: "Home Assistant Components 集成模式事实清单"
---

# Home Assistant Components 集成模式事实清单

> 源码根路径：`homeassistant/components/`
> 采集日期：2026-08-22
> 零推测原则：每条事实均标注 `文件路径:行号`

---

## 1. manifest.json 标准

1. manifest.json 是 JSON 格式文件，位于每个集成目录根下，如 `tuya/manifest.json`（`tuya/manifest.json:1`）。
2. `domain` 字段：集成的唯一标识符，小写蛇形命名，如 `"domain": "tuya"`（`tuya/manifest.json:2`）。
3. `name` 字段：集成的人类可读名称，如 `"name": "Tuya"`（`tuya/manifest.json:3`）。
4. `codeowners` 字段：GitHub 用户名/团队名列表，负责维护该集成，如 `["@Tuya", "@zlinoliver"]`（`tuya/manifest.json:4`）。
5. `config_flow` 字段：布尔值，标识是否支持 ConfigFlow 配置界面，`"config_flow": true`（`tuya/manifest.json:5`）。
6. `dependencies` 字段：集成所依赖的其他集成 domain 列表，如 tuya 依赖 `["ffmpeg"]`（`tuya/manifest.json:6`）。
7. `documentation` 字段：集成文档 URL，如 `"https://www.home-assistant.io/integrations/tuya"`（`tuya/manifest.json:42`）。
8. `integration_type` 字段：集成类型，如 tuya 为 `"hub"`（`tuya/manifest.json:43`）。
9. `iot_class` 字段：IoT 通信类别，如 tuya 为 `"cloud_push"`（`tuya/manifest.json:44`）。
10. `requirements` 字段：Python 依赖包列表，含版本锁定，如 tuya 的 `["tuya-device-handlers==0.0.24", "tuya-device-sharing-sdk==0.2.10"]`（`tuya/manifest.json:46-49`）。
11. `loggers` 字段：集成使用的 Python logger 名称列表，如 tuya 的 `["tuya_sharing"]`（`tuya/manifest.json:45`）。
12. `dhcp` 字段：DHCP 发现规则列表，支持 `macaddress` 通配符匹配，如 tuya 配置了 11 条 MAC 前缀规则（`tuya/manifest.json:7-41`）。
13. `after_dependencies` 字段：后置依赖，在该集成之后加载，如 mqtt 的 `["hassio"]`（`mqtt/manifest.json:4`）。
14. `quality_scale` 字段：集成质量等级，如 mqtt 为 `"platinum"`（`mqtt/manifest.json:11`），anthropic 为 `"gold"`（`anthropic/manifest.json:11`），conversation 为 `"internal"`（`conversation/manifest.json:8`）。
15. `single_config_entry` 字段：布尔值，标识是否只允许单个配置条目，mqtt 设置为 `true`（`mqtt/manifest.json:13`）。
16. `homekit` 字段：HomeKit 相关配置，hue 配置了 `{"models": ["BSB002"]}`（`hue/manifest.json:7-9`）。
17. `zeroconf` 字段：mDNS/DNS-SD 发现服务类型列表，如 hue 的 `["_hue._tcp.local."]`（`hue/manifest.json:14`），zwave_js 的 `["_zwave-js-server._tcp.local."]`（`zwave_js/manifest.json:40`）。
18. `usb` 字段：USB 设备发现规则列表，zwave_js 配置了 4 条 USB 设备规则，含 `vid`/`pid`/`known_devices`/`manufacturer`/`description`（`zwave_js/manifest.json:13-39`）。
19. mqtt 的 requirements 为 `["paho-mqtt==2.1.0"]`（`mqtt/manifest.json:12`）。
20. hue 的 requirements 为 `["aiohue==4.8.1"]`，loggers 为 `["aiohue"]`（`hue/manifest.json:12-13`）。
21. zwave_js 的 requirements 为 `["zwave-js-server-python==0.72.0"]`，loggers 为 `["zwave_js_server"]`（`zwave_js/manifest.json:11-12`）。
22. conversation 的 requirements 为 `["hassil==3.8.0", "home-assistant-intents==2026.6.24"]`（`conversation/manifest.json:9`）。
23. anthropic 的 requirements 为 `["anthropic==0.108.0"]`（`anthropic/manifest.json:12`）。
24. assist_pipeline 的 requirements 为 `["pymicro-vad==1.0.1", "pyspeex-noise==1.0.2"]`（`assist_pipeline/manifest.json:11`）。
25. default_config 的 dependencies 包含 20 个核心集成：`assist_pipeline`、`bluetooth`、`cloud`、`conversation`、`dhcp`、`energy`、`file`、`go2rtc`、`history`、`homeassistant_alerts`、`logbook`、`media_source`、`mobile_app`、`my`、`ssdp`、`stream`、`sun`、`usage_prediction`、`usb`、`webhook`、`zeroconf`（`default_config/manifest.json:5-27`）。

---

## 2. integration_type 与 iot_class

26. `integration_type` 可取 `"hub"`（中心枢纽型），如 tuya、hue、zwave_js（`tuya/manifest.json:43`、`hue/manifest.json:10`、`zwave_js/manifest.json:9`）。
27. `integration_type` 可取 `"service"`（服务型），如 mqtt、anthropic（`mqtt/manifest.json:9`、`anthropic/manifest.json:9`）。
28. `integration_type` 可取 `"entity"`（实体平台型），如 conversation（`conversation/manifest.json:7`）。
29. `integration_type` 可取 `"system"`（系统内置型），如 assist_pipeline、default_config（`assist_pipeline/manifest.json:8`、`default_config/manifest.json:29`）。
30. `iot_class` 可取 `"cloud_push"`（云端推送），如 tuya（`tuya/manifest.json:44`）。
31. `iot_class` 可取 `"local_push"`（本地推送），如 mqtt、hue、zwave_js、assist_pipeline（`mqtt/manifest.json:10`、`hue/manifest.json:11`、`zwave_js/manifest.json:10`、`assist_pipeline/manifest.json:9`）。
32. `iot_class` 可取 `"cloud_polling"`（云端轮询），如 anthropic（`anthropic/manifest.json:10`）。
33. zwave_js 的 integration_type 为 `"hub"`，iot_class 为 `"local_push"`（`zwave_js/manifest.json:9-10`）。

---

## 3. Entity 基类继承层次

34. `LightEntity` 继承自 `ToggleEntity`（`light/__init__.py:741`，导入自 `homeassistant.helpers.entity`，`light/__init__.py:23`）。
35. `SwitchEntity` 继承自 `ToggleEntity`（`switch/__init__.py:95`，导入自 `homeassistant.helpers.entity`，`switch/__init__.py:20`）。
36. `SensorEntity` 继承自 `Entity`（`sensor/__init__.py:183`，导入自 `homeassistant.helpers.entity`，`sensor/__init__.py:25`）。
37. `BinarySensorEntity` 继承自 `Entity`（`binary_sensor/__init__.py:157`，导入自 `homeassistant.helpers.entity`，`binary_sensor/__init__.py:16`）。
38. `ClimateEntity` 继承自 `Entity`（`climate/__init__.py:242`，导入自 `homeassistant.helpers.entity`，`climate/__init__.py:24`）。
39. `CoverEntity` 继承自 `Entity`（`cover/__init__.py:199`，导入自 `homeassistant.helpers.entity`，`cover/__init__.py:27`）。
40. `Camera` 继承自 `Entity`（`camera/__init__.py:421`，导入自 `homeassistant.helpers.entity`，`camera/__init__.py:53`）。
41. `SelectEntity` 继承自 `Entity`（`select/__init__.py:122`，导入自 `homeassistant.helpers.entity`，`select/__init__.py:15`）。
42. `NumberEntity` 继承自 `Entity`（`number/__init__.py`，导入自 `homeassistant.helpers.entity`，`number/__init__.py:28`）。
43. `ButtonEntity` 继承自 `RestoreEntity`（`button/__init__.py:85`，`RestoreEntity` 导入自 `homeassistant.helpers.restore_state`，`button/__init__.py:17`）。
44. `BaseAutomationEntity` 继承自 `ToggleEntity` 和 `ABC`（`automation/__init__.py:319`，`ToggleEntity` 导入自 `homeassistant.helpers.entity`，`automation/__init__.py:53`）。
45. `AutomationEntity` 继承自 `BaseAutomationEntity` 和 `RestoreEntity`（`automation/__init__.py:478`）。
46. `ConversationEntity` 继承自 `RestoreEntity`（`conversation/entity.py:16`）。
47. `ToggleEntity` 是 `Entity` 的子类，为可开关实体提供 `is_on`、`async_turn_on`、`async_turn_off`、`async_toggle` 等基础能力（`light/__init__.py:23`、`switch/__init__.py:20`）。
48. 实体描述类均继承自 `EntityDescription`，如 `LightEntityDescription(ToggleEntityDescription)`（`light/__init__.py:719`）、`SwitchEntityDescription(ToggleEntityDescription)`（`switch/__init__.py:84`）、`SensorEntityDescription(EntityDescription)`（`sensor/__init__.py:111`）。
49. 实体描述类使用 `frozen_or_thawed=True` 参数支持可变/不可变双模式（`light/__init__.py:719`、`sensor/__init__.py:111`、`switch/__init__.py:84`、`binary_sensor/__init__.py:145`）。
50. 实体类使用 `cached_properties=CACHED_PROPERTIES_WITH_ATTR_` 元类参数声明缓存属性集合（`light/__init__.py:741`、`sensor/__init__.py:183`、`switch/__init__.py:95`、`binary_sensor/__init__.py:157`）。

---

## 4. Light 平台

51. `DOMAIN = "light"`（`light/const.py:14`）。
52. `ENTITY_ID_FORMAT = DOMAIN + ".{}"`，即 `"light.{}"`（`light/__init__.py:45`）。
53. `PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA`，平台配置 schema 引用全局基础 schema（`light/__init__.py:46`）。
54. `PLATFORM_SCHEMA_BASE = cv.PLATFORM_SCHEMA_BASE`（`light/__init__.py:47`）。
55. `SCAN_INTERVAL = timedelta(seconds=30)`（`light/const.py:16`）。
56. `ColorMode` 枚举值包括：`UNKNOWN`、`ONOFF`、`BRIGHTNESS`、`COLOR_TEMP`、`HS`、`XY`、`RGB`、`RGBW`、`RGBWW`、`WHITE`（`light/const.py:52-68`）。
57. `ColorMode.ONOFF` 必须是唯一支持的模式（`light/const.py:58` 注释）。
58. `ColorMode.BRIGHTNESS` 必须是唯一支持的模式（`light/const.py:60` 注释）。
59. `ColorMode.WHITE` 不能作为唯一支持的模式（`light/const.py:68` 注释）。
60. `VALID_COLOR_MODES` 集合包含除 `UNKNOWN` 外的所有 9 种颜色模式（`light/const.py:71-81`）。
61. `COLOR_MODES_BRIGHTNESS = VALID_COLOR_MODES - {ColorMode.ONOFF}`，即除 ONOFF 外所有模式均支持亮度（`light/const.py:82`）。
62. `COLOR_MODES_COLOR` 集合包含 `HS`、`RGB`、`RGBW`、`RGBWW`、`XY` 五种彩色模式（`light/const.py:83-89`）。
63. `LightEntityFeature(IntFlag)` 枚举值：`EFFECT = 4`、`FLASH = 8`、`TRANSITION = 32`（`light/const.py:44-49`）。
64. `DEFAULT_MIN_KELVIN = 2000`（对应 500 mireds），`DEFAULT_MAX_KELVIN = 6535`（对应 153 mireds），采用 Philips Hue 默认值（`light/const.py:93-94`）。
65. `ATTR_COLOR_MODE = "color_mode"`，当前颜色模式（`light/__init__.py:51`）。
66. `ATTR_SUPPORTED_COLOR_MODES = "supported_color_modes"`，支持的颜色模式列表（`light/__init__.py:53`）。
67. `ATTR_TRANSITION = "transition"`，过渡时间（秒）（`light/__init__.py:131`）。
68. `ATTR_BRIGHTNESS = "brightness"`，亮度 0..255（`light/__init__.py:146`）。
69. `ATTR_BRIGHTNESS_PCT = "brightness_pct"`，亮度百分比 0..100（`light/__init__.py:147`）。
70. `ATTR_RGB_COLOR = "rgb_color"`，RGB 三元组（`light/__init__.py:134`）。
71. `ATTR_RGBW_COLOR = "rgbw_color"`，RGBW 四元组（`light/__init__.py:135`）。
72. `ATTR_RGBWW_COLOR = "rgbww_color"`，RGBWW 五元组（`light/__init__.py:136`）。
73. `ATTR_XY_COLOR = "xy_color"`，XY 颜色坐标（`light/__init__.py:137`）。
74. `ATTR_HS_COLOR = "hs_color"`，色相/饱和度（`light/__init__.py:138`）。
75. `ATTR_COLOR_TEMP_KELVIN = "color_temp_kelvin"`，色温（开尔文）（`light/__init__.py:139`）。
76. `ATTR_EFFECT = "effect"`，当前效果（`light/__init__.py:163`）。
77. `ATTR_EFFECT_LIST = "effect_list"`，支持的效果列表（`light/__init__.py:160`）。
78. `ATTR_FLASH = "flash"`，闪烁模式（`light/__init__.py:155`）。
79. `FLASH_SHORT = "short"`，`FLASH_LONG = "long"`（`light/__init__.py:156-157`）。
80. `EFFECT_COLORLOOP = "colorloop"`，`EFFECT_OFF = "off"`，`EFFECT_RANDOM = "random"`，`EFFECT_WHITE = "white"`（`light/__init__.py:164-167`）。
81. `VALID_TRANSITION` 验证范围 0..6553 秒（`light/__init__.py:174`）。
82. `VALID_BRIGHTNESS` 验证范围 0..255 整数（`light/__init__.py:175`）。
83. `LightEntity` 的缓存属性集合包含：`brightness`、`color_mode`、`hs_color`、`xy_color`、`rgb_color`、`rgbw_color`、`rgbww_color`、`color_temp_kelvin`、`min_color_temp_kelvin`、`max_color_temp_kelvin`、`effect_list`、`effect`、`supported_color_modes`、`supported_features`（`light/__init__.py:723-738`）。
84. `LightEntity._attr_supported_features` 类型为 `LightEntityFeature`，默认值 `LightEntityFeature(0)`（`light/__init__.py:775`）。
85. `LightEntity._attr_supported_color_modes` 类型为 `set[ColorMode] | None`（`light/__init__.py:774`）。
86. `capability_attributes` 属性返回 `supported_color_modes`、`min/max_color_temp_kelvin`、`effect_list`（`light/__init__.py:873-897`）。
87. Light 平台注册了 `SERVICE_TURN_ON`、`SERVICE_TURN_OFF`、`SERVICE_TOGGLE` 三个实体服务（`light/__init__.py:537-553`）。
88. `filter_supported_color_modes` 函数过滤颜色模式：若 `ONOFF`/`BRIGHTNESS` 与其他模式共存则移除（`light/__init__.py:58-72`）。
89. `brightness_supported` 函数检测是否支持亮度（`light/__init__.py:91-95`）。
90. `color_supported` 函数检测是否支持彩色（`light/__init__.py:98-102`）。
91. `color_temp_supported` 函数检测是否支持色温（`light/__init__.py:105-109`）。

---

## 5. Sensor 平台

92. `DOMAIN = "sensor"`（`sensor/const.py:81`）。
93. `SCAN_INTERVAL = timedelta(seconds=30)`（`sensor/__init__.py:66`）。
94. `SensorDeviceClass(StrEnum)` 非数值设备类：`DATE`、`ENUM`、`TIMESTAMP`、`UPTIME`（`sensor/const.py:107-143`）。
95. `SensorDeviceClass.DATE` 使用 ISO8601 日期格式，无单位（`sensor/const.py:107-113`）。
96. `SensorDeviceClass.ENUM` 提供固定选项列表，无单位（`sensor/const.py:115-121`）。
97. `SensorDeviceClass.TIMESTAMP` 使用 ISO8601 时间戳格式，无单位（`sensor/const.py:123-129`）。
98. `SensorDeviceClass.UPTIME` 表示设备/服务上次重启时间点，自动抑制小漂移（`sensor/const.py:131-143`）。
99. 数值设备类与 NumberDeviceClass 对齐，包括：`ABSOLUTE_HUMIDITY`、`APPARENT_POWER`、`AQI`、`AREA`、`ATMOSPHERIC_PRESSURE`、`BATTERY`、`BLOOD_GLUCOSE_CONCENTRATION`、`CO`、`CO2`、`CONDUCTIVITY`、`CURRENT`、`DATA_RATE`、`DATA_SIZE`、`DISTANCE`、`DURATION`、`ENERGY`、`ENERGY_DISTANCE`、`ENERGY_STORAGE`、`FREQUENCY`、`GAS`、`HUMIDITY`、`ILLUMINANCE`、`IRRADIANCE`、`MOISTURE`、`MONETARY`、`NITROGEN_DIOXIDE`、`NITROGEN_MONOXIDE`、`NITROUS_OXIDE`、`OZONE`、`PH`、`PM1`、`PM10`、`PM25`、`PM4`、`POWER_FACTOR`、`POWER`、`PRECIPITATION`、`PRECIPITATION_INTENSITY`、`PRESSURE`、`REACTIVE_ENERGY`、`REACTIVE_POWER`、`SIGNAL_STRENGTH`、`SOUND_PRESSURE`、`SPEED`、`SULPHUR_DIOXIDE`、`TEMPERATURE`、`TEMPERATURE_DELTA`、`VOLATILE_ORGANIC_COMPOUNDS`、`VOLATILE_ORGANIC_COMPOUNDS_PARTS`、`VOLTAGE`、`VOLUME`、`VOLUME_STORAGE`、`VOLUME_FLOW_RATE`、`WATER`、`WEIGHT`、`WIND_DIRECTION`、`WIND_SPEED`（`sensor/const.py:146-548`）。
100. `SensorDeviceClass.BATTERY` 单位为 `%`（`sensor/const.py:176-180`）。
101. `SensorDeviceClass.TEMPERATURE` 单位为 `°C`、`°F`、`K`（`sensor/const.py:452-456`）。
102. `SensorDeviceClass.HUMIDITY` 单位为 `%`（`sensor/const.py:285-289`）。
103. `SensorDeviceClass.POWER` 单位为 `mW`、`W`、`kW`、`MW`、`GW`、`TW`、`BTU/h`（`sensor/const.py:379-383`）。
104. `SensorDeviceClass.ENERGY` 单位包括 `J`、`kJ`、`Wh`、`kWh`、`MWh`、`cal`、`kcal` 等（`sensor/const.py:239-247`）。
105. `NON_NUMERIC_DEVICE_CLASSES` 集合包含 `DATE`、`ENUM`、`TIMESTAMP`、`UPTIME`（`sensor/const.py:551-556`）。
106. `SensorStateClass(StrEnum)` 枚举值：`MEASUREMENT`、`MEASUREMENT_ANGLE`、`TOTAL`、`TOTAL_INCREASING`（`sensor/const.py:565-585`）。
107. `SensorStateClass.MEASUREMENT` 表示当前时刻的测量值（`sensor/const.py:568-569`）。
108. `SensorStateClass.MEASUREMENT_ANGLE` 表示角度测量值，目前仅支持度（`sensor/const.py:571-575`）。
109. `SensorStateClass.TOTAL` 表示总量，如净能耗（`sensor/const.py:577-580`）。
110. `SensorStateClass.TOTAL_INCREASING` 表示单调递增总量，如消耗燃气量（`sensor/const.py:582-585`）。
111. `SensorEntityDescription` 字段：`device_class`、`last_reset`、`native_unit_of_measurement`、`options`、`state_class`、`suggested_display_precision`、`suggested_unit_of_measurement`（`sensor/__init__.py:111-121`）。
112. `SensorEntity._attr_native_value` 类型为 `StateType | date | datetime | Decimal`，默认 `None`（`sensor/__init__.py:197`）。
113. `SensorEntity._attr_state: None = None`，子类不应直接设置 `_attr_state`（`sensor/__init__.py:200`）。
114. `SensorEntity._attr_unit_of_measurement: None = None`，子类应使用 `native_unit_of_measurement`（`sensor/__init__.py:203-205`）。
115. `capability_attributes` 返回 `state_class` 或 `options`（`sensor/__init__.py:374-384`）。
116. Sensor 平台的 `async_setup` 创建 `EntityComponent[SensorEntity]`，并调用 `async_setup_ws_api`（`sensor/__init__.py:90-98`）。
117. `UPTIME_DEFAULT_TOLERANCE_SECONDS = 60`，uptime 漂移容差默认 60 秒（`sensor/__init__.py:67`）。
118. `UPTIME_MIN_TOLERANCE_SECONDS = 5`，最小容差 5 秒（`sensor/__init__.py:68`）。
119. `UNIT_CONVERTERS` 字典将 `SensorDeviceClass` 映射到对应的 `BaseUnitConverter` 子类（`sensor/const.py:593`）。
120. Sensor 实体不允许 `entity_category == EntityCategory.CONFIG`，否则抛出 `HomeAssistantError`（`sensor/__init__.py:307-311`）。

---

## 6. Switch/BinarySensor 平台

121. Switch `DOMAIN = "switch"`（`switch/__init__.py:25` 导入 `from .const import DOMAIN`）。
122. Switch `SCAN_INTERVAL = timedelta(seconds=30)`（`switch/__init__.py:33`）。
123. `SwitchDeviceClass(StrEnum)` 枚举值：`OUTLET = "outlet"`、`SWITCH = "switch"`（`switch/__init__.py:38-42`）。
124. `SwitchEntity` 继承自 `ToggleEntity`，注册了 `turn_off`、`turn_on`、`toggle` 三个服务（`switch/__init__.py:67-69`）。
125. `SwitchEntityDescription` 包含 `device_class: SwitchDeviceClass | None`（`switch/__init__.py:84-87`）。
126. BinarySensor `DOMAIN = "binary_sensor"`（`binary_sensor/__init__.py:23`）。
127. BinarySensor `SCAN_INTERVAL = timedelta(seconds=30)`（`binary_sensor/__init__.py:28`）。
128. `BinarySensorDeviceClass(StrEnum)` 包含 28 个枚举值：`BATTERY`、`BATTERY_CHARGING`、`CO`、`COLD`、`CONNECTIVITY`、`DOOR`、`GARAGE_DOOR`、`GAS`、`HEAT`、`LIGHT`、`LOCK`、`MOISTURE`、`MOTION`、`MOVING`、`OCCUPANCY`、`OPENING`、`PLUG`、`POWER`、`PRESENCE`、`PROBLEM`、`RUNNING`、`SAFETY`、`SMOKE`、`SOUND`、`TAMPER`、`UPDATE`、`VIBRATION`、`WINDOW`（`binary_sensor/__init__.py:31-116`）。
129. `BinarySensorDeviceClass.BATTERY`：On 表示低电量，Off 表示正常（`binary_sensor/__init__.py:35` 注释）。
130. `BinarySensorDeviceClass.CONNECTIVITY`：On 表示已连接，Off 表示已断开（`binary_sensor/__init__.py:47` 注释）。
131. `BinarySensorDeviceClass.DOOR`：On 表示打开，Off 表示关闭（`binary_sensor/__init__.py:50` 注释）。
132. `BinarySensorDeviceClass.LOCK`：On 表示解锁，Off 表示已锁（`binary_sensor/__init__.py:65` 注释）。
133. `BinarySensorDeviceClass.MOTION`：On 表示检测到运动，Off 表示无运动（`binary_sensor/__init__.py:71` 注释）。
134. `BinarySensorDeviceClass.OCCUPANCY`：On 表示有人占用，Off 表示无人（`binary_sensor/__init__.py:77` 注释）。
135. `BinarySensorDeviceClass.PRESENCE`：On 表示在家，Off 表示离开（`binary_sensor/__init__.py:89` 注释）。
136. `BinarySensorDeviceClass.PROBLEM`：On 表示检测到问题，Off 表示正常（`binary_sensor/__init__.py:92` 注释）。
137. `BinarySensorEntity._attr_is_on: bool | None = None`（`binary_sensor/__init__.py:162`）。
138. `BinarySensorEntity._attr_state: None = None`（`binary_sensor/__init__.py:163`）。
139. BinarySensor 实体不允许 `entity_category == EntityCategory.CONFIG`（`binary_sensor/__init__.py:169-173`）。
140. `MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)` 用于 switch 和 select 平台（`switch/__init__.py:35`、`select/__init__.py:39`）。

---

## 7. Climate/Cover/MediaPlayer 平台

141. Climate `DOMAIN = "climate"`（`climate/const.py:127`）。
142. Climate `SCAN_INTERVAL = timedelta(seconds=60)`（`climate/__init__.py:100`）。
143. `HVACMode(StrEnum)` 枚举值：`OFF`、`HEAT`、`COOL`、`HEAT_COOL`、`AUTO`、`DRY`、`FAN_ONLY`（`climate/const.py:6-29`）。
144. `HVACMode.OFF`：所有活动禁用/设备关闭/待机（`climate/const.py:10` 注释）。
145. `HVACMode.HEAT_COOL`：设备支持加热/冷却到一个范围（`climate/const.py:19` 注释）。
146. `HVACMode.AUTO`：温度由计划/学习行为/AI 设定，用户不可调节（`climate/const.py:23` 注释）。
147. `HVACAction(StrEnum)` 枚举值：`COOLING`、`DEFROSTING`、`DRYING`、`FAN`、`HEATING`、`IDLE`、`OFF`、`PREHEATING`（`climate/const.py:83-93`）。
148. 预设模式常量：`PRESET_NONE`、`PRESET_ECO`、`PRESET_AWAY`、`PRESET_BOOST`、`PRESET_COMFORT`、`PRESET_HOME`、`PRESET_SLEEP`、`PRESET_ACTIVITY`（`climate/const.py:35-56`）。
149. 风扇模式常量：`FAN_ON`、`FAN_OFF`、`FAN_AUTO`、`FAN_LOW`、`FAN_MEDIUM`、`FAN_HIGH`、`FAN_TOP`、`FAN_MIDDLE`、`FAN_FOCUS`、`FAN_DIFFUSE`（`climate/const.py:59-68`）。
150. 摇摆模式常量：`SWING_ON`、`SWING_OFF`、`SWING_BOTH`、`SWING_VERTICAL`、`SWING_HORIZONTAL`（`climate/const.py:72-76`）。
151. `ClimateEntityFeature(IntFlag)` 枚举值：`TARGET_TEMPERATURE=1`、`TARGET_TEMPERATURE_RANGE=2`、`TARGET_HUMIDITY=4`、`FAN_MODE=8`、`PRESET_MODE=16`、`SWING_MODE=32`、`TURN_OFF=128`、`TURN_ON=256`、`SWING_HORIZONTAL_MODE=512`（`climate/const.py:172-183`）。
152. `DEFAULT_MIN_TEMP = 7`，`DEFAULT_MAX_TEMP = 35`（`climate/const.py:122-123`）。
153. `DEFAULT_MIN_HUMIDITY = 30`，`DEFAULT_MAX_HUMIDITY = 99`（`climate/const.py:124-125`）。
154. Climate 注册了 `turn_on`、`turn_off`、`toggle`、`set_hvac_mode`、`set_preset_mode`、`set_temperature`、`set_humidity`、`set_fan_mode`、`set_swing_mode`、`set_swing_horizontal_mode` 共 10 个服务（`climate/__init__.py:133-194`）。
155. `ClimateEntity.state` 属性返回 `hvac_mode.value`（`climate/__init__.py:288-299`）。
156. Cover `DOMAIN = "cover"`（`cover/const.py:5`）。
157. Cover `SCAN_INTERVAL = timedelta(seconds=15)`（`cover/__init__.py:55`）。
158. `CoverDeviceClass(StrEnum)` 枚举值：`AWNING`、`BLIND`、`CURTAIN`、`DAMPER`、`DOOR`、`GARAGE`、`GATE`、`SHADE`、`SHUTTER`、`WINDOW`（`cover/const.py:48-61`）。
159. `CoverEntityFeature(IntFlag)` 枚举值：`OPEN=1`、`CLOSE=2`、`SET_POSITION=4`、`STOP=8`、`OPEN_TILT=16`、`CLOSE_TILT=32`、`STOP_TILT=64`、`SET_TILT_POSITION=128`（`cover/const.py:26-36`）。
160. `CoverState(StrEnum)` 枚举值：`CLOSED`、`CLOSING`、`OPEN`、`OPENING`（`cover/const.py:39-45`）。
161. Cover 注册了 `open_cover`、`close_cover`、`set_cover_position`、`stop_cover`、`toggle`、`open_cover_tilt`、`close_cover_tilt`、`stop_cover_tilt`、`set_cover_tilt_position`、`toggle_cover_tilt` 共 10 个服务（`cover/__init__.py:101-168`）。
162. MediaPlayer `DOMAIN = "media_player"`（`media_player/const.py:44`）。
163. MediaPlayer `SCAN_INTERVAL = timedelta(seconds=10)`（`media_player/__init__.py:130`）。
164. `MediaPlayerDeviceClass(StrEnum)` 枚举值：`TV`、`SPEAKER`、`RECEIVER`、`PROJECTOR`（`media_player/__init__.py:154-160`）。
165. `MediaPlayerState(StrEnum)` 枚举值：`OFF`、`ON`、`IDLE`、`PLAYING`、`PAUSED`、`STANDBY`（已弃用）、`BUFFERING`（`media_player/const.py:57-72`）。
166. `MediaPlayerState.STANDBY` 已弃用，替代为 `OFF` 或 `IDLE`，弃用版本 `2026.8.0`（`media_player/const.py:60-61`）。
167. `MediaClass(StrEnum)` 包含 20 种媒体分类：`ALBUM`、`APP`、`ARTIST`、`CHANNEL`、`COMPOSER`、`CONTRIBUTING_ARTIST`、`DIRECTORY`、`EPISODE`、`GAME`、`GENRE`、`IMAGE`、`MOVIE`、`MUSIC`、`PLAYLIST`、`PODCAST`、`SEASON`、`TRACK`、`TV_SHOW`、`URL`、`VIDEO`（`media_player/const.py:75-97`）。
168. `RepeatMode(StrEnum)` 枚举值：`ALL`、`OFF`、`ONE`（`media_player/const.py:136-141`）。
169. `MediaPlayerEnqueue(StrEnum)` 枚举值：`ADD`、`NEXT`、`PLAY`、`REPLACE`（`media_player/__init__.py:141-151`）。
170. `MediaPlayerEntityFeature(IntFlag)` 部分值：`PAUSE=1`、`SEEK=2`、`VOLUME_SET=4`、`VOLUME_MUTE=8`、`PREVIOUS_TRACK=16`、`NEXT_TRACK=32`、`TURN_ON=128`、`TURN_OFF=256`、`PLAY_MEDIA=512`、`VOLUME_STEP=1024`、`SELECT_SOURCE=2048`、`STOP=4096`、`CLEAR_PLAYLIST=8192`（`media_player/const.py:184-200`）。

---

## 8. Select/Number/Button 等小平台

171. Select `DOMAIN = "select"`（`select/__init__.py:20-29` 从 const 导入）。
172. Select `SCAN_INTERVAL = timedelta(seconds=30)`（`select/__init__.py:37`）。
173. `SelectEntity` 继承自 `Entity`，缓存属性为 `current_option` 和 `options`（`select/__init__.py:116-122`）。
174. `SelectEntityDescription` 包含 `options: list[str] | None = None`（`select/__init__.py:110-113`）。
175. Select 注册了 `select_first`、`select_last`、`select_next`、`select_option`、`select_previous` 五个服务（`select/__init__.py:67-95`）。
176. `SelectEntity.state` 返回 `current_option`，若为 None 或不在 options 中则返回 None（`select/__init__.py:142-150`）。
177. Number `DOMAIN = "number"`（`number/const.py:90`）。
178. Number `SCAN_INTERVAL = timedelta(seconds=30)`（`number/__init__.py:61`）。
179. `DEFAULT_MIN_VALUE = 0.0`，`DEFAULT_MAX_VALUE = 100.0`，`DEFAULT_STEP = 1.0`（`number/const.py:86-88`）。
180. `NumberMode(StrEnum)` 枚举值：`AUTO`、`BOX`、`SLIDER`（`number/const.py:104-109`）。
181. `NumberDeviceClass` 与 `SensorDeviceClass` 数值类对齐（`number/const.py:112-115` 注释）。
182. Number 注册了 `set_value` 服务，值会进行范围校验和原生值转换（`number/__init__.py:96-128`）。
183. Button `DOMAIN = "button"`（`button/__init__.py:22` 从 const 导入）。
184. Button `SCAN_INTERVAL = timedelta(seconds=30)`（`button/__init__.py:30`）。
185. `ButtonDeviceClass(StrEnum)` 枚举值：`IDENTIFY`、`RESTART`、`UPDATE`（`button/__init__.py:35-40`）。
186. `ButtonEntity` 继承自 `RestoreEntity`，`_attr_should_poll = False`（`button/__init__.py:85-89`）。
187. Button 注册了 `press` 服务，调用 `_async_press_action`（`button/__init__.py:55-59`）。
188. Camera `DOMAIN = "camera"`（`camera/__init__.py:67` 从 const 导入）。
189. Camera `SCAN_INTERVAL = timedelta(seconds=30)`（`camera/__init__.py:104`）。
190. `CameraEntityFeature(IntFlag)` 枚举值：`ON_OFF = 1`、`STREAM = 2`（`camera/__init__.py:116-120`）。
191. `DEFAULT_CONTENT_TYPE = "image/jpeg"`（`camera/__init__.py:123`）。
192. `Camera` 基类 `_attr_should_poll = False`，`_attr_state: None = None`（`camera/__init__.py:437-438`）。
193. Camera 注册了 `enable_motion_detection`、`disable_motion_detection`、`snapshot`、`play_stream`、`record`、`turn_on`、`turn_off` 共 7 个服务（`camera/__init__.py:376-394`）。
194. `TOKEN_CHANGE_INTERVAL = timedelta(minutes=5)`，相机访问令牌每 5 分钟更新（`camera/__init__.py:126`）。

---

## 9. setup 与 config_entry 函数模式

195. 每个平台集成均定义 `async_setup(hass: HomeAssistant, config: ConfigType) -> bool` 作为 YAML 配置入口（`light/__init__.py:483`、`sensor/__init__.py:90`、`switch/__init__.py:60`、`binary_sensor/__init__.py:125`、`climate/__init__.py:126`、`cover/__init__.py:93`、`camera/__init__.py:323`、`select/__init__.py:60`、`number/__init__.py:88`、`button/__init__.py:48`、`media_player/__init__.py:280`）。
196. `async_setup` 中创建 `EntityComponent` 实例并存入 `hass.data[DATA_COMPONENT]`（`light/__init__.py:485-487`、`sensor/__init__.py:92-94`、`switch/__init__.py:62-64`）。
197. `DATA_COMPONENT` 使用 `HassKey` 类型安全键，如 `HassKey[EntityComponent[LightEntity]]`（`light/const.py:15`、`sensor/__init__.py:62`、`switch/__init__.py:29`）。
198. `async_setup` 中调用 `await component.async_setup(config)` 完成组件初始化（`light/__init__.py:488`、`sensor/__init__.py:97`、`switch/__init__.py:65`）。
199. `async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool` 是 ConfigEntry 入口，委托给 `hass.data[DATA_COMPONENT].async_setup_entry(entry)`（`light/__init__.py:558-560`、`sensor/__init__.py:101-103`、`switch/__init__.py:74-76`、`binary_sensor/__init__.py:135-137`）。
200. `async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool` 委托给 `hass.data[DATA_COMPONENT].async_unload_entry(entry)`（`light/__init__.py:563-565`、`sensor/__init__.py:106-108`、`switch/__init__.py:79-81`）。
201. Tuya 的 `async_setup_entry` 创建 `DeviceListener`，在 executor 中初始化，存入 `entry.runtime_data`，注册设备，转发平台设置（`tuya/__init__.py:37-68`）。
202. Tuya 使用 `hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)` 批量转发到 18 个平台（`tuya/__init__.py:63`、`tuya/const.py:49-68`）。
203. Tuya 的 `async_unload_entry` 调用 `async_unload_platforms`，停止 MQ 连接，移除设备监听器（`tuya/__init__.py:87-95`）。
204. Tuya 的 `async_remove_entry` 创建 Manager 并调用 `manager.unload()` 撤销凭证（`tuya/__init__.py:98-110`）。
205. Tuya 的 `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)` 标识仅支持 ConfigEntry 配置（`tuya/__init__.py:24`）。
206. zwave_js 的 `async_setup_entry` 创建 `ZwaveClient`，连接服务器（10 秒超时），处理 addon（`zwave_js/__init__.py:177-200`）。
207. zwave_js 转发到 16 个平台：`binary_sensor`、`button`、`climate`、`cover`、`event`、`fan`、`humidifier`、`light`、`lock`、`number`、`select`、`sensor`、`siren`、`switch`、`update`（`zwave_js/__init__.py:145-161`）。
208. ZHA 的 `async_setup` 从 YAML 配置创建 `HAZHAData` 并存入 `hass.data[DATA_ZHA]`（`zha/__init__.py:117-124`）。
209. ZHA 的 `async_setup_entry` 执行设备路径迁移、创建网关配置、初始化 `Gateway`、缓存设备触发器（`zha/__init__.py:135-200`）。
210. ZHA 转发到 15 个平台（`zha/__init__.py:91-107`）。
211. Anthropic 的 `async_setup_entry` 创建 `AnthropicCoordinator`，首次刷新，存入 `runtime_data`，转发到 `ai_task` 和 `conversation` 两个平台（`anthropic/__init__.py:29-36`）。
212. Anthropic 注册 `entry.add_update_listener(async_update_options)` 监听选项变更（`anthropic/__init__.py:38`）。
213. Anthropic 的 `async_update_options` 调用 `hass.config_entries.async_reload` 重新加载条目（`anthropic/__init__.py:62-66`）。
214. `component.async_register_entity_service(service_name, schema, method, [required_features])` 注册实体级服务，第四参数为所需特性列表（`switch/__init__.py:67-69`、`climate/__init__.py:133-194`、`cover/__init__.py:101-168`）。
215. `CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)` 表示空配置 schema，用于 api、websocket_api、default_config（`api/__init__.py:70`、`websocket_api/__init__.py:44`、`default_config/__init__.py:9`）。

---

## 10. config_flow 与 OptionsFlow

216. MQTT ConfigFlow 导入 `ConfigFlow`、`ConfigFlowResult`、`OptionsFlow`、`ConfigSubentryFlow`、`SubentryFlowResult`、`SOURCE_RECONFIGURE`（`mqtt/config_flow.py:63-71`）。
217. MQTT ConfigFlow 支持 TLS 证书配置，导入 `cryptography` 库处理 PEM/DER 格式私钥和证书（`mqtt/config_flow.py:16-23`）。
218. MQTT ConfigFlow 导入所有实体平台的 DeviceClass 用于 discovery schema 验证：`BinarySensorDeviceClass`、`ButtonDeviceClass`、`CoverDeviceClass`、`NumberDeviceClass`、`SensorDeviceClass`、`SensorStateClass`、`SwitchDeviceClass`（`mqtt/config_flow.py:27-61`）。
219. MQTT 支持 Hass.io addon 发现，使用 `AddonManager`、`AddonError`、`AddonState`（`mqtt/config_flow.py:38`）。
220. ConfigFlow 相关常量：`CONF_CLIENT_ID`、`CONF_CODE`、`CONF_HOST`、`CONF_PASSWORD`、`CONF_PORT`、`CONF_PROTOCOL`、`CONF_USERNAME` 等（`mqtt/config_flow.py:72-100`）。
221. `async_migrate_entry(hass, entry)` 函数用于配置条目版本迁移，MQTT 从 1.x 迁移到 2.1（`mqtt/__init__.py:468-497`）。
222. Anthropic 的 `async_migrate_entry` 处理版本 2.1→2.2→2.3 的迁移（`anthropic/__init__.py:177-200`）。
223. Anthropic 迁移使用 `ConfigSubentry` 将多个 API key 条目合并为带子条目的父条目（`anthropic/__init__.py:69-175`）。

---

## 11. platform 转发机制

224. `async_forward_entry_setups(entry, PLATFORMS)` 是标准的多平台转发方法（`tuya/__init__.py:63`、`anthropic/__init__.py:36`）。
225. `async_unload_platforms(entry, PLATFORMS)` 用于卸载已转发的平台（`tuya/__init__.py:89`、`anthropic/__init__.py:59`）。
226. Tuya 的 PLATFORMS 列表包含 18 个平台：`alarm_control_panel`、`binary_sensor`、`button`、`camera`、`climate`、`cover`、`event`、`fan`、`humidifier`、`light`、`number`、`scene`、`select`、`sensor`、`siren`、`switch`、`vacuum`、`valve`（`tuya/const.py:49-68`）。
227. MQTT 的 `ENTITY_PLATFORMS` 包含 31 个平台，是支持平台最多的集成之一（`mqtt/const.py:388-418`）。
228. MQTT 的 `async_forward_entry_setup_and_setup_discovery` 是自定义的转发+发现函数（`mqtt/__init__.py:115`、`mqtt/util.py`）。
229. `platforms_from_config(new_config)` 从 YAML 配置中提取使用的平台集合（`mqtt/__init__.py:118`、`mqtt/__init__.py:434`）。
230. `async_get_platforms(hass, DOMAIN)` 获取已加载的平台实例列表（`mqtt/__init__.py:446`）。

---

## 12. automation 集成

231. Automation `DOMAIN = "automation"`（`automation/__init__.py:92` 从 const 导入）。
232. `BaseAutomationEntity(ToggleEntity, ABC)` 是自动化实体的抽象基类（`automation/__init__.py:319`）。
233. `AutomationEntity(BaseAutomationEntity, RestoreEntity)` 是具体实现类（`automation/__init__.py:478`）。
234. `UnavailableAutomationEntity(BaseAutomationEntity)` 用于验证失败的自动化，状态为 unavailable（`automation/__init__.py:381-388`）。
235. 自动化配置三要素：`CONF_TRIGGERS`（触发器）、`CONF_CONDITIONS`（条件）、`CONF_ACTIONS`（动作）（`automation/__init__.py:22-24`）。
236. 其他配置键：`CONF_ALIAS`（别名）、`CONF_ID`、`CONF_MODE`、`CONF_VARIABLES`、`CONF_TRIGGER_VARIABLES`、`CONF_INITIAL_STATE`、`CONF_TRACE`（`automation/__init__.py:23-30`、`automation/__init__.py:88-91`）。
237. 自动化使用 `Script` 类执行动作序列（`automation/__init__.py:61-69`）。
238. 自动化支持 Blueprint，导入 `CONF_USE_BLUEPRINT`（`automation/__init__.py:14`）。
239. `SERVICE_TRIGGER = "trigger"` 手动触发服务（`automation/__init__.py:114`）。
240. `ATTR_LAST_TRIGGERED = "last_triggered"`（`automation/__init__.py:111`）。
241. `EVENT_AUTOMATION_TRIGGERED = "automation_triggered"`（`automation/__init__.py:109`）。
242. `EVENT_AUTOMATION_RELOADED = "automation_reloaded"`（`automation/__init__.py:108`）。
243. 自动化注册了 `trigger`、`toggle`、`turn_on`、`turn_off`、`reload` 五个服务（`automation/__init__.py:273-312`）。
244. `BaseAutomationEntity` 定义了抽象属性：`referenced_labels`、`referenced_floors`、`referenced_areas`、`referenced_devices`、`referenced_entities`、`referenced_blueprint`（`automation/__init__.py:341-369`）。
245. `BaseAutomationEntity.async_trigger` 是抽象方法，接受 `run_variables`、`context`、`skip_condition` 参数（`automation/__init__.py:371-378`）。
246. `automations_with_entity(hass, entity_id)` 返回引用该实体的所有自动化列表（`automation/__init__.py:158-161`）。
247. `automations_with_device(hass, device_id)` 返回引用该设备的所有自动化（`automation/__init__.py:170-173`）。
248. `automations_with_area(hass, area_id)` 返回引用该区域的所有自动化（`automation/__init__.py:182-185`）。
249. `automations_with_blueprint(hass, blueprint_path)` 返回使用指定 Blueprint 的所有自动化（`automation/__init__.py:218-228`）。
250. `AutomationEntity._attr_should_poll = False`（`automation/__init__.py:481`）。

---

## 13. mqtt 集成

251. MQTT `DOMAIN = "mqtt"`（`mqtt/const.py:88`）。
252. MQTT 使用 `paho-mqtt==2.1.0` 作为底层客户端库（`mqtt/manifest.json:12`）。
253. MQTT 核心客户端类 `MQTT` 从 `.client` 导入（`mqtt/__init__.py:47`）。
254. `async_subscribe(hass, topic, msg_callback, qos=0, encoding="utf-8")` 订阅主题（`mqtt/__init__.py:50`）。
255. `async_publish(hass, topic, payload, qos=0, retain=False)` 发布消息（`mqtt/__init__.py:49`）。
256. `ReceiveMessage` 数据类表示接收到的 MQTT 消息（`mqtt/__init__.py:104`）。
257. `MqttValueTemplate` 和 `MqttCommandTemplate` 处理 Jinja2 模板（`mqtt/__init__.py:99-100`）。
258. `EntitySubscription` 管理实体的主题订阅生命周期（`mqtt/__init__.py:108`）。
259. `async_prepare_subscribe_topics`、`async_subscribe_topics`、`async_unsubscribe_topics` 是订阅管理三函数（`mqtt/__init__.py:109-111`）。
260. MQTT 支持 MQTT 协议 5.0 和 3.1.1：`PROTOCOL_5`、`PROTOCOL_311`（`mqtt/const.py:91-92`）。
261. `DEFAULT_PORT`、`DEFAULT_QOS`、`DEFAULT_RETAIN`、`DEFAULT_PREFIX`、`DEFAULT_ENCODING`、`DEFAULT_DISCOVERY` 为默认值常量（`mqtt/const.py:82-87`）。
262. `CONF_BIRTH_MESSAGE` 和 `CONF_WILL_MESSAGE` 配置出生/遗嘱消息（`mqtt/const.py:65`、`mqtt/const.py:77`）。
263. MQTT 可用性模式：`AVAILABILITY_ALL`、`AVAILABILITY_ANY`、`AVAILABILITY_LATEST`（`mqtt/const.py:20-22`）。
264. `SERVICE_PUBLISH = "publish"` 和 `SERVICE_DUMP = "dump"` 是 MQTT 集成提供的两个服务（`mqtt/__init__.py:200-201`）。
265. `MQTT_PUBLISH_SCHEMA` 验证发布服务参数：`topic`（必填）、`payload`、`qos`、`retain`、`evaluate_payload`、`message_expiry_interval`（`mqtt/__init__.py:244-254`）。
266. `MAX_RECONNECT_WAIT = 300` 秒，最大重连等待时间（`mqtt/__init__.py:205`）。
267. MQTT 配置支持两种 YAML 书写风格：首选列表风格和遗留字典风格（`mqtt/__init__.py:211-241`）。
268. `CONFIG_ENTRY_VERSION = 2`，`CONFIG_ENTRY_MINOR_VERSION` 用于配置条目版本控制（`mqtt/const.py:80-81`）。
269. `MQTT_CONNECTION_STATE` 跟踪连接状态（`mqtt/const.py:90`）。
270. `DATA_MQTT` 和 `DATA_MQTT_AVAILABLE` 是 `hass.data` 键（`mqtt/models.py` 导入，`mqtt/__init__.py:97-98`）。
271. MQTT 注册了 `websocket_subscribe` 和 `websocket_mqtt_info` 两个 WebSocket 命令（`mqtt/__init__.py:336-337`）。
272. `mqtt_config_entry_enabled(hass)` 检查 MQTT 配置条目是否已启用（`mqtt/__init__.py:117`、`mqtt/__init__.py:323`）。
273. `valid_publish_topic` 和 `valid_subscribe_topic` 验证主题格式（`mqtt/__init__.py:119-121`）。

---

## 14. tuya 集成

274. Tuya 使用 `tuya-device-sharing-sdk==0.2.10` 和 `tuya-device-handlers==0.0.24` 两个 Python 包（`tuya/manifest.json:47-48`）。
275. Tuya 的 `Manager` 类从 `tuya_sharing` 包导入（`tuya/__init__.py:5`）。
276. 认证配置常量：`CONF_ENDPOINT`、`CONF_TERMINAL_ID`、`CONF_TOKEN_INFO`、`CONF_USER_CODE`（`tuya/const.py:29-32`）。
277. `TUYA_CLIENT_ID = "HA_3y9q4ak7g4ephrvke"`，Tuya IoT 平台客户端 ID（`tuya/const.py:34`）。
278. `TUYA_SCHEMA = "haauthorize"`，OAuth 授权 schema（`tuya/const.py:35`）。
279. `TUYA_DISCOVERY_NEW = "tuya_discovery_new"`，新设备发现信号（`tuya/const.py:37`）。
280. `TUYA_HA_SIGNAL_UPDATE_ENTITY = "tuya_entry_update"`，实体更新信号（`tuya/const.py:38`）。
281. `DeviceListener` 类负责设备监听，从 `.coordinator` 导入（`tuya/__init__.py:21`）。
282. Tuya 使用 `manager.refresh_mq()` 刷新消息队列连接（`tuya/__init__.py:67`）。
283. Tuya 的 `cleanup_device_registry` 清理设备注册表中不再存在的设备（`tuya/__init__.py:71-84`）。
284. Tuya 使用 `dr.async_entries_for_config_entry` 遍历关联设备（`tuya/__init__.py:76-77`）。
285. Tuya 日志抑制：`logging.getLogger("tuya_sharing").setLevel(logging.CRITICAL)`（`tuya/__init__.py:27`）。
286. `WorkMode(StrEnum)` 包含 `COLOUR`、`MUSIC`、`SCENE`、`WHITE` 四种工作模式（`tuya/const.py:71-77`）。
287. `DeviceCategory(StrEnum)` 定义 Tuya 设备类别代码，如 `AMY`（按摩椅）、`BGL`（壁挂炉）、`BH`（智能水壶）等（`tuya/const.py:80-99`）。

---

## 15. websocket_api

288. WebSocket API `DOMAIN = "websocket_api"`（`websocket_api/const.py:19`）。
289. WebSocket URL 为 `/api/websocket`（`websocket_api/const.py:20`）。
290. `DEPENDENCIES = ("http",)`，依赖 HTTP 集成（`websocket_api/__init__.py:42`）。
291. `async_register_command(hass, command_or_handler, handler=None, schema=None)` 注册 WebSocket 命令（`websocket_api/__init__.py:47-63`）。
292. `@websocket_command(schema)` 装饰器标记函数为 WebSocket 命令处理器，schema 中必须含 `"type"` 键（`websocket_api/decorators.py:131-150`）。
293. `@async_response` 装饰器将 async 函数包装为后台任务调度（`websocket_api/decorators.py:31-51`）。
294. `@require_admin` 装饰器要求用户为管理员，否则抛出 `Unauthorized`（`websocket_api/decorators.py:54-69`）。
295. `@ws_require_user(...)` 装饰器工厂支持细粒度用户验证：`only_owner`、`only_system_user`、`allow_system_user`、`only_active_user`、`only_inactive_user`、`only_supervisor`（`websocket_api/decorators.py:72-128`）。
296. 错误码常量：`ERR_ID_REUSE`、`ERR_INVALID_FORMAT`、`ERR_NOT_ALLOWED`、`ERR_NOT_FOUND`、`ERR_NOT_SUPPORTED`、`ERR_HOME_ASSISTANT_ERROR`、`ERR_SERVICE_VALIDATION_ERROR`、`ERR_UNKNOWN_COMMAND`、`ERR_UNKNOWN_ERROR`、`ERR_UNAUTHORIZED`、`ERR_TIMEOUT`、`ERR_TEMPLATE_ERROR`（`websocket_api/const.py:35-46`）。
297. `TYPE_RESULT = "result"`（`websocket_api/const.py:48`）。
298. `MAX_PENDING_MSG = 4096`，最大待处理消息数（`websocket_api/const.py:29`）。
299. `PENDING_MSG_PEAK = 1024`（`websocket_api/const.py:21`）。
300. WebSocket 命令处理器类型签名：`Callable[[HomeAssistant, ActiveConnection, dict[str, Any]], None]`（`websocket_api/const.py:12-14`）。
301. 异步命令处理器类型签名：`Callable[[HomeAssistant, ActiveConnection, dict[str, Any]], Awaitable[None]]`（`websocket_api/const.py:15-17`）。
302. `commands.async_register_commands(hass, async_register_command)` 在 setup 时注册核心命令集（`websocket_api/__init__.py:69`）。
303. 信号 `SIGNAL_WEBSOCKET_CONNECTED` 和 `SIGNAL_WEBSOCKET_DISCONNECTED`（`websocket_api/const.py:52-53`）。
304. `FEATURE_COALESCE_MESSAGES = "coalesce_messages"` 特性标识（`websocket_api/const.py:58`）。

---

## 16. AI/Assist 集成

305. `assist_pipeline` 是系统级集成，`integration_type = "system"`，`iot_class = "local_push"`（`assist_pipeline/manifest.json:8-9`）。
306. assist_pipeline 依赖：`conversation`、`stt`、`tts`、`wake_word`（`assist_pipeline/manifest.json:6`）。
307. `Pipeline` 类表示一条 Assist 管道，从 `.pipeline` 导入（`assist_pipeline/__init__.py:28`）。
308. `PipelineStage` 枚举定义管道阶段：`STT`（语音转文字）到 `TTS`（文字转语音）（`assist_pipeline/__init__.py:34`、`assist_pipeline/__init__.py:109-110`）。
309. `PipelineInput` 封装管道输入，包含 `session`、`device_id`、`satellite_id`、`stt_metadata`、`stt_stream`、`wake_word_phrase` 等（`assist_pipeline/__init__.py:118-137`）。
310. `async_pipeline_from_audio_stream` 从音频流创建并执行管道（`assist_pipeline/__init__.py:94-138`）。
311. 音频参数：`SAMPLE_RATE`、`SAMPLE_WIDTH`、`SAMPLE_CHANNELS`、`SAMPLES_PER_CHUNK`（`assist_pipeline/__init__.py:21-23`）。
312. `conversation` 集成 `integration_type = "entity"`，提供对话实体平台（`conversation/manifest.json:7`）。
313. conversation 依赖 `http` 和 `intent`（`conversation/manifest.json:5`）。
314. `AbstractConversationAgent(ABC)` 是对话代理抽象基类（`conversation/models.py:91`）。
315. `AbstractConversationAgent.supported_languages` 返回 `list[str] | Literal["*"]`（`conversation/models.py:94-97`）。
316. `AbstractConversationAgent.async_process(user_input: ConversationInput) -> ConversationResult` 是核心处理方法（`conversation/models.py:99-101`）。
317. `ConversationInput` 数据类字段：`text`、`context`、`conversation_id`、`device_id`、`satellite_id`、`language`、`agent_id`、`extra_system_prompt`（`conversation/models.py:22-48`）。
318. `ConversationResult` 数据类字段：`response: intent.IntentResponse`、`conversation_id`、`continue_conversation`（`conversation/models.py:74-88`）。
319. `AgentInfo` 数据类字段：`id`、`name`、`supports_streaming`（`conversation/models.py:13-19`）。
320. `async_set_agent(hass, config_entry, agent)` 将代理注册到配置条目（`conversation/__init__.py:125-132`）。
321. `async_unset_agent(hass, config_entry)` 取消注册（`conversation/__init__.py:135-141`）。
322. `HOME_ASSISTANT_AGENT` 是内置代理 ID 常量（`conversation/__init__.py:52`）。
323. `SERVICE_PROCESS_SCHEMA` 验证 `text`（必填）、`language`、`agent_id`、`conversation_id`（`conversation/__init__.py:94-101`）。
324. `ConversationEntity(RestoreEntity)` 是对话实体基类，`_attr_should_poll = False`（`conversation/entity.py:16-19`）。
325. `ConversationEntity` 有 `supports_streaming` 属性（`conversation/entity.py:24-27`）。
326. `ChatLog` 类管理对话日志，内容类型包括 `UserContent`、`AssistantContent`、`SystemContent`、`ToolResultContent`（`conversation/__init__.py:32-44`）。
327. Anthropic 集成 `integration_type = "service"`，`iot_class = "cloud_polling"`，`config_flow = true`（`anthropic/manifest.json:6,9-10`）。
328. Anthropic 依赖 `conversation` 集成，后置依赖 `assist_pipeline` 和 `intent`（`anthropic/manifest.json:4,7`）。
329. Anthropic 转发到 `Platform.AI_TASK` 和 `Platform.CONVERSATION` 两个平台（`anthropic/__init__.py:19`）。
330. Anthropic 使用 `AnthropicCoordinator` 数据协调器（`anthropic/__init__.py:17,31`）。
331. Anthropic 配置迁移使用子条目（`ConfigSubentry`），`subentry_type="conversation"`（`anthropic/__init__.py:86-91`）。
332. Alexa 集成为云智能音箱提供 Smart Home API 端点（`alexa/__init__.py:1`）。
333. Alexa 配置包含 `flash_briefings`（闪电简报）和 `smart_home`（智能家居）两大块（`alexa/__init__.py:34-35,68-92`）。
334. Alexa Smart Home 支持三个区域端点：美国、欧洲、远东（`alexa/__init__.py:40-44`）。
335. `DEFAULT_LOCALE = "en-US"`（`alexa/__init__.py:36`）。
336. Alexa Smart Home schema 包含 `endpoint`、`client_id`、`client_secret`、`locale`、`filter`、`entity_config`（`alexa/__init__.py:55-66`）。
337. Google Assistant 集成支持 Actions on Google Smart Home 控制（`google_assistant/__init__.py:1`）。
338. Google Assistant 配置必需 `project_id`，可选 `expose_by_default`、`exposed_domains`、`entity_config`、`secure_devices_pin`、`report_state`、`service_account`（`google_assistant/__init__.py:69-91`）。
339. Google Assistant 转发到 `Platform.BUTTON` 平台（`google_assistant/__init__.py:43`）。
340. Google Assistant 使用 service account（`private_key` + `client_email`）进行报告状态认证（`google_assistant/__init__.py:54-60`）。
341. 若 `report_state` 启用但未提供 service account，配置校验失败（`google_assistant/__init__.py:63-66`）。

---

## 17. default_config 与系统集成

342. `default_config` 是系统集成，`integration_type = "system"`，`quality_scale = "internal"`（`default_config/manifest.json:29-30`）。
343. default_config 的 `async_setup` 直接返回 `True`，本身不做初始化，仅通过 dependencies 拉取其他集成（`default_config/__init__.py:12-14`）。
344. default_config 使用 `cv.empty_config_schema(DOMAIN)` 空配置 schema（`default_config/__init__.py:9`）。
345. API 集成 `DOMAIN = "api"`，提供 REST API（`api/__init__.py:65`）。
346. API 注册了 13 个 HTTP 视图：`APIStatusView`、`APICoreStateView`、`APIEventStream`、`APIConfigView`、`APIStatesView`、`APIEntityStateView`、`APIEventListenersView`、`APIEventView`、`APIServicesView`、`APIDomainServicesView`、`APIComponentsView`、`APITemplateView`、`APIErrorLog`（`api/__init__.py:75-89`）。
347. `APIEventStream` 提供 SSE（Server-Sent Events）流，`content_type = "text/event-stream"`（`api/__init__.py:127-191`）。
348. `STREAM_PING_INTERVAL = 50` 秒，SSE 心跳间隔（`api/__init__.py:67`）。
349. `SERVICE_WAIT_TIMEOUT = 10`，服务调用超时（`api/__init__.py:68`）。
350. Frontend 集成 `DOMAIN = "frontend"`，管理 Web 前端（`frontend/__init__.py:46`）。
351. Frontend 支持主题配置：`CONF_THEMES`，含 light/dark 双模式（`frontend/__init__.py:48-51,114-127`）。
352. Frontend 支持开发模式：`CONF_FRONTEND_REPO`、`CONF_DEVELOPMENT_PR`、`CONF_GITHUB_TOKEN`（`frontend/__init__.py:56-59`）。
353. Frontend 支持额外模块 URL：`CONF_EXTRA_MODULE_URL`、`CONF_EXTRA_JS_URL_ES5`（`frontend/__init__.py:54-55`）。
354. Frontend 提供 `SERVICE_SET_THEME` 和 `SERVICE_RELOAD_THEMES` 两个服务（`frontend/__init__.py:169-170`）。
355. Frontend 使用 `Store` 持久化主题和面板配置（`frontend/__init__.py:74-85`）。
356. `DATA_PANELS` 存储注册的面板字典（`frontend/__init__.py:66`）。
357. `DEFAULT_THEME_COLOR = "#2980b9"`（`frontend/__init__.py:63`）。
358. zwave_js 依赖 `http`、`repairs`、`usb`、`websocket_api`（`zwave_js/manifest.json:7`）。
359. zwave_js 使用 `ZwaveClient` 连接到 zwave-js-server，`CONNECT_TIMEOUT = 10` 秒（`zwave_js/__init__.py:182-191`）。
360. zwave_js 定义 `DRIVER_READY_TIMEOUT = 60` 秒（`zwave_js/__init__.py:139`）。
361. zwave_js 自定义事件：`EVENT_VALUE_ADDED`、`EVENT_VALUE_UPDATED`、`EVENT_DEVICE_ADDED_TO_REGISTRY`、`EVENT_METADATA_UPDATED`（`zwave_js/__init__.py:110-113`）。
362. ZHA 依赖 `zigpy` 和 `zha` 库，支持多种 RadioType（`zha/__init__.py:9-13`）。
363. ZHA 配置支持 `baudrate`、`database`、`device_config`、`enable_quirks`、`zigpy`、`radio_type`、`usb_path`、`custom_quirks_path`（`zha/__init__.py:65-76`）。
364. ZHA 使用 `Gateway.async_from_config(zha_lib_data)` 创建网关（`zha/__init__.py:159`）。
365. ZHA 注册固件信息提供者 `async_register_firmware_info_provider`（`zha/__init__.py:122`）。
366. 所有平台集成均使用 `EntityComponent` 作为实体管理核心，从 `homeassistant.helpers.entity_component` 导入（`light/__init__.py:24`、`sensor/__init__.py:26`、`switch/__init__.py:21` 等）。
367. `cv.PLATFORM_SCHEMA` 和 `cv.PLATFORM_SCHEMA_BASE` 是所有平台的标准配置 schema 基础（各平台 `__init__.py` 中均有引用）。
368. `propcache.api.cached_property` 是 HA 使用的缓存属性装饰器，替代标准库 `functools.cached_property`（`light/__init__.py:10`、`sensor/__init__.py:13`、`switch/__init__.py:8` 等）。
369. `voluptuous as vol` 是 HA 统一使用的数据验证库（`light/__init__.py:11`、`sensor/__init__.py` 未直接导入但通过 cv 使用等）。
370. `homeassistant.helpers.config_validation as cv` 提供 HA 专用验证器（`light/__init__.py:22`、`sensor/__init__.py:24` 等）。
371. `HassKey` 提供类型安全的 `hass.data` 键，从 `homeassistant.util.hass_dict` 导入（`sensor/__init__.py:32`、`switch/__init__.py:23`、`cover/__init__.py:30` 等）。
372. `EntityCategory.CONFIG` 类别的实体不能作为 sensor/binary_sensor 添加（`sensor/__init__.py:307-311`、`binary_sensor/__init__.py:169-173`）。
373. `@callback` 装饰器标记函数为事件循环回调，从 `homeassistant.core` 导入（`light/__init__.py:20`、`binary_sensor/__init__.py` 未直接导入等）。
374. `@final` 装饰器防止方法被子类重写，用于 `state` 属性等（`sensor/__init__.py:336-337`、`binary_sensor/__init__.py:198-199`、`climate/__init__.py:288-289`、`select/__init__.py:143-144`）。
375. `@override` 装饰器标记方法重写父类方法（`light/__init__.py:8`、`sensor/__init__.py:11`、`switch/__init__.py:6` 等）。
