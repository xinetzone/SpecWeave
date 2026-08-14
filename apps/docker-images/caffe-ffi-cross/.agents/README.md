---
id: "caffe-ffi-cross-agents-readme"
title: "caffe-ffi-cross AI资产容器"
source: "AGENTS.md"
---
# caffe-ffi-cross - .agents 目录

本目录是 caffe-ffi-cross 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   ├── dockerfile.md  ← Dockerfile 交叉编译规范（双Dockerfile/conda-forge交叉编译器/SDK/Wine）
│   └── build-test.md  ← 构建与测试流程（--mirror/--skip-sdk/跨平台编译验证/产物检查）
├── roles/             ← 角色定义（预留，回退到父级）
├── skills/            ← 技能（预留，回退到父级）
├── scripts/           ← 自动化脚本（预留）
├── workflows/         ← 工作流（预留）
├── templates/         ← 模板（预留）
└── docs/              ← AI知识库（预留）
```

**关键区别**：本项目是**纯构建工具镜像**（交叉编译conda包），无entrypoint、无服务管理（supervisord/SSH/Jupyter），因此不需要entrypoint.md和services.md规则文件。

## 父级继承

所有未在本目录定义的规则、角色、技能均回退到 SpecWeave 根工作区：
- 全局规则：[../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../.agents/skills/](../../../../.agents/skills/)
- 七概念指令集：[../../../.agents/commands/](../../../../.agents/commands/)
- Dockerfile 自动化测试脚本：[../../../.agents/scripts/test-dockerfiles.ps1](../../../../.agents/scripts/test-dockerfiles.ps1)

## 变更日志

- 2026-08-07 | feat | 创建.agents/原子化结构（2个rules文件），因是纯构建镜像无entrypoint/services
