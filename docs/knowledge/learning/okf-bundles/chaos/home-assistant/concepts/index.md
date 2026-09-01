# 概念文档

## 基础组（00-06）：平台认知与启动

* [00 — Home Assistant 概览](/concepts/00-overview.md) — 了解 Home Assistant 是什么、核心能力、架构一览，快速建立对智能家居自动化平台的整体认知
* [01 — 三层架构：核心-集成-平台](/concepts/01-architecture.md) — 理解 Home Assistant 的三层架构设计，核心层、集成层与平台层的职责划分、交互方式和设计理念
* [02 — 安装与启动](/concepts/02-installation-runner.md) — 了解 Home Assistant 的安装方式、runner.py 进程入口、命令行参数、事件循环策略和单实例锁机制
* [03 — HomeAssistant 核心对象](/concepts/03-core-object.md) — 深入理解 HomeAssistant 根对象的属性、方法、生命周期与 CoreState 状态机，掌握 HA 运行时核心
* [04 — 启动流程](/concepts/04-bootstrap-lifecycle.md) — 详解 Home Assistant 的 bootstrap 启动阶段、组件加载顺序、依赖解析、Stage 0/1/2 分阶段加载机制
* [05 — 配置系统](/concepts/05-configuration.md) — 掌握 Home Assistant 配置系统，包括 configuration.yaml 结构、Config 类、核心配置项、secrets 管理和 YAML 验证
* [06 — 事件总线](/concepts/06-event-bus.md) — 掌握 Home Assistant 事件总线机制，包括 Event 对象、EventBus 发布订阅、监听/触发模式和内置事件类型

## 核心组（07-13）：运行时与工具库

* [07 — 状态机](/concepts/07-state-machine.md) — 深入理解 Home Assistant 状态机机制，包括 State 对象结构、StateMachine 的 async_set/async_remove 方法、STATE_CHANGED 与 STATE_REPORTED 事件的区别，以及状态恢复原理
* [08 — 服务注册表](/concepts/08-service-registry.md) — 掌握 Home Assistant 服务注册表机制，包括 Service/ServiceCall/ServiceRegistry 的结构、async_register/async_call 方法、实体服务装饰器、响应支持模式和服务描述系统
* [09 — 实体模型](/concepts/09-entity-model.md) — 深入理解 Home Assistant 实体模型，包括 Entity 基类、ToggleEntity、EntityDescription 声明式配置、EntityCategory 分类、_attr_ 属性后备机制、cached_properties 缓存和生命周期方法
* [10 — 注册表](/concepts/10-registries.md) — 理解 Home Assistant 注册表体系，包括 DeviceRegistry、EntityRegistry、AreaRegistry 的职责、RegistryStore 持久化机制、DeviceInfo 设备信息结构，以及唯一ID在设备-实体关联中的作用
* [11 — 认证与权限](/concepts/11-auth-permissions.md) — 深入理解 Home Assistant 认证与权限体系，包括 AuthManager、User、RefreshToken、JWT 令牌机制、Permission 权限策略、Owner/Admin/User 角色，以及 auth_store 持久化
* [12 — Helpers 工具库](/concepts/12-helpers-library.md) — 掌握 Home Assistant helpers 工具库，包括 Template 模板引擎、event helpers 状态跟踪、Debouncer 防抖、signal dispatcher 信号分发、Storage Store 持久化、Selector 选择器、config_validation 验证器和 intent/llm 集成
* [13 — Util 工具集](/concepts/13-utilities.md) — 掌握 Home Assistant util 工具集，包括 dt 日期时间处理、json（orjson）序列化、yaml（!secret）加载、async_ 异步工具、color 颜色空间转换、unit_system 单位系统、timeout 超时管理、ulid 标识符和 network 网络工具

## 高级/开发组（14-18）：集成开发

* [14 — 集成架构](/concepts/14-component-architecture.md) — 深入理解 Home Assistant 集成目录结构、manifest.json 字段契约、integration_type 与 iot_class 分类、async_setup/async_setup_entry/async_unload_entry 三函数生命周期以及依赖解析机制
* [15 — 配置流](/concepts/15-config-flow.md) — 掌握 ConfigFlow 状态机模型、多步表单实现、async_step_user/discovery/reauth 步骤、OptionsFlow 选项配置、async_migrate_entry 版本迁移与 ConfigSubentry 子条目机制
* [16 — 平台开发模式](/concepts/16-platform-pattern.md) — 掌握各平台实体基类（Light/Sensor/Switch/BinarySensor/Climate/Cover 等）的使用、PLATFORM_SCHEMA、async_forward_entry_setups 转发、EntityDescription 声明式模式、async_register_entity_service 实体服务注册与 supported_features 位标志
* [17 — hassfest 工具链](/concepts/17-hassfest-tooling.md) — 掌握 hassfest 29 个验证插件架构、validate 与 generate 双模式、quality_scale 四级 54 条质量规则、dependencies AST 依赖检测、scaffold 脚手架、translations 翻译工具、codeowners 自动生成与 mypy.ini 自动生成
* [18 — 测试模式](/concepts/18-testing-patterns.md) — 掌握 Home Assistant pytest 配置、conftest fixtures（hass/hass_client/snapshot）、tests/common.py 测试工具、syrupy 快照测试、MockConfigEntry、enable_custom_integrations、禁网/DNS 限制与 verify_cleanup 资源泄漏检测

```{toctree}
:maxdepth: 2

00-overview
01-architecture
02-installation-runner
03-core-object
04-bootstrap-lifecycle
05-configuration
06-event-bus
07-state-machine
08-service-registry
09-entity-model
10-registries
11-auth-permissions
12-helpers-library
13-utilities
14-component-architecture
15-config-flow
16-platform-pattern
17-hassfest-tooling
18-testing-patterns
```