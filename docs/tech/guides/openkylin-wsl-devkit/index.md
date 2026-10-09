---
type: "Tutorial"
id: "openkylin-wsl-devkit"
title: "openKylin WSL 开发工具包（okw）"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#定位"
---

# openKylin WSL 开发工具包（okw）

`okw` 是面向 Windows + WSL2 的 openKylin 开发工具包，提供 WSL 发行版管理、环境验收、deb/dput 脚手架、知识库快速参考，以及 rootless Podman 预检、安装与验收。工具以 WSL 为切入点，将已验证的操作经验封装为 CLI。

## 按任务阅读

| 我想…… | 阅读 |
|---|---|
| 安装工具并完成第一次环境检查 | [安装与快速开始](01-getting-started.md) |
| 查找 WSL、脚手架和知识参考命令 | [命令参考](02-command-reference.md) |
| 配置并验收 rootless Podman | [rootless Podman 指南](03-podman-rootless.md) |
| 了解设计、安全边界、开发和测试 | [开发与边界](04-development-and-boundaries.md) |
| 构建并使用 openKylin 开发容器镜像 | [openKylin 开发容器镜像指南](05-openkylin-dev-container.md) |

## 能力概览

| 能力 | 命令 |
|---|---|
| WSL 发行版生命周期 | `okw list`、`status`、`import`、`export`、`unregister`、`exec` |
| openKylin 环境验收 | `okw verify <name>` |
| deb 打包与 OKBS 上传配置 | `okw scaffold deb`、`okw scaffold dput` |
| 知识库快速参考 | `okw ref <主题>` |
| rootless Podman 工作流 | `okw podman preflight`、`install`、`verify` |

本工具不替代系统级 WSL 安装、不自动下载发行版镜像、不调用 OKBS/factory API，也不修改 openKylin 知识库。Desktop WSL 的运行时结论仍以对应实测资料为准；本工具不固化未验证建议。

## 相关知识

- [openKylin 官方文档平台学习教程](../../../knowledge/tech/openkylin-docs-wiki/index.md)：平台结构、版本生命周期、安装路径与开发者基础设施。
- [WSL 安装与稀疏 VHD 实操指南](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md)：openKylin WSL 安装实测与排障。
- [双 WSL 镜像对照与选型参考](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md)：最小镜像与 Desktop WSL 的实测差异。

```{toctree}
:maxdepth: 2

01-getting-started
02-command-reference
03-podman-rootless
04-development-and-boundaries
05-openkylin-dev-container
```
