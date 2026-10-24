# 质量门检查项映射表

本表对应 SpecWeave 仓库 `.agents/scripts/lib/check_skill_quality/` 的当前实现，核验日期 2026-10-23，共 34 个检查项。修改检查器版本后，须重新核对本表。

## 评分与退出码

- 起评分 100；每个失败项按 severity 扣分：error −15、warn −5、info −1；最低 0 分。
- 默认阈值 70；`--score --threshold 100` 时低于 100 即退出码 1。
- 完整模式只要存在 error 失败即退出码 1；warn 不导致退出码 1，但会扣分。
- `safety.*` 检查仅在正文命中写操作关键词时启用；未命中时只输出一条 info。

写操作关键词：`编辑`、`创建`、`删除`、`发布`、`更新`、`写`、`edit`、`create`、`delete`、`post`、`update`、`write`（大小写不敏感）。

## Frontmatter（7 项）

| 检查名 | 严重度 | 判定规则 | 修复 |
|---|---|---|---|
| `frontmatter存在` | error | 文件以 `---` 包裹的 YAML frontmatter | 补齐 frontmatter 块 |
| `frontmatter.name` | error | `name` 存在且非空 | 写入 Skill 名 |
| `frontmatter.description` | error | `description` 存在且非空 | 写入触发式描述 |
| `frontmatter.version` | warn | `version` 字段存在 | 补语义化版本 |
| `frontmatter.argument-hint` | warn | `argument-hint` 字段存在 | 补参数提示 |
| `frontmatter.user-invocable` | warn | `user-invocable` 字段存在 | 补布尔值 |
| `frontmatter.paths` | warn | `paths` 字段存在 | 补适用路径或 glob |

## Description（3 项）

| 检查名 | 严重度 | 判定规则 | 修复 |
|---|---|---|---|
| `description.length` | <50 时 error | 长度 ≥50 通过；<50 失败；<150 仅提示 | 扩写到 150–1024 字符 |
| `description.mandatory_phrase` | warn | 包含 `必须使用`、`Use this skill`、`必须`、`MUST use` 之一 | 加入强制触发措辞 |
| `description.trigger_context` | warn | 包含 `当用户`、`when`、`触发`、`提到` 之一 | 写明触发场景与用户原话 |

## 正文结构与安全（9 项）

| 检查名 | 严重度 | 判定规则 | 修复 |
|---|---|---|---|
| `file.length` | 超限时 error | 行数 ≤500 | 拆分到 `references/` |
| `why.explanations` | warn | `>\s*\*\*为什么` 匹配 ≥2 次 | 增加引用块式 Why |
| `why.vs_must_ratio` | warn | 失败条件：`**MUST` + `**必须` 数量 > Why 数 ×2 且 >3 | 减少加粗命令式规则，补 Why |
| `safety.write_ops_detected` | info | 命中写操作关键词即启用后续安全检查 | 无需修复 |
| `safety.dry_run` | error | 包含 `dry-run`、`dry_run`、`dryrun`、`预览`、`试运行`、`预演`、`预检`、`预检查`、`预提交`、`质量门` 之一 | 加入预览与确认门 |
| `safety.idempotent` | warn | 命中幂等关键词，**或**匹配 `步骤N: ...验证/确认/检查`，**或**勾选项含完成态词 | 写明重复执行策略与收尾验证 |
| `safety.checklist` | warn | 含「安全检查清单」或「检查清单……逐项」，且 `- [ ]` ≥5 个 | 建结构化清单 |
| `decision_tree.present` | 条件 warn | 仅当检测到多方案（`方案一`+`方案二` ≥2 或 `**方案1` ≥2）才检查；失败为 warn，单方案时输出 info | 单方案无需处理 |
| `trigger.tiered` | info | 不含 `T0/T1/T2` 分级时直接通过 | 无需修复 |

幂等关键词：`幂等`、`idempotent`、`重复检查`、`已存在`、`skipped`、`验证结果`、`无遗漏`、`无残留`、`收尾验证`、`无断链`、`已更新`。

勾选项完成态词：`已验证`、`已确认`、`已检查`、`已更新`、`已完成`、`已区分`、`已明确`、`无断链`、`无遗漏`、`无残留`、`更新了`。

## 路径（1 项）

| 检查名 | 严重度 | 判定规则 | 修复 |
|---|---|---|---|
| `paths.no_file_url` | error | 全文不得出现形如 `[文本](file:///...)` 或 `<file:///...>` 的绝对路径 | 改为相对路径或行内代码 |

## 开放标准（14 项）

| 检查名 | 严重度 | 判定规则 | 修复 |
|---|---|---|---|
| `open_standard.name.length` | warn | `name` ≤64 字符 | 缩短名称 |
| `open_standard.name.format` | warn | 全小写、kebab-case、仅字母数字与连字符、无首尾连字符、无连续连字符、无下划线 | 改为标准命名 |
| `open_standard.name.dir_match` | warn | `name` 与父目录名完全一致 | 改名或改目录 |
| `open_standard.name.compliant` | info | 仅当上述 name 检查全过时输出 | 修复 name 问题后会重新出现 |
| `open_standard.description.max_length` | warn | `description` ≤1024 字符 | 精简描述 |
| `open_standard.description.min_length` | warn | `description` ≥20 字符 | 补足描述 |
| `open_standard.description.trigger_hint` | info | 含 `when`、`使用`、`触发`、`提到`、`Use when`、`必须使用` 之一 | 建议补充，不影响分数 |
| `open_standard.structure.scripts` | info | 存在 `scripts/` 则为包含，否则提示可选 | 按需创建 |
| `open_standard.structure.references` | info | 存在 `references/` 则为包含，否则提示可选 | 按需创建 |
| `open_standard.structure.assets` | info | 存在 `assets/` 则为包含，否则提示可选 | 按需创建 |
| `open_standard.structure.evals` | info | 存在 `evals/` 则为包含，否则提示可选 | 按需创建 |
| `open_standard.custom_fields` | info | 列出标准与推荐字段之外的扩展字段 | 无需修复 |
| `open_standard.body.gotchas` | warn | 匹配 `^##\s+\d+\.\s*Gotchas` 或 `^##\s+\d+\.\s*(陷阱|反直觉|Gotchas)` | 改为带编号标题 |
| `open_standard.compliance` | info / warn | 所有 name 相关检查通过则合规 | 修复 name 问题 |

## 条件项与总数说明

- `decision_tree.present` 在单方案时仍输出 1 条通过结果。
- `trigger.tiered` 在未分级时仍输出 1 条通过结果；一旦出现 `T0/T1/T2`，会额外产生 `trigger.tiers_complete`（warn）与 `trigger.t2_action_intent`（warn），总数随之增加。
- `safety.write_ops_detected` 必输出 1 条；随后三条安全检查固定输出。
- 因此一份使用完整 frontmatter、单方案、未分级、含写操作关键词的 Skill，展开后为 34 条结果。

## 常见失败组合

- 65 分：`safety.dry_run`（−15）+ `why.explanations`、`safety.idempotent`、`safety.checklist`、`open_standard.body.gotchas`（各 −5）。
- 40 分：上述五项之外再缺 `version`、`argument-hint`、`user-invocable`、`paths`（各 −5）。
- 其他分数不要从分值反推组合；直接读 `--verbose` 输出里的失败清单，按实际检查名修复。

## 复跑命令

```bash
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --verbose
python .agents/scripts/check-skill-quality.py --path "<skill-dir>" --score --threshold 100
```

返回上级：[../SKILL.md](../SKILL.md)
