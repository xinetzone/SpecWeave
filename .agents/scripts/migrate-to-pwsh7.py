#!/usr/bin/env python3
"""PowerShell 7 迁移辅助脚本。

自动为 PowerShell 脚本添加 pwsh7 版本声明和版本校验代码块。

迁移策略：
  1. 已有 #Requires -Version 5.x 的脚本：替换为 5.1 + 插入版本校验块
  2. 无 #Requires 声明的脚本：在开头插入 #Requires -Version 5.1 和版本校验块
  3. 已包含版本校验代码的脚本：跳过
  4. 包含 # PWSH7-EXEMPT: 的脚本：跳过

迁移模式（自动根据文件位置选择）：
  - lib/ 目录下文件：dot-source 同目录 pwsh7-version-check.ps1
  - scripts/ 目录下文件（非 lib）：dot-source ../lib/pwsh7-version-check.ps1
  - 其他位置文件：内联版本校验块（自包含）

默认使用 DRY-RUN 预览模式，使用 --apply 参数实际执行修改。
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
from dataclasses import dataclass
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root
from lib.cli import print_header, print_summary, print_warn, print_error, print_pass, setup_safe_output
from lib.ps1_syntax import (
    find_non_whitespace,
    skip_whitespace_and_comments,
    find_comment_block_end,
    find_param_block_end,
    find_top_level_insert_point,
    PARAM_START_RE,
)

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
REQUIRES_VERSION_RE = re.compile(r"^(\s*)#\s*Requires\s+-Version\s+(\d+)(?:\.(\d+))?", re.IGNORECASE | re.MULTILINE)
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

# ── 版本校验块模板 ─────────────────────────────────────────────────────────

VERSION_CHECK_BLOCK = """\
# ==============================================================================
# 版本校验（自包含，不依赖外部 lib 文件）
# 兼容 Windows PowerShell 5.1 和 PowerShell 7.4+
# ==============================================================================
function Test-Pwsh7Requirement {
    [CmdletBinding()]
    param(
        [switch]$PassThru
    )

    $isCore = $false
    $currentVersion = $null
    $edition = 'Desktop'
    $versionOk = $false

    if ($PSVersionTable.ContainsKey('PSEdition')) {
        $edition = $PSVersionTable.PSEdition
    }
    $isCore = ($edition -eq 'Core')

    if ($PSVersionTable.ContainsKey('PSVersion')) {
        $currentVersion = $PSVersionTable.PSVersion
    }

    if ($isCore -and $null -ne $currentVersion) {
        $majorOk = ($currentVersion.Major -gt 7)
        $minorOk = ($currentVersion.Major -eq 7 -and $currentVersion.Minor -ge 4)
        $versionOk = ($majorOk -or $minorOk)
    }

    $result = [PSCustomObject]@{
        IsCore      = $isCore
        PSEdition   = $edition
        PSVersion   = $currentVersion
        VersionOk   = $versionOk
        IsSupported = ($isCore -and $versionOk)
    }

    if ($PassThru) {
        return $result
    }

    return $result.IsSupported
}

function Show-Pwsh7RequirementError {
    [CmdletBinding()]
    param()

    $checkResult = Test-Pwsh7Requirement -PassThru

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  错误：PowerShell 版本不支持" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    Write-Host "  当前 PowerShell 信息：" -ForegroundColor Yellow
    Write-Host "    PSEdition : $($checkResult.PSEdition)"
    Write-Host "    PSVersion : $($checkResult.PSVersion)"
    Write-Host ""

    Write-Host "  问题说明：" -ForegroundColor Yellow
    Write-Host "    本脚本需要 PowerShell 7.4 或更高版本（pwsh7）。"
    Write-Host "    当前运行的是旧版本或不兼容版本。"
    Write-Host ""

    Write-Host "  安装命令：" -ForegroundColor Yellow
    Write-Host "    winget install Microsoft.PowerShell"
    Write-Host ""

    Write-Host "  文档提示：" -ForegroundColor Yellow
    Write-Host "    请参考项目 ONBOARDING.md 配置开发环境。"
    Write-Host ""

    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    exit 1
}

if ($MyInvocation.InvocationName -ne '.') {
    $supported = Test-Pwsh7Requirement
    if (-not $supported) {
        Show-Pwsh7RequirementError
    }
}
"""

REQUIRES_LINE = "#Requires -Version 5.1"

# lib 文件使用 dot-source 模式（同目录引用共享库）
LIB_VERSION_CHECK_BLOCK = """\
# 版本校验：dot-source 共享库
. "$PSScriptRoot/pwsh7-version-check.ps1"
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Requirement)) { Show-Pwsh7RequirementError }
}
"""

# scripts/ 目录下脚本使用 ../lib/ 路径
SCRIPT_VERSION_CHECK_BLOCK = """\
# 版本校验：dot-source 共享库
. "$PSScriptRoot/../lib/pwsh7-version-check.ps1"
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Requirement)) { Show-Pwsh7RequirementError }
}
"""


def _is_lib_file(file_path: Path | None) -> bool:
    """判断文件是否位于 lib/ 目录下（应使用 dot-source 模式）。"""
    if file_path is None:
        return False
    return "lib" in file_path.parts


def _is_script_in_scripts_dir(file_path: Path | None) -> bool:
    """判断文件是否位于 scripts/ 目录下（但不在 lib/ 子目录中）。"""
    if file_path is None:
        return False
    parts = file_path.parts
    if "lib" in parts:
        return False
    return "scripts" in parts


def _get_version_check_block(file_path: Path | None) -> tuple[str, str]:
    """根据文件位置返回合适的版本校验块和描述。"""
    if _is_lib_file(file_path):
        return LIB_VERSION_CHECK_BLOCK.rstrip("\n"), "插入dot-source版本校验(lib模式)"
    if _is_script_in_scripts_dir(file_path):
        return SCRIPT_VERSION_CHECK_BLOCK.rstrip("\n"), "插入dot-source版本校验(scripts模式)"
    return VERSION_CHECK_BLOCK.rstrip("\n"), "插入内联版本校验块"


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
    if root.is_file() and root.suffix.lower() == ".ps1":
        result.append(root)
        return result
    for path in sorted(root.rglob("*.ps1")):
        if not path.is_file():
            continue
        if is_excluded_dir(path, root):
            continue
        result.append(path)
    return result


def read_ps1_file(file_path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "gbk", "cp936"]
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return file_path.read_text(encoding="utf-8", errors="replace")


def write_ps1_file(file_path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    crlf_content = normalized.replace("\n", "\r\n")
    file_path.write_text(crlf_content, encoding="utf-8-sig", newline="")


def has_version_check(content: str) -> bool:
    has_psedition = bool(PSEDITION_RE.search(content))
    has_psversion = bool(PSVERSION_RE.search(content))
    has_version_compare = bool(VERSION_COMPARE_RE.search(content))
    has_version_error_exit = bool(VERSION_CHECK_EXIT_RE.search(content))
    has_version_detection = has_psedition or (has_psversion and has_version_compare)
    return has_version_detection and has_version_error_exit


def analyze_structure(content: str) -> dict:
    """分析 PowerShell 脚本结构，确定 #Requires 和版本校验块的插入位置。

    使用 lib.ps1_syntax 中的共享函数进行括号深度感知的插入点检测，
    正确区分脚本级 param 和函数内 param，防止版本校验块被插入函数体内。
    """
    pos = 0
    pos = find_non_whitespace(content, pos)
    pos = skip_whitespace_and_comments(content, pos)

    comment_block_end = find_comment_block_end(content, pos)
    if comment_block_end > 0:
        pos = find_non_whitespace(content, comment_block_end)
        pos = skip_whitespace_and_comments(content, pos)
    else:
        comment_block_end = pos

    requires_match = REQUIRES_VERSION_RE.search(content, pos)
    requires_start = -1
    requires_end = -1
    requires_major = -1
    requires_minor = -1
    requires_indent = ""

    if requires_match and requires_match.start() <= pos + 10:
        requires_start = requires_match.start()
        line_end = content.find("\n", requires_match.end())
        if line_end == -1:
            line_end = len(content)
        requires_end = line_end
        requires_indent = requires_match.group(1) or ""
        requires_major = int(requires_match.group(2))
        requires_minor = int(requires_match.group(3)) if requires_match.group(3) else 0
        pos = find_non_whitespace(content, requires_end)
    else:
        requires_match = None

    # 使用共享模块的顶层插入点检测（括号深度感知，修复函数内插入 bug）
    insert_pos = find_top_level_insert_point(content, pos)

    # 检测脚本级 param 位置（用于返回信息）
    script_param_start = -1
    script_param_end = -1
    check_pos = skip_whitespace_and_comments(content, pos)
    param_match_check = PARAM_START_RE.match(content, check_pos)
    if param_match_check:
        pe = find_param_block_end(content, param_match_check.start())
        if pe > 0:
            script_param_start = param_match_check.start()
            script_param_end = pe

    leading_ws_end = find_non_whitespace(content, 0)
    requires_insert_pos = comment_block_end if comment_block_end > leading_ws_end else leading_ws_end

    return {
        "leading_whitespace_end": leading_ws_end,
        "comment_block_end": comment_block_end,
        "requires_match": requires_match,
        "requires_start": requires_start,
        "requires_end": requires_end,
        "requires_major": requires_major,
        "requires_minor": requires_minor,
        "requires_indent": requires_indent,
        "param_start": script_param_start,
        "param_end": script_param_end,
        "insert_pos": insert_pos,
        "requires_insert_pos": requires_insert_pos,
    }


def migrate_content(content: str, file_path: Path | None = None) -> tuple[str, str, bool]:
    exempt_match = EXEMPT_RE.search(content)
    if exempt_match:
        reason = exempt_match.group(1).strip() or "未指定原因"
        return content, f"豁免标记：{reason}", False

    if has_version_check(content):
        return content, "已包含版本校验代码", False

    struct = analyze_structure(content)
    new_content = content
    action_parts = []

    if struct["requires_match"]:
        major = struct["requires_major"]
        minor = struct["requires_minor"]
        if major >= 7:
            return content, f"已声明 #Requires -Version {major}.{minor}（pwsh7+）", False

        if major == 5 and minor == 1:
            pass
        else:
            old_start = struct["requires_start"]
            old_end = struct["requires_end"]
            indent = struct["requires_indent"]
            new_line = f"{indent}{REQUIRES_LINE}"
            new_content = new_content[:old_start] + new_line + new_content[old_end:]
            action_parts.append("替换#Requires版本声明")
            struct = analyze_structure(new_content)
    else:
        insert_pos = struct["requires_insert_pos"]
        prefix = "\n\n" if insert_pos > 0 else ""
        new_content = new_content[:insert_pos] + prefix + REQUIRES_LINE + "\n" + new_content[insert_pos:]
        action_parts.append("添加#Requires -Version 5.1声明")
        struct = analyze_structure(new_content)

    insert_pos = struct["insert_pos"]
    prefix = "\n\n" if insert_pos > 0 else ""
    block, block_desc = _get_version_check_block(file_path)
    new_content = new_content[:insert_pos] + prefix + block + "\n\n" + new_content[insert_pos:]
    action_parts.append(block_desc)

    while "\n\n\n" in new_content:
        new_content = new_content.replace("\n\n\n", "\n\n")

    action = "+".join(action_parts)
    return new_content, action, True


@dataclass
class FileResult:
    file_path: Path
    rel_path: Path
    status: str
    message: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PowerShell 7 迁移辅助脚本 - 自动添加版本声明和校验代码",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="迁移根路径或单个 .ps1 文件（默认为项目根目录）",
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

    ps1_files = collect_ps1_files(project_root)
    results: list[FileResult] = []

    mode_str = "APPLY模式" if args.apply_mode else "DRY-RUN模式"

    print_header(f"PowerShell 7 Migration Assistant ({mode_str})")
    print(f"迁移根路径: {project_root}")
    print(f"待处理文件数: {len(ps1_files)}")
    print()

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in ps1_files:
        if project_root.is_file():
            rel_path = file_path.name
        else:
            try:
                rel_path = file_path.relative_to(project_root)
            except ValueError:
                rel_path = file_path

        try:
            content = read_ps1_file(file_path)
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
                write_ps1_file(file_path, new_content)
            except Exception as e:
                print(f"    ERROR: 写入失败: {e}")
                error_count += 1

    print()
    total = len(ps1_files)
    if args.apply_mode:
        if migrated_count == 0 and error_count == 0:
            print_pass(f"所有 {total} 个 PowerShell 脚本均无需迁移（{skipped_count} 跳过）")
        else:
            msg = f"已迁移 {migrated_count} 个文件，跳过 {skipped_count} 个文件"
            if error_count > 0:
                msg += f"，{error_count} 个错误"
                print_error(msg)
            else:
                print_pass(msg)
    else:
        if migrated_count == 0:
            print_pass(f"所有 {total} 个 PowerShell 脚本均无需迁移（{skipped_count} 跳过）")
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

