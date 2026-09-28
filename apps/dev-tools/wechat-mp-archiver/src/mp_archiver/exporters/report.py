"""分析报表（Task 11 / AC-12）：CSV 明细 + 单文件离线 HTML。

纯派生离线任务：不发起任何网络请求。数据源为元数据库，产出：

- ``report.csv``：逐篇明细（含北京时间派生列），UTF-8 BOM，Excel 可直接打开；
- ``report.html``：单文件报表，内联 CSS，无 JS/外链/CDN，断网可开。

统计口径（两套分母，HTML 内同样声明）：

- 集合 M（有 ``publish_time`` 的文章）：时间序列（年/月）、星期×时段热力、
  原创占比、合集 Top——只依赖列表元数据，未归档文章也参与；
- 集合 D（``status=downloaded`` 的文章）：含音频/视频占比分母——媒体行仅在
  正文归档阶段写入，未归档文章无法判断富媒体，纳入分母会造成假性偏低。

时区：微信公众号运营场景按北京时间（UTC+8）聚合。库内 ``publish_time`` 为
UTC ISO，聚合 SQL 用 SQLite ``strftime(..., '+8 hours')``，与 Python 侧
``ZoneInfo('Asia/Shanghai')`` 一致；HTML 页脚附每项数字的对账 SQL。
"""

import os
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from jinja2 import Environment, select_autoescape

# 周一 … 周日；SQLite strftime('%w') 以周日=0，按此顺序展示
WEEKDAY_LABELS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
_WEEKDAY_ROWS = (1, 2, 3, 4, 5, 6, 0)
_BEIJING_TZ = "Asia/Shanghai"

# CSV 明细列顺序与中文表头（HTML 字段为英文内部名）
_CSV_COLUMNS: tuple[tuple[str, str], ...] = (
    ("id", "ID"),
    ("account_alias", "账号"),
    ("title", "标题"),
    ("author", "作者"),
    ("publish_time", "发布时间_UTC"),
    ("publish_time_beijing", "发布时间_北京"),
    ("year", "年"),
    ("month", "年月"),
    ("weekday_name", "星期"),
    ("hour", "小时(北京)"),
    ("is_original", "原创"),
    ("album", "合集"),
    ("status", "状态"),
    ("has_audio", "含音频"),
    ("has_video", "含视频"),
    ("url", "链接"),
)


@dataclass(frozen=True, slots=True)
class ReportData:
    """五项统计的聚合结果；所有数字均可由一条 SQL 对账（见 HTML 页脚）。"""

    account_label: str
    generated_at: str = ""  # UTC ISO，渲染时注入
    scoped: bool = False  # 是否限定单账号（决定对账 SQL 是否带 biz 过滤）
    total_articles: int = 0
    timed_articles: int = 0  # 集合 M：publish_time 非空
    missing_time: int = 0
    yearly: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    monthly: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    # (SQLite %w 星期值 0=周日, 小时 0-23) → 篇数；缺格为 0
    heatmap: dict[tuple[int, int], int] = field(default_factory=dict)
    original_count: int = 0
    non_original_count: int = 0
    album_top: tuple[tuple[str, int], ...] = field(default_factory=tuple)
    no_album_count: int = 0
    downloaded_total: int = 0  # 集合 D：音视频占比分母
    with_audio: int = 0
    with_video: int = 0
    with_av: int = 0  # 含音频或视频（去重文章数）

    @property
    def original_ratio(self) -> float | None:
        if self.timed_articles == 0:
            return None
        return self.original_count / self.timed_articles

    @property
    def av_ratio(self) -> float | None:
        if self.downloaded_total == 0:
            return None
        return self.with_av / self.downloaded_total


def _scope(account_biz: str | None) -> tuple[str, tuple]:
    """账号过滤子句与参数。"""
    if account_biz is None:
        return "", ()
    return " AND biz = ?", (account_biz,)


def load_report_data(
    conn, *, account_biz: str | None = None, top_n: int = 10
) -> ReportData:
    """用聚合 SQL 取五项统计（每条数字对应一条可对账查询）。"""
    clause, params = _scope(account_biz)
    time_clause = "publish_time IS NOT NULL AND publish_time <> ''"

    total = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE 1=1{clause}", params
    ).fetchone()[0]
    timed = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE {time_clause}{clause}", params
    ).fetchone()[0]

    yearly = tuple(
        (row["period"], row["n"])
        for row in conn.execute(
            f"SELECT strftime('%Y', publish_time, '+8 hours') AS period, "
            f"COUNT(*) AS n FROM articles "
            f"WHERE {time_clause}{clause} GROUP BY period ORDER BY period",
            params,
        )
    )
    monthly = tuple(
        (row["period"], row["n"])
        for row in conn.execute(
            f"SELECT strftime('%Y-%m', publish_time, '+8 hours') AS period, "
            f"COUNT(*) AS n FROM articles "
            f"WHERE {time_clause}{clause} GROUP BY period ORDER BY period",
            params,
        )
    )
    heatmap: dict[tuple[int, int], int] = {}
    for row in conn.execute(
        "SELECT CAST(strftime('%w', publish_time, '+8 hours') AS INTEGER) AS wd, "
        "CAST(strftime('%H', publish_time, '+8 hours') AS INTEGER) AS hr, "
        f"COUNT(*) AS n FROM articles WHERE {time_clause}{clause} "
        "GROUP BY wd, hr",
        params,
    ):
        heatmap[(int(row["wd"]), int(row["hr"]))] = int(row["n"])

    original = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE {time_clause} AND is_original = 1{clause}",
        params,
    ).fetchone()[0]

    album_rows = conn.execute(
        f"SELECT album, COUNT(*) AS n FROM articles "
        f"WHERE {time_clause} AND album <> ''{clause} "
        f"GROUP BY album ORDER BY n DESC, album ASC LIMIT ?",
        (*params, int(top_n)),
    ).fetchall()
    album_top = tuple((row["album"], int(row["n"])) for row in album_rows)
    in_album = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE {time_clause} AND album <> ''{clause}",
        params,
    ).fetchone()[0]

    downloaded = conn.execute(
        f"SELECT COUNT(*) FROM articles WHERE status = 'downloaded'{clause}",
        params,
    ).fetchone()[0]

    def _count_media(types: tuple[str, ...]) -> int:
        placeholders = ",".join("?" for _ in types)
        biz_join = " AND a.biz = ?" if account_biz is not None else ""
        sql_params = (*types, *(params if account_biz is not None else ()))
        return conn.execute(
            "SELECT COUNT(DISTINCT a.id) FROM articles a "
            "JOIN media m ON m.article_id = a.id "
            f"WHERE m.media_type IN ({placeholders}){biz_join}",
            sql_params,
        ).fetchone()[0]

    with_audio = _count_media(("audio",))
    with_video = _count_media(("video",))
    with_av = _count_media(("audio", "video"))

    if account_biz is not None:
        label_row = conn.execute(
            "SELECT account_alias FROM articles WHERE biz = ? "
            "AND account_alias <> '' LIMIT 1",
            (account_biz,),
        ).fetchone()
        account_label = label_row["account_alias"] if label_row else account_biz
    else:
        account_label = "全部账号"

    return ReportData(
        account_label=account_label,
        scoped=account_biz is not None,
        total_articles=int(total),
        timed_articles=int(timed),
        missing_time=int(total - timed),
        yearly=yearly,
        monthly=monthly,
        heatmap=heatmap,
        original_count=int(original),
        non_original_count=int(timed - original),
        album_top=album_top,
        no_album_count=int(timed - in_album),
        downloaded_total=int(downloaded),
        with_audio=int(with_audio),
        with_video=int(with_video),
        with_av=int(with_av),
    )


_ARTICLES_SQL = (
    "SELECT a.id, a.account_alias, a.title, a.author, a.publish_time, "
    "a.is_original, a.album, a.status, a.url, "
    "EXISTS(SELECT 1 FROM media m WHERE m.article_id = a.id "
    "AND m.media_type = 'audio') AS has_audio, "
    "EXISTS(SELECT 1 FROM media m WHERE m.article_id = a.id "
    "AND m.media_type = 'video') AS has_video "
    "FROM articles a{where} ORDER BY a.publish_time IS NULL, "
    "a.publish_time ASC, a.id ASC"
)


def build_articles_frame(conn, *, account_biz: str | None = None) -> pd.DataFrame:
    """逐篇明细 DataFrame：UTC 原文 + 北京时间派生列（年/月/星期/小时）。"""
    if account_biz is None:
        frame = pd.read_sql_query(_ARTICLES_SQL.format(where=""), conn)
    else:
        frame = pd.read_sql_query(
            _ARTICLES_SQL.format(where=" WHERE a.biz = ?"), conn,
            params=(account_biz,),
        )

    dt_bj = (
        pd.to_datetime(
            frame["publish_time"], utc=True, errors="coerce", format="ISO8601"
        )
        .dt.tz_convert(_BEIJING_TZ)
    )
    frame["publish_time_beijing"] = dt_bj.dt.strftime("%Y-%m-%d %H:%M:%S")
    frame["year"] = dt_bj.dt.year.astype("Int64")
    frame["month"] = dt_bj.dt.strftime("%Y-%m")
    weekday_num = (dt_bj.dt.weekday + 1)  # pandas: 0=周一；+1 后 1=周一…7=周日
    frame["weekday_name"] = weekday_num.map(
        lambda v: WEEKDAY_LABELS[int(v) - 1] if pd.notna(v) else ""
    )
    frame["hour"] = dt_bj.dt.hour.astype("Int64")
    frame["is_original"] = frame["is_original"].map(bool)
    frame["has_audio"] = frame["has_audio"].map(bool)
    frame["has_video"] = frame["has_video"].map(bool)
    return frame


def _atomic_write(path: Path, data: str | bytes) -> None:
    """同目录临时文件 + os.replace 整体覆盖（与 RAG 导出一致）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    if isinstance(data, str):
        tmp.write_text(data, encoding="utf-8", newline="\n")
    else:
        tmp.write_bytes(data)
    os.replace(tmp, path)


def _csv_safe(value):
    """防 CSV/Excel 公式注入：``= + - @``/制表/回车开头的文本单元格前置单引号。

    标题/链接/合集名均为公众号侧用户可控文本，报表可能被分享后用 Excel 打开。
    """
    if isinstance(value, str) and value[:1] in {"=", "+", "-", "@", "\t", "\r"}:
        return "'" + value
    return value


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    """CSV 明细：固定列序 + 中文表头，UTF-8 BOM（Excel 打开不乱码）。"""
    ordered = frame[[en for en, _ in _CSV_COLUMNS]].copy()
    for col in ("is_original", "has_audio", "has_video"):
        ordered[col] = ordered[col].map(lambda v: "是" if v else "否")
    for col in ("account_alias", "title", "author", "album", "status", "url"):
        ordered[col] = ordered[col].map(_csv_safe)
    ordered.columns = [zh for _, zh in _CSV_COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    # utf-8-sig：Excel 直接打开中文不乱码
    ordered.to_csv(tmp, index=False, lineterminator="\n", encoding="utf-8-sig")
    os.replace(tmp, path)


def _heat_color(value: int, peak: int) -> str:
    """热力格背景色：0 留白，峰值最深（静态内联色，无 JS）。"""
    if value <= 0 or peak <= 0:
        return "#f6f8fa"
    alpha = 0.18 + 0.72 * (value / peak)
    return f"rgba(31,119,180,{alpha:.3f})"


def render_html(data: ReportData) -> str:
    """渲染单文件离线 HTML（自动转义，内联 CSS，零外部资源）。"""
    env = Environment(
        autoescape=select_autoescape(("html", "htm")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["weekday_rows"] = _WEEKDAY_ROWS
    env.globals["weekday_labels"] = WEEKDAY_LABELS
    # SQLite strftime('%w') 值（0=周日）→ 中文标签
    env.globals["wd_label"] = {0: WEEKDAY_LABELS[6], **{
        i: WEEKDAY_LABELS[i - 1] for i in range(1, 7)
    }}
    env.globals["heat_color"] = _heat_color
    env.globals["hours"] = range(24)
    env.globals["peak"] = max(data.heatmap.values(), default=0)
    env.globals["month_peak"] = max((n for _, n in data.monthly), default=0)
    env.globals["year_peak"] = max((n for _, n in data.yearly), default=0)
    return env.from_string(_HTML_TEMPLATE).render(d=data)


@dataclass(frozen=True, slots=True)
class ReportResult:
    html_path: Path
    csv_path: Path
    data: ReportData


def generate_report(
    conn,
    out_dir: str | Path,
    *,
    account_biz: str | None = None,
    top_n: int = 10,
) -> ReportResult:
    """编排：聚合 → 明细 → 渲染 → 原子落盘 HTML+CSV。"""
    out_dir = Path(out_dir)
    data = load_report_data(conn, account_biz=account_biz, top_n=top_n)
    data = replace(
        data,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    frame = build_articles_frame(conn, account_biz=account_biz)

    html_path = out_dir / "report.html"
    csv_path = out_dir / "report.csv"
    _atomic_write(html_path, render_html(data))
    _write_csv(frame, csv_path)
    return ReportResult(html_path=html_path, csv_path=csv_path, data=data)


_HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>公众号归档分析报表 - {{ d.account_label }}</title>
<style>
  :root { --ink:#1f2328; --muted:#656d76; --line:#d0d7de; --bg:#ffffff; --soft:#f6f8fa; --blue:#1f77b4; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--soft); color:var(--ink);
        font-family:"Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;
        font-size:14px; line-height:1.6; }
  main { max-width:980px; margin:0 auto; padding:24px 20px 56px; }
  h1 { font-size:22px; margin:0 0 4px; }
  h2 { font-size:17px; margin:28px 0 10px; padding-bottom:6px; border-bottom:1px solid var(--line); }
  .meta { color:var(--muted); font-size:12px; margin-bottom:16px; }
  section.card { background:var(--bg); border:1px solid var(--line); border-radius:8px;
        padding:16px 18px; margin-top:14px; }
  .scope { background:#ddf4ff; border:1px solid #b6e3ff; border-radius:6px;
        padding:10px 12px; font-size:12.5px; color:#0a3069; }
  .kpis { display:flex; flex-wrap:wrap; gap:12px; margin:14px 0 4px; }
  .kpi { flex:1 1 150px; background:var(--soft); border:1px solid var(--line);
        border-radius:8px; padding:10px 12px; }
  .kpi .num { font-size:22px; font-weight:700; }
  .kpi .lab { color:var(--muted); font-size:12px; }
  table { border-collapse:collapse; width:100%; }
  th, td { border:1px solid var(--line); padding:5px 8px; text-align:center; }
  th { background:var(--soft); font-weight:600; }
  td.name, th.name { text-align:left; }
  .bar-row { display:flex; align-items:center; gap:8px; margin:3px 0; }
  .bar-row .lbl { width:84px; color:var(--muted); font-size:12px; text-align:right; flex:none; }
  .bar-row .track { flex:1; background:var(--soft); border-radius:4px; height:18px; position:relative; }
  .bar-row .fill { position:absolute; left:0; top:0; bottom:0; background:var(--blue);
        border-radius:4px; min-width:2px; }
  .bar-row .val { width:130px; flex:none; font-size:12px; }
  .heat td { width:3.6%; height:30px; font-size:11px; padding:2px; }
  .heat th { font-size:11px; padding:3px 1px; font-weight:500; color:var(--muted); }
  .ratio { display:flex; height:26px; border-radius:5px; overflow:hidden; border:1px solid var(--line); }
  .ratio .yes { background:#2da44e; }
  .ratio .no { background:#d0d7de; }
  .ratio-lab { margin-top:6px; font-size:12.5px; color:var(--muted); }
  .empty { color:var(--muted); padding:18px 0; text-align:center; }
  details { margin-top:8px; }
  summary { cursor:pointer; color:var(--muted); font-size:12.5px; }
  pre { background:var(--soft); border:1px solid var(--line); border-radius:6px;
        padding:10px 12px; font-size:12px; overflow-x:auto; white-space:pre-wrap; }
</style>
</head>
<body>
<main>
  <h1>公众号归档分析报表</h1>
  <div class="meta">范围：{{ d.account_label }} ｜ 生成时间（UTC）：{{ d.generated_at }} ｜ mp-archiver report</div>
  <div class="scope">
    统计口径：① 发文时间/原创/合集四项基于<b>有发布时间的 {{ d.timed_articles }} 篇</b>
    （共 {{ d.total_articles }} 篇，其中 {{ d.missing_time }} 篇无发布时间不参与时间类统计）；
    ② 音视频占比基于<b>已归档 {{ d.downloaded_total }} 篇</b>——富媒体仅在正文归档时识别，
    未归档文章无法判定。时间均按<b>北京时间（UTC+8）</b>聚合。
  </div>

  <div class="kpis">
    <div class="kpi"><div class="num">{{ d.total_articles }}</div><div class="lab">文章总数</div></div>
    <div class="kpi"><div class="num">{% if d.original_ratio is none %}—{% else %}{{ (d.original_ratio * 100) | round(1) }}%{% endif %}</div><div class="lab">原创占比（{{ d.original_count }}/{{ d.timed_articles }}）</div></div>
    <div class="kpi"><div class="num">{{ d.album_top | length }}</div><div class="lab">合集数（Top{{ d.album_top | length }}）</div></div>
    <div class="kpi"><div class="num">{% if d.av_ratio is none %}—{% else %}{{ (d.av_ratio * 100) | round(1) }}%{% endif %}</div><div class="lab">含音视频（{{ d.with_av }}/{{ d.downloaded_total }}）</div></div>
  </div>

  <section class="card">
    <h2>① 发文量时间序列（年）</h2>
    {% if d.yearly %}
    {% for period, n in d.yearly %}
    <div class="bar-row">
      <span class="lbl">{{ period }}</span>
      <span class="track"><span class="fill" style="width:{{ (n / year_peak * 100) | round(1) }}%"></span></span>
      <span class="val">{{ n }} 篇</span>
    </div>
    {% endfor %}
    {% else %}<div class="empty">暂无带发布时间的文章</div>{% endif %}
  </section>

  <section class="card">
    <h2>② 发文量时间序列（月）</h2>
    {% if d.monthly %}
    {% for period, n in d.monthly %}
    <div class="bar-row">
      <span class="lbl">{{ period }}</span>
      <span class="track"><span class="fill" style="width:{{ (n / month_peak * 100) | round(1) }}%"></span></span>
      <span class="val">{{ n }} 篇</span>
    </div>
    {% endfor %}
    {% else %}<div class="empty">暂无带发布时间的文章</div>{% endif %}
  </section>

  <section class="card">
    <h2>③ 星期 × 时段发布热力（北京时间）</h2>
    {% if d.timed_articles %}
    <table class="heat">
      <tr><th class="name">星期＼时</th>{% for h in hours %}<th>{{ "%02d" | format(h) }}</th>{% endfor %}</tr>
      {% for wd in weekday_rows %}
      <tr>
        <th class="name">{{ wd_label[wd] }}</th>
        {% for h in hours %}
        {% set n = d.heatmap.get((wd, h), 0) %}
        <td style="background:{{ heat_color(n, peak) }}" title="{{ wd_label[wd] }} {{ "%02d" | format(h) }}时：{{ n }} 篇">{{ n if n else "" }}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </table>
    {% else %}<div class="empty">暂无带发布时间的文章</div>{% endif %}
  </section>

  <section class="card">
    <h2>④ 原创占比</h2>
    {% if d.original_ratio is not none %}
    <div class="ratio">
      <div class="yes" style="width:{{ (d.original_ratio * 100) | round(1) }}%"></div>
      <div class="no" style="width:{{ (100 - d.original_ratio * 100) | round(1) }}%"></div>
    </div>
    <div class="ratio-lab">原创 {{ d.original_count }} 篇（{{ (d.original_ratio * 100) | round(1) }}%）｜ 非原创 {{ d.non_original_count }} 篇（{{ ((1 - d.original_ratio) * 100) | round(1) }}%），分母为有发布时间的 {{ d.timed_articles }} 篇</div>
    {% else %}<div class="empty">暂无带发布时间的文章</div>{% endif %}
  </section>

  <section class="card">
    <h2>⑤ 合集 Top 分布</h2>
    {% if d.album_top %}
    <table>
      <tr><th class="name">合集</th><th>篇数</th><th>占比</th></tr>
      {% for name, n in d.album_top %}
      <tr><td class="name">{{ name }}</td><td>{{ n }}</td><td>{{ (n / d.timed_articles * 100) | round(1) }}%</td></tr>
      {% endfor %}
    </table>
    <div class="ratio-lab">未归入合集：{{ d.no_album_count }} 篇（分母 {{ d.timed_articles }} 篇）</div>
    {% else %}<div class="empty">暂无合集数据</div>{% endif %}
  </section>

  <section class="card">
    <h2>⑥ 含音频/视频文章占比</h2>
    {% if d.av_ratio is not none %}
    <div class="ratio">
      <div class="yes" style="width:{{ (d.av_ratio * 100) | round(1) }}%"></div>
      <div class="no" style="width:{{ (100 - d.av_ratio * 100) | round(1) }}%"></div>
    </div>
    <div class="ratio-lab">
      含音频或视频 {{ d.with_av }} 篇（{{ (d.av_ratio * 100) | round(1) }}%），其中含音频 {{ d.with_audio }} 篇、含视频 {{ d.with_video }} 篇（一篇可同时含两类）；
      分母为已归档 {{ d.downloaded_total }} 篇。
    </div>
    {% else %}<div class="empty">暂无已归档文章（执行 fetch 归档正文后生成）</div>{% endif %}
  </section>

  <section class="card">
    <h2>对账 SQL（每项数字一条；时间聚合 +8 小时即北京时间）</h2>
    <details open>
      <summary>展开/收起全部对账语句</summary>
      <pre>-- 文章总数 / 有发布时间数
SELECT COUNT(*) AS total FROM articles{{ " WHERE biz = :biz" if d.scoped else "" }};
SELECT COUNT(*) AS timed FROM articles WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }};

-- ①② 年/月发文量
SELECT strftime('%Y', publish_time, '+8 hours') AS period, COUNT(*) FROM articles
 WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }} GROUP BY period ORDER BY period;
SELECT strftime('%Y-%m', publish_time, '+8 hours') AS period, COUNT(*) FROM articles
 WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }} GROUP BY period ORDER BY period;

-- ③ 星期(0=周日)×小时热力
SELECT CAST(strftime('%w', publish_time, '+8 hours') AS INTEGER) AS wd,
       CAST(strftime('%H', publish_time, '+8 hours') AS INTEGER) AS hr, COUNT(*) AS n
  FROM articles WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }} GROUP BY wd, hr;

-- ④ 原创占比
SELECT SUM(is_original = 1) AS original, COUNT(*) AS timed FROM articles
 WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }};

-- ⑤ 合集 Top
SELECT album, COUNT(*) AS n FROM articles
 WHERE publish_time IS NOT NULL AND publish_time &lt;&gt; '' AND album &lt;&gt; ''{{ " AND biz = :biz" if d.scoped else "" }}
 GROUP BY album ORDER BY n DESC, album;

-- ⑥ 含音视频文章数（分母为 downloaded）
SELECT COUNT(DISTINCT a.id) FROM articles a JOIN media m ON m.article_id = a.id
 WHERE m.media_type IN ('audio','video'){{ " AND a.biz = :biz" if d.scoped else "" }};
SELECT COUNT(*) FROM articles WHERE status = 'downloaded'{{ " AND biz = :biz" if d.scoped else "" }};</pre>
    </details>
  </section>
</main>
</body>
</html>
"""
