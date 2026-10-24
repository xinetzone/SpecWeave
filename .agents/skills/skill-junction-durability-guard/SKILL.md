---
name: skill-junction-durability-guard
version: 1.0.0
description: 交付或审计用户级 Skill 目录联接时，先判定权威副本与登记面的 git 跟踪状态，把联接创建与内容提交拆成两项授权，标注 git clean 会删掉未跟踪技能并让联接悬空的风险，并在提交后复验哈希与联接目标。当用户提到「联接指向的技能突然没了」「目录联接悬空」「用户级技能能触发但没入库」「建了联接还要不要提交」「git clean 会不会删技能」时必须使用。不用于创建联接本体（用 user-level-skill-junction-delivery）、四处登记（用 native-skill-surface-registration）或用户级技能迁入主权区（用 user-skill-sovereign-migration）。
argument-hint: "<skill-name> [--repo <仓库根>] [--target <用户级路径>] [--audit]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
source: "会话 f42493e0 的 version-floor-contract-guard 联接交付预案与同轮磁盘取证"
title: "Skill 目录联接持久性守卫"
x-toml-ref: "../../../.meta/toml/.agents/skills/skill-junction-durability-guard/SKILL.toml"
---

# Skill 目录联接持久性守卫

目录联接让技能**立刻可触发**，但它不保证技能**还在**。本技能把「联接是否可用」与「权威副本是否已入库」拆成两个独立判定，并在两者不一致时阻止把交付说成完成。

## 1. 适用与不适用

适用：用户级 `~/.qoder/skills/<name>` 已经或即将指向主权区 `.agents/skills/<name>`，而你需要回答「这条联接在 `git clean`、切换分支、换机器之后还成立吗」。

| 场景 | 使用本技能 | 改用什么 |
|---|---|---|
| 已建好联接，要确认权威副本已提交 | 是 | — |
| 权威副本未跟踪，要判断联接风险并拆分授权 | 是 | — |
| 怀疑联接悬空或技能「突然消失」 | 是 | — |
| 在用户级新建联接、复跑六项验收 | 否 | `user-level-skill-junction-delivery` |
| 需要同步 README/registry/CHANGELOG/TOML 四处面 | 否 | `native-skill-surface-registration` |
| 用户级实体目录迁入主权区 | 否 | `user-skill-sovereign-migration` |
| 判断推荐指令该 create 还是 register | 否 | `skill-recommendation-disk-triage` |
| 质量门掉分需要补齐 | 否 | `skill-quality-gate-remediation` |

> **为什么**要单独设这个技能？`user-level-skill-junction-delivery` 用「`git status` 哈希前后一致」证明交付过程只读，这恰恰**假设**权威副本已经稳定；当副本本身还是未跟踪文件时，同一个哈希既能证明「过程干净」，也掩盖了「内容随时会被清理」。判定对象不同，不能共用一条验收结论。

## 2. 核心命题：可见性不等于可恢复性

| 事实 | 联接的表现 | 清理/恢复后的表现 |
|---|---|---|
| 权威副本已跟踪且已提交（D0） | 可触发 | 可重建，`git clean` 不影响 |
| 权威副本已跟踪但工作树有改动（D1） | 可触发 | 内容可能是未提交版本，提交前不可复现 |
| 权威副本未跟踪（D2） | 可触发 | `git clean -fd` 删除副本，联接变悬空 |
| 权威副本未跟踪且被忽略（D2i） | 可触发 | `git clean -fd` 保留，`-fdx` 删除，同样悬空 |
| 联接目标不存在（D3） | 不可触发或读到旧缓存 | 需重建目标后重做联接 |

> **为什么** D2i 要单列？很多人记得「`git clean -fd` 不删 ignored」，于是认为被忽略的技能是安全的；但 `-fdx`、换机器 clone、CI 干净检出都会让它消失，而联接在本地看起来完全正常。**联接的健康状态无法反推副本的持久状态**。

## 3. 只读取证（写盘前五步）

固定变量，后续命令都用它们：

```bash
REPO="${SPECWEAVE_ROOT:-D:/spaces/SpecWeave}"
NAME="<skill-name>"
SRC="$REPO/.agents/skills/$NAME"
MIRROR="$REPO/.meta/toml/.agents/skills/$NAME/SKILL.toml"
TARGET="$HOME/.qoder/skills/$NAME"
```

**步骤1：确认两个根各自的状态。**

```bash
git -C "$REPO" ls-files --error-unmatch "$SRC/SKILL.md" >/dev/null 2>&1; echo "TRACKED_SKILL_EXIT=$?"
git -C "$REPO" ls-files --error-unmatch "$MIRROR" >/dev/null 2>&1; echo "TRACKED_MIRROR_EXIT=$?"
git -C "$REPO" status --porcelain=v1 -- ".agents/skills/$NAME" ".meta/toml/.agents/skills/$NAME"
```

- `TRACKED_SKILL_EXIT=0` 且状态行为空 → D0。
- `TRACKED_SKILL_EXIT=0` 且状态行非空 → D1（看 ` M` / `A ` / `M ` 前缀）。
- `TRACKED_SKILL_EXIT` 非 0 且状态行以 `??` 开头 → D2。
- 两条都不命中 → 目录可能不存在，先确认路径拼写。

**步骤2：判定是否被忽略。**

```bash
git -C "$REPO" check-ignore -v "$SRC" "$MIRROR"; echo "CHECK_IGNORE_EXIT=$?"
git -C "$REPO" ls-files -o --exclude-standard -- ".agents/skills/$NAME" ".meta/toml/.agents/skills/$NAME"
```

`check-ignore` 退出 0 表示命中忽略规则（D2i）。`ls-files -o --exclude-standard` 列出未跟踪且未被忽略的文件；D2 时非空，D2i 时为空格。

**步骤3：确认联接本身。**

```powershell
Get-Item "$env:USERPROFILE\.qoder\skills\<name>" | Select-Object LinkType, Target
```

```bash
find -L "$HOME/.qoder/skills/$NAME" -type f | sort; echo "FIND_EXIT=$?"
```

期望 `LinkType: Junction`，`Target` 精确指向 `$SRC`；`find -L` 必须非空。目标目录不存在或 `find -L` 报 `No such file or directory` → D3。**不加 `-L` 返回 0 个文件不代表空包**，只代表没跟随联接。

**步骤4：确认登记面在 HEAD 中的状态。**

```bash
git -C "$REPO" grep -n "$NAME" HEAD -- .agents/skills/README.md .agents/capability-registry/02-skills.md .agents/skills/CHANGELOG.md; echo "GREP_HEAD_EXIT=$?"
git -C "$REPO" diff --stat HEAD -- .agents/skills/README.md .agents/capability-registry/02-skills.md .agents/skills/CHANGELOG.md
```

`git grep HEAD` 零命中说明「**已提交的**登记面还没有它」。工作树里能看到行但 HEAD 看不到，属于登记未落盘，不是登记缺失。

**步骤5：读回 `HEAD` 中的副本，确认提交内容与磁盘一致。**

```bash
git -C "$REPO" rev-parse --verify "HEAD:.agents/skills/$NAME/SKILL.md"; echo "HEAD_BLOB_EXIT=$?"
git -C "$REPO" hash-object "$SRC/SKILL.md"; echo "WORKTREE_BLOB"
```

D0 时两个哈希必须相等；D1 时通常不等，差值就是尚未提交的改动。

> **为什么**要同时查 `git status` 与 `git grep HEAD`？前者回答「有没有未落盘改动」，后者回答「落盘的版本里有没有这一行」。共享工作树里两者经常不一致——别人改了文件，你的目录仍是未跟踪，只查一个会把两种缺口混成一种。

## 4. 授权拆分

| 授权 | 动作 | 默认 | 越权的后果 |
|---|---|---|---|
| A | 创建/修复用户级目录联接 | 本技能可执行（用户已要求交付时） | 悬空联接、`~` 下噪声 |
| B | 把权威副本与镜像 `git add` + `commit` | **需单独确认** | 把他人在途改动一并提交 |
| C | `git push` | **需单独确认** | 污染共享分支 |
| D | 四处登记（README/registry/CHANGELOG/TOML） | **需单独确认** | 计数漂移、与在途登记互相覆盖 |

规则：A 完成不等于交付完成。没有 B 时，正确表述是「已联接、未持久化」，不是「已安装」。

> **为什么**把 A 和 B 拆开？联接创建是本地可见性变更，提交是共享历史变更，两者的回滚成本差一个数量级。用户在「给我装上」和「提交这些改动」之间通常只授权了前者；把它们打包会让一次口头同意变成对仓库历史的授权。

## 5. 提案与确认门（写盘前）

输出下表并停下，等用户明确回答：

| 项目 | 内容 |
|---|---|
| 持久性判定 | D0/D1/D2/D2i/D3，附判定命令与原始输出 |
| 联接现状 | 类型、Target、`find -L` 文件数 |
| 登记现状 | HEAD 命中数、工作树改动文件 |
| 拟执行授权 | A / B / C / D 中实际被批准的子集 |
| 唯一写入 | 逐个列出将被创建或修改的路径 |
| 明确不做 | 未批准的那几项，逐项点名 |
| 验收方式 | 第 6 节或第 7 节的具体命令 |

用户只批准部分面时，只做被批准的部分，并在报告里写缺口。**预览门是硬门**：未拿到确认前不写联接、不暂存、不提交。

> **为什么**要把「唯一写入」与「明确不做」分开列？联接是写操作，提交也是写操作，但它们的可见范围完全不同。混成一句「我来处理一下」，事后无法判断哪一步在授权内。

## 6. 交付流程（含耐久检查）

1. 第 3 节取证，得到 D 级判定。
2. 输出第 5 节提案表，等待确认。
3. 联接本体的创建/幂等判定交给 `user-level-skill-junction-delivery` 第 5～6 节执行，本技能只在其前后各加一次耐久检查。
4. 联接创建后立刻重跑第 3 节步骤3，确认 `LinkType` 与 `Target` 正确、`find -L` 非空。
5. 若判定为 D2/D2i 且 B 未授权：交付到此为止，报告必须写「联接可用，权威副本未入库，`git clean` 后可悬空」。
6. 若 B 已授权：按第 7 节提交并复验。

不要为了「让联接更稳」而把文件复制到用户级目录：复制产生两份真相，后续修改只落在其中一份，且第二份同样不在版本控制里。

## 7. 提交后复验

**步骤1：确认提交对象正确、没有夹带。**

```bash
git -C "$REPO" status --porcelain=v1 -- ".agents/skills/$NAME" ".meta/toml/.agents/skills/$NAME" \
  .agents/skills/README.md .agents/capability-registry/02-skills.md .agents/skills/CHANGELOG.md
git -C "$REPO" show --stat --oneline HEAD
```

暂存时按路径逐个加入，不要 `git add -A`：共享工作树里其它会话的在途改动会被一并带走。

**步骤2：确认 blob 一致。**

```bash
git -C "$REPO" hash-object "$SRC/SKILL.md"
git -C "$REPO" rev-parse "HEAD:.agents/skills/$NAME/SKILL.md"
git -C "$REPO" cat-file -e "HEAD:.meta/toml/.agents/skills/$NAME/SKILL.toml"; echo "MIRROR_IN_HEAD_EXIT=$?"
```

两个哈希相等、`MIRROR_IN_HEAD_EXIT=0` 才算 D0。

**步骤3：确认登记面已随提交落盘。**

```bash
git -C "$REPO" grep -c "$NAME" HEAD -- .agents/skills/README.md
git -C "$REPO" grep -c "$NAME" HEAD -- .agents/capability-registry/02-skills.md
git -C "$REPO" grep -c "$NAME" HEAD -- .agents/skills/CHANGELOG.md
```

三处都应 ≥1。计数为 0 说明登记只在工作树里。

**步骤4：经目标路径复验联接仍可解析。**

```bash
find -L "$TARGET" -type f | sort
sha256sum "$SRC/SKILL.md" "$TARGET/SKILL.md"
PYTHONDONTWRITEBYTECODE=1 python "$REPO/.agents/scripts/check-skill-quality.py" --path "$TARGET" --score --threshold 100
```

哈希相等证明读的是同一份内容；质量门经目标路径通过，证明 Qoder 的发现入口能解析。链接门要分仓库路径与目标路径两次跑：

```bash
PYTHONDONTWRITEBYTECODE=1 python "$REPO/.agents/scripts/check-links.py" --path "$SRC" --check-frontmatter-paths
PYTHONDONTWRITEBYTECODE=1 python "$REPO/.agents/scripts/check-links.py" --path "$TARGET" --check-frontmatter-paths
```

第一次必须 0 断链、退出 0。第二次允许**且仅允许** `x-toml-ref` 一项失败：该字段按 SKILL.md 所在目录向上相对解析，从用户级根出发会落到仓库之外（实测解析为 `C:\Users\<user>\.meta\...`）。健康态的判据是「本地引用 0 断链，frontmatter 失败项只有 `x-toml-ref`」；若还出现别的 frontmatter 失败，说明资源引用真的断了。

**步骤5：确认清理动作不会再制造悬空。**

```bash
git -C "$REPO" ls-files -o --exclude-standard -- ".agents/skills/$NAME" ".meta/toml/.agents/skills/$NAME"
find -L "$TARGET" \( -name '__pycache__' -o -name '*.pyc' \) -print
```

D0 时第一条应为空；第二条应为空，否则运行残留已写回主权区。

> **为什么**提交后还要经目标路径再跑一遍门？提交证明内容进了历史，不证明联接仍指向它。换过目录、重建过联接、或提交时移动了文件，都可能让 Target 失配，而 `HEAD` 里的 blob 一切正常。

## 8. 纯审计模式（`--audit`）

用户只想确认现状、不要求交付时，只执行第 3 节与第 7 节步骤2～3，输出：

| 项 | 值 |
|---|---|
| 持久性等级 | D0/D1/D2/D2i/D3 |
| 权威副本 | 路径、是否在 HEAD |
| 镜像 | 路径、是否在 HEAD |
| 联接 | 类型、Target、是否悬空 |
| 登记面 | README/registry/CHANGELOG 在 HEAD 的命中数 |
| 风险 | 会删除该副本的具体命令（如 `git clean -fdx`） |
| 建议 | A/B/C/D 中缺哪一项 |

审计模式零写入：不建联接、不暂存、不提交、不修登记。

## 9. 幂等与重入

| 探针 | 状态 | 重入动作 |
|---|---|---|
| 副本跟踪状态 | D0 | 跳过提交，只做联接与经目标路径复验 |
| 副本跟踪状态 | D1 | 报告未提交改动，等 B 授权；不自动提交 |
| 副本跟踪状态 | D2 | 报告 `git clean` 风险；D 未授权时不登记 |
| 副本跟踪状态 | D2i | 额外指出只有 `-fdx` 才删除，风险等级不降低 |
| 联接 | 已指向同一副本 | 幂等，跳过创建，仅复验 |
| 联接 | 指向别处 | 停止，报告冲突，不覆盖 |
| 联接 | 目标不存在（D3） | 先恢复目标，再评估联接 |
| 登记面 | HEAD 已命中 | 不回滚登记，只核对计数一致性 |

## 10. Gotchas

1. **`git clean -fd` 不删 ignored，但 `-fdx` 会**：D2i 看起来更安全，实际上换机器 clone 一样消失。
2. **`find` 不带 `-L` 对联接返回空**：Windows 目录联接在 Git Bash 里表现为符号链接，空结果不是空包。
3. **`ls -la` 显示 `lrwxrwxrwx` 是正常的**：那是联接表现，不是断链；用 `Get-Item | Select LinkType, Target` 定类型。
4. **`git grep` 默认只搜工作树**：不加 `HEAD` 会在未跟踪/已暂存改动上误报「已登记」。
5. **`git status` 哈希一致不能证明内容持久**：它只证明过程没改动，D2 副本同样能得到一致哈希。
6. **`git ls-files --error-unmatch` 对目录会展开**：目录存在但全未跟踪时也可能返回 0，判定要以 `SKILL.md` 单文件为准再交叉 `status`。
7. **`check-ignore` 退出 1 不是错误**：它表示未命中忽略规则，属正常 D2 信号。
8. **复制到用户级不会让技能更安全**：两份副本都可能不在版本控制里，还额外制造了漂移源。
9. **向联接内写文件会穿透到主权区**：在目标路径下跑脚本产生的 `__pycache__` 落在仓库里，会污染 `git status`。
10. **提交时 `git add -A` 会夹带他人在途改动**：共享工作树必须按路径暂存。
11. **登记面计数不会自动正确**：新增行后 README 与 registry 的表头数字要同轮 +1，否则审计脚本报漂移。
12. **拒绝 `quick_validate.py` 的极简头不代表主权区技能无效**：主权区用仓库原生字段，验收以 `check-skill-quality.py` 为准。
13. **`--json` 混在人类报告之后**：`json.load` 会报 `Extra data`，不要把它当纯 JSON 解析。
14. **管道会吞退出码**：`... | head` 返回 `head` 的状态，门禁结论要取 `$?` 或开 `pipefail`。
15. **目标路径链接门必然在 `x-toml-ref` 报错**：该字段从 `~/.qoder/skills/<name>` 向上解析会落到仓库之外；已联接的 `user-level-skill-junction-delivery` 实测同样只报这一条。仓库路径 0 断链、目标路径仅此一项失败，才是健康态。

## 11. 安全检查清单

- [ ] 已用 `git ls-files --error-unmatch` 对本技能 `SKILL.md` 与镜像各判定一次跟踪状态
- [ ] 已用 `git status --porcelain` 区分 D0/D1/D2，没有只凭目录存在就下结论
- [ ] 已用 `git check-ignore -v` 判定 D2i，并在报告中写明 `-fdx` 风险
- [ ] 已确认联接 `LinkType` 与 `Target`，且 `find -L` 结果非空
- [ ] 已在 HEAD 中检索 README/registry/CHANGELOG，区分「已提交」与「仅工作树」
- [ ] 已输出提案表并取得 A/B/C/D 的明确授权子集，未擅自扩大范围
- [ ] 提交时按路径暂存，未使用 `git add -A`
- [ ] 已比对 `git hash-object` 与 `HEAD:<path>`，确认 blob 一致
- [ ] 已经在仓库路径复跑质量门与链接门并取得退出码 0，目标路径链接门除 `x-toml-ref` 外无其它失败
- [ ] 已确认无 `__pycache__`/`.pyc` 残留、无未跟踪遗留
- [ ] 报告中已写明未执行项（未授权的 B/C/D），未把「已联接」写成「已安装」

## 12. 参考

- 来源取证与磁盘事实：[references/durability-case.md](references/durability-case.md)
- 上下游技能：`user-level-skill-junction-delivery`、`native-skill-surface-registration`、`skill-recommendation-disk-triage`、`user-skill-sovereign-migration`、`skill-quality-gate-remediation`

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：基于会话 f42493e0 的联接交付预案与同轮磁盘取证，固化 D0/D1/D2/D2i/D3 分级、五步只读取证、A/B/C/D 授权拆分、提交后 blob 与联接双复验 |
