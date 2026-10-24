---
name: skill-quality-baseline-check
version: 1.0.0
description: 在更新、迁移或新建已有 Skill 前，用 SpecWeave 质量门做只读基线、拆解失分构成并预测写入后的分数，写入后再以满分阈值复验。当用户要求更新 Skill、核对格式与质量分、追问 85 或 95 分怎么构成、纠结该用 quick_validate 还是 check-skill-quality，或准备宣称已通过质量门时，必须使用此技能。只做基线与门禁取证，不负责内容返工与四处登记。
argument-hint: "<skill-dir> [质量门脚本路径]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
  - ".qoder/skills/**/SKILL.md"
title: "Skill 质量基线取证"
source: "来源会话 0f8d24ae-195c-407b-af91-6a8b26227212；user-skill-sovereign-migration 基线 85（3 warn）到 100 实测"
---

# Skill 质量基线取证

改 Skill 之前先量一次分。本技能把「跑哪个验证器、分怎么算、改完预期几分、写完怎么复验」固化成可逐字复跑的只读取证流程，避免写完才发现掉分再返工。

## 1. 这个技能解决什么

`check-skill-quality.py` 是这仓库里 Skill 评分的唯一真源，但 `skill-creator` 的更新流程只写到 Validate，它自带的 `quick_validate.py` 校验的是另一套契约。三处高代价误判：

| 误判 | 真实后果 |
|---|---|
| 拿 `quick_validate.py` 校验仓库原生 Skill | 它只允许 6 个字段，`version`、`argument-hint`、`paths` 等原生字段会被判为 unexpected key，得到假失败 |
| 不看基线直接改正文 | 改完才发现 85 分来自 2 个缺失字段加 1 个标题编号，与正文质量无关 |
| 把 85 分当成「内容差」 | 于是大改内容，实际只需补元数据与一个编号标题即可到 100 |

> **为什么？** 质量门是文档契约的机械评分，不是内容好坏的主观判断。先拿到失败项清单，才能把「修什么」与「改哪里」分开，避免为凑分破坏本来有效的规则。

> **为什么？** 用户级目录（`~/.qoder/skills`）与仓库主权区（`.agents/skills`）的元数据契约不同。用同一把尺子前，先确认这把尺子量的是什么契约，否则会把「契约差异」误报成「Skill 有缺陷」。

> **为什么？** 分数是可预测的算术结果，不是玄学。100 起算、error 减 15、warn 减 5、info 减 1，知道本轮会消掉哪些失败项，就能在写入前说出预期分数，并在写入后验证「预测是否兑现」。

## 2. 适用边界

适用：

- 准备更新、迁移或重命名一个已有 Skill，需要先确认当前质量分与失分项
- 用户追问「85 分 / 95 分是怎么来的」「为什么没过质量门」
- 需要在两个验证器之间做选择，避免用错契约
- 写入完成后需要以 `--threshold 100` 复验并报告实际退出码

不适用：

| 场景 | 改用什么 |
|---|---|
| 已确认掉分，需要改内容补齐 | `skill-quality-gate-remediation` |
| 写完后的整包验收（编码、脚本、evals） | `skill-package-verification-gates` |
| create / update / 补登记的磁盘分诊 | `skill-recommendation-disk-triage` |
| 从零设计 Skill 内容与触发词 | `skill-creator` |
| 修改检查器或评分公式来提分 | 禁止；检查器是评分真源 |

## 3. 验证器选择

```
这次要验证什么？
├─ 通用客户端能否加载（Open Standard 最小字段集）？ → skill-creator 的 quick_validate.py
├─ 仓库质量分与失分项？ → check-skill-quality.py（唯一评分真源）
├─ 正文链接与 frontmatter 路径是否可达？ → check-links.py --check-frontmatter-paths
└─ 整包是否可交付（BOM、缓存残留、脚本、evals）？ → skill-package-verification-gates
```

两个验证器的字段契约不同：

| 验证器 | 允许的 frontmatter 字段 |
|---|---|
| `quick_validate.py` | `name`、`description`、`license`、`allowed-tools`、`metadata`、`compatibility` |
| `check-skill-quality.py` | 必需 `name`、`description`；推荐 `version`、`argument-hint`、`user-invocable`、`paths`；其余自定义字段按 info 处理 |

仓库原生 Skill 通常带 `version`、`paths`、`title`、`source`，因此 `quick_validate.py` 不适用于它们。它的失败不代表 Skill 有错，只代表用了错误的尺子。

## 4. 基线流程（零写入）

### B1 解析目标与检查器

```bash
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
CHECKER="$REPO/.agents/scripts/check-skill-quality.py"
SKILL_DIR="<绝对或相对路径>"
test -f "$SKILL_DIR/SKILL.md" || echo "TARGET_INVALID"
test -f "$CHECKER" || echo "CHECKER_INVALID"
```

`--path` 接受仓库外的绝对路径，因此用户级 Skill 也能直接评分。

### B2 取失败项清单与分数

```bash
python "$CHECKER" --path "$SKILL_DIR" --verbose
python "$CHECKER" --path "$SKILL_DIR" --score --threshold 100
```

第一条列出每个检查的 PASS / WARN / FAIL 与原始提示；第二条只输出 `名称: 分数`、`平均: 分数`，并在低于阈值时以退出码 1 结束。两条都要跑：没有清单无法解释分数，没有分数无法判断阈值。

### B3 用评分公式对账

评分规则：100 起算，每个未通过的 error 减 15、warn 减 5、info 减 1，下限 0。只有「未通过」的检查扣分，通过的 warn 不扣。

把 B2 的失败项逐条换算后求和，必须等于 B2 报出的分数。常见构成：

| 分数 | 可能的构成 |
|---|---|
| 85 | 3 个 warn（100 − 5 × 3） |
| 95 | 1 个 warn（100 − 5） |
| 65 | 1 个 error 加 4 个 warn（100 − 15 − 5 × 4） |
| 40 | 多个 error 叠加，注意下限为 0 |

对不上时不要继续写，先重跑 `--verbose`：多半是漏读了某条 FAIL，或把已通过的检查也算成了扣分项。

### B4 写入前预测

在修改方案里列一张表，逐项写明「拟改动 → 对应检查名 → 预计消除的扣分」，并单列仍会保留的失败项。预测必须标注为「预期，未实测」，写入后再用 B6 兑现。

| 拟改动 | 检查名 | 预计变化 |
|---|---|---|
| 补 `user-invocable: true` | `frontmatter.user-invocable` | +5 |
| 补 `paths` | `frontmatter.paths` | +5 |
| Gotchas 标题改为带编号 | `open_standard.body.gotchas` | +5 |

### B5 链接门只读取证

```bash
python "$REPO/.agents/scripts/check-links.py" --path "$SKILL_DIR" --check-frontmatter-paths
```

该命令默认只校验 `source`、`x-toml-ref` 两个 frontmatter 字段（另自动扩展 `related_*`），**不校验 `paths`**。含义有两层：新增 `paths` 不会制造 frontmatter 路径假断链；反过来，`paths` 的值是否正确也不被这道门证明。没有对应 TOML 镜像时不要写 `x-toml-ref`，否则会引入真实断链。

### B6 写入后复验

用与 B2、B5 完全相同的命令复跑，并逐项比对：

- 实际分数是否等于 B4 的预测；不等时先定位差异对应的检查名
- `--score --threshold 100` 的退出码是否为 0
- `--verbose` 中是否仍有 WARN / FAIL
- 链接门是否 0 断链且退出码 0

差异定位优先读检查源码中的字段清单或正则，不要凭印象反复改正文。

## 5. 契约速查

| 项目 | 契约 | 源码位置 |
|---|---|---|
| 必需字段 | `name`、`description` | `lib/check_skill_quality/constants.py` |
| 推荐字段 | `version`、`argument-hint`、`user-invocable`、`paths` | 同上 |
| 评分 | 100 起算，error −15、warn −5、info −1 | `lib/check_skill_quality/scoring.py` |
| Gotchas 通过条件 | 二级标题以编号开头，例如 `## 6. Gotchas（陷阱与反直觉行为）` | `lib/check_skill_quality/checks_open_standard.py` |
| 正文长度 | 不超过 500 行 | `lib/check_skill_quality/constants.py` |
| 描述长度 | 低于 50 字为 error，150 字以上更稳，上限 1024 | `checks_description.py` 与 `constants.py` |
| 默认阈值 | 70；验收必须显式传 100 | `lib/check_skill_quality/cli.py` |
| 链接门默认字段 | `source`、`x-toml-ref`，外加 `related_*` | `.agents/scripts/check-links.py` |

## 6. Gotchas（陷阱与反直觉行为）

1. **`quick_validate.py` 会拒绝仓库原生字段**：它的允许字段只有 6 个，`version`、`paths` 等会报 unexpected key。这是契约不同，不是 Skill 损坏。
2. **`## Gotchas` 不带编号仍失分**：检查器要求标题以 `## 数字.` 开头，措辞可以是 Gotchas、陷阱或反直觉。
3. **`## Why` 标题不算 Why 解释**：只统计 `> **为什么` 引用块，且全文至少 2 处。
4. **`paths` 不在链接门默认字段内**：新增 `paths` 不会造成假断链，但也不能用它证明路径正确。
5. **`--score` 低于阈值时退出码为 1**：只看输出数字不看退出码，会把失败当成功；反之，退出码 1 也可能是阈值设错而非内容变差。
6. **默认阈值 70 不等于及格线**：验收统一用 100，避免「过了 70」掩盖 warn。
7. **用户级目录可直接评分**：`--path` 支持仓库外绝对路径，无需先迁移再测。
8. **没有 TOML 就不要写 `x-toml-ref`**：链接门会按该字段真实解析并报断链。
9. **通过的 warn 不扣分**：`file.length` 等检查即使 severity 是 warn，只要通过就不计入扣分，不要误减。

## 7. 安全检查清单（逐项确认）

- [ ] 已确认目标目录含 `SKILL.md`，检查器路径真实存在
- [ ] 已用 `quick_validate.py` 的字段契约排除误用场景
- [ ] 已保存 `--verbose` 的失败项清单与 `--score` 的分数、退出码
- [ ] 已用评分公式对账，换算结果与实际分数一致
- [ ] 已把预测写成「预期未实测」，未冒充结果
- [ ] 已确认链接门默认字段范围，未把 `paths` 当成受检字段
- [ ] 已用相同命令复跑，确认分数、退出码与断链数
- [ ] 未修改检查器、评分公式或其他 Skill

## 8. 参考

- 命令、字段与实测样例：[references/tool-contracts.md](references/tool-contracts.md)
- 内容返工：`skill-quality-gate-remediation`
- 整包交付验收：`skill-package-verification-gates`
- Skill 创作与格式：`skill-creator`

## 9. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：验证器选择、只读基线、评分对账、写入前预测与写入后复验 |
