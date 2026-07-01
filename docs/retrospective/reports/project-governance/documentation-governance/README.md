---
id: "documentation-governance-index"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/README.toml"
---
# 文档体系治理

> 本主题存放文档体系治理相关复盘报告，涵盖文档结构优化、品牌命名一致性、重复内容清理、链接自动修复、Mermaid渲染兼容性、洞察库重组等文档质量保障工作。
>
> 本主题共包含 8 份报告（7个目录+1个独立文件），记录了文档体系从规划到持续优化的完整治理过程，其中 Mermaid 安全编码五规则是高频复用的实践指南。

## 报告列表

| 报告 | 日期 | 核心内容 | 子模块导航 |
|------|------|---------|-----------|
| [retrospective-report-document-dedup-insights-20260626/](retrospective-report-document-dedup-insights-20260626/) | 2026-06-26 | 文档重复内容治理洞察萃取，提炼去冗余方法论、五阶段执行法、三角验证法 | [README](retrospective-report-document-dedup-insights-20260626/README.md) · [execution-retrospective.md](retrospective-report-document-dedup-insights-20260626/execution-retrospective.md) · [insight-extraction.md](retrospective-report-document-dedup-insights-20260626/insight-extraction.md) · [export-suggestions.md](retrospective-report-document-dedup-insights-20260626/export-suggestions.md) |
| [reports-duplication-optimization-report.md](reports-duplication-optimization-report.md) | 2026-06-24 | 复盘报告体系重复内容优化，移除冗余引用块、精简导航结构 | 独立文件 |
| [retrospective-report-system-planning/](retrospective-report-system-planning/) | 2026-06-23 | README系统规划章节设计，四层闭环架构 | [README](retrospective-report-system-planning/README.md) · [execution-retrospective.md](retrospective-report-system-planning/execution-retrospective.md) · [insight-extraction.md](retrospective-report-system-planning/insight-extraction.md) · [export-suggestions.md](retrospective-report-system-planning/export-suggestions.md) |
| [retrospective-readme-sync-and-brand-naming-20260624/](retrospective-readme-sync-and-brand-naming-20260624/) | 2026-06-24 | README同步与SpecWeave品牌命名一致性修复 | [README](retrospective-readme-sync-and-brand-naming-20260624/README.md) · [execution-retrospective.md](retrospective-readme-sync-and-brand-naming-20260624/execution-retrospective.md) · [insight-extraction.md](retrospective-readme-sync-and-brand-naming-20260624/insight-extraction.md) · [export-suggestions.md](retrospective-readme-sync-and-brand-naming-20260624/export-suggestions.md) |
| [retrospective-report-four-topic-structure-optimization-20260624/](retrospective-report-four-topic-structure-optimization-20260624/) | 2026-06-24 | 复盘报告四主题结构优化推广，24个project-overview合并、23个连接器删除 | [README](retrospective-report-four-topic-structure-optimization-20260624/README.md) · [execution-retrospective.md](retrospective-report-four-topic-structure-optimization-20260624/execution-retrospective.md) · [insight-extraction.md](retrospective-report-four-topic-structure-optimization-20260624/insight-extraction.md) · [export-suggestions.md](retrospective-report-four-topic-structure-optimization-20260624/export-suggestions.md) |
| [retrospective-insights-reorg-20260626/](retrospective-insights-reorg-20260626/) | 2026-06-26 | 竹简悟道洞察库重组，从2个失衡文件重组为3个四层结构均衡文件 | [README](retrospective-insights-reorg-20260626/README.md) · [execution-retrospective.md](retrospective-insights-reorg-20260626/execution-retrospective.md) · [insight-extraction.md](retrospective-insights-reorg-20260626/insight-extraction.md) · [export-suggestions.md](retrospective-insights-reorg-20260626/export-suggestions.md) |
| [retrospective-link-fix-depth-adjustment-20260626/](retrospective-link-fix-depth-adjustment-20260626/) | 2026-06-26 | 断链修复与链接自动校正工具增强，新增try_adjust_relative_depth()算法 | [README](retrospective-link-fix-depth-adjustment-20260626/README.md) · [execution-retrospective.md](retrospective-link-fix-depth-adjustment-20260626/execution-retrospective.md) · [insight-extraction.md](retrospective-link-fix-depth-adjustment-20260626/insight-extraction.md) · [export-suggestions.md](retrospective-link-fix-depth-adjustment-20260626/export-suggestions.md) |
| [retrospective-mermaid-rendering-fix-20260626/](retrospective-mermaid-rendering-fix-20260626/) | 2026-06-26 | Mermaid渲染兼容性修复，提炼安全编码五规则与陷阱速查表，已原子化insights/和suggestions/子目录 | [README](retrospective-mermaid-rendering-fix-20260626/README.md) · [execution-retrospective.md](retrospective-mermaid-rendering-fix-20260626/execution-retrospective.md) · [insight-extraction.md](retrospective-mermaid-rendering-fix-20260626/insight-extraction.md) · [export-suggestions.md](retrospective-mermaid-rendering-fix-20260626/export-suggestions.md) · [insights/](retrospective-mermaid-rendering-fix-20260626/insights/) · [suggestions/](retrospective-mermaid-rendering-fix-20260626/suggestions/) |

## 高频复用资产

| 资产 | 位置 | 用途 |
|------|------|------|
| Mermaid安全编码五规则 | [retrospective-mermaid-rendering-fix-20260626/](retrospective-mermaid-rendering-fix-20260626/) | 编写Mermaid图表时避免95%渲染失败 |
| 链接自动校正算法 | [retrospective-link-fix-depth-adjustment-20260626/](retrospective-link-fix-depth-adjustment-20260626/) | 相对路径深度自动调整 |
| 文档结构优化方法论 | [retrospective-report-four-topic-structure-optimization-20260624/](retrospective-report-four-topic-structure-optimization-20260624/) | 大规模文档重组参考 |

---
[返回项目治理报告索引](../README.md)
