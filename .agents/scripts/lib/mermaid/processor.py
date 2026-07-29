"""Mermaid 代码块处理器。"""

from typing import List, Tuple, Optional, Callable

from .common import (
    MERMAID_FENCE_RE,
    detect_diagram_type,
    line_from_offset,
)


def process_mermaid_fences(
    content: str,
    start_line_base: int = 1,
    fix: bool = False,
    checker_registry=None,
    fixer_registry=None,
    security_checker=None,
) -> Tuple[str, List[Tuple[int, str, str]], List[str]]:
    all_issues: List[Tuple[int, str, str]] = []
    all_fixes: List[str] = []

    def _rep_block(m):
        fence_start, block_text, fence_end = m.group(1), m.group(2), m.group(3)
        start_off = m.start(2)
        start_line = start_line_base + line_from_offset(content, start_off) - 1

        dia_type = detect_diagram_type(block_text)

        fixed_text = block_text
        fixes: List[str] = []

        if fix and fixer_registry is not None:
            fixer = fixer_registry.get_fixer(dia_type)
            if fixer is None:
                from .fixers.generic import GenericFixer
                fixer = GenericFixer(dia_type)
            fixed_text, fixes = fixer.fix(block_text)
            all_fixes.extend(fixes)

        text_to_check = fixed_text if fix else block_text

        if checker_registry is not None:
            checker = checker_registry.get_checker(dia_type)
            if checker is not None:
                issues = checker.check(text_to_check, start_line)
                all_issues.extend(issues)

        if security_checker is not None:
            sec_issues = security_checker.check(text_to_check, start_line)
            all_issues.extend(sec_issues)

        if fixes and fixed_text != block_text:
            return fence_start + fixed_text + fence_end
        return m.group(0)

    processed_content = MERMAID_FENCE_RE.sub(_rep_block, content)
    return processed_content, all_issues, all_fixes
