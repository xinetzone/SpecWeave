# 来源会话证据：sed 变量退化导致 rm -rf 作用于盘根

取证来源：会话 `0fc0150f-e330-487f-82dd-b70ab8532806`（2026-10-28）。以下均为该会话内的原始工具输出摘录，未改动措辞。

## 1. 失败命令原文

```bash
cd /d/spaces/SpecWeave && T="$(cygpath -w "$(mktemp -d)")"; echo "T=$T"
mkdir -p "/c/$(echo "$T" | sed 's|^C:\\\\||; s|\\\\|/|g')/realdir" 2>/dev/null
W() { echo "$1" | sed 's|/|\\\\|g'; }
root="$(echo "$T" | sed 's|\\\\|/|g')"; rootu="/c/${root#C:/}"
mkdir -p "$rootu/realdir"; touch "$rootu/realfile"
echo "--- A: cmd mklink /J from Git Bash ---"
cmd //c mklink /J "$(cygpath -w "$rootu/mklinkd")" "$(cygpath -w "$rootu/realdir")" 2>&1 | head -3
...
rm -rf "$rootu"; echo "CLEANED"; ls -d "$rootu" 2>&1 | head -1
```

## 2. 原始报错

```text
T=C:\Users\xinzo\AppData\Local\Temp\tmp.B3Zh76dB55
sed: -e expression #1, char 13: unknown option to `s'
sed: -e expression #1, char 7: unterminated `s' command
touch: cannot touch '/c//realfile': Permission denied
```

`touch` 的目标 `/c//realfile` 直接暴露了退化结果：`rootu` 塌成 `/c/`，后续 `mkdir`、`mklink`、`rm -rf` 全部作用在盘根。

命令超时后被转入后台（`Command exceeded its timeout and was moved to background`），`rm` 在后台继续运行数秒才被显式停止。停止时输出尾部是：

```text
rm: cannot remove '/c/Program Files/Lenovo/ModelMgr/Plugins/Image/Lib/site-packages/networkx/readwrite/tests/test_p2g.py': Permission denied
```

## 3. 影响面（会话内后续只读核对确认）

| 对象 | 结论 | 证据 |
|---|---|---|
| `C:\$SysReset` | 已删除，不可恢复 | 根级清单差异 `GONE $SysReset`；`rm` 不进回收站 |
| `C:\OneDriveTemp` | 已删除，应用会自动重建 | 根级清单差异 `GONE OneDriveTemp` |
| `C:\Program Files\Lenovo` | 一个字节未删 | `icacls` 显示 `BUILTIN\Users:(I)(RX)`；`Program Files` 目录 mtime 仍是 `Oct 22 22:54`；被报 `Permission denied` 的样本文件仍在 |
| 该子树 103 个空目录 | 安装期既有空壳 | 路径类型为 `Lib/**/__pycache__`、`tap-snapshots` 等只读路径 |
| 回收站 | 无本次条目 | 当前用户 SID 子目录条目数为 0 |
| 盘根其余 19 项 | 全部在位 | 事故前后清单逐项比对 |

留下的遗留物是 `C:\jdang`（指向已不存在的 `C:\realdir` 的目录联接）。删除它时安全分类器拦截了所有盘根删除操作，最终由用户手动执行 `rmdir C:\jdang`。

## 4. 成功对照：单命令离夹具

同一会话里，使用 `%TEMP%` 下带前缀的夹具目录、在同一条命令内完成建/测/清，正常结束：

```text
create jok rc=0
create jdangle rc=0
absent    ABSENT
jok       OCCUPIED JUNCTION -> C:\Users\xinzo\AppData\Local\Temp\dlf-probe-c1ilt4u5\realdir exists=True test-e=True
jdangle   OCCUPIED JUNCTION -> C:\Users\xinzo\AppData\Local\Temp\dlf-probe-c1ilt4u5\gone exists=False test-e=False
realfile  OCCUPIED OTHER-FILE exists=True test-e=True
PROBE_EXIT=0
```

对照点有三处：夹具根由工具生成（`%TEMP%\dlf-probe-<rand>`）、带固定前缀、建与清在同一进程内。事故命令恰好三条全不满足。

## 5. 本技能据此固化的规则

1. 单进程闭环，不跨命令保留夹具路径。
2. 不做 `cygpath` + `sed` + `${var#prefix}` 的三级转换。
3. 删除前 `resolve()` 后断言「在 `%TEMP%` 之下」「深度 ≥ 1（不落在 temp 根自身）」「带夹具前缀」，失败即退出。
4. 不把变量交给 `rm -rf`；链接只删本体。

## 6. 未覆盖与限制

- 本技能未复跑事故命令，也不应复跑：成功删除不产生新证据，只会扩大影响面。
- `os.path.isjunction` 需 Python ≥3.12；在更低版本上脚本回退到 `os.path.islink`，未逐版本实测。
- 随包脚本的拒绝用例覆盖 `C:/`、`/c`、`C:/Users`、`%TEMP%` 自身、无前缀同级目录、`--min-depth 2` 下的深度不足、前缀不符；不覆盖 UNC 路径与 8.3 短文件名形式。
