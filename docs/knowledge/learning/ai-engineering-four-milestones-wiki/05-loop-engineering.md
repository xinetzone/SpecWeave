---
id: "ai-engineering-four-milestones-wiki-05-loop-engineering"
title: "第四站：Loop Engineering"
source: "https://mp.weixin.qq.com/s/eeB14yOtDU6akQUp0Mkauw"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/ai-engineering-four-milestones-wiki/05-loop-engineering.toml"
---

# 第四站：Loop Engineering

## 瓶颈移到你自己身上

假设你把 harness 修炼到家了，整条线上最后还剩一个瓶颈是谁？

**是你。**

- 模型在等你布置任务
- harness 在等你启动
- 整条链路的入口是你，出口的判断也是你

Loop Engineering 瞄准的就是这最后一环。

## 回合制→循环制

范式迁移：

| 模式 | 描述 | 特征 |
|---|---|---|
| 回合制 | 人握着 Agent：人下指令→Agent 执行→人评估→人下下一条指令 | 人是节奏的中心 |
| 循环制 | Loop 握着 Agent：人设计循环→循环自动给 Agent 下指令→Agent 执行→循环评估→循环下下一条指令 | 人设计循环，循环运行节奏 |

```
回合制：人 → Agent → 人 → Agent → 人 → ...
              ↓ 范式迁移
循环制：人 → 设计Loop → Loop ↔ Agent（自动循环）→ 人（监控与判断）
```

关键变化：**从人握着 Agent，到 loop 握着 Agent**。

## 三人同期点响

Loop Engineering 这个词几乎是同一周被三个人同时点响：

| 人物 | 身份 | 表述 |
|---|---|---|
| Peter Steinberger | OpenClaw | "你该去设计那个给 agent 打 prompt 的循环" |
| Addy Osmani | Google | 给 Loop Engineering 写了正式定义 |
| Boris Cherny | Claude Code | "我已经不 prompt Claude 了，是 loop 在运行着 prompt Claude" |

Boris Cherny 的话尤其形象：
> "我已经不 prompt Claude 了，是 loop 在运行着 prompt Claude。"

这标志着工程重心从"优化单次 prompt"转向"设计运行 prompt 的循环"。

## Loop未删除人

但 **loop 改变了你的工作，没有把你从工作里删除**。

关键认知：

### 1. Harness假设会过期

harness 编码的是"**模型此刻还做不到什么**"的假设。

```
harness编码假设 = "模型此刻做不到X"
    ↓
模型变强（现在能做到X了）
    ↓
原假设过期 → 对应的harness防护变成冗余甚至阻碍
```

### 2. 需持续修订

模型一变强，这些假设就会过期。驾驭 AI 这件事，**从来不是一劳永逸地"搭好一套"**：

- 一边盯着模型的边界变化
- 一边持续地修你那套环境
- 删除已过时的防护
- 增加对新边界的防护

### 3. 人的新角色

写代码、敲提示词这些活，会越来越多地交给 Agent。但**这两件事在很长一段时间里得是人来做**：

| 人仍需做的事 | 说明 |
|---|---|
| 设计能让 Agent 高质量产出的环境 | harness 工程的核心 |
| 对 Agent 的产出保持判断 | 质量把关、价值判断 |
| 监控模型边界变化 | 决定何时修订 harness |
| 设计运行 Agent 的循环 | loop 工程的核心 |

## 瓶颈外移走到尽头

Loop Engineering 标志着瓶颈外移主线**走到尽头**：

```
Prompt（怎么说）→ Context（给什么）→ Harness（环境）→ Loop（你自己）
                                                              ↑
                                                          瓶颈终点
```

瓶颈最终移到了人身上——但这不是终结，而是新的开始：
- 人的工作从"执行"转向"设计"
- 人的价值从"产出"转向"判断"
- 人的角色从"操作员"转向"环境设计师"与"循环设计师"

这意味着 AI 工程的演进进入新阶段：**不再是把人从循环中删除，而是让人在更高层次上参与循环**。

← 返回 [索引页](../ai-engineering-four-milestones-wiki.md) | 上一节 [04-Harness Engineering](./04-harness-engineering.md) | 下一节 [06-深度洞察与可复用方法论](./06-insights-patterns.md)
