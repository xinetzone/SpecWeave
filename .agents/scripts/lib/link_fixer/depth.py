"""link_fixer 相对路径深度校正模块。

处理目录迁移/重构后，相对路径中 ../ 层级数不正确导致的断链。
"""

from __future__ import annotations

from pathlib import Path


def try_adjust_relative_depth(
    url_without_anchor: str,
    source_file: Path,
    max_adjust: int = 3,
) -> Path | None:
    """通过增减 ../ 层级数来校正断链的相对路径。

    这是目录迁移/重构后最常见的断链类型：文件移动到更深（或更浅）的目录后，
    相对路径中 ../ 的数量需要相应增减，但路径的后半段（目标文件名和中间目录）是正确的。

    策略：
    1. 统计现有 ../ 的数量 N
    2. 尝试 N+1, N+2, ..., N+max_adjust（增加层级，文件被移到更深位置）
    3. 尝试 N-1, N-2, ..., max(0, N-max_adjust)（减少层级，文件被移到更浅位置）
    4. 优先尝试增加层级（这是更常见的场景：目录原子化拆分导致深度增加）
    5. 对每个候选路径检查目标是否存在，返回第一个有效的目标

    Args:
        url_without_anchor: 不含锚点的相对 URL 路径。
        source_file: 包含该链接的源文件绝对路径。
        max_adjust: 最大调整层数（默认 3）。

    Returns:
        找到的目标文件绝对路径，或 None。
    """
    if not url_without_anchor or url_without_anchor.startswith("/"):
        return None

    cleaned = url_without_anchor.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]

    parts = cleaned.split("/")
    dotdot_count = 0
    for p in parts:
        if p == "..":
            dotdot_count += 1
        else:
            break

    if dotdot_count == 0 and not any(p == ".." for p in parts):
        return None

    remaining_parts = parts[dotdot_count:]
    if not remaining_parts:
        return None

    base_dir = source_file.parent.resolve()

    candidates: list[tuple[int, Path]] = []

    for delta in range(1, max_adjust + 1):
        new_dotdot = dotdot_count + delta
        candidate_parts = [".."] * new_dotdot + remaining_parts
        candidate_url = "/".join(candidate_parts)
        target = (base_dir / candidate_url).resolve()
        if target.exists():
            candidates.append((delta, target))

    for delta in range(1, min(dotdot_count, max_adjust) + 1):
        new_dotdot = dotdot_count - delta
        if new_dotdot < 0:
            break
        candidate_parts = [".."] * new_dotdot + remaining_parts if new_dotdot > 0 else remaining_parts
        candidate_url = "/".join(candidate_parts)
        target = (base_dir / candidate_url).resolve()
        if target.exists():
            candidates.append((delta + max_adjust, target))

    for depth_delta in [0, 1, 2]:
        target = (base_dir / cleaned).resolve()
        if target.exists() and target.is_dir():
            for suffix in ["README.md", "index.md"]:
                readme = target / suffix
                if readme.exists():
                    candidates.append((100 + depth_delta, readme))
                    break
            break

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    best = candidates[0][1]

    if best.is_dir():
        readme = best / "README.md"
        if readme.exists():
            return readme
        return best

    return best
