# Home Assistant Core 核心架构事实清单

> 源码基准路径：`d:\AI\.chaos\libs\home-assistant\core\homeassistant\`
> 以下行号均基于该基准路径的相对文件。零推测。

---

## 1. 版本与常量

1. `APPLICATION_NAME` 常量值为 `"HomeAssistant"`（const.py:22）
2. `MAJOR_VERSION` 为 `2026`，`MINOR_VERSION` 为 `8`，`PATCH_VERSION` 为 `"0.dev0"`（const.py:23-25）
3. `__short_version__` 由 f-string 拼接为 `f"{MAJOR_VERSION}.{MINOR_VERSION}"`（const.py:26）
4. `__version__` 为 `f"{__short_version__}.{PATCH_VERSION}"`（const.py:27）
5. `REQUIRED_PYTHON_VER` 要求 Python 版本 `(3, 14, 2)`（const.py:28）
6. `PLATFORM_FORMAT` 格式为 `"{platform}.{domain}"`（const.py:31）
7. `Platform` 直接重导出自 `EntityPlatforms`（const.py:34）
8. `BASE_PLATFORMS` 是所有 `Platform` 枚举值的集合（const.py:36）
9. `MATCH_ALL` 常量为 `"*"`，用于注册通配事件监听器（const.py:40）
10. 实体匹配常量：`ENTITY_MATCH_NONE="none"`、`ENTITY_MATCH_ALL="all"`、`ENTITY_MATCH_ANY="any"`（const.py:43-45）
11. `DEVICE_DEFAULT_NAME` 为 `"Unnamed Device"`（const.py:48）
12. 记录器存储最大长度限制：事件类型 64 字符、事件来源 32 字符、上下文 ID 36 字符（const.py:52-54）
13. 状态最大长度限制：domain 64、entity_id 255、state 255（const.py:55-57）
14. 太阳事件常量：`SUN_EVENT_SUNSET="sunset"`、`SUN_EVENT_SUNRISE="sunrise"`（const.py:60-61）
15. 配置键 `CONF_*` 系列从 `CONF_ABOVE` 到 `CONF_ZONE` 共 200+ 个字符串常量（const.py:64-264）
16. 核心事件类型 `EVENT_CALL_SERVICE="call_service"`（const.py:267）
17. `EVENT_COMPONENT_LOADED="component_loaded"`（const.py:268）
18. `EVENT_CORE_CONFIG_UPDATE="core_config_updated"`（const.py:269）
19. `EVENT_HOMEASSISTANT_CLOSE` 使用 `EventType` 包装，值为 `"homeassistant_close"`（const.py:270）
20. `EVENT_HOMEASSISTANT_START` 值为 `"homeassistant_start"`（const.py:271）
21. `EVENT_HOMEASSISTANT_STARTED` 值为 `"homeassistant_started"`（const.py:272）
22. `EVENT_HOMEASSISTANT_STOP` 值为 `"homeassistant_stop"`（const.py:273）
23. `EVENT_HOMEASSISTANT_FINAL_WRITE` 值为 `"homeassistant_final_write"`（const.py:274-276）
24. `EVENT_SERVICE_REGISTERED="service_registered"`、`EVENT_SERVICE_REMOVED="service_removed"`（const.py:280-281）
25. `EVENT_STATE_CHANGED` 为 `EventType[EventStateChangedData]`，值 `"state_changed"`（const.py:282）
26. `EVENT_STATE_REPORTED` 为 `EventType[EventStateReportedData]`，值 `"state_reported"`（const.py:283）
27. 基础状态常量：`STATE_ON="on"`、`STATE_OFF="off"`、`STATE_HOME="home"`、`STATE_NOT_HOME="not_home"`、`STATE_UNKNOWN="unknown"`、`STATE_OPEN="open"`（const.py:295-300）
28. core.py 顶部定义关闭阶段超时：`STOPPING_STAGE_SHUTDOWN_TIMEOUT=20`、`STOP_STAGE_SHUTDOWN_TIMEOUT=100`、`FINAL_WRITE_STAGE_SHUTDOWN_TIMEOUT=60`、`CLOSE_STAGE_SHUTDOWN_TIMEOUT=30`（core.py:111-114）
29. `DOMAIN` 常量为 `"homeassistant"`（core.py:121）
30. `BLOCK_LOG_TIMEOUT` 为 60 秒，用于记录阻塞任务的等待阈值（core.py:124）
31. `TIMEOUT_EVENT_START` 为 15 秒，启动阶段等待任务完成的超时（core.py:158）
32. `EVENTS_EXCLUDED_FROM_MATCH_ALL` 包含 `EVENT_HOMEASSISTANT_CLOSE` 和 `EVENT_STATE_REPORTED`（core.py:161-164）

---

## 2. CoreState 与启动状态

33. `CoreState` 是 `enum.Enum` 子类（core.py:363）
34. `CoreState.not_running` 值为 `"NOT_RUNNING"`（core.py:366）
35. `CoreState.starting` 值为 `"STARTING"`（core.py:367）
36. `CoreState.running` 值为 `"RUNNING"`（core.py:368）
37. `CoreState.stopping` 值为 `"STOPPING"`（core.py:369）
38. `CoreState.final_write` 值为 `"FINAL_WRITE"`（core.py:370）
39. `CoreState.stopped` 值为 `"STOPPED"`（core.py:371）
40. `CoreState.__str__` 返回 `self.value`（core.py:373-376）
41. `ReleaseChannel` 是 `enum.StrEnum`，包含 BETA/DEV/NIGHTLY/STABLE 四个频道（core.py:263-269）
42. `get_release_channel()` 根据版本号判断发布频道：含 `dev0` 为 DEV，含 `dev` 为 NIGHTLY，含 `b` 为 BETA，否则 STABLE（core.py:272-282）
43. `HassJobType` 枚举包含 `Coroutinefunction=1`、`Callback=2`、`Executor=3`（core.py:285-291）
44. HomeAssistant 初始化时 `self.state` 设置为 `CoreState.not_running`（core.py:410）
45. `is_running` 缓存属性在 state 为 `starting` 或 `running` 时返回 True（core.py:443-446）
46. `is_stopping` 缓存属性在 state 为 `stopping` 或 `final_write` 时返回 True（core.py:448-451）
47. `set_state()` 方法更新状态后清除 `is_running` 和 `is_stopping` 的缓存（core.py:453-457）
48. `async_start()` 首先设置状态为 `starting`，触发 `EVENT_CORE_CONFIG_UPDATE` 和 `EVENT_HOMEASSISTANT_START`（core.py:505-507）
49. `async_start()` 等待 `_tasks` 最多 `TIMEOUT_EVENT_START`(15秒)，超时则警告（core.py:509-527）
50. `async_start()` 完成后设置状态为 `running`，触发 `EVENT_CORE_CONFIG_UPDATE` 和 `EVENT_HOMEASSISTANT_STARTED`（core.py:536-538）
51. `async_stop()` 分四个阶段：shutdown jobs → stop integrations(stopping) → final_write → close(not_running)（core.py:1084-1147）
52. `async_stop()` 在 stopping 阶段触发 `EVENT_HOMEASSISTANT_STOP`（core.py:1122）
53. `async_stop()` 在 final_write 阶段触发 `EVENT_HOMEASSISTANT_FINAL_WRITE`（core.py:1134）
54. `async_stop()` 在 close 阶段触发 `EVENT_HOMEASSISTANT_CLOSE`（core.py:1147）
55. `async_run()` 是主入口，创建 `_stopped` Event，调用 `async_start()` 后等待停止信号（core.py:476-496）

---

## 3. HomeAssistant 核心对象

56. `HomeAssistant` 类是 HA 自动化框架的根对象（core.py:379-380）
57. `HomeAssistant.auth` 类型注解为 `AuthManager`（core.py:382）
58. `HomeAssistant.http` 类型为 `HomeAssistantHTTP`，默认 None（core.py:383）
59. `HomeAssistant.config_entries` 类型为 `ConfigEntries`，默认 None（core.py:384）
60. `__new__` 方法将实例设置到线程局部变量 `_hass.hass`（core.py:386-390）
61. `__init__` 接收 `config_dir: str` 参数（core.py:397）
62. `self.data` 是 `HassDict()` 实例，供任何组件存储任意数据（core.py:401）
63. `self.loop` 通过 `asyncio.get_running_loop()` 获取（core.py:402）
64. `self._tasks` 和 `self._background_tasks` 是 `set[asyncio.Future]`（core.py:403-404）
65. `self.bus` 是 `EventBus(self)` 实例（core.py:405）
66. `self.services` 是 `ServiceRegistry(self)` 实例（core.py:406）
67. `self.states` 是 `StateMachine(self.bus, self.loop)` 实例（core.py:407）
68. `self.config` 是 `Config(self, config_dir)` 实例（core.py:408）
69. `self.config.async_initialize()` 在 `__init__` 中立即调用（core.py:409）
70. `self.exit_code` 初始化为 0（core.py:411）
71. `self._stopped` 是 `asyncio.Event | None`，用于信号结束（core.py:413）
72. `self.timeout` 是 `TimeoutManager()` 实例（core.py:415）
73. `self.import_executor` 是 `InterruptibleThreadPoolExecutor`，max_workers=1，线程名前缀 `"ImportExecutor"`（core.py:418-420）
74. `self.loop_thread_id` 记录事件循环线程 ID（core.py:421）
75. `verify_event_loop_thread()` 检查当前线程是否为事件循环线程，否则报告非线程安全操作（core.py:423-429）
76. `add_job()` 是线程安全方法，根据 target 类型（协程/callback/普通函数）调度到事件循环或执行器（core.py:540-570）
77. `async_add_job()` 在事件循环中添加任务，支持协程函数和 callback（core.py:599-635）
78. `async_create_task()` 创建被追踪的任务，集成应使用 config entry 的创建方法（core.py:763-781）
79. `async_create_task_internal()` 是内部使用的任务创建方法，不保证 API 稳定（core.py:783-798）
80. `async_block_till_done()` 先 `await asyncio.sleep(0)` 刷新 call_soon_threadsafe，然后循环等待所有非取消任务（core.py:972-987）
81. `async_add_shutdown_job()` 注册关闭时执行的 HassJob，返回移除函数（core.py:1029-1049）
82. `_active_tasks` 属性返回 `self._tasks`，供 bootstrap 记录阻塞任务（core.py:431-441）
83. `async_get_hass()` 从线程局部变量获取 HomeAssistant 实例，错误线程抛出 `HomeAssistantError`（core.py:241-252）
84. `async_get_hass_or_none()` 返回实例或 None（core.py:255-260）

---

## 4. Event 与 EventBus

85. `Context` 类使用 `__slots__` 限定属性：`_cache`、`id`、`origin_event`、`parent_id`、`user_id`（core.py:1221）
86. `Context.__init__` 接收 `user_id`、`parent_id`、`id`，`id` 默认通过 `ulid_now()` 生成（core.py:1223-1230）
87. `Context.origin_event` 初始为 None，在 Event 构造时设置（core.py:1233, 1323-1324）
88. Context 的相等性基于 `id` 比较（core.py:1237-1239）
89. `Context.as_dict()` 返回 `ReadOnlyDict`，包含 id/parent_id/user_id（core.py:1262-1264）
90. `EventOrigin` 枚举有 `local="LOCAL"` 和 `remote="REMOTE"` 两个值（core.py:1277-1281）
91. `EventOrigin.idx` 缓存属性返回枚举序号（core.py:1288-1291）
92. `Event` 类被 `@final` 装饰，禁止子类化（core.py:1294）
93. `Event` 是泛型类 `Generic[_DataT]`（core.py:1295）
94. Event 使用 `__slots__`：`_cache`、`context`、`data`、`event_type`、`origin`、`time_fired_timestamp`（core.py:1298-1305）
95. Event 构造时若未提供 context，则创建一个 id 基于 `ulid_at_time(time_fired_timestamp)` 的 Context（core.py:1320-1322）
96. `Event.time_fired` 缓存属性通过 `dt_util.utc_from_timestamp` 转换时间戳（core.py:1327-1330）
97. `Event.as_dict()` 返回 ReadOnlyDict，包含 event_type/data/origin/time_fired/context（core.py:1350-1355）
98. `Event.json_fragment` 返回 JSON 序列化片段（core.py:1373-1376）
99. `_OneTimeListener` 是 dataclass，包装一次性监听器，触发后自动移除（core.py:1400-1422）
100. `_verify_event_type_length_or_raise()` 使用 `lru_cache`，事件类型超过 64 字符抛出 `MaxLengthExceeded`（core.py:1429-1433）
101. `_MAX_QUEUED_EVENT_DISPATCHES` 限制为 10,000，防止事件监听器无限循环触发事件（core.py:1439）
102. `EventBus` 使用 `__slots__`：`_debug`、`_dispatching`、`_event_queue`、`_hass`、`_listeners`、`_match_all_listeners`、`_queued_event_count`（core.py:1445-1453）
103. `EventBus.__init__` 中 `_listeners` 是 `defaultdict(list)`，`MATCH_ALL` 键映射到 `_match_all_listeners`（core.py:1457-1461）
104. EventBus 构造时自动监听 `EVENT_LOGGING_CHANGED` 事件以更新 debug 标志（core.py:1468-1469）
105. `fire()` 是线程安全方法，通过 `call_soon_threadsafe` 调度 `async_fire_internal`（core.py:1489-1500）
106. `async_fire()` 要求在事件循环线程中调用，否则报告非线程安全操作（core.py:1502-1522）
107. `async_fire_internal()` 是核心内部方法，嵌套触发时入队，超过 10,000 抛出 `HomeAssistantError`（core.py:1524-1566）
108. `_async_dispatch()` 遍历特定类型监听器和 match_all 监听器，支持 event_filter 过滤（core.py:1578-1616）
109. `EVENT_STATE_REPORTED` 事件必须提供 event_filter，否则抛出 `HomeAssistantError`（core.py:1674-1678）
110. event_filter 必须是 callback 装饰的函数，否则抛出 `HomeAssistantError`（core.py:1671-1672）
111. `async_listen()` 返回 `CALLBACK_TYPE`（移除监听器的函数）（core.py:1638-1679）
112. `async_listen_once()` 注册一次性监听器，通过 `_OneTimeListener` 包装（core.py:1715-1756）
113. `_async_remove_listener()` 从列表移除监听器，空列表时删除事件类型键（MATCH_ALL 除外）（core.py:1758-1779）
114. `EventStateChangedData` TypedDict 包含 `entity_id`、`new_state: State | None`、`old_state: State | None`（core.py:136-143）
115. `EventStateReportedData` TypedDict 包含 `entity_id`、`last_reported`、`new_state: State`、`old_last_reported`（core.py:146-154）

---

## 5. State 与 StateMachine

116. `State` 类公开属性：`entity_id`、`domain`、`object_id`、`state`、`attributes`、`last_changed`、`last_reported`、`last_updated`、`context`（core.py:1795-1824）
117. State 使用 `__slots__` 包含 `state_info` 和 `last_updated_timestamp`（core.py:1826-1839）
118. State 构造时 `validate_entity_id=True` 会校验实体 ID 格式，无效则抛出 `InvalidEntityFormatError`（core.py:1856-1860）
119. State 的 state 值若非 str 则通过 `str()` 转换（core.py:1862）
120. attributes 若非 ReadOnlyDict 则包装为 ReadOnlyDict（core.py:1866-1869）
121. `last_reported` 默认为 `dt_util.utcnow()`，`last_updated` 默认同 `last_reported`，`last_changed` 默认同 `last_updated`（core.py:1870-1872）
122. State 构造时通过 `split_entity_id` 拆分 domain 和 object_id（core.py:1875）
123. `State.name` 缓存属性返回 attributes 中的 friendly_name 或 object_id 替换下划线（core.py:1891-1896）
124. `State.as_compressed_state` 构建压缩字典，键为 s/a/c/lc/lu（core.py:1987-2014）
125. 当 context 无 parent_id 和 user_id 时，压缩状态中 context 仅为 id 字符串（core.py:1996-1997）
126. `State.from_dict()` 类方法从字典反序列化，解析 ISO 格式时间字符串（core.py:2026-2060）
127. `State.expire()` 用相同 id 的新 Context 替换原 context，允许旧 context 被垃圾回收（core.py:2062-2078）
128. `States` 继承 `UserDict[str, State]`，维护 `domain -> dict[str, State]` 的二级索引（core.py:2091-2101）
129. `States.__setitem__` 同时更新主字典和 domain 索引（core.py:2109-2112）
130. `States.__delitem__` 同时从主字典和 domain 索引删除（core.py:2115-2119）
131. `States.domain_entity_ids()` 返回指定 domain 的实体 ID 视图（core.py:2121-2126）
132. `States.domain_states()` 返回指定 domain 的 State 视图（core.py:2128-2133）
133. `StateMachine` 使用 `__slots__`：`_bus`、`_loop`、`_reservations`、`_states`、`_states_data`（core.py:2139）
134. `StateMachine.__init__` 创建 `States()` 实例并缓存 `_states.data` 引用以加速读取（core.py:2141-2149）
135. `async_reserve()` 为即将添加的实体预留状态，防止竞态条件（core.py:2299-2314）
136. `async_available()` 检查 entity_id 是否可用（不在状态机也不在预留中）（core.py:2316-2322）
137. `async_remove()` 删除实体状态，触发 `EVENT_STATE_CHANGED`，new_state 为 None（core.py:2246-2272）
138. `async_set()` 是核心方法，验证 state 长度后调用 `async_set_internal`（core.py:2324-2354）
139. `async_set_internal()` 中，若 state 和 attributes 都未变且非 force_update，更新 last_reported 并触发 `EVENT_STATE_REPORTED`（core.py:2411-2428）
140. state 或 attributes 变化时，创建新 State 对象，旧 State 调用 `expire()`，触发 `EVENT_STATE_CHANGED`（core.py:2447-2472）
141. 新 state 超过 255 字符时记录错误并回退为 `STATE_UNKNOWN`（core.py:2435-2443）
142. `get()` 方法先按原 entity_id 查找，再按小写查找（core.py:2220-2227）
143. `is_state()` 检查实体是否存在且处于指定状态（core.py:2229-2235）
144. `validate_state()` 函数检查 state 长度不超过 `MAX_LENGTH_STATE_STATE`(255)，否则抛出 `InvalidStateError`（core.py:199-206）
145. `split_entity_id()` 使用 `lru_cache(MAX_EXPECTED_ENTITY_IDS)` 缓存拆分结果（core.py:169-175）
146. `valid_entity_id()` 使用 `lru_cache(512)` 缓存校验结果（core.py:190-196）
147. 实体 ID 格式正则：`<domain>.<object_id>`，两者均为 slug 格式（core.py:178-181）

---

## 6. Service 与 ServiceRegistry

148. `SupportsResponse` 是 `enum.StrEnum`，包含 NONE/OPTIONAL/ONLY 三个值（core.py:2475-2485）
149. `SupportsResponse.NONE` 表示服务不支持响应（默认）（core.py:2478-2479）
150. `SupportsResponse.OPTIONAL` 表示服务可选返回响应数据（core.py:2481-2482）
151. `SupportsResponse.ONLY` 表示服务只读且调用方必须请求响应（core.py:2484-2485）
152. `Service` 类使用 `__slots__`：`description_placeholders`、`job`、`schema`、`supports_response`（core.py:2491-2496）
153. `Service.__init__` 创建 `HassJob(func, f"service {domain}.{service}")`（core.py:2516）
154. `ServiceCall` 使用 `__slots__`：`context`、`data`、`domain`、`hass`、`return_response`、`service`（core.py:2525）
155. ServiceCall 的 data 包装为 `ReadOnlyDict`（core.py:2540）
156. ServiceCall 的 context 若未提供则创建新 Context（core.py:2541）
157. `ServiceRegistry` 使用 `__slots__`：`_hass`、`_services`（core.py:2559）
158. `_services` 结构为 `dict[str, dict[str, Service]]`，按 domain → service 名组织（core.py:2563）
159. `async_services()` 返回注册表的副本（domain 级和 service 级都复制）（core.py:2571-2580）
160. `async_services_internal()` 直接返回内部字典不复制，仅供内部性能优化使用（core.py:2592-2603）
161. `has_service()` 检查服务是否存在，domain 和 service 名都转小写（core.py:2605-2610）
162. `async_register()` 要求在事件循环线程中调用（通过 `verify_event_loop_thread`）（core.py:2672）
163. 注册服务时 domain 和 service 名都转小写（core.py:2706-2707）
164. 服务注册后触发 `EVENT_SERVICE_REGISTERED` 事件，携带 domain 和 service（core.py:2723-2725）
165. `async_remove()` 移除服务后触发 `EVENT_SERVICE_REMOVED` 事件（core.py:2742-2762）
166. `async_call()` 首先查找 handler，找不到时尝试小写转换后再找，仍找不到抛出 `ServiceNotFound`（core.py:2820-2830）
167. `return_response=True` 要求 `blocking=True`，否则抛出 `ServiceValidationError`（core.py:2832-2841）
168. 若 handler 的 `supports_response` 为 NONE 但请求了 response，抛出 `ServiceValidationError`（core.py:2842-2849）
169. 若 handler 的 `supports_response` 为 ONLY 但未请求 response，抛出 `ServiceValidationError`（core.py:2850-2855）
170. service_data 若有 schema 则通过 schema 校验和强制转换（core.py:2860-2872）
171. 服务调用前触发 `EVENT_CALL_SERVICE` 事件，携带 domain/service/service_data（core.py:2878-2886）
172. 非阻塞调用通过 `async_create_task_internal` 在后台执行，异常被捕获记录（core.py:2889-2895, 2910-2927）
173. 阻塞调用等待协程完成，若请求 response 则验证返回值为 dict（core.py:2897-2908）
174. `_execute_service()` 根据 job_type 决定执行方式：协程函数直接 await，callback 直接调用，executor 在线程池执行（core.py:2929-2937+）
175. `ServiceResponse` 类型定义为 `JsonObjectType | None`（core.py:126）
176. `EntityServiceResponse` 类型定义为 `dict[str, ServiceResponse]`（core.py:127）

---

## 7. Context

177. Context 类位于 core.py:1218，文档字符串为 "The context that triggered something."
178. Context 的 `id` 使用 ULID（Universally Unique Lexicographically Sortable Identifier）（core.py:1230）
179. Context 支持 `__copy__` 和 `__deepcopy__`，两者都返回相同 id 的新 Context（core.py:1241-1247）
180. `_as_dict` 缓存属性返回普通 dict，调用者不应修改（core.py:1249-1260）
181. `_as_read_only_dict` 缓存属性包装为 ReadOnlyDict（core.py:1266-1269）
182. `json_fragment` 缓存属性返回 `json_fragment(json_bytes(self._as_dict))`（core.py:1271-1274）
183. `origin_event` 属性持有触发该 Context 的原始 Event 引用（core.py:1233）
184. Event 构造时若 context 未设置 origin_event，则将自身设为 origin_event（core.py:1323-1324）

---

## 8. bootstrap 启动流程

185. `async_setup_hass()` 是顶层启动协程，接收 `RuntimeConfig`（bootstrap.py:309-311）
186. 内部 `create_hass()` 创建 `core.HomeAssistant` 实例，调用 `loader.async_setup(hass)`，启用日志（bootstrap.py:314-334）
187. 启动时调用 `conf_util.async_ensure_config_exists(hass)` 确保配置存在（bootstrap.py:343）
188. 非恢复模式下执行配置升级 `process_ha_config_upgrade`（bootstrap.py:355）
189. 通过 `async_hass_config_yaml` 解析 configuration.yaml（bootstrap.py:358）
190. 非虚拟环境时调用 `async_mount_local_lib_path` 挂载本地依赖路径（bootstrap.py:365-366）
191. `async_from_config_dict()` 是配置加载的核心方法（bootstrap.py:520-576）
192. `async_from_config_dict()` 首先创建 `ConfigEntries(hass, config)`（bootstrap.py:530）
193. 预加载自定义组件缓存 `await loader.async_get_custom_components(hass)`（bootstrap.py:533）
194. 调用 `async_load_base_functionality()` 加载注册表和基础功能（bootstrap.py:535）
195. 无条件加载 `CORE_INTEGRATIONS = {"homeassistant", "persistent_notification"}`（bootstrap.py:152, 541-554）
196. 通过 `async_process_ha_core_config` 处理 `[homeassistant]` 配置段（bootstrap.py:558-565）
197. 调用 `_async_set_up_integrations()` 设置所有集成（bootstrap.py:572）
198. `CORE_INTEGRATIONS` 是无条件加载的核心集成集合（bootstrap.py:152）
199. `LOGGING_AND_HTTP_DEPS_INTEGRATIONS` 包含 isal/logger/network/system_log/sentry（bootstrap.py:155-168）
200. `FRONTEND_INTEGRATIONS` 包含 `frontend`（bootstrap.py:169-174）
201. `STAGE_0_INTEGRATIONS` 是元组序列，包含 logging/labs/frontend/recorder/debugger/zeroconf 子阶段（bootstrap.py:183-196）
202. Stage 0 中 recorder 子阶段无超时（timeout=None），避免中断数据库迁移（bootstrap.py:177-178, 191）
203. `STAGE_1_INTEGRATIONS` 包含 bluetooth/dhcp/ssdp/usb/mqtt_eventstream/cloud/hassio（bootstrap.py:200-213）
204. `DEFAULT_INTEGRATIONS` 是默认加载的集成集合，包括 analytics/automation/frontend/logger 等（bootstrap.py:215-268）
205. `DEFAULT_INTEGRATIONS_RECOVERY_MODE` 仅包含 backup/cloud/frontend（bootstrap.py:269-274）
206. `CRITICAL_INTEGRATIONS = {"frontend"}`，加载失败则激活恢复模式（bootstrap.py:280-283）
207. Stage 超时：STAGE_0_SUBSTAGE_TIMEOUT=60s、STAGE_1_TIMEOUT=120s、STAGE_2_TIMEOUT=300s、WRAP_UP_TIMEOUT=300s（bootstrap.py:145-148）
208. `_async_set_up_integrations()` 解析依赖后按 stage 0 → stage 1 → stage 2 顺序加载（bootstrap.py:907-1011）
209. 每个 stage 使用 `hass.timeout.async_timeout` 包裹，超时则警告并继续（bootstrap.py:982-994）
210. 最后 wrap up 阶段调用 `hass.async_block_till_done()` 等待所有启动任务（bootstrap.py:996-1009）
211. `_WatchPendingSetups` 定期记录正在设置的集成，每 60 秒警告一次慢启动（bootstrap.py:1021-1089）
212. `_async_setup_multi_components()` 并行创建多个组件设置任务，base platforms 优先排序（bootstrap.py:1092-1117）
213. `async_load_base_functionality()` 并行加载 area/category/device/entity/floor/issue/label 注册表（bootstrap.py:484-500）
214. 恢复模式下加载 `{"recovery_mode": {}, "http": http_conf}` 配置（bootstrap.py:419-422）
215. `PRELOAD_STORAGE` 列表预加载 15 个存储键以加速启动（bootstrap.py:291-306）
216. `ERROR_LOG_FILENAME = "home-assistant.log"`（bootstrap.py:132）
217. `async_enable_logging()` 设置彩色日志、捕获 warnings、配置日志文件（bootstrap.py:579-684）

---

## 9. Config 与配置管理

218. `Config` 类位于 `core_config.py:534`，文档为 "Configuration settings for Home Assistant."
219. Config 构造函数初始化 latitude=0、longitude=0、elevation=0（core_config.py:545-548）
220. Config 的 `radius` 默认从 zone 组件的 `DEFAULT_RADIUS` 导入（core_config.py:541, 551）
221. `location_name` 默认为 `"Home"`（core_config.py:555）
222. `time_zone` 默认为 `"UTC"`（core_config.py:556）
223. `units` 默认为 `METRIC_SYSTEM`（core_config.py:557）
224. `currency` 默认为 `"EUR"`，`language` 默认为 `"en"`（core_config.py:560, 562）
225. `config_source` 默认为 `ConfigSource.DEFAULT`（core_config.py:564）
226. `top_level_components` 和 `all_components` 是 set，由 `_ComponentSet` 管理（core_config.py:574-581）
227. `components` 是 `_ComponentSet` 实例，包装上述两个集合（core_config.py:581）
228. `api` 属性为 `ApiConfig | None`，存储 HTTP 服务器配置（core_config.py:584）
229. `config_dir` 存储配置目录路径（core_config.py:587）
230. `allowlist_external_dirs` 和 `allowlist_external_urls` 是 set（core_config.py:590, 593）
231. `media_dirs` 是 dict，映射媒体文件夹名称到路径（core_config.py:596）
232. `recovery_mode` 和 `safe_mode` 布尔标志默认为 False（core_config.py:599, 605）
233. `legacy_templates` 布尔标志默认为 False（core_config.py:602）
234. `path(*path)` 方法在 config_dir 下拼接路径（core_config.py:626-631）
235. `cache_path(*path)` 在 `.cache` 子目录下拼接路径（core_config.py:633-641）
236. `is_allowed_external_url()` 检查 URL 是否在白名单中（core_config.py:643-651）
237. `is_allowed_path()` 解析路径并检查是否在 allowlist_external_dirs 下（core_config.py:653-679）
238. `distance()` 方法使用 units 系统计算从 HA 位置到指定坐标的距离（core_config.py:616-624）
239. `async_initialize()` 创建内部 `_ConfigStore` 实例（core_config.py:609-614）
240. config.py 中 `YAML_CONFIG_FILE = "configuration.yaml"`（config.py:39）
241. `VERSION_FILE = ".HA_VERSION"`，`CONFIG_DIR_NAME = ".homeassistant"`（config.py:40-41）
242. 自动化/脚本/场景配置路径：`automations.yaml`、`scripts.yaml`、`scenes.yaml`（config.py:43-45）
243. `SAFE_MODE_FILENAME = "safe-mode"`（config.py:50）
244. `DEFAULT_CONFIG` 包含 default_config、frontend themes、automation/script/scene 的 include（config.py:52-63）
245. `ConfigExceptionInfo` dataclass 包含 exception/translation_key/platform_path/config/integration_link（config.py:111-119）
246. `IntegrationConfigInfo` dataclass 包含 config 和 exception_info_list（config.py:122-127）
247. `ConfigErrorTranslationKey` StrEnum 定义配置错误翻译键（config.py:80-97）

---

## 10. ConfigEntry 配置条目

248. `ConfigEntryState` 枚举有 8 个状态：LOADED/SETUP_ERROR/MIGRATION_ERROR/SETUP_RETRY/NOT_LOADED/FAILED_UNLOAD/SETUP_IN_PROGRESS/UNLOAD_IN_PROGRESS（config_entries.py:147-165）
249. 每个 ConfigEntryState 关联 `_recoverable: bool`，LOADED/SETUP_ERROR/SETUP_RETRY/NOT_LOADED 为可恢复（config_entries.py:167-183）
250. `recoverable` 属性指示是否允许卸载和重载（config_entries.py:176-183）
251. 配置条目来源常量：SOURCE_BLUETOOTH/SOURCE_DHCP/SOURCE_DISCOVERY/SOURCE_HASSIO/SOURCE_HOMEKIT/SOURCE_IMPORT/SOURCE_MQTT/SOURCE_SSDP/SOURCE_USB/SOURCE_USER/SOURCE_ZEROCONF 等（config_entries.py:104-118）
252. `SOURCE_IGNORE = "ignore"` 用于用户忽略发现的条目（config_entries.py:123）
253. `SOURCE_REAUTH = "reauth"` 表示需要重新认证（config_entries.py:126）
254. `SOURCE_RECONFIGURE = "reconfigure"` 表示用户发起重新配置（config_entries.py:129）
255. `STORAGE_KEY = "core.config_entries"`，`STORAGE_VERSION = 1`，`STORAGE_VERSION_MINOR = 5`（config_entries.py:133-135）
256. `SAVE_DELAY = 1` 秒（config_entries.py:137）
257. `SETUP_RETRY_MAX_WAIT = 600`（10 分钟）（config_entries.py:141）
258. `ConfigEntryChange` StrEnum 包含 ADDED/REMOVED/UPDATED（config_entries.py:224-229）
259. `ConfigEntryDisabler` StrEnum 目前仅含 USER = "user"（config_entries.py:232-235）
260. `SIGNAL_CONFIG_ENTRY_CHANGED` 是 SignalType，值为 `"config_entry_changed"`（config_entries.py:205-207）
261. `HANDLERS` 是 `Registry[str, type[ConfigFlow]]` 装饰器注册表（config_entries.py:131）
262. `ConfigFlowContext` 继承 FlowContext，支持 alternative_domain/configuration_url/confirm_only/discovery_key 等字段（config_entries.py:293-300）
263. `NO_RESET_TRIES_STATES` 包含 SETUP_RETRY 和 SETUP_IN_PROGRESS（config_entries.py:218-221）
264. `FROZEN_CONFIG_ENTRY_ATTRS` 包含 entry_id/domain/state/reason/error_reason_translation_key/error_reason_translation_placeholders（config_entries.py:280）
265. `UPDATE_ENTRY_CONFIG_ENTRY_ATTRS` 包含 unique_id/title/data/options/pref_disable_new_entities/pref_disable_polling/minor_version/version（config_entries.py:281-290）
266. ConfigEntry 相关异常：`ConfigError`、`UnknownEntry`、`UnknownSubEntry`、`OperationNotAllowed`（config_entries.py:254-267）

---

## 11. loader 集成加载器

267. `Integration` 类位于 loader.py:667，代表一个 HA 集成
268. `Integration.resolve_from_root()` 类方法从根模块路径解析集成，读取 manifest.json（loader.py:670-762）
269. 自定义集成必须有 `version` 键且版本号符合 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 策略之一（loader.py:709-744）
270. `BLOCKED_CUSTOM_INTEGRATIONS` 字典记录被阻止的自定义集成及其最低安全版本（loader.py:101-140）
271. Integration 构造函数接收 hass/pkg_path/file_path/manifest/top_level_files（loader.py:764-792）
272. Integration 在 manifest 中设置 `is_built_in` 和 `overwrites_built_in` 标志（loader.py:778-779）
273. `domain`、`name`、`dependencies`、`after_dependencies`、`requirements`、`config_flow` 等均为 `cached_property`（loader.py:799-832）
274. `integration_type` 缓存属性返回 Literal 类型：entity/device/hardware/helper/hub/service/system/virtual（loader.py:862-866）
275. `quality_scale` 对内置集成返回 manifest 值，自定义集成返回 `"custom"`（loader.py:849-855）
276. `import_executor` 标志指示是否在执行器中导入代码（loader.py:701）
277. `BASE_PRELOAD_PLATFORMS` 列表预加载 backup/condition/config/config_flow/diagnostics 等 15 个平台（loader.py:74-90）
278. `DATA_COMPONENTS`、`DATA_INTEGRATIONS`、`DATA_MISSING_PLATFORMS`、`DATA_CUSTOM_COMPONENTS`、`DATA_PRELOAD_PLATFORMS` 是 HassKey（loader.py:142-152）
279. `PACKAGE_CUSTOM_COMPONENTS = "custom_components"`，`PACKAGE_BUILTIN = "homeassistant.components"`（loader.py:153-154）
280. `Manifest` TypedDict 定义集成清单结构，包含 name/domain/integration_type/dependencies/requirements/config_flow/documentation/iot_class 等字段（loader.py:246-282）
281. `async_setup()` 初始化 hass.data 中的组件/集成/缺失平台/预加载平台字典（loader.py:285-291）
282. `IntegrationNotFound` 和 `IntegrationNotLoaded` 是 `LoaderError` 子类（loader.py:1654, 1663）
283. 虚拟集成（integration_type="virtual"）不执行 listdir 也不能有平台（loader.py:691-699）
284. `CUSTOM_WARNING` 消息警告自定义集成未经 HA 测试（loader.py:155-160）

---

## 12. runner 启动入口

285. `RuntimeConfig` 是 `@dataclasses.dataclass(slots=True)`，包含 config_dir/skip_pip/skip_pip_packages/recovery_mode/verbose/log_rotate_days/log_file/log_no_color/debug/open_ui/safe_mode（runner.py:155-173）
286. `MAX_EXECUTOR_WORKERS = 64`（runner.py:43）
287. `TASK_CANCELATION_TIMEOUT = 5` 秒（runner.py:44）
288. `LOCK_FILE_NAME = ".ha_run.lock"`，`LOCK_FILE_VERSION = 1`（runner.py:47-48）
289. `ensure_single_execution()` 上下文管理器使用 `fcntl.flock` 确保每个配置目录只有一个 HA 实例运行（runner.py:118-152）
290. 获取锁失败时设置 `exit_code=1` 并报告已运行实例的 PID/版本/启动时间（runner.py:136-143, 79-115）
291. `HassEventLoopPolicy` 继承 `asyncio.DefaultEventLoopPolicy`（runner.py:176）
292. `HassEventLoopPolicy.new_event_loop()` 设置自定义异常处理器、InterruptibleThreadPoolExecutor、绑定 `time.monotonic` 为 `loop.time`（runner.py:189-207）
293. 执行器线程名前缀为 `"SyncWorker"`，max_workers=64（runner.py:196-198）
294. `_async_loop_exception_handler()` 处理事件循环异常，EMFILE 错误（文件描述符耗尽）为致命错误（runner.py:210-251）
295. `setup_and_run_hass()` 调用 `bootstrap.async_setup_hass()` 然后 `hass.async_run()`（runner.py:254-264）
296. `run()` 函数是主入口：启用 posix_spawn、设置文件描述符限制、设置事件循环策略、运行 setup_and_run_hass（runner.py:280-297）
297. `run()` finally 块中调用 `_cancel_all_tasks_with_timeout` 取消所有任务，然后关闭异步生成器和默认执行器（runner.py:291-297）
298. `_enable_posix_spawn()` 在 Alpine Linux/musl 上强制启用 posix_spawn 以提升效率（runner.py:267-277）
299. `_cancel_all_tasks_with_timeout()` 给所有任务发送取消信号，等待 5 秒，未完成则警告（runner.py:300-329）

---

## 13. setup 组件设置

300. `async_setup_component()` 是公共协程，设置组件及其所有依赖（setup.py:148-190）
301. 若 domain 已在 `hass.config.components` 中，直接返回 True（setup.py:155-156）
302. 使用 `_DATA_SETUP` 字典追踪正在设置的组件 Future，防止并发重复设置（setup.py:52, 158-165）
303. `_DATA_SETUP_DONE` 字典追踪即将加载的 domain 的 Future（setup.py:59）
304. `_DATA_SETUP_STARTED` 记录设置开始时间，键为 `(domain, group)` 元组（setup.py:63-65）
305. `SLOW_SETUP_WARNING = 10` 秒，`SLOW_SETUP_MAX_WAIT = 300` 秒（setup.py:84-85）
306. `_async_setup_component()` 是内部实现，首先通过 `loader.async_get_integration` 获取集成（setup.py:280-288）
307. IntegrationNotFound 时创建 issue 并返回 False（setup.py:289-305）
308. 集成被 disabled 时记录错误并返回 False（setup.py:309-311）
309. 调用 `integration.resolve_dependencies()` 验证依赖存在且无循环依赖（setup.py:327）
310. `async_process_deps_reqs()` 处理依赖和 Python requirements（setup.py:332-336）
311. 通过 `integration.async_get_component()` 导入组件模块（setup.py:340-344）
312. 使用 `conf_util.async_process_component_config()` 处理组件配置（setup.py:346-352）
313. 仅支持 config entry 的集成若在 YAML 中配置则创建 issue（setup.py:364-391）
314. 组件设置优先级：`async_setup` 协程 → `setup` 同步函数（在 executor 中运行）→ 都没有则报错（setup.py:411-421）
315. 设置任务包裹在 `hass.timeout.async_timeout(SLOW_SETUP_MAX_WAIT, domain)` 中（setup.py:424）
316. 设置成功后 domain 添加到 `hass.config.components`（setup.py:465）
317. 设置完成后触发 `EVENT_COMPONENT_LOADED` 事件（setup.py:487-489）
318. `SetupPhases` StrEnum 定义设置阶段：SETUP/CONFIG_ENTRY_SETUP/PLATFORM_SETUP/CONFIG_ENTRY_PLATFORM_SETUP/WAIT_BASE_PLATFORM_SETUP/WAIT_IMPORT_PLATFORMS/WAIT_IMPORT_PACKAGES（setup.py:665-688）
319. `async_start_setup()` 上下文管理器追踪设置开始/结束时间，记录耗时（setup.py:742-803）
320. `async_pause_setup()` 上下文管理器记录等待其他操作的负时间（setup.py:699-731）
321. `async_get_setup_timings()` 返回每个集成的总设置时间（setup.py:806-825）
322. `async_when_setup()` 注册组件设置完成时的回调（setup.py:591-598）
323. `async_wait_component()` 等待组件设置完成并返回是否成功（setup.py:836-841）
324. `_async_process_dependencies()` 并发设置所有 dependencies 和 after_dependencies（setup.py:193-259）
325. `async_prepare_setup_platform()` 加载平台模块并确保顶级组件已设置（setup.py:494-565）
326. `async_notify_setup_error()` 创建持久通知显示设置失败的集成（setup.py:94-120）
327. `current_setup_group` 是 ContextVar，追踪当前设置组（setup.py:36-38）

---

## 14. data_entry_flow

328. `FlowResultType` StrEnum 包含 FORM/CREATE_ENTRY/ABORT/EXTERNAL_STEP/EXTERNAL_STEP_DONE/SHOW_PROGRESS/SHOW_PROGRESS_DONE/MENU（data_entry_flow.py:27-37）
329. `EVENT_DATA_ENTRY_FLOW_PROGRESSED = "data_entry_flow_progressed"`（data_entry_flow.py:41）
330. `FLOW_NOT_COMPLETE_STEPS` 集合包含 FORM/EXTERNAL_STEP/EXTERNAL_STEP_DONE/SHOW_PROGRESS/SHOW_PROGRESS_DONE/MENU（data_entry_flow.py:44-51）
331. `FlowError` 继承 `HomeAssistantError`，是数据录入错误基类（data_entry_flow.py:74-75）
332. `UnknownHandler`、`UnknownFlow`、`UnknownStep` 继承 FlowError（data_entry_flow.py:78-87）
333. `InvalidData` 继承 `vol.Invalid`，携带 `schema_errors` 字典（data_entry_flow.py:90-103）
334. `AbortFlow` 异常携带 `reason` 和 `description_placeholders`（data_entry_flow.py:106-115）
335. `FlowContext` TypedDict 包含可选 `source` 字段（data_entry_flow.py:118-121）
336. `FlowResult` TypedDict 包含 flow_id/handler/type/data_schema/data/errors/step_id/title/description 等字段（data_entry_flow.py:124-148）
337. `FlowManager` 是抽象基类，管理所有进行中的 flow（data_entry_flow.py:174）
338. FlowManager 维护 `_progress` 字典（flow_id → FlowHandler）和 `_handler_progress_index` 索引（data_entry_flow.py:186-191）
339. `async_create_flow()` 是抽象方法，由子类实现创建特定 flow（data_entry_flow.py:196-200）
340. `BaseServiceInfo` 是 dataclass(slots=True)，作为发现 ServiceInfo 的基类（data_entry_flow.py:69-71）

---

## 15. auth 认证体系

341. `AuthManager` 类位于 auth/__init__.py:176，管理 HA 的认证
342. AuthManager 构造参数：hass/store/providers/mfa_modules（auth/__init__.py:179-186）
343. AuthManager 持有 `login_flow` 属性为 `AuthManagerFlowManager` 实例（auth/__init__.py:191）
344. `auth_manager_from_config()` 从配置创建 AuthManager，加载 auth store、providers 和 MFA modules（auth/__init__.py:48-97）
345. AuthManager 事件：`EVENT_USER_ADDED="user_added"`、`EVENT_USER_UPDATED="user_updated"`、`EVENT_USER_REMOVED="user_removed"`（auth/__init__.py:31-33）
346. `async_create_user()` 创建普通用户，首个非系统用户自动成为 owner（auth/__init__.py:284-306, 697-707）
347. `async_create_system_user()` 创建系统生成用户（auth/__init__.py:264-282）
348. `async_get_or_create_user()` 从 credentials 获取或创建用户，新用户通过 auth provider 获取元数据（auth/__init__.py:308-335）
349. `async_link_user()` 将 credentials 链接到现有用户（auth/__init__.py:337-347）
350. `async_deactivate_user()` 停用用户，owner 不可停用，同时移除所有 refresh tokens（auth/__init__.py:402-408）
351. `async_create_refresh_token()` 创建刷新令牌，系统用户只能有 system 类型令牌（auth/__init__.py:455-519）
352. 普通刷新令牌（TOKEN_TYPE_NORMAL）需要 client_id，有效期为 `REFRESH_TOKEN_EXPIRATION`（90天）（auth/__init__.py:481-482, 491-492）
353. 长期访问令牌（TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN）需要 client_name，每个 client_name 只能有一个（auth/__init__.py:494-508）
354. `async_create_access_token()` 从 refresh_token 创建 JWT，包含 iss/iat/exp 声明，使用 HS256 算法（auth/__init__.py:600-619）
355. `async_validate_access_token()` 先不解码验证获取 issuer，再用 refresh_token 的 jwt_key 验证（auth/__init__.py:655-684）
356. JWT 验证允许 10 秒 leeway（auth/__init__.py:676）
357. `async_register_revoke_token_callback()` 注册令牌撤销回调（auth/__init__.py:588-598）
358. `_async_track_next_refresh_token_expiration()` 调度下一个过期令牌的清理任务（auth/__init__.py:558-572）
359. `AuthManagerFlowManager` 继承 FlowManager，handler_key 为 `(provider_type, provider_id)` 元组（auth/__init__.py:100-124）
360. `InvalidAuthError` 和 `InvalidProvider` 是认证模块异常（auth/__init__.py:40-45）

### auth 模型

361. `User` 类使用 `attr.s(slots=False)`，包含 name/perm_lookup/id/is_owner/is_active/system_generated/local_only/groups/credentials/refresh_tokens（auth/models.py:56-78）
362. User 的 `is_owner`、`is_active`、`groups` 属性变更时触发 `invalidate_cache()`（auth/models.py:63-69）
363. `permissions` 缓存属性：owner 返回 `OwnerPermissions`，否则合并所有 group 的策略（auth/models.py:80-88）
364. `is_admin` 缓存属性：owner 或在 admin group 中且 active（auth/models.py:90-95）
365. `Group` 类使用 `attr.s(slots=True)`，包含 name/policy/id/system_generated（auth/models.py:40-47）
366. `RefreshToken` 类使用 `attr.s(slots=True)`，包含 user/client_id/access_token_expiration/client_name/client_icon/token_type/id/created_at/token/jwt_key/last_used_at/last_used_ip/expire_at/credential/version（auth/models.py:103-130）
367. RefreshToken 的 `token` 和 `jwt_key` 通过 `secrets.token_hex(64)` 生成（auth/models.py:120-121）
368. `Credentials` 类使用 `attr.s(slots=True)`，包含 auth_provider_type/auth_provider_id/data/id/is_new（auth/models.py:133-144）
369. 令牌类型常量：`TOKEN_TYPE_NORMAL="normal"`、`TOKEN_TYPE_SYSTEM="system"`、`TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN="long_lived_access_token"`（auth/models.py:21-23）
370. `UserMeta` NamedTuple 包含 name/is_active/group/local_only（auth/models.py:147-153）

### auth 常量

371. `ACCESS_TOKEN_EXPIRATION = timedelta(minutes=30)`（auth/const.py:5）
372. `MFA_SESSION_EXPIRATION = timedelta(minutes=5)`（auth/const.py:6）
373. `REFRESH_TOKEN_EXPIRATION = timedelta(days=90).total_seconds()`（auth/const.py:7）
374. 系统组 ID：`GROUP_ID_ADMIN="system-admin"`、`GROUP_ID_USER="system-users"`、`GROUP_ID_READ_ONLY="system-read-only"`（auth/const.py:9-11）

### auth_store

375. `AuthStore` 类位于 auth/auth_store.py:44，使用 Store 持久化认证数据
376. `STORAGE_VERSION = 1`，`STORAGE_KEY = "auth"`，private=True，atomic_writes=True（auth/auth_store.py:26-27, 60-62）
377. 系统组名：`GROUP_NAME_ADMIN="Administrators"`、`GROUP_NAME_USER="Users"`、`GROUP_NAME_READ_ONLY="Read Only"`（auth/auth_store.py:28-30）
378. `INITIAL_LOAD_SAVE_DELAY = 300`（5分钟），首次加载后延迟保存以迁移数据（auth/auth_store.py:39）
379. AuthStore 维护 `_users`、`_groups`、`_perm_lookup`、`_token_id_to_user_id` 映射（auth/auth_store.py:57-63）
380. AuthStore 是懒加载的，调用需要数据的方法时才从磁盘加载（auth/auth_store.py:49-50）

### jwt_wrapper

381. `JWT_TOKEN_CACHE_SIZE = 16`，`MAX_TOKEN_SIZE = 8192`（auth/jwt_wrapper.py:19-20）
382. `_PyJWSWithLoadCache` 继承 PyJWS，使用 `lru_cache(16)` 缓存 `_load` 结果（auth/jwt_wrapper.py:35-45）
383. `_PyJWTWithVerify` 继承 PyJWT，要求 `exp` 和 `iat` 声明存在（auth/jwt_wrapper.py:60-68）
384. 超过 8192 字节的 token 抛出 `DecodeError("Token too large")`（auth/jwt_wrapper.py:105-107）
385. `unverified_hs256_token_decode()` 使用 `lru_cache(16)` 缓存未验证解码结果（auth/jwt_wrapper.py:131-139）
386. `verify_and_decode` 是模块级单例 `_jwt.verify_and_decode` 的引用（auth/jwt_wrapper.py:127-128）

---

## 16. 异常层次

387. `HomeAssistantError` 是所有 HA 异常的基类，继承 Exception（exceptions.py:33）
388. HomeAssistantError 支持翻译：`translation_domain`、`translation_key`、`translation_placeholders`（exceptions.py:38-40）
389. 无参数但提供 translation_key 和 translation_domain 时，`generate_message=True`（exceptions.py:50-52）
390. `__str__` 方法在 `generate_message=True` 时通过 `async_get_exception_message` 生成翻译消息（exceptions.py:59-87）
391. `ConfigValidationError` 同时继承 `HomeAssistantError` 和 `ExceptionGroup[Exception]`（exceptions.py:90）
392. `ServiceValidationError` 继承 HomeAssistantError，服务调用验证错误（exceptions.py:110-111）
393. `InvalidEntityFormatError` — 实体格式无效（exceptions.py:114-115）
394. `NoEntitySpecifiedError` — 未指定实体（exceptions.py:118-119）
395. `TemplateError` — 模板渲染错误，接受 Exception 或 str（exceptions.py:122-130）
396. `ConditionError` 是条件评估错误基类，支持缩进输出（exceptions.py:133-153）
397. `ConditionErrorMessage` 携带具体消息（exceptions.py:156-171）
398. `ConditionErrorIndex` 携带索引和总数（exceptions.py:174-209）
399. `ConditionErrorContainer` 包含子条件错误列表（exceptions.py:212-228）
400. `IntegrationError` 是平台和配置条目异常的基类，`__str__` 回退到 `__cause__`（exceptions.py:231-237）
401. `PlatformNotReady` — 平台未就绪（exceptions.py:240-241）
402. `ConfigEntryError` — 配置条目设置失败（exceptions.py:244-245）
403. `ConfigEntryNotReady` — 配置条目尚未就绪（exceptions.py:248-249）
404. `ConfigEntryAuthFailed` — 配置条目认证失败（exceptions.py:252-253）
405. `OAuth2TokenRequestError` 同时继承 `ClientResponseError` 和 `HomeAssistantError`（exceptions.py:256-283）
406. `OAuth2TokenRequestTransientError` — 可恢复的 OAuth2 令牌错误（exceptions.py:286-295）
407. `OAuth2TokenRequestReauthError` — 不可恢复，需要重新认证（exceptions.py:298-310）
408. `InvalidStateError` — 无效状态（exceptions.py:313-314）
409. `Unauthorized` — 未授权操作，携带 context/user_id/entity_id/config_entry_id/perm_category/permission（exceptions.py:317-342）
410. `UnknownUser` 继承 Unauthorized，用户 ID 不存在（exceptions.py:345-346）
411. `ServiceNotFound` 继承 ServiceValidationError，携带 domain 和 service（exceptions.py:349-361）
412. `ServiceNotSupported` 继承 ServiceValidationError，携带 domain/service/entity_id（exceptions.py:364-380）
413. `MaxLengthExceeded` — 属性值超过最大字符长度，携带 value/property_name/max_length（exceptions.py:383-404）
414. `DependencyError` — 依赖无法设置，携带 failed_dependencies 列表（exceptions.py:407-415）
415. `UnsupportedStorageVersionError` — 存储文件版本高于支持版本，携带 storage_key/found_version/max_supported_version（exceptions.py:418-432）

---

## 附：HassJob 与 callback 机制

416. `callback` 装饰器将函数标记为事件循环安全，设置 `_hass_callback=True` 属性（core.py:209-212）
417. `is_callback()` 检查函数是否被 callback 装饰（core.py:215-217）
418. `is_callback_check_partial()` 递归检查 partial 链中的原始函数（core.py:220-229）
419. `HassJob` 类使用 `__slots__`：`_cache`、`_cancel_on_shutdown`、`name`、`target`（core.py:303）
420. `HassJob.__init__` 接收 target/name/cancel_on_shutdown/job_type（core.py:305-321）
421. `job_type` 缓存属性通过 `get_hassjob_callable_job_type` 确定（core.py:323-326）
422. `get_hassjob_callable_job_type()` 检查 partial 链：协程函数→Coroutinefunction，callback→Callback，协程对象抛 ValueError，否则→Executor（core.py:347-360）
423. `HassJobWithArgs` 是 frozen dataclass，包装 job 和 args（core.py:339-344）
424. `CALLBACK_TYPE` 类型别名是 `Callable[[], None]`（core.py:119）
