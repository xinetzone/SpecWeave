+++
id = "p-arch-001"
name = "渐进式披露架构"
name_en = "Progressive Disclosure Architecture"
date = "2026-06-29"
type = "pattern-detail"
maturity = "L2"
source = "export-suggestions.md#p-arch-001"
+++

# P-ARCH-001 渐进式披露架构

**问题**：成熟的规范体系文档量巨大，新 Agent 入门需要读取大量文档，浪费上下文窗口。

**解决方案**：三层入口架构：
- L0 入口层（<100行）：ONBOARDING.md——身份+能力速查+路由表
- L1 索引层（<500行/能力）：SKILL.md——触发词+决策树+核心步骤+安全清单
- L2 深度层（不限）：原规范文档——完整参考手册

**正反例**：
- ✅ Firecrawl agent-onboarding 设计
- ✅ SKILL-TEMPLATE 五要素模型
- ❌ 当前 PDR 协议要求"全量读取所有前置文档"
