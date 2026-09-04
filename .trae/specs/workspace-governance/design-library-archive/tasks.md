# Tasks

> 目标目录：`.agents/skills/`；源目录：`external/dao/xinzo/.trae-cn/design_libraries/`（只读）。沿用 spec 的命名映射表与完整性要求。

- [x] Task 1: 生成并冻结迁移清单（migration-manifest.md）
  - [x] 1.1 遍历 16 个源目录，收集每个设计库的 metadata.json + SKILL.md name + 文件数/字节数
  - [x] 1.2 断言唯一设计库 = 16，目标目录名与命名映射表一致
  - [x] 1.3 将结果写入 `.trae/specs/workspace-governance/design-library-archive/migration-manifest.md`（frontmatter 含 source 溯源）
  - [x] 1.4 自检：任何设计库无选中结果或选中源目录不存在 → 终止并报告

- [x] Task 2: 归档前 8 个设计库（21th/apple/barbie/claude/doubao/golden_time/google/minimalist）
  - [x] 2.1 将各设计库**整目录**复制到 `.agents/skills/<skill-name>/`，排除 `__MACOSX/`
  - [x] 2.2 对 doubao/golden_time 的 SKILL.md 前置最小 frontmatter（含 name/description/source/user-invocable）
  - [x] 2.3 修复 golden_time/SKILL.md 中所有 `/workspace/.design_library/goldentime/...` 为相对路径 `./...`
  - [x] 2.4 对所有 8 个新 SKILL.md 增补 `source` 溯源字段
  - [x] 2.5 自检：目录数与 manifest 一致，SKILL.md 存在且 frontmatter 可解析，source 已写入

- [x] Task 3: 归档后 8 个设计库（motion_fit/nerv/tik_tok/trae/trae_work/vercel/volcengine/vibe_camp）
  - [x] 3.1 将各设计库**整目录**复制到 `.agents/skills/<skill-name>/`，排除 `__MACOSX/`
  - [x] 3.2 对 trae 的 SKILL.md 前置最小 frontmatter（描述从 TRAE(1)/README.md 推断）
  - [x] 3.3 对 trae_work/volcengine 的 SKILL.md 前置最小 frontmatter
  - [x] 3.4 对所有 8 个新 SKILL.md 增补 `source` 溯源字段
  - [x] 3.5 自检：目录数与 manifest 一致，SKILL.md 存在且 frontmatter 可解析，source 已写入

- [x] Task 4: 更新 `.agents/skills/README.md` 索引（依赖 Task 2-3）
  - [x] 4.1 新增「设计库镜像 Skill」分类小节（16 行，含名称/来源/功能描述/路径）
  - [x] 4.2 顶部引言更新为六类（追加第 6 类说明：设计库镜像 Skill）
  - [x] 4.3 追加 Changelog 条目（版本号 +1）
  - [x] 4.4 自检：16 个相对链接全部存在，无断链/无重复

- [x] Task 5: 归档验证（依赖 Task 2-4）
  - [x] 5.1 断言新增设计库目录恰为 manifest 的 16 个且各含 SKILL.md
  - [x] 5.2 断言 16 个新 SKILL.md frontmatter 均含 `source` 且值路径可解析
  - [x] 5.3 断言既有技能零改动：`git status --porcelain` 对已有技能无 M/D
  - [x] 5.4 断言无 `__MACOSX/` 残留于目标目录
  - [x] 5.5 断言 golden_time SKILL.md 无 `/workspace/.design_library/` 绝对路径残留
  - [x] 5.6 前端 matter 解析级兜底：16 个 SKILL.md 全扫，真实解析失败 = 0

- [x] Task 6: 原子提交（依赖 Task 5 全绿）
  - [x] 6.1 经 atomic-commit-cmd 执行单一职责提交（`chore(.agents): 归档 16 个 Trae 设计库并登记索引`，主体中文）
  - [x] 6.2 提交后核对暂存区与工作树状态

# Task Dependencies

- Task 2 / 3 相互独立，可并行执行。
- Task 4 依赖 Task 2-3（复制与溯源完成后才能登记索引）。
- Task 5 依赖 Task 2-4。
- Task 6 依赖 Task 5（验证全绿后才允许提交）。
