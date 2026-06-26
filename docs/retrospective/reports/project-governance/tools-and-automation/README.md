+++
id = "tools-and-automation-index"
date = "2026-06-26"
type = "index"
topic = "tools-and-automation"
+++

# 工具与自动化治理

> 本主题存放工具与自动化治理相关复盘报告，涵盖工具熵的非线性优化规律、自动化文档生成、共享代码库提取等内容。重点记录了自动化规模不经济现象与系统性重复消除方法，为工具建设的ROI评估与代码可维护性提升提供决策依据。
>
> 本主题共包含 3 份报告，记录了从工具熵理论到共享库提取的探索过程。

## 报告列表

| 报告目录 | 日期 | 核心内容 | 子模块导航 |
|---------|------|---------|-----------|
| [retrospective-report-tool-entropy-nonlinear-optimization/](retrospective-report-tool-entropy-nonlinear-optimization/) | 2026-06-23 | 工具熵非线性优化，自动化规模不经济规律 | [README](retrospective-report-tool-entropy-nonlinear-optimization/README.md) · [execution-retrospective.md](retrospective-report-tool-entropy-nonlinear-optimization/execution-retrospective.md) · [insight-extraction.md](retrospective-report-tool-entropy-nonlinear-optimization/insight-extraction.md) · [export-suggestions.md](retrospective-report-tool-entropy-nonlinear-optimization/export-suggestions.md) |
| [retrospective-report-code-wiki-generation/](retrospective-report-code-wiki-generation/) | 2026-06-24 | Code Wiki自动化文档生成任务 | [README](retrospective-report-code-wiki-generation/README.md) · [execution-retrospective.md](retrospective-report-code-wiki-generation/execution-retrospective.md) · [insight-extraction.md](retrospective-report-code-wiki-generation/insight-extraction.md) · [export-suggestions.md](retrospective-report-code-wiki-generation/export-suggestions.md) |
| [retrospective-scripts-shared-lib-extraction-20260626/](retrospective-scripts-shared-lib-extraction-20260626/) | 2026-06-26 | 24 脚本共享库提取，12 类重复模式消除，发现路径解析 bug | [README](retrospective-scripts-shared-lib-extraction-20260626/README.md) · [execution-retrospective.md](retrospective-scripts-shared-lib-extraction-20260626/execution-retrospective.md) · [insight-extraction.md](retrospective-scripts-shared-lib-extraction-20260626/insight-extraction.md) · [export-suggestions.md](retrospective-scripts-shared-lib-extraction-20260626/export-suggestions.md) |

## 核心概念

| 概念 | 来源报告 | 说明 |
|------|---------|------|
| 工具熵 | retrospective-report-tool-entropy-nonlinear-optimization | 工具数量增长带来的认知负担与维护成本非线性上升 |
| 自动化规模不经济 | retrospective-report-tool-entropy-nonlinear-optimization | 超过临界点后，新增自动化工具带来的收益递减甚至为负 |
| ROI驱动自动化 | retrospective-report-tool-entropy-nonlinear-optimization | 工具建设前需评估触发条件（如3次手动）与投资回报 |
| 共享库引力效应 | retrospective-scripts-shared-lib-extraction-20260626 | 共享库覆盖面越大，新脚本使用共享库概率越高，形成正反馈循环 |
| 重构三层价值 | retrospective-scripts-shared-lib-extraction-20260626 | 重构价值 = 消除重复 + 发现隐藏 bug + 建立结构基础，仅评估第一层低估 ROI 约 50% |
| 重复代码 3 次阈值 | retrospective-scripts-shared-lib-extraction-20260626 | 同一模式出现 ≥3 次时提取 ROI 转正，1-2 次可暂缓 |

---
[返回项目治理报告索引](../README.md)
