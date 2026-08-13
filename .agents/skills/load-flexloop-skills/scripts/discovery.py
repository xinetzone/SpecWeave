"""技能发现模块。

扫描指定目录下的 SKILL.md 文件，支持默认目录和用户额外指定目录，
处理 .validate-skip 跳过列表，返回排序后的技能文件路径列表。
"""

from __future__ import annotations

from pathlib import Path


DEFAULT_SCAN_DIRS: list[tuple[str, str]] = [
    ("vendor/flexloop/apps/chaos/.agents/skills/", "vendor"),
    (".agents/skills/", "local"),
]


def _load_skip_list(skills_dir: Path) -> set[str]:
    """加载 .validate-skip 文件中的跳过目录列表。

    Args:
        skills_dir: 技能根目录路径。

    Returns:
        需要跳过的技能目录名集合。
    """
    skip_file = skills_dir / ".validate-skip"
    if not skip_file.exists():
        return set()

    skip_dirs: set[str] = set()
    try:
        content = skip_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                skip_dirs.add(line)
    except OSError:
        pass

    return skip_dirs


def _scan_skills_dir(skills_dir: Path, source: str) -> list[tuple[Path, str]]:
    """扫描单个技能目录下的所有 SKILL.md 文件。

    Args:
        skills_dir: 技能根目录绝对路径。
        source: 来源标记（"vendor" 或 "local"）。

    Returns:
        (SKILL.md 绝对路径, source) 元组列表。
    """
    if not skills_dir.exists() or not skills_dir.is_dir():
        return []

    skip_dirs = _load_skip_list(skills_dir)
    results: list[tuple[Path, str]] = []

    for skill_md in skills_dir.rglob("SKILL.md"):
        if "SKILL-TEMPLATE" in skill_md.name:
            continue

        try:
            rel_path = skill_md.parent.relative_to(skills_dir)
            rel_parts = rel_path.parts
            if rel_parts and rel_parts[0] in skip_dirs:
                continue
        except ValueError:
            pass

        results.append((skill_md.resolve(), source))

    return results


def discover_skill_files(
    project_root: Path,
    extra_dirs: list[str] | None = None,
) -> list[tuple[Path, str]]:
    """发现项目中的所有技能 SKILL.md 文件。

    Args:
        project_root: 项目根目录路径（Path 对象）。
        extra_dirs: 用户额外指定的扫描目录列表（相对于 project_root），
            source 标记为 "local"。

    Returns:
        发现的 (SKILL.md 绝对路径, source) 元组列表，按路径排序。
    """
    project_root = project_root.resolve()
    all_results: list[tuple[Path, str]] = []

    scan_dirs: list[tuple[str, str]] = list(DEFAULT_SCAN_DIRS)
    if extra_dirs:
        for d in extra_dirs:
            scan_dirs.append((d, "local"))

    for rel_dir, source in scan_dirs:
        skills_dir = (project_root / rel_dir).resolve()
        all_results.extend(_scan_skills_dir(skills_dir, source))

    all_results.sort(key=lambda x: str(x[0]).replace("\\", "/"))

    return all_results
