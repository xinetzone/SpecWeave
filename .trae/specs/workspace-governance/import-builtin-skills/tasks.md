# Tasks

> 目标目录：`.agents/skills/`；源目录：`external/dao/xinzo/.trae-cn/builtin/{work,global,design,code,trae}`（只读）。沿用 spec 的四决策与确定性选择规则（总字节 ↓ → 文件数 ↓ → 源路径字典序 asc）。
>
> **基线修正（Task 7 实测）**：导入前磁盘含 SKILL.md 目录 32（30 已跟踪 + 小写 `trae-computer-use-ptc` 未跟踪适配版 + 被忽略 `alipay-aipay`）；导入 21 后为 53，无 manifest 之外的多余新增。

- [x] Task 1: 生成并冻结迁移清单（migration-manifest.md）
  - [x] 1.1 用脚本（PowerShell/Python 均可）遍历五源目录全部 SKILL.md，按键名聚合候选（含 profile），按确定性规则选版；输出 `name / selected_source_dir / target_dir / files / bytes`
  - [x] 1.2 断言唯一技能名 = 24，新增 = 21（跳过 TRAE-plan-mode / TRAE-spec-mode / trae-computer-use-ptc），合计约 750 文件 / 17.9MB
  - [x] 1.3 将结果写入 `.trae/specs/workspace-governance/import-builtin-skills/migration-manifest.md`（frontmatter 含 source 溯源）
  - [x] 1.4 自检：任何技能名无选中结果或选中源目录不存在 → 终止并报告（禁止编造路径）

- [x] Task 2: 迁移 work 办公/文档家族（8 技能）：doc-writing-guide、docx、html-deck、html-report、pdf、pptx、research-guide、xlsx
  - [x] 2.1 依据 manifest 将各技能**整目录**复制到 `.agents/skills/<name>/`，保留 scripts/assets/references/LICENSE 等全部子文件
  - [x] 2.2 对每个新 SKILL.md 增补 frontmatter `source` 字段（值 = 仓库根相对的原 SKILL.md 路径）；无 frontmatter 则前置最小 frontmatter
  - [x] 2.3 自检：目录数与 manifest 一致（520 文件），SKILL.md 存在，source 已写入（YAML 可解析）
  - [x] 2.4 复制遇 git 忽略 → 记录并用 `git add -f` 纳入（实测无新文件被忽略）

- [x] Task 3: 迁移 global 通用家族（6 技能）：TRAE-browseruse、TRAE-browseruse-external、TRAE-code-mode-orchestrator、TRAE-computer-use、digital-avatar-creator、dynamic-ui
  - [x] 3.1 按 manifest 整目录复制到 `.agents/skills/<name>/`
  - [x] 3.2 增补 frontmatter `source`
  - [x] 3.3 自检：64 文件齐备；dynamic-ui 的 templates/tokens/scenes 子目录完整

- [x] Task 4: 迁移 design 设计家族（4 技能）：design-library-creator、solo-design、solo-graphic-generation、solo-image-edit
  - [x] 4.1 按 manifest 整目录复制到 `.agents/skills/<name>/`
  - [x] 4.2 增补 frontmatter `source`
  - [x] 4.3 自检：163 文件齐备；skill-release-manifest.json 保留

- [x] Task 5: 迁移 code 基建家族（3 技能）：feedback、skill-creator、TRAE-product-knowledge
  - [x] 5.1 按 manifest 整目录复制到 `.agents/skills/<name>/`
  - [x] 5.2 增补 frontmatter `source`
  - [x] 5.3 自检：3 文件齐备；未从多源重复复制

- [x] Task 6: 更新 `.agents/skills/README.md` 索引（依赖 Task 2-5）
  - [x] 6.1 新增「内置镜像 Skill」分类小节（work 8 / global 6 / design 4 / code 3 四张子表，21 行，含名称/来源家族/功能描述/路径）
  - [x] 6.2 顶部引言「分为四类」→「五类」并追加第 5 类说明（内置镜像 Skill）
  - [x] 6.3 追加 Changelog v1.15 条目
  - [x] 6.4 自检：21 个相对链接全部存在，无断链/无重复

- [x] Task 7: 迁移验证（依赖 Task 2-6）
  - [x] 7.1 断言新增技能目录恰为 manifest 的 21 个且各含 SKILL.md；磁盘总数 53（= 基线 32 + 新增 21），无 manifest 之外的多余新增
  - [x] 7.2 断言 21 个新 SKILL.md frontmatter 均含 `source` 且值路径可解析（21/21 PASS）
  - [x] 7.3 断言既有技能零改动：`git status --porcelain` 对 TRAE-plan-mode / TRAE-spec-mode / computer-use-ptc（含大小写变体）无 M/D；git index 无 computer-use-ptc 跟踪记录（既有为磁盘未跟踪小写适配版，保持现状未纳入）
  - [x] 7.4 断言新增体积/文件数合计 750 文件 / 18,305KB（manifest 18,303KB，偏差 +0.01%）；无新文件被 git 忽略
  - [x] 7.5 暂存核对：`git add .agents/skills .trae/specs/workspace-governance/import-builtin-skills` 后 staged 集合 = A 754（750 技能文件 + 4 spec 文件）+ M 1（README.md），无 D、无对既有技能文件的 M；将不属于本次范围的未跟踪 `trae-computer-use-ptc/` 移出暂存（磁盘保留不动）
  - [x] 7.6 frontmatter 解析级兜底：53 个含 SKILL.md 目录全扫，真实解析失败 = 0

- [x] Task 8: 原子提交（依赖 Task 7 全绿）
  - [x] 8.1 经 atomic-commit-cmd 执行单一职责提交（`chore(.agents): 导入 21 个 Trae 内置技能并登记索引`，主体中文），add 与 commit 分两次调用并核对暂存集（提交哈希 4c7f6798e，755 文件）
  - [x] 8.2 提交后核对暂存区与工作树状态（残留的未跟踪 trae-computer-use-ptc/ 属既有现状，非本次引入，不入提交）

# Task Dependencies

- Task 2 / 3 / 4 / 5 相互独立，可并行执行（各任务内同一文件的编辑必须串行，不同文件可并行）。
- Task 6 依赖 Task 2-5（复制与溯源完成后才能登记索引）。
- Task 7 依赖 Task 2-6。
- Task 8 依赖 Task 7（验证全绿后才允许提交）。
