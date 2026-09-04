# 导入 Trae 内置技能至 .agents/skills（import-builtin-skills）Spec

## Why

`external/dao/xinzo/.trae-cn/builtin/{work,global,design,code,trae}` 五个目录镜像了 Trae IDE 内置技能集（git-ignored，不入库），而 `.agents/skills/` 是 SpecWeave 主权区技能唯一权威目录。当前内置技能散落于非跟踪镜像中，既无法被项目技能体系统一发现/登记，也无法进入版本控制。本次将五个目录下全部技能**扁平去重取最全版**并入 `.agents/skills/`，实现「单一事实来源」统一入口（先例：TRAE-plan-mode/TRAE-spec-mode v1.13 已自 `builtin/trae/doutops` 集成）。

> **方法论映射（seven-concepts-cmd 场景3 重构优化，轻量链路）**：事实盘点（R/I，技能清单与候选差异）→ 原子化分批迁移（A，按来源家族并行）→ 原子提交（C）。G1/G4 质量门分别对应「去重清单客观可核验」与「单次提交单一职责」。

## 内容敏感度判定

- **级别：公开/工具内容**——被迁移对象为 Trae IDE 内置技能（通用工程工具），不含个人凭证或隐私；仅来源目录位于用户私有镜像路径下（只读引用，不搬移/删除源）。
- **工作流**：标准工作流，规划落盘 `.trae/specs/workspace-governance/import-builtin-skills/`，产物入 `.agents/skills/` 并纳入 git。
- **溯源约束**：每个导入 SKILL.md 增补 `source` 字段指向原始内置路径；技能包内自带 LICENSE（如 html-deck/LICENSE）原样保留。

## What Changes

- **新增 21 个技能目录**至 `.agents/skills/<name>/`（扁平结构，去重取最全版），约 750 文件 / 17.9MB，全量纳入 git。
- **跳过 3 个既有同名技能**：`TRAE-plan-mode`、`TRAE-spec-mode`（项目中文五要素适配版，保留现状）、`TRAE-computer-use-ptc`（已存在）。
- **去重选择规则（确定性）**：对每个技能名，跨五目录与全部 profile 收集候选，按「总字节 ↓ → 文件数 ↓ → 源路径字典序 asc」取唯一入选版本；结果冻结为 [migration-manifest.md](migration-manifest.md)（Task 1 生成）。
- **轻治理**：① 每个导入 SKILL.md frontmatter 增补 `source` 溯源；② `.agents/skills/README.md` 新增「内置镜像 Skill」分类索引并更新 Changelog。**不**改动 capability-registry / `.meta/toml` 镜像（留作后续增量）。
- **源目录只读**：不移动、不删除 `external/dao/xinzo/.trae-cn/builtin/` 下任何文件（镜像保留，用于同步/比对）。

## Impact

- Affected specs：无（新建独立 spec）。
- Affected code：
  - `.agents/skills/<21 个新技能目录>/**`（新增）
  - `.agents/skills/README.md`（索引与 Changelog）
  - `.trae/specs/workspace-governance/import-builtin-skills/migration-manifest.md`（清单证据）
- **新增技能清单（21）**：

| 来源家族 | 技能名 |
|---|---|
| work（办公/文档，8） | doc-writing-guide、docx、html-deck、html-report、pdf、pptx、research-guide、xlsx |
| global（通用，6） | TRAE-browseruse、TRAE-browseruse-external、TRAE-code-mode-orchestrator、TRAE-computer-use、digital-avatar-creator、dynamic-ui |
| design（设计，4） | design-library-creator、solo-design、solo-graphic-generation、solo-image-edit |
| code（基建，3） | feedback、skill-creator、TRAE-product-knowledge |

- **风险与已知限制**：
  - 仓库体积净增约 17.9MB（html-report 字体/echarts 等资产为主），已获用户确认全量入 git。
  - `skill-creator` 与 vendor `flexloop/apps/chaos/.agents/skills/skill-creator` 同名，auto-loader 扫描时可能出现重复名 WARN（非阻断；README 引用 vendor skill-creator 的既有指引不受影响）。
  - 导入技能保持内置原貌（英文、未做五要素适配），`check-skill-quality` 类格式门可能 WARN，轻治理阶段主动接受（同 TRAE-* v1.14 先例）。
  - `.meta/toml`/capability-registry 未同步更新，技能在 TOML 驱动面板/registry 层不可见（明确留待后续任务）。

## ADDED Requirements

### Requirement: 全面去重导入内置技能
系统 SHALL 将五个内置目录下全部技能并入 `.agents/skills/`，同名去重取最全版，共新增 21 个技能目录。

#### Scenario: 24 个技能名收敛为 21 个新增目录
- **WHEN** 盘点五源目录全部 SKILL.md 并按键名聚合
- **THEN** 得到 24 个唯一技能名；跳过既有 3 个（TRAE-plan-mode/TRAE-spec-mode/TRAE-computer-use-ptc），其余 21 个复制到 `.agents/skills/<name>/`

#### Scenario: 重复候选确定性选择
- **WHEN** 同一技能名存在多个候选目录（跨 top-level 目录或跨 profile，如 docx 在 work 的 4 个 profile 下各一份）
- **THEN** 按「总字节 ↓ → 文件数 ↓ → 源路径字典序 asc」唯一选版，且选择结果写入 migration-manifest.md 可复核

### Requirement: 保留既有同名技能不动
系统 SHALL 不覆盖 `.agents/skills/` 中已存在的 TRAE-plan-mode / TRAE-spec-mode / TRAE-computer-use-ptc。

#### Scenario: 导入过程零改动既有目录
- **WHEN** 执行全部复制
- **THEN** 上述 3 个既有技能目录内容与 git 状态保持原样（git status 中无 M 记录）

### Requirement: 轻治理溯源与登记
系统 SHALL 为每个导入技能增补 frontmatter `source` 溯源，并在 `.agents/skills/README.md` 登记。

#### Scenario: source 溯源完整
- **WHEN** 导入完成
- **THEN** 21 个新 SKILL.md 的 YAML frontmatter 均含 `source` 字段，值指向原始内置相对路径（如 `../../../external/dao/xinzo/.trae-cn/builtin/work/default/skills/html-deck` 形态），技能包内自带 LICENSE 文件保留

#### Scenario: README 索引登记
- **WHEN** 导入完成
- **THEN** `.agents/skills/README.md` 新增「内置镜像 Skill」分类表（含名称/来源家族/功能描述/路径）并追加 Changelog 条目（版本号 +1）

### Requirement: 迁移验证与原子提交
系统 SHALL 验证迁移完整性并以单一职责原子提交收尾。

#### Scenario: 完整性验证通过
- **WHEN** 全部复制与登记完成
- **THEN** 断言：目标 21 个技能目录数正确、每个含 SKILL.md、source 字段全覆盖、`git status --porcelain .agents/skills` 仅含新增（无对既有文件的修改）、体积/文件数合计约 750 / 17.9MB

#### Scenario: 原子提交
- **WHEN** 验证全部通过
- **THEN** 经 atomic-commit-cmd 提交单一变更（conventional commit，主体中文，单一职责：导入内置技能），不混入其他变更

## MODIFIED Requirements

（无既有需求被修改）

## REMOVED Requirements

（无既有需求被移除）

## Changelog

- **v0.1** (2026-09-03)：初稿。四决策已确认（扁平去重取最全版 / 保留既有同名 / 全量入 git / 轻治理索引登记）。
