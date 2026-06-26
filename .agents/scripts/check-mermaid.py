#!/usr/bin/env python3
"""扫描 Markdown 文件中的 Mermaid 代码块，检测常见语法陷阱。

检测项：
1. Mermaid 代码块内空行
2. 含中文/特殊字符未加引号的节点/边标签
3. 中文裸 subgraph ID（含全角字符的 subgraph 声明）
4. 节点/边标签中「数字+英文句点+空格」触发 Markdown 列表的模式
5. 边标签含中文/特殊字符未加引号

支持 --fix 自动修复可安全修复的问题：
- 移除代码块内空行
- 为含中文/特殊字符的节点添加双引号
- 为含中文/特殊字符的边标签添加双引号
- 将「数字+英文句点+空格」替换为中文冒号
"""

import argparse
import re
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS, ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_RESET, ANSI_CYAN
from lib.project import resolve_project_root
from lib.cli import add_common_args

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_CHARS_RE = re.compile(r"[\u4e00-\u9fff]")


def find_markdown_files(root_dir: Path, exclude_dirs: set[str]) -> list[Path]:
    md_files = []
    for md_path in root_dir.rglob("*.md"):
        parts = set(md_path.parts)
        if EXCLUDED_DIRS & parts:
            continue
        try:
            rel_path = md_path.relative_to(root_dir)
        except ValueError:
            rel_path = md_path
        rel_str = rel_path.as_posix()
        if any(rel_str.startswith(excl.replace("\\", "/")) for excl in exclude_dirs):
            continue
        md_files.append(md_path)
    return md_files


def line_number_from_offset(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def fix_mermaid_block(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text

    blank_before = text.count("\n\n") + text.count("\n \n") + text.count("\n\t\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < block_text.count("\n"):
        fixes.append("空行")

    def node_quote_already(m):
        return m.group(0)

    node_pattern = re.compile(
        r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]",
        re.MULTILINE,
    )

    def node_replace(m):
        prefix = m.group(1)
        node_id = m.group(2)
        node_text = m.group(3)
        if node_text.startswith('"') and node_text.endswith('"'):
            return m.group(0)
        if CHINESE_CHARS_RE.search(node_text) or "@" in node_text or "#" in node_text or "≥" in node_text or "≤" in node_text or "+" in node_text:
            return f'{prefix}{node_id}["{node_text}"]'
        return m.group(0)

    text = node_pattern.sub(node_replace, text)
    if text != node_pattern.sub(node_quote_already, block_text):
        fixes.append("节点引号")

    edge_pattern = re.compile(r"(-->)\|([^\"|][^|]*?)\|")

    def edge_replace(m):
        arrow = m.group(1)
        label = m.group(2)
        if label.startswith('"') and label.endswith('"'):
            return m.group(0)
        if CHINESE_CHARS_RE.search(label) or "@" in label or "#" in label or "/" in label or "+" in label or label in ("是", "否"):
            return f'{arrow}|"{label}"|'
        return m.group(0)

    text = edge_pattern.sub(edge_replace, text)

    number_dot_pattern = re.compile(r"(\d+)\.(\s+)")

    def number_dot_replace(m):
        num = m.group(1)
        space = m.group(2)
        return f"{num}：{space}"

    text_before_num = text
    text = number_dot_pattern.sub(number_dot_replace, text)
    if text != text_before_num:
        fixes.append("数字点格式")

    return text, fixes


def check_mermaid_block(block_text: str, block_start_line: int) -> list[tuple[int, str, str]]:
    issues = []

    if "\n\n" in block_text or "\n \n" in block_text:
        line_num = block_start_line
        issues.append((line_num, "error", "Mermaid 代码块内存在空行，可能导致解析中断"))

    subgraph_pattern = re.compile(r"^(\s*subgraph\s+)([^\s\[\"]+)(.*)$", re.MULTILINE)
    for match in subgraph_pattern.finditer(block_text):
        subgraph_id = match.group(2).strip()
        if CHINESE_CHARS_RE.search(subgraph_id) or "：" in subgraph_id:
            line_in_block = block_text[:match.start()].count("\n") + 1
            line_num = block_start_line + line_in_block - 1
            issues.append((line_num, "error", f"subgraph 使用裸中文ID「{subgraph_id}」，应使用 subgraph EN_ID [\"中文标题\"] 格式"))

    return issues


def process_file(file_path: Path, root_dir: Path, fix: bool = False, dry_run: bool = False) -> tuple[list[tuple[int, str, str]], int]:
    rel_path = file_path.relative_to(root_dir).as_posix()
    content = file_path.read_text(encoding="utf-8")
    all_issues = []
    total_fixes = 0

    def replace_block(match):
        nonlocal total_fixes
        fence_start = match.group(1)
        block_text = match.group(2)
        fence_end = match.group(3)
        block_start_offset = match.start(2)
        block_start_line = line_number_from_offset(content, block_start_offset)

        fixed_text, fixes = fix_mermaid_block(block_text) if fix else (block_text, [])
        issues = check_mermaid_block(fixed_text if fix else block_text, block_start_line)
        all_issues.extend(issues)

        if fixes:
            total_fixes += 1
            return fence_start + fixed_text + fence_end
        return match.group(0)

    new_content = MERMAID_FENCE_RE.sub(replace_block, content)

    if fix and not dry_run and new_content != content:
        file_path.write_text(new_content, encoding="utf-8")

    return all_issues, total_fixes


def main():
    parser = argparse.ArgumentParser(description="Mermaid 语法安全检查工具")
    add_common_args(parser)
    parser.add_argument("--exclude", type=str, nargs="*", default=[], help="排除目录（相对于项目根）")
    parser.add_argument("--fix", action="store_true", help="自动修复可安全修复的问题")
    parser.add_argument("--dry-run", action="store_true", help="仅展示修复方案，不实际写入文件")
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    check_root = Path(args.path).resolve() if args.path else project_root

    exclude_dirs = set(args.exclude)
    md_files = find_markdown_files(check_root, exclude_dirs)

    total_files = len(md_files)
    files_with_issues = 0
    total_errors = 0
    total_warnings = 0
    total_fixes = 0

    fix_mode = args.fix or args.dry_run
    fix_label = " (dry-run)" if args.dry_run else ""

    print(f"🔍 Mermaid 语法安全检查{fix_label}")
    print(f"   扫描目录: {check_root}")
    print(f"   文件总数: {total_files}")
    if fix_mode:
        print(f"   修复模式: {'预览' if args.dry_run else '自动修复'}")
    print()

    for md_path in sorted(md_files):
        issues, fixes = process_file(md_path, project_root, fix=args.fix, dry_run=args.dry_run)
        total_fixes += fixes
        if issues:
            files_with_issues += 1
            errors = [i for i in issues if i[1] == "error"]
            warnings = [i for i in issues if i[1] == "warning"]
            total_errors += len(errors)
            total_warnings += len(warnings)
            rel_path = md_path.relative_to(project_root).as_posix()
            print(f"📄 {rel_path}")
            for line_num, level, msg in sorted(issues, key=lambda x: x[0]):
                color = ANSI_RED if level == "error" else ANSI_YELLOW
                level_icon = "❌" if level == "error" else "⚠️"
                print(f"   {color}{level_icon} L{line_num}: {msg}{ANSI_RESET}")
            if fixes > 0:
                print(f"   {ANSI_CYAN}🔧 已修复 {fixes} 个代码块{ANSI_RESET}")
            print()

    print("=" * 60)
    print(f"📊 检查结果:")
    print(f"   扫描文件: {total_files}")
    print(f"   问题文件: {files_with_issues}")
    print(f"   {ANSI_RED}错误: {total_errors}{ANSI_RESET}")
    print(f"   {ANSI_YELLOW}警告: {total_warnings}{ANSI_RESET}")
    if fix_mode:
        print(f"   {ANSI_GREEN}自动修复: {total_fixes} 个文件块{ANSI_RESET}")

    if total_errors > 0 and not args.fix:
        print(f"\n{ANSI_RED}❌ 发现 {total_errors} 个错误，请修复后再提交。可使用 --fix 参数自动修复部分问题。{ANSI_RESET}")
        sys.exit(1)
    elif args.fix and total_errors > 0:
        print(f"\n{ANSI_YELLOW}⚠️  已自动修复可修复问题，仍有 {total_errors} 个错误需手动修复（主要为裸中文 subgraph ID）。{ANSI_RESET}")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n{ANSI_YELLOW}⚠️  发现 {total_warnings} 个警告，建议检查。{ANSI_RESET}")
        sys.exit(0)
    else:
        print(f"\n{ANSI_GREEN}✅ 所有 Mermaid 代码块检查通过！{ANSI_RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
