---
title: "Agent Skills 开放标准完整指南"
category: "learning"
tags: ["agent-skills", "skills", "open-standard", "specification", "ai-agent", "skill-development", "progressive-disclosure", "skills-ref", "client-implementation", "skill-evals"]
date: "2026-07-02"
version: "1.2"
status: "stable"
author: ""
summary: "基于 agentskills.io 官方完整教程（快速入门/最佳实践/描述优化/质量评估/脚本使用/客户端实现）和 .temp/libs/agentskills 源码深度核实的 Agent Skills 开放标准完整指南。覆盖目录结构、SKILL.md格式规范、渐进式披露机制、自包含脚本设计、触发准确率优化、评估驱动迭代、skills-ref验证工具使用、客户端5步集成指南，以及与本项目现有Skill体系的对比分析。本文档已原子化，详细内容见 agent-skills-wiki/ 子目录。"
source: "https://agentskills.io/home"
changelog: "2026-07-02 | refactor | 文档原子化：将1510行单文件拆分为15个原子文件，遵循单一职责原则，源文件转为索引页"
---

# Agent Skills 开放标准完整指南

> 基于 agentskills.io 官方文档 + `.temp/libs/agentskills` 源码深度核实
> 创建日期：2026-07-01
> 本地源码路径：[.temp/libs/agentskills](file:///d:/spaces/SpecWeave/.temp/libs/agentskills)
> 验证工具：[skills-ref](file:///d:/spaces/SpecWeave/.temp/libs/agentskills/skills-ref)
> 核实方法：官方文档交叉验证 + skills-ref 源码（validator.py/parser.py/models.py）逐行核实

---

## 文档导航

本文档已按单一职责原则原子化为15个独立章节文件，存放于 [agent-skills-wiki/](agent-skills-wiki/) 目录：

| 序号 | 章节 | 文件 | 内容概要 |
|------|------|------|---------|
| 一 | 概述 | [00-overview.md](agent-skills-wiki/00-overview.md) | 什么是Agent Skills、为什么需要、支持的客户端（40+） |
| 二 | 核心机制：渐进式披露 | [01-progressive-disclosure.md](agent-skills-wiki/01-progressive-disclosure.md) | 三阶段加载机制：发现→激活→执行，Token预算与触发时机 |
| 三 | 目录结构规范 | [02-directory-structure.md](agent-skills-wiki/02-directory-structure.md) | 标准目录结构（SKILL.md/scripts/references/assets/evals） |
| 四 | SKILL.md 格式规范 | [03-skill-md-format.md](agent-skills-wiki/03-skill-md-format.md) | YAML frontmatter字段规范（name/description等）、正文内容规范 |
| 五 | 快速入门 | [04-quickstart.md](agent-skills-wiki/04-quickstart.md) | 创建第一个Skill（掷骰子示例）、工作原理解析 |
| 六 | 最佳实践 | [05-best-practices.md](agent-skills-wiki/05-best-practices.md) | 从真实知识出发、执行精炼、上下文使用、控制粒度、有效指令模式 |
| 七 | 脚本使用指南 | [06-scripts-guide.md](agent-skills-wiki/06-scripts-guide.md) | 一次性命令vs捆绑脚本、自包含脚本（PEP723/Deno/Bun/Ruby）、面向智能体的脚本设计 |
| 八 | 优化技能描述 | [07-description-optimization.md](agent-skills-wiki/07-description-optimization.md) | 触发工作原理、评估查询设计、触发率测试、训练/验证集拆分、优化循环 |
| 九 | 质量评估（Evals） | [08-evals.md](agent-skills-wiki/08-evals.md) | 测试用例设计、运行评估、断言编写、评分输出、迭代循环 |
| 十 | 验证工具：skills-ref | [09-skills-ref-tool.md](agent-skills-wiki/09-skills-ref-tool.md) | 安装、CLI命令（validate/read-properties/to-prompt）、Python API、验证检查清单 |
| 十一 | 文件引用规范 | [10-file-references.md](agent-skills-wiki/10-file-references.md) | 相对路径规则、引用深度建议 |
| 十二 | 与本项目对比 | [11-project-comparison.md](agent-skills-wiki/11-project-comparison.md) | 对齐情况、扩展特性、可借鉴改进点、国际化支持说明 |
| 十三 | 客户端实现指南 | [12-client-implementation.md](agent-skills-wiki/12-client-implementation.md) | 5步集成：发现技能→解析SKILL.md→披露目录→激活技能→管理上下文 |
| 十四 | 资源链接 | [13-resources.md](agent-skills-wiki/13-resources.md) | 官方资源、本地资源、本项目相关链接 |
| 十五 | 快速参考卡 | [14-quick-reference.md](agent-skills-wiki/14-quick-reference.md) | SKILL.md最小模板、验证命令速查、名称规则、检查清单 |

---

## 快速开始

### 最简示例：掷骰子 Skill

创建 `.agents/skills/roll-dice/SKILL.md`：

````markdown
---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die (d6, d20, etc.), roll dice, or generate a random dice roll.
---

To roll a die, use the following command that generates a random number from 1 to the given number of sides:

```bash
echo $((RANDOM % <sides> + 1))
```

```powershell
Get-Random -Minimum 1 -Maximum (<sides> + 1)
```

Replace `<sides>` with the number of sides on the die (e.g., 6 for a standard die, 20 for a d20).
````

### 验证命令速查

```bash
# 验证技能
skills-ref validate path/to/skill

# 查看属性
skills-ref read-properties path/to/skill

# 生成提示
skills-ref to-prompt path/to/skill
```

---

## 相关资源

- **本项目 Skills 目录**：[.agents/skills/](../../../.agents/skills/)
- **渐进式披露模式**：[progressive-context-disclosure.md](../../retrospective/patterns/methodology-patterns/ai-collaboration/progressive-context-disclosure.md)
- **Skill 五要素模型**：[skill-five-elements-model.md](../../retrospective/patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md)
- **Markdown 即接口模式**：[markdown-as-interface.md](../../retrospective/patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md)

---

## Changelog

<!-- changelog -->
- 2026-07-02 | refactor | 文档原子化：将1510行单文件拆分为15个原子文件（00-overview.md ~ 14-quick-reference.md），源文件转为索引页，遵循单一职责原则
- 2026-07-02 | docs | 补充完整客户端实现5步指南、评估工作区结构、训练/验证集拆分、Ruby自包含脚本、时间数据捕获等官方教程内容
