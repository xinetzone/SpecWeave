---
id: "host-channel-pass-through"
title: "宿主通道透传模式"
type: "code-pattern"
date: "2026-09-09"
maturity: "L1-single-case-pending"
source: "jupyter-podman-rootless 嵌套 userns 修复 (2026-09-09)"
related_patterns:
  - "fixuid-runtime-uid-mapping"
  - "wsl-podman-build-bridge"
  - "docker-podman-cross-platform-container"
  - "oci-image-wsl-rootfs-bridge"
tags: ["podman", "container", "userns", "rootless", "socket", "pass-through", "wsl", "devtool"]
validation_count: 1
reuse_count: 0
---

# 宿主通道透传模式

## 触发场景

- 容器/虚拟化环境中，**内层运行时无法自建管理 daemon**（如嵌套 userns 触发 `newuidmap ... Operation not permitted`），但**宿主已有可用的 rootless daemon**
- 需要让容器内的客户端工具（CLI / SDK / compose）复用**宿主已有的 daemon 通道**，而不是在容器内自建一份
- 运行时的守护进程（socket）受宿主 UID 保护，但宿主与容器间存在 userns 映射，直接 bind-mount 的 socket 路径在容器内属主/权限不一致
- 内层运行时的客户端身份（UID）与宿主 daemon socket 属主**不一致**，需要符号链接适配到客户端可控目录

## 不适用场景（边界与反目标）

以下场景不应强行套用本模式，否则会引入不必要的复杂度或直接失败：

1. **需要独立资源隔离的内层运行时**：若每个容器必须拥有完全独立、相互隔离的 daemon 与镜像/卷存储，则透传宿主 daemon 会引入跨容器的共享耦合，破坏隔离性，应改用容器内自建
2. **宿主与客户端 UID 映射无法建立可控目录的场景**：若客户端进程对任何挂载进容器的目录都无写权限、且无法在客户端可控目录建立符号链接，则透传通道无法落地（本模式依赖"客户端可控目录 + 符号链接适配 UID"）
3. **需要 root 特权或安全隔离跨租户的场景**：透传宿主 daemon 意味着客户端能访问宿主全部镜像/卷/容器，在跨租户或强安全边界场景下是越权风险，应禁止透传
4. **宿主机未运行 rootless daemon 或不存在可挂载 socket 的场景**：没有宿主通道就没有可透传的对象，属于前置条件缺失
5. **单进程短生命周期 CLI 场景**：`podman exec` 这类每次创建新进程、不继承守护进程树环境变量的调用，透传通道需显式传环境，否则该通道对这类调用无效（见反模式4）

## 失败案例

### 案例：嵌套 userns 下容器内自建 Podman daemon 失败

**场景**：WSL（宿主 UID=1000）三层 userns 嵌套，在容器内以 root 自建 rootless podman daemon（Model A）。

**操作**：
```bash
podman system service --time=0 unix:///run/user/0/podman/podman.sock &
```
（在容器内 root 下自建 daemon）

**结果**：容器内自建 daemon 触发：
```
running `/usr/bin/newuidmap 313 0 1000 1 1 100000 65536`: newuidmap: write to uid_map failed: Operation not permitted
```
WSL 三层 userns 嵌套导致 `newuidmap` 无权完成 uid_map 写，容器内自建 daemon（Model A）方案直接失败。

**教训**：嵌套 userns 环境下，"容器内自建管理 daemon"这一默认心智模型是错的。宿主已有一个**现成且工作正常的 rootless daemon**，应优先选择**透传宿主通道**而非自建。

## 核心做法

### 1. 将宿主 daemon socket bind-mount 进容器

在容器编排层把宿主 rootless daemon socket 通过 volume 挂载进容器（路径与宿主一致，简化映射）：

```yaml
# compose.yaml
volumes:
  - ${HOST_PODMAN_SOCK:-/run/user/1000/podman/podman.sock}:/run/user/1000/podman/podman.sock
environment:
  HOST_PODMAN_SOCK: ${HOST_PODMAN_SOCK:-/run/user/1000/podman/podman.sock}
```

### 2. 通过环境变量声明"宿主通道契约"

不再用客户端进程的运行时目录作为唯一事实来源，而是**显式声明**宿主 daemon socket 已挂载到容器内哪个路径，由入口脚本消费：

```python
# client.py
"HOST_PODMAN_SOCK": podman_sock_path(),
```

```bash
# manage.py CLI
cmd_parts.extend(["-e", f"HOST_PODMAN_SOCK={podman_sock_path()}"])
```

`podman_sock_path()` 由可配置的运行时 UID（默认 `PODMAN_RUNTIME_UID=1000`）导出，避免硬编码：

```python
def _podman_runtime_uid():
    return os.environ.get("PODMAN_RUNTIME_UID", "1000")

def podman_sock_path():
    return f"/run/user/{_podman_runtime_uid()}/podman/podman.sock"
```

### 3. 在客户端可控目录建立符号链接 + 设置 `CONTAINER_HOST`

入口脚本（entrypoint）在**客户端可控目录**（`XDG_RUNTIME_DIR=/run/user/$(id -u <client>)`）内建立指向挂载 socket 的符号链接，并显式设置 `CONTAINER_HOST`：

```bash
# entrypoint.sh
export XDG_RUNTIME_DIR="$(eval echo ~${NON_ROOT_USER})/run"  # 客户端可控目录
local host_sock="${HOST_PODMAN_SOCK:-}"
if [ -n "${host_sock}" ] && [ -S "${host_sock}" ]; then
    local run_sock_dir="${podman_run_dir}/podman"
    mkdir -p "${run_sock_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${run_sock_dir}" 2>/dev/null || true
    chmod 700 "${run_sock_dir}" 2>/dev/null || true
    ln -sf "${host_sock}" "${run_sock_dir}/podman.sock"
    export CONTAINER_HOST="unix://${run_sock_dir}/podman.sock"
fi
```

> 关键：`CONTAINER_HOST` 指向的是**客户端可控目录下的符号链接**，而不是直接指向挂载路径——因为 ul/userns 映射后，挂载路径的属主（宿主 1000）与客户端 UID（如容器内 1001）不一致，客户端可能无权访问挂载路径；符号链接把通道落到客户端可读写的目录。

### 4. 客户端以「动态 UID」适配而不是硬编码宿主 UID

客户端 UID（镜像内 devuser）与宿主 socket 属主 UID 往往不一致（本例宿主=1000、容器 devuser 实际=1001）。关键洞察是：**容器 root 通常映射到宿主 1000（socket 属主），而非 root 客户端映射到宿主 1000**。因此：

- 不硬编码客户端目录为 `/run/user/1000`，而是用 `$(id -u <client>)` 动态推导客户端可控目录
- 符号链接在客户端可控目录建立，客户端天然可读写该目录下的 socket 通道

## 反模式（不要这么做）

### ❌ 反模式1：容器内自建 daemon（嵌套 userns 下）

```bash
# 容器内自建 daemon
podman system service --time=0 unix:///run/user/0/podman/podman.sock &
```
嵌套 userns 下 `newuidmap` 无权限，自建 daemon 直接失败。应改为透传宿主已有 daemon。

### ❌ 反模式2：环境变量硬编码宿主 UID、不落客户端可控目录

```bash
export XDG_RUNTIME_DIR=/run/user/1000
```
容器内客户端实际 UID 是 1001（不是 1000），把运行时目录硬编码为 1000，客户端对 `/run/user/1000` 无写权限，无法建立 socket 链接与 `CONTAINER_HOST`，通道失效。应改用 `$(id -u <client>)` 动态推导。

### ❌ 反模式3：客户端进程直接用挂载路径作为 `CONTAINER_HOST`

```bash
export CONTAINER_HOST=unix:///run/user/1000/podman/podman.sock
```
挂载路径在容器内属主是宿主映射的 UID（1000），与客户端实际 UID（1001）不一致；若客户端不能写该目录，会因权限报错。应建立客户端可控目录下的符号链接后指向它。

### ❌ 反模式4：`podman exec` 场景未显式传环境，误判为通道缺陷

```bash
podman exec -u devuser <ctr> podman images
# 报 newuidmap Operation not permitted
```
`podman exec` 创建的是**新进程**，不继承 entrypoint 中 export 的 `CONTAINER_HOST`/`XDG_RUNTIME_DIR`，podman 误走本地 rootless 触发 newuidmap。这是 `podman exec` 的预期行为，不是通道缺陷。显式传环境即可：

```bash
podman exec -e CONTAINER_HOST=unix:///run/user/1001/podman/podman.sock \
  -e XDG_RUNTIME_DIR=/run/user/1001 -u devuser <ctr> podman images
```
正常守护进程树（supervisord：sshd/Jupyter）会正确继承 entrypoint 环境，无需显式传。

## 检验标准

做完之后怎么知道做对了？

1. **三层后端全部连通宿主 daemon**：CLI 的 `Server` 版本与宿主一致；SDK 能列出宿主镜像；compose 能运行
   ```bash
   podman version --format "Client={{.Client.Version}} Server={{.Server.Version}}"
   # Client=5.7.0 Server=5.7.1  （Server 与宿主一致 → 走宿主 daemon）
   ```
   ```python
   PodmanClient.from_env().images.list()  # 返回宿主镜像列表
   ```
2. **无嵌套 userns 报错**：连接过程不再出现 `newuidmap ... Operation not permitted`
3. **客户端可控符号链接生效**：`readlink <client_run_dir>/podman/podman.sock` 指向挂载 socket，客户端进程对其可读写
4. **契约变量贯穿全链路**：`HOST_PODMAN_SOCK` 从 compose → 构建端 → 入口脚本一致传递，未出现硬编码 UID

## 迁移示例

| 场景 | 宿主通道 | 客户端 | 适配点 |
|------|---------|--------|--------|
| Podman rootless + WSL | `/run/user/1000/podman/podman.sock` | 容器 devuser(1001) | 符号链接到客户端可控目录 |
| Docker daemon 透传 | `/var/run/docker.sock` (root) | 容器 root `-v /var/run` | root 客户端无需 UID 适配，直接挂载 |
| Podman socket activation | 任意 rootless sock | 容器内 SDK | 上面流程 |

### 跨领域迁移
- **GPU 设备透传**：宿主 GPU `/dev/nvidia*` 通过 `--device` 透传进容器，容器内 driver 复用宿主设备节点——同样是"复用宿主现成通道，而非在容器内自建"的抽象
- **宿主机网络命名空间透传**：把宿主 netns 共享给容器（`--network=host`），容器内服务直接监听宿主端口而非做容器端口映射
- **Docker socket proxy 透传**：把 docker.sock 挂进容器执行 CI，容器内 docker CLI 走宿主 daemon——同一心智模型

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [fixuid-runtime-uid-mapping.md](fixuid-runtime-uid-mapping.md) | 互补 | 解决容器内客户端 UID 与宿主映射不一致问题，本模式依赖其动态 UID 适配 |
| [wsl-podman-build-bridge.md](wsl-podman-build-bridge.md) | 互补 | WSL 下 podman 构建桥接，与跨层 socket 访问协同 |
| [docker-podman-cross-platform-container.md](docker-podman-cross-platform-container.md) | 互补 | CLI 层跨平台统一，本模式是 daemon 通道层统一 |
| [oci-image-wsl-rootfs-bridge.md](oci-image-wsl-rootfs-bridge.md) | 互补 | OCI 镜像与 WSL rootfs 桥接，同类跨层通道抽象 |

## 待验证场景

本模式目前为 **L1-single-case-pending**（单一案例：jupyter-podman-rootless 嵌套 userns 修复），建议在以下场景验证：

1. **Docker socket 直接透传**（root 客户端，无 userns 映射）验证根容器场景
2. **Podman 容器套容器**（非 WSL）验证不同宿主平台
3. **跨租户安全边界**：透传宿主 daemon 带来的越权风险如何用最小权限（如 socket 代理、只读访问）缓解
