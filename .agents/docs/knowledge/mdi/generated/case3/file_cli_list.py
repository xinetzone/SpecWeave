from typing import TypedDict, Optional, Union, Literal, Any, List


class List(TypedDict):
    """列出目录内容"""

    path: str
    """目标目录路径，默认为当前目录"""

    recursive: bool | None
    """是否递归列出子目录"""

    pattern: str | None
    """文件名通配符过滤模式（如 *.py）"""

    sort_by: str | None
    """排序方式：name/size/modified"""

    show_hidden: bool | None
    """是否显示隐藏文件"""
