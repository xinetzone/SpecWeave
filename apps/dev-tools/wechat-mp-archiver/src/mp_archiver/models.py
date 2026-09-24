"""领域枚举与数据模型。"""

import enum
from dataclasses import dataclass


class ArticleStatus(str, enum.Enum):
    """文章采集状态机。"""

    PENDING = "pending"
    DOWNLOADED = "downloaded"
    FAILED = "failed"
    SKIPPED = "skipped"
    SKIPPED_NO_CREDENTIAL = "skipped_no_credential"
    EXTERNAL_REF = "external_ref"  # 迁移到视频号/站外等，仅登记外链


class MediaType(str, enum.Enum):
    IMAGE = "image"
    AUDIO = "audio"  # mpvoice
    VIDEO = "video"
    FILE = "file"  # 附件/文档
    EXTERNAL = "external"  # 站外资源（视频号等），仅登记引用


class MediaStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADED = "downloaded"
    FAILED = "failed"
    EXTERNAL = "external"


class CredentialStatus(str, enum.Enum):
    VALID = "valid"
    EXPIRED = "expired"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class ArticleRecord:
    """文章元数据（来自采集列表或官方接口）。

    唯一键：``biz + mid + idx``；无法取得时退化使用 ``sn``。
    """

    biz: str
    account_alias: str = ""
    mid: str | None = None
    idx: int | None = None
    sn: str | None = None
    title: str = ""
    author: str = ""
    publish_time: str | None = None  # ISO8601 字符串
    url: str | None = None
    cover_url: str | None = None
    digest: str = ""
    is_original: bool = False  # 原创声明（copyright_stat，经验值 ==11，待实测校准）
    album: str = ""  # 所属合集/专辑（列表阶段可能为空，正文阶段回填）
    status: ArticleStatus = ArticleStatus.PENDING

    def unique_key(self) -> tuple[str, str | None, int | None] | tuple[None, None, str]:
        if self.mid is not None and self.idx is not None:
            return (self.biz, self.mid, self.idx)
        if self.sn:
            return (None, None, self.sn)
        raise ValueError("文章必须具备 (biz, mid, idx) 或 sn 才能唯一标识")
