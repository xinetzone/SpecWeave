# scrapli 知识束生成任务指导书

## 路径
- 源码: `d:\spaces\SpecWeave\external\libs\scrapli\scrapli\`
- 输出: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\scrapli\`
- 事实: `.trae\specs\ssh-python-okf-wiki\scrapli-facts.md`
- 洞察: `.trae\specs\ssh-python-okf-wiki\scrapli-insights.md`
- 格式参考: `bundles\networking\paramiko\index.md`

## 版本: scrapli2 0.0.0-dev, commit 343e149b6eba
**重要：这是 scrapli 大版本重写版（包名 scrapli2），Zig + Python 混合架构。**

### 实际架构
- **核心层**: libscrapli 用 Zig 编写（独立仓库 github.com/scrapli/libscrapli），编译为共享库
- **绑定层**: Python 通过 ctypes 调用 Zig 共享库（`ffi.py`, `ffi_mapping*.py`, `ffi_types.py`, `ffi_options.py`）
- **Python API 层**: Cli 类、Netconf 类、Options 数据类、Result 类
- **平台定义**: YAML 文件（definitions/ 目录，44 个平台定义）
- 不包含旧版 scrapli 的 driver/transport/channel 三层 Python 类

### 公开 API（从 __init__.py 确认）
- `Cli` — CLI 驱动主类（cli.py）
- `Netconf` — NETCONF 驱动类（netconf.py）
- `AuthOptions` — 认证选项（auth.py，别名 Options）
- `SessionOptions` — 会话选项（session.py，别名 Options）
- `TransportBinOptions` — BIN 传输选项（调用系统 ssh）
- `TransportSsh2Options` — SSH2 传输选项（libssh2 via Zig）
- `TransportTelnetOptions` — Telnet 传输选项
- `TransportTestOptions` — 测试传输选项
- `LookupKeyValue` — 键值查找
- `ReadCallback` — 读回调

### Cli 类核心方法（从 cli.py Grep 确认）
- `open()` / `open_async()` — 打开连接
- `close()` / `close_async()` — 关闭连接
- `send_input()` / `send_input_async()` — 发送单条命令
- `send_inputs()` / `send_inputs_async()` — 发送多条命令
- `send_inputs_from_file()` / `send_inputs_from_file_async()` — 从文件发送
- `send_prompted_input()` / `send_prompted_input_async()` — 带提示的输入
- `read()` — 读取字节
- `read_with_callbacks()` / `read_with_callbacks_async()` — 回调读取
- 上下文管理器: `__enter__/__exit__`, `__aenter__/__aexit__`

### 核心模块
- `cli.py` — Cli 类、LoadedDefinition、InputHandling 枚举
- `netconf.py` — Netconf 类
- `cli_result.py` — Result 类（CLI 命令结果）
- `netconf_result.py` — NETCONF 结果
- `cli_decorators.py` / `netconf_decorators.py` — 操作超时处理装饰器
- `cli_parse.py` — 输出解析
- `transport.py` — 传输选项（Bin/Ssh2/Telnet/Test）
- `session.py` — 会话选项
- `auth.py` — 认证选项
- `exceptions.py` — 异常体系
- `ffi.py` — ctypes FFI 绑定
- `helper.py` — 工具函数
- `definitions/` — YAML 平台定义
- `definition_options/` — 定义选项扩展

## R 阶段（50+ 事实）
阅读以上模块提取 F-001~F-050+。重点：
- Cli.__init__ 参数（platform/host/auth_options/session_options/transport_options/transport 等）
- Cli.open/close 连接生命周期
- send_input 参数（channel_input、strip_prompt、failed_when、send_inputs 等）
- Result 对象结构（result、failed、elapsed_time 等）
- 四种 Transport 模式（BIN=系统ssh、SSH2=libssh2、TELNET、TEST）
- FFI ctypes 绑定机制（ZigSlice、指针操作）
- YAML 平台定义加载机制
- 同步/异步双 API 设计
- Netconf 类基本方法
- 异常体系

**禁止推断词，只记录代码中客观存在的内容。**

## I 阶段（3-5 洞察）
1. Zig 核心 + Python ctypes 绑定的混合语言架构——性能与开发效率的权衡
2. Cli/Netconf 双驱动 + 同步/异步双 API 的组合设计
3. 可插拔 Transport 模式（BIN/SSH2/Telnet/Test）
4. YAML 声明式平台定义替代旧版 Python 类继承
5. FFI 边界设计——ctypes 类型映射与 ZigSlice 数据交换

## E 阶段

### references/scrapli-source.md（先生成）
- 准确记录：这是 scrapli2 重写版、Zig+Python 混合架构、版本 0.0.0-dev、libscrapli 独立仓库
- 核心模块清单、公开 API、四种 Transport 说明
- 与旧版 scrapli（v202x）的架构差异说明

### concepts/（≥8篇）
1. `00-introduction.md` — scrapli 简介、scrapli2 重写、Zig+Python 架构、安装
2. `01-getting-started.md` — 第一个 Cli 连接、platform 参数、发送命令
3. `02-transport-layer.md` — 四种 Transport：BIN（系统ssh）、SSH2（libssh2）、Telnet、Test；Transport Options
4. `03-auth-session.md` — AuthOptions、SessionOptions、认证与会话配置
5. `04-cli-driver.md` — Cli 类详解：open/close、上下文管理器、send_input/send_inputs
6. `05-async-mode.md` — open_async/send_input_async、async with、asyncio 集成
7. `06-platform-definitions.md` — YAML 定义系统、LoadedDefinition、44 个内置平台、自定义定义
8. `07-netconf.md` — Netconf 类、NETCONF 操作、与 CLI 的对比
9. `08-advanced-patterns.md` — read_with_callbacks、send_prompted_input、send_inputs_from_file、Result 对象、异常处理、FFI 架构深入

### examples/（≥4篇）
1. `basic-connect.md` — 基础连接与命令发送
2. `send-commands.md` — 单条/批量命令发送
3. `async-parallel.md` — 异步并行连接多设备
4. `custom-driver.md` — 自定义平台定义与高级用法

### index.md 文件（最后生成）

## Frontmatter
tags 包含 scrapli，stale_after: 2027-06-30（scrapli2 仍在开发中，API 可能变化）
跨束交叉引用:
- paramiko: `../../paramiko/concepts/02-ssh-client.md`
- asyncssh: `../../asyncssh/concepts/02-async-connection.md`

## V 阶段 Grep 验证（必须严格执行）
在 `external/libs/scrapli/scrapli/` 中验证所有类名和方法名。
**注意：旧版 scrapli 的 Scrapli/AsyncScrapli/NetworkDriver/Driver/Channel 等类在本版本中不存在！**
本版本只有 Cli 和 Netconf 两个主驱动类。
必验: Cli, Netconf, AuthOptions, SessionOptions, TransportBinOptions, TransportSsh2Options, TransportTelnetOptions, Result, LoadedDefinition, InputHandling, ReadCallback, LookupKeyValue
必验方法: open, open_async, close, close_async, send_input, send_input_async, send_inputs, send_inputs_async, send_inputs_from_file, send_prompted_input, read, read_with_callbacks

## 返回
事实数、文件列表、虚构 API 修复、Grep 验证摘要、架构形态确认。
