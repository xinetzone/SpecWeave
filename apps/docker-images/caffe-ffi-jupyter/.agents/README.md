---
id: "caffe-ffi-jupyter-agents-readme"
title: "caffe-ffi-jupyter AI资产容器"
source: "AGENTS.md"
---
# caffe-ffi-jupyter - .agents 目录

本目录是 caffe-ffi-jupyter 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   ├── dockerfile.md  ← Dockerfile 增量构建规范（继承jupyter-ssh-base/Miniconda/caffe-ffi编译/RPATH/内核注册）
│   └── build-test.md  ← 构建与测试流程（WSL前提/基础镜像依赖/Compose/内核验证/动态库验证）
├── roles/             ← 角色定义（预留，回退到父级）
├── skills/            ← 技能（预留，回退到父级）
├── scripts/           ← 自动化脚本（预留）
├── workflows/         ← 工作流（预留）
├── templates/         ← 模板（预留）
└── docs/              ← AI知识库（预留）
```

## 父级继承链

```
SpecWeave 根 AGENTS.md（全局规则/Skill/角色）
  └─ apps/docker-images/jupyter-ssh-base/.agents/（SSH + Jupyter + supervisord + entrypoint规范）
       └─ apps/docker-images/caffe-ffi-jupyter/.agents/（本文件，增量构建caffe-ffi规范）
```

**关键**：entrypoint、services、security等规范直接继承自jupyter-ssh-base，本项目无需重复定义entrypoint.md和services.md。

- 全局规则：[../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md)
- 父镜像规范：[../jupyter-ssh-base/.agents/](../../jupyter-ssh-base/.agents/)
- 全局 Skill：[../../../.agents/skills/](../../../../.agents/skills/)
- 七概念指令集：[../../../.agents/commands/](../../../../.agents/commands/)
- Dockerfile 自动化测试脚本：[../../../.agents/scripts/test-dockerfiles.ps1](../../../../.agents/scripts/test-dockerfiles.ps1)

## 变更日志

- 2026-08-07 | feat | 从AGENTS.md拆分出.agents/目录，约束规则按主题原子化为2个rules文件（继承jupyter-ssh-base的entrypoint/services规范）
