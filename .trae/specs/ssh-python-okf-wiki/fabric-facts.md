# fabric v4.0.0 源码事实清单

> 基于 `external/libs/fabric/fabric/` 逐模块阅读提取，共 60 条事实。

## __init__.py — 公开 API

- F-001: [__init__] `__version__` 从 `_version.py` 导入，值为 `"4.0.0"`
- F-002: [__init__] 公开导出 `Config`、`Connection`（来自 connection.py）
- F-003: [__init__] 公开导出 `Remote`、`RemoteShell`、`Result`（来自 runners.py）
- F-004: [__init__] 公开导出 `Group`、`SerialGroup`、`ThreadingGroup`、`GroupResult`（来自 group.py）
- F-005: [__init__] 公开导出 `task`、`Task`（来自 tasks.py）
- F-006: [__init__] 公开导出 `Executor`（来自 executor.py）
- F-007: [__init__] `OpenSSHAuthStrategy` 通过 try/except ImportError 条件导出，依赖 Paramiko 3.2+ API

## connection.py — Connection 类

- F-008: [connection] `Connection` 继承 `invoke.Context`，类定义在 connection.py:49
- F-009: [connection] `Connection.__init__(host, user=None, port=None, config=None, gateway=None, forward_agent=None, connect_timeout=None, connect_kwargs=None, inline_ssh_env=None, remainder=None)` 接受 10 个参数
- F-010: [connection] 构造函数内部创建 `paramiko.SSHClient()` 实例并调用 `set_missing_host_key_policy(AutoAddPolicy())`
- F-011: [connection] `from_v1(cls, env, **kwargs)` 类方法，从 Fabric 1.x 的 env 字典构造 Connection
- F-012: [connection] `derive_shorthand(host_string)` 模块级函数，解析 `user@host:port` 格式；IPv6 地址（含多个 `:`）不解析端口
- F-013: [connection] `open()` 方法发起 SSH 连接，若 `is_connected` 为 True 则短路返回；3.1 版本起返回 `SSHClient.connect()` 的返回值
- F-014: [connection] `open()` 拒绝 `connect_kwargs` 中同时出现 `hostname`/`port`/`username`（抛出 ValueError），也拒绝同时设置 `timeout` 和 `connect_timeout`
- F-015: [connection] `open_gateway()` 方法：gateway 为字符串时返回 `ProxyCommand` 对象；gateway 为 Connection 时调用其 `transport.open_channel(kind="direct-tcpip")` 返回 Channel
- F-016: [connection] `close()` 关闭 SFTP 会话（`_sftp`）和 SSH 客户端；若启用 agent 转发还关闭 `_agent_handler`
- F-017: [connection] `create_session()` 被 `@opens` 装饰器修饰，调用 `transport.open_session()`；若 `forward_agent` 为 True 则包装 `AgentRequestHandler(channel)`
- F-018: [connection] `run(command, **kwargs)` 被 `@opens` 装饰，通过 `_remote_runner()` 创建 Remote runner 后调用 `self._run()`
- F-019: [connection] `sudo(command, **kwargs)` 被 `@opens` 装饰，通过 `_remote_runner()` 创建 Remote runner 后调用 `self._sudo()`
- F-020: [connection] `shell(**kwargs)` 被 `@opens` 装饰，使用 `RemoteShell` runner；仅允许 `encoding`/`env`/`in_stream`/`replace_env`/`watchers` 五个 kwargs；强制 `pty=True`
- F-021: [connection] `local(*args, **kwargs)` 调用 `super().run()`（即 invoke.Context.run），执行本地命令
- F-022: [connection] `sftp()` 被 `@opens` 装饰，memoize 模式：首次调用 `client.open_sftp()`，后续返回缓存的 `_sftp`
- F-023: [connection] `get(*args, **kwargs)` 创建 `Transfer(self)` 并委托其 `get()` 方法
- F-024: [connection] `put(*args, **kwargs)` 创建 `Transfer(self)` 并委托其 `put()` 方法
- F-025: [connection] `forward_local(local_port, remote_port=None, remote_host="localhost", local_host="localhost")` 是上下文管理器，内部创建 `TunnelManager` 线程
- F-026: [connection] `forward_remote(remote_port, local_port=None, remote_host="127.0.0.1", local_host="localhost")` 是上下文管理器，通过 `transport.request_port_forward()` 注册回调
- F-027: [connection] `is_connected` 属性返回 `self.transport.active if self.transport else False`
- F-028: [connection] `resolve_connect_kwargs(connect_kwargs)` 合并构造函数 kwargs、config kwargs 和 SSH config 的 IdentityFile，key_filename 按 config→constructor→ssh_config 顺序合并
- F-029: [connection] `get_gateway()` 解析 SSH config 的 `proxyjump`（反向遍历跳点创建 Connection 链）或 `proxycommand`（返回字符串），否则回退到 `self.config.gateway`
- F-030: [connection] Connection 实现了 `__eq__`、`__lt__`、`__hash__`，identity 元组为 `(host, user, port)`
- F-031: [connection] `@opens` 装饰器定义在模块级别（connection.py:20），在方法执行前调用 `self.open()`
- F-032: [connection] SSH config 的 `hostname` 指令会覆盖 `self.host`，原始值保存在 `self.original_host`

## config.py — Config 类

- F-033: [config] `Config` 继承 `invoke.config.Config`，`prefix = "fabric"`（环境变量前缀为 FABRIC_）
- F-034: [config] `Config.__init__` 接受 `ssh_config`、`runtime_ssh_path`、`system_ssh_path`（默认 `/etc/ssh/ssh_config`）、`user_ssh_path`（默认 `~/.ssh/config`）、`lazy` 等 Fabric 特有参数
- F-035: [config] `set_runtime_ssh_path(path)` 设置 `_runtime_ssh_path`；若设置则跳过系统和用户 SSH config 文件
- F-036: [config] `load_ssh_config()` 先检查 `ssh_config_path` 配置值更新 runtime 路径，然后调用 `_load_ssh_files()`
- F-037: [config] `_load_ssh_files()` 优先级：runtime 路径（若存在文件不存在则抛 FileNotFoundError）> user + system 路径（文件不存在静默跳过）
- F-038: [config] `from_v1(cls, env, **kwargs)` 类方法，从 Fabric 1.x env 字典生成 Config，映射 pty/gateway/forward_agent/key_filename/allow_agent/sudo_password/timeout/warn_only 等
- F-039: [config] `global_defaults()` 静态方法扩展 invoke 默认值，新增 `authentication`（含 identities/strategy_class）、`connect_kwargs`、`forward_agent`、`gateway`、`inline_ssh_env`（默认 True）、`load_ssh_configs`（默认 True）、`port`（默认 22）、`runners`（remote=Remote, remote_shell=RemoteShell）、`ssh_config_path`、`timeouts.connect`、`user`（通过 `get_local_user()` 获取）
- F-040: [config] `clone()` 方法复制 `_runtime_ssh_path`/`_system_ssh_path`/`_user_ssh_path` 属性，并调用 `load_ssh_config()`
- F-041: [config] `_clone_init_kwargs()` 通过深拷贝 `base_ssh_config._config` 传递 SSHConfig 数据，避免二次加载文件

## group.py — Group 系列

- F-042: [group] `Group` 继承 `list`，`__init__(*hosts, **kwargs)` 从主机字符串列表创建 Connection 对象列表
- F-043: [group] `Group.from_connections(cls, connections)` 类方法，从已有 Connection 对象列表创建 Group
- F-044: [group] `Group._do(method, *args, **kwargs)` 是抽象方法，抛出 `NotImplementedError`
- F-045: [group] `Group.run()`/`sudo()`/`put()`/`get()` 均委托 `_do()`；`get()` 默认 local 参数为 `"{host}/"`
- F-046: [group] `SerialGroup._do()` 串行遍历连接，收集结果到 `GroupResult`，任何异常则最终抛出 `GroupException`
- F-047: [group] `ThreadingGroup._do()` 为每个 Connection 创建 `ExceptionHandlingThread`，通过 `Queue` 收集结果，从线程 exception() 获取异常
- F-048: [group] `GroupResult` 继承 `dict`，有 `succeeded` 和 `failed` 两个 property，分别返回非异常和异常值的子字典
- F-049: [group] `thread_worker(cxn, queue, method, args, kwargs)` 模块级函数，调用 `getattr(cxn, method)` 并将 `(cxn, result)` 放入队列

## runners.py — Remote Runner

- F-050: [runners] `Remote` 继承 `invoke.Runner`，`__init__` 额外接受 `inline_env` 参数（默认 None，3.0 起默认行为为 True）
- F-051: [runners] `Remote.start(command, shell, env, timeout=None)` 创建 channel，若使用 PTY 则调用 `get_pty()` 并注册 SIGWINCH 处理器；env 处理：inline_env=True 时拼接 `export K=V &&` 前缀，否则调用 `channel.update_environment(env)`
- F-052: [runners] `Remote.send_start_message(command)` 调用 `self.channel.exec_command(command)`
- F-053: [runners] `RemoteShell` 继承 `Remote`，覆盖 `send_start_message` 调用 `self.channel.invoke_shell()`
- F-054: [runners] `Result` 继承 `invoke.runners.Result`，额外保存 `connection` 属性引用
- F-055: [runners] `Remote.returncode()` 调用 `self.channel.recv_exit_status()`
- F-056: [runners] `Remote.run()` 默认设置 `replace_env=True`（与 invoke.Local 的默认行为不同）

## transfer.py — Transfer 类

- F-057: [transfer] `Transfer.__init__(connection)` 保存 Connection 引用；`sftp` property 返回 `connection.sftp()`
- F-058: [transfer] `get(remote, local=None, preserve_mode=True)` 支持路径插值（host/user/port/dirname/basename）、自动创建目录、file-like 对象（使用 `getfo`）、preserve_mode 调用 `os.chmod`
- F-059: [transfer] `put(local, remote=None, preserve_mode=True)` 支持 file-like 对象（使用 `putfo`，保存/恢复文件指针位置）、自动检测远程是否为目录、preserve_mode 调用 `sftp.chmod`
- F-060: [transfer] `transfer.Result` 类包含 `local`/`orig_local`/`remote`/`orig_remote`/`connection` 五个属性

## tunnels.py — 隧道

- F-061: [tunnels] `TunnelManager` 继承 `invoke.util.ExceptionHandlingThread`，`__init__(local_host, local_port, remote_host, remote_port, transport, finished)`
- F-062: [tunnels] `TunnelManager._run()` 创建非阻塞监听 socket，接受连接后通过 `transport.open_channel("direct-tcpip", ...)` 创建通道并启动 `Tunnel` 线程
- F-063: [tunnels] `Tunnel` 继承 `ExceptionHandlingThread`，`__init__(channel, sock, finished)`，在 channel 和 socket 之间双向转发数据，chunk_size 均为 1024
- F-064: [tunnels] `Tunnel.read_and_write(reader, writer, chunk_size)` 从 reader recv 数据后 sendall 到 writer，recv 返回空数据时返回 True 表示结束

## executor.py — Executor

- F-065: [executor] `Executor` 继承 `invoke.Executor`
- F-066: [executor] `normalize_hosts(hosts)` 将混合的字符串/字典列表统一为字典列表（字符串转为 `dict(host=value)`）
- F-067: [executor] `expand_calls(calls, apply_hosts=True)` 将 Task 调用按主机展开为多个 `ConnectionCall`；CLI hosts（`-H`）优先级高于任务装饰器的 hosts
- F-068: [executor] `parameterize(call, connection_init_kwargs)` 将 Call 克隆为 `ConnectionCall`，附加 init_kwargs
- F-069: [executor] `dedupe(tasks)` 直接返回 tasks 不做去重（因为不同主机的"重复"任务实际是不同执行）

## tasks.py — Task/ConnectionCall

- F-070: [tasks] `Task` 继承 `invoke.Task`，`__init__` 额外提取 `hosts` kwarg
- F-071: [tasks] `task(*args, **kwargs)` 函数包装 `invoke.task`，默认设置 `klass=Task`
- F-072: [tasks] `ConnectionCall` 继承 `invoke.Call`，`__init__` 必需 `init_kwargs` 参数；`make_context(config, core_parse_result)` 创建 `Connection(**init_kwargs, config=config, remainder=...)`

## auth.py — 认证策略

- F-073: [auth] `OpenSSHAuthStrategy` 继承 `paramiko.auth_strategy.AuthStrategy`，`__init__(ssh_config, fabric_config, username)`
- F-074: [auth] `get_pubkeys()` 按 OpenSSH 顺序加载密钥：config certs → cli certs → agent keys（config 中存在的优先）→ cli keys → config keys；默认密钥位置 Windows 为 `~/ssh/`，Unix 为 `~/.ssh/`
- F-075: [auth] `get_sources()` 先 yield 公钥，再 yield `Password`（通过 `getpass` 提示输入）
- F-076: [auth] `authenticate()` 调用父类方法后在 finally 中调用 `self.agent.close()`

## main.py — CLI 入口

- F-077: [main] `Fab` 继承 `invoke.Program`，`print_version()` 额外打印 Paramiko 和 Invoke 版本
- F-078: [main] `Fab.core_args()` 添加 `-H/--hosts`、`-i/--identity`（list 类型）、`--list-agent-keys`、`--prompt-for-login-password`、`--prompt-for-passphrase`、`-S/--ssh-config`、`-t/--connect-timeout`（int 类型）参数
- F-079: [main] `make_program()` 返回配置了 name="Fabric"、executor_class=Executor、config_class=Config 的 `Fab` 实例

## exceptions.py

- F-080: [exceptions] `NothingToDo(Exception)` — 无主机可执行时抛出
- F-081: [exceptions] `GroupException(Exception)` — 包装 `GroupResult`，`self.result` 属性保存结果字典
- F-082: [exceptions] `InvalidV1Env(Exception)` — v1 env 数据缺失时抛出

## testing/ — 测试工具

- F-083: [testing.base] `Command` 数据类，字段：`cmd`/`out`/`err`/`in_`/`exit`/`waits`
- F-084: [testing.base] `ShellCommand(Command)` 覆盖 `expect_execution` 断言 `invoke_shell` 被调用
- F-085: [testing.base] `MockChannel(Mock)` 跟踪 recv/recv_stderr/sendall 状态，stdout/stderr 使用 BytesIO
- F-086: [testing.base] `Session` 类模拟单个远程连接会话，`generate_mocks()` 创建 Mock client/transport/channel；支持 `enable_sftp` 和 `transfers` 参数
- F-087: [testing.base] `MockRemote` 类 patch `fabric.connection.SSHClient`，支持 `expect()`/`expect_sessions()`/`start()`/`stop()`/`safety()`，可作为上下文管理器
- F-088: [testing.base] `MockSFTP` 类（3.2 起标记 deprecated），patch `fabric.transfer.os`、`fabric.connection.SSHClient`、`fabric.transfer.Path`
- F-089: [testing.fixtures] pytest fixtures：`connection`、`cxn`（别名）、`remote`、`remote_with_sftp`、`sftp`、`sftp_objs`、`transfer`、`client`

## util.py

- F-090: [util] `get_local_user()` 通过 `getpass.getuser()` 获取本地用户名，Windows 回退到 `win32api.GetUserName()`
- F-091: [util] `win32 = sys.platform == "win32"` 模块级常量
- F-092: [util] `log = logging.getLogger("fabric")`，导出 `debug` 函数
