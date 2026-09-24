"""采集源适配器层（Task 3/4/8 实现）。

适配器把不同采集后端（R2 私有部署的 wechat-download-api /
wechat-article-exporter、R1 微信官方发布接口）封装为统一协议，
核心管线不依赖任何单一工具的接口形态。
"""

from typing import Protocol, runtime_checkable

from ..models import ArticleRecord, CredentialStatus


class AdapterError(RuntimeError):
    """适配器基类异常。"""


class CredentialExpired(AdapterError):
    """采集服务登录态过期，需要重新扫码续期。"""


@runtime_checkable
class ArticleListAdapter(Protocol):
    """文章列表来源适配器统一契约。"""

    name: str

    def credential_status(self) -> CredentialStatus:
        """返回当前登录态是否可用。"""
        ...

    def list_articles(
        self, account_biz: str, *, cursor: str | None = None
    ) -> tuple[list[ArticleRecord], str | None]:
        """拉取一页文章列表，返回 (本页记录, 下一页游标)；无下一页时游标为 None。"""
        ...
