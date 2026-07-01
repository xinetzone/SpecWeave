"""CLI 输出格式化工具。

提供彩色终端输出、通用 argparse 参数注册等跨脚本复用的 CLI 能力。
"""

import argparse
import sys
from pathlib import Path

from constants import ANSI_GREEN, ANSI_YELLOW, ANSI_RED, ANSI_RESET


def setup_safe_output() -> None:
    """配置 stdout/stderr 编码安全模式，防止 GBK 等窄编码终端因 emoji 等
    Unicode 字符输出而崩溃。

    在 Windows 简体中文环境下，控制台默认使用 GBK 编码，无法编码 emoji 等
    特殊 Unicode 字符，会导致 UnicodeEncodeError。此函数将 stdout/stderr
    重新配置为 errors='replace' 模式，不可编码字符将替换为 '?' 而非抛异常。

    所有 CI 关键路径的统一入口脚本应在 main() 开头调用此函数。
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(errors='replace')
            except Exception:
                pass


# ── 彩色输出 ────────────────────────────────────────────────

def _color(msg: str, code: str) -> str:
    """包装 ANSI 颜色代码（仅在终端中启用）。"""
    if not sys.stdout.isatty():
        return msg
    return f"{code}{msg}{ANSI_RESET}"


def print_pass(msg: str) -> None:
    """打印绿色 [PASS] 通过信息。"""
    print(f"  {_color('✓ [PASS]', ANSI_GREEN)} {msg}")


def print_warn(msg: str) -> None:
    """打印黄色 [WARN] 警告信息。"""
    print(f"  {_color('⚠ [WARN]', ANSI_YELLOW)} {msg}")


def print_error(msg: str) -> None:
    """打印红色 [FAIL] 错误信息。"""
    print(f"  {_color('✗ [FAIL]', ANSI_RED)} {msg}")


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
