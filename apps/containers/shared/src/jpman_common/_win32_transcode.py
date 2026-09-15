"""Windows 双端字符集修复（jpman-common 内部模块）。

模块级单例，防止 run_cmd 被重复调用 100+ 次时重复执行。

乱码根因（三层模型，V 阶段对抗验证得出）：
  ① 容器/Linux 输出的 bytes 永远 = UTF-8。
  ② Trae Sandbox 把整个 Python 进程树的 stdout/stderr 以 PIPE 方式重定向，
     并按宿主 Windows 默认 cp936(GBK) 解码 PIPE bytes → 经典错位乱码
     （``清理`` → UTF-8 bytes → GBK 解读 → ``娓呯悊``）。
  ③ invoke c.run() 内部 subprocess.Popen(stdout=PIPE) 同样按
     locale.getpreferredencoding() = cp936 decode，在 Python 内部 Result.stdout
     阶段就已经乱码，后续写入即使是 Console Handle 也无法救回。

双端修复策略（两端同时生效才闭环，缺一不可）：
  A. 宿主打印端：sys.stdout/stderr.reconfigure(encoding=<宿主编码>, errors='replace')
     → 宿主 print("执行：...") 写成 cp936 bytes，Sandbox 按 cp936 解码 → 中文正确。
  B. 子进程捕获端：c.run(..., encoding='utf-8') 强制按 UTF-8 解码子进程 stdout
     → Result.stdout 里的 str 就是正确中文，再走 A 路径编码成宿主 bytes。
  辅助：SetConsoleOutputCP(65001)（非 Sandbox 原生 Console 的情况下生效，
     做 defense-in-depth，失败静默）。
"""
import ctypes
import os
import platform
import sys

_WIN32_STDOUT_TRANSCODE_READY = False


def _ensure_win32_stdout_transcode() -> tuple[str, bool]:
    """Windows 双端字符集初始化（TTY / PIPE 分路径策略）。

    返回值 ``(subproc_encoding, is_tty_console)``：
        - ``subproc_encoding``：传给 invoke ``c.run(encoding=...)`` 的值；空串表示走默认。
        - ``is_tty_console``：True = 原生 TTY Console，可 bypass invoke PIPE 捕获层
                                用 ``subprocess.call(shell=True, stdout=None)`` 直接继承 Console Handle；
                              False = 被外层 Sandbox/PIPE 重定向，必须走 invoke c.run + Python stdout 重编码。

    只 Windows 执行，其他平台直接返回 ``("", False)``。初始化完成后单例标记不再重复执行。

    分路径策略（V阶段对抗验证出的双环境分裂）：
      1. 原生 TTY Console（用户在自己的 PowerShell / cmd / IDE Terminal 直接跑 invoke）
         → 子进程（podman/docker/...）直接继承 Console Handle 写入，
            只要把 SetConsoleOutputCP/SetConsoleCP 切到 65001，并把 PowerShell
            Console::OutputEncoding/InputEncoding 改成 UTF8，
            再加 sys.stdout/stderr 的 TextIOWrapper encoding=utf-8，中文就能 100% 正确渲染。
      2. 外层 PIPE 捕获（Trae Sandbox / CI 重定向 stdout）
         → Python 进程树 stdout 是 PIPE 而非 Console Handle，
            SetConsoleOutputCP 对 PIPE 解码端无效；必须把 sys.stdout/stderr
            的 TextIOWrapper encoding 改成 GetConsoleOutputCP() 的宿主原生编码（通常 cp936），
            保证 write 端 bytes 与外层 capture 端的解码编码匹配，才能把正确中文传出去。
    """
    global _WIN32_STDOUT_TRANSCODE_READY
    if platform.system() != "Windows":
        return "", False
    if _WIN32_STDOUT_TRANSCODE_READY:
        # 注意：第一次初始化时已把 (subproc_encoding, is_tty_console) 缓存在闭包外
        return _WIN32_TRANSCODE_CACHED_RESULT

    kernel32 = None
    console_cp = 0
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # ⚠ 先 Get 再 Set：启动时的真实 Console CP 才是宿主/PIPE 捕获端的解码编码；
        # SetConsoleOutputCP(65001) 会让后续 GetConsoleOutputCP() 返回 65001，影响判断。
        console_cp = kernel32.GetConsoleOutputCP()
        CP_UTF8 = 65001
        # 原生 TTY Console 时才需要 Set*CP：PIPE 场景下此调用无副作用也无效
        kernel32.SetConsoleOutputCP(ctypes.c_uint(CP_UTF8))
        kernel32.SetConsoleCP(ctypes.c_uint(CP_UTF8))
    except Exception:
        console_cp = 0

    # ── TTY vs PIPE 判别 ──
    is_tty = False
    try:
        is_tty = os.isatty(sys.stdout.fileno())
    except Exception:
        is_tty = False  # 典型：sys.stdout 被重定向成 StringIO

    subproc_encoding = ""
    if is_tty:
        # 路径 1：原生 TTY Console
        #   SetConsoleOutputCP 已切到 65001；现在把 PowerShell [Console]::OutputEncoding 也
        #   改到 UTF8（影响用 PowerShell CreateProcess 启动的子进程在父 PS 里的编码行为）。
        try:
            import io as _io  # noqa: F401

            try:
                from System import Console as _NETConsole  # type: ignore
                from System.Text import Encoding as _NETEncoding  # type: ignore
                _utf8 = _NETEncoding.UTF8
                _NETConsole.OutputEncoding = _utf8
                _NETConsole.InputEncoding = _utf8
            except Exception:
                # .NET interop 不可用时回退到 chcp.com（外部命令，副作用大）
                try:
                    import subprocess as _sp
                    _sp.run(
                        ["chcp.com", "65001"],
                        stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, check=False,
                    )
                except Exception:
                    pass
        except Exception:
            pass
        # A 端：sys.stdout / stderr 写 UTF-8 bytes → Console 按 CP65001 渲染 → 中文正确
        _wrap_stdio_encoding("utf-8")
        # B 端：invoke c.run 捕获子进程 bytes → 源头按 UTF-8 解码才会得到正确 str
        subproc_encoding = "utf-8"
    else:
        # 路径 2：外层 PIPE 捕获（Trae Sandbox / CI）
        #   宿主捕获端通常按启动时 console_cp 解码（一般是 cp936）。
        #   A 端必须：Python print str → encode 成宿主端一致的 bytes → 捕获端 decode 后得回正确中文。
        host_encoding = ""
        if console_cp and console_cp != 65001:
            host_encoding = f"cp{console_cp}"
        else:
            try:
                import locale
                pref = locale.getpreferredencoding(False) or ""
                if pref and pref.lower() not in ("utf-8", "utf8", "cp65001"):
                    host_encoding = pref
            except Exception:
                pass
        if host_encoding:
            _wrap_stdio_encoding(host_encoding)
        # B 端：invoke c.run 仍然强制 UTF-8 解码子进程 stdout bytes（容器/Podman 永远输出 UTF-8）
        subproc_encoding = "utf-8"

    _WIN32_STDOUT_TRANSCODE_READY = True
    cached = (subproc_encoding, is_tty)
    globals()["_WIN32_TRANSCODE_CACHED_RESULT"] = cached
    return cached


def _wrap_stdio_encoding(encoding_name: str) -> None:
    """把 sys.stdout/sys.stderr 的 TextIOWrapper 换壳为指定 encoding；失败静默跳过。"""
    import io
    for _io_name in ("stdout", "stderr"):
        _io = getattr(sys, _io_name)
        try:
            old_buf = _io.buffer
            line_buffering = getattr(_io, "line_buffering", True)
            write_through = getattr(_io, "write_through", False)
            try:
                _io.flush()
            except Exception:
                pass
            new_wrap = io.TextIOWrapper(
                old_buf,
                encoding=encoding_name,
                errors="replace",
                line_buffering=line_buffering,
                write_through=write_through,
            )
            setattr(sys, _io_name, new_wrap)
        except Exception:
            # 典型：被重定向成 StringIO / BytesIO 无 buffer 的对象 —— 不影响主流程
            pass


# 运行期单例结果缓存（避免每次 run_cmd 重新判别；但第一次必须真正初始化完毕后才写入）
_WIN32_TRANSCODE_CACHED_RESULT: tuple[str, bool] = ("", False)


# 兼容老命名（给任何可能存在的历史直接调用点留别名）
def _ensure_win32_console_utf8() -> None:
    _ensure_win32_stdout_transcode()
    return None
