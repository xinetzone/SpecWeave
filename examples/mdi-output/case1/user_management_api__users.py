from typing import TypedDict, Optional, Union, Literal, Any, List


class Users(TypedDict):
    """创建新用户"""

    name: str
    """用户姓名，2-50个字符"""

    email: str
    """邮箱地址，需唯一"""

    password: str
    """密码，至少8位，包含大小写字母和数字"""

    avatar: Optional[str]
    """头像URL"""

    role: Optional[str]
    """用户角色：user/admin/moderator"""

    bio: Optional[str]
    """个人简介，最多200字"""
