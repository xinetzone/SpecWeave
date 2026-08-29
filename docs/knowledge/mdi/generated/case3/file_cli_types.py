from typing import TypedDict, Optional, Union, Literal, Any


class Cli(TypedDict):
    """一个轻量级的跨平台文件操作命令行工具，支持文件列出、复制、删除等常用文件管理功能。"""

    FILE_CLI_CONFIG: str | None
    """配置文件路径"""

    FILE_CLI_VERBOSE: bool | None
    """是否启用详细输出"""

