"""受控异常体系：所有面向用户的错误消息均为中文指引。"""


class CheckinHubError(Exception):
    """应用异常基类。"""


class WorkspaceError(CheckinHubError):
    """工作区定位/校验失败（路径越界、缺 tracker.md 等）。"""


class TrackerFormatError(CheckinHubError):
    """tracker.md 格式漂移，无法安全解析/回写。"""

    def __init__(self, message: str, line_no: int | None = None) -> None:
        if line_no is not None:
            message = f"第 {line_no} 行：{message}"
        super().__init__(message)
        self.line_no = line_no


class StorageError(CheckinHubError):
    """local 文件存储读写失败或路径越界。"""


class GateRejected(CheckinHubError):
    """发布前固定门未通过。"""


class BridgeError(CheckinHubError):
    """WebBridge 通道错误（调用方应走降级，不向外抛传输异常）。"""


class PublishError(CheckinHubError):
    """发布编排失败（前置条件不满足、回读不一致、确认时 URL 不匹配等）。"""
