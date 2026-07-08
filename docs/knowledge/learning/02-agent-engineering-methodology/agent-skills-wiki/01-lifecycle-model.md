---
id: "agent-skills-lifecycle-model"
title: "六阶段生命周期模型详解"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/agent-skills-wiki/01-lifecycle-model.toml"
summary: "Agent Skills将软件开发生命周期划分为Define→Plan→Build→Verify→Review→Ship六个顺序阶段，用结构化工作流对抗AI的最短路径谬误。"
---
# 六阶段生命周期模型详解

Agent Skills 将软件开发生命周期划分为 **Define（定义）→ Plan（规划）→ Build（构建）→ Verify（验证）→ Review（评审）→ Ship（发布）** 六个顺序阶段。

| 阶段 | 核心问题 | 为什么必须在这个位置 | 设计意图 |
|------|---------|-------------------|---------|
| **Define（定义）** | "要解决什么问题？为什么做？成功标准是什么？" | 最开始——如果目标错了，后面所有工作都是浪费 | 对抗AI"拿到需求就写代码"的本能，强制先澄清问题边界、用户价值、验收标准，避免构建错误的东西 |
| **Plan（规划）** | "怎么拆解任务？先做什么后做什么？依赖关系是什么？" | 定义之后，构建之前——没有规划就动手是返工的根源 | 强制AI将大需求拆解为原子化、可独立验证的小任务，明确每个任务的验收标准和依赖顺序，避免"大爆炸式"开发 |
| **Build（构建）** | "怎么按正确的工程实践实现？" | 规划之后——这是产生代码的阶段，但必须有前置约束 | 强制采用增量式实现、TDD、基于官方文档决策、组件化架构、契约优先API设计，避免一次性写大段无测试代码 |
| **Verify（验证）** | "它真的能工作吗？在浏览器里表现如何？出问题怎么定位？" | 构建之后——代码写完不等于完成，必须证明它能工作 | 强制运行时验证（Chrome DevTools检查DOM/网络/性能）和系统化调试，而不是"看起来没报错就算了" |
| **Review（评审）** | "代码质量怎么样？有没有安全漏洞？能不能简化？性能如何？" | 验证之后，合并之前——质量门禁必须在合入主干前执行 | 强制代码评审五轴检查、安全加固、复杂度简化、性能优化，防止技术债务积累 |
| **Ship（发布）** | "怎么安全上线？出问题怎么回滚？以后怎么维护？" | 最后——发布不是终点，而是运维的起点 | 强制Git工作流规范、CI/CD质量门禁、废弃代码清理、文档/ADR记录、分阶段发布+回滚预案 |

## 顺序的必然性

这个顺序严格遵循"**先想清楚再动手，先验证再合入，先准备回滚再上线**"的工程原则。

AI天然倾向于跳过前两个阶段直接写代码，再跳过验证评审直接"完成"——六阶段模型就是用结构化工作流对抗这种"最短路径谬误"。

---

**下一章**：[02 - 20个核心技能索引](02-skills-index.md)
