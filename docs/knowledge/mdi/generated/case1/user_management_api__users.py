from typing import TypedDict, Optional, Union, Literal, Any, List


class Users(TypedDict):
    """创建新用户"""

    name: str
    """用户姓名，2-50个字符"""

    email: str
    """邮箱地址，需唯一"""

    password: str
    """密码，至少8位，包含大小写字母和数字"""

    avatar: str | None
    """头像URL"""

    role: str | None
    """用户角色：user/admin/moderator"""

    bio: str | None
    """个人简介，最多200字"""
