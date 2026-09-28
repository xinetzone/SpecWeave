"""富媒体下载、占位登记与正文节点改写。

硬约束（TR-6.2）：不可下载类型（腾讯视频/视频号/站外播放器）**不得生成伪造
本地文件**，只在 media 表以 external 状态登记，并把正文原节点替换为可读说明。
可下载的微信语音落盘 ``media/NNN.ext``，登记大小/哈希/MIME，失败则 FAILED。
"""

import hashlib
import logging
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup, Tag

from ..db import upsert_media
from ..models import MediaStatus, MediaType
from .media_discovery import MediaCandidate, iter_media_nodes

logger = logging.getLogger(__name__)

_AUDIO_HEADERS = {"Referer": "https://mp.weixin.qq.com/"}
_AUDIO_EXT = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/x-amr": ".amr",
    "audio/amr": ".amr",
    "audio/mp4": ".m4a",
    "audio/aac": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
}

_LABELS = {
    "mpvoice": "音频·微信语音",
    "tencent_video": "视频·腾讯视频",
    "channels": "视频号",
    "external_audio": "站外音频",
    "external_video": "站外视频",
    "external_embed": "站外内容",
}


@dataclass(frozen=True, slots=True)
class MediaResult:
    candidate: MediaCandidate
    file: str | None
    ok: bool
    size_bytes: int
    sha256: str | None
    error: str = ""


def guess_audio_ext(url: str, content_type: str | None) -> str:
    if content_type:
        mime = content_type.split(";", 1)[0].strip().lower()
        if mime in _AUDIO_EXT:
            return _AUDIO_EXT[mime]
    lowered = url.lower()
    for ext in (".mp3", ".amr", ".m4a", ".aac", ".wav"):
        if ext in lowered:
            return ext
    return ".mp3"


def _duration_label(ms: int | None) -> str:
    if not ms:
        return ""
    total_seconds = max(1, round(ms / 1000))
    return f"时长 {total_seconds // 60}:{total_seconds % 60:02d}"


def _replace_with_note(tag: Tag, text: str) -> None:
    """把原媒体节点替换为斜体说明段落（HTML 与 Markdown 均可读）。"""
    owner = tag
    while owner is not None and not isinstance(owner, BeautifulSoup):
        owner = owner.parent
    paragraph = owner.new_tag("p") if owner is not None else BeautifulSoup(
        f"<p><em>{text}</em></p>", "html.parser"
    ).p
    italic = owner.new_tag("em") if owner is not None else paragraph.new_tag("em")
    italic.string = text
    paragraph.append(italic)
    tag.replace_with(paragraph)


def _note_text(candidate: MediaCandidate, *, file: str | None, error: str = "") -> str:
    label = _LABELS.get(candidate.provider, candidate.provider)
    title = candidate.title
    if candidate.provider == "mpvoice":
        duration = _duration_label(candidate.extra.get("duration_ms"))
        if file:
            tail = f"已归档：{file}" + (f"（{duration}）" if duration else "")
        else:
            tail = f"下载失败：{error}，原链接 {candidate.url}"
        return f"[{label}] {title}，{tail}"
    if candidate.provider == "tencent_video":
        vid = candidate.extra.get("vid", "")
        return (
            f"[{label}] {title}（平台限制未下载，vid={vid}）"
            f"{'：' + candidate.url if candidate.url else ''}"
        )
    if candidate.provider == "channels":
        return f"[{label}] {title}（平台限制，无法归档）"
    return f"[{label}] {title}（仅登记引用）：{candidate.url or candidate.local_id}"


def collect_rich_media(conn, client, content, article_id: int, target_dir) -> tuple[MediaResult, ...]:
    """发现→下载/占位→改写节点→登记 media 表；单条失败不影响其他媒体。"""
    results: list[MediaResult] = []
    seq = 0
    for tag, candidate in iter_media_nodes(content):
        registry_url = candidate.url or f"{candidate.provider}:{candidate.local_id}"

        if not candidate.downloadable:
            upsert_media(
                conn,
                article_id=article_id,
                media_type=candidate.media_type,
                url=registry_url,
                status=MediaStatus.EXTERNAL,
                fail_reason=candidate.extra.get("reason", "not_downloadable"),
            )
            _replace_with_note(tag, _note_text(candidate, file=None))
            results.append(
                MediaResult(candidate, file=None, ok=True, size_bytes=0,
                            sha256=None)
            )
            continue

        seq += 1
        try:
            response = client.get(candidate.url, headers=_AUDIO_HEADERS)
            if response.status_code != 200:
                raise httpx.HTTPStatusError(
                    f"媒体 HTTP {response.status_code}",
                    request=response.request,
                    response=response,
                )
            ext = guess_audio_ext(candidate.url, response.headers.get("content-type"))
            media_dir = target_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            relative = f"media/{seq:03d}{ext}"
            (target_dir / relative).write_bytes(response.content)
            digest = hashlib.sha256(response.content).hexdigest()
            upsert_media(
                conn,
                article_id=article_id,
                media_type=candidate.media_type,
                url=registry_url,
                status=MediaStatus.DOWNLOADED,
                local_path=relative,
                mime=response.headers.get("content-type", "").split(";", 1)[0] or None,
                sha256=digest,
                size_bytes=len(response.content),
            )
            _replace_with_note(tag, _note_text(candidate, file=relative))
            results.append(
                MediaResult(candidate, file=relative, ok=True,
                            size_bytes=len(response.content), sha256=digest)
            )
        except (httpx.HTTPError, OSError) as exc:
            logger.warning("媒体下载失败：%s (%s)", candidate.url, exc)
            upsert_media(
                conn,
                article_id=article_id,
                media_type=candidate.media_type,
                url=registry_url,
                status=MediaStatus.FAILED,
                fail_reason=str(exc)[:300],
            )
            _replace_with_note(tag, _note_text(candidate, file=None, error=str(exc)[:120]))
            results.append(
                MediaResult(candidate, file=None, ok=False, size_bytes=0,
                            sha256=None, error=str(exc)[:200])
            )

    return tuple(results)
