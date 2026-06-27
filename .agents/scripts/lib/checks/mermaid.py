"""Mermaid 语法安全检查（来自 check-mermaid.py）。"""

import re
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS, ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_RESET, ANSI_CYAN

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_CHARS_RE = re.compile(r"[\u4e00-\u9fff]")


def _find_md_files(root_dir: Path, exclude_dirs: set[str]) -> list[Path]:
    files = []
    for md in root_dir.rglob("*.md"):
        parts = set(md.parts)
        if EXCLUDED_DIRS & parts:
            continue
        try:
            rel = md.relative_to(root_dir).as_posix()
        except ValueError:
            rel = str(md)
        if any(rel.startswith(excl.replace("\\", "/")) for excl in exclude_dirs):
            continue
        files.append(md)
    return files


def _line_from_offset(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def _fix_block(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text
    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")

    node_pat = re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]", re.MULTILINE)

    def _node_rep(m):
        pre, nid, ntxt = m.group(1), m.group(2), m.group(3)
        if ntxt.startswith('"') and ntxt.endswith('"'):
            return m.group(0)
        if CHINESE_CHARS_RE.search(ntxt) or "@" in ntxt or "#" in ntxt or "≥" in ntxt or "≤" in ntxt or "+" in ntxt:
            return f'{pre}{nid}["{ntxt}"]'
        return m.group(0)

    text_new = node_pat.sub(_node_rep, text)
    text_orig = node_pat.sub(lambda m: m.group(0), text)
    if text_new != text_orig:
        fixes.append("节点引号")
    text = text_new

    edge_pat = re.compile(r"(-->)\|([^\"|][^|]*?)\|")

    def _edge_rep(m):
        arrow, label = m.group(1), m.group(2)
        if label.startswith('"') and label.endswith('"'):
            return m.group(0)
        if CHINESE_CHARS_RE.search(label) or "@" in label or "#" in label or "/" in label or "+" in label or label in ("是", "否"):
            return f'{arrow}|"{label}"|'
        return m.group(0)

    text = edge_pat.sub(_edge_rep, text)

    num_pat = re.compile(r"(\d+)\.(\s+)")
    text_before = text
    text = num_pat.sub(lambda m: f"{m.group(1)}：{m.group(2)}", text)
    if text != text_before:
        fixes.append("数字点格式")

    return text, fixes


def _check_block(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = []
    if "\n\n" in block_text or "\n \n" in block_text:
        issues.append((start_line, "error", "Mermaid 代码块内存在空行，可能导致解析中断"))
    sub_pat = re.compile(r"^(\s*subgraph\s+)([^\s\[\"]+)(.*)$", re.MULTILINE)
    for m in sub_pat.finditer(block_text):
        sid = m.group(2).strip()
        if CHINESE_CHARS_RE.search(sid) or "：" in sid:
            lb = block_text[:m.start()].count("\n") + 1
            issues.append((start_line + lb - 1, "error", f'subgraph 使用裸中文ID「{sid}」，应使用 subgraph EN_ID ["中文标题"] 格式'))
    return issues


def _process_file(file_path: Path, root_dir: Path, fix: bool, dry_run: bool) -> tuple[list[tuple[int, str, str]], int]:
    content = file_path.read_text(encoding="utf-8")
    all_issues: list[tuple[int, str, str]] = []
    total_fixes = 0

    def _rep_block(m):
        nonlocal total_fixes
        fence_start, block_text, fence_end = m.group(1), m.group(2), m.group(3)
        start_off = m.start(2)
        start_line = _line_from_offset(content, start_off)
        if fix:
            fixed_text, fixes = _fix_block(block_text)
        else:
            fixed_text, fixes = block_text, []
        issues = _check_block(fixed_text if fix else block_text, start_line)
        all_issues.extend(issues)
        if fixes:
            total_fixes += 1
            return fence_start + fixed_text + fence_end
        return m.group(0)

    new_content = MERMAID_FENCE_RE.sub(_rep_block, content)
    if fix and not dry_run and new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
    return all_issues, total_fixes


def run(project_root: Path, args) -> int:
    check_root = Path(args.path).resolve() if getattr(args, "path", None) else project_root
    exclude = set(getattr(args, "exclude", []) or [])
    fix = getattr(args, "fix", False)
    dry_run = getattr(args, "dry_run", False)

    md_files = _find_md_files(check_root, exclude)
    total = len(md_files)
    files_with_issues = 0
    total_errors = 0
    total_warnings = 0
    total_fixes = 0

    fix_mode = fix or dry_run
    fix_label = " (dry-run)" if dry_run else ""

    print(f"🔍 Mermaid 语法安全检查{fix_label}")
    print(f"   扫描目录: {check_root}")
    print(f"   文件总数: {total}")
    if fix_mode:
        print(f"   修复模式: {'预览' if dry_run else '自动修复'}")
    print()

    for md in sorted(md_files):
        issues, fixes = _process_file(md, project_root, fix=fix, dry_run=dry_run)
        total_fixes += fixes
        if issues:
            files_with_issues += 1
            errs = [i for i in issues if i[1] == "error"]
            warns = [i for i in issues if i[1] == "warning"]
            total_errors += len(errs)
            total_warnings += len(warns)
            rel = md.relative_to(project_root).as_posix()
            print(f"📄 {rel}")
            for ln, lvl, msg in sorted(issues, key=lambda x: x[0]):
                color = ANSI_RED if lvl == "error" else ANSI_YELLOW
                icon = "❌" if lvl == "error" else "⚠️"
                print(f"   {color}{icon} L{ln}: {msg}{ANSI_RESET}")
            if fixes > 0:
                print(f"   {ANSI_CYAN}🔧 已修复 {fixes} 个代码块{ANSI_RESET}")
            print()

    print("=" * 60)
    print(f"📊 检查结果:")
    print(f"   扫描文件: {total}")
    print(f"   问题文件: {files_with_issues}")
    print(f"   {ANSI_RED}错误: {total_errors}{ANSI_RESET}")
    print(f"   {ANSI_YELLOW}警告: {total_warnings}{ANSI_RESET}")
    if fix_mode:
        print(f"   {ANSI_GREEN}自动修复: {total_fixes} 个文件块{ANSI_RESET}")

    if total_errors > 0 and not fix:
        print(f"\n{ANSI_RED}❌ 发现 {total_errors} 个错误，请修复后再提交。可使用 --fix 参数自动修复部分问题。{ANSI_RESET}")
        return 1
    if fix and total_errors > 0:
        print(f"\n{ANSI_YELLOW}⚠️  已自动修复可修复问题，仍有 {total_errors} 个错误需手动修复（主要为裸中文 subgraph ID）。{ANSI_RESET}")
        return 1
    if total_warnings > 0:
        print(f"\n{ANSI_YELLOW}⚠️  发现 {total_warnings} 个警告，建议检查。{ANSI_RESET}")
        return 0
    print(f"\n{ANSI_GREEN}✅ 所有 Mermaid 代码块检查通过！{ANSI_RESET}")
    return 0
