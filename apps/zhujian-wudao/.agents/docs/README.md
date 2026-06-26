# 竹简悟道 - 文档体系索引

## 文档体系说明

本目录是竹简悟道项目的设计文档、洞察库、复盘报告和知识资产存放目录。所有文档按类型分类存放，便于查找、维护和复用。

## 目录结构树

```
docs/
├── README.md
├── restructure-comparison.md
├── product/
│   └── 2026-06-17-product-spec.md
├── insights/
│   ├── 2026-06-17-insights-01-30.md
│   ├── 2026-06-17-insights-31-53.md
│   └── 2026-06-17-insights-54-68.md
├── reviews/
│   ├── 2026-06-17-project-review.md
│   └── 2026-06-17-registration-review.md
└── knowledge-transfer/
    ├── 2026-06-17-transferable-methods.md
    └── 2026-06-17-transferable-patterns.md
```

## 文件清单表格

| 分类 | 文件名 | 用途说明 | 行数 | 内容简介 |
|---|---|---|---|---|
| product/ | [2026-06-17-product-spec.md](product/2026-06-17-product-spec.md) | 产品规格文档 | 约314行 | 包含产品定位、核心功能、交互设计、内容体系等完整规格 |
| insights/ | [2026-06-17-insights-01-30.md](insights/2026-06-17-insights-01-30.md) | 洞察库1-30 | 约700行 | 产品层（1-15）+ 架构层（16-30）洞察 |
| insights/ | [2026-06-17-insights-31-53.md](insights/2026-06-17-insights-31-53.md) | 洞察库31-53 | 约1500行 | 哲学层·帛书核心概念与体道四法系统化手册 |
| insights/ | [2026-06-17-insights-54-68.md](insights/2026-06-17-insights-54-68.md) | 洞察库54-68 | 约1800行 | 元层·场景拓展、产品深化与柔弱不争手册补全 |
| reviews/ | [2026-06-17-project-review.md](reviews/2026-06-17-project-review.md) | 项目全面复盘报告 | 约467行 | 18轮迭代复盘、68条洞察汇总、优先级行动清单 |
| reviews/ | [2026-06-17-registration-review.md](reviews/2026-06-17-registration-review.md) | 报名流程复盘报告 | 约180行 | 比赛报名全流程复盘 |
| knowledge-transfer/ | [2026-06-17-transferable-methods.md](knowledge-transfer/2026-06-17-transferable-methods.md) | 可迁移方法论 | 约513行 | 13章面向人类读者的方法论萃取 |
| knowledge-transfer/ | [2026-06-17-transferable-patterns.md](knowledge-transfer/2026-06-17-transferable-patterns.md) | 可迁移模板集 | 约305行 | 9章面向AI Agent的模板与模式 |
| 根目录 | [restructure-comparison.md](restructure-comparison.md) | 重组对比报告 | - | 文档结构重组详细对比 |

## 快速查找表

| 需求场景 | 对应文件/目录 |
|---|---|
| 了解产品定位、核心功能 | product/2026-06-17-product-spec.md |
| 查看已有洞察、经验总结 | insights/ 目录 |
| 回顾项目历程、迭代复盘 | reviews/2026-06-17-project-review.md |
| 查看报名流程专项复盘 | reviews/2026-06-17-registration-review.md |
| 学习可迁移方法论（人类读者） | knowledge-transfer/2026-06-17-transferable-methods.md |
| 获取可复用模板（AI Agent） | knowledge-transfer/2026-06-17-transferable-patterns.md |
| 了解文档结构重组历史 | restructure-comparison.md |

## 新增文档归类指南

新增文档请按以下分类放入对应目录：

| 目录 | 存放内容类型 |
|---|---|
| product/ | 产品规格文档、功能设计文档、交互设计文档、PRD |
| insights/ | 洞察库、经验总结、问题发现、认知升级记录 |
| reviews/ | 项目复盘报告、专项流程复盘、迭代回顾、经验教训 |
| knowledge-transfer/ | 可迁移方法论、模板集、模式库、最佳实践 |

文件命名规范：`YYYY-MM-DD-{类型}-{序号/主题}.md`，例如：
- `2026-06-26-insights-69-100.md`
- `2026-06-27-product-user-system-spec.md`

> **注意**：洞察库文件按层级分文件存放（01-30产品+架构层、31-53哲学层、54-68元层），新增洞察应续接最新文件末尾或创建新文件，编号全局递增。文件行数仅供参考，随内容增长会变化（参见洞察55：文档声明的熵增定律）。

## 重组说明

本目录结构于 **2026-06-26** 完成结构重组，从原平铺式结构调整为4分类结构，大幅提升可维护性和查找效率。重组详情请参阅 [restructure-comparison.md](restructure-comparison.md)。
