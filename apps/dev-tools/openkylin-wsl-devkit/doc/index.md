# openKylin WSL 开发工具包（okw）

`okw` 面向 Windows + WSL2：通过 `okw` 管理 WSL 发行版、验收 openKylin 环境、生成 deb/dput 脚手架，并查询知识库快速参考；同时提供 rootless Podman、本地离线 OCR 与 UKUI 桌面（xrdp）的预检/安装/验收能力。

## 环境要求

- Windows + WSL2。
- Python 3.10 或更高版本。
- 无第三方运行时依赖。

## 按任务阅读

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 安装与快速开始
安装工具、完成第一次环境检查与发行版导入。

[进入](01-getting-started.md)
:::

:::{grid-item-card} 命令参考
发行版生命周期、开发脚手架、镜像、compose、AI 与桌面命令速查。

[进入](02-command-reference.md)
:::

:::{grid-item-card} rootless Podman
只读预检、显式安装与发行版内 rootless 验收三步流程。

[进入](03-podman-rootless.md)
:::

:::{grid-item-card} 开发、测试与边界
设计要点、验收口径、测试方式与已知边界。

[进入](04-development-and-boundaries.md)
:::

:::{grid-item-card} openKylin 开发容器镜像
基于 openKylin 3.0 的 SSH + JupyterLab + 容器内 rootless Podman 开发镜像。

[进入](05-openkylin-dev-container.md)
:::

:::{grid-item-card} xuan-compose（xc）引导
在 rootless Podman 就绪后，以用户级 uv 引导安装 xc 并做端到端探活。

[进入](06-xuan-compose.md)
:::

:::{grid-item-card} AI 栈（本地离线 OCR）
预检、安装与验收 tesseract 离线 OCR，支持本地图片冒烟。

[进入](07-ai-stack.md)
:::

:::{grid-item-card} 桌面（UKUI / xrdp）
在已预装桌面的 Desktop WSL 镜像上启用 xrdp 并经 mstsc 连接。

[进入](08-desktop.md)
:::

::::

```{toctree}
:hidden:

01-getting-started
02-command-reference
03-podman-rootless
04-development-and-boundaries
05-openkylin-dev-container
06-xuan-compose
07-ai-stack
08-desktop
```