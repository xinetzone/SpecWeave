---
name: repo-native-skill-frontmatter-contract
version: 1.0.0
description: 仓库原生 Skill（.agents/skills）的 frontmatter 键位契约：version、argument-hint、user-invocable、paths 必须写在顶层，缩进到 metadata 下会被质量门的行首锚点漏读并静默扣 20 分；quick_validate 对原生键集退出 1 属于尺子不同而非技能缺陷。必须使用此技能：当用户提到「frontmatter 怎么写」「质量门只有 80 分」「version 放哪」「quick_validate 报 Unexpected key」「新建 Skill 头字段」时。不用于用户级 ~/.qoder/skills 的键集（用 qoder-user-skill-authoring）、四处登记（用 native-skill-surface-registration）或内容返工（用 skill-quality-gate-remediation）。
argument-hint: "<skill-dir>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
  - ".agents/scripts/lib/check_skill_quality/**/*.py"
  - ".agents/skills/skill-creator/scripts/quick_validate.py"
title: "仓库原生 Skill Frontmatter 契约"
x-toml-ref: "../../../.meta/toml/.agents/skills/repo-native-skill-frontmatter-contract/SKILL.toml"
source: "来源会话 48f79e3f-4485-4274-86c5-bf77dd7ddb31（git-sandbox-rehearsal 创建时 80 分，补齐顶层字段后 100 分）；本技能创建会话完成 100 与 80 的对照实测"
---

# 仓库原生 Skill Frontmatter 契约

本技能只回答一个问题：在 `.agents/skills/<name>/SKILL.md` 里写头字段时，**哪些键、写在哪一层**，以及写完之后用哪几把尺子量、量出什么结果算正常。

它不负责正文怎么写，也不负责登记。技能写得好不好是另一件事；这里保证的是：头字段不会在你不知情的情况下扣 20 分。

## 1. 这个技能解决什么

仓库里同时存在两套 frontmatter 契约，它们互相排斥：

| 尺子 | 允许/推荐的键 | 典型使用者 |
|---|---|---|
| SpecWeave 质量门 `check-skill-quality.py` | 必需 name、description；推荐**顶层** version、argument-hint、user-invocable、paths | `.agents/skills/` 原生 Skill |
| 通用 `quick_validate.py`（skill-creator 自带） | 仅 name、description、license、allowed-tools、metadata、compatibility | Open Standard 最小集、用户级 `~/.qoder/skills` |

危害不在「选错尺子」本身，而在**嵌套写法不报错**：

质量门用行首锚点 `^version:` 在 frontmatter 原文里找字段（见 `.agents/scripts/lib/frontmatter.py` 的 `extract_yaml_field`）。写成

```yaml
metadata:
  version: "1.0.0"
```

时，`version` 前面有缩进，正则匹配不到，检查器只记一条「建议字段缺失」的 warn，**不报错、不提示位置**。四个推荐字段都这样写，就是 100 − 5 × 4 = **80 分**，而且从输出里看不出「你其实写了，只是写错了层」。

> **为什么不能靠 `quick_validate` 兜底？** 它只认 6 个顶层键，且显式跳过 `metadata` 下的嵌套键。原生键集在它眼里全是 unexpected key，因此它对「键位放错」给不出任何判别信号，只会一律退出 1。

> **为什么不在两个根之间复制同一份内容？** 用户级根要满足的是另一把尺子（见 `qoder-user-skill-authoring`），其 frontmatter 恰恰把 `version` 放进 `metadata`。同一份文件无法同时拿两边满分，先按**所在根**选尺子，再定键位。

## 2. 适用边界

适用：

- 在 `.agents/skills/` 新建 Skill，需要一次写对头字段
- 原生 Skill 质量门只有 80 / 95 分，且失分项全是 `frontmatter.*`
- 需要向用户解释 `quick_validate` 为什么退出 1
- 迁移或治理后需要复核头字段层级

不适用：

| 场景 | 交给他 |
|---|---|
| 用户级 `~/.qoder/skills` 的键集 | `qoder-user-skill-authoring` |
| 只想知道分数怎么构成、两个验证器怎么选 | `skill-quality-baseline-check` |
| 已有 Skill 内容 65 分档返工 | `skill-quality-gate-remediation` |
| 登记后补 `source` / `x-toml-ref` | `registered-skill-frontmatter-completion` |
| 四处登记与用户级联接交付 | `native-skill-surface-registration` |

## 3. 标准键位（直接抄）

```yaml
---
name: <与目录名完全一致>
version: 1.0.0
description: <一句话功能 + 何时必须使用 + 不适用场景>
argument-hint: "<skill-dir>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/<name>/**"
title: "<人类可读标题>"
source: "<来源会话或知识源；没有就别写>"
---
```

字段归属速查：

| 键 | 层级 | 质量门影响 | quick_validate |
|---|---|---|---|
| name / description | 顶层、必需 | 缺失为 error（每个 −15） | 必需且合法 |
| version / argument-hint / user-invocable / paths | 顶层、推荐 | 缺失或嵌套 → 每个 −5 | 一律 unexpected |
| title / source / x-toml-ref / disable-model-invocation | 顶层、自定义 | 记 info，不扣分 | 一律 unexpected |
| metadata.* | 嵌套 | 质量门不读 | 允许，但不替代顶层推荐字段 |

> **为什么 `paths` 一定要写？** 它是推荐字段之一，缺了就是 −5；同时它不参与链接门的 frontmatter 路径校验（链接门默认只看 `source`、`x-toml-ref`、`related_*`），所以写错 `paths` 不会制造假断链，也就不会被另一道门替你发现。

## 4. 验收序列

对目标目录 `<SKILL_DIR>` 依次执行，**每一步都记录退出码**。

### 步骤1：仓库质量门打分

```bash
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
python "$REPO/.agents/scripts/check-skill-quality.py" --path "<SKILL_DIR>" --score --threshold 100
echo "exit=$?"
```

期望：`<name>: 100`，退出码 0。只看分数不够，再加 `--verbose` 看是否有未通过的 warn。

> **为什么阈值必须显式写 100？** 脚本默认阈值是 70，只跑默认值会把 80 分判为通过，正好放过本技能要防的那 20 分。

### 步骤2：链接门

```bash
python "$REPO/.agents/scripts/check-links.py" --path "<SKILL_DIR>" --check-frontmatter-paths
echo "exit=$?"
```

期望：0 断链，退出码 0。没有对应 TOML 镜像时不要写 `x-toml-ref`，否则这一步会真实报断链。

### 步骤3：通用门（预期失败）

```bash
python "$REPO/.agents/skills/skill-creator/scripts/quick_validate.py" "<SKILL_DIR>"
echo "exit=$?"
```

原生 Skill 的期望结果是**退出 1**，输出形如：

```text
Unexpected key(s) in SKILL.md frontmatter: argument-hint, paths, title, user-invocable, version.
```

这不是待修缺陷。**不要**为了让它退出 0 而删除 `version`、`paths` 等字段，也**不要**把 `version` 挪进 `metadata`——前者让质量门掉分，后者让质量门静默掉 20 分，两者都是拿错尺子改对了另一把。

### 步骤4：用兄弟技能做对照取证

单看一个技能退出 1，无法区分「契约差异」与「这个技能真的写坏了」。取同一根下一个**已通过质量门**的原生 Skill 跑同一条命令：

```bash
python "$REPO/.agents/skills/skill-creator/scripts/quick_validate.py" "$REPO/.agents/skills/atomic-commit-mixed-file-split"
echo "exit=$?"
```

若质量门 100 的技能同样退出 1、同样报 unexpected key，则证明这是尺子问题。对照结果写进交付报告，不要只在心里判断。

> **为什么用「已满分」的兄弟而不是随便找一个？** 只有满分样本才能同时证明「质量门认可」与「通用门拒绝」，两者并存才构成契约差异的证据；拿一个本来就掉分的样本对照，无法排除「两边都不认」的解释。

### 步骤5：回读与编码

```bash
python -c "import yaml,pathlib; p=pathlib.Path(r'<SKILL_DIR>/SKILL.md'); t=p.read_text(encoding='utf-8'); fm=t.split('---')[1]; print(sorted(yaml.safe_load(fm).keys()))"
```

期望：打印出的键全部位于顶层；文件无 BOM；无 `__pycache__` 残留。

> **为什么回读而不是相信写入工具？** 写入成功只说明字节落了盘，不说明 YAML 层级正确。上面这条命令打印的是解析后的**顶层键集合**，嵌套的 `metadata.version` 不会出现在里面，一眼就能看出层级错误。

## 5. 结果口径

交付报告分三行写，不要合并成「全部验证通过」：

| 门 | 结论 |
|---|---|
| 仓库质量门 | 100/100，退出码 0 |
| 链接门 | 0 断链，退出码 0 |
| 通用 `quick_validate` | 按契约不适用：退出 1，报 unexpected key；同根满分技能 `atomic-commit-mixed-file-split` 同样退出 1 |

> **为什么必须把「不适用」写出来？** 省略它会让人以为通用门也过了；写成「修复了退出 1」则是造假。准确表述是「该门校验的是 Open Standard 最小键集，仓库原生键集不在其契约内」。

## 6. 失败矩阵

| 现象 | 根因 | 处置 |
|---|---|---|
| 80/100，4 条 `frontmatter.*` warn | 四个推荐字段缺失，或全部缩进在 `metadata` 下 | 全部提到顶层 |
| 95/100 | 单个推荐字段缺失 | 补齐该字段 |
| 65/100 以下 | 另有 error（如 description 过短、缺 Why） | 转 `skill-quality-gate-remediation` |
| `quick_validate` 退出 1 | 使用了原生键集 | 预期行为，按第 5 节口径记录 |
| 链接门报 `source` 断链 | `source` 里的路径片段被当成真实路径 | 把路径说明移到正文，`source` 只留来源标识 |

## 7. Gotchas（陷阱与反直觉行为）

1. **`metadata.version` 不报错**：它是合法 YAML、`quick_validate` 也接受，只有仓库质量门的行首锚点读不到，代价是静默 −5。
2. **四个字段全嵌套正好 −20**：80 分看起来像「内容一般」，实际只是键位问题。
3. **`title` / `source` 不扣分也不被通用门接受**：自定义字段记 info；别把「info 不扣分」误读成「通用门兼容」。
4. **不要为了让 `quick_validate` 绿而删字段**：删掉 `paths` 会让质量门 −5，且 `paths` 是仓库导航契约的一部分。
5. **不要把 `version` 挪进 `metadata`**：那是用户级根的写法，搬到原生区就是本技能要防的 80 分。
6. **默认阈值 70 会放过 80 分**：验收命令必须显式 `--threshold 100`。
7. **`--score` 不显示失分项**：定位靠 `--verbose`，两个都要跑。
8. **`paths` 不受链接门保护**：`--check-frontmatter-paths` 默认不校验 `paths`，写错不会报。
9. **`source` 里的路径写法会被链接门当成真实路径**：`source` 中只要出现含 `.md` 且带 `/` 的片段（例如把说明写成「见 references/xxx.md」），链接门就把整段当路径解析并报断链；把路径说明移到正文，`source` 只保留来源标识。
10. **别写指向 Skill 目录之外的相对链接**：`../../../scripts/...` 在主权区可解析，经目录联接暴露到用户级根后层级变化，同一份文件会报断链；仓库内路径写成行内代码即可，不做成链接。
11. **对照样本必须是同根满分技能**：跨根对照会把两把尺子的差异误当成单边缺陷。

## 8. 安全检查清单（逐项确认）

- [ ] 已确认目标目录含 `SKILL.md`，且 `name` 与目录名一致
- [ ] 已确认 `version`、`argument-hint`、`user-invocable`、`paths` 均在顶层，未缩进到 `metadata`
- [ ] 已用 `--score --threshold 100` 取得 100 分与退出码 0
- [ ] 已用 `--verbose` 确认没有残留的未通过项
- [ ] 已跑链接门并确认 0 断链、退出码 0
- [ ] 已跑 `quick_validate` 并把退出 1 记为契约差异，而非修复目标
- [ ] 已用同根满分兄弟技能做对照，证据已写入报告
- [ ] 已回读顶层键集合与编码，未残留 `__pycache__`
- [ ] 未修改检查器、评分公式或其他 Skill
- [ ] 未把用户级键集与原生键集混写在同一份文件里

## 9. 参考

- 命令、原始输出与退出码：[references/verified-case.md](references/verified-case.md)
- 评测场景：[evals/evals.json](evals/evals.json)
- 评分与验证器选择：`skill-quality-baseline-check`
- 用户级键集：`qoder-user-skill-authoring`

## 10. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：两把尺子对照、顶层键位模板、五步验收、结果口径与失败矩阵 |
