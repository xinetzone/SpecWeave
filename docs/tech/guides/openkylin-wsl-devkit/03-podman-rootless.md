---
type: "Tutorial"
title: "okw rootless Podman 指南"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#Podman-入门"
---

# okw rootless Podman 指南

`okw podman` 针对指定 WSL 发行版提供只读预检、显式确认安装和 rootless 验收。该流程不会切换 WSL 默认发行版、修改软件源或编辑 `wsl.conf`。

## 三步流程

```text
okw podman preflight <name>
okw podman install <name> --yes
okw podman verify <name>
```

1. `preflight` 只读检查发行版身份、WSL 版本、APT 能力、软件包候选及 `subuid`/`subgid` 映射；不执行 `apt update`、不写文件。
2. `install` 必须显式提供 `--yes`。省略时仅打印副作用清单，以退出码 2 中止，不做写入。
3. `verify` 以发行版默认非 root 用户检查映射、`unshare` 和 `podman info --rootless`。默认不创建或启动容器。

## 安装会执行什么

提供 `--yes` 后，工具依次执行以下操作：

1. 以 root 身份运行 `apt update` 并复查软件包候选。
2. 安装 `podman`、`uidmap`、`slirp4netns`、`fuse-overlayfs` 四个直接包及其依赖。
3. 仅当默认用户缺少映射且区间无冲突时，向 `/etc/subuid` 与 `/etc/subgid` 各追加 `默认用户:100000:65536`。两文件共同校验后再写入，失败时自动回滚。
4. 以默认用户身份执行 rootless 验收子集。

安装不添加第三方软件源、不修改 `wsl.conf`，也不宣称整个安装过程具备事务回滚；中断后可重跑，APT 与映射写入按幂等设计。

## 为什么选择 rootless

日常开发优先使用默认用户的 rootless Podman，而不是 `sudo podman`。rootless 容器通过 `/etc/subuid` 与 `/etc/subgid` 将容器 UID/GID 映射到从属 ID 区间 `[100000, 165536)`；这与 rootful 容器直接以主机 root 上下文运行不同。rootless 是权限隔离措施，不代表容器风险消失。

## 本地镜像冒烟

冒烟是可选项，且验收全程不联网：

```text
okw podman verify <name> --smoke-image <本地镜像>
```

运行前会检查镜像是否已在目标发行版本地存在；运行容器时固定使用 `--pull=never`，禁止隐式拉取。请先在发行版内自行运行 `podman pull <镜像>` 或 `podman load -i <镜像包>`。镜像缺失时验收会直接 FAIL 并给出提示。

## 退出码

| 退出码 | 含义 |
|---|---|
| `0` | 检查或安装全部通过 |
| `1` | 存在 FAIL；报告包含中文修复指引 |
| `2` | 用法错误、`preflight`/`verify` 仅有 UNKNOWN，或 `install` 未提供 `--yes` |

## 常见问题

- **rootless 和 `sudo podman` 怎么选？** 日常开发使用默认用户的 rootless 模式。`okw podman verify` 在 root 身份下不会报告 rootless PASS。
- **APT 找不到候选包怎么办？** 检查当前发行版软件源是否提供该包；不要添加第三方源。若需启用官方 backports 或 proposed 组件，请手动编辑发行版的 `sources.list`。
- **APT 网络错误怎么办？** 检查发行版网络与 DNS；网络恢复后可在发行版内重跑 `sudo apt update`，再重试安装。
- **APT 哈希校验失败怎么办？** 可切换到官方镜像，或清理 `/var/lib/apt/lists` 后重新执行 `sudo apt update`。
- **冒烟提示镜像不存在怎么办？** 先在发行版内拉取或加载镜像，再确认 `podman image exists <镜像>` 返回 0，最后重跑 `verify --smoke-image`。

发行版名称可通过 `okw list` 或 `wsl -l -v` 查询。
