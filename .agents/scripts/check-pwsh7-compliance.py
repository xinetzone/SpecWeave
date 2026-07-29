#!/usr/bin/env python3
"""PowerShell 7 合规性检查脚本。

扫描项目中的 .ps1 文件，验证其是否声明了 PowerShell 7.x 版本要求，
或包含自包含的版本校验代码块以在 PowerShell 5.1 下显示友好错误。

合规条件（满足任一即可）：
  1. 文件包含 # PWSH7-EXEMPT: 注释（豁免）
  2. 文件包含 #Requires -Version 7.x 声明
  3. 文件包含 #Requires -Version 5.x 且同时包含内联版本校验代码块
     （PSEdition 检测或 PSVersionTable.PSVersion 版本比较 + 错误提示）
  4. 文件包含 #Requires -Version 5.x 且 dot-source 了共享版本校验库
     （pwsh7-version-check.ps1）并调用了 Test-Pwsh7Version/Test-Pwsh7Requirement

使用 --verbose (-v) 参数输出每个文件的详细检测过程。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import print_header, print_summary, print_warn, print_error, print_pass, setup_safe_output
from lib.ps1_syntax import (
    validate_brace_balance,
    strip_line_comment,
)


def _strip_comment_blocks(content: str) -> str:
    """移除 PowerShell 注释块 <# ... #>（支持嵌套），用等长空格替换以保持位置映射。

    保留换行符以维持行号对应关系。
    """
    result = list(content)
    i = 0
    n = len(content)
    while i < n - 1:
        if content[i] == '<' and content[i + 1] == '#':
            depth = 1
            start = i
            i += 2
            while i < n and depth > 0:
                if i + 1 < n and content[i] == '<' and content[i + 1] == '#':
                    depth += 1
                    i += 2
                elif i + 1 < n and content[i] == '#' and content[i + 1] == '>':
                    depth -= 1
                    i += 2
                else:
                    i += 1
            # 用空格替换注释块内容（保留换行符）
            for j in range(start, i):
                if result[j] not in ('\n', '\r'):
                    result[j] = ' '
        else:
            i += 1
    return ''.join(result)

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
}
EXCLUDE_DIR_PATTERNS = (
    re.compile(r".*[.-]venv$", re.IGNORECASE),
)
EXCLUDE_DIR_SUFFIXES = (".egg-info",)

EXEMPT_RE = re.compile(r"#\s*PWSH7-EXEMPT\s*:?\s*(.*)", re.IGNORECASE)
REQUIRES_VERSION_RE = re.compile(r"#\s*Requires\s+-Version\s+(\d+)(?:\.(\d+))?", re.IGNORECASE)
PSEDITION_RE = re.compile(r"\$PSEdition|\$PSVersionTable\.PSEdition", re.IGNORECASE)
PSVERSION_RE = re.compile(r"\$PSVersionTable\.PSVersion", re.IGNORECASE)
VERSION_COMPARE_RE = re.compile(
    r"(?:-ge|-gt|-le|-lt|-eq|-ne)\s*\d+\.\d+|Major\s*-[a-z]+\s*\d+|Version\s*-[a-z]+\s*\d+",
    re.IGNORECASE
)
VERSION_CHECK_EXIT_RE = re.compile(
    r"winget\s+install\s+Microsoft\.PowerShell|"
    r"需要\s*PowerShell\s*7|"
    r"PowerShell\s*版本不支持|"
    r"pwsh7",
    re.IGNORECASE
)
DOTSOURCE_LIB_RE = re.compile(
    r"""(?:\.|\.\s)"""                        # dot-source operator (.)
    r"""\s*"""                                 # optional whitespace
    r"""["']?.*?pwsh7-version-check\.ps1["']?""",  # path containing pwsh7-version-check.ps1
    re.IGNORECASE
)
VERSION_FUNC_CALL_RE = re.compile(
    r"Test-Pwsh7(?:Version|Requirement)\b",
    re.IGNORECASE
)


@dataclass
class FileResult:
    file_path: Path
    rel_path: Path
    compliant: bool = False
    exempt: bool = False
    exempt_reason: str = ""
    errors: list[tuple[int, str]] = field(default_factory=list)
    requires_version: tuple[int, int] | None = None
    requires_line: int = 0
    has_psedition: bool = False
    has_psversion: bool = False
    has_version_compare: bool = False
    has_version_error_exit: bool = False
    has_dotsource_lib: bool = False
    has_version_func_call: bool = False
    has_inline_check: bool = False
    structure_errors: list[tuple[int, str]] = field(default_factory=list)
    compliance_mode: str = ""  # "v7+" / "inline" / "shared-lib" / "exempt" / "missing-requires" / "noncompliant"


def _log(verbose: bool, msg: str) -> None:
    """详细日志输出（仅在 verbose 模式下）。"""
    if verbose:
        print(f"    [DEBUG] {msg}")


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


def collect_ps1_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in sorted(root.rglob("*.ps1")):
        if not path.is_file():
            continue
        if is_excluded_dir(path, root):
            continue
        result.append(path)
    return result


def scan_file(file_path: Path, root: Path, verbose: bool = False) -> FileResult:
    """扫描单个 .ps1 文件，检测 pwsh7 合规性。

    检测流程：
    1. 读取文件内容（UTF-8 with BOM 兼容）
    2. 检查豁免标记 # PWSH7-EXEMPT:
    3. 查找 #Requires -Version 声明
    4. 检测版本校验方式（内联块 / dot-source 共享库）
    5. 判定合规性
    6. 执行括号平衡和函数结构校验
    """
    rel_path = file_path.relative_to(root)

    _log(verbose, f"开始扫描: {rel_path}")

    # ── 步骤1：读取文件 ──
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        _log(verbose, f"  编码警告: UTF-8解码失败，使用replace模式")

    result = FileResult(file_path=file_path, rel_path=rel_path)
    lines = content.splitlines()
    _log(verbose, f"  文件行数: {len(lines)}")

    # ── 步骤2：检查豁免标记 ──
    for idx, line in enumerate(lines, start=1):
        exempt_match = EXEMPT_RE.search(line)
        if exempt_match:
            result.exempt = True
            result.exempt_reason = exempt_match.group(1).strip() or "未指定原因"
            result.compliant = True
            result.compliance_mode = "exempt"
            _log(verbose, f"  豁免标记 L{idx}: {result.exempt_reason}")
            return result

    _log(verbose, "  无豁免标记，继续检测")

    # ── 步骤3：查找 #Requires -Version ──
    for idx, line in enumerate(lines, start=1):
        req_match = REQUIRES_VERSION_RE.search(line)
        if req_match:
            major = int(req_match.group(1))
            minor = int(req_match.group(2)) if req_match.group(2) else 0
            result.requires_version = (major, minor)
            result.requires_line = idx
            _log(verbose, f"  #Requires L{idx}: Version {major}.{minor}")
            break

    if result.requires_version is None:
        _log(verbose, "  缺少 #Requires -Version 声明")
        result.errors.append((0, "缺少 #Requires -Version 声明"))
        result.compliant = False
        result.compliance_mode = "missing-requires"
        # 仍然执行结构校验
        result.structure_errors = validate_brace_balance(lines)
        if result.structure_errors:
            _log(verbose, f"  结构错误: {len(result.structure_errors)} 个")
            result.errors.extend(result.structure_errors)
        else:
            _log(verbose, "  结构校验通过")
        return result

    # ── 步骤4：检测版本校验方式 ──
    # 预处理：先去除注释块 <# ... #>（替换为空格），再逐行去除行尾注释
    # 这样可以避免注释/字符串中的关键词（如 pwsh7-version-check.ps1、Test-Pwsh7Version）造成误报
    content_no_blocks = _strip_comment_blocks(content)
    lines_no_blocks = content_no_blocks.splitlines()
    code_lines = [strip_line_comment(line) for line in lines_no_blocks]
    code_content = '\n'.join(code_lines)

    # 4a. 内联版本校验：PSEdition检测 + 版本比较 + 错误提示
    result.has_psedition = bool(PSEDITION_RE.search(code_content))
    result.has_psversion = bool(PSVERSION_RE.search(code_content))
    result.has_version_compare = bool(VERSION_COMPARE_RE.search(code_content))
    result.has_version_error_exit = bool(VERSION_CHECK_EXIT_RE.search(code_content))
    has_version_detection = result.has_psedition or (result.has_psversion and result.has_version_compare)
    result.has_inline_check = has_version_detection and result.has_version_error_exit

    _log(verbose, f"  内联检测: PSEdition={result.has_psedition}, "
         f"PSVersion={result.has_psversion}, VersionCompare={result.has_version_compare}, "
         f"ErrorExit={result.has_version_error_exit}")
    _log(verbose, f"  内联版本校验块: {'是' if result.has_inline_check else '否'}")

    # 4b. dot-source 共享库（在去注释后的代码中搜索，避免注释中的路径误报）
    result.has_dotsource_lib = bool(DOTSOURCE_LIB_RE.search(code_content))
    result.has_version_func_call = bool(VERSION_FUNC_CALL_RE.search(code_content))
    uses_shared_lib = result.has_dotsource_lib and result.has_version_func_call

    _log(verbose, f"  dot-source共享库: {'是' if result.has_dotsource_lib else '否'}, "
         f"版本函数调用: {'是' if result.has_version_func_call else '否'}")
    _log(verbose, f"  共享库模式: {'是' if uses_shared_lib else '否'}")

    # ── 步骤5：判定合规性 ──
    major, minor = result.requires_version
    if major >= 7:
        result.compliant = True
        result.compliance_mode = "v7+"
        _log(verbose, f"  合规判定: #Requires -Version {major}.{minor} (pwsh7+原生)")
    elif major == 5 and (result.has_inline_check or uses_shared_lib):
        result.compliant = True
        if uses_shared_lib:
            result.compliance_mode = "shared-lib"
            _log(verbose, "  合规判定: v5.1 + dot-source共享库")
        else:
            result.compliance_mode = "inline"
            _log(verbose, "  合规判定: v5.1 + 内联版本校验块")
    elif major <= 5:
        if not result.has_inline_check and not uses_shared_lib:
            result.errors.append((
                result.requires_line,
                f"声明 #Requires -Version {major}.{minor} 但缺少版本校验："
                f"需要内联版本校验代码块，或 dot-source pwsh7-version-check.ps1 并调用 Test-Pwsh7Version"
            ))
        result.compliant = False
        result.compliance_mode = "noncompliant"
        _log(verbose, f"  合规判定: 不合规 - v{major}.{minor} 缺少版本校验")
    else:
        result.errors.append((result.requires_line, f"声明了不支持的版本 {major}.{minor}"))
        result.compliant = False
        result.compliance_mode = "noncompliant"
        _log(verbose, f"  合规判定: 不合规 - 不支持的版本 {major}.{minor}")

    # ── 步骤6：函数结构完整性校验（对所有文件执行）──
    result.structure_errors = validate_brace_balance(lines)
    if result.structure_errors:
        _log(verbose, f"  结构校验: {len(result.structure_errors)} 个错误")
        for line_num, msg in result.structure_errors:
            _log(verbose, f"    L{line_num}: {msg}")
        result.errors.extend(result.structure_errors)
        result.compliant = False
    else:
        _log(verbose, "  结构校验: 通过（括号平衡，无函数嵌套）")

    _log(verbose, f"  最终结果: {'合规' if result.compliant else '不合规'}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="检查 PowerShell 脚本 pwsh7 版本合规性",
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
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(args.path).resolve() if args.path else resolve_project_root(__file__)

    ps1_files = collect_ps1_files(project_root)

    if args.verbose:
        print(f"[INFO] 开始扫描，共发现 {len(ps1_files)} 个 .ps1 文件")
        print()

    results: list[FileResult] = []
    for file_path in ps1_files:
        result = scan_file(file_path, project_root, verbose=args.verbose)
        results.append(result)
        if args.verbose:
            status = "✓" if result.compliant else "✗"
            mode_str = f"[{result.compliance_mode}]" if result.compliance_mode else ""
            print(f"  {status} {result.rel_path} {mode_str}")
            if result.errors:
                for line_num, msg in result.errors:
                    loc = f":{line_num}" if line_num > 0 else ""
                    print(f"      → {msg}{loc}")
            print()

    total = len(results)
    compliant = sum(1 for r in results if r.compliant and not r.exempt)
    exempt = sum(1 for r in results if r.exempt)
    violations = [r for r in results if not r.compliant]
    error_count = len(violations)

    # 统计合规模式分布
    mode_counts: dict[str, int] = {}
    for r in results:
        mode = r.compliance_mode or "unknown"
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    print_header("PowerShell 7 Compliance Check")
    print(f"扫描根目录: {project_root}")
    mode_str = " (严格模式)" if args.strict_mode else " (WARN-ONLY 模式)"
    if args.verbose:
        mode_str += " (详细模式)"
    print(f"扫描文件数: {total}{mode_str}")
    print()

    if args.verbose:
        print("合规模式分布:")
        for mode in ["v7+", "inline", "shared-lib", "exempt", "missing-requires", "noncompliant"]:
            count = mode_counts.get(mode, 0)
            if count > 0:
                print(f"  {mode}: {count} 个文件")
        print()

    # 输出豁免文件
    for r in results:
        if r.exempt and not args.verbose:
            print(f"  EXEMPT: {r.rel_path} - {r.exempt_reason}")

    # 输出违规文件
    error_label = "ERROR" if args.strict_mode else "WARN"
    for r in violations:
        if args.verbose:
            continue  # verbose 模式下已在上面输出过
        for line_num, msg in r.errors:
            if line_num > 0:
                print(f"  {error_label}: {r.rel_path}:{line_num}: {msg}")
            else:
                print(f"  {error_label}: {r.rel_path}: {msg}")

    print()
    if error_count == 0:
        print_pass(f"所有 {total} 个 PowerShell 脚本均合规（{compliant} 合规，{exempt} 豁免）")
    else:
        if args.strict_mode:
            print_error(f"发现 {error_count} 个违规文件")
        else:
            print_warn(f"发现 {error_count} 个违规文件（warn-only 模式，不阻断）")

    print_summary(
        pass_count=compliant + exempt,
        warn_count=0 if args.strict_mode else error_count,
        error_count=error_count if args.strict_mode else 0,
    )

    if not args.strict_mode:
        return 0
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

