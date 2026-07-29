#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SpecWeave 项目标准 Python 3.10+ 脚本模板
==============================================================================
使用说明：
  1. 复制本模板到目标位置，重命名为你的脚本名称
  2. 修改模块docstring，描述脚本功能
  3. 根据需要删除或修改示例参数、辅助函数
  4. 在"主流程开始"区域编写你的业务逻辑
  5. 版本校验代码为自包含，无需依赖外部 lib 文件
  6. shebang 用 #!/usr/bin/env python3 是为了让旧版本 Python 也能启动，
     实际运行要求为 Python 3.10+，版本不符会由自包含检测代码拦截
==============================================================================
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# ==============================================================================
# Python 3.10+ 版本校验（自包含，不依赖外部 lib 文件）
# 兼容 Python 3.8/3.9 语法（不使用 match、| 联合类型、zip(strict=True) 等）
# ==============================================================================

def _check_python310() -> bool:
    """内部函数：检测当前 Python 版本是否满足 >= 3.10 要求。"""
    current = sys.version_info
    if current.major > 3:
        return True
    if current.major == 3 and current.minor >= 10:
        return True
    return False


def _show_python310_error() -> None:
    """内部函数：显示友好的 Python 版本不支持错误信息。"""
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    is_64bit = sys.maxsize > 2**32
    is_64bit_str = "64-bit" if is_64bit else "32-bit"
    version_str = "{}.{}.{}".format(major, minor, micro)
    impl = sys.implementation.name

    print()
    print("=" * 60)
    print("  错误：Python 版本不满足要求")
    print("=" * 60)
    print()
    print("  当前 Python 信息：")
    print("    版本     : Python {} ({})".format(version_str, is_64bit_str))
    print("    实现     : {}".format(impl))
    print("    可执行文件: {}".format(sys.executable))
    print()
    print("  问题说明：")
    print("    本脚本需要 Python 3.10 或更高版本。")
    print("    当前运行的是旧版本 Python {}.{}。".format(major, minor))
    print()
    print("  安装命令（选择适合你的方式）：")
    print()
    print("  [Windows]")
    print("    winget install Python.Python.3.12   # Python 3.12（推荐）")
    print("    或从官网下载: https://www.python.org/downloads/")
    print("    conda: conda create -n specweave python=3.12")
    print()
    print("  [macOS]")
    print("    brew install python@3.12")
    print("    或使用 pyenv: brew install pyenv && pyenv install 3.12.0")
    print()
    print("  [Linux (Ubuntu/Debian)]")
    print("    sudo add-apt-repository ppa:deadsnakes/ppa")
    print("    sudo apt update && sudo apt install python3.12 python3.12-venv")
    print()
    print("  [Linux (Fedora/RHEL)]")
    print("    sudo dnf install python3.12")
    print()
    print("  文档提示：")
    print("    请参考项目 ONBOARDING.md 配置开发环境。")
    print()
    print("=" * 60)
    print()


def _enforce_python310() -> None:
    """内部函数：强制执行版本检查，不符合要求则退出。"""
    if not _check_python310():
        _show_python310_error()
        sys.exit(1)


# 脚本启动时立即执行版本检查
_enforce_python310()

# ==============================================================================
# 全局配置与编码设置
# ==============================================================================

def _setup_safe_output() -> None:
    """配置 stdout/stderr 编码安全模式，防止 GBK 等窄编码终端崩溃。"""
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None and callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                try:
                    reconfigure(errors="replace")
                except Exception:
                    pass


_setup_safe_output()

# ==============================================================================
# ANSI 颜色输出工具
# ==============================================================================

_ANSI_GREEN = "\033[92m"
_ANSI_YELLOW = "\033[93m"
_ANSI_RED = "\033[91m"
_ANSI_CYAN = "\033[96m"
_ANSI_RESET = "\033[0m"


def _supports_color() -> bool:
    """检测是否支持彩色输出。"""
    isatty = getattr(sys.stdout, "isatty", None)
    if isatty is None or not callable(isatty):
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def _color(text: str, color_code: str) -> str:
    """包装 ANSI 颜色代码（仅在终端中启用）。"""
    if not _supports_color():
        return text
    return "{}{}{}".format(color_code, text, _ANSI_RESET)


def print_info(message: str) -> None:
    """输出信息级日志（绿色）。"""
    print(_color("[INFO] {}".format(message), _ANSI_GREEN))


def print_warn(message: str) -> None:
    """输出警告级日志（黄色）。"""
    print(_color("[WARN] {}".format(message), _ANSI_YELLOW))


def print_error(message: str) -> None:
    """输出错误级日志（红色）。"""
    print(_color("[ERROR] {}".format(message), _ANSI_RED))


def print_step(title: str) -> None:
    """输出步骤标题（青色分隔线）。"""
    print()
    print(_color("=" * 40, _ANSI_CYAN))
    print(_color("  {}".format(title), _ANSI_CYAN))
    print(_color("=" * 40, _ANSI_CYAN))


# ==============================================================================
# 命令行参数解析
# ==============================================================================

def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="脚本功能简述（请替换此描述）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python %(prog)s                          # 基础用法
  python %(prog)s --path /path/to/target   # 指定路径
  python %(prog)s --dry-run                # 试运行模式
  python %(prog)s --verbose                # 详细输出
        """,
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="目标路径（默认：当前工作目录）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，不执行实际修改操作",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细输出",
    )
    return parser


# ==============================================================================
# 辅助函数区域
# ==============================================================================

def example_helper_function(value: str) -> str:
    """示例辅助函数（请根据实际需求修改或删除）。"""
    return "processed: {}".format(value)


# ==============================================================================
# 主流程
# ==============================================================================

def main() -> int:
    """脚本主入口函数。"""
    parser = build_parser()
    args = parser.parse_args()

    target_path: Path = args.path
    dry_run: bool = args.dry_run
    verbose: bool = args.verbose

    print_step("脚本启动")
    print_info("Python 版本: {}.{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    ))
    print_info("工作目录: {}".format(target_path))
    if dry_run:
        print_warn("DryRun 模式已启用，不会执行实际修改操作")
    if verbose:
        print_info("详细输出模式已启用")

    # TODO: 在此处编写你的业务逻辑
    print()
    print_info("在此处添加你的脚本逻辑...")
    result = example_helper_function("test")
    if verbose:
        print_info("示例处理结果: {}".format(result))
    print()

    print_step("执行完成")
    print_info("脚本执行完毕")
    return 0


if __name__ == "__main__":
    sys.exit(main())
