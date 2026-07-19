#!/usr/bin/env python3
"""批量修复目录链接和缺失文件的 frontmatter source 路径。

修复策略：
1. 目录链接（目录内有README.md）→ 追加 /README.md
2. 目录链接（目录内无README.md）→ 标记为 external: 目录无README
3. 缺失文件且包含 d:\AI\ 或 d:/AI/ → external: 外部项目引用
4. 缺失文件其他 → external: 不存在
"""

import re
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def fix_source_value(value: str, md_path: Path) -> str:
    """修复单个 source 值中的路径问题。"""
    md_dir = md_path.parent

    # 跳过已标记为 external: 的值
    if value.startswith("external:"):
        return value

    # 跳过 http/https/mailto/session/spec 前缀
    if value.startswith(("http://", "https://", "mailto:", "session:", "spec:")):
        return value

    # 处理 d:\AI\ 或 d:/AI/ 跨项目路径
    if "d:\\AI\\" in value or "d:/AI/" in value or "d:\\\\AI\\\\" in value:
        return "external: 外部项目引用"

    # 处理多路径分隔（+ | ; ,）
    if any(sep in value for sep in [" + ", " | ", "; ", ", "]):
        parts = re.split(r'\s*[+|,;]\s*', value)
        fixed_parts = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            fixed_parts.append(fix_single_path(part, md_dir))
        return " + ".join(fixed_parts)

    return fix_single_path(value, md_dir)


def is_likely_path(path_str: str) -> bool:
    """判断字符串是否可能是文件路径（而非模式ID等纯标识符）。"""
    if "/" not in path_str and "\\" not in path_str:
        if not path_str.startswith(("../", "./", "docs/", "lib/", "retrospective/", "apps/", "task-reports/")):
            if not re.search(r'\.(md|toml|py|js|ts|json|yaml|yml|sh|ps1)$', path_str, re.IGNORECASE):
                return False
    return True


def fix_single_path(path_str: str, md_dir: Path) -> str:
    """修复单个路径。"""
    path_str = path_str.strip().strip('"').strip("'")

    if not path_str:
        return path_str

    if path_str.startswith(("external:", "http://", "https://", "mailto:", "session:", "spec:")):
        return path_str

    # 如果不像是文件路径（如模式ID），直接返回
    if not is_likely_path(path_str):
        return path_str

    # d:\AI\ 或 d:/AI/ 跨项目路径
    if "d:\\AI\\" in path_str or "d:/AI/" in path_str or "d:\\\\AI\\\\" in path_str:
        return "external: 外部项目引用"

    # 提取路径和锚点
    if "#" in path_str:
        path_part, anchor = path_str.split("#", 1)
        anchor = "#" + anchor
    else:
        path_part = path_str
        anchor = ""

    path_part = path_part.strip()
    if not path_part:
        return path_str

    # 检查目标是否存在
    target = (md_dir / path_part).resolve()

    if target.exists():
        if target.is_dir():
            # 目录链接
            readme = target / "README.md"
            if readme.exists():
                return path_part.rstrip("/") + "/" + "README.md" + anchor
            else:
                return f"external: 目录无README-{path_part}" + anchor
        else:
            # 文件存在，路径正确
            return path_str
    else:
        # 文件不存在
        # 检查是否是 lib/checks/vendor.py 等代码路径
        if path_part.startswith("lib/") or path_part.startswith(".agents/rules/"):
            # 这些可能是相对于项目根目录的路径
            root_target = ROOT / path_part
            if root_target.exists():
                rel = os.path.relpath(str(root_target), str(md_dir)).replace("\\", "/")
                return rel + anchor
            else:
                return f"external: 不存在-{path_part}" + anchor

        # 检查是否是 retrospective/ 开头的路径（相对于 docs/retrospective/）
        if path_part.startswith("retrospective/"):
            retro_target = ROOT / "docs" / path_part
            if retro_target.exists():
                if retro_target.is_dir():
                    readme = retro_target / "README.md"
                    if readme.exists():
                        rel = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                        return rel + anchor
                else:
                    rel = os.path.relpath(str(retro_target), str(md_dir)).replace("\\", "/")
                    return rel + anchor
            else:
                return f"external: 不存在-{path_part}" + anchor

        # 检查是否是 apps/ 开头的路径
        if path_part.startswith("apps/"):
            apps_target = ROOT / path_part
            if apps_target.exists():
                if apps_target.is_dir():
                    readme = apps_target / "README.md"
                    if readme.exists():
                        rel = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                        return rel + anchor
                    else:
                        return f"external: 目录无README-{path_part}" + anchor
                else:
                    rel = os.path.relpath(str(apps_target), str(md_dir)).replace("\\", "/")
                    return rel + anchor
            else:
                return f"external: 不存在-{path_part}" + anchor

        # 检查是否是 task-reports/ 开头的路径
        if path_part.startswith("task-reports/"):
            task_target = ROOT / ".agents/docs/retrospective/reports" / path_part
            if task_target.exists():
                if task_target.is_dir():
                    readme = task_target / "README.md"
                    if readme.exists():
                        rel = os.path.relpath(str(readme), str(md_dir)).replace("\\", "/")
                        return rel + anchor
                    else:
                        return f"external: 目录无README-{path_part}" + anchor
                else:
                    rel = os.path.relpath(str(task_target), str(md_dir)).replace("\\", "/")
                    return rel + anchor
            else:
                return f"external: 不存在-{path_part}" + anchor

        return f"external: 不存在-{path_part}" + anchor


def fix_frontmatter(content: str, md_path: Path) -> str:
    """修复 md 文件 YAML frontmatter 中的 source 路径。"""
    md_dir = md_path.parent

    def replace_source_string(match):
        prefix = match.group(1)  # " or '
        value = match.group(2)
        fixed = fix_source_value(value, md_path)
        return f"source: {prefix}{fixed}{prefix}"

    # 匹配 source: "..." 或 source: '...'
    content = re.sub(
        r'source:\s*("|\')([^"\']+)\1',
        replace_source_string,
        content
    )

    def replace_array_item(match):
        indent = match.group(1)  # 缩进 + - -
        prefix = match.group(2)  # " or '
        value = match.group(3)
        fixed = fix_source_value(value, md_path)
        return f'{indent}{prefix}{fixed}{prefix}'

    # 匹配 YAML 数组项（包括双重 - 缩进）:  - "value" 或  -   - "value"
    content = re.sub(
        r'^(\s*(?:-\s*)+-\s*)("|\')([^"\']+)\2',
        replace_array_item,
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

        content = fix_frontmatter(content, md_path)

        if content != original:
            md_path.write_text(content, encoding="utf-8", newline="")
            fixed_count += 1
            print(f"  Fixed: {md_path.relative_to(ROOT)}")

    print(f"\nTotal fixed: {fixed_count} files")


if __name__ == "__main__":
    main()
