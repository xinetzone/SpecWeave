---
id: "retrospective-specweave-contest-advantage-analysis-20260624-meta-insight-05"
title: "洞察 5：全量重写的幂等性——\"增量编辑的成本会在某处拐点超过全量重写\" ⭐⭐⭐⭐"
source: "retrospective-specweave-contest-advantage-analysis-20260624/ — export-suggestions.md v10→v11 SearchReplace 断裂"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/retrospective-meta-20260625/insights/full-rewrite-idempotency-threshold.toml"
---
# 洞察 5：全量重写的幂等性——"增量编辑的成本会在某处拐点超过全量重写" ⭐⭐⭐⭐

**现象**：export-suggestions.md 的 v10→v11 重写中，尝试用多轮 SearchReplace 将 SpecWeave 单作品策略改为双作品策略。第一轮替换成功了（写入 §4.0-4.2），第二轮替换因文件已被改变而失败——产生了"新头部 + 旧尾部"的混合状态文件。最终修复路径是整体读写拼接——恰好是"全量重写"策略。

**规律**：

```
编辑策略的成本曲线：

文件变更规模 →
    │
    │     增量编辑成本
    │    ／‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    │  ／                         拐点（>50 行变更时
    │ ／                          增量编辑的风险 > 成本节省）
───┼─────────────────────────────────────────────────
    │ 全量重写成本（恒定）
    │   ──────────────────────────────────────────
    │
```

**操作指南**：当单个文件的修改量超过 50 行或涉及结构性重写（如从一个作品的策略改为两个作品）时，优先选择全量读写策略而非多轮局部替换。具体做法：(1) 用 Read 读取全文件；(2) 在脑海中构建完整的替换后内容；(3) 用一次 Write 写入——而非多轮 SearchReplace。

> **一句话**：局部编辑是为了省事，但当省事本身变成了最大风险来源时，全量重写的"不省事"恰恰是最省事的。
