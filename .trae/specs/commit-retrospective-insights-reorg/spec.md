# 洞察库重组 — 原子提交与复盘导出 Spec

## Why

竹简悟道洞察库重组工作已完成（2个失衡文件拆分为3个均衡文件，修复标题层级、标准结构、临时统计块等问题，更新全项目交叉引用），但变更尚未提交至 Git。需要按项目原子提交规范将变更提交，并遵循项目复盘指令集对本次重组进行完整的「复盘→洞察→导出」闭环，将经验沉淀为可复用资产。

## What Changes

- **原子提交**：将洞察库重组的全部变更（12个修改文件 + 1个删除文件 + 2个新建文件 + 规划文档）作为一个原子提交提交至 Git，遵循 Conventional Commits 规范
- **复盘报告**：在 `docs/retrospective/reports/project-governance/` 下创建复盘报告目录，包含 README（概览）、execution-retrospective（执行复盘）、insight-extraction（洞察萃取）、export-suggestions（导出建议）四个子文件
- **洞察萃取**：从重组过程中萃取可复用的方法论洞察（如文件拆分策略、交叉引用更新流程、结构修复模式等）
- **结构化导出**：将复盘报告以标准格式归档，更新复盘报告索引

## Impact

- **Affected specs**: 无直接影响（本次为提交+复盘操作，不改变代码/文档功能）
- **Affected code**:
  - Git 仓库：新增1个原子提交
  - `docs/retrospective/reports/project-governance/retrospective-insights-reorg-20260626/`：新建复盘报告目录（4个文件）
  - `docs/retrospective/reports/README.md`：可能需要更新索引

## ADDED Requirements

### Requirement: 原子提交

系统 SHALL 将洞察库重组的所有变更作为一个原子提交提交至 Git 仓库。

#### Scenario: 提交包含所有重组变更
- **WHEN** 执行原子提交
- **THEN** 提交包含以下变更：12个修改文件（conventions.md, README.md, insights-01-30.md, product-spec.md, restructure-comparison.md, project-review.md, project.md, philosopher.md, SKILL.md, insight-structure.md, AGENTS.md）、1个删除文件（insights-31-65.md）、2个新建文件（insights-31-53.md, insights-54-68.md）、规划文档（.trae/specs/insights-reorganization/）
- **AND** 提交信息遵循 Conventional Commits 格式：`docs(insights): <中文描述为什么>`
- **AND** 提交信息主体使用中文描述"为什么"而非仅"做了什么"

#### Scenario: 提交前验证
- **WHEN** 执行预提交验证
- **THEN** 确认无临时文件（vendor/, .temp/, __pycache__/ 等）混入提交
- **AND** 确认提交文件列表与预期一致，无遗漏或多余

### Requirement: 复盘报告

系统 SHALL 在 `docs/retrospective/reports/project-governance/retrospective-insights-reorg-20260626/` 下生成完整的复盘报告，遵循项目复盘报告模板。

#### Scenario: 报告结构完整
- **WHEN** 复盘报告生成完成
- **THEN** 报告目录包含4个文件：README.md（概览索引）、execution-retrospective.md（执行复盘）、insight-extraction.md（洞察萃取）、export-suggestions.md（导出建议）
- **AND** README.md 包含项目概览、核心指标、交付物清单、子模块导航
- **AND** execution-retrospective.md 遵循「事实→分析→洞察→建议」结构
- **AND** insight-extraction.md 包含可复用模式与最佳实践，标注成熟度等级
- **AND** export-suggestions.md 包含改进行动项与优先级

### Requirement: 洞察萃取

系统 SHALL 从重组过程中萃取至少3条可复用洞察。

#### Scenario: 洞察质量
- **WHEN** 洞察萃取完成
- **THEN** 每条洞察有支撑事实（来自重组过程的实际数据）
- **AND** 每条洞察有可迁移性说明（适用于哪些类似场景）
- **AND** 洞察覆盖不同维度（如：文件拆分策略、交叉引用管理、结构修复模式、原子提交实践）

### Requirement: 结构化导出

系统 SHALL 将复盘报告归档至标准目录并更新索引。

#### Scenario: 归档与索引
- **WHEN** 导出完成
- **THEN** 复盘报告目录存在于 `docs/retrospective/reports/project-governance/` 下
- **AND** 报告文件格式为 Markdown，可在标准编辑器中阅读
- **AND** 复盘报告索引（如存在）已更新，包含本次报告的链接

## MODIFIED Requirements

无。

## REMOVED Requirements

无。
