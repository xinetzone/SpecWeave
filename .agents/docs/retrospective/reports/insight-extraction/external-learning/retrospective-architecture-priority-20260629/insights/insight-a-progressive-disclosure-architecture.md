---
id: "architecture-priority-insight-a"
title: "洞察 A：规范成熟度与可发现性呈反比"
source: "insight-extraction.md#洞察-a"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insights/insight-a-progressive-disclosure-architecture.toml"
---
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

---

## 实施验证（2026-06-30 更新）

**洞察成熟度：L3 → 已正式化为规范并在项目中全面落地**

### 正式规范归档

本洞察已提炼为正式架构规范，归档于：
- [ARCHITECTURE.md](../../../../../../../capabilities/ARCHITECTURE.md)（v1.1.0，成熟度 L2）
- 包含完整的三层定义、内容边界、跨层引用规则、质量检查清单、反模式

### 落地实例（P0 模块 1-3 完成）

| 模块 | 层 | 文件 | 实施前 | 实施后 | 优化比例 |
|------|----|------|--------|--------|----------|
| P0-M1 | L0 | [ONBOARDING.md](../../../../../../../ONBOARDING.md) | 141行 | 88行 | **-38%** ✅ |
| P0-M1 | L1 | [capability-registry.md](../../../../../../../capability-registry.md) | - | 236行 | 新建 ✅ |
| P0-M2 | L1 | retrospective-cmd/SKILL.md | 149行 | 117行 | **-21%** ✅ |
| P0-M2 | L1 | export-report-cmd/SKILL.md | 170行 | 122行 | **-28%** ✅ |
| P0-M3 | L1 | insight-cmd/SKILL.md | - | 124行 | 三层合规 ✅ |
| P0-M3 | L1 | atomization-cmd/SKILL.md | - | 131行 | 三层合规 ✅ |
| P0-M3 | L1 | atomic-commit-cmd/SKILL.md | - | 127行 | 三层合规 ✅ |
| P0-M2 | L2 | [onboarding-protocol.md](../../../../../../../protocols/onboarding-protocol.md) | - | 新建 | 深度层独立 ✅ |
| P0-M2 | L2 | [cmd-log-specification.md](../../../../../../../rules/cmd-log-specification.md) | - | 从L1下沉 | 修复分层断裂 ✅ |

### 修复的分层断裂问题

| 反模式 | 修复前状态 | 修复方案 |
|--------|-----------|----------|
| 入口过重 | ONBOARDING.md 141行，包含详细步骤 | 精简至88行，详细流程下沉至L2 onboarding-protocol.md |
| 分层断裂 | 5个命令Skill直接内嵌完整CMD-LOG规范 | L1仅保留8行摘要+L2锚点引用，修复"分层断裂"反模式 |

### 验证结果

- ✅ 所有 L0/L1 文件均符合行数限制（L0 <100行，L1 <500行）
- ✅ 所有本地引用链接验证通过
- ✅ 解决了"文档悖论"问题：新Agent只需先读88行L0即可建立身份认知，按需加载对应L1，仅在遇到边界情况时加载L2
