---
name: bundled-script-exit-code-ambiguity
version: 1.0.0
description: 验证自带脚本的退出码契约时，必须区分「契约检出的 1」与「未捕获异常返回的 1」。必须使用此技能：当用户提到「退出码对了但行为不对」「Traceback 也是退出 1」「目录路径报 IsADirectoryError」「夹具只看退出码」「PASS 但其实是崩了」「异常冒充契约码」时。不用于通用夹具搭建与缺陷注入（用 skill-bundled-script-validation）、质量门掉分修复（用 skill-quality-gate-remediation）或会话取证（用 chat-session-evidence-audit）。
argument-hint: "<script> [fixture-root]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**/scripts/**/*.py"
  - ".agents/skills/**/SKILL.md"
title: "自带脚本退出码歧义判别"
x-toml-ref: "../../../.meta/toml/.agents/skills/bundled-script-exit-code-ambiguity/SKILL.toml"
source: "来源会话 198e9c74-f925-4825-a798-7af8c50415bf 的漂移探针目录路径事故"
---

# 自带脚本退出码歧义判别

本技能只回答一个问题：当夹具断言「退出码等于契约值」时，它究竟证明了什么。

答案常常是「几乎什么也没证明」。Python 脚本未捕获异常时进程退出码固定为 `1`，而校验脚本最常见的「检出问题」契约码也是 `1`。两者在退出码上完全一致。

## 1. Why：退出码为什么不足以作为证据

三个叠加的事实：

| 事实 | 后果 |
|---|---|
| 未捕获异常 → 解释器退出 `1` | 与「检出失败」同码，退出码无法区分「我发现了问题」与「我崩了」 |
| 读取目录抛出的异常是 `OSError` 子类 | 脚本里一句 `except OSError` 宽兜底就能把崩溃正式映射成契约码，连 traceback 都不留 |
| 空 stdout 送进 `json.loads` 会抛 `JSONDecodeError` | 观察者容易把「死在打印之前」读成「没输出」，转而去怀疑断言写错，而不是怀疑脚本 |

实测（来源会话）：漂移探针对目录路径做读取，进程退出 `1`；该脚本契约中 `1` 同时承载「检出漂移」「目标缺失」「链接目标不可读」三种语义。原始行与修复前后输出见 [事故证据](references/verified-case.md)。

异常类型本身不可移植：本机 Windows 实测抛出 `PermissionError`（`errno 13`），POSIX 上是 `IsADirectoryError`，两者都是 `OSError` 子类。所以**不能按异常类型分支修补**，只能按类型判断的结果（`is_file()` / `is_dir()`）在读取前短路。

## 2. 适用边界

适用：

- 被验证脚本的契约含两个以上退出码，且 `1` 是其中一个约定值
- 夹具只看退出码，需要判断它到底证明了什么
- 出现「退出码对，但输出不像正常结果」的怀疑

不适用：

| 任务 | 交给 |
|---|---|
| 通用正向样本、缺陷注入、镜像夹具搭建 | `skill-bundled-script-validation` |
| Skill 包体整包验收（质量门/链接门/编码） | `skill-package-verification-gates` |
| 质量门掉分修复 | `skill-quality-gate-remediation` |
| 核实来源会话的历史过程 | `chat-session-evidence-audit` |

## 3. 预检：先把契约读成清单（零写入）

改脚本或改夹具之前，只读地列出每条契约路径：

| 字段 | 例 |
|---|---|
| 路径名 | `directory-probe` |
| 命令 | `python probe.py --path <dir>` |
| 期望码 | `2` |
| stdout 形状 | 空（原因写在 stderr） |
| stderr 允许内容 | 一行 `not a regular file` |

这份清单本身就是本技能的 dry-run：不执行任何写操作，只产出一张待断言表。清单少于两行说明契约没读全——先补契约，再谈断言。

> **为什么清单要写在改代码之前？** 修复时注意力只会落在失败那一条上，清单是唯一能把全集摆出来的东西；缺了它，「复跑全部路径」会退化成「复跑我记得的那几条」。

## 4. 判别规则：三断言

对清单中每条路径，同时断言三件事：

| # | 断言 | 单独失败时的含义 |
|---|---|---|
| A1 | `exit == expected` | 契约不符 |
| A2 | 契约声明了机器可读输出时，stdout 按声明的形式解析成功 | 输出形状不符，或进程在产出结果前就死了 |
| A3 | stderr 不含 `Traceback`，且未声明诊断的路径 stderr 必须为空 | `Traceback` = 未捕获异常；无 traceback 的非空文本 = 未声明的诊断 |

A3 是两级的：**无论契约是否允许 stderr 输出，`Traceback (most recent call last)` 都判失败**；只有「是否允许其他文本」由契约决定。否则一给退出 `2` 的路径开口子，堆栈就会跟着混进来。

判定表：

| A1 | A2 | A3 | 结论 |
|---|---|---|---|
| 命中 | 通过 | 通过 | PASS |
| 命中 | 失败（不可解析或为空） | 含 `Traceback` | **缺陷**：异常冒充契约码 |
| 命中 | 通过 | 非空但无 `Traceback`、契约未声明 | 未声明的诊断输出；核对契约后判为文档缺项或缺陷 |
| 未命中 | 任意 | 任意 | 契约不符；先读 stderr 是否已给出原因 |

规矩只有一条：**不得为了让 A1 变绿而放宽 A2 或 A3。** 放宽断言等于把缺陷写进验收标准。

> **为什么 A2 只要求「可解析」而不是「内容正确」？** 本技能管的是形状——进程是否活到了产出结果那一步。内容对不对由各脚本自己的业务断言负责，混在一起会让「JSON 能解析」被误当成「结论正确」。

## 5. 歧义码对照

| 码 | 常见来源 | 结构性歧义 |
|---|---|---|
| `0` | 显式成功 | 低——未捕获异常不会返回 0 |
| `1` | 检出问题 / 未捕获异常 / 部分脚本的用法错误 | **高**——多种语义同码 |
| `2` | `argparse` 用法错误；契约写明的 IO 错误 | 中——须分辨是脚本判定还是解析器退出 |
| 其它 | 自定义 | 逐条核对 |

> **为什么把 `1` 单列？** 它是解释器崩溃的默认码。凡是把 `1` 用作「发现问题」的脚本，都自带一条无提示的假阳性通道。

## 6. 修复模式

原则：**把类型与边界判断前移到读取之前**，让非法输入稳定落到用途码（通常是 `2`），而不是抛在读取里。

```python
if not os.path.isfile(path):          # 读取之前
    print(f"not a regular file: {path}", file=sys.stderr)
    return 2
```

三条禁止：

- 禁止 `except Exception: return 1`——把崩溃伪装成检出，直接制造假阳性
- 禁止只改夹具——缺陷在脚本侧，放宽夹具会把缺陷固化成验收标准
- 禁止 `2>&1` 合并两路输出后断言 stderr 为空——合并即失去判别力

> **为什么必须复跑全集而不是只跑失败那条？** 短路前移会改变相邻分支的执行顺序，原本经由异常路径返回的用例可能因此改道，只跑失败项看不到这类回归。

## 7. 复跑与证据

随包脚本 [scripts/assert_contract.py](scripts/assert_contract.py) 把三断言固化为一条命令。它只读且幂等：不修改夹具、不写缓存，重复执行结果一致。

```bash
python scripts/assert_contract.py --expect 2 --allow-stderr --name directory-probe -- \
  python probe.py --path fixtures/a-dir
echo "HARNESS_EXIT=$?"
```

`--json` 只在契约声明了机器可读输出的路径上加；`--allow-stderr` 只在契约声明了 stderr 诊断的路径上加。两者都按第 3 节的清单填，不按期望码推断。

自身退出码：`0` 三断言全过；`1` 有断言失败（失败项与捕获到的 stderr 打印到 stderr）；`2` 用法错误或命令无法启动。

交付报告用这张表，一行一条路径：

| 路径 | 期望码 | 实得码 | stdout | stderr | 结论 |
|---|---|---|---|---|---|

不要写「全部验证通过」而不附码与输出形状。

## 8. Gotchas（陷阱与反直觉行为）

1. **`2>&1` 之后 A3 无法成立**：合并流后 stderr 与 stdout 不可分，必须 `out=$(cmd 2>"$err")` 或让脚本分流捕获。
2. **读取目录的异常类型随平台变**：本机 Windows 实测 `PermissionError`（`errno 13`），POSIX 上是 `IsADirectoryError`；两者都是 `OSError` 子类，`except OSError` 会把它们一起吸收成正常返回，此时连 traceback 都没有，只剩 A2 能揭穿。
3. **不要按异常类型修补**：按 `is_file()` 的判定结果在读取前短路，才不依赖平台抛哪个子类。
4. **管道会换掉退出码**：`cmd | head` 返回 `head` 的状态；用 `set -o pipefail` 或先取 `$?`。
5. **空 stdout 的 `JSONDecodeError` 是误导源**：它同时对应「脚本没输出」与「脚本死在打印前」，必须结合 stderr 判读。
6. **`argparse` 自带退出码**：`--help` 退出 `0`、用法错误退出 `2`。这两条路径的 A2 要按路径豁免——`--help` 的 stdout 不是 JSON。
7. **`--expect 1` 的夹具天生漏报**：看到期望值为 `1` 的断言，先确认它是否也断言了 A2 与 A3。
8. **给退出 2 的路径开 stderr 口子时别把堆栈也放进来**：`--allow-stderr` 只放宽「非空」，`Traceback` 仍判失败。
9. **`grep -c` 零匹配会污染 `$?`**：统计行数加 `|| true`，但不要把 `|| true` 用到脚本调用本身。
10. **函数级单测不能替代子进程断言**：只有 `__main__` 里逃逸的异常才会转成退出码 1。
11. **不做四处登记不等于已交付**：本技能只产出包体；入库登记另走 `native-skill-surface-registration`。

## 9. 安全检查清单（逐项确认）

- [ ] 契约清单已写完（命令、期望码、stdout 形状、stderr 允许内容）
- [ ] 每条路径都断言了 A1 + A2 + A3，没有只留 A1
- [ ] 期望值为 `1` 的路径已单独标注，并确认 A2/A3 在断言范围内
- [ ] stdout 与 stderr 是分流捕获的，未使用 `2>&1`
- [ ] 退出码取自脚本本身，未被管道或复合命令替换
- [ ] 修复是把边界判断前移到读取之前，未新增 `except Exception`
- [ ] 修复后复跑了全部契约路径，不只失败那条
- [ ] 断言脚本只读且幂等，未修改夹具、未在技能目录留下 `__pycache__`
- [ ] 交付报告逐路径列出期望码、实得码、stdout 形状与 stderr 状态
- [ ] 未验证的路径已标注，未算进通过项

## 10. 参考

- [事故证据与修复前后输出](references/verified-case.md)
- 断言脚本：[scripts/assert_contract.py](scripts/assert_contract.py)
- 相邻技能：`skill-bundled-script-validation`（夹具与假失败识别）、`skill-package-verification-gates`（包体验收）
