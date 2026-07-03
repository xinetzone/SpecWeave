---
id: "capability-registry-commands-workflows"
title: "命令集、工作流、协议、规则索引"
source: "capability-registry.md#03-commands-workflows-protocols-rules"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/03-commands-workflows-protocols-rules.toml"
---
# 命令集、工作流、协议、规则索引

## 命令集索引（.agents/commands/）

| 命令 | ID | 用途 | 触发词 | 关联自我演进模块 | 路径 |
|------|----|------|--------|----------------|------|
| 复盘 | retrospective | 项目复盘流程，生成复盘报告与改进建议 | "复盘"、"retrospective"、"回顾"、"总结经验" | 自我复盘 (self-retrospective) | [commands/retrospective.md](../commands/retrospective.md) |
| 洞察 | insight | 数据分析与问题诊断，识别优化机会与异常 | "洞察"、"insight"、"分析问题"、"萃取洞察" | 自我洞察 (self-insight) | [commands/insight.md](../commands/insight.md) |
| 模式萃取 | pattern-extraction | 从复盘/洞察中萃取可复用模式，生成标准模式文档并入库 | "模式沉淀"、"萃取模式"、"模式入库"、"可复用模式" | 自我萃取 (self-extraction) | [skills/pattern-extraction-cmd/SKILL.md](../skills/pattern-extraction-cmd/SKILL.md) |
| 导出报告 | export-report | 结构化报告导出，支持多格式与归档 | "导出报告"、"export"、"生成报告" | 自我复盘 (self-retrospective) | [commands/export-report.md](../commands/export-report.md) |
| 原子化 | atomization | 文档与代码的原子化拆分，确保单一职责 | "原子化"、"拆分文件"、"atomize"、"拆分大文档" | 自我萃取 (self-extraction) | [commands/atomization.md](../commands/atomization.md) |
| 原子提交 | atomic-commit | Git原子化提交规范，确保单次提交单一职责 | "提交"、"commit"、"原子提交" | 自我迭代 (self-iteration) | [commands/atomic-commit.md](../commands/atomic-commit.md) |
| 文件创建 | file-creation | 文件创建标准化流程，包含三步前置检查（必要性/重复/命名） | "创建文件"、"新建文件"、"文件创建" | 自我管理 (self-management) | [commands/file-creation.md](../commands/file-creation.md) |
| Mermaid图表管理 | mermaid | Mermaid图表生成、解析、检查、修复与协作管理 | "mermaid"、"流程图"、"时序图"、"画个图"、"架构图" | 自我管理 (self-management) | [commands/mermaid.md](../commands/mermaid.md) |
| Home Assistant集成 | home-assistant | Home Assistant智能家居系统集成，设备控制与状态查询（可选模块） | "智能家居"、"Home Assistant"、"控制设备"、"查询设备状态" | 可选集成模块 | [commands/home-assistant.md](../commands/home-assistant.md) |

完整设计理念和执行流程见 [commands/README.md](../commands/README.md)。

---


## 工作流索引（.agents/workflows/）

| 工作流 | 适用场景 | 参与角色 | 路径 |
|--------|---------|---------|------|
| 功能开发（feature-development） | 新功能、功能扩展、功能重构三路径 | 全部角色 | [workflows/feature-development.md](../workflows/feature-development.md) |
| 代码审查（code-review） | PR审查、代码质量检查 | developer, reviewer, orchestrator | [workflows/code-review.md](../workflows/code-review.md) |
| 测试流程（testing） | 测试执行、用例编写、覆盖率验证 | tester, developer, reviewer | [workflows/testing.md](../workflows/testing.md) |

完整工作流定义和角色参与表见 [workflows/README.md](../workflows/README.md)。

---


## 协议索引（.agents/protocols/）

| 协议 | 用途 | 路径 |
|------|------|------|
| 会话启动协议（Onboarding） | L0-L2三层认知建立流程、设计理由、上下文恢复 | [protocols/onboarding-protocol.md](../protocols/onboarding-protocol.md) |
| 任务交接（handoff） | 智能体间任务转移规范 | [protocols/handoff.md](../protocols/handoff.md) |
| 消息传递（messaging） | 智能体间通信机制 | [protocols/messaging.md](../protocols/messaging.md) |
| 冲突解决（conflict-resolution） | 分歧仲裁流程 | [protocols/conflict-resolution.md](../protocols/conflict-resolution.md) |
| 前置文档强制读取（PDR） | 必读文档清单与确认机制 | [protocols/pre-document-reading.md](../protocols/pre-document-reading.md) |
| 临时依赖管理 | .temp/ 依赖存放与清理 | [protocols/dependency-management.md](../protocols/dependency-management.md) |
| 应用开发生命周期 | .temp/暂存 → apps/稳定迁移 | [protocols/app-development-workflow.md](../protocols/app-development-workflow.md) |

---


## 规则体系索引（.agents/rules/）

| 规则 | 用途 | 适用角色 | 路径 |
|------|------|---------|------|
| 阶段守卫（stage-guardrails） | 阶段边界定义、跨阶段拦截、SG-LOG规范 | 全部角色 | [rules/stage-guardrails.md](../rules/stage-guardrails.md) |
| Skill开发规范（skill-development） | SpecWeave主权区Skill开发补充规范 | developer, reviewer | [rules/skill-development.md](../rules/skill-development.md) |
| RACI治理规范（raci-governance-standards） | RACI矩阵A唯一性、R≠A分离、双列审批模型、co-founder审批边界 | 全部角色 | [rules/raci-governance-standards.md](../rules/raci-governance-standards.md) |
| 硬编码识别标准 | 8大类硬编码定义与检测要点 | developer, reviewer | [rules/identification-standards.md](../rules/identification-standards.md) |
| 硬编码允许场景与审批 | 允许场景清单、例外审批流程 | developer, reviewer, architect | [rules/allowable-scenarios.md](../rules/allowable-scenarios.md) |
| 硬编码替代方案指南 | 7种替代方案实施指南 | developer | [rules/alternatives-guide.md](../rules/alternatives-guide.md) |
| 检测与报告机制 | 三层检测体系 | developer, reviewer, orchestrator | [rules/detection-and-reporting.md](../rules/detection-and-reporting.md) |
| 执行与验证规则 | 6条可执行治理规则 | 全部角色 | [rules/enforcement-guidelines.md](../rules/enforcement-guidelines.md) |

完整规则体系见 [rules/README.md](../rules/README.md)。

---


---

## 相关模式


← 上一章: [Skill索引](02-skills.md) | **[返回索引](../capability-registry.md)** | 下一章 → [知识参考、快速查找指南与更新说明](04-knowledge-guide-changelog.md)
