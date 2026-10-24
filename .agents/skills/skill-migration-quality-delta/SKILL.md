---
name: skill-migration-quality-delta
version: 1.0.0
description: 判断 Skill 迁入后的分差是迁入漂移还是源侧既有缺口，对源根与目标根各跑一次 check-skill-quality.py --verbose，按检查名求差集并映射到 frontmatter 或正文改动，最后按本次引入 0 项、已消除 N 项、既有 M 项三段陈述。当用户提到迁入后掉分、65 变 70、警告是不是迁入引入、要不要回滚、质量门为什么不到 100 时，必须使用此技能。不用于单根基线预测、内容返工或四处登记。
argument-hint: "<源 Skill 目录> <目标 Skill 目录> [--checker <check-skill-quality.py>]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".qoder/skills/**/SKILL.md"
  - ".agents/skills/**/SKILL.md"
title: "Skill 迁移质量差值归因"
x-toml-ref: "../../../.meta/toml/.agents/skills/skill-migration-quality-delta/SKILL.toml"
metadata:
  source: "会话 511919f2-09d9-46aa-b6bb-a423d6f9e91d 的 ci-gate-effectiveness-audit 主权区迁移实测：源 65（7 warn）到目标 70（6 warn）"
---

# Skill 迁移质量差值归因

迁入前后分数变了，不等于内容变差。本技能把「两次 `--verbose` → 按检查名求差集 → 映射到 frontmatter 或正文 → 三段式陈述」固化成可逐字复跑的只读取证流程，回答一个具体问题：这次分差里，哪一项是迁入引入的，哪一项源侧本来就有。

## 1. 适用与不适用

适用需三条同时成立：

1. 同一个 Skill 在两个根各有一份（典型是 `~/.qoder/skills` 与 `.agents/skills`）
2. 迁入已经发生或已经尝试，需要判断分差归因
3. 需要向用户或交接方解释「质量门为什么没过」

| 场景 | 使用本技能 | 改用什么 |
|---|---|---|
| 迁入后分数从 65 变 70，要判断是变好还是变坏 | 是 | — |
| 迁移报告里只写了总分，需要拆成「引入 / 消除 / 既有」 | 是 | — |
| 怀疑目标正文被改过，但分数看起来没掉 | 是 | — |
| 只跑一个根的基线、预测写入后的分数 | 否 | `skill-quality-baseline-check` |
| 已确认既有缺口，需要改内容补到 100 | 否 | `skill-quality-gate-remediation` |
| 执行迁入、复制与哈希 | 否 | `user-skill-sovereign-migration` |
| 四处登记、Junction 收尾 | 否 | `native-skill-surface-registration` |

## 2. 为什么必须比集合，不能比总分

> **为什么**要按检查名求差集，而不是比较 65 与 70？
> 总分只有一个数，同样的 +5 既可能是「消除 1 条、引入 0 条」，也可能是「消除 3 条、引入 2 条」，两者处置完全相反：前者可以交接，后者必须回滚。检查名集合把「变好」和「变坏」拆开，总分做不到。两个副本分数相同也可能已经有 1 条引入加 1 条消除互相抵消。

> **为什么**差项落在正文就说明不是保真复制？
> 迁入的批准范围通常只允许改 frontmatter 与新增 `paths`。`why.*`、`safety.*`、`open_standard.body.*`、`file.length` 这些检查读的是正文；它们出现差异，说明目标正文与源正文已经不同。此时继续谈「分数归因」，等于为一次未申报的正文改动找理由。先做正文保真比对，再谈归因。

> **为什么**分母不变才可比？
> 质量门是「100 起算、按未通过项扣分」。只要两次跑的是同一个检查器版本、同一个 Skill 名，扣分项就可以逐项相减。若两次之间检查器被改过，或者一次递归扫到了多份 `SKILL.md`，分母就已经不同，任何差值都没有意义——所以 §3 的 S1 必须先固定检查器与扫描范围。

## 3. 归因决策树

```text
迁入后分数变了，怎么归因？
├─ 两个根任一侧没有 SKILL.md？ → 停止，先修路径；本技能不适用
├─ 源目录是联接且指向目标目录？ → 两个根是同一实体，没有差值可比
├─ 两次扫描得到的分数行数 ≠ 1？ → 停止，传入单个 Skill 目录，不要传技能根
├─ 理论分（100−5×WARN−15×FAIL）与实际分不符？ → 停止，按 Gotchas 第 3 条重解析
└─ 两次清单都可对账？
   ├─ 差项只含 frontmatter.* / description.* / open_standard.structure.* → 元数据增量，按 §4 映射
   └─ 差项含 why.* / safety.* / open_standard.body.* / file.length → 正文已分叉，先做保真比对
```

## 4. 取证流程（只读四步）

### S1 固定检查器与两个根

```bash
CHECKER="<仓库根>/.agents/scripts/check-skill-quality.py"
SRC="<源 Skill 目录>"
DST="<目标 Skill 目录>"
test -f "$CHECKER" && test -f "$SRC/SKILL.md" && test -f "$DST/SKILL.md" || echo "INPUT_INVALID"
```

`--path` 接受仓库外的绝对路径，用户级目录可以直接评分；传目录会递归扫描，所以两个参数都必须是**单个 Skill 目录**。

### S2 两个根各跑一次

```bash
PYTHONDONTWRITEBYTECODE=1 python "$CHECKER" --path "$SRC" --verbose
PYTHONDONTWRITEBYTECODE=1 python "$CHECKER" --path "$SRC" --score --threshold 100; echo "SRC_SCORE_EXIT=$?"
PYTHONDONTWRITEBYTECODE=1 python "$CHECKER" --path "$DST" --verbose
PYTHONDONTWRITEBYTECODE=1 python "$CHECKER" --path "$DST" --score --threshold 100; echo "DST_SCORE_EXIT=$?"
```

保存四份原始输出：两次失败清单用于求差集，两个分数与退出码用于对账。

### S3 按检查名求差集

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/diff_quality_warnings.py --source "$SRC" --target "$DST"
```

脚本只读，内部按 `--verbose` 行里的 `[WARN] <name>: <message>` 取**检查名**，自动排除末尾那条没有检查名的「平均评分低于阈值」摘要行，再输出引入、消除、既有三段与对账结果。手工核对时也照这个粒度，不要按 `[WARN]` 出现次数计数。

### S4 对账与归因

理论分 = 100 − 5 × WARN 数 − 15 × FAIL 数（下限 0）。两次都必须与实际分相等；相等才能证明清单没有漏项，随后把每个差项映射到 §5 的字段或章节。

## 5. 差项到改动面的映射

| 检查名 | 归属 | 分差 | 关键契约 |
|---|---|---|---|
| `frontmatter.version` / `argument-hint` / `user-invocable` / `paths` | frontmatter 增量 | ±5 | 推荐字段，只判是否存在 |
| `description.mandatory_phrase` / `description.trigger_context` | description 改写 | ±5 | 读 description 文本，不看正文 |
| `description.length` | description 改写 | ±5 或 ±15 | 低于 50 字符是 error |
| `open_standard.structure.*` / `open_standard.custom_fields` | 目录与字段结构 | ±5 | 增删 `references/`、`assets/` 或自定义字段 |
| `why.explanations` / `why.vs_must_ratio` | 正文 | ±5 | 只统计 `> **为什么` 引用块 |
| `safety.dry_run` / `safety.idempotent` / `safety.checklist` | 正文 | ±15 或 ±5 | 清单标题、勾选项数、幂等词 |
| `open_standard.body.gotchas` | 正文 | ±5 | 标题须以 `## 数字.` 开头 |
| `file.length` / `decision.*` / `trigger.*` | 正文 | ±15 或 ±5 | 行数、决策树、触发分级 |

`paths` 的值在两个根天然不同（`.qoder/skills/...` 与 `.agents/skills/...`），但检查只判字段有无，因此「新增 paths 消掉 1 条」与具体取值无关。

## 6. 三段式结论（唯一允许的汇报格式）

```text
本次引入 N 项：<检查名 + 归属，或「无」>
已消除 N 项：<检查名 + 归属>
既有缺口 N 项：<检查名>
质量门现状：<分数>/100。本次迁入<是否>引入新警告；未达 100 的原因是既有缺口，不是迁入。
```

只报总分、只报差值、或把「70 分」直接说成「迁入导致掉 30 分」，都属于错误陈述。既有缺口与本次引入必须分开写，因为它们对应完全不同的动作。

## 7. 归因结论到下一步

| 归因 | 动作 |
|---|---|
| 引入 0 项，差项只有 frontmatter 增量 | 可交接；既有缺口转 `skill-quality-gate-remediation` |
| 引入项全是 `frontmatter.*` | 回滚该字段或补齐，复跑确认引入归零 |
| 引入项含正文检查 | 停止归因，先做正文保真比对（去 frontmatter 后逐字比对）；未获授权的改动直接回滚 |
| 已消除项含正文检查 | 目标正文已分叉（通常是事后修复），报告写明「两副本已分叉」，禁止再称逐字复制 |
| 两侧清单完全一致 | 分数相同且无结构性差异，可如实写「迁入未改变质量画像」 |

## 8. Gotchas（陷阱与反直觉行为）

1. **每行有两个 `[WARN]`**：CLI 前缀一个、消息里一个，`grep -c "[WARN]"` 会双倍计数。按 `[WARN] <name>:` 取检查名。
2. **末尾摘要行不是检查项**：`平均评分65低于阈值70` 没有检查名，按名称解析会自动排除；按标签计数会多出一条。
3. **`--verbose` 的退出码不反映分数**：它只在存在 error 级失败时返回 1；65 分也可能退出 0。分数与阈值看 `--score --threshold`。
4. **`--path` 传目录会递归**：传技能根会得到多行 `名称: 分数`，求差集前必须确认只有一份 `SKILL.md`。
5. **`paths` 只校验存在性**：取值写错不会掉分，也不会被链接门检查；不要用「paths 通过」证明路径写对了。
6. **两个根的 `paths` 取值不同但都通过**：这是设计如此，不是漏改。
7. **Python 会在检查器旁写 `__pycache__`**：统一 `PYTHONDONTWRITEBYTECODE=1`，否则取证会污染仓库工作树。
8. **源目录可能是联接**：读到的是联接目标，此时两个根可能是同一份内容；先用 `Get-Item | Select LinkType, Target` 确认。
9. **分数相同不等于没有差异**：1 条引入加 1 条消除会互相抵消，必须比集合。
10. **既有缺口不是本次债务**：把源侧本来就有的 6 条写成「迁入引入」，会让正确的迁移被回滚。

## 9. 幂等与重入

| 探针 | 状态 | 重入动作 |
|---|---|---|
| 目标目录 | 不存在 | 停止，先修路径 |
| 两次清单 | 已保存且检查器版本未变 | 直接复用，不重复跑 |
| 两次清单 | 检查器已更新 | 丢弃旧结论，按 S2 全量重跑 |
| 结论 | 引入 0 项 | 内容未变则不重跑；怀疑被改才复跑 |
| 结论 | 引入非 0 | 修复后重跑两侧，确认引入归零而不是只消除被报的那条 |

## 10. 安全检查清单（逐项确认）

- [ ] 已确认两个根都存在且各含一份 `SKILL.md`
- [ ] 已确认两次扫描各只输出一行分数，未递归扫到多份
- [ ] 已保存两次 `--verbose` 失败清单与两次 `--score` 的分数、退出码
- [ ] 已按检查名求差集，未用总分或 `[WARN]` 计数代替
- [ ] 已用 100−5×WARN−15×FAIL 对账，两次都与实际分相等
- [ ] 已确认每个差项的归属；含正文项时已先做保真比对
- [ ] 已按「本次引入 / 已消除 / 既有缺口」三段陈述
- [ ] 已确认无 `__pycache__` 残留，未修改任何 Skill 内容

## 11. 参考

- 已验证案例（ci-gate-effectiveness-audit 迁移实测）：[references/verified-case-ci-gate.md](references/verified-case-ci-gate.md)
- 取证脚本：[scripts/diff_quality_warnings.py](scripts/diff_quality_warnings.py)
- 上下游：`skill-quality-baseline-check`、`skill-quality-gate-remediation`、`user-skill-sovereign-migration`

## 12. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：基于会话 `511919f2` 的 ci-gate-effectiveness-audit 主权区迁移实测，固化跨根差集归因、字段映射、三段式陈述与对账规则 |
