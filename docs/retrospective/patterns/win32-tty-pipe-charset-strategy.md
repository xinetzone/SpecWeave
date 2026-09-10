---
source: "会话复盘 sc-20260907-win32-tty-pipe-charset-fix"
created: "2026-09-07"
maturity: L2
category: methodology-patterns
tags: [windows, character-encoding, invoke, podman, jpman-client, TTY, PIPE]
validation_count: 1
reuse_count: 0
---

# 模式：Windows Console 字符集双路径策略（TTY vs PIPE）

## 触发场景

在 Windows 上运行 Python 脚本（尤其是通过 Invoke / PowerShell 调用容器工具如 Podman/Docker）时，若子进程输出含有非 ASCII 字符（如中文），且脚本需要在以下两种环境中都能正确渲染，则需要此模式：

1. **原生 TTY Console**（用户在自己的 PowerShell / cmd / IDE Terminal 中直接运行 invoke）
2. **外层 PIPE 捕获**（Trae Sandbox / CI / 日志收集系统重定向 stdout/stderr）

## 核心问题

Windows 原生 Console 的默认代码页通常是 `cp936`（GBK 变体），而 Python 子进程（容器、CLI 工具等）通常输出 UTF-8 bytes。当这两者之间存在**解码端不匹配**时，UTF-8 字节被 cp936 解码就会产生乱码。

### 三层字符集错配模型

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 容器/Linux 输出端                                  │
│    永远是 UTF-8 bytes                                      │
│    （Podman / Python / CLI 工具均输出 UTF-8）               │
└──────────────────┬──────────────────────────────────────────┘
                   │ bytes（UTF-8）
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 传输管道                                            │
│    TTY 模式：直接写入 Console Handle，OS 按当前 CP 解码      │
│    PIPE 模式：被捕获层（Sandbox/CI）按宿主 CP 解码           │
└──────────────────┬──────────────────────────────────────────┘
                   │ decode 结果（bytes vs str）
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 终端渲染端                                          │
│    原生 Console：CP936（GBK）或 CP65001（UTF-8）            │
│    宿主 capture 层：cp936 或 locale 预编码                   │
└─────────────────────────────────────────────────────────────┘
```

**乱码根因**：Layer 1（UTF-8 bytes）→ Layer 2（透明管道）→ Layer 3（按 cp936 解码）= 错位乱码

## 核心步骤

### Step 1：判别环境类型

使用 `os.isatty(sys.stdout.fileno())` 判别当前是 TTY 还是 PIPE：

```python
import os, sys
is_tty = os.isatty(sys.stdout.fileno())
```

- `True` = 原生 TTY Console
- `False` = 被重定向/PIPE 捕获（Sandbox / CI）

### Step 2a：原生 TTY 路径

目标：让 Console 和 Python 都使用 UTF-8 编码

```python
import ctypes, sys, os, io

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
CP_UTF8 = 65001
kernel32.SetConsoleOutputCP(ctypes.c_uint(CP_UTF8))
kernel32.SetConsoleCP(ctypes.c_uint(CP_UTF8))

# PowerShell .NET 层同步
try:
    from System import Console as _NETConsole
    from System.Text import Encoding as _NETEncoding
    _NETConsole.OutputEncoding = _NETEncoding.UTF8
    _NETConsole.InputEncoding = _NETEncoding.UTF8
except Exception:
    # fallback: chcp.com
    pass

# sys.stdout 换壳为 UTF-8 TextIOWrapper
_wrap_stdio_encoding("utf-8")

# 子进程：绕过 invoke PIPE 捕获，直接继承 Console Handle
subprocess.call(cmd, shell=True, stdout=None)
```

### Step 2b：外层 PIPE 路径

目标：让 Python 写出的 bytes 与捕获端的解码编码匹配

```python
# 获取宿主编码（启动时 console CP 或 locale fallback）
console_cp = kernel32.GetConsoleOutputCP()  # 先 Get 再 Set（已在 Step 2a 中 Set 过）
if console_cp and console_cp != CP_UTF8:
    host_encoding = f"cp{console_cp}"
else:
    import locale
    host_encoding = locale.getpreferredencoding(False)

# sys.stdout 换壳为宿主编码 TextIOWrapper
_wrap_stdio_encoding(host_encoding)

# 子进程：invoke c.run(encoding='utf-8') 强制按 UTF-8 解码
# Result.stdout str 正确后，再走宿主编码写入 stdout
```

### Step 3：辅助函数

```python
def _wrap_stdio_encoding(encoding_name: str) -> None:
    """把 sys.stdout/sys.stderr 的 TextIOWrapper 换壳为指定 encoding。"""
    import io
    for _io_name in ("stdout", "stderr"):
        _io = getattr(sys, _io_name)
        try:
            old_buf = _io.buffer
            line_buffering = getattr(_io, "line_buffering", True)
            write_through = getattr(_io, "write_through", False)
            _io.flush()
            new_wrap = io.TextIOWrapper(
                old_buf,
                encoding=encoding_name,
                errors="replace",
                line_buffering=line_buffering,
                write_through=write_through,
            )
            setattr(sys, _io_name, new_wrap)
        except Exception:
            pass
```

## 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 只调 `sys.stdout.reconfigure(encoding='utf-8')` | 在被重定向的 TextIOWrapper 上静默失败 | 使用 `io.TextIOWrapper` 直接换壳 |
| 只改 A 端（宿主输出编码）不改 B 端（子进程解码） | Result.stdout 在 invoke 内部就已乱码 | A/B 两端必须同时生效 |
| 不区分 TTY vs PIPE，统一走同一路径 | TTY 路径在 Sandbox 下仍乱码，或反之 | 用 `os.isatty()` 判别后分路径 |
| 重复初始化（每次调用都执行 kernel32 调用） | 性能损耗，可能干扰其他进程 | 模块级单例 flag 缓存结果 |
| 使用 `locale.getpreferredencoding()` 作为唯一来源 | py314 在 Sandbox 中返回 `utf-8`（非真实宿主编码） | 优先用 `GetConsoleOutputCP()`，locale 仅 fallback |

## 迁移验证

**验证条件**：
- [ ] 在原生 PowerShell 中运行 `invoke env.run-cmd --cmd "inv -l"`，中文清晰无乱码
- [ ] 在 Trae Sandbox PIPE 中运行相同命令，中文清晰无乱码
- [ ] `python -c "import sys; print(sys.stdout.encoding)"` 输出正确编码

**验证命令**：
```powershell
# 判别 TTY/PIPE
python -c "import sys,os; print('isatty(stdout)=', os.isatty(sys.stdout.fileno()))"
chcp.com

# 测试中文输出
invoke env.run-cmd --cmd "inv -l"
```

## 相关文件

- [apps/containers/client/src/jpman_client/tasks/utils.py](../../../apps/containers/client/src/jpman_client/tasks/utils.py) — 实际实现
- [apps/containers/client/README.md](../../../apps/containers/client/README.md#L296-L320) — §10.3 中文乱码排障
