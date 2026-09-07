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
| `invoke run [--name N] [--tag T] [--ssh-port P] [--jupyter-port P] [--workspace W] [--user-password PW] [--jupyter-token TK] [--ssh-public-key KEY] [--grant-sudo/--no-grant-sudo] [--no-detach]` | `invoke container.run` | 启动容器 |
| `invoke stop [--name N]` | `invoke container.stop` | 停止并删除容器 |
| `invoke status [--name N]` | `invoke container.status` | 查看状态 |
| `invoke clean [--name N] [--tag T] [--volume] [--image]` | `invoke container.clean` | 清理资源 |

配置合并优先级：`命令行参数 > .env 环境变量 > ContainerConfig 默认值`。

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

### 5.4 30 秒修复速查表（Windows 专属坑 W-I1~W-I3）

`invoke` 失败时终端会自动匹配以下三条，每个条目末尾附一行命令级修复：

| ID | 触发异常 | 根因 | 修复（30秒） |
|----|---------|------|------------|
| **W-I1** | `FileNotFoundError: .../run/user/.../podman/podman.sock No such file` | podman-py 无参构造回退是纯 Linux 路径，Windows 原生不存在该目录 | 三选一：a) 脚本改在 WSL2 内跑  b) 打开 Podman Desktop 初始化 Machine  c) `$env:CONTAINER_HOST="unix:///mnt/wsl/Ubuntu/run/user/1000/podman/podman.sock"` |
| **W-I2** | `ValueError: Unsupported URL scheme 'npipe'` | docker-py 老用户粘贴 `npipe:////./pipe/docker_engine`；podman-py 合法 scheme 中不含 npipe | 改成：`unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock` / `ssh://...` / `tcp://127.0.0.1:8888` |
| **W-I3** | `Timeout: Waiting on podman-forward-*.sock`（SSH Machine） | SSH 首次 StrictHostKeyChecking 交互阻塞在 stdin yes/no，SDK SSHSocket shell-out 的 `ssh -N -L` 子进程永不返回 | PowerShell 先跑一次：`podman machine ssh true`，提示 `Are you sure you want to continue connecting (yes/no/[fingerprint])?` 时敲 **yes** 回车，把 Machine HostKey 写入 `~/.ssh/known_hosts` |

### 5.5 挂载路径 vs 连接 URL（A/B 维度分离，避免混淆）

代码和文档中严格区分两个独立维度，维护者请勿混淆：

| 维度 | 说明 | 所在模块/函数 |
|------|------|-------------|
| **Dimension A · 容器卷挂载路径** | 启动容器时 `-v "D:\spaces:/mnt/d/spaces"` 的源路径转译：`D:\` → `/mnt/d/`，供容器内读工作区 | `tasks/utils.py::to_posix_path` |
| **Dimension B · SDK daemon 连接 URL** | `PodmanClient(base_url=...)` 所使用的 Podman daemon 监听地址，Windows 原生下必须显式给出 | `tasks/utils.py::sdk_base_url_candidates` + `tasks/client_core.py::get_client` |

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

## 8. .env 配置完整清单

复制 `.env.example` 为 `.env`，按需修改（与构建端容器级变量名保持一致；新增 **Windows WSL SDK 级变量** 三个）。
配置合并优先级：**命令行参数 > shell export 的环境变量 > .env 文件 > ContainerConfig 默认值**。

### 8.1 容器级（两端通用，与构建端一致）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CONTAINER_NAME` | `jupyter-podman` | 容器名，`--name` 参数覆盖 |
| `IMAGE_TAG` | `localhost/jupyter-podman-rootless:latest` | 加载镜像后运行的 tag |
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

> `.env` 文件中的 SDK 级变量由 `tasks/manage.py::_load_env_overrides` 中的 `load_dotenv(override=False)` 同步到 `os.environ`，
> 因此 shell 里已显式 `export` / `$env:` 的值不会被 `.env` 覆盖，符合"命令行 > .env > 默认"约定。

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
