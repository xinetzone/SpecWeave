---
id: "docs-retrospective-reports-incident-reports-index"
title: "事件复盘报告"
category: "retrospective"
date: "2026-07-15"
---
# 事件复盘报告

本目录收录“已经发生且需要复盘归因”的事件型报告，重点记录目标未达成、决策失误、方法论失配、流程断裂等 incident 场景。

## 收录边界

| 类型 | 说明 |
|---|---|
| 纳入 | 有明确失败事件、影响描述、根因分析和后续改进动作的 incident 复盘 |
| 不纳入 | 常规任务总结、纯学习报告、无明确事件触发的项目回顾 |

## 报告索引

| 报告目录 | 事件类型 | 严重度 | 简要说明 |
|---|---|---|---|
| [retrospective-first-principles-analogy-error-20260709/README.md](retrospective-first-principles-analogy-error-20260709/README.md) | 决策错误 / 方法论践行失败 | `medium` | 将 Markdown 内链错误类比为 `file:///` 绝对路径问题，13 个文件被误改后回滚并沉淀“决策前三查”教训 |
| [retrospective-ui-beautification-failure-20260714/README.md](retrospective-ui-beautification-failure-20260714/README.md) | 目标未达成 / 方法论与任务错配 | `high` | 两轮 UI 美化均未达到用户预期，暴露“优化不等于美化”“文本 AI 缺少视觉反馈闭环”等问题 |

## 结构约定

- 事件复盘目录默认采用四文件结构：`README.md`、`execution-retrospective.md`、`insight-extraction.md`、`export-suggestions.md`。
- 若单条 incident 的洞察数量较多，可扩展 `insights/` 子目录承载原子化洞察。
- `exports/` 子目录中的派生产物不视为 incident 主体内容，引用时应与正式报告文件区分。

## 相关入口

- [返回上级：复盘报告分类索引](../README.md)
- [事件案例：第一性原理类比推理错误](retrospective-first-principles-analogy-error-20260709/README.md)
- [事件案例：UI美化持续未达预期](retrospective-ui-beautification-failure-20260714/README.md)
