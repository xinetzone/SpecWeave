---
type: "Tutorial"
title: "okw 安装与快速开始"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#安装"
---

# okw 安装与快速开始

## 环境要求

- Windows + WSL2。
- Python 3.10 或更高版本。
- `openkylin-wsl-devkit` 没有第三方运行时依赖。

## 安装

在仓库根目录执行开发安装：

```powershell
cd apps\dev-tools\openkylin-wsl-devkit
python -m pip install -e .
```

也可以在应用目录构建 wheel：

```powershell
python -m build
```

安装后可通过 `okw --help` 查看命令入口。

## 第一次使用

先查看本机 WSL 发行版及默认发行版，再检查目标发行版：

```text
okw list
okw status <name>
okw verify <name>
```

`okw verify` 执行 openKylin 环境五步验收，覆盖 `os-release`、用户、UID、systemd 和包数。验收前可用 `okw list` 查看发行版名称与默认星标，也可在 PowerShell 中运行 `wsl -l -v`。

如需导入 openKylin 镜像，指定名称、安装目录和 WSL 版本：

```powershell
okw import <镜像.wsl> --name openKylin-3.0 --location D:\wsl\ok30 --version 2
```

预置账号 `openkylin/openkylin` 是弱口令；首次进入发行版后请立即运行 `passwd` 修改。

## 下一步

- [命令参考](02-command-reference.md)：发行版生命周期、脚手架和知识参考命令。
- [rootless Podman 指南](03-podman-rootless.md)：预检、安装与 rootless 验收。
- [开发与边界](04-development-and-boundaries.md)：安全约束、测试方式和已知限制。
