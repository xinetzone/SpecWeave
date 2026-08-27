# SSH/远程控制 Python 包 OKF Wiki 教程 - 实施计划

## [x] Task 1: 环境准备——克隆 6 个 SSH 包源码到 external/libs/
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 将 6 个开源仓库 git clone 到 `external/libs/` 下，目录命名与包名一致
  - paramiko: `git clone https://github.com/paramiko/paramiko.git external/libs/paramiko`
  - fabric: `git clone https://github.com/fabric/fabric.git external/libs/fabric`
  - asyncssh: `git clone https://github.com/ronf/asyncssh.git external/libs/asyncssh`
  - pexpect: `git clone https://github.com/pexpect/pexpect.git external/libs/pexpect`
  - netmiko: `git clone https://github.com/ktbyers/netmiko.git external/libs/netmiko`
  - scrapli: `git clone https://github.com/carlmontanari/scrapli.git external/libs/scrapli`
  - 记录每个仓库的最新 commit hash 和版本号（从 `_version.py`/`__init__.py`/pyproject.toml 获取）
  - 在 `.trae/specs/ssh-python-okf-wiki/source-versions.md` 记录版本信息
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 6 个目录均存在且包含 `.git`（通过 LS 验证）
  - `programmatic` TR-1.2: 每个目录下有 Python 源码包目录（paramiko/、fabric/、asyncssh/、pexpect/、netmiko/、scrapli/ 或 src/ 下）
  - `programmatic` TR-1.3: source-versions.md 记录了 6 个包的 commit hash 和版本号
- **Notes**: scrapli 新版可能含 Zig 代码，clone 后在 Task 7 中确认 Python 源码结构

## [x] Task 2: paramiko 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - **R 阶段（事实采集）**：深度阅读 `external/libs/paramiko/paramiko/` 核心模块（transport.py、client.py、channel.py、sftp_client.py、auth_handler.py、agent.py、pkey.py、rsakey.py、ed25519key.py、ecdsakey.py、dsskey.py、server.py、hostkeys.py、proxy.py、common.py、message.py、packet.py、kex.py、filetransfers.py、buffered_pipe.py、primes.py、config.py），提取 60+ 编号事实（F-001~F-060+），写入 `.trae/specs/ssh-python-okf-wiki/paramiko-facts.md`
  - **I 阶段（架构洞察）**：提炼 3-5 个核心洞察（Transport 加密隧道与 Channel 复用的分层模型、SSHClient 高层门面与策略模式、密钥体系继承层次、SFTP 子系统协议实现），设计知识地图（入门→核心→高级），写入 `paramiko-insights.md`
  - **E 阶段（批量生成，信源先行）**：
    1. 创建 `bundles/networking/paramiko/` 目录结构（concepts/examples/references）
    2. 先生成 `references/paramiko-source.md`（信源登记，含版本、核心模块清单、公开 API 导出）
    3. 分批生成 concepts/（每批 ≤7 篇），覆盖：00-introduction、01-getting-started、02-ssh-client、03-transport、04-channel、05-authentication、06-keys-and-hostkeys、07-sftp、08-port-forwarding、09-server、10-advanced-patterns
    4. 生成 examples/（4-6 篇）：basic-connection、execute-commands、file-transfer、port-forwarding、interactive-shell、jump-host
    5. 最后生成各级 index.md
  - **V 阶段（独立验证）**：Grep 验证所有类名/方法名在源码中存在；检查 frontmatter 完整性；检查交叉链接；修复虚构 API
- **Acceptance Criteria Addressed**: AC-2, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-2.1: paramiko/ 目录下存在 concepts/（≥10 .md）、examples/（≥4 .md）、references/（≥1 .md）、index.md、log.md
  - `programmatic` TR-2.2: 所有非 index/log .md 文件包含 type 字段且值为 Concept/Example/Reference
  - `programmatic` TR-2.3: Grep 验证 SSHClient、Transport、Channel、SFTPClient、AutoAddPolicy、RSAKey、Ed25519Key、ProxyCommand、ServerInterface、HostKeys 等类名在 paramiko/ 源码中存在
  - `programmatic` TR-2.4: Grep 验证 exec_command、invoke_shell、open_sftp、connect、start_client、open_channel、request_port_forward、from_transport 等方法名在源码中存在
  - `programmatic` TR-2.5: facts.md 无"用于"/"目的是"/"设计为"等因果推断词
  - `human-judgement` TR-2.6: 概念文档逻辑连贯，代码示例可运行（语法正确），学习路径从入门到高级递进
- **Notes**: paramiko 是其他多个包的基础，优先完成；fabric/netmiko 将交叉引用此束

## [x] Task 3: fabric 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - **R 阶段**：阅读 `external/libs/fabric/fabric/` 核心模块（connection.py、config.py、group.py、runners.py、transfer.py、tunnels.py、executor.py、tasks.py、testing/、cli.py、auth_strategies/、exceptions.py），提取 50+ 事实，写入 `fabric-facts.md`
  - **I 阶段**：提炼 3-5 洞察（Connection 继承 invoke.Context 并组合 paramiko.SSHClient 的双层架构、Group 并行执行模型、Config 多层级合并与 SSH config 集成、Remote Runner 继承 invoke.Runner 的模板方法模式、Tunnel 跳板机实现）
  - **E 阶段**：
    1. 创建 `bundles/networking/fabric/` 目录结构
    2. 先生成 `references/fabric-source.md`
    3. 分批生成 concepts/（≥8 篇）：00-introduction、01-getting-started、02-connection、03-configuration、04-command-execution、05-group-parallel、06-file-transfer、07-tunnels、08-advanced-patterns
    4. 生成 examples/（≥4 篇）：basic-deploy、multi-server-group、file-upload-download、tunnel-bastion
    5. 最后生成 index.md
  - **V 阶段**：Grep 验证 Connection、Config、SerialGroup、ThreadingGroup、Remote、Transfer、Tunnel、Executor、ConnectionCall 等 API；验证与 paramiko 和 pyinvoke 知识束的交叉引用
- **Acceptance Criteria Addressed**: AC-3, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: fabric/ 目录结构完整，concepts/ ≥8、examples/ ≥4、references/ ≥1
  - `programmatic` TR-3.2: Grep 验证 Connection、Config、SerialGroup、ThreadingGroup、GroupResult、Remote、Transfer、Tunnel、Executor、ConnectionCall 类名在 fabric/ 源码中存在
  - `programmatic` TR-3.3: Grep 验证 run、sudo、put、get、open、forward_local、forward_remote 等方法名存在
  - `programmatic` TR-3.4: frontmatter 中 sources 字段指向 /references/fabric-source.md
  - `human-judgement` TR-3.5: 文档清晰说明 fabric 与 paramiko（底层 SSH）和 invoke（任务执行）的关系，有交叉链接

## [x] Task 4: asyncssh 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - **R 阶段**：阅读 `external/libs/asyncssh/asyncssh/` 核心模块（connection.py、channel.py、stream.py、process.py、auth.py、public_key.py、kex.py、agent.py、sftp.py、scp.py、forward.py、config.py、cipher.py、mac.py、compression.py、known_hosts.py、editor.py、session.py），提取 70+ 事实，写入 `asyncssh-facts.md`
  - **I 阶段**：提炼 3-5 洞察（基于 asyncio 的全异步协议栈设计、SSHConnection 协程状态机、Channel→Stream→Process 三层 IO 抽象、SFTP 协议 v3-v6 全版本实现、模块化加密算法插件体系）
  - **E 阶段**：
    1. 创建 `bundles/networking/asyncssh/` 目录结构
    2. 先生成 `references/asyncssh-source.md`
    3. 分批生成 concepts/（≥10 篇）：00-introduction、01-getting-started、02-async-connection、03-channels、04-streams-processes、05-authentication、06-keys-certificates、07-sftp、08-scp、09-port-forwarding、10-server、11-advanced-patterns
    4. 生成 examples/（≥4 篇）：async-command、parallel-connections、sftp-transfer、port-forward-tunnel
    5. 最后生成 index.md
  - **V 阶段**：Grep 验证 connect、SSHClientConnection、SSHChannel、SSHReader、SSHWriter、SSHProcess、SFTPClient、create_connection、run、start_sftp_client 等 API
- **Acceptance Criteria Addressed**: AC-4, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: asyncssh/ 目录结构完整，concepts/ ≥10、examples/ ≥4、references/ ≥1
  - `programmatic` TR-4.2: Grep 验证 connect、SSHClientConnection、SSHServerConnection、SSHChannel、SSHReader、SSHWriter、SSHCompletedProcess、SFTPClient、SFTPServer、SSHAgent 等符号在源码中存在
  - `programmatic` TR-4.3: Grep 验证 create_connection、run、create_process、start_sftp_client、start_server、forward_local_port、forward_remote_port 等协程方法存在
  - `human-judgement` TR-4.4: 文档正确说明 asyncio 事件循环模型，所有代码示例使用 async/await 语法，与 paramiko 同步模型形成对比

## [x] Task 5: pexpect 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - **R 阶段**：阅读 `external/libs/pexpect/pexpect/` 核心模块（pty_spawn.py、pxssh.py、popen_spawn.py、fdpexpect.py、socket_pexpect.py、replwrap.py、run.py、exceptions.py、utils.py、expect.py），提取 50+ 事实，写入 `pexpect-facts.md`
  - **I 阶段**：提炼 3-5 洞察（spawn 的 PTY 子进程控制模型、expect 正则匹配引擎与增量缓冲区、pxssh 对 SSH 登录交互的状态机封装、跨平台 spawn 变体策略——pty_spawn/popen_spawn/fdspawn/SocketSpawn）
  - **E 阶段**：
    1. 创建 `bundles/networking/pexpect/` 目录结构
    2. 先生成 `references/pexpect-source.md`
    3. 分批生成 concepts/（≥8 篇）：00-introduction、01-getting-started、02-spawn-class、03-expect-patterns、04-send-interact、05-pxssh、06-cross-platform-spawn、07-replwrap、08-advanced-patterns
    4. 生成 examples/（≥4 篇）：ssh-login-automation、ftp-interaction、password-prompts、repl-control
    5. 最后生成 index.md
  - **V 阶段**：Grep 验证 spawn、pxssh、run、EOF、TIMEOUT、ExceptionPexpect、PopenSpawn、fdspawn、SocketSpawn、REPLWrapper 等 API；验证平台差异标注
- **Acceptance Criteria Addressed**: AC-5, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: pexpect/ 目录结构完整，concepts/ ≥8、examples/ ≥4、references/ ≥1
  - `programmatic` TR-5.2: Grep 验证 spawn、pxssh、run、EOF、TIMEOUT、ExceptionPexpect、ExceptionPxssh、PopenSpawn、fdspawn、SocketSpawn、REPLWrapper 等符号在源码中存在
  - `programmatic` TR-5.3: Grep 验证 expect、sendline、send、interact、before、after、match、close、kill、login、logout、prompt 等方法/属性存在
  - `human-judgement` TR-5.4: 文档明确标注 pty_spawn 仅 Unix 可用、popen_spawn 跨平台但无 PTY 等平台限制

## [x] Task 6: netmiko 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - **R 阶段**：阅读 `external/libs/netmiko/netmiko/` 核心模块（base_connection.py、ssh_dispatcher.py、ssh_autodetect.py、cisco_base_connection.py、utilities.py、exceptions.py、file_transfer.py、scp_functions.py、services/、__init__.py），采样阅读 3-5 个厂商驱动（cisco_ios.py、arista_eos.py、juniper_junos.py、linux.py、hp_comware.py），提取 60+ 事实，写入 `netmiko-facts.md`
  - **I 阶段**：提炼 3-5 洞察（ConnectHandler 工厂+ssh_dispatcher 类映射的多厂商驱动架构、BaseConnection 模板方法模式——establish_connection→session_preparation→disable_paging、SSHDetect 自动设备类型探测、100+ 驱动类的继承层次与代码复用、基于 paramiko 的 CLI screen-scraping 模型）
  - **E 阶段**：
    1. 创建 `bundles/networking/netmiko/` 目录结构
    2. 先生成 `references/netmiko-source.md`
    3. 分批生成 concepts/（≥8 篇）：00-introduction、01-getting-started、02-connect-handler、03-base-connection、04-command-execution、05-config-mgmt、06-driver-hierarchy、07-ssh-autodetect、08-file-transfer、09-advanced-patterns
    4. 生成 examples/（≥4 篇）：multi-vendor-connect、send-commands、config-changes、output-parsing-textfsm
    5. 最后生成 index.md
  - **V 阶段**：Grep 验证 ConnectHandler、BaseConnection、ssh_dispatcher、SSHDetect、NetmikoTimeoutException、FileTransfer 等 API；验证与 paramiko 知识束的交叉引用
- **Acceptance Criteria Addressed**: AC-6, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: netmiko/ 目录结构完整，concepts/ ≥8、examples/ ≥4、references/ ≥1
  - `programmatic` TR-6.2: Grep 验证 ConnectHandler、BaseConnection、ssh_dispatcher、SSHDetect、redispatch、platforms、FileTransfer、NetmikoTimeoutException、NetmikoAuthenticationException 等符号在源码中存在
  - `programmatic` TR-6.3: Grep 验证 send_command、send_config_set、send_config_from_file、establish_connection、session_preparation、disconnect、send_command_timing、send_command_expect 等方法存在
  - `human-judgement` TR-6.4: 文档清晰说明 netmiko 构建于 paramiko 之上的关系，有交叉链接；说明 CLI screen-scraping vs API 的选型考量

## [x] Task 7: scrapli 知识束 R→I→E→V 全流程
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 4
- **Description**:
  - **R 阶段**：阅读 `external/libs/scrapli/` 源码结构。注意：scrapli 新版可能已迁移至 Zig 核心（libscrapli）+ Python ctypes 绑定。若 Python 源码充足，阅读 scrapli/ 包核心模块（driver/、transport/、channel/、response.py、exceptions.py、cfg/、logging.py）；若以 Zig 为主，则聚焦 Python API 层和架构关系。提取 50+ 事实，写入 `scrapli-facts.md`
  - **I 阶段**：提炼 3-5 洞察（Transport-Channel-Driver 三层解耦架构、同步/异步双版本通过 mixin 类组装、可插拔 transport——system/ssh2/paramiko/asyncssh/telnet、核心平台驱动工厂模式、Response 对象统一命令结果模型）
  - **E 阶段**：
    1. 创建 `bundles/networking/scrapli/` 目录结构
    2. 先生成 `references/scrapli-source.md`（准确记录版本和架构——纯 Python 或 Zig+Python 绑定）
    3. 分批生成 concepts/（≥8 篇）：00-introduction、01-getting-started、02-transport-layer、03-channel、04-driver-architecture、05-core-platform-drivers、06-async-mode、07-response-object、08-advanced-patterns
    4. 生成 examples/（≥4 篇）：basic-connect、send-commands、async-parallel、custom-driver
    5. 最后生成 index.md
  - **V 阶段**：Grep 验证 Scrapli、AsyncScrapli、NetworkDriver、AsyncNetworkDriver、Driver、GenericDriver、IOSXEDriver、EOSDriver、Response、MultiResponse、transport 插件等实际存在的 API
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: scrapli/ 目录结构完整，concepts/ ≥8、examples/ ≥4、references/ ≥1
  - `programmatic` TR-7.2: Grep 验证文档中引用的所有公开类名在 scrapli Python 源码中存在（若 Zig 核心，验证 Python 绑定层导出的符号）
  - `programmatic` TR-7.3: references 中准确记录架构形态（纯 Python / Zig+ctypes 绑定），不虚构模块路径
  - `human-judgement` TR-7.4: 文档清晰说明 scrapli 与 paramiko/asyncssh 的 transport 插件关系，有交叉链接

## [x] Task 8: networking 分组索引与总索引更新
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 生成 `bundles/networking/index.md` 分组导航，包含：
    - frontmatter（无 okf_version，仅 type/title/description）
    - networking 分组概述
    - 生态关系图（ASCII 或 Mermaid，展示 paramiko 基础层→fabric/netmiko 封装层→asyncssh 异步范式→pexpect 交互控制→scrapli 现代网络自动化的层次关系）
    - 6 个知识束的导航表格（知识束名、简介、概念数、示例数）
    - 推荐学习路径
  - 更新 `bundles/index.md` 总索引：
    - 新增 networking 分组条目到分组导航表
    - 新增 networking 分组详情段落
    - 更新 total_bundles（+6）和 groups（+1）计数
    - 更新生态关系概览图（如适用）
- **Acceptance Criteria Addressed**: AC-1, AC-11, AC-12
- **Test Requirements**:
  - `programmatic` TR-8.1: bundles/networking/index.md 存在且包含 6 个知识束的链接
  - `programmatic` TR-8.2: bundles/index.md 中 networking 分组条目存在，total_bundles 计数已更新
  - `programmatic` TR-8.3: networking/index.md 中所有链接指向实际存在的知识束 index.md
  - `human-judgement` TR-8.4: 学习路径逻辑递进（paramiko 基础→fabric/netmiko 封装→asyncssh 异步→pexpect 交互→scrapli 现代），生态关系图准确反映包之间的依赖和范式对比

## [x] Task 9: 最终全局验证与 C 阶段模式沉淀
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 全局 V 阶段：
    - 遍历 networking/ 下所有 .md 文件，检查 frontmatter type 字段
    - 全局链接检查：所有 `/` 开头的 bundle-relative 路径目标存在
    - 全局交叉引用检查：包之间的交叉链接（fabric→paramiko、netmiko→paramiko、scrapli→paramiko/asyncssh、fabric→pyinvoke）有效
    - 检查每个知识束的 log.md 已记录创建日志
    - 检查 index.md 计数准确
  - C 阶段：
    - 在 `.trae/specs/ssh-python-okf-wiki/retrospective.md` 记录流程复盘
    - 如有可复用的新反模式或改进，更新 source-code-to-okf-wiki Skill 的模式文档（仅在发现新问题时）
- **Acceptance Criteria Addressed**: AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: networking/ 下所有非 index/log .md 文件均含非空 type 字段
  - `programmatic` TR-9.2: 无断裂链接（所有 `/concepts/`、`/examples/`、`/references/` 链接目标存在）
  - `programmatic` TR-9.3: 跨束交叉引用链接（fabric→paramiko、netmiko→paramiko 等）目标存在
  - `programmatic` TR-9.4: 每个知识束根目录存在 log.md 且包含创建记录
  - `human-judgement` TR-9.5: 整体文档质量审查——中文表达流畅、代码示例格式正确、无残留的占位符/TODO
