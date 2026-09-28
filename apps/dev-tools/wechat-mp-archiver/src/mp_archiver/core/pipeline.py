"""统一采集编排（Task 9 / AC-8）：列表 → 正文/富媒体 → 互动。

两条入口共用同一条幂等管线，区别仅在列表阶段策略：

- ``full=False``（``mp-archiver sync``，增量）：列表以 catch-up 模式从最新页
  向后翻，遇到整页全已知即停、不做下架对账；正文阶段只处理 pending 新文章。
  日常调度使用，请求量最小。
- ``full=True``（``mp-archiver run --full``，回溯+校验）：列表完整翻到尾页
  并执行不可见文章对账，正文阶段可带 ``--include-failed`` 重试历史失败。

断点续跑由既有状态机保证，无需额外检查点：文章级 ``status`` 使已 downloaded
的文章永不重下，账号级水位（sync_state）记录列表进度；进程在任意时刻被 kill，
重跑后 pending 集合自然排除已完成项，同一文章目录采用「整体清空重写」，
因此重复运行零重复文件。

凭证边界：列表阶段访问本地采集服务（带 Bearer Token）；正文/媒体/互动阶段
直连 ``mp.weixin.qq.com`` 公域，使用剥离 Token 的 Settings 副本，避免把
本地服务凭证发往微信域（与独立 ``fetch`` 命令同一纪律）。
"""

from dataclasses import dataclass

from pydantic import SecretStr

from ..adapters.wechat_download_api import WechatDownloadApiAdapter
from ..config import Settings
from ..http_client import RateLimitedClient
from .article_archive import FetchReport, fetch_articles
from .list_sync import SyncReport, sync_article_list


@dataclass(frozen=True, slots=True)
class PipelineReport:
    """一次统一编排（列表+正文）的结果摘要。"""

    account: str
    mode: str  # "incremental" / "full"
    list: SyncReport
    fetch: FetchReport

    @property
    def has_fetch_failures(self) -> bool:
        return self.fetch.failed > 0


def run_list_stage(
    conn,
    client,
    settings: Settings,
    account: str,
    *,
    full: bool,
    max_pages: int | None,
    no_reconcile: bool,
) -> SyncReport:
    """列表阶段：构造采集服务适配器并按全量/增量策略同步。"""
    adapter = WechatDownloadApiAdapter.build(
        client,
        base_url=settings.exporter_url,
        search_override=settings.exporter_search_path,
        history_override=settings.exporter_history_path,
    )
    return sync_article_list(
        conn,
        adapter,
        name=account,
        max_pages=max_pages,
        full_reconcile=full and not no_reconcile,
        catch_up=not full,
    )


def run_pipeline(
    conn,
    settings: Settings,
    account: str,
    *,
    full: bool = False,
    include_failed: bool = False,
    fetch_limit: int | None = None,
    max_pages: int | None = None,
    no_reconcile: bool = False,
    client_factory=RateLimitedClient,
) -> PipelineReport:
    """执行 列表 → 正文/富媒体/互动 的两阶段编排。

    异常不在本层吞掉：列表阶段的凭证失效（退出码 2）、未知账号（3）、
    环境/端点异常（4）由 CLI 统一映射；正文阶段单篇失败已在 fetch_articles
    内部隔离并体现在报告中。

    ``client_factory`` 仅用于测试注入假客户端；生产路径为
    :class:`mp_archiver.http_client.RateLimitedClient`。
    """
    mode = "full" if full else "incremental"

    # 阶段 1：本地采集服务（携带本地 Token）
    with client_factory(settings) as client:
        list_report = run_list_stage(
            conn,
            client,
            settings,
            account,
            full=full,
            max_pages=max_pages,
            no_reconcile=no_reconcile,
        )

    # 阶段 2：微信公域直连（剥离本地采集服务 Token）
    public_settings = settings.model_copy(update={"exporter_token": SecretStr("")})
    with client_factory(public_settings) as client:
        fetch_report = fetch_articles(
            conn,
            client,
            account,
            public_settings.archive_root,
            include_failed=include_failed,
            limit=fetch_limit,
            settings=public_settings,
        )

    return PipelineReport(
        account=account,
        mode=mode,
        list=list_report,
        fetch=fetch_report,
    )
