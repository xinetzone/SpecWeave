---
type: Facts
title: "Home Assistant 工具链与测试模式事实清单"
---

# Home Assistant 工具链与测试模式事实清单

> R 阶段事实采集。源码根目录：`d:\AI\.chaos\libs\home-assistant\core\`
> 每条事实标注 `文件路径:行号`。零推测。

## 1. hassfest 架构总览

1. hassfest 主入口位于 `script/hassfest/__main__.py`，模块文档字符串为 `"Validate manifests."`。`script/hassfest/__main__.py:1`
2. hassfest 通过 argparse 支持 `--action` 参数，取值为 `validate` 或 `generate`，默认为 None（自动推断）。`script/hassfest/__main__.py:105-107`
3. `--integration-path` 参数可重复指定（`action="append"`），用于验证单个集成目录。`script/hassfest/__main__.py:109-113`
4. `--requirements` 参数为布尔标志，用于验证依赖需求。`script/hassfest/__main__.py:115-118`
5. `-p/--plugins` 参数接受逗号分隔的插件名列表，默认运行全部插件。`script/hassfest/__main__.py:120-125`
6. `--skip-plugins` 参数接受逗号分隔的需跳过插件名列表。`script/hassfest/__main__.py:127-134`
7. `--core-path` 参数指定 core 根路径，默认为当前目录 `Path()`。`script/hassfest/__main__.py:136-140`
8. 当未指定 `--action` 且指定了 `--integration-path` 时，action 自动推断为 `validate`；否则推断为 `generate`。`script/hassfest/__main__.py:143-144`
9. `generate` 模式不允许与 `--integration-path` 同时使用，否则抛出 RuntimeError。`script/hassfest/__main__.py:146-149`
10. 未指定 `--integration-path` 时，必须存在 `requirements_all.txt` 文件，否则抛出 RuntimeError("Run from Home Assistant root")。`script/hassfest/__main__.py:151-155`
11. `INTEGRATION_PLUGINS` 列表包含 23 个按集成维度运行的验证插件：application_credentials, bluetooth, codeowners, conditions, config_schema, dependencies, dhcp, icons, integration_info, integration_type, json, labs, manifest, mqtt, quality_scale, requirements, services, ssdp, translations, triggers, usb, zeroconf, config_flow。`script/hassfest/__main__.py:42-66`
12. `config_flow` 插件必须在 `INTEGRATION_PLUGINS` 列表中最后运行，因为它需要在 translations 处理完成后执行。`script/hassfest/__main__.py:65`
13. `HASS_PLUGINS` 列表包含 6 个全局维度插件：core_files, docker, mdi_icons, mypy_config, metadata, sensor。`script/hassfest/__main__.py:67-74`
14. `ALL_PLUGIN_NAMES` 通过从模块名提取最后一段（`rsplit(".", maxsplit=1)[-1]`）生成所有插件名列表。`script/hassfest/__main__.py:76-79`
15. `valid_integration_path()` 函数验证路径是否为目录，否则抛出 argparse.ArgumentTypeError。`script/hassfest/__main__.py:82-88`
16. `validate_plugins()` 函数将逗号分隔字符串拆分为列表，并验证每个插件名是否在 `ALL_PLUGIN_NAMES` 中。`script/hassfest/__main__.py:91-99`
17. `get_config()` 返回 `Config` 数据类实例，包含 root、specific_integrations、action、requirements、plugins 字段。`script/hassfest/__main__.py:160-166`
18. `main()` 函数中，指定单集成时仅运行 `INTEGRATION_PLUGINS`；全量运行时追加 `HASS_PLUGINS`。`script/hassfest/__main__.py:177-189`
19. 每个插件通过调用 `plugin.validate(integrations, config)` 执行验证，并打印耗时（monotonic 计时）。`script/hassfest/__main__.py:191-205`
20. 插件抛出 RuntimeError 时，main 函数打印错误并返回退出码 1。`script/hassfest/__main__.py:206-211`
21. `generate` 模式下，仅不可修复错误（`not err.fixable`）导致失败；`validate` 模式下所有错误均导致失败。`script/hassfest/__main__.py:215-225`
22. `generate` 模式下，验证通过后对每个有 `generate` 属性的插件调用 `plugin.generate(integrations, config)`。`script/hassfest/__main__.py:237-243`
23. `print_integrations_status()` 按 domain 字母序排列集成，打印 [ERROR]/[WARNING] 前缀。`script/hassfest/__main__.py:263-278`
24. `Config` 数据类包含 `specific_integrations`、`root`、`action`、`requirements`、`core_integrations_path`、`errors`、`cache`、`plugins` 字段。`script/hassfest/model.py:24-34`
25. `Config.__post_init__()` 将 `core_integrations_path` 设置为 `root / "homeassistant/components"`。`script/hassfest/model.py:36-38`
26. `Config.add_error()` 创建 `Error` 实例并追加到 `errors` 列表。`script/hassfest/model.py:40-42`
27. `Error` 数据类包含 `plugin`、`error`、`fixable`（默认 False）三个字段。`script/hassfest/model.py:10-16`
28. `Error.__str__()` 返回格式 `[PLUGIN] error message`。`script/hassfest/model.py:18-20`
29. `Brand` 数据类表示品牌验证对象，具有 `load_dir()` 类方法批量加载品牌 JSON 文件。`script/hassfest/model.py:46-59`
30. `Integration` 数据类是核心模型，表示一个集成，包含 `path`、`_config`、`_manifest`、`manifest_path`、`errors`、`warnings`、`translated_name` 字段。`script/hassfest/model.py:107-143`
31. `Integration.load_dir()` 遍历目录，跳过文件和 `__pycache__`，要求至少存在 `__init__.py` 或 `manifest.json`。`script/hassfest/model.py:112-134`
32. `Integration.manifest` 属性是受保护访问，未加载时断言失败。`script/hassfest/model.py:144-148`
33. `Integration.domain` 属性返回目录名（`self.path.name`）。`script/hassfest/model.py:150-153`
34. `Integration.core` 属性判断集成路径是否以 `core_integrations_path` 开头。`script/hassfest/model.py:155-162`
35. `Integration.disabled` 返回 manifest 中的 `disabled` 字段。`script/hassfest/model.py:164-167`
36. `Integration.name` 返回 manifest 中的 `name` 字段（必需）。`script/hassfest/model.py:169-173`
37. `Integration.quality_scale` 返回 manifest 中的 `quality_scale` 字段。`script/hassfest/model.py:175-178`
38. `Integration.config_flow` 返回 manifest 中的 `config_flow` 字段，默认 False。`script/hassfest/model.py:180-183`
39. `Integration.requirements` 返回 manifest 中的 `requirements` 列表，默认空。`script/hassfest/model.py:185-188`
40. `Integration.dependencies` 返回 manifest 中的 `dependencies` 列表，默认空。`script/hassfest/model.py:190-193`
41. `Integration.integration_type` 属性解析 manifest 中的 `integration_type`（默认 `"hub"`），无效值回退为 `IntegrationType.HUB`。`script/hassfest/model.py:200-209`
42. `Integration.load_manifest()` 读取 `manifest.json`，解析 JSON 失败时添加 model 错误。`script/hassfest/model.py:238-252`
43. `IntegrationType` 是 StrEnum，支持 8 种类型：device, entity, hardware, helper, hub, service, system, virtual。`script/hassfest/model.py:255-265`
44. `ScaledQualityScaleTiers` 是 IntEnum，BRONZE=1, SILVER=2, GOLD=3, PLATINUM=4。`script/hassfest/model.py:268-274`

## 2. manifest 验证

45. manifest 验证模块位于 `script/hassfest/manifest.py`，使用 voluptuous 进行 schema 校验。`script/hassfest/manifest.py:1-21`
46. 文档 URL 必须使用 HTTPS scheme，主机为 `www.home-assistant.io`，路径前缀为 `/integrations/`。`script/hassfest/manifest.py:24-27`
47. `DOCUMENTATION_URL_EXCEPTIONS` 包含 `https://www.home-assistant.io/hassio` 作为例外。`script/hassfest/manifest.py:27`
48. `NonScaledQualityScaleTiers` 枚举包含 CUSTOM、NO_SCORE、INTERNAL、LEGACY 四个非评分等级。`script/hassfest/manifest.py:32-38`
49. `SUPPORTED_QUALITY_SCALES` 合并了 `ScaledQualityScaleTiers`（bronze/silver/gold/platinum）和 `NonScaledQualityScaleTiers`（custom/no_score/internal/legacy）。`script/hassfest/manifest.py:41-45`
50. `SUPPORTED_IOT_CLASSES` 包含 6 种 IoT 类别：assumed_state, calculated, cloud_polling, cloud_push, local_polling, local_push。`script/hassfest/manifest.py:46-53`
51. `NO_IOT_CLASS` 列表列出不应有 iot_class 的集成（包括所有 Platform 值和 auth/automation/frontend 等系统集成）。`script/hassfest/manifest.py:56-134`
52. `core_documentation_url()` 验证核心集成文档 URL 必须以 `https://www.home-assistant.io/integrations` 开头。`script/hassfest/manifest.py:137-146`
53. `custom_documentation_url()` 验证自定义集成文档 URL 使用 HTTPS 且不指向核心文档。`script/hassfest/manifest.py:149-159`
54. `verify_lowercase()` 验证字符串全小写；`verify_uppercase()` 验证全大写。`script/hassfest/manifest.py:162-175`
55. `verify_version()` 使用 AwesomeVersion 验证版本号，支持 CALVER/SEMVER/SIMPLEVER/BUILDVER/PEP440 策略。`script/hassfest/manifest.py:178-193`
56. `verify_wildcard()` 验证匹配器包含通配符 `*`。`script/hassfest/manifest.py:196-200`
57. `INTEGRATION_MANIFEST_SCHEMA` 定义核心集成 manifest schema，必需字段为 `domain`、`name`、`documentation`、`codeowners`。`script/hassfest/manifest.py:203-299`
58. `integration_type` 可选字段默认值为 `"hub"`，不允许 `virtual` 类型（虚拟集成使用独立 schema）。`script/hassfest/manifest.py:207-209`
59. `zeroconf` 字段支持字符串列表或对象列表，对象包含 `type`（必需）、`macaddress`、`manufacturer`、`model`、`name`、`properties`。`script/hassfest/manifest.py:212-237`
60. `ssdp` 字段要求至少包含一个键的字典列表（`vol.Length(min=1)`）。`script/hassfest/manifest.py:238-240`
61. `bluetooth` 字段支持 `connectable`、`service_uuid`、`service_data_uuid`、`local_name`、`manufacturer_id`、`manufacturer_data_start`。`script/hassfest/manifest.py:241-252`
62. `dhcp` 字段支持 `macaddress`（大写+通配符）、`hostname`（小写）、`registered_devices`（布尔）。`script/hassfest/manifest.py:254-264`
63. `usb` 字段支持 `vid`/`pid`（大写）、`serial_number`/`manufacturer`/`description`（小写）、`known_devices`。`script/hassfest/manifest.py:265-276`
64. `quality_scale` 字段值必须在 `SUPPORTED_QUALITY_SCALES` 中。`script/hassfest/manifest.py:278`
65. `VIRTUAL_INTEGRATION_MANIFEST_SCHEMA` 要求 `integration_type` 为 `virtual`，使用 `vol.Exclusive` 确保 `iot_standards` 和 `supported_by` 互斥。`script/hassfest/manifest.py:301-311`
66. `CUSTOM_INTEGRATION_MANIFEST_SCHEMA` 扩展核心 schema，添加必需的 `version` 字段和可选的 `issue_tracker`、`import_executor`。`script/hassfest/manifest.py:321-328`
67. `validate_version()` 检查自定义集成必须有 `version` 字段。`script/hassfest/manifest.py:331-338`
68. `validate_manifest()` 根据 core 属性选择核心或自定义 schema 验证，检查 domain 与目录名一致性。`script/hassfest/manifest.py:341-354`
69. 自定义集成 domain 与核心集成冲突时产生警告（非错误）。`script/hassfest/manifest.py:356-359`
70. `NO_IOT_CLASS` 中的 domain 不应有 `iot_class` 字段，否则报错；其他 domain 必须有 `iot_class`（虚拟集成除外）。`script/hassfest/manifest.py:361-369`
71. 虚拟集成的 `supported_by` 必须指向存在的核心集成。`script/hassfest/manifest.py:371-379`
72. SILVER 及以上等级的集成必须有 codeowners。`script/hassfest/manifest.py:381-391`

## 3. quality_scale 质量标准

73. quality_scale 验证模块位于 `script/hassfest/quality_scale.py`。`script/hassfest/quality_scale.py:1`
74. `QUALITY_SCALE_TIERS` 将等级名映射到 `ScaledQualityScaleTiers` 枚举值。`script/hassfest/quality_scale.py:24`
75. `Rule` 数据类包含 `name`、`tier`、`validator`（可选，类型为 `RuleValidationProtocol`）三个字段。`script/hassfest/quality_scale.py:27-33`
76. `ALL_RULES` 列表定义了所有质量规则及其所属等级。`script/hassfest/quality_scale.py:36-95`
77. BRONZE 等级规则包括 20 项：action-setup, appropriate-polling, brands, common-modules, config-flow, config-flow-test-coverage, dependency-transparency, docs-actions, docs-conditions, docs-high-level-description, docs-installation-instructions, docs-removal-instructions, docs-triggers, entity-event-setup, entity-unique-id, has-entity-name, runtime-data, test-before-configure, test-before-setup, unique-config-entry。`script/hassfest/quality_scale.py:37-57`
78. SILVER 等级规则包括 10 项：action-exceptions, config-entry-unloading, docs-configuration-parameters, docs-installation-parameters, entity-unavailable, integration-owner, log-when-unavailable, parallel-updates, reauthentication-flow, test-coverage。`script/hassfest/quality_scale.py:58-68`
79. GOLD 等级规则包括 21 项：devices, diagnostics, discovery, discovery-update-info, docs-data-update, docs-examples, docs-known-limitations, docs-supported-devices, docs-supported-functions, docs-troubleshooting, docs-use-cases, dynamic-devices, entity-category, entity-device-class, entity-disabled-by-default, entity-translations, exception-translations, icon-translations, reconfiguration-flow, repair-issues, stale-devices。`script/hassfest/quality_scale.py:69-90`
80. PLATINUM 等级规则包括 3 项：async-dependency, inject-websession, strict-typing。`script/hassfest/quality_scale.py:91-94`
81. 部分规则带程序化验证器：config-flow→config_flow.validate, discovery→discovery.validate, reconfiguration-flow→reconfiguration_flow.validate, runtime-data→runtime_data.validate, strict-typing→strict_typing.validate, test-before-setup→test_before_setup.validate, unique-config-entry→unique_config_entry.validate。`script/hassfest/quality_scale.py:13-22,42,54,56-57,72,88,94`
82. `SCALE_RULES` 字典按等级分组所有规则名。`script/hassfest/quality_scale.py:97-100`

## 4. 服务发现验证器

83. zeroconf 验证器从 manifest 收集 zeroconf 和 homekit 条目，生成 `homeassistant/generated/zeroconf.py`。`script/hassfest/zeroconf.py:14-36`
84. zeroconf 验证器检测 HomeKit 模型重叠冲突。`script/hassfest/zeroconf.py:38-52`
85. zeroconf 的 `always_discover` 标志基于集成的 `iot_class` 通过 `homekit_always_discover()` 确定。`script/hassfest/zeroconf.py:47-51`
86. dhcp 验证器从 manifest 收集 dhcp 条目，生成 `homeassistant/generated/dhcp.py`，类型注解为 `Final[list[dict[str, str | bool]]]`。`script/hassfest/dhcp.py:7-22`
87. ssdp 验证器从 manifest 收集 ssdp 条目，使用 `defaultdict(list)` 按 domain 分组，生成 `homeassistant/generated/ssdp.py`。`script/hassfest/ssdp.py:9-23`
88. usb 验证器从 manifest 收集 usb 条目，排除 `known_devices` 字段，生成 `homeassistant/generated/usb.py`。`script/hassfest/usb.py:7-25`
89. bluetooth 验证器从 manifest 收集 bluetooth 条目，生成 `homeassistant/generated/bluetooth.py`，类型注解为 `Final[list[dict[str, bool | str | int | list[int]]]]`。`script/hassfest/bluetooth.py:7-24`
90. 所有服务发现验证器遵循相同模式：`generate_and_validate()` 生成内容字符串，`validate()` 比较文件内容（不匹配则添加 fixable 错误），`generate()` 写入文件。`script/hassfest/dhcp.py:25-44`
91. 所有生成文件使用 `format_python_namespace()` 序列化器（来自 `script/hassfest/serializer.py`）。`script/hassfest/dhcp.py:5,19`
92. config_flow 验证器检查 `config_flow.py` 文件存在性，manifest 声明 config_flow 但文件不存在时报错。`script/hassfest/config_flow.py:14-23`
93. config_flow 验证器检测可发现配置流（含 async_step_discovery/bluetooth/hassio/homekit/mqtt/ssdp/zeroconf/dhcp/usb）是否设置 unique_id。`script/hassfest/config_flow.py:27-37`
94. `UNIQUE_ID_IGNORE` 集合包含 huawei_lte, mqtt, adguard, unifi_discovery，这些集成豁免 unique_id 检查。`script/hassfest/config_flow.py:10`
95. config_flow 生成器将集成分为 `integration` 和 `helper` 两类。`script/hassfest/config_flow.py:62-67`

## 5. 翻译工具

96. translations 工具入口位于 `script/translations/__main__.py`，通过 `importlib.import_module()` 动态加载 action 模块。`script/translations/__main__.py:16-25`
97. translations 支持 7 种 action：clean, deduplicate, develop, download, frontend, migrate, upload。`script/translations/util.py:20-28`
98. Lokalise 令牌通过环境变量 `LOKALISE_TOKEN` 或 `.lokalise_token` 文件获取。`script/translations/util.py:34-48`
99. translations const 定义 `CORE_PROJECT_ID = "130246255a974bd3b5e8a1.51616605"` 和 `FRONTEND_PROJECT_ID = "3420425759f6d6d241f598.13594006"`。`script/translations/const.py:5-6`
100. Lokalise CLI v2 Docker 镜像版本为 `v3.1.4`。`script/translations/const.py:7`
101. hassfest translations 验证器定义 `UNDEFINED=0`、`REQUIRED=1`、`REMOVED=2` 三个状态常量。`script/hassfest/translations.py:18-20`
102. 翻译键正则 `RE_TRANSLATION_KEY` 要求小写字母数字、连字符、下划线，不允许前后连字符/下划线或连续双连字符。`script/hassfest/translations.py:23`
103. `ALLOW_NAME_TRANSLATION` 白名单列出允许翻译集成名称的 domain（如 generic, local_calendar, nmap_tracker 等）。`script/hassfest/translations.py:33-54`
104. 核心集成翻译文件为 `strings.json`，自定义集成翻译文件为 `translations/en.json`。`script/hassfest/services.py:256-259`

## 6. scaffold 脚手架

105. scaffold 入口位于 `script/scaffold/__main__.py`，模板列表从 `templates/` 子目录自动发现。`script/scaffold/__main__.py:13-15`
106. scaffold CLI 接受位置参数 `template`（choices=TEMPLATES）和 `--develop`、`--integration` 选项。`script/scaffold/__main__.py:20-28`
107. scaffold 必须从项目根目录运行（检查 `requirements_all.txt` 存在）。`script/scaffold/__main__.py:68-70`
108. 新建集成时，先生成 `integration` 模板，再根据条件自动生成 config_flow 模板：helper 类型→config_flow_helper，oauth2→config_flow_oauth2，authentication 或不可发现→config_flow，否则→config_flow_discovery。`script/scaffold/__main__.py:81-96`
109. `Info` 数据类（使用 attr.s）包含 domain, name, is_new, codeowner, requirement, iot_class, authentication, discoverable, oauth2, integration_type 字段。`script/scaffold/model.py:14-27`
110. `Info` 跟踪 `files_added`、`tests_added`、`examples_added` 三个集合。`script/scaffold/model.py:29-31`
111. `Info.integration_dir` 返回 `homeassistant/components/<domain>`，`tests_dir` 返回 `tests/components/<domain>`。`script/scaffold/model.py:33-41`
112. `Info.update_manifest()` 合并 kwargs 后调用 `sort_manifest()` 排序并写入 JSON。`script/scaffold/model.py:52-60`
113. scaffold const 定义 `COMPONENT_DIR = Path("homeassistant/components")` 和 `TESTS_DIR = Path("tests/components")`。`script/scaffold/const.py:5-6`

## 7. 其他 script 工具

114. `script/const.py` 定义 `COMPONENT_DIR = Path("homeassistant/components")`。`script/const.py:4`
115. `script/util.py` 提供 `valid_integration()` 函数验证集成目录存在。`script/util.py:9-16`
116. `sort_manifest()` 函数对 manifest 字典排序，`domain` 和 `name` 键始终排在最前（通过 `_MANIFEST_SORT_KEYS` 映射为 `.domain`/`.name`）。`script/util.py:19-36`
117. codeowners 验证器自动生成 `CODEOWNERS` 文件，包含核心文件归属（@home-assistant/core）、Supervisor 归属（@home-assistant/supervisor）、各集成归属。`script/hassfest/codeowners.py:5-53`
118. codeowners 验证虚拟集成不生成 CODEOWNERS 条目。`script/hassfest/codeowners.py:73-74`
119. codeowners 验证每个 codeowner 必须以 `@` 开头，否则报错。`script/hassfest/codeowners.py:81-85`
120. 如果集成有 `tests/components/<domain>/__init__.py`，同时生成测试目录的 CODEOWNERS 条目。`script/hassfest/codeowners.py:89-90`
121. CODEOWNERS 中翻译目录被排除（`/homeassistant/components/*/translations/`）。`script/hassfest/codeowners.py:60-63`
122. dependencies 验证器使用 AST 解析（`ImportCollector`）收集集成间引用关系。`script/hassfest/dependencies.py:19-89`
123. `ImportCollector` 忽略 `TYPE_CHECKING` 块中的导入。`script/hassfest/dependencies.py:50-57`
124. `ALLOWED_USED_COMPONENTS` 包含 CORE_INTEGRATIONS、所有 Platform、以及 alert/automation/frontend 等内部集成。`script/hassfest/dependencies.py:91-125`
125. dependencies 验证器使用 `multiprocessing.Pool` 并行解析数千个 Python 文件。`script/hassfest/dependencies.py:240-249`
126. dependencies 验证器检查三类问题：未声明的依赖引用、重复依赖（同时在 dependencies 和 after_dependencies）、循环依赖。`script/hassfest/dependencies.py:235-359`
127. `IGNORE_VIOLATIONS` 包含白名单元组（如 lutron_caseta→lutron, http→network, zha→homeassistant_hardware 等）。`script/hassfest/dependencies.py:127-147`
128. CORE_INTEGRATIONS = {"homeassistant", "persistent_notification"}，不能被其他集成声明为依赖。`script/hassfest/dependencies.py:16`
129. services 验证器使用 voluptuous schema 验证 `services.yaml`，区分核心集成和自定义集成 schema。`script/hassfest/services.py:140-162`
130. services 验证器通过 grep 检测代码中 `hass.services.register/async_register` 调用，注册了服务但无 services.yaml 时报错。`script/hassfest/services.py:218-228`
131. 核心集成每个服务必须在 icons.json 中有对应图标。`script/hassfest/services.py:276-281`
132. 核心集成服务名称和描述必须在 strings.json 中有翻译条目。`script/hassfest/services.py:284-300`
133. mypy_config 生成器从 `.strict-typing` 文件读取严格类型模块列表，自动生成 `mypy.ini`。`script/hassfest/mypy_config.py:1-73`
134. mypy 一般设置包含 python_version（从 REQUIRED_PYTHON_VER 派生）、strict_equality、strict_bytes、no_implicit_optional 等。`script/hassfest/mypy_config.py:31-73`
135. `NO_IMPLICIT_REEXPORT_MODULES` 为 components、application_credentials、diagnostics、spotify、stream、update 设置 no_implicit_reexport。`script/hassfest/mypy_config.py:15-22`

## 8. pytest 配置

136. pytest 配置位于 `pyproject.toml` 的 `[tool.pytest.ini_options]` 段。`pyproject.toml:440`
137. `pythonpath = ["pylint/plugins"]` 将 pylint 插件目录加入 Python 路径。`pyproject.toml:441`
138. `testpaths = ["tests"]` 指定测试目录。`pyproject.toml:442`
139. `norecursedirs = [".git", "testing_config"]` 排除这些目录。`pyproject.toml:443`
140. `asyncio_mode = "auto"` 启用 pytest-asyncio 自动模式，无需 `@pytest.mark.asyncio` 装饰器。`pyproject.toml:447`
141. `asyncio_default_fixture_loop_scope = "function"` 设置默认事件循环 fixture 作用域为函数级。`pyproject.toml:448`
142. `asyncio_debug = true` 启用 asyncio 调试模式。`pyproject.toml:446`
143. `filterwarnings` 将 SQLAlchemy SAWarning 升级为错误。`pyproject.toml:450`
144. pytest 自定义选项 `--dburl`（默认 `sqlite://`）和 `--drop-existing-db`。`tests/conftest.py:164-165`
145. pytest marker `no_fail_on_log_exception` 标记测试不因日志异常失败。`tests/conftest.py:170-172`

## 9. conftest fixtures

146. `tests/conftest.py` 在导入 HA 之前先导入 `patch_json`、`patch_recorder`、`patch_time` 进行 monkey-patch。`tests/conftest.py:45-55`
147. `pytest.register_assert_rewrite("tests.common")` 注册 tests.common 以获得更详细的断言信息。`tests/conftest.py:129`
148. 事件循环策略设置为 `runner.HassEventLoopPolicy(False)`，并禁止后续覆盖。`tests/conftest.py:154-156`
149. `pytest_runtest_setup()` 中配置 pytest_socket：允许 127.0.0.1，禁用其他 socket（allow_unix_socket=True）。`tests/conftest.py:193-212`
150. DNS 解析被限制：仅允许 localhost/127.0.0.1/::1/0.0.0.0 等本地地址，其他主机名抛出 RuntimeError("DNS resolution disabled in tests")。`tests/conftest.py:214-236`
151. `HASocketBlockedError` 继承自 `pytest_socket.SocketBlockedError`，维护 `instances` 类变量计数。`tests/conftest.py:182-190`
152. `caplog` fixture 被覆盖，设置日志级别为 DEBUG。`tests/conftest.py:285-289`
153. `garbage_collection` fixture（autouse, scope="module"）在每个模块前后执行 `gc.collect()` 和 `gc.freeze()`。`tests/conftest.py:292-303`
154. `expected_lingering_tasks` 和 `expected_lingering_timers` 是 autouse fixture，可通过 parametrize 设为 True 来绕过清理检查。`tests/conftest.py:306-335`
155. 非 platform 组件的 lingering timers 默认允许（`expected_lingering_timers` 返回 True）。`tests/conftest.py:327-335`
156. `enable_event_loop_debug` 是 autouse async fixture，启用事件循环调试。`tests/conftest.py:380-383`
157. `verify_cleanup` 是 `@pytest_asyncio.fixture(autouse=True)`，在测试后检查：残留任务、残留定时器、残留线程、时区恢复、respx mock 清理、socket 连接。`tests/conftest.py:386-472`
158. `verify_cleanup` 检测到 ≥2 个未停止 INSTANCES 时调用 `pytest.exit()` 中止测试运行。`tests/conftest.py:406-410`
159. `verify_cleanup` 验证默认时区恢复为 UTC。`tests/conftest.py:446-451`
160. `verify_cleanup` 验证 respx.mock.routes 为空，否则提示使用 `@respx.mock` 装饰器。`tests/conftest.py:453-461`
161. `reset_globals` fixture（autouse）在测试后重置 `_Hass` threading.local 和 frame helper 全局变量。`tests/conftest.py:475-485`
162. `bcrypt_cost` fixture（autouse, scope="session"）将 bcrypt rounds 从 12 降为 4 以加速测试。`tests/conftest.py:494-504`
163. `hass_storage` fixture 包装 `mock_storage()` 上下文管理器。`tests/conftest.py:507-511`
164. `load_registries` fixture 控制是否加载注册表，可通过 `@pytest.mark.parametrize("load_registries", [False])` 跳过。`tests/conftest.py:514-521`
165. `aiohttp_client_cls` fixture 返回 `CoalescingClient` 类，模拟 WebSocket JS 客户端的消息合并行为。`tests/conftest.py:557-560`
166. `aiohttp_client` fixture 覆盖 pytest-aiohttp 默认实现，支持 Application/BaseTestServer 参数。`tests/conftest.py:563-599`
167. `hass` 是 async fixture，创建 `async_test_home_assistant()` 实例，设置异常处理器，预加载 homeassistant 翻译。`tests/conftest.py:657-697`
168. `hass` fixture 依赖 `hass_fixture_setup`、`load_registries`、`hass_config_dir`、`hass_storage`、`mock_recorder_before_hass`。`tests/conftest.py:657-664`
169. `hass_client` fixture 返回已认证的 HTTP 客户端（自动携带 Bearer token）。`tests/conftest.py:902-916`
170. `hass_client_no_auth` fixture 返回未认证的 HTTP 客户端。`tests/conftest.py:919-931`
171. `enable_custom_integrations` fixture 通过清除 `DATA_CUSTOM_COMPONENTS` 缓存启用测试目录中的自定义集成。`tests/conftest.py:1500-1503`
172. `enable_statistics`、`enable_missing_statistics`、`enable_schema_validation`、`enable_nightly_purge` fixture 默认返回 False，可通过 parametrize 启用。`tests/conftest.py:1506-1543`
173. `snapshot` fixture 覆盖 syrupy 默认 fixture，使用 `HomeAssistantSnapshotExtension` 扩展。`tests/conftest.py:2223-2225`
174. `disable_block_async_io` fixture 用于禁用 block_async_io 循环保护。`tests/conftest.py:2228-2237`

## 10. tests/common 工具

175. `tests/common.py` 模块文档为 `"Test the helper method for writing tests."`。`tests/common.py:1`
176. `INSTANCES = []` 全局列表跟踪所有创建的 HA 测试实例。`tests/common.py:135`
177. `CLIENT_ID = "https://example.com/app"` 和 `CLIENT_REDIRECT_URI = "https://example.com/app/callback"` 用于 OAuth 测试。`tests/common.py:136-137`
178. `QualityScaleStatus` 是 StrEnum，值为 done/exempt/todo。`tests/common.py:140-145`
179. `threadsafe_callback_factory()` 和 `threadsafe_coroutine_factory()` 将回调/协程转换为线程安全版本。`tests/common.py:160-191`
180. `get_test_config_dir()` 返回 `tests/testing_config` 路径。`tests/common.py:194-196`
181. `StoreWithoutWriteLoad` 是不写入不加载的 Store 测试替身。`tests/common.py:199-215`
182. `async_test_home_assistant()` 是创建测试 HA 实例的核心异步函数。`tests/common.py:217`
183. `async_mock_service()` 异步注册模拟服务并返回调用记录列表。`tests/common.py:374`
184. `async_fire_time_changed_exact()` 和 `async_fire_time_changed()` 触发时间变更事件。`tests/common.py:484-533`
185. `get_fixture_path()` 返回测试 fixture 文件路径，支持 `integration` 参数定位 `tests/components/<integration>/` 下的 fixture。`tests/common.py:564-580`
186. `load_fixture()`/`load_fixture_bytes()` 读取 fixture 文件内容。`tests/common.py:582-591`
187. `load_json_value_fixture()`、`load_json_array_fixture()`、`load_json_object_fixture()` 分别加载 JSON 标量/数组/对象 fixture。`tests/common.py:600-633`
188. `mock_component()` 标记集成为已加载（通过设置 `hass.data[DATA_COMPONENTS]`）。`tests/common.py:653-659`
189. `mock_registry()`、`mock_area_registry()`、`mock_device_registry()` 创建模拟注册表。`tests/common.py:661-770`
190. `MockGroup` 和 `MockUser` 是 auth 模型的测试替身。`tests/common.py:772-832`
191. `MockModule` 和 `MockPlatform` 模拟集成模块和平台。`tests/common.py:860-998`
192. `MockConfigEntry` 继承自 `config_entries.ConfigEntry`，提供测试默认值（domain="test", title="Mock Title", source=SOURCE_USER）。`tests/common.py:1088-1132`
193. `MockConfigEntry.add_to_hass()` 将条目直接添加到 `hass.config_entries._entries`。`tests/common.py:1136-1138`
194. `MockConfigEntry.mock_state()` 调用 `_async_set_state()` 设置条目状态（如 LOADED/SETUP_ERROR）。`tests/common.py:1144-1163`
195. `MockConfigEntry.start_reauth_flow()` 和 `start_reconfigure_flow()` 启动重新认证/重新配置流程。`tests/common.py:1165-1191`
196. `assert_setup_component()` 是上下文管理器，验证组件设置次数。`tests/common.py:1274-1324`
197. `mock_restore_cache()` 和 `mock_restore_cache_with_extra_data()` 模拟状态恢复缓存。`tests/common.py:1326-1378`
198. `MockEntity` 是实体测试基类。`tests/common.py:1400`
199. `mock_storage()` 上下文管理器模拟存储层，返回存储数据字典。`tests/common.py:1498-1576`
200. `flush_store()` 异步刷新 Store 数据。`tests/common.py:1578-1586`
201. `patch_yaml_files()` 上下文管理器临时替换 YAML 文件内容。`tests/common.py:1237-1272`
202. `tests/components/common.py` 提供 `target_entities()` 辅助函数，创建关联 area/device/label 的测试实体。`tests/components/common.py:52-177`
203. `parametrize_target_entities()` 返回参数化测试数据，覆盖 entity_id/label_id/area_id/floor_id 等目标类型。`tests/components/common.py:180-200`

## 11. syrupy snapshot 测试

204. syrupy 扩展位于 `tests/syrupy.py`，定义 `HomeAssistantSnapshotExtension`。`tests/syrupy.py:253`
205. `HomeAssistantSnapshotSerializer` 继承 `AmberDataSerializer`，处理 HA 特殊数据类型。`tests/syrupy.py:76`
206. serializer 将 `State` 对象序列化为字典，将 context/last_changed/last_reported/last_updated 替换为 `ANY`。`tests/syrupy.py:227-237`
207. serializer 将 `ConfigEntry` 序列化为字典，将 entry_id 替换为 `ANY`，移除 created_at/modified_at。`tests/syrupy.py:150-154,179-185`
208. serializer 将 `DeviceEntry` 序列化为字典，将 config_entries/id/via_device_id/primary_config_entry 替换为 `ANY`。`tests/syrupy.py:157-176`
209. serializer 将 `EntityRegistryEntry` 序列化为字典，将 config_entry_id/device_id/id 替换为 `ANY`。`tests/syrupy.py:188-207`
210. serializer 将 `AreaEntry` 的 id 替换为 `ANY`。`tests/syrupy.py:143-148`
211. serializer 将 `IssueEntry` 的 created 替换为 `ANY`。`tests/syrupy.py:220-224`
212. serializer 将 `FlowResult` 的 flow_id 替换为 `ANY`。`tests/syrupy.py:210-212`
213. serializer 支持 `vol.Schema` 通过 `voluptuous_serialize.convert()` 序列化。`tests/syrupy.py:116-117`
214. serializer 支持 dataclass（通过 `dataclasses.asdict()`）和 attrs 类（通过 `attrs.asdict()`）。`tests/syrupy.py:120-130`
215. `_IntFlagWrapper` 规范化 IntFlag 的 repr，消除 Python 3.10/3.11 差异。`tests/syrupy.py:240-250`
216. `HomeAssistantSnapshotExtension.dirname()` 将快照目录从默认 `__snapshots__` 改为 `snapshots`。`tests/syrupy.py:264-274`
217. `VERSION = "1"` 是序列化格式版本，变更序列化逻辑时需 bump。`tests/syrupy.py:256-260`
218. `override_syrupy_finish()` 覆盖 syrupy 默认 finish 方法以支持 pytest-xdist 并行测试的快照合并。`tests/syrupy.py:375-435`
219. xdist worker 将结果写入 `.pytest_syrupy_<worker>_result` JSON 文件，controller 合并后删除。`tests/syrupy.py:391-425`

## 12. patch 工具

220. `patch_json.py` 在导入时替换 `json_helper.json_encoder_default`，检测 mock 对象序列化并抛出 TypeError。`tests/patch_json.py:16-27`
221. `patch_json.py` 使用 `orjson.dumps` 替换 `json_bytes` 和 `json_bytes_sorted`，配置 `OPT_NON_STR_KEYS`。`tests/patch_json.py:28-35`
222. `patch_time.py` 提供 `HAFakeDate` 和 `HAFakeDatetime` 类，扩展 freezegun 以支持 fold 属性和改进类字符串表示。`tests/patch_time.py:27-50`
223. `ha_datetime_to_fakedatetime()` 包含 freezegun PR #424 的修复（fold 支持）。`tests/patch_time.py:9-24`
224. `patch_recorder.py` 包装 `recorder_helper.session_scope` 为可 patch 的上下文管理器，必须在 recorder.util 导入前执行。`tests/patch_recorder.py:1-25`
225. `patch_recorder.py` 使用断言确保 `homeassistant.components.recorder.util` 尚未导入。`tests/patch_recorder.py:10`

## 13. 测试模式示例

226. 测试中通过 `MockConfigEntry(domain="test")` 创建模拟配置条目，然后调用 `entry.add_to_hass(hass)` 添加到 HA 实例。`tests/components/common.py:75-76`
227. `enable_custom_integrations` fixture 启用测试目录中的自定义集成，用于集成测试。`tests/conftest.py:1500-1503`
228. snapshot 测试模式：`assert result == snapshot` 或 `assert entity.state == snapshot`，快照文件存放在 `snapshots/` 目录。`tests/syrupy.py:264-274`
229. `async_fire_time_changed(hass, datetime)` 用于测试时间相关逻辑（定时器、调度）。`tests/common.py:503`
230. `async_mock_service(hass, domain, service)` 注册模拟服务并返回调用列表，用于验证服务调用。`tests/common.py:374`
231. 设备注册测试中使用 `dr.DeviceEntry(id="test_device", area_id=area.id)` 和 `mock_device_registry(hass, {device.id: device})` 模拟设备。`tests/components/common.py:93-94`
232. `location_util.async_detect_location_info` 被 `check_real()` 守卫包装，测试中必须传 `_test_real=True` 或 mock 才能调用。`tests/conftest.py:262-282`
233. `CoalescingResponse` 模拟 WebSocket 客户端的 JSON 数组合并行为（与 JS 客户端一致）。`tests/conftest.py:524-546`

## 14. 静态检查（ruff/mypy）

234. ruff 配置位于 `pyproject.toml` 的 `[tool.ruff]` 段，要求版本 `>=0.15.18`。`pyproject.toml:650-651`
235. ruff 启用了大量规则集：A001(builtin-shadowing), ASYNC, B(bugbear), BLE, C(complexity), D(docstrings), DTZ(timezone), E/F(pycodestyle/pyflakes), FLY(flynt), FURB(refurb), G(logging), I(isort), LOG, PGH, PIE, PL(pylint), PT(pytest), PTH(pathlib), RET, RSE, RUF, S(security), SIM(simplify), SLF, SLOT, T(flake8-debugger), TC(type-checking), TID(tidy-imports), TRY(tryceratops), UP(pyupgrade), W(pycodestyle)。`pyproject.toml:653-721`
236. ruff 忽略规则包括 E501(行长度)、B008(默认参数中的函数调用)、D203/D213(docstring 格式)、PLR0911/0912/0913/0915(复杂度)、TC001-003(类型检查导入)、SIM102/103/108/115 等。`pyproject.toml:723-785`
237. ruff import 约定：`voluptuous` 必须导入为 `vol`；各组件 PLATFORM_SCHEMA 有标准别名（如 BINARY_SENSOR_PLATFORM_SCHEMA）。`pyproject.toml:787-789`
238. ruff pytest-style 配置：`fixture-parentheses = false`、`mark-parentheses = false`。`pyproject.toml:849-851`
239. ruff banned-api：禁止 `async_timeout`（用 asyncio.timeout）、`pytz`（用 zoneinfo）、`tests` 包导入、`__future__.annotations`。`pyproject.toml:853-857`
240. ruff isort 配置：`force-sort-within-sections = true`、`known-first-party = ["homeassistant"]`、`combine-as-imports = true`。`pyproject.toml:859-863`
241. ruff mccabe 最大复杂度为 25。`pyproject.toml:884-885`
242. ruff pydocstyle 使用 google 约定。`pyproject.toml:887-888`
243. ruff per-file-ignores 允许 `script/*` 和 `homeassistant/scripts/*` 使用 print（T201/T20）。`pyproject.toml:867-870`
244. mypy.ini 由 hassfest 自动生成（`script/hassfest/mypy_config.py`）。`mypy.ini:1-3`
245. mypy 目标 Python 版本为 3.14，平台为 linux。`mypy.ini:6-7`
246. mypy 启用 pydantic 插件、show_error_codes、strict_equality、strict_bytes、no_implicit_optional、warn_unused_ignores 等。`mypy.ini:8-30`
247. mypy 启用错误代码：deprecated, explicit-override, ignore-without-code, redundant-self, truthy-iterable。`mypy.ini:20`
248. mypy 禁用错误代码：annotation-unchecked, import-not-found, import-untyped。`mypy.ini:21`
249. `.strict-typing` 文件列出启用 `disallow_any_generics` 的模块，包括 homeassistant.core、homeassistant.exceptions、homeassistant.auth.auth_store、homeassistant.helpers 下多个模块。`.strict-typing:8-30`
250. pydantic mypy 插件配置：init_forbid_extra=true, init_typed=true, warn_required_dynamic_aliases=true, warn_untyped_fields=true。`mypy.ini:32-36`
251. pre-commit 配置使用 ruff-pre-commit v0.15.18（ruff-check --fix 和 ruff-format）。`.pre-commit-config.yaml:2-9`
252. pre-commit 包含 codespell v2.4.2（拼写检查）、zizmor v1.24.1（GitHub Actions 安全）、yamllint v1.38.0、prettier v3.6.2。`.pre-commit-config.yaml:10-50`
253. pre-commit local hooks 包括 mypy、pylint、gen_requirements_all、hassfest、hassfest-metadata、hassfest-mypy-config。`.pre-commit-config.yaml:65-119`
254. hassfest pre-commit hook 监听 `manifest.json`、`strings.json`、`services.yaml`、`quality_scale.yaml`、`brands/*.json` 等文件变更。`.pre-commit-config.yaml:99-105`
255. requirements_test.txt 固定测试依赖版本：pytest==9.0.3, pytest-asyncio==1.4.0, pytest-aiohttp==1.1.1, pytest-xdist==3.8.0, pytest-cov==7.1.0, syrupy==5.3.2, mypy==2.1.0, pylint==4.0.6, freezegun==1.5.5, respx==0.23.1, pytest-socket==0.8.0。`requirements_test.txt:14-41`

## 15. CI 工作流

256. CI 工作流位于 `.github/workflows/ci.yaml`，名称为 "CI"。`.github/workflows/ci.yaml:1`
257. CI 触发条件：push 到 dev/rc/master 分支、所有 pull_request、手动 workflow_dispatch。`.github/workflows/ci.yaml:5-12`
258. workflow_dispatch 支持输入参数：full（全量运行）、lint-only（跳过 pytest）、skip-coverage、pylint-only、mypy-only、audit-licenses-only。`.github/workflows/ci.yaml:13-37`
259. CI 环境变量：`HA_SHORT_VERSION = "2026.8"`、`PYTHONASYNCIODEBUG = 1`、`HASS_CI = 1`、`SQLALCHEMY_WARN_20 = 1`。`.github/workflows/ci.yaml:39-66`
260. CI 并发组按 PR 编号或 ref 分组，取消进行中的旧运行（`cancel-in-progress: true`）。`.github/workflows/ci.yaml:70-72`
261. `info` job 收集变更信息，使用 dorny/paths-filter 检测核心文件和集成变更。`.github/workflows/ci.yaml:75-135`
262. CI 动态生成集成路径过滤器（`.integration_paths.yaml`），映射每个集成到 `homeassistant/components/<domain>/**` 和 `tests/components/<domain>/**`。`.github/workflows/ci.yaml:121-130`
263. 变更仅涉及集成时，仅运行相关集成测试（test_group_count=1），不运行 MariaDB/PostgreSQL 矩阵。`.github/workflows/ci.yaml:168-196`
264. dev/master/rc 分支、核心文件变更、full 输入或 `ci-full-run` 标签触发全量测试（10 个分组，所有数据库版本）。`.github/workflows/ci.yaml:198-212`
265. 测试分为 10 个组并行运行（`test_groups="[1,2,...,10]"`）。`.github/workflows/ci.yaml:156`
266. MariaDB 测试矩阵包含 6 个版本：10.3.32, 10.6.10, 10.10.3, 10.11.2, 11.4.9, mysql:8.0.32。`.github/workflows/ci.yaml:56`
267. PostgreSQL 测试矩阵包含 2 个版本：12.14, 15.2。`.github/workflows/ci.yaml:61`
268. `prek` job 运行 pre-commit 检查，跳过 no-commit-to-branch/mypy/pylint/gen_requirements_all/hassfest/hassfest-metadata/hassfest-mypy-config/zizmor。`.github/workflows/ci.yaml:255-280`
269. `zizmor` job 检查 GitHub Actions workflow 安全性（--all-files --pedantic）。`.github/workflows/ci.yaml:282-300`
270. `lint-hadolint` job 检查 Dockerfile、Dockerfile.dev、script/hassfest/docker/Dockerfile。`.github/workflows/ci.yaml:302-330`
271. `base` job 准备 Python 虚拟环境，使用 actions/cache 缓存 venv 和 uv wheel 缓存。`.github/workflows/ci.yaml:332-456`
272. base job 安装 OS 依赖：bluez, ffmpeg, libturbojpeg, libxml2-utils, libav* 系列, libudev-dev。`.github/workflows/ci.yaml:385-398`
273. base job 使用 uv 安装 requirements.txt、requirements_all.txt、requirements_test.txt，并以 editable 模式安装 HA。`.github/workflows/ci.yaml:417-419`
274. base job 运行 `script/check_dirty` 验证无意外文件变更。`.github/workflows/ci.yaml:434-436`
275. `hassfest` job 运行 `python -m script.hassfest --requirements --action validate`。`.github/workflows/ci.yaml:496-499`
276. `gen-requirements-all` job 运行 `python -m script.gen_requirements_all validate`。`.github/workflows/ci.yaml:533-536`
277. 运行器使用 `ubuntu-24.04`。`.github/workflows/ci.yaml:77`
278. Python 版本从 `.python-version` 文件读取，支持通过 `ADDITIONAL_PYTHON_VERSIONS` 环境变量添加额外版本矩阵。`.github/workflows/ci.yaml:162-166`
