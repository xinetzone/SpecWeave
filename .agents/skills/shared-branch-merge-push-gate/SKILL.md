---
name: shared-branch-merge-push-gate
version: 1.0.0
description: "在共享分支执行 merge 与 push 前必须先预检：当用户的工作树可能被其他会话并发提交，或用户提到「合并后推送」「同步上游」「merge origin/main」「落后上游几条怎么办」「推送被拒」时必须使用本技能。先现取分歧度并核对用户授权时的基线是否漂移，再 fetch、预演冲突、求上游改动路径与本地脏/未跟踪集合的交集、检查索引锁与 merge/rebase 中间态；全部通过才用 git merge --no-edit（--no-rebase 是 pull 专属参数），并按子模块到父仓的顺序推送，推送前再次现取分歧度。合并引入的 vendor gitlink 偏移属正常记录与检出差异，未经授权不跑 git submodule update。不用于单纯提交隔离（用 scoped-commit-shared-worktree 或 scoped-submodule-commit）、rebase 进行中的写入判断（用 shared-worktree-rebase-write-guard）或普通单仓提交（用 git-commit）。"
argument-hint: "[--repo <path>] [--upstream <ref>] [--expect-ahead N --expect-behind M] [--expect-head SHA]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/shared-branch-merge-push-gate/**"
source: "来源会话 c9d91a62-53d0-4853-8e7d-1f4b25892d0d 的 2026-10-23 合并与推送实测：授权时落后 6 条、执行时 11 条触发分类器拦截；git merge --no-rebase 误用；约 2.9 天陈旧索引锁经排查后改名保留"
title: "共享分支合并与推送门禁"
x-toml-ref: "../../../.meta/toml/.agents/skills/shared-branch-merge-push-gate/SKILL.toml"
---

# 共享分支合并与推送门禁

共享分支上，「合并 + 推送」不是两条 git 命令，而是**一次以授权前提为输入的事务**。用户批准时听到的可能是「落后 6 条、工作区安静」，执行时现实却可能已经变成「落后 11 条、另一个进程正在提交」。本技能在动手前把现实重新测一遍，把差异摆回用户面前，而不是沿用旧前提硬做。

## 1. Why：三种高代价失败

1. **用过期分歧度执行**：会话早期读到 `behind 6`，几分钟后上游已推进到 `behind 11`。数字本身不会报错，只会让合并范围、冲突概率和推送竞争全部失真。
2. **忽略并发提交者**：同一工作树里另一进程可能在会话中途提交两次（HEAD 从 34 推进到 36），并持续写入未提交文件。合并可能不碰这些路径，但推送会与对方竞争，语义重叠也无法靠路径交集发现。
3. **把 pull 的参数用在 merge 上**：`git merge --no-rebase` 只会打印用法文本并退出，不会执行合并。若把「有输出」当成「已成功」，后续推送的就是旧 HEAD。

> **为什么**必须现取分歧度？分歧度是远端状态的时间切片，不是仓库的稳定属性。任何来自会话早期、用户描述或上一轮输出的数字，在 fetch 之后都可能已经过期。

> **为什么**前提变化要重新问，而不是自动继续？用户批准的是「在落后 6 条、工作区安静的前提下合并」。前提变了，批准的对象也就变了；自动继续等于替用户接受一个他没看过的新风险。

## 2. 适用边界

| 场景 | 使用本技能 | 交给谁 |
|---|---|---|
| 合并上游前的分歧度、冲突、路径碰撞、授权漂移检查 | 是 | — |
| 子模块与父仓的推送顺序、推送后验收 | 是 | — |
| 索引锁与 merge/rebase 中间态的合并前排查 | 是 | — |
| 只把本次改动放进提交（暂存隔离） | 否 | `scoped-commit-shared-worktree` |
| 子模块与父仓 gitlink 的两级提交 | 否 | `scoped-submodule-commit` |
| rebase 进行中判断哪些写入可以继续 | 否 | `shared-worktree-rebase-write-guard` |
| 子模块只读审计、授权后提交 | 否 | `readonly-submodule-audit-to-commit` |
| 普通单仓、干净工作树的提交 | 否 | `git-commit` |

## 3. G0：先固化授权基线

在第一次 fetch 或 merge 之前，把用户批准时的口径写成可比较的值：

- 目标仓库与分支（父仓、子模块分别记）
- `HEAD` 的完整 SHA 与短 SHA
- `ahead / behind` 两个数字
- 上游 ref 名与其当时 SHA
- 工作区是否有未提交改动；若有，记下路径集合
- 合并策略（merge 还是 rebase）与推送范围（只推子模块、只推父仓、还是两者）

执行时任何一项变化，都先停下，用「批准时 / 现在」两列报告 delta，再取得新的明确授权。用户说「照旧」也意味着他知道了新数字，而不是让你忽略数字。

## 4. G1–G6：执行前预检

按顺序跑，任一步失败就停在该步，不要「先合并再补救」。

**步骤1：现取分歧度与 HEAD。**
```bash
git -C <repo> rev-list --left-right --count HEAD...<upstream>
git -C <repo> rev-parse HEAD
```
输出第一列是 HEAD 独有（ahead），第二列是上游独有（behind）。不要交换顺序，也不要用会话早期缓存值。

**步骤2：fetch 并记录上游真值。**
```bash
git -C <repo> fetch <remote> <branch>
git -C <repo> rev-parse <upstream>
git -C <repo> log -1 --format='%H %cI %s' <upstream>
```
大仓可能因 LFS 或 `fetch.recurseSubmodules=on-demand` 很慢。超时转后台不等于失败：检查后台任务输出与 `origin/<branch>` 引用是否已更新，再决定继续等待还是缩小 fetch 范围。

**步骤3：列出上游将要带入的路径。**
```bash
git -C <repo> merge-base HEAD <upstream>
git -C <repo> diff --name-only --no-renames -z <merge-base> <upstream>
```
用 merge-base 到上游的单侧 diff；不要用 `HEAD...<upstream>` 的双侧 diff，否则本地改动会被算进「上游路径」，碰撞检查必然误报。

**步骤4：列出本地脏文件与未跟踪文件。**
```bash
git -C <repo> status --porcelain=v1 -z
```
保留目录条目（如 `work/`）与子模块状态（如 ` m projects/x`），它们是碰撞检查的一部分。

**步骤5：求交集。**
对每个上游路径与本地路径做前缀比较：完全相等、或一方是另一方的目录前缀，都算碰撞。空集只是**路径级**通过，不代表语义不重叠；若上游正在改写另一会话也在编辑的同一主题文档，要在报告里点明。

**步骤6：冲突预演与中间态检查。**
```bash
git -C <repo> merge-tree --write-tree HEAD <upstream>
```
`exit 0` 表示无冲突，`exit 1` 表示有冲突，其他退出码表示该 Git 版本不支持或参数不可用——一律按「无法证明无冲突」处理。随后检查 `.git/index.lock`、`MERGE_HEAD`、`CHERRY_PICK_HEAD`、`REVERT_HEAD`、`rebase-merge/`、`rebase-apply/`。

## 5. 一键预检脚本

`scripts/merge_gate.py` 把 G1–G6 串成一次只读检查，并与 `--expect-*` 基线比较：

```bash
python .agents/skills/shared-branch-merge-push-gate/scripts/merge_gate.py \
  --repo . --upstream origin/main \
  --expect-ahead 36 --expect-behind 11
```

| 退出码 | 含义 | 下一步 |
|---|---|---|
| 0 | 全部通过 | 执行合并 |
| 2 | 授权前提漂移 | 报告 delta，重新取得授权 |
| 3 | 冲突预演失败或不可用 | 停止，报告冲突或 Git 能力不足 |
| 4 | 上游路径与本地脏/未跟踪集合有交集 | 停止，逐路径确认归属 |
| 5 | 存在索引锁或 merge/rebase 中间态 | 先排查状态，不要直接删锁 |
| 6 | 仓库、上游引用或 Git 环境错误 | 先 fetch 或修正参数 |

同时命中多项时按 `6 → 5 → 3 → 4 → 2` 取最高优先级，报告会列出全部原因。脚本不会执行 fetch、merge 或 push，也不会改索引与工作树；上游新鲜度取决于你在此之前是否 fetch。

> **为什么**脚本不自动 fetch？fetch 会改变引用，且在本仓可能极慢或递归拉子模块。把「取真值」和「判断能否合并」分开，才能让慢操作可中断、可重试，也不让一次超时污染判断。

## 6. 执行合并

只有预检为 0 才执行：

```bash
git -C <repo> merge --no-edit <upstream>
```

- 不要用 `git merge --no-rebase`：`--no-rebase` 属于 `git pull`，merge 只会打印用法并退出。
- 合并前再取一次 `rev-list --left-right --count` 与 HEAD；并发进程可能在预检与合并之间又提交。
- 若出现预演未预测到的冲突：停止，列出冲突路径，不擅自选择 ours/theirs，也不执行 `merge --abort` 破坏对方状态。

合并后立即验证：

```bash
git -C <repo> rev-parse HEAD
git -C <repo> rev-list --left-right --count HEAD...<upstream>
git -C <repo> status --porcelain=v1
```

确认 `behind` 为 0、HEAD 是预期的合并提交、并发会话的未提交路径仍在。

## 7. 推送与收尾

推送顺序固定为**先子模块、后父仓**，因为父仓 gitlink 应指向已经存在于远端的子模块提交。

```bash
git -C <submodule> push <remote> <branch>
git -C <parent> push <remote> <branch>
```

- 不使用 `--force`、`--force-with-lease` 或 `+refspec`，除非用户在当前轮明确要求并知道后果。
- 推送被拒（non-fast-forward）说明上游在你 fetch 后又前进：重新 fetch、重跑 G1–G6、重新取授权，不要用 force 把别人的提交抹掉。
- 推送后再次现取两侧 `rev-list --left-right --count HEAD...<upstream>`，期望都是 `0 0`；同时记录推送区间与 pre-push 钩子结果。

## 8. 索引锁与中间态处置

锁文件存在时，先证明它是否可以安全移走：

1. 记录路径、大小、mtime：`git rev-parse --git-path index.lock`。
2. 检查 `MERGE_HEAD`、`rebase-merge/`、`rebase-apply/`、`CHERRY_PICK_HEAD`、`REVERT_HEAD`。
3. 列出当前 git 进程：Windows 用 `tasklist /FI "IMAGENAME eq git.exe"`，POSIX 用 `ps -eo pid,lstart,cmd | grep '[g]it'`。
4. 若锁为 0 字节、mtime 远早于当前进程、无中间态、无对应活进程：改名保留而非删除：

```bash
mv .git/index.lock .git/index.lock.stale-<timestamp>
```

5. 重试操作；成功后只清理自己创建的备份。若有活进程或中间态，停止并报告，绝不 `rebase --abort` 或 `merge --abort` 别人的状态。

> **为什么**先改名而不是删除？改名是可回退的证据保全；删除会同时消灭「谁在何时创建了它」这条线索。即使判断为陈旧，也应先保留再清理。

## 9. Gotchas

1. **`--no-rebase` 不是 merge 参数**：它会让命令打印用法并退出，看起来「有输出」，实际什么都没合并。
2. **分歧度会自己变**：本案例从 `behind 6` 变成 `behind 11`，HEAD 从 34 变成 36，全部发生在同一次会话内。
3. **「工作区安静」是最先过期的前提**：对方可能在你批准后 5 分钟继续写入；每次执行前都要重取脏文件集合。
4. **路径交集为空不等于语义安全**：上游可能正在改另一会话也在编辑的同一主题文档，计数器同步尤其容易语义冲突。
5. **`merge-tree --write-tree` 的非 0/1 退出码不是冲突**：旧 Git 或参数不支持时会打印用法；应报「无法证明」，不能当成通过。
6. **合并后 vendor 子模块的 ` M` 是正常偏移**：上游更新了 gitlink 记录，本地检出仍停在旧版本。未经授权不要 `git submodule update`，那会改共享检出并可能联网拉包。
7. **子模块先推、父仓后推**：反过来会让父仓短暂指向远端不存在的子模块提交。
8. **推送竞争不是冲突**：对方先推成功时你只会被拒；正确动作是重新 fetch 并重新过门，不是 force。
9. **untracked 目录按前缀碰撞**：本地 `work/` 与上游新增 `work/foo.py` 必须算碰撞，不能只比较完整路径。
10. **分离 HEAD 的子模块不能直接推分支**：先确认分支与上游跟踪关系；提交与分支问题交给 `scoped-submodule-commit`。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认本轮 fetch 后上游 ref 的 SHA 与提交时间，且记录在报告中
- [ ] 已现取 ahead/behind，不是复用会话早期数字
- [ ] 已确认分歧度、HEAD 与工作区状态和用户授权基线一致；不一致已回报 delta 并取得新授权
- [ ] 已确认上游改动路径与本地脏/未跟踪集合的交集为空，或已逐条确认归属
- [ ] 已确认冲突预演 exit 0；若不可用，已按「无法证明」停止
- [ ] 已检查索引锁与 merge/rebase/cherry-pick 中间态，未直接删除锁文件
- [ ] 已确认推送未使用 force，且顺序为子模块到父仓
- [ ] 已验证合并后并发会话的未提交改动原样保留
- [ ] 已验证最终两侧分歧度为 0 0，或如实报告残留与原因

## 11. 验证记录与参考

- 真实案例、命令原文与失败输出见 [references/verified-case.md](references/verified-case.md)。
- 测试场景见 [evals/evals.json](evals/evals.json)。
- 本次技能创建时，脚本在当前仓库做过只读运行，并在临时夹具中验证过冲突、路径碰撞、索引锁、前提漂移与环境错误五类退出码。
