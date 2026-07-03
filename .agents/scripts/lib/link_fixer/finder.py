"""link_fixer 文件查找模块。

在项目中查找文件/目录、路径解析、近源匹配等逻辑。
"""

from __future__ import annotations

from pathlib import Path

from .constants import _DIR_FILENAMES, _GENERIC_FILENAMES


def _is_excluded_path(path: Path, project_root: Path) -> bool:
    """判断路径是否应排除（不搜索）。"""
    excluded_names = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp"}
    try:
        rel = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return True
    return any(part in excluded_names for part in rel.parts)


def _find_all_matches(
    filename: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    find_dir: bool = False,
) -> list[Path]:
    """查找所有匹配的文件/目录，返回排序后的列表（近源优先）。"""
    project_root = project_root.resolve()
    matches: list[Path] = []

    search_dirs = []
    if search_subdir is not None:
        first_try = (project_root / search_subdir).resolve()
        if first_try.exists():
            search_dirs.append(first_try)
    search_dirs.append(project_root)

    for search_dir in search_dirs:
        for candidate in search_dir.rglob(filename):
            if _is_excluded_path(candidate, project_root):
                continue
            if find_dir and candidate.is_dir():
                readme = candidate / "README.md"
                if readme.exists():
                    matches.append(candidate.resolve())
            elif not find_dir and candidate.is_file():
                matches.append(candidate.resolve())

    return matches


def find_file_in_project(
    filename: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    find_dir: bool = False,
    near: Path | None = None,
) -> Path | None:
    """在项目中查找指定文件名的文件或目录。

    Args:
        filename: 要查找的文件名（含扩展名）或目录名。
        project_root: 项目根目录。
        search_subdir: 优先搜索的子目录（相对于 project_root）。
        find_dir: True=查找目录，False=查找文件。
        near: 优先返回距离此路径最近的匹配。

    Returns:
        匹配路径的绝对路径，或 None。
    """
    matches = _find_all_matches(filename, project_root, search_subdir, find_dir=find_dir)
    if not matches:
        return None

    if near is not None:
        near = near.resolve()
        def _shared_depth(p: Path) -> int:
            try:
                rel_p = p.relative_to(project_root)
                rel_near = near.relative_to(project_root)
            except ValueError:
                return -1
            shared = 0
            for a, b in zip(rel_p.parts, rel_near.parts):
                if a == b:
                    shared += 1
                else:
                    break
            return shared

        matches.sort(key=lambda p: -_shared_depth(p))

    return matches[0]


def _extract_search_terms(url_path: str) -> list[str]:
    """从 URL 路径中提取有意义的搜索关键词（过滤掉 . 和 ..）。"""
    parts = Path(url_path).parts
    terms = []
    for part in parts:
        if part in (".", "..", ""):
            continue
        name = part
        if name.endswith(".md"):
            name = name[:-3]
        if name and name not in {"docs", "retrospective", "reports", "patterns", "assets"}:
            terms.append(name)
    return terms


def _try_root_based_path(url_path: str, project_root: Path) -> Path | None:
    """当 URL 以项目顶级目录开头时，尝试作为项目根相对路径解析。

    动态检测 project_root 下的实际顶级目录（含子项目自己的目录结构），
    而非依赖硬编码列表，确保主项目和子项目（如 apps/xxx/）都能正确识别。
    """
    pr = project_root.resolve()
    cleaned = url_path.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    parts = [p for p in cleaned.split("/") if p and p != ".."]
    if not parts:
        return None

    first_part = parts[0]
    top_dirs = {
        p.name for p in pr.iterdir() if p.is_dir()
    } if pr.exists() else set()
    top_files = {
        p.name for p in pr.iterdir() if p.is_file() and p.suffix in {".md", ".html"}
    } if pr.exists() else set()

    if first_part in top_dirs:
        candidate = pr.joinpath(*parts)
        if candidate.is_dir():
            readme = candidate / "README.md"
            if readme.exists():
                return readme
            return candidate
        if candidate.exists():
            return candidate
        if not candidate.suffix:
            readme = candidate / "README.md"
            if readme.exists():
                return readme
    elif first_part in top_files and len(parts) == 1:
        candidate = pr / first_part
        if candidate.exists():
            return candidate
    return None


def find_target_by_stem(
    url_path: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    near: Path | None = None,
) -> Path | None:
    """通过 URL 路径的关键段在项目中查找目标。

    策略：
    1. 如果最后段是通用文件名（README.md 等），用其父目录名搜索
    2. 否则用文件名搜索 .md 文件和同名目录
    3. 对候选结果评分：共享路径深度 + URL关键词匹配数
    4. 排除与源文件自身相同的候选

    Args:
        url_path: 不含锚点的 URL 路径部分。
        project_root: 项目根目录。
        search_subdir: 优先搜索的子目录。
        near: 源文件位置，用于选择最近的匹配。

    Returns:
        找到的目标文件（.md 或目录下的 README.md），或 None。
    """
    p = Path(url_path)
    last_part = p.name

    if not last_part:
        return None

    search_terms = _extract_search_terms(url_path)
    near_resolved = near.resolve() if near else None
    pr = project_root.resolve()
    root_based_resolved = None

    use_dir_search = last_part.endswith(".md") or ("." not in last_part)

    if last_part in _DIR_FILENAMES and last_part.endswith(".md"):
        parent_name = p.parent.name
        if parent_name and parent_name not in (".", "..", ""):
            dir_matches = _find_all_matches(parent_name, project_root, search_subdir, find_dir=True)
            candidates = [d / "README.md" for d in dir_matches]
        else:
            candidates = []
    else:
        if last_part.endswith(".md"):
            md_name = last_part
            dir_name = last_part[:-3]
        elif "." not in last_part:
            md_name = last_part + ".md"
            dir_name = last_part
        else:
            md_name = last_part
            dir_name = None

        root_based = _try_root_based_path(url_path, project_root)
        candidates = []
        if root_based is not None:
            root_based_resolved = root_based.resolve()
            candidates.append(root_based)

        file_matches = _find_all_matches(md_name, project_root, search_subdir, find_dir=False)
        candidates.extend(file_matches)

        if dir_name:
            dir_matches = _find_all_matches(dir_name, project_root, search_subdir, find_dir=True)
            candidates.extend(d / "README.md" for d in dir_matches)

        if not candidates and last_part.endswith(".md"):
            stem = last_part[:-3]
            dir_matches2 = _find_all_matches(stem, project_root, search_subdir, find_dir=True)
            candidates.extend(d / "README.md" for d in dir_matches2)

    if not candidates:
        return None

    if near_resolved is not None:
        try:
            near_rel = near_resolved.relative_to(pr)
        except ValueError:
            near_rel = None

        def _score(candidate: Path) -> tuple[int, int, int]:
            try:
                cand_rel = candidate.relative_to(pr)
            except ValueError:
                return (-1, -1, len(candidate.parts))

            shared = 0
            if near_rel is not None:
                for a, b in zip(cand_rel.parts, near_rel.parts):
                    if a == b:
                        shared += 1
                    else:
                        break

            keyword_hits = 0
            cand_str = str(cand_rel).lower()
            for term in search_terms:
                if term.lower() in cand_str:
                    keyword_hits += 1

            is_self = 0
            if candidate.resolve() == near_resolved:
                is_self = -100

            root_bonus = 50 if root_based_resolved and candidate.resolve() == root_based_resolved else 0

            return (shared + keyword_hits + is_self + root_bonus, shared, -len(cand_rel.parts))

        candidates.sort(key=_score, reverse=True)

    if near_resolved is not None and candidates[0].resolve() == near_resolved:
        return candidates[0] if len(candidates) == 1 else None

    return candidates[0]
