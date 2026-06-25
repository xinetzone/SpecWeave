"""Markdown 链接修复工具。

提供检测和修复 Markdown 文档中断链的能力，核心功能：
- 检测 file:/// 本地绝对路径链接
- 将绝对路径自动转换为正确的相对路径
- 处理同文件自引用（简化为纯锚点）
- 支持文件名映射（文件重命名场景）
- 支持行号偏移映射（内容移位场景）
- Dry-run 模式预览变更不写入

典型用法：
    from lib.link_fixer import fix_directory_links

    rename_map = {"竹简悟道.html": "竹简悟道_完整版.html"}
    fixes = fix_directory_links(
        root_dir=Path("apps/zhujian-wudao"),
        project_root=Path("."),
        rename_map=rename_map,
        dry_run=True,
    )
"""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# 匹配 file:/// 本地绝对路径 URL（支持 Windows 盘符和 Unix 路径，捕获完整路径含锚点）
FILE_URL_RE = re.compile(
    r"file:///([A-Za-z]:/[^\s)]+|/[^\s)]+)"
)

# 匹配 Markdown 内联链接: [text](url) — 同 check-links.py 保持一致
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


@dataclass
class LinkFix:
    """记录一次链接修复操作。"""
    file_path: Path
    line_num: int
    link_text: str
    old_url: str
    new_url: str
    fix_type: str  # "absolute_to_relative" | "same_file_anchor" | "filename_mapped" | "line_remapped"
    reason: str = ""

    def __str__(self) -> str:
        return f"  L{self.line_num}: [{self.link_text}] {self.old_url} → {self.new_url} ({self.fix_type})"


def parse_file_url(url: str) -> tuple[str, str]:
    """解析 file:/// URL，返回 (文件路径部分, 锚点部分)。

    Args:
        url: 完整的 file:/// URL，可能包含 #L行号 锚点。

    Returns:
        (file_path_str, anchor) 元组。锚点以 '#' 开头，无锚点时为空字符串。
    """
    if "#" in url:
        path_part, anchor = url.split("#", 1)
        return path_part, f"#{anchor}"
    return url, ""


def extract_filename_from_url(file_url_path: str) -> str:
    """从 file:/// 路径中提取文件名。

    Args:
        file_url_path: 去除 file:/// 前缀和锚点后的文件路径。

    Returns:
        文件名（含扩展名）。
    """
    return Path(file_url_path).name


def find_file_in_project(filename: str, project_root: Path, search_subdir: Path | None = None) -> Path | None:
    """在项目中查找指定文件名的文件。

    优先在 search_subdir 下查找，找不到再全局搜索。
    返回第一个匹配的文件绝对路径，找不到返回 None。

    Args:
        filename: 要查找的文件名（含扩展名）。
        project_root: 项目根目录。
        search_subdir: 优先搜索的子目录（相对于 project_root）。

    Returns:
        匹配文件的绝对路径，或 None。
    """
    project_root = project_root.resolve()
    search_dirs = []

    if search_subdir is not None:
        first_try = (project_root / search_subdir).resolve()
        if first_try.exists():
            search_dirs.append(first_try)

    search_dirs.append(project_root)

    for search_dir in search_dirs:
        for candidate in search_dir.rglob(filename):
            if candidate.is_file():
                return candidate.resolve()

    return None


def compute_relative_path(source_file: Path, target_file: Path) -> str:
    """计算从 source_file 到 target_file 的相对路径（POSIX 格式，用于 Markdown 链接）。

    如果 source 和 target 是同一文件，返回空字符串（用于纯锚点引用）。

    Args:
        source_file: 包含链接的源文件绝对路径。
        target_file: 被引用的目标文件绝对路径。

    Returns:
        相对路径字符串（POSIX 格式），同文件时返回空字符串。
    """
    source_file = source_file.resolve()
    target_file = target_file.resolve()

    if source_file == target_file:
        return ""

    source_dir = source_file.parent
    return os_path_to_posix(Path(os.path.relpath(str(target_file), str(source_dir))))


def os_path_to_posix(path: Path | str) -> str:
    """将 OS 路径转换为 POSIX 格式（Markdown 链接通用）。"""
    return str(path).replace("\\", "/")


def apply_filename_mapping(file_path: str, rename_map: dict[str, str] | None) -> str:
    """应用文件名映射，处理文件重命名场景。

    Args:
        file_path: 原始文件路径（可能是 file:/// 路径或普通路径）。
        rename_map: {旧文件名: 新文件名} 映射表。

    Returns:
        映射后的文件名（仅替换文件名部分，保留目录结构）。
    """
    if not rename_map:
        return file_path

    p = Path(file_path)
    old_name = p.name
    if old_name in rename_map:
        new_name = rename_map[old_name]
        return os_path_to_posix(p.parent / new_name) if p.parent.name else new_name
    return file_path


def apply_line_remap(anchor: str, line_remap: dict[str, dict[int, int]] | None, source_filename: str) -> str:
    """应用行号重映射，处理文件内容移位后行号变化的场景。

    Args:
        anchor: 锚点字符串（如 '#L656-L692'）。
        line_remap: {文件名: {旧行号: 新行号}} 映射表。
        source_filename: 源文件名（用于查找对应映射）。

    Returns:
        重映射后的锚点字符串。
    """
    if not line_remap or not anchor or not anchor.startswith("#L"):
        return anchor

    basename = Path(source_filename).name
    if basename not in line_remap:
        return anchor

    mapping = line_remap[basename]
    line_spec = anchor[2:]  # 去掉 "#L" 前缀

    def _parse_line_num(s: str) -> int | None:
        s = s.lstrip("L")
        try:
            return int(s)
        except ValueError:
            return None

    if "-" in line_spec:
        start_str, end_str = line_spec.split("-", 1)
        start_line = _parse_line_num(start_str)
        end_line = _parse_line_num(end_str)
        if start_line is not None and end_line is not None:
            new_start = mapping.get(start_line, start_line)
            new_end = mapping.get(end_line, end_line)
            return f"#L{new_start}-L{new_end}"
        return anchor
    else:
        line_num = _parse_line_num(line_spec)
        if line_num is not None:
            new_line = mapping.get(line_num, line_num)
            return f"#L{new_line}"
        return anchor


def fix_link_url(
    old_url: str,
    source_file: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
) -> tuple[str, str, str] | None:
    """修复单个链接 URL，返回 (new_url, fix_type, reason) 或 None（无需修复）。

    修复策略（按优先级）：
    1. file:/// 绝对路径 → 解析目标文件位置并计算相对路径
    2. 同文件引用（文件名指向自身）→ 简化为纯锚点
    3. 文件名映射 → 替换重命名的文件名
    4. 行号重映射 → 调整移位后的行号

    Args:
        old_url: 原始 URL。
        source_file: 包含此链接的 Markdown 文件路径。
        project_root: 项目根目录。
        rename_map: 文件重命名映射 {旧文件名: 新文件名}。
        line_remap: 行号重映射 {文件名: {旧行号: 新行号}}。
        prefer_subdir: 查找目标文件时优先搜索的子目录。

    Returns:
        (new_url, fix_type, reason) 元组，或 None（无需修复/无法修复）。
    """
    file_url_match = FILE_URL_RE.match(old_url)
    anchor = ""
    file_part = old_url

    if file_url_match:
        raw_path = file_url_match.group(1)
        file_part, anchor = parse_file_url(raw_path)
        filename = extract_filename_from_url(file_part)
        filename = apply_filename_mapping(filename, rename_map)
        anchor = apply_line_remap(anchor, line_remap, filename)

        target_file = find_file_in_project(filename, project_root, prefer_subdir)
        if target_file is None:
            return None

        rel_path = compute_relative_path(source_file, target_file)

        if rel_path == "":
            new_url = anchor if anchor else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor}"
            fix_type = "absolute_to_relative"
            reason = f"绝对路径 → 相对路径（目标: {target_file.name}）"

        return (new_url, fix_type, reason)

    if old_url.startswith("#"):
        return None

    if not old_url.startswith("http://") and not old_url.startswith("https://") and not old_url.startswith("mailto:"):
        clean_url = old_url.split("#")[0]
        if not clean_url:
            return None

        target = (source_file.parent / clean_url).resolve()
        if target.exists():
            return None

        target_filename = Path(clean_url).name
        if rename_map and target_filename in rename_map:
            new_filename = rename_map[target_filename]
            new_clean = os_path_to_posix(Path(clean_url).parent / new_filename) if Path(clean_url).parent.name else new_filename
            new_target = (source_file.parent / new_clean).resolve()
            if new_target.exists():
                url_anchor = old_url[len(clean_url):]
                url_anchor = apply_line_remap(url_anchor, line_remap, new_filename)
                new_url = f"{new_clean}{url_anchor}"
                return (new_url, "filename_mapped", f"文件名映射: {target_filename} → {new_filename}")

        guessed = find_file_in_project(target_filename, project_root, prefer_subdir)
        if guessed is not None:
            rel_path = compute_relative_path(source_file, guessed)
            url_anchor = ""
            if "#" in old_url:
                url_anchor = "#" + old_url.split("#", 1)[1]
            url_anchor = apply_line_remap(url_anchor, line_remap, guessed.name)
            new_url = f"{rel_path}{url_anchor}" if rel_path else (url_anchor if url_anchor else "#")
            fix_type = "absolute_to_relative" if not rel_path else "broken_relative_fixed"
            reason = f"断链修复: {clean_url} → {rel_path or '(同文件)'}"
            return (new_url, fix_type, reason)

    return None


def fix_file_links(
    file_path: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = False,
) -> list[LinkFix]:
    """修复单个 Markdown 文件中的断链。

    Args:
        file_path: 要修复的 Markdown 文件路径。
        project_root: 项目根目录。
        rename_map: 文件重命名映射。
        line_remap: 行号重映射。
        prefer_subdir: 查找目标文件时优先搜索的子目录。
        dry_run: 仅预览不写入文件。

    Returns:
        修复操作列表。
    """
    file_path = file_path.resolve()
    content = file_path.read_text(encoding="utf-8")
    fixes: list[LinkFix] = []
    new_content = content

    offset = 0
    for m in INLINE_LINK_RE.finditer(content):
        text = m.group(1)
        old_url = m.group(2).strip()

        if is_code_fence_context(content, m.start()):
            continue

        result = fix_link_url(
            old_url,
            file_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
        )

        if result is None:
            continue

        new_url, fix_type, reason = result
        old_link = f"[{text}]({old_url})"
        new_link = f"[{text}]({new_url})"

        start = m.start() + offset
        end = m.end() + offset
        new_content = new_content[:start] + new_link + new_content[end:]
        offset += len(new_link) - len(old_link)

        line_num = content[:m.start()].count("\n") + 1
        fixes.append(LinkFix(
            file_path=file_path,
            line_num=line_num,
            link_text=text,
            old_url=old_url,
            new_url=new_url,
            fix_type=fix_type,
            reason=reason,
        ))

    if fixes and not dry_run:
        file_path.write_text(new_content, encoding="utf-8")

    return fixes


def is_code_fence_context(content: str, pos: int) -> bool:
    """判断位置 pos 是否在三反引号代码块内部（避免修改代码示例中的链接）。"""
    before = content[:pos]
    fence_count = before.count("```")
    return fence_count % 2 == 1


def fix_directory_links(
    root_dir: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = True,
    exclude_dirs: set[str] | None = None,
) -> list[LinkFix]:
    """递归修复目录下所有 Markdown 文件中的断链。

    Args:
        root_dir: 要扫描修复的目录。
        project_root: 项目根目录。
        rename_map: 文件重命名映射 {旧文件名: 新文件名}。
        line_remap: 行号重映射 {文件名: {旧行号: 新行号}}。
        prefer_subdir: 查找目标文件时优先搜索的子目录。
        dry_run: 仅预览不写入文件（默认 True）。
        exclude_dirs: 排除的目录名集合。

    Returns:
        所有修复操作列表。
    """
    from constants import EXCLUDED_DIRS

    if exclude_dirs is None:
        exclude_dirs = set()
    all_excluded = EXCLUDED_DIRS | exclude_dirs

    root_dir = root_dir.resolve()
    project_root = project_root.resolve()
    all_fixes: list[LinkFix] = []

    for md_path in sorted(root_dir.rglob("*.md")):
        parts = set(md_path.parts)
        if all_excluded & parts:
            continue
        fixes = fix_file_links(
            md_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
            dry_run=dry_run,
        )
        all_fixes.extend(fixes)

    return all_fixes


def print_fix_report(fixes: list[LinkFix], dry_run: bool = True) -> None:
    """打印修复报告。

    Args:
        fixes: 修复操作列表。
        dry_run: 是否为预览模式。
    """
    if not fixes:
        print("  未发现需要修复的断链。")
        return

    mode = "预览（未写入）" if dry_run else "已修复"
    print(f"\n链接修复{mode}，共 {len(fixes)} 处：")

    by_file: dict[Path, list[LinkFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file_path, []).append(fix)

    for file_path, file_fixes in sorted(by_file.items()):
        print(f"\n  {file_path.name}（{len(file_fixes)} 处）：")
        for fix in file_fixes:
            print(f"  L{fix.line_num}: [{fix.link_text}] {fix.old_url}")
            print(f"         → {fix.new_url}  [{fix.fix_type}]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Markdown 断链自动修复工具")
    parser.add_argument("--path", type=Path, required=True, help="要修复的目录或文件路径")
    parser.add_argument("--project-root", type=Path, default=None, help="项目根目录（默认自动推断）")
    parser.add_argument("--apply", action="store_true", default=False, help="实际写入修复（默认 dry-run 预览）")
    parser.add_argument("--prefer-subdir", type=str, default=None, help="查找目标文件时优先搜索的子目录")
    parser.add_argument(
        "--rename",
        nargs="*",
        default=[],
        metavar=("OLD=NEW"),
        help="文件名重命名映射，如 --rename 竹简悟道.html=竹简悟道_完整版.html",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = args.project_root or script_dir.parent.parent.parent

    rename_map = {}
    for mapping in args.rename:
        if "=" in mapping:
            old, new = mapping.split("=", 1)
            rename_map[old] = new

    target = args.path.resolve()
    prefer_subdir = Path(args.prefer_subdir) if args.prefer_subdir else None

    print("=" * 60)
    print("Markdown 断链修复工具")
    print("=" * 60)
    print(f"目标路径: {target}")
    print(f"项目根目录: {project_root}")
    print(f"模式: {'实际修复' if args.apply else '预览（dry-run）'}")
    if rename_map:
        print(f"文件名映射: {rename_map}")

    if target.is_file():
        fixes = fix_file_links(
            target, project_root,
            rename_map=rename_map,
            prefer_subdir=prefer_subdir,
            dry_run=not args.apply,
        )
    else:
        fixes = fix_directory_links(
            target, project_root,
            rename_map=rename_map,
            prefer_subdir=prefer_subdir,
            dry_run=not args.apply,
        )

    print_fix_report(fixes, dry_run=not args.apply)
