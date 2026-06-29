+++
id = "firecrawl-action-2-skill-discovery"
date = "2026-06-29"
type = "action"
priority = "high"
category = "架构"
status = "pending"
source = "insight-extraction.md#洞察4"
+++

# 行动2：增强 Skill 发现协议

**优先级**：🔴 高
**预计工作量**：中（设计规范 + 改造现有 skill）

## 目标

参考 Firecrawl Agent Onboarding 的 SKILL.md 设计，增强 SpecWeave 的 skill 可发现性。

## 落地步骤

1. 为每个 skill 增加标准化的 SKILL.md 描述文件（类似 Firecrawl 的 `/agent-onboarding/SKILL.md`）
2. 定义统一的 frontmatter 字段（能力描述、输入输出、依赖、示例）
3. 实现 agent 可通过固定路径获取 skill 列表和描述
4. 考虑增加"零配置试用"机制——首次调用某 skill 无需完整配置即可运行 demo 级别任务

## 验收标准

新 Agent 在新会话中可通过固定入口发现所有可用 Skill，无需遍历多个目录。

## 关联模式与洞察

- [洞察1：Keyless模式](../insights/insight-1-keyless.md)
- [洞察4：Agent Onboarding](../insights/insight-4-agent-onboarding.md)
- [架构优先级评估 P0模块1](../../retrospective-architecture-priority-20260629/README.md#重构模块-1能力注册与发现中心capability-registry) — 此行动已纳入架构重构P0
- [📘 SOP文档：Skill发现协议增强](../../../../patterns/methodology-patterns/ai-collaboration/skill-discovery-protocol.md)（三层发现机制+四步实施详解+验收标准）

> **SOP沉淀状态**：📝 已完成SOP设计文档（L1成熟度，待实施验证）
