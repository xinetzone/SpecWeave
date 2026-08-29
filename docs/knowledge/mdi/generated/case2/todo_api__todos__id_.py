from typing import TypedDict, Optional, Union, Literal, Any, List


class TodosId(TypedDict):
    """/todos/{id}"""

    id: int
    """待办事项ID，必填"""

    completed: bool | None
    """是否已完成过滤，可选"""
