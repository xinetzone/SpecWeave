---
id: "context-routing"
title: "上下文路由表"
source: ".agents/context-routing.md"
---
# 上下文路由表

本文件是启动协议步骤 2 的核心依据，定义任务类型与必读规范入口的映射关系。所有智能体在执行任务前必须查阅本表，确定需要加载的规范文件。

## 常规任务路由

| 任务类型 | 必读入口 |
|---|---|
| 全局核心规则（启动协议、内容分流、沟通语言） | [global-core-rules.md](global-core-rules.md) |
| 内容敏感度预检（公开/私域判定与工作流分流） | [rules/content-sensitivity-precheck.md](rules/content-sensitivity-precheck.md) |
| AI 编码行为准则（歧义澄清/简约设计/精确编辑/目标驱动） | [rules/ai-coding-guidelines.md](rules/ai-coding-guidelines.md) |
| Bug 修复闭环（修复→预防→闭环） | [rules/fix-prevent-close-loop.md](rules/fix-prevent-close-loop.md) |
| Spec 文档编写 | [rules/spec-writing-guide.md](rules/spec-writing-guide.md) |
| Spec 创建前预检（位置+格式） | [rules/spec-creation-precheck.md](rules/spec-creation-precheck.md) |
| 角色定义、职责分工 | [roles/README.md](roles/README.md) |
| 协作协议 | [protocols/README.md](protocols/README.md) |
| 工作区发现与零安装自举 | [protocols/workspace-discovery.md](protocols/workspace-discovery.md) |
| 一句话提示词自举 | [protocols/prompt-bootstrap.md](protocols/prompt-bootstrap.md) |
| 标准工作流（功能开发/代码审查） | [workflows/README.md](workflows/README.md) |
| 任务与交接模板 | [templates/README.md](templates/README.md) |
| 标准化指令集 | [commands/README.md](commands/README.md) |
| 检查清单 | [checklists/README.md](checklists/README.md) |
| Skill 技能门面 | [skills/README.md](skills/README.md) |
| 能力索引（L1） | [capability-registry.md](capability-registry.md) |

## 关联入口

- [../AGENTS.md](../AGENTS.md) — 智能体全局契约入口（含启动协议）
- [global-core-rules.md](global-core-rules.md) — 全局核心规则
- [README.md](README.md) — `.agents/` 规范容器总览