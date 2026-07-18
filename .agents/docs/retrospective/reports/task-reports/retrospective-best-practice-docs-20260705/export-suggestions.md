---
title: "最佳实践文档整理复盘—导出建议"
date: 2026-07-05
source: "retrospective:best-practice-docs-20260705"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/task-reports/retrospective-best-practice-docs-20260705/export-suggestions.toml"
type: "export-suggestions"
tags: [best-practice, action-items, pattern-library]
---
# 最佳实践文档整理复盘—导出建议

## 行动项落地计划

| 行动项 | 优先级 | 负责方 | 验收标准 | 建议完成时间 |
|--------|--------|--------|---------|-------------|
| A1: 本次交付的两个新模式正式纳入模式库，后续研究vendor仓库和处理工具故障时主动应用 | 高 | 全体执行者 | 下次遇到外部仓库研究任务时，第一步先找AGENTS.md；工具连续失败2次立即降级 | 立即生效 |
| A2: 后续沉淀模式时执行"先看现有模板再创作"流程 | 中 | 全体执行者 | 沉淀新模式前先读1-2个同分类现有模式作为参考 | 下次模式沉淀时 |
| A3: 补充模式沉淀checklist到协作规范 | 低 | 流程治理团队 | 在相关规范中增加"模式沉淀标准步骤" | 2026-07-15前 |
| A4: 核实"高层文档优先研究法"的第二次验证记录 | 低 | 知识管理团队 | 确认Agent Proto Wiki复盘是否明确记录了该模式的应用，如没有则暂降为L1 | 2026-07-10前 |

## 后续跟进事项

1. **模式应用追踪**：后续任务中主动应用这两个新模式，记录validation_count增长
2. **tools-automation/README.md**：该目录已有28个模式但缺少分类级README，当有明确需求或用户要求时再创建，当前遵守"不主动创建文档"规则
3. **索引自动化**：长期可考虑脚本自动扫描更新模式计数，减少手动编辑错误

## 知识沉淀清单

### 本次新增知识

| 知识类型 | 位置 | 内容摘要 |
|---------|------|---------|
| L2最佳实践模式 | [vendor-high-level-doc-first-research.md](../../../patterns/methodology-patterns/research-knowledge/vendor-high-level-doc-first-research.md) | Vendor仓库自顶向下研究法，AGENTS.md优先，效率提升5-10倍 |
| L1最佳实践模式 | [tool-failure-three-tier-degradation.md](../../../patterns/methodology-patterns/tools-automation/tool-failure-three-tier-degradation.md) | 工具故障三级降级：sub-agent→附带信息→已有知识，2次失败禁止第3次重试 |

### 可复用流程经验

"复盘洞察→模式库平滑转化法"已在洞察萃取中详细描述，可作为后续模式沉淀的标准流程参考。

---

## 导航
- [复盘报告](retrospective-report.md)
- [洞察萃取](insight-extraction.md)
- [返回任务复盘索引](../../README.md)
