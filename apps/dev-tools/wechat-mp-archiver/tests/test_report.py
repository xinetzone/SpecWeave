"""分析报表测试（Task 11 / TR-11.1、TR-11.2、AC-12）。

覆盖：
- TR-11.1：五项统计每个数字与独立重算的 SQL 一致；HTML 含五项区块与对账 SQL；
  CSV 明细行数/派生列（北京时间）与聚合一致；
- TR-11.2：空库/单篇/无时间/无合集/无媒体边界不报错且渲染空态；
- 时区：UTC 跨日/跨月/跨年按北京时间（+8）归属；
- 口径：音视频分母仅 downloaded，未归档 pending 不参与；一篇同时含音视频去重；
- HTML 单文件离线（无外链资源）与专辑名 HTML 转义；
- 原子写入幂等、无 .tmp 残留；CLI 退出码 0/3。
"""

import csv
import io
import sqlite3

import pytest

from mp_archiver.db import (
    connect,
    init_db,
    upsert_article,
    upsert_media,
)
from mp_archiver.exporters.report import (
    WEEKDAY_LABELS,
    build_articles_frame,
    generate_report,
    load_report_data,
    render_html,
)
from mp_archiver.models import (
    ArticleRecord,
    ArticleStatus,
    MediaStatus,
    MediaType,
)

BIZ1 = "biz-one"
BIZ2 = "biz-two"


def _article(
    idx: int,
    *,
    biz: str = BIZ1,
    alias: str = "号甲",
    publish_time: str | None = "2024-03-01T01:30:00",
    is_original: bool = False,
    album: str = "",
    status: ArticleStatus = ArticleStatus.DOWNLOADED,
    title: str | None = None,
):
    return ArticleRecord(
        biz=biz,
        account_alias=alias,
        mid=f"mid-{biz}-{idx}",
        idx=idx,
        sn=f"sn-{biz}-{idx}",
        title=title if title is not None else f"{alias}文章{idx}",
        author="作者",
        publish_time=publish_time,
        url=f"https://mp.weixin.qq.com/s/{idx}",
        is_original=is_original,
        album=album,
        status=status,
    )


def _add(conn, record, *, status=None):
    return upsert_article(conn, record, status=status or record.status)


def _media(conn, article_id, mtype):
    upsert_media(
        conn,
        article_id=article_id,
        media_type=mtype,
        url=f"{mtype.value}:{article_id}",
        status=MediaStatus.EXTERNAL,
    )


@pytest.fixture
def conn(tmp_path):
    c = connect(tmp_path / "test.db")
    init_db(c)
    return c


# ---------- TR-11.2：边界数据 ----------

def test_empty_database_renders_without_error(conn, tmp_path):
    result = generate_report(conn, tmp_path / "report")
    html = result.html_path.read_text(encoding="utf-8")
    raw = result.csv_path.read_bytes()

    assert result.html_path.exists() and result.csv_path.exists()
    # 五项区块均在，且为空态而非异常
    assert html.count("暂无") >= 4
    assert "公众号归档分析报表" in html
    # CSV 仅有表头行（utf-8-sig BOM 开头）
    assert raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines()
    assert len(lines) == 1
    assert "标题" in lines[0]


def test_single_article_renders_all_sections(conn, tmp_path):
    _add(conn, _article(1, publish_time="2024-03-01T01:30:00", is_original=True))
    result = generate_report(conn, tmp_path / "report")
    html = result.html_path.read_text(encoding="utf-8")

    d = result.data
    assert d.total_articles == 1 and d.timed_articles == 1
    assert d.yearly == (("2024", 1),)
    assert d.monthly == (("2024-03", 1),)
    assert d.original_count == 1 and d.original_ratio == 1.0
    assert "2024-03" in html and "100.0%" in html


def test_articles_without_publish_time_excluded_from_time_stats(conn, tmp_path):
    _add(conn, _article(1, publish_time=None))
    _add(conn, _article(2, publish_time=""))
    _add(conn, _article(3, publish_time="2024-03-01T00:00:00"))
    d = load_report_data(conn)

    assert d.total_articles == 3
    assert d.timed_articles == 1
    assert d.missing_time == 2
    assert d.yearly == (("2024", 1),)
    # 无合集时为空元组而非异常
    assert d.album_top == () and d.no_album_count == 1


# ---------- TR-11.1：五项统计与独立 SQL 对账 ----------

@pytest.fixture
def populated(conn):
    """构造跨账号/跨年/含富媒体/状态混合的数据集。

    北京时间口径（UTC+8）：
    - a1 2024-03-01 09:30 周五，原创，合集「算法」，含音频+视频
    - a2 2024-03-05 04:00 周二（UTC 3-4 晚跨日），非原创，合集「算法」，含视频
    - a3 2024-01-01 01:00 周一（UTC 2023-12-31 跨年），原创，无合集
    - a4 2024-02-15 12:00 周四，非原创，合集「随笔」
    - a5 pending 未归档（有发布时间）：参与前四项，不参与音视频分母
    - a6 号乙 2024-03-01 09:30 周五，原创，合集「算法」
    """
    a1 = _add(conn, _article(1, publish_time="2024-03-01T01:30:00",
                             is_original=True, album="算法"))
    a2 = _add(conn, _article(2, publish_time="2024-03-04T20:00:00",
                             is_original=False, album="算法"))
    a3 = _add(conn, _article(3, publish_time="2023-12-31T17:00:00",
                             is_original=True, album=""))
    a4 = _add(conn, _article(4, publish_time="2024-02-15T04:00:00",
                             is_original=False, album="随笔"))
    _add(conn, _article(5, publish_time="2024-03-02T00:00:00"),
         status=ArticleStatus.PENDING)
    _add(conn, _article(6, biz=BIZ2, alias="号乙",
                        publish_time="2024-03-01T01:30:00",
                        is_original=True, album="算法"))
    _media(conn, a1, MediaType.AUDIO)
    _media(conn, a1, MediaType.VIDEO)
    _media(conn, a2, MediaType.VIDEO)
    return conn


def test_five_stats_match_independent_sql(populated):
    """每个数字用独立 SQL 重算（不经过被测 SQL 形态）。"""
    d = load_report_data(populated)

    # 总数/有时间
    assert d.total_articles == populated.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    assert d.timed_articles == populated.execute(
        "SELECT COUNT(*) FROM articles WHERE publish_time IS NOT NULL AND publish_time <> ''"
    ).fetchone()[0]
    # 六篇均有发布时间（a5 pending 但有时间，仍参与时间类统计）
    assert d.timed_articles == 6 and d.missing_time == 0

    # ① 年（北京时间；a3 跨年归入 2024）
    year_counts = dict(populated.execute(
        "SELECT strftime('%Y', publish_time, '+8 hours') y, COUNT(*) FROM articles "
        "WHERE publish_time IS NOT NULL AND publish_time <> '' GROUP BY y"
    ).fetchall())
    assert dict(d.yearly) == year_counts == {"2024": 6}

    # ② 月（a5 2024-03-02 北京计入 3 月）
    month_counts = dict(populated.execute(
        "SELECT strftime('%Y-%m', publish_time, '+8 hours') m, COUNT(*) FROM articles "
        "WHERE publish_time IS NOT NULL AND publish_time <> '' GROUP BY m"
    ).fetchall())
    assert dict(d.monthly) == month_counts == {"2024-01": 1, "2024-02": 1, "2024-03": 4}

    # ③ 热力：a1 与号乙 a6 同为周五(5) 09 时
    assert d.heatmap[(5, 9)] == 2
    assert d.heatmap[(2, 4)] == 1  # a2 周二 04 时（跨日）
    assert d.heatmap[(1, 1)] == 1  # a3 周一 01 时（跨年）
    assert d.heatmap[(6, 8)] == 1  # a5 周六 08 时
    assert sum(d.heatmap.values()) == 6

    # ④ 原创（a1/a3/a6）
    assert d.original_count == 3 and d.non_original_count == 3
    assert d.original_ratio == pytest.approx(3 / 6)

    # ⑤ 合集 Top（含号乙的同名合集；a5 无合集）
    assert d.album_top == (("算法", 3), ("随笔", 1))
    assert d.no_album_count == 2  # a3、a5

    # ⑥ 音视频：分母为 downloaded=5 篇（pending a5 不计）
    assert d.downloaded_total == 5
    assert d.with_audio == 1
    assert d.with_video == 2
    assert d.with_av == 2  # a1 同时含音视频只计一次
    assert d.av_ratio == pytest.approx(2 / 5)


def test_account_scope_filters_all_stats(populated):
    d = load_report_data(populated, account_biz=BIZ1)
    assert d.account_label == "号甲"
    assert d.total_articles == 5
    assert d.album_top == (("算法", 2), ("随笔", 1))
    # 媒体统计同样限账号
    assert d.with_video == 2 and d.downloaded_total == 4


def test_album_top_respects_limit_and_tiebreak(conn):
    for i, album in enumerate(["丙", "乙", "甲", "甲", "乙", "甲"]):
        _add(conn, _article(
            10 + i, publish_time=f"2024-0{(i % 9) + 1}-01T00:00:00", album=album
        ))
    d = load_report_data(conn, top_n=2)
    assert d.album_top == (("甲", 3), ("乙", 2))


def test_csv_detail_rows_and_beijing_columns(populated, tmp_path):
    result = generate_report(populated, tmp_path / "report")
    raw = result.csv_path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert len(rows) == 6
    headers = set(rows[0])
    assert {"发布时间_UTC", "发布时间_北京", "年", "年月", "星期",
            "小时(北京)", "原创", "合集", "含音频", "含视频", "状态"} <= headers

    by_id = {int(r["ID"]): r for r in rows}
    # a3：UTC 2023-12-31 17:00 → 北京 2024-01-01 01:00 周一
    a3 = next(r for r in rows if r["发布时间_UTC"].startswith("2023-12-31"))
    assert a3["发布时间_北京"] == "2024-01-01 01:00:00"
    assert a3["年"] == "2024" and a3["年月"] == "2024-01"
    assert a3["星期"] == "周一" and a3["小时(北京)"] == "1"
    # 布尔列中文化
    assert a3["原创"] == "是"
    assert by_id[1]["含音频"] == "是" and by_id[1]["含视频"] == "是"
    assert by_id[5]["状态"] == "pending" and by_id[5]["含音频"] == "否"


def test_html_contains_five_sections_and_reconciliation_sql(populated, tmp_path):
    result = generate_report(populated, tmp_path / "report")
    html = result.html_path.read_text(encoding="utf-8")

    for title in (
        "发文量时间序列（年）", "发文量时间序列（月）",
        "星期 × 时段发布热力", "原创占比", "合集 Top 分布",
        "含音频/视频文章占比", "对账 SQL",
    ):
        assert title in html
    for sql_fragment in (
        "strftime('%Y-%m'", "strftime('%w'", "is_original = 1",
        "media_type IN ('audio','video')", "status = 'downloaded'",
    ):
        assert sql_fragment in html
    # 热力表 7 行 × 24 小时列 + 表头
    assert html.count('class="heat"') == 1


def test_html_is_offline_single_file(populated, tmp_path):
    result = generate_report(populated, tmp_path / "report")
    html = result.html_path.read_text(encoding="utf-8")
    # 无外部资源引用（http(s) 链接/CDN/脚本）
    assert 'src="http' not in html
    assert 'href="http' not in html
    assert "<script" not in html.lower()


def test_album_name_html_escaped(conn, tmp_path):
    _add(conn, _article(1, album="<img src=x onerror=alert(1)>合集"))
    result = generate_report(conn, tmp_path / "report")
    html = result.html_path.read_text(encoding="utf-8")
    assert "<img src=x onerror" not in html
    assert "&lt;img" in html


def test_frame_has_one_row_per_article_with_media_flags(populated):
    frame = build_articles_frame(populated)
    assert len(frame) == 6
    assert list(frame.columns)  # 非空
    a1 = frame[frame["id"] == 1].iloc[0]
    assert bool(a1["has_audio"]) and bool(a1["has_video"])


# ---------- 原子性与 CLI ----------

def test_regenerate_is_idempotent_without_tmp_leftover(populated, tmp_path):
    out = tmp_path / "report"
    first = generate_report(populated, out)
    html1 = first.html_path.read_bytes()
    csv1 = first.csv_path.read_bytes()
    second = generate_report(populated, out)
    assert second.html_path.read_bytes() == html1
    assert second.csv_path.read_bytes() == csv1
    assert list(out.glob("*.tmp")) == []


def test_render_empty_html_does_not_raise(conn):
    html = render_html(load_report_data(conn))
    assert "公众号归档分析报表" in html
    # 空态 KPI 显示破折号而非 Python 的 None
    assert "—" in html
    assert ">None<" not in html


def test_upstream_iso_with_offset_supported(conn):
    """上游 _to_iso_datetime 实际产出 '...+00:00' 后缀形态（SQL 与 pandas 均须兼容）。"""
    _add(conn, _article(1, publish_time="2024-03-01T01:30:00+00:00",
                        is_original=True))
    d = load_report_data(conn)
    assert d.timed_articles == 1
    assert d.monthly == (("2024-03", 1),)
    assert d.heatmap[(5, 9)] == 1
    frame = build_articles_frame(conn)
    row = frame.iloc[0]
    assert row["publish_time_beijing"] == "2024-03-01 09:30:00"
    assert row["weekday_name"] == "周五" and row["hour"] == 9


def test_csv_formula_injection_neutralized(conn, tmp_path):
    _add(conn, _article(1, title="=CMD|'/c calc'!A1",
                        publish_time="2024-03-01T00:00:00+00:00"))
    result = generate_report(conn, tmp_path / "report")
    text = result.csv_path.read_bytes().decode("utf-8-sig")
    assert "'=CMD|'/c calc'!A1" in text
    # 单元格首字符不再是公式触发符
    for line in csv.reader(io.StringIO(text)):
        for cell in line:
            assert not cell[:1] in {"=", "+", "@"}


def test_footer_sql_scope_clause_matches_scope(populated, tmp_path):
    all_html = generate_report(populated, tmp_path / "all").html_path.read_text("utf-8")
    assert "biz = :biz" not in all_html.split("对账 SQL")[1]

    scoped_html = generate_report(
        populated, tmp_path / "one", account_biz=BIZ1
    ).html_path.read_text("utf-8")
    footer = scoped_html.split("对账 SQL")[1]
    assert footer.count("biz = :biz") >= 6
    # 账号恰好命名为「全部账号」时不影响 scoped 判定（显式布尔标志）
    c2 = connect(tmp_path / "t2.db"); init_db(c2)
    _add(c2, _article(1, biz="biz-x", alias="全部账号",
                      publish_time="2024-03-01T00:00:00"))
    tricky = generate_report(c2, tmp_path / "tricky", account_biz="biz-x")
    assert tricky.data.scoped is True
    assert "biz = :biz" in tricky.html_path.read_text("utf-8").split("对账 SQL")[1]


def test_cli_report_exit_codes(conn, tmp_path, monkeypatch):
    from mp_archiver.cli import main

    _add(conn, _article(1, publish_time="2024-03-01T01:30:00", is_original=True))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    # 测试默认使用内存式隔离：直接把库放在临时目录
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "data" / "t.db"))

    # 复用连接已写入另一库；CLI 使用自己的库，故通过环境库重放一篇
    cli_conn = connect(tmp_path / "data" / "t.db")
    init_db(cli_conn)
    _add(cli_conn, _article(1, publish_time="2024-03-01T01:30:00",
                            is_original=True))

    out = tmp_path / "out"
    assert main(["report", "-o", str(out)]) == 0
    assert (out / "report.html").exists() and (out / "report.csv").exists()

    # 未知账号 → 3
    assert main(["report", "-a", "不存在的号", "-o", str(out)]) == 3
    # 已知账号 → 0
    assert main(["report", "-a", "号甲", "-o", str(out / "scoped")]) == 0
