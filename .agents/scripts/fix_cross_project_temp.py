"""修复 frontmatter source 字段中的跨项目路径和 temp 路径（通用版）。

使用正则模式匹配所有 .temp/ 和 d:/AI/ 路径，替换为描述性字符串。
同时处理 YAML 双引号转义形式（\\ → \\\\）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

TEMP_PATTERN = re.compile(r'source\s*[:=]\s*["\']?\S*\.temp/\S*?(?=["\'\s\n]|$)')
CROSS_PROJECT_PATTERNS = [
    re.compile(r'source\s*[:=]\s*["\']?d:\\\\?AI\\\\\S*?(?=["\'\s\n]|$)'),
    re.compile(r'source\s*[:=]\s*["\']?d:/AI/\S*?(?=["\'\s\n]|$)'),
]


def fix_content(content: str) -> str:
    def replace_temp(m):
        return 'source = "external: 临时分析文件（已清理）"'

    def replace_cross(m):
        return 'source = "external: 外部项目引用"'

    content = TEMP_PATTERN.sub(replace_temp, content)
    for pat in CROSS_PROJECT_PATTERNS:
        content = pat.sub(replace_cross, content)
    return content


def main():
    docs_dir = ROOT / "docs"
    toml_dir = ROOT / ".meta" / "toml"
    fixed = 0
    scanned = 0
    for d in [docs_dir, toml_dir]:
        for f in d.rglob("*"):
            if f.suffix not in (".md", ".toml"):
                continue
            scanned += 1
            try:
                content = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            new_content = fix_content(content)
            if new_content != content:
                f.write_text(new_content, encoding="utf-8", newline="")
                fixed += 1
                print(f"  修复: {f.relative_to(ROOT)}")
    print(f"\n扫描 {scanned} 个文件，修复 {fixed} 个文件")


if __name__ == "__main__":
    main()
