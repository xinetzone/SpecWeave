# 方法论模式

> 可复用的开发方法论与工作流程模式，每个模式描述一个经过验证的"如何做"指南。

## 模式列表

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [spec-driven-development.md](spec-driven-development.md) | Spec-driven 开发流程，"先设计后实施"的完整方法论 | L3 | 任何需要"先设计后实施"的 AI 辅助开发任务 |
| [review-insight-export-loop.md](review-insight-export-loop.md) | 复盘→洞察→导出知识闭环，含报告结构模板 | L2 | 项目复盘、经验萃取、知识沉淀 |
| [document-system-refactoring.md](document-system-refactoring.md) | 文档体系原子化重构方法论，含六步流程 | L2 | 大型文档拆分、模块化重组 |
| [tool-trigger-mechanism.md](tool-trigger-mechanism.md) | 工具开发触发器机制，3 次手动操作触发自动化评估 | L1 | 重复性操作的自动化决策 |
| [three-tier-governance.md](three-tier-governance.md) | 三层治理模型（原子化→自动化→验证），含实施检查清单 | L2 | 文档体系、代码库、配置管理的治理 |
| [tool-entropy-metrics.md](tool-entropy-metrics.md) | 工具熵减度量体系，含 ROI 公式与已实施工具的熵减分析 | L1 | 自动化投资决策、工具价值评估 |
| [fact-statement-consistency-loop.md](fact-statement-consistency-loop.md) | 事实表述一致性闭环，修正一处→搜索同类→统一修正 | L2 | 文档事实性修正、命名规范统一、术语一致性调整 |
| [convention-driven-creation.md](convention-driven-creation.md) | 约定驱动创建模型，先读范例提取模板再填充内容，零结构决策 | L2 | 成熟规范体系内的模块扩展 |
| [spec-level-defense-in-depth.md](spec-level-defense-in-depth.md) | 规范层纵深防御模型，权限定义+验证机制+防滥用+审计追溯四维防护 | L1 | 涉及特权操作的模块安全设计 |
| [dual-zone-development-model.md](dual-zone-development-model.md) | 双区开发模型（非正式区→质量门禁→正式区） | L2 | 新实体的开发工作流规范 |
| [short-command-patterns.md](short-command-patterns.md) | 短指令模式库：登记已验证的 AI 协作快捷指令 | L2 | AI 人机协作指令优化 |
| [five-category-asset-coverage.md](five-category-asset-coverage.md) | 五类资产覆盖原则：概念/模式/脚本/报告/索引五类互补覆盖 | L2 | 知识产出质量控制 |
| [reference-as-trigger.md](reference-as-trigger.md) | 引用即触发协作模式：用户选中行号触发精确实施 | L2 | 复盘报告改进建议执行 |
| [content-migration-workflow.md](content-migration-workflow.md) | 文档内容迁移标准操作流程，存量盘点→缺口计算→富化归档→验证闭环 | L2 | 从综合性文档提取结构化内容迁移至独立规范文件 |
| [suggestion-priority-driven-execution.md](suggestion-priority-driven-execution.md) | 建议执行优先级驱动模型，高/中/低优先级分类 + 投入估算 + 状态追踪 | L2 | 复盘报告改进建议执行 |
| [report-as-tracking.md](report-as-tracking.md) | 报告即追踪载体，每执行一个建议后立即更新报告状态形成闭环 | L2 | 所有复盘报告的改进建议章节 |
| [structure-first-extension.md](structure-first-extension.md) | 结构阅读先行：扩展前先完整阅读包结构，同概念域追加、异概念域新建 | L2 | 已有模块的功能扩展决策 |
| [amphibious-positioning-model.md](amphibious-positioning-model.md) | 两栖定位模型：通过资产清单+泛化路径图+落地案例三支柱支撑双重定位 | L1 | 积累大量可复用资产的项目的定位升级 |
| [diff-driven-refactoring.md](diff-driven-refactoring.md) | 差异驱动重构：逐段对比→标注重复/相似/独有→分类提取→回归验证 | L1 | 两个及以上功能重叠文件的合并重构 |
| [progressive-templating.md](progressive-templating.md) | 渐进式模板化：硬编码验证→模板分离→多类型扩展三阶段 | L1 | 将硬编码内容转化为可复用模板 |
| [retrospective-acceleration-effect.md](retrospective-acceleration-effect.md) | 复盘加速效应：高频复盘→低延迟改进→知识转化率递增 | L1 | 长时间密集开发会话中的知识管理 |
| [two-phase-processing.md](two-phase-processing.md) | 双阶段加工策略：大型文档先横切（原子化）再纵切（模块化）的固定先后顺序 | L1 | >200 行文档的深度加工 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 模式关系

```mermaid
flowchart TD
    A[spec-driven-development] --> B[review-insight-export-loop]
    B --> C[document-system-refactoring]
    C --> D[three-tier-governance]
    D --> E[tool-trigger-mechanism]
    E --> F[tool-entropy-metrics]
    F --> A
    B --> G[fact-statement-consistency-loop]
    G --> D
    B --> H[convention-driven-creation]
    H --> I[spec-level-defense-in-depth]
    I --> D
    B --> J[retrospective-acceleration-effect]
    J --> B
    H --> K[structure-first-extension]
    H --> L[progressive-templating]
    A --> M[dual-zone-development-model]
    M --> C
    C --> N[diff-driven-refactoring]
    N --> D
    C --> O[two-phase-processing]
    O --> C
```

**演进路径**：从"如何开发"（spec-driven）→"如何复盘"（review-loop）→"如何重构"（document-refactoring）→"如何治理"（three-tier）→"何时自动化"（tool-trigger）→"如何度量"（tool-entropy），形成完整的**开发→复盘→优化→治理→自动化→度量**闭环。`fact-statement-consistency-loop` 是 `review-insight-export-loop` 在文档修正场景的具体应用，其验证阶段可纳入 `three-tier-governance` 的验证层。`convention-driven-creation` 是 `spec-driven-development` 在高成熟度体系下的简化路径（范例即规格），`spec-level-defense-in-depth` 为涉及特权操作的模块提供安全设计蓝图。`structure-first-extension` 是 `convention-driven-creation` 在代码级的实现（先读包结构再扩展），`progressive-templating` 是其在模板化场景的特化。`diff-driven-refactoring` 是 `document-system-refactoring` 在代码层面的类比应用，`retrospective-acceleration-effect` 是 `review-insight-export-loop` 在时间维度的优化（高频复盘→低延迟改进）。`dual-zone-development-model` 与 `document-system-refactoring` 共享"高熵→低熵"迁移路径。`amphibious-positioning-model` 为整个模式体系提供对外定位策略。`two-phase-processing` 是 `document-system-refactoring` 在"一个文档需同时原子化和模块化"场景的精化（先横切再纵切）。

## 使用指南

1. **首次使用**：从 `spec-driven-development.md` 开始，它是所有模式的基础。
2. **项目复盘**：参考 `review-insight-export-loop.md` 的结构模板。
3. **文档优化**：遇到大型文档需要拆分时，使用 `document-system-refactoring.md` 和 `three-tier-governance.md`。
4. **工具决策**：不确定是否值得自动化时，参考 `tool-trigger-mechanism.md` 和 `tool-entropy-metrics.md`。
5. **文档修正**：修正文档中的事实表述时，使用 `fact-statement-consistency-loop.md` 确保全局一致性。
6. **模块扩展**：在成熟规范体系内创建新模块时，使用 `convention-driven-creation.md` 实现零结构决策。
7. **安全设计**：涉及特权操作的模块，使用 `spec-level-defense-in-depth.md` 设计四维防护。

> **关联模块**：
> - `../code-patterns/` — 代码模式
> - `../architecture-patterns/` — 架构模式
> - `../../frameworks/` — 决策框架
> - `../../concepts/` — 知识概念