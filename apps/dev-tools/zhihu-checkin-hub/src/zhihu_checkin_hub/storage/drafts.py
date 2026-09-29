"""创作草稿：local/posts/<slug>.md（YAML frontmatter + Markdown 正文）。

状态机：draft → ready → published（单向推进；published 由发布闭环写回）。
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml  # frontmatter 解析（safe_load）

from ..errors import StorageError
from .atomic import atomic_write_text, dump_yaml
from .entries import ContentKind
from .workspace import Workspace

VALID_STATUSES = ("draft", "ready", "published")
# 仅允许 draft → ready → published 单向
_STATUS_FLOW = {"draft": {"draft", "ready"}, "ready": {"ready", "published"}, "published": {"published"}}

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n\n?", re.DOTALL)
_SLUG_RE = re.compile(r"[^0-9A-Za-z\u4e00-\u9fff_-]+")


def slugify(title: str) -> str:
    slug = _SLUG_RE.sub("-", title.strip()).strip("-")
    return slug[:80]


@dataclass
class Draft:
    slug: str
    title: str
    kind: str
    body: str = ""
    question_url: str = ""
    status: str = "draft"
    created_at: str = ""
    updated_at: str = ""
    published_url: str = ""

    def __post_init__(self) -> None:
        if self.kind not in [k.value for k in ContentKind]:
            raise StorageError(f"草稿类型非法：{self.kind}")
        if self.status not in VALID_STATUSES:
            raise StorageError(f"草稿状态非法：{self.status}")


def draft_path(ws: Workspace, slug: str) -> Path:
    if not slug or slug in {".", ".."} or re.search(r"[\\/]", slug) or slug.startswith("."):
        raise StorageError(f"非法草稿 slug：{slug!r}")
    path = ws.posts_dir / f"{slug}.md"
    return ws.ensure_within_local(path)


def transition_status(current: str, target: str) -> str:
    if target not in _STATUS_FLOW.get(current, set()):
        raise StorageError(f"草稿状态不允许 {current} → {target}")
    return target


def save_draft(ws: Workspace, draft: Draft) -> Path:
    path = draft_path(ws, draft.slug)
    now = datetime.now().isoformat(timespec="seconds")
    if not draft.created_at:
        draft.created_at = now
    draft.updated_at = now
    meta = {
        "slug": draft.slug,
        "title": draft.title,
        "kind": draft.kind,
        "question_url": draft.question_url,
        "status": draft.status,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at,
        "published_url": draft.published_url,
    }
    normalized_body = draft.body.strip("\n")
    text = "---\n" + dump_yaml(meta) + "---\n\n" + normalized_body + "\n"
    atomic_write_text(path, text)
    return path


def load_draft(ws: Workspace, slug: str) -> Draft:
    path = draft_path(ws, slug)
    if not path.is_file():
        raise StorageError(f"草稿不存在：{slug}")
    return _parse_draft(path.read_text(encoding="utf-8"), slug)


def _parse_draft(text: str, slug: str) -> Draft:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise StorageError(f"草稿 {slug} 缺少合法 YAML frontmatter")
    meta = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :].strip("\n")
    return Draft(
        slug=meta.get("slug", slug),
        title=meta.get("title", ""),
        kind=meta.get("kind", ""),
        body=body,
        question_url=meta.get("question_url", ""),
        status=meta.get("status", "draft"),
        created_at=meta.get("created_at", ""),
        updated_at=meta.get("updated_at", ""),
        published_url=meta.get("published_url", ""),
    )


def list_drafts(ws: Workspace) -> list[Draft]:
    if not ws.posts_dir.is_dir():
        return []
    drafts = []
    for path in sorted(ws.posts_dir.glob("*.md")):
        drafts.append(_parse_draft(path.read_text(encoding="utf-8"), path.stem))
    return drafts
