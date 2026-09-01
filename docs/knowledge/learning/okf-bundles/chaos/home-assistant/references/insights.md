---
type: Insights
title: "Home Assistant 架构洞察"
---

# Home Assistant 架构洞察

> I 阶段产出。基于 1599 条 R 阶段事实综合分析。
> 生成日期：2026-08-22
> 信源：facts-core.md（424条）、facts-helpers.md（522条）、facts-components.md（375条）、facts-tooling.md（278条）

---

## 洞察一：核心-集成-平台三层架构——运行时内核、设备集成、实体类型的严格分离

**观察**：Home Assistant 的代码组织呈现清晰的三层架构。核心层（`homeassistant/core.py`）提供 `HomeAssistant` 根对象，持有 `EventBus`、`StateMachine`、`ServiceRegistry`、`Config` 等运行时基础设施；集成层（`homeassistant/components/<domain>/`）通过 `manifest.json` 自描述，由 `loader.Integration` 加载，经 `async_setup_component()` 初始化，通过 `async_forward_entry_setups()` 将设备能力转发到多个平台；平台层（`light/`、`sensor/`、`switch/` 等）定义标准化实体类型和服务，每个平台在 `async_setup` 中创建 `EntityComponent` 实例管理实体生命周期。一个 hub 型集成（如 Tuya）可同时转发到 18 个平台，MQTT 更支持 31 个平台。

**根因**：这种三层分离是关注点分离原则在 IoT 平台中的必然结果。核心层需要极高的稳定性——它管理事件循环、状态一致性和服务路由，不能因设备协议变更而频繁修改。集成层封装异构设备的通信细节（云推送、本地轮询、Zigbee、MQTT），每个集成独立演进。平台层提供统一的实体抽象——无论 Philips Hue 还是 Yeelight，"灯"的状态和服务接口必须一致，自动化和 UI 才能跨品牌工作。`manifest.json` 的 `dependencies`/`after_dependencies` 机制使核心无需硬编码集成加载顺序，而是由依赖图自动解析。

**证据**：
- facts-core.md F-56~F-69：`HomeAssistant` 类在 `__init__` 中实例化 `bus`/`states`/`services`/`config` 四大子系统
- facts-core.md F-267~F-283：`Integration` 类从 `manifest.json` 解析 domain/dependencies/config_flow 等元数据，`cached_property` 延迟加载
- facts-core.md F-300~F-327：`async_setup_component()` 实现依赖解析、组件导入、配置处理、设置超时（`SLOW_SETUP_MAX_WAIT=300s`）全流程
- facts-components.md F-195~F-214：所有平台遵循统一模式——`async_setup` 创建 `EntityComponent`，`async_setup_entry` 委托给 component，`async_unload_entry` 清理
- facts-components.md F-224~F-227：`async_forward_entry_setups(entry, PLATFORMS)` 是标准多平台转发方法，Tuya 转发 18 平台、MQTT 转发 31 平台
- facts-components.md F-366：所有平台集成均使用 `EntityComponent` 作为实体管理核心
- facts-core.md F-191~F-213：bootstrap 按 Stage 0/1/2 分阶段加载集成，base platforms 优先排序，每阶段有独立超时

**意义**：集成开发者应准确判断自己的代码处于哪一层。新设备集成的典型工作仅限于集成层（`async_setup_entry` 建立连接）和平台层（继承 `LightEntity`/`SensorEntity` 等），绝不应修改核心代码。理解三层边界有助于定位问题——状态不一致是核心层问题，设备离线是集成层问题，实体属性缺失是平台层问题。核心层的 `hass.data` 字典是跨层共享数据的唯一通道，应使用 `HassKey` 类型安全键。

---

## 洞察二：异步事件驱动模型——EventBus/StateMachine/ServiceRegistry 三位一体的 asyncio 架构

**观察**：HA 的三大运行时子系统全部构建在 asyncio 事件循环之上，形成"事件→状态变更→服务调用"的闭环。`EventBus` 支持线程安全的 `fire()`（通过 `call_soon_threadsafe` 调度）和事件循环内的 `async_fire()`，嵌套触发时入队防止无限循环（上限 10,000）。`StateMachine` 在状态变化时创建新的 `State` 对象（不可变），旧 State 调用 `expire()` 释放 Context 引用，触发 `EVENT_STATE_CHANGED`；状态未变时仅更新 `last_reported` 并触发轻量的 `EVENT_STATE_REPORTED`。`ServiceRegistry` 通过 `HassJob` 自动识别处理器类型——协程函数直接 await、callback 直接调用、普通函数分派到线程池执行器。所有核心数据类（Event/State/Service/Context）均使用 `__slots__` 减少内存开销。

**根因**：HA 需要同时管理数百个集成的并发 I/O——MQTT 消息监听、HTTP API 请求、蓝牙扫描、Zigbee 设备通信，同步模型会导致一个慢设备阻塞整个系统。asyncio 单线程事件循环消除了多线程锁竞争，同时通过 `InterruptibleThreadPoolExecutor`（64 工作线程）容纳无法改造为异步的阻塞库。事件驱动的发布-订阅模式使状态生产者无需知道消费者是谁——自动化、前端、历史记录、语音助手都可以独立监听 `state_changed` 事件而互不耦合。区分 `STATE_CHANGED`（值或属性变化）和 `STATE_REPORTED`（仅时间戳更新）则是为了避免高频传感器上报相同值时产生不必要的计算开销。

**证据**：
- facts-core.md F-92~F-98：`Event` 类被 `@final` 装饰禁止子类化，使用 `__slots__` 和泛型 `Generic[_DataT]`，Context 使用 ULID 作为可排序唯一 ID
- facts-core.md F-101~F-113：`EventBus` 嵌套触发保护（`_MAX_QUEUED_EVENT_DISPATCHES=10000`），`async_listen_once` 通过 `_OneTimeListener` 自动移除
- facts-core.md F-127~F-145：`States` 维护 `domain -> dict[str, State]` 二级索引，`split_entity_id` 和 `valid_entity_id` 使用 `lru_cache` 加速
- facts-core.md F-138~F-140：状态未变时触发 `EVENT_STATE_REPORTED` 而非 `EVENT_STATE_CHANGED`，旧 State 的 `expire()` 允许 Context 被 GC
- facts-core.md F-162~F-174：服务注册要求在事件循环线程中调用，`async_call` 支持阻塞/非阻塞模式，`SupportsResponse` 三态控制响应语义
- facts-core.md F-416~F-424：`callback` 装饰器标记事件循环安全函数，`get_hassjob_callable_job_type()` 递归检查 partial 链确定 job_type
- facts-core.md F-76~F-80：`add_job()` 是线程安全入口，根据 target 类型自动调度到协程/回调/执行器
- facts-helpers.md F-155~F-171：`async_track_state_change`/`async_track_time_interval`/`TrackTemplate` 等 helper 封装了常见的事件监听模式

**意义**：集成开发者必须建立严格的异步纪律。`@callback` 装饰的函数绝不能包含阻塞 I/O——它在事件循环线程中直接执行，阻塞会卡住整个 HA。需要网络请求时使用 `aiohttp` 等异步库，或通过 `hass.async_add_executor_job()` 分派到线程池。实体状态更新应调用 `async_write_ha_state()`（在事件循环中）而非 `schedule_update_ha_state()`（从外部线程），后者通过 `call_soon_threadsafe` 调度。`EVENT_STATE_REPORTED` 的存在意味着轮询传感器应设置合适的 `scan_interval`，避免高频上报相同值造成事件风暴。

---

## 洞察三：声明式集成清单——manifest.json + ConfigFlow + ConfigEntry 的生命周期契约

**观察**：每个集成通过 `manifest.json` 声明显式契约——必需字段 domain/name/documentation/codeowners，可选字段包括 dependencies/after_dependencies（加载顺序）、requirements（Python 包，版本锁定）、config_flow（是否支持 GUI 配置）、iot_class（通信模式：cloud_push/local_push/cloud_polling/local_polling 等）、integration_type（hub/service/entity/system/virtual 等 8 种类型）、zeroconf/dhcp/ssdp/usb/bluetooth（服务发现规则）。支持 config_flow 的集成交付 `ConfigFlow` 类，通过多步表单引导用户配置，成功后创建 `ConfigEntry` 持久化到 `.storage/core.config_entries`。ConfigEntry 有 8 种状态（LOADED/SETUP_ERROR/MIGRATION_ERROR/SETUP_RETRY/NOT_LOADED/FAILED_UNLOAD/SETUP_IN_PROGRESS/UNLOAD_IN_PROGRESS），其中 4 种可恢复，支持版本迁移（`async_migrate_entry`）、重新认证（`SOURCE_REAUTH`）和重新配置（`SOURCE_RECONFIGURE`）。

**根因**：早期 HA 使用 YAML 文件配置所有设备，这对简单场景可行，但无法应对 OAuth2 认证流程、设备发现、动态选项等复杂交互。manifest.json 将集成元数据从代码中提取为声明式数据，使核心能在不导入集成代码的情况下解析依赖图、安装 requirements、生成发现索引。ConfigFlow 将配置过程建模为状态机（FORM/CREATE_ENTRY/ABORT/EXTERNAL_STEP/SHOW_PROGRESS/MENU），支持前端渲染和外部 OAuth 跳转。ConfigEntry 作为运行时配置对象，提供了重载、卸载、迁移、错误重试的生命周期管理——当集成认证过期时抛 `ConfigEntryAuthFailed` 触发重新认证，当设备暂时不可用时抛 `ConfigEntryNotReady` 触发指数退避重试（最大 10 分钟）。

**证据**：
- facts-components.md F-1~F-25：manifest.json 字段详解——Tuya 配置 11 条 DHCP 发现规则，default_config 通过 dependencies 拉取 20 个核心集成
- facts-core.md F-248~F-266：`ConfigEntryState` 8 状态及 `recoverable` 属性，`SETUP_RETRY_MAX_WAIT=600`，`SAVE_DELAY=1` 秒，`STORAGE_VERSION_MINOR=5`
- facts-core.md F-251~F-254：配置来源常量——SOURCE_BLUETOOTH/DHCP/DISCOVERY/HASSIO/HOMEKIT/MQTT/SSDP/USB/USER/ZEROCONF/REAUTH/RECONFIGURE
- facts-components.md F-216~F-223：MQTT ConfigFlow 支持 TLS 证书和 Hass.io addon 发现，Anthropic 通过 `ConfigSubentry` 合并多 API key
- facts-core.md F-399~F-404：`ConfigEntryNotReady`/`ConfigEntryAuthFailed` 异常类触发重试/重新认证流程
- facts-tooling.md F-57~F-71：`INTEGRATION_MANIFEST_SCHEMA` 使用 voluptuous 验证，自定义集成需要 `version` 字段，虚拟集成使用独立 schema
- facts-tooling.md F-83~F-94：服务发现验证器从 manifest 收集 zeroconf/dhcp/ssdp/usb/bluetooth 条目，生成 `homeassistant/generated/*.py` 文件
- facts-core.md F-268~F-276：`Integration.resolve_from_root()` 读取 manifest，自定义集成版本号必须符合 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 之一

**意义**：新集成必须首先编写合规的 `manifest.json` 并通过 hassfest 验证。现代集成应优先实现 ConfigFlow 而非 YAML 配置——`cv.config_entry_only_config_schema(DOMAIN)` 是标准做法。`ConfigEntry.runtime_data` 是存储 API 客户端/协调器等运行时对象的标准位置，类型应使用 `Dataclass` 而非字典。版本升级时实现 `async_migrate_entry` 处理数据结构变更，MQTT 从 1.x 到 2.1、Anthropic 从 2.1 到 2.3 的迁移是参考范例。

---

## 洞察四：Entity 抽象与设备注册表——统一设备能力的声明式实体模型

**观察**：`Entity` 是所有设备能力的抽象基类，定义了 30+ 标准属性（name/state/available/unique_id/icon/unit_of_measurement/device_class/entity_category/supported_features 等）和两个生命周期钩子（`async_added_to_hass`/`async_will_remove_from_hass`）。实体属性支持三种声明方式：`_attr_*` 类属性后备值、`EntityDescription` frozen dataclass 元数据、`cached_property` 计算属性。继承层次为 `Entity` → `ToggleEntity`（添加 is_on/async_turn_on/async_turn_off/async_toggle）→ `LightEntity`/`SwitchEntity`/`AutomationEntity` 等；`RestoreEntity` 混入提供状态恢复能力。每个实体通过 `unique_id` 进入 `EntityRegistry`，通过 `device_info`（含 identifiers/connections/via_device）关联到 `DeviceRegistry`，设备可归属 `AreaRegistry` 中的区域。三个注册表均继承 `BaseRegistry`，使用 `Store` 延迟写入持久化。

**根因**：IoT 设备的碎片化是 HA 面临的根本挑战——同一类"灯"，Philips Hue 通过 Zigbee、Tuya 通过云端 MQTT、MQTT 通过主题消息控制，但用户和自动化期望统一的 `light.turn_on` 服务。Entity 抽象定义了"一个能力看起来像什么"（状态+属性）和"能做什么"（服务+supported_features 位标志），使得上层无需关心底层协议。`unique_id` 的稳定性是注册表的基石——它确保重启后用户自定义的实体名称、区域分配、禁用状态不丢失。`DeviceInfo` 的 identifiers/connections 双轨制允许不同集成通过 MAC 地址或设备序列号聚合到同一设备（如 Hue 灯同时被 ZHA 和 Hue 集成发现时合并）。`via_device` 建立父子关系（如传感器通过 Zigbee 协调器入网），支持拓扑可视化。

**证据**：
- facts-helpers.md F-23~F-53：`Entity` 基类定义，`EntityDescription` 含 key/device_class/entity_category/translation_key 等字段，`EntityCategory` 仅 CONFIG/DIAGNOSTIC 两值
- facts-components.md F-34~F-50：实体继承层次——LightEntity/SwitchEntity→ToggleEntity，SensorEntity/BinarySensorEntity/ClimateEntity→Entity，ButtonEntity→RestoreEntity
- facts-components.md F-83~F-87：`LightEntity` 声明 14 个缓存属性（brightness/color_mode/rgb_color 等），使用 `CACHED_PROPERTIES_WITH_ATTR_` 元类参数
- facts-helpers.md F-54~F-68：`DeviceInfo` TypedDict 含 identifiers/connections/via_device/manufacturer/model/sw_version/serial_number/configuration_url
- facts-helpers.md F-69~F-80：`BaseRegistry` 使用 Store 持久化，`BaseRegistryItems` 维护 `_entries` 字典和 `_index` 反向索引，延迟保存避免频繁写盘
- facts-components.md F-120：Sensor 实体禁止 `entity_category=CONFIG`，否则抛 `HomeAssistantError`——配置类实体应使用 `switch`/`number`/`select` 等可写平台
- facts-helpers.md F-47：`Entity.async_on_remove` 注册实体移除时的清理回调，防止资源泄漏
- facts-core.md F-135~F-136：`StateMachine.async_reserve()` 为即将添加的实体预留 entity_id，防止并发注册竞态

**意义**：集成开发者必须为每个实体提供稳定且唯一的 `unique_id`——使用设备序列号、MAC 地址或 UUID，绝不能用易变的设备名称。`device_info` 应至少提供一组 `identifiers`（格式为 `(integration_domain, unique_device_id)`），以便设备注册表正确聚合。实体状态计算应放在 `native_value`（Sensor）或 `is_on`（ToggleEntity）等属性中，通过 `cached_property` 缓存，在 `update()` 或推送回调中清除缓存。`entity_category` 应正确标记——配置参数（如调光曲线）用 CONFIG，诊断信息（如 RSSI 信号）用 DIAGNOSTIC，主状态实体留空。

---

## 洞察五：规模化质量保障——hassfest 29 验证器 + quality_scale 54 规则 + 严格测试基础设施

**观察**：HA 项目通过三层质量门禁保障 2000+ 集成的健康度。第一层是 hassfest——29 个验证插件（23 个集成级 + 6 个全局级），覆盖 manifest schema 校验、依赖完整性（AST 解析检测未声明依赖）、服务发现索引生成、codeowners 自动维护、翻译键格式、服务注册与 services.yaml 一致性、config_flow 文件存在性与 unique_id 设置、quality_scale 合规等。第二层是 quality_scale——bronze（20 条规则：config-flow、unique-config-entry、entity-unique-id 等基础要求）、silver（10 条：config-entry-unloading、parallel-updates、reauthentication-flow、test-coverage 等）、gold（21 条：devices、diagnostics、discovery、entity-translations、reconfiguration-flow、repair-issues 等）、platinum（3 条：async-dependency、inject-websession、strict-typing），部分规则带程序化验证器。第三层是测试基础设施——pytest-asyncio auto 模式、socket/DNS 禁网（仅允许 localhost）、`verify_cleanup` autouse fixture 检测残留任务/定时器/线程、syrupy 快照测试（自定义序列化器自动替换 entry_id/device_id/时间戳为 ANY，支持 xdist 并行合并）、`MockConfigEntry`/`MockEntity`/`mock_device_registry` 等丰富的测试替身。

**根因**：HA 核心仓库的集成数量超过 2000，贡献者数千人，纯靠人工 code review 无法保证一致性。hassfest 将结构性约束（manifest 格式、依赖声明、文件存在性）编码为自动化检查，在 pre-commit 和 CI 阶段拦截问题，比文档约定可靠得多。quality_scale 提供阶梯式质量提升路径——新集成只需满足 bronze 即可合入，但 silver/gold/platinum 徽章引导维护者持续改进，避免"合入即弃置"。测试基础设施的严格程度与异步系统的调试难度成正比——asyncio 中的残留定时器、未取消任务、跨测试时区污染等问题极难定位，`verify_cleanup` 在每个测试后强制执行清理检查，将问题消灭在萌芽阶段。快照序列化器替换动态 ID 的设计解决了快照测试最常见的脆弱性问题。

**证据**：
- facts-tooling.md F-11~F-13：`INTEGRATION_PLUGINS` 23 个 + `HASS_PLUGINS` 6 个 = 29 验证插件，config_flow 必须最后运行（依赖 translations 完成）
- facts-tooling.md F-28~F-29：generate 模式下可修复错误（fixable）不导致失败，validate 模式下所有错误均失败——CI 用 validate，开发用 generate
- facts-tooling.md F-77~F-80：BRONZE 20 条、SILVER 10 条、GOLD 21 条、PLATINUM 3 条质量规则
- facts-tooling.md F-81：7 条规则带程序化验证器（config-flow/discovery/reconfiguration-flow/runtime-data/strict-typing/test-before-setup/unique-config-entry）
- facts-tooling.md F-122~F-127：dependencies 验证器使用 AST `ImportCollector` 解析数千文件，`multiprocessing.Pool` 并行，检测未声明依赖/重复依赖/循环依赖
- facts-tooling.md F-148~F-161：conftest.py 禁网配置——`pytest_socket` 仅允许 127.0.0.1，DNS 仅允许 localhost，`verify_cleanup` 检查残留任务/定时器/线程/时区/respx mock
- facts-tooling.md F-204~F-218：`HomeAssistantSnapshotSerializer` 将 State/ConfigEntry/DeviceEntry/EntityRegistryEntry 中的动态 ID 和时间戳替换为 ANY，快照目录从 `__snapshots__` 改为 `snapshots`，支持 xdist worker 结果合并
- facts-tooling.md F-108~F-112：scaffold 根据 integration_type 自动选择 config_flow 模板（helper→config_flow_helper，oauth2→config_flow_oauth2，可发现→config_flow_discovery）
- facts-tooling.md F-234~F-250：mypy.ini 由 hassfest 自动生成，`.strict-typing` 列出启用 `disallow_any_generics` 的模块，ruff 启用 30+ 规则集

**意义**：集成贡献者应在开发循环中尽早运行 `python -m script.hassfest`（单集成：`--integration-path`），而非等到 CI 失败。新集成使用 `python -m script.scaffold <template>` 生成骨架，确保目录结构和测试模板符合规范。测试必须使用 `hass` fixture 而非手动创建 `HomeAssistant` 实例，网络访问通过 `respx`/`aiohttp_client` mock。快照测试中不要手动硬编码 entry_id——序列化器会自动处理，快照变更时用 `--snapshot-update` 更新。质量等级应作为集成成熟度的路标，而非一次性目标。

---

## 知识地图

> 19 篇概念文档，分 3 批组织。每篇列出核心问题、信源文件和 Grep 验证清单（关键类/函数/常量）。

### 第 1 批：入门组（00-06，7 篇）

#### 00-overview.md
- **核心问题**：Home Assistant 是什么？它解决什么问题？核心-集成-平台三层架构如何协作？事件驱动模型的基本数据流是什么？从设备状态变化到 UI 更新经历哪些环节？
- **信源**：facts-core.md, facts-components.md, facts-helpers.md
- **Grep 验证**：`HomeAssistant`, `EventBus`, `StateMachine`, `ServiceRegistry`, `EntityComponent`, `ConfigEntry`, `manifest.json`, `async_setup_component`, `PLATFORM_FORMAT`

#### 01-architecture.md
- **核心问题**：核心层、集成层、平台层各自的职责边界是什么？bootstrap 如何按 Stage 0/1/2 加载集成？dependencies 与 after_dependencies 的区别？EntityComponent 如何管理实体？平台转发机制如何工作？
- **信源**：facts-core.md（bootstrap/setup/loader）, facts-components.md（setup 模式/平台转发）
- **Grep 验证**：`STAGE_0_INTEGRATIONS`, `STAGE_1_INTEGRATIONS`, `CORE_INTEGRATIONS`, `async_setup_component`, `async_forward_entry_setups`, `EntityComponent`, `Integration`, `resolve_dependencies`, `BASE_PRELOAD_PLATFORMS`

#### 02-installation-runner.md
- **核心问题**：HA 的启动入口在哪里？`RuntimeConfig` 包含哪些参数？`HassEventLoopPolicy` 如何定制事件循环？单实例锁如何实现？事件循环异常处理器如何处理 EMFILE？任务取消超时机制是什么？
- **信源**：facts-core.md（runner 节 F-285~F-299）
- **Grep 验证**：`RuntimeConfig`, `HassEventLoopPolicy`, `ensure_single_execution`, `setup_and_run_hass`, `MAX_EXECUTOR_WORKERS`, `TASK_CANCELATION_TIMEOUT`, `LOCK_FILE_NAME`, `_cancel_all_tasks_with_timeout`, `InterruptibleThreadPoolExecutor`

#### 03-core-object.md
- **核心问题**：`HomeAssistant` 根对象持有哪些子系统和状态？`hass.data` 的用途和 HassKey 类型安全机制？`add_job`/`async_add_job`/`async_create_task` 的区别和使用场景？`verify_event_loop_thread` 如何保护线程安全？线程局部变量 `_hass` 的作用？
- **信源**：facts-core.md（HomeAssistant 核心对象 F-56~F-83）
- **Grep 验证**：`HomeAssistant`, `HassDict`, `HassKey`, `add_job`, `async_add_job`, `async_create_task`, `async_block_till_done`, `verify_event_loop_thread`, `async_get_hass`, `BLOCK_LOG_TIMEOUT`, `import_executor`

#### 04-bootstrap-lifecycle.md
- **核心问题**：`async_setup_hass` 的完整启动流程是什么？CoreState 六状态（not_running/starting/running/stopping/final_write/stopped）如何转换？async_stop 四阶段各触发什么事件？`_WatchPendingSetups` 如何监控慢启动？恢复模式和安全模式何时激活？
- **信源**：facts-core.md（CoreState F-33~F-55, bootstrap F-185~F-217）
- **Grep 验证**：`CoreState`, `async_start`, `async_stop`, `async_run`, `EVENT_HOMEASSISTANT_START`, `EVENT_HOMEASSISTANT_STARTED`, `EVENT_HOMEASSISTANT_STOP`, `EVENT_HOMEASSISTANT_FINAL_WRITE`, `EVENT_HOMEASSISTANT_CLOSE`, `_WatchPendingSetups`, `TIMEOUT_EVENT_START`, `recovery_mode`

#### 05-configuration.md
- **核心问题**：`Config` 对象管理哪些配置？YAML 配置（configuration.yaml）与 ConfigEntry 存储配置如何并存？`async_ensure_config_exists` 和配置升级流程？`ConfigSource` 枚举的含义？`allowlist_external_dirs`/`media_dirs` 的安全作用？
- **信源**：facts-core.md（Config F-218~F-247, ConfigEntry F-248~F-266）
- **Grep 验证**：`Config`, `YAML_CONFIG_FILE`, `CONFIG_DIR_NAME`, `async_ensure_config_exists`, `process_ha_config_upgrade`, `async_from_config_dict`, `ConfigSource`, `DEFAULT_CONFIG`, `ConfigEntryState`, `STORAGE_KEY`

#### 06-event-bus.md
- **核心问题**：Event/Context/EventOrigin 的数据模型是什么？ULID Context ID 的优势？`fire`（线程安全）与 `async_fire`（事件循环内）的区别？嵌套事件触发的入队保护机制？`async_listen`/`async_listen_once`/`MATCH_ALL` 的使用？event_filter 的作用和约束？
- **信源**：facts-core.md（Event/EventBus F-85~F-115）
- **Grep 验证**：`Event`, `Context`, `EventOrigin`, `EventBus`, `async_fire`, `async_listen`, `async_listen_once`, `MATCH_ALL`, `_OneTimeListener`, `_MAX_QUEUED_EVENT_DISPATCHES`, `EVENT_STATE_CHANGED`, `EVENT_STATE_REPORTED`, `ulid_now`

### 第 2 批：核心组（07-13，7 篇）

#### 07-state-machine.md
- **核心问题**：State 对象的不可变设计和 `__slots__` 优化？`States` 二级索引如何按 domain 加速查询？`async_set` 的状态变化检测逻辑——何时触发 STATE_CHANGED vs STATE_REPORTED？`async_reserve` 如何防止 entity_id 竞态？State 的压缩序列化格式？`expire()` 如何辅助 GC？
- **信源**：facts-core.md（State/StateMachine F-116~F-147）
- **Grep 验证**：`State`, `States`, `StateMachine`, `async_set`, `async_remove`, `async_reserve`, `async_available`, `EVENT_STATE_CHANGED`, `EVENT_STATE_REPORTED`, `split_entity_id`, `valid_entity_id`, `as_compressed_state`, `expire`, `MAX_LENGTH_STATE_STATE`

#### 08-service-registry.md
- **核心问题**：Service/ServiceCall/ServiceRegistry 的数据模型？`SupportsResponse` 三态（NONE/OPTIONAL/ONLY）语义？服务调用的阻塞/非阻塞模式和异常处理？HassJob 如何自动选择协程/回调/执行器执行方式？服务注册/移除时的事件通知？entity_service 装饰器如何解析目标实体？
- **信源**：facts-core.md（Service F-148~F-176, HassJob F-416~F-424）, facts-helpers.md（service helpers F-139~F-154）
- **Grep 验证**：`Service`, `ServiceCall`, `ServiceRegistry`, `SupportsResponse`, `async_register`, `async_call`, `async_remove`, `HassJob`, `HassJobType`, `EVENT_CALL_SERVICE`, `EVENT_SERVICE_REGISTERED`, `entity_service`, `ServiceNotFound`, `return_response`

#### 09-entity-model.md
- **核心问题**：Entity 基类的属性体系和生命周期钩子？`_attr_*` 后备值、EntityDescription、cached_property 三种声明方式的优先级？ToggleEntity 为可开关实体添加了什么？EntityCategory（CONFIG/DIAGNOSTIC）如何影响 UI？`async_update_ha_state` vs `schedule_update_ha_state`？`should_poll` 与推送更新的关系？
- **信源**：facts-helpers.md（Entity F-23~F-53）, facts-components.md（实体继承 F-34~F-50, 各平台实体）
- **Grep 验证**：`Entity`, `EntityDescription`, `ToggleEntity`, `RestoreEntity`, `EntityCategory`, `async_added_to_hass`, `async_will_remove_from_hass`, `async_update_ha_state`, `schedule_update_ha_state`, `should_poll`, `unique_id`, `device_info`, `supported_features`, `CACHED_PROPERTIES_WITH_ATTR_`

#### 10-registries.md
- **核心问题**：BaseRegistry/BaseRegistryItems 的通用持久化机制？DeviceRegistry/EntityRegistry/AreaRegistry 各自管理什么？DeviceInfo 的 identifiers/connections/via_device 如何实现设备聚合？注册表的延迟写入和索引维护？`async_entries_for_config_entry` 如何按集成查询设备？
- **信源**：facts-helpers.md（Device F-54~F-68, Registry F-69~F-80）
- **Grep 验证**：`BaseRegistry`, `BaseRegistryItems`, `DeviceRegistry`, `EntityRegistry`, `AreaRegistry`, `DeviceInfo`, `DeviceIdentifier`, `DeviceConnection`, `async_device_info_to_dr_device_info`, `async_entries_for_config_entry`, `via_device`, `Store`

#### 11-auth-permissions.md
- **核心问题**：AuthManager 如何管理用户/凭证/令牌？JWT access token 和 refresh token 的生命周期？系统用户与普通用户的区别？Group 策略合并和权限缓存？owner/admin 权限判定？登录流程（AuthManagerFlowManager）？
- **信源**：facts-core.md（auth 节 F-341~F-386）
- **Grep 验证**：`AuthManager`, `User`, `Group`, `Credentials`, `RefreshToken`, `async_create_user`, `async_create_access_token`, `async_validate_access_token`, `TOKEN_TYPE_NORMAL`, `TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN`, `OwnerPermissions`, `AuthStore`, `JWT`

#### 12-helpers-library.md
- **核心问题**：helpers 包提供哪些关键基础设施？Template 引擎的 Jinja2 封装和 RenderInfo 自动更新跟踪？Debouncer/Throttle 防抖节流模式？Storage Store 的延迟写入和版本迁移？config_validation 验证器库？Selector 选择器体系？trigger/script/condition 自动化基础设施？
- **信源**：facts-helpers.md（Template F-81~F-100, ConfigValidation F-101~F-138, EventHelpers F-155~F-171, Trigger/Script/Condition F-172~F-190, Storage F-244~F-256, Debouncer F-257~F-262, Selector F-221~F-243）
- **Grep 验证**：`Template`, `TemplateState`, `RenderInfo`, `Debouncer`, `Throttle`, `Store`, `async_call_later`, `async_track_state_change`, `TrackTemplate`, `Script`, `ScriptMode`, `Selector`, `EntitySelector`, `config_validation`, `intent`, `llm`

#### 13-utilities.md
- **核心问题**：util 包与 helpers 包的定位区别？dt 模块的时间处理——ciso8601 快速解析、aiozoneinfo 异步时区、parse_duration 多格式支持？json 模块的 orjson 集成和序列化器？yaml 加载器的 annotatedyaml 和 !secret 处理？async_ 工具的 run_callback_threadsafe 和并发限制？
- **信源**：facts-helpers.md（util F-305~F-399）
- **Grep 验证**：`slugify`, `convert`, `Throttle`, `utcnow`, `parse_datetime`, `parse_duration`, `as_timestamp`, `get_time_zone`, `async_get_time_zone`, `json_loads`, `load_json`, `load_yaml`, `create_eager_task`, `run_callback_threadsafe`, `gather_with_limited_concurrency`, `orjson`, `ciso8601`

### 第 3 批：高级/开发组（14-18，5 篇）

#### 14-component-architecture.md
- **核心问题**：集成目录的标准结构是什么？manifest.json 各字段的语义和验证规则？integration_type（hub/service/entity/system/hardware/helper/virtual/device）如何影响加载行为？iot_class 的六种通信模式？`async_setup`/`async_setup_entry`/`async_unload_entry` 三函数契约？`hass.data` 中 DATA_COMPONENT 的存储模式？
- **信源**：facts-components.md（manifest F-1~F-33, setup 模式 F-195~F-214）, facts-core.md（loader F-267~F-283）, facts-tooling.md（manifest 验证 F-45~F-71）
- **Grep 验证**：`manifest.json`, `Integration`, `integration_type`, `iot_class`, `async_setup`, `async_setup_entry`, `async_unload_entry`, `async_remove_entry`, `DATA_COMPONENT`, `HassKey`, `PLATFORM_SCHEMA`, `cv.config_entry_only_config_schema`, `CODEOWNERS`, `requirements`

#### 15-config-flow.md
- **核心问题**：ConfigFlow 的状态机模型（FlowResultType 8 种结果）？多步表单如何实现？`async_step_user`/`async_step_discovery`/`async_step_reauth` 的职责？OptionsFlow 与 ConfigFlow 的关系？配置条目版本迁移 `async_migrate_entry` 的实现模式？ConfigSubentry 的使用场景？外部 OAuth 跳转如何处理？
- **信源**：facts-core.md（data_entry_flow F-328~F-340, ConfigEntry F-248~F-266）, facts-components.md（config_flow F-216~F-223）
- **Grep 验证**：`ConfigFlow`, `OptionsFlow`, `ConfigSubentryFlow`, `FlowResultType`, `FlowManager`, `async_step_user`, `async_step_reauth`, `async_step_reconfigure`, `async_migrate_entry`, `SOURCE_USER`, `SOURCE_REAUTH`, `SOURCE_RECONFIGURE`, `AbortFlow`, `ConfigEntry`, `ConfigEntryState`

#### 16-platform-pattern.md
- **核心问题**：各平台实体（Light/Sensor/Switch/BinarySensor/Climate/Cover/Select/Number/Button/Camera/MediaPlayer）的特有抽象？EntityDescription 继承体系和 frozen_or_thawed 模式？`async_register_entity_service` 如何注册实体级服务？supported_features IntFlag 位标志如何声明能力？device_class/state_class 如何影响 UI 和历史统计？单位转换机制？
- **信源**：facts-components.md（Light F-51~F-91, Sensor F-92~F-120, Switch/BinarySensor F-121~F-140, Climate/Cover/MediaPlayer F-141~F-170, Select/Number/Button F-171~F-194）
- **Grep 验证**：`LightEntity`, `SensorEntity`, `SwitchEntity`, `BinarySensorEntity`, `ClimateEntity`, `CoverEntity`, `ColorMode`, `SensorDeviceClass`, `SensorStateClass`, `HVACMode`, `CoverEntityFeature`, `MediaPlayerEntityFeature`, `EntityComponent`, `async_register_entity_service`, `SCAN_INTERVAL`, `UNIT_CONVERTERS`

#### 17-hassfest-tooling.md
- **核心问题**：hassfest 的 29 个验证插件各检查什么？validate 与 generate 模式的区别？quality_scale 四级 54 条规则的阶梯逻辑？dependencies 验证器如何用 AST 检测未声明依赖？服务发现验证器如何生成 `homeassistant/generated/` 文件？scaffold 脚手架如何根据集成类型选择模板？mypy.ini 自动生成机制？
- **信源**：facts-tooling.md（hassfest F-1~F-95, scaffold F-105~F-113, 其他 script F-114~F-135）
- **Grep 验证**：`hassfest`, `INTEGRATION_PLUGINS`, `HASS_PLUGINS`, `INTEGRATION_MANIFEST_SCHEMA`, `quality_scale`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `ImportCollector`, `scaffold`, `sort_manifest`, `mypy_config`, `.strict-typing`, `codeowners`, `zeroconf`, `dhcp`, `ssdp`

#### 18-testing-patterns.md
- **核心问题**：pytest-asyncio auto 模式如何工作？`hass` fixture 如何创建测试用 HA 实例？`verify_cleanup` 检测哪些资源泄漏？socket/DNS 禁网策略和例外？syrupy 快照序列化器如何处理动态 ID？MockConfigEntry/MockEntity 的使用模式？`async_fire_time_changed` 如何测试时间逻辑？`enable_custom_integrations` 的作用？
- **信源**：facts-tooling.md（pytest F-136~F-174, tests/common F-175~F-203, syrupy F-204~F-218, patch F-219~F-225, 测试模式 F-226~F-233）
- **Grep 验证**：`hass`, `hass_client`, `MockConfigEntry`, `MockEntity`, `mock_device_registry`, `verify_cleanup`, `snapshot`, `HomeAssistantSnapshotExtension`, `async_fire_time_changed`, `async_mock_service`, `mock_storage`, `enable_custom_integrations`, `pytest_socket`, `respx`, `freezegun`, `INSTANCES`, `assert_setup_component`
