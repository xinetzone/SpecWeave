# openkylin-wsl-devkit（okw）

openKylin WSL 开发工具包：通过 `okw` 管理 WSL 发行版、验收 openKylin 环境、生成 deb/dput 脚手架，并查询知识库快速参考。

## 文档

完整使用手册已迁入 SpecWeave 文档中心：

- [openKylin WSL 开发工具包指南](../../../docs/tech/guides/openkylin-wsl-devkit/index.md)
- [安装与快速开始](../../../docs/tech/guides/openkylin-wsl-devkit/01-getting-started.md)
- [WSL 与开发命令参考](../../../docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md)
- [rootless Podman 指南](../../../docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md)
- [开发、测试与边界](../../../docs/tech/guides/openkylin-wsl-devkit/04-development-and-boundaries.md)
- [openKylin 开发容器镜像指南](../../../docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md)
- [xuan-compose（xc）引导指南](../../../docs/tech/guides/openkylin-wsl-devkit/06-xuan-compose.md)
- [AI 栈：本地 OCR 指南](../../../docs/tech/guides/openkylin-wsl-devkit/07-ai-stack.md)
- [桌面：UKUI（xrdp/WSL）指南](../../../docs/tech/guides/openkylin-wsl-devkit/08-desktop.md)

## openKylin 开发容器镜像

`openkylin-dev-container` 应用目录提供基于本地导入的 openKylin 3.0 WSL rootfs（`localhost/openkylin:3.0`）的全功能开发容器镜像——**SSH（22）+ JupyterLab（8888）+ 容器内 rootless Podman（devuser）**，由 supervisord 管理、tini 作 init。与 `okw podman` 的「WSL 发行版内」rootless Podman 互补，构成「WSL 发行版 → 容器开发环境」完整链路。

```powershell
# 构建（Windows Podman Machine，自动探测；默认基底 localhost/openkylin:3.0）
./openkylin-dev-container/scripts/build.ps1

# 冒烟（仅本地镜像 --pull=never；G3 三必需参数）
./openkylin-dev-container/scripts/smoke.ps1
```

**okw image 一键构建/验收**（在 openKylin WSL 发行版内以 root 身份执行，2026-10-09 实测通过）：

```text
okw image build openKylin-3.0-desktop --tag my-dev   # 基镜像本地 exists 禁拉；--format docker
okw image verify openKylin-3.0-desktop               # 静态探针 P1-P8 + 健康 + 服务/HTTP 200
```

镜像不依赖 okw Python 包（零第三方运行时依赖，沿用 bash+pwsh 双环境模式）；构建/冒烟脚本与 `okw podman verify` 语义一致：不修改软件源、不隐式拉取。`okw image` 子命令完整说明见[命令参考](../../../docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md)与[开发容器指南](../../../docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md)。

## 快速安装

要求 Windows + WSL2、Python 3.10 或更高版本；运行时不依赖第三方包。

```powershell
python -m pip install -e .
okw list
okw verify <name>
```

rootless Podman 操作从只读预检开始，安装必须显式确认：

```text
okw podman preflight <name>
okw podman install <name> --yes
okw podman verify <name>
```

`okw podman verify --smoke-image` 仅使用发行版内已存在的镜像，不会隐式拉取。完整约束与操作说明见[工具包指南](../../../docs/tech/guides/openkylin-wsl-devkit/index.md)。

## AI 栈（本地离线 OCR）

`okw ai` 仅封装 AI 栈中唯一完成落机 POC 的能力——Gen1 Kylin AI SDK 的文字识别（本地 tesseract、CPU、离线、无密钥、不下载模型）：

```text
okw ai preflight <name>
okw ai install  <name> --yes
okw ai verify   <name>
okw ai verify   <name> --smoke-ocr /tmp/sample.png   # 对发行版内本地图片离线识别
```

`<name>` 为目标 WSL 发行版名称，先在 PowerShell 运行 `wsl -l -v` 查看（如 `openKylin-3.0-desktop`）。`--smoke-ocr` 的图片可给发行版内路径（如 `/tmp/sample.png`），也支持 Windows 盘符路径（如 `C:\Users\me\sample.png`，自动转换为 `/mnt/c/Users/me/sample.png`、经 drvfs 访问）。

`install` 以 root 执行 `apt install -y --no-install-recommends libkylin-ai-base-dev`，由 APT 解析 tesseract 与 `chi_sim/eng` 语言包；必须 `--yes`，漏确认零写入。可选层（Gen2 引擎、模型管理器、ollama 等）仅在 preflight/verify 中只读盘点、UNKNOWN 不阻断。okw 不配置密钥、不下载模型、不装 ollama/Gen2 全栈。完整背景与边界见[AI 栈指南](../../../docs/tech/guides/openkylin-wsl-devkit/07-ai-stack.md)。

## 桌面（UKUI / xrdp）

`okw desktop` 针对**已预装**桌面的 openKylin Desktop WSL 镜像（如 `openKylin-3.0-desktop`）做只读预检、显式补齐与只读验收：发行版内 UKUI 桌面经 xrdp（默认端口 **3390**）供 Windows 侧 `mstsc` 连接。它**不安装桌面套件**，只启用 xrdp 并补齐首登黑屏看门狗：

```text
okw desktop launch    <name>
okw desktop preflight <name>
okw desktop install   <name> --yes
okw desktop verify    <name>
```

`launch` 一键启动：启动发行版 → 等 `localhost:3390` 就绪 → 拉起 `mstsc`（「连不上」多为发行版 `Stopped`）。

首登黑屏（KWin 窗口管理器冷启动不驻留）的根因与可逆修复（`~/.xsession` 看门狗）已在镜像上实测闭环；`install` 落地该脚本（先备份）。最小镜像（无 xrdp）请改用 Desktop WSL 镜像。完整说明见[桌面指南](../../../docs/tech/guides/openkylin-wsl-devkit/08-desktop.md)。

## xuan-compose（xc）引导

rootless Podman 就绪后，可用 `okw compose` 在同一发行版内以普通用户身份引导 [xuan-compose](https://github.com/xinetzone/xuanspace/tree/main/libs/xuan-compose)（`xinetzone/xuanspace` monorepo 的 `libs/xuan-compose` 子目录，命令 `xc`），串起「WSL 发行版 → rootless Podman → compose」完整链路：

```text
okw podman  preflight <name>
okw podman  install   <name> --yes
okw podman  verify    <name>
okw compose preflight <name> --source <本地目录|URL|包名>
okw compose install   <name> --yes --source <本地目录|URL|包名>
okw compose verify    <name> --smoke
```

`compose install` 经用户级 uv（`~/.local/bin`）托管一份独立 CPython 3.14（不改系统 Python 3.12），再 `uv tool install --python 3.14` 安装 xuan-compose 并生成 `xc`/`xuan-compose` 双 shim；`--source` 必填且无内置默认源，本地源默认拷贝安装（`--editable` 仅限本地源）；缺 `--yes` 仅打印副作用清单、零写入。

> **许可证边界**：xuan-compose 是 **GPL-2.0-only** 第三方软件。okw（MIT）不 import、不复制、不链接、不分发其源码或制品，仅在用户显式授权后，于用户本机按用户指定来源做 CLI 聚合引导（与 `apt` 安装 GPL 包同理）。详见[xuan-compose（xc）引导指南](../../../docs/tech/guides/openkylin-wsl-devkit/06-xuan-compose.md)。
