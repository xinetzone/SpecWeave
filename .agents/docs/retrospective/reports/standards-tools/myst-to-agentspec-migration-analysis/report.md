---
id: "myst-to-agentspec-migration-analysis"
title: "MyST Directives/Roles 系统在 Agent Spec 开发中的可迁移性技术评估"
source: "Task 1 基线数据分析 + MyST 语法规范研究 + 现有解析器代码审计 + 六维技术支持评估 + LLM融合创新场景研究 + MyST-NB可执行notebook能力分析"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/standards-tools/myst-to-agentspec-migration-analysis/report.toml"
---

# MyST Directives/Roles 系统在 Agent Spec 开发中的可迁移性技术评估

## 摘要

本报告基于对现有 SpecWeave 解析器架构（file:///d:/spaces/SpecWeave/.agents/scripts/mdi/parser.py）的代码审计、66份存量文档（52个spec.md + 14个SKILL.md）的统计分析，以及MyST Markdown语法规范的系统研究，全面评估了MyST Directives/Roles系统在Agent Spec开发中的可迁移性。研究发现：现有解析器已具备基础Directive识别能力但使用率为0%，表格是当前核心结构化元素（spec.md平均0.67个/文档，SKILL.md平均3.79个/文档）；mdit-py-plugins 0.5.0生态提供colon_fence插件但未启用；当前仅支持反引号围栏和`:key: value`选项格式，不支持冒号围栏、YAML选项块、内联选项和Roles语法。

v1.1.0版本新增六维技术支持深度评估（MDI/API/ABI/MCP/ACP/A2A）和LLM×Sphinx/MyST生态融合创新场景分析。六维评估显示MDI/API/MCP/A2A四个维度对Agent开发具有P0/P1高价值，其中MCP维度的"文档即MCP Server"构想最具创新性；LLM融合场景分析识别出七个高潜力方向，"基于MDI的智能代码生成"价值最高。

v1.2.0版本补充MyST-NB可执行notebook能力专题分析。MyST-NB作为Executable Books项目的Sphinx扩展，提供code-cell可执行代码块、glue变量绑定、inline eval内联计算等核心能力，为"计算性叙事"和可执行Spec文档开辟了新思路。分析表明MyST-NB的思想高度适配Agent Spec场景（API示例可执行验证、MCP工具测试用例嵌入、性能数据动态绑定），但其依赖的Sphinx/docutils/Jupyter生态与当前轻量架构存在冲突，建议采取"灵感借鉴而非直接引入"策略，在markdown-it-py架构上实现精简版exec/glue-simple概念。报告提出"可执行Spec文档"创新场景，为SpecWeave未来演进提供了新方向。报告提出保守、平衡、激进三种实施方案，经技术权衡后推荐"平衡方案"并建议优先实现mcp域——选择性启用MyST核心特性而非引入完整myst-parser，在保持现有架构轻量性的同时，获得结构化表达能力和LLM增强的双重提升。

## 目录

本报告已按章节原子化拆分为独立文件，可按顺序阅读或按需查阅：

| 序号 | 章节 | 文件链接 | 核心内容 |
|---|---|---|---|
| 1 | 背景与上下文 | [01-background.md](01-background.md) | 项目现状统计、现有解析器架构特征、MyST核心概念（Directives/Roles/嵌套机制）简述 |
| 2 | 核心概念适配性分析 | [02-concept-adaptability.md](02-concept-adaptability.md) | 适配性评估方法论、核心概念映射矩阵、18+项Directives和12项Roles详细评估、适配性可视化Mermaid图 |
| 3 | 关键技术挑战 | [03-technical-challenges.md](03-technical-challenges.md) | 双围栏语法兼容、选项格式扩展、Roles解析缺口、扩展架构设计、存量迁移成本、错误恢复体验六大挑战 |
| 4 | 实施路径设计 | [04-implementation-paths.md](04-implementation-paths.md) | 保守/平衡/激进三种方案对比、实施决策树、推荐方案四里程碑详细路线图 |
| 5 | 架构兼容性分析 | [05-architecture-compatibility.md](05-architecture-compatibility.md) | mdit-py-plugins生态评估、不引入完整myst-parser的决策权衡、Lite/Standard/Full三类Profile配置、代码生成器和验证器增强点 |
| 6 | 优势与局限性评估 | [06-pros-and-limitations.md](06-pros-and-limitations.md) | 语义表达、行内标记、渐进采用、生态对齐、高级功能五大优势；学习成本、解析复杂度、降级效果、工具链、过度使用五大局限性；多维度权衡表格 |
| 7 | Agent开发场景化建议 | [07-scenario-recommendations.md](07-scenario-recommendations.md) | 接口定义、参数说明、提示框、SKILL文档、版本记录、错误码六大场景的正反例和使用规范 |
| 8 | 前瞻性洞察 | [08-forward-looking-insights.md](08-forward-looking-insights.md) | 从文档到可执行规范的跨越、表格向语义化指令演进、自定义Domain的核心价值、工具链的关键作用、Roles的被低估价值五大洞察 |
| 9 | 六维技术支持深度评估 | [09-six-dimensions-evaluation.md](09-six-dimensions-evaluation.md) | MDI/API/ABI/MCP/ACP/A2A六个技术维度的生态分析、Domain设计建议、代码示例、可行性评级与对比总表 |
| 10 | LLM×Sphinx/MyST生态融合创新场景 | [10-llm-sphinx-innovation.md](10-llm-sphinx-innovation.md) | 文档自动化生成、知识图谱提取、智能代码生成、交互式文档、Domain辅助扩展、mystmd运行时交互、AI增强引用导航七个创新场景，含PoC代码和优先级矩阵 |
| 11 | 结论与建议 | [11-conclusions.md](11-conclusions.md) | 十大核心结论、八条具体行动建议（含MCP域P0优先级调整、MyST-NB思想借鉴）、从"文档"到"文档即服务"的分阶段长期展望 |
| 12 | MyST-NB与可执行文档专题分析 | [12-myst-nb-executable-docs.md](12-myst-nb-executable-docs.md) | MyST-NB核心能力详解（code-cell/glue/inline eval/执行缓存）、在Agent Spec场景的适配性分析、轻量实现方案设计（exec/glue-simple/eval-inline）、概念验证代码示例、可行性评级与实施建议 |

## 阅读建议

- **快速了解**：先阅读本页摘要，再阅读[第11章结论与建议](11-conclusions.md)
- **技术决策**：重点阅读[第4章实施路径设计](04-implementation-paths.md)、[第5章架构兼容性分析](05-architecture-compatibility.md)和[第12章MyST-NB专题分析](12-myst-nb-executable-docs.md)
- **开发实践**：参考[第7章Agent开发场景化建议](07-scenario-recommendations.md)的正反例
- **前沿探索**：关注[第9章六维评估](09-six-dimensions-evaluation.md)（特别是MCP维度）、[第10章LLM融合创新](10-llm-sphinx-innovation.md)和[第12章可执行文档](12-myst-nb-executable-docs.md)
- **完整阅读顺序**：按序号从01到12顺序阅读，获得完整上下文

## 版本信息

- **版本**：1.2.0（MyST-NB可执行文档专题版）
- **完成日期**：2026年7月2日
- **数据基线**：Task 1 研究成果 + parser.py代码审计 + MyST语法规范研究 + 六维技术支持评估（MDI/API/ABI/MCP/ACP/A2A） + LLM×Sphinx/MyST融合创新场景研究 + MyST-NB可执行notebook能力分析
- **文件结构**：本索引页 + 12个章节原子文件
- **原始文档**：拆分前的完整版本已通过原子化重构为当前结构，内容无删减；v1.2.0新增第12章MyST-NB专题分析
