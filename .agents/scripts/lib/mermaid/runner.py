"""Mermaid 检查运行器模块。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import sys
import difflib
from pathlib import Path
from typing import Optional, List, Tuple, TextIO

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from .scanner import FileScanner
from .registry import (
    create_default_checker_registry,
    create_default_fixer_registry,
)
from .processor import process_mermaid_fences


class ConsoleColors:
    ANSI_RED = "\033[91m"
    ANSI_GREEN = "\033[92m"
    ANSI_YELLOW = "\033[93m"
    ANSI_CYAN = "\033[96m"
    ANSI_RESET = "\033[0m"
    ANSI_BOLD = "\033[1m"
    ANSI_DIM = "\033[2m"


_DEBUG = False
_DEBUG_CTX: dict = {}


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def _debug_enter(file_rel: str, start_line: int, dia_type: str) -> None:
    _DEBUG_CTX["file"] = file_rel
    _DEBUG_CTX["line"] = start_line
    _DEBUG_CTX["type"] = dia_type


def _debug_log(stage: str, msg: str) -> None:
    if not _DEBUG:
        return
    f = _DEBUG_CTX.get("file", "?")
    sl = _DEBUG_CTX.get("line", 0)
    dt = _DEBUG_CTX.get("type", "?")
    print(f"  [DEBUG:{dt}] {f}:L{sl} [{stage}] {msg}", file=sys.stderr)


class MermaidRunner:
    def __init__(self, project_root: Path, fix: bool = False, dry_run: bool = False,
                 output: Optional[TextIO] = None):
        self.project_root = project_root.resolve()
        self.fix = fix
        self.dry_run = dry_run
        self.output = output or sys.stdout
        self.exclude_dirs: set[str] = set()
        self._setup_excludes()

    def _setup_excludes(self) -> None:
        config_paths = [
            self.project_root / "spec-loader.toml",
            self.project_root / ".specweave" / "spec-loader.toml",
        ]
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "rb") as f:
                        config = tomllib.load(f)
                    exclude = config.get("exclude", [])
                    if isinstance(exclude, list):
                        self.exclude_dirs.update(exclude)
                except Exception:
                    pass
                break

    def run(self) -> int:
        check_root = self.project_root
        scanner = FileScanner(check_root, self.exclude_dirs)
        md_files = scanner.scan()
        total = len(md_files)
        files_with_issues = 0
        total_errors = 0
        total_warnings = 0
        total_fixes = 0
        all_diffs: list[tuple[str, str]] = []

        fix_mode = self.fix or self.dry_run
        fix_label = " (dry-run)" if self.dry_run else ""

        print(f"[检查] Mermaid 语法安全检查{fix_label}", file=self.output)
        print(f"   扫描目录: {check_root}", file=self.output)
        print(f"   文件总数: {total}", file=self.output)
        if fix_mode:
            print(f"   修复模式: {'预览(dry-run)' if self.dry_run else '自动修复'}", file=self.output)
        print(file=self.output)

        checker_registry = create_default_checker_registry()
        fixer_registry = create_default_fixer_registry()
        security_checker = checker_registry.get_security_checker()

        for md in sorted(md_files):
            issues, fixes, diffs = self._process_file(
                md, checker_registry, fixer_registry, security_checker
            )
            total_fixes += fixes
            all_diffs.extend(diffs)
            if issues:
                files_with_issues += 1
                errs = [i for i in issues if i[1] == "error"]
                warns = [i for i in issues if i[1] == "warning"]
                total_errors += len(errs)
                total_warnings += len(warns)
                rel = md.relative_to(self.project_root).as_posix()
                print(f"[文件] {rel}", file=self.output)
                for ln, lvl, msg in sorted(issues, key=lambda x: x[0]):
                    color = ConsoleColors.ANSI_RED if lvl == "error" else ConsoleColors.ANSI_YELLOW
                    icon = "[错误]" if lvl == "error" else "[警告]"
                    print(f"   {color}{icon} L{ln}: {msg}{ConsoleColors.ANSI_RESET}", file=self.output)
                if fixes > 0 and not self.dry_run:
                    print(f"   {ConsoleColors.ANSI_CYAN}[修复] 已修复 {fixes} 个代码块{ConsoleColors.ANSI_RESET}", file=self.output)
                print(file=self.output)

        if self.dry_run and all_diffs:
            print("=" * 60, file=self.output)
            print(f"[预览] 修复预览（{len(all_diffs)} 个代码块变更）:", file=self.output)
            print(file=self.output)
            for diff_text, fix_desc in all_diffs:
                print(f"   [修复] {fix_desc}:", file=self.output)
                for line in diff_text.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        print(f"   {ConsoleColors.ANSI_GREEN}{line}{ConsoleColors.ANSI_RESET}", file=self.output)
                    elif line.startswith("-") and not line.startswith("---"):
                        print(f"   {ConsoleColors.ANSI_RED}{line}{ConsoleColors.ANSI_RESET}", file=self.output)
                    elif line.startswith("@@"):
                        print(f"   {ConsoleColors.ANSI_CYAN}{line}{ConsoleColors.ANSI_RESET}", file=self.output)
                    else:
                        print(f"   {line}", file=self.output)
                print(file=self.output)

        print("=" * 60, file=self.output)
        print(f"[结果] 检查结果:", file=self.output)
        print(f"   扫描文件: {total}", file=self.output)
        print(f"   问题文件: {files_with_issues}", file=self.output)
        print(f"   {ConsoleColors.ANSI_RED}错误: {total_errors}{ConsoleColors.ANSI_RESET}", file=self.output)
        print(f"   {ConsoleColors.ANSI_YELLOW}警告: {total_warnings}{ConsoleColors.ANSI_RESET}", file=self.output)
        if fix_mode:
            print(f"   {ConsoleColors.ANSI_GREEN}自动修复: {total_fixes} 个文件块{ConsoleColors.ANSI_RESET}", file=self.output)

        if total_errors > 0 and not self.fix:
            print(f"\n{ConsoleColors.ANSI_RED}[错误] 发现 {total_errors} 个错误，请修复后再提交。可使用 --fix 参数自动修复部分问题，或使用 --dry-run 预览修复效果。{ConsoleColors.ANSI_RESET}", file=self.output)
            return 1
        if self.fix and total_errors > 0:
            print(f"\n{ConsoleColors.ANSI_YELLOW}[警告] 已自动修复可修复问题，仍有 {total_errors} 个错误需手动修复。{ConsoleColors.ANSI_RESET}", file=self.output)
            return 1
        if total_warnings > 0:
            print(f"\n{ConsoleColors.ANSI_YELLOW}[警告] 发现 {total_warnings} 个警告，建议检查。{ConsoleColors.ANSI_RESET}", file=self.output)
            return 0
        print(f"\n{ConsoleColors.ANSI_GREEN}[通过] 所有 Mermaid 代码块检查通过！{ConsoleColors.ANSI_RESET}", file=self.output)
        return 0

    def _process_file(self, md_path: Path, checker_registry, fixer_registry,
                      security_checker) -> Tuple[List[Tuple[int, str, str]], int, List[Tuple[str, str]]]:
        content = md_path.read_text(encoding="utf-8")
        total_fixes = 0
        diffs: List[Tuple[str, str]] = []
        all_issues: List[Tuple[int, str, str]] = []
        all_fixes_per_block: List[List[str]] = []

        def _rep_block(m):
            nonlocal total_fixes
            fence_start, block_text, fence_end = m.group(1), m.group(2), m.group(3)
            from .common import detect_diagram_type, line_from_offset
            start_off = m.start(2)
            start_line = line_from_offset(content, start_off)

            dia_type = detect_diagram_type(block_text)
            rel_path = md_path.relative_to(self.project_root).as_posix()
            _debug_enter(rel_path, start_line, dia_type)
            _debug_log("block", f"发现 {dia_type} 代码块，文本长度 {len(block_text)} 字符")

            fixed_text = block_text
            fixes: List[str] = []

            if self.fix or self.dry_run:
                fixer = fixer_registry.get_fixer(dia_type)
                if fixer is None:
                    from .fixers.generic import GenericFixer
                    fixer = GenericFixer(dia_type)
                fixed_text, fixes = fixer.fix(block_text)
                if fixes:
                    _debug_log("block", f"fixer返回修复项: {fixes}")

            text_to_check = fixed_text if self.fix else block_text

            checker = checker_registry.get_checker(dia_type)
            issues = []
            if checker is not None:
                issues = checker.check(text_to_check, start_line)
            sec_issues = security_checker.check(text_to_check, start_line)
            issues.extend(sec_issues)
            all_issues.extend(issues)
            all_fixes_per_block.append(fixes)
            _debug_log("block", f"checker返回问题 {len(issues)} 个（含安全检测 {len(sec_issues)} 个）")

            if fixes and fixed_text != block_text:
                total_fixes += 1
                if self.dry_run:
                    old_lines = block_text.split("\n")
                    new_lines = fixed_text.split("\n")
                    diff = difflib.unified_diff(
                        old_lines, new_lines,
                        fromfile=f"{md_path.relative_to(self.project_root).as_posix()} (before)",
                        tofile=f"{md_path.relative_to(self.project_root).as_posix()} (after)",
                        lineterm="", n=2
                    )
                    diffs.append(("\n".join(diff), ", ".join(fixes)))
                return fence_start + fixed_text + fence_end
            return m.group(0)

        from .common import MERMAID_FENCE_RE
        new_content = MERMAID_FENCE_RE.sub(_rep_block, content)
        if self.fix and not self.dry_run and new_content != content:
            md_path.write_text(new_content, encoding="utf-8")
        return all_issues, total_fixes, diffs

