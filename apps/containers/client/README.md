# jupyter-podman-client（镜像消费端）

> **定位**：`apps/containers/jupyter-podman-rootless` 镜像构建端的**消费端**。
> 基于 `podman-py` 从本地加载构建端产出的镜像，并提供极简的容器生命周期管理。
>
> - 需要快速启停、日常驾驶（status/shell/logs 等）→ 用构建端的 `jpman` CLI
> - 需要 Python 脚本化集成、在其他应用里以 SDK 方式加载/运行镜像 → 用本项目

## 1. 与构建端的关系

```
apps/containers/
├── jupyter-podman-rootless/   ← 构建端（Containerfile + invoke + jpman CLI）
│   └── .image-cache/          ← 构建端 save 产出的 tar.gz 缓存目录（git 忽略）
└── client/                    ← 本项目：消费端（podman-py SDK + invoke）
```

消费端的默认加载路径：
```
../jupyter-podman-rootless/.image-cache/<latest-timestamp>.tar.gz
```
（即自动从构建端的最新缓存加载，无需手工传路径。）

## 2. 安装

> 需要 Python ≥ 3.14（与构建端 `py314` 环境对齐）。

```bash
cd apps/containers/client
pip install -e .
# 验证
invoke --list
```

## 3. 快速开始

### 步骤 0：构建端先 save 出镜像缓存（首次/改镜像后）

```bash
cd ../jupyter-podman-rootless
bash bin/jpman rebuild-all    # 或 invoke build
bash bin/jpman save           # 产出 .image-cache/*.tar.gz
```

### 步骤 1：消费端加载镜像

```bash
cd ../client
# 方式 A：自动从构建端 .image-cache 选最新 tar.gz（推荐）
invoke load

# 方式 B：显式指定路径
invoke load --path /mnt/d/backup/jupyter-podman-rootless-xxxx.tar.gz
```

### 步骤 2：启动容器

```bash
# 使用默认配置（端口 2222/8888，工作区 ./workspace）
invoke run

# 指定工作区路径（Windows D 盘会自动转 /mnt/d）
invoke run --workspace D:/spaces/SpecWeave

# 显式传密码/token，不自动生成
invoke run --user-password mypass --jupyter-token mytoken32charsxxxxxxxx
```

启动成功后会打印 SSH/Jupyter URL 与挂载信息。

> **🛟 排障：JupyterLab 看不到 `.temp` / `.env` / `.gitignore` 等隐藏项**
>
> 症状：项目目录里的 `.temp`、`.env`、`.image-cache` 等以 `.` 开头的项在 JupyterLab 文件树里不显示。
> 根因：JupyterLab 前端默认**隐藏以 `.` 开头的文件/目录**——与服务端无关（服务端
> `ContentsManager/FileContentsManager.allow_hidden=True` 已内置）；挂载与容器内文件均正常，仅展示层隐藏。
> 修复：JupyterLab 顶部菜单 **View → Show Hidden Files** 勾选后即显示
> （`.temp` 为空目录时勾选后可见但为空，写入内容并刷新后即可看到文件）。

### 步骤 3：状态/停止/清理

```bash
invoke status        # 查看状态
invoke stop          # 停止+删除容器（保留镜像与工作区）
invoke clean --image # 连镜像一起删
invoke images        # 列出本地所有镜像
```

## 4. 命令速查

| 命令 | 等价 container.* 别名 | 说明 |
|---|---|---|
| `invoke load [--path TAR] [--cache-dir DIR]` | `invoke container.load` | 从 tar.gz 加载镜像 |
| `invoke images` | `invoke container.images` | 列出本地镜像 |
| `invoke run [--name N] [--tag T] [--ssh-port P] [--jupyter-port P] [--workspace W] [--user-password PW] [--jupyter-token TK] [--ssh-public-key KEY] [--grant-sudo/--no-grant-sudo] [--no-detach] [--host-network/--no-host-network] [--wayland/--no-wayland] [--gpu/--no-gpu] [--usb/--no-usb] [--dbus/--no-dbus]` | `invoke container.run` | 启动容器（后 5 组为运行时透传三态开关，见 §11） |
| `invoke stop [--name N]` | `invoke container.stop` | 停止并删除容器 |
| `invoke status [--name N]` | `invoke container.status` | 查看状态 |
| `invoke clean [--name N] [--tag T] [--volume] [--image]` | `invoke container.clean` | 清理资源 |
| `invoke env.build-layer [--tag T] [--base-image I] [--no-cache]` | —（无别名） | 构建容器内自举叠加层镜像（见 §10） |
| `invoke env.run-cmd --cmd CMD [--tag T] [--keep] [--extra-mount M]` | —（无别名） | 在自举容器内执行单条命令（rootless 三必需 + workspace/.image-cache 双挂载） |
| `invoke env.shell [--tag T] [--workspace W] [--cache-dir D]` | —（无别名） | 进入自举容器的交互式 bash shell |

> **布尔项统一为三态**：`--x` 显式开启 / `--no-x` 显式关闭（可覆盖 `.env` 开启项）/ 两者都不给才回落 `.env` → 默认。
> `run` 任务已关闭 invoke 自动短选项（`auto_shortflags=False`），**只承诺长选项契约**——此前自动短名顺序敏感且误导
> （实测 `-h` 被 `--ssh-public-key` 抢走致使 `invoke run -h` 报错、`--host-network` 退化到短名 `-`）。

配置合并优先级：`命令行参数 > .env 环境变量 > ContainerConfig 默认值`。

**SSH known_hosts 自动维护**：每次执行 `invoke run` 时，启动流程会自动扫描并清理 `~/.ssh/known_hosts` 中与当前 `SSH_PORT`（默认 2222）匹配的 `[localhost]:PORT` / `[127.0.0.1]:PORT` 过期条目，然后尝试用 `ssh-keyscan` 写入最新 key。JPMan 容器重建后 host key 必然变更，此逻辑消除了手动干预需求。

## 5. Windows 11 × WSL2 支持

本项目显式支持 **Windows 11 原生 CPython 调用 podman-py SDK 连到 WSL2 内 / Podman Machine 的 Podman daemon**，无需用户手写 `base_url`，默认零配置即可运行。

### 5.1 三种落地路径（推荐度递减）

| 方案 | 技术路径 | 前置条件（一次性） |
|------|---------|------------------|
| ⭐⭐⭐⭐⭐ **WSL9P socket 直连** | Windows 原生 CPython → WSL2 发行版间 9P 互挂 unix socket：`unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock` | ① WSL2 发行版内：`sudo loginctl enable-linger $USER && systemctl --user enable --now podman.socket`  ② `/mnt/wsl/` 挂载点存在（WSL2 自带） |
| ⭐⭐⭐⭐ **Podman Machine** | 打开 Podman Desktop 初始化默认 Machine；SDK 通过 `active_service` 走 `http+ssh://` | 首次命令行执行：`podman machine ssh true`，在 `Are you sure ...?` 后敲 yes 写 known_hosts（否则 SDK SSH 子进程会阻塞在 stdin） |
| ⭐⭐⭐ **tcp loopback** | 手动 `podman system service tcp:127.0.0.1:8888 --time 0`；SDK 连 `tcp://127.0.0.1:8888` | 手动起 daemon；无认证仅建议本机 loopback |

### 5.2 连接优先级（默认 `PODMAN_CLIENT_SDK_STRATEGY=auto`）

1. **P0 环境变量覆盖**：`CONTAINER_HOST` / `DOCKER_HOST` 已设置则直接用（生产逃生舱）
2. **P1 WSL9P unix socket**（Windows 独有）：自动探测 发行版名（`WSL_DISTRO_NAME` → `wsl.exe -l -q` 默认 → `wsl.exe -l -v` Running 首个）和 UID（不硬编码 1000，通过 `wsl.exe -d <Distro> id -u` 取），拼出 `/mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock`
3. **P2 Podman Machine**：SDK `PodmanClient()` 默认 `from_env()` 会读 `containers.conf` 的 `active_service`，非 Machine 环境会跳过
4. **P3 tcp loopback**：`tcp://127.0.0.1:8888` 兜底
5. 全部失败：`get_client() yield None` → **CLI fallback**（走 Podman Desktop 的 `podman.exe` 子进程，保持 `jpman-podman-ops` Skill 既有行为 100% 兼容）

### 5.3 逃生舱（策略切换）

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

### 5.4 30 秒修复速查表（Windows 原生坑 W-I1~W-I4 + 容器/运行时坑 C-I1~C-I3）

`invoke` 失败时终端会自动匹配以下条目（前三条为 Windows 原生坑；C-I1~C-I3 为容器/运行时坑且**与平台无关**），每个条目末尾附一行命令级修复：

| ID | 触发异常 | 根因 | 修复（30秒） |
|----|---------|------|------------|
| **W-I1** | `FileNotFoundError: .../run/user/.../podman/podman.sock No such file` | podman-py 无参构造回退是纯 Linux 路径，Windows 原生不存在该目录 | 三选一：a) 脚本改在 WSL2 内跑  b) 打开 Podman Desktop 初始化 Machine  c) `$env:CONTAINER_HOST="unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock"` |
| **W-I2** | `ValueError: Unsupported URL scheme 'npipe'` | docker-py 老用户粘贴 `npipe:////./pipe/docker_engine`；podman-py 合法 scheme 中不含 npipe | 改成：`unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock` / `ssh://...` / `tcp://127.0.0.1:8888` |
| **W-I3** | `Timeout: Waiting on podman-forward-*.sock`（SSH Machine） | SSH 首次 StrictHostKeyChecking 交互阻塞在 stdin yes/no，SDK SSHSocket shell-out 的 `ssh -N -L` 子进程永不返回 | PowerShell 先跑一次：`podman machine ssh true`，提示 `Are you sure you want to continue connecting (yes/no/[fingerprint])?` 时敲 **yes** 回车，把 Machine HostKey 写入 `~/.ssh/known_hosts` |
| **W-I4** | `AttributeError: module 'os' has no attribute 'getuid'` 或 `module 'socket' has no attribute 'AF_UNIX'` | **podman-py 在 Windows 原生 CPython 结构性不可用**：`from_env()` 回退链调用 `os.getuid()`（[path_utils.py](https://github.com/containers/podman-py/blob/main/podman/api/path_utils.py)），unix/ssh 适配调用 `socket.AF_UNIX`（[uds.py](https://github.com/containers/podman-py/blob/main/podman/api/uds.py)），Windows 原生 Python 两者皆无 → 任一候选必然 AttributeError，与配置无关 | 本工具已**自动降级 CLI fallback**（`podman.exe` 子进程，正常可用）；确认可用后无需操作。如需**强制 SDK**：a) 改在 WSL2 内跑本脚本（100% Linux 行为）b) 显式设 `CONTAINER_HOST=ssh://user@127.0.0.1:<MachinePort>/run/user/1000/podman/podman.sock`（端口用 `podman system connection list --format json` 查询）。P2-machine 候选在 Windows 原生已由 `machine_connection_uri()` 自动填充该 ssh:// 值 |
| **C-I1** | 同一 `FileNotFoundError: .../run/user/.../podman/podman.sock No such file`，但出现在**容器内** SDK 调用（bootstrap `env.run-cmd`/`env.shell` 或常驻容器 JupyterLab Web Terminal）；容器内 CLI `podman images` 同时报 `open ${XDG_RUNTIME_DIR}/libpod/tmp/pause.pid: no such file or directory` 与 `error creating temporary file: Permission denied` | 容器内两个根因叠加：① 从无运行中的 podman daemon（bootstrap 用 `--entrypoint /usr/bin/tini` 跳过 `entrypoint.sh::setup_podman()`，或常驻容器旧版从不拉起 service），`from_env()` 回退到纯 Linux 默认路径连不存在的 rootless UDS socket → `APIError`；② rootless podman 初始化时未预建 `${XDG_RUNTIME_DIR}/libpod/tmp/`（`pause.pid` 落盘目录），缺目录触发 ENOENT / `Permission denied`（devuser 自 2026-09-11 起固定 UID 1000） | bootstrap 由 `PODMAN_SERVICE_BOOT` 自动拉起 `podman system service --time=0` 并预建 `libpod/tmp`（见 `src/jpman_client/tasks/env_in_container.py`）；常驻容器由方案 A 保证：`entrypoint.sh::setup_podman()` 默认拉起 service + 预建 `${XDG_RUNTIME_DIR}/libpod/tmp` + `jupyter.conf` 改 `user=devuser` 并以 `%(ENV_CONTAINER_HOST)s` / `%(ENV_XDG_RUNTIME_DIR)s` 继承 entrypoint 导出的运行时路径（路径以 `id -u` 动态派生，**不在配置里写死 `/run/user/<uid>`**）；详见 `summary-jpman-client-podman-sdk-file-not-found-20260908.md` |
| **C-I2** | 同上 `PermissionError` 类，但为 **`[Errno 13] Permission denied` / EACCES**（非 ENOENT）：SDK 报 `podman/api/uds.py::UDSSocket.connect() → PermissionError: [Errno 13] Permission denied`；CLI 报 `dial unix /run/user/<uid>/podman/podman.sock: connect: permission denied` | **容器内 devuser 无权访问宿主直通 socket**：宿主 rootless socket（宿主 `<uid>:<gid>` 0660）经 bind-mount + userns 映射进容器后呈现为 `root:root 0660`，而 devuser 是非 root UID（固定 1000，≠0）且镜像基线未将其加入 socket 属组（`/etc/group` 的 `root:x:0:` 无成员）→ `socket.connect()` 直接 EACCES。**与 C-I1 的语义差异**：C-I1 是 socket/目录不存在（ENOENT），C-I2 是存在但无权限（EACCES）。**代价与红线**：让 devuser 入 socket 属组会扩大其组权限；**严禁 `chmod 666`/`chown` 宿主 socket**（会改到宿主 socket 本体、破坏宿主侧权限） | `entrypoint.sh::setup_podman()` 的 **B-scheme** 分支自动 `stat -Lc '%G' <host_sock>` 解析属组并 `usermod -aG <socket组> ${NON_ROOT_USER}`，随后以 devuser 身份实测 socket 可读写（`su - devuser -c "test -r/-w ..."`，失败仅告警不阻断）。**时机关键**：该步骤必须早于 `exec /usr/bin/supervisord`——supervisord 的 `drop_privileges()` 在 spawn 子进程时才用 `grp.getgrall()` 派生补充组，已在运行的 jupyter 进程不受后续 usermod 影响，故须重建镜像/重启容器生效。自检：容器内 `supervisorctl status jupyter` 取 PID 后 `/proc/<pid>/status` 的 `Groups` 应含 socket 属组 |

| **C-I3** | podman 原生报错 `Error: statfs <路径>: no such file or directory`（卷缺失）或 `Error: stat <路径>: no such file or directory`（设备缺失），退出码 125 | **运行时透传资源在 daemon 宿主上不存在**：`--wayland` / `--gpu` / `--usb` / `--dbus` 挂载的 socket 或设备节点是 **WSL2 / Podman Machine 内**的路径，而 podman 对缺失路径**硬失败且不会自动创建**（`:ro`/`:rw`/裸挂载表现一致）；客户端可能跑在 Windows 原生 CPython 上，本机 `Path.exists()` 对这些路径必然为假，**故不做本机预检**（否则会误判并拒绝正确的透传请求） | 先确认资源在 daemon 宿主真实存在：`podman machine ssh "test -e <路径>"`（Machine）或 `wsl -d <Distro> -- test -e <路径>`（WSL2）；路径不同则用 `HOST_XDG_RUNTIME_DIR` / `HOST_WAYLAND_DISPLAY` / `DBUS_SESSION_BUS_PATH` / `GPU_DEVICE` / `USB_DEVICE` 覆盖；宿主本就不具备该资源时**去掉对应开关**（详见 §11） |

### 5.5 挂载路径 vs 连接 URL（A/B 维度分离，避免混淆）

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

## 6. 作为 SDK 使用（Python import）

```python
from pathlib import Path
from invoke import MockContext

from jpman_client.tasks.client_core import load_image, run_container, stop_container
from jpman_client.tasks.utils import ContainerConfig, default_build_cache_dir, find_latest_image_tar

ctx = MockContext()

# 1) 加载镜像
tar = find_latest_image_tar(default_build_cache_dir())
result = load_image(ctx, tar)
assert result.loaded, result.message

# 2) 启动容器
cfg = ContainerConfig(
    image="localhost/jupyter-podman-rootless:latest",
    workspace="/mnt/d/spaces/SpecWeave",
    ssh_port=2222,
    jupyter_port=8888,
)
run_container(ctx, cfg)

# ... 使用完毕 ...
stop_container(ctx, cfg.name)
```

## 7. 内置纪律（rootless 三必需参数）

所有启动路径（SDK 与 CLI）均自动携带以下参数，调用方无需关心：

- `--device /dev/fuse`
- `--security-opt label=disable`
- `--cgroupns=host`

对应 `jpman-podman-ops` Skill 中 rootless 容器三必需纪律。
默认不使用 `--privileged`。

> **运行身份（user=root 覆盖本镜像的 USER=devuser）**：`client` 镜像是构建端叠加的消费端镜像，
> `Containerfile` 固化 `USER=devuser`（non-root）。但镜像的 `entrypoint.sh` 需以 **root** 执行初始化
> （`setup_passwords` 的 `chpasswd` 写 `/etc/shadow`、写 `/root/.jupyter`、启动 supervisord），
> 若以 devuser 运行会触发 PAM `chpasswd` 失败，容器在 `set -euo pipefail` 下立即退出（`Exited (1)`）。
> 因此 `ContainerConfig` 内置 `user="root"`，`invoke run` 以 root 启动 entrypoint，
> **supervisord 内部再降权给 devuser 跑 jupyter/sshd**——对用户完全透明，无需感知。

## 8. .env 配置完整清单

复制 `.env.example` 为 `.env`，按需修改（与构建端容器级变量名保持一致；新增 **Windows WSL SDK 级变量** 四个）。
配置合并优先级：**命令行参数 > shell export 的环境变量 > .env 文件 > ContainerConfig 默认值**。

### 8.1 容器级（两端通用，与构建端一致）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CONTAINER_NAME` | `jupyter-podman` | 容器名，`--name` 参数覆盖 |
| `IMAGE_TAG` | `localhost/jupyter-podman-client:latest` | 加载镜像后运行的 tag |
| `SSH_PORT` | `2222` | 宿主 → 容器的 SSH `-p 2222:22` 映射 |
| `JUPYTER_PORT` | `8888` | 宿主 → 容器的 Jupyter `-p 8888:8888` 映射 |
| `WORKSPACE` | `./workspace` | 挂载到容器 `/home/devuser/workspace` 的宿主工作区 |
| `USER_PASSWORD` | （空 = 自动生成 12 位打印） | devuser shell 登录密码 |
| `JUPYTER_TOKEN` | （空 = 自动生成 32 位打印） | Jupyter 登录 token |
| `SSH_PUBLIC_KEY` | （空） | 追加到 `~devuser/.ssh/authorized_keys` 的公钥内容 |
| `GRANT_SUDO` | `yes` | 是否给 devuser 开 NOPASSWD sudo，opt-out 写 `no` |

### 8.2 Windows WSL SDK 级（仅消费端，可选；默认 auto 可全省略）

| 变量 | 合法值 | 说明 |
|------|--------|------|
| `PODMAN_CLIENT_SDK_STRATEGY` | `auto` / `legacy` / `wsl` / `machine` | SDK 连接策略，shell 优先级高于 .env |
| `WSL_DISTRO_NAME` | 任意 `wsl.exe -l -q` 能列出的发行版名 | P1 WSL9P 路径第一级回退，省略则 3 级探测 |
| `CONTAINER_HOST` | 合法 podman-py scheme | **最高优先级**显式 daemon URL，用于 P0 覆盖；常见值见速查表 |
| `DOCKER_HOST` | 同上 | 兼容兜底，优先级低于 `CONTAINER_HOST` |

> `.env` 文件中的 SDK 级变量由 `src/jpman_client/tasks/manage.py::_load_env_overrides` 中的 `load_dotenv(override=False)` 同步到 `os.environ`，
> 因此 shell 里已显式 `export` / `$env:` 的值不会被 `.env` 覆盖，符合"命令行 > .env > 默认"约定。

### 8.3 运行时透传（消费端新增；与构建端 `docs/07-toolbx-passthrough.md` 的分层覆盖逐项对应）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PASSTHROUGH_HOST_NETWORK` | `no` | ① Host 网络模式（不发布端口；SSH=`localhost:<SSH_PORT>`，Jupyter=`localhost:8888`） |
| `PASSTHROUGH_WAYLAND` | `no` | ② Wayland 套接字透传 |
| `PASSTHROUGH_GPU` | `no` | ③ GPU 透传 |
| `PASSTHROUGH_DBUS` | `no` | ④ D-Bus 会话总线透传 |
| `PASSTHROUGH_USB` | `no` | ⑤ USB 透传 |
| `HOST_XDG_RUNTIME_DIR` | `/run/user/<PODMAN_RUNTIME_UID>`（默认 1000） | daemon 宿主运行时目录（②④ 的基准路径） |
| `HOST_WAYLAND_DISPLAY` | `wayland-0` | ② Wayland socket 名（**daemon 宿主**侧的实例名，不是客户端环境变量） |
| `DBUS_SESSION_BUS_PATH` | `<HOST_XDG_RUNTIME_DIR>/bus` | ④ 会话总线 socket 路径 |
| `GPU_DEVICE` | `/dev/dri` | ③ GPU 设备节点 |
| `USB_DEVICE` | `/dev/bus/usb` | ⑤ USB 设备路径 |

> 布尔项写法：`yes/true/1/on` 为真，`no/false/0/off` 为假。**三态优先级**：
> `--x`（显式开启）> `--no-x`（显式关闭，可覆盖 `.env`）> 未指定时才读 `.env` > 内置默认。
> 资源路径全部在 **daemon 宿主** 侧解析，缺失时表现为 C-I3（见 §5.4 与 §11.2）。

## 9. 与 jpman CLI 的分工

| 维度 | jpman（构建端） | client（消费端） |
|---|---|---|
| 入口 | `bash bin/jpman` / `jpman.ps1` | `pip install -e .` 后 `invoke` / Python import |
| 构建镜像 | ✅ `rebuild / rebuild-all` | ❌ 只消费 |
| 镜像缓存 save/load | ✅ 双路 | ✅ load 单向（从 tar 恢复） |
| wsl-export / keepalive | ✅ 支持 | ❌ |
| ML 模型管理 (omlmd/olot) | ✅ 支持 | ❌ |
| podman-compose 后端 | ✅ Tier 1 | ❌ 仅 SDK + CLI fallback |
| podman-py SDK 作为一等公民 | 可选依赖 `.[full]` | **强制核心依赖** |
| 面向用户 | 人类驾驶员（日常操作） | 自动化集成 / 其他应用嵌入调用 |

## 10. 在容器中使用客户端自举（env.* 命令）

如果宿主没有 Python ≥ 3.14 / podman-py SDK / invoke，或希望在**隔离环境**
中使用消费端（例如 CI、临时排障、给不希望安装本地依赖的同事），
可直接基于 `localhost/jupyter-podman-rootless:latest` 构建一个叠加层镜像，
镜像内已经装好 conda `main`（即 Python 3.14t cp314t free-threading，
`/opt/conda/envs/main/bin` 位于 PATH 顶端）+ editable 版本的
`jupyter-podman-client`，进入后可直接 `inv load/run/stop/status`。

> **注意**：基础镜像的 conda 环境名是 **`main`**（不是 `py314`），登录
> shell（bash -l）会通过 `~/.bashrc` + `/etc/profile.d/conda-init.sh`
> 自动激活；非交互 RUN 阶段直接用 PATH 上的 `python -m pip` 即可，
> 不要 `conda activate py314`（不存在）。

### 10.1 首次/源码修改后：构建叠加层

```bash
cd apps/containers/client

# 构建叠加层（单层 COPY + pip install -e，层缓存复用率极高，<1 分钟）
invoke env.build-layer
# 等价：invoke env.build-layer --tag localhost/jupyter-podman-client:latest \
#                        --base-image localhost/jupyter-podman-rootless:latest

# 强制全量重建（忽略所有 Docker 层缓存，适用于基础镜像或 Containerfile 改动后）
invoke env.build-layer --no-cache
```

> **构建上下文说明**：`podman build` 以 client 根目录为 build context，`COPY .` 会把整个目录打包，但受 `.containerignore` 过滤（`.image-cache/`、`workspace/`、`.env`、`__pycache__/` 等已剔除），实际打包内容最小化。

产出镜像：`localhost/jupyter-podman-client:latest`。

### 10.2 单条命令执行（脚本化）

```bash
# 在容器内跑 inv --list，验证环境 OK
invoke env.run-cmd --cmd "inv --list"

# 在容器内加载宿主缓存的镜像（宿主 ./.image-cache 会自动挂载到容器 /workspace/.image-cache）
invoke env.run-cmd --cmd "inv load"

# 启动 jupyter-podman-rootless 容器（与在宿主本地直接 inv run 行为一致）
invoke env.run-cmd --cmd "inv run --workspace /workspace"
```

默认挂载（宿主路径 → 容器路径）：
- `$IMAGE_CACHE_DIR`（或 `./.image-cache`）→ `/workspace/.image-cache`
- `workspace`（或 `IMAGE_CACHE_DIR` 的父目录）→ `/workspace`

额外挂载：
```bash
invoke env.run-cmd \
  --cmd "ls /extra" \
  --extra-mount "D:/data:/extra" \
  --extra-mount "D:/models:/models"
```

### 10.3 交互式 shell（人类排障）

```bash
invoke env.shell
# 进入后会自动激活 conda main + cd /workspace + 打印欢迎语
#   === jupyter-podman-client 自举环境 ===
#   [可用命令]  inv --list   inv load   inv run   inv stop   inv status
#   [退出]      exit
(in-container) $ inv --list
(in-container) $ inv load
(in-container) $ inv run --workspace /workspace
```

> **🛟 中文乱码排查（仅 Windows / Trae Sandbox 默认 chcp 936 时）**
>
> 症状：`invoke env.*` / `inv --list` 等命令的中文任务描述出现 `娓呯悊瀹瑰櫒` 之类的错位字符。
> 根因：**三层字符集错配**：容器/Podman 管道输出 bytes 永远 = UTF-8，而 Windows PowerShell 5 / Trae Sandbox 默认 chcp 936 (GBK) 在解码这些 bytes。
> 修复：`src/jpman_client/tasks/utils.py::_ensure_win32_stdout_transcode()` 已在 `run_cmd()` 入口自动执行以下双端修复（模块级单例只初始化一次）：
>
> 1. **B 端捕获修复（源头不乱码）：`invoke c.run(..., encoding='utf-8')` 强制 UTF-8 解码子进程 stdout bytes → `Result.stdout` 里的 str 就是正确中文。
> 2. **A 端打印修复：用 `kernel32.GetConsoleOutputCP()` 获取宿主真实代码页（通常 936），通过 `io.TextIOWrapper` 把 `sys.stdout` / `sys.stderr` 换壳编码成宿主实际解码端一致的 bytes（trae-sandbox 收到 cp936 解码 → 中文正确显示。
> 3. **逃生舱（如仍出现个别 `?` 字符）：这些字符大概率不在 GBK 字符集中（如某些异体字 / Unicode 私人区的 挙 ），属于文档 / 代码源文件中的字符串中使用全角标点；可改用 GB2312/GBK 可直接表示的常见简体中文即可。
> 4. 容器层加固：Containerfile.client ENV 追加 `PYTHONIOENCODING=UTF-8` + `PYTHONUTF8=1`，保证容器内 invoke 也永远输出 UTF-8 bytes。
>

### 10.4 叠加镜像内约定（由 Containerfile.client 保证）

| 约定 | 值 | 说明 |
|------|---|---|
| 默认用户 | `devuser`（固定 UID/GID 1000） | 与基础镜像一致，non-root；2026-09-11 起固定 1000（此前被基础镜像 ubuntu 账号挤到 1001） |
| Python 环境 | `conda main`（cp314t free-threading，`/opt/conda/envs/main/bin`） | 登录 shell 自动激活；PATH 顶端已生效 |
| 客户端安装路径 | `/opt/apps/containers/client/`（editable） | `_project_root()` 锚点完整 |
| WORKDIR | `/workspace` | `Path.cwd()` 与宿主期望一致 |
| SDK 策略 | `PODMAN_CLIENT_SDK_STRATEGY=legacy` | 容器内 pure-Linux，直接 `from_env()`，不走 Windows 多候选 |
| 容器内 SDK 前置条件 | `env.run-cmd` / `env.shell` 会先启动 `podman system service --time=0` | R1 修复：bootstrap 用 `--entrypoint /usr/bin/tini` 跳过 entrypoint、supervisord 只监督 Jupyter，容器内从无运行中 daemon；若未提前拉起 service，`from_env()` 会连不存在的默认 UDS socket `/run/user/<UID>/podman/podman.sock` 报 `FileNotFoundError`（被 urllib3 包装成 `APIError`） |
| 默认缓存目录 | `IMAGE_CACHE_DIR=/workspace/.image-cache` | 可被宿主挂载覆盖 |
| 自举容器 rootless | `/dev/fuse + label=disable + cgroupns=host` | 与 `ContainerConfig` 硬编码对齐，**不使用 `--privileged`** |
| 容器名（默认） | `jpman-client-env`（用完自动 `--rm` 删除） | 可通过 `--name` 覆盖 |

### 10.5 叠加层基底指纹防陈旧机制（`base-digest` 检测，2026-09-11）

**问题本质：镜像 tag 是移动指针，叠加层固化的是 digest（不可变指纹）。**

`localhost/jupyter-podman-client:latest` 是一个「叠加镜像」——基于 `localhost/jupyter-podman-rootless:latest`（基底）加一层 `COPY + pip install -e` 构建。**`invoke run` 使用的不是基底 tag，而是叠加镜像构建那一刻固化的基底内容**。基底 tag 之后被更新（重建 / `invoke load`）不会传导给已构建的叠加层，导致「容器跑的还是旧基底」。

**解决机制闭环（三环节）**：

1. **构建时固化**（`invoke env.build-layer`）：构建前取基底当前 digest，经 `--build-arg BASE_DIGEST` 烤进叠加镜像 LABEL（`org.specweave.base-image` / `org.specweave.base-digest`，见 [Containerfile.client](Containerfile.client) 末尾）。指纹保存在**构建时快照**，运行时不重算。
2. **启动前比对**（`invoke run` → [manage.py::_warn_if_layer_stale](src/jpman_client/tasks/manage.py)）：读叠加层 LABEL 的固化 digest，与本地基底当前 digest 比较；不一致打印中文警告并给出重建指引。**只警告不阻断**（旧基底可能是有意选择）。
3. **一键恢复**（`invoke run --rebuild-layer`，B 档 2026-09-11 新增）：检测到陈旧时自动执行 `env.build-layer` 重建叠加层，随后继续正常启动；**重建失败自动回退旧基底启动**（不因重建失败而让容器起不来）。

```bash
# 启动前检测到「叠加层基底陈旧」警告时，两条路径任选：
invoke run --rebuild-layer          # 推荐：自动重建+重启（失败回退旧基底）
invoke run                          # 继续用旧基底（有意保持；警告仅提示）

# 手动重建（等价）
invoke env.build-layer && invoke stop && invoke run
# 确定有意使用旧基底 / 不想每次看到警告
# （.env 或 export）JPUMAN_SKIP_BASE_CHECK=1
```

**层级不变式**：LABEL 放在 Containerfile **末尾**（仅新增薄层），前置 COPY/pip 层缓存不受基底变化影响——重建叠加层通常 <1 分钟（见 §10.1）。

## 11. 运行时透传（对齐构建端 `docs/07-toolbx-passthrough.md`）

构建端把 5 项运行时透传以 **compose 分层覆盖文件**交付；消费端没有 compose 层（SDK/CLI 编程式启动），
等价形态是 `invoke run` 的 **5 个独立布尔开关**，语义逐项对齐：

| # | 开关 | 等价覆盖文件 | 宿主前置条件 |
|---|------|-------------|-------------|
| ① | `--host-network` | `compose.passthrough.yaml`（Host 网络） | 宿主 `22`/`8888`（或 `<SSH_PORT>`/`8888`）未被占用 |
| ② | `--wayland` | `compose.passthrough.gui.yaml` | daemon 宿主存在 Wayland socket |
| ③ | `--gpu` | `compose.passthrough.gpu.yaml` | daemon 宿主存在 `GPU_DEVICE`（默认 `/dev/dri`） |
| ④ | `--dbus` | `compose.passthrough.yaml`（D-Bus） | daemon 宿主存在会话总线 socket |
| ⑤ | `--usb` | `compose.passthrough.usb.yaml` | daemon 宿主存在 `USB_DEVICE`（默认 `/dev/bus/usb`） |
| ⑥ | `--video` | —（client 扩展，usbipd 挂载后 UVC 字符设备） | daemon 宿主存在 `/dev/video0-3`（可用 `VIDEO_DEVICES` 指定） |

**默认全关（默认隔离）**：不带任何开关时生成的运行参数与旧版本完全一致（输出零变化），
rootless 三必需 `/dev/fuse + label=disable + cgroupns=host` 始终硬编码保留，**任何路径都不使用 `--privileged`**。

```bash
# 主层等价：Host 网络 + D-Bus
invoke run --host-network --dbus

# 按宿主能力叠加（示例：图形会话 + GPU）
invoke run --host-network --dbus --wayland --gpu
```

`--no-<开关>` 可**显式关闭** `.env` 中已开启的同名项，无需修改 `.env`：

```bash
# .env 里 PASSTHROUGH_GPU=yes 时，临时关闭 GPU 透传（例如切到无 /dev/dri 的宿主）
invoke run --no-gpu
```

同一对开关不可同时给出（`--gpu --no-gpu` 会报参数冲突）。

### 11.1 Host 网络模式的端口语义

* 不发布端口映射（`--network host` 与 `-p` 互斥）
* SSH 走 `--ssh-port`（默认 2222）：rootless Podman 无法绑定特权端口 22，消费端会自动把
  `SSHD_PORT` 设为该值——基础镜像的 `entrypoint.sh` 支持该变量，而 `Containerfile.client`
  `FROM localhost/jupyter-podman-rootless:latest` 并继承其 ENTRYPOINT/CMD，故开箱可用
* Jupyter 固定为容器内 `8888`；此时 `--jupyter-port` 不生效，运行时会打印告警

### 11.2 缺资源时的行为（C-I3）

消费端**不做本机存在性预检**：透传资源由 daemon 宿主（WSL2 / Podman Machine）解析，而客户端
可能跑在 Windows 原生 CPython 上，本机 `Path.exists()` 对这些路径必然为假。podman 对缺失源
硬失败（退出码 125、不自动创建）后，消费端会把原生报错翻译为 **C-I3** 指引（见 §5.4）：
给出缺失路径、可覆盖的变量名，以及 daemon 侧自检命令。

### 11.3 三大透传的宿主侧前置（2026-09-11 实测）

三项透传（Wayland / GPU / USB）的资源**都在 daemon 宿主**（podman machine / WSL2）侧，
消费端 `.env` 只负责把开关与路径转成 `invoke run` 参数。以下为各资源的宿主就绪方法。

**② Wayland（WSLg）**

```bash
# 关键：podman machine 的 Wayland socket 在 /mnt/wslg（WSLg），不在 /run/user/1000
# 必须把 HOST_XDG_RUNTIME_DIR 设为 /mnt/wslg/runtime-dir，client 才能拼出
# {xdg}/wayland-0 命中该 socket
ls /mnt/wslg/runtime-dir/wayland-0     # 应存在 srwxrwxrwx

# .env：
#   PASSTHROUGH_WAYLAND=yes
#   HOST_XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
```

容器内验证：`printenv WAYLAND_DISPLAY`=wayland-0，`/tmp/runtime-user/wayland-0` 为可写 socket。

**③ GPU（NVIDIA → CDI）**

```bash
# NVIDIA 下 /dev/dri 不存在（那是 Intel/AMD Mesa 路径）；WSL2 NVIDIA 走
# /dev/dxg（DXCore）+ /usr/lib/wsl/lib/libcuda*，必须用 CDI 设备引用
sudo dnf install -y golang-github-nvidia-container-toolkit    # Fedora（VM 内）
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# .env：
#   PASSTHROUGH_GPU=yes
#   GPU_DEVICE=nvidia.com/gpu=all            # CDI 引用（原样透传）
#   # GPU_DEVICE=/dev/dri                    # Intel/AMD 时（映射容器内 /dev/dri）
```

容器内验证：`nvidia-smi` 显示真实 GPU（Driver/CUDA 版本）。

**⑤ USB（usbipd-win）**

```powershell
# Windows：安装 + 绑定（需管理员；绑定的设备在 attach 期间由 WSL 独占）
winget install --id Dorssel.usbipd-win
& "C:\Program Files\usbipd-win\usbipd.exe" bind --busid <BUSID>        # 一次
# Windows：挂载到目标 WSL 发行版（每次会话）
& "C:\Program Files\usbipd-win\usbipd.exe" attach --wsl podman-machine-default --busid <BUSID>
# 用毕归还 Windows
& "C:\Program Files\usbipd-win\usbipd.exe" detach --busid <BUSID>
```

```bash
# VM 内确认 + 安装排障工具（摄像头采集需 v4l2）
sudo dnf install -y v4l-utils usbutils
lsusb                                   # 应列出绑定的设备（如 Bison Integrated RGB Camera）
ls /dev/video*                          # 摄像头 → /dev/video0/1/2

# .env：
#   PASSTHROUGH_USB=yes
```

`usbipd list` 中设备 STATE 由 `Not shared` → `Shared` 即绑定成功；attach 后 VM 内
`/dev/bus/usb` 出现 001/002 目录。**注意**：attach 是一次性会话操作，VM/podman
machine 重启后需重新 attach。

> ✅ **Video 透传（2026-09-11 新增）**：`--video`（或 `.env` `PASSTHROUGH_VIDEO=yes`）把
> UVC 摄像头字符设备透传给容器——默认 `/dev/video0-3`，可用 `VIDEO_DEVICES=/dev/video0,/dev/video1`
> 精确指定。配合 `--usb`（USB 总线级）即可在容器内用 v4l2/OpenCV 直接采集摄像头。
> 前置：先完成上方 usbipd bind/attach 使摄像头在 daemon 宿主出现 `/dev/video*`；
> 缺失时 podman 硬失败（exit 125），走 C-I3 诊断。

