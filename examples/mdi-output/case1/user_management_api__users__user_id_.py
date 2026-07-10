from typing import TypedDict, Optional, Union, Literal, Any, List


class UsersUserId(TypedDict):
    """删除用户"""

    user_id: str
    """用户ID，路径参数"""

    force: bool | None
    """是否强制删除（跳过二次确认）"""
