"""SpecWeave 工作区检测模块。

识别逻辑对齐 SpecWeave 五步发现流程
（.agents/protocols/workspace-discovery.md）中的步骤 1 / 3 / 4：

- **主信号**（Root Workspace，步骤 1）：存在 ``AGENTS.md`` 且包含「启动协议」关键词；
- **兼容信号**（兼容模式，步骤 3）：存在 ``.agents/`` 目录且 ``roles/`` 与
  ``skills/`` 特征子目录同时存在——旧版 SpecWeave 项目即使没有标准
  ``AGENTS.md`` 也能被识别（较协议文字描述更严格，见
  ``_has_agents_dir_signature``，避免通用技能目录误判）；
- **向上递归**（步骤 4）：从起始路径逐级向上查找，**就近命中即返回**，
  不再继续向上（嵌套子工作区按其自身上下文治理）。

同一目录内主信号优先于兼容信号。
"""

import logging
from pathlib import Path
from typing import Optional

from ._constants import (
    AGENTS_DIR_NAME,
    AGENTS_DIR_REQUIRED_SUBDIRS,
    AGENTS_MD_FILENAME,
    SIGNAL_AGENTS_DIR,
    SIGNAL_AGENTS_MD,
    SPECWEAVE_SIGNATURE_KEYWORD,
    SUBREGIONS,
)

logger = logging.getLogger(__name__)


def _has_agents_md_signature(path_obj: Path) -> bool:
    """主信号：``AGENTS.md`` 存在且包含「启动协议」关键词。"""
    agents_md = path_obj / AGENTS_MD_FILENAME
    if not agents_md.is_file():
        return False
    try:
        content = agents_md.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        logger.debug(f"读取 AGENTS.md 失败: {e}")
        return False
    return SPECWEAVE_SIGNATURE_KEYWORD in content


def _has_agents_dir_signature(path_obj: Path) -> bool:
    """兼容信号：``.agents/`` 存在且 ``roles/`` 与 ``skills/`` 同时存在。

    较五步发现流程步骤 3 的文字描述更严格：仅含单一 ``skills/``（通用技能
    管理器目录，如 ``~/.agents/skills``）不判定，避免用户主目录被误判为
    兼容工作区。
    """
    agents_dir = path_obj / AGENTS_DIR_NAME
    if not agents_dir.is_dir():
        return False
    return all(
        (agents_dir / sub).is_dir() for sub in AGENTS_DIR_REQUIRED_SUBDIRS
    )


def detect_workspace_signal(path: str) -> Optional[str]:
    """
    返回指定目录命中的 SpecWeave 识别信号（主信号优先）。

    Args:
        path: 要检查的目录路径

    Returns:
        Optional[str]: 命中的信号名——``"agents_md"``（Root Workspace 主信号）
        或 ``"agents_dir"``（兼容模式信号）；未命中返回 ``None``
    """
    try:
        path_obj = Path(path).resolve()
    except PermissionError:
        logger.debug(f"权限不足，无法访问路径: {path}")
        return None
    except Exception as e:
        logger.debug(f"检查工作区时发生错误: {e}")
        return None

    if _has_agents_md_signature(path_obj):
        return SIGNAL_AGENTS_MD
    if _has_agents_dir_signature(path_obj):
        return SIGNAL_AGENTS_DIR
    return None


def is_specweave_workspace(path: str) -> bool:
    """
    检查指定路径是否为 SpecWeave 工作区（``.agents`` + ``AGENTS.md`` 双信号识别）。

    命中任一信号即返回 True：

    1. 主信号：``AGENTS.md`` 存在且包含「启动协议」关键词；
    2. 兼容信号：``.agents/`` 目录存在且 ``roles/`` 与 ``skills/`` 同时存在。

    Args:
        path: 要检查的目录路径

    Returns:
        bool: 命中任一信号返回 True
    """
    return detect_workspace_signal(path) is not None


def find_specweave_root(start_path: str = None) -> Optional[str]:
    """
    从起始路径向上遍历，查找 SpecWeave 工作区根目录。

    Args:
        start_path: 起始路径，默认为当前工作目录

    Returns:
        Optional[str]: 找到的 SpecWeave 根目录绝对路径，未找到返回 None
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    try:
        current_path = start_path
        while True:
            if is_specweave_workspace(str(current_path)):
                return str(current_path)
            parent_path = current_path.parent
            if parent_path == current_path:
                break
            current_path = parent_path
    except PermissionError:
        logger.debug(f"权限不足，无法遍历目录: {start_path}")
    except Exception as e:
        logger.debug(f"查找工作区根目录时发生错误: {e}")

    return None


def detect_subregion(cwd: str, specweave_root: str) -> Optional[str]:
    """
    检测当前工作目录是否位于 apps/projects/vendor 子区域下。

    Args:
        cwd: 当前工作目录
        specweave_root: SpecWeave 工作区根目录

    Returns:
        Optional[str]: 子区域名称（apps/projects/vendor），不在子区域下返回 None
    """
    try:
        cwd_path = Path(cwd).resolve()
        root_path = Path(specweave_root).resolve()

        try:
            cwd_path.relative_to(root_path)
        except ValueError:
            return None

        for subregion in SUBREGIONS:
            subregion_path = root_path / subregion
            try:
                cwd_path.relative_to(subregion_path)
                return subregion
            except ValueError:
                continue

        return None
    except PermissionError:
        logger.debug(f"权限不足，无法检测子区域: {cwd}")
        return None
    except Exception as e:
        logger.debug(f"检测子区域时发生错误: {e}")
        return None
