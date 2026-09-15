---
id: "containers-group-docs-index"
title: "apps/containers 组级文档索引"
source: "../README.md"
---
# apps/containers 组级文档

Podman rootless 容器生态工作组：**构建端**（jupyter-podman-rootless）+
**消费端**（client）+ **组内共享包**（shared / jpman-common）。

组级文档只覆盖**跨成员**主题；成员内使用手册见各成员 `docs/`：

- 构建端：[jupyter-podman-rootless/docs/](../jupyter-podman-rootless/docs/README.md)（18 篇）
- 消费端：[client/docs/](../client/docs/README.md)（13 篇，含 Windows/WSL 与三栈手册）

## 文档目录

| 文档 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | 组全景：三成员职责、镜像流与依赖流、工作负载栈/端口速查、jpman 与 invoke 分工 |
| [01-getting-started.md](01-getting-started.md) | 跨成员端到端：环境前置 → shared → 构建 → 缓存交接 → load/run → 可选工作负载栈 |

## AI 协作者规范

组级跨成员硬约束（G1-G4）见 [../AGENTS.md](../AGENTS.md)；
共享包治理见 [../.agents/rules/shared-package.md](../.agents/rules/shared-package.md)。
