"""RAG JSONL 导出端到端测试（Task 10 / TR-10.1、AC-11、AC-18）。

覆盖：
- 仅 downloaded 文章入库 JSONL；状态过滤、按发布时间升序；
- TR-10.1：逐行 json.loads、字段齐全、UTF-8 中文、original 为 bool；
- 清洗/不清洗/对照（text_raw）三种模式；
- HTML 缺失隔离失败不阻断、空正文仍保留元数据、空库导出 0 行；
- 幂等重跑与 .tmp 清理；CLI 退出码 0/1/3。
"""

import json
import sqlite3

import pytest

from mp_archiver.db import (
    connect,
    init_db,
    mark_article_archived,
    upsert_article,
)
from mp_archiver.exporters.rag import export_rag_jsonl
from mp_archiver.models import ArticleRecord, ArticleStatus


def _article(
    biz: str,
    mid: str,
    idx: int,
    *,
    title: str,
    alias: str = "测试号",
    publish_time: str | None = "2024-03-01T08:00:00",
    is_original: bool = True,
    album: str = "",
    digest: str = "摘要",
) -> ArticleRecord:
    return ArticleRecord(
        biz=biz,
        account_alias=alias,
        mid=mid,
        idx=idx,
        sn=f"sn-{biz}-{mid}-{idx}",
        title=title,
        author="作者甲",
        publish_time=publish_time,
        url=f"https://mp.weixin.qq.com/s/{mid}{idx}",
        digest=digest,
        is_original=is_original,
        album=album,
    )


def _archive_article(conn, root, record, *, html_body: str | None, rel_dir: str):
    """upsert → 写 article.html → 回写归档路径；返回文章 id。"""
    article_id = upsert_article(conn, record, status=ArticleStatus.PENDING)
    if html_body is not None:
        article_dir = root / rel_dir
        article_dir.mkdir(parents=True, exist_ok=True)
        html_file = article_dir / "article.html"
        html_file.write_text(
            f"<!doctype html><html><body><div id='js_content'>{html_body}</div>"
            "</body></html>",
            encoding="utf-8",
        )
    rel_html = f"{rel_dir}/article.html"
    mark_article_archived(conn, article_id, rel_html, f"{rel_dir}/article.md")
    return article_id


@pytest.fixture
def db_and_root(tmp_path):
    conn: sqlite3.Connection = connect(tmp_path / "test.db")
    init_db(conn)
    root = tmp_path / "arc"
    root.mkdir()
    return conn, root, tmp_path


_JSONL_FIELDS = {
    "id", "account", "title", "author", "publish_time", "url",
    "original", "album", "digest", "text",
}


def test_jsonl_lines_valid_and_fields_complete(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root,
        _article("BIZ1", "2222", 1, title="第一篇：中文标题", album="专栏A"),
        html_body="<p>首段正文。</p><p>第二段正文。</p>",
        rel_dir="测试号/2024/2024-03-01_a",
    )
    _archive_article(
        conn, root,
        _article("BIZ1", "2222", 2, title="第二篇", is_original=False,
                 publish_time="2024-02-01T08:00:00"),
        html_body="<p>另一篇正文。</p>",
        rel_dir="测试号/2024/2024-02-01_b",
    )
    out = tmp_path / "exports" / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out)

    assert report.total == 2 and report.exported == 2 and report.failed == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]  # TR-10.1 逐行合法
    assert len(records) == 2
    # 发布时间升序（早的在前）
    assert [r["title"] for r in records] == ["第二篇", "第一篇：中文标题"]
    for record in records:
        assert set(record) == _JSONL_FIELDS
        assert isinstance(record["original"], bool)
        assert record["text"]
    assert records[1]["album"] == "专栏A"
    assert records[0]["original"] is False


def test_only_downloaded_articles_exported(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="已归档"),
        html_body="<p>正文甲</p>", rel_dir="测试号/2024/a",
    )
    # pending 文章（未下载正文，无归档路径）
    upsert_article(conn, _article("BIZ1", "1", 2, title="待采集"),
                   status=ArticleStatus.PENDING)
    out = tmp_path / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out)

    titles = [json.loads(line)["title"]
              for line in out.read_text(encoding="utf-8").splitlines()]
    assert titles == ["已归档"]
    assert report.total == 1


def test_account_scope_filtering(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="甲号文章", alias="甲号"),
        html_body="<p>甲</p>", rel_dir="甲号/2024/a",
    )
    _archive_article(
        conn, root, _article("BIZ2", "1", 1, title="乙号文章", alias="乙号"),
        html_body="<p>乙</p>", rel_dir="乙号/2024/b",
    )
    out = tmp_path / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out, account_biz="BIZ2")

    titles = [json.loads(line)["title"]
              for line in out.read_text(encoding="utf-8").splitlines()]
    assert titles == ["乙号文章"]
    assert report.total == 1


def test_clean_no_clean_and_raw_comparison(db_and_root):
    conn, root, tmp_path = db_and_root
    body = "<p>正文段落。</p><p>长按识别二维码关注我们</p>"
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="噪声文"),
        html_body=body, rel_dir="测试号/2024/a",
    )

    cleaned_out = tmp_path / "clean.jsonl"
    report = export_rag_jsonl(conn, root, cleaned_out)
    record = json.loads(cleaned_out.read_text(encoding="utf-8"))
    assert "二维码" not in record["text"]
    assert report.removed_noise_lines >= 1

    raw_out = tmp_path / "raw.jsonl"
    export_rag_jsonl(conn, root, raw_out, clean=False)
    raw_record = json.loads(raw_out.read_text(encoding="utf-8"))
    assert "长按识别二维码关注我们" in raw_record["text"]

    both_out = tmp_path / "both.jsonl"
    export_rag_jsonl(conn, root, both_out, with_raw=True)
    both = json.loads(both_out.read_text(encoding="utf-8"))
    assert "text_raw" in both
    assert "长按识别二维码关注我们" in both["text_raw"]
    assert "二维码" not in both["text"]


def test_missing_html_isolated_as_failure_but_batch_continues(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="完好文章"),
        html_body="<p>正文</p>", rel_dir="测试号/2024/ok",
    )
    # downloaded 状态但归档文件被外部删除
    missing_id = upsert_article(
        conn, _article("BIZ1", "1", 2, title="文件丢失"),
        status=ArticleStatus.PENDING,
    )
    mark_article_archived(conn, missing_id, "测试号/2024/gone/article.html",
                          "测试号/2024/gone/article.md")

    out = tmp_path / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out)

    assert report.failed == 1 and report.exported == 1
    assert report.has_failures
    titles = [json.loads(line)["title"]
              for line in out.read_text(encoding="utf-8").splitlines()]
    assert titles == ["完好文章"]
    failed_item = next(item for item in report.items if item.state == "failed")
    assert failed_item.article_id == missing_id and failed_item.error


def test_path_traversal_in_db_rejected(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="正常文"),
        html_body="<p>正文</p>", rel_dir="测试号/2024/ok",
    )
    # 脏数据：绝对路径 / 含 .. 的归档路径不得逃逸 archive_root
    evil_id = upsert_article(
        conn, _article("BIZ1", "1", 2, title="越界文"),
        status=ArticleStatus.PENDING,
    )
    mark_article_archived(
        conn, evil_id, "../../../../etc/passwd", "../../../../etc/passwd.md"
    )
    out = tmp_path / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out)

    assert report.failed == 1 and report.exported == 1
    titles = [json.loads(line)["title"]
              for line in out.read_text(encoding="utf-8").splitlines()]
    assert titles == ["正常文"]


def test_empty_text_article_still_exported_with_metadata(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="纯图片帖"),
        html_body="<p><img data-src='x.jpg'></p>",
        rel_dir="测试号/2024/img",
    )
    out = tmp_path / "rag.jsonl"
    report = export_rag_jsonl(conn, root, out)

    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["title"] == "纯图片帖" and record["text"] == ""
    assert report.empty_text == 1 and report.exported == 1


def test_empty_database_exports_zero_lines(db_and_root):
    conn, root, tmp_path = db_and_root
    out = tmp_path / "nested" / "rag.jsonl"  # 目录不存在自动创建
    report = export_rag_jsonl(conn, root, out)

    assert report.total == 0 and report.exported == 0
    assert out.read_text(encoding="utf-8") == ""


def test_idempotent_overwrite_and_no_tmp_left(db_and_root):
    conn, root, tmp_path = db_and_root
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="唯一文"),
        html_body="<p>正文</p>", rel_dir="测试号/2024/a",
    )
    out = tmp_path / "rag.jsonl"
    export_rag_jsonl(conn, root, out)
    first = out.read_bytes()
    # 再写入一篇后重跑：整体覆盖（无残留），结果与库一致
    _archive_article(
        conn, root, _article("BIZ1", "1", 2, title="第二篇"),
        html_body="<p>正文二</p>", rel_dir="测试号/2024/b",
    )
    export_rag_jsonl(conn, root, out)
    second = out.read_bytes()
    assert first != second
    assert len(second.splitlines()) == 2
    assert not (tmp_path / "rag.jsonl.tmp").exists()
    # 同态重跑输出字节一致
    export_rag_jsonl(conn, root, out)
    assert out.read_bytes() == second


# ---- CLI ----------------------------------------------------------------


def _cli_env(monkeypatch, tmp_path):
    from mp_archiver import cli as cli_module

    cli_module.get_settings.cache_clear()
    monkeypatch.setenv("MP_ARCHIVER_EXPORTER_TOKEN", "")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "cli.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "arc"))
    monkeypatch.setenv("MP_ARCHIVER_EXPORT_ROOT", str(tmp_path / "exports"))
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")


def test_cli_export_rag_success_and_unknown_account(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    conn = connect(tmp_path / "cli.db")
    init_db(conn)
    root = tmp_path / "arc"
    _archive_article(
        conn, root, _article("BIZ1", "1", 1, title="命令行文", alias="甲号"),
        html_body="<p>正文</p><p>点个在看</p>", rel_dir="甲号/2024/a",
    )

    code = cli_module.main(["export-rag", "-a", "甲号"])
    assert code == 0
    out_file = tmp_path / "exports" / "rag.jsonl"
    record = json.loads(out_file.read_text(encoding="utf-8"))
    assert record["title"] == "命令行文"
    assert "在看" not in record["text"]
    printed = capsys.readouterr().out
    assert "导出完成" in printed

    # 未知账号 → 退出码 3
    assert cli_module.main(["export-rag", "-a", "不存在的号"]) == 3


def test_cli_export_rag_reports_failure_exit_1(monkeypatch, tmp_path):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    conn = connect(tmp_path / "cli.db")
    init_db(conn)
    missing_id = upsert_article(
        conn, _article("BIZ1", "1", 9, title="缺失"),
        status=ArticleStatus.PENDING,
    )
    mark_article_archived(conn, missing_id, "x/article.html", "x/article.md")

    code = cli_module.main(["export-rag"])
    assert code == 1
