---
id: "retrospective-zhujian-wudao-specs-analysis-20260625-insight-e"
title: "洞察 E：双受众萃取模型——一次投入，两类资产"
source: "insight-extraction.md#核心洞察E"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-zhujian-wudao-specs-analysis-20260625/insights/dual-audience-extraction-model.toml"
---
# 洞察 E：双受众萃取模型——一次投入，两类资产

**发现**：竹简悟道在萃取可迁移资产时，同时产出了面向两个不同受众的文档：
- transferable-patterns.md：面向 AI Agent（模板化、占位符、可直接套用）
- transferable-methods.md：面向人类开发者（原理解释、迁移指南、适用场景判断）

## 双受众对比

| 维度 | 面向 Agent（patterns） | 面向人类（methods） |
|------|---------------------|-------------------|
| 核心目标 | 可直接复制替换 | 理解后适配 |
| 内容形态 | 代码块/模板 + `{占位符}` | 方法论阐述 + 迁移方式说明 |
| 结构 | 9章：骨架→洞察→复盘→同步→交付→打包→约束→词典→使用指南 | 10章：流程→模板→基础设施→命名→禁令→设计→文档→元分析→熵→迁移矩阵 |
| 使用方式 | Agent 读取后直接创建文件结构 | 人类阅读后理解原则再灵活应用 |
| 抽象级别 | 高抽象（去主题化） | 中抽象（保留原理说明） |
| 示例 | 提供 AGENTS.md 完整模板含占位符 | 解释"为什么 AGENTS.md 要控制在60行以内" |

## 关键洞察

面向AI的模板和面向人类的方法论不是"简化版vs详细版"的关系，而是两种不同的知识形态——AI需要可执行的结构，人类需要可理解的原理。两者分开撰写比试图用一份文档同时服务两类读者效果更好。

## 可迁移性

**高**。任何需要沉淀方法论的项目都应考虑双受众萃取。

---
*所属报告：[竹简悟道 Specs 文档体系深度分析复盘](../README.md)*
