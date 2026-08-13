"""SpecWeave 工作区检测模块。"""

import logging
from pathlib import Path
from typing import Optional

from ._constants import (
    AGENTS_MD_FILENAME,
    SPECWEAVE_SIGNATURE_KEYWORD,
    SUBREGIONS,
)

logger = logging.getLogger(__name__)


def is_specweave_workspace(path: str) -> bool:
    """
    检查指定路径是否为 SpecWeave 工作区。

    Args:
        path: 要检查的目录路径

    Returns:
        bool: 如果路径下存在 AGENTS.md 且包含"启动协议"关键词，返回 True
    """
    try:
        path_obj = Path(path).resolve()
        agents_md = path_obj / AGENTS_MD_FILENAME
        if not agents_md.is_file():
            return False
        content = agents_md.read_text(encoding="utf-8", errors="ignore")
        return SPECWEAVE_SIGNATURE_KEYWORD in content
    except PermissionError:
        logger.debug(f"权限不足，无法访问路径: {path}")
        return False
    except Exception as e:
        logger.debug(f"检查工作区时发生错误: {e}")
        return False


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
