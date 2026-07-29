#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpecWeave Python 3.10+ 版本校验库（可复用共享模块）
=====================================================
检测当前运行环境是否为 Python 3.10 或更高版本。
兼容 Python 3.8/3.9（用于显示友好错误提示），不使用 Python 3.10+ 专属语法。

使用方法：
    # 在 scripts/ 目录脚本中
    from pathlib import Path
    import sys
    _lib_dir = Path(__file__).parent
    sys.path.insert(0, str(_lib_dir))
    from python310_version_check import enforce_python310, check_python310

    # 方式1：直接强制执行（不符合版本就退出并显示友好错误）
    enforce_python310()

    # 方式2：先检查再处理
    if not check_python310():
        show_python310_error()
        sys.exit(1)

幂等安全：多次导入不会产生副作用。
"""

from __future__ import annotations

import sys
from typing import Dict, Any


_PYTHON310_CHECK_LOADED = True

# 最低要求版本
REQUIRED_MAJOR = 3
REQUIRED_MINOR = 10


def check_python310() -> bool:
    """
    检测当前 Python 版本是否满足 >= 3.10 要求。

    Returns:
        bool: True 表示版本满足要求，False 表示版本过低。
    """
    current = sys.version_info
    if current.major > REQUIRED_MAJOR:
        return True
    if current.major == REQUIRED_MAJOR and current.minor >= REQUIRED_MINOR:
        return True
    return False


def get_version_info() -> Dict[str, Any]:
    """
    获取当前 Python 版本详细信息。

    Returns:
        dict: 包含 major, minor, micro, version_str, is_64bit, implementation 等信息。
    """
    info: Dict[str, Any] = {
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro,
        "version_str": "{}.{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
        ),
        "is_64bit": sys.maxsize > 2**32,
        "implementation": sys.implementation.name,
        "executable": sys.executable,
    }
    return info


def show_python310_error() -> None:
    """
    显示友好的 Python 版本不支持错误信息。

    错误信息包含：
    - 当前 Python 版本信息
    - 所需版本说明
    - 各平台安装命令
    - 文档链接
    """
    info = get_version_info()
    is_64bit_str = "64-bit" if info["is_64bit"] else "32-bit"
    version_str = info["version_str"]
    impl = info["implementation"]

    print()
    print("=" * 60)
    print("  错误：Python 版本不满足要求")
    print("=" * 60)
    print()
    print("  当前 Python 信息：")
    print("    版本     : Python {} ({})".format(version_str, is_64bit_str))
    print("    实现     : {}".format(impl))
    print("    可执行文件: {}".format(info["executable"]))
    print()
    print("  问题说明：")
    print("    本脚本需要 Python 3.10 或更高版本。")
    print("    当前运行的是旧版本 Python {}.{}。".format(info["major"], info["minor"]))
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


def enforce_python310(skip_check: bool = False) -> None:
    """
    强制检查 Python 版本，不符合要求则显示错误并退出。

    Args:
        skip_check: 如果为 True，跳过版本检查（用于特殊场景）。
    """
    if skip_check:
        return
    if not check_python310():
        show_python310_error()
        sys.exit(1)


# 如果是直接运行此文件（而不是被导入），执行版本检查
if __name__ == "__main__":
    if check_python310():
        info = get_version_info()
        print("Python 版本检查通过: {} ({})".format(
            info["version_str"],
            "64-bit" if info["is_64bit"] else "32-bit",
        ))
        sys.exit(0)
    else:
        show_python310_error()
        sys.exit(1)
