"""批量修复剩余的 frontmatter 路径问题。

处理以下模式：
1. comprehensive-retrospective-template/ → external: 标记（模板已删除）
2. .agents/insights/ 路径 → external: 标记（已迁移）
3. d:/spaces/SpecWeave/ 绝对路径 → 转换为相对路径
4. d:\\AI\\ 跨项目路径 → external: 标记
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / ".agents" / "scripts"))


def fix_md_source(content: str, md_path: Path) -> str:
    """修复 md 文件 YAML frontmatter 中的 source 路径。"""
    md_dir = md_path.parent

    def replace_source(match):
        prefix = match.group(1)  # source: " or source: '
        value = match.group(2)

        # Pattern 1: comprehensive-retrospective-template/
        if 'comprehensive-retrospective-template/' in value:
            return f'source: {prefix}external: 模板引用-{value}{prefix}'

        # Pattern 2: .agents/insights/
        if value.startswith('.agents/insights/'):
            return f'source: {prefix}external: 已迁移-{value}{prefix}'

        # Pattern 3: d:/spaces/SpecWeave/ absolute path → relative
        if 'd:/spaces/SpecWeave/' in value or 'd:\\\\spaces\\\\SpecWeave\\\\' in value:
            # Normalize path
            normalized = value.replace('d:/spaces/SpecWeave/', '').replace('d:\\\\spaces\\\\SpecWeave\\\\', '')
            # Handle multi-path (separated by |)
            if '|' in normalized:
                parts = [p.strip() for p in normalized.split('|')]
                fixed_parts = []
                for part in parts:
                    target = ROOT / part
                    if target.exists():
                        rel = os.path.relpath(str(target), str(md_dir)).replace('\\', '/')
                        fixed_parts.append(rel)
                    else:
                        fixed_parts.append(f'external: 不存在-{part}')
                return f'source: {prefix}{" | ".join(fixed_parts)}{prefix}'
            else:
                target = ROOT / normalized
                if target.exists():
                    rel = os.path.relpath(str(target), str(md_dir)).replace('\\', '/')
                    return f'source: {prefix}{rel}{prefix}'
                else:
                    return f'source: {prefix}external: 不存在-{normalized}{prefix}'

        # Pattern 4: d:\\AI\\ or d:/AI/ cross-project
        if 'd:\\\\AI\\\\' in value or 'd:/AI/' in value:
            return f'source: {prefix}external: 外部项目引用{prefix}'

        return match.group(0)

    # Match: source: "value" or source: 'value' (YAML format)
    content = re.sub(
        r'source:\s*("|\')([^"\']+)\1',
        replace_source,
        content
    )
    return content


def fix_toml_source(content: str) -> str:
    """修复 TOML 文件中的 source 路径。"""

    def replace_toml_source(match):
        value = match.group(1)

        if 'comprehensive-retrospective-template/' in value:
            return f'source = "external: 模板引用-{value}"'

        if value.startswith('.agents/insights/'):
            return f'source = "external: 已迁移-{value}"'

        if 'd:\\\\AI\\\\' in value or 'd:/AI/' in value:
            return 'source = "external: 外部项目引用"'

        return match.group(0)

    content = re.sub(
        r'^source\s*=\s*"([^"]+)"\s*$',
        replace_toml_source,
        content,
        flags=re.MULTILINE
    )
    return content


def main():
    docs = ROOT / "docs"
    meta = ROOT / ".meta" / "toml" / "docs"

    md_fixed = 0
    toml_fixed = 0

    # Fix markdown files
    for md in docs.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_content = fix_md_source(content, md)
        if new_content != content:
            md.write_text(new_content, encoding="utf-8", newline="")
            md_fixed += 1
            print(f"  Fixed MD: {md.relative_to(ROOT)}")

    # Fix TOML files
    if meta.exists():
        for toml in meta.rglob("*.toml"):
            try:
                content = toml.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            new_content = fix_toml_source(content)
            if new_content != content:
                toml.write_text(new_content, encoding="utf-8", newline="")
                toml_fixed += 1
                print(f"  Fixed TOML: {toml.relative_to(ROOT)}")

    print(f"\n总计: 修复 {md_fixed} 个 md 文件, {toml_fixed} 个 toml 文件")


if __name__ == "__main__":
    main()
