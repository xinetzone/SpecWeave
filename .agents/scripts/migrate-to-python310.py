#!/usr/bin/env python3
"""Python 3.10+ 迁移辅助脚本。

自动为 Python 脚本添加 Python 3.10+ 版本校验代码块。

迁移策略：
  1. 已有版本校验代码的脚本：跳过
  2. 包含 # PY310-EXEMPT: 的脚本：跳过
  3. __init__.py 文件：跳过（无顶层可执行代码时自动合规）
  4. 无版本校验的脚本：在合适位置插入版本校验代码

迁移模式（自动根据文件位置选择）：
  - lib/ 目录下文件：from .python310_version_check import enforce_python310
  - scripts/ 目录下文件（非 lib）：添加lib路径后导入
  - 其他位置文件：内联版本校验块（自包含，兼容3.8/3.9语法）

默认使用 DRY-RUN 预览模式，使用 --apply 参数实际执行修改。
"""

from __future__ import annotations

# ==============================================================================
# 版本校验（启动时立即执行，兼容 Python 3.8/3.9 语法）
# ==============================================================================
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root
from lib.cli import print_header, print_summary, print_warn, print_error, print_pass, setup_safe_output

EXCLUDE_DIR_EXACT = {
    "vendor",
    "projects",
    "__pycache__",
    ".temp",
    "temp",
    "playground",
    ".git",
    ".trae",
    "node_modules",
    ".eggs",
    ".venv",
    "venv",
    "docs",
    ".agents/docs",
}
EXCLUDE_DIR_PATTERNS = (
    re.compile(r".*[.-]venv$", re.IGNORECASE),
)
EXCLUDE_DIR_SUFFIXES = (".egg-info",)

EXEMPT_RE = re.compile(r"#\s*PY310-EXEMPT\s*:?\s*(.*)", re.IGNORECASE)

# 检测是否已有版本校验
VERSION_INFO_RE = re.compile(r"sys\.version_info", re.MULTILINE)
VERSION_COMPARE_RE = re.compile(
    r"(?:version_info|\w+)\.(?:major|minor)\s*[<>=!]+\s*\d+|"
    r"version_info\s*[>=<!]+\s*\(\s*3\s*,\s*10|"
    r"python310_version_check|check_python310|enforce_python310",
    re.MULTILINE
)
VERSION_ERROR_MSG_RE = re.compile(
    r"Python\s*版本|需要\s*Python|版本不满足|版本不支持|python3\.10|3\.10\s*或更高|"
    r"winget\s+install\s+Python\.Python|conda\s+create|pyenv\s+install",
    re.IGNORECASE | re.MULTILINE
)

# Shebang 和编码声明
SHEBANG_RE = re.compile(r"^#!\s*/usr/bin/env\s+python3?\b[^\n]*\n?", re.MULTILINE)
CODING_RE = re.compile(r"^#.*?-\*-\s*coding[:=]\s*([-\w.]+)\s*-\*-[^\n]*\n?", re.MULTILINE | re.IGNORECASE)

# docstring（三引号开头，匹配多行）
DOCSTRING_START_RE = re.compile(r'^\s*("""|\'\'\')', re.MULTILINE)


# ── 版本校验块模板 ─────────────────────────────────────────────────────────

# 内联版本校验块（自包含，兼容 Python 3.8/3.9 语法）
INLINE_VERSION_CHECK_BLOCK = '''\
# ==============================================================================
# 版本校验（自包含，不依赖外部 lib 文件，兼容 Python 3.8/3.9）
# ==============================================================================
import sys as _sys


def _check_python310() -> bool:
    """检测当前 Python 版本是否满足 >= 3.10 要求。"""
    current = _sys.version_info
    if current.major > 3:
        return True
    if current.major == 3 and current.minor >= 10:
        return True
    return False


def _show_python310_error() -> None:
    """显示 Python 3.10+ 版本要求错误信息并退出。"""
    current = _sys.version_info
    current_version = f"{current.major}.{current.minor}.{current.micro}"
    print()
    print("=" * 50)
    print("  错误：Python 版本不支持")
    print("=" * 50)
    print()
    print(f"  当前 Python 版本: {current_version}")
    print()
    print("  问题说明：")
    print("    本脚本需要 Python 3.10 或更高版本。")
    print("    当前运行的是旧版本或不兼容版本。")
    print()
    print("  安装命令（Windows）：")
    print("    winget install Python.Python.3.12")
    print()
    print("  或使用 conda：")
    print("    conda create -n specweave python=3.12")
    print("    conda activate specweave")
    print()
    print("  或使用 pyenv：")
    print("    pyenv install 3.12.0")
    print("    pyenv local 3.12.0")
    print()
    print("  文档提示：")
    print("    请参考项目 ONBOARDING.md 配置开发环境。")
    print()
    print("=" * 50)
    print()


def _enforce_python310() -> None:
    """强制要求 Python 3.10+，版本不满足则显示错误并退出。"""
    if not _check_python310():
        _show_python310_error()
        _sys.exit(1)


_enforce_python310()

'''

# lib/ 目录下文件：使用相对导入（根据嵌套深度动态生成点数）
# depth=0 (lib/xxx.py)         → from .python310_version_check
# depth=1 (lib/sub/xxx.py)     → from ..python310_version_check
# depth=2 (lib/sub/sub/xxx.py) → from ...python310_version_check
def _make_lib_version_check_block(file_path: Path) -> str:
    """根据文件在lib/下的嵌套深度生成正确的相对导入版本校验块。"""
    # 找到lib在路径中的位置，计算相对深度
    try:
        lib_idx = list(file_path.parts).index("lib")
    except ValueError:
        lib_idx = -1
    # 相对于lib/的目录深度：文件名前面有几个部分在lib/之后
    # e.g. lib/foo.py → parts after lib: ["foo.py"] → depth=0
    #       lib/sub/foo.py → parts after lib: ["sub", "foo.py"] → depth=1
    parts_after_lib = file_path.parts[lib_idx + 1:]
    depth = len(parts_after_lib) - 1  # 减去文件名本身
    dots = "." * (depth + 1)
    return (
        f"# 版本校验：相对导入共享库（depth={depth}）\n"
        f"from {dots}python310_version_check import enforce_python310\n"
        f"\n"
        f"enforce_python310()\n"
    )

# scripts/ 目录下文件（非 lib）：动态查找lib/目录后导入
# 使用向上遍历方式定位lib/，兼容任意嵌套深度（scripts/*.py, scripts/mdi/*.py, scripts/mdi/sub/*.py）
SCRIPT_VERSION_CHECK_BLOCK = '''\
# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

'''


def _is_lib_file(file_path: Optional[Path]) -> bool:
    """判断文件是否位于 lib/ 目录下（应使用相对导入模式）。"""
    if file_path is None:
        return False
    return "lib" in file_path.parts and file_path.name != "__init__.py"


def _is_script_in_scripts_dir(file_path: Optional[Path]) -> bool:
    """判断文件是否位于 scripts/ 目录下（但不在 lib/ 子目录中）。"""
    if file_path is None:
        return False
    parts = file_path.parts
    if "lib" in parts:
        return False
    return "scripts" in parts


def _get_lib_depth(file_path: Path) -> int:
    """计算文件相对于lib/目录的嵌套深度。"""
    try:
        lib_idx = list(file_path.parts).index("lib")
    except ValueError:
        return 0
    parts_after_lib = file_path.parts[lib_idx + 1:]
    return len(parts_after_lib) - 1


def _get_version_check_block(file_path: Optional[Path]) -> Tuple[str, str]:
    """根据文件位置返回合适的版本校验块和描述。"""
    if _is_lib_file(file_path):
        depth = _get_lib_depth(file_path)
        dots = "." * (depth + 1)
        return _make_lib_version_check_block(file_path).rstrip("\n"), f"插入相对导入版本校验(lib模式, depth={depth}, import={dots}python310_version_check)"
    if _is_script_in_scripts_dir(file_path):
        return SCRIPT_VERSION_CHECK_BLOCK.rstrip("\n"), "插入路径导入版本校验(scripts模式)"
    return INLINE_VERSION_CHECK_BLOCK.rstrip("\n"), "插入内联版本校验块"


def is_excluded_dir(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    for part in rel_parts:
        if part in EXCLUDE_DIR_EXACT:
            return True
        for suffix in EXCLUDE_DIR_SUFFIXES:
            if part.endswith(suffix):
                return True
        for pattern in EXCLUDE_DIR_PATTERNS:
            if pattern.match(part):
                return True
    return False


def collect_py_files(root: Path) -> List[Path]:
    result: List[Path] = []
    if root.is_file() and root.suffix.lower() == ".py":
        result.append(root)
        return result
    for path in sorted(root.rglob("*.py")):
        if not path.is_file():
            continue
        if is_excluded_dir(path, root):
            continue
        result.append(path)
    return result


def read_py_file(file_path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "gbk", "cp936"]
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return file_path.read_text(encoding="utf-8", errors="replace")


def write_py_file(file_path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    # Python文件统一使用LF换行符
    file_path.write_text(normalized + "\n", encoding="utf-8", newline="\n")


def has_version_check(content: str) -> bool:
    """检测内容中是否已包含版本校验代码。"""
    has_version_info = bool(VERSION_INFO_RE.search(content))
    has_version_compare = bool(VERSION_COMPARE_RE.search(content))
    has_error_msg = bool(VERSION_ERROR_MSG_RE.search(content))
    
    # 检查共享库导入
    has_shared_lib = "python310_version_check" in content and "enforce_python310" in content
    
    # 内联模式：有version_info + 版本比较 + 错误提示
    has_inline = has_version_info and has_version_compare and has_error_msg
    
    return has_inline or has_shared_lib


def find_insert_position(content: str) -> int:
    """分析Python脚本结构，确定版本校验块的插入位置。
    
    插入顺序：shebang → 编码声明 → docstring → 版本校验块 → 其他代码
    """
    pos = 0
    
    # 跳过 shebang
    shebang_match = SHEBANG_RE.match(content, pos)
    if shebang_match:
        pos = shebang_match.end()
    
    # 跳过编码声明（可能在shebang后）
    while True:
        # 跳过空行
        while pos < len(content) and content[pos] in "\r\n\t ":
            if content[pos] in "\r\n":
                pos += 1
                if pos < len(content) and content[pos-1] == '\r' and content[pos] == '\n':
                    pos += 1
            else:
                pos += 1
        
        coding_match = CODING_RE.match(content, pos)
        if coding_match:
            pos = coding_match.end()
        else:
            break
    
    # 跳过空行
    while pos < len(content) and content[pos] in "\r\n\t ":
        if content[pos] in "\r\n":
            pos += 1
            if pos < len(content) and content[pos-1] == '\r' and content[pos] == '\n':
                pos += 1
        else:
            pos += 1
    
    # 跳过模块级 docstring
    docstring_match = DOCSTRING_START_RE.match(content, pos)
    if docstring_match:
        quote = docstring_match.group(1)
        # 找到匹配的结束三引号
        start_pos = docstring_match.end()
        # 先检查单行docstring情况："""内容"""
        end_quote = content.find(quote, start_pos)
        if end_quote != -1:
            # 检查是不是结束（不是转义的）
            pos = end_quote + len(quote)
            # 跳过docstring后的换行
            while pos < len(content) and content[pos] in "\r\n\t ":
                if content[pos] in "\r\n":
                    pos += 1
                    if pos < len(content) and content[pos-1] == '\r' and content[pos] == '\n':
                        pos += 1
                else:
                    pos += 1
    
    # 跳过 from __future__ import 语句（必须在最前面）
    while True:
        while pos < len(content) and content[pos] in "\r\n\t ":
            if content[pos] in "\r\n":
                pos += 1
                if pos < len(content) and content[pos-1] == '\r' and content[pos] == '\n':
                    pos += 1
            else:
                pos += 1
        future_match = re.match(r'^from\s+__future__\s+import\s+[^\n]+\n?', content[pos:], re.MULTILINE)
        if future_match:
            pos += future_match.end()
        else:
            break
    
    return pos


def migrate_content(content: str, file_path: Optional[Path] = None) -> Tuple[str, str, bool]:
    """迁移单个Python脚本内容，返回(新内容, 操作描述, 是否修改)。"""
    # 检查豁免标记
    exempt_match = EXEMPT_RE.search(content)
    if exempt_match:
        reason = exempt_match.group(1).strip() or "未指定原因"
        return content, f"豁免标记：{reason}", False
    
    # __init__.py 跳过
    if file_path and file_path.name == "__init__.py":
        return content, "__init__.py自动跳过", False
    
    # 已包含版本校验
    if has_version_check(content):
        return content, "已包含版本校验代码", False
    
    # 确定插入位置
    insert_pos = find_insert_position(content)
    
    # 获取合适的版本校验块
    block, block_desc = _get_version_check_block(file_path)
    
    # 处理前后空行
    prefix = ""
    suffix = ""
    
    # 前面有内容时，添加换行
    if insert_pos > 0:
        # 确保插入位置前有换行
        before_char = content[insert_pos-1] if insert_pos > 0 else ""
        if before_char not in "\r\n":
            prefix = "\n\n"
        elif before_char in "\r\n":
            # 检查是否有足够的空行
            # 简单处理：在插入前添加一个空行
            prefix = "\n"
    else:
        prefix = ""
    
    # 后面有内容时，添加换行
    if insert_pos < len(content):
        after_char = content[insert_pos] if insert_pos < len(content) else ""
        if after_char not in "\r\n":
            suffix = "\n\n"
        elif after_char in "\r\n":
            suffix = "\n"
    
    new_content = content[:insert_pos] + prefix + block + suffix + content[insert_pos:]
    
    # 清理多余空行
    while "\n\n\n\n" in new_content:
        new_content = new_content.replace("\n\n\n\n", "\n\n\n")
    
    return new_content, block_desc, True


@dataclass
class FileResult:
    file_path: Path
    rel_path: Path
    status: str
    message: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python 3.10+ 迁移辅助脚本 - 自动添加版本校验代码",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="迁移根路径或单个 .py 文件（默认为项目根目录）",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        dest="apply_mode",
        action="store_false",
        help="预览模式（默认），不实际修改文件",
    )
    mode_group.add_argument(
        "--apply",
        dest="apply_mode",
        action="store_true",
        help="实际执行修改",
    )
    parser.set_defaults(apply_mode=False)
    return parser


def main() -> int:
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(args.path).resolve() if args.path else resolve_project_root(__file__)

    py_files = collect_py_files(project_root)
    results: List[FileResult] = []

    mode_str = "APPLY模式" if args.apply_mode else "DRY-RUN模式"

    print_header(f"Python 3.10+ Migration Assistant ({mode_str})")
    print(f"迁移根路径: {project_root}")
    print(f"待处理文件数: {len(py_files)}")
    print()

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in py_files:
        if project_root.is_file():
            rel_path = file_path.name
        else:
            try:
                rel_path = file_path.relative_to(project_root)
            except ValueError:
                rel_path = file_path

        try:
            content = read_py_file(file_path)
        except Exception as e:
            results.append(FileResult(file_path, rel_path, "ERROR", f"读取失败: {e}"))
            error_count += 1
            print(f"  ERROR: {rel_path} - 读取失败: {e}")
            continue

        new_content, action, changed = migrate_content(content, file_path)

        if not changed:
            results.append(FileResult(file_path, rel_path, "SKIP", action))
            skipped_count += 1
            print(f"  SKIP: {rel_path} - {action}")
            continue

        results.append(FileResult(file_path, rel_path, "MIGRATE", action))
        migrated_count += 1
        print(f"  MIGRATE: {rel_path} - {action}")

        if args.apply_mode:
            try:
                write_py_file(file_path, new_content)
            except Exception as e:
                print(f"    ERROR: 写入失败: {e}")
                error_count += 1

    print()
    total = len(py_files)
    if args.apply_mode:
        if migrated_count == 0 and error_count == 0:
            print_pass(f"所有 {total} 个 Python 脚本均无需迁移（{skipped_count} 跳过）")
        else:
            msg = f"已迁移 {migrated_count} 个文件，跳过 {skipped_count} 个文件"
            if error_count > 0:
                msg += f"，{error_count} 个错误"
                print_error(msg)
            else:
                print_pass(msg)
    else:
        if migrated_count == 0:
            print_pass(f"所有 {total} 个 Python 脚本均无需迁移（{skipped_count} 跳过）")
        else:
            print_warn(f"预览：将迁移 {migrated_count} 个文件，跳过 {skipped_count} 个文件（使用 --apply 实际执行）")

    print_summary(
        pass_count=skipped_count,
        warn_count=migrated_count if not args.apply_mode else 0,
        error_count=error_count,
    )

    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
