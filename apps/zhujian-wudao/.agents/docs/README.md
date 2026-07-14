# 竹简悟道 - 文档体系索引

本目录是竹简悟道项目的设计文档、洞察库、复盘报告和知识资产存放目录。文档按职责分层组织，遵循原子化原则（单一职责、独立可读、<=600行）。

## 目录结构

```
docs/
├── README.md                          ← 本文档
├── product/                           ← 产品规格
│   └── 2026-06-17-product-spec.md
├── insights/                          ← 洞察库（68条编号洞察，按四层分类）
│   ├── _index.md                      ← 洞察库索引
│   ├── product-layer/                 ← 产品层：定位、用户价值、功能设计
│   ├── architecture-layer/            ← 架构层：技术架构、交互设计、命名
│   ├── philosophy-layer/              ← 哲学层：帛书概念、体道四法
│   └── meta-layer/                    ← 元层：项目方法论、场景拓展、风险合规
├── reviews/                           ← 复盘与分析
│   ├── _index.md                      ← 复盘文档索引
│   ├── retrospectives/                ← 过程复盘（滚动审计、迭代记录）
│   ├── analysis/                      ← 深度分析（方法论反思、第一性原理）
│   └── history/                       ← 历史归档（旧版结构对比等）
└── knowledge-transfer/                ← 可迁移知识资产
    ├── 2026-06-17-transferable-methods.md   ← 面向人类读者的方法论（16章）
    └── 2026-06-17-transferable-patterns.md  ← 面向AI Agent的模板与模式
```

## 文件清单

| 分类 | 文件 | 用途 | 行数 |
|------|------|------|------|
| product/ | [2026-06-17-product-spec.md](product/2026-06-17-product-spec.md) | 产品规格文档（定位/功能/交互/内容体系） | 314 |
| insights/product-layer/ | [2026-06-17-insights-01-15.md](insights/product-layer/2026-06-17-insights-01-15.md) | 产品层洞察 1-15 | 194 |
| insights/architecture-layer/ | [2026-06-17-insights-16-30.md](insights/architecture-layer/2026-06-17-insights-16-30.md) | 架构层洞察 16-30 | 214 |
| insights/philosophy-layer/ | [2026-06-17-insights-31-40.md](insights/philosophy-layer/2026-06-17-insights-31-40.md) | 哲学层洞察 31-40（帛书核心概念） | 178 |
| insights/philosophy-layer/ | [2026-06-17-insights-41-48.md](insights/philosophy-layer/2026-06-17-insights-41-48.md) | 哲学层洞察 41-48（实践与架构） | 142 |
| insights/philosophy-layer/ | [2026-06-17-insights-49.md](insights/philosophy-layer/2026-06-17-insights-49.md) | 哲学层洞察 49（虚静内观操作手册） | 404 |
| insights/philosophy-layer/ | [2026-06-17-insights-51-52.md](insights/philosophy-layer/2026-06-17-insights-51-52.md) | 哲学层洞察 51-52（自然无为+生活实践操作手册） | 452 |
| insights/philosophy-layer/ | [2026-06-17-insights-53.md](insights/philosophy-layer/2026-06-17-insights-53.md) | 哲学层洞察 53（每日一问习惯引擎） | 157 |
| insights/meta-layer/ | [2026-06-17-insights-50-54-58.md](insights/meta-layer/2026-06-17-insights-50-54-58.md) | 元层洞察 50/54-58（前台视图/UX法则/文档熵增/元分析） | 537 |
| insights/meta-layer/ | [2026-06-17-insights-59-62.md](insights/meta-layer/2026-06-17-insights-59-62.md) | 元层洞察 59-62（困境映射/合规/竞争） | 466 |
| insights/meta-layer/ | [2026-06-17-insights-63-65.md](insights/meta-layer/2026-06-17-insights-63-65.md) | 元层洞察 63-65（定位解缚/反效率/决策方法论） | 579 |
| insights/meta-layer/ | [2026-06-17-insights-66-68.md](insights/meta-layer/2026-06-17-insights-66-68.md) | 元层洞察 66-68（柔弱不争/留存/睡前静心） | 245 |
| reviews/retrospectives/ | [2026-06-17-project-review.md](reviews/retrospectives/2026-06-17-project-review.md) | 项目全面复盘（18轮滚动审计+P0-P3优先级） | 403 |
| reviews/retrospectives/ | [2026-06-17-registration-review.md](reviews/retrospectives/2026-06-17-registration-review.md) | 报名流程专项复盘 | 180 |
| reviews/analysis/ | [2026-07-14-first-principles-review.md](reviews/analysis/2026-07-14-first-principles-review.md) | 第一性原理复盘评审（理想态分析+迁移方法论） | 233 |
| reviews/history/ | [2026-06-26-restructure-comparison.md](reviews/history/2026-06-26-restructure-comparison.md) | 2026-06-26 文档重组对比报告（归档） | 82 |
| knowledge-transfer/ | [2026-06-17-transferable-methods.md](knowledge-transfer/2026-06-17-transferable-methods.md) | 可迁移方法论（16章，面向人类读者） | 557 |
| knowledge-transfer/ | [2026-06-17-transferable-patterns.md](knowledge-transfer/2026-06-17-transferable-patterns.md) | 可复用模板集（面向AI Agent） | 305 |

> *标注行数超过600行的文件为系统化操作手册，符合原子化规范的豁免条件（操作手册需保持内容完整性）。

## 快速查找

| 需求 | 对应文件 |
|------|---------|
| 了解产品定位与核心功能 | [product/2026-06-17-product-spec.md](product/2026-06-17-product-spec.md) |
| 浏览洞察库（按主题） | [insights/_index.md](insights/_index.md) |
| 回顾项目历程与审计发现 | [reviews/retrospectives/2026-06-17-project-review.md](reviews/retrospectives/2026-06-17-project-review.md) |
| 查看第一性原理深度分析 | [reviews/analysis/2026-07-14-first-principles-review.md](reviews/analysis/2026-07-14-first-principles-review.md) |
| 学习可迁移方法论 | [knowledge-transfer/2026-06-17-transferable-methods.md](knowledge-transfer/2026-06-17-transferable-methods.md) |
| 获取AI Agent可复用模板 | [knowledge-transfer/2026-06-17-transferable-patterns.md](knowledge-transfer/2026-06-17-transferable-patterns.md) |
| 查看文档重组历史 | [reviews/history/2026-06-26-restructure-comparison.md](reviews/history/2026-06-26-restructure-comparison.md) |

## 新增文档归类指南

| 目录 | 存放内容 |
|------|---------|
| product/ | 产品规格、功能设计、交互设计、PRD |
| insights/ | 洞察库、经验总结、问题发现、认知升级 |
| reviews/retrospectives/ | 滚动复盘报告、迭代回顾、过程审计 |
| reviews/analysis/ | 方法论深度分析、第一性原理评审 |
| reviews/history/ | 已归档的历史文档 |
| knowledge-transfer/ | 可迁移方法论、模板集、模式库、最佳实践 |

文件命名规范：`YYYY-MM-DD-{类型}-{主题/序号}.md`。

## 重构日志

- **2026-07-14**：七概念重构——洞察库四层原子化拆分（8个原子文件）、reviews/三子目录重组、内容去重（可迁移方法论统一沉淀至transferable-methods.md）、project-review洞察列表精简为索引表
- **2026-06-26**：首次重组——从平铺结构调整为4分类（product/insights/reviews/knowledge-transfer）
