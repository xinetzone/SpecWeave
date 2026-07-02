from typing import TypedDict, Optional, Union, Literal, Any, List


class Delete(TypedDict):
    """删除文件或目录"""

    target: str
    """要删除的文件或目录路径（必填）"""

    recursive: Optional[bool]
    """是否递归删除非空目录"""

    force: Optional[bool]
    """强制删除（不提示确认）"""

    dry_run: Optional[bool]
    """预览模式，仅显示将被删除的文件"""
