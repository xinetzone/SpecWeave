# asyncssh 知识束生成任务指导书

## 任务概述
为 asyncssh v2.24.0 生成符合 OKF v0.2 规范的系统化中文 Wiki 教程，遵循 R→I→E→V 四阶段工作流。

## 路径
- **源码路径**: `d:\spaces\SpecWeave\external\libs\asyncssh\asyncssh\`
- **输出路径**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\asyncssh\`
- **事实清单**: `d:\spaces\SpecWeave\.trae\specs/okf-wiki-ecosystem/ssh-python-okf-wiki\asyncssh-facts.md`
- **洞察文件**: `d:\spaces\SpecWeave\.trae\specs/okf-wiki-ecosystem/ssh-python-okf-wiki\asyncssh-insights.md`
- **格式范例**: 读 `bundles\networking\paramiko\index.md` 了解格式

## 版本信息
- asyncssh 2.24.0, commit 25370783e5c1
- 基于 asyncio 的异步 SSHv2 客户端/服务端，Python 3.10+
- 依赖 cryptography
- 147 个 .py 文件，含 crypto/ 子包

## 核心模块（R阶段必读）
- `__init__.py` — 公开 API（重点看导出了哪些符号）
- `connection.py` — SSHConnection、SSHClientConnection、SSHServerConnection、connect() 入口
- `channel.py` — SSHChannel、SSHClientChannel、SSHServerChannel、SSHTCPChannel、SSHUNIXChannel
- `stream.py` — SSHReader、SSHWriter、SSHClientStreamSession、SSHServerStreamSession
- `process.py` — SSHProcess、SSHCompletedProcess、SSHServerProcess
- `session.py` — 会话基类
- `auth.py` — 认证框架
- `public_key.py` — SSHKey、SSHCertificate、密钥生成/读取/序列化
- `agent.py` — SSHAgentClient、SSHAgentServer
- `sftp.py` — SFTPClient、SFTPServer、SFTPAttrs、SFTPName、VFS
- `scp.py` — SCP 客户端/服务端协程
- `forward.py` — SSHForwarder、本地/远程端口转发
- `config.py` — SSHConfig 解析
- `known_hosts.py` — KnownHosts
- `listener.py` — SSHListener
- `editor.py` — SSHLineEditorChannel/SSHLineEditorSession
- `subprocess.py` — 异步 subprocess 桥接
- `crypto/` — 加密算法子包（cipher.py, kdf.py, dh.py, ec.py, ed.py, rsa.py, dsa.py, chacha.py, pq.py 等）
- `logging.py` — 日志
- `misc.py` — 工具函数
- `constants.py` — 常量
- `packet.py` — 包处理（如存在）

## R 阶段（70+ 事实）
提取 F-001~F-070+，重点：
- connect() 函数参数和返回值
- SSHClientConnection 的核心协程方法：run、create_process、start_server、start_sftp_client、start_sftp_server、create_connection、forward_local_port、forward_remote_port、add_server_key、get_server_host_key、check_channel_permission
- SSHChannel 的方法：write、writelines、write_extended、read、readline、readuntil、pause_reading、resume_reading、close、wait_closed、get_exit_status、change_terminal_size
- SSHReader/SSHWriter 的 async API
- SSHProcess 的 stdin/stdout/stderr、wait、check、communicate
- SFTPClient 方法：get、put、mget、mput、stat、lstat、chmod、chown、mkdir、rmdir、listdir、rename、posix_rename、readfile、writefile、open
- SSHKey 类方法：generate、read_private_key、read_public_key、import_private_key、export_private_key、export_public_key、append_public_key、write_private_key、write_public_key
- 加密算法列表和协商机制

**禁止**"用于"/"目的是"/"设计为"等推断词。

## I 阶段（3-5 洞察）
建议方向：
1. 全异步协程协议栈——SSHConnection 作为 asyncio Protocol 的状态机设计
2. Channel→Stream→Process 三层 IO 抽象的递进关系
3. SFTP v3-v6 多版本协议实现与 OpenSSH 扩展
4. 模块化加密插件体系（crypto/ 子包的算法注册模式）
5. 双端对称设计——客户端和服务端共享同一套基类

## E 阶段

### Step 1: 创建目录

### Step 2: references/asyncssh-source.md（先生成！）

### Step 3: concepts/（≥10篇，分2批，每批≤7）

**批次1（6篇）**:
1. `00-introduction.md` — asyncssh 简介、异步模型、安装、与 paramiko 对比
2. `01-getting-started.md` — asyncio.run、connect()、第一个命令执行
3. `02-async-connection.md` — SSHClientConnection 详解、connect() 参数、认证方式、主机密钥验证、连接生命周期
4. `03-channels.md` — SSHChannel、会话/执行/直接TCPIP/转发通道、PTY、窗口调整
5. `04-streams-processes.md` — SSHReader/SSHWriter、create_process、SSHCompletedProcess、stdin/stdout/stderr
6. `05-authentication.md` — 密码/公钥/键盘交互/GSSAPI、SSHKey、authorized_keys、known_hosts

**批次2（5篇）**:
7. `06-keys-certificates.md` — SSHKey 生成/读取/导出、SSHCertificate、证书认证、SSH Agent
8. `07-sftp.md` — SFTPClient/SFTPServer、get/put、stat/listdir、SFTPAttrs、VFS、协议版本
9. `08-scp.md` — SCP 协程、scp_recv/scp_send、第三方远程复制
10. `09-port-forwarding.md` — forward_local_port/forward_remote_port、SSHForwarder、SOCKS、UNIX socket
11. `10-server.md` — SSHServer、start_server、自定义认证/通道处理器、SFTPServer VFS
12. `11-advanced-patterns.md` — 并发连接、进程池、加密算法配置、后量子密钥交换、调试日志

### Step 4: examples/（≥4篇）
1. `async-command.md` — 异步执行命令
2. `parallel-connections.md` — 多主机并行连接（asyncio.gather）
3. `sftp-transfer.md` — SFTP 文件传输
4. `port-forward-tunnel.md` — 端口转发隧道

### Step 5: index.md 文件（最后生成）
- concepts/index.md, examples/index.md, references/index.md（无 frontmatter）
- 根 index.md（okf_version: "0.2"）
- log.md

## Frontmatter
同 paramiko 格式，tags 包含 asyncssh，stale_after: 2027-06-30（asyncssh 迭代较快）

## 交叉引用
- 跨束引用 paramiko：`../../paramiko/concepts/02-ssh-client.md`（对比同步模型）
- 束内用 `/concepts/xx.md` 或相对路径

## V 阶段 Grep 验证
在 `external/libs/asyncssh/asyncssh/` 中验证：
- 函数/类: connect, SSHClientConnection, SSHServerConnection, SSHChannel, SSHClientChannel, SSHReader, SSHWriter, SSHProcess, SSHCompletedProcess, SSHServerProcess, SFTPClient, SFTPServer, SFTPAttrs, SFTPName, SSHKey, SSHCertificate, SSHAgentClient, SSHForwarder, SSHListener, SSHServer, SSHServerSession
- 方法: run, create_process, start_sftp_client, start_server, forward_local_port, forward_remote_port, open_session, open_connection, create_connection, get, put, stat, listdir, mkdir, read, write, readline, wait, wait_closed, close, generate, read_private_key, export_private_key
- 注意：必须在源码中实际确认方法名，不要凭训练数据猜测。asyncssh 的 API 可能与 paramiko 不同。

## 返回
事实总数、文件列表、虚构 API 修复记录、Grep 验证结果。
