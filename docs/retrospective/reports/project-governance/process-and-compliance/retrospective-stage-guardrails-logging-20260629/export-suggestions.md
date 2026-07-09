---
id: "retrospective-stage-guardrails-logging-20260629-export"
title: "导出建议"
source: "insight-extraction.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-stage-guardrails-logging-20260629/export-suggestions.toml"
---
# 导出建议

## 改进项（按优先级排序）

### P0：立即执行

| 编号 | 改进项 | 类型 | 建议做法 |
|------|--------|------|---------|
| A1 | 新增模式：规则落地三层模型（定义+痕迹+验证） | 模式萃取 | 萃取为methodology-patterns/governance-strategy/下的新模式 |
| A2 | 新增模式：结构化轻量日志（键值对+JSON ctx） | 模式萃取 | 萃取为code-patterns/下的新模式，指导后续日志格式设计 |
| A3 | 配置.gitattributes统一换行符 | 环境修复 | 创建.gitattributes，设置* text=auto，*.md text eol=lf |

### P1：近期执行

| 编号 | 改进项 | 类型 | 建议做法 |
|------|--------|------|---------|
| B1 | 将check-stage-guardrails.py集成到CI | CI增强 | 在ci-check.ps1/sh中增加阶段守卫日志检查步骤（如果存在日志文件） |
| B2 | 为check-stage-guardrails.py添加--strict模式 | 脚本增强 | strict模式下WARN也返回非零退出码，用于CI门禁 |
| B3 | 更新spec模板增加"可观测性需求" | 模板增强 | 在.trae/specs/模板或.spec模板中强制要求考虑日志/验证 |

### P2：后续规划

| 编号 | 改进项 | 类型 | 建议做法 |
|------|--------|------|---------|
| C1 | 阶段守卫的运行时强制执行 | 功能增强 | 未来实现一个装饰器/中间件层，在智能体调用工具时实时检查阶段权限 |
| C2 | 日志聚合仪表盘 | 可视化 | 多会话日志聚合，阶段完成率、拦截率、审批通过率等指标可视化 |
| C3 | PowerShell UTF-8配置 | 环境 | 设置[Console]::OutputEncoding和git i18n.commitEncoding |

## 模式萃取清单

本次迭代萃取以下3个可复用模式（成熟度L2：已在一个场景中验证有效）：

1. **three-layer-rule-enforcement**（规则落地三层模型）→ governance-strategy
   - 核心：定义层（规范文档）+ 痕迹层（结构化日志）+ 验证层（检查工具）
   - 适用场景：任何需要智能体"自觉遵守"的治理规则落地

2. **structured-lightweight-logging**（结构化轻量日志）→ code-patterns
   - 核心：`[PREFIX] | key=value | key=value | ctx={json}` 单行格式
   - 适用场景：AI Agent执行过程中的可观测性需求，无需重量级基础设施

3. **elastic-workflow-classification**（弹性流程分级）→ governance-strategy
   - 核心：变更类型判定决策树→按风险选择流程路径（新功能/扩展/重构）
   - 适用场景：需要灵活但不失控的开发流程治理

## 知识更新项

| 更新目标 | 更新内容 |
|---------|---------|
| AGENTS.md上下文路由表 | 已在本次迭代中同步更新（日志规范+check脚本入口） |
| docs/knowledge/ | 待创建stage-guardrails-guide.md（阶段守卫使用指南） |
| .trae/specs/README.md | 看板状态：roles-governance 5/5（含本次add-development-stage-guardrails） |
