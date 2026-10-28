---
name: windows-temp-fixture-teardown-safety
version: 1.0.0
description: 在 Windows 与 Git Bash 下搭建一次性夹具时，用单个 Python 进程内的 tempfile.mkdtemp 建、断言、shutil.rmtree 清理，禁止把 cygpath、sed 或变量替换得到的路径交给 rm -rf，删除前必须打印并断言解析后的绝对路径前缀与层级深度。必须使用此技能：当用户要建临时夹具、跑受控删除验证、清理探针目录，或清理命令里出现变量拼接路径时。不用于误删后的影响面取证（用 windows-deletion-blast-radius-attribution）、Git 多仓沙箱预演（用 git-sandbox-rehearsal）或 Skill 包验收（用 skill-package-verification-gates）。
argument-hint: "<fixture-purpose>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/windows-temp-fixture-teardown-safety/**"
title: "Windows 临时夹具建测清安全约束"
x-toml-ref: "../../../.meta/toml/.agents/skills/windows-temp-fixture-teardown-safety/SKILL.toml"
source: "来源会话 0fc0150f-e330-487f-82dd-b70ab8532806（sed 变量退化使 rm -rf 作用于 C 盘根的事故，与同会话内单命令夹具成功对照）"
---

# Windows 临时夹具建测清安全约束

本技能只回答一件事：在 Windows 与 Git Bash 下搭一次性夹具（临时目录 + 探针文件 + 断言 + 清理）时，**怎么保证清理范围永远等于你刚建的那个目录**。它不负责误删后的取证，也不负责 git 沙箱预演。

## 1. 这个技能解决什么

事故链条短得可怕：一条清理命令里叠了三层路径转换。

```bash
T="$(cygpath -w "$(mktemp -d)")"
root="$(echo "$T" | sed 's|\\|/|g')"      # 报错：unknown option to `s'
rootu="/c/${root#C:/}"                     # 报错后 root 为空 → rootu=/c
rm -rf "$rootu"                            # 实际作用于 C:\ 根
```

`sed` 失败不中断（没有 `set -e`，也没检查 `$?`），变量塌成 `/c`，`rm -rf` 把盘根当成夹具清理。已确认删除 `C:\$SysReset` 与 `C:\OneDriveTemp`；成功删除不打印任何日志，范围只能靠事故前后的清单差异反推。

> **为什么这件事与具体任务无关？** 任何「建临时目录 → 跑断言 → 删除」的夹具都走同一条路径转换链：`mktemp` 给 `/tmp` 风格路径，Windows 工具要 `C:\` 风格路径，中间再加一段变量裁剪。三层里任一层静默失败，删除范围就放大一级。换成别的任务，同一条链会原样重演。

> **为什么删除前打印路径还不够？** 事故命令的输出里确实打印过 `T=...`，但没有人也没有断言去检查 `rootu` 最终等于什么。打印是给人看的，断言才能中断执行。

## 2. 适用与不适用

### 2.1 选择夹具的托管方式

```text
需要一次性夹具？
├─ 只需 建 / 测 / 清，无 GUI 交互
│   └─ 单进程 Python：tempfile.mkdtemp + finally shutil.rmtree（默认选择）
├─ 需要 Git Bash 命令参与（ls、find、被测脚本）
│   └─ 仍由 Python 起 subprocess，路径走参数列表，不拼 shell 字符串
└─ 清理只能在 shell 里做
    └─ 先跑 §4 的 guard 断言，再在同一命令内 rm -rf -- "$target"
```

### 2.2 不适用

| 任务 | 交给 |
|---|---|
| 已经误删，要定性影响面 | `windows-deletion-blast-radius-attribution` |
| 多仓 git 操作的沙箱预演 | `git-sandbox-rehearsal` |
| Skill 自带脚本的正负用例设计 | `skill-bundled-script-validation` |
| Skill 包的最终验收 | `skill-package-verification-gates` |

## 3. 五条硬规则（写前预检）

R1 **单进程闭环**：建、测、清在同一个 Python 进程内完成，用 `tempfile.TemporaryDirectory`，或 `mkdtemp` 加 `finally`。
R2 **不做多级路径转换**：`cygpath` + `sed` + `${var#prefix}` 叠加禁止；需要转换时只做一次，判定交给 `pathlib`。
R3 **删除前断言**：`resolve()` 之后同时满足「位于 `tempfile.gettempdir()` 之下」「相对深度 ≥ 1（`%TEMP%` 的直接子目录就是合法夹具根）」「顶层目录名带夹具前缀」；任一不满足就 `raise`，不 `continue`。
R4 **不把变量喂给 `rm -rf`**：Python 侧不调 `subprocess` 删目录；确需 shell 时只传已经过 R3 的绝对路径，并加 `--`。
R5 **清理失败不掩盖原错误**：`finally` 内清理，清理异常单独记录；链接/联接只删本体，不递归。

> **为什么深度阈值只能取 1，却仍拦得住盘根？** 事故里塌掉的 `/c` 并不是空串，`[ -z "$x" ]` 一类检查拦不住它；但 `mkdtemp` 建的夹具根就落在 `%TEMP%` 下一级，把阈值写成 2 会把**所有合法夹具**拒掉（本技能自测当场暴露过这个错误）。真正拦住 `/c`、`C:/Users`、`Temp` 自身的是「必须严格位于 `%TEMP%` 之下」加「顶层目录名以 `sw-fixture-` 开头」这两条，深度只负责排除「等于 temp 根」。需要更严格时可显式传 `--min-depth 2`。

> **为什么链接与实体目录要分开删？** `shutil.rmtree` 对链接本体会直接拒绝，`rm -rf` 却会沿链接删到目标内容；两种工具在这一点上相反，只有先判类型再选删除方式才不会删错对象。

## 4. 标准模板

随包脚本 `scripts/temp_fixture_guard.py` 提供断言与夹具上下文：

```bash
python scripts/temp_fixture_guard.py --selftest
python scripts/temp_fixture_guard.py --check "C:/Users/<user>/AppData/Local/Temp/sw-fixture-abc123"
```

退出码契约：`0` 放行或自测通过，`1` 自测失败，`2` 参数错误，`3` 断言拒绝。拒绝时打印 `REFUSE reason=... path=... depth=... root=...`。

不需要 guard 时的最小内联写法：

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="sw-fixture-") as td:
    root = Path(td)
    (root / "realdir").mkdir()
    (root / "realfile").write_text("x", encoding="utf-8")
    assert root.is_dir()
# 出作用域即清理，不需要任何 rm
```

> **为什么 `TemporaryDirectory` 比手写 `rm -rf` 更安全？** 它在解释器内部持有绝对路径对象，不经过 shell 词法，也就不存在「变量退化」这一层；清理失败时它在 `__exit__` 里重试并报错，而不是静默成功。

## 5. 路径交给外部工具时的规则

1. 一次转换：Python 里用 `str(Path)`，不在同一条命令里再做 `sed` 回改。
2. 检查退出码：shell 加 `set -euo pipefail`；Python 用 `subprocess.run(..., check=True)`。
3. 参数列表而非字符串拼接：`subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)])`。
4. Git Bash 的 `/c/...` 不能直接喂给 Windows Python；用 `C:/...` 或 `Path.home()`。
5. 执行前打印 `ALLOW path=... depth=... root=...`，把判定结果留在输出里。

> **为什么参数列表能挡住一类事故？** 字符串拼接时，路径里的空格、引号、`$` 会被 shell 重新解释；参数列表把这些字符原样交付，退化只可能来自代码逻辑，不会来自词法层。

## 6. 坏味道扫描

```bash
grep -rn --include='*.sh' --include='*.md' -e 'rm -rf "\$' . | grep -e 'sed ' -e 'cygpath' -e '\${.*#'
```

命中任意一条即按 §3 改写：

| 味道 | 含义 |
|---|---|
| `rm -rf "$var"` 附近出现 `sed` / `cygpath` | 三层转换链，任一环失败即放大 |
| 建夹具在一条命令、清理在另一条命令 | 路径跨调用漂移，`%TEMP%` 还可能被系统清理 |
| 没有 `set -euo pipefail` | 中间步骤失败后仍继续执行后续删除 |
| `mkdir -p` 后直接 `rm -rf`，中间无断言 | 删除范围未经校验 |

## 7. Gotchas（陷阱与反直觉行为）

1. `sed` 表达式写错只打印错误、退出码非零，但脚本继续跑；不检查 `$?` 就等于没失败。
2. 变量为空与变量退化成 `/c` 是两种不同故障；只查空串拦不住后者。
3. `rm` 成功删除不打印，失败才打印——「没有报错」不等于「没有删除」。
4. 命令超时会被转入后台，`rm` 继续运行；清理命令不要设长超时后放任不管。
5. `rm -rf` 不进回收站；删除一旦发生就没有恢复路径。
6. 盘根删除即使拿到用户口头授权，仍可能被安全分类器拦截；此时交用户手动执行，不换工具绕行。
7. `%TEMP%` 下路径含空格与非 ASCII（用户名），任何拼接都要加引号或用参数列表。
8. `shutil.rmtree` 拒绝删除链接本体，`rm -rf` 会沿链接删目标；两者都必须先判 `is_link`/`isjunction`。
9. `os.path.isjunction` 需 Python ≥3.12；低版本用 `os.path.islink` 兜底。
10. 在 `%TEMP%` 之外（尤其盘根）建探针，即使后来清掉了，也可能已经触发拦截或留下遗留物。

## 8. 安全检查清单（逐项确认）

- [ ] 夹具根由 `mkdtemp`/`TemporaryDirectory` 创建，不是手写字符串
- [ ] 建、测、清在同一进程或同一命令内完成
- [ ] 删除前已 `resolve()` 并断言位于 `tempfile.gettempdir()` 之下
- [ ] 已断言路径严格位于 `tempfile.gettempdir()` 之下（相对深度 ≥ 1，不含 temp 根自身）
- [ ] 已断言顶层目录名带夹具前缀（如 `sw-fixture-`）
- [ ] 输出的 `ALLOW` 行里能看到解析后的绝对路径与深度
- [ ] 链接/联接条目只删本体，未使用递归删除
- [ ] 清理失败与业务失败分别记录，未互相掩盖
- [ ] 未在系统盘根或 `%TEMP%` 之外创建探针
- [ ] 未把未经断言的变量交给 `rm -rf`

## 9. 验收步骤

步骤1：跑 `--selftest` 验证建、断言、清理与拒绝用例，退出码为 `0`。
步骤2：用 `--check` 对真实 `mkdtemp` 目录验证放行（`0`），对 `C:/`、`/c`、`C:/Users`、`%TEMP%` 自身、`%TEMP%` 下无前缀的同级目录验证拒绝（`3`）；再对合法夹具根加 `--min-depth 2` 验证深度拒绝（`3`）。
步骤3：清理后验证 `os.path.lexists(root)` 为假，并确认 `%TEMP%` 下无同前缀遗留。

## 10. 参考

- 事故命令、原始报错与现场证据：[references/verified-case.md](references/verified-case.md)
- 误删后的影响面定性：`windows-deletion-blast-radius-attribution`
- 夹具式脚本测试：`skill-bundled-script-validation`

## 11. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-28 | 初始版本：五条硬规则、guard 脚本、坏味道扫描与验收步骤 |
