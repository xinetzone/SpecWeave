+++
id = "architecture-priority-insight-a"
date = "2026-06-29"
type = "insight"
source = "insight-extraction.md#洞察-a"
maturity = "L2"
+++

# 洞察 A：规范成熟度与可发现性呈反比

**现象**：SpecWeave 的规范层（stage-guardrails、PDR协议、硬编码治理）已达到 L4 成熟度，但能力发现层是 L0 缺失。

**深层洞察**：
- 规范越成熟、越完善，新 Agent 的入门门槛反而越高——需要读的文档越多
- 这是"文档悖论"：文档写得越好、越详细，反而越不利于 Agent 自主发现
- Firecrawl 用 Keyless API 解决了这个问题：零配置入口，渐进式披露深度信息
- SpecWeave 的 PDR 协议恰恰是反模式——要求新会话"重新读取所有前置文档"

**可复用模式**：**渐进式披露架构（Progressive Disclosure Architecture）**
> 任何成熟的规范/能力体系都应该有三层入口：
> 1. **L0 入口层**（<100行）：ONBOARDING.md——身份+能力速查+路由表
> 2. **L1 索引层**（<500行/能力）：SKILL.md——触发词+决策树+核心步骤+安全清单
> 3. **L2 深度层**（不限）：原规范文档——完整参考手册
