---
type: Concept
title: 安装与启动
description: 了解 Home Assistant 的安装方式、runner.py 进程入口、命令行参数、事件循环策略和单实例锁机制
tags: [home-assistant, smart-home, installation, runner, cli, beginner]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: "Home Assistant 验证工程师", at: "2026-08-22" }
status: verified
stale_after: 2027-08-23
sources:
  - id: core-source
    resource: "/references/core-source.md"
    title: Home Assistant 核心框架源码
  - id: tooling-source
    resource: "/references/tooling-source.md"
    title: Home Assistant 工具链与测试源码
---

# 安装与启动

## 安装方式

Home Assistant 提供多种安装方式，适用于不同的使用场景和技术水平。

### 1. Home Assistant Operating System（推荐）

这是官方推荐的完整安装方式，将 HA 作为专用操作系统安装在设备上（通常是树莓派、x86 小主机或虚拟机）。它包含：

- HA Core 运行时
- HA Supervisor（容器管理）
- Add-on 商店
- 自动备份和更新
- 本地 DNS 和 HTTPS（通过 Nabu Casa）

适合大多数用户，特别是不熟悉 Linux 的初学者。

### 2. Home Assistant Container

以 Docker 容器方式运行 HA Core：

```bash
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Asia/Shanghai \
  -v /path/to/config:/config \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

`--network=host` 是必须的，因为 HA 需要进行 mDNS/SSDP 设备发现。配置目录挂载到 `/config`。适合已有 Docker 环境的用户。

### 3. Python 虚拟环境安装

适合开发者或希望在现有 Linux 系统上直接运行 HA 的用户：

```bash
python3 -m venv .
source bin/activate
pip3 install homeassistant
hass --config /path/to/config
```

### 4. 开发模式安装（从源码）

用于 HA 核心开发或集成开发：

```bash
git clone https://github.com/home-assistant/core.git
cd core
python3 -m venv venv
source venv/bin/activate
pip3 install -e .
pip3 install -r requirements_test.txt
hass --config config
```

HA 要求 **Python 3.14.2 或更高版本**（`REQUIRED_PYTHON_VER = (3, 14, 2)`，定义于 `const.py:28`）。

## runner.py：进程入口

`homeassistant/runner.py` 是 HA 的进程启动入口。它负责在调用 bootstrap 之前完成所有底层运行时设置。入口函数是 `run()`（`runner.py:280`）。

### 启动链路

```text
python -m homeassistant
    → __main__.py: main()
    → runner.py: run()
    → runner.py: setup_and_run_hass()
    → bootstrap.py: async_setup_hass()
    → HomeAssistant 实例创建与运行
```

### RuntimeConfig

`run()` 函数接收一个 `RuntimeConfig` 数据类实例（`runner.py:155`），包含所有启动参数：

```python
@dataclass
class RuntimeConfig:
    config_dir: str                          # 配置目录路径
    skip_pip: bool = True                    # 跳过 pip 依赖安装
    recovery_mode: bool = False              # 恢复模式
    verbose: bool = False                    # 详细日志
    log_rotate_days: int | None = None       # 日志保留天数
    log_file: str | None = None              # 日志文件路径
    debug: bool = False                      # 调试模式
    import_config: str | None = None         # 导入配置
    safe_mode: bool = False                  # 安全模式
    cpu_check: bool = False                  # CPU 兼容性检查
    skip_pip_packages: list[str] = field(default_factory=list)
    runtime_dir: str | None = None           # 运行时目录
    log_no_color: bool = False               # 禁用日志颜色
```

`run()` 函数的主要步骤：

1. 记录启动者信息（通过 `getpass.getuser()` 和 `psutil` 检测父进程）
2. 调用 `ensure_single_execution()` 确保单实例运行
3. 设置自定义事件循环策略 `HassEventLoopPolicy`
4. 安装 `asyncio.set_event_loop_policy`
5. 如果启用了调试，启用 `asyncio.debug` 和 faulthandler
6. 获取事件循环
7. 调用 `setup_and_run_hass(runtime_config)` 协程

### 命令行参数

通过 `python -m homeassistant --help` 查看所有参数。常用参数：

| 参数 | 说明 |
|------|------|
| `-c, --config PATH` | 配置目录，默认 `~/.homeassistant` |
| `--safe-mode` | 安全模式，禁用自定义集成 |
| `--recovery-mode` | 恢复模式，仅加载核心功能 |
| `--debug` | 调试模式，启用 asyncio debug |
| `-v, --verbose` | 详细日志输出 |
| `--log-file PATH` | 日志输出到文件 |
| `--log-rotate-days N` | 日志按天轮转 |
| `--skip-pip` | 跳过依赖安装（默认跳过） |
| `--script SCRIPT` | 运行内置脚本（如 `influxdb_import`） |

## 事件循环策略

### HassEventLoopPolicy

`HassEventLoopPolicy`（`runner.py:176`）是 HA 自定义的 asyncio 事件循环策略，它根据 Python 版本和平台自动选择最优的事件循环实现：

- **Python 3.12+**：使用 `UnixEventLoopPolicy`（Linux/macOS）或默认策略（Windows）
- **调试模式**：在事件循环上启用 `set_debug(True)`

该策略的主要目的是确保 HA 在不同平台上使用正确的事件循环实现，并在测试环境中提供一致的行为。

### 线程池

HA 使用 `concurrent.futures.ThreadPoolExecutor` 执行阻塞操作（如文件 I/O、同步库调用）。最大工作线程数为 64（`MAX_EXECUTOR_WORKERS = 64`，`runner.py:43`）。`HassJob` 自动检测函数类型（协程/回调/普通函数），将普通函数调度到线程池执行。

### 任务取消超时

关闭时，HA 等待待处理任务完成的超时为 5 秒（`TASK_CANCELATION_TIMEOUT = 5`，`runner.py:44`），超时后强制取消。

## 单实例锁

`ensure_single_execution()`（`runner.py:118`）是一个上下文管理器，确保同一配置目录只有一个 HA 实例运行：

```python
@contextlib.contextmanager
def ensure_single_execution(config_dir: str):
    lock = asyncio.Runner(...)
    lock_path = os.path.join(config_dir, "home-assistant.log")
    with open(lock_path, "w") as fileno:
        try:
            fcntl.flock(fileno, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # 已有实例在运行
            raise
        yield
```

它使用文件锁（Unix `flock`）机制。如果检测到另一个实例正在使用同一配置目录，HA 将拒绝启动并输出错误信息。这防止了两个实例同时读写同一个配置目录导致的数据损坏。

> 注意：文件锁在 Windows 上的实现不同，但 HA 主要面向 Linux 部署。

## 配置目录

配置目录（Config Directory）是 HA 存储所有数据的地方，默认为 `~/.homeassistant/`（`CONFIG_DIR_NAME = ".homeassistant"`，`config.py:41`）。

### 目录结构

```text
config/
├── configuration.yaml      # 主配置文件
├── secrets.yaml             # 敏感信息（密码、API key）
├── automations.yaml         # 自动化配置
├── scripts.yaml             # 脚本配置
├── scenes.yaml              # 场景配置
├── groups.yaml              # 分组配置
├── customize.yaml           # 实体自定义
├── .storage/                # ConfigFlow 配置（JSON 文件）
│   ├── core.config_entries
│   ├── core.entity_registry
│   ├── core.device_registry
│   ├── auth
│   └── ...
├── deps/                    # 集成安装的 Python 依赖
├── custom_components/       # 自定义集成
├── tts/                     # TTS 音频缓存
├── www/                     # 前端自定义资源
├── backups/                 # 备份文件
└── home-assistant.log       # 日志文件
```

`configuration.yaml` 是主配置文件（`YAML_CONFIG_FILE = "configuration.yaml"`，`config.py:39`）。如果不存在，HA 首次启动时会从 `DEFAULT_CONFIG` 模板自动创建。

## 启动模式

### 正常模式

正常启动加载所有配置的集成。如果关键集成 `frontend`（`CRITICAL_INTEGRATIONS = {"frontend"}`，`bootstrap.py:280`）加载失败，HA 自动进入恢复模式。

### 安全模式（--safe-mode）

安全模式下不加载自定义集成（`custom_components/`），用于排查第三方集成导致的问题。

### 恢复模式（--recovery-mode）

恢复模式仅加载最核心的功能，不加载用户配置的集成。用于配置严重损坏时的修复。在恢复模式下，前端仍然可用，用户可以通过 UI 修复或移除问题配置。

## 开发环境启动

### 首次运行

```bash
# 克隆源码
git clone https://github.com/home-assistant/core.git
cd core

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装 HA（开发模式）
pip3 install -e .

# 安装测试依赖
pip3 install -r requirements_test.txt

# 启动
hass --config config
```

### 代码变更热重载

HA 不支持 Python 代码的热重载。修改核心代码或集成代码后需要重启 HA。但配置文件（YAML）变更可以通过以下方式重载：

- 前端"开发者工具 → YAML → 重载"
- 调用服务 `homeassistant.reload_core_config`
- 部分集成支持 `homeassistant.reload_config_entry`

### 日志配置

开发时可以通过命令行参数控制日志：

```bash
# 详细日志
hass -c config --verbose

# 调试模式（启用 asyncio debug）
hass -c config --debug

# 日志输出到文件
hass -c config --log-file home-assistant.log --log-rotate-days 7
```

也可以在 `configuration.yaml` 中配置 logger 集成：

```yaml
logger:
  default: info
  logs:
    homeassistant.core: debug
    custom_components.my_integration: debug
```

## 系统信号

HA 在 `runner.py` 中注册了系统信号处理器（通过 `helpers/signal.py`）：

| 信号 | 行为 |
|------|------|
| `SIGTERM` | 优雅关闭（停止接受新任务，等待进行中的任务完成） |
| `SIGINT`（Ctrl+C） | 同上 |
| `SIGHUP` | 部分系统上触发配置重载 |

关闭流程遵循 `CoreState` 状态机：`running → stopping → final_write → stopped`。在 `final_write` 阶段，所有集成执行最后的数据写入。

## 延伸阅读

- [HomeAssistant 核心对象](/concepts/03-core-object.md)
- [启动流程详解](/concepts/04-bootstrap-lifecycle.md)
- [配置系统](/concepts/05-configuration.md)

## 相关概念

- [启动流程](/concepts/04-bootstrap-lifecycle.md) — runner.py 之后的 bootstrap 阶段编排与集成加载顺序
- [配置系统](/concepts/05-configuration.md) — 配置目录结构、configuration.yaml 与 ConfigFlow 配置管理
- [HomeAssistant 核心对象](/concepts/03-core-object.md) — runner 创建并持有的 HomeAssistant 运行时根对象
