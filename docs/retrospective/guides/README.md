---
title: 通用指南索引
date: 2026-07-31
type: guides-index
tags:
  - 指南
  - 索引
---

# 通用指南（Guides）

> 本目录存放面向新成员和团队成员的通用培训指南、Checklist、考核题、策略对比等文档。按主题分子目录组织，与具体里程碑复盘报告（reports/）和可复用模式（patterns/）分离。

---

## 目录导航

| 主题 | 目录 | 内容 |
|------|------|------|
| 代码优化 | [code-optimization/](code-optimization/README.md) | 代码优化安全入门指南、反模式Checklist、考核题、策略对比表、方法论验证 |

---

## 与其他目录的关系

```
retrospective/
├── guides/          ← 你在这里：通用指南、培训材料、Checklist
│   └── code-optimization/
├── reports/         ← 具体里程碑复盘报告（每次任务的完整记录）
├── patterns/        ← 可复用模式（代码模式/方法论模式，跨项目复用）
├── frameworks/      ← 决策框架与矩阵
└── assets/          ← 共享资产清单
```

**使用建议**：
- 新成员入门 → 先看 `guides/` 下对应主题的入门指南
- 做具体任务 → 参考 `reports/` 下同类里程碑复盘报告
- 沉淀方法论 → 萃取到 `patterns/` 对应目录

---

## Changelog

<!-- changelog -->
- 2026-07-31 | feat | 初始版本，guides目录创建，code-optimization子目录从reports/迁移
