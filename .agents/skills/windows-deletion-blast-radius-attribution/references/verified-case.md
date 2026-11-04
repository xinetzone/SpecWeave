# 本案原始证据摘录（2026-10-28 误删 C 盘根目录条目）

本文件只记录事故处置中实际产生的输出片段与由此得到的结论，作为 [SKILL.md](../SKILL.md) 第 3 节四步取证的实测依据。时间戳来自工具输出，未改写。

## 1. 事故形态

一条"核实失败路径"的验证命令在执行末尾出现路径变量退化：

```text
sed: -e expression #1, char 13: unknown option to `s'
sed: -e expression #1, char 7: unterminated `s' command
touch: cannot touch '/c//realfile': Permission denied
```

`sed` 输出为空后，`rootu="/c/${root#C:/}"` 塌缩为 `/c`，末尾 `rm -rf "$rootu"` 作用在盘根。命令因超时被转入后台，显式停止时输出尾部是 `Permission denied`：

```text
rm: cannot remove '/c/Program Files/Lenovo/ModelMgr/Plugins/Image/Lib/site-packages/networkx/readwrite/tests/test_p2g.py': Permission denied
rm: cannot remove '/c/Program Files/Lenovo/ModelMgr/Plugins/Image/Lib/site-packages/networkx/readwrite/text.py': Permission denied
```

同一命令在 `rm` 之前执行过 `ls -la "$rootu"`（此时 `rootu` 已是 `/c`），因此**事故前快照恰好留在这条失败命令的前置输出里**。

## 2. 事故前根清单（同命令前置输出，节选）

```text
drwxr-xr-x 1 xinzo 197609           0 Apr 18  2026 $Recycle.Bin
drwxr-xr-x 1 xinzo 197609           0 Apr 24  2026 $SysReset
drwxr-xr-x 1 xinzo 197609           0 Nov  4  2025 OneDriveTemp
lrwxrwxrwx 1 xinzo 197609           8 Nov  4  2025 Documents and Settings -> /c/Users
drwxr-xr-x 1 xinzo 197609           0 Jul 17 20:16 PerfLogs
drwxr-xr-x 1 xinzo 197609           0 Oct 22 22:54 Program Files
drwxr-xr-x 1 xinzo 197609           0 Sep 28 21:28 Program Files (x86)
drwxr-xr-x 1 xinzo 197609           0 Oct 24 11:01 ProgramData
drwxr-xr-x 1 xinzo 197609           0 Dec 19  2025 QMDownload
drwxr-xr-x 1 xinzo 197609           0 Aug 18 05:31 Recovery
drwxr-xr-x 1 xinzo 197609           0 Aug  1 08:20 Users
drwxr-xr-x 1 xinzo 197609           0 Oct 25 20:26 Windows
-rw-r--r-- 1 xinzo 197609 33820106752 Oct 26 15:43 pagefile.sys
drwxr-xr-x 1 xinzo 197609           0 Aug 19 17:12 temp
drwxr-xr-x 1 xinzo 197609           0 Oct 23 17:06 tmp
```

（另有 `AMTAG.BIN`、`DumpStack.log.tmp`、`System Volume Information`、`appverifUI.dll`、`config.ini`、`inetpub`、`swapfile.sys`、`vfcompat.dll` 等，合计 21 项。）

## 3. 事故后根清单与差异

同一目录的复核输出与新清单比对结果：

```text
=== C 根条目差异（事故前清单 vs 现在） ===
GONE $SysReset
GONE OneDriveTemp
--- 差异比对结束 ---
```

其余 19 项仍在位。`Program Files` 的 mtime 事故前后同为 `Oct 22 22:54`。

## 4. 权限证据

```text
C:\Program Files\Lenovo NT SERVICE\TrustedInstaller:(I)(F)
                        NT AUTHORITY\SYSTEM:(I)(F)
                        BUILTIN\Administrators:(I)(F)
                        BUILTIN\Users:(I)(RX)
                        BUILTIN\Users:(I)(OI)(CI)(IO)(GR,GE)
```

配套交叉印证：

- 被 `rm` 报过 `Permission denied` 的样本文件 `networkx/readwrite/text.py`、`networkx/readwrite/tests/test_pajek.py` 仍在原处。
- `ModelMgr` 顶层 `ModelMgr.exe`、`ModelMgrService.exe`、`Plugins`、`SDK`、`Tools`、`Uninstall` 等条目齐全，mtime 为 2025-05 至 2026-01。
- 空目录计数 `EMPTY_COUNT=103`，抽样全部是 `ModelMgr/.../Lib/**/__pycache__`、`AIAgent/mcp/.../npm/tap-snapshots`、`LearningZone/...` 一类安装期空壳，均位于只读路径。

## 5. 服务写入证据

观察时刻 `NOW=2026-10-28 10:06:42`，`ProgramData\Lenovo` 下目录在同一窗口内继续推进 mtime：

```text
2026-10-28 10:06 /c/ProgramData/Lenovo/devicecenter/extends/cefcache/Network
2026-10-28 10:06 /c/ProgramData/Lenovo/devicecenter/extends/modules/desktopmainframe/Custom
2026-10-28 10:07 /c/ProgramData/Lenovo/LeAppStore/LStoreSoftsCache
2026-10-28 10:07 /c/ProgramData/Lenovo/devicecenter/logs
2026-10-28 10:07 /c/ProgramData/Lenovo/devicecenter/ludp
```

`Program Files\Lenovo\AIAgent` 的 09:59 mtime 同样来自服务写入，不是删除。

## 6. 回收站

```text
/c/$Recycle.Bin/S-1-5-18/ -> 0 entries
/c/$Recycle.Bin/S-1-5-21-1360840929-909226577-3124298871-500/ -> 0 entries
/c/$Recycle.Bin/S-1-5-21-2716555632-999833528-2508072796-1000/ -> 0 entries
/c/$Recycle.Bin/S-1-5-21-2716555632-999833528-2508072796-1001/ -> 2 entries
/c/$Recycle.Bin/S-1-5-21-2716555632-999833528-2508072796-1002/ -> 0 entries
```

含 2 个文件的目录中，文件时间为 2025-12 与 2026-09，均不在事故窗口内；同目录 `desktop.ini` 由 Windows 在 10:08 重写。

## 7. 结论与未验证项

| 项 | 结论 | 依据 |
|---|---|---|
| `C:\$SysReset` | 已删除，无回收站恢复路径 | 根级差异 + `rm` 不进回收站 |
| `C:\OneDriveTemp` | 已删除，应用会重建 | 同上 |
| `C:\Program Files\Lenovo` | 一个字节未删 | 报错行 + ACL + 父目录 mtime + 样本文件 |
| C 盘根其余条目 | 全部在位 | 21 项逐项比对 |
| 回收站 | 当前用户无事故窗口内条目 | 按 SID 计数 + 文件时间 |

未验证：

- 探针遗留物 `C:\jdang`（指向已不存在的 `C:\realdir` 的目录联接）在会话结束时仍在盘根；删除被安全分类器拦截，改为向用户提供手动命令，未执行。
- 权限结论的前提是删除进程未提权；本案以 `Permission denied` 行与父目录 mtime 佐证，该前提未被单独测量。
- 除 C 盘根以外的其他卷未做全量比对，本结论不外推。
