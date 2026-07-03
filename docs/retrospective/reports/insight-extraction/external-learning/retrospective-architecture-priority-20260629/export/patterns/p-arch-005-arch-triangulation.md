---
id: "p-arch-005"
title: "P-ARCH-005 架构决策三角验证"
source: "export-suggestions.md#p-arch-005"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/patterns/p-arch-005-arch-triangulation.toml"
---
# P-ARCH-005 架构决策三角验证

**问题**：架构决策容易基于单一视角（只看代码/只凭感觉/只抄标杆），导致偏差。

**解决方案**：架构决策必须同时覆盖三个视角：
1. **代码视角（What is）**：读代码/看文件，了解当前实际状态
2. **使用视角（What hurts）**：实际使用中的痛点和摩擦点
3. **标杆视角（What good looks like）**：外部优秀实践作为参照

**缺少任何一个的后果**：
- 缺标杆：不知道好的设计是什么样
- 缺使用痛点：变成象牙塔架构
- 缺代码实际：变成空中楼阁
