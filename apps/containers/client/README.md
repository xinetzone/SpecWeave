# jupyter-podman-client（镜像消费端）

> **定位**：`apps/containers/jupyter-podman-rootless` 镜像构建端的**消费端**。
> 基于 `podman-py` 从本地加载构建端产出的镜像，并提供极简的容器生命周期管理。
> 核心差异能力：**Windows 11 × WSL2 跨平台 SDK 连接** + **rootless 三必需硬编码** +
> 两层后端自动降级（SDK → CLI fallback）。

- 需要快速启停、日常驾驶（status/shell/logs 等）→ 用构建端的 `jpman` CLI
- 需要 Python 脚本化集成、在其他应用里以 SDK 方式加载/运行镜像 → 用本项目

## 快速开始

```bash
cd apps/containers/client
pip install -e .
invoke --list        # 应看到 load / images / run / stop / status / clean + container.* / env.*
invoke load          # 自动从 ../jupyter-podman-rootless/.image-cache/ 拿最新 tar
invoke run --workspace D:/spaces/SpecWeave   # 启动成功打印 SSH/Jupyter URL
```

Windows 11 原生 CPython 零配置即可运行（自动探测 WSL9P / Podman Machine / tcp）。

## 文档导航

详细文档已原子化拆分至 [docs/](docs/README.md) 目录：

| 分类 | 文档 | 说明 |
|------|------|------|
| 入门 | [docs/00-overview.md](docs/00-overview.md) [docs/01-getting-started.md](docs/01-getting-started.md) | 项目概述、快速开始、镜像备份恢复 |
| 使用参考 | [docs/02-invoke-reference.md](docs/02-invoke-reference.md) [docs/03-windows-wsl.md](docs/03-windows-wsl.md) [docs/04-troubleshooting-guide.md](docs/04-troubleshooting-guide.md) [docs/05-sdk-usage.md](docs/05-sdk-usage.md) [docs/06-run-discipline.md](docs/06-run-discipline.md) [docs/07-environment-variables.md](docs/07-environment-variables.md) | 命令速查、Windows×WSL2、排障速查、SDK 用法、三必需纪律、.env 清单 |
| 架构与高级 | [docs/08-env-bootstrap.md](docs/08-env-bootstrap.md) [docs/09-passthrough.md](docs/09-passthrough.md) [docs/10-quant-overlay.md](docs/10-quant-overlay.md) [docs/11-xmnn-overlay.md](docs/11-xmnn-overlay.md) [docs/12-monetize-overlay.md](docs/12-monetize-overlay.md) | env.* 自举、运行时透传、quant/xmnn/monetize 工作负载栈 |

## AI 协作者规范

项目特有的 AI 协作者规范（AI 级硬约束）以 [.agents/](.agents/README.md) 为索引，
规则文件见 `.agents/rules/`（invoke-tasks / sdk-connection / windows-wsl /
quant-overlay / xmnn-overlay / monetize-overlay）。复杂任务需走
SpecWeave 七概念方法论编排（[根指令](../../../.agents/commands/seven-concepts.md)）。