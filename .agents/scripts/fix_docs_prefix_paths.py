#!/usr/bin/env python3
"""批量修复 docs/ 前缀的 frontmatter source 路径。

修复策略：
1. source 以 docs/ 开头且目标文件存在 → 修复为相对路径
2. source 以 docs/ 开头且目标文件不存在，但同目录有 README.md → 修复为 README.md#锚点
3. source 以 docs/ 开头且目标文件不存在，无 README.md → 标记为 external: 不存在
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def fix_docs_prefix_source(content: str, md_path: Path) -> str:
    """修复 md 文件 YAML frontmatter 中的 docs/ 前缀 source 路径。"""
    md_dir = md_path.parent

    def replace_source(match):
        prefix = match.group(1)  # " or '
        value = match.group(2)

        if not value.startswith("docs/"):
            return match.group(0)

        # 提取路径和锚点
        if "#" in value:
            path_part, anchor = value.split("#", 1)
            anchor = "#" + anchor
        else:
            path_part = value
            anchor = ""

        # 检查目标文件是否存在（相对于项目根目录）
        target = ROOT / path_part
        if target.exists() and target.is_file():
            # 情况1：目标存在，修复为相对路径
            rel = md_dir.resolve().relative_to(ROOT.resolve())
            # 计算 md 文件到目标文件的相对路径
            import os
            rel_path = os.path.relpath(str(target), str(md_dir)).replace("\\", "/")
            return f"source: {prefix}{rel_path}{anchor}{prefix}"

        # 情况2：目标不存在，检查是否已拆分为子目录
        # 提取报告名（去掉 .md 后缀）
        stem = Path(path_part).stem
        parent_dir = Path(path_part).parent

        # 检查同目录下是否有以 stem 命名的子目录
        sibling_dir = ROOT / parent_dir / stem
        if sibling_dir.exists() and sibling_dir.is_dir():
            readme = sibling_dir / "README.md"
            if readme.exists():
                # 修复为同目录的 README.md
                import os
                rel_path = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                return f"source: {prefix}{rel_path}{anchor}{prefix}"

        # 情况3：检查 spec-system 目录下是否有对应子目录
        # 例如 docs/retrospective/reports/retrospective-report-XXX.md
        # → docs/retrospective/reports/spec-system/retrospective-report-XXX/
        if "retrospective/reports/" in path_part and stem.startswith("retrospective-report"):
            spec_system_dir = ROOT / parent_dir / "spec-system" / stem
            if spec_system_dir.exists() and spec_system_dir.is_dir():
                readme = spec_system_dir / "README.md"
                if readme.exists():
                    import os
                    rel_path = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                    return f"source: {prefix}{rel_path}{anchor}{prefix}"

        # 情况4：目标不存在且无拆分子目录，标记为 external
        return f"source: {prefix}external: 不存在-{path_part}{anchor}{prefix}"

    # 匹配 source: "..." 或 source: '...'
    content = re.sub(
        r'source:\s*("|\')([^"\']+)\1',
        replace_source,
        content
    )
    return content


def fix_docs_prefix_array_source(content: str, md_path: Path) -> str:
    """修复 YAML 数组形式的 source（source: 列表）。"""
    md_dir = md_path.parent

    def replace_array_item(match):
        prefix = match.group(1)  # " or '
        value = match.group(2)

        if not value.startswith("docs/"):
            return match.group(0)

        # 提取路径和锚点（处理 + 分隔的多路径）
        if "+" in value:
            parts = [p.strip() for p in value.split("+")]
        elif "|" in value:
            parts = [p.strip() for p in value.split("|")]
        else:
            parts = [value]

        fixed_parts = []
        for part in parts:
            part = part.strip().strip('"').strip("'")
            if not part.startswith("docs/"):
                fixed_parts.append(part)
                continue

            if "#" in part:
                path_part, anchor = part.split("#", 1)
                anchor = "#" + anchor
            else:
                path_part = part
                anchor = ""

            target = ROOT / path_part
            if target.exists() and target.is_file():
                import os
                rel_path = os.path.relpath(str(target), str(md_dir)).replace("\\", "/")
                fixed_parts.append(rel_path + anchor)
                continue

            stem = Path(path_part).stem
            parent_dir = Path(path_part).parent

            sibling_dir = ROOT / parent_dir / stem
            if sibling_dir.exists() and sibling_dir.is_dir():
                readme = sibling_dir / "README.md"
                if readme.exists():
                    import os
                    rel_path = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                    fixed_parts.append(rel_path + anchor)
                    continue

            if "retrospective/reports/" in path_part and stem.startswith("retrospective-report"):
                spec_system_dir = ROOT / parent_dir / "spec-system" / stem
                if spec_system_dir.exists() and spec_system_dir.is_dir():
                    readme = spec_system_dir / "README.md"
                    if readme.exists():
                        import os
                        rel_path = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                        fixed_parts.append(rel_path + anchor)
                        continue

            fixed_parts.append(f"external: 不存在-{path_part}{anchor}")

        return f'{prefix}{" + ".join(fixed_parts)}{prefix}'

    # 匹配 YAML 数组项:  - "value" 或  - 'value'
    content = re.sub(
        r'^(\s*-\s*)("|\')([^"\']+)\2',
        lambda m: m.group(1) + replace_array_item(m),
        content,
        flags=re.MULTILINE
    )
    return content


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_links",
        ROOT / ".agents" / "scripts" / "check-links.py"
    )
    check_links = importlib.util.module_from_spec(spec)
    sys.modules["check_links"] = check_links
    spec.loader.exec_module(check_links)

    from lib.markdown import find_markdown_files

    docs = ROOT / "docs"
    md_files = find_markdown_files(docs)

    fixed_count = 0
    for md_path in md_files:
        content = md_path.read_text(encoding="utf-8")
        original = content

        content = fix_docs_prefix_source(content, md_path)
        content = fix_docs_prefix_array_source(content, md_path)

        if content != original:
            md_path.write_text(content, encoding="utf-8", newline="")
            fixed_count += 1
            print(f"  Fixed: {md_path.relative_to(ROOT)}")

    print(f"\nTotal fixed: {fixed_count} files")


if __name__ == "__main__":
    main()
