---
id: "jupyter-podman-client-docs-index"
title: "jupyter-podman-client 文档索引"
source: "README.md"
---
# jupyter-podman-client 文档

`apps/containers/jupyter-podman-rootless` 镜像构建端的**消费端**：基于 `podman-py`
从本地加载构建端产出的镜像，并提供极简的容器生命周期管理。核心差异能力是
**Windows 11 × WSL2 跨平台 SDK 连接** + **rootless 三必需硬编码** +
**两层后端自动降级（SDK → CLI fallback）**，另含 opt-in 的 `quant.*` / `xmnn.*` /
`monetize.*` 三个 podman-compose 工作负载栈命名空间。

## 文档目录

### 入门指南

| 文档 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | 项目概述：与构建端的关系、与 jpman 分工 |
| [01-getting-started.md](01-getting-started.md) | 快速开始：安装、加载镜像、启动/停止/清理、镜像备份恢复 |

### 使用参考

| 文档 | 说明 |
|------|------|
| [02-invoke-reference.md](02-invoke-reference.md) | 命令速查：invoke 任务表、布尔三态契约、known_hosts 自动维护 |
| [03-windows-wsl.md](03-windows-wsl.md) | Windows 11 × WSL2 支持：三种落地路径、连接优先级、逃生舱、A/B 维度分离 |
| [04-troubleshooting-guide.md](04-troubleshooting-guide.md) | 30 秒修复速查表：Windows 原生坑 W-I1~W-I4 + 容器/运行时坑 C-I1~C-I5 |
| [05-sdk-usage.md](05-sdk-usage.md) | 作为 SDK 使用（Python import） |
| [06-run-discipline.md](06-run-discipline.md) | 内置纪律：rootless 三必需参数、运行身份 |
| [07-environment-variables.md](07-environment-variables.md) | .env 配置完整清单：容器级、SDK 级、运行时透传 |

### 架构与高级主题

| 文档 | 说明 |
|------|------|
| [08-env-bootstrap.md](08-env-bootstrap.md) | 容器内自举：env.* 命令、叠加层镜像约定、base-digest 防陈旧机制 |
| [09-passthrough.md](09-passthrough.md) | 运行时透传：5+1 开关、Host 网络端口语义、宿主侧前置 |
| [10-quant-overlay.md](10-quant-overlay.md) | 工作负载栈 onnx-quantized：quant.* 命令、配置、裸 compose |
| [11-xmnn-overlay.md](11-xmnn-overlay.md) | 工作负载栈 xmnn-dev：xmnn.* 命令、双 ABI、源码挂载、Nuitka 打包 |
| [12-monetize-overlay.md](12-monetize-overlay.md) | 工作负载栈 agent-monetize-dev：monetize.* 命令、tvm-ffi 原生编译 |

## AI 协作者规范

项目特有的 AI 协作者规范（AI 级硬约束）已原子化拆分至 [.agents/](../.agents/README.md) 目录：
invoke 任务规范 / SDK 连接硬约束 / Windows WSL 规则 / quant 工作负载栈规则 /
xmnn 开发/打包栈规则 / monetize tvm-ffi 栈规则。

## 快速开始

```bash
cd apps/containers/client
pip install -e .
invoke load                                          # 自动从构建端 .image-cache 加载最新镜像
invoke run --workspace D:/spaces/SpecWeave           # 启动容器（打印 SSH/Jupyter URL）
invoke status                                        # 查看状态
invoke stop                                          # 停止+删除容器
```

在 Windows 11 原生 CPython 下零配置即可运行（自动探测 WSL9P / Podman Machine / tcp）。

## 变更日志

完整变更历史见 [.agents/CHANGELOG.md](../.agents/CHANGELOG.md)。