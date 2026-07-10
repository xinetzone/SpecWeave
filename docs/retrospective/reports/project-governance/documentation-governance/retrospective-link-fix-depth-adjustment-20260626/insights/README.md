---
id: "retrospective-link-fix-depth-adjustment-20260626-insights-index"
title: "链接修复深度调整复盘 · 洞察原子索引"
source: "../insight-extraction.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/README.toml"
---
# 链接修复深度调整复盘 · 洞察原子索引

> 本目录存放从链接修复深度调整复盘中萃取的 13 条核心洞察（5条问题层发现 + 8条执行层元洞察），每条洞察均已拆分为独立原子文件。
> 母文件：[insight-extraction.md](../insight-extraction.md)
>
> ✅ 13条洞察全部归档为全局模式（9个新建+3个已有覆盖）。

## 洞察清单

### 问题层发现（5条）

| 编号 | 文件 | 核心命题 | 已归档全局模式 |
|------|------|---------|--------------|
| 发现1 | [insight-01-predictable-link-breakage.md](insight-01-predictable-link-breakage.md) | 目录重构后相对路径断链可预测、可算法修复 | [relative-depth-adjustment](../../../../../patterns/code-patterns/relative-depth-adjustment.md)（代码模式） |
| 发现2 | [insight-02-path-suffix-invariance.md](insight-02-path-suffix-invariance.md) | 路径后缀不变性是自动校正的关键假设 | [relative-depth-adjustment](../../../../../patterns/code-patterns/relative-depth-adjustment.md)（核心假设） |
| 发现7 | [insight-07-tool-composition-effect.md](insight-07-tool-composition-effect.md) | 工具组合形成工作流闭环价值大于单个工具之和 | [tool-workflow-composition](../../../../../patterns/methodology-patterns/tools-automation/tool-workflow-composition.md)（L1新建） |
| 发现8 | [insight-08-cache-for-periodic-checks.md](insight-08-cache-for-periodic-checks.md) | 缓存是定期检查类工具的必备能力 | [periodic-check-caching](../../../../../patterns/code-patterns/periodic-check-caching.md)（代码模式 L1新建） |
| 发现9 | [insight-09-link-decay-four-laws.md](insight-09-link-decay-four-laws.md) | 链接衰变四条规律（下移/上移/跨目录/同目录） | [link-decay-laws](../../../../../patterns/methodology-patterns/document-architecture/link-decay-laws.md)（L1新建） |

### 执行层元洞察（8条）

| 编号 | 文件 | 核心命题 | 已归档全局模式 |
|------|------|---------|--------------|
| ME-01 | [meta-exec-01-paradigm-three-level-jump.md](meta-exec-01-paradigm-three-level-jump.md) | 问题解决三层跃迁（症状→病因→免疫） | [three-level-problem-solving](../../../../../patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)（L1新建） |
| ME-02 | [meta-exec-02-link-tax-hidden-cost.md](meta-exec-02-link-tax-hidden-cost.md) | 最佳实践隐性成本"链接税"，需工具链吸收 | [best-practice-hidden-cost](../../../../../patterns/methodology-patterns/tools-automation/best-practice-hidden-cost.md)（L1新建） |
| ME-03 | [meta-exec-03-tool-bootstrap-effect.md](meta-exec-03-tool-bootstrap-effect.md) | 工具自举正反馈循环（dogfooding） | [tool-bootstrap-effect](../../../../../patterns/methodology-patterns/tools-automation/tool-bootstrap-effect.md)（L1新建） |
| ME-04 | [meta-exec-04-precision-over-recall.md](meta-exec-04-precision-over-recall.md) | 精度优先：破坏性工具零误报原则 | [precision-over-recall](../../../../../patterns/methodology-patterns/tools-automation/precision-over-recall.md)（L1新建） |
| ME-05 | [meta-exec-05-governance-maturity-quantified.md](meta-exec-05-governance-maturity-quantified.md) | 9维度治理成熟度量化跃迁L1→L5 | [toolchain-maturity](../../../../../patterns/methodology-patterns/tools-automation/toolchain-maturity.md)（已归档） |
| ME-06 | [meta-exec-06-methodology-compound-interest.md](meta-exec-06-methodology-compound-interest.md) | 方法论复利：临界质量后速度非线性加快 | [methodology-critical-mass](../../../../../patterns/methodology-patterns/retrospective-knowledge/methodology-critical-mass.md)（已覆盖） |
| ME-07 | [meta-exec-07-counterfactual-thinking.md](meta-exec-07-counterfactual-thinking.md) | 反事实推演：技术债复利代价量化 | [counterfactual-debt-analysis](../../../../../patterns/methodology-patterns/retrospective-knowledge/counterfactual-debt-analysis.md)（L1新建） |
| ME-08 | [meta-exec-08-experience-transferability.md](meta-exec-08-experience-transferability.md) | 经验迁移映射：核心机制vs上下文细节 | [experience-transfer-mapping](../../../../../patterns/methodology-patterns/retrospective-knowledge/experience-transfer-mapping.md)（L1新建） |

## 归档统计（本目录）

| 类型 | 数量 |
|------|------|
| 新建方法论模式 | 8个（three-level-problem-solving, best-practice-hidden-cost, tool-bootstrap-effect, precision-over-recall, tool-workflow-composition, link-decay-laws, counterfactual-debt-analysis, experience-transfer-mapping） |
| 新建代码模式 | 1个（periodic-check-caching） |
| 覆盖已有模式 | 3个（relative-depth-adjustment, toolchain-maturity, methodology-critical-mass） |
| 合计归档 | 12个模式引用（8新建方法论+1新建代码+3已有覆盖），13条洞察100%归档 |

## 关联产出

- 建议层元洞察（6条）已原子化至 [../suggestions/](../suggestions/README.md) 目录（6条全部归档）
- 可复用模式已归档至全局模式库 [patterns/](../../../../../patterns/README.md)
- 治理规范已固化至 [development-standards.md](../../../../../../development-standards.md)

---
*数据来源：链接修复深度调整复盘（14个断链100%修复，工具链从L2跃迁至L5）*
