"""采集源适配器契约。"""

from dataclasses import dataclass
from typing import Protocol

from ..models import ArticleRecord


@dataclass(frozen=True, slots=True)
class AccountRef:
    """公众号标识集合。

    微信搜索接口返回 ``fakeid``（平台内部数字 id），历史列表接口需要
    ``biz``（base64 形态的账号标识）；不同采集服务获得二者的路径不同，
    故同时保留，由适配器负责补齐。
    """

    nickname: str
    alias: str = ""
    fakeid: str = ""
    biz: str = ""


@dataclass(frozen=True, slots=True)
class HistoryPage:
    """一页历史群发的解析结果。"""

    articles: tuple[ArticleRecord, ...]
    next_offset: int
    has_more: bool
    skipped_non_article: int


class ArticleListAdapter(Protocol):
    """文章列表采集适配器协议（Task 4 实现 wechat-download-api 形态）。"""

    def resolve_account(self, name: str) -> AccountRef:
        """按昵称/微信号解析账号，必须在多个结果中选中最匹配者。"""
        ...

    def fetch_history_page(self, account: AccountRef, offset: int) -> HistoryPage:
        """拉取从 ``offset`` 起的一页历史群发。"""
        ...
