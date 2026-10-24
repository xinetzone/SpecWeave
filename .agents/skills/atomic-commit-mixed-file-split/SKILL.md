---
name: atomic-commit-mixed-file-split
version: 1.0.0
description: "当用户提到「一个文件里混了两类改动」「拆成两个原子提交」「git add -p 不好用」「拆提交」「分层推送」「远端指针校验」时，必须使用此技能。用工作树终态加确定性替换构造只含单一关注点的中间态，逐次验证 diff 后分别提交，替代交互式 add -p；再按嵌套仓到父仓顺序推送，用 ls-remote 与 ls-tree 校验远端提交与 gitlink。不用于可按文件分离的改动、共享工作树中他人改动的隔离（用 scoped-commit-shared-worktree）、子模块两级提交的一般流程（用 scoped-submodule-commit），也不用于决定许可或版本下限本身怎么改（用 pep639-license-metadata-migration、version-floor-contract-guard）。"
argument-hint: "<repo-root> <file> [concern-a] [concern-b]"
user-invocable: true
paths:
  - ".agents/skills/atomic-commit-mixed-file-split/**"
title: "混合关注点单文件原子拆分"
source: "会话 c9d91a62-53d0-4853-8e7d-1f4b25892d0d（xuanspace 许可元数据与构建下限的拆分提交及两级推送实测）"
---

# 混合关注点单文件原子拆分

一个文件同时承载两类独立意图时（典型：`pyproject.toml` 既把许可改成 SPDX 表达式、又把构建后端下限从 `>=0.10` 提到 `>=0.11`），按文件 `git add` 会把两类意图压进同一个提交，事后无法单独回滚或引用。本技能把「拆分」变成可复核的三步：备份终态 → 用确定性替换造出中间态 → 提交后还原终态，再提交第二类；最后按嵌套仓到父仓顺序推送并核对远端指针。

## 1. 这个技能解决什么

| 常见做法 | 失败方式 | 本技能的做法 |
|---|---|---|
| `git add -p` 逐块挑选 | 交互式界面无法在智能体会话中稳定驱动，选择顺序与上下文行容易错位 | 不交互：从终态回退另一类改动，得到中间态 |
| 先提交全部、再补一个「拆分」提交 | 历史仍是一个混合提交，拆分目标落空 | 中间态在提交前就物理成立，diff 可逐条核对 |
| 两个提交的信息凭记忆写 | 顺序与依赖关系说不清，回滚时不知道先退哪个 | 先确定顺序与两条提交信息，经确认后才落第一个提交 |

> **为什么？** 拆分的目标不是「看起来有两条提交」，而是「任意一条都能被单独回滚」。只有第一个提交的树内容真的不含第二类改动，回滚才有意义；交互式挑选无法给出可机器复核的证据。

> **为什么？** 用确定性替换而不是手工编辑？手工编辑会漏改、改错缩进，且无法证明替换完整性；带出现次数断言的替换把「这次替换是否覆盖了全部目标」变成脚本退出码，失败时文件不被写入。

> **为什么？** 备份放在 `rev-parse --absolute-git-dir` 下而不是 `/tmp`？Git Bash 的 `/tmp` 与 Windows Python 看到的临时目录不是同一个命名空间，把一个 shell 的临时路径交给另一个运行时必然出现「文件不存在」；放在 git 目录下两边都能访问，且不污染工作树与 `git status`。

> **为什么？** 推送顺序必须嵌套仓在前？父仓库记录的是子仓库的提交 SHA，子仓库提交尚未到达远端时先推父仓库，会把父仓指向一个远端取不到的提交，其他人拉取后子模块检出直接失败。

## 2. 适用与不适用

适用：

- 一个已跟踪文件里混有两类互不依赖或依赖方向明确的改动，用户要求拆成两个原子提交。
- 交互式 `git add -p` 不可用、不稳定，或需要可复现的拆分证据。
- 拆分提交完成后需要推送，并且要核对嵌套仓远端提交与父仓 gitlink 一致。

不适用：

| 场景 | 交给 |
|---|---|
| 两类改动本来就落在不同文件 | `atomic-commit-cmd` 或 `git-commit-helper`，按文件暂存即可 |
| 工作树里还混着其他会话的未提交改动 | `scoped-commit-shared-worktree` 先做隔离，再回到本技能 |
| 子模块提交、detached HEAD、gitlink 一般流程 | `scoped-submodule-commit` |
| 决定许可元数据该怎么写 | `pep639-license-metadata-migration` |
| 决定版本下限该定在哪个版本、怎么写断言 | `version-floor-contract-guard` |
| 只想登记 Skill 或改文档 | 与本技能无关，不要顺手扩大范围 |

## 3. 输入与前置

开工前把六个值写下来，不要边做边猜：

| 变量 | 含义 | 缺失时 |
|---|---|---|
| `REPO` | 目标仓库绝对路径（子模块就是子模块根） | 先确认，禁止用相对路径猜 |
| `FILE` | 混合关注点文件相对 `REPO` 的路径 | 先确认 |
| `A` | 先提交的关注点名称与替换对 | 先列出，不能只有「许可」这种抽象词 |
| `B` | 后提交的关注点名称与替换对 | 同上 |
| `MSG_A` / `MSG_B` | 两条 Conventional Commits 中文提交信息 | 先草拟并确认 |
| `PUSH` | 是否推送 | 默认否，需要用户单独授权 |

前置检查（只读）：

```bash
git -C "$REPO" rev-parse --show-toplevel
git -C "$REPO" status --porcelain=v1 -- "$FILE"
git -C "$REPO" diff --stat -- "$FILE"
git -C "$REPO" branch --show-current
```

若 `status` 中该文件之外还有本包以外的改动，先停下：本技能只处理单个文件的拆分，混合工作树隔离属于 `scoped-commit-shared-worktree`。若当前是 detached HEAD，可以提交，但必须在报告中说明该提交暂无分支引用。

## 4. 选择决策树

```text
一个文件里有两类改动
├─ 两类改动能否逐条列出「现值 → 回退值」的文本对？
│   ├─ 不能（结构性重写、大量重排）→ 停：先与用户确认拆分边界，或退回按文件/按目录提交
│   └─ 能 → 继续
├─ 两类改动之间是否存在依赖？
│   ├─ A 的提交内容依赖 B（例如新许可形态要求更高构建后端）
│   │   → 先确认用户接受「A 先提交、B 紧随其后且推送前不留中间态」，否则改为 B 先提交
│   └─ 无依赖 → 按用户指定的顺序
└─ 是否还有第三类改动？
    ├─ 有 → 停：拆成三段前先确认，不要用两段硬塞
    └─ 无 → 进入预览与确认门
```

## 5. 预览与确认门

正式写盘前输出一张表并等待确认。确认对象是「顺序 + 两条提交信息 + 替换对」，不是「帮我拆一下」这种口头授权。

| 项目 | 内容 |
|---|---|
| 文件 | `$REPO/$FILE` |
| 关注点 A | 名称、替换对（现值 → 回退值）、预期次数 |
| 关注点 B | 名称、替换对（现值 → 回退值）、预期次数 |
| 顺序 | A 先还是 B 先，以及依赖理由 |
| 提交信息 | `MSG_A`、`MSG_B` 原文 |
| 推送 | 不推送 / 已单独授权推送 |
| 不做 | 不碰其他文件、不 `git add -A`、不推送（未授权时）、不跳过 hooks |

替换对先用 `--dry-run` 核对次数，这一步只读：

```bash
python .agents/skills/atomic-commit-mixed-file-split/scripts/split_state.py revert \
  --repo "$REPO" --file "$FILE" --dry-run \
  --pair "scikit-build-core>=0.11|||scikit-build-core>=0.10|||4"
```

输出里的 `count` 必须与预期一致。用户只确认部分项时，只做被确认的部分，并在交付报告里写明缺口。

> **为什么？** 次数断言是拆分正确性的唯一机械证据。次数为 0 说明替换串根本不在文件里，次数偏大说明别处也有同形文本，两种情况都会让「中间态只含 A」的结论失效。

## 6. 工作流

以下命令统一用 `git -C "$REPO"`，不依赖当前 shell 工作目录——Bash 每次调用的 cwd 可能被重置。脚本路径以仓库根为基准，在其他目录执行时改成绝对路径。

### 步骤1：定位 git 目录

```bash
GITDIR="$(git -C "$REPO" rev-parse --absolute-git-dir)"
echo "$GITDIR"
```

子模块的 `.git` 是文件而不是目录，直接拼 `$REPO/.git/...` 会失败，必须用 `--absolute-git-dir` 解析。

### 步骤2：备份终态

```bash
BACKUP="$GITDIR/atomic-split/$(date +%Y%m%d-%H%M%S)/$(basename "$FILE")"
python .agents/skills/atomic-commit-mixed-file-split/scripts/split_state.py backup \
  --repo "$REPO" --file "$FILE" --backup "$BACKUP"
```

记录输出的 `sha256`。备份目录在 git 目录内，不出现在 `git status`，也不会被清理工作树的命令带走。

### 步骤3：构造只含 A 的中间态

从终态回退 B 的替换对（`PRESENT` 是终态里的文本，`REPLACEMENT` 是 A 阶段的文本）：

```bash
python .agents/skills/atomic-commit-mixed-file-split/scripts/split_state.py revert \
  --repo "$REPO" --file "$FILE" \
  --pair "scikit-build-core>=0.11|||scikit-build-core>=0.10|||4"
```

退出码 `0` 才继续；`3` 表示次数不符，文件未被写入，回到第 5 节重新核对；`2` 表示路径或参数错误。整行删除时把换行写成 `\n`，例如 `--pair "old line\n|||\n|||1"`。

### 步骤4：验证中间态只含 A

```bash
git -C "$REPO" diff -- "$FILE"
if git -C "$REPO" diff -- "$FILE" | grep -qF "scikit-build-core>=0.11"; then
  echo "FAIL: 关注点 B 仍出现在 diff 中"; else echo "PASS: diff 只含关注点 A"; fi
git -C "$REPO" diff --stat -- "$FILE"
```

diff 里只能出现 A 的行；出现 B 的特征串就停止，重新构造。同时看 `--stat` 的增删行数是否与 A 的预期一致。

> **为什么？** 次数断言只证明替换执行过，不证明替换后 diff 里没有 B。diff 是暂存前的最后一道人工可读证据，跳过它等于把正确性完全交给脚本。

### 步骤5：暂存并提交 A

```bash
git -C "$REPO" add -- "$FILE"
git -C "$REPO" diff --cached --name-status
git -C "$REPO" diff --cached -- "$FILE"
git -C "$REPO" commit -m "$MSG_A"
git -C "$REPO" show --stat --oneline HEAD
```

`diff --cached --name-status` 必须只有 `$FILE` 一行。多出文件就停下：要么它属于本次范围并补进说明，要么不属于并从暂存区移除。hook 失败时修根因后重新提交，不跳过 hook，不 amend 已推送的提交。

### 步骤6：还原终态

```bash
python .agents/skills/atomic-commit-mixed-file-split/scripts/split_state.py restore \
  --repo "$REPO" --file "$FILE" --backup "$BACKUP"
```

输出里的 `sha256` 必须等于步骤 2 记录的值；退出码 `4` 表示备份或还原校验失败，立即停止并报告，不要继续第二个提交。

### 步骤7：验证并提交 B

```bash
git -C "$REPO" diff -- "$FILE"
if git -C "$REPO" diff -- "$FILE" | grep -qF "license = {file = \"LICENSE\"}"; then
  echo "FAIL: 关注点 A 回退了"; else echo "PASS: diff 只含关注点 B"; fi
git -C "$REPO" add -- "$FILE"
git -C "$REPO" diff --cached --name-status
git -C "$REPO" commit -m "$MSG_B"
```

### 步骤8：收尾验证

```bash
git -C "$REPO" status --porcelain=v1 -- "$FILE"
git -C "$REPO" log --oneline -3
git -C "$REPO" show --stat --oneline HEAD~1
```

该文件在 `status` 中必须为空；最近两次提交应分别只含 A 与 B 的改动。删除备份目录后结束（备份在 git 目录内，确认路径无误再删）。

## 7. 分层推送与远端校验

推送会让变更离开本机，必须在用户单独授权后执行。默认只做本地提交。

```bash
# 嵌套仓（或单仓）先推
git -C "$REPO" fetch origin
git -C "$REPO" rev-list --left-right --count HEAD...origin/main
git -C "$REPO" push origin HEAD:main
git -C "$REPO" ls-remote origin refs/heads/main
```

`rev-list` 输出必须形如 `N	0`：本地领先 N 个提交、落后 0 个。落后不为 0 时先同步，不要强推。`ls-remote` 返回的 SHA 必须等于 `git -C "$REPO" rev-parse HEAD`。

父仓库最后提交 gitlink：

```bash
git -C "$PARENT" add -- "projects/<name>"
git -C "$PARENT" diff --cached --name-status
git -C "$PARENT" commit -m "chore(submodule): 前移 <name> 指针至 <sha>"
git -C "$PARENT" fetch origin
git -C "$PARENT" rev-list --left-right --count HEAD...origin/main
git -C "$PARENT" push origin HEAD:main
git -C "$PARENT" ls-tree origin/main "projects/<name>"
```

`ls-tree` 的 gitlink SHA 必须等于嵌套仓的 `HEAD`，并且该 SHA 已能在嵌套远端取到。子模块工作树若仍显示 dirty，属预期状态，不要用 reset 或 clean 消除。

> **为什么？** 本地提交成功、父仓 gitlink 也写了，仍可能不可用：gitlink 指向的提交没推上去，别人 `submodule update` 就会失败。`ls-remote` 与 `ls-tree` 分别从远端验证「提交到了」和「指针指对了」。

## 8. 失败处理

| 失败点 | 判断依据 | 处理 |
|---|---|---|
| 替换次数为 0 或偏大 | 脚本退出码 `3`，文件未写 | 回到预览门重列替换对；不要改用整文件重写绕过 |
| diff 里出现另一类改动 | 步骤 4 或 7 的 grep 命中 | 停止，重新构造中间态；不要提交半成品 |
| 暂存区混入其他文件 | `diff --cached --name-status` 行数大于 1 | 只保留 `$FILE`，其余用 `restore --staged` 取消暂存 |
| 备份还原哈希不符 | 脚本退出码 `4` | 停止第二个提交，报告备份路径与两个哈希 |
| hook 失败 | commit 退出码非 0 | 修根因后重新提交；不跳过 hook，不 amend 已推送提交 |
| 推送被拒或落后 | `rev-list` 第二个数字不为 0，或 push 报 non-fast-forward | 先 fetch 并确认分歧来源，禁止强推 |
| 父仓 gitlink 指向未推送提交 | `ls-remote` 里找不到该 SHA | 先补推嵌套仓，再更新父仓指针 |
| 发现第三类改动 | 预览门或 diff 中暴露 | 停止，重新与用户确认拆分边界 |

## 9. Gotchas（陷阱与反直觉行为）

1. Git Bash 的 `/tmp` 与 Windows Python 的临时目录不是同一路径，跨运行时传临时文件必然「文件不存在」；备份放 `--absolute-git-dir` 下。
2. Bash 每次调用的工作目录可能重置，`cd projects/x` 后下一条命令就在别处；统一用 `git -C <绝对路径>`。
3. `git add -- <file>` 暂存的是整个文件，拆分发生在工作树内容里，不在索引挑选里；中间态必须先物理成立。
4. 替换对按书写顺序执行，存在包含关系时先长后短，并给每对独立的预期次数。
5. `--pair` 的三段用 `|||` 分隔；替换文本里出现 `|||` 时改用更小的替换粒度。
6. 整行删除要把换行写成字面 `\n`，否则会把相邻两行粘成一行。
7. 两个提交的顺序有依赖时，第一个提交可能短暂不自洽；要么先确认用户接受并在推送前补齐，要么调换顺序。
8. 行尾风格可能被工具改写；若 `git diff --stat` 显示整文件重写，先查 `core.autocrlf`，不要继续提交。
9. 管道会吞退出码，`... | head` 返回的是 `head` 的状态；需要判据时用 `grep -q` 加 `if` 或取 `${PIPESTATUS[0]}`。
10. 父仓 gitlink 只能指向一个确定提交；嵌套仓还在后续修改时，先完成嵌套提交再更新指针。
11. 共享工作树里不要用 `git stash`、`reset --hard`、`clean` 来「让状态干净」，那会破坏其他会话的未提交内容。
12. 子模块的 `.git` 是文件，`$REPO/.git/...` 不是目录；必须 `rev-parse --absolute-git-dir`。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认 `REPO` 与 `FILE` 为绝对路径与实际文件，未误改其他文件
- [ ] 已确认工作树中没有本包之外的其他会话改动（否则先转隔离技能）
- [ ] 已列出两类改动的替换对与精确预期次数，并跑过 `--dry-run`
- [ ] 已输出预览表并取得用户对顺序、两条提交信息与推送范围的确认
- [ ] 已备份终态并记录 sha256，备份路径在 git 目录内
- [ ] 步骤4 与步骤7 的 diff 均只含对应一类改动，无泄漏
- [ ] 两次 `diff --cached --name-status` 都只有目标文件
- [ ] 已还原终态且 sha256 与备份一致，工作树该文件收尾为空
- [ ] 推送前 `rev-list` 落后数为 0，推送后 `ls-remote` 与本地 HEAD 一致，`ls-tree` 与嵌套 HEAD 一致
- [ ] 未使用 `git add -A`、未跳过 hooks、未强推、未 amend 已推送提交
- [ ] 未提交或推送未获授权的仓库，报告中已列明未执行项

## 11. 参考

- 完整命令序列与实测记录：[references/split-runbook.md](references/split-runbook.md)
- 来源会话取证与未验证项：[references/verified-case.md](references/verified-case.md)
- 行为评估场景：[evals/evals.json](evals/evals.json)
- 相邻技能：`scoped-commit-shared-worktree`、`scoped-submodule-commit`、`atomic-commit-cmd`
