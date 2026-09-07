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

## 5. 作为 SDK 使用（Python import）

```python
from pathlib import Path
from invoke import MockContext

from tasks.client_core import load_image, run_container, stop_container
from tasks.utils import ContainerConfig, default_build_cache_dir, find_latest_image_tar

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

## 6. 内置纪律（rootless 三必需参数）

所有启动路径（SDK 与 CLI）均自动携带以下参数，调用方无需关心：

- `--device /dev/fuse`
- `--security-opt label=disable`
- `--cgroupns=host`

对应 `jpman-podman-ops` Skill 中 rootless 容器三必需纪律。
默认不使用 `--privileged`。

## 7. .env 配置

复制 `.env.example` 为 `.env`，按需修改（与构建端变量名保持一致）。
命令行参数会覆盖 `.env` 中的同名变量。

## 8. 与 jpman CLI 的分工

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
