# 已验证案例：ci-gate-effectiveness-audit 主权区迁移

来源会话：`511919f2-09d9-46aa-b6bb-a423d6f9e91d`。本案例是「源 65 → 目标 70」的原始实测，用来验证本技能的差集流程与字段映射。

## 1. 场景

| 项目 | 内容 |
|---|---|
| Skill | `ci-gate-effectiveness-audit` |
| 源 | `C:\Users\xinzo\.qoder\skills\ci-gate-effectiveness-audit`（实体目录） |
| 目标 | `D:\spaces\SpecWeave\.agents\skills\ci-gate-effectiveness-audit` |
| 正文 | 逐字复制，未改 |
| frontmatter | 新增 `paths` 与 `title` 两项 |

## 2. 两次实测

```bash
python .agents/scripts/check-skill-quality.py --path <DST> --verbose
python .agents/scripts/check-skill-quality.py --path <DST> --score --threshold 100
```

| | 警告数 | 分数 | `--score` 退出码 |
|---|---|---|---|
| 源（用户级） | 7 | 65 | 1 |
| 目标（主权区） | 6 | 70 | 1 |

目标侧残余 6 项：

```text
description.mandatory_phrase
description.trigger_context
why.explanations
safety.idempotent
safety.checklist
open_standard.body.gotchas
```

源侧清单等于上述 6 项再加 `frontmatter.paths`。

## 3. 差集结果

| 集合 | 内容 |
|---|---|
| 本次引入 | 无 |
| 已消除 | `frontmatter.paths`（新增字段，−5 → +5 分） |
| 既有缺口 | 上述 6 项 |

结论：`+5` 恰好等于新增 `paths` 消掉的那一条，迁入没有引入新警告；70 分不是迁入造成的，而是源侧本就有 6 个内容缺口。

## 4. 当时若按总分汇报，会错在哪

| 错误陈述 | 真实后果 |
|---|---|
| 「迁入后只有 70 分，说明迁入有问题」 | 把源侧既有缺口当成迁入回归，可能触发不必要的回滚 |
| 「从 65 涨到 70，迁入提升了质量」 | 提升只来自一个元数据字段，正文质量分毫未动 |
| 「残余 6 项是迁移引入的」 | 6 项全部在源侧同时存在，归因方向完全相反 |

## 5. 后续分叉（同一 Skill 的下一轮）

同一会话的修复轮把主权区副本从 70 修到 100，用户级源副本保留在 65，两个副本从此**正文分叉**。此时再跑本技能应得到：

| 集合 | 内容 |
|---|---|
| 本次引入 | 无 |
| 已消除 | 7 项，其中 4 项为正文检查（`why.explanations`、`safety.idempotent`、`safety.checklist`、`open_standard.body.gotchas`） |
| 判定 | `DIVERGED_REMEDIATED` |

含义：分数是变好的，但两份正文已经不同。任何「逐字复制」「内容一致」的表述都不再成立；后续建联接时必须用联接替换用户级实体副本，而不是再复制一次。

## 6. 复跑提示

- 两个路径都必须指向**单个 Skill 目录**，不要传技能根。
- 统一 `PYTHONDONTWRITEBYTECODE=1`，避免在检查器旁留下 `__pycache__`。
- `--verbose` 的退出码不反映分数；分数以 `--score` 那行与退出码为准。
