#!/usr/bin/env python3
"""验证文件名是否符合命名规范（禁止中英文混合、特殊字符等）。"""

import argparse
import re
import sys
from pathlib import Path


# Windows 保留名称
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

# 允许的扩展名
ALLOWED_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java",
    ".yaml", ".yml", ".json", ".toml", ".xml", ".html", ".css",
    ".sh", ".bat", ".ps1", ".gitignore", ".gitattributes",
    ".txt", ".csv", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".tag",  # pytest cache file
}

# 允许的字符（不包括空格）
ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9._\-/\\]+$')

# 非 ASCII 字符检测（包括中文）
NON_ASCII_PATTERN = re.compile(r'[^\x00-\x7F]')

# 连续连字符检测
CONSECUTIVE_HYPHENS_PATTERN = re.compile(r'--+')

# 数字开头检测
STARTS_WITH_NUMBER_PATTERN = re.compile(r'^[/\\]?\d')

# 目录路径（Vendor 目录等外部依赖，跳过检查）
EXCLUDED_DIRS = {"vendor", "node_modules", ".git", "__pycache__", ".venv", "venv"}


def is_valid_filename(filename: str, extension: str = None) -> tuple[bool, str]:
    """验证文件名是否符合规范。

    Returns:
        (is_valid, error_message)
    """
    # 检查是否包含非 ASCII 字符
    if NON_ASCII_PATTERN.search(filename):
        return False, f"包含非 ASCII 字符（中文或其他）: {filename}"

    # 检查是否包含空格
    if ' ' in filename:
        return False, f"包含空格字符: {filename}"

    # 检查是否以数字开头
    if STARTS_WITH_NUMBER_PATTERN.match(filename):
        return False, f"以数字开头: {filename}"

    # 检查是否包含连续连字符
    if CONSECUTIVE_HYPHENS_PATTERN.search(filename):
        return False, f"包含连续连字符: {filename}"

    # 检查是否是保留名称（Windows）
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    if name_without_ext.upper() in RESERVED_NAMES:
        return False, f"是 Windows 保留名称: {filename}"

    # 检查扩展名是否允许
    if extension and extension.lower() not in ALLOWED_EXTENSIONS:
        return False, f"扩展名不允许: {extension}"

    return True, ""


def scan_directory(directory: Path, fix: bool = False) -> list[tuple[Path, str]]:
    """扫描目录下的所有文件，检查文件名是否符合规范。

    Args:
        directory: 要扫描的目录
        fix: 是否自动修复（重命名文件）

    Returns:
        [(违规文件路径, 错误信息), ...]
    """
    violations = []

    for item in directory.rglob("*"):
        # 跳过排除的目录
        if any(excluded in item.parts for excluded in EXCLUDED_DIRS):
            continue

        if item.is_file():
            filename = item.name
            extension = item.suffix

            is_valid, error_msg = is_valid_filename(filename, extension)
            if not is_valid:
                violations.append((item, error_msg))

    return violations


def fix_filename(file_path: Path) -> Path | None:
    """尝试修复文件名。

    对于本规范，主要问题是中文名称，我们不能自动将其转换为英文。
    这里仅返回 None，表示无法自动修复。

    Returns:
        修复后的文件路径，如果无法自动修复则返回 None
    """
    # 由于中文名称无法自动转换为英文，我们只能报告问题
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="验证文件名是否符合命名规范"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="尝试自动修复违规文件名（仅对部分问题有效）"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=None,
        help="指定要扫描的目录（默认为项目根目录）"
    )
    args = parser.parse_args()

    # 确定项目根目录
    if args.directory:
        project_root = args.directory
    else:
        project_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("文件名命名规范验证")
    print("=" * 60)
    print(f"\n扫描目录: {project_root}")

    # 扫描文件
    violations = scan_directory(project_root, fix=args.fix)

    if not violations:
        print("\n通过: 所有文件名符合规范")
        print("=" * 60)
        return 0

    # 报告违规
    print(f"\n发现问题: {len(violations)} 个违规文件")
    print("-" * 60)

    for file_path, error_msg in violations:
        rel_path = file_path.relative_to(project_root)
        print(f"  {rel_path}")
        print(f"    问题: {error_msg}")

        if args.fix:
            new_path = fix_filename(file_path)
            if new_path:
                print(f"    已修复: -> {new_path.name}")
            else:
                print(f"    无法自动修复，需要手动处理")

    print("-" * 60)
    print("\n建议:")
    print("  1. 对于包含中文字符的文件，请手动重命名为英文")
    print("  2. 对于其他违规，请修正文件名")
    print("  3. 重新运行脚本验证")

    print("\n" + "=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
