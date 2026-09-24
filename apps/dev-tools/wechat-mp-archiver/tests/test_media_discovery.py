"""media_discovery 富媒体识别纯函数测试（TR-6.2）。

覆盖：微信语音（新旧两种标签）、腾讯视频 embed、视频号卡片/链接、
站外播放器、去重与可下载性判定。
"""

from bs4 import BeautifulSoup

from mp_archiver.core.media_discovery import discover_rich_media
from mp_archiver.models import MediaType

SAMPLE = """
<div id="js_content">
  <mpvoice voice_encode_fileid="MzAxF123" name="旧版语音" play_length="30000"
           src="/mp/readtemplate?t=media/voice_detail"></mpvoice>
  <mp-common-mpvoice data-fileid="MzAxF456" data-name="新版语音"
                     data-playlength="65000"
                     data-src="https://res.wx.qq.com/voice/getvoice?mediaid=MzAxF456">
  </mp-common-mpvoice>
  <iframe class="video_iframe"
          data-src="https://v.qq.com/txp/iframe/player.html?vid=vid789&tiny=0">
  </iframe>
  <mp-common-videosnap data-vid="vid999" data-title="短视频组件"></mp-common-videosnap>
  <mp-common-channels_video data-object_id="oid111" data-nickname="某视频号">
  </mp-common-channels_video>
  <iframe data-src="https://www.xiaoyuzhoufm.com/player/episode/abc123"></iframe>
  <iframe data-src="https://player.bilibili.com/player.html?bvid=BV1xx"></iframe>
  <a href="weixin://channels/live/profile/xxx">点此观看视频号直播</a>
  <mpvoice voice_encode_fileid="MzAxF123" name="旧版语音重复"></mpvoice>
</div>
"""


def _candidates():
    soup = BeautifulSoup(SAMPLE, "html.parser")
    return discover_rich_media(soup)


def test_voice_candidates_are_downloadable():
    voices = [c for c in _candidates() if c.provider == "mpvoice"]
    assert len(voices) == 2
    old, new = voices
    assert old.media_type is MediaType.AUDIO
    assert old.local_id == "MzAxF123"
    assert old.url == "https://res.wx.qq.com/voice/getvoice?mediaid=MzAxF123"
    assert old.downloadable is True
    assert old.extra["duration_ms"] == 30000

    assert new.url.endswith("mediaid=MzAxF456")
    assert new.extra["duration_ms"] == 65000
    assert new.downloadable is True


def test_tencent_video_candidates_are_placeholder_only():
    videos = [c for c in _candidates() if c.provider == "tencent_video"]
    assert {c.extra["vid"] for c in videos} == {"vid789", "vid999"}
    assert all(c.media_type is MediaType.VIDEO for c in videos)
    assert all(c.downloadable is False for c in videos)


def test_channels_candidates_unavailable():
    channels = [c for c in _candidates() if c.provider == "channels"]
    # 卡片 + weixin:// 链接（不同 local_id，均保留）
    assert len(channels) == 2
    assert all(c.media_type is MediaType.EXTERNAL for c in channels)
    assert all(c.extra["reason"] == "video_channel_unavailable" for c in channels)
    assert all(c.downloadable is False for c in channels)


def test_external_players_classified_by_domain():
    externals = [
        c for c in _candidates()
        if c.provider.startswith("external_")
    ]
    assert len(externals) == 2
    by_host = {c.extra["host"]: c for c in externals}
    assert by_host["www.xiaoyuzhoufm.com"].media_type is MediaType.AUDIO
    assert by_host["player.bilibili.com"].media_type is MediaType.VIDEO
    assert all(c.downloadable is False for c in externals)


def test_dedupe_same_fileid():
    providers = [(c.provider, c.local_id) for c in _candidates()]
    assert providers.count(("mpvoice", "MzAxF123")) == 1


def test_voice_without_fileid_or_direct_url_not_downloadable():
    soup = BeautifulSoup(
        '<mpvoice name="无ID语音" src="/mp/readtemplate?t=x"></mpvoice>',
        "html.parser",
    )
    candidate = discover_rich_media(soup)[0]
    assert candidate.downloadable is False
    assert candidate.url is None
