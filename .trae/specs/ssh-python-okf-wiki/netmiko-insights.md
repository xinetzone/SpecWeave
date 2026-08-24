# netmiko 架构洞察

> I阶段：从120条源码事实中提炼的5个核心架构洞察。

## 洞察1：ConnectHandler 工厂 + CLASS_MAPPER 字典驱动的多厂商架构

netmiko 的核心设计是一个**字符串到类的映射字典** `CLASS_MAPPER`。`ConnectHandler(device_type=...)` 工厂函数根据 `device_type` 字符串查找对应的驱动类并实例化。这种设计使得：

- 新增厂商驱动只需创建一个继承 `BaseConnection` 的类并在 `CLASS_MAPPER_BASE` 中注册
- `CLASS_MAPPER` 自动为每个基础 device_type 生成 `_ssh` 后缀别名，Telnet/Serial 驱动单独追加
- `redispatch()` 通过修改 `obj.__class__` 实现运行时动态切换驱动类（典型场景：终端服务器连接后切换到实际设备驱动）
- `FileTransfer()` 工厂使用独立的 `FILE_TRANSFER_MAP`，仅18个平台有专用 SCP 驱动

这是一种**注册表模式（Registry Pattern）**，将"选择哪个类"的逻辑从代码分支转变为数据声明。

## 洞察2：BaseConnection 模板方法模式——连接生命周期

`BaseConnection` 定义了标准化的连接生命周期，子类通过重写特定步骤定制行为：

```
_open()
  → _modify_connection_params()      # 子类可修改连接参数
  → establish_connection()           # 建立 SSH/Telnet/Serial 连接
      → _build_ssh_client()          # 创建 paramiko SSHClient
      → _connect_params_dict()       # 生成连接参数
      → invoke_shell("vt100")        # 建立交互式 shell
      → special_login_handler()      # 特殊登录处理（如 WLC）
  → _try_session_preparation()
      → session_preparation()        # 子类重写：终端初始化
          → _test_channel_read()     # 验证通道可读
          → set_base_prompt()        # 识别设备提示符
          → set_terminal_width()     # 设置终端宽度
          → disable_paging()         # 禁用分页
```

基类 `session_preparation()` 提供了默认实现（Cisco 风格），但各厂商驱动可以完全重写：
- Cisco IOS: terminal width → disable paging → set prompt
- Arista: ANSI on → terminal width → disable paging → set prompt
- Juniper: enter CLI → screen-width → complete-on-space off → screen-length 0 → set prompt
- Linux: test channel → set prompt（无需设置宽度和分页）

这是典型的**模板方法模式（Template Method Pattern）**——基类定义算法骨架，子类重写特定步骤。

## 洞察3：三种命令发送模式的分层设计

netmiko 提供三种命令执行方法，适用于不同场景：

| 方法 | 机制 | 默认超时 | cmd_verify | 适用场景 |
|------|------|----------|------------|----------|
| `send_command_timing` | 延迟驱动：等待 last_read 秒无新数据 | 120s | False | 不确定输出格式、命令持续产生输出 |
| `send_command` | 模式驱动：等待提示符或 expect_string | 10s | True | 标准 show 命令，知道提示符会返回 |
| `send_command_expect` | send_command 的别名 | - | - | 向后兼容 |

关键设计决策：
- `send_command` 使用 `@select_cmd_verify` 装饰器，`global_cmd_verify` 全局属性优先于方法参数
- `send_command` 默认 `auto_find_prompt=True`，每次自动调用 `find_prompt()` 更新提示符
- 三者底层都调用 `write_channel()` + `read_channel_timing()`/`read_until_pattern()`
- 均通过 `structured_data_converter()` 支持 TextFSM/TTP/Genie 结构化输出

这种分层让用户可以在**可靠性**（模式匹配，快速失败）和**鲁棒性**（延迟等待，容忍未知输出）之间选择。

## 洞察4：SSHDetect 自动探测——命令输出指纹匹配

`SSHDetect` 使用**指纹匹配**策略自动识别设备类型：

1. 使用 `TerminalServerSSH`（generic 驱动）建立连接
2. `SSH_MAPPER_DICT` 定义了约50种设备的探测规则，每条包含：
   - `cmd`: 发送的命令（如 "show version"）
   - `search_patterns`: 正则表达式列表，匹配命令输出
   - `priority`: 置信度 0-99
   - `dispatch`: 探测方法名
3. 按命令频率排序（最常见的 "show version" 优先），减少命令发送次数
4. 三种探测方式：标准命令输出匹配、SSH 远程版本匹配、登录横幅匹配
5. priority >= 99 立即返回；结果缓存避免重复发送相同命令

这是一种**启发式分类器**——不依赖 SSH 协议层面的设备识别，而是通过 CLI 输出的文本指纹判断设备类型。虽然不如 NETCONF/RESTCONF 等 API 精确，但适用于所有支持 SSH CLI 的设备。

## 洞察5：基于 paramiko 的 CLI screen-scraping 模型

netmiko 本质上是一个**终端屏幕抓取（screen-scraping）库**，其技术栈为：

```
netmiko（多厂商 CLI 自动化）
  → paramiko（SSH2 协议实现）
    → cryptography/bcrypt/pynacl（加密原语）
```

核心工作方式：
1. 使用 paramiko 的 `invoke_shell(term="vt100")` 建立交互式 PTY 会话
2. 通过 `write_channel()` 发送命令字符串 + 回车
3. 通过 `read_channel()` 读取终端输出字节
4. 使用正则表达式匹配提示符/模式判断命令执行完成
5. 使用字符串处理（strip_prompt/strip_command/normalize_linefeeds）清洗输出

这种模型的特点：
- **通用性强**：任何支持 SSH CLI 的设备都可以通过 screen-scraping 管理
- **脆弱性**：依赖文本格式，CLI 输出变化可能导致解析失败
- **延迟敏感**：需要等待设备返回提示符，使用全局延迟因子和超时控制
- **TextFSM/Genie 补完**：通过模板引擎将非结构化文本转为结构化数据
- `NoEnable`/`NoConfig` mixin 处理不同设备的权限模型差异

与 paramiko 的 `exec_command`（非交互式命令执行）不同，netmiko 始终使用 `invoke_shell`（交互式 shell），这是因为网络设备通常只支持 PTY 会话而不支持独立 exec 通道。跨束参考：[paramiko SSHClient](../../paramiko/concepts/02-ssh-client.md) 中 `invoke_shell` 与 `exec_command` 的区别。
