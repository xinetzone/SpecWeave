---
version: 1.1
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/spec-standards-enhancement/spec.toml"
---
# Spec 文档标准化框架 Spec

<!-- changelog -->
## Changelog
- 2026-06-26 | modified | 完成所有遗留任务：格式检查脚本完善9项边界情况，编写指南与实际项目格式对齐（推荐纯英文章节标题、列表项加粗Scenario），更新参考模板包含TOML frontmatter和changelog标记，全项目spec验证通过，spec-standards-enhancement v1.1 交付完成
- 2026-06-24 | added | 初始版本发布，包含标准化框架定义、格式检查脚本需求、增强一致性检查需求
<!-- changelog -->

## Why

当前项目的 spec 文档虽然遵循基本格式，但在完整性、精确性、可执行性及可维护性方面存在改进空间。具体表现为：各 spec 文档的编写风格与结构细节不完全统一、部分技术指标与验收标准不够明确、缺乏版本控制与变更追踪机制。这导致智能体在依据 spec 生成代码时可能产生理解偏差，影响代码质量与需求一致性。系统 SHALL 建立一套标准化的 spec 编写框架，明确各项要求与最佳实践，确保 spec 文档能够准确传达需求意图并有效指导代码生成。

## What Changes

- **新增 `.agents/rules/spec-writing-guide.md`**：Spec 文档编写指南（标准化的章节结构、必需元素、可选元素、编写规范与示例）
- **新增 `.agents/rules/spec-version-control.md`**：Spec 文档版本控制规范（版本号规则、变更日志格式、弃用处理流程）
- **新增 `.agents/scripts/check-spec-format.py`**：Spec 格式检查脚本（验证文档结构完整性、必要元素存在性、格式规范遵循度），v1.1 修复多处边界兼容性问题
- **修改现有 `check-spec-consistency.py`**：增强对 spec 自身质量的检查能力（区分度、清晰度、可执行性）
- **新增 `.trae/specs/spec-standards-enhancement/` 下的所有内容**：本规范自身

## Impact

- Affected specs: 所有现有及未来的 spec 文档均需遵循新的编写标准
- Affected code: `.agents/scripts/check-spec-consistency.py`（增强检查能力）、新增 `check-spec-format.py`
- 与 `AGENTS.md` 的关系：作为 `AGENTS.md` 中"规则体系索引"的补充，为 spec 文档提供更细化的编写指导

## ADDED Requirements

### Requirement: Spec 文档结构标准化

系统 SHALL 要求所有 Spec 文档包含以下核心章节，且顺序固定：Why（动机）、What Changes（变更摘要）、Impact（影响范围）、ADDED Requirements（新增需求）、MODIFIED Requirements（修改需求）、REMOVED Requirements（移除需求）。章节标题使用纯英文（如 `## Why`），允许附加中文括号注释（如 `## Why（动机）`），两种格式均合规。每个核心章节必须有实质性内容，禁止空章节。

#### Scenario: 标准结构通过检查

- **WHEN** `spec.md` 包含完整的 Why、What Changes、Impact、ADDED Requirements 章节
- **AND** 各章节内容非空
- **THEN** 格式检查通过，无结构警告

#### Scenario: 缺少核心章节

- **WHEN** `spec.md` 缺少 Why 章节
- **OR** Why 章节内容为空
- **THEN** 格式检查输出错误："缺少核心章节: Why（动机）"

### Requirement: 需求描述规范化

系统 SHALL 要求每个 Requirement 包含以下要素：名称（以"### Requirement:"开头）、主体描述（推荐使用"系统 SHALL"句式说明系统必须提供什么功能）、至少一个 Scenario（以"#### Scenario:"开头，包含 WHEN/AND/THEN 结构）。

#### Scenario: 需求描述完整

- **WHEN** Requirement 包含名称、主体描述、至少一个 Scenario
- **AND** Scenario 包含完整的 WHEN/AND/THEN 结构
- **THEN** 格式检查通过，无需求描述警告

#### Scenario: 需求缺少 Scenario

- **WHEN** Requirement 包含名称和描述
- **AND** 缺少任何 Scenario
- **THEN** 格式检查输出错误："Requirement [名称] 缺少 Scenario 定义"

### Requirement: 验收标准可验证性

系统 SHALL 要求每个 Scenario 包含可验证的验收条件（WHEN 部分描述触发条件，THEN 部分描述可观察的预期结果）。禁止使用模糊词汇（如"良好"、"优秀"、"合适"），必须使用具体可测量的标准。

#### Scenario: 验收标准具体可测

- **WHEN** Scenario 的 THEN 部分包含具体数值或可验证的状态描述
- **THEN** 格式检查通过，无可执行性警告

#### Scenario: 验收标准模糊

- **WHEN** Scenario 的 THEN 部分使用"良好"、"合适"等模糊词汇
- **THEN** 格式检查输出警告："验收标准使用了模糊词汇'[word]'，应使用具体数值或可验证状态描述"

### Requirement: 版本号显式声明

系统 SHALL 要求每个 Spec 文档在文件头部显式声明版本号，推荐使用 TOML frontmatter 格式 `---\nversion: X.Y\n---`（X 为主版本号，Y 为次版本号），初始版本为 `version: 1.0`。兼容旧版简单头部 `version: X.Y` 格式但给出警告提示迁移。

#### Scenario: 版本号声明正确（frontmatter格式）

- **WHEN** `spec.md` 头部包含 TOML frontmatter 格式的 `version: 1.0` 或更高版本
- **THEN** 格式检查通过，无版本号相关警告

#### Scenario: 版本号使用旧格式（兼容模式）

- **WHEN** `spec.md` 文件开头包含简单声明 `version: 1.0`（无 `---` 包裹）
- **THEN** 格式检查输出警告提示建议迁移到 frontmatter 格式，但不视为错误

#### Scenario: 缺少版本号声明

- **WHEN** `spec.md` 头部不包含版本号声明
- **THEN** 格式检查输出错误："缺少版本号声明"

### Requirement: 变更日志维护

系统 SHALL 要求每个 Spec 文档包含成对 `<!-- changelog -->` 标记包裹的变更日志章节，记录每次重大变更的时间、变更类型（added/modified/removed/deprecated）、变更描述。变更记录按时间倒序排列（最新在顶部）。

#### Scenario: 变更日志完整规范

- **WHEN** `spec.md` 包含成对的 `<!-- changelog -->` 标记
- **AND** `## Changelog` 位于标记之间
- **AND** 每条记录格式为 `YYYY-MM-DD | type | description`
- **AND** 记录按时间倒序排列
- **THEN** 格式检查通过

#### Scenario: 变更日志缺少结束标记

- **WHEN** `spec.md` 仅包含一个 `<!-- changelog -->` 开始标记
- **THEN** 格式检查输出警告提示添加结束标记

#### Scenario: 变更日志缺失

- **WHEN** `spec.md` 不包含任何 `<!-- changelog -->` 标记
- **THEN** 格式检查输出警告："缺少变更日志章节"

### Requirement: Scenario 格式兼容

系统 SHALL 的格式检查脚本同时兼容两种 Scenario WHEN/THEN 书写格式：五级标题格式（`##### WHEN`）和列表项加粗格式（`- **WHEN**`），两种格式均视为合规。

#### Scenario: 使用五级标题格式

- **WHEN** Scenario 内使用 `##### WHEN` 和 `##### THEN` 五级标题
- **THEN** 格式检查正确识别，无缺少 WHEN/THEN 错误

#### Scenario: 使用列表项加粗格式

- **WHEN** Scenario 内使用 `- **WHEN**` 和 `- **THEN**` 列表项加粗格式
- **THEN** 格式检查正确识别，无缺少 WHEN/THEN 错误

## MODIFIED Requirements

### Requirement: Spec 文档结构标准化

当前 spec 文档格式依赖人工审查与约定俗成，缺乏强制性的结构验证机制。系统 SHALL 引入自动化检查脚本 `check-spec-format.py`，对文档结构完整性进行系统性验证，支持多种格式变体兼容。

#### Scenario: 自动化结构验证

- **WHEN** 执行 `python .agents/scripts/check-spec-format.py --spec-dir .trae/specs/XXX`
- **THEN** 输出包含结构完整性评分（0-100）、错误列表、警告列表
- **AND** 有错误时退出码为 1，无错误时退出码为 0

#### Scenario: 批量检查所有 spec

- **WHEN** 执行 `python .agents/scripts/check-spec-format.py --check-all`
- **THEN** 递归检查 `.trae/specs/` 下所有包含 `spec.md` 的子目录
- **AND** 输出检查摘要，列出未通过的 spec 及其评分

## REMOVED Requirements

### Requirement: 强制中文括号章节标题

**Reason**: 实际项目中所有 spec 均使用纯英文标题（如 `## Why`），带中文括号的标题（如 `## Why（动机）`）从未被使用过。强制要求中文括号导致脚本无法识别现有文档，脱离实际。
**Migration**: 规范调整为两种格式均兼容（纯英文为推荐，中文括号为可选注释），脚本正则同时匹配两种模式。

#### Scenario: 旧文档无需迁移

- **WHEN** 现有 spec 使用纯英文章节标题（`## Why`）
- **THEN** 格式检查正常通过，无需修改文档
- **AND** 不产生缺少章节的错误
