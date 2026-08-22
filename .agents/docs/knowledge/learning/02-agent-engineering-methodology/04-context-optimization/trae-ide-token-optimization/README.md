---
id: "trae-ide-token-optimization"
title: "Trae IDE Token 节省方法体系"
date: 2026-08-01
type: knowledge
source: "seven-concepts methodology knowledge沉淀: sc-20260801-token-saving-analysis"
domain: "tool-usage"
maturity: "L1-experimental"
validation_count: 1
---
# Trae IDE Token 节省方法体系

本知识库沉淀了 Trae IDE 使用过程中的 Token 节省方法，基于真实社区经验和用户实测数据提炼而成。

## 知识体系结构

| 模块 | 路径 | 内容 |
|-----|------|------|
| 原理与事实 | [01-principles/](./01-principles/README.md) | Token消耗结构、实测数据、核心原理 |
| 可复用模式 | [02-patterns/](./02-patterns/README.md) | P-T-001~P-T-005 五大节省模式详解 |
| 决策框架 | [03-decision-framework/](./03-decision-framework/README.md) | ROI优先级、快速检查清单、反模式识别 |
| 快速参考 | [04-quick-reference.md](./04-quick-reference.md) | 3分钟速查卡 |

## 核心结论

> **Trae IDE Token 消耗的核心洞察：不是让AI少写代码（输出），而是让它少读无用信息（静态配置 + 历史上下文）。**

按ROI从高到低排序的五大杠杆：
1. ✅ **勤开新对话清上下文**（0成本，减30-50%）
2. ✅ **精简AGENTS.md和规则文件**（5分钟，减20-40%）
3. ✅ **关闭不用的MCP/Skills**（1分钟，减15-30%）
4. ✅ **简单任务用轻量模型**（每次点击，简单任务省60-80%）
5. ✅ **配置输出精简规则**（5分钟，减15-25%）

## 术语表

参见 [glossary.md](./glossary.md)
