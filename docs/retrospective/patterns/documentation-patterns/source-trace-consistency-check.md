---
type: Pattern
id: pattern-source-trace-consistency-check
title: 溯源一致性三查
date: 2026-08-31
source: create-sexology-classics-wiki-retrospective-20260830
maturity: draft
validation_count: 1
reuse_count: 0
tags: [OKF, 知识包, 信源溯源, 一致性检查, 质量门, 知识沉淀]
pattern_type: methodology
category: documentation
---

# 溯源一致性三查（Source-Trace Consistency Check）

## 触发场景

OKF 知识包或任何含「事实登记表 + 信源引用」的文档体系交付后，特别是：

- 存在跨文件交叉引用（概念↔事实↔信源多层引用链）
- 调研阶段产生过临时中间产物（如 `.temp/` 下的调研笔记）
- 存在全局计数/索引（如 bundles/index.md 的束数/分组数）
- 经历过独立评审或多会话并行修改后的收尾复核

**不适用**：纯新增、无既有约定、无临时产物残留的小改动（直接过常规门禁即可）。

## 核心步骤

### 查一：临时文件残留指向扫描

1. `grep -r "\.temp"` 全库扫描正文与 frontmatter 的 `source`/信源字段
2. 同时扫描绝对临时路径（`file:///`、`C:\Users\...` 等不符合相对路径约定的引用）
3. **产出**：残留指向清单，逐条改指 bundle 内正式文件（如 `facts.md` 相对链接）

### 查二：术语/译名全库一致性扫描

1. 列出关键实体的全部候选写法（含异体字，如「蔼理士/霭理士」）
2. 全库 grep 各变体，统计分布
3. 依权威信源裁决唯一写法后统一替换，复查零残留
4. **产出**：统一裁决记录 + 各变体零残留证明

### 查三：版本差异 vs 转录歧义判别

1. 对"同一实体多值"现象，先做权威核验（作者官方页/馆藏目录/出版社登记）
2. 确属**版本真实差异** → 分版表述 + 逐版本给出来源（详见 [version-discrepancy-arbitration.md](version-discrepancy-arbitration.md)）
3. 确属**转录歧义**（如用字不同）→ 全库统一 + 记录裁决
4. **产出**：每个多值实体都有"分版 or 统一 + 依据"的明确记录

### 查四：计数/索引算术自洽核对

1. 对全局索引（如 bundles/index.md）的束数/分组数做**独立累加还原**
2. 累加结果与 frontmatter 声明值逐一比对
3. 不一致时以累加还原值为准修正，禁止凭印象臆断
4. **产出**：计数自洽核对记录

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 把临时调研产物设为主文档信源（`.temp` 残留） | 临时文件清理后信源断链，溯源失效 | 信源一律指向 bundle 内正式文件的相对链接 |
| 译名用字混用不设统一裁决 | 同一实体在库内多个写法，读者困惑 | 列变体→权威裁决→全库统一→零残留复查 |
| 把真实版本差异一刀切"修复"为统一值 | 用一致性掩盖正确性，引入错误 | 先核验再判别：分版或统一，均有依据 |
| 凭"多一个分组"臆断计数而不做算术累加 | 索引声明值与实际不符且无人发现 | 独立累加还原，与 frontmatter 比对 |

## 检验标准

- 查四类机械门禁（toctrees/utf8）通过
- 全库 grep 各变体候选值为零残留
- 计数经独立累加还原与 frontmatter 完全一致

## 迁移验证

- ✅ 性学经典 OKF 知识包（think/sexology/classics-reading）：独立评审 6 项问题中 4 项属本模式覆盖的隐患类（临时文件指向、译名混用、福柯译者无信源、索引计数歧义），全部修复闭环
- 🔄 可迁移到：任意"文献/书目/版本史"知识体系（古籍整理、合规清单、资产盘点表）

## 相关资源

- [版本差异判别模式](version-discrepancy-arbitration.md)（本模式查三的展开）
- [博文类文章→OKF知识包转化模式](blog-article-to-okf-bundle.md)（交付前工作流，本模式为其交付后复核层）
- 来源复盘：`.agents/docs/retrospective/reports/concepts/milestone/retrospective-sexology-classics-wiki-20260830.md`
