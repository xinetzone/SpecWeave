---
id: "karpathy-llm-coding-guidelines-four-principles"
title: "四条核心原则详解"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, principles, think-before-coding, simplicity, surgical-changes, goal-driven]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "四条核心原则的详细说明：编码前先思考、简约至上、精确编辑、目标驱动，包含每条原则的问题根源、具体要求和检验标准。"
source: "https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/karpathy-llm-coding-guidelines/01-four-principles.toml"
---
# 四条核心原则详解

## 原则一：编码前先思考（Think Before Coding）

> **口诀：不确定的先问别瞎猜**

### 问题根源

LLM 经常默默选择一种解释然后执行，完全不表现出任何犹豫。你让 AI「加个验证功能」，它不会问你要验证什么、严不严格，而是自己猜一个最复杂的方案，写了一大堆你根本不需要的代码。

### 核心要求

**不要假设。不要隐藏困惑。呈现权衡。**

在开始实现之前：
1. **明确说明假设** —— 如果不确定，询问而不是猜测
2. **呈现多种解释** —— 当存在歧义时，不要默默选择，列出选项让用户选
3. **适时提出异议** —— 如果存在更简单的方法，主动说出来，该推回来就推回来
4. **困惑时停下来** —— 指出不清楚的地方并要求澄清

### 检验标准

- 在开始写代码之前，是否有需要澄清的问题？
- 如果有多种理解方式，是否都列出来了？
- 如果发现更简单的方案，是否主动提出来了？

---

## 原则二：简约至上（Simplicity First）

> **口诀：代码能简短就别写长**

### 问题根源

LLM 特别容易过度设计——你要一个简单的小功能，它给你写出一整套企业级架构，附带登录认证、安全校验、流量控制。你说「能简单点吗」，它立刻砍掉大半，还来一句「当然可以！」——说明它一开始就知道不用写那么多，但就是忍不住。

### 核心要求

**用最少的代码解决问题。不要过度推测。**

对抗过度工程的倾向：
1. **没被要求的功能不写** —— 不要"顺手添加"自以为有用的额外特性
2. **只用一次的代码不建抽象层** —— 当代码第二次被复用时再考虑抽象
3. **没人要求的"灵活性"和"可配置"不加** —— YAGNI（You Aren't Gonna Need It）
4. **不可能发生的异常场景不做错误处理** —— 仅处理合理可预期的错误路径
5. **如果 200 行代码可以写成 50 行，重写它**

### 检验标准

> 一个资深工程师看了会不会说「太复杂了」？
>
> 如果会，直接砍。

---

## 原则三：精确编辑（Surgical Changes）

> **口诀：没让你改的地方别碰**

### 问题根源

你让它修一个 bug，它改完 bug 顺手把旁边的代码也重构了，变量名换了，注释删了，代码风格也按它自己的偏好改了。最后你对比改动记录，改了 30 处，其中 25 处跟你的需求毫无关系。

### 核心要求

**只碰必须碰的。只清理自己造成的混乱。**

编辑现有代码时：
1. **不要"改进"相邻的代码、注释或格式** —— 不是你的活别干
2. **不要重构没坏的东西** —— 即使你觉得可以写得更好
3. **匹配现有风格** —— 即使你更倾向于不同的写法，保持一致性更重要
4. **如果注意到无关的死代码，提一下就行** —— 不要删除它

当你的改动产生孤儿代码时：
1. **删除因你的改动而变得无用的导入/变量/函数** —— 这是你的责任
2. **不要删除预先存在的死代码** —— 除非被明确要求

### 检验标准

> 每一行修改都应该能直接追溯到用户的请求。
>
> 提交前看 diff——如果有任何一行改动跟当前任务无关，那就是改多了。

---

## 原则四：目标驱动（Goal-Driven Execution）

> **口诀：给目标别给步骤**

### 问题根源

AI 特别擅长「循环到达标为止」这件事，那就别告诉它具体步骤，直接给它验收标准让它自己跑。

告诉 AI 具体怎么做，它可能亦步亦趋但达不到最终效果；告诉它成功的标准，它会自己迭代直到成功。

### 核心要求

**定义成功标准。循环验证直到达成。**

将指令式任务转化为可验证的目标：

| 不要这样说... | 应该这样说... |
|--------------|--------------|
| "添加验证" | "为无效输入编写测试，然后让它们通过" |
| "修复 bug" | "编写重现 bug 的测试，然后让它通过" |
| "重构 X" | "确保重构前后测试都能通过" |
| "写一个函数实现 X" | "先写测试用例定义 X 的行为，然后实现让测试通过" |

对于多步骤任务，说明一个简短的计划，每一步都带上验证方式：

```
1. [步骤] → 验证: [检查标准]
2. [步骤] → 验证: [检查标准]
3. [步骤] → 验证: [检查标准]
```

### 核心洞察

> "LLM 非常擅长循环执行直到达成特定目标……不要告诉它该做什么，给它成功标准，然后看着它完成。"
> —— Andrej Karpathy

强有力的成功标准让 LLM 能够独立循环执行，你需要介入的频率就越低。弱标准（"让它工作"）需要不断澄清。

这是用 AI 编程时杠杆最大的一条原则。

---

## 如何判断它在起作用

如果你看到以下情况，说明这些指南正在发挥作用：

| 现象 | 对应原则 |
|------|---------|
| diff 中不必要的改动更少 | 原则三：精确编辑 |
| 因过度复杂而导致的重写更少 | 原则二：简约至上 |
| 澄清问题在实现之前提出（而不是犯错之后） | 原则一：编码前思考 |
| 干净、精简的 PR，没有顺带的重构或"改进" | 原则三：精确编辑 |
| AI 能独立工作更长时间，不需要频繁介入 | 原则四：目标驱动 |

---

## 权衡说明

这些指南倾向于 **谨慎而非速度**。

对于琐碎的任务（简单的拼写错误修复、显而易见的一行修改），请自行判断——并非每个改动都需要完整的严谨流程。

**目标是减少非琐碎工作中的代价高昂的错误，而不是拖慢简单任务。**

---

## CLAUDE.md 原文

````markdown
# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
````
