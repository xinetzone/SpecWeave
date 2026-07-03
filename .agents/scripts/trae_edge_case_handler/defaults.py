"""trae_edge_case_handler 默认边界条件模块。

规范文档中定义的19个默认边界条件的注册初始化。
"""

from __future__ import annotations

from .models import BoundaryCondition, BoundaryLevel, BoundaryScene
from .registry import register_boundary


def _init_default_boundaries() -> None:
    """初始化规范文档中定义的19个默认边界条件。"""

    register_boundary(BoundaryCondition(
        name="trae-ide-sandbox-limitation",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.FATAL,
        description="沙箱文件系统限制：写入操作返回权限错误",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-mcp-unavailable",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.WARNING,
        description="MCP 工具可用性波动：工具调用返回 not found/timeout",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-browser-login-dependency",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.WARNING,
        description="集成浏览器登录状态依赖：操作跳转至登录页",
    ))
    register_boundary(BoundaryCondition(
        name="trae-ide-terminal-session-isolation",
        scene=BoundaryScene.IDE_INTEGRATION,
        default_level=BoundaryLevel.INFO,
        description="IDE 内终端会话隔离：命令间状态不持久",
    ))

    register_boundary(BoundaryCondition(
        name="trae-forum-login-expired",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="登录状态过期：Cookie 失效，页面跳转登录页",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-dom-change",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="DOM 结构变化：CSS 选择器返回空",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-rate-limit",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="频率限制触发：HTTP 429 或页面提示操作太频繁",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-draft-accumulation",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.INFO,
        description="草稿残留堆积：草稿列表超过阈值",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-review-status-uncertain",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.INFO,
        description="帖子审核状态不确定：状态为 pending/queued",
    ))
    register_boundary(BoundaryCondition(
        name="trae-forum-pagination-anomaly",
        scene=BoundaryScene.FORUM_OPERATION,
        default_level=BoundaryLevel.WARNING,
        description="回复分页导航异常：分页选择器失效",
    ))

    register_boundary(BoundaryCondition(
        name="trae-toolchain-install-failed",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.FATAL,
        description="工具安装失败：command not found",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-api-key-missing",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.FATAL,
        description="API Key 缺失：环境变量为空，API 返回 401/403",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-version-incompatible",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="工具版本不兼容：参数不支持或版本低于要求",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-powershell-encoding",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="跨平台编码差异：中文乱码或引号转义异常",
    ))
    register_boundary(BoundaryCondition(
        name="trae-toolchain-network-unreachable",
        scene=BoundaryScene.EXTERNAL_TOOLCHAIN,
        default_level=BoundaryLevel.WARNING,
        description="网络可达性不确定：连接超时或 DNS 解析失败",
    ))

    register_boundary(BoundaryCondition(
        name="trae-work-token-expired",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.WARNING,
        description="授权 Token 过期：API 返回 401 或 token_expired",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-api-rate-limited",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.WARNING,
        description="API 限流：HTTP 429 或 X-RateLimit-Remaining: 0",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-link-permission-denied",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.INFO,
        description="消息链接权限限制：访问返回 403",
    ))
    register_boundary(BoundaryCondition(
        name="trae-work-app-scope-insufficient",
        scene=BoundaryScene.TRAE_WORK,
        default_level=BoundaryLevel.FATAL,
        description="飞书应用范围不足：app_scope_insufficient",
    ))
