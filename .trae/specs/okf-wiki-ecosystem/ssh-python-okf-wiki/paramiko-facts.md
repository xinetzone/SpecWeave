# paramiko v5.0.0 事实清单

> R 阶段产出：从源码逐模块提取的编号事实，不含因果推断词。

## 包入口 (`__init__.py`)

- F-001: [__init__] __version__ 通过 importlib.metadata.version("paramiko") 获取 — `__init__.py:21`
- F-002: [__init__] 从 transport 模块导出 SecurityOptions、ServiceRequestingTransport、Transport 三个类 — `__init__.py:24-28`
- F-003: [__init__] 从 client 模块导出 AutoAddPolicy、MissingHostKeyPolicy、RejectPolicy、SSHClient、WarningPolicy — `__init__.py:29-35`
- F-004: [__init__] 从 auth_strategy 模块导出 AuthFailure、AuthStrategy、AuthResult、AuthSource、InMemoryPrivateKey、NoneAuth、OnDiskPrivateKey、Password、PrivateKey、SourceResult — `__init__.py:37-48`
- F-005: [__init__] 从 channel 模块导出 Channel、ChannelFile、ChannelStderrFile、ChannelStdinFile — `__init__.py:49-54`
- F-006: [__init__] 从 ssh_exception 模块导出 AuthenticationException、BadAuthenticationType、BadHostKeyException、ChannelException、ConfigParseError、CouldNotCanonicalize、IncompatiblePeer、MessageOrderError、PasswordRequiredException、ProxyCommandFailure、SSHException — `__init__.py:55-67`
- F-007: [__init__] 从 server 模块导出 ServerInterface、SubsystemHandler、InteractiveQuery — `__init__.py:68`
- F-008: [__init__] 导出 RSAKey、ECDSAKey、Ed25519Key 三种密钥类；key_classes 列表为 [RSAKey, Ed25519Key, ECDSAKey] — `__init__.py:69-71,115`
- F-009: [__init__] 从 sftp_client 导出 SFTP 和 SFTPClient；从 sftp_server 导出 SFTPServer；从 sftp_attr 导出 SFTPAttributes；从 sftp_handle 导出 SFTPHandle；从 sftp_si 导出 SFTPServerInterface；从 sftp_file 导出 SFTPFile — `__init__.py:73-78`
- F-010: [__init__] 从 agent 导出 Agent 和 AgentKey；从 pkey 导出 PKey、PublicBlob、UnknownKeyType；从 hostkeys 导出 HostKeys；从 config 导出 SSHConfig、SSHConfigDict；从 proxy 导出 ProxyCommand — `__init__.py:82-86`
- F-011: [__init__] 从 common 导出 AUTH_SUCCESSFUL、AUTH_PARTIALLY_SUCCESSFUL、AUTH_FAILED 三个认证返回码常量，以及 OPEN_SUCCEEDED 等通道打开结果码 — `__init__.py:88-97`
- F-012: [__init__] 从 sftp 导出 SFTP_OK、SFTP_EOF、SFTP_NO_SUCH_FILE、SFTP_PERMISSION_DENIED、SFTP_FAILURE、SFTP_BAD_MESSAGE、SFTP_NO_CONNECTION、SFTP_CONNECTION_LOST、SFTP_OP_UNSUPPORTED 九个状态码 — `__init__.py:99-109`

## 客户端 (`client.py`)

- F-013: [client] SSHClient 继承 ClosingContextManager，__init__ 初始化 _system_host_keys 和 _host_keys 为 HostKeys 实例，_policy 默认 RejectPolicy() — `client.py:47,67-77`
- F-014: [client] SSHClient.load_system_host_keys(filename=None) 从 ~/.ssh/known_hosts 加载只读主机密钥，filename 为 None 时静默忽略 IOError — `client.py:79-106`
- F-015: [client] SSHClient.load_host_keys(filename) 加载可写主机密钥文件，记录 _host_keys_filename — `client.py:108-125`
- F-016: [client] SSHClient.save_host_keys(filename) 将 _host_keys 写回文件，格式为 "hostname keytype base64-key" — `client.py:127-150`
- F-017: [client] SSHClient.set_missing_host_key_policy(policy) 接受类或实例，inspect.isclass 判断后实例化 — `client.py:170-190`
- F-018: [client] SSHClient.connect() 签名含 18 个参数：hostname、port=SSH_PORT(22)、username、password、pkey、key_filename、timeout、allow_agent=True、look_for_keys=True、compress=False、sock、banner_timeout、auth_timeout、channel_timeout、passphrase、disabled_algorithms、transport_factory、auth_strategy — `client.py:216-236`
- F-019: [client] connect() 认证优先级：pkey/key_filename → SSH agent → ~/.ssh/id_* 密钥 → password；auth_strategy 参数与旧认证参数互斥 — `client.py:245-264,308-317`
- F-020: [client] connect() 通过 _families_and_addresses 遍历 getaddrinfo 结果，IPv4/IPv6 双栈尝试，全部失败抛 NoValidConnectionsError — `client.py:192-214,386-387`
- F-021: [client] SSHClient.exec_command(command, bufsize=-1, timeout=None, get_pty=False, environment=None) 返回 (stdin, stdout, stderr) 三元组，通过 open_session→exec_command→makefile 实现 — `client.py:508-558`
- F-022: [client] SSHClient.invoke_shell(term="vt100", width=80, height=24, width_pixels=0, height_pixels=0, environment=None) 返回 Channel，内部调用 get_pty + invoke_shell — `client.py:560-588`
- F-023: [client] SSHClient.open_sftp() 委托 self._transport.open_sftp_client() 返回 SFTPClient — `client.py:590-596`
- F-024: [client] SSHClient.get_transport() 返回底层 Transport 对象 — `client.py:598-606`
- F-025: [client] SSHClient.close() 关闭 Transport 和 Agent，警告未显式关闭可能导致进程挂起 — `client.py:487-506`
- F-026: [client] MissingHostKeyPolicy 基类定义 missing_host_key(client, hostname, key) 接口，默认 pass — `client.py:786-804`
- F-027: [client] AutoAddPolicy.missing_host_key 将密钥添加到 _host_keys 并 save_host_keys — `client.py:807-822`
- F-028: [client] RejectPolicy.missing_host_key 抛出 SSHException("Server ... not found in known_hosts") — `client.py:825-840`
- F-029: [client] WarningPolicy.missing_host_key 调用 warnings.warn 但接受密钥 — `client.py:843-854`

## 传输层 (`transport.py`)

- F-030: [transport] Transport 继承 threading.Thread 和 ClosingContextManager，_PROTO_ID="2.0"，_CLIENT_ID="paramiko_{version}" — `transport.py:153,167-168`
- F-031: [transport] Transport.__init__ 接受 sock、default_window_size=DEFAULT_WINDOW_SIZE(2097152)、default_max_packet_size=DEFAULT_MAX_PACKET_SIZE(32768)、disabled_algorithms、server_sig_algs=True、strict_kex=True、packetizer_class — `transport.py:346-355`
- F-032: [transport] _preferred_ciphers 按优先级排列：aes128-ctr、aes192-ctr、aes256-ctr、aes128-cbc、aes192-cbc、aes256-cbc、3des-cbc、aes128-gcm@openssh.com、aes256-gcm@openssh.com — `transport.py:175-185`
- F-033: [transport] _preferred_macs 包含 hmac-sha2-256、hmac-sha2-512、etm 变体、hmac-sha1、hmac-md5 等 — `transport.py:186-195`
- F-034: [transport] _preferred_keys 按序：ssh-ed25519、ecdsa-sha2-nistp256/384/521、rsa-sha2-512/256、ssh-rsa — `transport.py:197-207`
- F-035: [transport] start_client(event=None, timeout=None) 启动客户端模式 SSH 协商 — `transport.py:650`
- F-036: [transport] start_server(event=None, server=None) 启动服务端模式，server 为 ServerInterface 实例 — `transport.py:708`
- F-037: [transport] open_session(timeout=None, window_size=None, max_packet_size=None) 打开 "session" 类型通道 — `transport.py:893`
- F-038: [transport] open_channel(kind, dest_addr=None, src_addr=None, timeout=None, window_size=None, max_packet_size=None) 通用通道打开方法 — `transport.py:970`
- F-039: [transport] request_port_forward(address, port, handler=None) 请求远程端口转发，返回绑定端口 — `transport.py:1065`
- F-040: [transport] cancel_port_forward(address, port) 取消远程端口转发 — `transport.py:1119`
- F-041: [transport] open_sftp_client() 调用 open_session + invoke_subsystem("sftp") 返回 SFTPClient.from_transport — `transport.py:1133`
- F-042: [transport] auth_none(username)、auth_password(username, password, event=None, fallback=True)、auth_publickey(username, key, event=None)、auth_interactive(username, handler, submethods="")、auth_interactive_dumb(username, handler=None, submethods="") 五种认证方法 — `transport.py:1440-1677`
- F-043: [transport] get_remote_server_key() 返回对端服务器公钥 PKey 对象 — `transport.py:866`
- F-044: [transport] is_active() 返回传输是否活跃；is_authenticated() 返回是否已认证 — `transport.py:883,1400`
- F-045: [transport] set_keepalive(interval) 设置保活间隔秒数 — `transport.py:1189`
- F-046: [transport] use_compression(compress=True) 启用 zlib 压缩 — `transport.py:1726`
- F-047: [transport] SecurityOptions 类提供 ciphers/digests/key_types/kex/compression 五个可读写属性，通过 _set 方法校验算法名 — `transport.py:3037-3110`
- F-048: [transport] ServiceRequestingTransport 继承 Transport，v3.2 新增，处理 MSG_SERVICE_ACCEPT，支持 ssh-userauth 服务请求 — `transport.py:3158-3188`
- F-049: [transport] global_request(kind, data=None, wait=True) 发送全局请求；accept(timeout=None) 在服务端模式接受入站通道 — `transport.py:1206,1243`
- F-050: [transport] add_server_key(key) 添加服务端主机密钥；load_server_moduli(filename=None) 静态方法加载 DH moduli 文件 — `transport.py:774,815`

## 通道 (`channel.py`)

- F-051: [channel] Channel 继承 ClosingContextManager，构造函数接受 chanid，初始化 in_buffer/in_stderr_buffer 为 BufferedPipe — `channel.py:75,92-134`
- F-052: [channel] open_only 装饰器检查 closed/eof_received/eof_sent/active 状态，未打开抛 SSHException("Channel is not open") — `channel.py:52-72`
- F-053: [channel] Channel.get_pty(term, width, height, width_pixels, height_pixels) 请求伪终端 — `channel.py:162`
- F-054: [channel] Channel.invoke_shell() 请求交互式 shell；exec_command(command) 执行单条命令；invoke_subsystem(subsystem) 请求子系统 — `channel.py:204,231,258`
- F-055: [channel] Channel.resize_pty(width=80, height=24, width_pixels=0, height_pixels=0) 调整终端尺寸 — `channel.py:284`
- F-056: [channel] Channel.recv(nbytes)、recv_stderr(nbytes)、send(s)、send_stderr(s)、sendall(s) 为核心 IO 方法 — `channel.py:683,727,781,801,825`
- F-057: [channel] Channel.recv_exit_status() 阻塞等待并返回远端进程退出码；exit_status_ready() 非阻塞检查 — `channel.py:362,377`
- F-058: [channel] Channel.makefile(*params)、makefile_stderr、makefile_stdin 返回 ChannelFile/ChannelStderrFile/ChannelStdinFile 文件对象 — `channel.py:869-913`
- F-059: [channel] Channel.request_x11(...) 请求 X11 转发；request_forward_agent(handler) 请求 agent 转发 — `channel.py:426,493`
- F-060: [channel] Channel.set_combine_stderr(combine) 控制 stderr 是否合并到 stdout；settimeout/gettimeout/setblocking 模拟 socket 接口 — `channel.py:549,586,604,612`
- F-061: [channel] ChannelFile 继承 BufferedFile，_read 从 channel.recv，_write 调用 channel.send；ChannelStderrFile 和 ChannelStdinFile 类似 — `channel.py:1347-1390`

## 认证 (`auth_handler.py`, `auth_strategy.py`)

- F-062: [auth_handler] AuthHandler 内部类管理认证状态机，持有 transport（weakref.proxy）、username、authenticated、auth_event 等属性 — `auth_handler.py:66-84`
- F-063: [auth_strategy] AuthSource 基类接受 username，定义 authenticate(transport) 抽象方法 — `auth_strategy.py:15-41`
- F-064: [auth_strategy] NoneAuth 调用 transport.auth_none；Password 接受 password_getter 惰性调用；PrivateKey mixin 调用 transport.auth_publickey — `auth_strategy.py:44-103`
- F-065: [auth_strategy] InMemoryPrivateKey 接受已解密 PKey；OnDiskPrivateKey 接受 source（"ssh-config"/"python-config"/"implicit-home"）、path、pkey — `auth_strategy.py:106-151`
- F-066: [auth_strategy] AuthResult 继承 list，元素为 SourceResult namedtuple(source, result)，持有 strategy 属性，__str__ 将空结果显示为 "success" — `auth_strategy.py:158-212`
- F-067: [auth_strategy] AuthFailure 继承 AuthenticationException，持有 result 属性；AuthStrategy.get_sources() 是子类主要覆盖点，authenticate() 遍历 sources 直到成功 — `auth_strategy.py:216-305`

## 密钥 (`pkey.py`, `rsakey.py`, `ed25519key.py`, `ecdsakey.py`)

- F-068: [pkey] PKey 基类定义 _CIPHER_TABLE 支持 AES-128-CBC、AES-256-CBC、DES-EDE3-CBC 三种私钥加密 — `pkey.py:127-146`
- F-069: [pkey] PKey.from_path(path, password=None) 类方法从文件路径加载密钥；from_type_string(key_type, key_bytes) 根据类型字符串构造密钥 — `pkey.py:153,228`
- F-070: [pkey] PKey.get_name() 返回算法名；get_bits() 返回密钥位数；can_sign() 返回是否可签名；get_fingerprint() 返回 MD5 指纹字节；get_base64() 返回 base64 编码公钥 — `pkey.py:332-416`
- F-071: [pkey] PKey.sign_ssh_data(data, algorithm=None) 签名；verify_ssh_sig(data, msg) 验签 — `pkey.py:417,434`
- F-072: [pkey] PKey.from_private_key_file(cls, filename, password=None) 和 from_private_key(cls, file_obj, password=None) 类方法加载私钥 — `pkey.py:447,471`
- F-073: [pkey] PKey.write_private_key_file(filename, password=None) 和 write_private_key(file_obj, password=None) 写出私钥 — `pkey.py:491,518`
- F-074: [pkey] PKey.load_certificate(value) 加载 OpenSSH 公钥证书；PublicBlob 类包含 type_、blob、comment，提供 from_file/from_string/from_message 构造器 — `pkey.py:892,944-1013`
- F-075: [rsakey] RSAKey.name="ssh-rsa"，HASHES 映射 rsa-sha2-256→SHA256、rsa-sha2-512→SHA512（含 cert 变体） — `rsakey.py:41-47`
- F-076: [ed25519key] Ed25519Key.name="ssh-ed25519"，使用 pynacl 的 nacl.signing.VerifyKey，仅支持 OpenSSH 格式私钥 — `ed25519key.py:30-68`
- F-077: [ecdsakey] ECDSAKey 使用 _ECDSACurve 和 _ECDSACurveSet 管理 nistp256/384/521 曲线，key_format_identifier 为 "ecdsa-sha2-{nist_name}" — `ecdsakey.py:41-79`
- F-078: [pkey] UnknownKeyType 异常类包含 key_type 和 key_bytes 属性 — `pkey.py:82-92`

## SFTP (`sftp_client.py`, `sftp_file.py`, `sftp_attr.py`, `sftp_server.py`, `sftp_si.py`, `sftp_handle.py`)

- F-079: [sftp_client] SFTPClient 继承 BaseSFTP 和 ClosingContextManager，__init__(sock) 接受已请求 sftp 子系统的 Channel，发送版本协商 — `sftp_client.py:90-138`
- F-080: [sftp_client] SFTPClient.from_transport(cls, t, window_size=None, max_packet_size=None) 类方法从 Transport 创建 SFTP 会话 — `sftp_client.py:140-170`
- F-081: [sftp_client] SFTPClient.listdir(path=".") 返回文件名列表；listdir_attr(path=".") 返回 SFTPAttributes 列表；listdir_iter(path=".", read_aheads=50) 返回迭代器 — `sftp_client.py:206,220,262`
- F-082: [sftp_client] SFTPClient.open(filename, mode="r", bufsize=-1) 返回 SFTPFile；remove(path)、rename(oldpath, newpath)、posix_rename(oldpath, newpath) — `sftp_client.py:326,387,402,425`
- F-083: [sftp_client] SFTPClient.mkdir(path, mode=o777)、rmdir(path)、stat(path)、lstat(path)、symlink(source, dest)、chmod(path, mode)、chown(path, uid, gid) — `sftp_client.py:447-560`
- F-084: [sftp_client] SFTPClient.utime(path, times)、truncate(path, size)、readlink(path)、normalize(path)、chdir(path=None)、getcwd() — `sftp_client.py:560-674`
- F-085: [sftp_client] SFTPClient.put(localpath, remotepath, callback=None, confirm=True)、putfo(fl, remotepath, ...)、get(remotepath, localpath, ...)、getfo(...) — `sftp_client.py:687,729,761,803`
- F-086: [sftp_file] SFTPFile 继承 BufferedFile，MAX_REQUEST_SIZE=32768，支持 pipelined 和 prefetch 预取模式 — `sftp_file.py:49-73`
- F-087: [sftp_attr] SFTPAttributes 镜像 os.stat 字段：st_size、st_uid、st_gid、st_mode、st_atime、st_mtime，另有 attr 字典和 filename 字段；from_stat(obj, filename=None) 类方法 — `sftp_attr.py:24-81`
- F-088: [sftp_attr] SFTPAttributes 定义 FLAG_SIZE=1、FLAG_UIDGID=2、FLAG_PERMISSIONS=4、FLAG_AMTIME=8、FLAG_EXTENDED=x80000000 — `sftp_attr.py:43-47`
- F-089: [sftp_server] SFTPServer 继承 BaseSFTP 和 SubsystemHandler，通过 set_subsystem_handler 注册为 "sftp" 处理器 — `sftp_server.py:86-100`
- F-090: [sftp_si] SFTPServerInterface 定义 open/list_folder/stat/lstat/remove/rename/mkdir/rmdir/chattr/chmod/chown/symlink/readlink/realpath 等回调接口，默认返回 SFTP_OP_UNSUPPORTED — `sftp_si.py:28-108`
- F-091: [sftp_handle] SFTPHandle 继承 ClosingContextManager，默认 close() 关闭 self.readfile/self.writefile；read(offset, length)、write(offset, data) 为子类覆盖点 — `sftp_handle.py:28-80`

## 服务端 (`server.py`)

- F-092: [server] ServerInterface 定义 check_channel_request(kind, chanid)，默认返回 OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED — `server.py:34-87`
- F-093: [server] ServerInterface 定义 get_allowed_auths(username)（默认 "password"）、check_auth_none/password/publickey/interactive — `server.py:89-200`
- F-094: [server] ServerInterface 定义 check_channel_pty_request、check_channel_shell_request、check_channel_exec_request、check_channel_subsystem_request 等通道回调 — `server.py:302-390`
- F-095: [server] ServerInterface 定义 check_port_forward_request、cancel_port_forward_request、check_global_request、check_channel_direct_tcpip_request — `server.py:238-492`
- F-096: [server] InteractiveQuery 类包含 name、instructions、prompts，add_prompt(prompt, echo=True) 方法 — `server.py:530-570`
- F-097: [server] SubsystemHandler 继承 threading.Thread，start_subsystem(name, transport, channel) 类方法启动子系统 — `server.py:579-651`

## 主机密钥 (`hostkeys.py`)

- F-098: [hostkeys] HostKeys 继承 MutableMapping，内部 _entries 列表存储 HostKeyEntry；add(hostname, keytype, key) 添加条目 — `hostkeys.py:33-70`
- F-099: [hostkeys] HostKeys.load(filename) 解析 OpenSSH known_hosts 格式；save(filename) 写回；lookup(hostname) 返回 keytype→PKey 字典 — `hostkeys.py:72-188`
- F-100: [hostkeys] HostKeys.check(hostname, key) 验证密钥是否匹配；hash_host(hostname, salt=None) 静态方法生成 HMAC-SHA1 哈希主机名 — `hostkeys.py:206-302`
- F-101: [hostkeys] HostKeyEntry 类表示 known_hosts 一行，from_line(line, lineno) 类方法解析，to_line() 序列化 — `hostkeys.py:312-380`

## Agent (`agent.py`)

- F-102: [agent] AgentSSH 基类定义 _connect(conn)、get_keys() 返回 AgentKey 元组、_close() — `agent.py:62-102`
- F-103: [agent] Agent 继承 AgentSSH，__init__ 自动连接本地 SSH agent（Unix socket 或 Windows pageant） — `agent.py:391`
- F-104: [agent] AgentKey 继承 PKey，持有 agent 引用和 comment，sign_ssh_data 通过 agent 签名 — `agent.py:425`
- F-105: [agent] AgentRequestHandler 在服务端模式处理 agent 请求转发；AgentLocalProxy/AgentRemoteProxy/AgentClientProxy/AgentServerProxy 实现 agent 转发代理链 — `agent.py:182-390`

## 其他模块

- F-106: [proxy] ProxyCommand 继承 ClosingContextManager，__init__(command_line) 通过 subprocess.Popen 启动代理命令，实现 send/recv/close/settimeout socket-like 接口 — `proxy.py:39-134`
- F-107: [file] BufferedFile 继承 ClosingContextManager，定义 SEEK_SET/CUR/END、FLAG_READ/WRITE/APPEND/BINARY/BUFFERED/LINE_BUFFERED/UNIVERSAL_NEWLINE 常量 — `file.py:31-49`
- F-108: [file] BufferedFile 提供 read/readline/readlines/write/writelines/close/flush/seek/tell/readinto 方法，_read/_write 为子类抽象方法 — `file.py:156-447`
- F-109: [config] SSHConfig 类解析 OpenSSH ssh_config 格式，from_text/from_file/from_path 类方法，lookup(hostname) 返回 SSHConfigDict — `config.py:45-99`
- F-110: [config] SSH_PORT=22 常量定义在 config.py — `config.py:42`
- F-111: [common] 认证返回码 AUTH_SUCCESSFUL=0、AUTH_PARTIALLY_SUCCESSFUL=1、AUTH_FAILED=2；通道打开结果码 OPEN_SUCCEEDED=0 至 OPEN_FAILED_RESOURCE_SHORTAGE=4 — `common.py:175-185`
- F-112: [common] DEFAULT_WINDOW_SIZE=64*2^15=2097152；DEFAULT_MAX_PACKET_SIZE=2^15=32768；MIN_WINDOW_SIZE=2^15；MIN_PACKET_SIZE=2^12 — `common.py:232-242`
- F-113: [common] io_sleep=0.01 秒，为 IO/select 通用休眠周期 — `common.py:230`
- F-114: [ssh_exception] SSHException 基类；AuthenticationException 子类；PasswordRequiredException、BadAuthenticationType（含 allowed_types）、PartialAuthentication、UnableToAuthenticate 继承 AuthenticationException — `ssh_exception.py:22-94`
- F-115: [ssh_exception] ChannelException 含 code/text 属性；BadHostKeyException 含 hostname/key/expected_key；IncompatiblePeer、ProxyCommandFailure、CouldNotCanonicalize、ConfigParseError、MessageOrderError 均继承 SSHException — `ssh_exception.py:97-254`
- F-116: [ssh_exception] NoValidConnectionsError 继承 socket.error，含 errors 属性（地址→异常字典） — `ssh_exception.py:178-220`
- F-117: [message] Message 类封装 SSH 消息的二进制读写，提供 get_int/get_string/get_binary/get_mpint/add_int/add_string/add_mpint 等方法 — `message.py:31`
- F-118: [packet] Packetizer 类处理 SSH 数据包的加密/解密/组包/拆包；NeedRekeyException 触发密钥重协商 — `packet.py:50,65`
- F-119: [buffered_pipe] BufferedPipe 类提供线程安全的字节缓冲，支持 read/readline/send/set_timeout；PipeTimeout 继承 IOError — `buffered_pipe.py:31-39`
- F-120: [compress] ZlibCompressor/ZlibDecompressor 类实现 zlib 压缩和解压 — `compress.py:26-35`
- F-121: [kex] 密钥交换算法类：KexCurve25519、KexNistp256/384/521、KexGexSHA256、KexGroup14SHA256、KexGroup16SHA512 — `kex_*.py`
- F-122: [util] ClosingContextManager 类提供 close() 和 context manager 协议；b(s)/u(s) 为字节/字符串转换；constant_time_bytes_eq 常量时间比较；get_logger(name) 获取日志器 — `util.py:274-329`
- F-123: [util] ClosingContextManager 同时被 SSHClient、Transport、Channel、SFTPClient、ProxyCommand、BufferedFile、SFTPHandle 等核心类继承 — `util.py:284`
