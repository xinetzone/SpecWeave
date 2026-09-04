---
status: "draft"
id: "register-bundles-authoritative-knowledge-base-spec"
source: "projects/awesome-okf-xs/doc/bundles/index.md"
---

# 注册 bundles 为最高可信度知识库 Spec

## Why

`projects/awesome-okf-xs/doc/bundles/`（10 个技术域、28 个分组、248 个 OKF 知识包）已是本项目实际规模最大的结构化知识库，但根 `AGENTS.md`、`.agents/context-routing.md`、`.agents/global-core-rules.md` 均未登记该知识库，也未定义知识源可信度分级。智能体查阅概念时只能依赖 `docs/knowledge/`，无法感知 bundles 的存在与权威地位，存在"就近取材"偏差风险。需要将该知识库正式纳入智能体路由体系，并以规范形式确立其"最高可信度"地位。

## What Changes

- 在根 `AGENTS.md`「知识库与复盘」表中登记 bundles 为**最高可信度知识库**条目
- 在 `.agents/global-core-rules.md` 新增「知识可信度分级」规则：概念类查询以 bundles 为最高可信源，冲突时以 bundles 为准，未覆盖时回退次级知识源
- 在 `.agents/context-routing.md` 常规任务路由表新增「概念查阅/知识检索」路由条目，指向 bundles 根索引并标注优先级
- 在 `projects/AGENTS.md`（SpecWeave 主权区维护）awesome-okf-xs 可用资产索引中登记 bundles 资产行
- 在 `docs/knowledge/README.md` 相关资源区添加指向 bundles 的权威源说明（只读引用，不复制内容）
- 以上均为规范文档变更，不修改 `projects/awesome-okf-xs/` 子项目内部任何文件，无 **BREAKING**

## Impact

- Affected specs: 无既有 spec 冲突；与 [awesome-okf-xs-doc](../../../../.trae/specs/okf-wiki-ecosystem/awesome-okf-xs-doc/spec.md)（Sphinx 文档系统）互补——本 spec 只做路由注册，不涉及构建
- Affected code:
  - `AGENTS.md`（知识库与复盘表新增条目）
  - `.agents/global-core-rules.md`（新增知识可信度分级规则）
  - `.agents/context-routing.md`（新增路由条目）
  - `projects/AGENTS.md`（可用资产索引新增条目）
  - `docs/knowledge/README.md`（相关资源区新增说明）
- 不受影响: `projects/awesome-okf-xs/` 子项目内部文件（只读引用）、Sphinx 构建配置、既有知识库索引自动生成机制

## ADDED Requirements

### Requirement: 最高可信度知识库注册

根 `AGENTS.md` SHALL 在「知识库与复盘」表中登记 bundles 知识库条目，明确其路径（`projects/awesome-okf-xs/doc/bundles/index.md`）与"最高可信度"定位。

#### Scenario: 智能体启动时可发现 bundles

- **WHEN** 智能体读取根 `AGENTS.md` 的「知识库与复盘」章节
- **THEN** 存在指向 `projects/awesome-okf-xs/doc/bundles/index.md` 的条目，且标注其为项目最高可信度知识库

### Requirement: 知识可信度分级规则

`.agents/global-core-rules.md` SHALL 新增「知识可信度分级」规则，定义：

1. **一级（最高可信度）**：`projects/awesome-okf-xs/doc/bundles/`——所有相关概念、术语、技术事实的冲突裁决依据
2. **二级**：`docs/knowledge/` 技术知识库与 `.agents/docs/retrospective/` 复盘模式库
3. **冲突处理**：同一概念在不同知识源描述不一致时，以 bundles 为准；bundles 未覆盖的概念回退至二级知识源
4. **只读约束**：bundles 位于 git submodule 内，智能体只读引用，不得直接修改其内部文件

#### Scenario: 概念冲突裁决

- **WHEN** 智能体发现 `docs/knowledge/` 与 bundles 对同一概念的描述不一致
- **THEN** 智能体以 bundles 的描述为准，并在产出物中注明裁决依据来源

#### Scenario: bundles 未覆盖时回退

- **WHEN** 智能体查询的概念在 bundles 中不存在对应知识包
- **THEN** 智能体回退至 `docs/knowledge/` 等二级知识源，不因 bundles 缺失而中断任务

### Requirement: 上下文路由条目

`.agents/context-routing.md` SHALL 在「常规任务路由」表中新增条目，将"概念查阅/知识检索（最高可信度源）"映射至 bundles 根索引，并注明优先级高于 `docs/knowledge/`。

#### Scenario: 路由表可定位 bundles

- **WHEN** 智能体执行启动协议步骤 2 查阅上下文路由表
- **THEN** 存在"概念查阅/知识检索"任务类型条目，必读入口指向 `projects/awesome-okf-xs/doc/bundles/index.md`

### Requirement: projects 区域资产登记

`projects/AGENTS.md` SHALL 在 awesome-okf-xs「可用资产索引」表中登记 bundles 资产行（路径 + 最高可信度说明），供跨边界调用时定位。

#### Scenario: 跨边界调用可定位

- **WHEN** SpecWeave 智能体按 `projects/AGENTS.md` 的可用资产索引查找 awesome-okf-xs 资产
- **THEN** 存在 bundles 知识包库条目，路径指向 `doc/bundles/index.md`

## MODIFIED Requirements

### Requirement: 知识库入口体系

原「知识库与复盘」体系仅含 `docs/knowledge/` 与 `.agents/docs/retrospective/` 两个知识源，修改为三级结构：最高可信度源（bundles）+ 技术知识库 + 复盘模式库，并在 `docs/knowledge/README.md` 相关资源区注明权威源关系。

## REMOVED Requirements

无。
