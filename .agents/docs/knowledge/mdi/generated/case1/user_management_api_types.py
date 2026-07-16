from typing import TypedDict, Optional, Union, Literal, Any


class Api(TypedDict):
    """提供完整的用户生命周期管理功能，包括用户注册、信息查询、资料更新和账号删除。"""

    id: str | None
    """用户唯一标识，格式：`usr_{随机字符串}`"""

    name: str | None
    """用户姓名"""

    email: str | None
    """邮箱地址"""

    avatar: str | None
    """头像URL"""

    status: str | None
    """账号状态：active/inactive/banned"""

    role: str | None
    """用户角色：user/admin/moderator"""

    bio: str | None
    """个人简介"""

    created_at: str | None
    """创建时间（ISO 8601）"""

    updated_at: str | None
    """更新时间（ISO 8601）"""

    total: int | None
    """符合条件的总用户数"""

    page: int | None
    """当前页码"""

    page_size: int | None
    """每页数量"""

    items: Any | None
    """用户列表数据"""

    error_code: str | None
    """错误码"""

    error_message: str | None
    """错误描述"""

    error_details: dict | None
    """错误详细信息"""

