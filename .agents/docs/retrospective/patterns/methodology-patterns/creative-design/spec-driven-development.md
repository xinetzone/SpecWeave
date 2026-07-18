---
id: "spec-driven-development"
title: "Spec-driven 开发流程"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md#三、可复用方法论; SpecWeave 13天全生命周期复盘量化验证"
maturity: "L3"
tags: ["spec-driven", "development-process", "planning", "quality", "creative-design"]
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.toml"
---
# Spec-driven 开发流程

## 模式类型
创意设计与开发流程模式

## 成熟度
**L3 标准化**（111个Spec 87%完成度验证 + SpecWeave 13天793次提交大规模实践，本次全生命周期复盘本身使用Spec Mode）

## 量化验证结论
- **验证规模**：SpecWeave项目累计创建111个Spec，整体完成度87%
- **质量提升**：Spec先行的任务返工率显著低于无Spec直接执行的任务
- **自验证案例**：本次13天全生命周期复盘本身全程使用Spec Mode执行，从规划到交付全程遵循spec三件套流程
- **复用验证**：Wiki教程生产、功能开发、复盘报告、模式萃取等多类任务均验证有效

## 待跨场景验证项
- [ ] 在非AI辅助开发场景（纯人类开发者团队）中验证有效性
- [ ] 在超大型项目（>10人月）中验证Spec维护成本收益比
- [ ] 在需求高度不确定的探索性项目中验证（是否需要更轻量的规划方式）

## 来源
多个项目的完整开发过程验证，包括SpecWeave本体、59个Wiki教程生产、14+ Skill开发、150+脚本工具开发。

## 核心思想

"理解需求"与"执行任务"解耦——先想清楚做什么、怎么验证，再动手做。通过规格三件套（spec.md + tasks.md + checklist.md）将隐性的规划过程显性化，减少返工和沟通成本。

## 流程图
```mermaid
flowchart LR
    A["需求分析"] --> B["spec.md<br/>需求规格<br/>(做什么+为什么)"]
    B --> C["tasks.md<br/>任务分解<br/>(步骤+依赖+验收)"]
    C --> D["checklist.md<br/>验证清单<br/>(DoD完成定义)"]
    D --> E["实施<br/>按tasks执行"]
    E --> F["验证<br/>按checklist逐项打勾"]
    F --> G["交付"]
    style A fill:#fff3e0,stroke:#ff9800
    style B fill:#e3f2fd,stroke:#2196f3
    style C fill:#e3f2fd,stroke:#2196f3
    style D fill:#e3f2fd,stroke:#2196f3
    style E fill:#f3e5f5,stroke:#9c27b0
    style F fill:#e8f5e9,stroke:#4caf50
    style G fill:#e8f5e9,stroke:#4caf50
```

## 三件套说明

| 文件 | 核心问题 | 内容要点 |
|------|---------|---------|
| **spec.md** | 做什么？为什么做？ | 背景、目标、范围、非目标、核心需求、验收标准 |
| **tasks.md** | 怎么做？分几步？ | 任务拆解、依赖关系、优先级、每个任务的完成定义 |
| **checklist.md** | 怎么算做完了？ | DoD完成定义、质量门禁、验证步骤、发布检查项 |

## 关键原则

1. **理解与执行解耦**：规格阶段专注需求表达和方案设计，不写代码/不做具体实施；实施阶段专注机械执行，不临时大改需求
2. **验证标准前置**：checklist在规格阶段即编写，不随实施结果调整——不能做完了再改验收标准
3. **需求冻结机制**：进入实施阶段后原则上不修改spec核心需求；如需变更走正式变更流程（更新spec→评估影响→更新tasks/checklist）
4. **单一职责**：每个Spec对应一个独立的变更单元，不把多个不相关的任务塞进同一个Spec
5. **即时验证**：完成一个task立即验证，不要等全部做完再统一验证

## Spec Mode五阶段标准工作流

针对AI协作场景，Spec Mode扩展为五阶段闭环：

| 阶段 | 动作 | 产出 |
|------|------|------|
| **阶段0：内容提取** | 收集上下文、读取相关规范和现有文档 | 完整的上下文理解 |
| **阶段1：规范阅读** | 按启动协议读取AGENTS.md和对应任务类型的规范 | 明确约束和规则 |
| **阶段2：Spec三件套** | 创建spec.md + tasks.md + checklist.md，通过用户审核 | 批准的执行计划 |
| **阶段3：原子执行** | 按tasks逐项执行，每个task完成即时验证 | 完成的产出物 |
| **阶段4：验证收尾** | 按checklist逐项验证，运行自动化检查，更新索引 | 交付物+验证记录 |

## 复用场景

- 任何需要"先设计后实施"的开发任务
- AI辅助开发场景（减少sub-agent跑偏）
- 大型文档生产任务（如批量Wiki教程）
- 复盘报告、模式萃取等知识生产任务
- 需要明确验收标准的跨角色协作任务

## 反模式

| 反模式 | 表现 | 后果 |
|--------|------|------|
| **边做边想** | 不写spec直接动手，做一步想一步 | 返工率高，做出来的东西偏离需求 |
| **Spec过度详细** | spec写成实现设计，规定了每个函数怎么写 | 抑制执行者的创造力，spec维护成本高 |
| **Checklist事后补** | 做完了再写checklist，照着完成的结果勾 | 验证失去意义，无法保证质量 |
| **Spec写完就扔** | 实施过程中不看spec，凭记忆做 | spec与实际产出脱节，失去指导意义 |
| **巨型Spec** | 一个Spec包含几十个任务、跨多个主题 | 任务依赖混乱，进度无法追踪，容易半途而废 |

## 关联模式
- [spec-mode-doc-creation-workflow.md](../ai-collaboration/spec-mode-doc-creation-workflow.md)：Spec Mode文档创建五阶段工作流
- [two-stage-outline-then-expand.md](../ai-collaboration/two-stage-outline-then-expand.md)：两阶段大纲展开模式（Spec的简化版）
- [batched-creation-independent-review.md](../ai-collaboration/batched-creation-independent-review.md)：分批创作+独立质检模式
- [spec-three-sync.md](../governance-strategy/spec-triple-sync.md)：规范三同步原则（新规范发布必须更新索引）
