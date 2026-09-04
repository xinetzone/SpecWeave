# scrapli2 源码事实清单

> 基于 `external/libs/scrapli/scrapli/` 逐模块阅读提取。版本 0.0.0-dev，libscrapli 版本 0.0.1-rc.35。
> 所有事实均可通过源码行号溯源。禁止推断词，只记录代码中客观存在的内容。

## 包元数据与公开 API

- F-001: `__init__.py` 导出 `Cli`、`Netconf`、`AuthOptions`、`SessionOptions`、`TransportBinOptions`、`TransportSsh2Options`、`TransportTelnetOptions`、`TransportTestOptions`、`LookupKeyValue`、`ReadCallback`、`NetconfOptions`（`__all__` 元组，第21-33行）。
- F-002: `__version__ = "0.0.0"`，`__semver_version__ = "0.0.0"`，`__calendar_version__ = "0.0.0"`，`__definitions_version__ = "0.0.5"`（`__init__.py` 第15-19行）。
- F-003: `AuthOptions` 是 `scrapli.auth.Options` 的别名（`from scrapli.auth import Options as AuthOptions`，`__init__.py` 第4行）。
- F-004: `SessionOptions` 是 `scrapli.session.Options` 的别名（`__init__.py` 第8行）。
- F-005: `TransportBinOptions` 是 `scrapli.transport.BinOptions` 的别名（`__init__.py` 第9行）。
- F-006: `TransportSsh2Options` 是 `scrapli.transport.Ssh2Options` 的别名（`__init__.py` 第10行）。
- F-007: `TransportTelnetOptions` 是 `scrapli.transport.TelnetOptions` 的别名（`__init__.py` 第11行）。
- F-008: `TransportTestOptions` 是 `scrapli.transport.TestOptions` 的别名（`__init__.py` 第12行）。
- F-009: `NetconfOptions` 是 `scrapli.netconf.Options` 的别名（`__init__.py` 第7行）。
- F-010: 本版本不存在旧版 scrapli 的 `Scrapli`、`AsyncScrapli`、`NetworkDriver`、`Driver`、`Channel` 等类（经全目录 Grep 确认，`__all__` 中无这些名称）。

## Cli 类

- F-011: `Cli.__init__` 签名为 `(self, host: str, *, port: int | None = None, definition_file_or_name: str | LoadedDefinition | None = None, cli_options: Options | None = None, auth_options: AuthOptions | None = None, session_options: SessionOptions | None = None, transport_options: TransportOptions | None = None, logging_uid: str | None = None, skip_static_options: bool = False)`（`cli.py` 第275-287行）。
- F-012: `Cli` 默认端口：telnet 时为 23，否则为 22（`cli.py` 第311行：`self.port = 23 if isinstance(transport_options, TransportTelnetOptions) else 22`）。
- F-013: `Cli` 默认 `transport_options` 为 `TransportBinOptions()`（`cli.py` 第316行）。
- F-014: `Cli` 支持同步上下文管理器 `__enter__`/`__exit__` 和异步上下文管理器 `__aenter__`/`__aexit__`（`cli.py` 第349-429行）。
- F-015: `Cli.__str__` 返回 `f"scrapli.Cli {self.host}:{self.port}"`（`cli.py` 第445行）。
- F-016: `Cli.open()` 被 `@handle_operation_timeout` 装饰，接受 `operation_timeout_ns` 和 `cancel` 参数，返回 `Result`（`cli.py` 第716-747行）。
- F-017: `Cli.open_async()` 被 `@handle_operation_timeout_async` 装饰，签名与 `open()` 一致（`cli.py` 第749-780行）。
- F-018: `Cli.close()` 接受 `force: bool = False`、`operation_timeout_ns`、`cancel`，返回 `Result`，关闭后调用 `self._free()`（`cli.py` 第796-835行）。
- F-019: `Cli.close_async()` 为异步版本（`cli.py` 第837-876行）。
- F-020: `Cli.send_input(input_: str, *, requested_mode: str = "", input_handling: InputHandling = InputHandling.FUZZY, retain_input: bool = False, retain_trailing_prompt: bool = False, operation_timeout_ns=None, cancel=None) -> Result`（`cli.py` 第1317-1370行）。
- F-021: `Cli.send_input_async()` 为 `send_input` 的异步版本（`cli.py` 第1372-1426行）。
- F-022: `Cli.send_inputs(inputs: list[str], *, ..., stop_on_indicated_failure: bool = True, ...) -> Result`（`cli.py` 第1429-1495行）。
- F-023: `Cli.send_inputs_async()` 为异步版本（`cli.py` 第1497-1566行）。
- F-024: `Cli.send_inputs_from_file(f: str, *, ...) -> Result` 读取文件后按行分割调用 `send_inputs`（`cli.py` 第1568-1613行）。
- F-025: `Cli.send_inputs_from_file_async()` 为异步版本（`cli.py` 第1615-1660行）。
- F-026: `Cli.send_prompted_input(input_: str, prompt: str, prompt_pattern: str, response: str, *, abort_input: str = "", hidden_response: bool = False, ...) -> Result`（`cli.py` 第1663-1733行）。
- F-027: `Cli.send_prompted_input_async()` 为异步版本（`cli.py` 第1735-1806行）。
- F-028: `Cli.read(size: int = 1_024) -> bytes` 直接从 session 读取字节，绕过操作循环，无异步版本（`cli.py` 第878-905行）。
- F-029: `Cli.write(input_: str)` 写入输入不发送回车（`cli.py` 第907-930行）。
- F-030: `Cli.write_and_return(input_: str)` 写入输入并发送回车（`cli.py` 第932-955行）。
- F-031: `Cli.write_return()` 仅发送回车字符（`cli.py` 第957-974行）。
- F-032: `Cli.enter_mode(requested_mode: str, ...) -> Result` 进入指定模式（`cli.py` 第1155-1195行），存在异步版本。
- F-033: `Cli.get_prompt(...) -> Result` 获取当前提示符（`cli.py` 第1241-1276行），存在异步版本。
- F-034: `Cli.read_with_callbacks(callbacks: list[ReadCallback], *, initial_input: str = "", ...) -> Result`（`cli.py` 第1808-1919行），存在异步版本，异步版须设置 `callback_async` 而非 `callback`。
- F-035: `Cli.replace_definition(definition_file_or_name: str)` 运行时替换平台定义（`cli.py` 第2038-2060行）。
- F-036: `Cli.ntc_templates_platform` 属性从 Zig 层获取 ntc-templates 平台名（`cli.py` 第616-645行）。
- F-037: `Cli.genie_platform` 属性从 Zig 层获取 genie 平台名（`cli.py` 第647-674行）。
- F-038: `Cli` 内部持有 `self.ptr: DriverPointer | None`（Zig 对象指针）和 `self.poll_fd: int`（轮询文件描述符）（`cli.py` 第318-319行）。
- F-039: `Cli._get_options()` 返回 JSON 字符串形式的选项配置（`cli.py` 第568-614行）。

## LoadedDefinition、InputHandling、ReadCallback、Cli Options

- F-040: `LoadedDefinition` 是 dataclass，字段为 `platform_name: str` 和 `definition: str`（`cli.py` 第63-85行）。
- F-041: `InputHandling` 是 `str, Enum`，值为 `EXACT = "exact"`、`FUZZY = "fuzzy"`、`IGNORE = "ignore"`（`cli.py` 第88-116行）。
- F-042: `ReadCallback` 是 dataclass，字段包括 `name`、`contains`、`contains_pattern`、`not_contains`、`search_depth`、`once`、`completes`、`callback`、`callback_async`（`cli.py` 第119-188行）。
- F-043: `ReadCallback.__post_init__` 要求 `contains` 或 `contains_pattern` 至少设置一个，且 `callback` 或 `callback_async` 至少设置一个，否则抛 `OperationException`（`cli.py` 第158-163行）。
- F-044: `cli.Options`（CliOptions）是 dataclass，字段为 `normalize_line_feeds: bool | None` 和 `normalize_trailing_whitespace: bool | None`（`cli.py` 第191-257行）。

## Netconf 类

- F-045: `Netconf.__init__` 签名为 `(self, host: str, *, port: int = 830, options: Options | None = None, auth_options=None, session_options=None, transport_options=None, logging_uid=None)`（`netconf.py` 第454-464行）。
- F-046: `Netconf` 默认端口为 830（NETCONF 标准端口）（`netconf.py` 第458行）。
- F-047: `Netconf` 支持同步/异步上下文管理器（`netconf.py` 第490-574行）。
- F-048: `Netconf` 有 `open()`/`open_async()`/`close()`/`close_async()` 方法，签名与 Cli 对应方法类似（`netconf.py` 第747-907行）。
- F-049: `Netconf.session_id` 属性从 Zig 层获取会话 ID（`netconf.py` 第1065-1091行）。
- F-050: `Netconf.raw_rpc(payload: str, *, base_namespace_prefix: str = "", extra_namespaces: list[tuple[str, str]] | None = None, ...) -> Result`（`netconf.py` 第1196-1259行），存在异步版本。
- F-051: `Netconf.get_config(*, source: DatastoreType = DatastoreType.RUNNING, filter_: str = "", filter_type: FilterType = FilterType.SUBTREE, ...) -> Result`（`netconf.py` 第1327-1384行），存在异步版本。
- F-052: `Netconf.edit_config(*, config: str = "", target: DatastoreType = DatastoreType.RUNNING, default_operation=DefaultOperation.UNSET, test_option=TestOption.UNSET, error_option=ErrorOption.UNSET, ...) -> Result`（`netconf.py` 第1447-1499行），存在异步版本。
- F-053: `Netconf.copy_config(*, target=DatastoreType.RUNNING, source=DatastoreType.STARTUP, ...) -> Result`（`netconf.py` 第1557-1598行），存在异步版本。
- F-054: `Netconf.delete_config(*, target=DatastoreType.RUNNING, ...) -> Result`（`netconf.py` 第1645-1683行），存在异步版本。
- F-055: `Netconf.lock(*, target=DatastoreType.RUNNING, ...) -> Result` 和 `unlock()`（`netconf.py` 第1727-1806行），均存在异步版本。
- F-056: `Netconf.get(*, filter_="", filter_type=FilterType.SUBTREE, ...) -> Result`（`netconf.py` 第1891-1945行），存在异步版本。
- F-057: `Netconf.close_session()` 和 `kill_session(session_id: int)`（`netconf.py` 第2005-2119行），均存在异步版本。
- F-058: `Netconf.commit()`、`discard()`、`cancel_commit(*, persist_id: str | None = None)`、`validate(*, source=DatastoreType.RUNNING)`（`netconf.py` 第2163-2439行），均存在异步版本。
- F-059: `Netconf.get_schema(identifier: str, *, version: str = "", format_: SchemaFormat = SchemaFormat.YANG, ...) -> Result`（`netconf.py` 第2483-2530行），存在异步版本。
- F-060: `Netconf.get_data(...)` 支持 `config_filter`、`origin_filters`、`max_depth`、`with_origin` 等参数（`netconf.py` 第2583-2653行），存在异步版本。
- F-061: `Netconf.edit_data(content: str, *, target=DatastoreType.RUNNING, ...) -> Result`（`netconf.py` 第2729-2775行），存在异步版本。
- F-062: `Netconf.action(action: str, ...) -> Result`（`netconf.py` 第2827-2867行），存在异步版本。
- F-063: `Netconf.get_subscription_id(payload: str) -> int` 从 rpc-reply 中提取订阅 ID（`netconf.py` 第1093-1115行）。
- F-064: `Netconf.get_next_notification() -> str` 获取下一个通知，无通知时抛 `NoMessagesException`（`netconf.py` 第1117-1152行）。
- F-065: `Netconf.get_next_subscription(subscription_id: int) -> str` 获取指定订阅的下一条消息（`netconf.py` 第1154-1194行）。

## Netconf 枚举与 Options

- F-066: `Version` 枚举值为 `VERSION_1_0 = "1.0"`、`VERSION_1_1 = "1.1"`（`netconf.py` 第58-74行）。
- F-067: `DatastoreType` 枚举值为 `CONVENTIONAL`、`RUNNING`、`CANDIDATE`、`STARTUP`、`INTENDED`、`DYNAMIC`、`OPERATIONAL`（`netconf.py` 第77-117行）。
- F-068: `FilterType` 枚举值为 `SUBTREE = "subtree"`、`XPATH = "xpath"`（`netconf.py` 第120-145行）。
- F-069: `DefaultsType` 枚举值为 `REPORT_ALL`、`REPORT_ALL_TAGGED`、`TRIM`、`EXPLICIT`、`UNSET`（`netconf.py` 第148-180行）。
- F-070: `SchemaFormat` 枚举值为 `XSD`、`YANG`、`YIN`、`RNG`、`RNC`（`netconf.py` 第183-217行）。
- F-071: `ConfigFilter` 枚举值为 `TRUE`、`FALSE`、`UNSET`（`netconf.py` 第220-246行）。
- F-072: `DefaultOperation` 枚举值为 `MERGE`、`REPLACE`、`NONE`、`UNSET`（`netconf.py` 第249-278行）。
- F-073: `TestOption` 枚举值为 `TEST_THEN_SET`、`SET`、`UNSET`（`netconf.py` 第281-307行）。
- F-074: `ErrorOption` 枚举值为 `STOP_ON_ERROR`、`CONTINUE_ON_ERROR`、`ROLLBACK_ON_ERROR`、`UNSET`（`netconf.py` 第310-339行）。
- F-075: `netconf.Options`（NetconfOptions）dataclass 字段为 `error_tag`、`preferred_version`、`message_poll_interval_ns`、`capabilities_callback`、`close_force: bool = False`（`netconf.py` 第342-436行）。

## Transport 层

- F-076: `TransportKind` 枚举值为 `BIN = "bin"`、`TELNET = "telnet"`、`SSH2 = "ssh2"`、`TEST = "test_"`（`transport.py` 第12-43行）。
- F-077: `TransportKind._to_ffi()` 将 BIN→0、TELNET→1、SSH2→2、TEST→3 映射为 `c_uint8`（`transport.py` 第32-43行）。
- F-078: `BinOptions` dataclass 字段：`bin`、`extra_open_args: list[str]`、`override_open_args: list[str]`、`ssh_config_path`、`known_hosts_path`、`enable_strict_key: bool`、`term_height: int`、`term_width: int`（`transport.py` 第111-213行）。
- F-079: `Ssh2Options` dataclass 字段：`known_hosts_path`、`libssh2_trace: bool`、`proxy_jump_host`、`proxy_jump_port`、`proxy_jump_username`、`proxy_jump_password`、`proxy_jump_private_key_path`、`proxy_jump_private_key_passphrase`、`proxy_jump_libssh2_trace: bool`（`transport.py` 第216-346行）。
- F-080: `Ssh2Options` 中 `proxy_jump_host` 为 None 时，其余 proxy_jump 字段均不应用（`transport.py` 第293-298行）。
- F-081: `TelnetOptions` dataclass 无额外字段，`apply` 方法为空操作（`transport.py` 第349-382行）。
- F-082: `TestOptions` dataclass 仅有 `f: str | None = None` 字段（测试传输读取文件）（`transport.py` 第384-424行）。
- F-083: `Options`（transport 基类）是 ABC，定义 `transport_kind` 属性和抽象方法 `apply`（`transport.py` 第46-108行）。

## Auth 层

- F-084: `LookupKeyValue` dataclass 字段为 `key: str`、`value: str`，`__repr__` 中 value 显示为 `'REDACTED'`（`auth.py` 第10-43行）。
- F-085: `auth.Options`（AuthOptions）dataclass 字段：`username`、`password`、`private_key_path`、`private_key_passphrase`、`private_key_content`、`lookups: list[LookupKeyValue]`、`force_in_session_auth: bool`、`bypass_in_session_auth: bool`、`username_pattern`、`password_pattern`、`private_key_passphrase_pattern`（`auth.py` 第46-237行）。
- F-086: `AuthOptions` 的 `__repr__` 将 `password`、`private_key_passphrase`、`private_key_content` 显示为 `REDACTED`（`auth.py` 第222-236行）。
- F-087: `private_key_content` 仅支持 ssh2 transport（文档字符串说明，`auth.py` 第59行）。

## Session 层

- F-088: `DEFAULT_OPERATION_TIMEOUT_NS = 10_000_000_000`（10秒）（`session.py` 第11行）。
- F-089: `session.Options`（SessionOptions）dataclass 字段：`read_size`、`read_min_delay_ns`、`read_max_delay_ns`、`return_char`、`operation_timeout_s`、`operation_timeout_ns`、`operation_max_search_depth`、`scratch_initial_size`、`scratch_retain_max`、`recorder_path`、`recorder_callback`（`session.py` 第14-139行）。
- F-090: `SessionOptions.__post_init__` 在设置了 `operation_timeout_s` 但未设 `operation_timeout_ns` 时，自动将秒转换为纳秒（`session.py` 第51-54行）。

## Result 对象

- F-091: CLI `Result` 类构造参数为 `host`、`port`、`inputs: bytes`、`input_lens: list[int]`、`start_time: int`、`splits: list[int]`、`result_raw_journals: bytes`、`result_raw_journal_lens: list[int]`、`results: bytes`、`result_lens: list[int]`、`results_failed_indicator: str`、`textfsm_platform: str`、`genie_platform: str`（`cli_result.py` 第54-70行）。
- F-092: CLI `Result.result` 属性返回 `"\n".join(self.results)`（`cli_result.py` 第213-227行）。
- F-093: CLI `Result.failed` 属性返回 `bool(self.results_failed_indicator)`（`cli_result.py` 第156-170行）。
- F-094: CLI `Result.elapsed_time_seconds` 属性返回 `(end_time - start_time) / 1_000_000_000`（`cli_result.py` 第196-210行）。
- F-095: CLI `Result.results_raw` 属性延迟重构原始字节，首次访问时通过 FFI 调用 Zig 的 `get_reconstructed_result_raw` 并缓存（`cli_result.py` 第230-299行）。
- F-096: CLI `Result.textfsm_parse(index=0, template=None, to_dict=True)` 支持 TextFSM 解析（`cli_result.py` 第318-350行）。
- F-097: CLI `Result.genie_parse(index=0)` 支持 Cisco genie 解析（`cli_result.py` 第352-371行）。
- F-098: CLI `Result.extend(result)` 方法合并另一个 Result 对象（`cli_result.py` 第132-153行）。
- F-099: NETCONF `Result` 是 dataclass，字段为 `input_: str`、`host`、`port`、`start_time: int`、`end_time: int`、`result_raw_journal: bytes`、`_result: str`、`rpc_warnings: str`、`rpc_errors: str`（`netconf_result.py` 第9-46行）。
- F-100: NETCONF `Result.failed` 返回 `bool(self.rpc_errors)`（`netconf_result.py` 第108-122行）。
- F-101: NETCONF `Result.result` 属性剥离 XML header（`<?xml ...?>`）后返回（`netconf_result.py` 第142-165行）。

## 异常体系

- F-102: 异常基类为 `ScrapliException(Exception)`（`exceptions.py` 第4行）。
- F-103: 异常类清单：`LibScrapliException`、`OptionsException`、`AllocationException`、`FFIException`、`NotOpenedException`、`OperationException`、`ParsingException`、`NoMessagesException`、`OutOfMememoryException`（同时继承 `MemoryError`）、`EOFException`（同时继承 `EOFError`）、`CancelledException`、`TimeoutException`（同时继承 `TimeoutError`）、`DriverException`、`SessionException`、`TransportException`、`InvalidArgumentException`（`exceptions.py` 第8-68行）。

## FFI 层

- F-104: `ffi.py` 中 `LIBSCRAPLI_VERSION = "0.0.1-rc.35"`（`ffi.py` 第15行）。
- F-105: `LIBSCRAPLI_PATH_OVERRIDE_ENV = "LIBSCRAPLI_PATH"`，`LIBSCRAPLI_CACHE_PATH_OVERRIDE_ENV = "LIBSCRAPLI_CACHE_PATH"`（`ffi.py` 第16-17行）。
- F-106: `get_libscrapli_shared_object_filename()` 支持 Linux（区分 musl/gnu）和 macOS，不支持 Windows（抛 `LibScrapliException("unsupported platform")`）（`ffi.py` 第55-81行）。
- F-107: `get_libscrapli_path()` 优先从 `LIBSCRAPLI_PATH` 环境变量获取，否则从 `scrapli.lib` 包资源目录加载（`ffi.py` 第84-117行）。
- F-108: `ZigSlice` 是 ctypes Structure，字段为 `ptr: POINTER(c_uint8)` 和 `len: c_size_t`，提供 `get_contents() -> bytes` 和 `get_decoded_contents() -> str`（`ffi_types.py` 第238-311行）。
- F-109: `ZigU64Slice` 是 ctypes Structure，字段为 `ptr: POINTER(c_uint64)` 和 `len: c_size_t`，提供 `get_contents() -> list[int]`（`ffi_types.py` 第173-229行）。
- F-110: `Cancel` 类包装 `c_bool(False)`，提供 `cancel()` 方法设为 True 和 `cancelled` 属性（`ffi_types.py` 第79-95行）。
- F-111: `LibScrapliFFIResult` 是 IntEnum，值为 SUCCESS=0、UNKNOWN=1、OUT_OF_MEMORY=2、EOF=3、CANCELLED=4、TIMEOUT=5、DRIVER=6、SESSION=7、TRANSPORT=8、OPERATION=9、INVALID_ARGUMENT=10（`ffi_types.py` 第98-129行）。
- F-112: `LibScrapliFFIResult.raise_if_error(message)` 根据错误码抛出对应异常（`ffi_types.py` 第131-170行）。
- F-113: `to_c_string(s: str) -> c_char_p` 将 UTF-8 字符串编码为 `c_char_p`（`ffi_types.py` 第320-334行）。
- F-114: FFI 函数映射分三层：`LibScrapliSharedMapping`（共享）、`LibScrapliCliMapping`（CLI 专属）、`LibScrapliNetconfMapping`（NETCONF 专属），由 `LibScrapliMapping` 组合（`ffi_mapping.py`）。

## Helper 与装饰器

- F-115: `wait_for_available_operation_result(fd, cancel, operation_id_ptr)` 使用 `select.select` 同步等待 fd 可读（`helper.py` 第65-105行）。
- F-116: `wait_for_available_operation_result_async` 使用 `asyncio` 事件循环的 `add_reader` 异步等待（`helper.py` 第137-182行）。
- F-117: `WAKEUP_FD_POLL_INTERVAL_S = 0.1`（`helper.py` 第15行）。
- F-118: `resolve_file(file)` 支持直接路径和 `~` 展开路径，失败抛 `OperationException`（`helper.py` 第18-37行）。
- F-119: `second_to_nano(d)` 将秒转换为纳秒：`int(d / 1e-9)`（`helper.py` 第185-199行）。
- F-120: `handle_operation_timeout` 装饰器在操作前后临时设置/重置 `operation_timeout_ns`（`cli_decorators.py` 第17-81行）。
- F-121: `handle_operation_timeout_async` 为异步版本装饰器（`cli_decorators.py` 第84-147行）。

## 平台定义

- F-122: `definitions/` 目录包含 44 个 YAML 平台定义文件（含 `default.yaml`）。
- F-123: 平台定义通过 `SCRAPLI_DEFINITIONS_PATH` 环境变量可覆盖路径（`cli.py` 第59-60行：`CLI_DEFINITIONS_PATH_OVERRIDE_ENV = "SCRAPLI_DEFINITIONS_PATH"`）。
- F-124: `_load_definition()` 先在内置 definitions 目录查找，再按文件路径查找，均失败抛 `OptionsException`（`cli.py` 第500-531行）。
- F-125: `default.yaml` 定义 `prompt_pattern: '^.*[>#$]\s?+$'`、`default_mode: 'cli'`、`on_close_instructions` 发送 `exit`。
- F-126: `cisco_iosxe.yaml` 定义 4 个模式：`exec`、`privileged_exec`、`configuration`、`tclsh`，含 `failure_indicators`、`on_open_instructions`（自动进入特权模式、设置 term width/len）、`on_close_instructions`。
- F-127: 平台定义支持 `__lookup::enable` 模板语法，从 `AuthOptions.lookups` 中查找值（cisco_iosxe.yaml 第13行）。
- F-128: `definition_options/mikrotik_routeros.py` 定义 `mikrotik_routeros_post_init(c: Cli)` 函数，在用户名后追加 `+tc` 并设置 `return_char = "\r\n"`（`mikrotik_routeros.py` 第6-20行）。
- F-129: `Cli.__init__` 通过 `import_module(f"scrapli.definition_options.{self._platform_name}")` 动态加载平台特定选项，可通过 `skip_static_options=True` 跳过（`cli.py` 第330-347行）。
- F-130: 平台定义 YAML 支持 `ntc_templates_platform` 和 `genie_platform` 字段（cisco_iosxe.yaml 第63-64行）。

## 输出解析

- F-131: `textfsm_get_template(platform, command)` 需要安装 `ntc_templates` 和 `textfsm` 包，否则抛 `ParsingException("optional extra 'textfsm' not found")`（`cli_parse.py` 第14-48行）。
- F-132: `textfsm_parse(template, output, to_dict=True)` 支持文件路径、URL 和 TextIO 模板（`cli_parse.py` 第76-124行）。
- F-133: `genie_parse(platform, command, output)` 需要安装 `genie` 包（`cli_parse.py` 第127-161行）。
