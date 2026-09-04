---
name: conda-source-facts
version: 1.0.0
created: 2026-08-21
source: external/libs/conda-dev/conda/conda/
---

# Conda 源码事实清单

> 本文件记录从 conda 源码中提取的纯客观事实，不含因果推断。共80条。

## 一、包入口与元数据（__init__.py / __main__.py / pyproject.toml）

**F-001**: `conda/__init__.py` 定义 `__version__`，通过三级回退获取：`._version`（pip install后生成）→ `setuptools_scm.get_version()` → `"0.0.0.dev0+placeholder"`。来源：`conda/__init__.py` L19-L33

**F-002**: `__all__` 导出 `CondaError`, `CondaMultiError`, `CondaExitZero`, `conda_signal_handler`, `CONDA_PACKAGE_ROOT` 等核心符号。来源：`conda/__init__.py` L35-L49

**F-003**: 环境变量 `CONDA_ROOT` 未设置时默认设为 `sys.prefix`。来源：`conda/__init__.py` L59-L60

**F-004**: `CONDA_PACKAGE_ROOT = abspath(dirname(__file__))`，`CONDA_SOURCE_ROOT = dirname(CONDA_PACKAGE_ROOT)`。来源：`conda/__init__.py` L62-L65

**F-005**: `CondaError` 基类有 `return_code: int = 1`、`reportable: bool = False` 属性；构造参数 `message, *args, caused_by=None, guidance=None, **kwargs`。来源：`conda/__init__.py` L73-L124

**F-006**: `CondaError.__str__()` 使用 `self.message % self._kwargs` 做printf风格格式化。来源：`conda/__init__.py` L139-L156

**F-007**: `CondaMultiError` 接收 `errors: Iterable[CondaError]`，`__str__` 用换行连接各error。来源：`conda/__init__.py` L173-L210

**F-008**: `CondaExitZero` 的 `return_code = 0`。来源：`conda/__init__.py` L213-L214

**F-009**: `conda_signal_handler(signum, frame)` 遍历 `ACTIVE_SUBPROCESSES` 集合发送信号，然后抛出 `CondaSignalInterrupt`。来源：`conda/__init__.py` L220-L230

**F-010**: `conda/__main__.py` 导入 `from .cli import main` 并 `sys.exit(main())`。来源：`conda/__main__.py` L1-L9

**F-011**: `pyproject.toml` 声明 `build-backend = "hatchling.build"`，`requires-python = ">=3.10"`，支持Python 3.10-3.14和PyPy。来源：`pyproject.toml` L1-L22

**F-012**: CLI入口点 `conda = "conda.cli.main_pip:main"`。来源：`pyproject.toml` L54-L55

**F-013**: 核心依赖包括：archspec, boltons, charset-normalizer, conda-package-handling, distro, frozendict, menuinst, msgpack, packaging, platformdirs, pluggy, pycosat, requests, ruamel.yaml, setuptools, tqdm, truststore。来源：`pyproject.toml` L24-L45

**F-014**: 版本管理使用hatch-vcs，`version-file = "conda/_version.py"`。来源：`pyproject.toml` L105-L112

## 二、CLI入口与命令分发（cli/main.py / cli/conda_argparse.py）

**F-015**: `cli/main.py` 有三个入口函数：`main(*args, **kwargs)`（顶层）、`main_subshell(*args, post_parse_hook=None, **kwargs)`（子shell命令）、`main_sourced(shell, *args, **kwargs)`（shell激活命令）。来源：`conda/cli/main.py` L19-L112

**F-016**: `main()` 中如果 `args[0]` 以 `"shell."` 开头则走 `main_sourced`，否则走 `main_subshell`；`-V`/`--version` 快速路径直接输出版本号。来源：`conda/cli/main.py` L91-L112

**F-017**: `main_subshell()` 执行流程：generate_pre_parser → parse_known_args → context.__init__(argparse_args=pre_args) → 禁用外部插件(若no_plugins) → generate_parser → parse_args → context.__init__(argparse_args=args) → init_loggers() → do_call(args, parser)。来源：`conda/cli/main.py` L19-L57

**F-018**: `main_sourced()` 调用 `activate._build_activator_cls(shell)` 获取激活器类，实例化后 `execute()` 输出shell脚本。来源：`conda/cli/main.py` L60-L88

**F-019**: `BUILTIN_COMMANDS` 集合包含24个内置命令名：activate, clean, commands, compare, config, create, deactivate, env, export, info, init, install, list, notices, package, remove, rename, run, search, uninstall, update, upgrade。来源：`conda/cli/conda_argparse.py` L74-L97

**F-020**: `conda_argparse.py` 为每个命令导入对应的 `configure_parser` 函数（configure_parser_clean/install/create等共20个）。来源：`conda/cli/conda_argparse.py` L48-L67

**F-021**: 日志初始化 `init_loggers()` 调用 `initialize_logging()` 和 `set_log_level(context.log_level)`。来源：`conda/cli/main.py` L8-L16

## 三、全局上下文与配置（base/context.py / common/configuration.py / base/constants.py）

**F-022**: `base/context.py` 的 `context` 是一个全局单例对象，聚合所有配置文件、环境变量和命令行参数。来源：`conda/base/context.py` L3-L7

**F-023**: `context` 使用 `frozendict` 做不可变配置，`cached_property`/`memoizedproperty` 做缓存。来源：`conda/base/context.py` L20-L27

**F-024**: 配置搜索路径包括：用户级 `~/.condarc`（`user_rc_path`）、系统级 `sys.prefix/.condarc`（`sys_rc_path`）。来源：`conda/base/context.py` L135-L136

**F-025**: 平台映射 `_platform_map`：freebsd13→freebsd, linux2/linux→linux, darwin→osx, win32→win, zos→zos。来源：`conda/base/context.py` L107-L114

**F-026**: `common/configuration.py` 提供通用配置框架：`Configuration` 类、`ParameterLoader`、`PrimitiveParameter`、`SequenceParameter`、`MapParameter`、`YamlRawParameter`。来源：`conda/common/configuration.py` L36-L46

**F-027**: 配置错误类层次：`ConfigurationError` → `ConfigurationLoadError`, `ValidationError` → `MultipleKeysError`。来源：`conda/common/configuration.py` L93-L119

**F-028**: `base/constants.py` 定义关键常量：`APP_NAME = "conda"`、`DEFAULT_CHANNELS`（Unix/Windows不同）、`REPODATA_FN = "repodata.json"`、`PREFIX_MAGIC_FILE = "conda-meta/history"`、`ChannelPriority`/`DepsModifier`/`UpdateModifier`/`SafetyChecks`/`SatSolverChoice`/`PathConflict` 枚举。来源：`conda/base/constants.py`

**F-029**: `KNOWN_SUBDIRS` 列出所有已知平台子目录；`DEFAULT_SOLVER = "classic"`；`ROOT_ENV_NAME = "base"`；`DEFAULTS_CHANNEL_NAME = "defaults"`。来源：`conda/base/constants.py`

## 四、数据模型层（models/）

**F-030**: `models/channel.py` 定义 `Channel` 类，URL分解为：scheme <> auth <> location <> token <> channel <> subchannel <> platform <> package_filename。来源：`conda/models/channel.py` L53-L61

**F-031**: `Channel.__new__()` 使用缓存模式：单参数且为Channel实例直接返回；单str参数走 `from_value()` 缓存；含 `channels` kwarg 返回 `MultiChannel`。来源：`conda/models/channel.py` L67-L76

**F-032**: `Channel` 属性：scheme, auth, location, token, name, platform(subdir), package_filename。来源：`conda/models/channel.py` L78-L96

**F-033**: `from_value(value)` 使用 `@cache` 装饰器做字符串到Channel的缓存。来源：`conda/models/channel.py` L118-L120

**F-034**: `models/match_spec.py` 实现包查询语言 MatchSpec，支持 `name[version='>=3.6',build=py37_0]` 方括号语法。来源：`conda/models/match_spec.py` L3-L7

**F-035**: MatchSpec 使用多个正则解析：`_BRACKETS_RE`/`_BRACKETS_KV_RE`/`_BRACKETS_RE_V3`/`_BRACKETS_KV_RE_V3`/`_NAME_VERSION_RE`/`_VERSION_BUILD_RE`/`_CEP26_NAME_RE`。来源：`conda/models/match_spec.py` L52-L120

**F-036**: `models/version.py` 定义 `VersionOrder` 类（metaclass=`SingleStrArgCachingType`），实现版本字符串的解析和比较。来源：`conda/models/version.py` L38-L52

**F-037**: 版本解析规则：按 `!` 分割epoch和version，按 `+` 分割local version，按 `.`/`_` 分割组件，每个组件按数字/非数字runs分割，数字转int，字符串转小写，dev/post特殊处理。来源：`conda/models/version.py` L88-L99

**F-038**: `VersionSpec` 类实现版本约束匹配（>,<,=,>=,<=,==,!=等）；`BuildNumberMatch` 处理build number匹配。来源：`conda/models/version.py`

**F-039**: `models/records.py` 定义三级记录继承链：`PackageRecord`（通道中的包）→ `PackageCacheRecord`（已下载缓存的包）→ `PrefixRecord`（已安装到环境的包）。来源：`conda/models/records.py` L3-L14

**F-040**: 记录使用 `auxlib.entity` 的 `Entity` 系统：`StringField`, `IntegerField`, `BooleanField`, `ListField`, `EnumField`, `NumberField`, `ComposableField` 等字段类型。来源：`conda/models/records.py` L23-L33

**F-041**: `Link` 实体包含 source（StringField）和 type（LinkTypeField，支持hardlink/softlink/copy）。来源：`conda/models/records.py` L98-L100

**F-042**: `models/enums.py` 定义枚举：`LinkType`（hardlink/softlink/copy/directory）、`NoarchType`（python/generic）、`PackageType`（conda/virtual_generic/virtual_system/...）、`FileMode`、`PathEnum`、`Platform`。来源：`conda/models/enums.py`

**F-043**: `models/prefix_graph.py` 实现 `PrefixGraph`，用于已安装包的依赖图拓扑排序。来源：`conda/models/prefix_graph.py`

## 五、核心业务逻辑（core/）

**F-044**: `core/solve.py` 定义 `BaseSolver` 类，三个公开方法：`solve_final_state()`、`solve_for_diff()`、`solve_for_transaction()`。来源：`conda/core/solve.py` L58-L66

**F-045**: `BaseSolver.__init__()` 接收 prefix, channels, subdirs, specs_to_add, specs_to_remove, repodata_fn, command 参数。来源：`conda/core/solve.py` L71-L100

**F-046**: `core/subdir_data.py` 定义 `SubdirData` 类（metaclass=`SubdirDataType`），管理单个subdir的repodata.json，有缓存机制。来源：`conda/core/subdir_data.py` L52-L88

**F-047**: `SubdirData` 缓存key为 `(channel.url(with_credentials=True), repodata_fn)`，file:// URL检查mtime决定是否使用缓存。来源：`conda/core/subdir_data.py` L71-L81

**F-048**: `REPODATA_PICKLE_VERSION = 30`，`MAX_REPODATA_VERSION = 2`。来源：`conda/core/subdir_data.py` L47-L48

**F-049**: `PackageRecordList(UserList)` 实现懒加载：dicts到PackageRecord的延迟转换。来源：`conda/core/subdir_data.py` L90-L100

**F-050**: `core/index.py` 的 `Index(UserDict)` 聚合四类包信息源：Channels（远端通道包→PackageRecord）、Prefix（已安装包→PrefixRecord）、Package Cache（本地缓存包→PackageCacheRecord）、Virtual Packages（虚拟包→特殊PackageRecord）。来源：`conda/core/index.py` L38-L75

**F-051**: `core/link.py` 实现包安装/卸载的事务机制：`UnlinkLinkTransaction` 和 `PrefixSetup`。来源：`conda/core/link.py` L3-L4

**F-052**: `determine_link_type()` 函数决定链接类型：always_copy→copy, always_softlink→softlink, 否则按hardlink→softlink→copy顺序检测。来源：`conda/core/link.py` L94-L100

**F-053**: 链接操作使用 `path_actions` 模块中的Action类：`LinkPathAction`, `UnlinkPathAction`, `CompileMultiPycAction`, `CreatePythonEntryPointAction`, `MakeMenuAction` 等。来源：`conda/core/link.py` L68-L81

**F-054**: `core/package_cache_data.py` 管理包缓存（pkgs_dirs），提供 `query()`, `first_writable()`, `is_writable` 等方法。来源：`conda/core/package_cache_data.py`

**F-055**: `core/prefix_data.py` 管理环境前缀（prefix）中的已安装包记录，读取 `conda-meta/` 目录下的JSON文件。来源：`conda/core/prefix_data.py`

**F-056**: `core/envs_manager.py` 管理已知环境列表，注册/注销环境位置。来源：`conda/core/envs_manager.py`

## 六、SAT求解器（resolve.py / common/logic.py）

**F-057**: `resolve.py` 是经典求解器的底层SAT封装，`Resolve` 类管理子句（Clauses）和包的SAT变量映射。来源：`conda/resolve.py` L3-L6

**F-058**: 支持三种SAT求解器后端：`PycoSatSolver`（默认）、`PyCryptoSatSolver`、`PySatSolver`，通过 `_sat_solvers` 字典注册。来源：`conda/resolve.py` L65-L69

**F-059**: `_get_sat_solver_cls()` 使用 `@cache` 装饰器，按优先级尝试求解器，先做简单的SAT冒烟测试。来源：`conda/resolve.py` L72-L100

**F-060**: `common/logic.py` 的 `Clauses` 类封装SAT子句管理，核心方法 `add_clause()`, `Require()`, `Prevent()`, `And()`, `Or()`, `Not()`, `sat()`。来源：`conda/common/logic.py` L48-L79

**F-061**: Clauses通过Tseitin转换添加新变量来嵌套逻辑表达式，避免分发导致的指数膨胀。来源：`conda/common/logic.py` L4-L27

**F-062**: `common/logic.py` 从 `._logic` C扩展导入 `Clauses as _Clauses` 和 `TRUE`/`FALSE` 常量。来源：`conda/common/logic.py` L32-L33

**F-063**: `common/toposort.py` 提供拓扑排序功能，用于包依赖排序。来源：`conda/common/toposort.py`

## 七、高层API（api.py）

**F-064**: `conda/api.py` 提供四个高层API类：`Solver`、`SubdirData`、`PackageCacheData`、`PrefixData`，均采用 `_internal` 委托模式（公开类包装内部实现类）。来源：`conda/api.py` L21-L501

**F-065**: `Solver.__init__()` 通过 `context.plugin_manager.get_cached_solver_backend()` 获取求解器后端。来源：`conda/api.py` L54-L57

**F-066**: `SubdirData.query_all()` 静态方法查询所有通道/子目录矩阵中的repodata。来源：`conda/api.py` L232-L255

**F-067**: 每个API类都有 `reload()` 方法用于强制刷新数据。来源：`conda/api.py` L268-L281, L396-L409, L488-L501

## 八、插件系统（plugins/）

**F-068**: `plugins/manager.py` 的 `CondaPluginManager` 继承自 `pluggy.PluginManager`，使用 `importlib.metadata.distributions()` 发现已安装插件。来源：`conda/plugins/manager.py` L11-L26

**F-069**: `plugins/hookspec.py` 使用 `pluggy.HookspecMarker(APP_NAME)` 定义 `_hookspec` 和 `hookimpl` 装饰器；`CondaSpecs` 类定义所有hookspec。来源：`conda/plugins/hookspec.py` L47-L55

**F-070**: 内置插件钩子类型：`conda_solvers`, `conda_subcommands`, `conda_virtual_packages`, `conda_reporter_backends`, `conda_post_commands`, `conda_pre_commands`, `conda_auth_handlers`, `conda_settings`, `conda_health_checks`, `conda_error_hints`, `conda_post_solves`, `conda_pre_solves`, `conda_package_extractors`, `conda_prefix_data_loaders`, `conda_environment_specifiers`, `conda_environment_exporters`, `conda_pre_transaction_actions`, `conda_post_transaction_actions`, `conda_exception_observers`, `conda_request_headers`。来源：`conda/plugins/hookspec.py`; `conda/plugins/`

**F-071**: 内置插件实现在 `plugins/` 子目录：`solvers/`（classic求解器）、`subcommands/`（doctor/plugins/config等子命令）、`virtual_packages/`（archspec/cuda/conda/linux/osx/windows/freebsd虚拟包）、`reporter_backends/`（console/json）、`environment_exporters/`、`environment_specifiers/`、`package_extractors/`、`prefix_data_loaders/`、`post_solves/`、`previews/`。来源：`conda/plugins/`

**F-072**: `plugins/config.py` 提供 `PluginConfig` 类管理插件配置。来源：`conda/plugins/config.py`

**F-073**: `plugins/previews.py` 管理预览功能（feature flags）。来源：`conda/plugins/previews.py`

## 九、网关层（gateways/）

**F-074**: `gateways/connection/session.py` 的 `CondaSession` 配置五种协议适配器：HTTPAdapter（http/https）、FTPAdapter（ftp）、LocalFSAdapter（file）、S3Adapter（s3）。来源：`conda/gateways/connection/session.py` L37-L40, L49-L57

**F-075**: `CondaSession` 有 `FORBIDDEN_HEADERS` 集合，禁止插件设置20个HTTP禁止头。来源：`conda/gateways/connection/session.py` L64-L80

**F-076**: `gateways/disk/` 子模块包含 create/delete/read/update/link/lock/permissions/test 等磁盘操作模块。来源：`conda/gateways/disk/`

**F-077**: `gateways/connection/download.py` 实现并行下载，`gateways/repodata/` 管理repodata缓存（`CACHE_STATE_SUFFIX`, `RepodataFetch`, `RepodataState`, `cache_fn_url`）。来源：`conda/gateways/connection/download.py`; `conda/gateways/repodata/`

**F-078**: `gateways/subprocess.py` 封装子进程调用。来源：`conda/gateways/subprocess.py`

## 十、环境与激活（activate.py / env/ / history.py）

**F-079**: `activate.py` 的 `_Activator` 抽象基类（metaclass=ABCMeta）处理三个任务：①设置/取消环境变量 ②执行activate.d/deactivate.d脚本 ③更新PATH和提示符。来源：`conda/activate.py` L77-L80

**F-080**: `activate.py` 的 `BUILTIN_COMMANDS` 字典包含 activate, deactivate, hook, commands, reactivate 五个内置shell命令。来源：`conda/activate.py` L68-L74
