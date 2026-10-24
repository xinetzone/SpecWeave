# 案例：declared-consistency-fix 用户级 → 主权区迁移

本案例来自会话 `0b5028ae-4c67-46da-8e99-0c2b68ae9c3a`，是 `user-skill-sovereign-migration` 的首个实证来源。它记录的不是“顺利路径”，而是两次位置纠正、一次质量门返工和一次 move 收尾。

## 1. 背景

`declared-consistency-fix` 最初在用户级目录 `~/.qoder/skills/declared-consistency-fix` 创建并可正常工作：有 `SKILL.md`、`references/case-xuanspace-license.md`、`references/verification-recipes.md`、`scripts/check_license_consistency.py`。

问题不在内容，而在位置：用户级 Skill 不进入 SpecWeave 的 README 索引、capability-registry、TOML 镜像与 CHANGELOG，也不受仓库质量门与链接门约束。

## 2. 用户纠正（本技能存在的直接原因）

| 顺序 | 用户原话 | 含义 |
|---|---|---|
| 1 | “为何没有放在 `.agents/skills`?” | 位置判断缺失，Skill 被默认创建在用户级 |
| 2 | “移入 `.agents/skills` 目录” | 要求从“创建在哪”转为“迁移到哪” |

两次纠正指向同一个稳定痛点：**Skill 能在当前用户下触发，不等于它已进入团队治理体系**。创作流程默认落在用户级目录，而项目需要的是主权区原生 Skill。

## 3. 实际执行链

### 3.1 原生化 frontmatter

迁入时补齐了原生轨字段，并保留原有描述与来源说明。关键点：

- `name` 与目标目录名一致
- 增加 `version`、`argument-hint`、`user-invocable`、`disable-model-invocation`、`paths`
- `x-toml-ref` 从模板位置的 `../../` 改为 `../../../`，因为 SKILL.md 多了一层技能目录
- 不写入本机绝对路径

### 3.2 保真复制

正文与 `references/`、`scripts/` 使用文件复制，不手抄。复制后逐文件核对，`SKILL.md` 只允许 frontmatter 变化，正文保持原样。

### 3.3 质量门：65 → 100

首次运行质量门得 65 分，构成是 **1 个 error（−15）+ 4 个 warn（−5×4）**。失败项不是功能问题，而是文档契约缺失：

| 失败项 | 实际缺什么 | 修复方式 |
|---|---|---|
| Why 解释（warn） | 0 处 `> **为什么？**` 引用块 | 补 2 处以上实质解释，不用 `## Why` 标题充数 |
| dry-run / 预览（error） | 写操作没有确认门 | 在工作流中加入“列变更 → 确认 → 写入” |
| 安全检查清单（warn） | 无清单或 `- [ ]` 少于 5 项 | 补 5 项以上真实可勾选项 |
| Gotchas（warn） | 标题未编号 | 改为 `## N. Gotchas（陷阱与反直觉行为）` |
| frontmatter 推荐字段（warn） | 缺 `version` 等字段 | 按原生模板补齐 |

修复后 34 项全过、100/100、退出码 0。结论：**用户级 Skill 直接迁移会稳定丢分**，因为用户级元数据契约更简；迁移与质量门修复应分成两步，不要在登记后再返工。

### 3.4 四处登记

`declared-consistency-fix` 在 README、`capability-registry/02-skills.md`、`.meta/toml` 镜像与 CHANGELOG 各登记一次。登记时发现既有计数漂移：README 完整Skill 表头 11、表体 12 行；registry 表头 9、表体 10 行。按“表头数字 = 表体行数”各自修正，并在 CHANGELOG 记录漂移修正本身，而不是悄悄改数字。

两个登记面的路径基准不同：

- README：`declared-consistency-fix/SKILL.md`
- registry：`../skills/declared-consistency-fix/SKILL.md`

### 3.5 链接门与一个既有误报

链接门扫描时出现 `source` 相关断链提示。核查后确认：该字段按“文件所在目录”解析，而原写法是仓库根相对路径，属于**迁移前就存在的写法问题**，不是本次新增行引入。处理方式：

1. 与 HEAD 对照，确认断链在迁移前已存在
2. 不把既有问题算作本次回归，但也不忽略
3. 在交付报告中单独归类，避免与新增断链混在一起

若断链确由新增行引入，则必须改到具体文件；指向目录的 Markdown 链接会被链接门判失败。

### 3.6 move 收尾

目标目录校验通过后，删除用户级实体源目录，完成从“用户级副本”到“主权区唯一权威副本”的 move。删除前满足了三个条件：目标完整、哈希一致、用户明确要求“移入”。

当前状态核实：`D:\spaces\SpecWeave\.agents\skills\declared-consistency-fix` 存在（`SKILL.md` + 2 个 references + 1 个 script），用户级 `~/.qoder/skills/declared-consistency-fix` 已不存在。该 Skill 没有保留用户级联接，属于“纯 move”；若需要用户级直接触发，应另建 Junction。

## 4. 后续演进：登记职责已移交

本案例发生时，四处登记、双门验收与用户级 Junction 还没有独立技能，步骤写在迁移流程内。现在这些职责由 `native-skill-surface-registration` 承担，本技能第 5 步只负责移交事实：

- 源路径、目标路径、源是实体目录还是联接
- frontmatter 变更摘要与已批准的正文变更
- 哈希与正文比对结果
- 质量门基线
- 是否已授权删除实体源目录

因此本案例中的手工登记细节只作历史参考；执行新迁移时不要复制那套模板，避免与 `native-skill-surface-registration` 的格式产生漂移。

## 5. 可复用结论

1. **位置决策要在创作前做**：Skill 只要依赖仓库脚本、规则或索引，就应直接落在 `.agents/skills`。
2. **迁移不是复制**：copy + 校验 + 联接/删除才构成 move；删除实体源目录必须单独授权。
3. **用户级与项目级元数据契约不同**：迁移必然触发 frontmatter 补齐，质量门要在登记前跑。
4. **计数漂移要按面独立校正**：README 与 registry 的基数不同，不能互相“对齐”。
5. **既有断链先定性再处理**：与 HEAD 对照，区分本次回归与历史问题。
6. **职责边界随资产演进**：登记与联接已有专用技能时，迁移技能只做交接，不重复实现。
