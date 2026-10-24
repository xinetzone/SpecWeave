---
name: user-level-junction-acceptance
version: 1.0.0
description: "对已建好的用户级目录联接做三段验收时必须使用此技能：经联接路径跑 quick_validate 时先对既有联接技能取基线，区分仓库原生 frontmatter 的既有失败与本次引入；共享工作树中全局 git status 哈希前后不等时，改用路径级 status、mtime 与 diff 逐路径归因；Windows Python 不接受 Bash 的 /c/ 路径，统一改用 C:/ 或 Path.home()。当用户提到「联接建好了怎么验收」「quick_validate 报 Unexpected key」「git status 哈希变了」「evals 解析 FileNotFoundError」「经目标路径验证用户级技能」时必须使用。不用于创建联接本体（用 user-level-skill-junction-delivery）、四处登记（用 native-skill-surface-registration）、判断副本持久性（用 skill-junction-durability-guard）或新建用户级实体技能（用 qoder-user-skill-authoring）。"
argument-hint: "<skill-name> [--target <user-level-path>] [--repo <repo-root>]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/SKILL.md"
source: "会话 fc8b3e6f-3a94-42dd-abd4-b0e7ff7e9005 的 atomic-commit-mixed-file-split 用户级联接验收实测：quick_validate 既有基线、共享工作树哈希归因、Windows Python 路径纠错"
title: "用户级 Skill 联接验收"
x-toml-ref: "../../../.meta/toml/.agents/skills/user-level-junction-acceptance/SKILL.toml"
---

# 用户级 Skill 联接验收

联接建好只证明“路径存在”，不证明“验收通过”。本技能只回答两个问题：这条联接现在能不能用，以及失败的项是不是本次引入的。

## 1. 适用与边界

适用前提：

1. 用户级 `~/.qoder/skills/<name>` 已经存在，且是指向某个权威副本的目录联接。
2. 已知道预期目标路径与仓库根。
3. 本轮验收保持只读；内容修复需要单独授权。

| 场景 | 使用本技能 | 改用什么 |
|---|---|---|
| 联接已建好，需要出验收结论 | 是 | — |
| 创建联接本体、判断该不该建 | 否 | `user-level-skill-junction-delivery` |
| 在用户级新建实体技能 | 否 | `qoder-user-skill-authoring` |
| 同步 README/registry/CHANGELOG/TOML 四处面 | 否 | `native-skill-surface-registration` |
| 判断副本是否已入库、会不会被 `git clean` 删掉 | 否 | `skill-junction-durability-guard` |
| 推荐指令该 create 还是 register | 否 | `skill-recommendation-disk-triage` |
| 质量门掉分需要实质修复 | 否 | `skill-quality-gate-remediation` |

> **为什么**只做验收？把创建、登记、修复混进同一轮，一旦失败就无法判断是联接坏了、内容坏了，还是本轮写坏了。

## 2. 验收结论三档

| 结论 | 成立条件 | 报告口径 |
|---|---|---|
| `ACCEPTED` | 所有适用门通过，无基线例外 | 可以写“验收通过” |
| `ACCEPTED WITH KNOWN BASELINE` | `quick_validate` 失败，但同一错误类在至少两个既有联接技能中同样出现；其余门通过 | 必须写明“功能验收通过，格式门为既有基线失败，退出码 1” |
| `REJECTED` | 联接悬空或目标错误、文件不可见、出现基线中没有的新错误、链接/脚本/evals 因目标本身失败、技能目录内出现非预期写入 | 不得写“通过” |

```text
联接存在？
├─ 否 → REJECTED
└─ 是 → Target 正确？
        ├─ 否 → REJECTED
        └─ 是 → 经联接可见文件非空？
                ├─ 否 → REJECTED
                └─ 是 → quick_validate 通过？
                        ├─ 是 → 其余门通过？→ ACCEPTED / REJECTED
                        └─ 否 → 同一错误类在 ≥2 个既有联接中出现？
                                ├─ 是 → 其余门通过？→ ACCEPTED WITH KNOWN BASELINE
                                └─ 否 → REJECTED（本次引入）
```

## 3. A0 固化输入与基线

固定变量，后续命令只引用变量：

```bash
REPO="${SPECWEAVE_ROOT:-D:/spaces/SpecWeave}"
NAME="<skill-name>"
TARGET="C:/Users/<user>/.qoder/skills/$NAME"
VALIDATOR="$REPO/.agents/skills/skill-creator/scripts/quick_validate.py"
```

写盘前预检（dry-run）：确认 `TARGET` 存在、`LinkType=Junction`、`Target` 精确指向预期目录；不满足就直接判 `REJECTED`，不要继续跑后续门。

记录两个基线：

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
git -C "$REPO" status --porcelain=v1 -- ".agents/skills/$NAME"
git -C "$REPO" status --porcelain=v1
```

第一条是**路径级基线**，后面对它做前后比对；第二条只是**全局快照**，用于解释差异，不作为通过条件。

> **为什么**全局哈希不能当不变量？共享工作树里其他会话随时会改登记面；把它当验收线，每一次并行提交都会变成“本次写坏了”。

## 4. A1 联接身份与文件可见性

```powershell
Get-Item "$env:USERPROFILE\.qoder\skills\<name>" | Select-Object LinkType, Target
```

期望 `LinkType: Junction`，且 `Target` 与预期主权区目录一致。目标是实体目录时停止：本技能不删除、不替换用户已有内容。

```bash
find -L "$TARGET" -type f | sort
```

清单必须非空，并记录文件数。`find` 默认不跟随联接，不加 `-L` 会返回 0 个文件。

> **为什么**必须经目标路径？用户级路径才是 Qoder 的发现入口；源路径通过只证明内容存在，不证明联接可解析。

## 5. A2 内置格式门与基线对照

先跑目标，原样捕获退出码：

```bash
python "$VALIDATOR" "$TARGET"
echo "QUICK_VALIDATE_EXIT=$?"
```

不要接管道，不要加 `|| true`：管道会把退出码替换成最后一个命令的退出码。

再取至少两个**同根、既有、已联接**技能的基线：

```bash
for s in shared-branch-merge-push-gate native-skill-surface-registration skill-package-verification-gates; do
  echo "=== $s ==="
  python "$VALIDATOR" "C:/Users/<user>/.qoder/skills/$s"
  echo "EXIT=$?"
done
```

基线必须与目标使用同一个校验器文件、同一个用户级根；仓库源路径或任意无关技能不能充当基线。

| 观察 | 结论 | 动作 |
|---|---|---|
| 目标退出 0 | 无格式问题 | 继续 |
| 目标失败，且同一错误类在至少两个基线中同样出现 | 既有基线 | 判 `ACCEPTED WITH KNOWN BASELINE`，如实写退出码 1 |
| 目标失败，基线均通过 | 本次引入 | 判 `REJECTED`；修复需单独授权并转 `qoder-user-skill-authoring` |
| 目标失败，错误键与基线不同 | 本次引入 | 判 `REJECTED` |
| 同根可对照联接少于两个 | 无法归类 | 写 `UNCLASSIFIED`，不得声称既有基线 |

仓库原生 frontmatter（`version`、`paths`、`source`、`title`、`argument-hint`、`user-invocable`、`x-toml-ref`）在 Qoder 最小键集下预期失败；新建技能若只写最小键集却失败，则是真缺陷，不能套用基线豁免。

> **为什么**先取基线？同一个校验器对仓库原生包与用户级最小包是两把尺子；没有基线，就无法区分既有债务与本次写坏。

## 6. A3 仓库门（条件适用）

只有联接指向 SpecWeave 主权区副本时，才经目标路径跑仓库门：

```bash
PYTHONDONTWRITEBYTECODE=1 python "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$TARGET" --score --threshold 100
PYTHONDONTWRITEBYTECODE=1 python "$REPO/.agents/scripts/check-links.py" \
  --path "$TARGET" --check-frontmatter-paths
```

期望质量门 100/100、链接门 0 断链、退出码均为 0。目标若是用户级实体目录，仓库门记 `N/A`，不得写成通过。

> **为什么**要区分适用性？仓库质量门衡量仓库原生包，不衡量用户级实体技能；把 `N/A` 写成“通过”会制造假绿。

## 7. A4 脚本与 evals（Windows 路径）

正确写法：

```bash
PYTHONDONTWRITEBYTECODE=1 python "$TARGET/scripts/<script>.py" --help
PYTHONDONTWRITEBYTECODE=1 python -c "import json,pathlib; p=pathlib.Path.home().joinpath('.qoder/skills/<name>/evals/evals.json'); d=json.loads(p.read_text(encoding='utf-8')); assert d['skill_name']=='<name>'; print('EVALS_OK', len(d['evals']))"
```

错误写法：

```bash
python -c "... pathlib.Path(r'$HOME/.qoder/skills/<name>/evals/evals.json') ..."
```

Bash 把 `$HOME` 展开成 `/c/Users/...`，Windows Python 收到的是 `\c\Users\...`，于是报 `FileNotFoundError`。规则：Shell 工具（`find`、`ls`）可以继续用 `$HOME` 或 `/c/...`；只要路径进入 Python 参数，就改成 `C:/...`，或让 Python 自己用 `Path.home()` 计算。

技能没有 `scripts/` 或 `evals/` 时记 `N/A`，不要伪造通过。

> **为什么**路径错误最容易被误判成内容坏？`FileNotFoundError` 指向一个不存在的 `\c\Users`，先修路径，再判断技能内容。

## 8. A5 工作树归因（替代哈希相等）

路径级状态前后比对，这是本次交付边界的主证据：

```bash
git -C "$REPO" status --porcelain=v1 -- ".agents/skills/$NAME"
```

两次输出必须一致（例如都为 `?? .agents/skills/<name>/`，或都为空）。

全局快照只在变化时用于归因：

```bash
git -C "$REPO" status --porcelain=v1
```

若前后不同，逐路径分类：

- 变化在技能目录内：可能是本轮写入，必须检查并修复，否则判 `REJECTED`。
- 变化在技能目录外：检查 `git diff -- <path>`、文件 mtime 与内容，归因为并行会话，或标记 `UNRESOLVED`。
- mtime 只能作辅助证据，不能单独证明“谁写的”。

报告措辞：

- 允许：“本次验收未在 `<skill-dir>` 内产生写入；全局差异 N 条，路径为 …，归因为并行会话 / 未归因。”
- 禁止：全局哈希不同却写“工作树未变”。

复查运行残留：

```bash
find -L "$TARGET" \( -name '__pycache__' -o -name '*.pyc' \) -print
```

期望为空。

> **为什么**用路径级状态？全局哈希混入了所有并发会话的改动，只能解释差异，不能证明本次只读；路径级状态才对应本次交付的授权边界。

## 9. Gotchas

1. **退出码被管道吞掉**：`python quick_validate.py ... | tail` 返回的是 `tail` 的退出码；必须裸跑并立即 `echo $?`。
2. **基线选错**：基线必须是同根、既有、已联接的技能；仓库源路径或无关技能不能证明“既有”。
3. **把既有债务修成绿**：仓库原生 frontmatter 失败是既有基线；未经授权不要改写主权副本去迎合用户级最小键集。
4. **新建技能套用基线豁免**：只写最小键集的新技能若失败，是本次引入的真缺陷。
5. **全局哈希当不变量**：共享工作树中哈希变化是常态，不能作为“本次写坏”的证据。
6. **未跟踪目录只显示一行**：`git status --porcelain` 对未跟踪目录通常只显示 `?? dir/`；不要用 `-uall` 扫描大仓，改用目录前缀加 `find`。
7. **`find` 不带 `-L` 返回空**：Windows 目录联接在 Git Bash 里表现为符号链接，空结果不等于空包。
8. **`lrwxrwxrwx` 不是断链**：那是联接的正常表现；用 PowerShell 的 `LinkType`/`Target` 确认。
9. **`/c/` 路径传给 Windows Python**：Bash 可以，Python 不行；统一 `C:/...` 或 `Path.home()`。
10. **链接门相对路径**：用户级目标在仓库外，`--path` 必须给绝对路径，否则会按当前工作目录解析到别处。
11. **`__pycache__` 穿透联接**：Python 经联接运行会写回主权区；统一 `PYTHONDONTWRITEBYTECODE=1` 并在验收后复查。
12. **mtime 不是作者证据**：并行会话与文件复制都会改 mtime；必须结合路径范围与 diff 内容。
13. **`N/A` 不是通过**：不适用的门必须显式写 `N/A`，不能计入通过项。
14. **验收中顺手修内容**：修复会改变被验收对象，必须单独授权并转修复技能。

## 10. 安全检查清单（逐项确认）

- [ ] 已确认联接存在且 Target 精确指向预期目录
- [ ] 已确认 `find -L` 文件清单非空
- [ ] 已确认 quick_validate 原始退出码已记录，未被管道吞掉
- [ ] 已确认基线来自至少两个同根既有联接技能
- [ ] 已区分既有失败与本次引入，未把基线失败写成通过
- [ ] 已确认仓库门仅在主权区副本上适用，否则明确记 N/A
- [ ] 已确认脚本 `--help` 与 evals 解析实跑，未伪造通过
- [ ] 已确认 Python 路径使用 `C:/` 或 `Path.home()`，未传入 `/c/...`
- [ ] 已确认技能目录路径级 status 前后一致
- [ ] 已确认全局差异逐路径归因，未宣称“工作树未变”
- [ ] 已确认无 `__pycache__`/`.pyc` 残留
- [ ] 报告已列明未验证项与未执行项

## 11. 验收报告模板

| 项目 | 内容 |
|---|---|
| 联接 | 路径、`LinkType`、`Target` |
| 经联接可见文件 | 文件数、清单 |
| quick_validate | 原始退出码、错误类 |
| 基线对照 | 基线技能、同一错误类是否出现 |
| 仓库质量门 | 分数或 `N/A` |
| 链接门 | 断链数或 `N/A` |
| 脚本与 evals | `--help` 退出码、evals 场景数或 `N/A` |
| 路径级状态 | 前后两次输出 |
| 全局差异 | 变化路径、归因结论 |
| 最终结论 | `ACCEPTED` / `ACCEPTED WITH KNOWN BASELINE` / `REJECTED` |
| 未验证与未执行 | 基线缺失、mtime 未取证、登记/提交/推送等 |

## 12. 参考

- 已验证案例：[references/verified-case.md](references/verified-case.md)
- 行为评估场景：[evals/evals.json](evals/evals.json)
- 上下游技能：`user-level-skill-junction-delivery`、`qoder-user-skill-authoring`、`native-skill-surface-registration`、`skill-junction-durability-guard`、`skill-package-verification-gates`

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-24 | 初始版本：基于会话 `fc8b3e6f` 的联接验收实测，固化三档结论、quick_validate 基线对照、共享工作树路径级归因与 Windows Python 路径规则 |
