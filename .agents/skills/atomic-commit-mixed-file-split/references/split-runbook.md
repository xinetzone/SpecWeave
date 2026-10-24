# 拆分执行手册与实测记录

本文件给出可直接复制的命令序列，并记录 2026-10-24 在临时仓库中的完整实测。命令中的占位符按第 3 节替换。

## 1. 一次性变量

```bash
REPO="D:/path/to/repo"          # 必须是绝对路径
FILE="pyproject.toml"           # 相对 REPO
MSG_A="refactor(license): 许可元数据统一为 SPDX 表达式"
MSG_B="build(deps): 构建下限提升至 scikit-build-core>=0.11"
SPLIT="D:/spaces/SpecWeave/.agents/skills/atomic-commit-mixed-file-split/scripts/split_state.py"
GITDIR="$(git -C "$REPO" rev-parse --absolute-git-dir)"
BACKUP="$GITDIR/atomic-split/$(date +%Y%m%d-%H%M%S)/$(basename "$FILE")"
```

`GITDIR` 对普通仓库是 `.git` 目录，对子模块是 `.git` 文件指向的真实 git 目录。备份必须放在这里：Git Bash 与 Windows Python 对 `/tmp` 的解析不同，跨运行时传临时路径会出现「文件不存在」。

## 2. 六步序列

```bash
# 1 只读快照
git -C "$REPO" status --porcelain=v1 -- "$FILE"
git -C "$REPO" diff -- "$FILE"

# 2 备份终态
python "$SPLIT" backup --repo "$REPO" --file "$FILE" --backup "$BACKUP"

# 3 先试算 B 的替换次数（零写入）
python "$SPLIT" revert --repo "$REPO" --file "$FILE" --dry-run \
  --pair "scikit-build-core>=0.11|||scikit-build-core>=0.10|||3" \
  --pair "minimum-version = \"0.11\"|||minimum-version = \"0.10\"|||1"

# 4 构造只含 A 的中间态
python "$SPLIT" revert --repo "$REPO" --file "$FILE" \
  --pair "scikit-build-core>=0.11|||scikit-build-core>=0.10|||3" \
  --pair "minimum-version = \"0.11\"|||minimum-version = \"0.10\"|||1"
git -C "$REPO" diff --stat -- "$FILE"
if git -C "$REPO" diff -- "$FILE" | grep -qF "scikit-build-core>=0.11"; then
  echo "FAIL: B 泄漏"; else echo "PASS: 只含 A"; fi

# 5 提交 A
git -C "$REPO" add -- "$FILE"
git -C "$REPO" diff --cached --name-status
git -C "$REPO" commit -m "$MSG_A"

# 6 还原终态并提交 B
python "$SPLIT" restore --repo "$REPO" --file "$FILE" --backup "$BACKUP"
git -C "$REPO" diff -- "$FILE"
git -C "$REPO" add -- "$FILE"
git -C "$REPO" diff --cached --name-status
git -C "$REPO" commit -m "$MSG_B"
git -C "$REPO" status --porcelain=v1 -- "$FILE"
```

## 3. 实测记录（可复跑）

环境：Windows 10，Python 3.14，`core.autocrlf=true`；临时仓库位于 `D:/spaces/SpecWeave/.git/atomic-split-rehearsal-20261024-114136`。

基线文件同时含两类改动：许可从 `{file = "LICENSE"}` 改为 SPDX 字符串并删掉 `License ::` classifier；构建下限 `0.10 → 0.11`（3 处依赖串加 1 处 `minimum-version`）。

| 步骤 | 命令 | 实测结果 | 退出码 |
|---|---|---|---|
| 备份 | `split_state.py backup` | sha256 `0b8d4f46256609f3de92462e4d03ae34fed739e4feb7ea6cf05c3cccbed81b2c` | 0 |
| 试算 | `split_state.py revert --dry-run` | 两对替换 count 分别为 3 与 1 | 0 |
| 构造 | `split_state.py revert` | 写入中间态，返回两对替换计数 | 0 |
| 验证 A | `git diff` + `grep -qF "scikit-build-core>=0.11"` | `PASS: A-only`；stat `2 insertions(+), 2 deletions(-)` | — |
| 提交 A | `git commit -m "$MSG_A"` | `033ce42`，仅 `pyproject.toml` | 0 |
| 还原 | `split_state.py restore` | sha256 与备份一致 | 0 |
| 验证 B | `git diff` + `grep -qF 'license = {file = "LICENSE"}'` | `PASS: B-only`；stat `4 insertions(+), 4 deletions(-)` | — |
| 提交 B | `git commit -m "$MSG_B"` | `eacbd94`，仅 `pyproject.toml` | 0 |
| 收尾 | `git status --porcelain -- "$FILE"` | 0 行 | — |

负向用例：

| 用例 | 输入 | 实测输出 | 退出码 | 文件是否被改 |
|---|---|---|---|---|
| 次数不符 | `--pair "...>=0.11\|\|\|...>=0.10\|\|\|99"` | `"actual": 3, "written": false` | 3 | 否（前后 sha256 相同） |
| 目标不存在 | `--file nope.toml` | `不是可读文件` | 2 | 否 |
| 替换对缺段 | `--pair "a\|\|\|b"` | `--pair 需要三段` | 2 | 否 |
| 备份被篡改 | 覆写 `.sha256` 后 `restore` | `backup-hash-mismatch` | 4 | 否 |

分层推送（本地裸仓，无网络）：

| 检查 | 命令 | 实测 |
|---|---|---|
| 推送前分歧 | `git rev-list --left-right --count HEAD...origin/main` | 首次 `no-upstream`，推送后 `0	0` |
| 远端提交 | `git ls-remote origin refs/heads/main` | `eacbd94a5b0f7035d02d421fad04475ab7896570`，与本地 HEAD 相同 |
| 父仓 gitlink | `git ls-tree origin/main projects/nested` | `eacbd94a…`，与嵌套 HEAD 相同 |
| 落后检测 | 另一克隆推一个提交后 `fetch` 再比 | `0	1`，应停止推送 |

## 4. 替换对的构造方法

对每一类改动，从 `git diff` 逐 hunk 抄出「终态文本 → A 阶段文本」：

```text
--pair "<终态里出现的文本>|||<A 阶段应出现的文本>|||<终态中精确出现次数>"
```

规则：

1. 只取单行文本；跨行结构改写不适用本技能。
2. 存在包含关系时先替换更长的串（例如先 `minimum-version = "0.11"` 再 `"0.11"`），避免短串吃掉长串的一部分。
3. 整行删除把换行写成字面 `\n`，如 `--pair "old line\n|||\n|||1"`。
4. 次数取 `git diff` 中该串的新增行数，不凭印象；`--dry-run` 的结果与之一致才继续。
5. 替换文本里不要出现 `|||`；出现时缩小替换粒度。

## 5. 两个提交的顺序

顺序不是审美问题，而是可回滚性问题：

- 无依赖：按用户指定顺序。
- A 依赖 B（新写法只有在新下限下才被接受）：先确认用户接受「A 先提交、B 紧随其后，推送前不留中间态」；否则先提交 B。
- 无论哪种顺序，推送应在两个提交都完成且本地检查通过之后进行，避免远端出现半成品状态。

## 6. 清理

备份目录在 git 目录内，不进入版本控制。确认两次提交都成功、工作树目标文件为空后删除：

```bash
rm -rf "$GITDIR/atomic-split/<timestamp>"
```

删除前先打印路径并确认它在 `$GITDIR` 下；不要删除 git 目录里的其他内容。
