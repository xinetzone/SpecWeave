# 事故证据：漂移探针的目录路径退出码

来源会话 `198e9c74-f925-4825-a798-7af8c50415bf`（第二轮用户纠正为「改用 .agents/skills 目录」）。被验证脚本为主权区 `.agents/skills/stale-read-edit-reconciliation/scripts/probe_drift.py`。

## 1. 契约（脚本 docstring 原文）

```text
Exit codes
  0  probed; no drift (or baseline written)
  1  drift detected, target absent, or link target unreadable
  2  usage or IO error (bad arguments, missing/invalid baseline, directory path)
```

`1` 一条承载三种语义（检出漂移 / 目标缺失 / 链接目标不可读），`2` 明写包含目录路径。

## 2. 首轮夹具输出（15 条断言）

原始输出片段，仅一条失败：

```text
PASS absent-probe: expected=1 got=1
FAIL directory-probe: expected=2 got=1
PASS missing-baseline: expected=2 got=2
HAS_FAILURE
fixture_dir_removed True
```

`PASS absent-probe: expected=1 got=1` 与紧随其后的 `FAIL directory-probe: expected=2 got=1` 并列，正是歧义的形态：同一个 `1`，一条是真的检出，一条是崩溃。

## 3. 根因

目录路径进入探测函数后直接对路径做字节读取。该调用对目录抛 `OSError` 子类：**本机 Windows 实测为 `PermissionError`（`errno 13`），POSIX 上是 `IsADirectoryError`**。异常未被捕获，Python 解释器打印 traceback 后以 `1` 退出。`1` 恰好是契约里「检出漂移」的码。

复现取证（本机）：

```text
platform win32
type PermissionError | subclass_of_OSError True | errno 13
is_file(d) False
```

异常类型不可移植，所以修复判据只能是 `is_file()` 的布尔结果，不能是异常的名字。

两条并存的失败面：

- **未捕获异常路径**：退出 1 + traceback 到 stderr → 只断言退出码的夹具会把期望值为 `1` 的用例判 PASS。
- **宽兜底路径**：若脚本改为 `except OSError: ... return 1`，`IsADirectoryError` / `PermissionError` 被一并吸收，traceback 消失，退出码仍是 1 → 此时只有 stdout 形状（A2）还能揭穿。

## 4. 修复

两处改动，都是「把判定前移到读取之前」：

1. 探测函数在读取前按 `kind != "file"` 提前返回，不进入 `read_bytes()`；
2. 主流程在探测后立刻短路：`directory` / `other` → stderr 打印一行 `not a regular file: ...` → `return 2`。

现盘落地形态：

```python
    current = probe(args.path)
    if current["kind"] == "directory" or current["kind"] == "other":
        print(f"not a regular file: {args.path} ({current['kind']})", file=sys.stderr)
        return 2
```

## 5. 复跑

```text
PASS absent-probe: expected=1 got=1
PASS directory-probe: expected=2 got=2
PASS missing-baseline: expected=2 got=2
ALL_PASS
fixture_dir_removed True
```

15 条断言全过，夹具目录已清理，技能目录无 `__pycache__`。

## 6. 判读边界（不要过度解读）

这次事故是**「期望 2、实得 1」被抓到的**，不是「期望 1、实得 1」的假通过。它证明的是 `1` 无法区分「检出」与「崩溃」；把它说成「本次已发生假 PASS」是过度解读。

真正的假 PASS 通道出现在**期望值为 `1`** 的路径上：那时 A1 命中，A2（stdout 可解析）与 A3（stderr 为空）是唯一判别手段。本技能的断言三元组正是为那条通道设计的。

## 7. 落地检查表

| 契约路径 | 期望码 | A2 启用 | stderr | 只看码会怎样 |
|---|---|---|---|---|
| `directory-probe` | `2` | 否（stdout 为空，原因在 stderr） | 一行 `not a regular file` | 期望 2 时能抓到（本次） |
| `absent-probe` | `1` | 是（JSON，`drift=true`） | 空 | 期望 1 时抓不到，必须靠 A2/A3 |
| `drift-detected` | `1` | 是（JSON，`changes` 非空） | 空 | 同上 |
| `missing-baseline` | `2` | 否（stdout 为空，原因在 stderr） | 一行 `baseline not found` | 期望 2 时能抓到 |

A2 是否启用由契约声明，不由期望码推断：退出 `2` 的路径通常不产出机器可读结果，强行加 `--json` 会把合法路径判失败。
