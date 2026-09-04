# SSH/远程控制 Python 包 OKF Wiki 教程 - 验证清单

## 环境准备
- [ ] 6 个源码仓库已 clone 到 external/libs/ 下（paramiko、fabric、asyncssh、pexpect、netmiko、scrapli）
- [ ] source-versions.md 记录了每个包的 commit hash 和版本号
- [ ] 每个仓库的 Python 源码包目录可定位（paramiko/、fabric/、asyncssh/、pexpect/、netmiko/、scrapli/）

## OKF v0.2 规范符合性
- [ ] 每个非 index/log 的 .md 文件包含可解析的 YAML frontmatter
- [ ] 每个 frontmatter 包含非空 `type` 字段（Concept/Example/Reference）
- [ ] 每个 frontmatter 包含 title、description、tags、generated、verified、status、stale_after、sources
- [ ] 每个知识束根 index.md 包含 `okf_version: "0.2"`
- [ ] 子目录 index.md（concepts/index.md、examples/index.md、references/index.md）不含 frontmatter
- [ ] 所有文档 `status: stable`
- [ ] `generated.by` 使用 actor 约定（如 `reference_agent/trae-glm`）
- [ ] `verified.by` 使用 `process:seven-concepts-v`
- [ ] sources 字段中 resource 路径使用 `/` 开头的 bundle-relative 路径

## 目录结构
- [ ] bundles/networking/ 目录存在
- [ ] bundles/networking/index.md 分组导航存在
- [ ] 6 个子目录存在：paramiko/、fabric/、asyncssh/、pexpect/、netmiko/、scrapli/
- [ ] 每个子目录包含 concepts/、examples/、references/ 三个子目录
- [ ] 每个子目录包含 index.md 和 log.md
- [ ] paramiko concepts/ ≥10 篇
- [ ] fabric concepts/ ≥8 篇
- [ ] asyncssh concepts/ ≥10 篇
- [ ] pexpect concepts/ ≥8 篇
- [ ] netmiko concepts/ ≥8 篇
- [ ] scrapli concepts/ ≥8 篇
- [ ] 每个知识束 examples/ ≥4 篇
- [ ] 每个知识束 references/ ≥1 篇信源登记

## R 阶段事实质量
- [ ] 每个包有编号事实清单（F-001~F-xxx）
- [ ] 事实清单中无"用于"/"目的是"/"设计为"等因果推断词
- [ ] 每个事实指向具体源码文件和行号/模块
- [ ] paramiko 事实数 ≥60
- [ ] fabric 事实数 ≥50
- [ ] asyncssh 事实数 ≥70
- [ ] pexpect 事实数 ≥50
- [ ] netmiko 事实数 ≥60
- [ ] scrapli 事实数 ≥50

## I 阶段洞察质量
- [ ] 每个包有 3-5 个架构洞察
- [ ] 每个洞察包含四元组：陈述+证据+反常识+行动
- [ ] 每个包有知识地图（文档分组和学习路径）

## E 阶段生成纪律
- [ ] references/ 信源文件先于 concepts/examples 生成
- [ ] 每批生成 ≤7 个文档
- [ ] 各级 index.md 在所有内容文档定稿后最后生成
- [ ] 交叉引用使用 `/` 开头的 bundle-relative 路径（无 `../`）
- [ ] 每个文档结尾有"相关概念"章节
- [ ] 代码块标注语言（python/bash）
- [ ] 正文使用中文，文件名 kebab-case 纯英文

## V 阶段 API 真实性（Grep 验证）
- [ ] paramiko: SSHClient、Transport、Channel、SFTPClient、AutoAddPolicy、RejectPolicy、WarningPolicy、RSAKey、Ed25519Key、ECDSAKey、DSSKey、ProxyCommand、ServerInterface、HostKeys、Agent 在源码中存在
- [ ] paramiko: exec_command、invoke_shell、open_sftp、connect、start_client、open_channel、request_port_forward、from_transport、set_missing_host_key_policy 方法在源码中存在
- [ ] fabric: Connection、Config、SerialGroup、ThreadingGroup、GroupResult、Remote、Transfer、Tunnel、Executor、ConnectionCall 在源码中存在
- [ ] fabric: run、sudo、put、get、open、forward_local、forward_remote 方法在源码中存在
- [ ] asyncssh: connect、SSHClientConnection、SSHChannel、SSHReader、SSHWriter、SSHCompletedProcess、SFTPClient、SFTPServer、SSHAgent 在源码中存在
- [ ] asyncssh: create_connection、run、create_process、start_sftp_client、start_server、forward_local_port、forward_remote_port 方法在源码中存在
- [ ] pexpect: spawn、pxssh、run、EOF、TIMEOUT、ExceptionPexpect、PopenSpawn、fdspawn、SocketSpawn、REPLWrapper 在源码中存在
- [ ] pexpect: expect、sendline、send、interact、before、after、match、close、kill、login、logout、prompt 方法/属性在源码中存在
- [ ] netmiko: ConnectHandler、BaseConnection、ssh_dispatcher、SSHDetect、redispatch、platforms、FileTransfer 在源码中存在
- [ ] netmiko: send_command、send_config_set、send_config_from_file、establish_connection、session_preparation、disconnect、send_command_timing 方法在源码中存在
- [ ] scrapli: 文档中引用的所有公开类名在 Python 源码中存在（Scrapli/AsyncScrapli/NetworkDriver/Driver/Response 等，以实际源码为准）
- [ ] 所有文档中无虚构 API（Grep 验证覆盖率 ≥95%）

## 交叉引用
- [ ] fabric 知识束有指向 paramiko 知识束的链接
- [ ] netmiko 知识束有指向 paramiko 知识束的链接
- [ ] scrapli 知识束有指向 paramiko 和/或 asyncssh 知识束的链接
- [ ] fabric 知识束有指向 tooling/pyinvoke 知识束的链接
- [ ] 所有 `/` 开头的链接目标文件存在
- [ ] 无 `../` 相对路径链接

## 分组索引和总索引
- [ ] bundles/networking/index.md 包含 6 个知识束导航
- [ ] bundles/networking/index.md 包含生态关系图
- [ ] bundles/networking/index.md 包含推荐学习路径
- [ ] bundles/index.md 新增 networking 分组条目
- [ ] bundles/index.md total_bundles 计数已更新（+6）
- [ ] bundles/index.md groups 计数已更新（+1）

## log.md
- [ ] 每个知识束 log.md 记录了 R/I/E/V/C 各阶段完成情况
- [ ] log.md 包含日期（2026-08-23）
- [ ] log.md 记录了事实数、洞察数、文档数

## 内容质量（人工审查）
- [ ] 概念文档逻辑连贯，从入门到高级递进
- [ ] 代码示例语法正确，API 调用与源码一致
- [ ] asyncssh 文档正确使用 async/await 语法
- [ ] pexpect 文档正确标注 Unix/Windows 平台差异
- [ ] scrapli 文档准确描述架构形态（纯 Python 或 Zig+Python 绑定）
- [ ] 中文表达流畅，无残留占位符或 TODO
- [ ] 学习路径从 paramiko 基础到 scrapli 现代方案逻辑递进
