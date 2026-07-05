# scikit-build-core 源码结构研究摘要

> 源码版本：v0.12.2-164-g4f0a4b6
> 源码根：`external/tools/scikit-build-core/`
> 所有路径相对 `src/scikit_build_core/`，行号锚点格式 `path#L行号` 或 `path#L起-L止`

---

## 模块树总览

### 顶层文件（13 个 .py + 类型标记）

| 文件 | 一句话职责 |
|---|---|
| `__init__.py` | 包入口，导出 `__version__`（由 hatch-vcs 写入 `_version.py`） |
| `__main__.py#L37` | CLI 入口 `main()`，注册 4 个子命令：`build` / `builder` / `file-api` / `init` |
| `cmake.py` | `CMake`（值对象，含 `default_search`）与 `CMaker`（重量级构建器，封装 configure/build/install） |
| `errors.py` | 项目异常体系（`CMakeNotFoundError`、`CMakeConfigError`、`FailedLiveProcessError` 等） |
| `format.py` | 模板格式化 `pyproject_format`，用于 `generate` 配置项与字符串替换 |
| `program_search.py#L39-L46` | 系统中 CMake/Ninja/Make 程序查找（`Program` NamedTuple、`best_program`、`get_cmake_programs` 等） |
| `_logging.py` | 基于 rich 的彩色结构化日志（`ScikitBuildLogger`、`LEVEL_VALUE`、`rich_print`/`rich_error`/`rich_warning`） |
| `_reproducible.py` | 可复现构建辅助（`get_reproducible_epoch`、`normalize_file_permissions`、`parse_source_date_epoch`，ZIP 时间戳边界 1980–2107） |
| `_shutil.py` | subprocess 包装类 `Run`，统一进程调用与日志 |
| `_variants.py` | 实验性 PEP 817 变体支持（`variant_build_requires`、`validate_variant_settings`、`get_wheel_variant`） |
| `_check_extra.py` | 可选依赖缺失告警（`warn_missing_extra`） |
| `_version.pyi` | 版本字符串类型存根 |
| `py.typed` | PEP 561 类型标记 |

### 子目录（14 个）

| 目录 | 一句话职责 |
|---|---|
| `_compat/` | 跨版本兼容垫片：`tomllib`、`typing`（`Self`/`Annotated`/`assert_never`）、`importlib`（`metadata`/`resources`）、`setuptools.errors`、`builtins`（`ExceptionGroup` 回退）。Ruff 强制使用，禁止直接 import 标准库对应模块 |
| `_vendor/pyproject_metadata/` | vendored 的 `pyproject_metadata` 库，解析 PEP 621 `[project]` 表为 `StandardMetadata`。**禁止 lint 或手改** |
| `ast/` | 自定义 AST 解析器（`tokenizer.py`、`ast.py`），用于解析 overrides 中的条件表达式（如 `if.env.X`、`if.python-version`） |
| `build/` | PEP 517 构建后端入口与 wheel/sdist 实现的核心目录 |
| `builder/` | 高层 CMake 构建编排（`Builder` 类、generator 选择、wheel tag、sysconfig、macos 跨编译、get_requires） |
| `file_api/` | CMake File API 客户端：`query.py` 写入 stateless query，`reply.py` 读取回复，`model/` 为 6 个响应数据类 |
| `hatch/` | hatchling 构建钩子插件（实验性），`ScikitBuildHook` 复用 Builder/CMaker 基础设施 |
| `init/` | 项目脚手架生成器，支持 pybind11/nanobind/c/cython/swig/fortran/abi3/abi3t 后端模板 |
| `metadata/` | 4 个内置动态元数据提供者（`regex`、`template`、`setuptools_scm`、`fancy_pypi_readme`） |
| `resources/` | 打包资源：`_editable_redirect.py`（可编辑安装重定向 shim）、`find_python/`（CMake FindPython 助手）、`scikit-build.schema.json`（生成的 JSON Schema） |
| `settings/` | 配置系统：数据模型 + 源链 + 覆盖 + JSON Schema 生成 + 自动版本检测 |
| `setuptools/` | setuptools 兼容层：`build_meta.py` 包装 `setuptools.build_meta`，`build_cmake.py` 实现 distutils `build_cmake` 命令，`wrapper.py` 提供 `setup()` |
| `utils/` | 通用工具：`typing.py`（`get_target_raw_type`、`is_union_type`、`process_union`，供 settings 反射用） |
| （`resources/find_python/`） | CMake `find_python` 模块资源子目录 |

---

## PEP 517 构建后端入口

### 后端声明

`external/tools/scikit-build-core/pyproject.toml#L1-L3`：
- `[build-system]` requires = `hatchling >=1.24`、`hatch-vcs >=0.4`
- `build-backend` = `hatchling.build`（scikit-build-core 自身用 hatchling 构建）

scikit-build-core **作为依赖项被下游项目使用**时，下游 `pyproject.toml` 写 `build-backend = "scikit_build_core.build"`，钩子从 `src/scikit_build_core/build/__init__.py` 导出。

### 钩子函数位置（`build/__init__.py`）

| 钩子 | 行号 | 委托目标 |
|---|---|---|
| `build_wheel` | `src/scikit_build_core/build/__init__.py#L45-L58` | `_build_wheel_impl(..., editable=False)` |
| `build_editable` | `src/scikit_build_core/build/__init__.py#L61-L74` | `_build_wheel_impl(..., editable=True)` |
| `prepare_metadata_for_build_wheel` | `src/scikit_build_core/build/__init__.py#L95-L104`（仅当 `_has_safe_metadata()` 为真） | `_build_wheel_impl(None, ...)` 返回 dist-info 目录 |
| `prepare_metadata_for_build_editable` | `src/scikit_build_core/build/__init__.py#L106-L116`（同上条件） | 同上，`editable=True` |
| `build_sdist` | `src/scikit_build_core/build/__init__.py#L124-L131` | `build.sdist.build_sdist` |
| `get_requires_for_build_sdist` | `src/scikit_build_core/build/__init__.py#L134-L150` | `GetRequires.from_config_settings(state="sdist")` |
| `get_requires_for_build_wheel` | `src/scikit_build_core/build/__init__.py#L173-L176` | `_get_requires_for_build_wheel(state="wheel")` |
| `get_requires_for_build_editable` | `src/scikit_build_core/build/__init__.py#L179-L182` | `_get_requires_for_build_wheel(state="editable")` |

`_has_safe_metadata()`（`build/__init__.py#L77-L90`）会扫描 `tool.scikit-build.overrides[].if.failed`，若存在则以"不安全"模式禁用 `prepare_metadata_*`（避免 metadata 阶段失败导致后续 retry 失效）。

### 钩子实现位置

| 实现函数 | 行号 | 说明 |
|---|---|---|
| `_build_wheel_impl` | `src/scikit_build_core/build/wheel.py#L215` | wheel/editable 共用入口，分发到 `_build_wheel_impl_impl` |
| `_build_wheel_impl_impl` | `src/scikit_build_core/build/wheel.py#L310` | 实际构建逻辑：settings→metadata→configure→build→install→pack |
| `build_sdist` | `src/scikit_build_core/build/sdist.py#L129` | sdist 实现（默认 `sdist.cmake=false`，跳过 CMake） |
| `get_standard_metadata` | `src/scikit_build_core/build/metadata.py#L53` | 由 wheel/sdist 共用，调用 vendored `pyproject_metadata` |

### 入口点注册（`pyproject.toml`）

- `validate_pyproject.tool_schema.scikit-build` → `scikit_build_core.settings.skbuild_schema:get_skbuild_schema`（`pyproject.toml#L89`）
- `dynamic_metadata.provider` 4 个：`scikit_build_core.metadata.{regex,template,setuptools_scm,fancy_pypi_readme}:Provider`（`pyproject.toml#L95-L98`）
- `distutils.commands.build_cmake` → `scikit_build_core.setuptools.build_cmake:BuildCMake`（`pyproject.toml#L81`）
- `distutils.setup_keywords.cmake_*`（6 个）→ `setuptools.build_cmake`（`pyproject.toml#L82-L87`）
- `setuptools.finalize_distribution_options.scikit_build_entry` → `setuptools.build_cmake:finalize_distribution_options`（`pyproject.toml#L88`）
- `hatch.scikit-build` → `scikit_build_core.hatch.hooks`（`pyproject.toml#L90`）

### CLI 入口（`pyproject.toml#L74-L78`）

- `scikit-build` 与 `scikit-build-core` 两个脚本均指向 `scikit_build_core.__main__:main`
- CLI 子命令树见 `src/scikit_build_core/__main__.py#L37-L82`：`build` / `builder` / `file-api` / `init`

---

## 配置系统

### 数据模型（`settings/skbuild_model.py`）

主数据类 `ScikitBuildSettings`（`src/scikit_build_core/settings/skbuild_model.py#L815-L933+`）聚合 11 个子节 + 顶级字段：

| 子节 / 字段 | 行号 | 说明 |
|---|---|---|
| `cmake: CMakeSettings` | `skbuild_model.py#L164` | CMake 二进制版本/路径/args/define/build-type/toolchain 等 |
| `search: SearchSettings` | `skbuild_model.py#L270` | CMake/Ninja 查找上下文 |
| `ninja: NinjaSettings` | `skbuild_model.py#L278` | Ninja 版本/路径 |
| `logging: LoggingSettings` | `skbuild_model.py#L313` | 日志级别 |
| `sdist: SDistSettings` | `skbuild_model.py#L323` | sdist 配置（`cmake`/`reproducible`/`include`/`exclude`/`force-include`/`strip`/`add` 等） |
| `wheel: WheelSettings` | `skbuild_model.py#L434` | wheel 配置（`platlib`/`pure-python`/`py-api`/`expand-macos-universal-tags`/`license-files`/`build-tag`/`exclude`/`build-tool` 等） |
| `backport: BackportSettings` | （L434 之后） | Python 旧版本回退配置 |
| `editable: EditableSettings` | `skbuild_model.py#L636` | 可编辑安装（`mode`、`rebuild`、`verbose`、`install_dir`） |
| `build: BuildSettings` | `skbuild_model.py#L689` | 构建目录、工具选择、component 安装目标 |
| `install: InstallSettings` | `skbuild_model.py#L718` | 安装目标路径映射（components、strip） |
| `generate: List[GenerateSettings]` | `skbuild_model.py#L759` | 文件生成项（template/template-path + path） |
| `messages: MessagesSettings` | `skbuild_model.py#L798` | 自定义构建阶段消息 |
| `metadata: Dict[str, Dict[str, Any]]` | `skbuild_model.py#L829` | 旧式动态元数据表（legacy） |
| `env: Annotated[Dict[str, EnvValue], "EnvTable"]` | `skbuild_model.py#L834-L848` | CMake 子进程环境变量（v1.0+） |
| `strict_config: bool = True` | `skbuild_model.py#L850` | 严格校验未知配置项 |
| `experimental: bool = False` | `skbuild_model.py#L859` | 启用未定稿特性 |
| `variant` / `variant_name` / `variant_label` / `null_variant` | `skbuild_model.py#L864-L910` | PEP 817 实验性变体（override-only，不能在静态表设置） |
| `minimum_version: Optional[Version]` | `skbuild_model.py#L912` | 向后兼容版本门 |
| `build_dir: str = ""` | `skbuild_model.py#L922` | CMake 构建目录（默认临时目录） |
| `fail: Optional[bool]` | `skbuild_model.py#L929` | override-only，立即失败 |

`CMakeSettingsDefine`（`skbuild_model.py#L61-L82`）：str 子类型，自动将 bool/list 归一化为 CMake 表示（`TRUE`/`FALSE`/分号分隔列表）。

`EnvValue`（`skbuild_model.py#L85-L120+`）：支持 `{env, default, force}` 表或裸字符串，延迟到构建时解析。

### 源链（`settings/sources.py`）

文件顶部 docstring（`src/scikit_build_core/settings/sources.py#L1-L79`）描述三个具体 Source 与 `SourceChain`：

| Source | 输入 | 编码 |
|---|---|---|
| `EnvSource` | `SKBUILD_*` 环境变量 | 列表 `a;b`，dict `k=v;k2=v2` |
| `ConfSource` | PEP 517 `config-settings`（扁平点号键，如 `-Ca.b=c`） | 同上 |
| `TOMLSource` | `tool.scikit-build` 嵌套 TOML 表 | 原生 TOML 类型 |
| `SourceChain` | 按顺序查询，第一个匹配的 source 转换值 | dict 跨源合并而非替换 |

优先级：env > config-settings > TOML。

### 编排器（`settings/skbuild_read_settings.py`）

`SettingsReader`（`src/scikit_build_core/settings/skbuild_read_settings.py#L61`，类定义在后）：
- 用 `SourceChain` 合并三源
- 调用 `process_overrides` 应用条件覆盖
- 调用 `_handle_minimum_version`（`#L71`）做版本兼容改写
- 调用 `find_min_cmake_version`（`settings/auto_cmake_version.py`）解析 `cmake_minimum_required`
- 调用 `get_min_requires`（`settings/auto_requires.py`）自动检测最小依赖
- 调用 `load_config_providers`（`settings/_load_entrypoint_config.py`）加载入口点配置提供者
- 校验未知选项、override-only 字段

### 条件覆盖（`settings/skbuild_overrides.py`）

`process_overrides`（`src/scikit_build_core/settings/skbuild_overrides.py#L38`）支持 `if` 选择器（见 `skbuild_schema.py#L106-L173`）：
- `scikit-build-version`、`python-version`、`implementation-name`、`implementation-version`
- `platform-system`、`platform-machine`、`platform-node`
- `state`（`sdist`/`wheel`/`editable`/`metadata_wheel`/`metadata_editable`）
- `from-sdist`、`failed`（构建失败重试）、`system-cmake`、`cmake-wheel`、`abi-flags`
- `env`（环境变量正则或布尔）
- `any`（任一子条件满足）

`inherit`（`skbuild_schema.py#L174-L177`）：`none`/`append`/`prepend`，控制覆盖是否继承默认值。

`OverrideRecord`（`skbuild_overrides.py#L51`）：记录覆盖动作的原始值、最终值与原因。

### JSON Schema（`settings/skbuild_schema.py`）

- `generate_skbuild_schema`（`src/scikit_build_core/settings/skbuild_schema.py#L41`）：从 `ScikitBuildSettings` 数据类生成完整 JSON Schema
  - 通过 `settings/json_schema.py` 的 `to_json_schema` 转换
  - 特殊处理：`generate` 项的 `template`/`template-path` 互斥（oneOf）、`metadata` 限制字段集、`override-only` 字段单独分组
  - 生成 `if_overrides`、`inherit` 定义
- `get_skbuild_schema`（`src/scikit_build_core/settings/skbuild_schema.py#L233`）：从打包资源读取已生成的 `resources/scikit-build.schema.json`
- **生成的 schema 落地于 `src/scikit_build_core/resources/scikit-build.schema.json`，由 `nox -t gen` 重新生成**

### 配置项文档

- `settings/documentation.py`：从数据类 docstring 抽取配置项文档
- `settings/skbuild_docs_readme.py` / `skbuild_docs_sphinx.py`：分别生成 README 与 Sphinx 格式文档
- `docs/reference/configs.md` 与 `README.md` 含 cog 生成段（修改 model 后须 `nox -t gen`）

---

## CMake 集成机制

### 三层抽象

1. **`CMake`（值对象，`src/scikit_build_core/cmake.py#L67-L99`）**：frozen dataclass，持有 `version` 与 `cmake_path`。`default_search` 类方法（`#L71-L95`）按 `SpecifierSet` 在系统路径与 PyPI 包中查找 CMake，找不到抛 `CMakeNotFoundError`。

2. **`CMaker`（重量级构建器，`src/scikit_build_core/cmake.py#L102`）**：管理构建目录生命周期与 CMake 子进程调用：
   - `configure`（`cmake.py#L284`）：写 `CMakeInit.txt`（含所有 `SKBUILD_*` cache entry），运行 `cmake -S … -B …`，并在配置前写入 `file_api.query.stateless_query` 触发 file-api 响应
   - `build`（`cmake.py#L327`）：运行 `cmake --build`，按 generator（Ninja/Make/MSVC）传递参数
   - `install`（`cmake.py#L352`）：运行 `cmake --install` 到 staging 目录，映射到 wheel 布局（platlib/data/headers/scripts/metadata）
   - 构建目录通过 `.skbuild-info.json` 检测 stale cache

3. **`Builder`（高层包装，`src/scikit_build_core/builder/builder.py#L213`）**：被 `build/wheel.py` 使用，封装：
   - `configure`（`builder.py#L257`）：注入 Python 发现变量（`PYTHON_EXECUTABLE`、`Python3_EXECUTABLE`）、Limited API / Stable ABI（`SKBUILD_SOABI`、`SKBUILD_SABI_*`，由 `_SabiMode` 枚举 `builder.py#L64-L67` 控制）、macOS 跨编译（`ARCHFLAGS` → `CMAKE_OSX_ARCHITECTURES`，由 `get_archs` `builder.py#L75` 解析）、entry-point 注入的 CMake 模块路径，然后委托给 `CMaker.configure`
   - `build`（`builder.py#L488`）：委托给 `CMaker.build`
   - `install`（`builder.py#L502`）：委托给 `CMaker.install`

### 程序查找（`program_search.py`）

- `Program` NamedTuple（`src/scikit_build_core/program_search.py#L39-L46` 导出列表）
- `get_cmake_programs` / `get_ninja_programs` / `get_make_programs`：从 PATH 与 PyPI 安装位置枚举候选
- `best_program`：按版本 specifier 选择最佳
- `get_cmake_program`：单路径包装
- `_macos_binary_is_x86`（`program_search.py#L57`）：macOS 上检测二进制架构

### Generator 选择（`builder/generator.py`）

- `parse_generator`（`src/scikit_build_core/builder/generator.py#L39`）：从 CMake args 中提取 `-G` 指定的 generator（同时支持 `-GNinja` 与 `-G Ninja`）
- `set_environment_for_gen`：为 generator 设置环境变量（Ninja 路径等）
- `parse_help_default`（`generator.py#L58`）：解析 `cmake --help` 默认 generator

### 辅助模块

- `builder/sysconfig.py`：`get_python_include_dir`、`get_python_library`、`get_soabi`、`get_platform`、`get_numpy_include_dir`、`get_abi_flags`、`get_cmake_platform`、`info_print`
- `builder/wheel_tag.py`：`WheelTag` 类，`WheelTag.compute_best([])` 计算默认 wheel tag
- `builder/macos.py`：`normalize_macos_version`（处理 macOS 版本字符串与 ARCHFLAGS 跨编译）
- `builder/get_requires.py#L56`：`GetRequires` 类，提供 `cmake()` / `ninja()` / `variants()` / `dynamic_metadata()` 方法，供 PEP 517 `get_requires_for_build_*` 钩子使用
- `builder/_load_provider.py`：`load_provider` / `load_dynamic_metadata` / `process_dynamic_metadata` / `process_legacy_dynamic_metadata` / `dynamic_wheel_fields`，加载动态元数据提供者（含入口点机制）

### 完整调用流程（wheel 构建）

```
build_wheel (build/__init__.py#L45)
  → _build_wheel_impl (build/wheel.py#L215)
    → _build_wheel_impl_impl (build/wheel.py#L310)
      1. SettingsReader.from_file → SettingsReader (settings/skbuild_read_settings.py#L61)
      2. get_standard_metadata (build/metadata.py#L53)
      3. CMake.default_search (cmake.py#L71) → 通过 program_search
      4. Builder.configure (builder/builder.py#L257)
           → 写 file_api.query.stateless_query (file_api/query.py#L19)
           → CMaker.configure (cmake.py#L284) 写 CMakeInit.txt + 运行 cmake -S -B
           → file_api.reply.load_reply_dir (file_api/reply.py#L38) 解析响应
      5. Builder.build (builder/builder.py#L488) → CMaker.build (cmake.py#L327) → cmake --build
      6. Builder.install (builder/builder.py#L502) → CMaker.install (cmake.py#L352) → cmake --install 到 staging
      7. 打包 Python 文件 (build/_pathutil.py、build/_file_processor.py)
      8. WheelWriter (build/_wheelfile.py) 写 .whl + 计算 tag (builder/wheel_tag.py)
```

---

## 其他关键模块

### CMake File API（`file_api/`）

- `query.py#L19` `stateless_query(build_dir)`：在 `build_dir/.cmake/api/v1/query/` 创建 4 个空文件（`codemodel-v2`、`cache-v2`、`cmakeFiles-v1`、`toolchains-v1`），返回 `reply/` 目录路径。CMake configure 时会写入响应。
- `reply.py#L38` `load_reply_dir(reply_dir)`：定位最新 `index-*.json`，通过 `Converter` 类（`reply.py#L50`）解析为 typed dataclass。
- `model/` 6 个数据类（`__init__.py` 为空）：
  - `Index`（`model/index.py`）：file-api 入口索引
  - `CodeModel`、`Target`（`model/codemodel.py`）：项目结构与目标
  - `Cache`（`model/cache.py`）：CMakeCache.txt 解析
  - `CMakeFiles`（`model/cmakefiles.py`）：参与的 CMake 文件
  - `Toolchains`（`model/toolchains.py`）：工具链信息
  - `Directory`（`model/directory.py`）：目录结构
  - `common.py`：共享基类
- `_cattrs_converter.py`：使用 cattrs 的替代转换器
- `__main__.py#L16-L32`：CLI 子命令 `query` / `reply`

### 元数据系统（`build/metadata.py` + `metadata/`）

- `build/metadata.py#L53` `get_standard_metadata(pyproject_dict, settings, build_state)`：
  1. 先处理 legacy `tool.scikit-build.metadata` 表（`process_legacy_dynamic_metadata`）
  2. 再处理新式 `[[tool.dynamic-metadata]]`（`process_dynamic_metadata`，dynamic-metadata 0.3）
  3. 在 SDist 阶段标记 `dynamic_metadata` 字段为 Dynamic（METADATA 2.2）
  4. 调用 vendored `StandardMetadata.from_pyproject`
  5. `minimum_version` 控制 name 归一化、metadata version 等行为
- `metadata/__init__.py`：定义字段分类（`_STR_FIELDS`、`_LIST_STR_FIELDS`、`_DICT_STR_FIELDS`、`_LIST_DICT_FIELDS`、`_SCALAR_FIELDS`、`_EXTENDABLE_FIELDS`），`_process_dynamic_metadata` helper，`_require_field` 用于新式 plugin 分离 `field` 与配置
- 4 个内置 provider（通过 `dynamic_metadata.provider` 入口点注册）：
  - `metadata/regex.py:Provider`：正则替换
  - `metadata/template.py:Provider`：模板填充
  - `metadata/setuptools_scm.py:Provider`：setuptools-scm 版本
  - `metadata/fancy_pypi_readme.py:Provider`：hatch-fancy-pypi-readme 兼容

### 可编辑安装（`build/_editable.py`）

两种模式（由 `editable.mode` 配置）：
- **redirect（默认）**：`editable_redirect`（`build/_editable.py#L48`）读取 `resources/_editable_redirect.py` 模板，生成 `.pth` 文件 + `_editable_skbc_<pkg>.py` shim，使用 `sys.meta_path` 映射 import；若 `editable.rebuild=true`，import 时触发 CMake 重建
- **inplace**：`editable_inplace` 生成简单 `.pth` 指向源码包目录

辅助函数：`get_packages`、`package_search_dirs`、`collect_search_locations`、`mapping_to_modules`、`libdir_to_installed`。

### Init 脚手架（`init/__main__.py`）

- `generate_project`（`src/scikit_build_core/init/__main__.py#L28` 导出，函数定义在后）：交互式生成最小 CMake + scikit-build-core 项目
- `_Backend` 数据类（`init/__main__.py#L35-L41`）：描述后端所需的 requires / dependencies / tool 片段
- `_BACKENDS` 字典（`init/__main__.py#L45-L60+`）：支持 8 种后端模板
  - `pybind11`、`nanobind`、`c`、`cython`（需 cython-cmake）、`swig`、`fortran`（需 numpy + f2py-cmake）、`abi3`（设 `wheel.py-api = "cp38"`）、`abi3t`（自由线程，`wheel.py-api = "cp315.cp315t"`）

### Hatchling 插件（`hatch/`，实验性）

- `hatch/hooks.py#L18` `hatch_register_build_hook`：注册 `ScikitBuildHook`
- `hatch/plugin.py` `ScikitBuildHook`（继承 `BuildHookInterface`）：让 hatchling 驱动 CMake 构建，复用 `Builder`/`CMaker`，但产物回填给 hatchling 而非自组装 wheel
- 入口点 `hatch.scikit-build` → `scikit_build_core.hatch.hooks`（`pyproject.toml#L90`）

### Setuptools 兼容层（`setuptools/`，实验性）

- `setuptools/build_meta.py#L14-L19`：从 `setuptools.build_meta` 重导出 `build_sdist`/`build_wheel`/`prepare_metadata_for_build_wheel`
- `setuptools/build_meta.py#L25-L47`：条件定义 `build_editable`，先 `_validate_editable_settings` 再委托
- `setuptools/build_cmake.py`：实现 distutils `BuildCMake` 命令（`distutils.commands.build_cmake` 入口点），含 `cmake_source_dir`/`cmake_args`/`cmake_install_dir`/`cmake_process_manifest_hook`/`cmake_install_target`/`cmake_with_sdist` 等 setup() 关键字（`pyproject.toml#L82-L87`），并通过 `finalize_distribution_options` 钩子（`pyproject.toml#L88`）注入
- `setuptools/wrapper.py#L25` `setup()`：兼容旧 `scikit-build` 项目的 setup() 包装

### 资源（`resources/`）

- `resources/__init__.py`：导出 `resources`（通过 `_compat.importlib.resources`）
- `resources/_editable_redirect.py`：可编辑安装重定向 shim 模板
- `resources/find_python/`：CMake FindPython 助手模块
- `resources/scikit-build.schema.json`：生成的 JSON Schema（由 `nox -t gen` 从 `skbuild_model.py` 重新生成）

### AST 解析（`ast/`）

- `ast/tokenizer.py`：词法分析
- `ast/ast.py`：语法分析，`ParseError` 异常
- 用于解析 overrides 中的条件表达式（如 `if.env.X`、`if.python-version`）

### 通用工具（`utils/`）

- `utils/typing.py`：`get_target_raw_type`、`is_union_type`、`process_union` 等反射工具，供 settings 反序列化用
- `utils/__init__.py`：空

### build/ 目录辅助文件

| 文件 | 职责 |
|---|---|
| `build/_init.py#L17` | `setup_logging(log_level)`，lru_cache 缓存 |
| `build/generate.py#L20` | `generate_file_contents(gen, metadata)`，从模板生成文件（供 `generate` 配置项） |
| `build/_pathutil.py` | 路径工具：`iter_force_include`、`packages_to_file_mapping`、`resolve_wheel_tree`、`editable_redirectable`、`scantree`、`is_module`、`path_to_module`、`module_loader_rank` 等 |
| `build/_scripts.py` | `process_script_dir`，处理 wheel scripts 目录（shebang 改写等） |
| `build/_wheelfile.py` | `WheelWriter`、`WheelMetadata`，组装 .whl 文件 |
| `build/_file_processor.py` | `each_unignored_file`、`symlink_escapes`，遍历未忽略文件 |
| `build/common_wheel_helpers.py` | `build_wheel`、`configure_wheel`、`get_build_dir`、`get_install_dir`、`get_targetlib`、`get_wheel_tag`、`editable_rebuild_options`、`build_install_extra_build_types`（wheel 与 hatch plugin 共享） |
| `build/metadata.py#L53` | `get_standard_metadata`（见上文） |
| `build/__main__.py` | CLI `build` 子命令：`build requires`（输出 PEP 517 requires）、`build project-table`（输出含动态元数据的 project 表） |

---

## 建议 Wiki 目录结构章节应包含的内容

基于源码研究，目录结构章节应覆盖以下要点：

1. **顶层文件职责表**：13 个 .py 文件 + 类型标记（`py.typed`/`_version.pyi`），逐项一句话职责
2. **子目录职责矩阵**：14 个子目录，标注"核心 / 兼容 / 实验性 / vendored"四类性质
3. **PEP 517 钩子入口表**：8 个钩子函数的 `文件:行号` 锚点与委托链，说明 `_has_safe_metadata` 对 `prepare_metadata_*` 的禁用机制
4. **构建流程调用图**：从 `build_wheel` 到 `_build_wheel_impl_impl` 的 8 步流程（settings→metadata→CMake查找→configure→build→install→打包→写 wheel），含每步对应文件:行号
5. **配置系统四层架构**：
   - 数据模型层：`ScikitBuildSettings` 及 11 个子节的字段表与行号锚点
   - 源链层：`EnvSource`/`ConfSource`/`TOMLSource`/`SourceChain` 的优先级与合并语义
   - 编排层：`SettingsReader` 的处理步骤（含 overrides、auto-cmake-version、auto-requires、entry-point providers）
   - Schema 层：`generate_skbuild_schema` 生成机制与 `nox -t gen` 工作流
6. **条件覆盖（overrides）**：12 种 `if` 选择器、`inherit` 三模式、`override-only` 字段约束、`failed` 重试机制
7. **CMake 集成三层抽象**：`CMake`（值对象）→ `CMaker`（进程调用）→ `Builder`（高层包装），含各方法的文件:行号
8. **CMake File API 工作流**：`stateless_query` 写 4 个 query 文件 → CMake configure 写 reply → `load_reply_dir` 解析为 6 个 typed dataclass
9. **元数据插件机制**：legacy `tool.scikit-build.metadata` 与新式 `[[tool.dynamic-metadata]]` 两种形式，4 个内置 provider，PEP 808 extendable 字段规则
10. **可编辑安装两种模式**：redirect（默认，含 rebuild-on-import）vs inplace，含 `.pth` + shim 工作原理
11. **后端适配层**：hatchling（`ScikitBuildHook`）与 setuptools（`BuildCMake` 命令 + `build_meta` 包装 + `setup()` wrapper），均标注实验性
12. **Init 脚手架**：8 种后端模板（pybind11/nanobind/c/cython/swig/fortran/abi3/abi3t）及各自依赖
13. **CLI 子命令树**：`scikit-build` 4 个子命令的完整功能列表
14. **兼容性与 vendored**：`_compat/` 5 个垫片（Ruff 强制使用，禁止直接 import）、`_vendor/pyproject_metadata`（禁止 lint/手改）
15. **实验性特性**：PEP 817 variants（`variant`/`variant_name`/`variant_label`/`null_variant`，override-only）
16. **生成文件清单**：`resources/scikit-build.schema.json`、`README.md` cog 段、`docs/reference/configs.md` cog 段，统一由 `nox -t gen` 重新生成

章节建议配图：
- 模块依赖关系图（顶层 → 子目录）
- PEP 517 钩子调用时序图
- 配置源链合并示意图
- CMake 集成三层调用图
- File API query/reply 时序图
- 可编辑安装两种模式对比图
