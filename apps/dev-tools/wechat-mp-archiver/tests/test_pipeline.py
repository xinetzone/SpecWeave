"""统一编排（Task 9 / TR-9.1）测试：

- 全量/增量两种模式的阶段接线（catch_up、对账、重试开关）；
- 列表阶段带本地 Token、正文阶段剥离 Token 的凭证边界；
- 列表阶段失败不进入正文阶段；
- 失败注入 + 重跑补齐（模拟 kill 后续跑）且零重复文件（按哈希）。
"""

import hashlib
import sqlite3
from pathlib import Path

import pytest
from pydantic import SecretStr

from mp_archiver.adapters.base import AccountRef, HistoryPage
from mp_archiver.adapters.wechat_payload import CredentialExpiredError
from mp_archiver.config import Settings
from mp_archiver.core import pipeline
from mp_archiver.core.article_archive import FetchReport
from mp_archiver.core.list_sync import SyncReport
from mp_archiver.db import (
    init_db,
    mark_article_archived,
    mark_article_failed,
    upsert_article,
)
from mp_archiver.models import ArticleRecord, ArticleStatus

from test_list_sync import FakeAdapter, _record


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(connection)
    yield connection
    connection.close()


@pytest.fixture
def settings(tmp_path):
    return Settings(
        exporter_token=SecretStr("local-token"),
        archive_root=tmp_path / "archive",
        db_path=tmp_path / "data" / "x.db",
        request_delay_min=0.0,
        request_delay_max=0.0,
    )


class _DummyClient:
    """记录构造时 Settings（用于断言 Token 剥离），不发起任何请求。"""

    constructed = []

    def __init__(self, settings):
        self.token = settings.exporter_token.get_secret_value()
        type(self).constructed.append(self.token)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _dummy_list_report(**overrides) -> SyncReport:
    base = dict(
        account_name="意识食谱", biz="BIZ==", pages=1, inserted=0, updated=0,
        skipped_non_article=0, hidden_marked=0, completed=True, final_offset=0,
    )
    base.update(overrides)
    return SyncReport(**base)


def test_incremental_wiring_and_token_boundary(conn, settings, monkeypatch):
    list_calls = {}
    fetch_calls = {}

    def fake_list_stage(conn_, client_, settings_, account, **kwargs):
        list_calls.update(kwargs)
        return _dummy_list_report()

    def fake_fetch(conn_, client_, account, root, **kwargs):
        fetch_calls.update(kwargs)
        return FetchReport(biz="BIZ==")

    monkeypatch.setattr(pipeline, "run_list_stage", fake_list_stage)
    monkeypatch.setattr(pipeline, "fetch_articles", fake_fetch)
    _DummyClient.constructed = []

    report = pipeline.run_pipeline(
        conn, settings, "意识食谱", client_factory=_DummyClient
    )

    assert report.mode == "incremental"
    assert list_calls["full"] is False
    assert fetch_calls["include_failed"] is False
    # 阶段 1 带本地 Token，阶段 2 剥离
    assert _DummyClient.constructed == ["local-token", ""]


def test_full_wiring_passes_retry_and_reconcile(conn, settings, monkeypatch):
    list_calls = {}
    fetch_calls = {}

    monkeypatch.setattr(
        pipeline,
        "run_list_stage",
        lambda c, cl, s, a, **kw: (list_calls.update(kw), _dummy_list_report())[1],
    )
    monkeypatch.setattr(
        pipeline,
        "fetch_articles",
        lambda c, cl, a, root, **kw: (fetch_calls.update(kw), FetchReport(biz="BIZ=="))[1],
    )

    report = pipeline.run_pipeline(
        conn, settings, "意识食谱",
        full=True, include_failed=True, fetch_limit=5,
        no_reconcile=True, max_pages=9,
        client_factory=_DummyClient,
    )

    assert report.mode == "full"
    assert list_calls["full"] is True
    assert list_calls["no_reconcile"] is True
    assert list_calls["max_pages"] == 9
    assert fetch_calls["include_failed"] is True
    assert fetch_calls["limit"] == 5


def test_list_stage_failure_aborts_before_fetch(conn, settings, monkeypatch):
    def boom(*a, **k):
        raise CredentialExpiredError(200013, "session expired")

    def must_not_run(*a, **k):
        raise AssertionError("列表阶段失败时不应进入正文阶段")

    monkeypatch.setattr(pipeline, "run_list_stage", boom)
    monkeypatch.setattr(pipeline, "fetch_articles", must_not_run)

    with pytest.raises(CredentialExpiredError):
        pipeline.run_pipeline(conn, settings, "意识食谱", client_factory=_DummyClient)


def test_run_list_stage_incremental_uses_catch_up(conn, settings, monkeypatch):
    # 先种一轮完整全量，建立全量完成标记
    seeded = HistoryPage(
        articles=(_record(100),),
        next_offset=0, has_more=False, skipped_non_article=0,
    )
    adapter = FakeAdapter({0: seeded})
    monkeypatch.setattr(
        pipeline.WechatDownloadApiAdapter, "build", classmethod(lambda cls, *a, **k: adapter)
    )
    # 全量
    pipeline.run_list_stage(
        conn, object(), settings, "意识食谱",
        full=True, max_pages=None, no_reconcile=False,
    )

    # 增量：首页全已知即追平（adapter 没有 offset=10 的页，继续翻就会 KeyError）
    page_known = HistoryPage(
        articles=(_record(100),),
        next_offset=10, has_more=True, skipped_non_article=0,
    )
    adapter_inc = FakeAdapter({0: page_known})
    monkeypatch.setattr(
        pipeline.WechatDownloadApiAdapter, "build",
        classmethod(lambda cls, *a, **k: adapter_inc),
    )
    report = pipeline.run_list_stage(
        conn, object(), settings, "意识食谱",
        full=False, max_pages=None, no_reconcile=False,
    )
    assert report.caught_up is True
    assert adapter_inc.requests == [0]


def _seed_pending_articles(conn, count: int):
    for i in range(1, count + 1):
        upsert_article(
            conn,
            ArticleRecord(
                biz="BIZ==",
                account_alias="意识食谱",
                mid=str(1000 + i),
                idx=1,
                sn=f"sn-{1000 + i}",
                title=f"第{i}篇",
                publish_time=f"2024-01-{i:02d}T00:00:00+00:00",
                url=f"https://mp.weixin.qq.com/s/sn-{1000 + i}",
                status=ArticleStatus.PENDING,
            ),
        )


def _hash_tree(root: Path) -> set[str]:
    digests = set()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digests.add(hashlib.sha256(path.read_bytes()).hexdigest())
    return digests


def test_failure_injection_resume_without_duplicate_files(
    conn, settings, monkeypatch
):
    """TR-9.1：前两轮注入失败（模拟中断），重跑补齐；再跑一次零新增，
    全量文件哈希集合不变（零重复文件）。"""
    from mp_archiver.core import article_archive

    _seed_pending_articles(conn, 4)
    attempts = {"n": 0}

    def fake_archive(conn_, client_, article, archive_root):
        attempts["n"] += 1
        if attempts["n"] <= 2:
            mark_article_failed(conn_, article["id"], "RuntimeError: injected outage")
            raise RuntimeError("injected outage（模拟进程中断/故障）")
        target = Path(archive_root) / f"a{article['id']}"
        target.mkdir(parents=True, exist_ok=True)
        body = f"正文 {article['id']}".encode("utf-8")
        (target / "article.md").write_bytes(body)
        (target / "article.html").write_bytes(b"<html>" + body + b"</html>")
        mark_article_archived(
            conn_, article["id"],
            f"a{article['id']}/article.html", f"a{article['id']}/article.md",
        )

        class _Outcome:
            images_failed = 0
            skipped_kind = None

        return _Outcome()

    monkeypatch.setattr(article_archive, "archive_article", fake_archive)
    monkeypatch.setattr(
        pipeline, "run_list_stage",
        lambda *a, **k: _dummy_list_report(inserted=0),
    )

    # 第一次：2 篇成功、2 篇失败
    first = pipeline.run_pipeline(
        conn, settings, "意识食谱", full=True, client_factory=_DummyClient
    )
    assert first.fetch.downloaded == 2
    assert first.fetch.failed == 2

    # 第二次（增量 + 重试失败）：补齐剩余 2 篇
    second = pipeline.run_pipeline(
        conn, settings, "意识食谱",
        include_failed=True, client_factory=_DummyClient,
    )
    assert second.fetch.total == 2
    assert second.fetch.downloaded == 2
    assert second.fetch.failed == 0

    statuses = {
        row["status"]
        for row in conn.execute("SELECT DISTINCT status FROM articles")
    }
    assert statuses == {"downloaded"}

    hashes_after_resume = _hash_tree(settings.archive_root)
    assert len(hashes_after_resume) == 8  # 4 篇 × html/md

    # 第三次：无待采集，文件系统零变化
    third = pipeline.run_pipeline(
        conn, settings, "意识食谱", client_factory=_DummyClient
    )
    assert third.fetch.total == 0
    assert _hash_tree(settings.archive_root) == hashes_after_resume
