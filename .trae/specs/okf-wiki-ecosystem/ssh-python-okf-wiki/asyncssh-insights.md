# asyncssh 架构洞察

> I 阶段产出，基于 R 阶段 180 条源码事实提炼。

## 洞察一：全异步协程协议栈——asyncio.Protocol 状态机

asyncssh 的核心设计是将 SSH 协议实现为 `asyncio.Protocol` 的子类。`SSHConnection`（connection.py:867）同时继承 `SSHPacketHandler` 和 `asyncio.Protocol`，通过 `connection_made()`、`data_received()`、`connection_lost()` 等 asyncio 回调驱动协议状态机。密钥交换、加密协商、认证、通道管理全部在这一状态机内以协程方式推进。

与 paramiko 的 `Transport`（继承 `threading.Thread`）形成对比：paramiko 使用后台线程 + 锁的同步模型，asyncssh 使用单线程事件循环 + 协程的异步模型。这意味着 asyncssh 不需要线程同步原语，但要求所有 SSH 操作通过 `await` 挂起，不能在同步上下文中直接调用。

`SSHClientConnection` 和 `SSHServerConnection` 均继承 `SSHConnection`，共享密钥交换、包处理、通道多路复用等核心逻辑，仅在认证方向和通道打开方向上分化。

## 洞察二：Channel→Stream→Process 三层 IO 抽象递进

asyncssh 的 IO 抽象分为三层，每层在上层封装下层：

1. **SSHChannel**（channel.py:86）——最底层，模拟字节流通道，提供 `write()`/`writelines()`/`write_eof()`/`close()`/`wait_closed()`，支持扩展数据类型（stderr 通过 `datatype` 参数区分）。通道管理接收窗口和包大小（默认 2 MiB / 32 KiB）。

2. **SSHReader/SSHWriter**（stream.py:72/257）——中层，提供 asyncio 流风格 API：`SSHReader.read(n)`、`readline()`、`readuntil()`、`readexactly()`；`SSHWriter.write()`、`drain()`、`write_eof()`。`SSHStreamSession`（stream.py:373）作为通道与读写器之间的桥接，实现背压（pause_writing/resume_writing）和缓冲管理。

3. **SSHProcess**（process.py:819）——高层，封装 stdin/stdout/stderr 三个流，支持 `communicate()`、`wait()`、`redirect()`，以及 `PIPE`/`DEVNULL`/`STDOUT` 常量（类比 `subprocess` 模块）。`SSHClientProcess` 和 `SSHServerProcess` 分别面向客户端和服务端场景。

三层递进使用户可以按需选择抽象级别：底层通道可用于自定义协议，中层流适合需要逐行读取的场景，高层进程适合"执行命令并收集输出"的常见需求。

## 洞察三：SFTP v3-v6 多版本协议与 OpenSSH 扩展

asyncssh 的 SFTP 实现覆盖协议版本 3 到 6（sftp.py:172-173），是 Python 生态中支持最完整的 SFTP 实现之一。不同版本引入不同能力：

- v3：基础文件操作（open/close/read/write/stat/rename/mkdir/rmdir 等）
- v4：引入 `posix-rename`、`statvfs`、ACL 等
- v5：扩展文件锁、字节范围锁
- v6：完善 ACL、文件类型检查

`SFTPClient` 通过方法重载（`@overload`）提供类型友好的 API，同时支持 bytes 和 str 路径（通过 `path_encoding` 参数控制，默认 UTF-8）。`SFTPClientFile` 支持并行读取（`read_parallel()`，sftp.py:3470）和并行写入，通过 `_SFTPParallelIO` 基类（sftp.py:703）实现流水线优化。

OpenSSH 扩展方面，asyncssh 支持 `copy-data` 扩展（服务端远程复制，`supports_remote_copy` 属性）、`hardlink` 扩展、`fsync@openssh.com` 等。`SFTPServerFS`（sftp.py:8153）提供 VFS 抽象层，允许服务端将 SFTP 操作映射到任意后端存储。

## 洞察四：模块化加密插件体系

`crypto/` 子包采用插件注册模式。每种加密算法（RSA/DSA/ECDSA/Ed25519/Ed448）在各自模块中定义私钥/公钥类，并通过模块导入时的注册调用（`__init__.py:126` 触发 `sk_eddsa`/`sk_ecdsa`/`eddsa`/`ecdsa`/`rsa`/`dsa`/`kex_dh`/`kex_rsa` 模块的注册代码）将算法添加到全局注册表。

`encryption.py` 维护 `_enc_algs` 和 `_default_enc_algs` 列表，密码算法通过 `register_cipher()` 注册。这种设计使得：

- 添加新算法只需创建新模块并在导入时注册，无需修改核心代码
- 可选算法（如 ChaCha20-Poly1305、UMAC、X.509）通过 try/except 优雅降级
- 后量子密钥交换（ML-KEM、SNTRUP）作为独立模块集成，通过 `mlkem_available()`/`sntrup_available()` 检测

`SSHKey.generate()` 类方法（public_key.py:268）是工厂方法模式的典型应用：基类抛出 `NotImplementedError`，各算法子类根据 algorithm bytes 参数返回对应密钥实例。

## 洞察五：双端对称设计与回调协议

asyncssh 的客户端和服务端共享大量基类，形成对称架构：

- `SSHClientConnection` ↔ `SSHServerConnection`（均继承 `SSHConnection`）
- `SSHClientChannel` ↔ `SSHServerChannel`（均继承 `SSHChannel`）
- `SSHClientSession` ↔ `SSHServerSession`（均继承 `SSHSession`）
- `SSHClientProcess` ↔ `SSHServerProcess`（均继承 `SSHProcess`）
- `SSHClient` ↔ `SSHServer`（均为回调协议处理器）

这种对称性体现在回调设计上：`SSHClient` 定义 `password_auth_requested()`、`public_key_auth_requested()` 等回调让应用动态提供凭据；`SSHServer` 定义 `validate_password()`、`validate_public_key()`、`begin_auth()` 等回调让应用验证凭据。两端的认证方法类（`_ClientXxxAuth` ↔ `_ServerXxxAuth`）也成对出现，共享 `Auth` 基类和 `register_auth_method()` 注册机制。

双端对称使开发者可以用相同的心智模型编写客户端和服务端代码，也使 asyncssh 成为构建 SSH 中间人代理、跳板机、隧道等双端场景的理想选择。
