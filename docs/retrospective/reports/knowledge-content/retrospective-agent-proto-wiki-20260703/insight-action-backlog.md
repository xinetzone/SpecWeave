---
title: Agent通信协议Wiki教程复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/knowledge-content/retrospective-agent-proto-wiki-20260703/insight-action-backlog.toml"
project: retrospective-agent-proto-wiki-20260703
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。所有行动项均已闭环完成。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动计划高 | 子agent指令模板化（六要素） | 高 | ✅ 已完成 | subagent-atomic-task-template.md升级为六要素模板，新增Mermaid安全规则 | 2026-07-03 |
| IMP-002 | 行动计划中 | Mermaid自动检测脚本 | 中 | ✅ 已完成 | lib/checks/mermaid.py新增_check_security函数，检测6类违规 | 2026-07-03 |
| IMP-003 | 行动计划中 | 篇幅控制两阶段模式沉淀 | 中 | ✅ 已完成 | two-stage-outline-then-expand.md沉淀至ai-collaboration目录 | 2026-07-03 |
| IMP-004 | 行动计划低 | 代码示例验证补充 | 低 | ✅ 已完成 | MCP/A2A SDK示例补充安装命令和版本标注 | 2026-07-03 |
| IMP-005 | 行动计划低 | ANP章节内容补充 | 低 | ✅ 已完成 | 补充三层协议架构/ADP规范/did:wba方法/发现机制 | 2026-07-03 |

## 行动项详情

### IMP-001: 子agent指令模板化（六要素）
- **优先级**: 高
- **执行结果**: subagent-atomic-task-template.md从五要素升级为六要素模板，新增Mermaid安全规则作为第六要素，在2个项目中验证
- **产出物**: [subagent-atomic-task-template.md](../../../patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md)
- **状态**: ✅ 已完成

---

### IMP-002: Mermaid自动检测脚本
- **优先级**: 中
- **执行结果**: lib/checks/mermaid.py新增_check_security函数，检测click事件/危险HTML标签/事件处理器/javascript URL/end节点ID/classDef共6类安全违规
- **产出物**: [mermaid.py](../../../../../.agents/scripts/lib/checks/mermaid.py)
- **状态**: ✅ 已完成

---

### IMP-003: 篇幅控制两阶段模式沉淀
- **优先级**: 中
- **执行结果**: "先大纲后展开"模式沉淀为two-stage-outline-then-expand.md，包含两阶段工作流、适用场景、反模式警示
- **产出物**: [two-stage-outline-then-expand.md](../../../patterns/methodology-patterns/ai-collaboration/two-stage-outline-then-expand.md)
- **状态**: ✅ 已完成

---

### IMP-004: 代码示例验证补充
- **优先级**: 低
- **执行结果**: 为MCP Python/TypeScript SDK和A2A Python SDK示例补充安装命令（pip install mcp>=1.26.0 / npm install @modelcontextprotocol/sdk / pip install a2a-sdk）和版本标注
- **产出物**: 07-implementation章节更新
- **状态**: ✅ 已完成

---

### IMP-005: ANP章节内容补充
- **优先级**: 低
- **执行结果**: 补充ANP三层协议架构（身份层/元协议层/应用层）、did:wba DID方法、Agent Description Protocol (ADP) JSON-LD示例、Agent发现机制、IETF Draft状态更新
- **产出物**: 04-anp章节更新
- **状态**: ✅ 已完成

## 模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 |
|---------|-----------|---------|---------|
| 原子化技术文档组织 | L2（已验证） | 本项目成功复用agent-skills-wiki模式 | 2026-07-03 |
| 子agent约束前置 | L1→L2（已验证） | 从五要素升级为六要素，新增Mermaid安全规则 | 2026-07-03 |
| 类比锚点教学法 | L2（已验证） | 四层协议类比在多处验证有效 | 2026-07-03 |
| 三段式内容验证 | L1（已沉淀） | 终验发现自检遗漏问题，沉淀至governance-strategy | 2026-07-03 |
| Mermaid安全检测 | L1（新提炼） | 从人工检查升级为自动化安全检测 | 2026-07-03 |
| 篇幅控制两阶段模式 | L1（新提炼） | 从改进建议中提炼"先大纲后展开"模式 | 2026-07-03 |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~005 | 2026-07-03 | - | 全部5项行动计划闭环完成，含3个模式入库/更新、1个脚本增强、2个教程章节更新 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移5项已完成行动项至独立backlog文件
