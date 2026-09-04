---
title: "设计库归档到 .agents/skills（design-library-archive）Spec"
status: "draft"
---

# 设计库归档到 .agents/skills（design-library-archive）Spec

## Why

`external/dao/xinzo/.trae-cn/design_libraries/` 下有 16 个 Trae 内置设计库（`dl_builtin_*`），镜像了 Trae IDE 内置设计系统技能。与 builtin skills 相同，这些目录 git-ignored 且不入库，导致设计库无法被项目技能体系统一发现/登记。本次将 16 个设计库完整归档至 `.agents/skills/`，实现自包含、不依赖外部源路径。

> **方法论映射（seven-concepts-cmd 场景3 重构优化，轻量链路）**：事实盘点（R/I，设计库清单与候选差异）→ 原子化分批迁移（A，按源目录并行）→ 原子提交（C）。G1/G4 质量门分别对应「去重清单客观可核验」与「单次提交单一职责」。

## 内容敏感度判定

- **级别：公开/工具内容**——被迁移对象为 Trae IDE 内置设计库（通用设计系统），不含个人凭证或隐私；仅来源目录位于用户私有镜像路径下（只读引用，不搬移/删除源）。
- **工作流**：标准工作流，规划落盘 `.trae/specs/workspace-governance/design-library-archive/`，产物入 `.agents/skills/` 并纳入 git。
- **溯源约束**：每个归档 SKILL.md 增补 `source` 字段指向原始设计库路径；排除 `__MACOSX/` macOS 元数据目录。

## What Changes

- **新增 16 个设计库目录**至 `.agents/skills/<skill-name>/`（扁平结构），全量纳入 git。
- **跳过 `__MACOSX/` 目录**（macOS 资源分支元数据，非实际设计库内容）。
- **命名映射**（来自 metadata.json `name` + SKILL.md `name` frontmatter）：

| 源目录 | metadata.name | SKILL.md name | 目标 Skill 目录名 |
|---|---|---|---|
| dl_builtin_21th | 21th | 21th-design | 21th-design |
| dl_builtin_apple | 苹果 | pinguo-apple-design | pinguo-apple-design |
| dl_builtin_barbie | Barbie | barbie-design | barbie-design |
| dl_builtin_claude | Claude | claude-design-system-design | claude-design-system-design |
| dl_builtin_doubao | 豆包 | (无 frontmatter) | doubao-design |
| dl_builtin_golden_time | Golden Time | (无 frontmatter) | golden-time-design |
| dl_builtin_google | 谷歌 | google-design | google-design |
| dl_builtin_minimalist | 极简 | minimal-dashboard-design | minimal-dashboard-design |
| dl_builtin_motion_fit | Motion Fit | motionfit-design | motionfit-design |
| dl_builtin_nerv | Nerv | nerv-design | nerv-design |
| dl_builtin_tik_tok | 抖音 | tiktok-design | tiktok-design |
| dl_builtin_trae | TraeCode | Nimbus Core（无 frontmatter） | nimbus-core-design |
| dl_builtin_trae_work | TraeWork | TraeWork Design System（无 frontmatter） | trae-work-design |
| dl_builtin_vercel | Vercel | vercel-design-library-design | vercel-design-library-design |
| dl_builtin_volcengine | 源力 | 源力设计系统 (Yuanli Design System)（无 frontmatter） | yuanli-design-system |
| dl_builtin_vibe_camp | Vibe Camp | vibecamp-design | vibecamp-design |

- **路径修复**：`dl_builtin_golden_time/SKILL.md` 含硬编码绝对路径（`/workspace/.design_library/goldentime/...`），归档后须替换为相对路径（`./...`）。
- **轻治理**：① 每个归档 SKILL.md frontmatter 增补 `source` 溯源；② `.agents/skills/README.md` 新增「设计库镜像 Skill」分类索引并更新 Changelog。
- **源目录只读**：不移动、不删除 `external/dao/xinzo/.trae-cn/design_libraries/` 下任何文件。

## Impact

- Affected specs：无（新建独立 spec）。
- Affected code：
  - `.agents/skills/<16 个新设计库目录>/**`（新增）
  - `.agents/skills/README.md`（索引与 Changelog）
  - `.trae/specs/workspace-governance/design-library-archive/migration-manifest.md`（清单证据）
- **风险与已知限制**：
  - `dl_builtin_golden_time/SKILL.md` 含 10+ 处绝对路径引用 `/workspace/.design_library/goldentime/`，归档后须全部替换为相对路径。
  - `dl_builtin_trae` 顶层无 SKILL.md（仅在 `TRAE(1)/` 子目录），归档时取 `TRAE(1)/` 内完整版本。
  - `dl_builtin_doubao`、`dl_builtin_golden_time`、`dl_builtin_trae`、`dl_builtin_trae_work` 的 SKILL.md 无 YAML frontmatter，归档时前置最小 frontmatter（含 `name`、`description`、`source`、`user-invocable: true`）。
  - 导入设计库保持内置原貌，`check-skill-quality` 类格式门可能 WARN，轻治理阶段主动接受（同 builtin skills 先例）。
  - `.meta/toml`/capability-registry 未同步更新，技能在 TOML 驱动面板/registry 层不可见（明确留作后续任务）。

## ADDED Requirements

### Requirement: 完整归档 16 个设计库
系统 SHALL 将 16 个设计库整目录复制到 `.agents/skills/<skill-name>/`，排除 `__MACOSX/` 目录，保留全部子文件（assets/icons、components/*.json、preview/*.html、ui_kits、css.json、metadata.json 等）。

#### Scenario: 16 个设计库目录全量归档
- **WHEN** 执行归档
- **THEN** `.agents/skills/` 下新增 16 个设计库目录，目录名如表所示；每个目录不含 `__MACOSX/`；各目录含 SKILL.md + metadata.json + 完整子树

#### Scenario: 绝对路径修复
- **WHEN** 处理 `golden-time-design/SKILL.md`
- **THEN** 所有 `/workspace/.design_library/goldentime/...` 替换为 `./...`（相对路径），共约 10+ 处

#### Scenario: 无 frontmatter SKILL.md 前置最小 frontmatter
- **WHEN** 处理 doubao/golden_time/trae/trae_work 的 SKILL.md
- **THEN** 文件顶部增补 YAML frontmatter，含 `name`、`description`、`source`、`user-invocable: true`（description 从现有标题/内容推断）

### Requirement: 保留既有同名技能不动
系统 SHALL 不覆盖 `.agents/skills/` 中已存在的设计库同名目录（若存在）。

#### Scenario: 导入过程零改动既有目录
- **WHEN** 执行全部复制
- **THEN** `.agents/skills/` 中已有的同名设计库目录内容与 git 状态保持原样

### Requirement: 轻治理溯源与登记
系统 SHALL 为每个归档设计库增补 frontmatter `source` 溯源，并在 `.agents/skills/README.md` 登记。

#### Scenario: source 溯源完整
- **WHEN** 归档完成
- **THEN** 16 个新 SKILL.md 的 YAML frontmatter 均含 `source` 字段，值指向原始设计库相对路径

#### Scenario: README 索引登记
- **WHEN** 归档完成
- **THEN** `.agents/skills/README.md` 新增「设计库镜像 Skill」分类表（含名称/来源/功能描述/路径）并追加 Changelog 条目

### Requirement: 归档验证与原子提交
系统 SHALL 验证归档完整性并以单一职责原子提交收尾。

#### Scenario: 完整性验证通过
- **WHEN** 全部复制与登记完成
- **THEN** 断言：目标 16 个设计库目录数正确、每个含 SKILL.md、source 字段全覆盖、`git status --porcelain .agents/skills` 仅含新增（无对既有文件的修改）、无 `__MACOSX/` 残留

#### Scenario: 原子提交
- **WHEN** 验证全部通过
- **THEN** 经 atomic-commit-cmd 提交单一变更（conventional commit，主体中文，单一职责：归档设计库），不混入其他变更

## MODIFIED Requirements

（无既有需求被修改）

## REMOVED Requirements

（无既有需求被移除）

## Changelog

- **v0.1** (2026-09-03)：初稿。五决策已确认（完整归档16个 / 排除__MACOSX/ / 绝对路径修复 / 前置最小frontmatter / 全量入git）。
