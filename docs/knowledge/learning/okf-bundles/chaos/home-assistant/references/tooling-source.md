---
type: Reference
title: Home Assistant 工具链与测试源码
description: Home Assistant 开发工具链源码登记，包含 hassfest 验证器、scaffold 脚手架、翻译工具、pytest 测试基础设施与 CI 配置
tags: [home-assistant, smart-home, tooling, testing, hassfest, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-tooling
    resource: "/references/facts-tooling.md"
    title: Home Assistant 工具链与测试模式事实清单
---

# Home Assistant 工具链与测试源码

## 概述

Home Assistant 的工具链位于 `script/` 目录，测试位于 `tests/` 目录。工具链保障 2000+ 集成的代码质量和一致性，测试基础设施提供严格的异步测试环境和丰富的测试替身。

| 目录 | 路径 | 职责 |
|------|------|------|
| hassfest | `script/hassfest/` | 集成验证与代码生成（29 个插件） |
| scaffold | `script/scaffold/` | 新集成脚手架生成 |
| translations | `script/translations/` | 翻译管理（Lokalise） |
| check_requirements | `script/check_requirements/` | 依赖检查 |
| tests | `tests/` | pytest 测试套件 |

## script/hassfest/ 验证框架

路径：`script/hassfest/`

### 入口与模型

| 文件 | 职责 |
|------|------|
| `__main__.py` | CLI 入口，argparse 参数解析，插件调度 |
| `model.py` | 核心数据模型：`Config`、`Integration`、`Brand`、`Error`、`IntegrationType` |
| `manifest.py` | manifest.json schema 验证（voluptuous） |
| `serializer.py` | Python 命名空间文件序列化器 |
| `quality_scale.py` | quality_scale 规则定义与验证 |

### CLI 参数

| 参数 | 说明 |
|------|------|
| `--action {validate,generate}` | 验证或生成模式，默认自动推断 |
| `--integration-path PATH` | 验证单个集成（可重复） |
| `--requirements` | 验证依赖需求 |
| `-p/--plugins LIST` | 逗号分隔的插件列表 |
| `--skip-plugins LIST` | 跳过的插件列表 |
| `--core-path PATH` | core 根路径，默认当前目录 |

### 验证插件（29 个）

#### 集成级插件（INTEGRATION_PLUGINS，23 个）

| 插件文件 | 验证内容 |
|---------|---------|
| `application_credentials.py` | OAuth 凭证配置 |
| `bluetooth.py` | 蓝牙发现规则，生成 `generated/bluetooth.py` |
| `codeowners.py` | CODEOWNERS 文件自动生成与验证 |
| `conditions.py` | 条件平台定义 |
| `config_schema.py` | 配置 schema |
| `config_flow.py` | ConfigFlow 文件存在性与 unique_id 检查（必须最后运行） |
| `dependencies.py` | AST 解析依赖关系，检测未声明/重复/循环依赖 |
| `dhcp.py` | DHCP 发现规则，生成 `generated/dhcp.py` |
| `icons.py` | 图标引用验证 |
| `integration_info.py` | 集成信息完整性 |
| `integration_type.py` | integration_type 合规性 |
| `json.py` | JSON 格式验证 |
| `labs.py` | 实验室功能 |
| `manifest.py` | manifest.json schema 验证 |
| `mqtt.py` | MQTT 发现规则，生成 `generated/mqtt.py` |
| `quality_scale.py` | 质量等级规则验证 |
| `requirements.py` | Python 依赖验证 |
| `services.py` | services.yaml 与服务注册一致性 |
| `ssdp.py` | SSDP 发现规则，生成 `generated/ssdp.py` |
| `translations.py` | 翻译键格式与完整性 |
| `triggers.py` | 触发器平台定义 |
| `usb.py` | USB 发现规则，生成 `generated/usb.py` |
| `zeroconf.py` | zeroconf 发现规则，生成 `generated/zeroconf.py` |

#### 全局插件（HASS_PLUGINS，6 个）

| 插件文件 | 验证内容 |
|---------|---------|
| `core_files.py` | 核心文件完整性 |
| `docker.py` | Dockerfile 验证 |
| `mdi_icons.py` | Material Design Icons 引用 |
| `mypy_config.py` | 从 `.strict-typing` 生成 `mypy.ini` |
| `metadata.py` | 元数据验证 |
| `sensor.py` | 传感器平台验证 |

### quality_scale 质量等级

| 等级 | 规则数 | 核心要求 |
|------|--------|---------|
| BRONZE | 20 | config-flow, unique-config-entry, entity-unique-id, test-before-setup, docs 等基础要求 |
| SILVER | 10 | config-entry-unloading, parallel-updates, reauthentication-flow, test-coverage, entity-unavailable 等 |
| GOLD | 21 | devices, diagnostics, discovery, entity-translations, reconfiguration-flow, repair-issues, stale-devices 等 |
| PLATINUM | 3 | async-dependency, inject-websession, strict-typing |

带程序化验证器的规则：config-flow、discovery、reconfiguration-flow、runtime-data、strict-typing、test-before-setup、unique-config-entry。

### manifest 验证关键规则

| 规则 | 说明 |
|------|------|
| 文档 URL | 必须 HTTPS，主机 `www.home-assistant.io`，路径 `/integrations/` 前缀 |
| codeowners | SILVER 及以上必需，必须以 `@` 开头 |
| iot_class | 非平台/系统集成必需，6 种合法值 |
| version | 自定义集成必需，符合 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 |
| 虚拟集成 | 使用独立 schema，`supported_by` 必须指向存在的核心集成 |
| zeroconf | 支持字符串列表或对象列表（type/macaddress/manufacturer 等） |

## script/scaffold/ 脚手架

路径：`script/scaffold/`

| 文件 | 职责 |
|------|------|
| `__main__.py` | CLI 入口，模板发现与生成 |
| `model.py` | `Info` 数据类（domain/name/codeowner/iot_class 等） |
| `const.py` | 路径常量：`COMPONENT_DIR`、`TESTS_DIR` |
| `gather_info.py` | 交互式信息收集 |
| `generate.py` | 模板渲染与文件写入 |
| `error.py` | 错误定义 |
| `docs.py` | 文档生成 |

### 模板列表（templates/）

| 模板 | 说明 |
|------|------|
| `integration/` | 基础集成模板 |
| `config_flow/` | ConfigFlow 基础模板 |
| `config_flow_discovery/` | 可发现设备的 ConfigFlow |
| `config_flow_helper/` | Helper 类型 ConfigFlow |
| `config_flow_oauth2/` | OAuth2 ConfigFlow |
| `device_action/` | 设备动作 |
| `device_condition/` | 设备条件 |
| `device_trigger/` | 设备触发器 |
| `backup/` | 备份集成 |
| `reproduce_state/` | 状态重现 |
| `significant_change/` | 显著变更 |

### ConfigFlow 模板自动选择逻辑

1. helper 类型 → `config_flow_helper`
2. OAuth2 认证 → `config_flow_oauth2`
3. authentication 或不可发现 → `config_flow`
4. 其他可发现 → `config_flow_discovery`

## script/translations/ 翻译工具

路径：`script/translations/`

| 文件 | 职责 |
|------|------|
| `__main__.py` | 入口，动态加载 action 模块 |
| `util.py` | Lokalise 令牌获取、通用工具 |
| `const.py` | 项目 ID、Docker 镜像版本 |
| `download.py` | 从 Lokalise 下载翻译 |
| `upload.py` | 上传翻译到 Lokalise |
| `clean.py` | 清理未使用翻译 |
| `deduplicate.py` | 去重翻译键 |
| `develop.py` | 开发模式翻译 |
| `frontend.py` | 前端翻译 |
| `migrate.py` | 翻译迁移 |
| `lokalise.py` | Lokalise API 封装 |

支持的 action：clean, deduplicate, develop, download, frontend, migrate, upload。

Lokalise 令牌从环境变量 `LOKALISE_TOKEN` 或 `.lokalise_token` 文件获取。

## script/ 其他工具

| 文件 | 职责 |
|------|------|
| `gen_requirements_all.py` | 生成 requirements_all.txt |
| `check_requirements/` | 依赖检查子包（diff/gate/pypi/render/runner） |
| `inspect_schemas.py` | Schema 检查 |
| `install_integration_requirements.py` | 安装集成依赖 |
| `split_tests.py` | 测试分组拆分 |
| `version_bump.py` | 版本号升级 |
| `quality_scale_summary.py` | 质量等级汇总 |
| `languages.py` | 语言代码列表 |
| `countries.py` | 国家代码列表 |
| `currencies.py` | 货币代码列表 |
| `licenses.py` | 许可证检查 |
| `alexa_locales.py` | Alexa 区域设置 |
| `amazon_polly.py` | Amazon Polly TTS |
| `microsoft_tts.py` | Microsoft TTS |
| `gen_copilot_instructions.py` | Copilot 指令生成 |
| `const.py` | `COMPONENT_DIR = Path("homeassistant/components")` |
| `util.py` | `valid_integration()`、`sort_manifest()` |

## tests/ 测试基础设施

路径：`tests/`

### 核心测试文件

| 文件 | 职责 |
|------|------|
| `conftest.py` | pytest 全局 fixtures 与配置（socket 禁网、事件循环策略、verify_cleanup 等） |
| `common.py` | 测试工具函数与替身（`async_test_home_assistant`、`MockConfigEntry`、`MockEntity` 等） |
| `syrupy.py` | 快照测试扩展（`HomeAssistantSnapshotExtension`） |
| `patch_json.py` | JSON 序列化 monkey-patch |
| `patch_time.py` | 时间 monkey-patch（HAFakeDate/HAFakeDatetime） |
| `patch_recorder.py` | Recorder monkey-patch |
| `ignore_uncaught_exceptions.py` | 未捕获异常处理 |
| `typing.py` | 测试类型定义 |

### 测试目录结构

| 目录 | 说明 |
|------|------|
| `tests/components/<domain>/` | 各集成测试（2000+ 目录） |
| `tests/auth/` | 认证系统测试 |
| `tests/helpers/` | Helpers 单元测试 |
| `tests/util/` | Util 单元测试 |
| `tests/hassfest/` | hassfest 自测试 |
| `tests/pylint/` | Pylint 插件测试 |
| `tests/script/` | Script 工具测试 |
| `tests/scripts/` | scripts 目录测试 |
| `tests/fixtures/` | 测试固件文件 |
| `tests/testing_config/` | 测试配置目录 |
| `tests/snapshots/` | 快照文件（bootstrap/config/config_entries） |
| `tests/helpers/snapshots/` | Helpers 快照 |
| `tests/helpers/template/extensions/snapshots/` | 模板扩展快照 |

### pytest 配置（pyproject.toml）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `asyncio_mode` | `"auto"` | 自动异步模式，无需 `@pytest.mark.asyncio` |
| `asyncio_default_fixture_loop_scope` | `"function"` | 事件循环 fixture 作用域 |
| `asyncio_debug` | `true` | 启用 asyncio 调试 |
| `testpaths` | `["tests"]` | 测试目录 |
| `pythonpath` | `["pylint/plugins"]` | Python 路径 |
| `filterwarnings` | SQLAlchemy SAWarning → error | 警告升级 |

### 关键 conftest.py fixtures

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `hass` | function | 创建测试用 `HomeAssistant` 实例，预加载翻译 |
| `hass_client` | function | 已认证的 HTTP 客户端（Bearer token） |
| `hass_client_no_auth` | function | 未认证 HTTP 客户端 |
| `hass_storage` | function | 包装 `mock_storage()` |
| `load_registries` | function | 控制是否加载注册表 |
| `caplog` | function | 覆盖，日志级别 DEBUG |
| `garbage_collection` | module | autouse，模块前后 GC |
| `expected_lingering_tasks` | function | autouse，残留任务检查 |
| `expected_lingering_timers` | function | autouse，残留定时器检查 |
| `enable_event_loop_debug` | function | autouse async，事件循环调试 |
| `verify_cleanup` | function | autouse，测试后资源清理检查 |
| `reset_globals` | function | autouse，重置全局变量 |
| `bcrypt_cost` | session | autouse，bcrypt rounds 降为 4 加速 |
| `enable_custom_integrations` | function | 启用测试目录自定义集成 |
| `snapshot` | function | syrupy 快照 fixture |
| `aiohttp_client_cls` | function | `CoalescingClient` 类 |
| `enable_statistics` | function | 默认 False，可 parametrize 启用 |
| `disable_block_async_io` | function | 禁用 block_async_io 保护 |

### 测试环境隔离

| 隔离项 | 实现 |
|--------|------|
| 网络 | pytest_socket 仅允许 127.0.0.1，禁用其他 socket |
| DNS | 仅允许 localhost/127.0.0.1/::1/0.0.0.0 |
| 事件循环 | `HassEventLoopPolicy(False)`，禁止覆盖 |
| 时区 | 测试后验证恢复为 UTC |
| 残留任务 | `verify_cleanup` 检测未取消任务 |
| 残留定时器 | `verify_cleanup` 检测未停止定时器 |
| 残留线程 | `verify_cleanup` 检测未关闭线程 |
| Mock 清理 | respx.mock.routes 必须为空 |
| 全局变量 | `reset_globals` 重置 `_Hass` 和 frame helper |

### tests/common.py 关键工具

| 名称 | 类型 | 说明 |
|------|------|------|
| `INSTANCES` | 列表 | 跟踪所有测试 HA 实例 |
| `async_test_home_assistant` | 协程 | 创建测试 HA 实例 |
| `MockConfigEntry` | 类 | 配置条目测试替身（domain="test"） |
| `MockEntity` | 类 | 实体测试基类 |
| `MockUser`/`MockGroup` | 类 | Auth 模型测试替身 |
| `MockModule`/`MockPlatform` | 类 | 集成模块/平台模拟 |
| `async_mock_service` | 协程 | 注册模拟服务，返回调用记录 |
| `async_fire_time_changed` | 协程 | 触发时间变更事件 |
| `load_fixture`/`load_fixture_bytes` | 函数 | 读取 fixture 文件 |
| `load_json_value_fixture` 等 | 函数 | 加载类型化 JSON fixture |
| `mock_component` | 函数 | 标记集成为已加载 |
| `mock_registry`/`mock_area_registry`/`mock_device_registry` | 函数 | 创建模拟注册表 |
| `mock_storage` | 上下文管理器 | 模拟存储层 |
| `mock_restore_cache` | 函数 | 模拟状态恢复缓存 |
| `patch_yaml_files` | 上下文管理器 | 临时替换 YAML 文件 |
| `assert_setup_component` | 上下文管理器 | 验证组件设置次数 |
| `get_fixture_path` | 函数 | 获取 fixture 路径 |
| `threadsafe_callback_factory` | 函数 | 线程安全回调工厂 |
| `StoreWithoutWriteLoad` | 类 | 不写入不加载的 Store 替身 |
| `flush_store` | 协程 | 刷新 Store 数据 |

### 快照测试（tests/syrupy.py）

| 组件 | 说明 |
|------|------|
| `HomeAssistantSnapshotExtension` | syrupy 扩展，快照目录改为 `snapshots/` |
| `HomeAssistantSnapshotSerializer` | 自定义序列化器，处理 HA 特殊类型 |
| 序列化器替换规则 | State: context/时间戳→ANY；ConfigEntry: entry_id→ANY；DeviceEntry: config_entries/id/via_device→ANY；EntityRegistryEntry: config_entry_id/device_id/id→ANY；AreaEntry: id→ANY；FlowResult: flow_id→ANY；IssueEntry: created→ANY |
| `_IntFlagWrapper` | 规范化 IntFlag repr，消除 Python 版本差异 |
| `VERSION = "1"` | 序列化格式版本 |
| `override_syrupy_finish` | 覆盖 finish 方法支持 pytest-xdist 并行合并 |

## 静态检查配置

### ruff（pyproject.toml `[tool.ruff]`）

| 配置 | 值 |
|------|-----|
| 最低版本 | `>=0.15.18` |
| 目标 Python | 3.14 |
| 启用规则集 | A001, ASYNC, B, BLE, C, D, DTZ, E/F, FLY, FURB, G, I, LOG, PGH, PIE, PL, PT, PTH, RET, RSE, RUF, S, SIM, SLF, SLOT, T, TC, TID, TRY, UP, W（30+ 规则集） |
| mccabe 最大复杂度 | 25 |
| docstring 风格 | google |
| import 约定 | `voluptuous` 必须导入为 `vol` |
| banned-api | 禁止 `async_timeout`、`pytz`、`tests` 包导入、`__future__.annotations` |
| isort | `known-first-party = ["homeassistant"]`，`combine-as-imports = true` |
| per-file-ignores | `script/*` 和 `homeassistant/scripts/*` 允许 print |

### mypy（mypy.ini，由 hassfest 自动生成）

| 配置 | 值 |
|------|-----|
| Python 版本 | 3.14 |
| 平台 | linux |
| 插件 | pydantic |
| 启用 | show_error_codes, strict_equality, strict_bytes, no_implicit_optional, warn_unused_ignores |
| 错误代码 | deprecated, explicit-override, ignore-without-code, redundant-self, truthy-iterable |
| `.strict-typing` | 列出启用 `disallow_any_generics` 的模块（core/exceptions/auth_store/helpers 多个模块） |

### pre-commit（.pre-commit-config.yaml）

| Hook | 工具 | 说明 |
|------|------|------|
| ruff-check | ruff-pre-commit v0.15.18 | `ruff-check --fix` |
| ruff-format | ruff-pre-commit v0.15.18 | 代码格式化 |
| codespell | v2.4.2 | 拼写检查 |
| zizmor | v1.24.1 | GitHub Actions 安全 |
| yamllint | v1.38.0 | YAML 格式 |
| prettier | v3.6.2 | 通用格式化 |
| mypy | local | 类型检查 |
| pylint | local | 代码分析 |
| gen_requirements_all | local | 依赖生成 |
| hassfest | local | 集成验证 |
| hassfest-metadata | local | 元数据验证 |
| hassfest-mypy-config | local | mypy 配置生成 |

## CI 工作流（.github/workflows/ci.yaml）

| 配置 | 说明 |
|------|------|
| 触发分支 | dev, rc, master, 所有 PR, 手动 workflow_dispatch |
| 运行器 | ubuntu-24.04 |
| 测试分组 | 10 个并行组 |
| MariaDB 矩阵 | 6 个版本（10.3.32 ~ 8.0.32） |
| PostgreSQL 矩阵 | 2 个版本（12.14, 15.2） |
| 全量测试触发 | dev/master/rc 分支、核心文件变更、full 输入、ci-full-run 标签 |
| 增量测试 | 仅集成变更时只运行相关测试，不运行数据库矩阵 |
| 环境变量 | HA_SHORT_VERSION, PYTHONASYNCIODEBUG=1, HASS_CI=1 |
| 并发控制 | 按 PR/ref 分组，取消旧运行 |
| 缓存 | venv 和 uv wheel 缓存 |

### CI Jobs

| Job | 职责 |
|-----|------|
| `info` | 变更检测，生成集成路径过滤器 |
| `prek` | pre-commit 检查（跳过部分 hooks） |
| `zizmor` | GitHub Actions 安全审计 |
| `lint-hadolint` | Dockerfile 检查 |
| `base` | Python 环境准备、依赖安装 |
| `hassfest` | 运行 hassfest validate |
| `gen-requirements-all` | 依赖生成验证 |
| `test` | 10 组并行测试 + 数据库矩阵 |

## 测试依赖版本（requirements_test.txt）

| 包 | 版本 |
|----|------|
| pytest | 9.0.3 |
| pytest-asyncio | 1.4.0 |
| pytest-aiohttp | 1.1.1 |
| pytest-xdist | 3.8.0 |
| pytest-cov | 7.1.0 |
| syrupy | 5.3.2 |
| mypy | 2.1.0 |
| pylint | 4.0.6 |
| freezegun | 1.5.5 |
| respx | 0.23.1 |
| pytest-socket | 0.8.0 |
