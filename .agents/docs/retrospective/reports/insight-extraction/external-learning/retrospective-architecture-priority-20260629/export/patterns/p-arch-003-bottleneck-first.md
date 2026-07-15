---
id: "p-arch-003"
title: "P-ARCH-003 瓶颈优先重构法"
source: "export-suggestions.md#p-arch-003"
x-toml-ref: "../../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/patterns/p-arch-003-bottleneck-first.toml"
---
# P-ARCH-003 瓶颈优先重构法

**问题**：架构重构时容易陷入"先改最容易的"或"全面重构"两个极端。

**解决方案**：
1. 用成熟度分层模型（L0缺失/L1规划/L2起步/L3可用/L4成熟）评估各层
2. 找到全局瓶颈（最低成熟度的层）
3. 所有重构围绕解除瓶颈展开
4. 瓶颈解除后重新评估找下一个瓶颈
5. 非瓶颈层的优化推迟

**本次应用**：能力发现层 L0 缺失 → 先建注册中心（P0模块1）
