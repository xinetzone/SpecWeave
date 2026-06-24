"""项目路径解析工具。

提供基于脚本位置的工程根目录解析，解决各验证脚本中
`Path(__file__).parent.parent.parent` 的重复硬编码问题。
"""

from pathlib import Path


def resolve_project_root(anchor: str | Path | None = None) -> Path:
    """从 anchor 位置向上查找工程根目录。

    工程根目录定义为包含 AGENTS.md 的最近祖先目录。
    若不存在 AGENTS.md，则以包含 README.md 的最近祖先目录作为回退。

    Args:
        anchor: 起始查找路径。为 None 时须显式传入，不接受隐式推断。

    Returns:
        工程根目录的绝对路径。

    Raises:
        FileNotFoundError: 向上遍历到文件系统根目录仍未找到时抛出。
    """
    if anchor is None:
        raise ValueError("必须显式传入 __file__ 以确定锚点位置")

    current = Path(anchor).resolve()
    if current.is_file():
        current = current.parent

    readme_candidate: Path | None = None

    for ancestor in [current] + list(current.parents):
        if (ancestor / "AGENTS.md").exists():
            return ancestor
        if readme_candidate is None and (ancestor / "README.md").exists():
            readme_candidate = ancestor

    if readme_candidate is not None:
        return readme_candidate

    raise FileNotFoundError(
        f"从 '{anchor}' 向上遍历未找到工程根目录（含 AGENTS.md 或 README.md）"
    )


def resolve_agents_dir(anchor: str | Path) -> Path:
    """从锚点位置解析 .agents/ 目录路径。

    Args:
        anchor: 起始文件路径（通常为 __file__）。

    Returns:
        .agents/ 目录的绝对路径。
    """
    root = resolve_project_root(anchor)
    return root / ".agents"


def resolve_scripts_dir(anchor: str | Path) -> Path:
    """从锚点位置解析 .agents/scripts/ 目录路径。"""
    return resolve_agents_dir(anchor) / "scripts"
