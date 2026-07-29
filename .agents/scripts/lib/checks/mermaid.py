"""Mermaid 语法安全检查（兼容层）。

保持所有原有函数签名和行为，内部委托给新架构模块。
"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import re
import sys
from pathlib import Path
from typing import List, Tuple

from constants import EXCLUDED_DIRS, ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_RESET, ANSI_CYAN
from lib.project import is_non_worktree_path

from lib.mermaid.common import (
    MERMAID_FENCE_RE,
    CHINESE_CHARS_RE,
    LIST_TRIGGER_RE,
    SPECIAL_CHARS,
    detect_diagram_type as _new_detect_diagram_type,
    text_needs_quotes as _new_text_needs_quotes,
    state_text_needs_quotes as _new_state_text_needs_quotes,
    has_list_trigger as _new_has_list_trigger,
    line_from_offset as _new_line_from_offset,
    strip_inline_comment as _new_strip_inline_comment,
    check_empty_lines as _new_check_empty_lines,
    check_backslash_n as _new_check_backslash_n,
    fix_backslash_n as _new_fix_backslash_n,
    fix_empty_lines as _new_fix_empty_lines,
    check_list_trigger as _new_check_list_trigger,
    strip_mindmap_shape as _new_strip_mindmap_shape,
)
from lib.mermaid.checkers import (
    FlowchartChecker,
    StateDiagramChecker,
    SequenceDiagramChecker,
    ClassDiagramChecker,
    ErDiagramChecker,
    MindmapChecker,
    SecurityChecker,
    PieChecker,
    GanttChecker,
    TimelineChecker,
    XyChartChecker,
    QuadrantChecker,
)
from lib.mermaid.fixers import (
    FlowchartFixer,
    StateDiagramFixer,
    SequenceDiagramFixer,
    ClassDiagramFixer,
    ErDiagramFixer,
    MindmapFixer,
    PieFixer,
    GanttFixer,
    GenericFixer,
)
from lib.mermaid.scanner import FileScanner
from lib.mermaid.runner import MermaidRunner, ConsoleColors, _set_debug as _runner_set_debug

_DEBUG = False
_DEBUG_CTX: dict = {}


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled
    _runner_set_debug(enabled)


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


# 向后兼容的函数别名
_detect_diagram_type = _new_detect_diagram_type
_text_needs_quotes = _new_text_needs_quotes
_state_text_needs_quotes = _new_state_text_needs_quotes
_has_list_trigger = _new_has_list_trigger
_line_from_offset = _new_line_from_offset
_strip_inline_comment = _new_strip_inline_comment
_check_empty_lines = _new_check_empty_lines
_check_backslash_n = _new_check_backslash_n
_fix_backslash_n = _new_fix_backslash_n
_check_list_trigger = _new_check_list_trigger
_strip_mindmap_shape = _new_strip_mindmap_shape

# VS Code 预览最小兼容子集检测常量
CIRCLED_NUMBERS = {
    '\u2460': '1', '\u2461': '2', '\u2462': '3', '\u2463': '4', '\u2464': '5',
    '\u2465': '6', '\u2466': '7', '\u2467': '8', '\u2468': '9', '\u2469': '10',
}
CIRCLED_NUMBERS_RE = re.compile('[' + ''.join(CIRCLED_NUMBERS.keys()) + ']')
CJK_BRACKET_RE = re.compile(r'[【】]')
BR_TAG_RE = re.compile(r'<br\s*/?>', re.IGNORECASE)
ARROW_SYMBOL_RE = re.compile(r'[→←↑↓↔⇒⇐⇔]')


def _fix_empty_lines(text: str) -> str:
    return _new_fix_empty_lines(text)


def _check_security(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    checker = SecurityChecker()
    return checker.check(block_text, start_line)


_fc = FlowchartChecker()
_sc = StateDiagramChecker()
_seq = SequenceDiagramChecker()
_cls = ClassDiagramChecker()
_er = ErDiagramChecker()
_mm = MindmapChecker()
_pie = PieChecker()
_gantt = GanttChecker()
_timeline = TimelineChecker()
_xy = XyChartChecker()
_quad = QuadrantChecker()


def _check_flowchart(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _fc.check(block_text, start_line)


def _check_state_diagram(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _sc.check(block_text, start_line)


def _check_sequence_diagram(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _seq.check(block_text, start_line)


def _check_classDiagram(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _cls.check(block_text, start_line)


def _check_erDiagram(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _er.check(block_text, start_line)


def _check_mindmap(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _mm.check(block_text, start_line)


def _check_pie(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _pie.check(block_text, start_line)


def _check_gantt(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _gantt.check(block_text, start_line)


def _check_timeline(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _timeline.check(block_text, start_line)


def _check_xychart(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _xy.check(block_text, start_line)


def _check_quadrant(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    return _quad.check(block_text, start_line)


def _check_vscode_compat(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = []
    lines = block_text.split("\n")
    in_subgraph_depth = 0
    for i, line in enumerate(lines):
        code_part = _strip_inline_comment(line)
        stripped = code_part.strip()
        if not stripped:
            continue
        lb = start_line + i
        if re.match(r'^\s*subgraph\s+', code_part):
            in_subgraph_depth += 1
        if re.match(r'^\s*end\s*$', code_part) and in_subgraph_depth > 0:
            in_subgraph_depth -= 1
        if BR_TAG_RE.search(code_part):
            issues.append((lb, "error",
                          'Mermaid 代码块内使用了 <br/> HTML标签，VS Code预览不支持，应移除换行保持单行'))
        if CIRCLED_NUMBERS_RE.search(code_part):
            ch = CIRCLED_NUMBERS_RE.search(code_part).group()
            issues.append((lb, "error",
                          f'Mermaid 代码块内使用了带圈数字 {ch}，VS Code预览解析中断，应使用普通阿拉伯数字'))
        if CJK_BRACKET_RE.search(code_part):
            ch = CJK_BRACKET_RE.search(code_part).group()
            issues.append((lb, "error",
                          f'Mermaid 代码块内使用了中文方括号 {ch}，VS Code预览误解析为语法边界，应改用()或删除'))
        if ARROW_SYMBOL_RE.search(code_part):
            ch = ARROW_SYMBOL_RE.search(code_part).group()
            issues.append((lb, "warning",
                          f'Mermaid 代码块内使用了Unicode箭头符号 {ch}，可能导致VS Code预览兼容性问题，建议改用连字符-'))
        if in_subgraph_depth > 0 and re.match(r'^\s+direction\s+(TB|BT|LR|RL)\b', code_part):
            issues.append((lb, "error",
                          'subgraph 内嵌套 direction 语句，VS Code预览布局异常，应仅在顶层定义direction'))
    return issues


def _fix_vscode_compat(text: str) -> tuple[str, list[str]]:
    fixes = []
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%%"):
            result.append(line)
            continue
        if "%%" in line:
            code, comment = line.split("%%", 1)
        else:
            code, comment = line, ""
        new_code = code
        if BR_TAG_RE.search(new_code):
            new_code = BR_TAG_RE.sub(" ", new_code)
            if "br标签移除" not in fixes:
                fixes.append("br标签移除")
        if CIRCLED_NUMBERS_RE.search(new_code):
            def _crep(m): return CIRCLED_NUMBERS.get(m.group(), m.group())
            new_code = CIRCLED_NUMBERS_RE.sub(_crep, new_code)
            if "带圈数字替换" not in fixes:
                fixes.append("带圈数字替换")
        if CJK_BRACKET_RE.search(new_code):
            new_code = new_code.replace("【", "(").replace("】", ")")
            if "中文方括号替换" not in fixes:
                fixes.append("中文方括号替换")
        if ARROW_SYMBOL_RE.search(new_code):
            new_code = ARROW_SYMBOL_RE.sub("-", new_code)
            if "箭头符号替换" not in fixes:
                fixes.append("箭头符号替换")
        result.append(new_code + ("%%" + comment if comment else ""))
    return "\n".join(result), fixes


def _check_generic(block_text: str, start_line: int, dia_type: str) -> List[Tuple[int, str, str]]:
    checker_map = {
        "pie": _pie,
        "gantt": _gantt,
        "timeline": _timeline,
        "xychart-beta": _xy,
        "quadrantChart": _quad,
        "quadrantchart": _quad,
    }
    checker = checker_map.get(dia_type)
    if checker and hasattr(checker, 'check'):
        return checker.check(block_text, start_line)
    return _check_empty_lines(block_text, start_line)


_ff = FlowchartFixer()
_sf = StateDiagramFixer()
_seqf = SequenceDiagramFixer()
_clsf = ClassDiagramFixer()
_erf = ErDiagramFixer()
_mmf = MindmapFixer()
_pief = PieFixer()
_ganttf = GanttFixer()
_genf = GenericFixer()


def _fix_flowchart(block_text: str) -> Tuple[str, List[str]]:
    return _ff.fix(block_text)


def _fix_state_diagram(block_text: str) -> Tuple[str, List[str]]:
    return _sf.fix(block_text)


def _fix_sequence_diagram(block_text: str) -> Tuple[str, List[str]]:
    return _seqf.fix(block_text)


def _fix_classDiagram(block_text: str) -> Tuple[str, List[str]]:
    return _clsf.fix(block_text)


def _fix_erDiagram(block_text: str) -> Tuple[str, List[str]]:
    return _erf.fix(block_text)


def _fix_mindmap(block_text: str) -> Tuple[str, List[str]]:
    return _mmf.fix(block_text)


def _fix_pie(block_text: str) -> Tuple[str, List[str]]:
    return _pief.fix(block_text)


def _fix_gantt(block_text: str) -> Tuple[str, List[str]]:
    return _ganttf.fix(block_text)


def _fix_generic(block_text: str) -> Tuple[str, List[str]]:
    return _genf.fix(block_text)


DIAGRAM_FIXERS = {
    "flowchart": _fix_flowchart,
    "stateDiagram": _fix_state_diagram,
    "sequenceDiagram": _fix_sequence_diagram,
    "classDiagram": _fix_classDiagram,
    "erDiagram": _fix_erDiagram,
    "pie": _fix_generic,
    "gantt": _fix_generic,
    "timeline": _fix_generic,
    "mindmap": _fix_mindmap,
    "xychart-beta": _fix_generic,
    "quadrantchart": _fix_generic,
}


DIAGRAM_CHECKERS = {
    "flowchart": _check_flowchart,
    "stateDiagram": _check_state_diagram,
    "sequenceDiagram": _check_sequence_diagram,
    "classDiagram": _check_classDiagram,
    "erDiagram": _check_erDiagram,
    "pie": lambda b, sl: _check_generic(b, sl, "pie"),
    "gantt": lambda b, sl: _check_generic(b, sl, "gantt"),
    "timeline": lambda b, sl: _check_generic(b, sl, "timeline"),
    "mindmap": _check_mindmap,
    "xychart-beta": lambda b, sl: _check_generic(b, sl, "xychart-beta"),
    "quadrantchart": lambda b, sl: _check_generic(b, sl, "quadrantChart"),
}


def _find_md_files(root_dir: Path, exclude_dirs: set[str]) -> List[Path]:
    scanner = FileScanner(root_dir, exclude_dirs)
    return scanner.scan()


def process_mermaid_fences(*args, **kwargs):
    from lib.mermaid.processor import process_mermaid_fences as pmf
    return pmf(*args, **kwargs)


def _process_file(file_path: Path, root_dir: Path, fix: bool, dry_run: bool
                  ) -> Tuple[List[Tuple[int, str, str]], int, List[Tuple[str, str]]]:
    import difflib
    content = file_path.read_text(encoding="utf-8")
    all_issues: List[Tuple[int, str, str]] = []
    total_fixes = 0
    diffs: List[Tuple[str, str]] = []

    def _rep_block(m):
        nonlocal total_fixes
        fence_start, block_text, fence_end = m.group(1), m.group(2), m.group(3)
        start_off = m.start(2)
        start_line = _line_from_offset(content, start_off)

        dia_type = _detect_diagram_type(block_text)
        fixer = DIAGRAM_FIXERS.get(dia_type, _fix_generic)
        checker = DIAGRAM_CHECKERS.get(dia_type, lambda b, sl: _check_generic(b, sl, dia_type))

        rel_path = file_path.relative_to(root_dir).as_posix()
        _debug_enter(rel_path, start_line, dia_type)
        _debug_log("block", f"发现 {dia_type} 代码块，文本长度 {len(block_text)} 字符")

        if fix or dry_run:
            fixed_text, fixes = fixer(block_text)
            if fixes:
                _debug_log("block", f"fixer返回修复项: {fixes}")
        else:
            fixed_text, fixes = block_text, []

        if fix or dry_run:
            vscode_fixed, vscode_fixes = _fix_vscode_compat(fixed_text)
            if vscode_fixes:
                fixed_text = vscode_fixed
                fixes.extend(vscode_fixes)
                _debug_log("vscode:fix", f"VS Code兼容修复: {vscode_fixes}")
        check_text = fixed_text if fix else block_text
        issues = checker(check_text, start_line)
        sec_issues = _check_security(check_text, start_line)
        issues.extend(sec_issues)
        vscode_issues = _check_vscode_compat(check_text, start_line)
        issues.extend(vscode_issues)
        all_issues.extend(issues)
        _debug_log("block", f"checker返回问题 {len(issues)} 个（含安全检测 {len(sec_issues)} 个）")

        if fixes and fixed_text != block_text:
            total_fixes += 1
            if dry_run:
                old_lines = block_text.split("\n")
                new_lines = fixed_text.split("\n")
                diff = difflib.unified_diff(
                    old_lines, new_lines,
                    fromfile=f"{file_path.relative_to(root_dir).as_posix()} (before)",
                    tofile=f"{file_path.relative_to(root_dir).as_posix()} (after)",
                    lineterm="", n=2
                )
                diffs.append(("\n".join(diff), ", ".join(fixes)))
            return fence_start + fixed_text + fence_end
        return m.group(0)

    new_content = MERMAID_FENCE_RE.sub(_rep_block, content)
    if fix and not dry_run and new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
    return all_issues, total_fixes, diffs


def run(project_root: Path, args) -> int:
    check_root = Path(args.path).resolve() if getattr(args, "path", None) else project_root
    exclude = set(getattr(args, "exclude", []) or [])
    fix = getattr(args, "fix", False)
    dry_run = getattr(args, "dry_run", False)
    debug = getattr(args, "debug", False)
    _set_debug(debug)

    md_files = _find_md_files(check_root, exclude)
    total = len(md_files)
    files_with_issues = 0
    total_errors = 0
    total_warnings = 0
    total_fixes = 0
    all_diffs: list[tuple[str, str]] = []

    fix_mode = fix or dry_run
    fix_label = " (dry-run)" if dry_run else ""

    print(f"[检查] Mermaid 语法安全检查{fix_label}")
    print(f"   扫描目录: {check_root}")
    print(f"   文件总数: {total}")
    if fix_mode:
        print(f"   修复模式: {'预览(dry-run)' if dry_run else '自动修复'}")
    print()

    for md in sorted(md_files):
        issues, fixes, diffs = _process_file(md, project_root, fix=fix, dry_run=dry_run)
        total_fixes += fixes
        all_diffs.extend(diffs)
        if issues:
            files_with_issues += 1
            errs = [i for i in issues if i[1] == "error"]
            warns = [i for i in issues if i[1] == "warning"]
            total_errors += len(errs)
            total_warnings += len(warns)
            rel = md.relative_to(project_root).as_posix()
            print(f"[文件] {rel}")
            for ln, lvl, msg in sorted(issues, key=lambda x: x[0]):
                color = ANSI_RED if lvl == "error" else ANSI_YELLOW
                icon = "[错误]" if lvl == "error" else "[警告]"
                print(f"   {color}{icon} L{ln}: {msg}{ANSI_RESET}")
            if fixes > 0 and not dry_run:
                print(f"   {ANSI_CYAN}[修复] 已修复 {fixes} 个代码块{ANSI_RESET}")
            print()

    if dry_run and all_diffs:
        print("=" * 60)
        print(f"[预览] 修复预览（{len(all_diffs)} 个代码块变更）:")
        print()
        for diff_text, fix_desc in all_diffs:
            print(f"   [修复] {fix_desc}:")
            for line in diff_text.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    print(f"   {ANSI_GREEN}{line}{ANSI_RESET}")
                elif line.startswith("-") and not line.startswith("---"):
                    print(f"   {ANSI_RED}{line}{ANSI_RESET}")
                elif line.startswith("@@"):
                    print(f"   {ANSI_CYAN}{line}{ANSI_RESET}")
                else:
                    print(f"   {line}")
            print()

    print("=" * 60)
    print(f"[结果] 检查结果:")
    print(f"   扫描文件: {total}")
    print(f"   问题文件: {files_with_issues}")
    print(f"   {ANSI_RED}错误: {total_errors}{ANSI_RESET}")
    print(f"   {ANSI_YELLOW}警告: {total_warnings}{ANSI_RESET}")
    if fix_mode:
        print(f"   {ANSI_GREEN}自动修复: {total_fixes} 个文件块{ANSI_RESET}")

    if total_errors > 0 and not fix:
        print(f"\n{ANSI_RED}[错误] 发现 {total_errors} 个错误，请修复后再提交。可使用 --fix 参数自动修复部分问题，或使用 --dry-run 预览修复效果。{ANSI_RESET}")
        return 1
    if fix and total_errors > 0:
        print(f"\n{ANSI_YELLOW}[警告] 已自动修复可修复问题，仍有 {total_errors} 个错误需手动修复。{ANSI_RESET}")
        return 1
    if total_warnings > 0:
        print(f"\n{ANSI_YELLOW}[警告] 发现 {total_warnings} 个警告，建议检查。{ANSI_RESET}")
        return 0
    print(f"\n{ANSI_GREEN}[通过] 所有 Mermaid 代码块检查通过！{ANSI_RESET}")
    return 0
