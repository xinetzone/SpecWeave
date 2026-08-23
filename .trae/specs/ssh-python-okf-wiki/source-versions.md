# Source Code Versions

> 克隆日期: 2026-08-23
> 克隆方式: `git clone --depth 1` (SSH 协议)
> 存储路径: `d:\spaces\SpecWeave\external\libs\`

| Package | Commit Hash | Version | Package Dir | Notes |
|---------|------------|---------|-------------|-------|
| paramiko | d60d5c17d78f | 5.0.0 | paramiko/ | 纯 Python SSH2 协议库；版本通过 `importlib.metadata` 从 pyproject.toml 读取；依赖 cryptography、bcrypt、pynacl；无 src/ 布局；69 个 .py 文件 |
| fabric | ded51893f02c | 4.0.0 | fabric/ | 基于 paramiko/invoke 的高层 SSH 自动化工具；版本定义在 `fabric/_version.py`；无 src/ 布局；49 个 .py 文件 |
| asyncssh | 25370783e5c1 | 2.24.0 | asyncssh/ | 基于 asyncio 的异步 SSH 客户端/服务端库；版本定义在 `asyncssh/version.py`；含 crypto/ 子包；无 src/ 布局；147 个 .py 文件 |
| pexpect | fc8f062518b4 | 4.9.0 | pexpect/ | 纯 Python expect 风格交互控制库；版本定义在 `pexpect/__init__.py`；含 pxssh SSH 模块；无 src/ 布局；98 个 .py 文件 |
| netmiko | 8ace5f2ae7da | 4.7.0 | netmiko/ | 多厂商网络设备 SSH 库，基于 paramiko；版本定义在 `netmiko/__init__.py`；支持 100+ 网络平台，按厂商分子包；无 src/ 布局；348 个 .py 文件 |
| scrapli | 343e149b6eba | 0.0.0 (dev) | scrapli/ | **Zig + Python 混合架构**（非纯 Python）：核心传输层 libscrapli 用 Zig 编写，编译为共享库后通过 ctypes 调用；构建依赖 ziglang==0.16.0；Zig 源码在独立仓库 github.com/scrapli/libscrapli；支持 SSH2/libssh2、telnet、system binary 三种传输；pyproject.toml 中包名为 "scrapli2"（大版本重写）；__version__ 为 CI 发布时注入的占位符；libscrapli 核心版本 0.0.1-rc.35；无 src/ 布局；73 个 .py 文件 |

## 架构备注

### scrapli 架构详解

scrapli 是这六个库中唯一非纯 Python 的项目：

- **核心层 (Zig)**: `libscrapli` 是一个 Zig 编写的共享库，负责实际的 SSH/Telnet 连接和 I/O，源码托管在独立的 [scrapli/libscrapli](https://github.com/scrapli/libscrapli) 仓库
- **绑定层 (Python ctypes)**: `scrapli/ffi.py` 通过 `ctypes` 加载编译好的共享库，`ffi_mapping*.py` 和 `ffi_types.py` 定义 Python 与 C ABI 之间的类型映射
- **传输模式**:
  - `BIN`: 调用系统 ssh 二进制
  - `SSH2`: 通过 libssh2（Zig 编译）进行原生 SSH
  - `TELNET`: 原生 Telnet
  - `TEST`: 测试用
- **构建**: `pyproject.toml` 声明 `ziglang==0.16.0` 为构建依赖，安装时自动编译 Zig 代码
- **设备定义**: 使用 YAML 文件（`scrapli/definitions/`）声明各厂商平台的交互模式

### 其余 5 个库

paramiko、fabric、asyncssh、pexpect、netmiko 均为纯 Python 实现（paramiko/fabric/netmiko 依赖 cryptography 等 C 扩展作为依赖项，但自身代码为纯 Python）。
