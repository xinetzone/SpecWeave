---
id: "feat-dev-01"
title: "01 变更类型判定与流程概览"
source: "workflows/feature-development.md#01"
x-toml-ref: "../../../.meta/toml/.agents/workflows/feature-development/01-change-type-overview.toml"
---

# 01 变更类型判定与流程概览


在启动任何开发任务前，orchestrator必须首先判定变更类型，选择对应的流程路径。

```mermaid
flowchart TD
    START["接收到开发需求"] --> Q1{"是从零构建<br/>全新能力?"}
    Q1 -->|"是"| NEW["新功能<br/>(New Feature)"]
    Q1 -->|"否"| Q2{"是否改动已有功能的<br/>核心结构/数据模型/接口契约?"}
    Q2 -->|"否"| EXT["功能扩展<br/>(Extension)"]
    Q2 -->|"是"| REF["功能重构<br/>(Refactoring)"]
    style NEW fill:#d5f5e3,stroke:#27ae60
    style EXT fill:#d6eaf8,stroke:#2980b9
    style REF fill:#fadbd8,stroke:#e74c3c
```

| 变更类型 | 定义 | 风险等级 | 流程路径 |
|---------|------|---------|---------|
| **新功能** | 从零构建的全新能力，不涉及已有功能的修改 | 中 | 完整8步流程 |
| **功能扩展** | 在已有功能上新增能力，不破坏现有结构和接口 | 低 | 轻量6步流程 |
| **功能重构** | 改动已有功能的核心结构、数据模型或接口契约，可能影响现有行为 | 高 | 重量7步流程 |

**判定依据必须记录在任务分解清单中。**

---

### 新功能完整流程（8步）

```mermaid
flowchart TD
    A["①需求接收<br/>orchestrator"] --> B["②方案设计<br/>architect"]
    B --> C["③任务分配<br/>orchestrator"]
    C --> D["④代码实现<br/>developer"]
    D --> E["⑤测试编写<br/>tester"]
    E --> F["⑥代码审查<br/>reviewer"]
    F -->|"通过"| G["⑦合并代码<br/>orchestrator"]
    F -->|"不通过"| D
    G --> H["⑧完成确认<br/>orchestrator"]
```

### 功能扩展轻量流程（6步）

```mermaid
flowchart TD
    A1["E1 影响分析<br/>developer"] --> B1["E2 增量方案<br/>architect"]
    B1 --> D1["E3 增量实现<br/>developer"]
    D1 --> E1t["E4 回归测试<br/>tester"]
    E1t --> F1["E5 增量审查<br/>reviewer"]
    F1 -->|"通过"| G1["E6 合并<br/>orchestrator"]
    F1 -->|"不通过"| D1
    style A1 fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
    style B1 fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
    style D1 fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
    style E1t fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
    style F1 fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
    style G1 fill:#d6eaf8,stroke:#2980b9,stroke-dasharray:5
```

### 功能重构重量流程（7步）

```mermaid
flowchart TD
    A2["R1 全量影响评估<br/>architect"] --> B2["R2 方案重审<br/>architect + reviewer"]
    B2 --> C2["R3 全量重规划<br/>orchestrator"]
    C2 --> D2["R4 实现+迁移<br/>developer"]
    D2 --> E2["R5 全量回归<br/>tester"]
    E2 --> F2["R6 双重审查<br/>reviewer + architect"]
    F2 -->|"通过"| G2["R7 合并<br/>orchestrator"]
    F2 -->|"不通过"| D2
    style A2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style B2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style C2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style D2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style E2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style F2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
    style G2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px
```

---

| 角色 | 新功能 | 功能扩展 | 功能重构 |
|---|---|---|---|
| orchestrator | 需求接收、任务分配、合并、确认 | 指派任务、合并 | 重规划、合并 |
| architect | 方案设计 | 增量方案确认 | 全量评估、方案重审 |
| developer | 代码实现 | 影响分析+增量实现 | 实现+数据迁移 |
| tester | 测试编写 | 新增测试+回归测试 | 全量回归测试 |
| reviewer | 代码审查 | 增量审查 | 双重审查（代码+架构） |

---

---

## 相关模式

- [学习-验证-采用](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/learn-validate-adopt.md)
- [两阶段处理](../../docs/retrospective/patterns/methodology-patterns/document-architecture/two-phase-processing.md)
---

**[返回索引](../feature-development.md)** | 下一章: [02 新功能完整流程（8步）](02-new-feature-flow.md) →
