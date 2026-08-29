---
type: Reference
title: Home Assistant 核心框架源码
description: Home Assistant Core 运行时内核源码登记，包含核心对象、事件总线、状态机、服务注册、启动流程、认证体系与异常层次
tags: [home-assistant, smart-home, core, source, reference, python, asyncio]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-core
    resource: "/references/facts-core.md"
    title: Home Assistant Core 核心架构事实清单
---

# Home Assistant 核心框架源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | Home Assistant Core |
| 定位 | 开源智能家居自动化平台，基于 Python asyncio 的事件驱动内核 |
| 许可证 | Apache License 2.0 |
| 主语言 | Python 3.14+ |
| 版本 | 2026.8.0.dev0 |
| 仓库地址 | https://github.com/home-assistant/core |
| 本地路径 | `d:\AI\.chaos\libs\home-assistant\core\homeassistant\` |

## 根目录核心文件

源码根路径：`homeassistant/`

| 文件 | 职责 |
|------|------|
| `core.py` | 核心运行时：`HomeAssistant` 根对象、`EventBus`、`StateMachine`、`ServiceRegistry`、`Context`、`CoreState` |
| `const.py` | 全局常量：版本号、事件类型、状态常量、配置键 `CONF_*`、平台枚举 |
| `bootstrap.py` | 启动编排：`async_setup_hass()`、Stage 0/1/2 集成加载、日志配置、恢复模式 |
| `runner.py` | 进程入口：`RuntimeConfig`、`HassEventLoopPolicy`、单实例锁、事件循环策略 |
| `config.py` | 配置文件管理：`YAML_CONFIG_FILE`、`DEFAULT_CONFIG`、配置路径常量 |
| `core_config.py` | 核心配置对象：`Config` 类、位置/时区/单位/白名单等运行时配置 |
| `config_entries.py` | 配置条目管理：`ConfigEntry`、`ConfigEntries`、`ConfigFlow` 注册表、条目状态机 |
| `setup.py` | 组件设置：`async_setup_component()`、依赖解析、设置超时、平台加载 |
| `loader.py` | 集成加载器：`Integration` 类、`manifest.json` 解析、自定义组件、依赖准备 |
| `data_entry_flow.py` | 数据录入流：`FlowManager`、`FlowResultType`、配置流基类 |
| `exceptions.py` | 异常层次：`HomeAssistantError` 基类及 30+ 子类 |
| `requirements.py` | Python 依赖管理：requirements 安装与版本约束 |
| `__main__.py` | 模块入口：`python -m homeassistant` 命令行启动 |
| `block_async_io.py` | 异步 I/O 保护：阻塞事件循环的检测 |
| `backup_restore.py` | 备份与恢复：系统备份管理 |

## auth/ 认证子系统

路径：`homeassistant/auth/`

| 文件 | 职责 |
|------|------|
| `__init__.py` | `AuthManager` 类、用户/凭证/刷新令牌管理、登录流程、JWT 签发与验证 |
| `models.py` | 数据模型：`User`、`Group`、`RefreshToken`、`Credentials`、`UserMeta` |
| `auth_store.py` | `AuthStore`：基于 `Store` 的认证数据持久化，懒加载 |
| `jwt_wrapper.py` | JWT 封装：PyJWT 缓存、token 大小限制、HS256 验证 |
| `const.py` | 认证常量：token 过期时间、系统组 ID |

## 关键类与函数

### 核心对象（core.py）

| 名称 | 类型 | 行号 | 说明 |
|------|------|------|------|
| `HomeAssistant` | 类 | 379 | HA 自动化框架根对象，持有所有子系统 |
| `CoreState` | Enum | 363 | 运行时状态：not_running/starting/running/stopping/final_write/stopped |
| `EventBus` | 类 | 1445 | 事件总线，发布-订阅模式 |
| `Event` | 类 | 1294 | 事件对象，泛型 `Generic[_DataT]`，`@final` 禁止子类化 |
| `Context` | 类 | 1221 | 事件上下文，ULID 作为唯一可排序 ID |
| `EventOrigin` | Enum | 1277 | 事件来源：local/remote |
| `StateMachine` | 类 | 2139 | 状态机，管理实体状态与变更事件 |
| `State` | 类 | 1795 | 不可变状态对象，使用 `__slots__` |
| `States` | 类 | 2091 | 状态集合，维护 domain 二级索引 |
| `ServiceRegistry` | 类 | 2559 | 服务注册中心，domain → service 映射 |
| `Service` | 类 | 2491 | 服务描述，包装 `HassJob` 和 schema |
| `ServiceCall` | 类 | 2525 | 服务调用上下文 |
| `SupportsResponse` | StrEnum | 2475 | 服务响应模式：NONE/OPTIONAL/ONLY |
| `HassJob` | 类 | 303 | 作业包装，自动识别协程/回调/执行器类型 |
| `HassJobType` | Enum | 285 | 作业类型：Coroutinefunction/Callback/Executor |
| `callback` | 装饰器 | 209 | 标记函数为事件循环安全 |
| `HassDict` | 类 | - | 类型安全字典，配合 `HassKey` 使用 |
| `split_entity_id` | 函数 | 169 | 拆分 entity_id 为 (domain, object_id)，lru_cache |
| `valid_entity_id` | 函数 | 190 | 校验实体 ID 格式，lru_cache |
| `validate_state` | 函数 | 199 | 校验状态值长度不超过 255 字符 |
| `async_get_hass` | 函数 | 241 | 从线程局部变量获取 HA 实例 |

### 启动与配置（bootstrap.py, runner.py, config.py, core_config.py）

| 名称 | 类型 | 文件 | 说明 |
|------|------|------|------|
| `async_setup_hass` | 协程 | bootstrap.py:309 | 顶层启动协程，接收 `RuntimeConfig` |
| `async_from_config_dict` | 协程 | bootstrap.py:520 | 从配置字典加载集成 |
| `_async_set_up_integrations` | 协程 | bootstrap.py:907 | 按 Stage 0→1→2 顺序加载集成 |
| `async_load_base_functionality` | 协程 | bootstrap.py:484 | 并行加载注册表基础设施 |
| `RuntimeConfig` | dataclass | runner.py:155 | 运行时配置参数 |
| `HassEventLoopPolicy` | 类 | runner.py:176 | 自定义 asyncio 事件循环策略 |
| `ensure_single_execution` | 上下文管理器 | runner.py:118 | 文件锁确保单实例运行 |
| `setup_and_run_hass` | 协程 | runner.py:254 | 调用 bootstrap 后运行 HA |
| `run` | 函数 | runner.py:280 | 主入口函数 |
| `Config` | 类 | core_config.py:534 | 核心配置对象 |
| `ConfigSource` | Enum | core_config.py | 配置来源：DEFAULT/STORAGE/YAML/DISCOVERED |
| `YAML_CONFIG_FILE` | 常量 | config.py:39 | `"configuration.yaml"` |
| `CONFIG_DIR_NAME` | 常量 | config.py:41 | `".homeassistant"` |
| `DEFAULT_CONFIG` | 字典 | config.py:52 | 默认配置模板 |

### 组件设置与加载（setup.py, loader.py）

| 名称 | 类型 | 文件 | 说明 |
|------|------|------|------|
| `async_setup_component` | 协程 | setup.py:148 | 公共组件设置入口 |
| `_async_setup_component` | 协程 | setup.py:280 | 内部设置实现 |
| `SetupPhases` | StrEnum | setup.py:665 | 设置阶段枚举 |
| `async_when_setup` | 协程 | setup.py:591 | 注册组件设置完成回调 |
| `async_wait_component` | 协程 | setup.py:836 | 等待组件设置完成 |
| `Integration` | 类 | loader.py:667 | 集成元数据与代码加载 |
| `Manifest` | TypedDict | loader.py:246 | manifest.json 结构定义 |
| `IntegrationNotFound` | 异常 | loader.py:1654 | 集成未找到 |
| `CORE_INTEGRATIONS` | 集合 | bootstrap.py:152 | `{"homeassistant", "persistent_notification"}` |
| `STAGE_0_INTEGRATIONS` | 元组 | bootstrap.py:183 | 第一阶段集成序列 |
| `STAGE_1_INTEGRATIONS` | 元组 | bootstrap.py:200 | 第二阶段集成序列 |
| `DEFAULT_INTEGRATIONS` | 集合 | bootstrap.py:215 | 默认加载集成 |
| `CRITICAL_INTEGRATIONS` | 集合 | bootstrap.py:280 | `{"frontend"}`，失败则恢复模式 |

### 配置条目（config_entries.py, data_entry_flow.py）

| 名称 | 类型 | 文件 | 说明 |
|------|------|------|------|
| `ConfigEntry` | 类 | config_entries.py | 配置条目运行时对象 |
| `ConfigEntries` | 类 | config_entries.py | 配置条目管理器 |
| `ConfigEntryState` | Enum | config_entries.py:147 | 8 种状态：LOADED/SETUP_ERROR/MIGRATION_ERROR 等 |
| `ConfigEntryChange` | StrEnum | config_entries.py:224 | ADDED/REMOVED/UPDATED |
| `SIGNAL_CONFIG_ENTRY_CHANGED` | SignalType | config_entries.py:205 | 配置条目变更信号 |
| `FlowManager` | 抽象类 | data_entry_flow.py:174 | 流程管理器基类 |
| `FlowResultType` | StrEnum | data_entry_flow.py:27 | FORM/CREATE_ENTRY/ABORT/EXTERNAL_STEP 等 8 种 |

### 认证（auth/）

| 名称 | 类型 | 文件 | 说明 |
|------|------|------|------|
| `AuthManager` | 类 | auth/__init__.py:176 | 认证管理器 |
| `auth_manager_from_config` | 协程 | auth/__init__.py:48 | 从配置创建 AuthManager |
| `User` | 类 | auth/models.py:56 | 用户模型，使用 attrs |
| `Group` | 类 | auth/models.py:40 | 用户组与权限策略 |
| `RefreshToken` | 类 | auth/models.py:103 | 刷新令牌 |
| `Credentials` | 类 | auth/models.py:133 | 认证凭证 |
| `AuthStore` | 类 | auth/auth_store.py:44 | 认证数据持久化存储 |
| `TOKEN_TYPE_NORMAL` | 常量 | auth/models.py:21 | 普通刷新令牌 |
| `TOKEN_TYPE_LONG_LIVED_ACCESS_TOKEN` | 常量 | auth/models.py:23 | 长期访问令牌 |
| `ACCESS_TOKEN_EXPIRATION` | 常量 | auth/const.py:5 | 30 分钟 |
| `REFRESH_TOKEN_EXPIRATION` | 常量 | auth/const.py:7 | 90 天 |

### 异常层次（exceptions.py）

| 名称 | 继承自 | 说明 |
|------|--------|------|
| `HomeAssistantError` | Exception | 所有 HA 异常基类，支持翻译 |
| `ConfigValidationError` | HomeAssistantError, ExceptionGroup | 配置验证错误 |
| `ServiceValidationError` | HomeAssistantError | 服务调用验证错误 |
| `ServiceNotFound` | ServiceValidationError | 服务不存在 |
| `InvalidEntityFormatError` | HomeAssistantError | 实体 ID 格式无效 |
| `IntegrationError` | HomeAssistantError | 集成错误基类 |
| `ConfigEntryError` | IntegrationError | 配置条目设置失败 |
| `ConfigEntryNotReady` | IntegrationError | 配置条目未就绪（触发重试） |
| `ConfigEntryAuthFailed` | IntegrationError | 认证失败（触发重新认证） |
| `Unauthorized` | HomeAssistantError | 未授权操作 |
| `MaxLengthExceeded` | HomeAssistantError | 超出最大长度限制 |
| `TemplateError` | HomeAssistantError | 模板渲染错误 |
| `ConditionError` | HomeAssistantError | 条件评估错误 |

### 核心事件类型常量（const.py）

| 常量 | 值 | 说明 |
|------|-----|------|
| `EVENT_CALL_SERVICE` | `"call_service"` | 服务被调用 |
| `EVENT_COMPONENT_LOADED` | `"component_loaded"` | 组件加载完成 |
| `EVENT_CORE_CONFIG_UPDATE` | `"core_config_updated"` | 核心配置更新 |
| `EVENT_HOMEASSISTANT_START` | `"homeassistant_start"` | HA 开始启动 |
| `EVENT_HOMEASSISTANT_STARTED` | `"homeassistant_started"` | HA 启动完成 |
| `EVENT_HOMEASSISTANT_STOP` | `"homeassistant_stop"` | HA 停止中 |
| `EVENT_HOMEASSISTANT_FINAL_WRITE` | `"homeassistant_final_write"` | 最终写入阶段 |
| `EVENT_HOMEASSISTANT_CLOSE` | `"homeassistant_close"` | HA 关闭 |
| `EVENT_SERVICE_REGISTERED` | `"service_registered"` | 服务注册 |
| `EVENT_SERVICE_REMOVED` | `"service_removed"` | 服务移除 |
| `EVENT_STATE_CHANGED` | `"state_changed"` | 实体状态变更 |
| `EVENT_STATE_REPORTED` | `"state_reported"` | 实体状态上报（值未变） |
| `MATCH_ALL` | `"*"` | 通配事件监听器 |

### 关键超时常量

| 常量 | 值 | 文件 | 说明 |
|------|-----|------|------|
| `REQUIRED_PYTHON_VER` | `(3, 14, 2)` | const.py:28 | 最低 Python 版本 |
| `TIMEOUT_EVENT_START` | 15 秒 | core.py:158 | 启动阶段等待任务超时 |
| `SLOW_SETUP_WARNING` | 10 秒 | setup.py:84 | 慢设置警告阈值 |
| `SLOW_SETUP_MAX_WAIT` | 300 秒 | setup.py:85 | 组件设置最大等待 |
| `STAGE_0_SUBSTAGE_TIMEOUT` | 60 秒 | bootstrap.py:145 | Stage 0 子阶段超时 |
| `STAGE_1_TIMEOUT` | 120 秒 | bootstrap.py:146 | Stage 1 超时 |
| `STAGE_2_TIMEOUT` | 300 秒 | bootstrap.py:147 | Stage 2 超时 |
| `MAX_EXECUTOR_WORKERS` | 64 | runner.py:43 | 线程池最大工作线程 |
| `TASK_CANCELATION_TIMEOUT` | 5 秒 | runner.py:44 | 任务取消超时 |
| `SETUP_RETRY_MAX_WAIT` | 600 秒 | config_entries.py:141 | 配置条目重试最大等待 |
| `_MAX_QUEUED_EVENT_DISPATCHES` | 10,000 | core.py:1439 | 事件嵌套触发上限 |
