# 方法论模式

> 可复用的开发方法论与工作流程模式，每个模式描述一个经过验证的"如何做"指南。

## 主题导航

按核心主题思想分类，共7个主题类别，便于按场景快速定位相关模式：

| 主题目录 | 中文名称 | 模式数 | 核心描述 | 详细列表 |
|---------|---------|-------|---------|---------|
| retrospective-knowledge | 复盘与知识生命周期 | 26 | 项目复盘、知识萃取、洞察沉淀、经验迁移 | [查看](CATEGORIES.md#retrospective-knowledge--复盘与知识生命周期) |
| document-architecture | 文档架构与原子化 | 21 | 文档重构、原子化拆分、文档治理、结构设计 | [查看](CATEGORIES.md#document-architecture--文档架构与原子化) |
| tools-automation | 工具工程与自动化 | 18 | 工具决策、自动化、工具链、安全修改 | [查看](CATEGORIES.md#tools-automation--工具工程与自动化) |
| governance-strategy | 治理与优先级策略 | 21 | 治理模型、优先级决策、问题解决、流程规范 | [查看](CATEGORIES.md#governance-strategy--治理与优先级策略) |
| ai-collaboration | AI协作与提示词设计 | 10 | AI Skill设计、提示词工程、人机协作 | [查看](CATEGORIES.md#ai-collaboration--ai协作与提示词设计) |
| creative-design | 创意与设计原则 | 7 | 视觉设计、认知锚点、角色设计、创造力 | [查看](CATEGORIES.md#creative-design--创意与设计原则) |
| product-growth | 产品开发与竞争策略 | 7 | 产品Spec、增长、赛事、定位、交付 | [查看](CATEGORIES.md#product-growth--产品开发与竞争策略) |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 主题关系图

方法论体系按线性递进关系组织，前序主题为后序主题提供基础支撑，同时各主题通过复盘反哺上游：

```mermaid
flowchart LR
    KM["📚 复盘与知识生命周期"]
    DOC["📄 文档架构与原子化"]
    TOOL["🔧 工具工程与自动化"]
    GOV["⚖️ 治理与优先级策略"]
    AI["🤖 AI协作与提示词设计"]
    DESIGN["🎨 创意与设计原则"]
    PROD["🚀 产品开发与竞争策略"]
    KM -->|"知识萃取沉淀"| DOC
    DOC -->|"结构化支撑"| TOOL
    TOOL -->|"自动化提效"| GOV
    GOV -->|"决策框架"| AI
    AI -->|"协作模式"| DESIGN
    DESIGN -->|"方法论落地"| PROD
    PROD -.->|"业务场景反哺"| KM
    DESIGN -.->|"创意验证反馈"| DOC
    AI -.->|"协作痛点驱动"| TOOL
    GOV -.->|"治理缺口识别"| KM
    TOOL -.->|"工具能力边界"| GOV
```

**说明**：线性主链路为「复盘知识 → 文档治理 → 工具自动化 → 治理策略 → AI协作 → 创意设计 → 产品增长」，代表方法论从知识沉淀到业务落地的正向演进。虚线为反哺回路：产品实践产生的新经验回流到复盘环节，设计验证发现的问题回流到文档治理，以此形成持续优化的闭环。

## 使用指南

1. **首次使用**：从 [creative-design/spec-driven-development.md](creative-design/spec-driven-development.md) 开始，它是所有模式的基础。
2. **项目复盘**：参考 [retrospective-knowledge/review-insight-export-loop.md](retrospective-knowledge/review-insight-export-loop.md) 的结构模板。
3. **文档优化**：遇到大型文档需要拆分时，使用 [document-architecture/document-system-refactoring.md](document-architecture/document-system-refactoring.md) 和 [governance-strategy/three-tier-governance.md](governance-strategy/three-tier-governance.md)。
4. **工具决策**：不确定是否值得自动化时，参考 [tools-automation/tool-automation-decision-model.md](tools-automation/tool-automation-decision-model.md)。
5. **文档修正**：修正文档中的事实表述时，使用 [document-architecture/fact-statement-consistency-loop.md](document-architecture/fact-statement-consistency-loop.md) 确保全局一致性。
6. **模块扩展**：在成熟规范体系内创建新模块时，使用 [governance-strategy/convention-driven-creation.md](governance-strategy/convention-driven-creation.md) 实现零结构决策。
7. **安全设计**：涉及特权操作的模块，使用 [governance-strategy/spec-level-defense-in-depth.md](governance-strategy/spec-level-defense-in-depth.md) 设计四维防护。
8. **赛事运营**：设计产品驱动赛事时，使用 [product-growth/contest-growth-flywheel.md](product-growth/contest-growth-flywheel.md) 和 [product-growth/contest-funnel-aperture.md](product-growth/contest-funnel-aperture.md)。
9. **UGC 传播**：需要撬动用户传播时，使用 [product-growth/controlled-uncontrollable-ugc-rules.md](product-growth/controlled-uncontrollable-ugc-rules.md)。
10. **增长设计**：评估转化节点摩擦时，使用 [creative-design/intentional-friction-design.md](creative-design/intentional-friction-design.md)。
11. **改进价值论证**：需要说服团队投入资源做系统性改进时，使用 [retrospective-knowledge/counterfactual-debt-analysis.md](retrospective-knowledge/counterfactual-debt-analysis.md) 推演不做的复利代价。
12. **模式萃取质量**：评估洞察是否值得归档为全局模式时，使用 [retrospective-knowledge/experience-transfer-mapping.md](retrospective-knowledge/experience-transfer-mapping.md) 做跨领域迁移映射验证通用性。

> **关联模块**：
> - `../../code-patterns/` — 代码模式
> - `../../architecture-patterns/` — 架构模式
> - `../../../frameworks/` — 决策框架
> - `../../../concepts/` — 知识概念
