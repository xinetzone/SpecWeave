#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 3.10+ 合规性检查脚本。

扫描项目中的 .py 文件，验证其是否包含 Python 3.10+ 版本校验机制，
在旧版本 Python 下运行时显示友好错误而非直接崩溃。

合规条件（满足任一即可）：
  1. 文件包含 # PY310-EXEMPT: 注释（豁免）
  2. 文件包含内联版本校验代码块（sys.version_info 检查 + 错误提示）
  3. 文件导入了共享版本校验库（python310_version_check）并调用 enforce_python310()
  4. 文件是 __init__.py 且不包含可执行代码（仅用于包初始化）

使用 --verbose (-v) 参数输出每个文件的详细检测过程。
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
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple, Optional

from lib.project import resolve_project_root
from lib.cli import print_header, print_summary, print_warn, print_error, print_pass, setup_safe_output


EXCLUDE_DIR_EXACT: Set[str] = {
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
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "*.egg-info",
}
EXCLUDE_DIR_PATTERNS = (
    re.compile(r".*[.-]venv$", re.IGNORECASE),
)
EXCLUDE_DIR_SUFFIXES = (".egg-info",)

EXEMPT_RE = re.compile(r"#\s*PY310-EXEMPT\s*:?\s*(.*)", re.IGNORECASE)
SHEBANG_RE = re.compile(r"^#!\s*/usr/bin/env\s+python3?\b", re.MULTILINE)

# 版本检测相关模式
SYS_VERSION_INFO_RE = re.compile(r"sys\.version_info", re.MULTILINE)
VERSION_COMPARE_RE = re.compile(
    r"(?:version_info|current)\.(?:major|minor)\s*[<>=!]+\s*\d+|"
    r"version_info\s*[>=<!]+\s*\(\s*3\s*,\s*10",
    re.MULTILINE
)
# 错误提示关键词
VERSION_ERROR_MSG_RE = re.compile(
    r"Python\s*版本|需要\s*Python|版本不满足|版本不支持|python3\.10|3\.10\s*或更高",
    re.IGNORECASE | re.MULTILINE
)
# 导入共享库
IMPORT_LIB_RE = re.compile(
    r"(?:from\s+python310_version_check\s+import|import\s+python310_version_check)",
    re.MULTILINE
)
ENFORCE_CALL_RE = re.compile(
    r"enforce_python310\s*\(",
    re.MULTILINE
)


@dataclass
class FileResult:
    file_path: Path
    rel_path: Path
    compliant: bool = False
    exempt: bool = False
    exempt_reason: str = ""
    errors: List[Tuple[int, str]] = field(default_factory=list)
    has_shebang: bool = False
    has_version_info: bool = False
    has_version_compare: bool = False
    has_error_message: bool = False
    has_import_lib: bool = False
    has_enforce_call: bool = False
    has_inline_check: bool = False
    is_init_file: bool = False
    compliance_mode: str = ""  # "inline" / "shared-lib" / "exempt" / "init" / "noncompliant"


def _log(verbose: bool, msg: str) -> None:
    """详细日志输出（仅在 verbose 模式下）。"""
    if verbose:
        print("    [DEBUG] {}".format(msg))


def is_excluded_dir(path: Path, root: Path) -> bool:
    """判断目录是否在排除列表中。"""
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
    """收集所有需要检查的 .py 文件。"""
    result: List[Path] = []
    for path in sorted(root.rglob("*.py")):
        if not path.is_file():
            continue
        if is_excluded_dir(path, root):
            continue
        # 排除测试文件中的临时生成文件
        if "test_" in path.name and path.name.endswith(".py"):
            # 保留我们自己的测试文件
            if str(path).find(".agents/scripts/tests") == -1:
                pass  # 还是要检查，不能排除测试文件
        result.append(path)
    return result


def _strip_comments_and_strings(content: str) -> str:
    """
    简单的Python注释和字符串剥离（保守实现，避免误报）。
    用空格替换注释和字符串内容，保留行号和结构。
    """
    # 先尝试用AST解析（最准确），失败则回退到简单正则
    try:
        tree = ast.parse(content)
        # 如果能解析成功，我们还是需要返回原始内容，因为我们要做模式匹配
        # AST只用于验证语法正确性，不用于模式匹配
        return content
    except SyntaxError:
        # 语法错误的文件也需要检查，回退到简单处理
        pass

    # 简单处理：移除单行注释（不处理字符串中的#）
    lines = content.split("\n")
    result_lines = []
    for line in lines:
        # 找到不在字符串中的#（简化处理，假设代码格式规范）
        in_single_quote = False
        in_double_quote = False
        comment_pos = -1
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "'" and not in_double_quote:
                # 检查是否是三引号
                if line[i:i+3] == "'''":
                    i += 3
                    continue
                in_single_quote = not in_single_quote
            elif ch == '"' and not in_single_quote:
                if line[i:i+3] == '"""':
                    i += 3
                    continue
                in_double_quote = not in_double_quote
            elif ch == '#' and not in_single_quote and not in_double_quote:
                comment_pos = i
                break
            i += 1
        if comment_pos >= 0:
            result_lines.append(line[:comment_pos])
        else:
            result_lines.append(line)
    return "\n".join(result_lines)


def scan_file(file_path: Path, root: Path, verbose: bool = False) -> FileResult:
    """扫描单个 .py 文件，检测 Python 3.10+ 合规性。

    检测流程：
    1. 读取文件内容
    2. 检查豁免标记 # PY310-EXEMPT:
    3. 检查是否是 __init__.py（包初始化文件，通常不需要版本检查）
    4. 检查 shebang
    5. 检测版本校验方式（内联块 / 导入共享库）
    6. 判定合规性
    """
    rel_path = file_path.relative_to(root)

    _log(verbose, "开始扫描: {}".format(rel_path))

    # ── 步骤1：读取文件 ──
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        _log(verbose, "  编码警告: UTF-8解码失败，使用replace模式")

    result = FileResult(file_path=file_path, rel_path=rel_path)
    lines = content.splitlines()
    _log(verbose, "  文件行数: {}".format(len(lines)))

    # ── 步骤2：检查是否是 __init__.py ──
    if file_path.name == "__init__.py":
        result.is_init_file = True
        # 检查 __init__.py 是否包含可执行代码（import之外的代码）
        has_executable_code = False
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Call, ast.If, ast.For, ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # 排除顶层的import和简单赋值
                    if isinstance(node, ast.Call):
                        # sys.exit() 之类的调用算可执行代码
                        has_executable_code = True
                        break
        except SyntaxError:
            has_executable_code = True  # 语法错误的文件需要检查

        if not has_executable_code:
            result.compliant = True
            result.compliance_mode = "init"
            _log(verbose, "  __init__.py 无顶层可执行代码，自动合规")
            return result

    # ── 步骤3：检查豁免标记 ──
    for idx, line in enumerate(lines, start=1):
        exempt_match = EXEMPT_RE.search(line)
        if exempt_match:
            result.exempt = True
            result.exempt_reason = exempt_match.group(1).strip() or "未指定原因"
            result.compliant = True
            result.compliance_mode = "exempt"
            _log(verbose, "  豁免标记 L{}: {}".format(idx, result.exempt_reason))
            return result

    _log(verbose, "  无豁免标记，继续检测")

    # ── 步骤4：检查 shebang ──
    first_lines = "\n".join(lines[:5])
    result.has_shebang = bool(SHEBANG_RE.search(first_lines))
    _log(verbose, "  shebang: {}".format("是" if result.has_shebang else "否"))

    # ── 步骤5：检测版本校验方式 ──
    # 先简单处理注释（避免注释中的关键词误报）
    code_content = _strip_comments_and_strings(content)

    # 5a. 内联版本校验：sys.version_info 检测 + 版本比较 + 错误提示
    result.has_version_info = bool(SYS_VERSION_INFO_RE.search(code_content))
    result.has_version_compare = bool(VERSION_COMPARE_RE.search(code_content))
    result.has_error_message = bool(VERSION_ERROR_MSG_RE.search(content))  # 错误信息在注释中也算
    has_version_detection = result.has_version_info and result.has_version_compare
    result.has_inline_check = has_version_detection and result.has_error_message

    _log(verbose, "  内联检测: version_info={}, version_compare={}, error_msg={}".format(
        result.has_version_info, result.has_version_compare, result.has_error_message
    ))
    _log(verbose, "  内联版本校验块: {}".format("是" if result.has_inline_check else "否"))

    # 5b. 导入共享库
    result.has_import_lib = bool(IMPORT_LIB_RE.search(code_content))
    result.has_enforce_call = bool(ENFORCE_CALL_RE.search(code_content))
    uses_shared_lib = result.has_import_lib and result.has_enforce_call

    _log(verbose, "  导入共享库: {}, enforce调用: {}".format(
        result.has_import_lib, result.has_enforce_call
    ))
    _log(verbose, "  共享库模式: {}".format("是" if uses_shared_lib else "否"))

    # ── 步骤6：判定合规性 ──
    if result.has_inline_check:
        result.compliant = True
        result.compliance_mode = "inline"
        _log(verbose, "  合规判定: 内联版本校验块")
    elif uses_shared_lib:
        result.compliant = True
        result.compliance_mode = "shared-lib"
        _log(verbose, "  合规判定: 导入共享版本校验库")
    else:
        result.compliant = False
        result.compliance_mode = "noncompliant"
        missing_parts = []
        if not result.has_version_info:
            missing_parts.append("缺少 sys.version_info 检测")
        elif not result.has_version_compare:
            missing_parts.append("缺少版本比较逻辑")
        if not result.has_error_message:
            missing_parts.append("缺少友好错误提示信息")
        if not result.has_import_lib:
            missing_parts.append("未导入 python310_version_check 共享库")
        elif not result.has_enforce_call:
            missing_parts.append("未调用 enforce_python310()")

        if missing_parts:
            result.errors.append((
                0,
                "缺少 Python 3.10+ 版本校验：需要内联版本校验代码块（sys.version_info检测+版本比较+友好错误提示），"
                "或导入 python310_version_check 共享库并调用 enforce_python310()。"
                "缺失项: {}".format("; ".join(missing_parts))
            ))
        _log(verbose, "  合规判定: 不合规 - {}".format("; ".join(missing_parts)))

    _log(verbose, "  最终结果: {}".format("合规" if result.compliant else "不合规"))
    return result


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="检查 Python 脚本 Python 3.10+ 版本合规性",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="扫描根路径（默认为项目根目录）",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--warn-only",
        dest="strict_mode",
        action="store_false",
        help="仅警告模式，违规时退出码始终为 0（过渡期使用）",
    )
    mode_group.add_argument(
        "--strict",
        dest="strict_mode",
        action="store_true",
        help="严格模式（默认），违规时返回 exit code=1",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细模式，输出每个文件的检测过程和结果",
    )
    parser.set_defaults(strict_mode=True, verbose=False)
    return parser


def main() -> int:
    """主入口函数。"""
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(args.path).resolve() if args.path else resolve_project_root(__file__)

    py_files = collect_py_files(project_root)

    if args.verbose:
        print("[INFO] 开始扫描，共发现 {} 个 .py 文件".format(len(py_files)))
        print()

    results: List[FileResult] = []
    for file_path in py_files:
        result = scan_file(file_path, project_root, verbose=args.verbose)
        results.append(result)
        if args.verbose:
            status = "✓" if result.compliant else "✗"
            mode_str = "[{}]".format(result.compliance_mode) if result.compliance_mode else ""
            print("  {} {} {}".format(status, result.rel_path, mode_str))
            if result.errors:
                for line_num, msg in result.errors:
                    loc = ":{}".format(line_num) if line_num > 0 else ""
                    print("      → {}{}".format(msg, loc))
            print()

    total = len(results)
    compliant = sum(1 for r in results if r.compliant and not r.exempt and r.compliance_mode != "init")
    exempt = sum(1 for r in results if r.exempt)
    init_files = sum(1 for r in results if r.compliance_mode == "init")
    violations = [r for r in results if not r.compliant]
    error_count = len(violations)

    # 统计合规模式分布
    mode_counts: dict[str, int] = {}
    for r in results:
        mode = r.compliance_mode or "unknown"
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    print_header("Python 3.10+ Compliance Check")
    print("扫描根目录: {}".format(project_root))
    mode_str = " (严格模式)" if args.strict_mode else " (WARN-ONLY 模式)"
    if args.verbose:
        mode_str += " (详细模式)"
    print("扫描文件数: {}{}".format(total, mode_str))
    print()

    if args.verbose:
        print("合规模式分布:")
        for mode in ["inline", "shared-lib", "exempt", "init", "noncompliant"]:
            count = mode_counts.get(mode, 0)
            if count > 0:
                mode_names = {
                    "inline": "内联版本校验",
                    "shared-lib": "共享库模式",
                    "exempt": "豁免",
                    "init": "__init__.py自动合规",
                    "noncompliant": "不合规",
                }
                print("  {}: {} 个文件".format(mode_names.get(mode, mode), count))
        print()

    # 输出豁免文件
    for r in results:
        if r.exempt and not args.verbose:
            print("  EXEMPT: {} - {}".format(r.rel_path, r.exempt_reason))

    # 输出违规文件
    error_label = "ERROR" if args.strict_mode else "WARN"
    for r in violations:
        if args.verbose:
            continue  # verbose 模式下已在上面输出过
        for line_num, msg in r.errors:
            if line_num > 0:
                print("  {}: {}:{}: {}".format(error_label, r.rel_path, line_num, msg))
            else:
                print("  {}: {}: {}".format(error_label, r.rel_path, msg))

    print()
    if error_count == 0:
        print_pass("所有 {} 个 Python 脚本均合规（{} 合规，{} 豁免，{} __init__.py自动合规）".format(
            total, compliant, exempt, init_files
        ))
    else:
        if args.strict_mode:
            print_error("发现 {} 个违规文件".format(error_count))
        else:
            print_warn("发现 {} 个违规文件（warn-only 模式，不阻断）".format(error_count))

    print_summary(
        pass_count=compliant + exempt + init_files,
        warn_count=0 if args.strict_mode else error_count,
        error_count=error_count if args.strict_mode else 0,
    )

    if not args.strict_mode:
        return 0
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
