> **来源**：从 `docs/retrospective/knowledge-extraction.md` 六、可复用知识概念 拆分

# 正交验证（Orthogonal Verification）

## 定义
多项优化各自独立验证，每项验证的指标变化可精确归因到具体优化。

## 对比整体验证
- 整体验证：所有优化完成后一次性验证，指标变化原因难以定位
- 正交验证：每项优化独立验证 + 回归验证兜底，指标变化原因精确可追溯

> **关联模块**：
> - `patterns/architecture-patterns/incremental-regression-verification.md`