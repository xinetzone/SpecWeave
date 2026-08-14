---
id: "devcontainer-base-agents-readme"
title: "devcontainer-base AI资产容器"
source: "AGENTS.md"
---
# devcontainer-base - .agents 目录

本目录是 devcontainer-base 子项目的 AI 协作者资产容器，存放项目特有的规则、角色、技能、脚本、工作流和模板。

## 目录结构

```
.agents/
├── README.md          ← 本文件（目录索引）
├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   ├── dockerfile.md  ← Dockerfile 多阶段构建规范
│   ├── entrypoint.md  ← Entrypoint 启动脚本规范
│   ├── services.md    ← 服务管理规范（supervisord + SSH/Docker/Podman/Jupyter）
│   └── build-test.md  ← 构建与测试流程
├── roles/             ← 角色定义（预留，回退到父级）
├── skills/            ← 技能（预留，回退到父级）
├── scripts/           ← 自动化脚本（预留）
├── workflows/         ← CI/CD工作流设计文档
│   └── variants-ci.md ← 变体构建CI + ONNX量化工具包CI设计
├── templates/         ← 模板（预留）
└── docs/              ← AI知识库（预留）
```

## 快速开始：AI协作者规则加载指南

当 AI 智能体进入 `apps/docker-images/devcontainer-base/` 目录工作时，按以下顺序加载规则：

### 加载顺序（三层路由）

```
第1层（根级）：SpecWeave 全局规范 → ../../.agents/global-core-rules.md
第2层（区域级）：apps/ 区域路由 → ../AGENTS.md
第3层（应用级）：devcontainer-base 项目特有规则 → 本目录 rules/
```

### 必读规则文件（按任务类型路由）

| 任务场景 | 必读规则文件 | 核心关注点 |
|---------|-------------|-----------|
| 修改 Dockerfile | [rules/dockerfile.md](rules/dockerfile.md) | BuildKit语法、多阶段结构、层缓存、中文环境、非root用户、安全规范 |
| 修改启动脚本 | [rules/entrypoint.md](rules/entrypoint.md) | tini init、日志格式、启动流程、信号处理、命令模式 |
| 修改服务配置 | [rules/services.md](rules/services.md) | supervisord管理、Docker DinD、Podman rootless、Jupyter、SSH、健康检查 |
| 构建/测试/部署 | [rules/build-test.md](rules/build-test.md) | build.sh/start.sh用法、Compose profile、验证流程、问题排查 |
| 镜像变体构建/新增 | [../variants/AGENTS.md](../variants/AGENTS.md) | 变体路由入口，构建编排/共享约定/测试规范/新增指南 |
| CI流水线设计 | [workflows/variants-ci.md](workflows/variants-ci.md) | 双流水线设计（Docker变体构建+Python量化CI）、依赖拓扑、精度门禁 |

### 规则加载自检清单

AI协作者在开始工作前必须确认：
- [ ] 已读取 [AGENTS.md](../AGENTS.md) 了解项目概述和约束速览
- [ ] 已根据任务类型读取对应的 `rules/*.md` 文件
- [ ] 理解 Docker DinD 的 daemon.json 单一配置源原则（避免命令行参数冲突）
- [ ] 理解非root用户 devuser (UID 1000) 的权限模型
- [ ] 修改后运行 `python .agents/scripts/check-links.py --path apps/docker-images/devcontainer-base/` 验证链接

### 规则文件 frontmatter 规范

每个规则文件必须包含以下 frontmatter 字段：

```yaml
---
id: "唯一标识符（kebab-case）"
title: "规则标题"
source: "内容来源（原始文件路径#章节）"
---
```

### 父级继承

所有未在本目录定义的规则、角色、技能均回退到 SpecWeave 根工作区：
- 全局规则：[../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md)
- 全局 Skill：[../../../.agents/skills/](../../../.agents/skills/)
- 七概念指令集：[../../../.agents/commands/](../../../.agents/commands/)

## 变更日志

- 2026-08-07 | feat | 新增 workflows/variants-ci.md（双CI流水线设计文档）；更新路由表添加变体/CI入口
- 2026-08-07 | feat | 从 AGENTS.md 拆分出 .agents/ 目录，约束规则按主题原子化为4个rules文件
