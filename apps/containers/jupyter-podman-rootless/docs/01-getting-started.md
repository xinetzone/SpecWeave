---
id: "jupyter-getting-started"
title: "快速开始"
source: "README.md#快速开始"
---

# 快速开始

## 前置条件

- **Podman**（推荐）或 **Docker** 已安装
- **Python ≥3.14**（用于运行 invoke 任务）
- Linux 宿主机需要 FUSE 支持（`--device /dev/fuse`）
- **可选**：`podman-compose`（声明式编排，推荐安装）
- **可选**：`podman-py`（SDK 后端，比 CLI 更高效）
- **可选**：`omlmd` + `olot[oras-py]`（ML 模型 OCI artifact 管理，容器内预装）

> 注：上面的 podman-compose / podman-py 是**宿主机 invoke 三层后端**所需（`pip install`）；镜像内已另行内嵌同源工具（含 toolbox），版本经 vendor/ 子模块固定、与宿主 pip 版本相互独立，详见 [17-upstream-tools.md](17-upstream-tools.md)。

## 安装 invoke

```bash
# 基础安装（CLI fallback模式）
pip install -e .

# 安装 podman-compose 支持（推荐，声明式编排）
pip install -e ".[compose]"

# 安装完整功能（podman-py SDK + podman-compose）
pip install -e ".[full]"
```

> ML 模型工具（omlmd/olot）预装在容器镜像内，宿主机无需安装。如需在宿主机直接使用：
>
> ```bash
> pip install -e ".[model]"
> ```

安装完成后，查看可用任务：

```bash
invoke --list
# 应列出13个命令：8核心（build/run/stop/status/shell/logs/exec/clean）+ 5 model.*
```

## 三种使用方式

### 方式一：invoke 封装（推荐，自动密码生成 + 路径转换 + 三层后端）

最简单的使用方式，自动处理所有细节：

```bash
# 1. 构建镜像（使用清华镜像源加速）
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 2. 启动容器（自动生成密码和token，自动创建.env）
invoke run

# 3. 查看访问信息（启动时会打印）
# SSH:  ssh -p 2222 devuser@localhost
# Jupyter Lab: http://localhost:8888/lab?token=<自动生成的token>
```

启动后会自动打印SSH和Jupyter访问信息，包括随机生成的密码和token。

常用invoke命令见 [02-invoke-reference.md](02-invoke-reference.md)。

### 方式二：直接使用 podman-compose（标准 Compose Spec）

如果你熟悉Docker Compose，可以直接使用podman-compose：

```bash
# 1. 复制环境变量模板
cp .env.example .env
# 编辑 .env 设置密码、端口、镜像源等

# 2. 构建并启动（后台运行）
podman-compose up -d --build

# 3. 查看状态
podman-compose ps

# 4. 查看日志
podman-compose logs -f

# 5. 进入容器
podman-compose exec jupyter bash

# 6. 停止并删除
podman-compose down
```

### 方式三：开发透传模式（Toolbx-style "透传优于隔离"）

开发阶段推荐使用透传模式，复用主机的SSH密钥、git配置、X11 GUI等：

```bash
# 启动时叠加 compose.dev.yaml，启用SSH agent + git config + X11 GUI + pip cache透传
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 同时启动本地模型仓库（用于OMLMD开发测试）
podman-compose -f compose.yaml -f compose.dev.yaml --profile registry up -d

# 容器内可直接使用主机SSH密钥push/pull代码
podman-compose exec jupyter git clone git@github.com:your/repo.git

# 容器内可运行GUI应用（需主机有X11/Wayland）
podman-compose exec jupyter xclock
```

透传配置详情见 [07-toolbx-passthrough.md](07-toolbx-passthrough.md)。

## 进入容器

```bash
# SSH方式
ssh -p 2222 devuser@localhost

# 或直接进入shell
invoke shell

# 在容器中执行命令
invoke exec --command "python --version"
```

## 作为 Toolbx 容器使用

镜像满足 Toolbx 兼容规范，可直接被 `toolbox` 命令使用，获得更深度的主机集成：

```bash
# 使用已构建的镜像创建Toolbx容器
toolbox create -i jupyter-podman-rootless:latest -c jupyter-dev

# 进入Toolbx容器（自动透传HOME/cwd/Wayland/X11/SSH agent等）
toolbox enter jupyter-dev
```

Toolbx会自动透传用户主目录、当前工作目录、Wayland/X11显示、SSH agent等，提供无缝的开发体验。

## 下一步

- 详细命令参考：[02-invoke-reference.md](02-invoke-reference.md)
- 环境变量配置：[03-environment-variables.md](03-environment-variables.md)
- 镜像架构说明：[04-image-architecture.md](04-image-architecture.md)
- Rootless Podman使用：[05-rootless-podman.md](05-rootless-podman.md)
- ML模型管理：[06-ml-model-management.md](06-ml-model-management.md)
- 常见问题：[13-faq.md](13-faq.md)

