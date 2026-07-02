# 治理规则体系

本目录收录了项目的完整治理规则体系，涵盖硬编码治理、开发流程阶段守卫、Skill 开发规范、AI编码行为准则、AI智能体互联数据安全治理五大核心模块。所有开发者和智能体在编写代码、执行开发任务时，均应参照本规则体系确保开发过程得到系统性约束。

## 规则体系架构

```mermaid
flowchart TD
    subgraph FLOW ["开发流程治理"]
        SG["stage-guardrails.md<br/>开发流程阶段守卫"]
    end
    subgraph DEV ["编码阶段"]
        A["identification-standards.md<br/>硬编码识别标准"] --> B["alternatives-guide.md<br/>替代方案指南"]
    end
    subgraph REVIEW ["审查阶段"]
        C["allowable-scenarios.md<br/>允许场景与审批"] --> D["enforcement-guidelines.md<br/>执行与验证规则"]
    end
    subgraph GOV ["治理阶段"]
        E["detection-and-reporting.md<br/>检测与报告机制"]
    end
    SG --> |"阶段边界约束"| F1["需求接收"]
    SG --> |"阶段边界约束"| F2["方案设计"]
    SG --> |"阶段边界约束"| F3["代码实现"]
    SG --> |"阶段边界约束"| F4["测试/审查"]
    A --> |"判断是否为硬编码"| F{"是否允许场景内?"}
    F --> |"是"| C
    F --> |"否"| B
    B --> |"实施替代方案"| G["代码提交"]
    C --> |"标记例外或批准"| G
    G --> |"触发"| E
    E --> |"反馈结果"| D
    D --> |"趋势数据"| H["迭代复盘与改进"]
```

## 规则文档清单

| 文档 | 用途 | 适用阶段 | 适用角色 |
|---|---|---|---|
| [stage-guardrails.md](./stage-guardrails.md) | 开发流程阶段守卫规则：阶段边界定义、跨阶段拦截机制、阶段跳转审批流程、SG-LOG结构化日志规范 | 全阶段 | 全部角色 |
| [stage-guardrails-guide.md](./stage-guardrails-guide.md) | 阶段守卫运行时使用指南：8阶段权限矩阵、CLI工具用法、SG-LOG日志示例、例外处理工作流（运行时操作手册） | 全阶段 | developer, reviewer, orchestrator |
| [cmd-log-specification.md](./cmd-log-specification.md) | CMD-LOG命令集执行日志规范：5大命令集结构化日志格式、字段定义、事件枚举、解析正则、分析命令 | 命令集执行 | 全部角色 |
| [spec-writing-guide.md](./spec-writing-guide.md) | Spec 文档编写指南（标准章节结构、必需元素、编写规范与示例） | 编码、规范编写 | developer, reviewer |
| [spec-version-control.md](./spec-version-control.md) | Spec 文档版本控制规范（版本号规则、变更日志、弃用流程） | 编码、版本管理 | developer, reviewer |
| [identification-standards.md](./identification-standards.md) | 定义 8 大类硬编码的识别标准、正例反例、检测要点 | 编码、审查 | developer, reviewer |
| [allowable-scenarios.md](./allowable-scenarios.md) | 规定允许硬编码的 4 类场景、例外审批流程、例外清单模板 | 审查 | developer, reviewer, architect, orchestrator |
| [alternatives-guide.md](./alternatives-guide.md) | 提供 7 种替代方案的实施指南、代码示例、模板脚手架 | 编码、重构 | developer |
| [detection-and-reporting.md](./detection-and-reporting.md) | 建立三层检测体系（自动化扫描、人工审查、定期报告）的规范 | 全阶段 | developer, reviewer, orchestrator |
| [enforcement-guidelines.md](./enforcement-guidelines.md) | 定义 6 条可执行治理规则、验证手段、合规等级 | 全阶段 | 全部角色 |
| [skill-development.md](./skill-development.md) | SpecWeave Skill 开发补充规范：三层路由合规、五要素模型、双方案模式、资产盘点、验证清单（基于vendor skill-creator方法论） | Skill 创建/优化 | developer, reviewer |
| [skill-five-elements-mindmap.md](./skill-five-elements-mindmap.md) | 五要素模型可视化思维导图（Mermaid mindmap），含叶子节点检查点，用于Skill质量深度review | Skill 创建/优化（深度review） | developer, reviewer |
| [raci-governance-standards.md](./raci-governance-standards.md) | RACI治理规范与可复用模板：三大强制规则（A唯一性/R≠A分离/双列设计）、RACI编写模板、五层审批模型模板、质量验证Checklist | 规范编写、RACI矩阵设计 | 全部角色 |
| [ai-coding-guidelines.md](./ai-coding-guidelines.md) | AI 编码行为准则：四条核心原则（歧义主动澄清/简约至上/精确编辑/目标驱动），含一分钟速查表、正反例、工作流整合（蒸馏自 Karpathy LLM编程观察） | 编码、任务沟通 | 全部角色 |
| [data-security/README.md](./data-security/README.md) | AI智能体互联数据安全治理总览：五层架构导航、场景导航、使用流程 | 全阶段 | 全部角色 |
| [data-security/data-classification.md](./data-security/data-classification.md) | 数据分类分级标准：四级分类体系、AI场景特有数据归类、流转限制矩阵 | 全阶段 | 全部角色 |
| [data-security/cross-border-assessment.md](./data-security/cross-border-assessment.md) | 数据出境安全评估：出境判定、风险自评估、审批流程、DPA合同模板 | 设计、接入 | developer, reviewer, architect, orchestrator |
| [data-security/data-masking.md](./data-security/data-masking.md) | 数据脱敏技术规范：7种脱敏技术、静态/动态脱敏、AI场景脱敏规则 | 编码、审查 | developer, reviewer |
| [data-security/data-encryption.md](./data-security/data-encryption.md) | 数据加密与密钥管理：传输/存储/字段级加密、密钥全生命周期管理 | 编码、设计、审查 | developer, reviewer, architect |
| [data-security/vendor-admission.md](./data-security/vendor-admission.md) | 第三方API供应商安全准入：四阶段准入流程、资质审查、安全评估、黑白名单 | 接入、审查 | reviewer, architect, orchestrator |
| [data-security/vendor-audit.md](./data-security/vendor-audit.md) | 第三方API供应商持续审计：分级审计计划、日志审计、违规处置、安全评级 | 运营、审查 | reviewer, orchestrator |
| [data-security/security-monitoring.md](./data-security/security-monitoring.md) | 数据安全监控体系：18项监控指标、五级告警、全链路追踪、异常检测 | 运营、审查 | reviewer, orchestrator |
| [data-security/incident-response.md](./data-security/incident-response.md) | 数据安全应急响应：四级事件分级、六阶段响应、6类预案、通报机制 | 运营、应急 | 全部角色 |
| [data-security/role-responsibilities.md](./data-security/role-responsibilities.md) | 数据安全角色职责矩阵：角色映射、RACI矩阵、审批权限边界、阶段守卫集成 | 全阶段 | 全部角色 |

## 快速导航

### 按场景导航

| 场景 | 应查阅的文档 |
|---|---|
| 我要执行一个开发任务，需要遵守什么流程？ | [stage-guardrails.md](./stage-guardrails.md) |
| 我不确定现在是否可以开始编码？ | [stage-guardrails.md](./stage-guardrails.md)（阶段边界与拦截规则） |
| 我需要跳过某个阶段或回退到上一阶段？ | [stage-guardrails.md](./stage-guardrails.md)（阶段跳转审批流程） |
| 我要编写一个新的 spec 文档 | [spec-writing-guide.md](./spec-writing-guide.md) |
| 我需要管理 spec 文档的版本变更 | [spec-version-control.md](./spec-version-control.md) |
| 我不确定这段代码算不算硬编码 | [identification-standards.md](./identification-standards.md) |
| 我需要写一段包含固定值的代码，怎么替代？ | [alternatives-guide.md](./alternatives-guide.md) |
| 我这个硬编码确实无法替代，怎么申请例外？ | [allowable-scenarios.md](./allowable-scenarios.md) |
| 我作为 reviewer 怎么审查硬编码问题？ | [identification-standards.md](./identification-standards.md) + [enforcement-guidelines.md](./enforcement-guidelines.md) |
| 我想知道项目硬编码的整体趋势 | [detection-and-reporting.md](./detection-and-reporting.md) |
| 我想建立自动化硬编码检测 | [detection-and-reporting.md](./detection-and-reporting.md) |
| 我不遵守规则会有什么后果？ | [enforcement-guidelines.md](./enforcement-guidelines.md) + [stage-guardrails.md](./stage-guardrails.md) |
| 我要创建或优化一个 Skill？ | [skill-development.md](./skill-development.md)（先读 vendor skill-creator 方法论） |
| 我的 Skill description 触发率低怎么办？ | [skill-development.md](./skill-development.md)（Trigger-Ready Description 规范） |
| AI写代码总是过度设计/乱改/猜需求？ | [ai-coding-guidelines.md](./ai-coding-guidelines.md)（四条核心原则+速查表） |
| 我要给AI描述任务，怎么说效果最好？ | [ai-coding-guidelines.md](./ai-coding-guidelines.md)（原则四：目标驱动） |
| AI改bug总喜欢顺手改一堆不相关的代码？ | [ai-coding-guidelines.md](./ai-coding-guidelines.md)（原则三：精确编辑） |
| 我要接入第三方AI API（GPT/Claude等）？ | [data-security/vendor-admission.md](./data-security/vendor-admission.md) + [data-security/cross-border-assessment.md](./data-security/cross-border-assessment.md) |
| 我不确定数据分级，能否传给境外API？ | [data-security/data-classification.md](./data-security/data-classification.md) + [data-security/cross-border-assessment.md](./data-security/cross-border-assessment.md) |
| 如何实现数据脱敏和加密？ | [data-security/data-masking.md](./data-security/data-masking.md) + [data-security/data-encryption.md](./data-security/data-encryption.md) |
| 数据安全事件如何响应？ | [data-security/incident-response.md](./data-security/incident-response.md) |
| 数据安全治理完整入口？ | [data-security/README.md](./data-security/README.md)（五层架构+场景导航） |

### 按角色导航

| 角色 | 流程治理 | 编码阶段 | 审查阶段 | 治理阶段 | 数据安全 |
|---|---|---|---|---|---|
| **developer** | stage-guardrails.md | identification-standards.md<br/>alternatives-guide.md<br/>ai-coding-guidelines.md | allowable-scenarios.md<br/>enforcement-guidelines.md | detection-and-reporting.md | data-classification.md<br/>data-masking.md<br/>data-encryption.md<br/>cross-border-assessment.md |
| **reviewer** | stage-guardrails.md | identification-standards.md<br/>ai-coding-guidelines.md | allowable-scenarios.md<br/>enforcement-guidelines.md | - | data-security/README.md<br/>vendor-admission.md<br/>vendor-audit.md<br/>security-monitoring.md<br/>incident-response.md<br/>role-responsibilities.md |
| **architect** | stage-guardrails.md | ai-coding-guidelines.md | allowable-scenarios.md<br/>enforcement-guidelines.md | detection-and-reporting.md | data-encryption.md<br/>vendor-admission.md<br/>cross-border-assessment.md |
| **orchestrator** | stage-guardrails.md | ai-coding-guidelines.md | allowable-scenarios.md | detection-and-reporting.md<br/>enforcement-guidelines.md | vendor-admission.md<br/>vendor-audit.md<br/>security-monitoring.md<br/>incident-response.md |
| **tester** | stage-guardrails.md | ai-coding-guidelines.md | enforcement-guidelines.md | - | data-masking.md<br/>data-encryption.md<br/>incident-response.md |

## 规则体系使用流程

### 流程一：新功能开发

```mermaid
flowchart LR
    A["查阅阶段守卫规则"] --> A2["确认当前阶段"]
    A2 --> B["查阅识别标准"]
    B --> C["参考替代方案指南"]
    C --> D["编写代码"]
    D --> E["提交前自查<br/>(阶段合规+硬编码)"]
    E --> F{"自查通过?"}
    F -->|"否"| C
    F -->|"是"| G["提交 PR"]
    G --> H["自动化扫描"]
    H --> I{"扫描结果"}
    I -->|"ERROR"| C
    I -->|"WARNING"| J["Reviewer 审查"]
    I -->|"INFO"| J
    J --> K{"审查通过?"}
    K -->|"否"| C
    K -->|"是"| L["合并代码"]
```

### 流程二：存量重构

```mermaid
flowchart LR
    A["运行全量扫描"] --> B["按风险等级排序"]
    B --> C["选择一批硬编码点"]
    C --> D["查阅阶段守卫→功能重构流程"]
    D --> E["查阅替代方案指南"]
    E --> F["实施重构"]
    F --> G["运行全量测试"]
    G --> H{"测试通过?"}
    H -->|"否"| F
    H -->|"是"| I["提交 PR"]
    I --> J["自动化扫描验证"]
    J --> K["双重审查<br/>(代码+架构)"]
    K --> L["合并"]
```

### 流程三：功能扩展

```mermaid
flowchart LR
    A["判定变更类型=功能扩展"] --> B["执行轻量流程<br/>(影响分析→增量方案→增量实现→回归测试)"]
    B --> C["查阅阶段守卫规则"]
    C --> D["增量审查"]
    D --> E["合并"]
```

## 与现有体系的关联

本规则体系与 `.agents/` 目录下的其他规范存在以下关联：

| 关联规范 | 关联方式 |
|---|---|
| `.agents/workflows/feature-development.md` | 阶段守卫规则定义了功能开发流程的阶段边界，工作流每个步骤嵌入守卫检查点 |
| `.agents/protocols/pre-document-reading.md` | 前置文档强制读取是阶段守卫的进入条件之一 |
| `.agents/workflows/code-review.md` | 硬编码检查与阶段合规性检查均已纳入代码审查清单 |
| `.agents/protocols/conflict-resolution.md` | 例外审批争议与阶段跳转分歧可升级至冲突解决协议 |
| `.agents/scripts/ci-check.ps1` / `ci-check.sh` | 自动化扫描建议集成至 CI 综合检查 |
| `docs/retrospective/hardcode/` | 历史复盘数据为硬编码规则制定提供依据 |
| `.agents/roles/` | 各角色 Non-Goals 中已纳入阶段守卫与精确编辑约束；开发者角色职责已整合精确编辑要求 |
| `.agents/global-core-rules.md` | 已整合"歧义主动澄清"原则至全局核心规则 |
| `docs/development-standards.md` | 已整合"简约至上"与"目标驱动"原则至开发规范 |
| `AGENTS.md` | 路由表包含本规则体系的入口 |

## 规则维护

- 规则新增或变更应经过 architect 评审，并通过 orchestrator 通知所有相关智能体
- 每季度审查规则有效性，根据实际使用反馈调整识别标准和阈值
- 自动化扫描规则集应与 `.agents/scripts/` 下的检测脚本保持同步
- 例外清单应纳入版本控制，定期清理过期项
- 阶段守卫规则在功能演进实践中持续优化，如有频繁的合理越界场景应考虑调整阶段定义
