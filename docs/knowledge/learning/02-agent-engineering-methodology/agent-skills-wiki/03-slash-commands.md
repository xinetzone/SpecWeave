---
id: "agent-skills-slash-commands"
title: "7个触发命令机制"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/agent-skills-wiki/03-slash-commands.toml"
summary: "斜杠命令是用户与Agent Skills交互的入口，每个命令对应一个或多个技能，通过简洁口诀传递核心理念，作为阶段转换的显式信号。"
---
# 7个触发命令机制

斜杠命令是用户与Agent Skills交互的入口，每个命令对应一个或多个技能，通过简洁的口诀传递核心理念。

| 命令 | 关联技能 | 核心理念解读 | 设计机制 |
|------|---------|------------|---------|
| `/spec` | idea-refine + spec-driven-development | **先写需求再写代码**——对抗"拿到需求就编码"的本能 | 强制在写代码前先输出结构化的需求文档，明确目标、边界、验收标准，作为后续所有工作的契约 |
| `/plan` | planning-and-task-breakdown | **小的原子化任务**——大任务不可控，小任务可验证 | 强制将spec拆解为可独立完成、可独立验证的原子任务，每个任务大小控制在100行代码以内，明确依赖顺序 |
| `/build` | incremental-implementation + TDD + source-driven + 前端/API设计 | **一次只做一块**——薄垂直切片，做完一块验证一块 | 按照plan的顺序，每次只实现一个原子任务，严格遵循TDD红-绿-重构，实现完立即验证，不攒大活 |
| `/test` | browser-testing-with-devtools + TDD验证部分 | **测试就是证明**——代码写完不算完，证明它能工作才算 | 强制运行时验证：不仅跑单元测试，还要在真实浏览器环境中检查DOM、网络、控制台错误、性能指标 |
| `/review` | code-review-and-quality + code-simplification + security + performance | **提高代码健康度**——代码是给人看的，顺便能运行 | 合入前强制执行五轴评审（正确性/可读性/安全性/性能/测试），发现问题分严重性标签，大变更强制拆分 |
| `/code-simplify` | code-simplification | **清晰胜过聪明**——代码是写给人维护的，不是炫技 | 在保留精确行为的前提下降低复杂度：移除不必要的抽象、拆分大文件（500行规则）、理解Chesterton栅栏不随意删除 |
| `/ship` | git-workflow + CI/CD + deprecation + docs/ADRs + shipping-launch | **越快越安全**——发布流程标准化，快不是省略步骤而是自动化重复步骤 | 执行发布全流程：原子提交→CI门禁→废弃清理→文档记录→分阶段发布→回滚预案→监控告警 |

## 设计机制本质

斜杠命令不是简单的"快捷方式"，而是**阶段转换的显式信号**——用户输入`/spec`就是明确告诉AI"现在我们在定义阶段，请用定义阶段的技能工作，不要跳到构建阶段"。

每个命令的口诀都是对该阶段核心原则的高度浓缩，通过反复使用形成肌肉记忆和思维习惯。

---

**上一章**：[02 - 20个核心技能索引](02-skills-index.md)
**下一章**：[04 - Google工程文化术语](04-google-engineering-culture.md)
