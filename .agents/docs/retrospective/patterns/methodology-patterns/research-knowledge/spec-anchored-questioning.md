---
id: "spec-anchored-questioning"
domain: "methodology"
layer: "methodology"
title: "Spec锚定提问法（Spec-Anchored Questioning）"
maturity: "L1"
maturity_level: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
version: "1.0.0"
created_date: "2026-07-10"
last_updated: "2026-07-10"
source: "retrospective-adversarial-review-questions-20260710"
analysis_date: "2026-07-10"
tags: ["spec-anchored", "questioning", "knowledge-audit", "quality-assurance", "adversarial-review", "first-principles"]
trigger_conditions:
  - "知识库构建完成后需要进行质量审计"
  - "需要生成深度开放性问题以检验知识库的假设和边界"
  - "对抗性审查协议执行后需要补充目标一致性审查"
  - "知识库spec.md存在可用的FR/NFR/AC条款"
problem_solved: "知识库质量审计中常见的'泛泛而问'问题——审计者提出'这个知识库好不好''内容是否完整'等空泛问题，无法追溯到具体的设计承诺。Spec锚定提问法以spec.md的FR/NFR/AC条款为锚点，将每个问题绑定到具体的功能需求、质量要求或验收标准上，使得审计提问具有可追溯性、可验证性和系统性。"
related_patterns:
  - "adversarial-review-protocol"
  - "five-layer-progressive-analysis"
  - "credibility-dual-track"
---
> **来源**: 从 `retrospective-adversarial-review-questions-20260710` 任务提炼，基于对对抗性审查知识库的10个深度开放性问题生成实践

# Spec锚定提问法（Spec-Anchored Questioning）

## 模式类型

方法论模式（研究知识/质量审计/提问框架）

## 成熟度

L1 实验级（validation_count=1）：
1. 首次验证：对抗性审查知识库开放性提问任务（10个问题，5层结构，覆盖7个FR/5个NFR/8个AC）

## 适用场景

- 知识库构建完成后，需要对其进行系统性质量审计
- 需要检验知识库是否真正满足spec.md中承诺的功能需求和质量目标
- 对抗性审查五维验证完成后，需要补充"目标一致性"维度的审查
- 团队内部或外部评审需要结构化的提问框架

## 问题描述

知识库质量审计中的一个常见问题是"泛泛而问"——审计者倾向于提出"这个知识库好不好""内容是否完整""方法论是否合理"等空泛问题。这类问题有两个致命缺陷：

1. **不可追溯**：无法追溯到spec.md中的具体承诺，被审计者不知道"你在质疑哪个设计决策"
2. **不可验证**：没有明确的判断标准，回答者无法给出"是/否"或"在什么条件下成立"的结论

## 解决方案

### 核心思想

以spec.md的FR（功能需求）、NFR（非功能需求/质量要求）、AC（验收标准）条款为锚点，逐条生成深度问题。每个问题必须明确标注其锚定的spec条款。

### 操作步骤

```
步骤1：读取spec.md，提取所有FR/NFR/AC条款
步骤2：逐条审查每个条款，追问：
  - 这个条款的假设是否成立？（认识论层）
  - 这个条款与其他条款是否一致？（方法论层）
  - 这个条款的执行是否引入了新的偏差？（偏差层）
  - 这个条款在工程上是否可执行？（实践层）
  - 这个条款在什么条件下会失效？（边界层）
步骤3：将问题归类为五层递进结构（认识论→方法论→偏差→实践→边界）
步骤4：输出问题总览表，每问标注锚定条款和所属层次
```

### 正例

```markdown
## 问题3：两大应用分支的深层统一性

**锚定条款**: FR-6 "两大场景方法论"
**所属层次**: 方法论张力层

方法论框架将对抗性审查分为两大场景：知识研究（七模块协议）和AI协作/代码（多Agent对抗模式）。
这两大分支在操作层面差异显著——前者是静态的、文档驱动的，后者是动态的、交互驱动的。

**探究方向**：这两大分支是否共享足够深层的统一原理，以至于可以被合理地归入同一个方法论范畴？
还是说，它们只是因"对抗性"这个标签而被松散地关联在一起？
```

### 反例

```markdown
## 问题：这个知识库的对抗性审查方法好不好用？

**问题**：这句话没有锚定任何spec条款，被审计者无法知道"你在质疑什么"。
**改进**：改为"FR-6承诺两大场景方法论均完整覆盖，但00-adversarial-review-protocol.md只覆盖了知识研究场景。
AI协作/代码场景的方法论是否在所有相关文档中得到了同等程度的覆盖？"
```

## 适用边界

- **适用**：基于spec.md构建的知识库项目，spec.md包含明确的FR/NFR/AC条款
- **不适用**：无spec.md的临时性文档或非结构化笔记；FR/NFR/AC条款过于模糊或仅包含"TODO"占位符的项目
- **与对抗性审查协议的关系**：五维验证检查"来源是否可信"，Spec锚定提问检查"目标是否合理"——两者互补，建议在五维验证后执行

## 与其他模式的组合

| 组合模式 | 说明 |
|---------|------|
| + `five-layer-progressive-analysis` | 用五层递进结构组织锚定问题，形成从"为什么"到"何时失效"的完整追问链 |
| + `adversarial-review-protocol` | 五维验证（来源可信度）→ Spec锚定提问（目标一致性），构成完整的六维审查 |
| + `credibility-dual-track` | 对Spec锚定提问发现的"目标不符"问题，用可信度评分验证其严重程度 |

---

*本模式版本：v1.0.0 | 创建日期：2026-07-10 | 来源：INSIGHT-1*