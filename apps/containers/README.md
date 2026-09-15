# containers/ — Podman rootless 容器工作区分组

> **AI 智能体入口**：[AGENTS.md](AGENTS.md) — 组级路由与 G1-G4 跨成员契约，.agents/ 为组级 AI 资产容器。

`apps/containers/` 是 Podman rootless 容器生态的**三成员工作组**：一个构建端生产镜像，一个消费端加载镜像并管理容器生命周期，一个组内共享包承载连接层与只读工具。

| 成员 | 角色 | 入口 |
|------|------|------|
| [jupyter-podman-rootless/](jupyter-podman-rootless/README.md) | **构建端**：rootless Jupyter 镜像（Python 3.14t + Miniforge3 + SSH + Podman DinP + OMLMD/OLOT + Toolbx），三层后端 compose→SDK→CLI | README · [docs/](jupyter-podman-rootless/docs/README.md)（18 篇）· [AGENTS.md](jupyter-podman-rootless/AGENTS.md) |
| [client/](client/README.md) | **消费端**：从 tar 缓存加载镜像 + 生命周期管理，SDK→CLI 两层后端，Windows 11 × WSL2 原生支持；含 quant/xmnn/monetize 三个 opt-in podman-compose 工作负载栈 | README · [docs/](client/docs/README.md)（13 篇）· [AGENTS.md](client/AGENTS.md) |
| [shared/](shared/pyproject.toml) | **共享包** jpman-common 0.1.0：podman SDK 连接层唯一事实源 + 平台/进程/容器只读工具，两端共同依赖（无独立文档，由组层代管） | pyproject · `src/jpman_common/` · [组级规则](.agents/rules/shared-package.md) |

## 30 秒理解协作关系

构建端 `invoke build` 产出镜像 → 导出到构建端 `.image-cache/*.tar.gz` → 消费端 `invoke load` 自动取最新 tar → `invoke run` 启动容器；shared 包是两端共同的 Python 依赖，**必须最先安装**。

详见 [docs/00-overview.md](docs/00-overview.md)（组全景与端口/栈速查）。

## 快速开始

```bash
cd apps/containers
pip install -e shared                      # 先装组内共享包 jpman-common
cd client && pip install -e .              # 再装消费端（构建端已产出缓存镜像时）
invoke load                                # 自动从 ../jupyter-podman-rootless/.image-cache/ 取最新 tar
invoke run --workspace D:/spaces/SpecWeave  # 打印 SSH/Jupyter URL
```

跨成员端到端完整路径（含构建端步骤、验证清单、可选工作负载栈）见 [docs/01-getting-started.md](docs/01-getting-started.md)。

## 文档导航

| 文档 | 说明 |
|------|------|
| [docs/00-overview.md](docs/00-overview.md) | 组全景：三成员职责、镜像流/依赖流、工作负载栈与端口速查 |
| [docs/01-getting-started.md](docs/01-getting-started.md) | 跨成员端到端：环境前置 → shared → 构建 → 缓存交接 → load/run → 可选栈 |
| [jupyter-podman-rootless/docs/](jupyter-podman-rootless/docs/README.md) | 构建端文档索引（18 篇） |
| [client/docs/](client/docs/README.md) | 消费端文档索引（13 篇，含 Windows/WSL、排障速查、三栈手册） |

## AI 协作者规范

组级跨成员硬约束（G1-G4：共享包唯一事实源 / 安装顺序 / rootless 三必需 / 反双写）见 [AGENTS.md](AGENTS.md)；
组级 AI 资产容器见 [.agents/](.agents/README.md)。成员内规则以各成员 AGENTS.md 为权威。
复杂任务走 SpecWeave 七概念方法论编排（[根指令](../../.agents/commands/seven-concepts.md)）。
