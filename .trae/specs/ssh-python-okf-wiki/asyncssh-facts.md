# asyncssh 源码事实清单

> R 阶段产出，基于 asyncssh v2.24.0（commit 25370783e5c1）源码逐模块阅读。
> 禁止"用于"/"目的是"/"设计为"等推断词，所有事实均溯源至源码。

## 版本与包信息

- F-001: asyncssh 版本号为 `2.24.0`，定义于 `version.py:29`，`__author__ = 'Ron Frederick'`，`__url__ = 'http://asyncssh.timeheart.net'`。
- F-002: `__init__.py` 导出约 170 个公开符号，涵盖连接、通道、流、进程、SFTP、密钥、认证、转发、Agent 等模块。
- F-003: `__init__.py:126` 通过 `from . import sk_eddsa, sk_ecdsa, eddsa, ecdsa, rsa, dsa, kex_dh, kex_rsa` 触发算法注册调用。
- F-004: 包依赖 `cryptography` 库提供加密原语，`crypto/` 子包是对 cryptography 的封装层。
- F-005: Python 版本要求 3.10+（任务简报声明）。

## connect() 入口函数

- F-006: `connect()` 是模块级协程函数，定义于 `connection.py:9180`，签名为 `async def connect(host='', port=(), *, tunnel=(), family=(), flags=0, local_addr=(), sock=None, config=(), options=None, **kwargs) -> SSHClientConnection`。
- F-007: `connect()` 返回 `SSHClientConnection` 实例，认证成功后即可打开会话或设置转发。
- F-008: `connect()` 支持 `tunnel` 参数，可传入已有 `SSHClientConnection` 或 `[user@]host[:port]` 字符串实现跳板机。
- F-009: `connect()` 支持 `sock` 参数传入已连接的 socket，此时不应指定 host/port/family/flags/local_addr。
- F-010: `connect()` 支持 `config` 参数加载 OpenSSH 客户端配置文件，默认尝试加载 `~/.ssh/config`。
- F-011: `create_server()` 协程定义于 `connection.py:9691`，是 `listen()` 的向后兼容包装，签名为 `async def create_server(server_factory, host='', port=(), **kwargs) -> SSHAcceptor`。
- F-012: `listen()` 协程定义于 `connection.py:9400`，是创建 SSH 服务端的推荐入口。
- F-013: `create_connection()` 协程定义于 `connection.py:9665`，是创建 SSH 客户端的低级入口，需要传入 `client_factory`。
- F-014: `get_server_host_key()` 协程定义于 `connection.py:9709`，连接服务器并返回密钥交换中使用的服务器主机密钥。
- F-015: `get_server_auth_methods()` 协程定义于 `connection.py:9853`，返回服务器支持的认证方法列表。
- F-016: `run_client()` 协程定义于 `connection.py:9077`，`run_server()` 协程定义于 `connection.py:9131`，用于在已打开的 socket 上运行 SSH 协议。
- F-017: `connect_reverse()` 定义于 `connection.py:9299`，`listen_reverse()` 定义于 `connection.py:9525`，支持反向连接模式。

## SSHClientConnection 核心方法

- F-018: `SSHClientConnection` 类定义于 `connection.py:3415`，继承 `SSHConnection`。
- F-019: `SSHConnection` 基类定义于 `connection.py:867`，同时继承 `SSHPacketHandler` 和 `asyncio.Protocol`。
- F-020: `SSHClientConnection.run()` 协程定义于 `connection.py:4641`，签名为 `async def run(*args, check=False, timeout=None, **kwargs) -> SSHCompletedProcess`，内部调用 `create_process()` 后等待 `process.wait()`。
- F-021: `SSHClientConnection.create_process()` 协程定义于 `connection.py:4489`，返回 `SSHClientProcess`，支持 `input/stdin/stdout/stderr/bufsize/send_eof/recv_eof` 参数。
- F-022: `SSHClientConnection.create_session()` 协程定义于 `connection.py:4241`，是底层会话创建方法，接受 `session_factory` 和 `command/term_type/term_size/term_modes/env/send_env/encoding/errors` 等参数。
- F-023: `SSHClientConnection.open_session()` 协程定义于 `connection.py:4463`，是 `create_session(SSHClientStreamSession, ...)` 的便捷包装，返回 `(SSHWriter, SSHReader, SSHClientChannel)` 元组。
- F-024: `SSHClientConnection.start_sftp_client()` 协程定义于 `connection.py:5764`，签名为 `async def start_sftp_client(env=(), send_env=(), path_encoding='utf-8', path_errors='strict', sftp_version=3) -> SFTPClient`。
- F-025: `SSHClientConnection.create_connection()` 协程定义于 `connection.py:4687`，请求服务器打开出站 TCP 连接（direct-tcpip），返回 `(SSHTCPChannel, SSHTCPSession)`。
- F-026: `SSHClientConnection.open_connection()` 协程定义于 `connection.py:4761`，是 `create_connection()` 的流包装，返回 `(SSHReader, SSHWriter, SSHTCPChannel)`。
- F-027: `SSHClientConnection.create_server()` 协程定义于 `connection.py:4791`，请求服务器打开 TCP 监听器（tcpip-forward），返回 `SSHListener`。
- F-028: `SSHClientConnection.start_server()` 协程定义于 `connection.py:4881`，是 `create_server()` 的流包装，接受 `handler_factory` 回调。
- F-029: `SSHClientConnection.forward_local_port()` 协程定义于 `connection.py:3252`（基类 `SSHConnection`），签名为 `async def forward_local_port(listen_host, listen_port, dest_host, dest_port, accept_handler=None) -> SSHListener`。
- F-030: `SSHClientConnection.forward_remote_port()` 协程定义于 `connection.py:5476`，在远程服务器上设置端口转发。
- F-031: `SSHClientConnection.forward_local_port_to_path()` 定义于 `connection.py:5349`，实现本地 TCP 到远程 UNIX socket 的转发。
- F-032: `SSHClientConnection.forward_local_path_to_port()` 定义于 `connection.py:5425`，实现本地 UNIX socket 到远程 TCP 的转发。
- F-033: `SSHClientConnection.forward_remote_port_to_path()` 定义于 `connection.py:5557`，远程 TCP 到本地 UNIX socket 转发。
- F-034: `SSHClientConnection.forward_remote_path_to_port()` 定义于 `connection.py:5599`，远程 UNIX socket 到本地 TCP 转发。
- F-035: `SSHClientConnection.forward_socks()` 协程定义于 `connection.py:5639`，创建 SOCKS 代理监听器。
- F-036: `SSHClientConnection.forward_tun()` / `forward_tap()` 分别定义于 `connection.py:5695` 和 `5730`，支持三层/二层隧道转发。
- F-037: `SSHClientConnection.validate_server_host_key()` 定义于 `connection.py:3641`，验证并返回服务器主机密钥。
- F-038: `SSHClientConnection.get_server_host_key()` 定义于 `connection.py:3659`，返回密钥交换中使用的服务器主机密钥。
- F-039: `SSHClientConnection.get_server_auth_methods()` 定义于 `connection.py:3673`，返回服务器支持的认证方法序列。
- F-040: `SSHClientConnection` 支持 `create_unix_connection()`（line 4923）、`create_unix_server()`（line 5012）、`open_unix_connection()`（line 4981）、`start_unix_server()`（line 5075）等 UNIX socket 方法。
- F-041: `SSHClientConnection` 支持 `create_tun()`（line 5200）、`create_tap()`（line 5246）、`open_tun()`（line 5292）、`open_tap()`（line 5320）等 TUN/TAP 方法。

## SSHConnection 基类

- F-042: `SSHConnection` 继承 `asyncio.Protocol`，是 asyncio 协议栈的核心状态机。
- F-043: `SSHConnection` 定义了 `is_closing()`（line 1245）、`get_owner()`（line 1250）、`get_extra_info()`（line 2943）、`set_extra_info()`（line 2974）等方法。
- F-044: 默认 SSH 接收窗口大小为 2 MiB（`_DEFAULT_WINDOW = 2*1024*1024`，connection.py:277）。
- F-045: 默认最大包大小为 32 KiB（`_DEFAULT_MAX_PKTSIZE = 32768`，connection.py:278）。
- F-046: 默认 SSH 端口为 22（`DEFAULT_PORT = 22`，constants.py:27）。
- F-047: `SSHConnection` 支持 keepalive 机制，通过 `_set_keepalive_timer()` / `_make_keepalive_request()` 实现。

## SSHChannel 通道层

- F-048: `SSHChannel` 泛型类定义于 `channel.py:86`，继承 `SSHPacketHandler`，类型参数为 `AnyStr`。
- F-049: `SSHClientChannel` 定义于 `channel.py:1119`，`SSHServerChannel` 定义于 `channel.py:1497`。
- F-050: `SSHTCPChannel`、`SSHUNIXChannel`、`SSHTunTapChannel` 均在 `__init__.py` 中导出。
- F-051: `SSHChannel.write()` 定义于 `channel.py:896`，支持 `datatype` 参数发送扩展数据（如 stderr）。
- F-052: `SSHChannel.writelines()` 定义于 `channel.py:952`，`write_eof()` 定义于 `channel.py:981`。
- F-053: `SSHChannel.close()` 定义于 `channel.py:768`，`abort()` 定义于 `channel.py:749`，`wait_closed()` 协程定义于 `channel.py:794`。
- F-054: `SSHChannel.pause_reading()` 定义于 `channel.py:999`，`resume_reading()` 定义于 `channel.py:1020`。
- F-055: `SSHChannel.get_exit_status()` 定义于 `channel.py:1323`，返回 `Optional[int]`。
- F-056: `SSHChannel.get_returncode()` 定义于 `channel.py:1354`，返回退出状态或负信号编号。
- F-057: `SSHClientChannel.change_terminal_size()` 定义于 `channel.py:1374`，签名为 `change_terminal_size(width, height, pixwidth=0, pixheight=0)`。
- F-058: `SSHClientChannel.send_break()` 定义于 `channel.py:1405`，`send_signal()` 定义于 `channel.py:1424`。
- F-059: `SSHClientChannel.terminate()` 定义于 `channel.py:1462`，发送 SIGTERM；`kill()` 定义于 `channel.py:1479`，发送 SIGKILL。
- F-060: `SSHServerChannel.write_stderr()` 定义于 `channel.py:1944`，`writelines_stderr()` 定义于 `channel.py:1963`。
- F-061: `SSHServerChannel.exit()` 定义于 `channel.py:1974`，`exit_with_signal()` 定义于 `channel.py:1999`。
- F-062: `SSHServerChannel.get_terminal_type()` 定义于 `channel.py:1801`，`get_terminal_size()` 定义于 `channel.py:1820`。
- F-063: `SSHChannel.get_extra_info()` 定义于 `channel.py:804`，支持 `set_extra_info()`（line 833）附加自定义信息。

## SSHReader / SSHWriter 流层

- F-064: `SSHReader` 泛型类定义于 `stream.py:72`，`SSHWriter` 泛型类定义于 `stream.py:257`。
- F-065: `SSHReader.read()` 协程定义于 `stream.py:137`，签名为 `async def read(n=-1) -> AnyStr`。
- F-066: `SSHReader.readline()` 协程定义于 `stream.py:159`，`readuntil()` 协程定义于 `stream.py:180`，`readexactly()` 协程定义于 `stream.py:223`。
- F-067: `SSHReader.at_eof()` 定义于 `stream.py:241`，返回布尔值。
- F-068: `SSHWriter.write()` 定义于 `stream.py:333`，`writelines()` 定义于 `stream.py:347`，`write_eof()` 定义于 `stream.py:352`。
- F-069: `SSHWriter.drain()` 协程定义于 `stream.py:320`，`close()` 定义于 `stream.py:295`，`wait_closed()` 协程定义于 `stream.py:310`。
- F-070: `SSHWriter.is_closing()` 定义于 `stream.py:305`，`can_write_eof()` 定义于 `stream.py:290`。
- F-071: `SSHClientStreamSession` 定义于 `stream.py:689`，`SSHServerStreamSession` 定义于 `stream.py:694`。

## SSHProcess 进程层

- F-072: `SSHProcess` 泛型类定义于 `process.py:819`，继承 `SSHStreamSession`。
- F-073: `SSHClientProcess` 定义于 `process.py:1240`，`SSHServerProcess` 定义于 `process.py:1607`。
- F-074: `SSHCompletedProcess` 是 `Record` 子类，定义于 `process.py:774`，包含字段 `env/command/subsystem/exit_status/exit_signal/returncode/stdout/stderr`。
- F-075: `SSHClientProcess` 的 `stdin` 属性返回 `SSHWriter`，`stdout`/`stderr` 属性返回 `SSHReader`（process.py:1292-1306）。
- F-076: `SSHClientProcess.exit_status` / `exit_signal` / `returncode` 属性定义于 process.py:1274-1286。
- F-077: `SSHProcess.wait()` 协程定义于 `process.py:1551`，签名为 `async def wait(check=False, timeout=None) -> SSHCompletedProcess`。
- F-078: `SSHProcess.communicate()` 协程定义于 `process.py:1451`，签名为 `async def communicate(input=None) -> Tuple[AnyStr, AnyStr]`。
- F-079: `SSHProcess.redirect()` 协程定义于 `process.py:1323`，支持重定向 stdin/stdout/stderr。
- F-080: `SSHProcess.collect_output()` 定义于 `process.py:1435`，返回 `(stdout, stderr)` 元组。
- F-081: `SSHProcess.change_terminal_size()` 定义于 `process.py:1480`，`send_break()` 定义于 `process.py:1506`，`send_signal()` 定义于 `process.py:1520`。
- F-082: `SSHProcess.terminate()` 定义于 `process.py:1533`，`kill()` 定义于 `process.py:1542`。
- F-083: `SSHProcess.close()` 定义于 `process.py:1216`，`is_closing()` 定义于 `process.py:1222`，`wait_closed()` 协程定义于 `process.py:1228`。
- F-084: `PIPE`、`DEVNULL`、`STDOUT` 三个常量从 `process.py` 导出（`__init__.py:78`），行为类似 `subprocess` 模块。
- F-085: `ProcessError` 异常定义于 `process.py:694`，`TimeoutError` 定义于 `process.py:758`（继承 `ProcessError` 和 `asyncio.TimeoutError`）。
- F-086: `SSHServerProcess` 额外提供 `term_type`（line 1637）、`term_size`（line 1648）等服务端属性。

## SFTPClient 文件传输

- F-087: `SFTPClient` 类定义于 `sftp.py:3829`，通过 `SSHClientConnection.start_sftp_client()` 协程创建。
- F-088: SFTP 协议版本范围为 3 到 6（`MIN_SFTP_VERSION = 3`，`MAX_SFTP_VERSION = 6`，sftp.py:172-173），`start_sftp_client()` 默认版本为 3。
- F-089: `SFTPClient.get()` 协程定义于 `sftp.py:4118`，从远程下载文件到本地。
- F-090: `SFTPClient.put()` 协程定义于 `sftp.py:4229`，从本地上传文件到远程。
- F-091: `SFTPClient.mget()` 定义于 `sftp.py:4455`，`mput()` 定义于 `sftp.py:4478`，支持通配符批量传输。
- F-092: `SFTPClient.copy()` 定义于 `sftp.py:4340`，`mcopy()` 定义于 `sftp.py:4501`，`remote_copy()` 定义于 `sftp.py:4525`。
- F-093: `SFTPClient.stat()` 协程定义于 `sftp.py:5033`，`lstat()` 定义于 `sftp.py:5062`，`setstat()` 定义于 `sftp.py:5088`。
- F-094: `SFTPClient.chmod()` 协程定义于 `sftp.py:5211`，`chown()` 定义于 `sftp.py:5165`（重载支持 uid/gid 或 owner/group 字符串）。
- F-095: `SFTPClient.mkdir()` 协程定义于 `sftp.py:5639`，`rmdir()` 定义于 `sftp.py:5660`，`makedirs()` 定义于 `sftp.py:4639`。
- F-096: `SFTPClient.listdir()` 协程定义于 `sftp.py:5618`，返回文件名序列；`readdir()` 定义于 `sftp.py:5589`，返回 `SFTPName` 序列。
- F-097: `SFTPClient.scandir()` 异步迭代器定义于 `sftp.py:5544`，产出 `SFTPName` 对象。
- F-098: `SFTPClient.rename()` 协程定义于 `sftp.py:5474`，`posix_rename()` 定义于 `sftp.py:5513`。
- F-099: `SFTPClient.remove()` 定义于 `sftp.py:5453`，`unlink()` 定义于 `sftp.py:5469`，`rmtree()` 定义于 `sftp.py:4701`。
- F-100: `SFTPClient.open()` 协程定义于 `sftp.py:4806`，返回 `SFTPClientFile` 对象；`open56()` 定义于 `sftp.py:4938`，使用 SFTP v5/v6 风格打开。
- F-101: `SFTPClientFile` 类定义于 `sftp.py:3310`，支持 `read()`（line 3401）、`write()`（line 3530）、`seek()`（line 3583）、`tell()`（line 3621）、`stat()`（line 3638）、`close()`（line 3821）。
- F-102: `SFTPClientFile.read_parallel()` 协程定义于 `sftp.py:3470`，支持并行读取优化。
- F-103: `SFTPClientFile` 支持 `chmod()`（line 3758）、`chown()`（line 3722）、`utime()`（line 3774）、`truncate()`（line 3695）、`fsync()`（line 3813）、`lock()`/`unlock()`（line 3797/3805）。
- F-104: `SFTPAttrs` 是 `Record` 子类，定义于 `sftp.py:1658`，镜像 POSIX stat 属性。
- F-105: `SFTPName` 是 `Record` 子类，定义于 `sftp.py:2107`，包含 `filename` 和 `attrs` 字段。
- F-106: `SFTPLimits` 是 `Record` 子类，定义于 `sftp.py:2159`，描述 SFTP 协议限制。
- F-107: `SFTPVFSAttrs` 定义于 `sftp.py:2028`，`statvfs()` 返回此类型。
- F-108: `SFTPClient.truncate()` 定义于 `sftp.py:5135`，`utime()` 定义于 `sftp.py:5236`，`statvfs()` 定义于 `sftp.py:5114`。
- F-109: `SFTPClient.exists()` 定义于 `sftp.py:5271`，`lexists()` 定义于 `sftp.py:5284`，`isdir()` 定义于 `sftp.py:5413`，`isfile()` 定义于 `sftp.py:5426`，`islink()` 定义于 `sftp.py:5439`。
- F-110: `SFTPClient.getcwd()` 定义于 `sftp.py:5769`，`chdir()` 定义于 `sftp.py:5784`，`realpath()` 定义于 `sftp.py:5693`。
- F-111: `SFTPClient.readlink()` 定义于 `sftp.py:5803`，`symlink()` 定义于 `sftp.py:5827`，`link()` 定义于 `sftp.py:5854`。
- F-112: `SFTPClient.glob()` 定义于 `sftp.py:4564`，`glob_sftpname()` 定义于 `sftp.py:4611`。
- F-113: `SFTPClient.exit()` 定义于 `sftp.py:5880`，`wait_closed()` 协程定义于 `sftp.py:5890`。
- F-114: `SFTPClient` 支持异步上下文管理器协议（`__aenter__` / `__aexit__`，sftp.py:3846-3858）。
- F-115: SFTP 异常层次：`SFTPError`（sftp.py:944）为基类，下含 `SFTPEOFError`、`SFTPNoSuchFile`、`SFTPPermissionDenied`、`SFTPFailure`、`SFTPNoConnection`、`SFTPConnectionLost`、`SFTPOpUnsupported` 等 30+ 子类。
- F-116: `SFTPServer` 类定义于 `sftp.py:6991`，`SFTPServerFS` 定义于 `sftp.py:8153`，`SFTPServerFile` 定义于 `sftp.py:8099`。

## SSHKey 密钥管理

- F-117: `SSHKey` 类定义于 `public_key.py:247`，是所有密钥类型的基类。
- F-118: `generate_private_key()` 模块级函数定义于 `public_key.py:3065`，签名为 `def generate_private_key(alg_name, comment=None, **kwargs) -> SSHKey`。
- F-119: 支持的密钥算法包括：`ssh-dss`、`ssh-rsa`、`ecdsa-sha2-nistp256/384/521`、`ecdsa-sha2-1.3.132.0.10`、`ssh-ed25519`、`ssh-ed448`、`sk-ecdsa-sha2-nistp256@openssh.com`、`sk-ssh-ed25519@openssh.com`。
- F-120: RSA 密钥默认 2048 位，公钥指数 65537，可通过 `key_size` 和 `exponent` 参数调整。
- F-121: `SSHKey.generate()` 类方法定义于 `public_key.py:268`，基类抛出 `NotImplementedError`，由子类（`_RSAKey`/`_DSAKey`/`_ECKey`/`_EdKey`/`_SKKey`）实现。
- F-122: `import_private_key()` 函数定义于 `public_key.py:3165`，`import_public_key()` 定义于 `public_key.py:3204`，`import_certificate()` 定义于 `public_key.py:3232`。
- F-123: `read_private_key()` 函数定义于 `public_key.py:3292`，`read_public_key()` 定义于 `public_key.py:3325`，`read_certificate()` 定义于 `public_key.py:3347`。
- F-124: `read_private_key_list()` 定义于 `public_key.py:3365`，`read_public_key_list()` 定义于 `public_key.py:3401`，支持读取多密钥文件。
- F-125: `load_keypairs()` 函数定义于 `public_key.py:3442`，`load_public_keys()` 定义于 `public_key.py:3682`，`load_certificates()` 定义于 `public_key.py:3737`。
- F-126: `load_resident_keys()` 定义于 `public_key.py:3829`，从 FIDO2 安全密钥加载 resident key。
- F-127: `SSHKey.export_private_key()` 方法定义于 `public_key.py:1042`，签名为 `export_private_key(format_name='openssh', passphrase=None, ...)`。
- F-128: `SSHKey.export_public_key()` 方法定义于 `public_key.py:1223`，默认格式为 `'openssh'`。
- F-129: `SSHKey.write_private_key()` 定义于 `public_key.py:1282`，`write_public_key()` 定义于 `public_key.py:1299`，`append_private_key()` 定义于 `public_key.py:1316`，`append_public_key()` 定义于 `public_key.py:1333`。
- F-130: `SSHKey.get_algorithm()` 定义于 `public_key.py:415`，返回算法名称字符串。
- F-131: `SSHKey.get_fingerprint()` 定义于 `public_key.py:512`，默认使用 SHA256 哈希。
- F-132: `SSHKey.convert_to_public()` 定义于 `public_key.py:634`，返回只含公钥部分的新 `SSHKey` 实例。
- F-133: `SSHKey.sign()` 定义于 `public_key.py:567`，`verify()` 定义于 `public_key.py:579`，`sign_ssh()` 定义于 `public_key.py:556`，`verify_ssh()` 定义于 `public_key.py:561`。
- F-134: `KeyGenerationError`、`KeyImportError`、`KeyExportError` 均继承 `ValueError`，定义于 `public_key.py:202/214/223`。

## SSHCertificate 证书

- F-135: `SSHCertificate` 类定义于 `public_key.py:1351`。
- F-136: `SSHOpenSSHCertificate` 定义于 `public_key.py:1542`，`SSHOpenSSHCertificateV01` 定义于 `public_key.py:1784`。
- F-137: `SSHX509Certificate` 定义于 `public_key.py:1848`，`SSHX509CertificateChain` 定义于 `public_key.py:1952`。
- F-138: `SSHKey.generate_user_certificate()` 定义于 `public_key.py:649`，`generate_host_certificate()` 定义于 `public_key.py:773`。
- F-139: `SSHKey.generate_x509_user_certificate()` 定义于 `public_key.py:834`，`generate_x509_host_certificate()` 定义于 `public_key.py:905`，`generate_x509_ca_certificate()` 定义于 `public_key.py:975`。
- F-140: `SSHCertificate.export_certificate()` 定义于 `public_key.py:1454`，`write_certificate()` 定义于 `public_key.py:1505`，`append_certificate()` 定义于 `public_key.py:1523`。
- F-141: `SSHCertificate.validate()` 方法定义于 `public_key.py:1765`（OpenSSH 证书验证）。

## 认证体系

- F-142: 认证框架核心类 `Auth` 定义于 `auth.py:75`，`ClientAuth` 定义于 `auth.py:116`，`ServerAuth` 定义于 `auth.py:528`。
- F-143: 客户端支持的认证方法：none（`_ClientNullAuth`）、GSSAPI-KEX（`_ClientGSSKexAuth`）、GSSAPI-MIC（`_ClientGSSMICAuth`）、hostbased（`_ClientHostBasedAuth`）、publickey（`_ClientPublicKeyAuth`）、keyboard-interactive（`_ClientKbdIntAuth`）、password（`_ClientPasswordAuth`）。
- F-144: `register_auth_method()` 函数定义于 `auth.py:948`，注册认证方法处理器。
- F-145: `get_supported_client_auth_methods()` 定义于 `auth.py:957`，返回客户端支持的认证方法字节序列。
- F-146: `SSHClient` 回调类定义于 `client.py:35`，定义了 `connection_made()`、`connection_lost()`、`password_auth_requested()`、`public_key_auth_requested()`、`kbdint_auth_requested()`、`kbdint_challenge_received()`、`auth_banner_received()`、`auth_completed()` 等回调方法。
- F-147: `SSHServer` 回调类定义于 `server.py:66`，定义了 `begin_auth()`、`auth_completed()`、`password_auth_supported()`、`validate_gss_principal()`、`validate_host_based_request()`、`validate_public_key()`、`validate_password()`、`kbdint_auth_supported()`、`session_requested()`、`connection_requested()`、`server_requested()` 等回调。
- F-148: `SSHAuthorizedKeys` 类从 `auth_keys.py` 导出，`import_authorized_keys()` 和 `read_authorized_keys()` 函数解析 OpenSSH authorized_keys 文件。
- F-149: `SSHKnownHosts` 类定义于 `known_hosts.py:117`，`import_known_hosts()` 定义于 `known_hosts.py:285`，`read_known_hosts()` 定义于 `known_hosts.py:302`，`match_known_hosts()` 定义于 `known_hosts.py:327`。

## SSHAgent

- F-150: `SSHAgentClient` 类定义于 `agent.py:183`，`SSHAgentKeyPair` 定义于 `agent.py:108`。
- F-151: `connect_agent()` 协程定义于 `agent.py:634`，签名为 `async def connect_agent(agent_path='') -> SSHAgentClient`。
- F-152: 平台相关实现：`agent_unix.py`（UNIX domain socket）、`agent_win32.py`（Windows named pipe / Pageant）。

## 端口转发

- F-153: `SSHForwarder` 基类定义于 `forward.py:41`，继承 `asyncio.BaseProtocol`。
- F-154: `SSHLocalForwarder` 定义于 `forward.py:192`，`SSHLocalPortForwarder` 定义于 `forward.py:229`，`SSHLocalPathForwarder` 定义于 `forward.py:245`。
- F-155: `SSHListener` 基类定义于 `listener.py:52`，提供 `close()`、`wait_closed()`、`get_port()` 方法。
- F-156: `SSHClientListener` 定义于 `listener.py:114`，`SSHTCPClientListener` 定义于 `listener.py:150`，`SSHUNIXClientListener` 定义于 `listener.py:199`。
- F-157: `SSHForwardListener` 定义于 `listener.py:234`，用于本地端口转发监听器。
- F-158: SOCKS 转发器 `SSHSOCKSForwarder` 定义于 `socks.py`。

## SCP

- F-159: `scp()` 协程函数定义于 `scp.py:931`，签名为 `async def scp(srcpaths, dstpath=None, *, preserve=False, recurse=False, block_size=262144, progress_handler=None, error_handler=None, **kwargs) -> None`。
- F-160: SCP 默认块大小为 256 KiB（`_SCP_BLOCK_SIZE`，scp.py）。
- F-161: `scp()` 的源/目标路径可以是本地路径字符串，或 `(conn, path)` 元组引用远程文件，或 `'host:path'` 字符串自动建立连接。
- F-162: `run_scp_server()` 函数定义于 `scp.py:1129`，在服务端 SFTPServer 上运行 SCP 协议处理器。

## 加密子包

- F-163: `crypto/` 子包封装 `cryptography` 库，导出 `BasicCipher`、`GCMCipher`、`ChachaCipher`、`register_cipher`、`get_cipher_params`。
- F-164: `crypto/` 导出 `RSAPrivateKey`/`RSAPublicKey`（rsa.py）、`DSAPrivateKey`/`DSAPublicKey`（dsa.py）、`ECDSAPrivateKey`/`ECDSAPublicKey`/`ECDH`（ec.py）、`EdDSAPrivateKey`/`EdDSAPublicKey`/`Curve25519DH`/`Curve448DH`（ed.py）。
- F-165: `crypto/` 支持后量子密钥交换：`MLKEM` 和 `SNTRUP`（pq.py），通过 `mlkem_available`/`sntrup_available` 检测可用性。
- F-166: `crypto/` 导出 `DH`（dh.py）、`pbkdf2_hmac`（kdf.py）、`umac32/64/96/128`（umac.py，可选）。
- F-167: `crypto/` 可选支持 X.509 证书：`X509Certificate`、`X509Name`、`X509NamePattern`、`generate_x509_certificate`、`import_x509_certificate`（x509.py）。
- F-168: 加密算法通过注册模式管理：`encryption.py:34` 维护 `_enc_algs` 和 `_default_enc_algs` 列表，`register_cipher()` 添加算法。

## 其他模块

- F-169: `SSHLineEditorChannel` 从 `editor.py` 导出，提供行编辑功能通道。
- F-170: `SSHSubprocessReadPipe`、`SSHSubprocessWritePipe`、`SSHSubprocessProtocol`、`SSHSubprocessTransport` 从 `subprocess.py` 导出，桥接 asyncio subprocess。
- F-171: `set_log_level()` 定义于 `logging.py:177`，`set_sftp_log_level()` 定义于 `logging.py:196`，`set_debug_level()` 定义于 `logging.py:215`。
- F-172: `set_default_skip_rsa_key_validation()` 从 `rsa.py` 导出，用于跳过 RSA 密钥验证（性能优化）。
- F-173: `load_pkcs11_keys()` 从 `pkcs11.py` 导出，支持 PKCS#11 硬件安全模块。
- F-174: `SSHSocketSessionFactory`、`SSHServerSessionFactory`、`SFTPServerFactory` 从 `stream.py` 导出。
- F-175: `SSHServerProcessFactory` 从 `process.py` 导出，用于自定义服务端进程创建。
- F-176: `SSHAcceptor` 类定义于 `connection.py:759`，包装 `asyncio.AbstractServer`，支持异步上下文管理器。
- F-177: 异常类层次：`Error`（misc.py）为基类，下含 `DisconnectError`、`ChannelOpenError`、`ChannelListenError`、`ConnectionLost`、`CompressionError`、`HostKeyNotVerifiable`、`KeyExchangeFailed`、`PermissionDenied`、`ProtocolError`、`ProtocolNotSupported`、`ServiceNotAvailable`、`PasswordChangeRequired` 等。
- F-178: `BreakReceived`、`SignalReceived`、`TerminalSizeChanged` 异常定义于 `misc.py`，用于在进程中传递信号事件。
- F-179: `DataType` 枚举从 `session.py` 导出，`SSHClientSession`、`SSHServerSession`、`SSHTCPSession`、`SSHUNIXSession`、`SSHTunTapSession` 均从 `session.py` 导出。
- F-180: `SSHClientConnectionOptions` 定义于 `connection.py:7599`，`SSHServerConnectionOptions` 定义于 `connection.py:8478`，分别管理客户端和服务端连接配置。

## 事实统计

- 总计 **180 条**编号事实（F-001 ~ F-180）。
