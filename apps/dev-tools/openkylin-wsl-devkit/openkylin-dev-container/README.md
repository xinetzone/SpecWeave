# openkylin-dev-container

基于本地导入的 openKylin 3.0 WSL rootfs（`localhost/openkylin:3.0`）的全功能开发容器：**SSH（22）+ JupyterLab（8888）+ 容器内 rootless Podman（devuser）**，由 supervisord 管理服务栈，tini 作为 init。资产归属于 `openkylin-wsl-devkit`（okw）应用，与 `okw podman` 的 WSL 发行版内 rootless Podman 三步流程互补，形成「WSL 发行版 → 容器开发环境」完整链路。

## 镜像构成

| 组件 | 说明 |
|---|---|
| 基础镜像 | `localhost/openkylin:3.0`（本地导入 WSL 3.0 rootfs；官方 registry `latest` 实为 2.0 SP1 LTS，非 3.0） |
| SSH | openssh-server，密码由启动时 `DEV_PASSWORD` 或随机一次性密码提供 |
| Jupyter | jupyterlab + notebook（pip 安装，openKylin 源不提供），devuser 运行 |
| Podman | 容器内 rootless（fuse-overlayfs + crun + cgroupfs），subuid/subgid `devuser:100000:65536`（起点须高于用户自身 UID） |
| 服务管理 | supervisord（sshd + jupyter），tini 为 PID 1 入口 |
| 系统 | zh_CN.UTF-8 locale + Asia/Shanghai 时区，devuser UID 1000 |

## 快速开始（Windows 原生 Podman Machine）

```powershell
# 1. 基础镜像：本地已导入的 openKylin 3.0 WSL rootfs（localhost/openkylin:3.0），
#    无需拉取。导入方法见 docs/retrospective/patterns/code-patterns/wsl-rootfs-oci-image-export.md
#    （podman machine ssh -- podman import <wsl文件> openkylin:3.0）

# 2. 构建（自动探测本机 Podman Machine；默认基底 localhost/openkylin:3.0）
./scripts/build.ps1            # -BaseImage 可覆盖基底（registry 镜像时可用 -PullBase）

# 3. 冒烟（仅本地镜像，--pull=never；含 rootless 三必需参数）
./scripts/smoke.ps1
```

openKylin WSL 发行版内（或任意 Linux）使用同构脚本：

```bash
./scripts/build.sh   # 基底默认 localhost/openkylin:3.0（本地导入，无需 PULL_BASE）
./scripts/smoke.sh
```

## 运行容器

```bash
# 运行需携带容器契约参数（--device /dev/fuse 等，见 apps/containers G3；严禁 --privileged）
podman run -d --name openkylin-dev \
    --device /dev/fuse --security-opt label=disable --cgroupns=host \
    -p 2222:22 -p 8888:8888 \
    -e DEV_PASSWORD=yourpass \
    -v D:/spaces/SpecWeave:/workspace \
    localhost/openkylin-dev:3.0

ssh devuser@localhost -p 2222     # 密码：DEV_PASSWORD 或容器启动日志中的随机密码
# 浏览器打开 http://localhost:8888 （Jupyter，token 已按本地开发默认关闭）
```

> **安全边界**：Jupyter 默认无 token、SSH 密码认证——仅限本地开发环境，禁止将 22/8888 端口暴露到公网；生产使用请通过 `DEV_PASSWORD` 设置强密码并接入密钥认证。

## 与 okw 的关系

- 本镜像工程是 `openkylin-wsl-devkit` 的资产目录（非独立应用），构建脚本不依赖 okw Python 包（零第三方运行时依赖，沿用 offline-delivery 的 bash+pwsh 模式）。
- `okw podman preflight/install/verify` 负责 WSL **发行版内**的 rootless Podman；本镜像负责**容器内**的开发环境与 rootless Podman。
- 冒烟语义与 okw 一致：仅使用本地已存在镜像（`--pull=never`），不触发隐式拉取。

## 目录结构

```
openkylin-dev-container/
├── Containerfile          # 单阶段构建，5 层分层（系统/locale→jupyter→devuser→配置→元数据）
├── entrypoint.sh          # 启动初始化：密码、SSH host key、目录；exec supervisord
├── healthcheck.sh         # HEALTHCHECK 探针（sshd + jupyter）
├── conf/
│   ├── sshd_config
│   ├── supervisord.conf
│   ├── jupyter_notebook_config.py
│   ├── storage.conf       # 容器内 rootless Podman（fuse-overlayfs）
│   └── containers.conf    # cgroupfs + crun
├── scripts/
│   ├── build.ps1 / build.sh   # 双环境构建（Windows Podman Machine / WSL）
│   └── smoke.ps1 / smoke.sh   # 双环境冒烟（静态探针 + 全量启动 + 服务检查）
└── README.md
```

## 已知边界

- 仅 amd64 真实验证；`--platform` 透传保留但不承诺多架构验收。
- 容器内 live rootless Podman（devuser 建嵌套用户命名空间）依赖外层宿主的 rootful 能力：在 rootless 外层宿主（如 Windows Podman Machine）上，`newuidmap` 写 `uid_map` 会遇 `Operation not permitted`（嵌套 userns 受限）——冒烟按 spec 假设降级为「镜像内配置与二进制就绪检查」（P8）+ 记录 ENV-LIMIT；在 rootful 外层宿主（如 openKylin WSL 发行版内 podman）上可完整验证 live rootless。
- 不含 conda/OMLMD/OLOT/Toolbx 等 jupyter-podman-rootless 特色部件（openKylin 场景无对应资产）。
- 不修改 openKylin 软件源、不添加第三方 apt 源。
- 完整使用指南见文档中心 `docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`。
