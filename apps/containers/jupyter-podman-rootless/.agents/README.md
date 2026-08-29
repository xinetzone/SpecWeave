---
id: "jupyter-podman-rootless-agents-readme"
title: "jupyter-podman-rootless AI资产容器"
source: "AGENTS.md"
---
# jupyter-podman-rootless - .agents 目录

本目录是 jupyter-podman-rootless 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md              ← 本文件（目录索引）
├── CHANGELOG.md           ← 项目变更日志
├── rules/                 ← 项目特有规则（单一职责，按主题拆分）
│   ├── containerfile.md   ← Containerfile 编写规范（7层架构/Toolbx兼容/free-threading）
│   ├── entrypoint.md      ← Entrypoint 启动脚本规范（7步启动流程）
│   ├── services.md        ← supervisord/SSH/Jupyter/Podman服务配置规范
│   ├── compose.md         ← compose编排/profiles/透传配置规范
│   ├── invoke-tasks.md    ← invoke任务开发规范（三层后端/client.py）
│   ├── ml-models.md       ← ML模型管理规范（OMLMD/OLOT/model-registry）
│   └── build-test.md      ← 构建与测试规范
├── roles/                 ← 角色定义（预留，回退到父级）
├── skills/                ← 技能（预留，回退到父级）
├── scripts/               ← 自动化脚本（预留）
├── workflows/             ← 工作流（预留）
├── templates/             ← 模板（预留）
└── docs/                  ← AI知识库（预留）
```

## 项目核心资产（AI 协作者须知）

除 `.agents/rules/` 下的规则文件外，AI 协作者还需了解以下核心资产：

| 资产 | 路径 | 说明 |
|------|------|------|
| jpman CLI | [../bin/jpman](../bin/jpman) | 零依赖CLI，纯bash实现，跨平台（bash/cmd/ps1） |
| Containerfile | [../Containerfile](../Containerfile) | 多阶段构建定义（Layer 4/5 支持缓存增量重建） |
| pyproject.toml | [../pyproject.toml](../pyproject.toml) | Python项目配置（scikit-build-core + invoke） |
| CMakeLists.txt | [../CMakeLists.txt](../CMakeLists.txt) | scikit-build-core CMake配置 |
| .env.example | [../.env.example](../.env.example) | 环境变量模板（含jpman和invoke两种配置方式） |
| jupyter配置 | [../config/jupyter_notebook_config.py](../config/jupyter_notebook_config.py) | Jupyter配置（allow_hidden=True，allow_root=True） |

## 文档与规范对应关系

人类可读文档在 `../docs/` 目录，与 `.agents/rules/` 的规则对应关系：

| 规则文件 | 对应人类文档 |
|----------|-------------|
| containerfile.md | [04-image-architecture.md](../docs/04-image-architecture.md) |
| entrypoint.md | [04-image-architecture.md](../docs/04-image-architecture.md) |
| services.md | [04-image-architecture.md](../docs/04-image-architecture.md) |
| compose.md | [07-toolbx-passthrough.md](../docs/07-toolbx-passthrough.md) |
| invoke-tasks.md | [02-invoke-reference.md](../docs/02-invoke-reference.md), [09-three-tier-backend.md](../docs/09-three-tier-backend.md) |
| ml-models.md | [06-ml-model-management.md](../docs/06-ml-model-management.md) |
| build-test.md | [01-getting-started.md](../docs/01-getting-started.md) |
| （jpman CLI） | [14-jpman-cli.md](../docs/14-jpman-cli.md), [15-wsl-export.md](../docs/15-wsl-export.md), [16-image-cache.md](../docs/16-image-cache.md) |

## 父级继承

所有未在本目录定义的规则、角色、技能均回退到 SpecWeave 根工作区：
- 全局规则：[../../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../../.agents/skills/](../../../../.agents/skills/)
- 七概念指令集：[../../../../.agents/commands/](../../../../.agents/commands/)
- 根 AGENTS.md：[../../../../AGENTS.md](../../../../AGENTS.md)

## 变更日志

详见 [CHANGELOG.md](CHANGELOG.md)。

- 2026-08-27 | feat | jpman零依赖CLI（跨平台bash/cmd/ps1）、镜像缓存、WSL2一键导出、增量重建；文档从14个增至17个
- 2026-08-27 | refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（7个主题文件）；README.md原子化至docs/（14个文档）
- 2026-08-27 | feat | 初始化AGENTS.md + 完整功能实现
