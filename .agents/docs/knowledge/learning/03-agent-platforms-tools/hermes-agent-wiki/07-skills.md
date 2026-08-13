---
id: "hermes-agent-wiki-07-skills"
title: "07 技能系统"
source: "hermes-agent user-guide/features/skills.md + user-guide/features/curator.md + developer-guide/creating-skills.md + reference/skills-catalog.md + 源码 agent/curator.py"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/07-skills.toml"
type: "Wiki Tutorial"
description: "Hermes Agent 技能系统：过程记忆、SKILL.md 标准、skills/ 与 optional-skills/、技能中心、curator 生命周期、技能分类"
status: "stable"
category: "learning"
tags: ["hermes", "skills", "skill", "curator"]
date: "2026-08-09"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 以技能（skill）承载过程记忆：agent 从经验创建/改进 SKILL.md 形式的技能；内置 skills/ 与可选 optional-skills/ 分层，技能中心统一管理，curator 后台维护技能生命周期"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 07 技能系统

## 7.1 技能是什么：过程记忆

**技能（skill）** 是 Hermes Agent 的**过程记忆**载体——它把"如何完成某类任务"的步骤化知识封装为一个带 `SKILL.md` 的目录，供 agent 按需加载执行。与持久记忆（`MEMORY.md`/`USER.md` 的事实记忆）不同，技能偏重**可执行的步骤流程**。

Hermes 通过**自我改进循环（self-improvement loop）**：每当 agent 解决一个新颖问题，它会把经验沉淀为一个技能保存到 `~/.hermes/skills/`，并在后续任务中复用、改进这些技能。所有技能默认存放在 **`~/.hermes/skills/`**（单一事实来源）；新安装时内置（bundled）技能会从仓库拷贝到该目录。

## 7.2 SKILL.md 格式标准

每个技能目录的核心是 `SKILL.md`，它由 **YAML frontmatter（元数据头）** 与正文组成。frontmatter 标准字段（官方 `creating-skills.md`）：

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]        # 可选——限定 OS 平台，省略则全平台加载
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]     # 可选——仅当这些工具集激活时展示
    requires_tools: [web_search] # 可选——仅当这些工具可用时展示
    fallback_for_toolsets: [browser]  # 可选——这些工具集激活时隐藏
    config:                      # 可选——技能需要的 config.yaml 设置
      - key: my.setting
        description: "What this setting controls"
        default: "sensible-default"
        prompt: "Display prompt for setup"
    blueprint:                   # 可选——标记为可运行的自动化
      schedule: "0 9 * * *"
      deliver: origin
      prompt: "Task instruction for each run"
required_environment_variables:  # 可选——技能所需环境变量
  - name: MY_API_KEY
    prompt: "Enter your API key"
    help: "Get one at https://example.com"
    required_for: "API access"
---

# Skill Title

Brief intro.

## When to Use
触发条件——何时加载此技能

## Quick Reference
常用命令或 API 调用速查表

## Procedure
agent 遵循的分步指令

## Pitfalls
已知失败模式与处理方式

## Verification
agent 如何确认成功
```

> 上例的注释为中文说明，实际技能文件用英文。frontmatter 中的 `metadata.hermes` 结构支持条件激活、回退（fallback）、配置声明与 blueprint（自动化蓝图）等高级特性。

## 7.3 技能分类：bundled 与 optional

技能按来源/受众分为两类：

- **内置技能（bundled skills）**：随 Hermes 发行、从仓库播种到 `~/.hermes/skills/` 的技能，官方 `skills-catalog.md` 按类别（apple、autonomous-ai-agents、creative、web 等）列出完整目录
- **可选/小众技能（optional skills）**：不在默认内置集内、面向小众需求的技能（对应仓库 `optional-skills/` 目录）

内置技能在 `hermes update` 时同步，但同步清单尊重本地删除与用户编辑——若某内置技能缺失，可用 `hermes skills reset <name> --restore` 恢复。

## 7.4 技能中心（skills hub）

**技能中心（Skills Hub）** 是安装第三方技能的统一入口，`~/.hermes/skills/.hub/` 保存其状态（如 `lock.json` 记录锁定依赖）。通过 hub 可从 URL 或 GitHub 安装技能，这些技能同样落入 `~/.hermes/skills/`。

**技能即斜杠命令**：每个已安装技能自动作为斜杠命令可用，例如 `/github-pr-workflow`。也支持在一条命令内**堆叠多个技能**（stacking）。

技能还支持**技能包（skill bundles）**——一组技能的 YAML 别名，用 `--skill` 一次加载多个；bundle 只是别名，不替你安装技能，缺失的技能会被跳过而非报错。

**外部技能目录**：可通过配置扫描 `external_dirs`（如共享的 `~/.agents/skills/`），让 Hermes 复用其他 AI 工具维护的技能。

## 7.5 curator 技能生命周期

**curator（策展器）** 是后台维护进程，负责管理 agent 自动创建的技能，防止它们无限堆积。它在以下条件下运行并执行维护：

- **自动状态转换（确定性，无需 LLM）**：技能按使用情况在 `active → stale → archived` 状态间流转——闲置超过 `stale_after_days`（默认 30）标记 `stale`，闲置超过 `archive_after_days`（默认 90）移入 `~/.hermes/skills/.archive/`
- **LLM 驱动的整合（默认关闭）**：`curator.consolidate: true` 时，用辅助模型评审，提出合并重叠技能、构建"伞形"技能的方案；按需用 `hermes curator run --consolidate` 执行
- **固定（pin）与任务引用保护**：被 pin 的技能或被任何 cron 任务引用的技能，自动状态转换一律跳过

**curator 命令**：

```bash
hermes curator pin <skill>       # 永不自动转换
hermes curator restore <skill>   # 将归档技能移回活跃
hermes curator list-archived     # 列出归档技能
hermes curator prune [--days N]  # 批量归档闲置 >= N 天的 agent 技能
```

curator 只管理**显式标记为 agent 创建**的技能（其 `.usage.json` 含 `created_by: agent` 或 `agent_created: true`）。每次真正执行前，Hermes 会先对 `~/.hermes/skills/` 做 tar.gz 快照以便回滚。

## 7.6 agent 管理技能（skill_manage）

agent 通过 `skill_manage` 工具创建/修改技能，动作包括 `patch`、`edit`、`write_file`、`remove_file`、`delete` 等。写入受 `skills.write_approval` 门控：可要求对 agent 创建技能加审（guard），未批准的写入暂存于 `~/.hermes/pending/skills/`，重启后仍保留。

## 7.7 技能与工具/记忆的分工

| 机制 | 类型 | 承载内容 |
|------|------|----------|
| 工具（tool） | 可执行函数 | 原子操作（读文件、搜索、执行命令） |
| 技能（skill） | 过程记忆 | 多步任务流程（frontmatter + 步骤正文） |
| 记忆（memory） | 事实记忆 | MEMORY.md/USER.md 的持久事实与偏好 |

技能位于 Footprint Ladder 的第 2 级（CLI 命令 + skill）：许多新能力以"CLI 命令 + 引导它的技能"形式交付，模型零足迹。

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [06 工具与工具集](./06-tools-toolsets.md) | [README](./README.md) | [08 记忆系统](./08-memory.md) |
