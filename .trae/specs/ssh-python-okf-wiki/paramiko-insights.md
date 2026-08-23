# paramiko v5.0.0 架构洞察

> I 阶段产出：3-5 个核心洞察，每个包含陈述、证据、反常识、行动四元组。

## 洞察一：三层 API 架构——高层门面与底层引擎的显式分离

**陈述**：paramiko 的 API 分为三个层次：`SSHClient` 是高层门面，封装连接/认证/通道打开的完整流程；`Transport` 是核心协议引擎，继承 `threading.Thread`，独立运行协议主循环；`Channel` 是多路复用的逻辑通道，模拟 socket 接口。SFTP 又在 Channel 之上叠加了 `SFTPClient`。

**证据**：
- `SSHClient.connect()` (`client.py:216`) 内部创建 Transport、调用 `start_client()`、主机密钥验证、`_auth()`，最后返回 None 或 AuthResult
- `Transport` 继承 `threading.Thread` (`transport.py:153`)，`run()` 方法 (`transport.py:2005`) 是协议主循环
- `Channel` 的 API 包含 recv/send/settimeout/setblocking/fileno 等 socket 模拟方法 (`channel.py:683-944`)
- `SFTPClient.from_transport()` (`sftp_client.py:141`) 通过 `open_session` + `invoke_subsystem("sftp")` 在 Channel 上构建 SFTP 会话

**反常识**：直觉上 SSHClient 可能是核心类，但实际上 Transport 才是协议实现的重心（3000+ 行），SSHClient 只是约 800 行的便捷封装。Transport 继承 threading.Thread 意味着每个连接独占一个线程，这在高并发场景下是重要的架构约束。

**行动**：文档应先讲 SSHClient 快速上手，再深入 Transport 底层机制；明确说明"90% 用户只需 SSHClient，高级场景才直接使用 Transport"。

## 洞察二：认证双轨制——legacy _auth 与 AuthStrategy 并存

**陈述**：paramiko 5.0 存在两套认证机制。旧路径 `SSHClient._auth()` 硬编码了"密钥→agent→本地密钥文件→密码"的尝试顺序；新路径 `AuthStrategy` 是基于生成器的可插拔认证框架，通过 `get_sources()` yield `AuthSource` 对象。两者通过 `connect(auth_strategy=...)` 参数切换，且互斥。

**证据**：
- `SSHClient.connect()` 中 `if auth_strategy is not None: return auth_strategy.authenticate(transport=t)` (`client.py:466-467`) 直接返回
- 旧路径 `_auth()` (`client.py:640-780`) 硬编码 pkey→key_filenames→agent→look_for_keys→password 的顺序
- `AuthStrategy.authenticate()` (`auth_strategy.py:262-305`) 遍历 `get_sources()` 生成器，每个 source 独立 try/except
- `AuthResult` 是 list 子类，记录每个 SourceResult(source, result)，成功结果为空列表表示"无更多认证方式需要"

**反常识**：`AuthResult` 中认证成功的标志是 transport auth 方法返回**空列表**（表示没有后续允许的认证方式了），而非返回 True 或某种成功对象。`__str__` 中空列表显示为 "success"。

**行动**：认证文档需同时介绍两套机制，明确标注 AuthStrategy 是面向未来的 API；解释 AuthResult 的空列表语义。

## 洞察三：ClosingContextManager 贯穿所有资源类

**陈述**：`ClosingContextManager`（定义于 `util.py:284`）是一个混入类，被 SSHClient、Transport、Channel、SFTPClient、SFTPFile、SFTPHandle、ProxyCommand、BufferedFile 等几乎所有持有网络/文件资源的类继承。它提供 `__enter__`/`__exit__` 协议，使所有这些类都支持 `with` 语句。

**证据**：
- `class SSHClient(ClosingContextManager)` (`client.py:47`)
- `class Transport(threading.Thread, ClosingContextManager)` (`transport.py:153`)
- `class Channel(ClosingContextManager)` (`channel.py:75`)
- `class SFTPClient(BaseSFTP, ClosingContextManager)` (`sftp_client.py:90`)
- `class SFTPFile(BufferedFile)` 且 `BufferedFile(ClosingContextManager)` (`sftp_file.py:49`, `file.py:31`)
- `class ProxyCommand(ClosingContextManager)` (`proxy.py:39`)

**反常识**：Transport 的 close() 不仅关闭 socket，还需要停止线程（`stop_thread()`），因为它继承自 threading.Thread。而 Channel.close() 需要发送 SSH_MSG_CHANNEL_CLOSE 协议消息。ClosingContextManager 的 `__exit__` 只是调用 `close()`，但各子类的 close() 语义差异很大。

**行动**：文档中所有代码示例均使用 `with` 语句；在高级模式文档中专门说明 close 的语义差异和显式关闭的重要性（源码警告未关闭可能导致进程挂起）。

## 洞察四：主机密钥策略的可插拔设计

**陈述**：主机密钥验证通过策略模式实现。`MissingHostKeyPolicy` 是抽象策略，`RejectPolicy`（默认）、`AutoAddPolicy`、`WarningPolicy` 是三个具体策略。`HostKeys` 类继承 `MutableMapping`，管理 known_hosts 文件，区分 system_host_keys（只读）和 host_keys（可写）。

**证据**：
- `SSHClient.__init__` 设置 `self._policy = RejectPolicy()` (`client.py:75`)
- `set_missing_host_key_policy()` 接受类或实例 (`client.py:188-190`)
- `AutoAddPolicy.missing_host_key` 调用 `client._host_keys.add()` + `save_host_keys()` (`client.py:813-816`)
- `HostKeys` 内部用 `_entries` 列表存储 `HostKeyEntry`，支持 hashed hostname (`|1|salt|hash` 格式) (`hostkeys.py:33,282-302`)
- connect() 中先查 system_host_keys 再查 host_keys，已知密钥还会调整 SecurityOptions.key_types 优先级 (`client.py:411-441`)

**反常识**：AutoAddPolicy 不仅在内存中添加密钥，还会立即写入磁盘文件（如果 _host_keys_filename 已设置）。这意味着使用 AutoAddPolicy 会在首次连接时自动修改 known_hosts 文件，这在自动化场景中可能不是期望行为。

**行动**：密钥文档中用对比表说明三种策略的行为差异和安全影响；强调 RejectPolicy 是安全默认值，AutoAddPolicy 存在 MITM 风险。

## 洞察五：SFTP 协议的请求-应答模型与流水线优化

**陈述**：SFTPClient 实现了 SSH 文件传输协议，每个操作是一个编号请求（CMD_OPEN/CMD_READ 等），通过 Channel 发送并等待应答。`SFTPFile` 继承 `BufferedFile`，在 BufferedFile 的 Python 层缓冲之上实现了 prefetch 预取和 pipeline 流水线机制，MAX_REQUEST_SIZE=32768。

**证据**：
- SFTPClient 维护 `request_number` 自增和 `_expecting` WeakValueDictionary 映射请求号→SFTPFile (`sftp_client.py:116-121`)
- `_request(t, *args)` 和 `_async_request(fileobj, t, *args)` 区分同步/异步请求 (`sftp_client.py:855-883`)
- `SFTPFile.pipelined` 属性控制是否启用写流水线；`_prefetch_data`/`_prefetch_extents` 管理读预取 (`sftp_file.py:66-73`)
- `listdir_iter(read_aheads=50)` 参数控制预读目录项数量 (`sftp_client.py:262`)
- SFTPAttributes 用 FLAG_SIZE/UIDGID/PERMISSIONS/AMTIME/EXTENDED 位掩码选择性序列化字段 (`sftp_attr.py:43-47`)

**反常识**：SFTPFile 的 `prefetch()` 方法不是简单的缓冲读取，而是发送多个未完成的读请求（pipeline），利用 SSH 通道的全双工特性重叠往返延迟。但服务端实现可能对并发请求数有限制，因此 MAX_REQUEST_SIZE 限制了单个请求的大小。

**行动**：SFTP 文档需解释请求-应答模型；文件传输示例展示 prefetch 和 callback 进度回调；说明 SFTPClient 也是 context manager。
