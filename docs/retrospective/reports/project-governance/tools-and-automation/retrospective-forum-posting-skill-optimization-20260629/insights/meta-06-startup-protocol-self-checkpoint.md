---
id: "meta-startup-protocol-self-checkpoint"
source: "../insight-extraction.md#发现11启动协议缺少完成自检检查点"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/meta-06-startup-protocol-self-checkpoint.toml"
---
# Meta洞察6：启动协议缺少"完成自检"检查点导致跳步

→ 落地措施：AGENTS.md启动协议增加步骤3.5（自检清单）

## 事实

AGENTS.md启动协议原列出了步骤1-4（读AGENTS.md→按路由表确定规范→读取规范→执行任务），但没有步骤5"自检"——即加载Skill/开始生成前，确认"我是否已经读完了所有相关规范？"

## 后果

步骤执行容易"跳步"或"浅尝辄止"：
- 读了AGENTS.md但没有认真匹配路由表
- 读了路由表但只选了最明显的入口而忽略了vendor资产
- 读了规范但没理解到位就急于开始工作

这也是为什么即使读了AGENTS.md，仍然会发生路由违规——缺少一个"停下来确认"的检查点。

## 落地措施：步骤3.5自检

在步骤4（加载Skill执行任务）之前，增加结构化自检问题清单，逐项确认：

```
步骤3.5（自检·必做）：加载Skill或开始生成产出物之前，逐项确认：
  □ 当前任务类型是否命中vendor方法论资产？如命中，对应规范是否已读取？
  □ 是否已读取上下文路由表中所有与当前任务直接相关的入口？
  □ 是否有相关Skill应被加载？（禁止在无Skill指导下手动操作有对应Skill的领域）
```

## Why解释

> **为什么需要自检？** 读完规范≠理解到位≠无遗漏。自检是一个强制"停下来盘点"的检查点，防止"读了但没进脑子"的浅阅读。就像飞机起飞前的检查清单——不是怀疑飞行员能力，而是用结构性机制防止人为疏漏。

## 关联洞察

- [meta-05-availability-heuristic-structural-guard.md](meta-05-availability-heuristic-structural-guard.md) — 自检是对抗认知偏差的结构性机制
- [meta-02-nonlinear-correction-cost.md](meta-02-nonlinear-correction-cost.md) — 5分钟自检避免30分钟返工

---
*来源：[forum-posting Skill优化复盘](../README.md)*
