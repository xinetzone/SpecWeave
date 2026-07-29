"""Markdown 文件检查共享工具。

提供 check-frontmatter 和 check-metadata-layering 等脚本中重复的
文件读取、路径解析、参数解析、结果输出等通用逻辑。
"""

import sys
from pathlib import Path


def read_file_basic(
    md_path: Path,
    project_root: Path,
    *,
    skip_dirs: tuple[str, ...] = (".trae/specs/", "vendor/"),
) -> tuple[str, str] | None:
    """读取 Markdown 文件并计算相对路径，跳过排除目录。

    Args:
        md_path: Markdown 文件路径。
        project_root: 项目根目录。
        skip_dirs: 要跳过的路径前缀。

    Returns:
        (content, rel_path) 元组，文件应被跳过时返回 None。
    """
    try:
        content = md_path.read_text(encoding="utf-8")
    except Exception as e:
        return None

    try:
        rel_path = md_path.relative_to(project_root).as_posix()
    except ValueError:
        rel_path = str(md_path)

    if any(rel_path.startswith(prefix) for prefix in skip_dirs):
        return None

    return content, rel_path


def resolve_target_files(
    args,
    project_root: Path,
) -> list[Path]:
    """根据 CLI 参数解析目标 Markdown 文件列表。

    Args:
        args: argparse Namespace，需含 dir、file、exclude 属性。
        project_root: 项目根目录。

    Returns:
        Path 对象列表。
    """
    if not args.dir and not args.file:
        print("⚠️  请指定 --dir 或 --file")
        sys.exit(1)

    if args.file:
        return [Path(args.file).resolve()]

    target_dir = Path(args.dir).resolve()
    if not target_dir.is_dir():
        print(f"❌ 目录不存在: {target_dir}")
        sys.exit(1)

    md_files = sorted(target_dir.rglob("*.md"))
    if getattr(args, "exclude", None):
        md_files = [
            f for f in md_files
            if not any(
                ex in f.relative_to(project_root).as_posix().split("/")
                for ex in args.exclude
            )
        ]
    return md_files


def print_file_issues(
    rel_path: str,
    errors: list[str],
    warnings: list[str],
    *,
    strict: bool = False,
    verbose: bool = False,
    extra_items: list[tuple[str, list[str]]] | None = None,
) -> bool:
    """打印单个文件的检查问题，返回是否有输出。

    Args:
        rel_path: 文件相对路径。
        errors: 错误列表。
        warnings: 警告列表。
        strict: 严格模式（警告视为错误）。
        verbose: 显示所有文件（包括通过的）。
        extra_items: 额外条目列表，每项为 (标签, 内容列表)。

    Returns:
        True 如果有输出。
    """
    has_display = bool(errors) or (strict and bool(warnings))
    has_warn_only = bool(warnings) and not errors and not strict

    if has_display:
        print(f"❌ {rel_path}")
        for e in errors:
            print(f"   [错误] {e}")
        for w in warnings:
            print(f"   [{'错误' if strict else '警告'}] {w}")
        if extra_items:
            for label, items in extra_items:
                for item in items:
                    print(f"   [{label}] {item}")
        return True
    elif has_warn_only and verbose:
        print(f"⚠️  {rel_path}")
        for w in warnings:
            print(f"   [警告] {w}")
        return True

    return False


def unwrap_md_file_safe(
    safe_result: tuple[str, str] | tuple[None, str],
    result_dict: dict,
    error_key: str = "errors",
) -> tuple[str, str] | None:
    """解包 read_md_file_safe 的返回值，处理错误情况。

    将 check-frontmatter.py 和 check-metadata-layering.py 中重复的
    safe 结果解包 + 错误记录模式提取为共享函数。

    Args:
        safe_result: read_md_file_safe 的返回值。
        result_dict: 结果字典，错误信息会追加到 result_dict[error_key]。
        error_key: 错误信息在 result_dict 中的键名。

    Returns:
        (content, rel_path) 成功时，None 失败时（已记录错误到 result_dict）。
    """
    if safe_result[0] is None:
        if safe_result[1]:
            result_dict.setdefault(error_key, []).append(safe_result[1])
        return None
    return safe_result


def read_md_file_safe(
    md_path: Path,
    project_root: Path,
) -> tuple[str, str] | tuple[None, str]:
    """安全读取 Markdown 文件，返回 (content, rel_path) 或 (None, error_msg)。

    整合了 check-frontmatter.py 和 check-metadata-layering.py 中重复的
    文件读取+错误处理+read_file_basic 调用模式。

    Args:
        md_path: Markdown 文件路径。
        project_root: 项目根目录。

    Returns:
        (content, rel_path) 成功时返回内容与相对路径；
        (None, error_msg) 失败或应跳过时返回 None 与错误信息。
    """
    try:
        content = md_path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"读取失败: {e}"

    basic = read_file_basic(md_path, project_root)
    if basic is None:
        return None, "跳过（排除目录）"

    return basic