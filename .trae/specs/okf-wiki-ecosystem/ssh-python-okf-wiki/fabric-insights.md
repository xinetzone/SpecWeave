# fabric v4.0.0 架构洞察

## 洞察 1：Connection 的双层架构——is-a Context + has-a SSHClient

**陈述**：`Connection` 同时使用继承和组合两种关系：它继承 `invoke.Context` 获得任务执行上下文能力（配置、run/sudo 机制），同时内部组合 `paramiko.SSHClient` 处理 SSH 协议细节。这种双层架构使得 fabric 能复用 invoke 的任务执行框架和 paramiko 的 SSH 实现。

**证据**：
- `class Connection(Context)` （connection.py:49）
- `client = SSHClient()` 在 `__init__` 中创建（connection.py:464）
- `run()` 调用 `self._run(self._remote_runner(), command, **kwargs)`，runner 通过 `self.context.create_session()` 获取 paramiko channel（runners.py:49）
- `local()` 直接调用 `super().run()`（connection.py:877），远程 `run()` 则通过 Remote runner 走 SSH channel

**反常识**：`Connection.run` 和 `Connection.local` 看起来是对等的远程/本地执行方法，但实现机制完全不同。`local` 只是父类方法的直接别名，而 `run` 被 `@opens` 装饰器拦截确保连接已建立，并通过自定义的 `Remote` runner 执行。更反直觉的是，`Connection` 重绑定了 `invoke.Context.run` 的语义——在 invoke 中 `run` 就是本地执行，在 fabric 中 `run` 变成远程执行，本地执行改名为 `local`。

**行动**：文档中明确区分三个命令执行入口（run/sudo/local）的底层路径，在 connection 概念文档中画出双层架构图，交叉引用 pyinvoke 的 Context 对象文档和 paramiko 的 SSHClient 文档。

---

## 洞察 2：Group 的模板方法模式与结果聚合的异常处理

**陈述**：`Group` 作为继承 `list` 的部分抽象类，通过 `_do()` 模板方法定义操作骨架，子类 `SerialGroup` 和 `ThreadingGroup` 分别实现串行和并行执行。结果聚合到 `GroupResult`（dict 子类），异常被捕获并存入结果字典而非立即抛出，最终统一包装为 `GroupException`。

**证据**：
- `Group._do()` 抛出 `NotImplementedError`（group.py:102）
- `SerialGroup._do()` 简单 for 循环，每个连接的异常存入 results（group.py:211-222）
- `ThreadingGroup._do()` 使用 `ExceptionHandlingThread` + `Queue`，从 `thread.exception()` 获取异常（group.py:238-283）
- `GroupResult.succeeded`/`.failed` property 通过 `_bifurcate()` 惰性分类（group.py:312-342）

**反常识**：Group 方法的返回值在"成功"和"部分失败"时类型不同——无异常时返回 `GroupResult`，有异常时抛出 `GroupException`，但异常对象内的 `.result` 属性仍然是同一个 `GroupResult`（其中失败连接映射到异常对象）。这意味着调用方不能用 try/except 简单跳过错误处理，必须检查 `GroupException.result` 才能获取部分成功的结果。

**行动**：在 group 概念文档中重点展示 try/except GroupException 模式，说明 succeeded/failed 的用法，给出部分失败场景的示例代码。

---

## 洞察 3：Remote Runner 的模板方法——SSH channel 如何适配 invoke Runner 抽象

**陈述**：`Remote` 继承 `invoke.Runner` 并实现其定义的模板方法：`start()` 创建 SSH channel 并发送命令，`read_proc_stdout/stderr()` 从 channel recv，`returncode()` 从 channel recv_exit_status，`kill()` 关闭 channel。invoke.Runner 的主循环（在 `run()` 中定义）调用这些方法，不感知底层是本地进程还是 SSH 通道。

**证据**：
- `Remote.start()` 调用 `self.context.create_session()` → `transport.open_session()`，然后 `channel.exec_command(command)`（runners.py:48-79）
- `Remote.read_proc_stdout()` 直接返回 `self.channel.recv(num_bytes)`（runners.py:85-86）
- `Remote.returncode()` 返回 `self.channel.recv_exit_status()`（runners.py:117-118）
- `RemoteShell` 覆盖 `send_start_message()` 调用 `invoke_shell()` 而非 `exec_command()`（runners.py:167-169）
- PTY 模式下注册 `signal.SIGWINCH` 处理器调用 `channel.resize_pty()`（runners.py:56-57, 139-145）

**反常识**：`inline_env=True`（3.0 起默认）不是通过 SSH 协议的 `update_environment` 传递环境变量，而是在命令字符串前拼接 `export K=V &&`。原因是大多数 sshd 的 `AcceptEnv` 配置受限，协议方式经常失败。这意味着环境变量值不会被 shell 转义，存在注入风险——文档明确警告"不执行任何 shell escaping"。

**行动**：在命令执行概念文档中说明 inline_ssh_env 的行为变化（2.x 默认 False → 3.x 默认 True），展示安全注意事项；交叉引用 paramiko Channel 文档和 pyinvoke Runner 文档。

---

## 洞察 4：Config 的多层合并与 SSH config 文件的独立体系

**陈述**：fabric Config 在 invoke Config 的六层配置体系（defaults/collection/system/user/runtime/overrides）之上，额外维护一套独立的 SSH config 体系（`paramiko.config.SSHConfig` 实例），两者并行存在但不合并。SSH config 通过 `base_ssh_config.lookup(host)` 按主机查询，在 Connection 初始化时即被读取并影响 host/user/port/gateway/forward_agent/connect_timeout 等属性。

**证据**：
- `Config.__init__` 创建独立的 `SSHConfig()` 对象存入 `base_ssh_config`（config.py:153-155）
- SSH config 加载路径：runtime_ssh_path > user_ssh_path + system_ssh_path（config.py:246-256）
- Connection.__init__ 中 `self.ssh_config = self.config.base_ssh_config.lookup(host)`（connection.py:412）
- SSH config 的 `hostname` 指令覆盖 `self.host`，`user`/`port` 作为默认值，`proxyjump`/`proxycommand` 影响 gateway（connection.py:417-535）
- `prefix = "fabric"` 使环境变量前缀为 `FABRIC_`（config.py:39），区别于 invoke 的 `INVOKE_`

**反常识**：SSH config 文件的数据不进入 invoke 的配置合并体系。它不经过 merge_dicts，不参与 config 层级优先级，而是作为独立的 per-host 查询表存在。这意味着你不能通过 `config["user"]` 访问 SSH config 中的 User 值——它只在 Connection 构造时被读取并写入 Connection 属性。此外，`clone()` 方法通过深拷贝 `_config` 内部字典来传递 SSHConfig 数据，这是访问了 paramiko 的私有属性。

**行动**：在配置概念文档中画双层配置体系图（invoke 六层 vs SSH config 独立层），明确哪些参数来自哪个体系，给出优先级顺序说明。

---

## 洞察 5：跳板机网关的递归 Connection 链与 direct-tcpip 通道

**陈述**：fabric 支持两种网关模式：ProxyCommand（字符串命令，通过 paramiko ProxyCommand 创建子进程 socket）和 ProxyJump（Connection 对象，递归创建网关连接链）。`get_gateway()` 解析 SSH config 的 `ProxyJump hop1,hop2,hop3` 时反向遍历跳点，从最内层开始逐层创建 Connection 并设置外层的 gateway。`open_gateway()` 在 Connection gateway 上调用 `transport.open_channel(kind="direct-tcpip")` 返回 SSH channel 作为 socket。

**证据**：
- `get_gateway()` 中 `hops = reversed(self.ssh_config["proxyjump"].split(","))`（connection.py:513）
- 反向遍历：每个 hop 创建 `Connection(hop, **kwargs)`，前一个（更内层）作为当前的 gateway（connection.py:515-529）
- 自代理检测：`if self.derive_shorthand(hop)["host"] == self.host: return None`（connection.py:521-522）
- `open_gateway()` 对 Connection 类型 gateway：`self.gateway.transport.open_channel(kind="direct-tcpip", dest_addr=(host, port), src_addr=("", 0))`（connection.py:707-714）
- `TunnelManager` 也使用相同的 `open_channel("direct-tcpip", ...)` 机制创建本地转发隧道（tunnels.py:77-79）

**反常识**：ProxyJump 的跳点链是反向构建的——配置写 `hop1,hop2,hop3`（用户→hop1→hop2→hop3→目标），但代码从 hop3 开始创建 Connection，hop2 的 gateway 是 hop3 的 Connection，hop1 的 gateway 是 hop2 的 Connection，最终目标连接的 gateway 是 hop1。这种自底向上的构建保证了内层连接先建立。另外，自代理检测只比较 host 不比较 user/port，在通配符 SSH config 场景下可能产生误判。

**行动**：在隧道/跳板机概念文档中画出多跳 ProxyJump 的连接建立顺序图，说明 direct-tcpip channel 的角色，给出嵌套跳板机的示例代码，交叉引用 paramiko 端口转发文档。
