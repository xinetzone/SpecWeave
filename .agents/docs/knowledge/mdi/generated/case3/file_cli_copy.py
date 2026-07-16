from typing import TypedDict, Optional, Union, Literal, Any, List


class Copy(TypedDict):
    """复制文件或目录"""

    source: str
    """源文件或目录路径（必填）"""

    destination: str
    """目标路径（必填）"""

    recursive: bool | None
    """是否递归复制目录"""

    force: bool | None
    """强制覆盖已存在的目标文件"""

    preserve_metadata: bool | None
    """保留文件元数据（时间戳、权限）"""
