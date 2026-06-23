# 硬编码治理规则体系

本目录收录了项目硬编码治理的完整规则体系，涵盖识别标准、允许场景、替代方案、检测报告与执行验证五大核心模块。所有开发者和智能体在编写、审查、重构代码时，均应参照本规则体系确保硬编码问题得到系统性管理。

## 规则体系架构

```mermaid
flowchart TD
    subgraph 编码阶段
        A[identification-standards.md<br/>硬编码识别标准] --> B[alternatives-guide.md<br/>替代方案指南]
    end

    subgraph 审查阶段
        C[allowable-scenarios.md<br/>允许场景与审批] --> D[enforcement-guidelines.md<br/>执行与验证规则]
    end

    subgraph 治理阶段
        E[detection-and-reporting.md<br/>检测与报告机制]
    end

    A --> |"判断是否为硬编码"| F{是否允许场景内?}
    F --> |"是"| C
    F --> |"否"| B
    B --> |"实施替代方案"| G[代码提交]
    C --> |"标记例外或批准"| G
    G --> |"触发"| E
    E --> |"反馈结果"| D
    D --> |"趋势数据"| H[迭代复盘与改进]
```

## 规则文档清单

| 文档 | 用途 | 适用阶段 | 适用角色 |
|---|---|---|---|
| [identification-standards.md](./identification-standards.md) | 定义 8 大类硬编码的识别标准、正例反例、检测要点 | 编码、审查 | developer, reviewer |
| [allowable-scenarios.md](./allowable-scenarios.md) | 规定允许硬编码的 4 类场景、例外审批流程、例外清单模板 | 审查 | developer, reviewer, architect, orchestrator |
| [alternatives-guide.md](./alternatives-guide.md) | 提供 7 种替代方案的实施指南、代码示例、模板脚手架 | 编码、重构 | developer |
| [detection-and-reporting.md](./detection-and-reporting.md) | 建立三层检测体系（自动化扫描、人工审查、定期报告）的规范 | 全阶段 | developer, reviewer, orchestrator |
| [enforcement-guidelines.md](./enforcement-guidelines.md) | 定义 6 条可执行治理规则、验证手段、合规等级 | 全阶段 | 全部角色 |

## 快速导航

### 按场景导航

| 场景 | 应查阅的文档 |
|---|---|
| 我不确定这段代码算不算硬编码 | [identification-standards.md](./identification-standards.md) |
| 我需要写一段包含固定值的代码，怎么替代？ | [alternatives-guide.md](./alternatives-guide.md) |
| 我这个硬编码确实无法替代，怎么申请例外？ | [allowable-scenarios.md](./allowable-scenarios.md) |
| 我作为 reviewer 怎么审查硬编码问题？ | [identification-standards.md](./identification-standards.md) + [enforcement-guidelines.md](./enforcement-guidelines.md) |
| 我想知道项目硬编码的整体趋势 | [detection-and-reporting.md](./detection-and-reporting.md) |
| 我想建立自动化硬编码检测 | [detection-and-reporting.md](./detection-and-reporting.md) |
| 我不遵守规则会有什么后果？ | [enforcement-guidelines.md](./enforcement-guidelines.md) |

### 按角色导航

| 角色 | 编码阶段 | 审查阶段 | 治理阶段 |
|---|---|---|---|
| **developer** | identification-standards.md<br/>alternatives-guide.md | allowable-scenarios.md<br/>enforcement-guidelines.md | detection-and-reporting.md |
| **reviewer** | identification-standards.md | allowable-scenarios.md<br/>enforcement-guidelines.md | - |
| **architect** | - | allowable-scenarios.md<br/>enforcement-guidelines.md | detection-and-reporting.md |
| **orchestrator** | - | allowable-scenarios.md | detection-and-reporting.md<br/>enforcement-guidelines.md |
| **tester** | - | enforcement-guidelines.md | - |

## 规则体系使用流程

### 流程一：新功能开发

```mermaid
flowchart LR
    A[查阅识别标准] --> B[参考替代方案指南]
    B --> C[编写代码]
    C --> D[提交前自查]
    D --> E{自查通过?}
    E -->|"否"| B
    E -->|"是"| F[提交 PR]
    F --> G[自动化扫描]
    G --> H{扫描结果}
    H -->|"ERROR"| B
    H -->|"WARNING"| I[Reviewer 审查]
    H -->|"INFO"| I
    I --> J{审查通过?}
    J -->|"否"| B
    J -->|"是"| K[合并代码]
```

### 流程二：存量重构

```mermaid
flowchart LR
    A[运行全量扫描] --> B[按风险等级排序]
    B --> C[选择一批硬编码点]
    C --> D[查阅替代方案指南]
    D --> E[实施重构]
    E --> F[运行全量测试]
    F --> G{测试通过?}
    G -->|"否"| D
    G -->|"是"| H[提交 PR]
    H --> I[自动化扫描验证]
    I --> J[合并]
```

## 与现有体系的关联

本规则体系与 `.agents/` 目录下的其他规范存在以下关联：

| 关联规范 | 关联方式 |
|---|---|
| `.agents/workflows/code-review.md` | 硬编码检查已纳入代码审查清单 |
| `.agents/protocols/conflict-resolution.md` | 例外审批争议可升级至冲突解决协议 |
| `.agents/scripts/ci-check.ps1` / `ci-check.sh` | 自动化扫描建议集成至 CI 综合检查 |
| `docs/retrospective/hardcode/` | 历史复盘数据为规则制定提供依据 |
| `AGENTS.md` | 路由表包含本规则体系的入口 |

## 规则维护

- 规则新增或变更应经过 architect 评审，并通过 orchestrator 通知所有相关智能体
- 每季度审查规则有效性，根据实际使用反馈调整识别标准和阈值
- 自动化扫描规则集应与 `.agents/scripts/` 下的检测脚本保持同步
- 例外清单应纳入版本控制，定期清理过期项
