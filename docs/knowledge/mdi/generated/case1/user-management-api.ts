/** 获取用户列表 */
export interface Users {
    /** 页码，从1开始 */
    page?: number;
    /** 每页数量，最大100 */
    page_size?: number;
    /** 搜索关键词（用户名/邮箱模糊匹配） */
    keyword?: string;
    /** 用户状态筛选：active/inactive/banned */
    status?: string;
    /** 排序字段：created_at/updated_at/name */
    sort_by?: string;
    /** 排序方向：asc/desc */
    sort_order?: string;
}

/** 获取用户详情 */
export interface UsersUserId {
    /** 用户ID，路径参数 */
    user_id: string;
}

/** 创建新用户 */
export interface Users {
    /** 用户姓名，2-50个字符 */
    name: string;
    /** 邮箱地址，需唯一 */
    email: string;
    /** 密码，至少8位，包含大小写字母和数字 */
    password: string;
    /** 头像URL */
    avatar?: string;
    /** 用户角色：user/admin/moderator */
    role?: string;
    /** 个人简介，最多200字 */
    bio?: string;
}

/** 更新用户信息 */
export interface UsersUserId {
    /** 用户ID，路径参数 */
    user_id: string;
    /** 用户姓名 */
    name?: string;
    /** 邮箱地址 */
    email?: string;
    /** 头像URL */
    avatar?: string;
    /** 个人简介 */
    bio?: string;
    /** 用户状态（仅管理员可修改） */
    status?: string;
}

/** 删除用户 */
export interface UsersUserId {
    /** 用户ID，路径参数 */
    user_id: string;
    /** 是否强制删除（跳过二次确认） */
    force?: boolean;
}

export interface User {
    /** 用户唯一标识，格式：`usr_{随机字符串}` */
    id?: string;
    /** 用户姓名 */
    name?: string;
    /** 邮箱地址 */
    email?: string;
    /** 头像URL */
    avatar?: string;
    /** 账号状态：active/inactive/banned */
    status?: string;
    /** 用户角色：user/admin/moderator */
    role?: string;
    /** 个人简介 */
    bio?: string;
    /** 创建时间（ISO 8601） */
    created_at?: string;
    /** 更新时间（ISO 8601） */
    updated_at?: string;
}

export interface Userlistresponse {
    /** 符合条件的总用户数 */
    total?: number;
    /** 当前页码 */
    page?: number;
    /** 每页数量 */
    page_size?: number;
    /** 用户列表数据 */
    items?: any;
}

export interface Errorresponse {
    /** 错误码 */
    error_code?: string;
    /** 错误描述 */
    error_message?: string;
    /** 错误详细信息 */
    error_details?: Record<string, any>;
}

export {
    Users,
    UsersUserId,
    Users,
    UsersUserId,
    UsersUserId,
};
