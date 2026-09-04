# scrapli2 架构洞察

> 基于 133 条源码事实的深度分析。R→I 阶段产物。

## 洞察一：Zig 核心 + Python ctypes 绑定的混合语言架构

scrapli2 最根本的架构决策是将核心协议逻辑从 Python 迁移到 Zig，编译为共享库（`libscrapli-*.so`/`.dylib`），Python 层仅通过 ctypes 做薄绑定。这一决策体现在：

- Python 侧不包含任何 SSH/Telnet 协议实现代码，所有网络 IO、协议状态机、提示符匹配、模式切换均在 Zig 层完成
- Python 侧的 `Cli`/`Netconf` 类本质上是 Zig 对象的句柄包装器，持有 `self.ptr: DriverPointer`（`c_void_p`）和 `self.poll_fd: int`
- 数据交换通过 `ZigSlice`（ptr+len）和 `ZigU64Slice` 结构体完成，所有字符串在跨边界时编码为 UTF-8 字节
- `ffi.py` 负责定位和加载预编译的共享库，支持 Linux（musl/gnu 双 ABI）和 macOS，不支持 Windows

**权衡**：Zig 带来了原生性能和内存安全（无 GC 暂停），但代价是：(1) 增加了跨语言 FFI 边界的复杂度和调试难度；(2) 平台支持受限（当前无 Windows 原生共享库）；(3) 用户无法像旧版纯 Python scrapli 那样用 monkey-patch 修改核心行为。与 paramiko 的纯 Python 实现和 asyncssh 的纯 Python asyncio 实现形成鲜明对比——后两者用户可深入阅读和修改协议栈任意层级，而 scrapli2 的核心是黑盒。

## 洞察二：Cli/Netconf 双驱动 + 同步/异步双 API 的正交组合设计

scrapli2 提供两个正交的设计维度：

**驱动维度**：`Cli` 面向网络设备命令行（基于 YAML 平台定义的提示符/模式系统），`Netconf` 面向 NETCONF 协议（基于 XML RPC 的标准操作集）。两者共享相同的 transport/auth/session 选项层和 FFI 基础设施，但各自有独立的 Result 类型和操作方法集。

**并发维度**：每个 IO 操作都提供同步和异步两个版本（`open`/`open_async`、`send_input`/`send_input_async` 等）。同步版使用 `select.select` 轮询 poll fd（`helper.py` 第91行），异步版使用 asyncio 事件循环的 `add_reader`（`helper.py` 第129行）。两种模式共享完全相同的 Zig 层操作逻辑——异步并非用线程池包装同步方法，而是在等待结果时切换 IO 多路复用机制。

这种设计使得用户可以在同一个应用中根据场景选择同步或异步风格，无需切换库。对比 paramiko（纯同步，异步需自行用线程池包装）和 asyncssh（纯异步，同步调用需运行事件循环），scrapli2 的双 API 设计覆盖了更广泛的使用场景。

## 洞察三：可插拔 Transport 模式与声明式平台定义

scrapli2 通过两个正交的扩展点实现多厂商/多协议支持：

**Transport 可插拔**：四种传输模式由 `TransportKind` 枚举定义——`BIN`（调用系统 OpenSSH 客户端）、`SSH2`（通过 libssh2 原生实现）、`TELNET`、`TEST`（从文件读取，用于测试）。每种模式有独立的 Options dataclass，通过 `apply()` 方法将配置写入 ctypes 结构体。BIN 模式利用系统 ssh 的成熟生态（ssh_config、known_hosts、ProxyJump），SSH2 模式提供无外部依赖的嵌入式方案。

**平台定义声明式**：44 个 YAML 文件替代了旧版 scrapli 中庞大的 Python 类继承树。每个 YAML 定义提示符正则、模式层级、模式间切换指令、开关连接时的自动指令、失败指示器等。Cisco IOS-XE 的定义展示了其表达力：4 个模式（exec/privileged_exec/configuration/tclsh）、模式间转换指令、`on_open` 自动执行 `term width 512`/`term len 0`、`failure_indicators` 匹配 Cisco 错误消息。对于 YAML 无法表达的"怪癖"（如 MikroTik 要求用户名追加 `+tc`），提供了 `definition_options/` Python 钩子机制。

这一设计使得新增厂商支持只需编写 YAML 文件，无需修改 Python 代码——比旧版 scrapli 的类继承和 netmiko 的庞大驱动层次更易维护。

## 洞察四：FFI 边界的类型安全与错误传播设计

scrapli2 的 FFI 边界设计体现了对类型安全和错误处理的深思熟虑：

- **类型映射**：所有 Python Options dataclass 都有对应的 ctypes Structure（`ffi_options.py`），`apply()` 方法显式将 Python 类型转换为 c 类型（`c_char_p`、`c_uint16`、`c_bool` 指针等），字符串同时传递指针和长度（防止缓冲区溢出）。
- **错误码枚举**：`LibScrapliFFIResult` IntEnum 将 Zig 层的 10 种错误状态映射到 Python 异常类层次，`raise_if_error()` 方法根据错误码抛出 `OutOfMememoryException`/`EOFException`/`TimeoutException`/`TransportException` 等特定异常。
- **操作级取消**：`Cancel` 类包装 `c_bool`，通过指针传递给 Zig 层，Python 侧调用 `cancel()` 可异步通知 Zig 中止操作。
- **原始输出延迟重构**：CLI Result 不直接存储原始字节，而是存储（清理后结果, 清理日志journal）对，首次访问 `results_raw` 时通过 FFI 调用 Zig 的重构函数重建。这减少了 FFI 边界的数据传输量。
- **敏感数据保护**：`AuthOptions.__repr__` 和 `LookupKeyValue.__repr__` 将密码和密钥显示为 `REDACTED`，防止日志泄露。

对比 paramiko 在 Python 层处理所有加密和协议（无 FFI 边界），scrapli2 的 FFI 层增加了复杂度但换取了核心逻辑的语言无关性——同一套 libscrapli 可被 Python（scrapli2）、Go（scrapligo）等语言绑定复用。

## 洞察五：结果获取的轮询模型与操作超时装饰器

scrapli2 的操作执行采用异步操作模型，而非同步请求-响应：

1. Python 调用 Zig 的 `send_input`/`open` 等函数，Zig 立即返回一个 `operation_id`（uint32）
2. Zig 在后台执行操作，完成后通过 poll fd 写入 4 字节的 operation_id 作为唤醒信号
3. Python 侧 `wait_for_available_operation_result` 轮询 poll fd，直到收到匹配的 operation_id
4. Python 再调用 `fetch_sizes` + `fetch` 两步获取结果数据（先获取各缓冲区大小，再分配内存获取实际数据）

`handle_operation_timeout` 装饰器实现了操作级超时控制：在调用被装饰函数前，通过 FFI 临时设置 Zig 层的 `operation_timeout_ns`，操作完成后（无论成功或异常）在 `finally` 块中无条件重置为 SessionOptions 配置的默认值。这意味着超时不是 Python 侧的 `signal.alarm` 或线程定时器，而是 Zig 层协议引擎原生感知的超时——Zig 可以在超时发生时正确清理连接状态。
