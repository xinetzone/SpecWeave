from typing import TypedDict, Optional, Union, Literal, Any


class Api(TypedDict):
    """提供完整的用户生命周期管理功能，包括用户注册、信息查询、资料更新和账号删除。"""

    id: Optional[str]
    """用户唯一标识，格式：`usr_{随机字符串}`"""

    name: Optional[str]
    """用户姓名"""

    email: Optional[str]
    """邮箱地址"""

    avatar: Optional[str]
    """头像URL"""

    status: Optional[str]
    """账号状态：active/inactive/banned"""

    role: Optional[str]
    """用户角色：user/admin/moderator"""

    bio: Optional[str]
    """个人简介"""

    created_at: Optional[str]
    """创建时间（ISO 8601）"""

    updated_at: Optional[str]
    """更新时间（ISO 8601）"""

    total: Optional[int]
    """符合条件的总用户数"""

    page: Optional[int]
    """当前页码"""

    page_size: Optional[int]
    """每页数量"""

    items: Optional[Any]
    """用户列表数据"""

    error_code: Optional[str]
    """错误码"""

    error_message: Optional[str]
    """错误描述"""

    error_details: Optional[dict]
    """错误详细信息"""

