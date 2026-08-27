---
id: "jupyter-docs-readme"
title: "jupyter-podman-rootless 文档索引"
source: "README.md"
---
# jupyter-podman-rootless 文档

基于 Podman rootless 模式的 Jupyter 开发容器：Python 3.14t (free-threading) + Miniforge3 + SSH + rootless Podman，通过 supervisord 管理多服务。三层后端编排（podman-compose 声明式 → podman-py SDK → CLI fallback），内置 OMLMD 模型 artifact 分发、OLOT KServe ModelCar 打包、Toolbx 透传兼容。

## 文档目录

### 入门指南

| 文档 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | 特性一览 |
| [01-getting-started.md](01-getting-started.md) | 快速开始：前置条件、安装invoke、三种使用方式 |

### 使用参考

| 文档 | 说明 |
|------|------|
| [02-invoke-reference.md](02-invoke-reference.md) | Invoke任务参考：核心命令、ML命令、参数说明 |
| [03-environment-variables.md](03-environment-variables.md) | 环境变量参考：运行时变量、构建时变量 |
| [04-image-architecture.md](04-image-architecture.md) | 镜像架构：7层构建、7步启动、服务管理、Compose架构 |

### 高级主题

| 文档 | 说明 |
|------|------|
| [05-rootless-podman.md](05-rootless-podman.md) | Rootless Podman说明：容器内运行容器 |
| [06-ml-model-management.md](06-ml-model-management.md) | ML模型管理：OMLMD+OLOT、ModelCar打包 |
| [07-toolbx-passthrough.md](07-toolbx-passthrough.md) | Toolbx透传开发模式：透传配置、安全设计 |
| [08-directory-structure.md](08-directory-structure.md) | 目录结构说明 |
| [09-three-tier-backend.md](09-three-tier-backend.md) | 三层后端编排架构 |
| [10-direct-cli-usage.md](10-direct-cli-usage.md) | 直接使用Podman/Docker命令 |
| [11-free-threading.md](11-free-threading.md) | Python Free-Threading（无GIL）说明 |
| [12-healthcheck.md](12-healthcheck.md) | 健康检查机制 |
| [13-faq.md](13-faq.md) | 常见问题解答 |

## AI协作者规范

项目特有的AI协作者规范已原子化拆分至 [.agents/](../.agents/README.md) 目录：
- Containerfile编写规范
- Entrypoint启动脚本规范
- 服务配置规范
- Compose编排与透传规范
- Invoke任务开发规范
- ML模型管理规范
- 构建与测试规范

## 快速开始

```bash
# 安装依赖（invoke）
pip install -e ".[compose]"

# 构建镜像（清华源加速）
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 启动容器
invoke run

# 查看访问信息（启动时会打印）
# SSH:  ssh -p 2222 devuser@localhost
# Jupyter Lab: http://localhost:8888/lab?token=<自动生成的token>
```

详见 [01-getting-started.md](01-getting-started.md)。

## 变更日志

- 2026-08-27 | refactor | README.md原子化至docs/目录（14个文档），AGENTS.md精简为路由入口并迁移至.agents/
- 2026-08-27 | feat | R5/Toolbx集成：Toolbx兼容标记、compose.dev.yaml透传
- 2026-08-27 | feat | R4/OLOT集成：KServe ModelCar打包
- 2026-08-27 | feat | R3/OMLMD集成：ML模型OCI artifact分发
- 2026-08-27 | feat | R2/podman-compose集成：声明式编排
- 2026-08-27 | feat | R1/podman-py SDK集成：三层后端架构
- 2026-08-26 | feat | 完整实现：Containerfile、entrypoint、config、invoke任务
