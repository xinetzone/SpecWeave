---
id: "analysis-cards-readme"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/analysis-cards/README.toml"
---
# 分析卡片库（analysis-cards）

本目录存放轻量级分析工具卡片，用于竞品分析、产品评估、战略判断等场景的快速决策参考。

## 与模式（patterns）的区别

| 维度 | 分析卡片（analysis-cards） | 模式（patterns） |
|------|--------------------------|-----------------|
| **格式** | YAML frontmatter，轻量 | TOML frontmatter，结构化 |
| **目的** | 快速分析判断、信号提取 | 可复用执行流程、最佳实践 |
| **验证要求** | validation_count≥1即可入库 | 需经多轮验证逐步升级成熟度 |
| **典型内容** | 判断矩阵、信号清单、分级模型 | 完整工作流、正反例、检查清单 |

## 卡片索引

| 卡片文件 | 一句话说明 | 成熟度 |
|---------|-----------|--------|
| [dual-track-sdk-strategy-framework.md](dual-track-sdk-strategy-framework.md) | 双轨SDK策略识别框架：OpenAI兼容+原生SDK双轨战略L1-L4四级成熟度模型，6项信号清单快速判断平台生态策略阶段 | L1 |
| [default-config-values-probe.md](default-config-values-probe.md) | 默认配置价值观探针：从默认选择/默认参数/默认关闭三层次穿透营销话术，识别产品团队真实优先级和价值观 | L1 |
| [feature-layering-maturity-framework.md](feature-layering-maturity-framework.md) | 功能分层成熟度框架：通过文档/UI功能分层方式判断产品成熟度L1-L4四阶段，5项判断信号快速评估 | L1 |
| [css-stacking-context-overflow-clipping.md](css-stacking-context-overflow-clipping.md) | CSS层叠上下文与overflow裁剪知识卡片：澄清“z-index穿不过overflow:hidden”的根因，给出结构隔离与诊断决策树 | L1 |

## 使用方式

1. 根据分析场景选择对应卡片
2. 按卡片中的信号清单/判断矩阵提取信息
3. 对照分级模型快速得出结论
4. 与分析报告/洞察萃取结合使用
