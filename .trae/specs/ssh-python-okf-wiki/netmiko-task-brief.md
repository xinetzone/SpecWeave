# netmiko 知识束生成任务指导书

## 路径
- 源码: `d:\spaces\SpecWeave\external\libs\netmiko\netmiko\`
- 输出: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\netmiko\`
- 事实: `.trae\specs\ssh-python-okf-wiki\netmiko-facts.md`
- 洞察: `.trae\specs\ssh-python-okf-wiki\netmiko-insights.md`
- 格式参考: `bundles\networking\paramiko\index.md`

## 版本: netmiko 4.7.0, commit 8ace5f2ae7da
多厂商网络设备 SSH 库，基于 paramiko。348 个 .py 文件，支持 100+ 平台。

## 源码结构（先读 __init__.py 了解导出）
- `__init__.py` — 导出 ConnectHandler, redispatch, platforms 等
- `base_connection.py` — BaseConnection 核心基类（最大文件，重点读）
- `ssh_dispatcher.py` — ConnectHandler 工厂函数、CLASS_MAPPER/CLASS_MAPPER_BASE、platforms 列表、redispatch、ssh_dispatcher 函数、FileTransfer 映射
- `ssh_autodetect.py` — SSHDetect 自动设备类型探测
- `cisco_base_connection.py` — CiscoBaseConnection（Cisco 设备基类，继承 BaseConnection）
- `cisco_ios/` — Cisco IOS 驱动（cisco_ios.py = CiscoIosSSH）
- `arista/` — Arista EOS 驱动
- `juniper/` — Juniper Junos 驱动
- `linux/` — Linux SSH 驱动
- `hp/` — HP Comware 驱动
- `utilities.py` — 工具函数
- `exceptions.py` — 异常体系（NetmikoTimeoutException, NetmikoAuthenticationException 等）
- `file_transfer.py` — FileTransfer 文件传输类（基于 SCP/SFTP）
- `scp_functions.py` — SCP 便捷函数
- `services/` — 服务子包（如有）

## R 阶段（60+ 事实）
重点读 base_connection.py 和 ssh_dispatcher.py，采样 3-5 个厂商驱动。提取 F-001~F-060+：

- ConnectHandler(device_type=..., host=..., username=..., password=..., secret=..., port=..., ...) 工厂函数签名和参数
- ssh_dispatcher 函数和 CLASS_MAPPER 字典结构
- platforms 列表如何生成
- redispatch 函数（动态切换驱动类）
- SSHDetect 类（autodetect 方法、潜在设备列表）
- BaseConnection 核心方法：
  - establish_connection / open / close / disconnect
  - send_command / send_command_timing / send_command_expect
  - send_config_set / send_config_from_file
  - session_preparation / clear_buffer / find_prompt
  - enable / exit_enable_mode / check_enable_mode
  - config_mode / exit_config_mode / check_config_mode
  - save_config / commit（Junos 等）
  - set_base_prompt / set_terminal_width / disable_paging / terminal_width
  - normalize_linefeeds / strip_prompt / strip_answer
- BaseConnection 重要属性：host, username, password, secret, port, device_type, global_delay_factor, fast_cli, session_log, encoding, conn_timeout, auth_timeout, banner_timeout
- FileTransfer 类（scp_conn、file_transfer）
- 厂商驱动继承层次示例（CiscoIosSSH → CiscoBaseConnection → BaseConnection）
- 异常类层次

## I 阶段（3-5 洞察）
1. ConnectHandler 工厂 + ssh_dispatcher 类映射的多厂商驱动架构
2. BaseConnection 模板方法模式——establish_connection→session_preparation→disable_paging 生命周期
3. send_command vs send_command_timing vs send_command_expect 三种命令发送模式
4. SSHDetect 自动探测机制
5. 基于 paramiko 的 CLI screen-scraping 模型

## E 阶段

### references/netmiko-source.md（先生成）

### concepts/（≥9篇）
1. `00-introduction.md` — netmiko 简介、多厂商网络自动化、安装、CLI vs API
2. `01-getting-started.md` — ConnectHandler 基础、device_type、第一个命令
3. `02-connect-handler.md` — 工厂函数、设备参数字典、ssh_dispatcher、redispatch
4. `03-base-connection.md` — BaseConnection 核心：连接生命周期、session_preparation、disable_paging
5. `04-command-execution.md` — send_command/send_command_timing/send_command_expect、read_timeout、expect_string
6. `05-config-mgmt.md` — send_config_set/send_config_from_file、config_mode、enable 模式、save_config
7. `06-driver-hierarchy.md` — 继承体系：BaseConnection→CiscoBaseConnection→CiscoIosSSH，采样对比 Cisco/Arista/Juniper/Linux
8. `07-ssh-autodetect.md` — SSHDetect 自动探测设备类型
9. `08-file-transfer.md` — FileTransfer/SCP 文件传输、verify_space
10. `09-advanced-patterns.md` — session_log 日志、global_delay_factor、fast_cli、TextFSM 解析、异常处理最佳实践

### examples/（≥4篇）
1. `multi-vendor-connect.md` — 多厂商设备连接
2. `send-commands.md` — 命令执行模式对比
3. `config-changes.md` — 批量配置变更
4. `output-parsing-textfsm.md` — TextFSM/ntc-templates 输出解析

### index.md 文件（最后生成）

## Frontmatter
tags 包含 netmiko，stale_after: 2027-06-30（网络设备驱动迭代较快）
跨束交叉引用 paramiko: `../../paramiko/concepts/02-ssh-client.md`

## V 阶段 Grep 验证
在 `external/libs/netmiko/netmiko/` 中验证：
- ConnectHandler, BaseConnection, CiscoBaseConnection, SSHDetect, FileTransfer, ssh_dispatcher, redispatch, platforms
- send_command, send_command_timing, send_command_expect, send_config_set, send_config_from_file, establish_connection, session_preparation, disconnect, enable, config_mode, exit_config_mode, check_enable_mode, save_config, find_prompt, clear_buffer, strip_prompt, disable_paging, open, close
- NetmikoTimeoutException, NetmikoAuthenticationException, ReadException, ReadTimeout

## 返回
事实数、文件列表、虚构 API 修复、Grep 验证摘要。
