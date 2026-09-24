"""正文富媒体识别（纯函数层，无网络/无 IO）。

识别五类正文媒体（TR-6.2）：
- ``mpvoice`` 微信语音（可直链下载）；
- ``tencent_video`` 腾讯视频 embed（平台限制，仅登记 vid/链接占位）；
- ``channels`` 视频号卡片（不可下载，``video_channel_unavailable``）；
- ``external_audio`` / ``external_video`` 站外播放器（小宇宙等，仅登记引用）；
- 图片由 :mod:`mp_archiver.core.html_transform` 负责，不在本模块。

标签结构与直链形态依据 2024-2026 公开文章样本与社区导出工具共识，属经验值：
真实样本出现偏差时在本模块选择器处校准，不把经验结构扩散到归档层。
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup, Tag

from ..models import MediaType

VOICE_DIRECT_PREFIX = "https://res.wx.qq.com/voice/getvoice"

# 站外播放器域名 → 媒体类型（仅用于分类，全部不直下，只登记引用）
_EXTERNAL_AUDIO_DOMAINS = (
    "xiaoyuzhoufm.com",
    "ximalaya.com",
    "music.163.com",
    "y.qq.com",
    "mp3",
)
_EXTERNAL_VIDEO_DOMAINS = (
    "bilibili.com",
    "b23.tv",
    "youku.com",
    "iqiyi.com",
    "douyu.com",
)


@dataclass(frozen=True, slots=True)
class MediaCandidate:
    media_type: MediaType
    provider: str  # mpvoice / tencent_video / channels / external_audio / external_video
    url: str | None
    local_id: str  # fileid / vid / 卡片对象 id / 站外 URL
    title: str
    downloadable: bool
    extra: dict = field(default_factory=dict)


def _first_attr(tag: Tag, *names: str) -> str:
    for name in names:
        value = (tag.get(name) or "").strip()
        if value:
            return value
    return ""


def _voice_candidate(tag: Tag) -> MediaCandidate | None:
    """mpvoice 旧标签与 mp-common-mpvoice 新组件 → 语音直链候选。"""
    name = _first_attr(tag, "data-name", "name") or "未命名语音"
    play_length = _first_attr(tag, "data-playlength", "play_length")
    fileid = _first_attr(tag, "data-fileid", "voice_encode_fileid")
    src = _first_attr(tag, "data-src", "src")

    url: str | None = None
    if src.startswith(("http://", "https://")) and "getvoice" in src:
        url = src
    elif fileid:
        url = f"{VOICE_DIRECT_PREFIX}?mediaid={fileid}"

    extra: dict = {}
    if play_length.isdigit():
        extra["duration_ms"] = int(play_length)

    if not url:
        # 既无直链也无 fileid：无法下载，仅登记占位
        return MediaCandidate(
            MediaType.AUDIO, "mpvoice", None, fileid or src, name,
            downloadable=False, extra=extra,
        )
    return MediaCandidate(
        MediaType.AUDIO, "mpvoice", url, fileid or url, name,
        downloadable=True, extra=extra,
    )


def _tencent_video_candidate(tag: Tag) -> MediaCandidate | None:
    src = _first_attr(tag, "data-src", "src")
    vid = ""
    cover = ""
    if src:
        query = parse_qs(urlsplit(src).query)
        vid = (query.get("vid") or [""])[0]
    if not vid:
        vid = _first_attr(tag, "data-vid", "vid")
    cover = _first_attr(tag, "data-cover", "cover")
    if not src and not vid:
        return None
    return MediaCandidate(
        MediaType.VIDEO, "tencent_video",
        url=src or f"https://v.qq.com/x/page/{vid}.html" if vid else None,
        local_id=vid,
        title=_first_attr(tag, "data-title", "title") or "腾讯视频",
        downloadable=False,
        extra={"vid": vid, "cover_url": cover} if cover else {"vid": vid},
    )


def _channels_candidate(tag: Tag) -> MediaCandidate:
    title = _first_attr(tag, "data-nickname", "data-title", "title") or "视频号内容"
    object_id = _first_attr(
        tag, "data-object_id", "data-finder_user_name", "data-id"
    ) or tag.name
    return MediaCandidate(
        MediaType.EXTERNAL, "channels",
        url=_first_attr(tag, "data-src", "src") or None,
        local_id=object_id,
        title=title,
        downloadable=False,
        extra={"reason": "video_channel_unavailable"},
    )


def _external_candidate(tag: Tag) -> MediaCandidate | None:
    src = _first_attr(tag, "data-src", "src")
    if not src or src.startswith(("data:", "//res.wx.qq.com")):
        return None
    if src.startswith("//"):
        src = "https:" + src
    host = urlsplit(src).netloc.lower()
    if "v.qq.com" in host or "mp.weixin.qq.com" in host:
        return None  # 已由其他分支处理
    if any(domain in host for domain in _EXTERNAL_AUDIO_DOMAINS):
        media_type, provider = MediaType.AUDIO, "external_audio"
    elif any(domain in host for domain in _EXTERNAL_VIDEO_DOMAINS):
        media_type, provider = MediaType.VIDEO, "external_video"
    else:
        media_type, provider = MediaType.EXTERNAL, "external_embed"
    return MediaCandidate(
        media_type, provider, url=src, local_id=src,
        title=_first_attr(tag, "data-title", "title") or host or "站外资源",
        downloadable=False,
        extra={"host": host, "reason": "platform_embed_not_downloadable"},
    )


def iter_media_nodes(content: BeautifulSoup) -> Iterator[tuple[Tag, MediaCandidate]]:
    """遍历正文富媒体节点并去重产出 ``(DOM 节点, 媒体候选)``。

    归档层据此就地替换节点为可读说明；纯数据测试用 :func:`discover_rich_media`。
    """
    seen: set[tuple[str, str]] = set()

    def _emit(tag: Tag, candidate: MediaCandidate | None) -> Iterator[tuple[Tag, MediaCandidate]]:
        if candidate is None:
            return
        key = (candidate.provider, candidate.local_id or candidate.url or "")
        if key in seen:
            return
        seen.add(key)
        yield tag, candidate

    for tag in content.find_all(["mpvoice", "mp-common-mpvoice"]):
        yield from _emit(tag, _voice_candidate(tag))

    for tag in content.find_all("iframe"):
        src = _first_attr(tag, "data-src", "src")
        if "v.qq.com" in src:
            yield from _emit(tag, _tencent_video_candidate(tag))
        else:
            yield from _emit(tag, _external_candidate(tag))

    for tag in content.find_all("mp-common-videosnap"):
        yield from _emit(tag, _tencent_video_candidate(tag))

    for tag in content.find_all(True):
        if tag.name.startswith("mp-common-channels"):
            yield from _emit(tag, _channels_candidate(tag))

    for link in content.find_all("a", href=True):
        if "weixin://channels" in link.get("href", ""):
            yield from _emit(
                link,
                MediaCandidate(
                    MediaType.EXTERNAL, "channels",
                    url=link["href"], local_id=link["href"],
                    title=link.get_text(strip=True) or "视频号内容",
                    downloadable=False,
                    extra={"reason": "video_channel_unavailable"},
                ),
            )


def discover_rich_media(content: BeautifulSoup) -> list[MediaCandidate]:
    """发现正文内全部富媒体候选（去重：同 provider+local_id 只保留一条）。"""
    return [candidate for _, candidate in iter_media_nodes(content)]
