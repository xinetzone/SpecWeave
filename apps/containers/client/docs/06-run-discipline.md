---
id: "jupyter-podman-client-run-discipline"
title: "内置纪律：rootless 三必需参数"
source: "README.md#7-内置纪律rootless-三必需参数"
---
# 内置纪律（rootless 三必需参数）

所有启动路径（SDK 与 CLI）均自动携带以下参数，调用方无需关心：

- `--device /dev/fuse`
- `--security-opt label=disable`
- `--cgroupns=host`

对应 `jpman-podman-ops` Skill 中 rootless 容器三必需纪律。
默认不使用 `--privileged`。

> **运行身份（user=root 覆盖本镜像的 USER=devuser）**：`client` 镜像是构建端叠加的消费端镜像，
> `Containerfile` 固化 `USER=devuser`（non-root）。但镜像的 `entrypoint.sh` 需以 **root** 执行初始化
> （`setup_passwords` 的 `chpasswd` 写 `/etc/shadow`、写 `/root/.jupyter`、启动 supervisord），
> 若以 devuser 运行会触发 PAM `chpasswd` 失败，容器在 `set -euo pipefail` 下立即退出（`Exited (1)`）。
> 因此 `ContainerConfig` 内置 `user="root"`，`invoke run` 以 root 启动 entrypoint，
> **supervisord 内部再降权给 devuser 跑 jupyter/sshd**——对用户完全透明，无需感知。