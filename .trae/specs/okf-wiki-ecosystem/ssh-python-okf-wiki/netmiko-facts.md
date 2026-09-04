# netmiko 源码事实清单

> R阶段事实采集。基于 netmiko 4.7.0（commit 8ace5f2ae7da）源码阅读。
> 源码路径: `external/libs/netmiko/netmiko/`

## 版本与导出

- F-001: netmiko 版本为 `4.7.0`，最低 Python 要求 3.10（`__init__.py:3-6`）
- F-002: `__init__.py` 导出 `ConnectHandler`, `TelnetFallback`, `ConnLogOnly`, `ConnUnify`, `ssh_dispatcher`, `redispatch`, `platforms`, `FileTransfer`（`__init__.py:38-45`）
- F-003: 导出 `SCPConn`, `InLineTransfer`（`__init__.py:46-47`）
- F-004: 导出异常类 `NetmikoTimeoutException`, `NetMikoTimeoutException`（别名）, `NetmikoAuthenticationException`, `NetMikoAuthenticationException`（别名）, `ConfigInvalidException`, `ReadException`, `ReadTimeout`, `NetmikoBaseException`, `ConnectionException`（`__init__.py:48-58`）
- F-005: 导出 `SSHDetect`, `BaseConnection`, `file_transfer`, `progress_bar`（`__init__.py:59-61`）
- F-006: `Netmiko = ConnectHandler` 为替代命名别名（`__init__.py:64`）
- F-007: `CNTL_SHIFT_6 = chr(30)` 为 Cisco Ctrl+Shift+6 转义序列（`__init__.py:94`）

## ssh_dispatcher 工厂与映射

- F-008: `CLASS_MAPPER_BASE` 字典映射约170个基础 device_type 字符串到驱动类（`ssh_dispatcher.py:200-377`）
- F-009: `CLASS_MAPPER` 在 `CLASS_MAPPER_BASE` 基础上为每个 key 自动添加 `_ssh` 后缀别名（`ssh_dispatcher.py:401-406`）
- F-010: `FILE_TRANSFER_MAP` 映射18个平台到对应 FileTransfer 类，同样自动添加 `_ssh` 后缀（`ssh_dispatcher.py:379-413`）
- F-011: Telnet 驱动通过独立赋值添加到 `CLASS_MAPPER`，约60个 `_telnet` 条目（`ssh_dispatcher.py:416-477`）
- F-012: Serial 驱动有 `cisco_ios_serial` 和 `furukawa_fitelnet_serial`（`ssh_dispatcher.py:480-481`）
- F-013: `"autodetect"` 映射到 `TerminalServerSSH`（`ssh_dispatcher.py:485`）
- F-014: `platforms = list(CLASS_MAPPER.keys())`，排序后生成（`ssh_dispatcher.py:487-488`）
- F-015: `platforms_base = list(CLASS_MAPPER_BASE.keys())`，排序后生成（`ssh_dispatcher.py:489-490`）
- F-016: `ConnectHandler(*args, **kwargs)` 工厂函数校验 `device_type` 在 platforms 中，调用 `ssh_dispatcher` 获取类并实例化（`ssh_dispatcher.py:504-516`）
- F-017: `ssh_dispatcher(device_type)` 直接返回 `CLASS_MAPPER[device_type]`（`ssh_dispatcher.py:615-617`）
- F-018: `redispatch(obj, device_type, session_prep=True)` 通过修改 `obj.__class__` 动态切换驱动类，可选调用 `_try_session_preparation()`（`ssh_dispatcher.py:620-629`）
- F-019: `FileTransfer(*args, **kwargs)` 工厂函数校验 device_type 在 scp_platforms 中，返回对应 FileTransfer 类实例（`ssh_dispatcher.py:632-646`）
- F-020: `TelnetFallback` 先尝试 SSH 连接，失败后自动尝试对应 Telnet 驱动（`ssh_dispatcher.py:519-534`）
- F-021: `ConnLogOnly` 连接失败时返回 None 并记录日志，不抛出异常（`ssh_dispatcher.py:537-588`）
- F-022: `ConnUnify` 将所有连接异常包装为 `ConnectionException`（`ssh_dispatcher.py:591-612`）
- F-023: `GenericSSH = TerminalServerSSH`, `GenericTelnet = TerminalServerTelnet`（`ssh_dispatcher.py:196-197`）

## BaseConnection 初始化与属性

- F-024: `BaseConnection.__init__` 接受40+参数，包括 ip/host/username/password/secret/port/device_type（`base_connection.py:152-207`）
- F-025: 超时参数层次：`conn_timeout=10`（TCP连接）, `banner_timeout=15`（SSH banner）, `auth_timeout=None`（认证响应）, `blocking_timeout=20`（读取阻塞）, `timeout=100`（TCP/读取循环）, `session_timeout=60`（锁等待）（`base_connection.py:182-189`）
- F-026: `fast_cli=True` 默认开启，自动将 `global_delay_factor` 设为 0.1（`base_connection.py:195,381-382`）
- F-027: `global_delay_factor` 默认 1.0，影响所有延迟计算（`base_connection.py:162,379`）
- F-028: `auto_connect=True` 默认在 `__init__` 中调用 `_open()`（`base_connection.py:204,489-491`）
- F-029: 协议检测逻辑：device_type 含 `_telnet` → telnet，含 `_serial` → serial，否则 ssh（`base_connection.py:448-455`）
- F-030: 默认端口 SSH=22, Telnet=23（`base_connection.py:352-357`）
- F-031: 主机密钥策略：`ssh_strict=False` 时使用 `paramiko.AutoAddPolicy()`，True 时使用 `RejectPolicy()`（`base_connection.py:458-461`）
- F-032: `keepalive=0` 默认不发送保活包；设值后调用 `transport.set_keepalive()`（`base_connection.py:191,1217-1219`）
- F-033: `SecretsFilter` 日志过滤器将 password 和 secret 替换为 `********`（`base_connection.py:81-90,387-394`）
- F-034: `session_log` 支持文件路径字符串、`io.BufferedIOBase` 对象或 `SessionLog` 对象（`base_connection.py:397-422`）
- F-035: `_session_locker = Lock()` 使用 threading.Lock 保证通道线程安全（`base_connection.py:445`）
- F-036: `RETURN` 默认为 `"\n"`（SSH）或 `"\r\n"`（Telnet）；`TELNET_RETURN = "\r\n"`（`base_connection.py:333-340`）
- F-037: `encoding` 默认为 `"utf-8"`（`base_connection.py:201,374`）

## 连接生命周期

- F-038: `_open()` 调用链：`_modify_connection_params()` → `establish_connection()` → `_try_session_preparation()`（`base_connection.py:506-510`）
- F-039: `establish_connection(width=511, height=1000)` 对 SSH 创建 paramiko.SSHClient，调用 connect()，再 `invoke_shell(term="vt100", width=511, height=1000)`（`base_connection.py:1114-1228`）
- F-040: TCP socket.error 转换为 `NetmikoTimeoutException`，AuthenticationException 转换为 `NetmikoAuthenticationException`（`base_connection.py:1154-1206`）
- F-041: `_build_ssh_client()` 创建 SSHClient 实例，加载 system_host_keys/alt_host_keys，设置 missing_host_key_policy（`base_connection.py:1270-1283`）
- F-042: `_connect_params_dict()` 生成 paramiko connect 所需字典（hostname/port/username/password/key_filename/pkey/timeout等）（`base_connection.py:1076-1098`）
- F-043: `_use_ssh_config()` 支持 OpenSSH 配置文件中的 ProxyCommand 和 ProxyJump（单跳）（`base_connection.py:1029-1074`）
- F-044: `session_preparation()` 默认实现：`_test_channel_read()` → `set_base_prompt()` → `set_terminal_width()` → `disable_paging()`（`base_connection.py:1011-1027`）
- F-045: `_try_session_preparation()` 包装 session_preparation，异常时调用 disconnect() 清理（`base_connection.py:994-1009`）
- F-046: `_test_channel_read(count=40, pattern="")` 登录后验证通道有数据返回，发送 RETURN 并递增延迟（`base_connection.py:1230-1264`）
- F-047: `disconnect()` 调用 cleanup() → paramiko_cleanup() → 关闭 remote_conn/remote_conn_pre/session_log，移除 SecretsFilter（`base_connection.py:2518-2543`）
- F-048: 支持上下文管理器 `__enter__` 返回 self，`__exit__` 调用 disconnect()（`base_connection.py:512-523`）
- F-049: `is_alive()` 返回连接存活状态布尔值（`base_connection.py:604`）

## 命令执行

- F-050: `send_command(command_string, expect_string=None, read_timeout=10.0, auto_find_prompt=True, cmd_verify=True, ...)` 基于模式匹配读取，等待设备提示符或 expect_string（`base_connection.py:1671-1689`）
- F-051: `send_command_timing(command_string, last_read=2.0, read_timeout=120.0, cmd_verify=False, ...)` 基于延迟机制读取，等待 last_read 秒无新数据（`base_connection.py:1521-1538`）
- F-052: `send_command_expect(*args, **kwargs)` 是 `send_command` 的别名，向后兼容（`base_connection.py:1873-1877`）
- F-053: `write_channel(out_data)` 被 `@lock_channel` 和 `@log_writes` 装饰器修饰（`base_connection.py:594-602`）
- F-054: `read_channel_timing(last_read, read_timeout)` 循环读取直到 last_read 秒无新数据或 read_timeout 超时（`base_connection.py:766`）
- F-055: `read_until_pattern(pattern, read_timeout)` 读取直到匹配正则模式（`base_connection.py:674`）
- F-056: `read_until_prompt(read_entire_line=False)` 读取直到匹配 base_prompt（`base_connection.py:844`）
- F-057: `read_until_prompt_or_pattern(pattern, re_flags, read_entire_line)` 读取直到提示符或指定模式（`base_connection.py:862`）
- F-058: `clear_buffer(backoff=True, backoff_max=3.0)` 读取通道中所有可用数据，检测到数据时指数退避（`base_connection.py:1470-1495`）
- F-059: `command_echo_read(cmd, read_timeout)` 读取直到检测到命令回显（`base_connection.py:1497`）
- F-060: 三种命令方法均支持 `use_textfsm`, `textfsm_template`, `use_ttp`, `ttp_template`, `use_genie` 参数进行结构化输出解析（`base_connection.py:1531-1535,1682-1686`）
- F-061: `structured_data_converter()` 工具函数统一处理 TextFSM/TTP/Genie 解析（`utilities.py:589`）
- F-062: `send_multiline(commands, multiline=True, **kwargs)` 和 `send_multiline_timing()` 支持多行交互命令（`base_connection.py:1886,1930`）

## 提示符与输出处理

- F-063: `find_prompt(delay_factor=1.0, pattern=None)` 发送 RETURN，读取最后一行作为当前提示符（`base_connection.py:1427-1468`）
- F-064: `set_base_prompt(pri_prompt_terminator="#", alt_prompt_terminator=">")` 查找提示符并去除末尾终止符，存入 `self.base_prompt`（`base_connection.py:1376-1425`）
- F-065: `strip_prompt(a_string)` 如果最后一行包含 base_prompt 则移除该行（`base_connection.py:1619-1631`）
- F-066: `strip_command(command_string, output)` 从输出中移除命令回显（`base_connection.py:1951`）
- F-067: `normalize_linefeeds(a_string)` 将 `\r\r\n`, `\r\n`, `\n\r` 转换为 `\n`（`base_connection.py:1980-1993`）
- F-068: `normalize_cmd(command)` 去除尾部空白并追加 RETURN（`base_connection.py:1995-2003`）
- F-069: `strip_ansi_escape_codes(string_buffer)` 移除 ANSI 转义序列（`base_connection.py:2386`）
- F-070: `strip_backspaces(output)` 静态方法处理退格符（`base_connection.py:1942`）

## 终端设置

- F-071: `disable_paging(command="terminal length 0", cmd_verify=True, pattern=None)` 发送禁用分页命令（`base_connection.py:1308-1341`）
- F-072: `set_terminal_width(command="", cmd_verify=False, pattern=None)` 设置终端宽度防止输出变形，默认宽度511（`base_connection.py:1343-1374`）
- F-073: `select_delay_factor(delay_factor)` 在 fast_cli 模式下取较小值，否则取较大值（`base_connection.py:1285-1302`）

## 特权与配置模式

- F-074: `check_enable_mode(check_string="")` 发送 RETURN 读取提示符，检查是否在特权模式（`base_connection.py:2005-2013`）
- F-075: `enable(cmd="", pattern="ssword", enable_pattern=None, check_state=True)` 进入特权模式，处理密码提示（`base_connection.py:2040-2095`）
- F-076: `exit_enable_mode(exit_command="")` 退出特权模式（`base_connection.py:2097-2115`）
- F-077: `check_config_mode(check_string="", pattern="", force_regex=False)` 检查是否在配置模式（`base_connection.py:2117-2142`）
- F-078: `config_mode(config_command="", pattern="", re_flags=0)` 进入配置模式（`base_connection.py:2144-2168`）
- F-079: `exit_config_mode(exit_config="", pattern="")` 退出配置模式（`base_connection.py:2170-2192`）
- F-080: `send_config_set(config_commands, exit_config_mode=True, read_timeout=None, cmd_verify=True, enter_config_mode=True, error_pattern="", terminator=r"#", ...)` 批量发送配置命令，自动进入/退出配置模式（`base_connection.py:2213-2229`）
- F-081: `send_config_from_file(config_file, **kwargs)` 逐行读取配置文件并调用 send_config_set（`base_connection.py:2194-2211`）
- F-082: `save_config(cmd="", confirm=False, confirm_response="")` 在基类中抛出 `NotImplementedError`，由厂商驱动重写（`base_connection.py:2549-2551`）
- F-083: `commit()` 在基类中抛出 `AttributeError`，由支持 commit 的平台（如 Juniper）重写（`base_connection.py:2545-2547`）

## 异常体系

- F-084: `NetmikoBaseException(Exception)` 为 netmiko 自有异常基类（`exceptions.py:5-8`）
- F-085: `ConnectionException(NetmikoBaseException)` 通用连接失败异常（`exceptions.py:11-14`）
- F-086: `NetmikoTimeoutException(paramiko.ssh_exception.SSHException)` 继承 paramiko SSHException（`exceptions.py:17-20`）
- F-087: `NetmikoAuthenticationException(paramiko.ssh_exception.AuthenticationException)` 继承 paramiko AuthenticationException（`exceptions.py:26-29`）
- F-088: `ConfigInvalidException(NetmikoBaseException)` 配置无效异常（`exceptions.py:35-38`）
- F-089: `WriteException(NetmikoBaseException)` 写操作异常（`exceptions.py:41-44`）
- F-090: `ReadException(NetmikoBaseException)` 读操作异常（`exceptions.py:47-50`）
- F-091: `ReadTimeout(ReadException)` 读取超时异常（`exceptions.py:53-56`）
- F-092: `NetmikoParsingException(ReadException)` 解析错误异常（`exceptions.py:59-61`）

## 厂商驱动继承

- F-093: `CiscoBaseConnection(BaseConnection)` 提供 Cisco 风格默认值：enable cmd="enable", config_command="configure terminal", exit_config="end", save_config="copy running-config startup-config"（`cisco_base_connection.py:11-259`）
- F-094: `CiscoSSHConnection(CiscoBaseConnection)` 为空类 pass（`cisco_base_connection.py:262-263`）
- F-095: `CiscoIosBase(CiscoBaseConnection)` 重写 session_preparation（terminal width 511 → disable paging → set base prompt），set_base_prompt 截断为16字符，save_config 默认 "write mem"（`cisco/cisco_ios.py:13-61`）
- F-096: `CiscoIosSSH(CiscoIosBase)`, `CiscoIosTelnet(CiscoIosBase)`, `CiscoIosSerial(CiscoIosBase)` 均为空类（`cisco/cisco_ios.py:64-79`）
- F-097: `AristaBase(CiscoSSHConnection)` 重写 session_preparation 启用 ANSI、设置宽度、禁用分页；config_mode 使用 "configure terminal"（`arista/arista.py:12-96`）
- F-098: `JuniperBase(NoEnable, BaseConnection)` 使用 NoEnable mixin；session_preparation 进入 CLI 模式、设置 screen-width/length；commit() 支持 confirm/confirm_delay/check/comment/and_quit 参数（`juniper/juniper.py:10-169`）
- F-099: `LinuxSSH(CiscoSSHConnection)` disable_paging 为空操作；config_mode 使用 "sudo -s"；root 用户不退出配置模式（`linux/linux_ssh.py:17-100`）
- F-100: `HPComwareBase(CiscoSSHConnection)` 默认禁用 global_cmd_verify；config_command="system-view", exit_config="return"；disable_paging 使用 "screen-length disable"（`hp/hp_comware.py:7-80`）

## Mixin 类

- F-101: `NoEnable` mixin 为无特权模式平台提供：`check_enable_mode()` 返回 True，`enable()` 和 `exit_enable_mode()` 返回空字符串（`no_enable.py:5-33`）
- F-102: `NoConfig` mixin 为无配置模式平台提供：`check_config_mode()` 返回 True，`config_mode()` 和 `exit_config_mode()` 返回空字符串（`no_config.py:1-22`）

## SSHDetect 自动探测

- F-103: `SSHDetect` 类要求 `device_type="autodetect"`，构造时创建连接并 sleep 3 秒等待登录完成（`ssh_autodetect.py:439-456`）
- F-104: `SSH_MAPPER_DICT` 包含约50个设备类型的探测规则，每条有 cmd/search_patterns/priority/dispatch（`ssh_autodetect.py:55-394`）
- F-105: `SSH_MAPPER_BASE` 按命令使用频率排序（最常见命令优先），为列表而非字典（`ssh_autodetect.py:406-409`）
- F-106: `autodetect()` 遍历 SSH_MAPPER_BASE，调用 dispatch 方法，accuracy>=99 时立即返回；最终返回最佳匹配或 None（`ssh_autodetect.py:458-494`）
- F-107: `potential_matches` 字典存储所有匹配的 device_type 和 accuracy（`ssh_autodetect.py:455,474`）
- F-108: 三种 dispatch 方法：`_autodetect_std`（发送命令匹配输出）、`_autodetect_remote_version`（匹配 SSH transport remote_version）、`_autodetect_login_banner`（匹配登录横幅）（`ssh_autodetect.py:539-661`）
- F-109: `_send_command_wrapper` 缓存命令结果避免重复发送相同命令（`ssh_autodetect.py:516-537`）

## SCP 文件传输

- F-110: `SCPConn` 类建立独立 SSH 连接用于 SCP，使用 `scp.SCPClient`，提供 scp_put_file/scp_get_file/scp_transfer_file/close（`scp_handler.py:23-69`）
- F-111: `BaseFileTransfer` 管理 SCP 传输和 SSH 控制通道，支持 context manager（`scp_handler.py:72-143`）
- F-112: `BaseFileTransfer` 核心方法：verify_space_available, check_file_exists, remote_file_size, file_md5, remote_md5, compare_md5, transfer_file, verify_file（`scp_handler.py:205-408`）
- F-113: `file_transfer()` 便捷函数返回字典 `{file_exists, file_transferred, file_verified}`，支持 inline_transfer（仅 Cisco IOS 文本文件）（`scp_functions.py:52-154`）
- F-114: `progress_bar(filename, size, sent, peername)` 显示 ASCII 进度条（`scp_functions.py:19-42`）
- F-115: `InLineTransfer` 通过 Cisco IOS TCL 直接传输文件，仅支持 put 和文本文件（`cisco/cisco_ios.py:88-150`）

## 工具与其他

- F-116: `run_ttp(template, res_kwargs, **kwargs)` 方法使用 TTP 模板解析设备输出（`base_connection.py:2553-2585`）
- F-117: `@lock_channel` 装饰器在方法执行前后获取/释放会话锁（`base_connection.py:93-104`）
- F-118: `@log_writes` 装饰器记录写入通道的数据到 session_log（`base_connection.py:124-142`）
- F-119: `TelnetConnection(BaseConnection)` 为空类 pass（`base_connection.py:2588-2589`）
- F-120: `delay_factor_compat=True` 可恢复 Netmiko 3.x 的 delay_factor/global_delay_factor/max_loops 行为（`base_connection.py:205,319-321`）
