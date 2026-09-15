---
id: "jupyter-podman-client-invoke-reference"
title: "Invoke 命令参考"
source: "README.md#4-命令速查"
---
# Invoke 命令参考

## 命令速查

| 命令 | 等价 container.* 别名 | 说明 |
|---|---|---|
| `invoke load [--path TAR] [--cache-dir DIR]` | `invoke container.load` | 从 tar/tar.gz 加载镜像 |
| `invoke images` | `invoke container.images` | 列出本地镜像 |
| `invoke save [--tag T] [--cache-dir DIR]` | `invoke container.save` | 导出镜像到缓存目录（备份/恢复；产物含 manifest+SHA256，见 [01-getting-started.md](01-getting-started.md)） |
| `invoke run [--name N] [--tag T] [--ssh-port P] [--jupyter-port P] [--workspace W] [--user-password PW] [--jupyter-token TK] [--ssh-public-key KEY] [--grant-sudo/--no-grant-sudo] [--no-detach] [--host-network/--no-host-network] [--wayland/--no-wayland] [--gpu/--no-gpu] [--usb/--no-usb] [--dbus/--no-dbus] [--rebuild-layer]` | `invoke container.run` | 启动容器（透传三态开关见 [09-passthrough.md](09-passthrough.md)；`--rebuild-layer` 基底陈旧时自动重建叠加层，见 [08-env-bootstrap.md](08-env-bootstrap.md)） |
| `invoke stop [--name N]` | `invoke container.stop` | 停止并删除容器 |
| `invoke status [--name N]` | `invoke container.status` | 查看状态 |
| `invoke clean [--name N] [--tag T] [--volume] [--image]` | `invoke container.clean` | 清理资源 |
| `invoke env.build-layer [--tag T] [--base-image I] [--no-cache]` | —（无别名） | 构建容器内自举叠加层镜像（见 [08-env-bootstrap.md](08-env-bootstrap.md)） |
| `invoke env.run-cmd --cmd CMD [--tag T] [--keep] [--extra-mount M]` | —（无别名） | 在自举容器内执行单条命令（rootless 三必需 + workspace/.image-cache 双挂载） |
| `invoke env.shell [--tag T] [--workspace W] [--cache-dir DIR]` | —（无别名） | 进入自举容器的交互式 bash shell |
| `invoke quant.build [--pip-mirror M] [--base-image I] [--no-cache]` | —（opt-in，需 `[compose]` extra） | 构建 ONNX 量化叠加镜像（见 [10-quant-overlay.md](10-quant-overlay.md)） |
| `invoke quant.up [--gpu] [--skip-build]` | — | podman-compose 启动量化栈 |
| `invoke quant.down [--volumes]` / `quant.ps` / `quant.logs` / `quant.smoke` | — | 栈生命周期与 3 个纯 ONNX 冒烟 |

## 参数契约

> **布尔项统一为三态**：`--x` 显式开启 / `--no-x` 显式关闭（可覆盖 `.env` 开启项）/ 两者都不给才回落 `.env` → 默认。
> `run` 任务已关闭 invoke 自动短选项（`auto_shortflags=False`），**只承诺长选项契约**——此前自动短名顺序敏感且误导
> （实测 `-h` 被 `--ssh-public-key` 抢走致使 `invoke run -h` 报错、`--host-network` 退化到短名 `-`）。

配置合并优先级：`命令行参数 > .env 环境变量 > ContainerConfig 默认值`。

## SSH known_hosts 自动维护

每次执行 `invoke run` 时，启动流程会自动扫描并清理 `~/.ssh/known_hosts` 中与当前 `SSH_PORT`（默认 2222）匹配的 `[localhost]:PORT` / `[127.0.0.1]:PORT` 过期条目，然后尝试用 `ssh-keyscan` 写入最新 key。JPMan 容器重建后 host key 必然变更，此逻辑消除了手动干预需求。