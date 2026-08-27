---
id: "jupyter-rootless-podman"
title: "Rootless Podman 说明"
source: "README.md#rootless-podman-说明"
---
# Rootless Podman 说明

容器内预装 rootless Podman 环境，devuser 可在容器内运行容器（Docker-in-Podman / DinP 模式），实现容器嵌套。

## 快速验证

进入容器后验证Podman可用：

```bash
# 查看Podman版本和信息
podman info

# 运行测试容器（在容器内运行容器！）
podman run --rm docker.io/library/hello-world
```

## 关键配置

Rootless Podman需要以下特殊配置（容器镜像已预置）：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **存储驱动** | fuse-overlayfs | rootless模式下的overlay存储，需要宿主机传`--device /dev/fuse` |
| **运行时** | crun | 轻量级OCI运行时，兼容rootless |
| **Cgroup 管理器** | cgroupfs | rootless模式下使用cgroupfs而非systemd |
| **subuid/subgid** | `devuser:100000:65536` | 为devuser分配65536个从属UID/GID |
| **安全选项** | `--security-opt label=disable` | 禁用SELinux标签，避免FUSE权限问题 |
| **Cgroup 命名空间** | `--cgroupns=host` | 使用宿主机cgroup命名空间 |

## 宿主机运行要求

运行容器时必须添加以下参数（invoke的`run`命令已自动添加）：

```bash
podman run -d \
  --name jupyter-podman \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  -p 2222:22 -p 8888:8888 \
  jupyter-podman-rootless
```

关键参数说明：
- `--device /dev/fuse`：将FUSE设备传入容器，fuse-overlayfs需要
- `--security-opt label=disable`：禁用SELinux标签，否则FUSE挂载可能失败
- `--cgroupns=host`：共享宿主机cgroup命名空间，rootless Podman需要

## 存储配置

容器内Podman存储配置在 `/home/devuser/.config/containers/storage.conf`：

```toml
[storage]
driver = "fuse-overlayfs"
runroot = "/run/user/1000/containers"
graphroot = "/home/devuser/.local/share/containers"

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

- `graphroot`：容器和镜像存储在devuser家目录下，不占用宿主机root空间
- `runroot`：运行时数据存储在XDG_RUNTIME_DIR（tmpfs，重启消失）

## 使用场景

容器内的Podman可用于：

1. **开发测试容器**：在Jupyter环境中构建和测试其他容器镜像
2. **ML模型拉取**：OMLMD/OLOT工具使用Podman进行OCI镜像操作
3. **本地registry**：运行model-registry服务作为本地OCI仓库
4. **Toolbx兼容**：镜像本身满足Toolbx规范，可被toolbox命令管理

## 常见问题

### Q: Podman报错 "fuse: device not found"？

确保运行容器时添加了 `--device /dev/fuse` 参数。invoke的run命令已自动添加。

### Q: Podman拉取镜像很慢或失败？

检查网络连接。容器内Podman默认使用宿主机网络，可配置镜像加速器。

### Q: 容器内Podman无法运行？

验证配置：
```bash
# 检查subuid/subgid配置
cat /etc/subuid
cat /etc/subgid
# 应显示 devuser:100000:65536

# 检查fuse设备
ls -la /dev/fuse
# 应存在且权限正确

# 检查Podman配置
podman info --debug
```

### Q: 需要特权模式吗？

不需要。rootless Podman在非特权模式下运行，只需要`--device /dev/fuse`和`--security-opt label=disable`即可正常工作。
