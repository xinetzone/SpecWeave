from typing import TypedDict, Optional, Union, Literal, Any, List


class Todos(TypedDict):
    """/todos"""

    title: str
    """待办标题，必填"""

    userId: int
    """用户ID，必填"""

    completed: Optional[bool]
    """是否已完成，可选"""
