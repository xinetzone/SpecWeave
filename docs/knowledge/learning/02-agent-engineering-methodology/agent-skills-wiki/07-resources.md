---
id: "agent-skills-resources"
title: "延伸学习资源"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/agent-skills-wiki/07-resources.toml"
summary: "Google工程实践文档、Addy Osmani著作、《Software Engineering at Google》书籍、Andrej Karpathy相关项目等延伸学习资源。"
---
# 延伸学习资源

## 资源1：Google工程实践文档（Google Engineering Practices Documentation）

- **类型**：官方文档
- **获取途径**：https://google.github.io/eng-practices/
- **核心学习价值**：
  - Agent Skills中很多理念（代码评审标准、测试金字塔、基于主干开发）都直接来自Google的工程实践
  - 这份文档是Google公开的官方工程规范，包含两大部分：
    1. **代码评审指南**：评审什么、怎么评审、评审速度标准、变更大小建议、怎么写评审意见——对应code-review-and-quality技能
    2. **测试指南**：测试金字塔、测试大小（小/中/大测试）、Beyonce规则、测试覆盖率的正确理解——对应test-driven-development技能
  - 这是Agent Skills背后"为什么这么设计"的源头文档，读了能理解每个实践背后的工程逻辑，而不只是记住"要这么做"

---

## 资源2：Addy Osmani的其他著作——《Learning JavaScript Design Patterns》《Patterns.dev》

- **类型**：开源书籍/博客
- **获取途径**：
  - 《Learning JavaScript Design Patterns》：https://www.patterns.dev/posts/classic-design-patterns/
  - 《Patterns.dev》（现代Web设计模式）：https://www.patterns.dev/
  - Addy Osmani个人博客：https://addyosmani.com/blog/
- **核心学习价值**：
  - Addy Osmani是Google Chrome团队的资深工程师，写了大量工程实践相关的经典著作
  - 《Patterns.dev》覆盖现代Web应用的设计模式、性能优化、组件架构、渲染策略——对应frontend-ui-engineering和performance-optimization技能
  - 他的博客有大量关于代码质量、开发流程、AI辅助编程的文章，可以跟踪他对Agent Skills的后续更新和补充思考
  - 理解他的整体工程思想，能更好地理解Agent Skills中每个设计决策的权衡

---

## 资源3：《Software Engineering at Google》（Google软件工程）

- **类型**：书籍
- **获取途径**：O'Reilly出版，中文译名《Google软件工程》，纸质书/电子书均可获取
- **核心学习价值**：
  - 这本书是Google软件工程文化的集大成之作，由Google多名资深工程师合著
  - 深入讲解了：Hyrum定律（专门有一章）、为什么代码评审是这样的流程、测试为什么按金字塔分层、基于主干开发的权衡、代码即负债的理念、文档和ADR的价值——Agent Skills中几乎所有Google文化术语在这本书里都有详细阐述
  - 特别推荐章节：
    - 第2章：How to Work Well on Teams（团队协作）
    - 第7章：Code Review（代码评审）
    - 第8章：Testing（测试）
    - 第11章：Documentation（文档）
    - 第14章：Deprecation（废弃）——对应deprecation-and-migration技能
  - 读完这本书能从"知道Google怎么做"升级到"理解Google为什么这么做"

---

## 资源4：Andrej Karpathy的LLM编程观察与相关项目

- **类型**：博客/开源项目
- **获取途径**：
  - Andrej Karpathy X（原Twitter）账号：https://x.com/karpathy
  - 相关项目：https://github.com/forrestchang/andrej-karpathy-skills（Karpathy的LLM编程准则）
  - SpecWeave的AI编码行为准则就是基于他的观察整理的
- **核心学习价值**：
  - Agent Skills的核心洞察——"AI会走最短路径跳过关键环节"——与Karpathy对LLM编程陷阱的观察高度一致
  - 他提出的"给验收标准而非步骤"、"测试驱动让AI循环迭代"等理念，在Agent Skills中都有体现
  - 对比学习Karpathy的准则和Agent Skills的20个技能，能更好地理解AI编程的共性问题和不同的解决方案侧重点
  - SpecWeave已经整合了Karpathy的准则，可以对比两个体系的异同，思考如何将Agent Skills的内容也整合到SpecWeave中

---

**上一章**：[06 - 潜在应用场景](06-application-scenarios.md)
