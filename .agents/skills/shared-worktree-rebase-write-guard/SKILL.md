---
name: shared-worktree-rebase-write-guard
version: 1.0.0
description: "在共享工作树写入前探测进行中的 rebase/merge/cherry-pick 与冲突，区分可安全创建的新目录与必须延后的共享登记面，绝不 abort/continue 他人发起的 rebase；采用「内容+验证+联接先行、登记延后」的部分交付，恢复后重新读取版本号与计数再补登记。当用户要求在一个可能被其他会话 git pull/rebase/merge 的工作区新增或更新 Skill、修改索引/计数/登记文件，或出现 HEAD detached、UU 冲突、rebase-merge 目录、登记面数字突然回退时必须使用此技能。触发词：共享工作区、rebase 进行中、pull --rebase、gitlink 冲突、登记面数字回退、写入前预检、rebase guard、shared worktree、concurrent rebase、defer registration。不用于提交隔离（用 scoped-commit-shared-worktree）、计数审计（用 skill-registry-count-drift-audit）、四处登记本体（用 native-skill-surface-registration）。"
argument-hint: "[--repo <path>] [--target <path>]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/README.md"
  - ".agents/capability-registry/02-skills.md"
  - ".agents/skills/CHANGELOG.md"
  - "scripts/check_rebase_guard.js"
source: "会话 f89c6f62-8f22-4634-b17c-da29d8380837 的 2026-10-24 09:12-09:22 rebase 中断实测；登记面 18→11 与 v1.35→v1.29 的回退后恢复"
x-toml-ref: "../../../.meta/toml/.agents/skills/shared-worktree-rebase-write-guard/SKILL.toml"
---
# 共享工作树 rebase 写入门禁

共享工作树里，另一个会话随时可能启动 `git pull --rebase`。此时仓库看起来仍能读写，但检出正处于「重放中途」：已跟踪文件是旧基线的字节，未重放的提交还没落回来，冲突路径处于 `UU` 状态。任何基于这份快照的写入，都会在 rebase 继续时被覆盖、被重放成冲突，或者把别人的半成品带进提交。

本技能把「写之前先证明工作区允许写」变成一次可复跑的预检，并把交付拆成两段：**内容与验证现在做，共享登记面等 rebase 结束后再做**。

## Why：三种代价最高的失败

1. **写入被重放覆盖**：rebase 每 `pick` 一个提交都会改写工作树与索引。你在中途改的 README、registry、CHANGELOG，会在后续 `pick` 中被旧提交的版本替换，且通常没有任何报错。
2. **把冲突放大**：原本只有子模块 gitlink 一个冲突，中途改同一批共享文件会让后续提交产生新的文本冲突，解决成本从「一个指针」变成「多处人工合并」。
3. **替别人做决定**：`rebase --abort` 会丢弃正在重放的提交，`--continue` 会在冲突未解决时推进历史。发起者不是你时，这两种操作都可能销毁他人的工作。

> **为什么未跟踪的新目录可以写？** rebase 的 checkout 与 pick 只覆盖被跟踪路径，未跟踪文件不在重放集合里。新建 `.agents/skills/<new-name>/` 不会与任何提交冲突，也不会被 `--abort` 带走；前提是它确实未被跟踪，而不是「看起来像新目录」。

## 1. 适用边界

| 场景 | 使用本技能 | 交给谁 |
|---|---|---|
| 共享工作树写入前判断是否安全 | 是 | — |
| 发现 rebase/merge 进行中，决定哪些写入延后 | 是 | — |
| 新 Skill 内容、脚本、用户级联接的先行交付 | 是 | — |
| rebase 结束后补登记、重验计数 | 是（重验阶段） | 计数判定用 `skill-registry-count-drift-audit` |
| 混杂工作树的提交隔离 | 否 | `scoped-commit-shared-worktree` |
| 四处登记本体的字段与格式 | 否 | `native-skill-surface-registration` |
| 子模块内部审计、lock 处理、gitlink 提交 | 否 | `readonly-submodule-audit-to-commit` |

## 2. 输入

开始前写下来：

- `REPO`：仓库根，默认当前目录。
- `TARGET`：本次要写的路径；可以是一个新目录、一个共享登记文件，或仓库外路径。
- `WRITE_SET`：本次计划写入的全部路径。若包含 README、registry、CHANGELOG、TOML 镜像，视为共享写入。
- `OWNER`：这次 rebase/merge 是否由本会话发起。不是本会话发起的，一律只读。

> **为什么要先写 `WRITE_SET`？** 预检的结论依赖「写什么」。新目录与共享登记面的安全结论相反；不先列出写入面，就无法把「可写」和「延后」分开。

## 3. P0：写前探测

每次写入批次之前重跑，不要复用上一批的结论。

```bash
git -C "$REPO" rev-parse --abbrev-ref HEAD
git -C "$REPO" rev-parse --short HEAD
git -C "$REPO" rev-parse --absolute-git-dir
git -C "$REPO" rev-parse --path-format=absolute --git-path rebase-merge
git -C "$REPO" rev-parse --path-format=absolute --git-path rebase-apply
git -C "$REPO" rev-parse --path-format=absolute --git-path MERGE_HEAD
git -C "$REPO" rev-parse --path-format=absolute --git-path CHERRY_PICK_HEAD
git -C "$REPO" rev-parse --path-format=absolute --git-path REVERT_HEAD
git -C "$REPO" status --short
git -C "$REPO" ls-files -u
git -C "$REPO" reflog -8 --date=iso
```

若 rebase 目录存在，读取元数据而不是只看 `git status` 的摘要：

```bash
for f in head-name onto orig-head msgnum end stopped-sha done git-rebase-todo; do
  test -f "$REPO/.git/rebase-merge/$f" && { echo "--- $f"; sed -n '1,5p' "$REPO/.git/rebase-merge/$f"; }
done
```

用捆绑脚本一次拿到结构化结论：

```bash
node "$REPO/.agents/skills/shared-worktree-rebase-write-guard/scripts/check_rebase_guard.js" \
  --repo "$REPO" --target "$TARGET" --json
```

### 3.1 信号解释矩阵

| 信号 | 含义 | 对已跟踪路径 | 对未跟踪新目录/仓库外路径 |
|---|---|---|---|
| `rebase-merge/` 或 `rebase-apply/` 存在，`ls-files -u` 非空 | rebase 停在冲突 | 禁写 | 可写 |
| rebase 目录存在，`ls-files -u` 为空 | rebase 正在重放或等待 continue | 延后 | 可写 |
| `.git/MERGE_HEAD` 存在 | merge 未完成 | 延后 | 可写 |
| `.git/CHERRY_PICK_HEAD` 或 `.git/REVERT_HEAD` 存在 | pick/revert 未完成 | 延后 | 可写 |
| `HEAD` detached 且无 rebase/merge/pick 目录 | 正常的检出状态或残留 | 先查 reflog 与 `git status`，不臆断 | 可写 |
| 无上述信号，分支已附着 | 常规工作区 | 按普通写前检查 | 可写 |
| `.git/index.lock` 存在 | 可能有进程持有索引 | 不写、不删锁，先查进程 | 不写 |

> **为什么冲突信号优先于「分支已附着」？** rebase 过程中 `HEAD` 必然 detached，这是机制而不是损坏。只看 `git rev-parse --abbrev-ref HEAD` 得到 `HEAD` 就判断「仓库异常」会误判；反过来，只看 `status` 的摘要也可能漏掉刚启动的 rebase。目录信号与 unmerged 列表合起来才是事实。

> **为什么 reflog 必须看？** 它能回答「谁在什么时候发起了操作」。读到 `pull --rebase (start)`、`rebase (pick)`、`rebase (finish)` 的时间线，才能判断当前是进行中还是已结束，以及这次操作是否由本会话发起。发起者不是本会话时，`--abort`/`--continue` 都是越权。

## 4. 目标分类

```
TARGET 在仓库外？
├─ 是 → safe-outside（仍要验证联接目标存在，见 Gotchas）
└─ 否 → git ls-files -- TARGET 有输出？
        ├─ 是 → tracked
        │      ├─ 有 rebase/merge/pick → defer
        │      └─ 无操作 → clean（strict 模式再查该路径是否 dirty）
        └─ 否 → git check-ignore 命中？
                ├─ 是 → safe-ignored
                └─ 否 → safe-untracked（可创建）
```

| 分类 | 判定 | 动作 |
|---|---|---|
| `outside-repo` | 绝对路径不在 `--show-toplevel` 下 | 可写；若经 Junction 写入，先确认目标存在 |
| `untracked` | `git ls-files -- <rel>` 为空且未被忽略 | 可创建；只创建计划内的路径 |
| `ignored` | `git check-ignore` 命中 | 可写；注意不要把产物写进共享登记面 |
| `tracked` | `git ls-files -- <rel>` 非空 | 有操作进行中时延后；无操作时按普通写前检查 |
| `conflicted` | 出现在 `git ls-files -u` 的路径 | 禁写；冲突解决归发起者 |
| 共享登记面 | README、registry、CHANGELOG、TOML 镜像 | 任何操作进行中都延后；恢复后重读再写 |

> **为什么共享登记面要单独一类？** 它们的数值与版本号是全局共享状态。并发写入不会只影响一行：分类计数、跨面差、CHANGELOG 版本号会互相矛盾，后人无法判断哪个数字是真相。把登记动作放到 rebase 结束后，才能基于唯一基线做一次可复跑的写入。

## 5. 部分交付：内容先行，登记延后

rebase 进行中仍可完成一部分交付，把它明确切成两段：

1. **写入未跟踪内容**：新 Skill 目录、脚本、references。只创建 `WRITE_SET` 内的路径，不碰其他文件。创建前做幂等检查：目标已存在则复用或停止，不覆盖。
2. **本地验证**：语法检查、脚本自检、真实/夹具回归、质量门、链接门。验证只读，不受 rebase 影响。
3. **建立或校验用户级联接**：目标在仓库外时可直接建立；联接目标若因 rebase 暂时缺失，不要删除联接，先记录为悬空，恢复后回读。
4. **输出延后清单**：在最终报告里列出待写的共享面、待重读的版本号与计数、恢复后的复跑命令。不要把清单写进任何共享登记文件。
5. **不暂存、不提交**：本阶段结束时的正确状态是「只有未跟踪新目录」，而不是「工作树干净」。

> **为什么验证可以在 rebase 中做？** 验证读取的是新目录自己的字节，与共享登记面的重放无关。把验证前置，可以在等待恢复的时间里把内容质量确定下来；恢复后只剩「重读基线 + 补登记」这一小段，减少再次被打断的窗口。

## 6. 恢复后重验

只有同时满足以下条件，才进入登记阶段：

- `rebase-merge/`、`rebase-apply/`、`MERGE_HEAD`、`CHERRY_PICK_HEAD`、`REVERT_HEAD` 均不存在。
- `git status` 不再出现 `UU`/`AA`/`DD`。
- 分支已附着（不是 `HEAD`），且 reflog 出现 `rebase (finish)` 或 merge 完成记录。
- `git log --oneline -5` 显示重放后的提交；不要假设提交哈希与中断前相同。

然后按顺序做：

1. **重读基线**：`git rev-parse --short HEAD`、CHANGELOG 顶部版本号、README 与 registry 的分类计数。不要使用中断前的快照。
2. **重跑审计**：用 `skill-registry-count-drift-audit` 的脚本对两个登记面做一次只读审计，确认当前漂移集合。
3. **重跑质量门与链接门**：确认内容与引用在恢复后的文件树里仍然有效。
4. **逐面写入**：每写一个共享面之前重跑 P0 预检；若又出现新操作，立即停止并回到延后状态。
5. **只暂存目标路径**：需要提交时交给 `scoped-commit-shared-worktree`，显式列出路径，不用 `git add -A`。
6. **完成态检查**：对比写入前后共享文件的校验和（只允许目标文件变化），确认没有把他人改动带进来。

> **为什么不能复用中断前的数字？** 本次实测中，登记面在几分钟内从 18→11、16→9、v1.35→v1.29，rebase 完成后又恢复为 18/16/v1.35。任何基于旧数字的「+1」都会写错；恢复后必须重新取当前值。

## 7. 禁止清单

以下操作即使用户说「把工作区弄干净」也不要执行，除非用户明确指定由本会话发起并承担后果：

- `git rebase --abort`、`--continue`、`--skip`：会丢弃或推进他人正在重放的历史。
- `git reset --hard`、`git checkout -- <path>`、`git restore <path>`、`git clean -f`：会销毁未提交工作。
- 删除 `.git/rebase-merge/`、`.git/rebase-apply/`、`.git/index.lock`：伪造状态或破坏锁。
- 手工编辑 `UU projects/<submodule>` 的 gitlink：子模块指针冲突需要发起者决定目标提交。
- 在探测到操作进行中时写 README、registry、CHANGELOG、TOML 镜像。
- 用 `git add -A` 或 `git add .` 暂存；用 `git pull` 自行「帮忙」推进。

> **为什么不能删 `index.lock`？** 锁可能属于正在运行的 git 进程。删除它不会让操作更快，只会让两个进程同时写索引，产生更难恢复的状态。先判断锁的持有者，再决定等待还是由用户处理。

## 8. 报告模板

```markdown
## 共享工作区写入预检

- 仓库：<REPO>（<branch> @ <head>）
- 操作：<none / rebase / merge / cherry-pick / revert>
- rebase 元数据：onto=<...> orig-head=<...> 进度=<msgnum>/<end> stopped=<...>
- 冲突：<path 列表 / 无>
- 目标：<TARGET> → <outside-repo / untracked / ignored / tracked / conflicted>
- 结论：<可写 / 延后 / 只读>

### 已完成
- <新目录 / 脚本 / references / Junction>

### 延后
- <共享面清单>
- 恢复后命令：<重读版本与计数、审计、质量门、链接门>

### 未做
- 未执行 abort/continue/reset/checkout/clean；未暂存；未提交。
```

## 9. Gotchas（陷阱与反直觉行为）

1. **只读 `git status` 头部不够**：摘要可能只显示 `UU`，不显示正在重放；`rebase-merge/` 目录才是权威信号。
2. **`HEAD` detached 是 rebase 的正常状态**：不要把它当成仓库损坏，也不要自动 `checkout main`。
3. **未跟踪不等于被忽略**：`git check-ignore` 命中与 `git ls-files` 为空是两回事；忽略文件通常可写，但仍要确认它不是构建产物目录。
4. **`rebase-merge` 与 `rebase-apply` 二选一**：交互式 rebase 用前者，`am` 风格用后者；只查一个会漏判。
5. **登记面数字会回退再恢复**：并发 rebase 期间读到的是旧基线，不是「有人删了内容」。不要据此修表头。
6. **状态会在调查中途翻转**：本次 rebase 在 09:22:42 由另一进程完成，前一分钟的快照立即失效。每个写入批次前重新探测。
7. **用户级 Junction 可能悬空**：rebase 检出里新 Skill 目录暂时不存在时，`test -e <link>/SKILL.md` 会失败；不要删除联接，等恢复后回读。
8. **`UU` 子模块不是文本冲突**：`projects/<name>` 是 gitlink，冲突内容是提交指针；不要用编辑器改。
9. **恢复后行号与版本号会变**：重放提交可能改变文件内容与行号；引用行号前重新 `grep`。
10. **rebase 可能由其他会话发起**：reflog 的时间与 `pull --rebase (start)` 是判断依据；不是本会话发起的，一律只读。

## 10. 安全检查清单（逐项确认）

- [ ] 已探测 `rebase-merge`、`rebase-apply`、`MERGE_HEAD`、`CHERRY_PICK_HEAD`、`REVERT_HEAD`。
- [ ] 已读取 `git status --short`、`git ls-files -u`、`git reflog -8 --date=iso`。
- [ ] 已判断操作发起者；不是本会话发起的，未执行任何 abort/continue/skip。
- [ ] 已用 `git ls-files -- <TARGET>` 与 `git check-ignore` 完成目标分类。
- [ ] 只创建了 `WRITE_SET` 内的未跟踪路径。
- [ ] 共享登记面已列入延后清单，未在操作进行中写入。
- [ ] 未删除 `.git/rebase-*` 或 `index.lock`，未 `reset --hard`、`checkout --`、`clean`。
- [ ] 恢复后已重读 HEAD、CHANGELOG 版本号与两处分类计数。
- [ ] 写入前后共享文件校验和一致（除目标文件外零变化）。
- [ ] 未暂存、未提交；最终 `git status` 只出现预期的新目录。

## 11. 变更记录

- **v1.0.0** (2026-10-24): 初始版本。沉淀 2026-10-24 09:12-09:22 的 `git pull --rebase` 中断实测：rebase 停在 `projects/awesome-okf-xs` 的 gitlink 冲突（1/9），登记面回退为 11/9/v1.29；代理停止共享写入，只创建未跟踪 Skill 目录与用户级 Junction，完成脚本自检 8/8、质量门 100/100、链接门 0 断链，未 abort/continue、未提交。rebase 完成后登记面恢复为 18/16/v1.35。

## 参考

- [evidence-case.md](references/evidence-case.md)：本次事件的时间线、命令输出、回退与恢复数字、已验证步骤。
- [check_rebase_guard.js](scripts/check_rebase_guard.js)：零依赖只读探测器，支持 `--json`、`--target`、`--strict`、`--self-test`。
