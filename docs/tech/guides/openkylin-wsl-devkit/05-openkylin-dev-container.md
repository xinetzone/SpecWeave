---
type: "Tutorial"
title: "openKylin 开发容器镜像指南"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#openKylin-开发容器镜像"
---

# openKylin 开发容器镜像指南

`openkylin-dev-container` 提供基于 openKylin 3.0 的全功能开发容器镜像：**SSH（22）+ JupyterLab（8888）+ 容器内 rootless Podman（devuser）**，由 supervisord 管理服务栈、tini 作 init。它服务于「在容器内开发、测试 openKylin 软件包与服务」的场景，与 okw 的 WSL 发行版管理形成「**WSL 发行版 → 容器开发环境**」完整链路。

## 用途与定位

- 面向 openKylin 平台开发者：在 openKylin 基底容器内做 SSH/Jupyter 开发、运行 rootless 容器实验。
- 资产归属 `apps/dev-tools/openkylin-wsl-devkit/openkylin-dev-container/`（非独立应用），构建脚本零第三方运行时依赖（bash + pwsh 双环境）。
- 与 `okw podman`（发行版内 rootless Podman 三步流程，见 [rootless Podman 指南](03-podman-rootless.md)）互补：okw 管理宿主侧，本镜像提供容器侧开发环境。

## 镜像构成

| 组件 | 说明 |
|---|---|
| 基础镜像 | `localhost/openkylin:3.0`（本地导入的 WSL 3.0 rootfs；官方 registry `latest` 实测为 2.0 SP1 LTS，非 3.0） |
| SSH | openssh-server，密码由启动时 `DEV_PASSWORD` 或随机一次性密码提供 |
| Jupyter | jupyterlab + notebook（pip 安装，PEP 668 场景使用 `--break-system-packages`），devuser 运行 |
| Podman | 容器内 rootless（fuse-overlayfs + crun + cgroupfs），subuid/subgid `devuser:100000:65536` |
| 服务管理 | supervisord（sshd + jupyter）+ healthcheck，tini 为 PID 1 |
| 系统 | zh_CN.UTF-8 locale + Asia/Shanghai 时区，devuser UID 1000 |

## 构建（双环境）

基底镜像为**本地导入**（无 registry）：`podman machine ssh -- podman import <openKylin WSL 导出文件> openkylin:3.0`，转换方法见模式文档 [wsl-rootfs-oci-image-export](../../../retrospective/patterns/code-patterns/wsl-rootfs-oci-image-export.md)。

**Windows Podman Machine**（自动探测；建议 pwsh 7）：

```powershell
./scripts/build.ps1            # -Tag 覆盖；-BaseImage 覆盖基底
```

**openKylin WSL / 任意 Linux**：

```bash
./scripts/build.sh
```

构建要点：`--format docker`（OCI 格式会静默丢弃 `SHELL`/`HEALTHCHECK` 指令，docker 格式二者生效）；构建日志输出至 `.trae/specs/infra-env/openkylin-dev-container/evidence/`。

## 运行

容器启动必须携带容器契约参数（apps/containers G3 组级契约，**严禁 `--privileged`**）：

```bash
podman run -d --name openkylin-dev \
    --device /dev/fuse --security-opt label=disable --cgroupns=host \
    -p 2222:22 -p 8888:8888 \
    -e DEV_PASSWORD=yourpass \
    -v D:/spaces/SpecWeave:/workspace \
    localhost/openkylin-dev:3.0

ssh devuser@localhost -p 2222     # 密码：DEV_PASSWORD 或启动日志中的随机密码
# 浏览器打开 http://localhost:8888（Jupyter，本地开发默认关闭 token）
```

> **安全边界**：Jupyter 默认无 token、SSH 密码认证——仅限本地开发环境，禁止将 22/8888 暴露到公网；生产使用请设置强密码并接入密钥认证。

## 验证（冒烟）

冒烟仅使用本地镜像（`--pull=never`），不触发任何 registry 拉取：

```powershell
./scripts/smoke.ps1    # Windows Podman Machine
./scripts/smoke.sh     # Linux / openKylin WSL
```

探针清单：`sshd -t`、jupyter 版本、supervisord 版本、locale `zh_CN.UTF-8`、时区 Asia/Shanghai、devuser uid=1000、subuid 映射、podman 二进制就绪；随后全量启动容器并等待 HEALTHCHECK healthy，检查 sshd/jupyter 进程与 22/8888 端口。

## 已知边界

- **live rootless Podman 依赖外层宿主 rootful 能力**：devuser 在容器内建立嵌套用户命名空间，rootless 外层宿主（如 Windows Podman Machine）会遇 `newuidmap: write to uid_map ... Operation not permitted`；此时冒烟 P8 降级为「镜像内配置与二进制就绪检查」并记录 ENV-LIMIT（符合 spec 假设）。在 rootful 外层宿主（如 openKylin WSL 发行版内 podman）上可完整验证 live rootless。
- 仅 amd64 真实验证；`--platform` 透传保留但不承诺多架构验收。
- 不含 conda/OMLMD/OLOT/Toolbx 等 jupyter-podman-rootless 特色部件（openKylin 场景无对应资产）。
- 不修改 openKylin 软件源、不添加第三方 apt 源；不硬编码密码/密钥（SSH host key 启动时生成）。

## 故障排查（构建期常见失败）

| 症状 | 根因 | 处置 |
|---|---|---|
| `pip` 报 externally-managed-environment | openKylin 3.0 的 PEP 668 | Containerfile 已用 `--break-system-packages` |
| `useradd: UID 1000 并不唯一` | WSL 桌面版基底自带默认用户 `openkylin`（uid 1000） | 构建 Layer 3 `userdel -r openkylin` |
| `specified mapping 1000:65536 includes the user UID` | subuid 起点含自身 UID | 使用 `100000:65536` 起点 |
| `HEALTHCHECK is not supported for OCI image format` | 基底为 OCI 格式 | 构建加 `--format docker` |
| locale 探针失败但 `locale -a` 含 `zh_CN.utf8` | Debian 兼容模式小写/无连字符拼写 | 探针使用大小写与连字符兼容匹配 |

## 相关知识

- [rootless Podman 指南](03-podman-rootless.md)：okw 在 WSL 发行版内的 rootless Podman 三步流程（宿主侧）。
- [wsl-rootfs-oci-image-export](../../../retrospective/patterns/code-patterns/wsl-rootfs-oci-image-export.md)：WSL 导出文件转 OCI 镜像的模式文档。
- [openKylin 版本生命周期](../../../knowledge/tech/openkylin-docs-wiki/concepts/02-release-lifecycle.md)：2.0 LTS / 3.0 创新版与容器 tag 的关系。
