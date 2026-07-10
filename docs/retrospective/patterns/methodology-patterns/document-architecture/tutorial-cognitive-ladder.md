---
id: "tutorial-cognitive-ladder"
domain: "methodology"
layer: "methodology"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "basic"
source: "../../../reports/competitive-analysis/retrospective-karpathy-multica-tutorial-20260702/insight-extraction.md#洞察4"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/document-architecture/tutorial-cognitive-ladder.toml"
rules: []
references: []
skills: []
related_patterns:
  -   - "progressive-readme-growth"
  -   - "triangular-source-verification"
  -   - "review-insight-export-loop"
---
# 教程认知阶梯：技术教程六层结构设计法

## 模式概述

技术教程应遵循"是什么→怎么用→在哪用→为什么"的认知路径，通过六层递进结构（概述→原则→示例→快速开始→本地整合→生态上下文），让读者在每一层都可以停下来使用，也可以一直深入到源码级理解。纯原则文档无法落地，因为读者不知道违反原则的代价和场景；加入生态上下文和最佳实践案例后，抽象准则才能被真正内化。

## 问题现象

技术教程常见的失败模式：

1. **只有原则没有案例**：读者知道"应该做什么"，但不知道"怎么做到"、"做错了会怎样"
2. **只有API文档没有上下文**：能查到函数签名，但不知道什么时候该用、什么时候不该用
3. **只有本地用法没有生态视角**：学会了工具的用法，但不理解它在更大技术图景中的位置
4. **结构混乱无递进**：概念、示例、安装、参考混在一起，读者不知道从哪开始
5. **缺乏实践锚点**：读完感觉"懂了"，但动手时还是不知道第一步做什么

这些问题的共同根因是：文档作者按"知识的逻辑结构"组织内容，而不是按"读者的认知路径"组织内容。

## 解决方案

按六层认知阶梯组织技术教程，每一层解决一个认知问题：

| 层级 | 章节命名模式 | 解决的认知问题 | 读者状态 |
|------|-------------|---------------|---------|
| L1 背景 | 00-overview | 为什么需要这个？解决什么问题？ | "我知道这个东西是干嘛的" |
| L2 核心 | 01-principles/01-core-concepts | 核心内容是什么？关键概念有哪些？ | "我理解核心思想" |
| L3 示例 | 02-examples/02-code-examples | 具体怎么用？正反案例是什么？ | "我看到正确和错误的做法" |
| L4 上手 | 03-quickstart/03-getting-started | 怎么安装？第一步做什么？ | "我能跑起来一个hello world" |
| L5 落地 | 04-integration/04-usage-in-our-project | 在我们的项目/环境中怎么用？ | "我知道怎么在实际工作中用" |
| L6 生态 | 05-ecosystem/06-platform/07-best-practices | 这个东西在什么生态中？最佳实践案例是什么？违反的代价？ | "我理解为什么要这样做，不只是怎么做" |

**关键设计原则**：

1. **每一层独立可用**：读者在任何一层停下来都能获得价值（L1了解背景、L3抄示例、L4快速上手、L6深入理解）
2. **编号强制递进**：使用两位数字前缀（00-07），让阅读顺序明确，避免跳读导致认知断层
3. **生态层回答"为什么"**：前五层回答"是什么"和"怎么用"，第六层通过真实生态中的案例和代价回答"为什么"
4. **正反例配对**：L3示例层必须同时包含❌错误做法和✅正确做法，不能只给正确答案
5. **本地整合优先**：L5落地层必须关联到读者实际使用的项目/环境，否则教程停留在"别人的东西"

```
认知深度
    ▲
    │  L6 生态上下文（为什么重要·最佳实践·违反代价）
    │  L5 本地整合（我们项目怎么用）
    │  L4 快速开始（怎么安装·第一步）
    │  L3 代码示例（正反案例）
    │  L2 核心原则（是什么）
    │  L1 概述背景（为什么需要）
    └──────────────────────────────────► 实用性
         可随时停下来                    深入源码级理解
```

## 适用场景

- ✅ 编程准则/最佳实践类教程（如Karpathy LLM编程准则）
- ✅ 开源工具/框架学习文档
- ✅ 内部技术规范推广文档
- ✅ 新技术选型评估文档
- ✅ API/SDK入门教程
- ❌ 纯参考手册（API Reference不需要按认知路径组织）
- ❌ 单一任务How-to指南（如"如何部署到生产环境"不需要六层）
- ❌ 内部SOP操作文档（面向已掌握背景知识的执行者）

## 实际案例

### 案例1：Karpathy LLM编程准则教程（本次任务）

| 层级 | 文件 | 内容 |
|------|------|------|
| L1 | 00-overview.md | Karpathy是谁、准则解决什么问题、四条原则概览 |
| L2 | 01-four-principles.md | Think Before Coding/Simplicity First/Surgical Changes/Goal-Driven详解 |
| L3 | 02-code-examples.md | 真实代码正反例（❌LLM常犯错误 vs ✅正确做法） |
| L4 | 03-quickstart.md | Claude Code/Cursor四种安装方式、配置方法 |
| L5 | 04-specweave-integration.md | 在SpecWeave项目中如何落地、对应到哪些现有规范文件 |
| L6 | 06-multica-platform.md + 07-multica-cli-skill.md | Multica平台生态、multica-cli Skill作为最佳实践案例、违反准则的真实代价（Mention循环消耗token） |

效果：读者可以只读L1-L3理解准则，也可以深入到L6理解准则在真实AI Agent协作平台中的应用，看到Surgical Changes原则如何防止Agent间无限循环。

### 案例2：WSL系统学习计划（参考先例）

WSL学习计划采用了类似结构：背景→核心概念→API参考→示例→本地整合→官方文档生态（三源验证）。

## 反模式

### 反模式1：原则先行，案例后置

把所有原则讲完再给示例，读者在阅读原则时因为缺乏具体场景而无法理解，到示例时已经遗忘前面的原则。

**正确做法**：每个原则/概念在L2讲完后，L3立即给出对应的正反案例，形成即时反馈。

### 反模式2：跳过生态层

教程在L5本地整合后就结束了，读者"会用但不理解为什么"。遇到边缘情况时无法做出正确判断，因为不理解设计背后的权衡。

**正确做法**：至少研究一个使用该技术的真实开源项目/平台，在L6展示该技术在真实生态中的表现，包括违反原则的真实代价。

### 反模式3：生态层变成产品推销

L6生态层不应该是对某个产品的宣传，而应该是客观展示技术在真实场景中的应用方式、设计权衡和常见陷阱。

**正确做法**：L6应该包含"最佳实践案例"+"常见错误"+"违反代价"三个要素，而非单一的正面宣传。

### 反模式4：编号缺失导致阅读顺序混乱

不使用数字前缀，文件按字母顺序排列，读者可能先读到高级概念再读基础概念，造成认知障碍。

**正确做法**：统一使用两位数字前缀（00-09），强制阅读顺序，同时允许读者按需跳读。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [progressive-readme-growth.md](progressive-readme-growth.md) | 互补 | 本模式关注教程类文档的认知结构，progressive-readme-growth关注README的渐进式成长 |
| [triangular-source-verification.md](../retrospective-knowledge/triangular-source-verification.md) | 前置 | L6生态层研究应使用三角验证法（源码+官方文档+社区实践三源交叉验证） |
| [review-insight-export-loop.md](../retrospective-knowledge/review-insight-export-loop.md) | 后续 | 教程完成后应通过复盘→洞察→导出闭环持续改进 |
| [dual-audience-extraction-model.md](dual-audience-extraction-model.md) | 相关 | 本模式隐含了不同层次读者（新手/进阶/专家）的双受众设计 |

## 边界与选型

**何时使用本模式**：
- 教程目标读者包含不同层次的使用者（从新手到专家）
- 技术内容有明确的原则/概念层和实践/工具层
- 期望读者不仅"会用"还要"理解"
- 教程需要长期维护（结构化设计便于后续扩展）

**何时使用简单结构即可**：
- 单一任务的How-to指南（如"如何配置CI"）→ 直接用"问题→步骤→验证"三段式
- API参考文档 → 按模块/功能组织，不需要认知递进
- 面向已掌握背景的内部团队 → 可跳过L1背景层，从L2开始
- 快速原型验证文档 → L1+L4即可（背景+快速上手）

**与其他文档模式的选择**：
- 如果是README → 用progressive-readme-growth模式
- 如果是知识库条目 → 考虑one-stop-operation-guide模式
- 如果是架构决策 → 用spec-driven-development + ADR格式
- 如果是操作SOP → 用简洁的步骤清单格式
