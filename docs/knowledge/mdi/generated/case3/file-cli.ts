/** 列出目录内容 */
export interface List {
    /** 目标目录路径，默认为当前目录 */
    path: string;
    /** 是否递归列出子目录 */
    recursive?: boolean;
    /** 文件名通配符过滤模式（如 *.py） */
    pattern?: string;
    /** 排序方式：name/size/modified */
    sort_by?: string;
    /** 是否显示隐藏文件 */
    show_hidden?: boolean;
}

/** 复制文件或目录 */
export interface Copy {
    /** 源文件或目录路径（必填） */
    source: string;
    /** 目标路径（必填） */
    destination: string;
    /** 是否递归复制目录 */
    recursive?: boolean;
    /** 强制覆盖已存在的目标文件 */
    force?: boolean;
    /** 保留文件元数据（时间戳、权限） */
    preserve_metadata?: boolean;
}

/** 删除文件或目录 */
export interface Delete {
    /** 要删除的文件或目录路径（必填） */
    target: string;
    /** 是否递归删除非空目录 */
    recursive?: boolean;
    /** 强制删除（不提示确认） */
    force?: boolean;
    /** 预览模式，仅显示将被删除的文件 */
    dry_run?: boolean;
}

export interface  {
    /** 配置文件路径 */
    FILE_CLI_CONFIG?: string;
    /** 是否启用详细输出 */
    FILE_CLI_VERBOSE?: boolean;
}

export {
    List,
    Copy,
    Delete,
};
