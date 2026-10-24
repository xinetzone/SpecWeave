---
name: git-sandbox-rehearsal
version: 1.0.0
description: 在不碰真实仓库的前提下预演多仓 git 操作，用 rev-parse --absolute-git-dir 下的嵌套仓、本地裸远端和父仓子模块重放提交、分层推送与 gitlink 前移，再用 rev-list、ls-remote、ls-tree 断言结果。当用户提到「先试跑推送」「沙箱预演」「git 演练」「验证子模块指针」「复现远端领先」「不要碰真实仓库」时，必须使用此技能。不用于真实仓库的提交推送、同文件拆分或脚本夹具测试。
argument-hint: "<repo-root> [scenario]"
user-invocable: true
paths:
  - ".agents/skills/git-sandbox-rehearsal/**"
title: "Git 多仓沙箱预演"
x-toml-ref: "../../../.meta/toml/.agents/skills/git-sandbox-rehearsal/SKILL.toml"
metadata:
  source: "会话 758291eb-74a7-4b27-b7eb-956977dcbdea 的沙箱预演实测；交叉证据见 atomic-commit-mixed-file-split"
---

# Git 多仓沙箱预演

本技能只做一件事：在真实仓库之外搭一个一次性沙箱，把「嵌套仓提交 → 嵌套仓推送 → 父仓 gitlink 更新 → 父仓推送」完整跑一遍，并用可复核的命令断言结果。它不决定业务改动怎么拆，也不代替真实仓库的提交与推送。

## 1. 这个技能解决什么

多仓操作最容易在「看起来成功」的地方出错：远端没收到、父仓 gitlink 指向未推送的提交、断言读到的是 fetch 前的旧引用。这些问题一旦发生在真实仓库，修复成本远高于预演。

预演要回答三个问题：

| 问题 | 断言手段 |
|---|---|
| 被测流程会不会在中间步骤失败 | 逐步执行并保留每步退出码 |
| 推送后远端是否真的等于本地 HEAD | `ls-remote` 与本地 `rev-parse` 比较 |
| 父仓 gitlink 是否等于嵌套仓远端 head | `ls-tree origin/main <path>` 与嵌套 HEAD 比较 |

> **为什么？** 只跑一遍「命令没报错」不构成验证。没有断言时，`0 0` 这种 fetch 前的陈旧计数会被误读成「可安全推送」，这正是本技能要防的假绿。

## 2. 适用与不适用

### 2.1 决策：用沙箱还是直接操作

```text
需要写远端 / 改 gitlink / 试跑多步流程？
├─ 是，且用户明确要求在真实仓库执行
│   └─ 不在本技能范围：转 scoped-submodule-commit 或 shared-branch-merge-push-gate
├─ 是，但需求是「先验证流程能不能成」
│   └─ 用本技能：搭沙箱重放，输出断言结果
└─ 只读检查真实仓库现状
    └─ 直接 git -C <repo> status/log/ls-tree，不需要沙箱
```

### 2.2 移交边界

| 任务 | 交给 |
|---|---|
| 真实仓库的两级提交与 gitlink 前移 | `scoped-submodule-commit` |
| 共享分支的推送门与并发保护 | `shared-branch-merge-push-gate` |
| 同一文件两类改动的非交互拆分 | `atomic-commit-mixed-file-split` |
| 共享工作树中隔离他人改动 | `scoped-commit-shared-worktree` |
| 随包脚本的夹具与负向测试 | `skill-bundled-script-validation` |

**不适用**：单仓普通命令、需要联网或真实凭据的推送、需要复刻真实仓库历史规模的性能测试。

## 3. 输入与前置

| 输入 | 说明 |
|---|---|
| `REAL` | 真实仓库绝对路径，仅用于解析 git 目录，不写入 |
| 被测流程 | 要预演的命令序列，或要验证的脚本 |
| 断言清单 | 每步的期望输出与退出码 |

前置检查：

```bash
export GIT_TERMINAL_PROMPT=0
REAL="<绝对路径>"
GITDIR="$(git -C "$REAL" rev-parse --absolute-git-dir)" || { echo "NOT_A_GIT_REPO"; exit 2; }
git -C "$REAL" rev-parse --is-inside-work-tree
git --version
```

> **为什么用 `--absolute-git-dir`？** 子模块的 `.git` 是文件而不是目录，直接拼 `$REAL/.git` 在子模块里必然失败。该命令对普通仓库返回 `.git` 目录，对子模块返回其真实 git 目录，两种情况都能安全落盘。

## 4. 沙箱布局与硬规则

```text
$GITDIR/git-sandbox-<YYYYmmdd-HHMMSS>/
├── nested/              # 嵌套仓（模拟子模块源）
├── remote.git/          # 嵌套仓的本地裸远端
├── parent/              # 父仓，含 submodule
└── parent-remote.git/   # 父仓的本地裸远端
```

硬规则：

1. `ROOT` 必须在 `$GITDIR` 下且带 `git-sandbox-` 前缀；已存在就中止并换时间戳，绝不复用旧沙箱。
2. 所有命令用 `git -C <绝对路径>`，不依赖 shell 当前目录。
3. 远端只允许本地路径或 `file://`，禁止配置任何真实远端 URL。
4. 只改沙箱内仓库的本地配置（`user.*`、`core.autocrlf`），禁止 `git config --global`。
5. 推送只发生在沙箱仓与其本地裸远端之间。
6. 清理只删除本次创建的 `ROOT`，删除前用 case 模式校验前缀。

> **为什么放在 git 目录而不是 `/tmp`？** Git Bash 的 `/tmp` 与 Windows Python 看到的临时目录不是同一命名空间，把 shell 的临时路径交给另一个运行时会出现「文件不存在」；放在 git 目录下所有运行时都能访问，且不进入工作树、不出现在 `git status` 里。代价是：残留沙箱不会自己暴露，必须在收尾显式列出并删除。

## 5. 建仓

```bash
ROOT="$GITDIR/git-sandbox-$(date +%Y%m%d-%H%M%S)"
test -e "$ROOT" && { echo "SANDBOX_EXISTS: $ROOT"; exit 2; }
NESTED="$ROOT/nested"; BARE="$ROOT/remote.git"; PARENT="$ROOT/parent"

mkdir -p "$NESTED" "$PARENT"
git -C "$NESTED" init -q -b main
git -C "$NESTED" config user.email sandbox@example.invalid
git -C "$NESTED" config user.name "Sandbox Bot"
git -C "$NESTED" config core.autocrlf false
printf 'v1\n' > "$NESTED/data.txt"
git -C "$NESTED" add data.txt
git -C "$NESTED" commit -q -m "baseline"

git init -q --bare "$BARE"
git -C "$NESTED" remote add origin "$BARE"
git -C "$NESTED" push -q -u origin main
```

断言：`rev-parse --is-inside-work-tree` 为 `true`，`rev-list --count HEAD` 为 `1`，`ls-remote origin refs/heads/main` 等于 `rev-parse HEAD`。

> **为什么在沙箱里也设置 `user.*` 和 `core.autocrlf`？** 全局身份不一定存在，autocrlf 会让文件字节随平台变化，从而让「diff 只含预期行」这类断言产生噪声。沙箱内本地化这两个配置，断言才可复现。

## 6. 复现父仓 gitlink

```bash
git -C "$PARENT" init -q -b main
git -C "$PARENT" config user.email sandbox@example.invalid
git -C "$PARENT" config user.name "Sandbox Bot"
git -C "$PARENT" config core.autocrlf false

git -C "$PARENT" -c protocol.file.allow=always \
  submodule add "$BARE" libs/nested

git -C "$PARENT" add .gitmodules libs/nested
git -C "$PARENT" commit -q -m "baseline with submodule"
```

断言：

```bash
git -C "$PARENT" ls-tree HEAD libs/nested          # 行首必须是 160000 commit <sha>
git -C "$PARENT" config -f .gitmodules --get submodule.libs/nested.url
```

> **为什么必须显式带 `-c protocol.file.allow=always`？** 默认策略 `protocol.file.allow=user` 下，Git 拒绝子模块使用本地传输，报 `fatal: transport 'file' not allowed`，普通路径和 `file://` 都会中招。有些机器在全局配置里已经设成 `always`，会让预演「碰巧能跑」，换台机器就失败；把参数写进命令而不是依赖全局配置，预演才可移植。该参数只对这一条命令生效，不要改成全局。

## 7. 执行被测流程

在沙箱里按真实流程逐步执行，每步保留原始输出与退出码。至少覆盖：

1. 嵌套仓产生一个待推送提交。
2. 推送前门禁：`fetch` 后 `rev-list --left-right --count HEAD...origin/main`。
3. 推送嵌套仓。
4. 更新父仓 gitlink。
5. 推送父仓。
6. 读回远端指针。

失败的步骤不要跳过。预演的价值就在失败现场：记录命令、完整报错、退出码，再决定是流程问题还是环境问题。

> **为什么不在沙箱里「修到能跑」就结束？** 预演的目标是暴露真实流程在目标环境中的行为。为了让沙箱跑通而临时改参数，会把坑留给真实执行。先记录失败，再判断是否属于被测流程本身。

## 8. 断言清单

| 检查 | 命令 | 通过条件 |
|---|---|---|
| 沙箱位置 | `case "$ROOT" in "$GITDIR"/git-sandbox-*)` | 命中前缀 |
| 嵌套仓待推送 | `git -C "$NESTED" fetch -q origin && git -C "$NESTED" rev-list --left-right --count HEAD...origin/main` | `1<TAB>0` |
| 嵌套远端已更新 | `git -C "$NESTED" ls-remote origin refs/heads/main` | 等于本地 `HEAD` |
| 父仓 gitlink | `git -C "$PARENT" ls-tree HEAD libs/nested` | `160000 commit <嵌套 HEAD>` |
| 父仓远端 gitlink | `git -C "$PARENT" fetch -q origin && git -C "$PARENT" ls-tree origin/main libs/nested` | 等于嵌套仓远端 head |
| 远端领先 | 第二个克隆推一条后 `fetch` 再计数 | `0<TAB>1` |
| 落后时推送 | `git -C "$NESTED" push origin HEAD:main` | 非零退出、`non-fast-forward` |

`rev-list --left-right --count HEAD...origin/main` 的两个字段是「本地领先」与「本地落后」：

| 输出 | 含义 | 动作 |
|---|---|---|
| `N<TAB>0` | 只领先 | 可推送（仍需用户授权） |
| `0<TAB>0` | 看起来同步 | 先确认刚执行过 `fetch`，否则是陈旧读数 |
| `0<TAB>N` | 落后 | 停止，先同步 |
| `N<TAB>M` | 分叉 | 停止，交用户决定 |

> **为什么 `0 0` 可能是假安全？** 该命令读的是本地 `origin/main` 引用，不会联网。另一个克隆推送后若不 `fetch`，本地仍显示 `0 0`，此时推送会被远端拒绝。预演里应刻意构造一次这种情形，确认被测流程能识别。

## 9. 更新 gitlink 的正确方式

父仓记录的 gitlink 是「子模块工作副本的当前 HEAD」，不是子模块远端的 head。嵌套仓推送新提交后，父仓里那份子模块克隆仍然是旧 HEAD，直接 `git add libs/nested` 会显示 `nothing to commit`。

```bash
NESTED_HEAD="$(git -C "$NESTED" rev-parse HEAD)"
git -C "$PARENT/libs/nested" fetch -q origin
git -C "$PARENT/libs/nested" checkout -q "$NESTED_HEAD"
git -C "$PARENT" add libs/nested
git -C "$PARENT" commit -m "advance gitlink"
```

> **为什么不能只 `git add`？** 子模块的路径暂存的是其工作副本 HEAD。工作副本没动，暂存的自然还是旧指针；只有 fetch + checkout 之后，父仓才可能记录新 SHA。遇到「nothing to commit」先检查子模块副本的 HEAD，不要怀疑 `git add` 写错了。

## 10. 远端领先与推送门

```bash
git clone -q "$BARE" "$ROOT/second"
git -C "$ROOT/second" config user.email sandbox@example.invalid
git -C "$ROOT/second" config user.name "Sandbox Bot"
# 在 second 里提交并推送

# 不 fetch：计数可能仍是 0 0（陈旧）
git -C "$NESTED" rev-list --left-right --count HEAD...origin/main

git -C "$NESTED" fetch -q origin
git -C "$NESTED" rev-list --left-right --count HEAD...origin/main   # 期望 0 1
```

被测流程必须在发现 `0 N` 或 `N M` 时停止。预演中实际执行一次落后推送，确认远端拒绝并且被测流程能把这个非零退出正确上报。

## 11. 清理与不污染核验

```bash
case "$ROOT" in
  "$GITDIR"/git-sandbox-*) rm -rf "$ROOT" ;;
  *) echo "REFUSE: $ROOT"; exit 2 ;;
esac
test -e "$ROOT" && echo "STILL_EXISTS" || echo "REMOVED"
```

再核对：

- 沙箱路径已不存在；
- 全程对真实仓库只执行过 `rev-parse` / `status` / `ls-tree` 等只读命令；
- 没有向真实仓库写入文件、修改配置或推送。

> **为什么不能拿真实仓库 HEAD 是否变化当唯一判据？** 共享工作树里其他会话可能同时提交，HEAD 会合法地移动。判断「是否污染」要看自己执行过的命令与写入路径，而不是全局 HEAD 快照。对比 HEAD 只能作为辅助信号，差异要先归因再结论。

## 12. 失败处理矩阵

| 现象 | 原因 | 处置 |
|---|---|---|
| `fatal: transport 'file' not allowed` | 子模块本地传输被默认策略禁止 | 仅对 `submodule add` 加 `-c protocol.file.allow=always` |
| `not a git repository` | shell cwd 在工具调用间被重置 | 全部改成 `git -C <绝对路径>` |
| 跨运行时「文件不存在」 | Git Bash `/tmp` 与 Windows Python 临时目录不一致 | 把临时产物放到 `--absolute-git-dir` 下 |
| `git add` 后 `nothing to commit` | 子模块副本 HEAD 未更新 | 先 `fetch` + `checkout` 目标 SHA，再 `add` |
| `ls-tree origin/main` 查不到或结果陈旧 | 未 fetch，读的是旧引用 | 先 `fetch`，再断言 |
| `rev-list` 显示 `0 0` 但 push 被拒 | 陈旧读数 | fetch 后复核，按 `0 N` 处理 |
| `'libs/nested' already exists in the index` | 同一次沙箱里重复 `submodule add` | 换新沙箱，不要用强制参数覆盖 |
| `warning: LF will be replaced by CRLF` | 全局 autocrlf 生效 | 沙箱内设 `core.autocrlf false`，或在报告中标注为噪声 |
| 推送被拒 `non-fast-forward` | 远端已领先 | 停止并报告，禁止 `--force` |

## 13. Gotchas

1. `/tmp` 跨运行时不一致：Git Bash 与 Windows Python 看到的临时目录不同。
2. Bash 每次调用的 cwd 可能重置，相对路径会落到别处。
3. 子模块的 `.git` 是文件，`$REPO/.git` 不是目录。
4. `protocol.file.allow` 默认是 `user`，本地子模块克隆会被拒绝；宿主机全局设为 `always` 会掩盖这一点。
5. `git add <submodule>` 不会搬运 gitlink，搬运的是子模块工作副本 HEAD。
6. `rev-list` 与 `ls-tree` 都只读本地引用，不 fetch 就可能读到旧值。
7. 首次推送前 `origin/main` 不存在，`rev-parse --verify` 失败是正常状态，不是错误。
8. `rev-list --left-right --count HEAD...origin/main` 输出顺序是「领先在前、落后在后」。
9. 重复 `submodule add` 返回 128；换沙箱，不要强制覆盖。
10. 共享工作树的 HEAD 可能被其他会话推进，不要把自己的只读预演误判为污染源。
11. 沙箱在 `.git` 下，不会出现在 `git status` 里，残留只能靠显式路径检查发现。
12. 远端领先要用第二个克隆制造；在同一个克隆里改本地分支造不出「远端领先」。

## 14. 安全检查清单

- [ ] `ROOT` 位于 `$GITDIR` 下且带 `git-sandbox-` 前缀，创建前确认不存在。
- [ ] 真实仓库只执行过只读命令，未写入、未改配置、未推送。
- [ ] 所有远端都是本地路径或 `file://`，没有真实 URL。
- [ ] `protocol.file.allow=always` 只出现在 `submodule add` 这一条命令上。
- [ ] 没有修改任何 `--global` 配置。
- [ ] 推送前执行过 `fetch` 与 `rev-list`，并正确解释 `N 0` / `0 N` / `N M`。
- [ ] 父仓 gitlink 断言发生在 `fetch` 之后，且与嵌套仓远端 head 一致。
- [ ] 落后推送用例已实际执行，并确认返回非零。
- [ ] 清理用前缀校验的 `rm -rf`，并复核沙箱路径已不存在。
- [ ] 报告里区分「实际输出」与「未验证项」，没有用「命令没报错」代替断言。

## 15. 参考

- [沙箱执行手册（可复制命令与实测数值）](references/sandbox-runbook.md)
- [取证、实测与未验证项](references/verified-case.md)
- 相关技能：`atomic-commit-mixed-file-split`、`scoped-submodule-commit`、`shared-branch-merge-push-gate`
