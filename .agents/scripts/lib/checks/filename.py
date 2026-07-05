"""文件名命名规范检查（来自 check-filename-convention.py）。"""

import re
import subprocess
from pathlib import Path

from constants import EXCLUDED_DIRS as BASE_EXCLUDED

RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}
ALLOWED_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java",
    ".yaml", ".yml", ".json", ".toml", ".xml", ".html", ".css",
    ".sh", ".bat", ".ps1", ".gitignore", ".gitattributes",
    ".txt", ".csv", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".tag", ".example", ".template",
    ".ini", ".log", ".lock", ".env.example",
}
ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9._\-/\\]+$')
NON_ASCII = re.compile(r'[^\x00-\x7F]')
CONSECUTIVE_HYPHENS = re.compile(r'--+')
STARTS_WITH_NUMBER = re.compile(r'^[/\\]?(?!(\d{4}-\d{2}-\d{2}-|\d{2}-))\d')
EXCLUDED_DIRS = BASE_EXCLUDED | {"venv", ".chaos", "logs"}
EXCLUDED_FILES = {"报名帖_竹简悟道.md", "竹简悟道_完整版.html"}


def _is_valid(filename: str, extension: str | None) -> tuple[bool, str]:
    if NON_ASCII.search(filename):
        return False, f"包含非 ASCII 字符（中文或其他）: {filename}"
    if ' ' in filename:
        return False, f"包含空格字符: {filename}"
    if STARTS_WITH_NUMBER.match(filename):
        return False, f"以数字开头: {filename}"
    if CONSECUTIVE_HYPHENS.search(filename):
        return False, f"包含连续连字符: {filename}"
    name_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    if name_no_ext.upper() in RESERVED_NAMES:
        return False, f"是 Windows 保留名称: {filename}"
    if extension and extension.lower() not in ALLOWED_EXTENSIONS:
        return False, f"扩展名不允许: {extension}"
    return True, ""


def _get_staged(directory: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, cwd=str(directory),
    )
    return [directory / line for line in result.stdout.strip().split('\n') if line]


def _scan(directory: Path, staged_only: bool) -> list[tuple[Path, str]]:
    violations = []
    if staged_only:
        files = _get_staged(directory)
    else:
        files = [p for p in directory.rglob("*") if p.is_file() and not any(ex in p.parts for ex in EXCLUDED_DIRS)]
    for item in files:
        try:
            if item.name in EXCLUDED_FILES:
                continue
            ok, msg = _is_valid(item.name, item.suffix)
            if not ok:
                violations.append((item, msg))
        except OSError:
            continue
    return violations


def run(project_root: Path, args) -> int:
    directory = Path(args.directory).resolve() if getattr(args, "directory", None) else project_root
    staged = getattr(args, "staged", False)
    fix = getattr(args, "fix", False)

    print("=" * 60)
    print("文件名命名规范验证")
    print("=" * 60)
    print(f"\n扫描目录: {directory}")
    if staged:
        print("模式: 仅检查暂存区文件")

    violations = _scan(directory, staged_only=staged)
    if not violations:
        print("\n通过: 所有文件名符合规范")
        print("=" * 60)
        return 0

    print(f"\n发现问题: {len(violations)} 个违规文件")
    print("-" * 60)
    for fp, msg in violations:
        try:
            rel = fp.relative_to(project_root)
        except ValueError:
            rel = fp
        print(f"  {rel}")
        print(f"    问题: {msg}")
        if fix:
            print(f"    无法自动修复（中文名称需手动重命名为英文）")
    print("-" * 60)
    print("\n建议:")
    print("  1. 对于包含中文字符的文件，请手动重命名为英文")
    print("  2. 对于其他违规，请修正文件名")
    print("  3. 重新运行脚本验证")
    print("\n" + "=" * 60)
    return 1
