---
id: "dual-audience-extraction-model"
source: "docs/retrospective/reports/insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/insights/dual-audience-extraction-model.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/document-architecture/dual-audience-extraction-model.toml"
---
# 双受众萃取模型：一次投入，两类资产

## 模式概述

萃取可迁移资产时，同时产出面向两个不同受众的文档——面向 AI Agent（模板化、占位符、可直接套用）和面向人类开发者（原理解释、迁移指南、适用场景判断）。两者不是"简化版vs详细版"的关系，而是两种不同的知识形态。

## 双受众对比

| 维度 | 面向 Agent（patterns/templates） | 面向人类（methods/playbooks） |
|------|---------------------------------|-------------------------------|
| 核心目标 | 可直接复制替换 | 理解后适配 |
| 内容形态 | 代码块/模板 + `{占位符}` | 方法论阐述 + 迁移方式说明 |
| 结构 | 固定骨架：骨架→洞察→复盘→交付→约束 | 解释性结构：流程→模板→命名→禁令→设计 |
| 使用方式 | Agent 读取后直接创建文件结构 | 人类阅读后理解原则再灵活应用 |
| 抽象级别 | 高抽象（去主题化） | 中抽象（保留原理说明） |
| 示例 | 提供 AGENTS.md 完整模板含占位符 | 解释"为什么 AGENTS.md 要控制在60行以内" |

## 关键洞察

面向AI的模板和面向人类的方法论必须分开撰写。试图用一份文档同时服务两类读者会导致：
- AI无法提取可执行结构（被自然语言解释干扰）
- 人类无法理解设计原理（被模板占位符干扰）

## 典型结构参考

**面向Agent的模板集（9章结构）**：
1. 项目骨架（AGENTS.md等入口文件）
2. 洞察模板
3. 复盘SOP
4. 文档同步
5. 交付打包
6. 约束清单
7. 词典模板
8. 使用指南

**面向人类的方法论集（10章结构）**：
1. 核心流程
2. 模板设计原理
3. 基础设施
4. 命名规范
5. 禁止事项
6. 设计原则
7. 文档体系
8. 元分析
9. 熵管理
10. 迁移矩阵

## 适用场景

- 需要沉淀方法论的项目（高适用性）
- 既要给AI用又要给人看的知识库
- 开源项目文档（用户是人，贡献者可能用AI）
- 内部方法论资产化

## 反例

- 写一份"详细的README"，期望AI和人都能看懂——结果AI抓不到结构，人找不到重点
- 只写模板不写原理——别人不知道什么时候该用、什么时候不该用
- 只写原理不写模板——AI无法直接执行

> 来源：竹简悟道 transferable-patterns.md（Agent模板）+ transferable-methods.md（人类方法论）双文档实践
> 关联模式：`review-insight-export-loop`、`extraction-four-layer-funnel`、`three-tier-knowledge-sedimentation`
