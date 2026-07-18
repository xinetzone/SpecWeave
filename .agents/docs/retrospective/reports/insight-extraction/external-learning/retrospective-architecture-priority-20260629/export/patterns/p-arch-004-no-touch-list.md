---
id: "p-arch-004"
title: "P-ARCH-004 不重构清单"
source: "export-suggestions.md#p-arch-004"
x-toml-ref: "../../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/patterns/p-arch-004-no-touch-list.toml"
---
# P-ARCH-004 不重构清单

**问题**：架构评估容易陷入"重构癖"，什么都想改，导致范围蔓延。

**解决方案**：架构评估必须输出三类清单：
- ✅ 重构清单（按优先级排序，每个有理由）
- ❌ 不重构清单（每个项必须说明为什么不动）
- ⏸️ 暂缓清单（条件不满足时不动，明确触发条件）

**本次应用**：6个不重构项（阶段守卫、角色体系、工作流、协议层、硬编码规则、自我演进模块）
