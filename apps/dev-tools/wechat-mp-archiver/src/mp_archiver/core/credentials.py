"""手机端互动接口凭证加载（环境变量/.env，唯一入口）。

凭证仅在用户显式开启 ``fetch_metrics`` 时使用；不落日志、不入库。
必需项 ``appmsg_token`` 与 ``pass_ticket`` 任一缺失即视为无凭证，
主流程按 ``skipped_no_credential`` 优雅降级，不记为失败。
"""

from dataclasses import dataclass

from ..config import Settings


@dataclass(frozen=True, slots=True)
class WebCredentials:
    appmsg_token: str
    pass_ticket: str
    key: str = ""
    wxuin: str = ""

    def is_complete(self) -> bool:
        return bool(self.appmsg_token and self.pass_ticket)


def load_web_credentials(settings: Settings) -> WebCredentials | None:
    """从配置读取互动凭证；必需项缺失返回 ``None``（调用方走降级路径）。"""
    credentials = WebCredentials(
        appmsg_token=settings.wechat_appmsg_token.get_secret_value().strip(),
        pass_ticket=settings.wechat_pass_ticket.get_secret_value().strip(),
        key=settings.wechat_key.get_secret_value().strip(),
        wxuin=settings.wechat_wxuin.get_secret_value().strip(),
    )
    return credentials if credentials.is_complete() else None
