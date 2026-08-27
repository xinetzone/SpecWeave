---
id: jupyter-podman-rootless-changelog
title: jupyter-podman-rootless 变更日志
source: 从 apps/containers/jupyter-podman-rootless/AGENTS.md 拆分归档
---

# 变更日志

## 2026-08-27

| 类型 | 变更 |
|------|------|
| refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（7个主题文件）；README.md原子化至docs/（14个文档） |
| feat | R5/Toolbx集成：Toolbx兼容标记(LABEL+/run/host+markers+capsh)、compose.dev.yaml透传覆盖文件、注释式透传文档 |
| feat | R4/OLOT集成：KServe ModelCar标准镜像打包(model.pack/extract)、olot_car.py辅助脚本 |
| feat | R3/OMLMD集成：ML模型OCI artifact分发(model.push/pull/config)、model-registry compose service(profile:registry) |
| feat | R2/podman-compose集成：声明式compose.yaml编排、.env配置管理、compose_backend.py |
| feat | R1/podman-py SDK集成：三层exec后端架构、client.py封装 |

## 2026-08-26

| 类型 | 变更 |
|------|------|
| feat | 完整实现：Containerfile(7层)、entrypoint.sh(7步)、config/配置、invoke任务、healthcheck |
| feat | 初始化项目结构：AGENTS.md、目录结构、pyproject.toml、.containerignore、README.md |
