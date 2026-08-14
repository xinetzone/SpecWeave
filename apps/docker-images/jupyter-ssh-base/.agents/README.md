---
id: "jupyter-ssh-base-agents-readme"
title: "jupyter-ssh-base AI资产容器"
source: "AGENTS.md"
---
# jupyter-ssh-base - .agents 目录

本目录是 jupyter-ssh-base 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   ├── dockerfile.md  ← Dockerfile 多阶段构建规范（BuildKit/层缓存/安全/非root用户/可复用性）
│   ├── entrypoint.md  ← Entrypoint 启动脚本规范（日志/信号处理/密码初始化/命令模式）
│   ├── services.md    ← 服务管理规范（supervisord + SSH + Jupyter双服务+健康检查）
│   └── build-test.md  ← 构建与测试流程（快速开始/验证清单/依赖管理/.dockerignore）
├── roles/             ← 角色定义（预留，回退到父级）
├── skills/            ← 技能（预留，回退到父级）
├── scripts/           ← 自动化脚本（预留）
├── workflows/         ← 工作流（预留）
├── templates/         ← 模板（预留）
└── docs/              ← AI知识库（预留）
```

## 父级继承

所有未在本目录定义的规则、角色、技能均回退到 SpecWeave 根工作区：
- 全局规则：[../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../.agents/skills/](../../../../.agents/skills/)
- 七概念指令集：[../../../.agents/commands/](../../../../.agents/commands/)
- Dockerfile 自动化测试脚本：[../../../.agents/scripts/test-dockerfiles.ps1](../../../../.agents/scripts/test-dockerfiles.ps1)

## 变更日志

- 2026-08-07 | feat | 从 AGENTS.md 拆分出 .agents/ 目录，约束规则按主题原子化为4个rules文件
