# openkylin-wsl-devkit（okw）

openKylin WSL 开发工具包：通过 `okw` 管理 WSL 发行版、验收 openKylin 环境、生成 deb/dput 脚手架，并查询知识库快速参考。

## 环境要求

- Windows + WSL2。
- Python 3.10 或更高版本。
- 运行时不依赖第三方包。

## 快速开始

```powershell
python -m pip install -e .
okw list
okw verify <name>
```

## 文档

完整使用手册的**唯一真源**是本目录下的 Sphinx + MyST 站点 `doc/`：

| 页面 | 内容 |
|---|---|
| [文档首页](doc/index.md) | 站点入口：环境要求与按任务阅读的卡片导航 |
| [okw 安装与快速开始](doc/01-getting-started.md) | 安装工具、完成第一次环境检查与发行版导入 |
| [okw WSL 与开发命令参考](doc/02-command-reference.md) | 发行版生命周期、开发脚手架、镜像、compose、AI 与桌面命令速查 |
| [okw rootless Podman 指南](doc/03-podman-rootless.md) | 只读预检、显式安装与发行版内 rootless 验收三步流程 |
| [okw 开发、设计与边界](doc/04-development-and-boundaries.md) | 设计要点、验收口径、测试方式与已知边界 |
| [openKylin 开发容器镜像指南](doc/05-openkylin-dev-container.md) | 基于 openKylin 3.0 的 SSH + JupyterLab + 容器内 rootless Podman 开发镜像 |
| [okw 引导 xuan-compose（xc）指南](doc/06-xuan-compose.md) | 在 rootless Podman 就绪后，以用户级 uv 引导安装 `xc` 并做端到端探活 |
| [okw AI 栈：本地 OCR 预检、安装与验收](doc/07-ai-stack.md) | 预检、安装与验收 tesseract 离线 OCR，支持本地图片冒烟 |
| [okw 桌面：UKUI（xrdp/WSL）预检、补齐与验收](doc/08-desktop.md) | 在已预装桌面的 Desktop WSL 镜像上启用 xrdp 并经 `mstsc` 连接 |

## 能力概览

- **快速安装**：`pip install -e .` 后即可使用 `okw`，无第三方运行时依赖。[详见](doc/01-getting-started.md)
- **发行版与命令**：列出、导入、导出、注销发行版，在发行版内执行命令并做环境验收。[详见](doc/02-command-reference.md)
- **rootless Podman**：只读预检 → 显式安装 → rootless 验收；不切换默认发行版、不改软件源、不编辑 `wsl.conf`。[详见](doc/03-podman-rootless.md)
- **openKylin 开发容器镜像**：SSH（22）+ JupyterLab（8888）+ 容器内 rootless Podman（devuser），supervisord 管理服务栈、tini 作 init。[详见](doc/05-openkylin-dev-container.md)
- **xuan-compose（xc）**：rootless Podman 就绪后，以用户级 uv 托管独立 CPython 3.14 并安装 `xc`，再端到端探活。[详见](doc/06-xuan-compose.md)
- **AI 栈（本地离线 OCR）**：封装 Gen1 Kylin AI SDK 文字识别——本地 tesseract、CPU、离线、无密钥、不下载模型。[详见](doc/07-ai-stack.md)
- **桌面（UKUI / xrdp）**：针对已预装桌面的镜像启用 xrdp（默认端口 3390）供 `mstsc` 连接，不安装桌面套件。[详见](doc/08-desktop.md)
- **设计要点与边界**：零第三方运行时依赖、保护默认发行版、破坏性操作显式确认等。[详见](doc/04-development-and-boundaries.md)

## 许可证边界

okw 本体采用 **Apache-2.0** 许可证。xuan-compose 是 **GPL-2.0-only** 第三方软件：okw 不 import、不复制、不链接、不分发其源码或制品，仅在用户显式授权后，于用户本机按用户指定来源做 CLI 聚合引导（与 `apt` 安装 GPL 包同理）。详见[xuan-compose（xc）引导指南](doc/06-xuan-compose.md)。

## 本地预览文档

```powershell
python -m pip install -r doc/requirements.txt
python -m sphinx -b html doc doc/_build/html
```