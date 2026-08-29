---
type: Concept
title: hassfest 工具链
description: 掌握 hassfest 29 个验证插件架构、validate 与 generate 双模式、quality_scale 四级 54 条质量规则、dependencies AST 依赖检测、scaffold 脚手架、translations 翻译工具、codeowners 自动生成与 mypy.ini 自动生成
tags: [home-assistant, smart-home, hassfest, quality-scale, scaffold, codeowners, mypy, ci, validation, tooling]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: tooling-source
    resource: "/references/tooling-source.md"
    title: Home Assistant 工具链源码
  - id: facts-tooling
    resource: "/references/facts-tooling.md"
    title: Home Assistant 工具链与测试事实清单
  - id: components-source
    resource: "/references/components-source.md"
    title: Home Assistant Components 源码
---

# hassfest 工具链

hassfest 是 Home Assistant 的集成验证与代码生成工具，是保障 2000+ 集成一致性和质量的第一道防线。它通过 29 个验证插件检查 manifest 格式、依赖完整性、服务发现索引、翻译键、codeowners、config_flow 合规性等，同时自动生成 `homeassistant/generated/` 下的发现索引和 `mypy.ini` 配置。hassfest 在 pre-commit 和 CI 中强制运行，任何验证错误都会阻止代码合入。

## 架构总览

hassfest 主入口位于 `script/hassfest/__main__.py`，模块文档字符串为 `"Validate manifests."`（事实 #1）。它通过 argparse 提供 CLI 接口：

```bash
# 验证单个集成
python -m script.hassfest --integration-path homeassistant/components/tuya

# 验证所有集成并检查 requirements
python -m script.hassfest --requirements --action validate

# 生成所有自动生成文件
python -m script.hassfest --action generate

# 只运行特定插件
python -m script.hassfest -p manifest,dependencies
```

### CLI 参数

| 参数 | 说明 |
|------|------|
| `--action` | `validate`（验证模式）或 `generate`（生成模式），未指定时自动推断 |
| `--integration-path` | 可重复，指定单个集成目录验证路径 |
| `--requirements` | 布尔标志，验证 Python 依赖需求 |
| `-p/--plugins` | 逗号分隔的插件名列表，默认运行全部 |
| `--skip-plugins` | 逗号分隔的需跳过插件名 |
| `--core-path` | core 根路径，默认为当前目录 |

当指定 `--integration-path` 时，action 自动推断为 `validate`；否则推断为 `generate`（事实 #8）。`generate` 模式不允许与 `--integration-path` 同时使用（事实 #9）。未指定集成路径时必须存在 `requirements_all.txt` 文件，否则抛出 `RuntimeError("Run from Home Assistant root")`（事实 #10）。

### validate 与 generate 双模式

hassfest 有两种运行模式，行为有本质区别（事实 #21-22）：

- **validate 模式**：所有错误（`Error`）均导致失败，退出码 1。CI 中使用此模式，确保任何问题都不被放过。
- **generate 模式**：仅不可修复错误（`not err.fixable`）导致失败；可修复错误（如生成文件内容不匹配）会先修复再继续。验证通过后对每个有 `generate` 属性的插件调用 `plugin.generate(integrations, config)` 写入自动生成文件。开发时使用此模式。

每个插件执行时用 `monotonic` 计时并打印耗时（事实 #19）。插件抛出 RuntimeError 时 main 函数打印错误并返回退出码 1（事实 #20）。结果按 domain 字母序排列，打印 `[ERROR]`/`[WARNING]` 前缀（事实 #23）。

## 29 个验证插件

插件分为两类（事实 #11-13）：

### 集成级插件（INTEGRATION_PLUGINS，23 个）

这些插件对每个集成独立运行：

| 插件 | 职责 |
|------|------|
| `application_credentials` | OAuth2 应用凭证验证 |
| `bluetooth` | 蓝牙发现规则收集与生成 |
| `codeowners` | CODEOWNERS 文件自动生成与验证 |
| `conditions` | 条件验证 |
| `config_schema` | CONFIG_SCHEMA 合规性检查 |
| `config_flow` | config_flow.py 存在性与 unique_id 检查（必须最后运行） |
| `dependencies` | AST 依赖分析，检测未声明/重复/循环依赖 |
| `dhcp` | DHCP 发现规则收集与生成 |
| `icons` | 图标验证 |
| `integration_info` | 集成元数据验证 |
| `integration_type` | 集成类型一致性检查 |
| `json` | JSON 文件格式验证 |
| `labs` | 实验性功能标记 |
| `manifest` | manifest.json schema 验证 |
| `mqtt` | MQTT 发现规则验证 |
| `quality_scale` | 质量等级规则验证 |
| `requirements` | Python 依赖验证 |
| `services` | services.yaml 与服务注册一致性 |
| `ssdp` | SSDP 发现规则收集与生成 |
| `translations` | 翻译键格式与完整性验证 |
| `triggers` | 触发器验证 |
| `usb` | USB 发现规则收集与生成 |
| `zeroconf` | mDNS/HomeKit 发现规则收集与生成 |

`config_flow` 插件必须在 `INTEGRATION_PLUGINS` 列表中最后运行（事实 #12），因为它依赖 translations 插件处理完成后的结果。

### 全局插件（HASS_PLUGINS，6 个）

这些插件在全量运行时执行，检查跨集成或核心文件：

| 插件 | 职责 |
|------|------|
| `core_files` | 核心文件完整性验证 |
| `docker` | Dockerfile 验证 |
| `mdi_icons` | Material Design Icons 验证 |
| `mypy_config` | 从 `.strict-typing` 生成 `mypy.ini` |
| `metadata` | 集成元数据生成 |
| `sensor` | 传感器平台元数据 |

### 核心数据模型

`Config` 数据类（model.py:24-34）包含 `root`、`specific_integrations`、`action`、`requirements`、`core_integrations_path`、`errors`、`cache`、`plugins` 字段。`__post_init__` 将 `core_integrations_path` 设置为 `root / "homeassistant/components"`（事实 #25）。

`Integration` 数据类（model.py:107-143）是核心模型，表示一个集成。`load_dir()` 遍历目录，跳过文件和 `__pycache__`，要求至少存在 `__init__.py` 或 `manifest.json`（事实 #31）。它提供 `domain`、`name`、`quality_scale`、`config_flow`、`requirements`、`dependencies`、`integration_type` 等属性，从 manifest 中读取（事实 #33-42）。

`Error` 数据类包含 `plugin`、`error`、`fixable`（默认 False）三个字段（事实 #27），`__str__` 返回 `[PLUGIN] error message` 格式（事实 #28）。

## manifest 验证

manifest 验证模块（`script/hassfest/manifest.py`）使用 voluptuous 进行 schema 校验（事实 #45）。

### 核心 Schema

`INTEGRATION_MANIFEST_SCHEMA` 定义核心集成的 manifest 结构（事实 #57）。必需字段为 `domain`、`name`、`documentation`、`codeowners`。文档 URL 必须使用 HTTPS scheme，主机为 `www.home-assistant.io`，路径前缀为 `/integrations/`（事实 #46），唯一例外是 `https://www.home-assistant.io/hassio`（事实 #47）。

`integration_type` 默认为 `"hub"`，不允许 `virtual` 类型（虚拟集成使用独立 schema）（事实 #58）。发现字段的 schema 约束：
- `zeroconf`：字符串列表或对象列表，对象包含 `type`（必需）、`macaddress`、`manufacturer`、`model`、`name`、`properties`（事实 #59）
- `ssdp`：至少包含一个键的字典列表（`vol.Length(min=1)`）（事实 #60）
- `bluetooth`：支持 `connectable`、`service_uuid`、`local_name`、`manufacturer_id` 等（事实 #61）
- `dhcp`：`macaddress`（大写+通配符）、`hostname`（小写）、`registered_devices`（事实 #62）
- `usb`：`vid`/`pid`（大写）、`serial_number`/`manufacturer`/`description`（小写）、`known_devices`（事实 #63）

### iot_class 验证

`SUPPORTED_IOT_CLASSES` 包含 6 种类别（事实 #50）：`assumed_state`、`calculated`、`cloud_polling`、`cloud_push`、`local_polling`、`local_push`。

`NO_IOT_CLASS` 列表（事实 #51）列出不应有 iot_class 的集成，包括所有 Platform 值（light、sensor 等）和 auth/automation/frontend 等系统集成。这些集成如果声明了 iot_class 会报错；其他集成（虚拟集成除外）必须声明 iot_class（事实 #70）。

### 自定义与虚拟集成

`CUSTOM_INTEGRATION_MANIFEST_SCHEMA` 扩展核心 schema，添加必需的 `version` 字段和可选的 `issue_tracker`、`import_executor`（事实 #66）。`validate_version()` 检查自定义集成必须有 version 字段（事实 #67）。版本号通过 `verify_version()` 使用 AwesomeVersion 验证，支持 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 策略（事实 #55）。

`VIRTUAL_INTEGRATION_MANIFEST_SCHEMA` 要求 `integration_type` 为 `"virtual"`，使用 `vol.Exclusive` 确保 `iot_standards` 和 `supported_by` 互斥（事实 #65）。虚拟集成的 `supported_by` 必须指向存在的核心集成（事实 #71），且不生成 CODEOWNERS 条目。

### quality_scale 验证

`SUPPORTED_QUALITY_SCALES` 合并了评分等级和非评分等级（事实 #49）：
- 评分等级：`bronze`、`silver`、`gold`、`platinum`（`ScaledQualityScaleTiers` IntEnum，BRONZE=1 到 PLATINUM=4，事实 #44）
- 非评分等级：`custom`、`no_score`、`internal`、`legacy`（`NonScaledQualityScaleTiers`，事实 #48）

SILVER 及以上等级的集成必须有 codeowners（事实 #72）。

## quality_scale：四级质量标准

quality_scale 验证模块（`script/hassfest/quality_scale.py`）定义了阶梯式质量规则（事实 #73-82）。`Rule` 数据类包含 `name`、`tier`、可选的 `validator`（程序化验证器）。`ALL_RULES` 列表定义了所有 54 条规则。

### BRONZE（20 条规则）

基础入门要求（事实 #77）：

- `config-flow`：必须实现 ConfigFlow
- `unique-config-entry`：ConfigEntry 必须有 unique_id
- `entity-unique-id`：所有实体必须有 unique_id
- `config-flow-test-coverage`：ConfigFlow 必须有测试
- `test-before-configure`：配置前测试连接
- `test-before-setup`：setup 前测试
- `runtime-data`：使用 `entry.runtime_data` 而非 `hass.data`
- `dependency-transparency`：依赖透明
- `appropriate-polling`：合理的轮询策略
- `entity-event-setup`：实体事件设置
- `action-setup`：动作设置
- `brands`：品牌资产
- `common-modules`：不使用公共模块反模式
- `docs-actions`/`docs-conditions`/`docs-triggers`：文档完整性
- `docs-high-level-description`：高级描述
- `docs-installation-instructions`：安装说明
- `docs-removal-instructions`：移除说明
- `has-entity-name`：实体名称

### SILVER（10 条规则）

中级质量要求（事实 #78）：

- `config-entry-unloading`：支持配置条目卸载
- `reauthentication-flow`：重新认证流程
- `parallel-updates`：并行更新
- `entity-unavailable`：设备不可用处理
- `log-when-unavailable`：不可用时记录日志
- `integration-owner`：集成所有者
- `action-exceptions`：动作异常处理
- `docs-installation-parameters`/`docs-configuration-parameters`：参数文档
- `test-coverage`：测试覆盖率

### GOLD（21 条规则）

高级质量要求（事实 #79）：

- `devices`：设备注册
- `diagnostics`：诊断信息
- `discovery`/`discovery-update-info`：设备发现与更新
- `dynamic-devices`：动态设备
- `entity-device-class`：正确的设备类
- `entity-category`：实体分类
- `entity-disabled-by-default`：默认禁用实体
- `entity-translations`：实体翻译
- `exception-translations`：异常翻译
- `icon-translations`：图标翻译
- `reconfiguration-flow`：重新配置流程
- `repair-issues`：问题修复
- `stale-devices`：陈旧设备清理
- `docs-data-update`/`docs-examples`/`docs-known-limitations`/`docs-supported-devices`/`docs-supported-functions`/`docs-troubleshooting`/`docs-use-cases`：文档完整度

### PLATINUM（3 条规则）

最高质量标准（事实 #80）：

- `async-dependency`：异步依赖（不使用阻塞 I/O）
- `inject-websession`：注入 aiohttp session
- `strict-typing`：严格类型检查

### 程序化验证器

部分规则带有自动验证器（事实 #81），无需人工检查：
- `config-flow` → `config_flow.validate`
- `discovery` → `discovery.validate`
- `reconfiguration-flow` → `reconfiguration_flow.validate`
- `runtime-data` → `runtime_data.validate`
- `strict-typing` → `strict_typing.validate`
- `test-before-setup` → `test_before_setup.validate`
- `unique-config-entry` → `unique_config_entry.validate`

## dependencies：AST 依赖分析

dependencies 验证器是 hassfest 中最复杂的插件之一（事实 #122-127）。它使用 AST 解析（`ImportCollector` 类）静态收集集成间的 Python 导入关系。

`ImportCollector` 遍历每个 Python 文件的 AST，收集 `from homeassistant.components.xxx import` 和 `import homeassistant.components.xxx` 形式的导入，忽略 `TYPE_CHECKING` 块中的导入（事实 #123）。验证器使用 `multiprocessing.Pool` 并行解析数千个 Python 文件（事实 #125）。

检测三类问题（事实 #126）：
1. **未声明的依赖**：代码中导入了 `homeassistant.components.other`，但 manifest 的 `dependencies`/`after_dependencies` 中未声明
2. **重复依赖**：同一 domain 同时出现在 `dependencies` 和 `after_dependencies` 中
3. **循环依赖**：A 依赖 B，B 又（传递）依赖 A

`ALLOWED_USED_COMPONENTS` 包含无需声明的集成（事实 #124）：`CORE_INTEGRATIONS`（homeassistant、persistent_notification）、所有 Platform、以及 alert/automation/frontend 等内部集成。`CORE_INTEGRATIONS` 不能被其他集成声明为依赖（事实 #128）。少数已知白名单元组列在 `IGNORE_VIOLATIONS` 中（事实 #127）。

## 服务发现代码生成

zeroconf、dhcp、ssdp、usb、bluetooth 五个发现验证器遵循相同的代码生成模式（事实 #90-91）：

1. `generate_and_validate()` 生成目标文件的内容字符串
2. `validate()` 比较磁盘上的文件内容，不匹配则添加 `fixable=True` 错误
3. `generate()` 将内容写入文件

所有生成文件使用 `format_python_namespace()` 序列化器（来自 `script/hassfest/serializer.py`）。

| 验证器 | 生成文件 | 类型注解 |
|--------|----------|----------|
| zeroconf | `homeassistant/generated/zeroconf.py` | 按 domain 分组 |
| dhcp | `homeassistant/generated/dhcp.py` | `Final[list[dict[str, str \| bool]]]` |
| ssdp | `homeassistant/generated/ssdp.py` | `defaultdict(list)` 按 domain 分组 |
| usb | `homeassistant/generated/usb.py` | 排除 `known_devices` 字段 |
| bluetooth | `homeassistant/generated/bluetooth.py` | `Final[list[dict[str, bool \| str \| int \| list[int]]]]` |

zeroconf 验证器还检测 HomeKit 模型重叠冲突（事实 #84），并根据集成的 `iot_class` 通过 `homekit_always_discover()` 确定 `always_discover` 标志（事实 #85）。

## codeowners 自动生成

codeowners 验证器自动生成仓库根目录的 `CODEOWNERS` 文件（事实 #117-121）。生成的内容包括：
- 核心文件归属 `@home-assistant/core`
- Supervisor 相关文件归属 `@home-assistant/supervisor`
- 每个集成的目录归属其 manifest 中声明的 codeowners
- 如果集成有 `tests/components/<domain>/__init__.py`，同时生成测试目录归属

验证规则：
- 每个 codeowner 必须以 `@` 开头，否则报错（事实 #119）
- 虚拟集成不生成 CODEOWNERS 条目（事实 #118）
- 翻译目录被排除（`/homeassistant/components/*/translations/`）（事实 #121）

## config_flow 验证

config_flow 验证器执行两类检查（事实 #92-94）：

1. **文件存在性**：manifest 声明 `config_flow: true` 但 `config_flow.py` 文件不存在时报错
2. **unique_id 检查**：检测可发现配置流（含 `async_step_discovery`/`bluetooth`/`hassio`/`homekit`/`mqtt`/`ssdp`/`zeroconf`/`dhcp`/`usb` 方法）是否设置了 unique_id

`UNIQUE_ID_IGNORE` 集合包含 huawei_lte、mqtt、adguard、unifi_discovery 等豁免集成（事实 #94）。生成器将集成分为 `integration` 和 `helper` 两类（事实 #95）。

## scaffold 脚手架

`script/scaffold/` 提供新集成骨架生成工具（事实 #105-113）：

```bash
python -m script.scaffold integration
```

scaffold CLI 接受位置参数 `template`（从 `templates/` 子目录自动发现），支持 `--develop` 和 `--integration` 选项。必须从项目根目录运行（检查 `requirements_all.txt` 存在）。

`Info` 数据类（使用 `attr.s`）跟踪集成元数据：domain、name、is_new、codeowner、requirement、iot_class、authentication、discoverable、oauth2、integration_type（事实 #109），以及 `files_added`、`tests_added`、`examples_added` 三个集合（事实 #110）。

新建集成时，先生成 `integration` 模板，再根据条件自动选择 config_flow 模板（事实 #108）：
- helper 类型 → `config_flow_helper`
- oauth2 → `config_flow_oauth2`
- authentication 或不可发现 → `config_flow`
- 否则 → `config_flow_discovery`

`Info.integration_dir` 返回 `homeassistant/components/<domain>`，`tests_dir` 返回 `tests/components/<domain>`（事实 #111）。`update_manifest()` 合并 kwargs 后调用 `sort_manifest()` 排序并写入 JSON（事实 #112）。

## translations 翻译工具

翻译工具入口位于 `script/translations/__main__.py`（事实 #96），支持 7 种 action：clean、deduplicate、develop、download、frontend、migrate、upload（事实 #97）。Lokalise 令牌通过环境变量 `LOKALISE_TOKEN` 或 `.lokalise_token` 文件获取（事实 #98）。

hassfest translations 验证器定义三个状态常量（事实 #101）：`UNDEFINED=0`、`REQUIRED=1`、`REMOVED=2`。翻译键正则 `RE_TRANSLATION_KEY` 要求小写字母数字、连字符、下划线，不允许前后连字符/下划线或连续双连字符（事实 #102）。

核心集成翻译文件为 `strings.json`，自定义集成翻译文件为 `translations/en.json`（事实 #104）。`ALLOW_NAME_TRANSLATION` 白名单列出允许翻译集成名称的 domain（事实 #103）。

## mypy_config 自动生成

mypy_config 生成器从 `.strict-typing` 文件读取严格类型模块列表，自动生成 `mypy.ini`（事实 #133-135）。一般设置包括：
- Python 版本从 `REQUIRED_PYTHON_VER` 派生（当前 3.14）
- `strict_equality`、`strict_bytes`、`no_implicit_optional`
- pydantic 插件配置：`init_forbid_extra=true`、`init_typed=true`、`warn_required_dynamic_aliases=true`、`warn_untyped_fields=true`
- 启用错误代码：deprecated、explicit-override、ignore-without-code、redundant-self、truthy-iterable
- 禁用错误代码：annotation-unchecked、import-not-found、import-untyped

`.strict-typing` 文件列出启用 `disallow_any_generics` 的模块，包括 homeassistant.core、homeassistant.exceptions、homeassistant.auth.auth_store 及 helpers 下多个模块（事实 #249）。`NO_IMPLICIT_REEXPORT_MODULES` 为 components、application_credentials、diagnostics、spotify、stream、update 设置 `no_implicit_reexport`（事实 #135）。

## services 验证

services 验证器使用 voluptuous schema 验证 `services.yaml`（事实 #129），区分核心集成和自定义集成 schema。它通过 grep 检测代码中 `hass.services.register/async_register` 调用——注册了服务但无 services.yaml 时报错（事实 #130）。核心集成每个服务必须在 icons.json 中有对应图标（事实 #131），服务名称和描述必须在 strings.json 中有翻译条目（事实 #132）。

## sort_manifest：manifest 排序

`script/util.py` 的 `sort_manifest()` 函数对 manifest 字典排序（事实 #116），`domain` 和 `name` 键始终排在最前（通过 `_MANIFEST_SORT_KEYS` 映射为 `.domain`/`.name`）。scaffold 和 hassfest 在写入 manifest 时都调用此函数确保键顺序一致。

## 静态检查配置

HA 使用 ruff 进行代码风格检查（事实 #234-243）：
- 要求 ruff 版本 `>=0.15.18`
- 启用 30+ 规则集：A(buildin-shadowing)、ASYNC、B(bugbear)、C(complexity)、D(docstrings)、DTZ(timezone)、E/F(pycodestyle/pyflakes)、G(logging)、I(isort)、PL(pylint)、PT(pytest)、S(security)、TRY(tryceratops)、UP(pyupgrade) 等
- 特殊约定：`voluptuous` 必须导入为 `vol`；各组件 PLATFORM_SCHEMA 有标准别名
- 禁止使用 `async_timeout`（用 `asyncio.timeout`）、`pytz`（用 `zoneinfo`）、`__future__.annotations`
- isort 配置：`force-sort-within-sections = true`、`known-first-party = ["homeassistant"]`、`combine-as-imports = true`
- mccabe 最大复杂度为 25，pydocstyle 使用 google 约定

pre-commit 配置（事实 #251-254）使用 ruff-pre-commit v0.15.18（ruff-check --fix 和 ruff-format）、codespell v2.4.2（拼写检查）、zizmor v1.24.1（GitHub Actions 安全）、yamllint v1.38.0、prettier v3.6.2。hassfest pre-commit hook 监听 `manifest.json`、`strings.json`、`services.yaml`、`quality_scale.yaml`、`brands/*.json` 等文件变更。

## 开发工作流

集成开发者应遵循以下工作流：

1. **使用 scaffold 创建骨架**：`python -m script.scaffold integration`，根据提示输入 domain、name、iot_class 等信息
2. **实现 manifest.json**：填写所有必需字段，声明 dependencies、requirements、发现规则
3. **实现 ConfigFlow 和平台实体**：参考[配置流](/concepts/15-config-flow.md)和[平台开发模式](/concepts/16-platform-pattern.md)
4. **运行单集成 hassfest**：`python -m script.hassfest --integration-path homeassistant/components/<domain>`，快速验证
5. **运行 generate 模式**：`python -m script.hassfest --action generate`，自动修复生成文件
6. **编写测试**：参考[测试模式](/concepts/18-testing-patterns.md)
7. **运行 ruff 和 mypy**：`ruff check homeassistant/components/<domain>` 和 `mypy homeassistant/components/<domain>`
8. **提交前全量验证**：`python -m script.hassfest --requirements --action validate`

## 延伸阅读

- [集成架构](/concepts/14-component-architecture.md)
- [配置流](/concepts/15-config-flow.md)
- [平台开发模式](/concepts/16-platform-pattern.md)
- [测试模式](/concepts/18-testing-patterns.md)
- [Util 工具集](/concepts/13-utilities.md)

## 相关概念

- [集成架构](/concepts/14-component-architecture.md) — hassfest 验证集成的 manifest.json、目录结构和生命周期函数规范
- [平台开发模式](/concepts/16-platform-pattern.md) — hassfest 检查平台实体的 supported_features、翻译键和代码规范
- [测试模式](/concepts/18-testing-patterns.md) — hassfest 验证测试文件存在性和质量，与 pytest 测试框架配合保障集成质量
