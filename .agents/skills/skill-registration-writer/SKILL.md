---
name: skill-registration-writer
version: 1.0.0
description: "把 Skill 四处登记面的写入动作封装为可复跑的执行器：复用只读判定器的漂移事实，按 --assign 为漏登记技能显式指定分类后插入 README 与 registry 表行并同步（N个）计数，按 --note 在 CHANGELOG 顶部插入版本条目，镜像缺失时新建 .meta/toml/SKILL.toml；默认 dry-run，--write 才落盘，写前哈希校验 + 备份 + --revert 回滚，已对齐仓库复跑零改动。当用户提到「写入登记面」「补表行」「同步分类计数」「生成 SKILL.toml 镜像」「--assign 指定分类」「--note 写版本条目」「幂等重跑零改动」「回滚登记面改动」时必须使用此技能；不用于只读审计（用 skill-registry-count-drift-audit），不用于人工逐字套模板登记（用 native-skill-surface-registration）。"
argument-hint: "--assign <name>=<category> [--note <text>] [--write | --revert]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/README.md"
  - ".agents/capability-registry/02-skills.md"
  - ".agents/skills/CHANGELOG.md"
  - ".meta/toml/.agents/skills"
source: "P0 治理项「Skill 四处登记面生成器」阶段二：把 check-skill-registration.py 的只读判定事实封装为受边界约束的写入能力"
x-toml-ref: "../../../.meta/toml/.agents/skills/skill-registration-writer/SKILL.toml"
---

# Skill 登记面写入器

登记面的「判定」已经有只读尺子（`check-skill-registration.py`），「执行」此前仍靠手工对照。本技能把执行部分固化为一个脚本：**判定只信尺子，写入只动允许的两类行**。

目标产物：

1. 一份 dry-run 计划：要插哪几行、哪几个计数从 N 改到 M、CHANGELOG 新条目的版本号与正文；
2. `--write` 后四类改动按计划落盘，并附带回滚记录路径；
3. 写入后立即复跑，输出「零待办（幂等）」或剩余待办。

## 1. 适用边界

适用：

- 某原生技能已落盘、但 README/registry 缺行，需要按显式分类补行并同步计数。
- 已登记技能的 `.meta/toml` 镜像缺失，需要按五字段惯例补建。
- 需要为一次登记写 CHANGELOG 版本条目（取号 + 日期 + 说明）。
- 需要证明「在已对齐的仓库上重跑零改动」。

不适用：

- 只想知道哪里漂移、不想改任何文件 —— 用 `skill-registry-count-drift-audit` 或判定器本身。
- 需要逐字推敲表格措辞、分类归属尚无结论 —— 用 `native-skill-surface-registration` 人工流程。
- 修改 SKILL.md 正文、frontmatter 或质量门修复 —— 不属于本技能写权限。

> **为什么？** 判定与写入是两种权限。判定器已被验证「只读、可复跑、自检双向」；把写入塞进它会让「审计基线」失去可信度。反过来，写入器只消费判定结果，不自行解释表格，才不会出现「尺子量出 A、手写出 B」。

## 2. 参数契约

| 参数 | 必填 | 作用 |
|---|---|---|
| `--assign <name>=<category>` | 漏登记时必填 | 为目标技能显式指定分类；可重复。**不提供则只报告，不插入任何行** |
| `--note <text>` | 落表行或建镜像时必填 | CHANGELOG 条目正文；脚本自动取号与日期 |
| `--write` | 否 | 缺省永远 dry-run；只有显式开关才落盘 |
| `--only readme,registry,toml,changelog` | 否 | 限定作用面；缺省四处全开 |
| `--revert [journal]` | 否 | 按回滚记录撤销上一轮；缺省取最新一条 |
| `--json` | 否 | 输出机器可读计划，便于二次比对 |
| `--self-test` | 否 | 夹具自检（见第 6 节） |

`--assign` 的语义是「声明归属」，不是「猜归属」：分类名必须与 README 已有分类标题逐字一致，否则直接阻塞并列出可选分类。

> **为什么？** 分类归属是判断，字符串相似度做不了这个判断。`loop-engineering-cmd` 既可以读成命令集门面也可以读成脚本命令门面，任何自动贴标签都会把一个待确认的决策伪装成已完成的事实。脚本只接受人给的答案，把「未给答案」显式列进「待指定分类」。

## 3. 写入边界模型

每份文件只允许两类改动：

1. **计数 token**：分类标题行内 `（N个）` 的数字本身，其他字符不动；
2. **整行插入**：指定分类首张表最后一行之后插入一行；CHANGELOG 在最新条目之前插入一条。

落盘前依次执行三道具名检查：

- **越界断言**：用 `difflib` 对旧/新行序列求 opcode，任何 `replace`/`insert` 不落在允许行号即中止；
- **行数守恒**：新行数必须等于旧行数 + 计划插入数；
- **写前哈希**：计划时记录 sha256，写入前重算，不一致（并发改写）立即中止。

通过后先备份到 `.temp/skill-registration-writer/backup/<ts>/` 再原地替换，并把 journal 写成 `.temp/skill-registration-writer/journal-<ts>.json`（`.temp/` 已被 gitignore 覆盖）。

> **为什么？** 「只改登记面指定区块」必须可被机器验证，不能靠代码自觉。opcode 断言把「我以为只改了计数」变成「改动集合与允许集合逐项相等」；写前哈希则把共享工作树里其他会话的并发提交挡在门外，而不是覆盖掉。

## 4. 四类改动的生成规则

| 改动 | 生成来源 | 幂等条件 |
|---|---|---|
| README 表行 | SKILL.md frontmatter 的 `description` 摘要 + `「」` 触发词 | 该面已存在同名行即跳过 |
| registry 表行 | 同上，路径基准 `../skills/<name>/SKILL.md` | 同上；镜像轨技能不写 registry |
| 分类计数 | `实际数据行 + 本次插入数`，实际值取自判定器 | 声明已等于目标即跳过 |
| CHANGELOG 条目 | `--note` + 现有最大版本号 +1（末段递增） | 已存在以同说明结尾的条目即跳过 |
| TOML 镜像 | `id/title/category/date/version` 五字段，`version` 取两段快照 | 镜像已存在即跳过 |

README 与 registry 的行内路径基准不同（`<name>/SKILL.md` 与 `../skills/<name>/SKILL.md`），由两个 `*_row()` 各自生成，禁止互抄。

无 `version` 的技能（frontmatter 未声明）按仓内既有写法处理：README 类型列只写分类名不带 `（vX）`，registry 版本列写 `-`，TOML 镜像 `version` 回落 `1.0`。`description` 为 `>-` / `|` 块标量时先展开再取摘要与触发词。

> **为什么？** 两面基准不同是历史约定，互抄会产出能看不能点的断链；`version` 取两段快照是因为镜像库里 84 个样本中 70 个与 SKILL.md 不同，写入器跟随多数惯例，避免每次登记都制造一批「版本漂移」假发现。无版本时宁留空位也不编造 `v0.0.0`，否则会把「未声明」伪造成一个真实版本号。

## 5. 运行方式

```bash
# 0) 自检夹具：先证明写入器本身可用
python .agents/skills/skill-registration-writer/scripts/apply_registration.py --self-test

# 1) dry-run：看计划，不改盘
python .agents/skills/skill-registration-writer/scripts/apply_registration.py \
  --assign skill-registration-writer=完整Skill \
  --note "新增原生 Skill skill-registration-writer（完整 Skill 50→51）。"

# 2) 落盘
python .agents/skills/skill-registration-writer/scripts/apply_registration.py \
  --assign skill-registration-writer=完整Skill \
  --note "新增原生 Skill skill-registration-writer（完整 Skill 50→51）。" --write

# 3) 只修某个已登记技能缺失的镜像（不插行、不改计数）
python .agents/skills/skill-registration-writer/scripts/apply_registration.py \
  --assign docs-as-product-cmd=脚本命令门面 \
  --note "补齐 docs-as-product-cmd 的 SKILL.toml 镜像。" --write

# 4) 回滚上一轮
python .agents/skills/skill-registration-writer/scripts/apply_registration.py --revert
```

退出码：

| 码 | 含义 |
|---|---|
| 0 | 无待办（已对齐）或写入成功 |
| 1 | dry-run 检出待写动作 |
| 2 | 被阻塞（缺 `--note`、分类不存在、写前哈希不一致、写入后仍有待办） |
| 3 | 参数或环境错误 |

## 6. 验收：幂等与回滚

`--write` 成功后会立即用同一参数复跑计划，并断言剩余动作与阻塞均为 0；否则返回 2 并提示「幂等未达成」。人工验收按三证执行：

1. 写入前 dry-run 计划条数与写入后复跑「零待办」一致；
2. `git diff` 中每份登记面只有计数数字与新增行两种改动；
3. `--revert` 后三份登记面逐字节等于写入前，新建镜像被删除。

自检夹具覆盖 11 项断言：缺 `--assign` 不静默插入、四类动作齐备、dry-run 不改盘、写入结果、CHANGELOG 新→旧、复跑零动作、回滚逐字节还原、纯计数漂移可修正。

## 7. Gotchas（陷阱与反直觉行为）

1. `--assign` 不是可选装饰：漏登记技能不会被自动归入「看起来最像」的分类，缺参时只进「待指定分类」清单。
2. 镜像轨技能（frontmatter 有 `source`）按惯例不写 registry、不要求 SKILL.toml；把它们当原生登记会制造 `orphan_mirror`。
3. 不给 `--note` 却要插行，脚本会阻塞：否则登记成功但 CHANGELOG 缺条目，判定器立刻报 `changelog.native_missing`。
4. 同一 `--note` 重复执行不会重复取号；幂等判定比的是「条目结尾是否等于该说明」，不是整行相等。
5. 计数目标是「实际行数 + 本次插入数」，不是「声明值 + 1」；仓库若本来就有漂移，一次写入会顺带把它修正到扫描真值。
6. README 与 registry 的分类集合并不相同（镜像类只存在于 README），`--assign` 指向仅 README 有的分类时只会写 README 并提示。
7. CHANGELOG 取号取「现有最大版本号末段 +1」，不依赖文件首行；上游合并可能把编号打乱，取首行会撞号。
8. 写前哈希不一致必须中止而不是重试：说明计划与磁盘已不同源，重试只会把旧行号套到新内容上。
9. `.temp/` 下的 journal 是唯一回滚依据；手工删除后再想撤销，只能靠 git。
10. 脚本复制的是 SKILL.md 摘要与触发词，措辞仍需人复核；`脚本命令门面` 的第 3 列语义是「对应脚本」，摘要可能与列名不完全对齐。

## 8. 安全检查清单（逐项确认）

- [ ] 已运行 `--self-test` 且 11 项断言全 PASS
- [ ] 已先跑 dry-run，逐条核对要插入的技能名、分类与计数目标值
- [ ] 每个待写技能都有显式 `--assign <name>=<分类>`，未让脚本猜分类
- [ ] 已提供 `--note`，且条目正文写清「新增/补齐了什么、影响了哪个计数」
- [ ] 已确认写入范围只在四处登记面，未触碰 SKILL.md 正文与 frontmatter
- [ ] 写入后复跑显示「零待办（幂等）」
- [ ] 已核对 `git diff` 只有计数数字与新增行两类改动
- [ ] 已记录 journal 路径，必要时可用 `--revert` 整轮回滚

## 9. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-11-09 | 初始版本：复用判定器事实的写入器，支持 `--assign` / `--note` / `--only` / `--write` / `--revert`，含越界断言、写前哈希、备份与回滚、11 项自检夹具 |

## 参考

- 写入脚本：[scripts/apply_registration.py](scripts/apply_registration.py)
- 边界与回滚模型：[references/edit-boundary-model.md](references/edit-boundary-model.md)
- 只读判定器：`.agents/scripts/check-skill-registration.py`
- 关联技能：`skill-registry-count-drift-audit`（只读审计）、`native-skill-surface-registration`（人工登记模板）
