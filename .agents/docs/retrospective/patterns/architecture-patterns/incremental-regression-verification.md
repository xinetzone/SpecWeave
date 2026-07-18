---
id: "incremental-regression-verification"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/architecture-patterns/incremental-regression-verification.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 二、可复用架构模式 拆分

# 增量验证 + 回归验证双层策略

## 来源
v1.1 三项优化的验证过程

## 流程图
```
优化 1 完成 → 独立验证（确认指标变化）
优化 2 完成 → 独立验证（确认指标变化）
优化 3 完成 → 独立验证（确认指标变化）
              ↓
         回归验证（确认组合无副作用）
```

## 原则
- 每项优化独立验证 → 精确归因
- 全部完成后回归验证 → 兜底保障

## 复用场景
任何多优化迭代的开发流程。

> **关联模块**：
> - `concepts/orthogonal-verification.md`
> - `patterns/methodology-patterns/retrospective-knowledge/review-insight-export-loop.md`