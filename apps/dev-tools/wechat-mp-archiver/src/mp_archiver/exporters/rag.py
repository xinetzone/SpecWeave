"""RAG JSONL 语料导出（Task 10 / AC-11、AC-18）。

纯派生离线任务：不发起任何网络请求，数据源为 DB 中 ``status=downloaded``
的文章与其本地化归档 ``article.html``。

- 每篇一行 JSON（UTF-8、``ensure_ascii=False``），字段：
  ``id/account/title/author/publish_time/url/original/album/digest/text``；
  ``with_raw=True`` 时追加 ``text_raw`` 供清洗前后对照（TR-10.2 抽样评阅）。
- 幂等：输出文件采用「同目录临时文件 + os.replace」整体覆盖，重复导出
  结果稳定；单篇读取/解析失败计入 failed 但不阻断批次。
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from ..core.text_extract import clean_plain_text, html_to_plain_text
from ..db import iter_downloaded_articles


def _resolve_html(archive_root: Path, rel: str) -> Path | None:
    """归档相对路径 → 绝对路径；拒绝绝对路径与 ``..`` 逃逸（防脏数据越界）。"""
    rel_path = Path(rel)
    if rel_path.is_absolute() or ".." in rel_path.parts:
        return None
    return archive_root / rel_path


@dataclass(frozen=True, slots=True)
class RagExportItem:
    article_id: int
    title: str
    state: str  # exported / empty_text / failed
    error: str = ""


@dataclass(frozen=True, slots=True)
class RagExportReport:
    out_path: Path
    total: int = 0
    exported: int = 0
    empty_text: int = 0
    failed: int = 0
    cleaned: bool = True
    with_raw: bool = False
    removed_noise_lines: int = 0
    collapsed_duplicates: int = 0
    trimmed_tail_lines: int = 0
    items: tuple[RagExportItem, ...] = field(default_factory=tuple)

    @property
    def has_failures(self) -> bool:
        return self.failed > 0


def _build_record(article, text: str, text_raw: str | None) -> dict:
    record = {
        "id": article["id"],
        "account": article["account_alias"],
        "title": article["title"],
        "author": article["author"],
        "publish_time": article["publish_time"],
        "url": article["url"],
        "original": bool(article["is_original"]),
        "album": article["album"],
        "digest": article["digest"],
        "text": text,
    }
    if text_raw is not None:
        record["text_raw"] = text_raw
    return record


def export_rag_jsonl(
    conn,
    archive_root: str | Path,
    out_path: str | Path,
    *,
    account_biz: str | None = None,
    clean: bool = True,
    with_raw: bool = False,
    limit: int | None = None,
) -> RagExportReport:
    """导出已归档文章为 RAG JSONL。

    ``content_html_path`` 为空或文件不可读/解析异常的文章计入 failed；
    正文提取为空（纯图片/视频帖）仍导出（元数据可检索），单独计数。
    """
    archive_root = Path(archive_root)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    items: list[RagExportItem] = []
    exported = 0
    empty_text = 0
    failed = 0
    noise = dup = trimmed = 0

    tmp_path = out_path.with_name(out_path.name + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as sink:
        for article in iter_downloaded_articles(
            conn, account_biz=account_biz, limit=limit
        ):
            rel = article["content_html_path"]
            if not rel:
                failed += 1
                items.append(RagExportItem(
                    article["id"], article["title"], "failed",
                    "content_html_path 为空（文章状态为 downloaded 但缺归档路径）",
                ))
                continue
            html_file = _resolve_html(archive_root, rel)
            if html_file is None:
                failed += 1
                items.append(RagExportItem(
                    article["id"], article["title"], "failed",
                    f"归档路径越界（含绝对路径或 ..）：{rel}"[:200],
                ))
                continue
            try:
                raw_html = html_file.read_text(encoding="utf-8")
                text_raw = html_to_plain_text(raw_html)
            except (OSError, ValueError) as exc:
                failed += 1
                items.append(RagExportItem(
                    article["id"], article["title"], "failed",
                    f"{type(exc).__name__}: {exc}"[:200],
                ))
                continue

            text = text_raw
            if clean:
                text, stats = clean_plain_text(text_raw)
                noise += stats.removed_noise_lines
                dup += stats.collapsed_duplicates
                trimmed += stats.trimmed_tail_lines

            if not text.strip():
                empty_text += 1
                items.append(RagExportItem(
                    article["id"], article["title"], "empty_text"
                ))
            else:
                items.append(RagExportItem(
                    article["id"], article["title"], "exported"
                ))

            record = _build_record(
                article, text, text_raw if with_raw else None
            )
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            exported += 1

    os.replace(tmp_path, out_path)

    total = exported + failed
    return RagExportReport(
        out_path=out_path,
        total=total,
        exported=exported,
        empty_text=empty_text,
        failed=failed,
        cleaned=clean,
        with_raw=with_raw,
        removed_noise_lines=noise,
        collapsed_duplicates=dup,
        trimmed_tail_lines=trimmed,
        items=tuple(items),
    )
