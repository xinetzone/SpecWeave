# 复盘文档体系重构 Spec

## Why

当前 `docs/retrospective/` 目录下仅有 3 个大型 Markdown 文件，其中 `knowledge-extraction.md` 长达 598 行，涵盖了代码模式、架构模式、方法论、模板、决策框架、知识概念、资产清单等 7 个不同维度的内容。这种"大而全"的组织方式导致以下问题：1) 单文件体积过大，难以快速定位特定内容；2) 不同维度的内容混杂在一起，缺乏清晰的模块边界；3) 缺乏统一的目录索引，新成员难以理解整体结构；4) 后续维护时难以进行增量更新，修改一处可能影响整个文件。需要对现有文档进行原子化拆分与模块化重组，建立清晰的层级结构，提升管理效率与可维护性。

## What Changes

- **原子化拆分**：将 `knowledge-extraction.md` 按 7 大主题拆分为独立的原子化模块文件，每个文件聚焦单一主题
- **模块化归类**：建立 6 个功能子目录（`templates/`、`patterns/`、`frameworks/`、`concepts/`、`reports/`、`assets/`），按主题对内容进行归类
- **结构化层级**：设计合理的目录树结构，制定统一的命名规范（`kebab-case`），确保层级清晰
- **引用追溯**：确保各模块间的引用关系明确且可追溯，每个模块标注来源与关联模块
- **目录索引**：生成 `README.md` 作为目录索引与模块说明文档，方便后续维护与查阅
- **BREAKING**：原有 `knowledge-extraction.md` 将被删除，其内容拆分为 18 个独立模块文件

## Impact

- Affected specs: 无（不涉及任何 `.trae/specs/` 下的规格文档）
- Affected code: 无（纯文档重构，不涉及代码逻辑）
- Affected docs: `docs/retrospective/` 下所有文件（3 个文件将被重组为 22 个文件 + 6 个子目录）
- 不涉及 `.agents/` 目录下的任何文件

## ADDED Requirements

### Requirement: 原子化拆分

系统 SHALL 将 `knowledge-extraction.md` 的 7 个一级章节（可复用代码模式、可复用架构模式、可复用方法论、可复用模板、可复用决策框架、可复用知识概念、资产清单与复用指南）拆分为独立的原子化模块文件，每个文件仅包含一个主题的完整内容。

#### Scenario: 代码模式拆分

- **WHEN** 查看 `patterns/code-patterns/` 目录
- **THEN** 应包含 5 个独立文件，分别对应三段式检查工具架构、上下文感知路径解析、元文档识别、Git 忽略规则验证、正则驱动的 Markdown 解析

#### Scenario: 架构模式拆分

- **WHEN** 查看 `patterns/architecture-patterns/` 目录
- **THEN** 应包含 3 个独立文件，分别对应感知→检查→报告三层模型、多智能体并行执行模式、增量验证+回归验证双层策略

#### Scenario: 方法论拆分

- **WHEN** 查看 `patterns/methodology-patterns/` 目录
- **THEN** 应包含 2 个独立文件，分别对应 Spec-driven 开发流程、复盘→洞察→导出知识闭环

#### Scenario: 模板拆分

- **WHEN** 查看 `templates/` 目录
- **THEN** 应包含 4 个独立文件，分别对应 spec.md 模板、tasks.md 模板、checklist.md 模板、复盘报告模板

#### Scenario: 决策框架拆分

- **WHEN** 查看 `frameworks/` 目录
- **THEN** 应包含 4 个独立文件，分别对应目录命名决策矩阵、临时依赖管理决策矩阵、元文档处理决策矩阵、语义匹配阈值决策矩阵

#### Scenario: 知识概念拆分

- **WHEN** 查看 `concepts/` 目录
- **THEN** 应包含 5 个独立文件，分别对应元文档、上下文感知、正交验证、零依赖原则、语义前缀

#### Scenario: 资产清单拆分

- **WHEN** 查看 `assets/` 目录
- **THEN** 应包含 1 个 `asset-inventory.md` 文件，涵盖可直接复用的文件、需实例化后复用的模式、需按场景适配的决策框架三部分内容

### Requirement: 模块化归类

系统 SHALL 建立 6 个功能子目录，按主题对内容进行归类，创建清晰的模块边界。

#### Scenario: 子目录结构完整

- **WHEN** 查看 `docs/retrospective/` 目录
- **THEN** 应包含 `templates/`、`patterns/`（含 `code-patterns/`、`architecture-patterns/`、`methodology-patterns/` 子目录）、`frameworks/`、`concepts/`、`reports/`、`assets/` 共 6 个功能子目录

#### Scenario: 复盘报告归类

- **WHEN** 查看 `reports/` 目录
- **THEN** 应包含 `retrospective-report-agents-spec-system.md` 和 `retrospective-report-check-spec-consistency.md` 两个复盘报告文件

### Requirement: 结构化层级与命名规范

系统 SHALL 设计合理的目录树结构，所有文件名采用 `kebab-case`（小写字母 + 连字符）命名规范，确保层级清晰、风格统一。

#### Scenario: 命名规范一致

- **WHEN** 检查所有新增文件名
- **THEN** 所有文件名应使用 `kebab-case` 格式（如 `three-tier-check-tool.md`、`context-aware-path-resolution.md`），不包含空格、中文、下划线或驼峰命名

### Requirement: 引用关系可追溯

系统 SHALL 在每个模块文件中标注"来源"与"关联模块"信息，确保各模块间的引用关系明确且可追溯。

#### Scenario: 来源标注

- **WHEN** 读取任意原子化模块文件
- **THEN** 文件开头应包含 `> **来源**：` 引用块，标注原始来源文档

#### Scenario: 关联模块标注

- **WHEN** 读取任意原子化模块文件
- **THEN** 文件末尾应包含 `> **关联模块**：` 引用块，列出相关模块的文件路径

### Requirement: 目录索引与说明

系统 SHALL 在 `docs/retrospective/` 根目录下生成 `README.md` 文件，作为完整的目录索引与模块说明文档。

#### Scenario: 目录树展示

- **WHEN** 读取 `README.md`
- **THEN** 应包含完整的目录树结构（Mermaid 或文本格式），展示所有子目录和文件

#### Scenario: 模块说明

- **WHEN** 读取 `README.md`
- **THEN** 应包含每个模块的简要说明（1-2 句话），描述其用途与内容

#### Scenario: 导航入口

- **WHEN** 读取 `README.md`
- **THEN** 应包含指向各子目录和关键文件的链接，方便快速导航

## REMOVED Requirements

### Requirement: 原 knowledge-extraction.md 大文件

**Reason**：该文件已被原子化拆分为 18 个独立模块文件，原文件不再需要。
**Migration**：原文件中的所有内容均已迁移至 `patterns/`、`templates/`、`frameworks/`、`concepts/`、`assets/` 五个子目录下，无内容丢失。