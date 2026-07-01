"""CLI 输出格式化工具。

提供彩色终端输出、通用 argparse 参数注册等跨脚本复用的 CLI 能力。
"""

import argparse
import os
import sys
from pathlib import Path

from constants import ANSI_GREEN, ANSI_YELLOW, ANSI_RED, ANSI_RESET

_UTF8_ENCODINGS = frozenset({'utf8', 'utf8sig', 'cp65001'})


def _is_tty(stream=sys.stdout) -> bool:
    """安全检测 stream 是否为 TTY 终端。

    使用 getattr 保护，防止 stream 对象没有 isatty() 方法时抛出 AttributeError。
    """
    isatty = getattr(stream, 'isatty', None)
    if isatty is None or not callable(isatty):
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def _supports_unicode(stream=sys.stdout) -> bool:
    """检测指定 stream 是否支持 Unicode 符号输出。

    判断依据：
    1. stream 是 TTY（终端交互模式）
    2. 编码为 UTF-8 系列（utf-8、utf8-sig、cp65001 等 Windows UTF-8 代码页）
    3. 非 TTY（管道/重定向/测试捕获）或非 UTF-8 编码（如 GBK/CP936）时返回 False，
       回退到 ASCII 标签保证日志文件兼容性。

    所有访问均通过 getattr 防御，防止 stream 对象缺少属性时崩溃。
    """
    if not _is_tty(stream):
        return False
    encoding = getattr(stream, 'encoding', None)
    if not isinstance(encoding, str):
        return False
    normalized = encoding.lower().replace('-', '').replace('_', '')
    return normalized in _UTF8_ENCODINGS


def _symbol(kind: str) -> str:
    """根据当前终端能力返回状态符号（Unicode 符号或 ASCII 标签）。

    Unicode 模式：✓ / ⚠ / ✗（简洁符号，视觉清晰）
    ASCII 模式：[PASS] / [WARN] / [FAIL]（兼容 GBK 等窄编码终端和日志文件）

    传入无效 kind 时返回 [????] 而非抛出 KeyError，保证鲁棒性。
    """
    if _supports_unicode():
        return {'pass': '✓', 'warn': '⚠', 'error': '✗'}.get(kind, '?')
    return {'pass': '[PASS]', 'warn': '[WARN]', 'error': '[FAIL]'}.get(kind, '[????]')


def setup_safe_output() -> None:
    """配置 stdout/stderr 编码安全模式，防止 GBK 等窄编码终端因 emoji 等
    Unicode 字符输出而崩溃。

    三层防御体系：
    1. 环境变量层：设置 PYTHONIOENCODING 和 PYTHONUTF8
    2. 流重配置层：尝试将 stdout/stderr 重新配置为 UTF-8 编码
    3. 容错层：设置 errors='replace'，不可编码字符替换为 '?' 而非抛异常

    在 Windows 简体中文环境下，控制台默认使用 GBK 编码，无法编码 emoji 等
    特殊 Unicode 字符，会导致 UnicodeEncodeError。

    所有 CI 关键路径的统一入口脚本应在 main() 开头调用此函数。
    """
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None and callable(reconfigure):
            try:
                reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                try:
                    reconfigure(errors='replace')
                except Exception:
                    pass


# ── 彩色输出 ────────────────────────────────────────────────

def _color(msg: str, code: str, stream=sys.stdout) -> str:
    """包装 ANSI 颜色代码（仅在终端中启用）。"""
    if not _is_tty(stream):
        return msg
    return f"{code}{msg}{ANSI_RESET}"


def print_pass(msg: str) -> None:
    """打印通过信息（自适应符号格式）。"""
    print(f"  {_color(_symbol('pass'), ANSI_GREEN)} {msg}")


def print_warn(msg: str) -> None:
    """打印警告信息（自适应符号格式）。"""
    print(f"  {_color(_symbol('warn'), ANSI_YELLOW)} {msg}")


def print_error(msg: str) -> None:
    """打印错误信息（自适应符号格式）。"""
    print(f"  {_color(_symbol('error'), ANSI_RED)} {msg}")


def print_header(title: str, width: int = 60) -> None:
    """打印等宽分隔标题。"""
    print("=" * width)
    print(title)
    print("=" * width)


def print_summary(
    pass_count: int, warn_count: int, error_count: int, width: int = 60
) -> None:
    """打印彩色检查摘要。"""
    print("=" * width)
    parts = []
    if pass_count > 0:
        parts.append(f"{_color(f'通过 {pass_count} 项', ANSI_GREEN)}")
    if warn_count > 0:
        parts.append(f"{_color(f'警告 {warn_count} 项', ANSI_YELLOW)}")
    if error_count > 0:
        parts.append(f"{_color(f'错误 {error_count} 项', ANSI_RED)}")
    print(f"检查摘要: {', '.join(parts)}")
    print("=" * width)


# ── 通用 CLI 参数 ────────────────────────────────────────────

def add_common_args(parser: argparse.ArgumentParser) -> None:
    """注册跨脚本通用的 CLI 参数（--path、--json）。

    使用方式:
        parser = argparse.ArgumentParser(description="...")
        add_common_args(parser)
        parser.add_argument("--extra", ...)  # 脚本专属参数
    """
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="指定目标目录（默认为项目根目录下的默认路径）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出结果",
    )
