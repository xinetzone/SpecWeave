---
id: "jupyter-direct-cli-usage"
title: "直接使用 Podman/Docker 命令"
source: "README.md#直接使用-podmandocker-命令不通过-invoke"
---
# 直接使用 Podman/Docker 命令

如果不想用 invoke，也可以直接使用容器运行时命令。这提供了最大的灵活性，适合熟悉Podman/Docker CLI的用户。

## 构建镜像

### 使用Podman构建

```bash
# 基础构建
podman build -t jupyter-podman-rootless .

# 使用国内镜像源加速（推荐）
podman build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=tuna \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=tuna \
  .

# 使用阿里云镜像源
podman build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=aliyun \
  --build-arg PIP_MIRROR=aliyun \
  .

# 不使用缓存（完全重新构建）
podman build -t jupyter-podman-rootless --no-cache .

# 自定义标签
podman build -t my-jupyter:dev -t my-jupyter:latest \
  --build-arg APT_MIRROR=tuna \
  .
```

### 使用Docker构建（兼容）

镜像兼容Docker，可直接用docker命令构建：

```bash
docker build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=tuna \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=tuna \
  .
```

### 构建时可用的build-arg

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `APT_MIRROR` | official | APT镜像源：official/tuna/aliyun |
| `CONDA_MIRROR` | official | Conda镜像源：official/tuna/aliyun |
| `PIP_MIRROR` | official | PIP镜像源：official/tuna/aliyun |
| `PYTHON_VERSION` | 3.14 | Python版本 |
| `PYTHON_BUILD` | cp314t | Python构建类型（cp314t=free-threading, cp314=标准GIL） |

## 运行容器

### 基础运行

```bash
podman run -d \
  --name jupyter-podman \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  -p 2222:22 \
  -p 8888:8888 \
  -v ./workspace:/workspace \
  -e USER_PASSWORD=yourpassword \
  -e JUPYTER_TOKEN=yourtoken \
  jupyter-podman-rootless
```

**关键参数说明（必须）：**
- `--device /dev/fuse`：将FUSE设备传入容器（fuse-overlayfs需要）
- `--security-opt label=disable`：禁用SELinux标签（避免FUSE权限问题）
- `--cgroupns=host`：使用宿主机cgroup命名空间（rootless Podman需要）

### 完整参数示例

```bash
podman run -d \
  --name jupyter-podman \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  -p 2222:22 \
  -p 8888:8888 \
  -v ./workspace:/workspace \
  -e USER_PASSWORD=devpass123 \
  -e JUPYTER_TOKEN=mytoken123 \
  -e GRANT_SUDO=yes \
  -e APT_MIRROR=tuna \
  --restart unless-stopped \
  jupyter-podman-rootless
```

### 环境变量参考

运行时可用的`-e`环境变量详见 [03-environment-variables.md](03-environment-variables.md)。

### Docker运行（兼容）

```bash
docker run -d \
  --name jupyter-podman \
  --device /dev/fuse \
  --security-opt label=disable \
  -p 2222:22 -p 8888:8888 \
  -v ./workspace:/workspace \
  jupyter-podman-rootless
```

> **注意**：Docker的rootless模式支持可能不如Podman完善，推荐使用Podman。

## 调试模式

直接进入bash，不启动服务：

```bash
# Podman调试模式
podman run -it --rm \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  jupyter-podman-rootless bash

# Docker调试模式
docker run -it --rm \
  --device /dev/fuse \
  --security-opt label=disable \
  jupyter-podman-rootless bash
```

调试模式下：
- 不启动sshd、jupyter、supervisord
- 直接以root用户进入bash
- 可手动执行entrypoint步骤调试
- 退出后容器自动删除（--rm）

### 启用调试输出

```bash
podman run -it --rm \
  --device /dev/fuse \
  --security-opt label=disable \
  -e DEBUG=1 \
  jupyter-podman-rootless bash
```

`DEBUG=1`会在entrypoint中启用`set -x`，输出详细执行日志。

## 常用管理命令

```bash
# 查看容器状态
podman ps
podman inspect jupyter-podman

# 查看日志
podman logs jupyter-podman
podman logs -f jupyter-podman  # 实时跟踪

# 进入容器（devuser）
podman exec -it -u devuser jupyter-podman bash

# 进入容器（root）
podman exec -it jupyter-podman bash

# 在容器中执行命令
podman exec -u devuser jupyter-podman python --version
podman exec -u devuser jupyter-podman pip list

# 停止容器
podman stop jupyter-podman

# 删除容器
podman rm jupyter-podman

# 删除镜像
podman rmi jupyter-podman-rootless

# 清理所有停止的容器和未使用的镜像
podman container prune
podman image prune
```

## 健康检查

```bash
# 手动执行健康检查脚本
podman exec jupyter-podman /usr/local/bin/healthcheck.sh

# 查看健康状态
podman healthcheck run jupyter-podman

# 查看健康检查日志
podman inspect jupyter-podman --format '{{.State.Health}}'
```

## 直接使用podman-compose（推荐）

如果安装了podman-compose，可直接使用标准compose命令：

```bash
# 构建并启动
podman-compose up -d --build

# 查看状态
podman-compose ps

# 查看日志
podman-compose logs -f

# 进入容器
podman-compose exec jupyter bash

# 停止并删除
podman-compose down

# 开发透传模式
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 启动模型仓库
podman-compose --profile registry up -d
```
