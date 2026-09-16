---
id: "jupyter-podman-client-windows-wsl"
title: "Windows 11 × WSL2 支持"
source: "README.md#5-windows-11--wsl2-支持"
---
# Windows 11 × WSL2 支持

本项目显式支持 **Windows 11 原生 CPython 调用 podman-py SDK 连到 WSL2 内 / Podman Machine 的 Podman daemon**，无需用户手写 `base_url`，默认零配置即可运行。

## 三种落地路径（推荐度递减）

| 方案 | 技术路径 | 前置条件（一次性） |
|------|---------|------------------|
| ⭐⭐⭐⭐⭐ **WSL9P socket 直连** | Windows 原生 CPython → WSL2 发行版间 9P 互挂 unix socket：`unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock` | ① WSL2 发行版内：`sudo loginctl enable-linger $USER && systemctl --user enable --now podman.socket`  ② `/mnt/wsl/` 挂载点存在（WSL2 自带） |
| ⭐⭐⭐⭐ **Podman Machine** | 打开 Podman Desktop 初始化默认 Machine；SDK 通过 `active_service` 走 `http+ssh://` | 首次命令行执行：`podman machine ssh true`，在 `Are you sure ...?` 后敲 yes 写 known_hosts（否则 SDK SSH 子进程会阻塞在 stdin） |
| ⭐⭐⭐ **tcp loopback** | 手动 `podman system service tcp:127.0.0.1:8888 --time 0`；SDK 连 `tcp://127.0.0.1:8888` | 手动起 daemon；无认证仅建议本机 loopback |

## 连接优先级（默认 `PODMAN_CLIENT_SDK_STRATEGY=auto`）

1. **P0 环境变量覆盖**：`CONTAINER_HOST` / `DOCKER_HOST` 已设置则直接用（生产逃生舱）
2. **P1 WSL9P unix socket**（Windows 独有）：自动探测 发行版名（`WSL_DISTRO_NAME` → `wsl.exe -l -q` 默认 → `wsl.exe -l -v` Running 首个）和 UID（不硬编码 1000，通过 `wsl.exe -d <Distro> id -u` 取），拼出 `/mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock`
3. **P2 Podman Machine**：SDK `PodmanClient()` 默认 `from_env()` 会读 `containers.conf` 的 `active_service`，非 Machine 环境会跳过
4. **P3 tcp loopback**：`tcp://127.0.0.1:8888` 兜底
5. 全部失败：`get_client() yield None` → **CLI fallback**（走 Podman Desktop 的 `podman.exe` 子进程，保持 `jpman-podman-ops` Skill 既有行为 100% 兼容）

## 逃生舱（策略切换）

自动探测不符合预期时，临时切换（shell 级优先于 `.env`）：

```powershell
# 强制走 Podman Machine（只试 P0/P2，跳过 WSL9P/tcp）
$env:PODMAN_CLIENT_SDK_STRATEGY="machine"
invoke images

# 只连 WSL2（跳过 Machine/tcp）
$env:PODMAN_CLIENT_SDK_STRATEGY="wsl"
invoke images

# 退回到 v0.0.x 旧行为（只走 PodmanClient() 默认 from_env）
$env:PODMAN_CLIENT_SDK_STRATEGY="legacy"
invoke images
```

四种合法值：`auto | legacy | wsl | machine`。非合法值会被归一化回 `auto`。

## 挂载路径 vs 连接 URL（A/B 维度分离，避免混淆）

代码和文档中严格区分两个独立维度，维护者请勿混淆：

| 维度 | 说明 | 所在模块/函数 |
|------|------|-------------|
| **Dimension A · 容器卷挂载路径** | 启动容器时 `-v "D:\spaces:/mnt/d/spaces"` 的源路径转译：`D:\` → `/mnt/d/`，供容器内读工作区 | `src/jpman_client/tasks/utils.py::to_posix_path` |
| **Dimension B · SDK daemon 连接 URL** | `PodmanClient(base_url=...)` 所使用的 Podman daemon 监听地址，Windows 原生下必须显式给出 | `src/jpman_client/tasks/utils.py::sdk_base_url_candidates` + `src/jpman_client/tasks/client_core.py::get_client` |

两个维度彼此无依赖，可以单独配置：

```powershell
# 例：WSL9P 连 daemon（B 维），但工作区用 Windows D 盘原生路径（A 维自动转 /mnt/d）
$env:PODMAN_CLIENT_SDK_STRATEGY="wsl"
invoke run --workspace D:/spaces/SpecWeave
```

## 透明桥接 stdin 契约（非交互命令零转发）

经桥接（及 WSL 内原生）执行的所有编排命令**不转发父进程 stdin**：`jpman_common.proc.run_cmd` 默认向 invoke 传 `in_stream=False`，不创建 stdin 转发线程。原因：invoke 3.0.3 的 stdin 线程对 TTY 用 2 字节缓冲做 `FIONREAD`，而内核固定写回 4 字节 int，Python 3.14 加固后必抛 `SystemError: buffer overflow`，导致长任务"成功却 exit 1"的假失败（详见速查表 W-I13）。

- 桥接 stdin 是 console 中继 pty 而非管道：重定向 stdout（`> log`）不改变其 TTY 属性，崩溃与是否重定向无关。
- Ctrl+C 不依赖 stdin 转发：invoke 的 KeyboardInterrupt→send_interrupt 信号路径仍会中断 `logs -f` 与长任务。
- 唯一例外是真交互式入口（`invoke env.shell`、builder 的 `interact.shell`/exec），以 `forward_stdin=True` 显式 opt-in；其 py3.14 崩溃面由 `apply_invoke_stdin_compat()`（4 字节缓冲，同时替换 `invoke.terminals` 与 `invoke.runners` 绑定）在进程导入 `jpman_common.proc` 时自动兜底。

> **排障速查表（W-I1~W-I13 + C-I1~C-I5）** 见 [04-troubleshooting-guide.md](04-troubleshooting-guide.md)。