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

> **构建参数单一事实源（C15，2026-09-18）**：四个工作负载栈的构建 build-arg 只认四个
> **无前缀** `.env` 键——`PIP_MIRROR` / `CONDA_MIRROR` / `BASE_IMAGE` / `TORCH_FLAVOR`，它们同时就是
> `overlays/*/compose.yaml` 里 `${KEY:-默认}` 的插值键。`invoke x.build`、`invoke x.up`
> 的内联构建、compose 内部 build 段三处必须拿到同一组值：任何一处 build-arg 不同，
> 都会让构建层缓存整体失效（表现为"改了镜像源后每次 up 都全量白重建"）。
>
> 因此**换镜像源/节点请写 `.env`**；`--pip-mirror` / `--base-image` / `--conda-mirror` /
> `--torch` 等 CLI 旗标只覆盖**单次 `build` 调用**，`up` 内联构建与 compose 段看不到旗标，混用
> 必然不一致。推荐两步路径：写好 `.env` → `invoke x.build` → `invoke x.up --skip-build`。
> 权限顺序为 `CLI 旗标 > shell export > .env > 默认值`。
>
> `TORCH_FLAVOR` 取值受**白名单**约束（空 / `cpu` / `cu130`），非法值在解析期 Exit 1——
> 该值直接拼进 `download.pytorch.org/whl/<flavor>` 索引 URL，构建期网络请求目标不得由
> 用户输入任意拼接（C18）。仅 `native.build` 暴露 `--torch`。

> **构建执行者唯一（C16，2026-09-18）**：`invoke x.up` 恒以
> `podman-compose up -d --no-build` 起容器——**镜像存在性只由内核 `build_image()` 负责**。
> 默认路径先内联构建再起容器（全程恰好一次构建）；`--skip-build` 与 `--offline` 不做
> 任何构建，因此先做本地镜像存在性预检，缺失即 Exit 1 并给出可执行出口（不再由
> compose 的 build 段兜底）。`overlays/*/compose.yaml` 的 `build:` 段自此仅服务
> **裸 `podman-compose`** 路径。

> **`up` 输出收敛（C17，2026-09-18）**：`invoke x.up` 起容器走
> `overlay_core.run_compose_up()`——先捕获 podman-compose 的 stdout/stderr，再按**白名单**
> 过滤 podman 原生回显，最后打印编排层中文提示。被过滤的只有三类良性行：① 整行恰为
> 64 位十六进制对象 ID；② 整行与容器名 / `pod_<project>` / `<project>_default` 全等；
> ③ rootless netns 的 `failed to move the rootless netns pasta process to the systemd
> user.slice: dbus: couldn't determine address of session bus`（宿主无 systemd 用户会话总线
> 时的良性提示，容器照常创建）。命中时打印一行 `ℹ 已过滤 N 行 podman 原生回显噪声`。
>
> **失败路径零过滤**：非零退出码下 stdout/stderr **全量原样回放**后再 Exit（退出码透传），
> 不会因过滤吞掉真实错误。仅 `up` 走该路径；`down` / `ps` / `logs` / `exec` 与
> `build` / `build-tvm` / `wheel` 等长任务保持逐字实时透传。

## SSH known_hosts 自动维护

每次执行 `invoke run` 时，启动流程会自动扫描并清理 `~/.ssh/known_hosts` 中与当前 `SSH_PORT`（默认 2222）匹配的 `[localhost]:PORT` / `[127.0.0.1]:PORT` 过期条目，然后尝试用 `ssh-keyscan` 写入最新 key。JPMan 容器重建后 host key 必然变更，此逻辑消除了手动干预需求。