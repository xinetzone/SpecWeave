# 已验证案例：atomic-commit-mixed-file-split 的用户级联接验收

> 来源：会话 `fc8b3e6f-3a94-42dd-abd4-b0e7ff7e9005`。本文只记录该会话里可复现的原始输出与由输出直接得出的结论；凡是原文未出现的推断，均在文中标注为“未独立验证”。

## 1. 场景

该会话用 `user-level-skill-junction-delivery` 把主权区 `.agents/skills/atomic-commit-mixed-file-split` 以目录联接暴露到 `~/.qoder/skills/atomic-commit-mixed-file-split`，然后按该技能的六项验收执行。三项验收步骤在实测中失效或产生误导，需要临时补规则：

| 步骤 | 原技能要求 | 实测结果 | 需要补的规则 |
|---|---|---|---|
| 内置格式门 | 未覆盖 | `quick_validate.py` 退出 1 | 先取同根既有联接基线，再定性 |
| evals 解析 | 给出一条 Python 单行命令 | `FileNotFoundError` 指向 `\c\Users\...` | 路径进入 Python 前改成 `C:/` 或 `Path.home()` |
| 只读证明 | 全局 `git status` 哈希前后一致 | 哈希由 `99684c18…` 变为 `29d728c3…` | 改用路径级 status；全局差异逐路径归因 |

## 2. quick_validate 的原始失败

目标路径按用户级根执行，命令与输出（错误键按字典序排列）：

```text
$ python .../skill-creator/scripts/quick_validate.py C:/Users/xinzo/.qoder/skills/atomic-commit-mixed-file-split
Unexpected key(s) in SKILL.md frontmatter: argument-hint, paths, source, title, user-invocable, version
QUICK_VALIDATE_EXIT=1
```

该技能使用仓库原生 frontmatter，而 `quick_validate.py` 只允许 `name`、`description`、`license`、`allowed-tools`、`metadata`、`compatibility`。两者是不同的契约，不是内容缺陷。

### 2.1 基线对照

对同根、既有、已联接的三个技能跑同一个校验器，实测全部退出 1，错误类相同：

| 基线技能 | 触发的非法顶层键 | 退出码 |
|---|---|---|
| `shared-branch-merge-push-gate` | `argument-hint`, `disable-model-invocation`, `paths`, `source`, `title`, `user-invocable`, `version`, `x-toml-ref` | 1 |
| `native-skill-surface-registration` | `argument-hint`, `disable-model-invocation`, `paths`, `source`, `user-invocable`, `version` | 1 |
| `skill-package-verification-gates` | `argument-hint`, `disable-model-invocation`, `paths`, `source`, `title`, `user-invocable`, `version` | 1 |

结论：目标失败属既有基线，验收结论为 `ACCEPTED WITH KNOWN BASELINE`，报告必须写明退出码 1。

需要注意的执行细节：会话中某些基线命令在包装后打印了 `EXIT=0`，而裸跑同一命令得到退出码 1。判定只能取裸跑后的 `$?`，不得通过管道或 `|| true` 观察。

## 3. evals 解析的路径失败

原始失败：

```text
FileNotFoundError: [Errno 2] No such file or directory:
'\\c\\Users\\xinzo\\.qoder\\skills\\atomic-commit-mixed-file-split\\evals\\evals.json'
```

原因：Bash 把 `$HOME` 展开为 `/c/Users/xinzo`，该字符串交给 Windows Python 后变成 `\c\Users\xinzo`，盘符位置缺失。改用 `C:/...` 或 `Path.home()` 后：

```text
EVALS_OK 4
EVALS_EXIT=0
```

该技能 `evals/evals.json` 含 4 个场景。此项失败是路径表示错误，与技能包内容无关。

## 4. git status 哈希与路径级归因

| 时点 | 全局 `git status --porcelain=v1 -z` 的 sha256 |
|---|---|
| 创建联接前 | `99684c1830fe8cf85ca94e0bd0d2fde0fe26fa214ebb01173cfee63261608378` |
| 验收后 | `29d728c3152e4a016f9e1b6776a15f837c62524ad19a6e1b711f66a6aaf3fa75` |

同一时段内，本技能目录的路径级状态始终是：

```text
?? .agents/skills/atomic-commit-mixed-file-split/
```

而全局快照中新增/变化的路径来自并行会话的登记面：

```text
.agents/capability-registry/02-skills.md
.agents/skills/CHANGELOG.md
.agents/skills/README.md
```

以及另一个技能 `skill-junction-durability-guard` 的新增目录。

由此得出可复用判据：

1. 路径级状态前后一致，才是“本次验收未在授权范围内写入”的证据。
2. 全局哈希不等不是失败信号；它是共享工作树里并行会话的正常表现。
3. 全局差异要逐路径用 `git status`、`git diff -- <path>` 与内容判断归因；mtime 只能作辅助。

### 4.1 证据边界

来源报告的 `rationale` 提到并行会话在“12:15–12:17”修改登记面。原始工具输出里没有出现该时间戳；复测时登记面文件的 mtime 为 12:21–12:28。因此：

- **已独立验证**：全局哈希变化、路径级状态不变、变化的路径清单。
- **未独立验证**：`12:15–12:17` 这个精确时间段。引用时应写“并行会话期间”，不要复述精确到分钟的时间。

## 5. 该案例的验收结论

| 门 | 结果 | 结论 |
|---|---|---|
| 联接身份 | `LinkType: Junction`，Target 指向主权区同名目录 | 通过 |
| 经联接可见文件 | `find -L` 非空 | 通过 |
| quick_validate | 退出码 1，同一错误类在三个基线技能中出现 | 既有基线 |
| 仓库质量门（目标路径） | 100/100，退出码 0 | 通过 |
| 链接门（目标路径） | 仅 `x-toml-ref` 一项失败（字段从用户级根向上解析落到仓库外），本地引用 0 断链 | 已知边界 |
| evals | 修正路径后 4 个场景可解析 | 通过 |
| 路径级 status | 前后一致 | 通过 |
| 全局哈希 | 变化，已逐路径归因 | 不作为通过条件 |

最终结论：`ACCEPTED WITH KNOWN BASELINE`。此处的“已知边界”必须在报告中单列，不能被并入“通过”。

## 6. 复跑顺序（本案例实际顺序）

1. `Get-Item` 确认 `LinkType` 与 `Target`。
2. `find -L` 枚举文件，确认非空。
3. 裸跑 `quick_validate.py`，记录退出码。
4. 对两个及以上同根既有联接取基线，比较错误类。
5. 经目标路径跑仓库质量门与链接门（仅主权区副本适用）。
6. 用 `C:/` 或 `Path.home()` 解析 evals。
7. 比对路径级 status，逐路径归因全局差异。
8. 复查 `__pycache__`/`*.pyc`。

## 7. 复现要点

- 所有命令都经用户级目标路径执行，不对主权区源路径复跑后代替。
- Python 相关步骤统一加 `PYTHONDONTWRITEBYTECODE=1`。
- 基线技能必须同根、既有、已联接；用仓库源路径当基线会混淆两套契约。
- 判定结论必须落到三档之一，并显式写出退出码与未验证项。
