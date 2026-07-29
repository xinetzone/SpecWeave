#!/usr/bin/env python3
"""CMake 自定义模块命名冲突检查。

验证项目 cmake/ 目录下的自定义模块文件不使用 Find<Name>.cmake 命名规范，
该命名是 CMake 内置 find_package 模块的保留命名空间，使用会导致模块被意外加载、
覆盖内置 Find 模块或产生循环依赖等问题。

正确命名规范：
- 自定义检测模块使用 Detect<Name>.cmake（如 DetectBLAS.cmake）
- 配置模块使用 Config<Name>.cmake（如 ConfigCompiler.cmake）
- 工具模块使用 <Function>.cmake（如 ProtoCompile.cmake）

保留前缀（禁止用于自定义模块）：
- Find*   — CMake 内置 find_package 模块（FindBLAS.cmake、FindBoost.cmake 等）
- CMake*  — CMake 内部模块
- cmake*  — CMake 内部模块（小写）
- _*      — 私有/内部模块前缀

CLI 用法:
    python check-cmake-naming.py                   # 默认检查当前项目
    python check-cmake-naming.py --path /path/to   # 指定项目路径
    python check-cmake-naming.py --json            # JSON 输出
    python -m lib.checks.cmake_naming              # 模块方式调用
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from lib.cli import print_header, print_pass, print_error, print_warn, print_summary, setup_safe_output
from lib.project import resolve_project_root

_DEBUG = False

# CMake 保留命名前缀，自定义模块不得使用
RESERVED_PREFIXES = ("Find", "CMake", "cmake", "_")

# 标准 CMake 内置 Find 模块列表（常见示例，非穷举）
KNOWN_BUILTIN_FIND_MODULES = {
    "BLAS", "Boost", "CURL", "Curses", "Doxygen", "EXPAT", "FLEX",
    "FLTK", "GLEW", "GLUT", "GIF", "GTest", "GTK", "HDF5",
    "Iconv", "Intl", "JNI", "Java", "LAPACK", "LibXml2", "LibXslt",
    "Lua", "MPI", "Matlab", "OpenAL", "OpenGL", "OpenMP", "OpenSSL",
    "PNG", "PackageHandleStandardArgs", "PackageMessage", "Perl",
    "PhysFS", "PkgConfig", "PostgreSQL", "Protobuf", "Python3",
    "PythonInterp", "PythonLibs", "Qt", "QuickTime", "RTI", "Ruby",
    "SDL", "SWIG", "SelfPackers", "SQLite3", "Subversion", "TCL",
    "TIFF", "Threads", "Vulkan", "Wget", "X11", "ZLIB",
}

# 允许使用 Find 前缀的例外（通常是第三方提供的 find 模块）
ALLOWED_FIND_EXCEPTIONS: set[str] = set()


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def _debug(stage: str, msg: str) -> None:
    if not _DEBUG:
        return
    print(f"  [DEBUG:cmake-naming] [{stage}] {msg}", file=sys.stderr, flush=True)


def _is_reserved_filename(filename: str) -> tuple[bool, str]:
    """检查文件名是否使用保留前缀。

    返回 (是否保留, 原因说明)。
    """
    if not filename.endswith(".cmake"):
        return False, ""

    name = filename[:-len(".cmake")]

    # 检查保留前缀
    for prefix in RESERVED_PREFIXES:
        if name.startswith(prefix):
            # Find* 是最常见的冲突源
            if prefix == "Find":
                pkg_name = name[len("Find"):]
                if filename in ALLOWED_FIND_EXCEPTIONS:
                    return False, ""
                if pkg_name in KNOWN_BUILTIN_FIND_MODULES:
                    return True, f"文件名 {filename} 使用保留前缀 'Find' 且匹配已知内置模块 Find{pkg_name}.cmake，" \
                                  f"会与 CMake 内置 find_package({pkg_name}) 产生命名冲突"
                return True, f"文件名 {filename} 使用保留前缀 'Find'，" \
                              f"Find<pkg>.cmake 是 CMake find_package 的标准命名约定，" \
                              f"自定义检测模块应使用 Detect{pkg_name}.cmake 替代"
            if prefix in ("CMake", "cmake"):
                return True, f"文件名 {filename} 使用保留前缀 '{prefix}'，这是 CMake 内部模块的命名空间"
            if prefix == "_":
                return True, f"文件名 {filename} 以下划线开头，这是私有模块的约定命名，不建议用于项目自定义模块"

    return False, ""


def _find_cmake_dirs(project_root: Path) -> list[Path]:
    """发现项目中的 cmake 模块目录。

    搜索策略：
    1. 根目录的 cmake/ 或 CMake/ 目录
    2. 常见 CMake 模块位置
    3. 去重：Windows/macOS 默认大小写不敏感文件系统，cmake 和 CMake 可能指向同一目录
    """
    cmake_dirs: list[Path] = []
    seen_resolved: set[str] = set()

    candidates = [
        project_root / "cmake",
        project_root / "CMake",
        project_root / "cmake" / "Modules",
        project_root / "CMake" / "Modules",
    ]

    for c in candidates:
        if c.is_dir():
            resolved = str(c.resolve())
            if resolved not in seen_resolved:
                seen_resolved.add(resolved)
                cmake_dirs.append(c)
                _debug("discovery", f"发现 CMake 目录: {c}")
            else:
                _debug("discovery", f"跳过重复目录（大小写不敏感文件系统）: {c}")

    return cmake_dirs


def _scan_cmake_modules(cmake_dir: Path) -> tuple[list[dict], list[dict]]:
    """扫描单个 cmake 目录下的所有 .cmake 文件。

    返回 (问题列表, 通过列表)。
    """
    errors: list[dict] = []
    passes: list[dict] = []

    for cmake_file in sorted(cmake_dir.rglob("*.cmake")):
        rel_path = cmake_file.relative_to(cmake_dir.parent if cmake_dir.name in ("cmake", "CMake") else cmake_dir).as_posix()
        filename = cmake_file.name

        is_reserved, reason = _is_reserved_filename(filename)
        if is_reserved:
            errors.append({
                "file": str(cmake_file),
                "filename": filename,
                "rel_path": rel_path,
                "reason": reason,
            })
            _debug("scan", f"  ✗ {rel_path}: {reason}")
        else:
            passes.append({
                "file": str(cmake_file),
                "filename": filename,
                "rel_path": rel_path,
            })
            _debug("scan", f"  ✓ {rel_path}")

    # 额外检查：CMakeLists.txt 中 include() 命令引用的文件是否存在
    root_cmakelists = cmake_dir.parent / "CMakeLists.txt"
    if root_cmakelists.exists():
        _debug("scan", f"检查 CMakeLists.txt include 引用: {root_cmakelists}")
        content = root_cmakelists.read_text(encoding="utf-8", errors="replace")
        # 简单匹配 include(xxx) 模式
        for m in re.finditer(r'^\s*include\s*\(\s*([^)\s]+)', content, re.MULTILINE):
            included = m.group(1).strip()
            if not included.endswith(".cmake"):
                # include(xxx) 不带扩展名会自动查找 xxx.cmake
                included_file = cmake_dir / f"{included}.cmake"
                if not included_file.exists():
                    _debug("scan", f"  ⚠ include({included}): 引用的文件 {included_file} 不存在")

    return errors, passes


def run(project_root: Path, args) -> int:
    """CMake 命名检查主入口。

    返回退出码：0=通过，1=有错误。
    """
    debug = getattr(args, "debug", False)
    use_json = getattr(args, "json", False)
    _set_debug(debug)

    _t_total_start = time.perf_counter()

    errors = 0
    warnings = 0
    passes = 0
    results: dict = {
        "tool": "cmake-naming-check",
        "version": "1.0.0",
        "project_root": str(project_root),
        "checks": [],
        "summary": {},
    }

    def _record(name: str, status: str, message: str, details: list | None = None) -> None:
        entry = {"name": name, "status": status, "message": message}
        if details:
            entry["details"] = details
        results["checks"].append(entry)

    cmake_dirs = _find_cmake_dirs(project_root)

    if not cmake_dirs:
        if use_json:
            _record("cmake_dirs", "pass", "未发现 cmake/ 目录（项目可能不使用自定义 CMake 模块）")
            results["summary"] = {"pass": 1, "warn": 0, "error": 0}
            results["passed"] = True
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_header("CMake 自定义模块命名检查")
            print()
            print_pass("未发现 cmake/ 目录（项目可能不使用自定义 CMake 模块）")
            print()
            print_summary(1, 0, 0)
        return 0

    if not use_json:
        print_header("CMake 自定义模块命名检查")
        print()
        print(f"  扫描目录: {', '.join(str(d) for d in cmake_dirs)}")
        print()

    all_errors: list[dict] = []
    all_passes: list[dict] = []

    for cmake_dir in cmake_dirs:
        _debug("run", f"扫描目录: {cmake_dir}")
        dir_errors, dir_passes = _scan_cmake_modules(cmake_dir)
        all_errors.extend(dir_errors)
        all_passes.extend(dir_passes)

    if all_errors:
        for err in all_errors:
            msg = f"{err['rel_path']}: {err['reason']}"
            if use_json:
                _record("naming", "error", msg)
            else:
                print_error(msg)
                # 给出修复建议
                filename = err["filename"]
                if filename.startswith("Find"):
                    pkg = filename[4:-6]  # FindXXX.cmake -> XXX
                    print(f"    建议: 重命名为 Detect{pkg}.cmake，并更新 CMakeLists.txt 中的 include 引用")
            errors += 1
    else:
        msg = f"所有 {len(all_passes)} 个 CMake 自定义模块命名合规"
        if use_json:
            _record("naming", "pass", msg)
        else:
            print_pass(msg)
        passes = len(all_passes)

    total_ms = (time.perf_counter() - _t_total_start) * 1000

    if use_json:
        results["summary"] = {"pass": passes, "warn": warnings, "error": errors}
        results["total_files_scanned"] = len(all_passes) + len(all_errors)
        results["passed"] = errors == 0
        results["total_duration_ms"] = round(total_ms, 1)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print()
        print_summary(passes, warnings, errors)
        print()
        print(f"  总耗时: {total_ms:.1f}ms")
        print()

        if errors > 0:
            print_error("检查未通过，请修复上述命名冲突问题")
            return 1
        print_pass("CMake 命名检查通过！")

    return 0 if errors == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="cmake-naming-check",
        description="CMake 自定义模块命名冲突检查：防止自定义模块使用 Find<Name>.cmake 等保留前缀",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命名规范说明：
  自定义检测模块  → Detect<Name>.cmake  (如 DetectBLAS.cmake)
  配置模块        → Config<Name>.cmake  (如 ConfigCompiler.cmake)
  工具函数模块    → <Function>.cmake    (如 ProtoCompile.cmake)
  禁止使用        → Find<Name>.cmake    (CMake 内置 find_package 保留命名)

示例:
  python check-cmake-naming.py                  # 检查当前项目
  python check-cmake-naming.py --path ./build   # 指定项目路径
  python check-cmake-naming.py --json           # JSON 输出（CI 集成）
  python -m lib.checks.cmake_naming             # 模块方式调用
        """,
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="指定项目根目录路径（默认自动发现项目根）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="输出详细调试日志到 stderr",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出检查结果（用于 CI 集成）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="cmake-naming-check 1.0.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """独立 CLI 入口。"""
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = resolve_project_root(__file__)

    return run(project_root, args)


if __name__ == "__main__":
    sys.exit(main())
