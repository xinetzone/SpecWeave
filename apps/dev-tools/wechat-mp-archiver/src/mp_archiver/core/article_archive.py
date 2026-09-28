"""单篇文章归档与批量抓取编排。

产出物目录布局（TR-5.1 四件套）::

    archive/<账号别名>/<YYYY>/<YYYY-MM-DD_安全标题>/
        article.html      # 完整原始页面（正文图片已本地化，可离线打开）
        article.md        # 正文 Markdown（标题/列表/代码/引用结构保留）
        metadata.json     # 元数据与图片下载清单（含失败例外）
        images/001.png    # 正文图片（微信 mmbiz 及外链图全部本地化）

单篇图片失败不阻断归档：失败图片保留远程引用并登记进 metadata 的例外表
（TR-5.1 允许「原图失效的外链登记例外表」）；页面明确为已删除/违规时
标记 skipped（重试无意义）；风控验证页与传输异常由批量编排标记 failed。
"""

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import hashlib

import httpx

from ..db import (
    get_account_biz_by_alias,
    iter_articles_by_status,
    mark_article_archived,
    mark_article_failed,
    upsert_media,
)
from ..models import ArticleStatus, MediaStatus, MediaType
from ..naming import article_dir_name, safe_filename
from .html_transform import (
    classify_page,
    collect_image_urls,
    content_to_markdown,
    drop_placeholder_images,
    extract_content_soup,
    guess_image_ext,
    localize_image,
    preserve_remote_image,
)
from .media_collect import collect_rich_media
from .comment_sync import (
    STATE_COLLECTED,
    STATE_FAILED,
    STATE_SKIPPED,
    sync_article_interactions,
)
from ..config import Settings
from ..exceptions import RiskControlError

logger = logging.getLogger(__name__)

# 微信图床对无 Referer 请求一般也放行；显式带 Referer 规避部分防盗链策略
_IMAGE_HEADERS = {"Referer": "https://mp.weixin.qq.com/"}


@dataclass(frozen=True, slots=True)
class ImageOutcome:
    url: str
    file: str | None
    ok: bool
    size_bytes: int
    error: str = ""


@dataclass(frozen=True, slots=True)
class ArchiveOutcome:
    article_id: int
    dir: Path | None
    images: tuple[ImageOutcome, ...] = ()
    skipped_kind: str | None = None

    @property
    def images_failed(self) -> int:
        return sum(1 for item in self.images if not item.ok)


@dataclass(frozen=True, slots=True)
class FetchItem:
    article_id: int
    title: str
    state: str  # downloaded / skipped / failed
    images_failed: int = 0
    error: str = ""


@dataclass(frozen=True, slots=True)
class FetchReport:
    biz: str
    total: int = 0
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    image_failures: int = 0
    interactions_collected: int = 0
    interactions_skipped: int = 0
    interactions_failed: int = 0
    comments_collected: int = 0
    items: tuple[FetchItem, ...] = field(default_factory=tuple)
    # 账号/环境级故障熔断：True 表示批次提前中止，未处理文章保持 pending（现场保留）
    aborted: bool = False
    abort_reason: str = ""
    # 批次结束时账号下仍为 pending 的文章总数（含 --limit 未选入部分），
    # 供 CLI 在限流批次熔断时提示真实剩余规模。
    pending_in_account: int = 0

    @property
    def pending_left(self) -> int:
        """本批已选出但熔断时尚未触及的文章数（重跑后自然续跑）。"""
        return self.total - len(self.items)

# ---- 路径与元数据 -----------------------------------------------------

def _resolve_target_dir(root: Path, article) -> Path:
    """计算文章目录；同日同名且属于另一篇文章时追加 -2/-3 后缀。

    若目录中 metadata.json 的 mid+idx 与本文一致，视为本文既往产物
    （调用方负责清空重写）。
    """
    alias_dir = safe_filename(article["account_alias"] or "unknown-account")
    year = (article["publish_time"] or "unknown-date")[:4]
    base = root / alias_dir / year / article_dir_name(
        article["publish_time"], article["title"]
    )
    target = base
    suffix = 2
    while target.exists():
        meta_path = target / "metadata.json"
        if not meta_path.exists():
            break  # 残留空目录：视为本文目录，调用方会整体重建
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            meta = None
        if meta and meta.get("mid") == article["mid"] and meta.get("idx") == article["idx"]:
            break
        target = base.with_name(f"{base.name}-{suffix}")
        suffix += 1
    return target


def _build_metadata(
    article,
    images: tuple[ImageOutcome, ...],
    rich_media: tuple = (),
) -> dict:
    return {
        "title": article["title"],
        "author": article["author"],
        "publish_time": article["publish_time"],
        "biz": article["biz"],
        "mid": article["mid"],
        "idx": article["idx"],
        "sn": article["sn"],
        "url": article["url"],
        "cover_url": article["cover_url"],
        "digest": article["digest"],
        "is_original": bool(article["is_original"]),
        "album": article["album"],
        "archived_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "wechat-mp-archiver",
        "images": [
            {
                "url": item.url,
                "file": item.file,
                "ok": item.ok,
                "size_bytes": item.size_bytes,
                "error": item.error,
            }
            for item in images
        ],
        "rich_media": [
            {
                "type": item.candidate.media_type.value,
                "provider": item.candidate.provider,
                "title": item.candidate.title,
                "local_id": item.candidate.local_id,
                "url": item.candidate.url,
                "file": item.file,
                "ok": item.ok,
                "size_bytes": item.size_bytes,
                "error": item.error,
            }
            for item in rich_media
        ],
    }


def _build_markdown(article, body_markdown: str, archived_at: str) -> str:
    header_lines = [f"# {article['title']}", ""]
    meta_bits = []
    if article["author"]:
        meta_bits.append(f"作者：{article['author']}")
    if article["publish_time"]:
        meta_bits.append(f"发布时间：{article['publish_time']}")
    if article["url"]:
        meta_bits.append(f"原文：{article['url']}")
    if meta_bits:
        header_lines += ["> " + " ｜ ".join(meta_bits), ""]
    return (
        "\n".join(header_lines)
        + body_markdown.rstrip()
        + f"\n\n---\n归档时间：{archived_at}\n"
    )


# ---- 单篇归档 ---------------------------------------------------------

def archive_article(conn, client, article, archive_root: str | Path) -> ArchiveOutcome:
    """下载并归档单篇文章。

    - 成功：四件套落盘、DB 置 downloaded 并回写相对路径；
    - 平台明确删除/违规：DB 置 skipped，返回 ``skipped_kind``；
    - 403/429：抛 ``RiskControlError(kind="risk_control")``（立即熔断信号）；
    - 5xx 重试用尽：抛 ``RiskControlError(kind="transport")``（服务整体
      故障信号，参与批次连续传输故障计数）；
    - 容器缺失/未知拦截页/其他异常：向上抛出，由批量编排置 failed。
    """
    root = Path(archive_root)
    response = client.get(article["url"])
    if response.status_code != 200:
        # 403/429 在文章域是账号/IP 级风控信号（单篇文章不会单独 403）：
        # 请求级退避已用尽仍失败，交由批次立即熔断，避免逐篇继续猛打。
        if response.status_code in (403, 429):
            raise RiskControlError(
                "risk_control",
                f"文章页 HTTP {response.status_code}（疑似账号/IP 级风控）",
            )
        # 500/502/503/504 与超时同属服务整体不可用：client 层退避已用尽，
        # 标记为传输族故障，由批次按连续阈值熔断（不能当业务失败归零计数，
        # 否则网关整体故障时会对全部 pending 逐篇重试放大请求量）。
        if response.status_code in (500, 502, 503, 504):
            raise RiskControlError(
                "transport",
                f"文章页 HTTP {response.status_code}（网关/服务端故障）",
            )
        raise httpx.HTTPStatusError(
            f"文章页 HTTP {response.status_code}",
            request=response.request,
            response=response,
        )
    raw_html = response.text
    page_kind = classify_page(raw_html)
    if page_kind == "risk":
        # 风控/验证码页必须在此显式拦截：不能依赖正文容器缺失兜底，
        # 否则含空 js_content 的风控页会被归档成空壳并误标 downloaded。
        raise RiskControlError(
            "risk_control",
            "文章页命中风控/验证码标记（环境异常/需完成验证）",
        )
    if page_kind in ("deleted", "violation"):
        reason = f"content_{page_kind}@{datetime.now(timezone.utc):%Y-%m-%d}"
        conn.execute(
            "UPDATE articles SET status = ?, fail_reason = ?, "
            "updated_at = datetime('now') WHERE id = ?",
            (ArticleStatus.SKIPPED.value, reason, article["id"]),
        )
        conn.commit()
        return ArchiveOutcome(article_id=article["id"], dir=None, skipped_kind=page_kind)

    # 风控页或容器缺失时抛 PageUnavailableError(kind="risk")
    content = extract_content_soup(raw_html)

    # 目录先就位（既往产物整体清空，保证干净重跑）
    target_dir = _resolve_target_dir(root, article)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 下载正文图片并就地改写引用；失败保留远程 URL 并登记
    outcomes: list[ImageOutcome] = []
    for seq, url in enumerate(collect_image_urls(content), start=1):
        try:
            image_resp = client.get(url, headers=_IMAGE_HEADERS)
            if image_resp.status_code != 200:
                raise httpx.HTTPStatusError(
                    f"图片 HTTP {image_resp.status_code}",
                    request=image_resp.request,
                    response=image_resp,
                )
            ext = guess_image_ext(url, image_resp.headers.get("content-type"))
            relative = f"images/{seq:03d}{ext}"
            (target_dir / relative).write_bytes(image_resp.content)
            digest = hashlib.sha256(image_resp.content).hexdigest()
            localize_image(content, url, relative)
            upsert_media(
                conn,
                article_id=article["id"],
                media_type=MediaType.IMAGE,
                url=url,
                status=MediaStatus.DOWNLOADED,
                local_path=relative,
                mime=image_resp.headers.get("content-type", "").split(";", 1)[0] or None,
                sha256=digest,
                size_bytes=len(image_resp.content),
            )
            outcomes.append(
                ImageOutcome(url=url, file=relative, ok=True,
                             size_bytes=len(image_resp.content))
            )
        except (httpx.HTTPError, OSError) as exc:
            logger.warning("图片下载失败，保留远程引用：%s (%s)", url, exc)
            preserve_remote_image(content, url)
            upsert_media(
                conn,
                article_id=article["id"],
                media_type=MediaType.IMAGE,
                url=url,
                status=MediaStatus.FAILED,
                fail_reason=str(exc)[:300],
            )
            outcomes.append(
                ImageOutcome(url=url, file=None, ok=False, size_bytes=0,
                             error=str(exc)[:200])
            )

    # 真实图片均已处理（本地化或远程兜底）；剩余纯懒加载占位节点删除
    drop_placeholder_images(content)

    # 语音/视频/外链等富媒体：可下载者落盘 media/，不可下载者仅登记并改写节点
    rich_media = collect_rich_media(
        conn, client, content, article["id"], target_dir
    )

    images_tuple = tuple(outcomes)
    archived_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    metadata = _build_metadata(article, images_tuple, rich_media)
    markdown = _build_markdown(article, content_to_markdown(content), archived_at)

    # 完整页面序列化：回溯 <html> 保留原始外壳；确保 head 声明 utf-8
    from bs4 import BeautifulSoup

    page_root = content.find_parent("html")
    if page_root is not None:
        owner = content
        while not isinstance(owner, BeautifulSoup):
            owner = owner.parent
        head = page_root.find("head")
        if head is None:
            head = owner.new_tag("head")
            page_root.insert(0, head)
        if head.find("meta", attrs={"charset": True}) is None:
            head.insert(0, owner.new_tag("meta", charset="utf-8"))
        html_text = "<!doctype html>\n" + str(page_root)
    else:
        html_text = (
            '<!doctype html><html><head><meta charset="utf-8"></head>'
            f"<body>{str(content)}</body></html>"
        )

    (target_dir / "article.html").write_text(html_text, encoding="utf-8")
    (target_dir / "article.md").write_text(markdown, encoding="utf-8")
    (target_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    html_rel = (target_dir / "article.html").relative_to(root).as_posix()
    md_rel = (target_dir / "article.md").relative_to(root).as_posix()
    mark_article_archived(conn, article["id"], html_rel, md_rel)
    return ArchiveOutcome(
        article_id=article["id"], dir=target_dir, images=images_tuple
    )


# ---- 批量编排 ---------------------------------------------------------

def fetch_articles(
    conn,
    client,
    account_alias: str,
    archive_root: str | Path,
    *,
    include_failed: bool = False,
    limit: int | None = None,
    settings: Settings | None = None,
) -> FetchReport:
    """批量归档一个账号下 pending（可选含 failed）的文章，逐篇独立成败。

    故障分流（AC-10）：

    - 账号/IP 级风控信号（文章页 403/429 重试用尽、验证码/环境异常页）
      立即熔断：当前篇置 failed（原因可查），后续文章保持 pending 不发请求；
    - 连续传输故障（超时/连接错误，重试用尽）达
      ``settings.transport_abort_threshold`` 时熔断，网络整体不可用不空转；
    - 单篇业务失败（404/解析异常/删除违规）隔离标记，批次继续并给出清单。

    ``settings`` 传入且 ``fetch_metrics=True`` 时，对成功归档的文章追加
    评论/互动指标采集（缺凭证优雅降级，不影响归档结果与退出码）。
    """
    biz = get_account_biz_by_alias(conn, account_alias)
    if biz is None:
        raise LookupError(f"元数据库中没有账号「{account_alias}」，请先执行 list 同步列表")

    statuses = (ArticleStatus.PENDING,)
    if include_failed:
        statuses = (ArticleStatus.PENDING, ArticleStatus.FAILED)
    rows = list(iter_articles_by_status(conn, biz, statuses, limit=limit))
    # 注意：settings=None 时的兜底值必须与 Settings.transport_abort_threshold
    # 的 Field 默认值保持一致（生产路径始终传入 settings）。
    abort_threshold = (
        settings.transport_abort_threshold if settings is not None else 2
    )

    items: list[FetchItem] = []
    downloaded = skipped = failed = image_failures = 0
    interactions_collected = interactions_skipped = interactions_failed = 0
    comments_collected = 0
    transport_streak = 0  # 连续传输故障计数（成功/跳过/单篇业务失败均归零）
    aborted = False
    abort_reason = ""
    for article in rows:
        title = article["title"] or f"id={article['id']}"
        transport_failure: Exception | None = None
        try:
            outcome = archive_article(conn, client, article, archive_root)
        except RiskControlError as exc:
            if exc.kind == "risk_control":
                # 账号级风控：当前篇置 failed 后立即熔断，未触及文章保持 pending，
                # 不再发出任何请求——AC-10「保存现场，不继续猛打」。
                mark_article_failed(conn, article["id"], f"risk_abort: {exc}")
                failed += 1
                aborted = True
                abort_reason = str(exc)
                items.append(
                    FetchItem(article["id"], title, "failed", error=str(exc)[:200])
                )
                logger.error(
                    "风控熔断：文章 id=%s 触发账号级风控，本批剩余 %d 篇保留 pending 不再请求：%s",
                    article["id"], len(rows) - len(items), exc,
                )
                break
            # kind == "transport"（文章页 5xx 重试用尽）：与超时/连接故障
            # 同流，按连续计数决定是否熔断。
            transport_failure = exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            # 重试用尽的传输故障：先隔离为单篇 failed；连续达阈值才熔断。
            transport_failure = exc
        except Exception as exc:  # 单篇失败（404/解析等）不影响后续文章
            mark_article_failed(conn, article["id"], f"{type(exc).__name__}: {exc}")
            failed += 1
            transport_streak = 0  # 拿到业务响应说明网络可达
            items.append(
                FetchItem(article["id"], title, "failed", error=str(exc)[:200])
            )
            logger.warning("文章归档失败 id=%s：%s", article["id"], exc)
            continue

        if transport_failure is not None:
            exc = transport_failure
            transport_streak += 1
            if isinstance(exc, RiskControlError):
                reason = f"transport: {exc}"
                warn_msg = "文章页服务故障 id=%s（连续 %d 次）：%s"
            else:
                reason = f"{type(exc).__name__}: {exc}"
                warn_msg = "文章归档传输失败 id=%s（连续 %d 次）：%s"
            mark_article_failed(conn, article["id"], reason)
            failed += 1
            items.append(
                FetchItem(article["id"], title, "failed", error=str(exc)[:200])
            )
            logger.warning(warn_msg, article["id"], transport_streak, exc)
            if transport_streak >= abort_threshold:
                aborted = True
                abort_reason = (
                    f"连续 {transport_streak} 篇文章传输/服务故障"
                    f"（阈值 {abort_threshold}），疑似网络/服务整体不可用：{exc}"
                )
                logger.error(
                    "传输熔断：%s；本批剩余 %d 篇保留 pending，待网络恢复后续跑",
                    abort_reason, len(rows) - len(items),
                )
                break
            continue

        # 页面可达（成功或 deleted/violation），传输连续计数归零
        transport_streak = 0
        if outcome.skipped_kind is not None:
            skipped += 1
            items.append(
                FetchItem(article["id"], title, "skipped",
                          error=outcome.skipped_kind)
            )
            continue
        downloaded += 1
        image_failures += outcome.images_failed
        items.append(
            FetchItem(article["id"], title, "downloaded",
                      images_failed=outcome.images_failed)
        )

        if settings is not None and settings.fetch_metrics:
            interaction = sync_article_interactions(conn, settings, client, article)
            if interaction.state == STATE_COLLECTED:
                interactions_collected += 1
                comments_collected += interaction.comments_written
            elif interaction.state == STATE_SKIPPED:
                interactions_skipped += 1
            elif interaction.state == STATE_FAILED:
                interactions_failed += 1

    pending_in_account = conn.execute(
        "SELECT COUNT(*) AS c FROM articles WHERE biz = ? AND status = ?",
        (biz, ArticleStatus.PENDING.value),
    ).fetchone()["c"]

    return FetchReport(
        biz=biz,
        total=len(rows),
        downloaded=downloaded,
        skipped=skipped,
        failed=failed,
        image_failures=image_failures,
        interactions_collected=interactions_collected,
        interactions_skipped=interactions_skipped,
        interactions_failed=interactions_failed,
        comments_collected=comments_collected,
        items=tuple(items),
        aborted=aborted,
        abort_reason=abort_reason,
        pending_in_account=pending_in_account,
    )
