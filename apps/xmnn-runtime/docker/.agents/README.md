---
id: "xmnn-runtime-docker-agents-readme"
title: "xmnn-runtime/docker AI资产容器"
source: "docker/Dockerfile + docker/entrypoint.sh"
---
# xmnn-runtime/docker - .agents 目录

本目录是 xmnn-runtime 子项目的 Docker 构建资产容器。注意：.agents/ 位于 `docker/` 子目录下（非项目根目录），因为Docker相关文件集中在docker/目录。

## 目录结构

```
docker/.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← Docker构建特有规则
│   ├── dockerfile.md  ← Dockerfile 6阶段构建规范（BuildKit缓存/计时/★热点层设计）
│   ├── entrypoint.md  ← Entrypoint 启动脚本规范（conda激活/UID自适应/gosu切换）
│   └── build-test.md  ← 构建与测试流程（build.sh/verify.sh/上下文路径）
├── roles/             ← 角色定义（预留，回退到父级）
├── skills/            ← 技能（预留，回退到父级）
├── scripts/           ← 自动化脚本（预留）
├── workflows/         ← 工作流（预留）
├── templates/         ← 模板（预留）
└── docs/              ← AI知识库（预留）
```

## 特殊说明

- **.agents/位于docker/子目录**：因为xmnn-runtime的Docker文件（Dockerfile/entrypoint.sh/build.sh等）都集中在docker/目录
- **无services.md**：纯运行时镜像，无SSH/Jupyter/supervisord服务
- **无tini**：镜像不内置tini，使用`docker run --init`
- **UID/GID自适应**：从/workspace自动检测宿主机UID/GID，非固定UID

## 父级继承

所有未在本目录定义的规则、角色、技能均回退到 SpecWeave 根工作区：
- 全局规则：[../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../.agents/skills/](../../../.agents/skills/)
- 七概念指令集：[../../../.agents/commands/](../../../.agents/commands/)
- Dockerfile 自动化测试脚本：[../../../.agents/scripts/test-dockerfiles.ps1](../../../.agents/scripts/test-dockerfiles.ps1)
- 日志库：[lib/logging.sh](lib/logging.sh)（xmnn-runtime专用）

## 变更日志

- 2026-08-07 | feat | 创建.agents/原子化结构（3个rules文件），.agents位于docker/子目录
