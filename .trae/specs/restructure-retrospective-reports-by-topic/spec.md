# 复盘报告目录按主题分类重构 Spec

## Why

`docs/retrospective/reports/` 当前为扁平结构，34 个原子化子目录与 33 份源 `.md` 文件全部平铺在同一层级下，缺乏按主题维度的逻辑分组。用户查找特定主题领域的报告时，需逐一翻阅文件名猜测内容归属，检索效率低下。现有 `docs/retrospective/README.md` 已按"智能体规范体系""文档体系重构""工具与自动化"等主题对报告做了分类索引，但文件系统层面仍为扁平结构，分类未映射到目录层级。

## What Changes

- 在 `docs/retrospective/reports/` 下创建 5 个主题子文件夹，将全部报告按主题归类移入
- 每个主题子文件夹包含对应的原子化子目录及其源 `.md` 文件
- 创建 `docs/retrospective/reports/README.md` 说明主题分类标准、文件组织规则与快速导航
- 修正因文件移动导致的 TOML frontmatter `source` 字段路径引用
- 修正 `docs/retrospective/README.md` 中 reports/ 部分的目录树及分类索引
- 修正所有原子化子目录 README 中的内部链接（子模块导航表、关联报告引用）
- 修正各子模块文档中的相对链接引用
- **BREAKING**: 所有 reports/ 下的文件路径发生变更，外部引用需同步更新

## Impact

- Affected specs: 无现有 spec 受影响
- Affected code: 无代码文件受影响（纯文档重构）
- Affected files:
  - `docs/retrospective/reports/` 下全部 67 个文件/目录
  - `docs/retrospective/README.md`

## ADDED Requirements

### Requirement: 主题分类体系

系统 SHALL 将 `docs/retrospective/reports/` 下的全部报告按以下 5 个主题类别组织到对应子文件夹中：

| 主题文件夹 | 说明 | 报告数量 |
|-----------|------|----------|
| `atomization/` | 原子化与文档重构（内容拆分、模块化、README 原子化、复盘文档重构、协作场景迁移、子代理提取） | 9 |
| `insight-extraction/` | 洞察与萃取（知识发现、方法论提炼、优化循环、元分析、README 演进） | 8 |
| `spec-system/` | 规范体系建设（Agents Spec System、规范一致性、成熟度标准、模式自动化、事实表述修正、文件命名规范） | 7 |
| `roles-teams/` | 角色与团队管理（co-founder 角色标记与改进执行、团队管理模块） | 3 |
| `project-governance/` | 项目治理（应用目录创建、系统规划、Code Wiki 生成、建议执行、工具熵优化、导出卡片、报告重复优化） | 7 |

#### Scenario: 文件移动后目录结构清晰可导航

- **WHEN** 用户在 `docs/retrospective/reports/` 下浏览
- **THEN** 看到 5 个主题子文件夹和一个 README.md 索引文件
- **AND** 每个主题子文件夹内包含该主题的全部报告（原子化子目录 + 源 .md 文件）

### Requirement: 分类 README 文档

系统 SHALL 在 `docs/retrospective/reports/README.md` 中提供：
1. 5 个主题类别的定义与说明
2. 每个类别下的完整报告清单（含简要描述）
3. 文件组织规则说明（原子化子目录与源 .md 文件的关系）
4. 快速查找指南

#### Scenario: 新成员快速了解报告组织方式

- **WHEN** 新团队成员打开 `docs/retrospective/reports/README.md`
- **THEN** 能在 30 秒内理解分类标准和文件组织规则
- **AND** 能通过分类索引快速定位目标报告

### Requirement: 移动后链接完整性

移动完成后，所有报告内部的相对链接 SHALL 保持有效。

#### Scenario: 原子化子目录内部链接有效

- **WHEN** 在原子化子目录的 README.md 中点击子模块导航链接
- **THEN** 正确跳转到同目录下的子模块文档

#### Scenario: 关联报告引用有效

- **WHEN** 在 README.md 中点击关联报告链接
- **THEN** 正确跳转到目标报告的目录或文件

### Requirement: 上级 README 同步更新

系统 SHALL 同步更新 `docs/retrospective/README.md`：
1. 目录树中 `reports/` 部分反映新的主题分组结构
2. 按主题分类的报告索引更新为新的路径格式

#### Scenario: 上级索引与文件系统一致

- **WHEN** 用户查看 `docs/retrospective/README.md` 的 reports 部分
- **THEN** 目录树与实际文件结构一致
- **AND** 分类索引中的路径链接均有效

## MODIFIED Requirements

无现有需求被修改。

## REMOVED Requirements

无现有需求被移除。
