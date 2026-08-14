---
id: "docker-ssh-dind-agents-readme"
title: "docker-ssh-dind AI资产容器"
source: "AGENTS.md"
---
# docker-ssh-dind - .agents 目录

本目录是 docker-ssh-dind 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   ├── containerfile.md  ← Containerfile 编写规范（7阶段结构/层缓存/DinD配置/安全/中文环境）
│   ├── entrypoint.md     ← Entrypoint 启动脚本规范（6步启动流程/日志/信号处理/Docker等待/诊断）
│   └── build-test.md     ← 构建与测试规范（build/run命令/7步验证流程/常见问题排查）
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

- 2026-08-07 | refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（3个主题文件）
- 2026-07-20 | feat | 初始化AGENTS.md + .agents骨架
