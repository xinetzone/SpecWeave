---
id: "multi-product-wiki-template-readme"
title: "多产品原子化Wiki模板包使用说明"
source: "docs/retrospective/reports/competitive-analysis/retrospective-sunlogin-offline-hardware-20260704/insight-extraction.md#模式5"
x-toml-ref: "../../../.meta/toml/.agents/templates/multi-product-wiki-template/README.toml"
date: "2026-07-04"
tags: ["模板", "Wiki", "原子化", "多产品对比"]
---
# 多产品原子化Wiki模板包使用说明

本模板包基于向日葵5款无网远控硬件（控控2/Q1/Q2Pro/Q0.5/Q5Pro）和7次向日葵硬件Wiki任务迭代验证，适用于**≥3款同品类产品**的技术学习/产品分析Wiki文档。

## 适用条件（结构决策树）

根据产品数量选择结构：

```
产品数量=1? → 单文件结构（使用mdi-document-template.md）
产品数量=2? → 单文件结构（使用mdi-document-template.md，注意控制长度<800行）
产品数量=3? → 评估预计行数：>800行用本模板包，≤800行用单文件
产品数量≥5? → 必须使用本模板包（原子化11文件结构）
```

## 目录结构

```
multi-product-wiki-template/
├── README.md                    # 本说明文件
└── example-wiki/                # 原子文件目录（复制后重命名为{topic}-{type}/）
    ├── 00-overview.md           # 产品概述、产品矩阵、目录导航
    ├── 01-core-concepts.md      # 核心概念解析
    ├── 02-product-{p1}.md       # 产品1详解
    ├── 03-product-{p2}.md       # 产品2详解
    ├── ...                      # 根据产品数量增减
    ├── NN-comparison.md         # 横向对比分析（产品数+2）
    ├── NN-technology.md         # 核心功能与工作原理
    ├── NN-usage-guide.md        # 使用流程与操作指南
    ├── NN-scenarios.md          # 典型应用场景
    ├── NN-market-strategy.md    # 市场定位与产品策略
    ├── NN-faq.md                # FAQ
    └── NN-resources.md          # 相关资源链接
```

## 快速开始（4步）

1. **复制模板目录**：复制 `example-wiki/` 到目标目录，重命名为 `{topic}-{type}/`（kebab-case英文）
2. **根据产品数量增删产品章节**：N款产品对应N个 `0X-product-{name}.md` 文件
3. **全局替换占位符**：
   - `{{WikiID}}` → 实际wiki ID（kebab-case英文，如`sunlogin-offline-hardware`）
   - `{{Wiki标题}}` → 实际中文标题（如"向日葵五款无网远控硬件深度解析"）
   - `{{来源路径}}` → 溯源路径（如`task-execution`或来源URL）
   - `{{产品1}}`~`{{产品N}}` → 实际产品名称
   - `{{YYYY-MM-DD}}` → 当前日期
   - `{{标签列表}}` → 实际标签
4. **计算x-toml-ref路径**：根据实际目标目录层级调整TOML引用路径

## 章节文件命名规则

| 文件名 | 内容 | 必要性 |
|--------|------|--------|
| `00-overview.md` | 产品概述、产品矩阵一览表、目录导航 | 必须 |
| `01-core-concepts.md` | 核心技术概念解析 | 必须 |
| `02-product-{name}.md` | 各产品详解（定位/设计/规格/功能/适用人群） | 必须（每款产品一个） |
| `{N+1}-comparison.md` | 核心参数横向对比表、相同点/差异点、选型指南 | 多产品时必须 |
| `{N+2}-technology.md` | 技术原理深度解析、通信链路、关键技术 | 必须 |
| `{N+3}-usage-guide.md` | 操作指南、设置流程、排障 | 推荐 |
| `{N+4}-scenarios.md` | 典型应用场景（痛点→方案→流程→价值） | 必须 |
| `{N+5}-market-strategy.md` | 用户画像、定价策略、产品矩阵、商业模式 | 洞察类必须 |
| `{N+6}-design-insights.md` | 设计哲学、技术取舍、UX亮点（可选） | 推荐 |
| `{N+7}-industry-trends.md` | 行业趋势、技术演进（可选） | 可选 |
| `{N+8}-faq.md` | 购买前/使用中/故障时FAQ | 必须 |
| `{N+9}-resources.md` | 官方链接、App下载、帮助中心、评测视频 | 必须 |

> **注**：N=产品数量。文件序号需连续，若跳过可选章节则相应调整后续编号。

## 产品详解章统一结构

每个 `0X-product-{name}.md` 文件必须包含以下统一章节：

1. **产品定位**：一句话说明是什么、面向谁、解决什么问题
2. **外观设计**：形态、材质、颜色、接口、指示灯、按键
3. **技术规格**：表格形式列出核心参数
4. **核心功能**：3-5个核心功能点（是什么+怎么用+价值是什么）
5. **适用人群**：明确用户画像

## 对比章（comparison.md）编写要求

- 必须包含横向参数对比表（所有产品核心参数一表览）
- 必须有"相同点"和"差异点"文字总结
- 差异点必须回答"为什么有这个差异"（场景驱动参数取舍）
- 必须提供选型指南："X场景选A，Y场景选B"

## 场景章（scenarios.md）四要素

每个场景必须包含：
1. **用户痛点**：具体遇到什么问题？
2. **产品方案**：本产品如何解决？
3. **操作流程**：具体怎么设置/使用？
4. **价值收益**：解决后带来什么可量化收益？

## 配套TOML元数据

复制后需在 `.meta/toml/` 镜像路径创建对应TOML文件：

- 索引页（如有）：`.meta/toml/docs/knowledge/learning/{wiki-name}.toml`
- 原子文件：`.meta/toml/docs/knowledge/learning/{wiki-name}/NN-xxx.toml`

## 关联参考

- [mdi-document-template.md](../mdi-document-template.md) - 单文件MDI标准模板（产品≤2款时使用）
- [sunlogin-hardware-wiki-structure.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/sunlogin-hardware-wiki-structure.md) - 向日葵硬件Wiki结构模式（本模板的理论依据）
- [wiki-pre-creation-three-checks.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/wiki-pre-creation-three-checks.md) - Wiki创作三查流程（创建前必做）
- [向日葵无网远控硬件Wiki](../../../docs/knowledge/learning/sunlogin-bootbox-analysis/) - 本模板的完整验证案例