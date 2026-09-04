# Checklist — import-builtin-skills

> 逐项核验；全部通过后以单一职责原子提交收尾。

## 迁移完整性（Requirement: 全面去重导入内置技能）
- [x] 盘点得出 24 个唯一技能名，新增恰为 21 个目录，跳过既有 3 个（TRAE-plan-mode / TRAE-spec-mode / TRAE-computer-use-ptc）
- [x] 21 个新目录均位于 `.agents/skills/<name>/` 且各含 SKILL.md
- [x] migration-manifest.md 已生成并含 name / selected_source_dir / target_dir / files / bytes，选择规则与 spec 一致
- [x] 重复候选按确定性规则选版（总字节 ↓ → 文件数 ↓ → 路径 asc），manifest 无缺失、源路径全部真实存在

## 保留既有同名（Requirement: 保留既有同名技能不动）
- [x] TRAE-plan-mode / TRAE-spec-mode / TRAE-computer-use-ptc 三个既有目录内容未被覆盖或修改
- [x] `git status --porcelain .agents/skills/TRAE-*` 无 M 记录（仅可能有本次新增的同名项被跳过）

## 轻治理溯源与登记（Requirement: 轻治理溯源与登记）
- [x] 21 个新 SKILL.md frontmatter 均含 `source`，值指向原始内置相对路径，YAML 可解析无引号陷阱
- [x] 技能包内自带 LICENSE（如有）原样保留
- [x] `.agents/skills/README.md` 新增「内置镜像 Skill」分类表（21 技能，链接真实存在）
- [x] README Changelog 已追加新条目（版本号 +1），既有条目未删改
- [x] 源目录 `external/dao/xinzo/.trae-cn/builtin/` 未被移动或删除任何文件

## 验证与提交（Requirement: 迁移验证与原子提交）
- [x] 新增体积/文件数合计约 17.9MB / 750 文件（±5%）
- [x] 全量文件已纳入 git 暂存（大资产如 *.ttf/*.min.js 若被 .gitignore 拦截则已用 `git add -f`）
- [x] `git status --porcelain .agents/skills` 仅含本次 21 目录新增，无对既有文件的意外修改
- [x] 技能扫描/质量兜底无解析级错误（skill-creator 与 vendor 同名 WARN 属预期，已记录）
- [x] 原子提交完成（conventional commit，单一职责，add 与 commit 分开执行并核对暂存集，提交 4c7f6798e），提交后工作树无本次变更残留
