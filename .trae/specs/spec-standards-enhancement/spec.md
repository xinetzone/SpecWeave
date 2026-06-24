version: 1.0

# Spec 文档标准化框架 Spec

<!-- changelog -->
## Changelog
- 2026-06-24 | added | 初始版本发布，包含标准化框架定义、格式检查脚本需求、增强一致性检查需求

## Why

当前项目的 spec 文档虽然遵循基本格式，但在完整性、精确性、可执行性及可维护性方面存在改进空间。具体表现为：各 spec 文档的编写风格与结构细节不完全统一、部分技术指标与验收标准不够明确、缺乏版本控制与变更追踪机制。这导致智能体在依据 spec 生成代码时可能产生理解偏差，影响代码质量与需求一致性。需要建立一套标准化的 spec 编写框架，明确各项要求与最佳实践，确保 spec 文档能够准确传达需求意图并有效指导代码生成。

## What Changes

- **新增 `.agents/rules/spec-writing-guide.md`**：Spec 文档编写指南（标准化的章节结构、必需元素、可选元素、编写规范与示例）
- **新增 `.agents/rules/spec-version-control.md`**：Spec 文档版本控制规范（版本号规则、变更日志格式、弃用处理流程）
- **新增 `.agents/scripts/check-spec-format.py`**：Spec 格式检查脚本（验证文档结构完整性、必要元素存在性、格式规范遵循度）
- **修改现有 `check-spec-consistency.py`**：增强对 spec 自身质量的检查能力（区分度、清晰度、可执行性）
- **新增 `.trae/specs/spec-standards-enhancement/` 下的所有内容**：本规范自身

## Impact

- Affected specs: 所有现有及未来的 spec 文档均需遵循新的编写标准
- Affected code: `.agents/scripts/check-spec-consistency.py`（增强检查能力）、新增 `check-spec-format.py`
- 与 `AGENTS.md` 的关系：作为 `AGENTS.md` 中"规则体系索引"的补充，为 spec 文档提供更细化的编写指导

## ADDED Requirements

### Requirement: Spec 文档结构标准化

所有 Spec 文档必须包含以下核心章节，且顺序固定：Why（动机）、What Changes（变更摘要）、Impact（影响范围）、ADDED Requirements（新增需求）、MODIFIED Requirements（修改需求）、REMOVED Requirements（移除需求）。每个核心章节必须有实质性内容，禁止空章节。

#### Scenario: 标准结构通过检查

- **WHEN** `spec.md` 包含完整的 Why、What Changes、Impact、ADDED Requirements 章节
- **AND** 各章节内容非空
- **THEN** 格式检查通过，无结构警告

#### Scenario: 缺少核心章节

- **WHEN** `spec.md` 缺少 Why 章节
- **OR** Why 章节内容为空
- **THEN** 格式检查输出警告："缺少必需章节 Why 或内容为空"

### Requirement: 需求描述规范化

每个 Requirement 必须包含以下要素：名称（以"Requirement:"开头）、主体描述（说明系统 SHALL 提供什么功能）、至少一个 Scenario（以"#### Scenario:"开头，包含 WHEN/AND/THEN 结构）。

#### Scenario: 需求描述完整

- **WHEN** Requirement 包含名称、主体描述、至少一个 Scenario
- **AND** Scenario 包含完整的 WHEN/AND/THEN 结构
- **THEN** 格式检查通过，无需求描述警告

#### Scenario: 需求缺少 Scenario

- **WHEN** Requirement 包含名称和描述
- **AND** 缺少任何 Scenario
- **THEN** 格式检查输出警告："Requirement [名称] 缺少 Scenario"

### Requirement: 验收标准可验证性

每个 Scenario 必须包含可验证的验收条件（WHEN 部分描述触发条件，THEN 部分描述可观察的预期结果）。禁止使用模糊词汇（如"良好"、"优秀"、"合适"），必须使用具体可测量的标准。

#### Scenario: 验收标准具体可测

- **WHEN** Scenario 的 THEN 部分包含具体数值或可验证的状态描述
- **THEN** 格式检查通过，无可执行性警告

#### Scenario: 验收标准模糊

- **WHEN** Scenario 的 THEN 部分使用"良好"、"合适"等模糊词汇
- **THEN** 格式检查输出警告："Scenario [名称] 的验收标准不够具体，建议使用可测量指标"

### Requirement: 版本号显式声明

每个 Spec 文档必须在文件头部显式声明版本号，格式为 `version: X.Y`（X 为主版本号，Y 为次版本号）。初始版本为 `version: 1.0`。

#### Scenario: 版本号声明正确

- **WHEN** `spec.md` 头部包含 `version: 1.0` 或更高版本
- **THEN** 格式检查通过

#### Scenario: 缺少版本号声明

- **WHEN** `spec.md` 头部不包含版本号声明
- **THEN** 格式检查输出警告："缺少版本号声明"

### Requirement: 变更日志维护

每个 Spec 文档必须包含 `<!-- changelog -->` 标记的变更日志章节，记录每次重大变更的时间、变更类型（added/modified/removed）、变更描述。

#### Scenario: 变更日志完整

- **WHEN** `spec.md` 包含 `<!-- changelog -->` 章节
- **AND** 最近一次变更记录在章节顶部
- **AND** 包含变更日期、类型、描述
- **THEN** 格式检查通过

#### Scenario: 变更日志缺失

- **WHEN** `spec.md` 不包含变更日志章节
- **OR** 变更日志格式不完整（缺少日期、类型或描述）
- **THEN** 格式检查输出警告："变更日志缺失或不完整"

## MODIFIED Requirements

### Requirement: Spec 文档结构标准化

当前 spec 文档格式依赖人工审查与约定俗成，缺乏强制性的结构验证机制。本规范将引入自动化检查脚本，对文档结构完整性进行系统性验证。

#### Scenario: 自动化结构验证

- **WHEN** 执行 `python .agents/scripts/check-spec-format.py --spec-dir .trae/specs/XXX`
- **THEN** 输出包含结构完整性评分（0-100）、缺失章节列表、格式问题列表

## REMOVED Requirements

### Requirement: 非强制性格式约定

**Reason**: 原有的格式约定缺乏强制力，执行依赖人工审查，难以保证一致性。
**Migration**: 由 `check-spec-format.py` 脚本替代，实现自动化检查与报告。

## 技术指标

| 指标 | 目标值 |
|------|--------|
| Spec 文档结构完整性 | ≥ 95%（核心章节齐全率） |
| 需求 Scenario 覆盖率 | 100%（每个 Requirement 至少一个 Scenario） |
| 验收标准可验证性 | ≥ 90%（使用具体可测量指标的比例） |
| 版本号声明覆盖率 | 100% |
| 变更日志维护率 | ≥ 80%（重大变更有记录的比率） |
| 格式检查脚本准确率 | ≥ 95% |
| 格式检查脚本执行时间 | ≤ 5 秒/每个 spec 目录 |
