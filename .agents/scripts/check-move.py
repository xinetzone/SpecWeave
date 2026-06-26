#!/usr/bin/env python3
"""文件移动时的路径迁移工具。

当 Markdown 文件从一个目录移动到另一个目录时，自动调整文件内部的
相对链接路径，确保移动后所有链接仍然有效。同时可选地更新其他文件中
指向被移动文件的引用，并在移动后自动运行断链检测与修复。

用法:
  python check-move.py <源文件> <目标文件> [--dry-run] [--update-refs] [--no-auto-fix]
"""

import argparse
import os
import re
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS

# 匹配 Markdown 内联链接: [text](url)
INLINE_LINK_RE = re.compile(r"(\[([^\]]*)\]\([^)]+\))")


def parse_relative_links(content: str) -> list[tuple[str, str, int, int]]:
    """解析文件中的相对链接，返回 [(完整匹配, URL, 起始位置, 结束位置), ...] 列表。"""
    links = []
    for m in INLINE_LINK_RE.finditer(content):
        full = m.group(1)
        # 提取 URL 部分
        url_start = full.rfind("(") + 1
        url_end = full.rfind(")")
        url = full[url_start:url_end].strip()

        # 跳过外部链接、锚点、mailto、file:// 协议
        if (url.startswith("http://") or url.startswith("https://")
                or url.startswith("#") or url.startswith("mailto:")
                or url.startswith("file://")):
            continue

        # 跳过仅锚点或无路径的链接
        clean_url = url.split("#")[0]
        if not clean_url:
            continue

        start = m.start() + url_start
        end = m.start() + url_end
        links.append((full, url, start, end))

    return links


def adjust_link(old_url: str, old_dir: Path, new_dir: Path) -> str:
    """调整单个链接，使其在新目录下仍然指向同一目标。

    old_url: 原始链接（如 ../other.md 或 other.md#section）
    old_dir: 源文件所在目录
    new_dir: 目标文件新目录
    """
    # 分离锚点
    anchor = ""
    if "#" in old_url:
        old_url, anchor = old_url.split("#", 1)
        anchor = "#" + anchor

    if not old_url:
        return anchor  # 纯锚点不变

    # 解析旧链接的绝对路径
    old_target = (old_dir / old_url).resolve()
    # 计算新链接相对于新目录的路径
    new_url = os.path.relpath(str(old_target), str(new_dir.resolve())).replace("\\", "/")

    result = new_url
    if anchor:
        result += anchor
    return result


def adjust_file_content(content: str, old_dir: Path, new_dir: Path) -> str:
    """调整文件中所有相对链接的路径。"""
    links = parse_relative_links(content)
    if not links:
        return content

    # 从后往前替换，避免位置偏移
    parts = []
    last_end = 0
    for full, url, start, end in reversed(links):
        new_url = adjust_link(url, old_dir, new_dir)
        if new_url != url:
            parts.insert(0, content[end:last_end] if last_end else "")
            parts.insert(0, new_url)
            parts.insert(0, content[last_end if last_end else start:start])
            last_end = start
        else:
            # 未变化，跳过
            pass

    if not parts:
        return content

    # 使用原始内容重新构建（更简单可靠的方式）
    result = content
    for full, url, start, end in sorted(links, key=lambda x: x[2], reverse=True):
        new_url = adjust_link(url, old_dir, new_dir)
        if new_url != url:
            result = result[:start] + new_url + result[end:]

    return result


def find_references(root: Path, target_path: Path) -> list[Path]:
    """查找所有引用了目标文件的 Markdown 文件。"""
    refs = []
    for md_file in root.rglob("*.md"):
        if md_file == target_path:
            continue
        # 排除 .git 等目录
        parts = set(md_file.parts)
        if EXCLUDED_DIRS & parts:
            continue

        content = md_file.read_text(encoding="utf-8")
        # 检查是否包含对目标文件的引用
        target_name = target_path.name
        if target_name in content:
            refs.append(md_file)
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="移动 Markdown 文件时自动调整内部链接路径"
    )
    parser.add_argument("source", type=Path, help="源文件路径")
    parser.add_argument("dest", type=Path, help="目标文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅预览变更，不实际修改")
    parser.add_argument("--update-refs", action="store_true", help="同时更新其他文件中指向源文件的引用")
    parser.add_argument("--no-auto-fix", action="store_true", help="移动后跳过自动断链修复")
    args = parser.parse_args()

    source = args.source.resolve()
    dest = args.dest.resolve()

    # 自动推断项目根目录（向上查找 .agents/ 目录）
    from lib.link_fixer import _infer_project_root
    project_root = _infer_project_root(source)
    root = project_root

    if not source.exists():
        print(f"错误: 源文件不存在: {source}", file=sys.stderr)
        return 1

    old_dir = source.parent
    new_dir = dest.parent

    if old_dir == new_dir:
        print("源目录和目标目录相同，无需调整链接")
        return 0

    print(f"源文件: {source}")
    print(f"目标文件: {dest}")
    print(f"目录变更: {old_dir} -> {new_dir}")

    # 读取源文件内容
    content = source.read_text(encoding="utf-8")

    # 调整链接
    new_content = adjust_file_content(content, old_dir, new_dir)

    if new_content == content:
        print("\n无需调整: 文件中没有需要修改的相对链接")
        return 0

    # 显示变更
    links = parse_relative_links(content)
    print(f"\n调整 {len(links)} 个链接:")
    for full, url, start, end in links:
        new_url = adjust_link(url, old_dir, new_dir)
        if new_url != url:
            print(f"  {url} -> {new_url}")

    if args.dry_run:
        print("\n[DRY RUN] 未实际修改文件")
        return 0

    # 写入新内容
    if dest.exists():
        print(f"\n警告: 目标文件已存在，将被覆盖")

    # 创建目标目录
    new_dir.mkdir(parents=True, exist_ok=True)

    # 写入目标文件
    dest.write_text(new_content, encoding="utf-8")
    print(f"\n已写入: {dest}")

    # 删除源文件
    source.unlink()
    print(f"已删除: {source}")

    # 可选：更新其他文件中的引用
    if args.update_refs:
        print("\n查找引用...")
        refs = find_references(root, source)
        if refs:
            print(f"找到 {len(refs)} 个引用文件，更新中...")
            for ref in refs:
                ref_content = ref.read_text(encoding="utf-8")
                # 替换引用
                old_ref = source.relative_to(root).as_posix()
                new_ref = dest.relative_to(root).as_posix()
                if old_ref in ref_content:
                    new_ref_content = ref_content.replace(old_ref, new_ref)
                    if new_ref_content != ref_content:
                        ref.write_text(new_ref_content, encoding="utf-8")
                        print(f"  已更新: {ref.relative_to(root)}")
        else:
            print("未找到引用文件")

    # 自动断链修复：移动后对源目录和目标目录所在层级运行深度校正
    if not args.dry_run and not args.no_auto_fix:
        print("\n自动检测并修复断链...")
        from lib.link_fixer import fix_directory_links, print_fix_report

        # 找到 old_dir 和 new_dir 的最近公共祖先目录（限制在 project_root 内）
        def _common_ancestor(d1: Path, d2: Path, root: Path) -> Path:
            d1_parts = d1.resolve().parts
            d2_parts = d2.resolve().parts
            root_parts = root.resolve().parts
            common_len = 0
            for a, b in zip(d1_parts, d2_parts):
                if a == b:
                    common_len += 1
                else:
                    break
            ancestor = Path(*d1_parts[:common_len])
            # 确保不低于 project_root
            if len(ancestor.parts) < len(root_parts):
                return root
            return ancestor

        scan_root = _common_ancestor(old_dir, new_dir, project_root)
        rel = scan_root.relative_to(project_root) if scan_root != project_root else Path("(项目根)")
        print(f"  扫描范围: {rel}")
        fixes = fix_directory_links(scan_root, project_root, dry_run=False, exclude_dirs=EXCLUDED_DIRS)
        if fixes:
            print_fix_report(fixes, dry_run=False)
        else:
            print("  未发现断链，所有链接均有效。")
    elif args.dry_run and not args.no_auto_fix:
        print("\n[DRY RUN] 跳过自动修复（实际移动后将自动运行断链检测）")

    print("\n完成")
    if not args.no_auto_fix:
        print("提示: 如需验证，运行 python .agents/scripts/check-links.py 检查链接完整性")
    return 0


if __name__ == "__main__":
    sys.exit(main())