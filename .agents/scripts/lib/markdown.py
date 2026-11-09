"""Markdown 文件处理共享模块。

整合 check-links、check-mermaid、generate-apps-index、generate-nav、
generate-dashboard 等脚本中重复的 Markdown 文件遍历、标题/描述提取、
内联链接解析、HTML 标记区替换等逻辑，提供统一引用入口。
"""


# 版本校验：相对导入共享库（depth=0）
from .python310_version_check import enforce_python310

enforce_python310()

import os
import re
import subprocess
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS
from lib.atomic_write import atomic_edit_text
from lib.link_fixer import INLINE_LINK_RE
from lib.project import is_non_worktree_path, resolve_project_root

# 标题提取：匹配第一个一级标题
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
# 描述提取：匹配标题后第一个非空段落（排除引用块和元数据行）
DESC_RE = re.compile(r"^#\s+.+\n\n(?:>.*\n)*\n?([^\n#>`\-\|].+)", re.MULTILINE)


def find_markdown_files(
    root: Path, exclude_dirs: list[str] | set[str] | None = None
) -> list[Path]:
    """递归查找 root 目录下所有 Markdown 文件。

    默认排除 constants.EXCLUDED_DIRS 中的系统目录（.git、vendor、.venv、
    __pycache__、node_modules、.temp），可通过 exclude_dirs 传入额外排除
    目录。排除项采用双路匹配：①按相对扫描根的路径前缀匹配（兼容裸
    目录名与扫描根相对路径）；②按工程根解析的绝对路径匹配（修复仓库
    根相对路径排除项在子目录扫描时失效的问题）。

    Args:
        root: 扫描根目录。
        exclude_dirs: 额外排除的目录（list 或 set）。

    Returns:
        匹配的 .md 文件 Path 列表。
    """
    extra = set(exclude_dirs) if exclude_dirs else set()
    resolved_root = Path(root).resolve()
    exclude_abs: list[Path] = []
    for excl in extra:
        excl_path = Path(excl)
        if excl_path.is_absolute():
            exclude_abs.append(excl_path.resolve())
        else:
            # 相对路径排除项以工程根为基准解析（如 ".agents/templates/..."）
            try:
                base = resolve_project_root(resolved_root)
            except FileNotFoundError:
                base = resolved_root
            exclude_abs.append((base / excl_path).resolve())
    md_files: list[Path] = []
    for md_path in root.rglob("*.md"):
        parts = set(md_path.parts)
        if EXCLUDED_DIRS & parts:
            continue
        if is_non_worktree_path(md_path, root):
            continue
        # 路径①：相对扫描根的前缀匹配（兼容裸目录名）
        try:
            rel_str = md_path.relative_to(root).as_posix()
        except ValueError:
            rel_str = None
        if rel_str and any(
            rel_str.startswith(excl.replace("\\", "/")) for excl in extra
        ):
            continue
        # 路径②：工程根解析的绝对路径匹配（子目录扫描时仍生效）
        resolved_md = md_path.resolve()
        if any(
            resolved_md == excl or resolved_md.is_relative_to(excl)
            for excl in exclude_abs
        ):
            continue
        md_files.append(md_path)
    return md_files


# ============================================================================
# 未跟踪目录跳过（check-links 专用）
# ============================================================================
# 背景：本地语料库（.corpus/）、AI 工具目录（.workbuddy/）、本地缓存（.cache/）
# 不被 git 跟踪，其内部 Markdown 的链接无法按本仓相对路径解析，曾贡献 1.4 万条
# 假断链淹没真实问题。本机制只跳过「未被 git 跟踪」的内容：这些目录中一旦出现
# 受版本控制的文件，会被照常扫描，不会被前缀硬挡。
#
# 硬约束：被跳过的路径必须满足「未被 git 跟踪」或「是指向已跟踪目录的联接别名」。
# audit_skipped_paths() 在每个扫描批次结束后强制校验，违规立即抛错；索引不可用
# 时同样拒绝跳过（宁可不跳过，也不能误挡真断链）。

UNTRACKED_REASON = "untracked"
JUNCTION_ALIAS_REASON = "junction-alias"

_TRACKED_INDEX_CACHE: dict[str, set[str] | None] = {}


def _git_tracked_index(repo_root: Path) -> set[str] | None:
    """返回仓库 git 索引中全部文件的 posix 相对路径集合。

    Args:
        repo_root: 仓库根目录。

    Returns:
        相对仓库根的 posix 路径集合；非 git 仓库或 git 调用失败时返回 None。
    """
    key = str(repo_root)
    if key in _TRACKED_INDEX_CACHE:
        return _TRACKED_INDEX_CACHE[key]
    index: set[str] | None
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        )
        index = {
            rel.decode("utf-8", "surrogateescape").replace("\\", "/")
            for rel in proc.stdout.split(b"\0")
            if rel
        }
    except (OSError, subprocess.CalledProcessError):
        index = None
    _TRACKED_INDEX_CACHE[key] = index
    return index


def _literal_relative(path: Path, base: Path) -> str | None:
    """按字面路径求相对 base 的 posix 路径，不解析联接/符号链接。"""
    try:
        literal = Path(os.path.abspath(path))
        return literal.relative_to(Path(os.path.abspath(base))).as_posix()
    except ValueError:
        return None


def is_literal_path(path: Path) -> bool:
    """判断路径是否为字面路径（不穿透目录联接/符号链接）。

    同一文件可能既能按真实路径、又能按目录联接别名访问。字面路径才是它在
    仓库中的权威位置，别名视图只配当去重候选——否则「保留先到者」的去重
    会让别名视图挤掉真实路径，跳过集一开就把真实内容的断链一起吞掉。
    """
    try:
        literal = Path(os.path.abspath(path))
        resolved = Path(path).resolve()
    except OSError:
        return True
    return os.path.normcase(str(literal)) == os.path.normcase(str(resolved))


def audit_skipped_paths(
    skipped: dict[Path, str], tracked: set[str] | None, repo_root: Path
) -> None:
    """强制校验被跳过路径是否具备免除资格。

    硬约束（不可放宽）：每个被跳过的路径必须满足下列之一——
    ① 未被 git 跟踪；② 未被跟踪、且解析联接后的目标是被跟踪文件（别名重扫）。

    Args:
        skipped: 被跳过的文件 → 跳过原因（UNTRACKED_REASON / JUNCTION_ALIAS_REASON）。
        tracked: git 索引路径集合；None 表示索引不可用。
        repo_root: 仓库根目录。

    Raises:
        RuntimeError: 存在不具备免除资格的路径，或索引不可用却仍有跳过。
    """
    if not skipped:
        return
    if tracked is None:
        raise RuntimeError(
            f"跳过集缺少 git 索引，拒绝以未验证状态跳过 {len(skipped)} 个文件"
        )
    violations: list[str] = []
    for path, reason in skipped.items():
        literal = _literal_relative(path, repo_root)
        if literal is None:
            violations.append(f"{path}: 不在仓库范围内，无法验证跟踪状态")
            continue
        if literal in tracked:
            violations.append(
                f"{literal}: 已被 git 跟踪，不能跳过（它本身就是应该检查的内容）"
            )
            continue
        if reason == JUNCTION_ALIAS_REASON:
            real = _literal_relative(path.resolve(), repo_root)
            if real is None or real == literal or real not in tracked:
                violations.append(
                    f"{literal}: 声明为联接别名，但目标不是被跟踪文件"
                )
    if violations:
        raise RuntimeError(
            "跳过集违反硬约束（被跳过的路径必须未被 git 跟踪，"
            "或是指向已跟踪目录的联接别名）：\n  " + "\n  ".join(violations)
        )


def filter_untracked_paths(
    md_files: list[Path],
    repo_root: Path,
    skip_dirs: set[str] | frozenset[str] | None,
) -> tuple[list[Path], dict[str, int]]:
    """剔除位于未跟踪目录中的 Markdown 文件，并返回按原因计的跳过统计。

    Args:
        md_files: 待过滤的 Markdown 文件列表。
        repo_root: 仓库根目录（用于对齐 git 索引的相对路径）。
        skip_dirs: 候选跳过目录名集合（按目录段匹配，如 {".corpus", ".workbuddy"}）。

    Returns:
        (保留的文件列表, 统计字典)。统计含 total 与各原因计数；索引不可用时
        返回原列表与空统计。
    """
    if not skip_dirs:
        return list(md_files), {}
    tracked = _git_tracked_index(repo_root)
    if tracked is None:
        print(
            "警告: 无法读取 git 跟踪清单，跳过集未生效"
            "（避免把受版本控制的内容误挡在检查之外）",
            file=sys.stderr,
        )
        return list(md_files), {}
    kept: list[Path] = []
    skipped: dict[Path, str] = {}
    for md_path in md_files:
        if not (set(md_path.parts[:-1]) & set(skip_dirs)):
            kept.append(md_path)
            continue
        literal = _literal_relative(md_path, repo_root)
        if literal is None or literal in tracked:
            kept.append(md_path)
            continue
        real = _literal_relative(md_path.resolve(), repo_root)
        skipped[md_path] = (
            JUNCTION_ALIAS_REASON if real and real != literal else UNTRACKED_REASON
        )
    audit_skipped_paths(skipped, tracked, repo_root)
    if not skipped:
        return kept, {}
    stats = {"total": len(skipped)}
    for reason in skipped.values():
        stats[reason] = stats.get(reason, 0) + 1
    return kept, stats


def extract_title(path: Path | str) -> str:
    """从 Markdown 文件提取首个一级标题文本。

    Args:
        path: Markdown 文件路径（Path 对象或字符串）。

    Returns:
        标题文本字符串，无标题时返回空字符串。
    """
    content = Path(path).read_text(encoding="utf-8")
    m = TITLE_RE.search(content)
    if m:
        return m.group(1).strip()
    return ""


def extract_description(path: Path | str) -> str:
    """从 Markdown 文件提取标题下的首行描述文本。

    匹配首个一级标题后第一个非空段落（排除引用块和元数据行），
    取第一句作为描述。

    Args:
        path: Markdown 文件路径（Path 对象或字符串）。

    Returns:
        描述文本字符串，无描述时返回空字符串。
    """
    content = Path(path).read_text(encoding="utf-8")
    m = DESC_RE.search(content)
    if m:
        desc = m.group(1).strip()
        desc = re.split(r"[。\.]\s", desc)[0]
        return desc
    return ""


def parse_inline_links(content: str) -> list[tuple[str, str]]:
    """从 Markdown 内容提取所有内联链接。

    复用 lib.link_fixer.INLINE_LINK_RE 正则匹配 [text](url) 形式的链接。

    Args:
        content: Markdown 文本内容。

    Returns:
        (link_text, url) 元组列表。
    """
    return [
        (m.group(1), m.group(2).strip())
        for m in INLINE_LINK_RE.finditer(content)
    ]


def update_marker_region(
    file_path: Path | str,
    marker_start: str,
    marker_end: str,
    new_content: str,
) -> None:
    """替换 Markdown 文件中 marker_start 与 marker_end 标记之间的内容。

    保留标记本身和文件其他内容不变，仅在两个标记之间插入 new_content
    （前后各空一行）。使用原子写入保证读者不会看到部分更新状态。

    Args:
        file_path: 目标文件路径（Path 对象或字符串）。
        marker_start: 起始标记字符串（如 HTML 注释）。
        marker_end: 结束标记字符串（如 HTML 注释）。
        new_content: 替换标记区域的新内容。

    Raises:
        ValueError: 文件中未找到 marker_start 或 marker_end 标记。
    """
    p = Path(file_path)

    def _editor(content: str) -> str:
        start_idx = content.find(marker_start)
        end_idx = content.find(marker_end)
        if start_idx == -1 or end_idx == -1:
            raise ValueError(
                f"{p} 中未找到标记 {marker_start!r} / {marker_end!r}，无法更新标记区域"
            )
        return (
            content[: start_idx + len(marker_start)]
            + "\n\n"
            + new_content
            + "\n\n"
            + content[end_idx:]
        )

    atomic_edit_text(p, _editor, encoding="utf-8")


def apply_fix_to_markdown_files(
    root: Path,
    fix_func,
    *,
    label: str = "Fixed",
    target_dir: Path | None = None,
) -> int:
    """对项目 docs/ 目录下的所有 Markdown 文件应用修复函数。

    Args:
        root: 项目根目录。
        fix_func: 修复函数，签名为 (content: str, path: Path) -> str。
        label: 打印时的标签（默认 "Fixed"）。
        target_dir: 目标目录（默认为 root / "docs"）。

    Returns:
        修复的文件数量。
    """
    if target_dir is None:
        target_dir = root / "docs"

    md_files = find_markdown_files(target_dir)
    fixed_count = 0

    for md_path in md_files:
        content = md_path.read_text(encoding="utf-8")
        original = content

        content = fix_func(content, md_path)

        if content != original:
            md_path.write_text(content, encoding="utf-8", newline="")
            fixed_count += 1
            print(f"  {label}: {md_path.relative_to(root)}")

    print(f"\nTotal {label.lower()}: {fixed_count} files")
    return fixed_count

